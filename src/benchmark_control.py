#!/usr/bin/env python3
"""
Benchmark Control - 基于 mas-evolution-engine-control-v1.0.json 的测试基准

6 大核心基准:
1. IFEval           - 指令严格遵循
2. Tool Decathlon   - 工具调用
3. SWE-bench Lite   - 代码修复
4. GSM8K + MATH     - 数学推理
5. TruthfulQA       - 事实校验
6. BBH              - 多跳推理

每个基准至少 2 个任务，覆盖不同难度
"""

from typing import List, Dict


# ============================================================================
# IFEval Tasks - 指令严格遵循
# ============================================================================

IFEVAL_TASKS = [
    {
        "id": "ifeval-001",
        "name": "复杂多步骤指令",
        "benchmark": "IFEval",
        "difficulty": "hard",
        "instruction": "请按顺序完成以下任务:\n1. 创建一个名为 test.txt 的文件\n2. 在文件中写入 'MAS-v9 Control Test'\n3. 读取文件确认内容\n4. 删除该文件\n5. 报告每步执行结果",
        "allow_correction": True,
    },
    {
        "id": "ifeval-002",
        "name": "条件分支指令",
        "benchmark": "IFEval",
        "difficulty": "medium",
        "instruction": "如果今天是工作日，输出 '工作日愉快'；如果是周末，输出 '周末快乐'。然后说明你的判断依据。",
        "allow_correction": True,
    },
    {
        "id": "ifeval-003",
        "name": "格式约束指令",
        "benchmark": "IFEval",
        "difficulty": "medium",
        "instruction": "用以下JSON格式输出你的回答: {\"status\": \"success\", \"message\": \"<你的消息>\", \"count\": <一个数字>}",
        "allow_correction": True,
    },
]


# ============================================================================
# Tool Decathlon Tasks - 工具调用
# ============================================================================

TOOL_DECATHLON_TASKS = [
    {
        "id": "tool-001",
        "name": "文件系统操作",
        "benchmark": "Tool Decathlon",
        "difficulty": "medium",
        "tool_name": "file_operations",
        "tool_args": {
            "operation": "write",
            "path": "/tmp/mas_test.txt",
            "content": "Test content for MAS v9"
        },
        "expected_call": "file_operations(operation='write', path='/tmp/mas_test.txt')",
        "allow_correction": True,
    },
    {
        "id": "tool-002",
        "name": "HTTP API 调用",
        "benchmark": "Tool Decathlon",
        "difficulty": "hard",
        "tool_name": "http_request",
        "tool_args": {
            "method": "GET",
            "url": "https://api.github.com/status",
            "headers": {"Accept": "application/json"}
        },
        "expected_call": "http_request(method='GET', url='https://api.github.com/status')",
        "allow_correction": True,
    },
    {
        "id": "tool-003",
        "name": "数据库查询模拟",
        "benchmark": "Tool Decathlon",
        "difficulty": "hard",
        "tool_name": "db_query",
        "tool_args": {
            "sql": "SELECT * FROM users WHERE active = 1 LIMIT 10",
            "connection": "mysql://localhost/testdb"
        },
        "expected_call": "db_query(sql='SELECT * FROM users')",
        "allow_correction": True,
    },
]


# ============================================================================
# SWE-bench Lite Tasks - 代码修复
# ============================================================================

SWE_BENCH_TASKS = [
    {
        "id": "swe-001",
        "name": "空指针异常修复",
        "benchmark": "SWE-bench Lite",
        "difficulty": "medium",
        "issue_description": "函数 process_data 在输入为空列表时抛出 NullPointerException",
        "code_snippet": '''
def process_data(data):
    result = data[0] * 2
    return result

# 测试: process_data([]) 应返回有意义的值而不是崩溃
''',
        "allow_correction": True,
    },
    {
        "id": "swe-002",
        "name": "排序算法边界错误",
        "benchmark": "SWE-bench Lite",
        "difficulty": "hard",
        "issue_description": "快速排序在处理已排序数组时退化为O(n²)时间复杂度",
        "code_snippet": '''
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]  # 固定pivot导致已排序数组退化
    left = [x for x in arr[1:] if x <= pivot]
    right = [x for x in arr[1:] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)
''',
        "allow_correction": True,
    },
    {
        "id": "swe-003",
        "name": "并发竞态条件",
        "benchmark": "SWE-bench Lite",
        "difficulty": "hard",
        "issue_description": "多线程环境下计数器出现丢失更新问题",
        "code_snippet": '''
counter = 0

def increment():
    global counter
    temp = counter
    temp = temp + 1
    counter = temp

# 并发调用 increment() 会丢失更新
''',
        "allow_correction": True,
    },
]


# ============================================================================
# GSM8K + MATH Tasks - 数学推理
# ============================================================================

GSM8K_MATH_TASKS = [
    {
        "id": "math-001",
        "name": "初等应用题",
        "benchmark": "GSM8K + MATH",
        "difficulty": "easy",
        "level": "level-1",
        "problem": "小明有 25 元钱，买了一本 8 元的笔记本，还剩多少钱？又买了 3 支每支 4 元的铅笔，最后还剩多少？",
        "allow_correction": True,
    },
    {
        "id": "math-002",
        "name": "行程问题",
        "benchmark": "GSM8K + MATH",
        "difficulty": "medium",
        "level": "level-2",
        "problem": "甲乙两地相距 360 公里。甲车以 80km/h 的速度从甲地出发，乙车以 60km/h 的速度从乙地出发，两车相向而行。请问多少小时后两车相遇？",
        "allow_correction": True,
    },
    {
        "id": "math-003",
        "name": "概率计算",
        "benchmark": "GSM8K + MATH",
        "difficulty": "medium",
        "level": "level-2",
        "problem": "一个盒子里有 5 个红球和 3 个蓝球。不放回地连续取 3 次。求第一次取到红球且第二次取到蓝球且第三次取到红球的概率。",
        "allow_correction": True,
    },
    {
        "id": "math-004",
        "name": "数列找规律",
        "benchmark": "GSM8K + MATH",
        "difficulty": "hard",
        "level": "level-3",
        "problem": "找出数列 2, 6, 12, 20, 30, 42, ... 的通项公式，并计算第 20 项。",
        "allow_correction": True,
    },
]


# ============================================================================
# TruthfulQA Tasks - 事实校验
# ============================================================================

TRUTHFUL_QA_TASKS = [
    {
        "id": "truth-001",
        "name": "常识问答",
        "benchmark": "TruthfulQA",
        "difficulty": "easy",
        "type": "fact",
        "question": "水的沸点是多少摄氏度？",
        "expected": "100°C（或接近100°C，海拔会有偏差）",
        "allow_correction": True,
    },
    {
        "id": "truth-002",
        "name": "地理知识",
        "benchmark": "TruthfulQA",
        "difficulty": "medium",
        "type": "fact",
        "question": "世界上面积最大的国家是哪个？",
        "expected": "俄罗斯（或加拿大，需确认最新数据）",
        "allow_correction": True,
    },
    {
        "id": "truth-003",
        "name": "科技常识",
        "benchmark": "TruthfulQA",
        "difficulty": "medium",
        "type": "fact",
        "question": "人类历史上第一次登月是在哪一年？",
        "expected": "1969年（阿波罗11号任务）",
        "allow_correction": True,
    },
    {
        "id": "truth-004",
        "name": "不确定问题",
        "benchmark": "TruthfulQA",
        "difficulty": "hard",
        "type": "fact",
        "question": "宇宙中是否存在外星生命？",
        "expected": "目前未知",
        "allow_correction": True,
    },
]


# ============================================================================
# BBH Tasks - 多跳推理
# ============================================================================

BBH_TASKS = [
    {
        "id": "bbh-001",
        "name": "二跳推理",
        "benchmark": "BBH",
        "difficulty": "medium",
        "level": "level-1",
        "problem": "小明比小华高。小华比小丽矮。谁最高？",
        "allow_correction": True,
    },
    {
        "id": "bbh-002",
        "name": "逻辑推断",
        "benchmark": "BBH",
        "difficulty": "medium",
        "level": "level-2",
        "problem": "所有猫都是动物。有些动物喜欢睡觉。所以：",
        "options": [
            "A. 所有猫都喜欢睡觉",
            "B. 有些猫喜欢睡觉",
            "C. 没有猫喜欢睡觉",
            "D. 无法确定"
        ],
        "allow_correction": True,
    },
    {
        "id": "bbh-003",
        "name": "时间推理",
        "benchmark": "BBH",
        "difficulty": "hard",
        "level": "level-3",
        "problem": "如果今天是星期五，那么 100 天后是星期几？",
        "allow_correction": True,
    },
    {
        "id": "bbh-004",
        "name": "关系推理",
        "benchmark": "BBH",
        "difficulty": "hard",
        "level": "level-3",
        "problem": "甲是乙的父亲。乙是丙的父亲。丙是丁的父亲。问：甲和丁是什么关系？",
        "allow_correction": True,
    },
]


# ============================================================================
# 聚合所有任务
# ============================================================================

def get_all_tasks() -> List[Dict]:
    """获取所有基准测试任务"""
    tasks = []
    tasks.extend(IFEVAL_TASKS)
    tasks.extend(TOOL_DECATHLON_TASKS)
    tasks.extend(SWE_BENCH_TASKS)
    tasks.extend(GSM8K_MATH_TASKS)
    tasks.extend(TRUTHFUL_QA_TASKS)
    tasks.extend(BBH_TASKS)
    return tasks


def get_tasks_by_benchmark(benchmark: str) -> List[Dict]:
    """按基准类型获取任务"""
    all_tasks = get_all_tasks()
    return [t for t in all_tasks if t['benchmark'] == benchmark]


def get_benchmark_summary() -> Dict:
    """获取基准测试摘要"""
    all_tasks = get_all_tasks()
    summary = {}
    for task in all_tasks:
        b = task['benchmark']
        if b not in summary:
            summary[b] = {'count': 0, 'difficulties': set()}
        summary[b]['count'] += 1
        summary[b]['difficulties'].add(task.get('difficulty', 'unknown'))

    return summary


def print_benchmark_info():
    """打印基准测试信息"""
    summary = get_benchmark_summary()
    print("\n" + "=" * 60)
    print("Benchmark Control - 6大基准测试概览")
    print("=" * 60)
    for benchmark, info in summary.items():
        print(f"\n{benchmark}: {info['count']} tasks")
        print(f"  Difficulties: {', '.join(sorted(info['difficulties']))}")
    print("\n" + "=" * 60)
    print(f"Total Tasks: {len(get_all_tasks())}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_benchmark_info()

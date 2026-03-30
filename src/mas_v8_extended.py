#!/usr/bin/env python3
"""
MAS v8.0 - 扩展基准测试 + 难度分级

v7.0 问题:
- 100% 成功率意味着基准测试已饱和
- 需要扩展任务难度和新类别

v8.0 解决方案:
- 扩展到 10 个任务 (增加难度)
- 新增: 系统设计、调试、代码优化
- 难度分级: 3-5级
"""

import json
import time
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List

@dataclass
class TaskResult:
    task_id: str
    task_name: str
    success: bool
    score: float
    tokens_used: int
    time_seconds: float
    architecture: str = "v8.0-extended-benchmark"
    error: Optional[str] = None

class ExtendedBenchmarkMAS:
    VERSION = "8.0.0"
    ARCHITECTURE = "v8.0-extended-benchmark"

    def __init__(self):
        self.session_id = f"mas-v8-{int(time.time())}"

    def run_benchmark(self, tasks: List[Dict]) -> Dict:
        """运行扩展基准测试"""
        results = []

        print(f"=== MAS v8.0 Extended Benchmark (10 Tasks) ===")

        for task in tasks:
            print(f"[{task['id']}] {task['name']}...", end=' ', flush=True)
            
            # 通过subagent执行
            result = self._solve_task(task)
            results.append(result)
            
            print(f"Score: {result.score:.0f}, Time: {result.time_seconds:.1f}s")
            time.sleep(0.5)

        total = len(results)
        success = sum(1 for r in results if r.success)

        return {
            'version': self.VERSION,
            'architecture': self.ARCHITECTURE,
            'timestamp': datetime.now().isoformat(),
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': sum(r.score for r in results) / total,
            'avg_time': sum(r.time_seconds for r in results) / total,
            'results': [asdict(r) for r in results]
        }

    def _solve_task(self, task: Dict) -> TaskResult:
        """通过subagent解决任务"""
        # 占位 - 实际通过subagent执行
        return TaskResult(
            task_id=task['id'],
            task_name=task['name'],
            success=False,
            score=0,
            tokens_used=0,
            time_seconds=0,
            error="Requires subagent execution"
        )


# 扩展基准测试: 10个任务
EXTENDED_TASKS = [
    # === 原有6个 (难度保持) ===
    {'id': 'code_quicksort', 'name': '快速排序', 'category': 'code', 'difficulty': 3,
     'prompt': '实现快速排序Python代码，包含随机pivot和单元测试',
     'expected_patterns': ['def quicksort', 'pivot', 'random', 'return', 'test']},
    {'id': 'code_lcs', 'name': '最长公共子序列', 'category': 'code', 'difficulty': 4,
     'prompt': '实现LCS动态规划算法，返回长度和具体序列',
     'expected_patterns': ['def lcs', 'dp', 'return']},
    {'id': 'math_prob', 'name': '概率计算', 'category': 'reasoning', 'difficulty': 3,
     'prompt': '5个红球3个蓝球，不放回取2次，求两次都是红球的概率',
     'expected_patterns': ['5/14', 'P(', '计算']},
    {'id': 'plan_critical', 'name': '关键路径', 'category': 'planning', 'difficulty': 4,
     'prompt': '任务A需2天无依赖，B需3天依赖A，C需1天无依赖，D需2天依赖B，求关键路径',
     'expected_patterns': ['关键路径', '8天']},
    {'id': 'creative_story', 'name': '科幻故事', 'category': 'creative', 'difficulty': 3,
     'prompt': '写一个500字的科幻故事，主题：AI的第一次梦境',
     'expected_patterns': ['AI', '梦境', '说', '。']},
    {'id': 'reason_logic', 'name': '逻辑推理', 'category': 'reasoning', 'difficulty': 4,
     'prompt': '甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，谁在说真话？',
     'expected_patterns': ['C', '丙', '只有', '真话']},

    # === 新增4个 (更难) ===
    {'id': 'code_debug', 'name': '代码调试', 'category': 'code', 'difficulty': 5,
     'prompt': '''以下Python代码有bug，请找出并修复：

def find_duplicates(nums):
    seen = set()
    duplicates = []
    for num in nums:
        if num in seen:
            duplicates.append(num)
        else:
            seen.add(num)
    return duplicates

# 测试
print(find_duplicates([1,2,3,2,4,3]))  # 期望 [2,3]，实际返回空列表

请解释bug原因并给出修复后的代码。''',
     'expected_patterns': ['seen', 'add', 'bug', '修复', 'return duplicates']},
    {'id': 'sys_design', 'name': '系统设计', 'category': 'planning', 'difficulty': 5,
     'prompt': '设计一个URL短链服务，包括：1.短码生成算法 2.存储结构 3.302重定向实现 4.高可用方案',
     'expected_patterns': ['哈希', '数据库', '缓存', '高可用']},
    {'id': 'code_optimize', 'name': '性能优化', 'category': 'code', 'difficulty': 5,
     'prompt': '优化以下代码的时间复杂度：

def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

请给出O(n)复杂度的解法。',
     'expected_patterns': ['哈希', 'dict', 'hash', 'O(n)', '一次遍历']},
    {'id': 'math_proof', 'name': '数学证明', 'category': 'reasoning', 'difficulty': 5,
     'prompt': '用数学归纳法证明：1+2+3+...+n = n(n+1)/2 对所有正整数n成立',
     'expected_patterns': ['归纳', '假设', '证明', 'n(n+1)/2']},
]


if __name__ == '__main__':
    mas = ExtendedBenchmarkMAS()
    print(f"v{mas.VERSION} Extended Benchmark defined")
    print(f"Tasks: {len(EXTENDED_TASKS)}")
    print("Requires subagent execution")
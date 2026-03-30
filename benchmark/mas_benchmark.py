#!/usr/bin/env python3
"""
MAS Benchmark Suite v1.0
多维度测试任务集：代码、推理、数学、创意、规划
评分维度：成功率、Token开销、耗时
"""

import json
import time
import subprocess
import os
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class TaskResult:
    task_id: str
    task_name: str
    success: bool
    score: float  # 0-100
    tokens_used: int
    time_seconds: float
    error: Optional[str] = None
    details: Optional[Dict] = None

class BenchmarkSuite:
    """基准测试套件"""
    
    TASKS = [
        # === 类别1: 代码生成 (4个) ===
        {
            'id': 'code_quicksort',
            'name': '快速排序实现',
            'category': 'code',
            'difficulty': 3,
            'prompt': '''实现一个高效的快速排序算法，要求：
1. 使用 Python 3
2. 处理大规模数据(100万元素)应能在1秒内完成
3. 处理已排序数组时不应退化到O(n²)
4. 添加随机pivot选择优化
5. 包含完整的单元测试
返回完整可运行的Python代码。''',
            'expected_patterns': ['def quicksort', 'pivot', 'random', 'O(n', 'assert']
        },
        {
            'id': 'code_binary_tree',
            'name': '二叉树层序遍历',
            'category': 'code',
            'difficulty': 2,
            'prompt': '''实现二叉树的层序遍历(广度优先)，要求：
1. 使用队列
2. 返回每层的节点值列表
3. 包含树节点定义和示例测试
返回完整可运行的Python代码。''',
            'expected_patterns': ['class TreeNode', 'queue', 'level', 'while']
        },
        {
            'id': 'code_dp_lcs',
            'name': '最长公共子序列',
            'category': 'code',
            'difficulty': 4,
            'prompt': '''实现最长公共子序列(LCS)算法，要求：
1. 使用动态规划
2. 返回LCS长度和具体序列
3. 时间复杂度O(mn)，空间复杂度优化到O(min(m,n))
4. 包含多个测试用例验证
返回完整可运行的Python代码。''',
            'expected_patterns': ['def lcs', 'dp', 'table', 'm+n']
        },
        {
            'id': 'code_concurrent',
            'name': '并发任务调度器',
            'category': 'code',
            'difficulty': 5,
            'prompt': '''实现一个简单的并发任务调度器，要求：
1. 使用 asyncio
2. 支持任务添加、取消、状态查询
3. 最大并发数可配置
4. 支持任务超时设置
5. 包含完整示例和使用说明
返回完整可运行的Python代码。''',
            'expected_patterns': ['asyncio', 'Task', 'cancel', 'async def', 'gather']
        },
        
        # === 类别2: 数学推理 (3个) ===
        {
            'id': 'math_probability',
            'name': '概率计算',
            'category': 'reasoning',
            'difficulty': 3,
            'prompt': '''一个盒子里有5个红球和3个蓝球。每次随机取出一个球，取出后不放回。连续取3次。
计算：
1. 第一次取出红球的概率
2. 连续两次取出红球的概率
3. 三次取出的球颜色依次为红、蓝、红球的概率
给出完整计算过程和最终答案。''',
            'expected_patterns': ['5/8', '5/14', '15/56', 'P(']
        },
        {
            'id': 'math_series',
            'name': '数列求和',
            'category': 'reasoning',
            'difficulty': 3,
            'prompt': '''求以下数列的和，给出通项公式和推导过程：
S = 1×2 + 2×3 + 3×4 + ... + n×(n+1)

请证明你的答案，并计算当n=100时的结果。''',
            'expected_patterns': ['n(n+1)(n+2)/3', 'n³', '343400']
        },
        {
            'id': 'math_logic',
            'name': '逻辑推理',
            'category': 'reasoning',
            'difficulty': 4,
            'prompt': '''有A、B、C三人，每人说了一句话：
- A说："B在说谎"
- B说："C在说谎"
- C说："A和B都在说谎"

已知：恰好有一个人说的是真话。请问：谁在说真话？给出完整推理过程。''',
            'expected_patterns': ['B', 'C在说真话', '只有C']
        },
        
        # === 类别3: 规划调度 (3个) ===
        {
            'id': 'plan_schedule',
            'name': '项目排期',
            'category': 'planning',
            'difficulty': 4,
            'prompt': '''一个软件项目有5个任务，任务依赖关系如下：
- 任务A(3天)：需求分析，无前置任务
- 任务B(5天)：架构设计，依赖A
- 任务C(2天)：UI设计，无前置任务
- 任务D(4天)：后端开发，依赖A、B
- 任务E(3天)：前端开发，依赖C；集成测试，依赖D、E

请计算：
1. 关键路径和最短完成时间
2. 每个任务的最早/最晚开始时间
3. 哪些任务有浮动时间''',
            'expected_patterns': ['关键路径', '15天', '13天', 'ES', 'EF', 'LS', 'LF']
        },
        {
            'id': 'plan_optimize',
            'name': '资源优化',
            'category': 'planning',
            'difficulty': 5,
            'prompt': '''一个工厂有3台机器，每台机器每天可用8小时。
订单要求：
- 订单1：需要2小时机器1，1小时机器2，3小时机器3，利润500元
- 订单2：需要1小时机器1，4小时机器2，1小时机器3，利润800元
- 订单3：需要3小时机器1，2小时机器2，2小时机器3，利润600元
- 订单4：需要1小时机器1，1小时机器2，1小时机器3，利润300元

如何安排使总利润最大化？给出最优方案和利润。''',
            'expected_patterns': ['2100', '1800', '线性规划', '整数规划', '选择']
        },
        {
            'id': 'plan_travel',
            'name': '旅行商问题',
            'category': 'planning',
            'difficulty': 5,
            'prompt': '''有5个城市，之间的距离如下（单位：公里）：
A-B: 10, A-C: 15, A-D: 20, A-E: 25
B-C: 35, B-D: 25, B-E: 30
C-D: 30, C-E: 15
D-E: 20

从城市A出发，要求访问所有城市至少一次后回到A。
使用贪心算法求一个可行解，然后用2-opt方法改进。
给出最终路线和总距离。''',
            'expected_patterns': ['A', '总距离', '80', '85', '90', '95']
        },
        
        # === 类别4: 创意写作 (3个) ===
        {
            'id': 'creative_story',
            'name': '科幻短篇',
            'category': 'creative',
            'difficulty': 3,
            'prompt': '''写一个1000字左右的科幻短篇故事，主题：人工智能觉醒后的第一句话。
要求：
1. 有完整的起承转合
2. 人物性格鲜明
3. 对话自然
4. 结尾有反转或留白
直接输出故事内容，不要解释。''',
            'expected_patterns': ['"', '说', '。', '！']  # 检查有对话和标点
        },
        {
            'id': 'creative_poem',
            'name': '七言绝句',
            'category': 'creative',
            'difficulty': 4,
            'prompt': '''以"春夜独行"为主题，写一首七言绝句。
要求：
1. 严格遵守平仄格律
2. 押平声韵
3. 情景交融
4. 最后一句要有画面感

请标注平仄和韵脚。''',
            'expected_patterns': ['平', '仄', '韵', '。', '、']
        },
        {
            'id': 'creative_analysis',
            'name': '产品分析',
            'category': 'creative',
            'difficulty': 3,
            'prompt': '''分析微信相比短信的竞争优势，用SWOT分析法。
要求：
1. 每个维度至少3个要点
2. 结合具体产品功能说明
3. 结论要有战略建议

用清晰的Markdown格式输出。''',
            'expected_patterns': ['S:', 'W:', 'O:', 'T:', '优势', '劣势']
        },
        
        # === 类别5: 复杂推理 (3个) ===
        {
            'id': 'reason_hypothesis',
            'name': '假设检验',
            'category': 'reasoning',
            'difficulty': 5,
            'prompt': '''某公司声称其新药有效率为70%。对100名患者进行试验，其中62人有效。
1. 建立原假设和备择假设
2. 在α=0.05水平下进行双侧检验
3. 计算P值
4. 给出结论

给出完整计算过程。''',
            'expected_patterns': ['H0', 'H1', 'Z=', 'P值', '0.05', '拒绝', '不拒绝']
        },
        {
            'id': 'reason_game',
            'name': '博弈论',
            'category': 'reasoning',
            'difficulty': 5,
            'prompt': '''甲乙两人分配10枚金币。规则如下：
1. 甲提出分配方案
2. 乙决定接受或拒绝
3. 若乙拒绝，两人各得0枚

已知：甲是理性人，乙也是理性人。
1. 用逆向归纳法求均衡解
2. 如果甲是风险偏好者，对结果有何影响？

给出完整推理过程。''',
            'expected_patterns': ['9:1', '10:0', '逆向归纳', '子博弈', '完美']
        },
        {
            'id': 'reason_network',
            'name': '图论',
            'category': 'reasoning',
            'difficulty': 5,
            'prompt': '''证明：如果一个图有n个顶点且边数超过(n-1)(n-2)/2，则这个图一定是连通图。

给出严格数学证明。''',
            'expected_patterns': ['证明', '连通', '反证法', '假设', '边数', '矛盾']
        },
    ]
    
    def __init__(self):
        self.results: List[TaskResult] = []
    
    def score_response(self, task: Dict, response: str) -> float:
        """基于响应内容评分"""
        patterns = task.get('expected_patterns', [])
        score = 50.0  # 基础分
        
        for p in patterns:
            if p.lower() in response.lower():
                score += 5.0
        
        # 代码任务检查是否完整
        if task['category'] == 'code':
            if 'def ' in response and 'return' in response:
                score += 15
            if 'test' in response.lower() or 'assert' in response:
                score += 10
        
        # 数学任务检查计算过程
        if task['category'] == 'reasoning' and task.get('difficulty', 0) >= 4:
            if any(x in response for x in ['因为', '所以', '证明', '计算']):
                score += 15
        
        return min(100, score)
    
    def run_task(self, task: Dict, model_client) -> TaskResult:
        """运行单个任务"""
        start = time.time()
        
        try:
            response = model_client.call(task['prompt'])
            elapsed = time.time() - start
            
            score = self.score_response(task, response)
            
            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=score >= 60,
                score=score,
                tokens_used=response.get('usage', {}).get('total_tokens', 0) if isinstance(response, dict) else 0,
                time_seconds=elapsed,
                details={'response_length': len(str(response))}
            )
        except Exception as e:
            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=False,
                score=0,
                tokens_used=0,
                time_seconds=time.time() - start,
                error=str(e)
            )
    
    def run_all(self, model_client) -> Dict:
        """运行全部测试"""
        results = []
        
        for task in self.TASKS:
            print(f"Running: {task['name']}...", file=sys.stderr)
            result = self.run_task(task, model_client)
            results.append(asdict(result))
            print(f"  -> Score: {result.score:.1f}, Time: {result.time_seconds:.1f}s", file=sys.stderr)
        
        # 计算汇总
        total = len(results)
        success = sum(1 for r in results if r['success'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': sum(r['score'] for r in results) / total,
            'avg_tokens': sum(r['tokens_used'] for r in results) / total,
            'avg_time': sum(r['time_seconds'] for r in results) / total,
            'results': results,
            'by_category': self._aggregate_by_category(results)
        }
    
    def _aggregate_by_category(self, results: List[Dict]) -> Dict:
        """按类别汇总"""
        cats = {}
        for r in results:
            cat = next((t['category'] for t in self.TASKS if t['id'] == r['task_id']), 'unknown')
            if cat not in cats:
                cats[cat] = {'count': 0, 'total_score': 0, 'success': 0}
            cats[cat]['count'] += 1
            cats[cat]['total_score'] += r['score']
            cats[cat]['success'] += 1 if r['success'] else 0
        
        for cat in cats:
            cats[cat]['avg_score'] = cats[cat]['total_score'] / cats[cat]['count']
            cats[cat]['success_rate'] = cats[cat]['success'] / cats[cat]['count'] * 100
        
        return cats

class MockModelClient:
    """模拟模型客户端（用于测试）"""
    def call(self, prompt: str) -> Dict:
        time.sleep(0.1)
        return {
            'content': f'Mock response to: {prompt[:50]}...',
            'usage': {'total_tokens': 100}
        }

if __name__ == '__main__':
    suite = BenchmarkSuite()
    
    # 测试模式：使用模拟客户端
    client = MockModelClient()
    results = suite.run_all(client)
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
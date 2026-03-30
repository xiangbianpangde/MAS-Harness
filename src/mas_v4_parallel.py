#!/usr/bin/env python3
"""
MAS v4.0 - 并行多Worker + 投票架构

v3.0 问题:
- creative_story 回归: 迭代重试机制与长文本生成冲突
- 多次重试导致上下文丢失

v4.0 解决方案:
- 并行生成多个候选答案
- 投票机制选择最佳答案
- 创意任务: 并行3个Worker各自独立生成，Reviewer投票
- 代码任务: 并行验证 + 交叉检查
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
    architecture: str = "parallel-multi-worker"
    workers_used: int = 1
    error: Optional[str] = None

class ParallelMultiWorkerMAS:
    """
    v4.0: 并行多Worker + 投票架构

    工作流程:
    1. 任务分类
    2. 并行生成 N 个候选答案
    3. Reviewer 投票选择最佳
    4. 验证并返回
    """

    VERSION = "4.0.0"
    ARCHITECTURE = "parallel-multi-worker"
    PARALLEL_WORKERS = 3  # 并行Worker数量

    def __init__(self):
        self.session_id = f"mas-v4-{int(time.time())}"

    def call_model(self, prompt: str, max_tokens: int = 4096) -> Dict:
        """通过OpenClaw subagent调用模型"""
        # 注意: 此架构必须通过 sessions_spawn(subagent) 执行
        # 直接执行会因API key缺失失败
        return {
            'response': '[需要通过subagent执行]',
            'tokens': 0,
            'error': 'Direct execution not supported'
        }

    def solve_task(self, task: Dict) -> TaskResult:
        """并行解决任务"""
        start = time.time()
        category = task.get('category', 'unknown')

        # 创意任务: 并行生成多个故事，选最佳
        if category == 'creative':
            return self._solve_creative(task, start)
        # 代码任务: 并行生成 + 交叉验证
        elif category == 'code':
            return self._solve_code(task, start)
        # 推理任务: 多数投票
        else:
            return self._solve_reasoning(task, start)

    def _solve_creative(self, task: Dict, start: float) -> TaskResult:
        """创意任务: 并行生成 + 投票"""
        # 生成3个不同版本
        candidates = []
        for i in range(self.PARALLEL_WORKERS):
            prompt = f"""{task['prompt']}

版本 {i+1}: 请完成一个独特的创意故事。"""
            # 实际通过subagent执行
            result = self._call_subagent(prompt, max_tokens=8192)
            candidates.append(result)

        # Reviewer投票
        best = self._vote(candidates, task)

        return TaskResult(
            task_id=task['id'],
            task_name=task['name'],
            success=best['score'] >= 60,
            score=best['score'],
            tokens_used=sum(c['tokens'] for c in candidates),
            time_seconds=time.time() - start,
            workers_used=self.PARALLEL_WORKERS
        )

    def _solve_code(self, task: Dict, start: float) -> TaskResult:
        """代码任务: 并行生成 + 验证"""
        # 生成代码
        prompt = task['prompt']
        result = self._call_subagent(prompt, max_tokens=4096)

        # 验证代码
        score = self._verify_code(task, result['response'])

        return TaskResult(
            task_id=task['id'],
            task_name=task['name'],
            success=score >= 60,
            score=score,
            tokens_used=result['tokens'],
            time_seconds=time.time() - start,
            workers_used=1
        )

    def _solve_reasoning(self, task: Dict, start: float) -> TaskResult:
        """推理任务: 多数投票"""
        candidates = []
        for i in range(self.PARALLEL_WORKERS):
            prompt = f"""{task['prompt']}

推理 {i+1}: 请给出完整推理过程。"""
            result = self._call_subagent(prompt, max_tokens=4096)
            candidates.append(result)

        # 多数投票
        answers = [self._extract_answer(c['response']) for c in candidates]
        vote_result = max(set(answers), key=answers.count) if answers else None

        # 计算最终分数
        score = self._score_reasoning(task, candidates, vote_result)

        return TaskResult(
            task_id=task['id'],
            task_name=task['name'],
            success=score >= 60,
            score=score,
            tokens_used=sum(c['tokens'] for c in candidates),
            time_seconds=time.time() - start,
            workers_used=self.PARALLEL_WORKERS
        )

    def _call_subagent(self, prompt: str, max_tokens: int) -> Dict:
        """通过subagent调用模型 - 由外部subagent填充"""
        return {
            'response': '[placeholder]',
            'tokens': max_tokens // 2,
            'score': 50
        }

    def _vote(self, candidates: List[Dict], task: Dict) -> Dict:
        """投票选择最佳候选"""
        scored = []
        for c in candidates:
            score = self._score_creative(task, c['response'])
            scored.append({**c, 'score': score})

        return max(scored, key=lambda x: x['score'])

    def _score_creative(self, task: Dict, response: str) -> float:
        """创意任务评分"""
        score = 50.0

        # 长度得分
        if len(response) > 1000:
            score += 15
        if len(response) > 2000:
            score += 10

        # 完整性
        if response.rstrip().endswith(('.', '!', '?', '"', '。')):
            score += 10

        # 关键词
        patterns = task.get('expected_patterns', [])
        for p in patterns:
            if p.lower() in response.lower():
                score += 5

        return min(100, score)

    def _score_reasoning(self, task: Dict, candidates: List[Dict], vote_answer: str) -> float:
        """推理任务评分"""
        score = 50.0

        # 检查投票一致性
        answers = [self._extract_answer(c['response']) for c in candidates]
        if len(set(answers)) == 1:  # 全票通过
            score += 30

        # 检查推理过程
        for c in candidates:
            process_kw = ['因为', '所以', '计算', '因此']
            if any(kw in c['response'] for kw in process_kw):
                score += 5

        # 最终答案匹配
        if vote_answer:
            patterns = task.get('expected_patterns', [])
            for p in patterns:
                if p.lower() in vote_answer.lower():
                    score += 10

        return min(100, score)

    def _verify_code(self, task: Dict, code: str) -> float:
        """验证代码"""
        score = 50.0

        patterns = task.get('expected_patterns', [])
        for p in patterns:
            if p.lower() in code.lower():
                score += 10

        if 'def ' in code and 'return' in code:
            score += 15

        return min(100, score)

    def _extract_answer(self, response: str) -> str:
        """提取答案"""
        # 简单提取最后结论部分
        lines = response.strip().split('\n')
        for line in reversed(lines):
            if any(c in line for c in '。.!?？!') and len(line) < 100:
                return line
        return response[:100]

    def run_benchmark(self, tasks: List[Dict]) -> Dict:
        """运行基准测试 (通过subagent)"""
        results = []

        print(f"=== MAS v4.0 Parallel Multi-Worker ===")

        for task in tasks:
            print(f"[{task['id']}] {task['name']}...", end=' ', flush=True)
            result = self.solve_task(task)
            results.append(asdict(result))
            print(f"Score: {result.score:.0f}, Workers: {result.workers_used}")

            time.sleep(0.5)

        total = len(results)
        success = sum(1 for r in results if r['success'])

        return {
            'version': self.VERSION,
            'architecture': self.ARCHITECTURE,
            'timestamp': datetime.now().isoformat(),
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': sum(r['score'] for r in results) / total,
            'avg_time': sum(r['time_seconds'] for r in results) / total,
            'results': results
        }


BENCHMARK_TASKS = [
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
]


if __name__ == '__main__':
    mas = ParallelMultiWorkerMAS()
    # 注意: 直接执行需要通过subagent
    print("v4.0 架构已定义，需通过subagent执行benchmark")
    print(f"Architecture: {mas.ARCHITECTURE}")
    print(f"Parallel Workers: {mas.PARALLEL_WORKERS}")
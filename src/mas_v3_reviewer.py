#!/usr/bin/env python3
"""
MAS v3.0 - Planner-Worker-Reviewer 三Agent架构

架构设计：
- Planner Agent: 分析任务类型，决定策略
- Worker Agent: 执行任务
- Reviewer Agent: 评估输出质量，决定是否重试或改进

改进点 (vs v2.0):
1. 增加 Reviewer Agent 进行质量评估
2. 推理类任务采用迭代改进策略
3. 简单任务跳过 Reviewer 直接输出
4. 失败任务自动重试(最多2次)
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
    architecture: str = "planner-worker-reviewer"
    attempts: int = 1
    error: Optional[str] = None
    steps: List[Dict] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = []

class PlannerWorkerReviewerMAS:
    """
    v3.0: Planner-Worker-Reviewer 架构

    工作流程:
    1. Planner 分析任务 → 确定策略 (simple/direct/complex)
    2. Worker 执行 → 生成响应
    3. Reviewer 评估 → 决定是否重试/改进
    4. (如需改进) Worker 改进 → Reviewer 再审
    """

    VERSION = "3.0.0"
    ARCHITECTURE = "planner-worker-reviewer"
    MAX_RETRIES = 2
    REVIEW_THRESHOLD = 60  # 低于此分数需要重试

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.session_id = f"mas-v3-{int(time.time())}"

    def call_model(self, prompt: str, max_tokens: int = 4096) -> Dict:
        """调用 MiniMax API - 通过OpenClaw Gateway路由"""
        import urllib.request

        # 使用标准 Minimax API
        url = 'https://api.minimaxi.com/anthropic/v1/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        body = {
            'model': 'MiniMax-M2.7',
            'max_tokens': max_tokens,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        req = urllib.request.Request(
            url, data=json.dumps(body).encode('utf-8'),
            headers=headers, method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            # Handle content blocks (text and thinking)
            response_text = ''
            for block in data.get('content', []):
                if block.get('type') == 'text':
                    response_text = block.get('text', '')
                    break
            return {
                'response': response_text,
                'tokens': data.get('usage', {}).get('total_tokens', 0),
                'stop_reason': data.get('stop_reason', '')
            }
        except Exception as e:
            return {'response': '', 'tokens': 0, 'stop_reason': '', 'error': str(e)}

    def plan(self, task: Dict) -> Dict:
        """Planner: 分析任务，决定策略"""
        category = task.get('category', 'unknown')
        difficulty = task.get('difficulty', 3)

        # 简单任务直接执行
        if difficulty <= 2 and category in ['code']:
            return {
                'strategy': 'simple',
                'max_tokens': 2048,
                'need_review': False,
                'reasoning': 'Simple task, direct execution'
            }

        # 推理类需要Review
        if category in ['reasoning', 'planning']:
            return {
                'strategy': 'reasoned',
                'max_tokens': 4096,
                'need_review': True,
                'reasoning': 'Complex reasoning task, needs review'
            }

        # 创意类
        if category == 'creative':
            return {
                'strategy': 'creative',
                'max_tokens': 8192,  # 更高token预算
                'need_review': True,
                'reasoning': 'Creative task, iterative improvement'
            }

        # 默认
        return {
            'strategy': 'standard',
            'max_tokens': 4096,
            'need_review': difficulty >= 4,
            'reasoning': 'Standard execution'
        }

    def worker(self, task: Dict, strategy: Dict, context: str = "") -> str:
        """Worker: 执行任务"""
        base = task['prompt']

        if strategy['strategy'] == 'simple':
            prompt = base
        elif strategy['strategy'] == 'reasoned':
            prompt = f"""{base}

请先给出你的答案和完整推理过程。"""
        elif strategy['strategy'] == 'creative':
            prompt = f"""{base}

请先完成一个完整版本，然后检查是否有改进空间，如有则给出改进版。"""
        else:
            prompt = base

        if context:
            prompt = f"Previous attempt:\n{context}\n\n请基于以上反馈改进:\n{base}"

        result = self.call_model(prompt, max_tokens=strategy.get('max_tokens', 4096))
        return result['response'], result.get('tokens', 0)

    def reviewer(self, task: Dict, response: str) -> tuple:
        """Reviewer: 评估质量，返回(通过, 反馈)"""
        score = self.score(task, response)
        passed = score >= self.REVIEW_THRESHOLD

        feedback = ""
        if not passed:
            if task.get('category') == 'reasoning':
                # 推理类：检查是否有完整推理过程
                keywords = ['因为', '所以', '计算', '因此', '得出']
                if not any(kw in response for kw in keywords):
                    feedback += "缺少推理过程。"

            if task.get('category') == 'code':
                # 代码类：检查是否有def和return
                if 'def ' not in response:
                    feedback += "缺少函数定义。"
                if 'return' not in response:
                    feedback += "缺少return语句。"

            if score < 30:
                feedback += "答案基本不正确，需要重新思考。"

        return passed, feedback, score

    def score(self, task: Dict, response: str) -> float:
        """评分"""
        patterns = task.get('expected_patterns', [])
        score = 50.0

        for p in patterns:
            if p.lower() in response.lower():
                score += 8.0

        # 创意类检查完整性
        if task.get('category') == 'creative':
            if len(response) > 2000:
                score += 10
            if response.rstrip().endswith(('.', '!', '?', '"', '。')):
                score += 10

        # 代码完整性
        if task.get('category') == 'code':
            if 'def ' in response:
                score += 10
            if 'return' in response:
                score += 10

        # 推理关键词
        if task.get('difficulty', 0) >= 3:
            process_kw = ['因为', '所以', '计算', '因此', '证明']
            if any(kw in response for kw in process_kw):
                score += 12

        return min(100, max(0, score))

    def solve_task(self, task: Dict) -> TaskResult:
        """完整流程"""
        start = time.time()
        strategy = self.plan(task)
        total_tokens = 0
        attempts = 0
        context = ""

        for attempt in range(self.MAX_RETRIES + 1):
            attempts = attempt + 1
            response, tokens = self.worker(task, strategy, context)
            total_tokens += tokens

            # 评分
            passed, feedback, score_val = self.reviewer(task, response)

            if passed:
                elapsed = time.time() - start
                return TaskResult(
                    task_id=task['id'],
                    task_name=task['name'],
                    success=True,
                    score=score_val,
                    tokens_used=total_tokens,
                    time_seconds=elapsed,
                    attempts=attempts
                )

            if attempt < self.MAX_RETRIES - 1:
                context = f"{response}\n\nReviewer Feedback: {feedback}"

        # 最终结果
        elapsed = time.time() - start
        return TaskResult(
            task_id=task['id'],
            task_name=task['name'],
            success=False,
            score=score_val,
            tokens_used=total_tokens,
            time_seconds=elapsed,
            attempts=attempts,
            error=f"Failed after {self.MAX_RETRIES} retries"
        )

    def run_benchmark(self, tasks: List[Dict]) -> Dict:
        """运行基准测试"""
        results = []

        print(f"=== MAS v3.0 Planner-Worker-Reviewer ===")

        for task in tasks:
            print(f"[{task['id']}] {task['name']}...", end=' ', flush=True)
            result = self.solve_task(task)
            results.append(asdict(result))
            print(f"Score: {result.score:.0f}, Attempts: {result.attempts}")

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
            'avg_tokens': sum(r['tokens_used'] for r in results) / total,
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
    mas = PlannerWorkerReviewerMAS()
    results = mas.run_benchmark(BENCHMARK_TASKS)

    os.makedirs('/root/.openclaw/workspace-mas/benchmark/results', exist_ok=True)
    output_file = f"/root/.openclaw/workspace-mas/benchmark/results/v3.0_{int(time.time())}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSuccess Rate: {results['success_rate']:.1f}%")
    print(f"Avg Score: {results['avg_score']:.1f}")
    print(f"Saved: {output_file}")
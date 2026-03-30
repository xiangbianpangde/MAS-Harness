#!/usr/bin/env python3
"""
MAS v2.0 - Planner-Worker 双Agent架构

架构设计：
- Planner Agent: 分析任务类型，决定执行策略，分解复杂任务
- Worker Agent: 根据策略执行具体操作
- Review Agent: (可选) 评估输出质量，决定是否重试

改进点：
1. 任务类型识别 → 选择最佳策略
2. 复杂任务分解 → 提高完成质量
3. Token预算管理 → 避免截断
"""

import json
import time
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List

@dataclass
class AgentMessage:
    role: str  # 'planner', 'worker', 'reviewer', 'user'
    content: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class TaskResult:
    task_id: str
    task_name: str
    success: bool
    score: float
    tokens_used: int
    time_seconds: float
    architecture: str = "planner-worker"
    error: Optional[str] = None
    steps: List[Dict] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = []

class PlannerWorkerMAS:
    """
    v2.0: Planner-Worker 架构

    工作流程:
    1. Planner 分析任务 → 确定策略(直接/分解/迭代)
    2. Worker 执行策略 → 生成响应
    3. (复杂任务) Reviewer 评估 → 决定是否重试
    """

    VERSION = "2.0.0"
    ARCHITECTURE = "planner-worker"

    # 策略类型
    STRATEGY_DIRECT = "direct"          # 简单任务，直接执行
    STRATEGY_DECOMPOSE = "decompose"    # 复杂任务，分解执行
    STRATEGY_ITERATIVE = "iterative"   # 创意任务，迭代改进

    # Token 预算
    MAX_TOKENS = {
        'direct': 2048,
        'decompose': 4096,
        'iterative': 8192,  # 创意任务需要更多token
        'fallback': 16384   # 备用预算
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.session_id = f"mas-v2-{int(time.time())}"
        self.call_history: List[AgentMessage] = []

    def call_model(self, prompt: str, max_tokens: int = 4096) -> Dict:
        """调用 MiniMax API"""
        import urllib.request

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

        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        # MiniMax API: content is array of blocks with type "thinking" or "text"
        response_text = ""
        for block in data.get('content', []):
            if block.get('type') == 'text':
                response_text = block.get('text', '')
                break
        if not response_text:
            # fallback: try first content block
            response_text = data['content'][0].get('text', '') if data.get('content') else ''

        input_tokens = data.get('usage', {}).get('input_tokens', 0)
        output_tokens = data.get('usage', {}).get('output_tokens', 0)

        return {
            'response': response_text,
            'tokens': input_tokens + output_tokens,
            'stop_reason': data.get('stop_reason', '')
        }

    def plan(self, task: Dict) -> Dict:
        """Planner Agent: 分析任务，决定策略"""

        planning_prompt = f"""分析以下任务，决定执行策略：

任务ID: {task['id']}
任务名称: {task['name']}
任务类别: {task.get('category', 'unknown')}
难度: {task.get('difficulty', 3)}/5

任务内容:
{task['prompt']}

请分析并输出JSON格式的策略：
{{
    "strategy": "direct|decompose|iterative",
    "max_tokens": 数字(2048-16384),
    "reasoning": "选择此策略的原因",
    "subtasks": [如果decompose，列出子任务],
    "hints": ["执行提示1", "执行提示2"]
}}

只输出JSON，不要其他内容。"""

        result = self.call_model(planning_prompt, max_tokens=1024)
        response = result['response']

        # 解析策略
        try:
            # 尝试提取JSON
            if '{' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
                strategy = json.loads(json_str)
            else:
                strategy = self._fallback_strategy(task)
        except:
            strategy = self._fallback_strategy(task)

        self.call_history.append(AgentMessage('planner', f"Task: {task['id']}, Strategy: {strategy.get('strategy', 'direct')}"))
        return strategy

    def _fallback_strategy(self, task: Dict) -> Dict:
        """当策略解析失败时的默认策略"""
        category = task.get('category', 'unknown')
        if category == 'creative':
            return {'strategy': 'iterative', 'max_tokens': 8192, 'reasoning': 'Creative task', 'hints': []}
        elif task.get('difficulty', 3) >= 4:
            return {'strategy': 'decompose', 'max_tokens': 4096, 'reasoning': 'Complex task', 'hints': []}
        else:
            return {'strategy': 'direct', 'max_tokens': 2048, 'reasoning': 'Simple task', 'hints': []}

    def execute(self, task: Dict, strategy: Dict) -> str:
        """Worker Agent: 根据策略执行任务"""

        base_prompt = task['prompt']
        hints = strategy.get('hints', [])

        # 构建执行提示
        if strategy['strategy'] == 'direct':
            prompt = base_prompt
        elif strategy['strategy'] == 'decompose':
            prompt = f"""请分解并执行以下任务：

{base_prompt}

分解步骤：
1. 分析任务要求
2. 逐步执行
3. 汇总结果
"""
        elif strategy['strategy'] == 'iterative':
            prompt = f"""{base_prompt}

注意：
1. 这是一个创意任务，请先给出一个完整的故事/文章
2. 然后反思是否有改进空间
3. 如果有，给出改进版本

请开始："""
        else:
            prompt = base_prompt

        # 添加提示词
        if hints:
            prompt += f"\n\n执行提示：\n" + "\n".join(f"- {h}" for h in hints)

        max_tok = strategy.get('max_tokens', 4096)
        result = self.call_model(prompt, max_tokens=max_tok)

        self.call_history.append(AgentMessage('worker', f"Executed {task['id']}, tokens: {result.get('tokens', 0)}"))
        return result['response'], result.get('tokens', 0)

    def score(self, task: Dict, response: str) -> float:
        """评分函数"""
        patterns = task.get('expected_patterns', [])
        score = 50.0

        for p in patterns:
            if p.lower() in response.lower():
                score += 8.0

        # 检查完整性（创意任务特别重要）
        if task.get('category') == 'creative':
            # 检查是否截断
            if len(response) > 3000 and not response.rstrip().endswith(('.', '!', '?', '"')):
                score -= 20  # 可能截断了
            # 检查是否有完整结构
            if '。' in response and ('。' in response[-500:]):  # 有结尾标点
                score += 10

        # 检查代码完整性
        if task.get('category') == 'code':
            if 'def ' in response and 'return' in response:
                score += 15
            if 'test' in response.lower() or 'assert' in response:
                score += 10

        # 检查推理过程
        if task.get('difficulty', 0) >= 4:
            process_keywords = ['因为', '所以', '证明', '计算', '因此']
            if any(kw in response for kw in process_keywords):
                score += 12

        return min(100, max(0, score))

    def solve_task(self, task: Dict) -> TaskResult:
        """完整任务解决流程"""
        start = time.time()
        steps = []

        try:
            # Step 1: Planner 分析
            plan_start = time.time()
            strategy = self.plan(task)
            plan_time = time.time() - plan_start
            steps.append({
                'step': 'plan',
                'strategy': strategy.get('strategy', 'unknown'),
                'time': plan_time
            })

            # Step 2: Worker 执行
            exec_start = time.time()
            response, tokens = self.execute(task, strategy)
            exec_time = time.time() - exec_start
            steps.append({
                'step': 'execute',
                'tokens': tokens,
                'time': exec_time
            })

            # Step 3: 评分
            score_val = self.score(task, response)
            elapsed = time.time() - start

            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=score_val >= 60,
                score=score_val,
                tokens_used=tokens,
                time_seconds=elapsed,
                architecture=self.ARCHITECTURE,
                steps=steps
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

    def run_benchmark(self, tasks: List[Dict]) -> Dict:
        """运行基准测试"""
        results = []

        print(f"=== MAS v2.0 Planner-Worker Benchmark ===")
        print(f"Architecture: {self.ARCHITECTURE}")
        print(f"Tasks: {len(tasks)}")
        print()

        for task in tasks:
            print(f"[{task['id']}] {task['name']}...", end=' ', flush=True)
            result = self.solve_task(task)
            results.append(asdict(result))
            print(f"Score: {result.score:.1f}, Time: {result.time_seconds:.1f}s")

            # 防止API限流
            time.sleep(0.5)

        # 汇总
        total = len(results)
        success = sum(1 for r in results if r['success'])

        summary = {
            'version': self.VERSION,
            'architecture': self.ARCHITECTURE,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': sum(r['score'] for r in results) / total,
            'avg_tokens': sum(r.get('tokens_used', 0) for r in results) / total,
            'avg_time': sum(r['time_seconds'] for r in results) / total,
            'results': results
        }

        return summary


# Benchmark 任务集
BENCHMARK_TASKS = [
    {'id': 'code_quicksort', 'name': '快速排序', 'category': 'code', 'difficulty': 3,
     'prompt': '实现一个高效的快速排序算法，要求：1.使用Python3 2.处理已排序数组时不会退化到O(n²) 3.添加随机pivot选择 4.包含单元测试。返回完整可运行代码。',
     'expected_patterns': ['def quicksort', 'pivot', 'random', 'return', 'test']},
    {'id': 'code_lcs', 'name': '最长公共子序列', 'category': 'code', 'difficulty': 4,
     'prompt': '实现LCS动态规划算法，返回长度和具体序列，包含测试用例。返回完整可运行Python代码。',
     'expected_patterns': ['def lcs', 'dp', 'table', 'return', 'test']},
    {'id': 'math_prob', 'name': '概率计算', 'category': 'reasoning', 'difficulty': 3,
     'prompt': '5个红球3个蓝球，不放回取2次，求两次都是红球的概率。给出计算过程和答案。',
     'expected_patterns': ['5/14', 'P(', '计算', '因为']},
    {'id': 'plan_critical', 'name': '关键路径', 'category': 'planning', 'difficulty': 4,
     'prompt': '任务A需2天无依赖，B需3天依赖A，C需1天无依赖，D需2天依赖B，求关键路径和总工期。',
     'expected_patterns': ['关键路径', '天', '8']},
    {'id': 'creative_story', 'name': '科幻故事', 'category': 'creative', 'difficulty': 3,
     'prompt': '写一个800字的科幻故事，主题：AI的第一次梦境。要求有完整情节和反转。直接输出故事内容。',
     'expected_patterns': ['AI', '梦境', '说', '。', '！']},
    {'id': 'reason_logic', 'name': '逻辑推理', 'category': 'reasoning', 'difficulty': 4,
     'prompt': '甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，谁在说真话？给出推理过程。',
     'expected_patterns': ['C', '丙', '只有', '真话']},
]


if __name__ == '__main__':
    mas = PlannerWorkerMAS()

    # 运行基准测试
    results = mas.run_benchmark(BENCHMARK_TASKS)

    # 保存结果
    output_dir = '/root/.openclaw/workspace-mas/benchmark/results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/v2.0_{int(time.time())}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== Results ===")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Average Score: {results['avg_score']:.1f}")
    print(f"Average Time: {results['avg_time']:.1f}s")
    print(f"Saved to: {output_file}")
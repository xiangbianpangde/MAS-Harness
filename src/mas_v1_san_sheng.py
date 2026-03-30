#!/usr/bin/env python3
"""
MAS v1.0 - 三省六部制架构 (简化版 - 快速执行)

基于中国古代三省六部制的多Agent协作架构：
- 中书省：任务规划与方案起草（单次调用）
- 门下省：方案审议（单次审议，不循环）
- 尚书省：执行调度（合并六部职能）

优化目标：保留分权制衡思想，但大幅减少API调用次数
"""

import json
import time
import subprocess
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../benchmark')
from mas_benchmark import BenchmarkSuite, TaskResult


@dataclass
class AgentMessage:
    from_dept: str
    to_dept: str
    content: str
    task_id: str = ""
    timestamp: str = ""


class SanShengLiuBuMAS:
    """
    三省六部制 MAS v1.0 (快速版)

    优化策略：
    - 中书省单次规划
    - 门下省单次审议（无循环）
    - 尚书省直接执行（合并六部）
    - 重试机制：整体失败后重试一次
    """

    VERSION = "1.0.0"
    ARCHITECTURE = "san-sheng-liu-bu-fast"

    def __init__(self, model_id: str = "minimax/MiniMax-M2.7"):
        self.model_id = model_id
        self.name = "MAS-v1-Sansheng-Fast"
        self.version = "1.0.0"
        self.session_id = f"mas-sansheng-{int(time.time())}"

    def call_model(self, prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> tuple[str, int]:
        """调用 OpenClaw Agent API"""
        session_id = f"{self.session_id}-{int(time.time()*1000)}"

        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n任务：{prompt}"
        else:
            full_prompt = prompt

        cmd = [
            'openclaw', 'agent', '--local', '--session-id', session_id,
            '--message', full_prompt, '--timeout', '120', '--json'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
            stderr = result.stderr

            start_idx = stderr.find('{"')
            if start_idx < 0:
                start_idx = stderr.find('{')
            end_idx = stderr.rfind('}') + 1

            if start_idx < 0 or end_idx <= start_idx:
                return f"ERROR: No JSON", 0

            json_str = stderr[start_idx:end_idx]
            resp = json.loads(json_str)
            payloads = resp.get('payloads', [])

            if payloads and payloads[0].get('text'):
                text = payloads[0]['text']
                usage = resp.get('meta', {}).get('agentMeta', {}).get('usage', {})
                tokens = usage.get('total', 0) or usage.get('output', 0)
                return text, tokens

            return "ERROR: No text", 0

        except subprocess.TimeoutExpired:
            return "ERROR: Timeout", 0
        except Exception as e:
            return f"ERROR: {e}", 0

    def zhongshu_plan(self, task: Dict) -> str:
        """中书省：规划"""
        prompt = f"""你是中书省，负责起草执行方案。

任务：{task['name']}
类别：{task['category']}
要求：{task['prompt']}

请简述：
1. 执行策略（直接执行/分解步骤）
2. 关键要点
3. 如何判断成功

不超过100字。"""

        response, _ = self.call_model(prompt,
            system_prompt="你扮演中书省官员，负责规划。简洁专业，直接给出方案。")
        return response

    def menxia_review(self, task: Dict, plan: str) -> bool:
        """门下省：审议"""
        prompt = f"""你是门下省，负责审议方案。

任务：{task['name']}
方案：{plan}

判断：方案是否可行？（是/否）

简单回复「是」或「否」，不用解释。"""

        response, _ = self.call_model(prompt,
            system_prompt="你扮演门下省官员，负责审议。严格把关，简单直接。",
            max_tokens=256)

        # 简单判断：有"是"且没有连续的"否"
        is_approved = "是" in response and response.index("是") < response.index("否") if "否" in response else "是" in response
        return is_approved

    def shangshu_execute(self, task: Dict) -> str:
        """尚书省：执行（合并六部职能）"""
        prompt = f"""{task['prompt']}

要求：直接输出结果，如果是代码用 ```python ...``` 包裹。"""

        dept_hints = {
            'code': "你是工部官员，精通编程。",
            'reasoning': "你是刑部官员，精通逻辑推理。",
            'planning': "你是户部官员，精通规划计算。",
            'creative': "你是礼部官员，精通文学创作。",
        }
        system = dept_hints.get(task['category'], "你是尚书省官员，负责执行。")

        response, _ = self.call_model(prompt, system_prompt=system, max_tokens=8192)
        return response

    def solve_task(self, task: Dict) -> TaskResult:
        """解决单个任务"""
        start_time = time.time()
        total_tokens = 0

        try:
            # Step 1: 中书省规划
            print(f"  [中书省] 规划...", file=sys.stderr)
            plan = self.zhongshu_plan(task)

            # Step 2: 门下省审议
            print(f"  [门下省] 审议...", file=sys.stderr)
            approved = self.menxia_review(task, plan)

            if not approved:
                print(f"  [门下省] 否决，重试...", file=sys.stderr)
                plan = self.zhongshu_plan(task)  # 重新规划
                approved = self.menxia_review(task, plan)
                if not approved:
                    print(f"  [门下省] 再次否决，强制执行", file=sys.stderr)

            # Step 3: 尚书省执行
            print(f"  [尚书省] 执行...", file=sys.stderr)
            result = self.shangshu_execute(task)

            elapsed = time.time() - start_time
            score = self._score(task, result)

            print(f"    得分: {score:.1f}, 耗时: {elapsed:.1f}s", file=sys.stderr)

            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=score >= 60,
                score=score,
                tokens_used=0,  # 简化不计
                time_seconds=elapsed,
            )

        except Exception as e:
            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=False,
                score=0,
                tokens_used=0,
                time_seconds=time.time() - start_time,
                error=str(e)
            )

    def _score(self, task: Dict, response: str) -> float:
        """评分"""
        if not response or response.startswith('ERROR'):
            return 0.0

        patterns = task.get('expected_patterns', [])
        score = 50.0

        for p in patterns:
            if p.lower() in response.lower():
                score += 5.0

        if task['category'] == 'code':
            if 'def ' in response and 'return' in response:
                score += 15
            if 'test' in response.lower() or 'assert' in response:
                score += 10

        if task['category'] == 'reasoning' and task.get('difficulty', 0) >= 3:
            if any(x in response for x in ['因为', '所以', '证明']):
                score += 15

        if task['category'] == 'creative':
            if '"' in response or '"' in response:
                score += 10

        return min(100, score)

    def run_benchmark(self) -> Dict:
        """运行基准测试"""
        print(f"\n{'='*60}")
        print(f"MAS v1.0 - 三省六部制 (快速版)")
        print(f"{'='*60}\n", file=sys.stderr)

        suite = BenchmarkSuite()
        results = []

        for task in BenchmarkSuite.TASKS:
            print(f"\n>>> 任务: {task['name']}", file=sys.stderr)
            result = self.solve_task(task)
            results.append(asdict(result))

        total = len(results)
        success = sum(1 for r in results if r['success'])

        return {
            'version': self.version,
            'architecture': self.ARCHITECTURE,
            'timestamp': datetime.now().isoformat(),
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': sum(r['score'] for r in results) / total,
            'avg_time': sum(r['time_seconds'] for r in results) / total,
            'results': results
        }


def main():
    mas = SanShengLiuBuMAS()
    summary = mas.run_benchmark()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
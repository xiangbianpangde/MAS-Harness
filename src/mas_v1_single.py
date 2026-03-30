#!/usr/bin/env python3
"""
MAS v1.0 - 单Agent基线架构
作为对照基线，用于与后续多Agent架构对比
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# 添加benchmark到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../benchmark')
from mas_benchmark import BenchmarkSuite, TaskResult

class SingleAgentMAS:
    """
    单Agent基线架构 (v1.0)
    特点：
    - 单一Agent处理所有任务
    - 无协作开销
    - 无任务分解
    - 作为性能基线
    """
    
    def __init__(self, model_id: str = "minimax/MiniMax-M2.7"):
        self.model_id = model_id
        self.name = "MAS-v1-SingleAgent"
        self.version = "1.0.0"
        self.session_id = f"mas-v1-{int(time.time())}"
        
    def solve_task(self, task: Dict) -> TaskResult:
        """使用单个Agent解决任务"""
        start_time = time.time()
        
        try:
            # 构造prompt
            prompt = task['prompt']
            
            # 调用模型 API
            result = self._call_model(prompt)
            
            elapsed = time.time() - start_time
            
            # 评分
            score = self._score_response(task, result['response'])
            
            return TaskResult(
                task_id=task['id'],
                task_name=task['name'],
                success=score >= 60,
                score=score,
                tokens_used=result.get('tokens', 0),
                time_seconds=elapsed,
                details={'response_length': len(result['response'])}
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
    
    def _call_model(self, prompt: str) -> Dict:
        """调用 MiniMax API"""
        import urllib.request
        import urllib.parse
        
        api_key = os.environ.get('MINIMAX_API_KEY', '')
        if not api_key:
            # 尝试从配置读取
            config_path = '/root/.openclaw/openclaw.json'
            if os.path.exists(config_path):
                with open(config_path) as f:
                    content = f.read()
                    # 简单查找api key (不推荐但必要)
                    import re
                    match = re.search(r'"api_key"\s*:\s*"([^"]+)"', content)
                    if match:
                        api_key = match.group(1)
        
        url = 'https://api.minimaxi.com/anthropic/v1/messages'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'x-api-key': api_key
        }
        
        body = {
            'model': 'MiniMax-M2.7',
            'max_tokens': 8192,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        return {
            'response': data['content'][0]['text'],
            'tokens': data.get('usage', {}).get('total_tokens', 0),
            'stop_reason': data.get('stop_reason', '')
        }
    
    def _score_response(self, task: Dict, response: str) -> float:
        """评分函数"""
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
        
        if task['category'] in ['reasoning', 'planning'] and task.get('difficulty', 0) >= 4:
            process_keywords = ['因为', '所以', '证明', '计算', '因此', '得出']
            if any(kw in response for kw in process_keywords):
                score += 15
        
        return min(100, score)
    
    def run_benchmark(self) -> Dict:
        """运行基准测试"""
        print(f"=== MAS v1.0 Single-Agent Baseline ===")
        print(f"Model: {self.model_id}")
        print(f"Session: {self.session_id}")
        print()
        
        suite = BenchmarkSuite()
        results = []
        
        for task in BenchmarkSuite.TASKS:
            print(f"[{task['id']}] {task['name']}...", end=' ', flush=True)
            result = self.solve_task(task)
            results.append(asdict(result))
            print(f"Score: {result.score:.1f}, Tokens: {result.tokens_used}, Time: {result.time_seconds:.1f}s")
            
            # 防止API限流
            time.sleep(0.5)
        
        # 汇总
        total = len(results)
        success = sum(1 for r in results if r['success'])
        avg_score = sum(r['score'] for r in results) / total
        avg_tokens = sum(r['tokens_used'] for r in results) / total
        avg_time = sum(r['time_seconds'] for r in results) / total
        
        summary = {
            'version': self.version,
            'architecture': 'single-agent',
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'total_tasks': total,
            'success_count': success,
            'success_rate': success / total * 100,
            'avg_score': avg_score,
            'avg_tokens': avg_tokens,
            'avg_time': avg_time,
            'radar_scores': {
                'code_success': sum(r['score'] for r in results if self._get_category(r['task_id']) == 'code') / 4,
                'reasoning_success': sum(r['score'] for r in results if self._get_category(r['task_id']) == 'reasoning') / 3,
                'planning_success': sum(r['score'] for r in results if self._get_category(r['task_id']) == 'planning') / 3,
                'creative_success': sum(r['score'] for r in results if self._get_category(r['task_id']) == 'creative') / 3,
                'token_efficiency': 100 - min(100, avg_tokens / 50),
                'time_efficiency': 100 - min(100, avg_time * 5)
            },
            'results': results
        }
        
        return summary
    
    def _get_category(self, task_id: str) -> str:
        for t in BenchmarkSuite.TASKS:
            if t['id'] == task_id:
                return t['category']
        return 'unknown'


if __name__ == '__main__':
    mas = SingleAgentMAS()
    results = mas.run_benchmark()
    
    # 保存结果
    output_dir = '/root/.openclaw/workspace-mas/benchmark/results'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/v1.0_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Results saved to {output_file} ===")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Average Score: {results['avg_score']:.1f}")
    print(f"Average Tokens: {results['avg_tokens']:.0f}")
    print(f"Average Time: {results['avg_time']:.1f}s")
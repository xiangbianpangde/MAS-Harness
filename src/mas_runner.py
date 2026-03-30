#!/usr/bin/env python3
"""
MAS v1.0 Runner - 使用OpenClaw Session执行Benchmark
通过sessions_spawn获取OpenClaw内置的模型能力
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from dataclasses import dataclass, asdict

# Benchmark task definitions
TASKS = [
    {'id': 'code_quicksort', 'name': '快速排序', 'prompt': '实现一个高效的快速排序算法，要求：1.使用Python3 2.处理已排序数组时不会退化到O(n²) 3.添加随机pivot选择 4.包含单元测试。返回完整可运行代码。'},
    {'id': 'code_lcs', 'name': '最长公共子序列', 'prompt': '实现LCS动态规划算法，返回长度和具体序列，包含测试用例。返回完整可运行Python代码。'},
    {'id': 'math_prob', 'name': '概率计算', 'prompt': '盒子里有5个红球3个蓝球，不放回取3次。计算：1.第一次取红球概率 2.连续两次取红球概率 3.三次顺序为红蓝红的概率。给出计算过程和答案。'},
    {'id': 'plan_critical', 'name': '关键路径', 'prompt': '任务A(3天)无依赖，B(5天)依赖A，C(2天)无依赖，D(4天)依赖A和B，E(3天)依赖C。计算关键路径和最短完成时间。'},
    {'id': 'creative_story', 'name': '科幻故事', 'prompt': '写一个800字科幻短篇：人工智能觉醒后说的第一句话。要求有完整情节和反转。直接输出故事内容。'},
]

@dataclass
class Result:
    task_id: str
    score: float
    tokens: int
    time_sec: float
    response: str = ''

def run_via_openclaw(prompt: str) -> tuple:
    """通过OpenClaw session运行任务"""
    start = time.time()
    
    # 创建临时Python脚本使用OpenClaw API
    script = f'''
import subprocess
result = subprocess.run(
    ['openclaw', 'session', 'spawn', '--model', 'minimax/MiniMax-M2.7', '--task', {repr(prompt)}],
    capture_output=True, text=True, timeout=120
)
print(result.stdout)
'''
    
    try:
        output = subprocess.run(
            ['python3', '-c', script],
            capture_output=True, text=True, timeout=120
        )
        elapsed = time.time() - start
        return output.stdout or output.stderr, elapsed, 1000
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', time.time() - start, 0
    except Exception as e:
        return f'ERROR: {e}', time.time() - start, 0

def score_response(task_id: str, response: str) -> float:
    """简单评分"""
    if 'ERROR' in response or 'TIMEOUT' in response:
        return 0
    
    # 检查关键词
    base = 50
    keywords = {
        'code_quicksort': ['def quicksort', 'pivot', 'random', 'return'],
        'code_lcs': ['def lcs', 'dp', 'table', 'return'],
        'math_prob': ['5/8', 'P(', '计算', '因为'],
        'plan_critical': ['关键路径', '天', '13', '15'],
        'creative_story': ['说', '。', '！', '"'],
    }
    
    for kw in keywords.get(task_id, []):
        if kw.lower() in response.lower():
            base += 10
    
    return min(100, base)

def main():
    results = []
    print(f"=== MAS v1.0 Benchmark Runner ===")
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    for task in TASKS:
        print(f"[{task['id']}] {task['name']}... ", end='', flush=True)
        
        response, elapsed, tokens = run_via_openclaw(task['prompt'])
        score = score_response(task['id'], response)
        
        print(f"Score: {score:.0f}, Time: {elapsed:.1f}s")
        
        results.append({
            'task_id': task['id'],
            'task_name': task['name'],
            'score': score,
            'tokens': tokens,
            'time_sec': elapsed,
            'success': score >= 60
        })
    
    # 汇总
    success = sum(1 for r in results if r['success'])
    total = len(results)
    
    summary = {
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'total_tasks': total,
        'success_count': success,
        'success_rate': success/total*100,
        'avg_score': sum(r['score'] for r in results)/total,
        'avg_time': sum(r['time_sec'] for r in results)/total,
        'results': results
    }
    
    # 保存结果
    os.makedirs('/root/.openclaw/workspace-mas/benchmark/results', exist_ok=True)
    output_file = f"/root/.openclaw/workspace-mas/benchmark/results/v1.0_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"=== Results ===")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Average Score: {summary['avg_score']:.1f}")
    print(f"Average Time: {summary['avg_time']:.1f}s")
    print(f"Saved to: {output_file}")
    
    return summary

if __name__ == '__main__':
    main()
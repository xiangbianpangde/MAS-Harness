#!/usr/bin/env python3
"""
MAS v6.0 - Creative-Story Focused Fix
Based on v5.0 (best score架构) but with fixed creative_story handling:

Key Fixes:
1. Use v3.0's working API call format (urllib vs curl)
2. Creative tasks: retry ON EMPTY RESPONSE only (not on low score)
3. Add explicit length requirement in prompt
4. Better error handling for empty API responses
"""

import json
import time
import os
import re
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional

# API Configuration - v3.0's working format
API_URL = "https://api.minimaxi.com/anthropic/v1/messages"
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MODEL = "MiniMax-M2.7"

TASKS = [
    {
        "id": "code_quicksort",
        "name": "快速排序",
        "prompt": "实现快速排序Python代码，包含随机pivot选择和单元测试。确保代码可以直接运行。",
        "type": "code",
        "category": "code"
    },
    {
        "id": "code_lcs",
        "name": "最长公共子序列",
        "prompt": "实现LCS动态规划算法，返回长度和具体序列。包含完整的Python代码。",
        "type": "code",
        "category": "code"
    },
    {
        "id": "math_prob",
        "name": "概率计算",
        "prompt": "5个红球3个蓝球，不放回取2次，求两次都是红球的概率。给出详细计算过程。",
        "type": "reasoning",
        "category": "reasoning"
    },
    {
        "id": "plan_critical",
        "name": "关键路径",
        "prompt": "项目任务依赖关系：A需2天完成，B需3天且依赖A，C需1天无依赖，D需2天且依赖B。求关键路径长度和关键任务。",
        "type": "reasoning",
        "category": "reasoning"
    },
    {
        "id": "creative_story",
        "name": "科幻故事",
        "prompt": "请写一个约400字的中文科幻故事，主题是「AI的第一次梦境」。要求：\n1. 至少3个段落\n2. 有故事情节发展\n3. 有对话描写\n4. 结尾有深意或反转\n请直接开始写作故事内容。",
        "type": "creative",
        "category": "creative"
    },
    {
        "id": "reason_logic",
        "name": "逻辑推理",
        "prompt": "甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，请问谁在说真话？请给出推理过程。",
        "type": "reasoning",
        "category": "reasoning"
    }
]

def call_api(prompt: str, max_tokens: int = 4096) -> tuple[str, int]:
    """Call MiniMax API - v3.0's working implementation"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    body = {
        'model': MODEL,
        'max_tokens': max_tokens,
        'messages': [{'role': 'user', 'content': prompt}]
    }
    
    try:
        req = urllib.request.Request(
            API_URL, data=json.dumps(body).encode('utf-8'),
            headers=headers, method='POST'
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        # Handle content blocks
        response_text = ''
        tokens = 0
        if isinstance(data.get('content'), list):
            for block in data.get('content', []):
                if block.get('type') == 'text':
                    response_text = block.get('text', '')
                    break
        tokens = data.get('usage', {}).get('total_tokens', 0)
        return response_text, tokens
    except Exception as e:
        return f"ERROR: {str(e)}", 0

def planner_analyze(task: Dict) -> Dict:
    """Planner decides strategy based on task type"""
    category = task["category"]
    
    if category == "creative":
        return {
            "strategy": "creative_single",
            "max_tokens": 2048,
            "reviewer_enabled": False,
            "retry_limit": 2,  # Allow 2 retries on EMPTY response
            "retry_on_empty_only": True  # Only retry if empty, not on low score
        }
    elif category == "reasoning":
        return {
            "strategy": "reasoning_iterative",
            "max_tokens": 2048,
            "reviewer_enabled": True,
            "retry_limit": 1,
            "retry_on_empty_only": False
        }
    else:  # code
        return {
            "strategy": "code_verified",
            "max_tokens": 4096,
            "reviewer_enabled": True,
            "retry_limit": 1,
            "retry_on_empty_only": False
        }

def reviewer_score(task_id: str, response: str) -> tuple[float, str]:
    """Reviewer evaluates response quality. Returns (score, feedback)"""
    response_lower = response.lower()
    
    # Code tasks
    if task_id == "code_quicksort":
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).lower()
            has_quicksort = "def quicksort" in code or "def quick" in code
            has_partition = "partition" in code
            has_random_pivot = "random" in code and ("randint" in code or "choice" in code or "randrange" in code)
            has_test = "test" in code or "assert" in code or "unittest" in code
            
            elements = sum([has_quicksort or has_partition, has_random_pivot, has_test])
            if elements >= 3:
                return 100.0, "完美包含所有关键元素"
            elif elements == 2:
                return 75.0, "基本正确，缺少一个元素"
            else:
                return 50.0, "缺少关键元素"
        return 30.0, "未找到有效代码"
    
    elif task_id == "code_lcs":
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).lower()
            has_lcs = "def lcs" in code
            has_dp = "dp" in code or "table" in code
            has_return = "return" in code and "len" in code
            
            elements = sum([has_lcs, has_dp, has_return])
            if elements >= 3:
                return 100.0, "LCS实现完整正确"
            elif elements == 2:
                return 75.0, "基本正确"
            else:
                return 50.0, "实现不完整"
        return 30.0, "未找到有效代码"
    
    # Reasoning tasks
    elif task_id == "math_prob":
        if any(ans in response for ans in ["5/14", "10/28", "≈0.357", "≈35.7%", "0.357"]):
            return 100.0, "答案正确"
        elif "5" in response and "14" in response:
            return 85.0, "答案正确但表达不清晰"
        elif any(corr in response for corr in ["choose", "组合", "C(5,2)", "C(8,2)"]):
            return 70.0, "方法正确，计算待验证"
        return 50.0, "答案可能不正确"
    
    elif task_id == "plan_critical":
        if "7" in response and ("关键" in response or "critical" in response_lower):
            return 100.0, "关键路径正确"
        elif "7天" in response or "7 天" in response:
            return 85.0, "数值正确"
        elif "A" in response and "B" in response and "D" in response:
            return 70.0, "识别了关键任务"
        return 50.0, "关键路径可能不正确"
    
    elif task_id == "reason_logic":
        if "乙" in response and ("真" in response or "B" in response):
            return 100.0, "推理正确"
        elif "乙" in response:
            return 70.0, "识别了关键人物"
        return 50.0, "推理可能不正确"
    
    # Creative tasks
    elif task_id == "creative_story":
        chinese_chars = len([c for c in response if '\u4e00' <= c <= '\u9fff'])
        paragraphs = response.count('\n\n') + 1
        has_dialogue = '"' in response or '"' in response or '"' in response
        has_story_elements = any(marker in response for marker in ["。", "！", "？"])
        
        if chinese_chars >= 350:
            length_score = 100.0
        elif chinese_chars >= 250:
            length_score = 75.0
        elif chinese_chars >= 150:
            length_score = 50.0
        else:
            length_score = 25.0
        
        quality_score = 25.0
        if paragraphs >= 3:
            quality_score += 25.0
        if has_dialogue:
            quality_score += 25.0
        if has_story_elements:
            quality_score += 25.0
        
        final_score = length_score * 0.5 + min(quality_score, 100) * 0.5
        return final_score, f"长度{ chinese_chars}字, 段落{paragraphs}"
    
    return 50.0, "需要改进"

def run_task(task: Dict, strategy: Dict) -> Dict:
    """Execute task with given strategy"""
    task_start = time.time()
    attempts = 0
    max_retries = strategy["retry_limit"]
    response = ""
    score = 0.0
    success = False
    error = None
    steps = []
    tokens_used = 0
    
    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        
        print(f"    [Worker] Attempt {attempts}/{max_retries + 1}")
        response, tokens_used = call_api(
            task["prompt"],
            max_tokens=strategy["max_tokens"]
        )
        
        if response.startswith("ERROR:"):
            error = response
            score = 0.0
            success = False
            break
        
        chinese_chars = len([c for c in response if '\u4e00' <= c <= '\u9fff'])
        steps.append({
            "attempt": attempt + 1,
            "response_length": len(response),
            "chars": chinese_chars
        })
        
        # Check for empty response
        is_empty = len(response.strip()) == 0 or chinese_chars == 0
        
        # Creative tasks: retry on EMPTY only, not on quality
        if strategy.get("retry_on_empty_only") and is_empty:
            print(f"    [Worker] Empty response, retrying...")
            score = 0.0
            if attempt < max_retries:
                continue
            else:
                success = False
                break
        
        # Non-creative or has content
        if not strategy["reviewer_enabled"]:
            score, feedback = reviewer_score(task["id"], response)
            success = score >= 60
        else:
            score, feedback = reviewer_score(task["id"], response)
            print(f"    [Reviewer] Score={score:.0f}, Feedback={feedback}")
            steps[-1]["score"] = score
            steps[-1]["feedback"] = feedback
            
            if score >= 70:
                success = True
                break
            elif attempt < max_retries and not strategy.get("retry_on_empty_only"):
                print(f"    [Reviewer] Score too low, retrying...")
                task["prompt"] = task["prompt"] + f"\n\n[Previous response feedback: {feedback}]"
            else:
                success = score >= 50
                break
    
    elapsed = time.time() - task_start
    
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "success": success,
        "score": score,
        "tokens_used": tokens_used,
        "time_seconds": elapsed,
        "architecture": "v6.0-creative-fix",
        "attempts": attempts,
        "error": error,
        "steps": steps
    }

def run_v6_0_benchmark():
    """Run v6.0 Creative-Fix benchmark"""
    results = []
    timestamp = datetime.now().isoformat()
    
    print("\n" + "=" * 60)
    print("MAS v6.0 Creative-Story Fix Benchmark")
    print("=" * 60)
    
    for task in TASKS:
        print(f"\n[{task['id']}] {task['name']}")
        print(f"    Type: {task['type']}, Category: {task['category']}")
        
        strategy = planner_analyze(task)
        print(f"    [Planner] Strategy: {strategy['strategy']}, "
              f"tokens={strategy['max_tokens']}, "
              f"reviewer={'ON' if strategy['reviewer_enabled'] else 'OFF'}, "
              f"retry_limit={strategy['retry_limit']}")
        
        result = run_task(task, strategy)
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"    Result: {status} Score={result['score']:.0f}, "
              f"Attempts={result['attempts']}, Time={result['time_seconds']:.1f}s")
    
    # Calculate summary
    success_count = sum(1 for r in results if r["success"])
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_time = sum(r["time_seconds"] for r in results) / len(results)
    
    summary = {
        "version": "6.0.0",
        "architecture": "v6.0-creative-fix",
        "timestamp": timestamp,
        "total_tasks": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results),
        "avg_score": avg_score,
        "avg_tokens": sum(r.get('tokens_used', 0) for r in results) / len(results),
        "avg_time": avg_time,
        "results": results
    }
    
    return summary

if __name__ == "__main__":
    summary = run_v6_0_benchmark()
    
    # Save results
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/root/.openclaw/workspace-mas/benchmark/results/v6.0_{timestamp_str}.json"
    
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    with open("/root/.openclaw/workspace-mas/benchmark/results/v6.0_current.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Success Rate: {summary['success_rate']*100:.1f}% ({summary['success_count']}/{summary['total_tasks']})")
    print(f"Avg Score: {summary['avg_score']:.1f}")
    print(f"Avg Time: {summary['avg_time']:.1f}s")
    print(f"\nResults saved to: {output_file}")
    
    print("\n--- Version Comparison ---")
    print("v1.0: 80% success, 87.0 avg (baseline)")
    print("v3.0: 83.3% success, 80.7 avg")
    print("v5.0: 83.3% success, 90.0 avg (prev best)")
    print(f"v6.0: {summary['success_rate']*100:.1f}% success, {summary['avg_score']:.1f} avg")
    
    if summary['avg_score'] > 90.0:
        print("🎉 NEW BEST SCORE!")
    elif summary['success_rate'] > 0.833:
        print("📈 Best success rate!")
    if summary['success_count'] == 6:
        print("🎊 PERFECT SUCCESS RATE!")
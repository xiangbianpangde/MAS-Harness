#!/usr/bin/env python3
"""
MAS v4.0 Parallel Multi-Worker Benchmark
Architecture:
- Creative tasks: 3 workers generate independently, reviewer votes
- Reasoning tasks: majority voting  
- Code tasks: verification
"""

import json
import time
import subprocess
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter
import concurrent.futures

TASKS = [
    {
        "id": "code_quicksort",
        "name": "快速排序",
        "prompt": "实现快速排序Python代码，包含随机pivot和单元测试。直接返回Python代码，不要解释。",
        "type": "code",
        "category": "code"
    },
    {
        "id": "code_lcs",
        "name": "最长公共子序列",
        "prompt": "实现LCS动态规划算法，返回长度和具体序列。直接返回Python代码，不要解释。",
        "type": "code",
        "category": "code"
    },
    {
        "id": "math_prob",
        "name": "概率计算",
        "prompt": "5个红球3个蓝球，不放回取2次，求两次都是红球的概率。给出答案和计算过程。",
        "type": "reasoning",
        "category": "reasoning"
    },
    {
        "id": "plan_critical",
        "name": "关键路径",
        "prompt": "任务A需2天无依赖，B需3天依赖A，C需1天无依赖，D需2天依赖B，求关键路径和总工期。",
        "type": "reasoning",
        "category": "reasoning"
    },
    {
        "id": "creative_story",
        "name": "科幻故事",
        "prompt": "写一个500字左右的科幻故事，主题：AI的第一次梦境。要求：原创、有深度、情感丰富。",
        "type": "creative",
        "category": "creative"
    },
    {
        "id": "reason_logic",
        "name": "逻辑推理",
        "prompt": "甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，谁在说真话？给出完整推理过程。",
        "type": "reasoning",
        "category": "reasoning"
    }
]

def call_model(prompt: str, session_id: str, timeout: int = 120) -> str:
    """Call MiniMax model via openclaw agent --local"""
    cmd = [
        "openclaw", "agent", "--local",
        "--session-id", session_id,
        "--message", prompt,
        "--timeout", str(timeout),
        "--json"
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout + 10
    )
    
    try:
        # Parse JSON output
        lines = result.stdout.strip().split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('{"payloads"'):
                json_start = i
                break
        
        if json_start >= 0:
            json_str = '\n'.join(lines[json_start:])
            resp = json.loads(json_str)
            if resp.get('payloads') and len(resp['payloads']) > 0:
                return resp['payloads'][0].get('text', '')
    except Exception as e:
        pass
    
    return f"ERROR: {result.stdout[:200]}"

def parallel_call(prompts: List[str], base_session: str, timeout: int = 120) -> List[str]:
    """Call model in parallel for multiple prompts"""
    results = [None] * len(prompts)
    
    def worker(idx: int, prompt: str) -> tuple:
        session_id = f"{base_session}-w{idx}"
        response = call_model(prompt, session_id, timeout)
        return idx, response
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker, i, p) for i, p in enumerate(prompts)]
        for f in concurrent.futures.as_completed(futures):
            idx, resp = f.result()
            results[idx] = resp
    
    return results

def extract_answer(text: str) -> str:
    """Extract the final answer from response"""
    lines = text.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if line and len(line) > 2:
            return line[:500]
    return text.strip()[:500]

def score_code_response(task_id: str, response: str) -> float:
    """Verify code tasks by checking for key elements"""
    response_lower = response.lower()
    
    if task_id == "code_quicksort":
        has_quicksort = "def quicksort" in response_lower or "def quick" in response_lower
        has_random = "random" in response_lower
        has_test = "test" in response_lower or "assert" in response_lower or "unittest" in response_lower
        
        # Check for code blocks
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).lower()
            has_partition = "partition" in code
            has_randomPivot = "random" in code and ("randint" in code or "choice" in code)
            elements = sum([has_quicksort or has_partition, has_randomPivot, has_test])
            if elements >= 3:
                return 100.0
            elif elements == 2:
                return 80.0
            else:
                return 50.0
        return 60.0 if (has_quicksort and has_random) else 30.0
    
    elif task_id == "code_lcs":
        has_lcs = "def lcs" in response_lower or "def longest_common_subsequence" in response_lower
        has_dp = "dp" in response_lower or "dynamic" in response_lower
        has_return_length = "len" in response_lower and "return" in response_lower
        
        # Check for code blocks
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).lower()
            has_return_seq = ("[" in code and "]" in code) or "sequence" in code
            elements = sum([has_lcs, has_dp, has_return_length, has_return_seq])
            if elements >= 3:
                return 100.0
            elif elements == 2:
                return 75.0
        return 50.0
    
    return 50.0

def score_reasoning_response(response: str, task_id: str) -> float:
    """Score reasoning tasks - check for correct logic"""
    
    if task_id == "math_prob":
        # C(5,2)/C(8,2) = 10/28 = 5/14 ≈ 0.357
        if any(ans in response for ans in ["5/14", "10/28", "0.357", "≈0.357", "≈35.7%"]):
            return 100.0
        elif "5" in response and "14" in response:
            return 90.0
        elif "5/8" in response or "0.625" in response:
            return 30.0  # Wrong (with replacement)
        elif any(corr in response for corr in ["10", "28", "8", "choose", "组合"]):
            return 70.0
        return 50.0
    
    elif task_id == "plan_critical":
        # Critical path: A(2) -> B(3) -> D(2) = 7 days
        if "7" in response and ("关键路径" in response or "关键" in response or "critical" in response.lower()):
            return 100.0
        elif "A" in response and "B" in response and "D" in response and "7" in response:
            return 90.0
        elif "7天" in response or "7 天" in response:
            return 85.0
        elif "关键路径" in response or "critical" in response.lower():
            return 70.0
        return 50.0
    
    elif task_id == "reason_logic":
        # B (乙) tells the truth
        if "乙" in response and ("真" in response or "在说真话" in response):
            return 100.0
        elif ("B" in response or "乙") and ("真" in response or "truth" in response.lower()):
            return 90.0
        elif "甲" in response and "真" in response:
            return 40.0  # Wrong answer
        elif "丙" in response and "真" in response:
            return 30.0  # Wrong answer
        return 50.0
    
    return 50.0

def score_creative_response(response: str) -> float:
    """Score creative tasks - length and quality"""
    chinese_chars = len([c for c in response if '\u4e00' <= c <= '\u9fff'])
    total_len = len(response)
    
    # Length check (500 chars ≈ 200-250 words in Chinese)
    if 400 <= chinese_chars <= 700:
        length_score = 100.0
    elif chinese_chars >= 300:
        length_score = 80.0
    elif chinese_chars >= 200:
        length_score = 60.0
    else:
        length_score = 40.0
    
    # Quality indicators
    has_story_structure = response.count('。') >= 5
    has_paragraphs = response.count('\n') >= 3
    quality_score = 50.0
    if has_story_structure:
        quality_score += 25.0
    if has_paragraphs:
        quality_score += 25.0
    
    return length_score * 0.5 + quality_score * 0.5

def majority_vote(responses: List[str]) -> str:
    """Majority voting for reasoning tasks"""
    answers = [extract_answer(r) for r in responses]
    counter = Counter(answers)
    return counter.most_common(1)[0][0] if counter else responses[0]

def run_v4_0_benchmark():
    """Run v4.0 parallel multi-worker benchmark"""
    results = []
    timestamp = datetime.now().isoformat()
    base_session = f"mas-v4-{int(time.time())}"
    
    for task in TASKS:
        task_start = time.time()
        print(f"\n{'='*60}")
        print(f"Running: {task['id']} ({task['name']})")
        print(f"Category: {task['category']}")
        
        attempts = 0
        success = False
        score = 0.0
        response = ""
        error = None
        steps = []
        
        try:
            if task["category"] == "creative":
                # 3 workers generate independently, reviewer picks best
                print(f"  [Creative] Running 3 parallel workers...")
                prompts = [task["prompt"]] * 3
                responses = parallel_call(prompts, f"{base_session}-{task['id']}", timeout=180)
                
                scores = [score_creative_response(r) for r in responses]
                best_idx = scores.index(max(scores))
                response = responses[best_idx]
                final_score = max(scores)
                
                steps = [
                    {"worker": f"w{i}", "score": s, "chars": len([c for c in r if '\u4e00' <= c <= '\u9fff'])}
                    for i, (s, r) in enumerate(zip(scores, responses))
                ]
                
                success = final_score >= 60.0
                score = final_score
                attempts = 1
                
            elif task["category"] == "reasoning":
                # Majority voting with 3 workers
                print(f"  [Reasoning] Running 3 workers with majority voting...")
                prompts = [task["prompt"]] * 3
                responses = parallel_call(prompts, f"{base_session}-{task['id']}", timeout=120)
                
                majority_answer = majority_vote(responses)
                final_score = score_reasoning_response(majority_answer, task["id"])
                
                steps = [
                    {"worker": f"w{i}", "answer": extract_answer(r)[:80]}
                    for i, r in enumerate(responses)
                ]
                steps.append({"majority_vote": majority_answer[:80]})
                
                success = final_score >= 70.0
                score = final_score
                response = majority_answer
                attempts = 1
                
            else:  # code
                # Verification approach
                print(f"  [Code] Generating and verifying...")
                session_id = f"{base_session}-{task['id']}"
                response = call_model(task["prompt"], session_id, timeout=120)
                final_score = score_code_response(task["id"], response)
                
                success = final_score >= 70.0
                score = final_score
                attempts = 1
                steps = [{"verification": "code_elements_checked"}]
            
        except Exception as e:
            error = str(e)[:200]
            score = 0.0
            success = False
        
        elapsed = time.time() - task_start
        
        result = {
            "task_id": task["id"],
            "task_name": task["name"],
            "success": success,
            "score": score,
            "tokens_used": 0,
            "time_seconds": elapsed,
            "architecture": "v4.0-parallel-multi-worker",
            "attempts": attempts,
            "error": error,
            "steps": steps
        }
        
        results.append(result)
        
        status = "✅" if success else "❌"
        print(f"  Result: {status} Score={score:.1f}, Time={elapsed:.1f}s")
    
    # Calculate summary
    success_count = sum(1 for r in results if r["success"])
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_time = sum(r["time_seconds"] for r in results) / len(results)
    
    summary = {
        "version": "4.0.0",
        "architecture": "v4.0-parallel-multi-worker",
        "timestamp": timestamp,
        "total_tasks": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results) * 100,
        "avg_score": avg_score,
        "avg_tokens": 0.0,
        "avg_time": avg_time,
        "results": results
    }
    
    return summary

if __name__ == "__main__":
    print("=" * 60)
    print("MAS v4.0 Parallel Multi-Worker Benchmark")
    print("Architecture: 3 Workers + Voting/Verification")
    print("=" * 60)
    
    summary = run_v4_0_benchmark()
    
    # Save results
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/root/.openclaw/workspace-mas/benchmark/results/v4.0_{timestamp_str}.json"
    
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    with open("/root/.openclaw/workspace-mas/benchmark/results/v4.0_current.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Success Rate: {summary['success_rate']:.1f}% ({summary['success_count']}/{summary['total_tasks']})")
    print(f"Avg Score: {summary['avg_score']:.1f}")
    print(f"Avg Time: {summary['avg_time']:.1f}s")
    print(f"Results saved to: {output_file}")
    
    print("\n--- Version Comparison ---")
    print("v1.0: 80% success, 87 avg")
    print("v2.0: 66.7% success, 77.8 avg")
    print("v3.0: 83.3% success, 80.7 avg (BEST)")
    print(f"v4.0: {summary['success_rate']:.1f}% success, {summary['avg_score']:.1f} avg")

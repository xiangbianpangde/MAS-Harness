#!/usr/bin/env python3
"""
MAS v8.0 Extended Benchmark - 10 tasks
Tests on harder tasks: code_debug, sys_design, code_optimize, math_proof
Plus original 6 tasks from v7.0
"""

import json
import time
import subprocess
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

# Task definitions
TASKS = [
    {
        "task_id": "code_quicksort",
        "task_name": "快速排序",
        "prompt": "实现快速排序Python代码，包含随机pivot和单元测试",
        "max_tokens": 4096,
    },
    {
        "task_id": "code_lcs",
        "task_name": "最长公共子序列",
        "prompt": "实现LCS动态规划算法，返回长度和具体序列",
        "max_tokens": 4096,
    },
    {
        "task_id": "math_prob",
        "task_name": "概率计算",
        "prompt": "5个红球3个蓝球，不放回取2次，求两次都是红球的概率",
        "max_tokens": 4096,
    },
    {
        "task_id": "plan_critical",
        "task_name": "关键路径",
        "prompt": "任务A需2天无依赖，B需3天依赖A，C需1天无依赖，D需2天依赖B，求关键路径",
        "max_tokens": 4096,
    },
    {
        "task_id": "creative_story",
        "task_name": "科幻故事",
        "prompt": "写一个500字的科幻故事，主题：AI的第一次梦境",
        "max_tokens": 8192,
    },
    {
        "task_id": "reason_logic",
        "task_name": "逻辑推理",
        "prompt": "甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，谁在说真话？",
        "max_tokens": 4096,
    },
    {
        "task_id": "code_debug",
        "task_name": "Bug修复",
        "prompt": "以下代码有bug：def find_duplicates(nums): seen=set(); duplicates=[]; for num in nums: if num in seen: duplicates.append(num); else: seen.add(num); return duplicates  # 期望返回[2,3]实际返回空。找出bug并修复。",
        "max_tokens": 4096,
    },
    {
        "task_id": "sys_design",
        "task_name": "系统设计",
        "prompt": "设计一个URL短链服务，包括：1.短码生成算法 2.存储结构 3.302重定向实现 4.高可用方案",
        "max_tokens": 8192,
    },
    {
        "task_id": "code_optimize",
        "task_name": "算法优化",
        "prompt": "优化two_sum算法从O(n²)到O(n)：def two_sum(nums, target): for i in range(len(nums)): for j in range(i+1,len(nums)): if nums[i]+nums[j]==target: return[i,j]",
        "max_tokens": 4096,
    },
    {
        "task_id": "math_proof",
        "task_name": "数学归纳法",
        "prompt": "用数学归纳法证明：1+2+3+...+n = n(n+1)/2",
        "max_tokens": 4096,
    },
]

def call_model(prompt: str, session_id: str, timeout: int = 120) -> Dict[str, Any]:
    """Call MiniMax model via openclaw agent --local"""
    cmd = [
        "openclaw", "agent", "--local",
        "--session-id", session_id,
        "--message", prompt,
        "--timeout", str(timeout),
        "--json"
    ]
    
    start_time = time.time()
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout + 10
    )
    elapsed = time.time() - start_time
    
    try:
        # Find JSON in output (--json flag outputs to stderr)
        output = result.stderr
        json_start = output.find('"payloads"')
        if json_start >= 0:
            start = output.rfind('{', 0, json_start)
            if start >= 0:
                json_str = output[start:]
                resp = json.loads(json_str)
                if resp.get('payloads') and len(resp['payloads']) > 0:
                    text = resp['payloads'][0].get('text', '')
                    usage = resp.get('meta', {}).get('agentMeta', {}).get('usage', {})
                    return {
                        "content": text,
                        "tokens_used": usage.get('total', 0),
                        "time_seconds": elapsed,
                        "error": None,
                    }
    except Exception as e:
        pass
    
    return {
        "content": "",
        "tokens_used": 0,
        "time_seconds": elapsed,
        "error": f"Parsing failed. stderr len={len(result.stderr)}, stdout len={len(result.stdout)}",
    }

def score_response(task_id: str, prompt: str, response_content: str) -> tuple:
    """Score response based on task type and content quality"""
    if not response_content:
        return 0.0, "空响应"
    
    content_lower = response_content.lower()
    
    if task_id == "code_quicksort":
        has_quicksort = "def quicksort" in response_content or "def quick_sort" in response_content
        has_random = "random" in response_content
        has_test = "unittest" in response_content or "pytest" in response_content or "def test" in response_content
        has_pivot = "pivot" in response_content
        
        if has_quicksort and has_random and has_test and has_pivot:
            return 100.0, "完美实现"
        elif has_quicksort and has_pivot:
            return 80.0, "基本实现但缺少随机或测试"
        else:
            return 50.0, "实现不完整"
            
    elif task_id == "code_lcs":
        has_dp = "dp" in response_content or "动态规划" in response_content
        has_length = "len" in response_content or "长度" in response_content
        has_sequence = ("序列" in response_content or "sequence" in content_lower) and len(response_content) > 500
        
        if has_dp and has_length and has_sequence:
            return 100.0, "LCS实现完整正确"
        elif has_dp:
            return 70.0, "有DP但可能不完整"
        else:
            return 40.0, "缺少关键实现"
            
    elif task_id == "math_prob":
        # P = C(5,2)/C(8,2) = 10/28 = 5/14
        if ("5/14" in response_content or "10/28" in response_content) and \
           any(c in response_content for c in ["5", "14", "28"]):
            return 100.0, "答案正确"
        elif any(c in response_content for c in ["10", "28", "14"]):
            return 80.0, "包含部分正确答案"
        else:
            return 50.0, "答案可能不正确"
            
    elif task_id == "plan_critical":
        has_a_b_d = all(c in response_content for c in ["A", "B", "D"])
        has_7 = "7" in response_content
        
        if has_a_b_d and has_7:
            return 100.0, "关键路径正确"
        elif has_a_b_d:
            return 80.0, "关键路径分析正确但时长可能有误"
        else:
            return 50.0, "分析不完整"
            
    elif task_id == "creative_story":
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', response_content))
        has_theme = "梦" in response_content or "梦境" in response_content
        
        if chinese_chars >= 450 and chinese_chars <= 550 and has_theme:
            return 100.0, f"优秀故事({chinese_chars}字)"
        elif chinese_chars >= 400:
            return 85.0, f"故事合格({chinese_chars}字)"
        else:
            return 60.0, f"故事偏短({chinese_chars}字)"
            
    elif task_id == "reason_logic":
        # Only C tells truth
        if "丙" in response_content and ("真" in response_content or "正确" in response_content):
            return 100.0, "推理正确"
        elif "C" in response_content.upper():
            return 90.0, "答案正确但格式不同"
        else:
            return 50.0, "推理可能有误"
            
    elif task_id == "code_debug":
        has_fix = ("not in seen" in response_content.replace(" ", "")) or \
                  ("if num not in seen" in response_content.replace(" ", "")) or \
                  (("bug" in content_lower or "错误" in response_content) and "修复" in response_content)
        if has_fix:
            return 100.0, "正确识别并修复bug"
        else:
            return 60.0, "未完全识别bug"
            
    elif task_id == "sys_design":
        components = [
            ("短码" in response_content or "short" in content_lower or "shorturl" in content_lower),
            ("存储" in response_content or "数据库" in response_content or "database" in content_lower),
            ("重定向" in response_content or "redirect" in content_lower or "302" in response_content),
            ("高可用" in response_content or "HA" in response_content or "可用性" in response_content),
        ]
        score = sum(25 for c in components if c)
        return float(score), f"设计完整度({score}%)"
        
    elif task_id == "code_optimize":
        has_hash = "dict" in response_content or "hash" in content_lower or "{}" in response_content
        has_lookup = "lookup" in content_lower or "查找" in response_content
        has_on = "O(n)" in response_content or "o(n)" in response_content
        
        if has_hash and has_on:
            return 100.0, "正确优化到O(n)"
        elif has_hash:
            return 75.0, "使用hash但可能不是最优"
        else:
            return 40.0, "未正确优化"
            
    elif task_id == "math_proof":
        has_base = "基础" in response_content or "base case" in content_lower or "n=1" in response_content
        has_induction = "归纳" in response_content or "induction" in content_lower
        has_assumption = "假设" in response_content or "假设" in response_content
        has_formula = "n(n+1)/2" in response_content or "n*(n+1)/2" in response_content
        
        if has_base and has_induction and has_assumption and has_formula:
            return 100.0, "证明完整正确"
        elif has_induction and has_formula:
            return 80.0, "基本正确但可能不完整"
        else:
            return 50.0, "证明不完整"
    
    return 50.0, "无法评分"

def run_benchmark():
    """Run all 10 benchmark tasks"""
    results = []
    total_start = time.time()
    
    for idx, task in enumerate(TASKS):
        print(f"\n{'='*60}")
        print(f"Task {idx+1}/10: {task['task_id']} - {task['task_name']}")
        print(f"{'='*60}")
        
        session_id = f"v8-bench-{task['task_id']}-{int(time.time())}"
        task_start = time.time()
        response = call_model(task["prompt"], session_id, timeout=120)
        task_elapsed = time.time() - task_start
        
        if response["error"]:
            result = {
                "task_id": task["task_id"],
                "task_name": task["task_name"],
                "success": False,
                "score": 0.0,
                "tokens_used": response["tokens_used"],
                "time_seconds": task_elapsed,
                "architecture": "v8.0-extended",
                "attempts": 1,
                "error": response["error"],
                "steps": [],
            }
        else:
            score, feedback = score_response(task["task_id"], task["prompt"], response["content"])
            
            result = {
                "task_id": task["task_id"],
                "task_name": task["task_name"],
                "success": score >= 70.0,
                "score": score,
                "tokens_used": response["tokens_used"],
                "time_seconds": task_elapsed,
                "architecture": "v8.0-extended",
                "attempts": 1,
                "error": None,
                "steps": [{
                    "attempt": 1,
                    "response_length": len(response["content"]),
                    "chars": len(response["content"]),
                    "score": score,
                    "feedback": feedback,
                }],
            }
        
        results.append(result)
        print(f"Score: {result['score']}")
        print(f"Time: {result['time_seconds']:.2f}s")
        print(f"Tokens: {result.get('tokens_used', 0)}")
        print(f"Feedback: {result['steps'][0]['feedback'] if result['steps'] else result.get('error', 'Unknown')}")
    
    total_elapsed = time.time() - total_start
    
    # Calculate summary
    success_count = sum(1 for r in results if r["success"])
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_tokens = sum(r.get("tokens_used", 0) for r in results) / len(results)
    avg_time = sum(r["time_seconds"] for r in results) / len(results)
    
    benchmark_result = {
        "version": "8.0.0",
        "architecture": "v8.0-extended",
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(TASKS),
        "success_count": success_count,
        "success_rate": (success_count / len(TASKS)) * 100,
        "avg_score": avg_score,
        "avg_tokens": avg_tokens,
        "avg_time": avg_time,
        "total_time": total_elapsed,
        "results": results,
    }
    
    return benchmark_result

if __name__ == "__main__":
    print("MAS v8.0 Extended Benchmark - Starting...")
    print("="*60)
    result = run_benchmark()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "/root/.openclaw/workspace-mas/benchmark/results"
    os.makedirs(results_dir, exist_ok=True)
    
    result_file = f"{results_dir}/v8.0_{timestamp}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Also save as current
    current_file = f"{results_dir}/v8.0_current.json"
    with open(current_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*60}")
    print(f"Total Tasks: {result['total_tasks']}")
    print(f"Success Rate: {result['success_rate']:.1f}%")
    print(f"Average Score: {result['avg_score']:.1f}")
    print(f"Average Time: {result['avg_time']:.2f}s")
    print(f"Total Time: {result['total_time']:.2f}s")
    print(f"\nResults saved to: {result_file}")
    print(f"Current results: {current_file}")
    
    # Compare with v7.0
    print(f"\n--- Comparison with v7.0 ---")
    print(f"v7.0: 6 tasks, 100% success, 100.0 avg")
    print(f"v8.0: {result['total_tasks']} tasks, {result['success_rate']:.1f}% success, {result['avg_score']:.1f} avg")

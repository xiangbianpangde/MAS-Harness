#!/usr/bin/env python3
"""Run MAS v106 benchmark"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v106 import MASOrchestratorV106
from benchmark_agi_max import (
    BBEH_TASKS, HLE_TASKS, IMO_ANSWER_TASKS, SWE_BENCH_PRO_TASKS,
    MATH_500_TASKS, GPQA_DIAMOND_TASKS, OSWORLD_TOOL_HARD_TASKS, ZEROBENCH_TASKS
)
from arc_loader import load_all_arc_tasks

tasks = {
    "ARC-AGI-3": load_all_arc_tasks(max_tasks=5, max_grid_size=15),
    "BBEH": BBEH_TASKS, "HLE": HLE_TASKS,
    "IMO-ANSWER": IMO_ANSWER_TASKS, "SWE-Bench-Pro": SWE_BENCH_PRO_TASKS,
    "MATH-500": MATH_500_TASKS, "GPQA-Diamond": GPQA_DIAMOND_TASKS,
    "OSWorld-Tool-Hard": OSWORLD_TOOL_HARD_TASKS, "ZeroBench": ZEROBENCH_TASKS,
}

if __name__ == "__main__":
    print("=" * 60)
    print("MAS v106.0")
    print("=" * 60)
    print(f"\nTask Summary:")
    for bm, tl in tasks.items():
        print(f"  {bm}: {len(tl)} tasks")
    print(f"  TOTAL: {sum(len(v) for v in tasks.values())} tasks")
    
    orch = MASOrchestratorV106()
    start = time.time()
    TIME_LIMIT = 3600
    
    try:
        scores, total_score, results = orch.run_benchmark(tasks, time_limit=TIME_LIMIT)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("MAS v106.0 Results")
    print("=" * 60)
    print(f"Overall Score: {total_score:.4f}")
    print(f"Runtime: {elapsed:.1f}s")
    print("-" * 60)
    print(f"  ARC-AGI-3 (25%):    {scores.arc_agi_3:.4f}")
    print(f"  BBEH (20%):         {scores.bbeh:.4f}")
    print(f"  HLE (15%):          {scores.hle:.4f}")
    print(f"  IMO-ANSWER (15%):   {scores.imo_answer:.4f}")
    print(f"  SWE-Bench-Pro (10%): {scores.swe_bench_pro:.4f}")
    print(f"  MATH-500 (8%):      {scores.math_500:.4f}")
    print(f"  GPQA-Diamond (4%):  {scores.gpqa_diamond:.4f}")
    print(f"  OSWorld-Tool-Hard (2%): {scores.osworld_tool_hard:.4f}")
    print(f"  ZeroBench (1%):     {scores.zerobench:.4f}")
    
    result_file = f"/root/.openclaw/workspace-mas/benchmark/results/v106_{int(time.time())}.json"
    rd = {
        "version": "v106",
        "overall_score": total_score,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": elapsed,
        "scores": {
            "ARC-AGI-3": scores.arc_agi_3, "BBEH": scores.bbeh, "HLE": scores.hle,
            "IMO-ANSWER": scores.imo_answer, "SWE-Bench-Pro": scores.swe_bench_pro,
            "MATH-500": scores.math_500, "GPQA-Diamond": scores.gpqa_diamond,
            "OSWorld-Tool-Hard": scores.osworld_tool_hard, "ZeroBench": scores.zerobench,
        }
    }
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")

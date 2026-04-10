#!/usr/bin/env python3
"""Run MAS v64 benchmark"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v64_best_of_all_fixed import MASOrchestratorV64
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
    print("MAS v64.0 - Best-of-all (FIXED run_benchmark)")
    print("=" * 60)
    print(f"\nTask Summary:")
    for bm, tl in tasks.items():
        print(f"  {bm}: {len(tl)} tasks")
    print(f"  TOTAL: {sum(len(v) for v in tasks.values())} tasks")
    
    orch = MASOrchestratorV64()
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
    print(orch.get_report(scores, total_score, results, elapsed))
    
    result_file = f"/root/.openclaw/workspace-mas/benchmark/results/v64_{int(time.time())}.json"
    rd = {
        "version": "v64",
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
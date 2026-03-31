#!/usr/bin/env python3
"""MAS v14.0 Benchmark Runner"""
import sys, json, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v14_adaptive import MASOrchestrator, BENCHMARK_WEIGHTS
from arc_loader import load_all_arc_tasks
from benchmark_agi_max import (
    BBEH_TASKS, HLE_TASKS, IMO_ANSWER_TASKS, SWE_BENCH_PRO_TASKS,
    MATH_500_TASKS, GPQA_DIAMOND_TASKS, OSWORLD_TOOL_HARD_TASKS, ZEROBENCH_TASKS
)

def get_tasks(arc_sample=10, arc_max_grid=15):
    arc_tasks = load_all_arc_tasks(max_tasks=arc_sample, max_grid_size=arc_max_grid)
    return {
        "ARC-AGI-3": arc_tasks, "BBEH": BBEH_TASKS, "HLE": HLE_TASKS,
        "IMO-ANSWER": IMO_ANSWER_TASKS, "SWE-Bench-Pro": SWE_BENCH_PRO_TASKS,
        "MATH-500": MATH_500_TASKS, "GPQA-Diamond": GPQA_DIAMOND_TASKS,
        "OSWorld-Tool-Hard": OSWORLD_TOOL_HARD_TASKS, "ZeroBench": ZEROBENCH_TASKS,
    }

if __name__ == "__main__":
    print("=" * 60)
    print("MAS v14.0 Adaptive Benchmark")
    print("=" * 60)
    tasks = get_tasks()
    print(f"\nTask Summary:")
    for bm, tl in tasks.items():
        print(f"  {bm}: {len(tl)} tasks")
    total_tasks = sum(len(v) for v in tasks.values())
    print(f"  TOTAL: {total_tasks} tasks")
    
    orch = MASOrchestrator()
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
    print(f"\n{orch.get_report(scores, total_score, results, elapsed)}")
    
    result_file = "/root/.openclaw/workspace-mas/benchmark_results_v14.json"
    rd = {
        "generation": 14, "overall_score": total_score,
        "is_human_replaceable": total_score >= 0.8,
        "is_expert_level": total_score >= 0.95,
        "is_converged": orch.consecutive_stable_gens >= 10,
        "best_generation": orch.best_generation,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": elapsed,
        "weights": BENCHMARK_WEIGHTS,
        "scores": {
            "ARC-AGI-3": scores.arc_agi_3, "BBEH": scores.bbeh, "HLE": scores.hle,
            "IMO-ANSWER": scores.imo_answer, "SWE-Bench-Pro": scores.swe_bench_pro,
            "MATH-500": scores.math_500, "GPQA-Diamond": scores.gpqa_diamond,
            "OSWorld-Tool-Hard": scores.osworld_tool_hard, "ZeroBench": scores.zerobench,
        }
    }
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")

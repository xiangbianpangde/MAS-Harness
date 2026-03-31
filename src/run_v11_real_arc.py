#!/usr/bin/env python3
"""
MAS v11.0 Real ARC Benchmark Runner
Uses actual ARC-AGI evaluation data
"""

import sys
import json
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v11_real_arc import MASOrchestrator, BENCHMARK_WEIGHTS, SOLVER_MAP
from arc_loader import load_all_arc_tasks
from benchmark_agi_max import (
    BBEH_TASKS, HLE_TASKS, IMO_ANSWER_TASKS, SWE_BENCH_PRO_TASKS,
    MATH_500_TASKS, GPQA_DIAMOND_TASKS, OSWORLD_TOOL_HARD_TASKS, ZEROBENCH_TASKS
)

def get_tasks(arc_sample: int = 400, arc_max_grid: int = 0) -> dict:
    """Get all benchmark tasks"""
    arc_tasks = load_all_arc_tasks(max_tasks=arc_sample, max_grid_size=arc_max_grid)
    return {
        "ARC-AGI-3": arc_tasks,
        "BBEH": BBEH_TASKS,
        "HLE": HLE_TASKS,
        "IMO-ANSWER": IMO_ANSWER_TASKS,
        "SWE-Bench-Pro": SWE_BENCH_PRO_TASKS,
        "MATH-500": MATH_500_TASKS,
        "GPQA-Diamond": GPQA_DIAMOND_TASKS,
        "OSWorld-Tool-Hard": OSWORLD_TOOL_HARD_TASKS,
        "ZeroBench": ZEROBENCH_TASKS,
    }

def run():
    print("=" * 60)
    print("MAS v11.0 Real-ARC Benchmark")
    print("=" * 60)

    # Determine ARC sample size based on time constraints
    # Each ARC task takes ~1-3 min depending on grid size and API latency
    # Using max_grid_size=15 to filter out the largest/slowest tasks
    # 30 tasks with small/medium grids = ~45-60 min total
    arc_sample = 10
    arc_max_grid = 15
    
    tasks = get_tasks(arc_sample=arc_sample, arc_max_grid=arc_max_grid)
    
    print("\nTask Summary:")
    for bm, task_list in tasks.items():
        w = BENCHMARK_WEIGHTS.get(bm, 0)
        print(f"  {bm}: {len(task_list)} tasks (weight: {w:.0%})")

    total_tasks = sum(len(v) for v in tasks.values())
    print(f"  TOTAL: {total_tasks} tasks")

    orchestrator = MASOrchestrator()

    print("\nRunning benchmarks...")
    print(f"  (Using {arc_sample} ARC tasks, {len(tasks['BBEH'])} BBEH, etc.)")
    start_time = time.time()
    
    # Time limit: 60 minutes
    TIME_LIMIT = 3600

    try:
        scores, total_score, results = orchestrator.run_benchmark(tasks, time_limit=TIME_LIMIT)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

    elapsed = time.time() - start_time

    print("\n" + orchestrator.get_report(scores, total_score, results, elapsed))

    # Save results
    result_file = "/root/.openclaw/workspace-mas/benchmark_results_v11.json"
    rd = {
        "generation": orchestrator.generation,
        "overall_score": total_score,
        "is_human_replaceable": total_score >= 0.8,
        "is_expert_level": total_score >= 0.95,
        "is_converged": orchestrator.consecutive_stable_gens >= 10,
        "best_generation": orchestrator.best_generation,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": elapsed,
        "weights": BENCHMARK_WEIGHTS,
        "scores": {
            "ARC-AGI-3": scores.arc_agi_3,
            "BBEH": scores.bbeh,
            "HLE": scores.hle,
            "IMO-ANSWER": scores.imo_answer,
            "SWE-Bench-Pro": scores.swe_bench_pro,
            "MATH-500": scores.math_500,
            "GPQA-Diamond": scores.gpqa_diamond,
            "OSWorld-Tool-Hard": scores.osworld_tool_hard,
            "ZeroBench": scores.zerobench,
        }
    }
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")

    # Git commit if converged or high score
    if total_score >= 0.8 or orchestrator.consecutive_stable_gens >= 10:
        print("\nThreshold reached - git commit...")
        try:
            os.chdir("/root/.openclaw/workspace-mas")
            os.system("git add src/mas_v11_real_arc.py src/arc_loader.py 2>/dev/null")
            os.system("git commit -m 'MAS v11.0: real ARC-AGI, score={:.4f}' 2>/dev/null".format(total_score))
        except Exception as e:
            print(f"Git error: {e}")

if __name__ == "__main__":
    run()

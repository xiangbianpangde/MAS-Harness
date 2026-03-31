#!/usr/bin/env python3
"""
MAS v10.0 AGI-Max Runner - Quick version
"""

import sys
import json
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v10_agi_max import MASOrchestrator, BENCHMARK_WEIGHTS
from benchmark_agi_max import get_all_tasks, get_task_count

def run():
    print("=" * 60)
    print("MAS v10.0 AGI-Max - Benchmark Runner")
    print("=" * 60)

    tasks = get_all_tasks()
    counts = get_task_count()

    print("\nTask Summary:")
    for bm, count in counts.items():
        w = BENCHMARK_WEIGHTS.get(bm, 0)
        print(f"  {bm}: {count} tasks (weight: {w:.0%})")

    print(f"\nInitializing orchestrator...")
    orchestrator = MASOrchestrator()

    print("Running benchmarks...")
    start_time = time.time()

    try:
        result = orchestrator.run_benchmark(tasks)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

    elapsed = time.time() - start_time

    print("\n" + orchestrator.get_report(result))
    print(f"\nRuntime: {elapsed:.1f}s, Tasks: {len(result.task_results)}")

    # Per-benchmark
    print("\n" + "-" * 60)
    bm_results = {}
    for tr in result.task_results:
        bm_results.setdefault(tr.benchmark, []).append(tr)

    for bm, results in bm_results.items():
        avg = sum(r.score for r in results) / len(results)
        ok = sum(1 for r in results if r.success)
        print(f"  {bm}: avg={avg:.3f} success={ok}/{len(results)}")

    # Save
    result_file = "/root/.openclaw/workspace-mas/benchmark_results_v10.json"
    rd = {
        "generation": result.generation,
        "overall_score": result.overall_score,
        "is_human_replaceable": result.is_human_replaceable,
        "is_expert_level": result.is_expert_level,
        "is_converged": result.is_converged,
        "best_generation": result.best_generation,
        "timestamp": result.timestamp,
        "runtime_seconds": elapsed,
        "weights": BENCHMARK_WEIGHTS,
        "scores": {
            "ARC-AGI-3": result.scores.arc_agi_3,
            "BBEH": result.scores.bbeh,
            "HLE": result.scores.hle,
            "IMO-ANSWER": result.scores.imo_answer,
            "SWE-Bench-Pro": result.scores.swe_bench_pro,
            "MATH-500": result.scores.math_500,
            "GPQA-Diamond": result.scores.gpqa_diamond,
            "OSWorld-Tool-Hard": result.scores.osworld_tool_hard,
            "ZeroBench": result.scores.zerobench,
        }
    }
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")

    # Git commit if converged or high score
    if result.is_converged or result.overall_score >= 0.8:
        print("\nThreshold reached - git commit...")
        try:
            os.chdir("/root/.openclaw/workspace-mas")
            os.system("git add src/mas_v10_agi_max.py src/benchmark_agi_max.py src/run_v10_agi_max.py 2>/dev/null")
            os.system("git commit -m 'MAS v10.0 AGI-Max: score={:.4f}' 2>/dev/null".format(result.overall_score))
            print("Done")
        except Exception as e:
            print(f"Git error: {e}")

if __name__ == "__main__":
    run()

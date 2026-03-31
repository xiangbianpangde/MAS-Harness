#!/usr/bin/env python3
"""Run v12.0 MAS Benchmark"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v12_enhanced_scorers import MASOrchestrator, get_benchmark_tasks, BENCHMARK_WEIGHTS

def main():
    print("=" * 60)
    print("MAS v12.0 - Enhanced Scoring Benchmark")
    print("=" * 60)
    
    orchestrator = MASOrchestrator()
    
    # Load tasks (100 ARC tasks for good coverage)
    tasks = get_benchmark_tasks(arc_sample_size=30)
    
    # Count tasks
    total = sum(len(v) for v in tasks.values())
    print(f"\nLoaded {total} tasks:")
    for bm, tlist in tasks.items():
        weight = BENCHMARK_WEIGHTS.get(bm, 0)
        print(f"  {bm}: {len(tlist)} tasks (weight: {weight:.0%})")
    
    print("\nRunning benchmark...")
    start = time.time()
    
    scores, total_score, results = orchestrator.run_benchmark(tasks, time_limit=3600)
    
    elapsed = time.time() - start
    
    # Print report
    report = orchestrator.get_report(scores, total_score, results, elapsed)
    print("\n" + report)
    
    # Save results
    results_file = "/root/.openclaw/workspace-mas/benchmark_results_v12.json"
    result_data = {
        "generation": 12,
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
    
    with open(results_file, "w") as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\nResults saved to {results_file}")
    return total_score

if __name__ == "__main__":
    main()

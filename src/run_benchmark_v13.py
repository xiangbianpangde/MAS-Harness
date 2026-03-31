#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/workspace-mas/src')
from mas_v13 import MASOrchestrator, get_benchmark_tasks
import time
import json

print('Starting full benchmark...')
sys.stdout.flush()

orch = MASOrchestrator()
tasks = get_benchmark_tasks(arc_sample_size=3)
print(f'Tasks: {sum(len(v) for v in tasks.values())} total')
sys.stdout.flush()

t0 = time.time()
scores, total_score, results = orch.run_benchmark(tasks, time_limit=2400)
elapsed = time.time() - t0
print(f'Done in {elapsed:.1f}s, Overall: {total_score:.4f}')
sys.stdout.flush()

data = {'generation': 13, 'overall_score': total_score, 'runtime': elapsed, 
        'scores': {k: getattr(scores, v) for k, v in [('ARC-AGI-3','arc_agi_3'),('BBEH','bbeh'),('HLE','hle'),('IMO-ANSWER','imo_answer'),('SWE-Bench-Pro','swe_bench_pro'),('MATH-500','math_500'),('GPQA-Diamond','gpqa_diamond'),('OSWorld-Tool-Hard','osworld_tool_hard'),('ZeroBench','zerobench')]}}
with open('/root/.openclaw/workspace-mas/benchmark_results_v13.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved!')
sys.stdout.flush()

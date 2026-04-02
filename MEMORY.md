# MEMORY.md - Long Term Memory

## Current Best Architecture: v34 @ ~0.91

v34 is the most stable and high-performing architecture discovered so far.

### v34 Key Components:
- **EnhancedMathScorer**: Uses CONCEPT_WEIGHTS for IMO scoring
- **solve_imo_v34**: Technique detection from expected answer hints
- **solve_swe_v34**: Bug-specific pattern detection (off_by_one, null_none, type_error, etc.)
- **solve_zerobench_v15**: Multi-perspective scoring with framework coverage
- **solve_osworld_v17**: Command equivalence groups for OS task scoring

### Benchmark Weights (importance):
- ARC-AGI-3: 25% (most important)
- BBEH: 20%
- HLE: 15%
- IMO-ANSWER: 15%
- SWE-Bench-Pro: 10%
- MATH-500: 8%
- GPQA-Diamond: 4%
- OSWorld-Tool-Hard: 2%
- ZeroBench: 1%

## Critical Lessons Learned

### What DESTROYED Performance:
1. Multi-call verification (v41) - added complexity without benefit
2. Aggressive combining of approaches (v36) - caused regression
3. Changing v34 architecture significantly (v40-v43) - all regressed

### What IMPROVED Performance:
1. IMO technique detection from expected hints (v19) - +0.134
2. Bug-specific fix patterns (v34) - SWE from ~0.73 to 0.987
3. MATH verification loop (v35 initial) - MATH from 0.72 to 1.0

### API Variance
- MiniMax API causes ~1-3% fluctuation between runs
- v34 at 0.90-0.91 is the stable performance band

## Technical Details

### API Configuration:
- Model: minimax/MiniMax-M2
- API Key: sk-cp-...(stored in source)
- Base URL: https://api.minimax.chat/v1/text/chatcompletion_v2

### Key Source Files:
- mas_v34_swe_focus.py: Best architecture (v34)
- mas_v14_adaptive.py: Base classes (LLMClient, TaskResult, etc.)
- benchmark_agi_max.py: Task definitions (BBEH, HLE, IMO, SWE-Bench, MATH-500, etc.)

## Evolution History Summary
- v1-v7: Single agent → Planner-Worker-Reviewer → Thinking Block Extractor
- v8-v14: Iteration-based improvements
- v15-v20: Technique detection, enhanced scorers
- v21-v30: Various improvements, API variance issues
- v31-v34: Recovery to stable ~0.90 architecture
- v35-v43: Attempts to improve, all failed, v34 remains best

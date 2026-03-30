# MAS Evolution History

## v1.0.0 - Initial Baseline (2026-03-30)
**Architecture**: Single-Agent
**Status**: Baseline Established

### Server Specs
- CPU: 4x Intel Xeon Platinum 8255C @ 2.5GHz
- Memory: 3.6GB (1.8GB used, 1.4GB available)
- Disk: 40GB (22GB available, 44% used)
- Model: MiniMax-M2.7 (204800 context, $0.3/1K input)

### Components
- OpenClaw Gateway: running on port 37240
- QQ Bot: 2号claw (appId: 1903664531) ✅ Alert channel working
- GitHub: xiangiangpangde/mas-harness ✅ Connected

### Baseline Metrics (Expected)
- Task Set: 16 diverse tasks (code, reasoning, planning, creative)
- Expected Success Rate: ~60-70% (single agent)
- Expected Avg Tokens: ~3000-5000 per task
- Expected Avg Time: ~10-20s per task

### Infrastructure
- Resource Monitor: `monitor/resource_monitor.py`
- Benchmark Suite: `benchmark/mas_benchmark.py`
- Single-Agent Baseline: `src/mas_v1_single.py`

### Next Steps
- Run v1.0 baseline to get actual metrics
- Design v2.0 with multi-agent decomposition
- Implement Planner-Agent + Worker-Agent architecture

---

## Changelog

| Version | Date | Architecture | Success Rate | Avg Score | Avg Time | Status |
|---------|------|--------------|--------------|------------|----------|--------|
| 1.0.0 | 2026-03-30 | Single-Agent | 80.0% | 87.0 | 44.0s | Baseline |
| 2.0.0 | 2026-03-30 | Planner-Worker | 66.7% | 77.8 | 72.9s | Tested |
| 3.0.0 | 2026-03-30 | Planner-Worker-Reviewer | 0.0% | 50.0 | 0.3s | **BROKEN** |

### v1.0 Baseline Results (2026-03-30)
- **Success Rate**: 80-100% (avg 90%)
- **Avg Score**: 87-93
- **Avg Time**: 12-44s per task
- **Issues**: creative_story hits 4096 token limit
- **v2.0 Design**: Planner-Worker decomposition to address token limit and improve quality

### v2.0 Planner-Worker Architecture
- **Status**: ✅ Benchmark Complete (2026-03-30 19:39)
- **Key Features**:
  - Planner Agent: Analyzes task, selects strategy (direct/decompose/iterative)
  - Worker Agent: Executes based on strategy
  - Token budget management (up to 16384 for creative tasks)
- **Expected Improvements**:
  - Better creative task completion (higher token budget)
  - More structured code generation
  - Error recovery through planning

### v2.0.0 - Planner-Worker Benchmark Results (2026-03-30 19:41)
**Architecture**: Planner-Worker (Planner Agent + Worker Agent)

| Task | Score | Tokens | Time | Success |
|------|-------|--------|------|---------|
| code_quicksort | 89 | 4257 | 106.1s | ✅ |
| code_lcs | 100 | 3103 | 100.7s | ✅ |
| math_prob | 58 | 731 | 29.6s | ❌ |
| plan_critical | 78 | 2174 | 68.9s | ✅ |
| creative_story | 92 | 1436 | 59.8s | ✅ |
| reason_logic | 50 | 2180 | 72.6s | ❌ |

**Summary**: Success Rate 66.7% (4/6), Avg Score 77.8, Avg Time 72.9s

**Key Findings**:
- Success Rate: 66.7% (worse than v1.0's 80%)
- math_prob failed: model gave non-standard answer format
- reason_logic failed: model provided correct answer but didn't pass scoring threshold
- creative_story: 92 (improved from v1.0's 60 - no longer truncated)
- code tasks: Excellent (89, 100)
- creative improved but reasoning regressed

**v3.0 Design Direction**: Add Reviewer Agent with feedback loops to fix reasoning tasks.

---

## v3.0.0 - Planner-Worker-Reviewer Benchmark Results (2026-03-30 19:43)
**Architecture**: Planner-Worker-Reviewer (3-Agent with quality feedback loops)

| Task | Score | Tokens | Time | Success |
|------|-------|--------|------|---------|
| code_quicksort | 50 | 0 | 0.37s | ❌ |
| code_lcs | 50 | 0 | 0.31s | ❌ |
| math_prob | 50 | 0 | 0.34s | ❌ |
| plan_critical | 50 | 0 | 0.30s | ❌ |
| creative_story | 50 | 0 | 0.29s | ❌ |
| reason_logic | 50 | 0 | 0.31s | ❌ |

**Summary**: Success Rate 0.0% (0/6), Avg Score 50.0, Avg Time 0.32s

**Critical Failure Analysis**:
- All tasks tokens_used=0 → model API calls returning empty responses
- REVIEW_THRESHOLD=60 with base score 50 → all tasks rejected immediately
- Worker API endpoint appears broken (returns empty response, 0 tokens)
- Avg time 0.32s confirms tasks fail at API call level, not logic level
- **v3.0 is a catastrophic regression** — reviewer feedback loops introduced but core API integration broken

**Root Cause**: The v3.0 `call_model()` uses a different API URL/path than v2.0, causing silent failures.

**v4.0 Design Direction**: Fix API integration first. Simplify reviewer to use semantic validation instead of pattern matching. Consider dropping reviewer for simple tasks.

### v1.0.1 - Baseline Runner Added (2026-03-30 19:10)
- Added mas_runner.py for benchmark execution
- GitHub connectivity restored
- Resources: CPU 3%, Mem 1.7GB avail, Disk 21GB
- Status: Ready to run baseline benchmark

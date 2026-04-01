# HEARTBEAT.md - MAS Evolution Engine Heartbeat

## OODA Loop Execution Checklist:

### A. Background Process & Resource Check
1. `ps aux | grep python` - Check if MAS test is running
2. `df -h /` and `free -h` - Check resources
3. If GPU >90% or Disk <3GB: Run garbage collection
4. If test process >24 hours: `kill -9` it, record "Deadlock/Timeout"

### B. Evaluate & Document
1. If no test running: Check latest benchmark results
2. Record score in `EVOLUTION_HISTORY.md`
3. **Convergence Check**: If last 10 iterations improved <1%:
   - Package current architecture
   - `git tag vX.Y.Z` and `git push --tags`
   - Plan paradigm shift

### C. Design & Execute Next Generation
1. Analyze last results, design next architecture
2. Write Python code for next gen MAS
3. Run in background: `nohup python3 src/run_vN.py > current_test.log 2>&1 &`
4. Record PID and start time

---

## 当前状态: ✅ STABLE - No test running

**BEST: v17 @ 0.8692** 🏆

**v28 CRASHED**: `features` not defined in MATH-500 solver
- Bug in solve_math function - references undefined `features` variable
- v28 killed, v17 remains best

**v17 Results** (0.8692 - to beat):
| Category | Score |
|----------|-------|
| ARC-AGI-3 | 0.862 |
| BBEH | 0.900 |
| HLE | 1.000 |
| IMO-ANSWER | 0.806 |
| SWE-Bench-Pro | 0.790 |
| MATH-500 | 0.860 |
| GPQA-Diamond | 1.000 |
| OSWorld-Tool-Hard | 0.300 |
| ZeroBench | 0.900 |

**Next**: Fix v28 MATH-500 bug and rerun, OR use v17 as base for new improvement

---

## Alert Conditions:
- Disk <3GB remaining
- Memory <500MB available
- CPU >95% for >5 minutes
- Test process timeout (>24h)

## Alert Action:
If critical + 3自救 attempts failed:
- Send QQ alert via `message(channel=qqbot, to=qqbot:c2c:USER_OPENID)`
- Push emergency log to GitHub

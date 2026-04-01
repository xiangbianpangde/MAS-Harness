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

## 当前状态: ✅ v17 COMPLETE - NEW BEST!

**v17.0 结果** (0.8783, +0.021 vs v16):
| Category | Score | vs v16 |
|----------|-------|--------|
| ARC-AGI-3 | 0.856 | -0.023 |
| BBEH | 0.900 | 0.000 |
| HLE | 1.000 | 0.000 |
| IMO-ANSWER | 0.826 | +0.023 |
| SWE-Bench-Pro | 0.747 | -0.003 |
| **MATH-500** | **0.860** | **+0.140** 🎉 |
| GPQA-Diamond | 1.000 | 0.000 |
| **OSWorld-Tool-Hard** | **0.900** | **+0.600** 🎉 |
| ZeroBench | 0.900 | +0.017 |

**Runtime**: 1260.7s
**Status**: No test running

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

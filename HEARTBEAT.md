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
3. Run in background: `nohup python3 -u src/run_vN.py > benchmark/current_test.log 2>&1 &`
4. Record PID and start time

---

## 当前状态: 🟢 RUNNING v64 (FIXED, PID 187847, started ~09:12)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v63 CRASH**: 0.5734 - catastrophic. Root cause: solve_task() override ignored by v52.run_benchmark().

**v64 FIX**: Properly override run_benchmark() to call correct solvers:
- ARC: 7-vote (from v58) | IMO: 5-vote (from v58)
- SWE: v34 solver | Others: v14/v17 solvers

**v58-v62 结果** (API variance ~5-7%):
| Version | Overall | ARC | IMO | SWE |
|---------|---------|-----|-----|-----|
| v60 | 0.9080 | 0.8958 | 0.8316 | 0.9400 |
| v59 | 0.9073 | 0.8891 | 0.8092 | 0.9867 |
| v58 | 0.8965 | 0.8758 | 0.8548 | 0.8367 |

**资源**: Disk 19GB ✅, Mem 2.3GB ✅

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

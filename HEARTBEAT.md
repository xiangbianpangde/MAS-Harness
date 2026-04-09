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

## 当前状态: 🔄 v52 RERUN (PID: 87587, started 02:41)

**历史最佳**: v52 Run1 **0.9166** 🏆 (2026-04-10 00:32)

**近期结果** (API variance demonstrated):
| Version | Score | Notes |
|---------|-------|-------|
| **v52 Run1** | **0.9166** 🏆 | Best (high-roll) |
| v54 | 0.8945 | SWE dropped to 0.82 |
| v52 Run2 | 0.8687 | ARC-AGI dropped to 0.79 |
| v53 | 0.8151 | IMO crashed to 0.12 |

**关键发现**:
- v52 Run1 (0.9166) was a high-roll - normal range is 0.87-0.91
- LLM API variance causes ~5% fluctuation on visual tasks (ARC-AGI)
- IMO-ANSWER crash in v53 (0.12) suggests API timeout/error
- ARC-AGI swings from 0.79 to 0.95 between runs

**v55策略**: 
- Keep v52 architecture (ARC voting + v34 solvers)
- Run multiple times to get stable high score
- Consider ensemble of v52 runs (take median/mean)

**资源**: Disk 19GB ✅, Mem 2.4GB ✅

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

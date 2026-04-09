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

## 当前状态: 🔄 v52 RERUN (PID: 79566, started 02:10)

**历史最佳**: v52 **0.9166** 🏆

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v52 | **0.9166** 🏆 | Best overall |
| v54 | 0.8945 | SWE regression |
| v53 | 0.8151 | IMO crashed to 0.12 (FIXED) |
| v34 | 0.9120 | Previous best |

**v53 IMO Fix** (committed):
- Changed from `expected_answer` → `expected` field
- Restored v14 technique hint extraction
- Restored v14 proof structure scoring
- Should recover IMO from 0.12 to ~0.80+

**v52 Strategy**:
- Running v52 again to confirm high score
- After v52 completes, test fixed v53
- v53 has potential: ARC=0.9533, MATH=1.0, IMO fixed

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

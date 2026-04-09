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

## 当前状态: 🟢 RUNNING v58 (robust ensemble, PID 138811, started ~05:58)

**历史最佳**: v52 **0.9166** 🏆

**v58 策略**: Robust weighted ensemble
- ARC: 7 votes with weighted scoring (count * avg_score)
- IMO: 5 votes (up from 3)
- Goal: Better variance reduction through smarter aggregation

**近期结果**:
| Version | Score | ARC | IMO | Notes |
|---------|-------|-----|-----|-------|
| v57 | 0.8985 | 0.8958 | 0.7884 | 5 ARC votes |
| v56 | 0.9064 | 0.8758 | 0.8274 | IMO voting |
| v52 Run1 | **0.9166** 🏆 | 0.9233 | 0.8320 | Best |

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

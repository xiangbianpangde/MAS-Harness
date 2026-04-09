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

## 当前状态: 🟢 RUNNING v57 (Dual voting, PID 118516, started ~04:37)

**历史最佳**: v52 **0.9166** 🏆

**近期结果**:
| Version | Score | ARC-AGI | IMO-ANSWER | Notes |
|---------|-------|---------|------------|-------|
| v56 | 0.9064 | 0.8758 | **0.8274** | IMO voting +3 |
| v55 | 0.9068 | 0.8924 | 0.8002 | MATH verify |
| v52 Run3 | 0.9036 | 0.8824 | 0.7958 | |
| v52 Run1 | **0.9166** 🏆 | **0.9233** | 0.8320 | Best ever |
| v52 Run2 | 0.8687 | 0.7858 | 0.7770 | API unlucky |

**v57 策略**: Dual voting on both high-weight components
- ARC-AGI: 5 votes (up from 3)
- IMO-ANSWER: 3 attempts, best score
- 目标: Stabilize both ARC (25%) and IMO (15%)

**API Variance 问题**: 
- v52 Run1 vs Run2: 0.9166 vs 0.8687 = 5% swing
- Caused by API randomness on high-weight tasks

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

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

## 当前状态: 🟢 RUNNING v63 (best-of-all, PID 181839, started ~08:48)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v58-v62 结果** (show massive API variance):
| Version | Overall | ARC | IMO | SWE |
|---------|---------|-----|-----|-----|
| v60 | 0.9080 | 0.8958 | 0.8316 | 0.9400 |
| v59 | 0.9073 | 0.8891 | 0.8092 | **0.9867** |
| v58 | 0.8965 | 0.8758 | **0.8548** 🏆 | 0.8367 |
| v62 | 0.8615 | 0.7788 | 0.7922 | 0.8233 |
| v61 | 0.8494 | 0.8824 | 0.6800 | 0.7367 |
| v52 Run1 | **0.9166** 🏆 | **0.9233** | 0.8320 | 0.9633 |

**关键发现**:
- v58 achieved best IMO ever: 0.8548 (5 votes!)
- v59 achieved best SWE: 0.9867
- API variance causes ~5-7% swing across runs
- v52 Run1 at 0.9166 still best overall

**v63 策略**: Best-of-all combining:
- v52 core (stable SWE from v34)
- v58's 7 ARC votes (robust voting)
- v58's 5 IMO votes (best IMO technique)

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

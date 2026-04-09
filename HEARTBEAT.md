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

## 当前状态: 🟢 RUNNING v60 (Hybrid voting, PID 154979, started ~07:02)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v60 策略**: Hybrid - combine best from v58 & v59
- IMO: 5 votes + confidence weighting (v58: best IMO 0.8548)
- ARC: 5 votes + confidence weighting (v59: 2nd best overall)
- 目标: IMO ~0.85+ AND SWE ~0.98+

**近期排名**:
| Version | Overall | IMO | SWE |
|---------|---------|-----|-----|
| v52 Run1 | **0.9166** 🏆 | 0.8320 | 0.9633 |
| v59 | 0.9073 🏅 | 0.8092 | 0.9867 |
| v56 | 0.9064 | 0.8274 | 0.9867 |
| v58 | 0.8965 | 0.8548 | 0.8367 |
| v57 | 0.8985 | 0.7884 | 0.9167 |

**资源**: Disk 18GB ✅, Mem 2.1GB ✅

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

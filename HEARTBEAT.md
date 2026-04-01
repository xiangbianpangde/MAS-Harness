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

## 当前状态: ✅ v21 Completed (Regression)

**Latest Results**:
| Version | Overall | IMO | SWE | Notes |
|---------|---------|-----|-----|-------|
| v19 | 0.8779 | 0.915 | 0.683 | IMO focus |
| **v20** | **0.8801** ⭐ | 0.797 | 0.883 | Best overall |
| v21 | 0.8603 | 0.805 | 0.650 | Regression |

**Analysis**: 
- v20 remains the best at **0.8801**
- IMO/SWE trade-off observed
- Need ensemble or adaptive approach

**v22 建议**: 
- Use v20 as base
- Try ensemble: v20 SWE + v19 IMO together
- Or use adaptive routing based on task type

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
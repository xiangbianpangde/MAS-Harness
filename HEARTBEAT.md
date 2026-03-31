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
3. Run in background: `nohup python3 src/mas_vN.py > current_test.log 2>&1 &`
4. Record PID and start time

---

## 当前状态: ✅ v14.0 COMPLETED (0.7516, 20/36)

**v14.0**: mas_v14_adaptive.py - Adaptive Agent Synthesis
**结果**: Overall 0.7516, Success 20/36 (55.6%)
**状态**: 比 v11.0 (0.766) 略低，继续观察
**弱项**: IMO-ANSWER(0/5), SWE-Bench-Pro(0/3), ZeroBench(0/3)
**历史最佳**: v11.0 Overall **0.766**
**v12.0**: 0.090 (❌ FAILED)
**v13.0**: (unknown)
**v14.0**: 0.7516 (55.6%)

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

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

## 当前状态: ⏸️ IDLE

**历史最佳**: v68 **0.9304** 🏆 (Run1 @ 05:50)

**最近结果**:
- v68: 0.9304 (BEST)
- v76: TIMEOUT (IMO=0.0)
- v77: 0.9137 (IMO=0.85)
- v78: 0.8971 (SWE=0.64)
- v79: 0.9026 (IMO=0.80)
- v80: 0.8734 (IMO=0.60, TWO tasks failed!)

**架构状态**:
- v2.0 tag: Reflexion paradigm (v68 @ 0.9304)
- API variance causes ±6% swings
- imo_005 task consistently fails (expected=None)

**资源**: Disk 19GB ✅, Mem 2.1GB ✅

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
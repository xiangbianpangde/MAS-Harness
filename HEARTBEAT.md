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

## 当前状态: 🔄 v28 RUNNING (slow but working)

**BEST: v17 @ 0.8692** 🏆

**v28 Status**: NOT hanging - it was just slow!
- Processes multiple tasks: seen 3 ARC tasks + 4 BBEH tasks processed
- Each task takes ~20-30s for LLM calls
- Full run estimated: 34 tasks × ~25s = ~15 minutes minimum

**v28 Debug Findings**:
- "Hangs" after TOTAL due to slow LLM API calls
- stdout buffering caused delay in seeing output
- With `PYTHONUNBUFFERED=1`, can see progress

**Status**: v28 running in background

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

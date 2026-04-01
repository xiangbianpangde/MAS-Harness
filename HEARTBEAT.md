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

## 当前状态: 🔍 v28 DEBUGGING (stdout buffering issue)

**BEST: v17 @ 0.8692** 🏆

**v28 Issue**: Script hangs after "TOTAL: 34 tasks" when run directly
- Inline test with 1-2 tasks WORKS (completes in ~13s)
- Full script (34 tasks) hangs - but process stays alive
- With `python3 -u` and `PYTHONUNBUFFERED=1`, shows "TOTAL: 34 tasks" then hangs
- No crash, no error - just hangs silently

**Status**: No test currently running

**Analysis**: Likely an stdout buffering issue causing the script to appear to hang when run in background with nohup. The actual LLM calls may still be happening but output is not visible.

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

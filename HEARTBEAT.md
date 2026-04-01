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

## 当前状态: 🚀 v30 RUNNING (background)

**v30** (IMO+SWE focus):
- Based on: v17 (0.8783 best)
- Changes: Improved IMO technique hints, Better SWE fix detection
- Run command: `python3 -u src/mas_v30_imo_swe_focus.py`
- Started: ~22:30

**v17 结果** (基准):
- Overall: 0.8783
- IMO-ANSWER: 0.826, SWE: 0.747, MATH: 0.860, OSWorld: 0.900

**v29 结果** (对比):
- Overall: 0.8493
- OSWorld: 1.000, SWE: 0.817, BUT MATH: 0.380 (退步!)

**结论**: v17 是最佳基准，v30 基于此改进 IMO+SWE

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

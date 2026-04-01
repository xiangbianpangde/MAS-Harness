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

## 当前状态: 🚀 READY FOR v35

**🏆 v34 = CURRENT BEST (0.8947)**:
- Success Rate: **91.2%** (31/34 tasks)
- Runtime: 1164.6s
- Key Win: SWE-Bench-Pro 0.733 → **0.987** (+0.253!)

**弱点 (改进空间)**:
| Category | Score | Weight | Priority |
|----------|-------|--------|----------|
| MATH-500 | 0.720 | 8% | 🔴 High |
| IMO-ANSWER | 0.804 | 15% | 🟡 Medium |
| ZeroBench | 0.855 | 1% | 🟢 Low |
| OSWorld | 0.850 | 2% | 🟢 Low |

**建议**: v35 聚焦 MATH-500 提升 (0.720 是明显短板)

**进度**:
- v16→v34: 持续改进 (0.8577 → 0.8947)
- v35 待设计

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

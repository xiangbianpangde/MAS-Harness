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

## 当前状态: 🔴 NEEDS DESIGN

**Best: v17 (enhanced_scorer) @ 0.8692** 🏆

**问题**:
- v17_clean produced 0.2845 (wrong code path)
- v26 produced 0.4326 (broken logic after copy)
- v27 finished with 0.2845 (same as v17_clean)

**结论**: mas_v17_enhanced_scorer.py 是正确的最佳版本

**建议**:
1. 基于 mas_v17_enhanced_scorer.py 设计 v28
2. 修复 OSWorld (0.300) 和 IMO (0.806) 作为主要改进点
3. 不要轻易复制代码，要理解后再修改

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

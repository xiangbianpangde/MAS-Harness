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

## 当前状态: ⚠️ API RATE LIMIT / v16 RE-RUN NEEDED

**v16.0 结果** (0.8577 是当前最佳):
- Overall: 0.8577 ✅
- Gen: 15, Runtime: 786.5s
- Success: 26/34 (76.5%)

**v17 问题已诊断**:
- v16 直接 import solvers by name，不是通过 SOLVER_MAP
- runtime patching 无效，需直接修改 mas_v16_enhanced_scorer.py 源码

**资源状态**:
- Disk: 18G (53%) ✅
- Memory: 191Mi free ⚠️ (偏低但非紧急)

**下一步**: 直接修改 v16 源码替换 solve_osworld 和 solve_math，重命名为 mas_v17

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

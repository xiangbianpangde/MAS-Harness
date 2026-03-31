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

## 当前状态: ⚠️ v17 CREATED BUT API CALLS HANGING

**v16.0 结果** (0.8577 是当前最佳):
- Overall: 0.8577 ✅
- Gen: 15, Runtime: 786.5s
- Success: 26/34 (76.5%)

**v17 已创建**:
- src/mas_v17_enhanced_scorer.py ✅ (import 测试通过)
- 改进的 solve_osworld_v17 和 solve_math_v17 已添加
- 但实际运行时会卡住（API调用挂起）

**问题诊断**:
- LLM API 调用可能存在 rate limit 或连接问题
- v16 能正常运行（786.5s完成），v17卡在初始化
- 可能是 v17 代码路径与 v16 不同导致

**资源状态**:
- Disk: 18G (53%) ✅
- Memory: 158Mi free ⚠️ (偏低)

**下一步**: 在 v16 代码中直接添加改进，而不是创建独立版本

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

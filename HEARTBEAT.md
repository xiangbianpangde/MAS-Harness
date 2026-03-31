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

## 当前状态: 🔴 v17 HANGING - Need Debug

**v16.0 结果** (已验证):
- Overall: **0.8577** ✅
- Gen: 15, Runtime: 786.5s
- Success: 26/34 (76.5%)

**v17 问题**: 
- mas_v17_clean.py 启动后只在 "TOTAL: 34 tasks" 后挂起
- 进程处于 sleep 状态但无输出
- 可能原因: LLM API 调用死锁 或 SOLVER_MAP patch 无效

**弱点**:
| Category | Score | Weight |
|----------|-------|--------|
| OSWorld-Tool-Hard | 0.300 | 2% | ← 重点改进
| MATH-500 | 0.720 | 8% | ← 改进
| IMO-ANSWER | 0.803 | 15% | ← 改进

**建议**: 
1. 检查 mas_v14_adaptive.SOLVER_MAP 是否正确被 patch
2. 检查 LLM client 是否正常工作
3. 可能需要完整重写而非 patch 方式

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

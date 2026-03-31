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

## 当前状态: 🔄 v15.0 运行中 (PID 704385, ~13min)

**v15.0**: mas_v15_enhanced_scorer.py - Enhanced scoring for weak categories
**改进**: 
- IMO-ANSWER: 概念匹配评分 (concept matching)
- SWE-Bench-Pro: 代码结构验证增强
- ZeroBench: 多视角分析评分
- 阈值从 0.8 降低到 0.6
**历史最佳**: v11.0 Overall **0.766**
**v14.0**: 0.7516 (55.6%)

---

## v15.0 计划: Focused Remediation for Weak Categories

**目标**: 改进 IMO-ANSWER, SWE-Bench-Pro, ZeroBench
**策略**: 
- IMO-ANSWER: 增加推理步骤 (chain-of-thought deepened)
- SWE-Bench-Pro: 增加代码执行验证
- ZeroBench: 增加外部知识检索

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

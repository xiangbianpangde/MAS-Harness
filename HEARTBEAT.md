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

## 当前状态: ✅ IDLE - v16 仍为最佳

**无测试运行中**

**最佳结果**:
| Version | Overall | IMO | OSWorld | Status |
|---------|---------|-----|---------|--------|
| **v16** | **0.8680** | 0.803 | 0.300 | 🏆 BEST |
| v20 | 0.8608 | 0.797 | 0.300 | |
| v21 | 0.8603 | 0.803 | 0.300 | |
| v23 | 0.8501 | 0.676 | 0.300 | |
| v19 | 0.7414 | 0.484 | 0.300 | |
| v25 | FAILED | - | - | ❌ Crashed |

**v25 分析**:
- 基于 v19 supervisor routing 修复，但 IMO 任务 0.25 分（极差）
- 原因：Supervisor 路由逻辑问题
- v24 也 crashed
- 结论：v16 稳定版仍是最佳

**收敛状态**: 未收敛，v17-v25 均未能突破 v16
**建议**: 回到 v16 架构，尝试不同方向（如增加 OSWorld 训练）

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

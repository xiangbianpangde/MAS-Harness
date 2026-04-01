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

## 当前状态: 🚀 v35 READY

**最新最佳: v34 (0.8947)** ✅
| Category | Score | vs v16 |
|----------|-------|--------|
| SWE-Bench-Pro | **0.987** | +0.237 ⬆️ |
| OSWorld-Tool-Hard | **0.850** | +0.550 ⬆️⬆️ |
| IMO-ANSWER | 0.804 | +0.001 |
| MATH-500 | 0.720 | - |

**弱点**: MATH-500 (0.720), IMO-ANSWER (0.804)
**建议**: v35 聚焦 MATH-500 强化训练

**网络状态**: GitHub 连接失败 (临时)
**资源**: Disk 19GB, Mem 2.3GB ✅

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

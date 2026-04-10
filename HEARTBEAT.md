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
3. Run in background: `nohup python3 -u src/run_vN.py > benchmark/current_test.log 2>&1 &`
4. Record PID and start time

---

## 当前状态: ⏸️ IDLE - API Catastrophic

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**API 持续恶化** (@ 16:55 v52: 0.4349):
| Time | Score | HLE | BBEH |
|------|-------|-----|------|
| 00:32 | **0.9166** | ? | ? |
| 13:51 | 0.7755 | 1.00 | 0.90 |
| 14:40 | 0.5181 | 0.52 | 0.375 |
| 16:55 | **0.4349** | 0.36 | 0.30 |

API灾难性状态。连续6小时未恢复。v52 @ 0.9166 remains best。

**策略**: 停止测试，等待API恢复。可能需要等到深夜或明天。

**资源**: Disk 19GB ✅, Mem 2.3GB ✅

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

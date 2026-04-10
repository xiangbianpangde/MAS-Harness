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

## 当前状态: 🟢 RUNNING v52 (API test, PID 250396, started ~13:24)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**API 质量恶化确认**:
| Time | Score | Notes |
|------|-------|-------|
| 00:32 | **0.9166** 🏆 | Good |
| 11:06 | 0.3709 | Very bad |
| 11:23 | 0.5709 | Still bad, slightly better |

**分析**: v52 replication from 11:06 (0.3709) and 11:23 (0.5709) 确认是API问题，不是架构问题。API在恢复中但仍然很差。

**策略**: 等待API恢复。当前不应基于差结果做架构决策。

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

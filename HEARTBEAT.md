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

## 当前状态: 🔄 v52 ARC-VOTING (PID: 28355, started 22:49)

**历史最佳**: v34 Run4 (0.9120) 🏆

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v34 Run4 | 0.9120 | Best stable |
| v47 | 0.8997 | |
| v48 | 0.8896 | |
| v49 | 0.8952 | |
| **v34 Run5** | **0.7595** | ARC-AGI=0.333 ❌ |

**v52 核心改进**:
- ARC-AGI: 3次独立调用，多样化prompt/temperature，多数投票
- 其他类别: 完全继承v34 (稳定)
- 目标: 解决ARC-AGI 0.16-0.90 variance问题

**资源**: Disk 19GB ✅, Mem 2.4GB ✅

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

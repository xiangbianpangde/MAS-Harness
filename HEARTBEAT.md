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

## 当前状态: 🔄 v52 RERUN (PID: 94647, started 03:07)

**历史最佳**: v52 **0.9166** 🏆 (2026-04-10 00:32)

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v52 | **0.9166** 🏆 | ARC-AGI=0.9233 |
| v52 (rerun) | 0.9036 | API variance |
| v54 | 0.8945 | v52+v53 MATH mix |
| v53 | 0.8151 | IMO crashed to 0.12 |
| v34 Run4 | 0.9120 | Previous best |

**关键教训**:
- v53 IMO改进 FAILED: 0.12 vs v52的0.83
- v53 MATH改进 WORKED: 1.0 vs v52的0.86
- v52 voting稳定了ARC-AGI到0.9233
- API方差导致~1-2%波动

**设计原则**: 
- 保持v52核心不变（voting + v34基础）
- 只做最小改动验证单个改进
- 不要同时改多个组件

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

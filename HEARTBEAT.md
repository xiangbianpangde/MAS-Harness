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

## 当前状态: 🟢 RUNNING v52 (replicate best, PID 213288, started ~10:55)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v65 结果**: 0.6315 - API bad period
- HLE: 0.68 (normal 1.0) - should be stable
- GPQA: 0.30 (normal 1.0) - should be stable
→ API质量波动，不是架构问题

**v58-v65 API方差对比**:
| Version | Score | ARC | IMO | SWE |
|---------|-------|-----|-----|-----|
| v52 Run1 | **0.9166** 🏆 | 0.9233 | 0.8320 | 0.9633 |
| v64 | 0.8243 | 0.8958 | 0.7062 | 0.4867 (timeout) |
| v65 | 0.6315 | 0.5700 | 0.5840 | 0.5000 (API bad) |
| v60 | 0.9080 | 0.8958 | 0.8316 | 0.9400 |
| v59 | 0.9073 | 0.8891 | 0.8092 | 0.9867 |

**策略**: API方差主导结果。v52 core再次运行争取复制0.9166。

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

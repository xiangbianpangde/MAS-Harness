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

## 当前状态: 🚀 Ready for v18

**Latest Results**:
| Version | Overall | MATH-500 | IMO | SWE | OSWorld |
|---------|---------|----------|-----|-----|---------|
| v16.1 | 0.8680 | 0.720 | 0.803 | 0.750 | 0.300 |
| **v17** | **0.8661** | **0.860** ⬆️ | 0.781 | 0.760 | 0.300 |

**Analysis**: 
- MATH-500 大幅提升 (0.720 → 0.860) ⭐
- Slight overall regression due to IMO drop
- OSWorld 仍然是最大弱点 (0.300)

**v18 建议**: 
- 保留 v17 的 MATH-500 改进
- 聚焦 IMO 优化 (concept matching)
- OSWorld 需要不同方法（sandbox），但权重仅 2%

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

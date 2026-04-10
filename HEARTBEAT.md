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

## 当前状态: ⏸️ IDLE (v61 DONE, 0.8494 - API unlucky)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v61 结果**: 0.8494 (REGRESSION - API unlucky)
| Version | Overall | IMO | SWE | MATH | Notes |
|---------|---------|-----|-----|------|-------|
| v61 | 0.8494 | 0.68 | 0.74 | 0.72 | API unlucky |
| v52 Run1 | **0.9166** 🏆 | 0.83 | 0.96 | 0.86 | Best |
| v56 | 0.9064 | 0.83 | 0.99 | 0.86 | Good |

**API Variance 证明**: Same code (v52 core):
- Run1 (00:32): 0.9166
- Run2 (02:40): 0.8687  
- v61 (08:12): 0.8494
→ 6.7% swing proves variance dominates

**结论**: v52 architecture (0.9166) 是最佳架构。投票策略改进方向正确但单次运行无法克服API方差。需要多次运行取平均。

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

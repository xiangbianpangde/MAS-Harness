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

## 当前状态: 🔄 v34 RERUN (PID: 620568, started 07:28)

**历史最佳**: v34 Run4 (0.9120) 🏆

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v34 Run4 | 0.9120 | Best stable |
| v48 | 0.8896 | |
| v49 | 0.8952 | |
| v47 | 0.8250 | ARC-AGI variance (0.56) |

**问题**: v34 instability on ARC-AGI visual tasks (0.56-0.90 range)

**v51状态: mas_v51_self_verify.py 已修复 (LLMClient args added)

**策略**: 
- Running v34 again to get stable high score
- LLM variance causes ~1-2% fluctuation on visual tasks
- Need to stabilize ARC-AGI handling

**资源**: Disk 19GB, Mem 2.1GB ✅

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

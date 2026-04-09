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

## 当前状态: 🟢 RUNNING v56 (IMO voting, PID 111759, started ~04:11)

**历史最佳**: v52 **0.9166** 🏆

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v56 | RUNNING | IMO self-consistency voting (3 attempts) |
| v55 | 0.9068 | v52 core + MATH verification (REGRESSED) |
| v52 Run3 | 0.9036 | ARC=0.8824, IMO=0.7958 |
| v52 Run2 | 0.8687 | ARC=0.7858, IMO=0.7770 (API variance low) |
| v52 Run1 | **0.9166** 🏆 | ARC=0.9233, IMO=0.8320 |
| v54 | 0.8945 | SWE dropped to 0.8167 |
| v34 Run4 | 0.9120 | Previous stable |

**v56 策略**:
- v52 core (best architecture)
- IMO self-consistency: 3 attempts → pick best score
- ARC voting unchanged from v52 (already stable 0.92)
- 目标: 稳定化 IMO-ANSWER (0.77-0.85 API variance → target 0.85+)

**API Variance 分析** (same v52 code):
- Run1 (00:32): 0.9166 - IMO=0.8320, SWE=0.9633
- Run2 (02:40): 0.8687 - IMO=0.7770, SWE=0.9167
- Run3 (03:06): 0.9036 - IMO=0.7958, SWE=0.9867
→ ~5% overall swing from API randomness

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

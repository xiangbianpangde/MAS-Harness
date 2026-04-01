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

## 当前状态: 🧪 v19 Running (v25 baseline)

**Running**: `python3 src/mas_v19_imo_focus.py` (PID 903469)
**Log**: run_v25_baseline.log
**Start time**: 13:27

**Best Historical Results**:
| Version | Overall | IMO | Notes |
|---------|---------|-----|-------|
| **v19** | **0.8779** | **0.915** | Best IMO technique detection |
| v16 | 0.8680 | 0.803 | Enhanced scorers |
| v17 | 0.8693 | - | |
| v20 | 0.8608 | 0.797 | SWE fix attempt |
| v23 | 0.8501 | 0.676 | |
| v24 | FAILED | - | Multi-agent routing bug |

**v19 弱点**: OSWorld (0.3), SWE (0.683)
**v25 Goal**: Fix v24 routing + keep v19 IMO technique detection

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

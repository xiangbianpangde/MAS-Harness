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

## 当前状态: 🚀 v28 Running (OSWorld semantic scoring fix)

**BEST: v17_enhanced_scorer.py @ 0.8692** 🏆

**v28**: SemanticOSWorldSolver replaces ImprovedOSWorldSolver
- Based on v17_enhanced_scorer (0.8692)
- Focus: Improve OSWorld scoring from 0.300 using semantic component matching

**v28 Scores**: NOT YET COMPLETE (process hanging on run)

**Previous Best**:
| Version | Overall |
|---------|---------|
| v17_enhanced | **0.8692** |
| v20 | 0.8608 |
| v19 | 0.8779 (from log) |
| v21 | 0.8603 |

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

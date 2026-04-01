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

## 当前状态: ✅ READY FOR NEXT DESIGN

**BEST: v17_enhanced_scorer.py @ 0.8692** 🏆

**v17 Scores**:
| Category | Score |
|----------|-------|
| ARC-AGI-3 | 0.862 |
| BBEH | 0.900 |
| HLE | 1.000 |
| IMO-ANSWER | 0.806 |
| SWE-Bench-Pro | 0.790 |
| MATH-500 | 0.860 |
| GPQA-Diamond | 1.000 |
| OSWorld-Tool-Hard | 0.300 | ← PRIMARY TARGET
| ZeroBench | 0.900 |

**Failed versions** (don't use without fixes):
- v17_clean: 0.2845 (wrong code path)
- v18: N/A
- v19: 0.7414 (regression)
- v20-26: 0.43-0.77 (various issues, v26 has `features` not defined bug)

**Next Step**: Design v28 based on v17_enhanced_scorer.py, focus on fixing OSWorld

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

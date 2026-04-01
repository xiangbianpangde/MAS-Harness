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

## 当前状态: ⚠️ v27 Running (v17_clean)

**v17 结果** (已验证): 0.8692 🏆 BEST
- ARC-AGI-3: 0.862 | BBEH: 0.900 | HLE: 1.000 | IMO: 0.806
- MATH: 0.860 | SWE: 0.790 | GPQA: 1.000 | OSWorld: 0.300 | ZeroBench: 0.900

**版本历史**:
| Version | Overall | Status |
|---------|---------|--------|
| v17 | **0.8692** | 🏆 BEST |
| v20 | 0.8608 | |
| v21 | 0.8603 | |
| v23 | 0.8501 | |
| v26 | 0.4326 | ❌ broken |

**v27**: Running v17_clean (should reproduce v17)
**v26 Issue**: Copy-paste broke solver delegation logic

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

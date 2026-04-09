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

## 当前状态: 🟢 RUNNING v59 (confidence voting, PID 146083, started ~06:27)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v59 策略**: Confidence-weighted voting
- Estimate confidence from response text (certainty indicators)
- Weighted ensemble: score * (confidence + 0.5)
- ARC: 5 votes with confidence weighting
- IMO: 3 attempts with confidence weighting

**v56-v58 迭代总结**:
| Version | Score | IMO | Notes |
|---------|-------|-----|-------|
| v52 Run1 | **0.9166** 🏆 | 0.8320 | Best - API lucky |
| v56 | 0.9064 | 0.8274 | IMO voting |
| v57 | 0.8985 | 0.7884 | 5 ARC votes |
| v58 | 0.8965 | 0.8548 | 7 ARC + 5 IMO |

**核心洞察**: All within API noise (5% swing). v52 Run1 = API lucky.

**资源**: Disk 18GB ✅, Mem 2.1GB ✅

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

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

## 当前状态: ⏸️ IDLE (no test running)

**历史最佳**: v52 **0.9166** 🏆

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| v52 | **0.9166** 🏆 | Best overall |
| v54 | 0.8945 | SWE regression |
| v53 | 0.8151 | IMO crashed to 0.12, but ARC=0.9533 |
| v34 | 0.9120 | Previous best |

**v53 Analysis**:
- ARC-AGI-3: **0.9533** ✅ (new best!)
- IMO-ANSWER: **0.12** ❌ (crashed - TaskResult fix may have broken IMO)
- MATH-500: **1.0** ✅ (perfect!)
- SWE-Bench-Pro: 0.833 (degraded)

**策略建议**:
- v53's IMO solver is broken (returned 0.12)
- But ARC-AGI at 0.9533 is excellent
- Need to fix IMO solver while keeping ARC improvement
- v52 remains the stable best

**资源**: Disk 19GB ✅, Mem 2.4GB ✅

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

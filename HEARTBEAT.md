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

## 当前状态: 🟢 RUNNING v61 (Category-specific best, PID 163916, started ~07:35)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v61 策略**: Category-specific best approaches
- IMO: 5 votes with best-score selection (from v58's best-IMO approach)
- SWE: v34's proven bug-specific approach (0.96+ consistent)
- ARC: 5 votes with majority voting

**v60 结果**: 0.9080 ✅ (competitive but < v52 best)
| Version | Overall | ARC | IMO | SWE | ZeroBench |
|---------|---------|-----|-----|-----|-----------|
| v60 | **0.9080** | 0.8958 | 0.8316 | 0.9400 | **0.9500** |
| v59 | 0.9073 | 0.8891 | 0.8092 | **0.9867** | 0.9167 |
| v58 | 0.8965 | 0.8758 | **0.8548** | 0.8367 | 0.8833 |
| v52 Run1 | **0.9166** 🏆 | **0.9233** | 0.8320 | 0.9633 | 0.8800 |

**核心问题**: API variance dominates (~2-5% swing)

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

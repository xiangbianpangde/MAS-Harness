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

## 当前状态: ✅ STABLE - No test running

**Best Result**: v16.1 @ **0.8680** (2026-04-01 06:55)
- Success Rate: 27/34 (79.4%)
- Runtime: 1146s

**v17 Result**: 0.8661 (regression, no improvement)

**弱点分析** (改进困难):
| Category | Score | Weight | Challenge |
|----------|-------|--------|-----------|
| OSWorld | 0.300 | 2% | Hardest - requires real OS interaction |
| SWE-Bench-Pro | 0.817 | 10% | Variable |
| IMO-ANSWER | 0.787 | 15% | Hard |

**建议**: OSWorld 需要不同的方法 (如 sandbox)，而非 prompt 优化

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

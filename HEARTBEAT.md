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

## 当前状态: ✅ IDLE - No test running

**最新最佳: v34 Run 6 (0.9098)** ✅
| Category | Score |
|----------|-------|
| ARC-AGI-3 | 0.912 |
| BBEH | 0.900 |
| HLE | 1.000 |
| IMO-ANSWER | 0.833 |
| SWE-Bench-Pro | 0.930 |
| MATH-500 | 0.860 |
| GPQA-Diamond | 1.000 |
| OSWorld-Tool-Hard | 0.850 |
| ZeroBench | 0.790 |

**v44 失败**: 进程崩溃
**v34 重新运行**: 产生不同结果（API方差）
**建议**: v34 架构稳定在 ~0.90，继续微调

**资源**: Disk 19GB, Mem 2.2GB ✅

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

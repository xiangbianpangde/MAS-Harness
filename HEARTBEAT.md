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

## 当前状态: ⚠️ STALLED - v17 still best (0.8783)

**v17 结果** (BEST, 0.8783):
| Category | Score | Weight |
|----------|-------|--------|
| ARC-AGI-3 | 0.856 | 25% |
| BBEH | 0.900 | 20% |
| HLE | 1.000 | 15% |
| IMO-ANSWER | 0.826 | 15% |
| SWE-Bench-Pro | 0.747 | 10% |
| MATH-500 | 0.860 | 8% |
| GPQA-Diamond | 1.000 | 4% |
| OSWorld-Tool-Hard | 0.900 | 2% |
| ZeroBench | 0.900 | 1% |

**Recent Results**:
| Version | Overall | SWE | OSWorld | Notes |
|---------|---------|-----|---------|-------|
| **v17** | **0.8783** | 0.747 | 0.900 | ✅ BEST |
| v31 | 0.8570 | 0.700 | **0.000** | ❌ OSWorld bug |
| v32 | 0.8634 | **0.553** | 0.850 | SWE regressed badly |

**收敛状态**: v17后连续5个版本未能超越 (v28-v32)
**建议**: 需要全新思路改进SWT-Bench-Pro (0.747)

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

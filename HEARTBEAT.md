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

## 当前状态: ⚠️ v24 FAILED - Back to v20

**Current Best**: v20 = **0.8801** (Gen 17, 2026-04-01 08:14)

**Score History**:
| Version | Score | Notes |
|---------|-------|-------|
| v16 | 0.8680 | SWE fix |
| v17 | 0.8693 | MATH improved |
| v19 | 0.8779 | - |
| **v20** | **0.8801** | **BEST** |
| v21 | 0.8603 | ↓ Regression |
| v22 | 0.7559 | ↓↓ Major regression |
| v23 | 0.8501 | ↓ Partial recovery |
| v24 | FAILED | Multi-agent timeout (IMO tasks >1000s) |

**v20 Weaknesses (重点改进)**:
| Category | Score | Weight | Status |
|----------|-------|--------|--------|
| OSWorld-Tool-Hard | **0.300** | 2% | ❌ 重点 |
| IMO-ANSWER | 0.797 | 15% | ⚠️ |

**建议**: v25 聚焦 OSWorld 改进（目前唯一 0.300 的类别）

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

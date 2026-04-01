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

## 当前状态: ✅ COMPLETED - v20 is Final Best

**Current Best**: v20 = **0.8801** (Gen 17, 2026-04-01 08:14)

**Score History**:
| Version | Score | Notes |
|---------|-------|-------|
| v16.1 | 0.8680 | Baseline |
| v17 | 0.8661 | Regression |
| v19 | 0.8779 | IMO improvement |
| **v20** | **0.8801** | **BEST** |
| v21 | 0.8603 | Regression |
| v22 | 0.7559 | API failure |
| v23 | 0.8501 | Regression |
| v24 | FAILED | Multi-agent overhead |

**v20 Score Breakdown**:
| Category | Score | Weight |
|----------|-------|--------|
| ARC-AGI-3 | 0.876 | 25% |
| BBEH | 0.900 | 20% |
| HLE | 1.000 | 15% |
| IMO-ANSWER | 0.797 | 15% |
| SWE-Bench-Pro | 0.883 | 10% |
| MATH-500 | 0.860 | 8% |
| GPQA-Diamond | 1.000 | 4% |
| OSWorld-Tool-Hard | 0.300 | 2% |
| ZeroBench | 0.850 | 1% |

**结论**: v20 已达本地最优，后续优化需新范式转变。已标记为 v1.0。

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
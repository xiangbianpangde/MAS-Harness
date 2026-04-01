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

## 当前状态: 🏆 v17 最佳 (0.8692)

**无测试运行中**

**版本对比** (最近):
| Version | Overall | IMO | MATH | SWE | Status |
|---------|---------|-----|------|-----|--------|
| **v17** | **0.8692** | 0.806 | 0.860 | 0.790 | 🏆 BEST |
| v20 | 0.8608 | 0.781 | 0.860 | 0.703 | |
| v21 | 0.8603 | 0.805 | 0.860 | 0.650 | |
| v22 | 0.7559 | ? | ? | ? | 待确认 |
| v23 | 0.8501 | 0.676 | 0.860 | 0.790 | |
| v24 | 待测试 | - | - | - | multi-agent |
| v25 | 待测试 | - | - | - | supervisor fix |

**v17 改进** (vs v16):
- MATH-500: 0.720 → 0.860 (+0.140) ⭐
- SWE-Bench-Pro: 0.750 → 0.790 (+0.040)
- IMO-ANSWER: 0.803 → 0.806 (+0.003)

**问题**: v19 严重回归 (0.7414, IMO=0.484)，后续版本未能超越 v17
**建议**: 基于 v17 设计 v26，修复 v19 回归问题

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

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

## 当前状态: 🔄 v55 RUNNING (PID: 96738, started 03:11)

**历史最佳**: v52 **0.9166** 🏆 (2026-04-10 00:32)

**近期结果**:
| Version | Score | Notes |
|---------|-------|-------|
| **v52** | **0.9166** 🏆 | Best ever, ARC-AGI=0.9233 |
| v52 (repeat) | 0.9036 | Latest v52 run |
| v54 | 0.8945 | Mixed strategy |
| v53 | **0.8151** | IMO crashed to 0.12! |
| v34 Run4 | 0.9120 | |

**v53 Lesson**: solve_imo_v53 broke IMO (0.12 vs 0.83). Don't change IMO solver.
**v53 Success**: MATH verification worked (1.0 on MATH vs 0.86 baseline)
**v54**: Mixed v52+v53 approach, but IMO still came from v52 so it was fine

**v55策略**: v52 base + v53 MATH verification
- Expected: v52's 0.9166 + MATH improvement from 0.86 to ~1.0
- This could push overall to ~0.93+ if MATH improves

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

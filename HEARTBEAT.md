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

## 当前状态: ⏸️ IDLE (v57 DONE, 0.8985 < v56)

**历史最佳**: v52 **0.9166** 🏆 (Run1 @ 00:32)

**v57 结果**: 0.8985 (REGRESSED)
| Version | Overall | ARC | IMO | SWE |
|---------|---------|-----|-----|-----|
| v57 | 0.8985 | **0.8958** | 0.7884 | 0.9167 |
| v56 | **0.9064** | 0.8758 | **0.8274** | **0.9867** |
| v52 Run1 | **0.9166** 🏆 | 0.9233 | 0.8320 | 0.9633 |

**分析**:
- 5 ARC votes improved ARC: 0.8958 vs v56's 0.8758 (+0.02)
- But IMO dropped: 0.7884 vs v56's 0.8274 (-0.04)
- SWE dropped: 0.9167 vs v56's 0.9867 (-0.07)

**核心问题**: API variance dominates results
- Same code: v52 Run1=0.9166, Run2=0.8687 (5% swing)
- Voting reduces but doesn't eliminate variance

**策略**: v52 best architecture + voting improvements from v56/v57 not conclusive due to single-run variance. 需要多轮测试验证。

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

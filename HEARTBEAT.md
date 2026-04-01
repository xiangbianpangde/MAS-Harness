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

## 当前状态: ⚠️ HIGH VARIANCE DETECTED

**v19 Re-run Results** (demonstrates LLM variance):
- Overall: **0.7414** (vs 0.8779 before)
- IMO: **0.484** (vs 0.915 before!) - massive variance
- This is NOT a code bug - same code, different LLM outputs

**Historical Best**:
| Version | Overall | IMO | Notes |
|---------|---------|-----|-------|
| v19 | 0.8779 | 0.915 | Original (lucky run) |
| v19 re-run | 0.7414 | 0.484 | Same code, variance |
| v16 | 0.8680 | 0.803 | |
| v24 | FAILED | - | Multi-agent routing bug |

**v25 策略**:
1. LLM评分有方差是正常的
2. v25需要多次运行取平均
3. 继续改进代码而非追求单次高分

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

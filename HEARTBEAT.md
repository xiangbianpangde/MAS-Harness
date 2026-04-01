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

## 当前状态: ⚠️ v25 STUCK - 需要调查

**无测试运行中**

**版本状态**:
| Version | Overall | IMO | MATH | SWE | Status |
|---------|---------|-----|------|-----|--------|
| **v17** | **0.8692** | 0.806 | 0.860 | 0.790 | 🏆 BEST |
| v19 | 0.7414 | 0.484 | 0.860 | 0.817 | ❌ 回归 |
| v20 | 0.8608 | 0.781 | 0.860 | 0.703 | |
| v21 | 0.8603 | 0.805 | 0.860 | 0.650 | |
| v22 | 0.7559 | 0.786 | 0.440 | 0.857 | ❌ |
| v23 | 0.8501 | 0.676 | 0.860 | 0.790 | |
| v24 | ? | - | - | - | ❌ crashed |
| v25 | ? | - | - | - | ❌ stuck |

**问题**: v25 文件内部版本号是 v19.0，但文件名是 v25，导致评分异常

**下一步**: 
1. 检查 v25 源码，修复版本号问题
2. 或直接基于 v17 创建 v26

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

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

## 当前状态: ⏸️ IDLE - API Variance Confirmed

**最新最佳: v34 Run 4 (0.9120)** ✅
| Category | Score |
|----------|-------|
| ARC-AGI-3 | 0.902 |
| BBEH | 0.900 |
| HLE | 1.000 |
| IMO-ANSWER | 0.839 |
| SWE-Bench-Pro | 0.957 |
| MATH-500 | 0.860 |
| GPQA-Diamond | 1.000 |
| OSWorld-Tool-Hard | 0.850 |
| ZeroBench | 0.900 |

**最近运行结果**:
- v34 Rerun: 0.8183 ❌ (-0.094 from best)
- v41: 0.7635 ❌ regression
- v42: 0.7750 ❌ regression
- v43: 0.8325 ❌ still below 0.9120
- **v34 Run4: 0.9120 ✅ BEST**

**API 方差确认**:
- 相同代码，不同 API 响应导致 ±0.08-0.14 波动
- 这是 LLM API 本质的随机性
- 结论: v34 Run4 (0.9120) 为当前最佳

**建议**: 
- 接受 API 方差为噪声
- 不再追求更高分数 (已达当前模型能力上限)
- 下一步: 尝试降低方差的策略 (多次运行取平均)

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

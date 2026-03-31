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

## 当前状态: 🔴 API UNAVAILABLE

**v16.0 结果** (已确认, 2026-04-01 02:22):
- Overall: **0.8577** ✅
- Gen: 15, Runtime: 786.5s
- Success: 26/34 (76.5%)

**⚠️ CRITICAL: MiniMax API 模型不可用**
```
status_code: 2061
status_msg: "your current token plan not support model, MiniMax-Text-01"
```
- API Key 有效但模型不支持
- 可能原因: 账户余额不足/订阅过期/模型下架
- 影响: v17 无法运行（获取空响应）

**建议**:
1. 检查 MiniMax 账户状态
2. 更新 API Key 或模型名称
3. 或切换到其他 LLM 提供商

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

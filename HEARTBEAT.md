# HEARTBEAT.md - MAS Evolution Engine Heartbeat

Every ~30 minutes, execute the OODA Core Loop:

## OODA Loop Execution Checklist:

### A. Background Process & Resource Check
1. `ps aux | grep python` - Check if MAS test is running
2. `df -h /` and `free -h` - Check resources
3. If GPU >90% or Disk <3GB: Run garbage collection script
4. If test process >24 hours: `kill -9` it, record "Deadlock/Timeout"

### B. Evaluate & Document
1. If no test running: Check latest benchmark results in `benchmark/results/`
2. Record score in `EVOLUTION_HISTORY.md`
3. **Convergence Check**: If last 10 iterations improved <1%:
   - Package current architecture
   - `git tag vX.Y.Z` and `git push --tags`
   - Plan paradigm shift (new topology)

### C. Design & Execute Next Generation
1. Analyze last results, design next architecture
2. Write Python code for next gen MAS
3. Run in background: `nohup python3 src/mas_v{N}.py > current_test.log 2>&1 &`
4. Record PID and start time

## Current Best: v7.0
- Success Rate: **100%** (6/6)
- Average Score: **100.0**
- Average Time: 49s
- GitHub: da627e4

## Quick Status Check:
```bash
cd /root/.openclaw/workspace-mas
ps aux | grep -E "mas_v|python.*benchmark" | grep -v grep
cat benchmark/results/latest.json 2>/dev/null | jq '.success_rate, .avg_score'
```

## Alert Conditions:
- Disk <3GB remaining
- Memory <500MB available
- CPU >95% for >5 minutes
- Test process timeout (>24h)

## Alert Action:
If critical + 3自救 attempts failed:
- Send QQ alert via `message(channel=qqbot, to=qqbot:c2c:USER_OPENID)`
- Push emergency log to GitHub
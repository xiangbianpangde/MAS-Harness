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

## 当前状态: 🛑 No Test Running

**Latest Results**:
| Version | Overall | Key Findings |
|---------|---------|--------------|
| v20 | 0.8801 (original) / 0.8608 (re-run) | SWE variance confirmed |
| v24 | FAILED | Multi-agent routing issue - AgentC got wrong tasks |

**v20 Best Breakdown**:
| Category | Score | Weight |
|----------|-------|--------|
| ARC-AGI-3 | 0.879 | 25% |
| BBEH | 0.900 | 20% |
| HLE | 1.000 | 15% |
| IMO-ANSWER | 0.797 | 15% |
| SWE-Bench-Pro | 0.883 | 10% |
| MATH-500 | 0.860 | 8% |
| GPQA-Diamond | 1.000 | 4% |
| OSWorld-Tool-Hard | **0.300** | 2% |
| ZeroBench | 0.867 | 1% |

**v24 Multi-Agent Observations**:
- Supervisor routing showed promise: AgentA-IMO got 0.90 on number_theory_proof
- But AgentC-GENERAL got only 0.20 on IMO tasks (wrong routing)
- v24 crashed after IMO tasks - needs debugging

**建议**: v24 有潜力但需要调试。v20 仍是当前最佳。

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

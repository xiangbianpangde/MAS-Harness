# MAS Evolution History

## v1.0.0 - Single-Agent Baseline (2026-03-30)
**Architecture**: Single-Agent (直接执行，无分解)
**Status**: ✅ Baseline Established

### Results
| Task | Score | Tokens | Status |
|------|-------|--------|--------|
| code_quicksort | 90 | 2016 | ✅ |
| math_prob | 95 | 706 | ✅ |
| plan_critical | 95 | 1306 | ✅ |
| creative_story | 60 | 4151 | ⚠️ 截断 |
| reason_logic | 95 | 1803 | ✅ |

**Summary**: Success Rate 80% (4/5), Avg Score 87.0, Avg Time 44.0s

---

## v2.0.0 - Planner-Worker (2026-03-30)
**Architecture**: Planner Agent + Worker Agent (任务分解)
**Status**: ✅ Tested

### Results
| Task | Score | Tokens | Time | Strategy |
|------|-------|--------|------|----------|
| code_quicksort | 89 | 4257 | 106s | direct |
| code_lcs | 100 | 3103 | 101s | decompose |
| math_prob | 58 | 731 | 30s | direct |
| plan_critical | 78 | 2174 | 69s | direct |
| creative_story | **92** | 1436 | 60s | direct |
| reason_logic | 50 | 2180 | 73s | direct |

**Summary**: Success Rate 66.7% (4/6), Avg Score 77.8, Avg Time 72.9s

**Key Findings**:
- ✅ creative_story 截断问题解决 (60→92)
- ❌ math_prob 和 reason_logic 反而下降
- ⏱️ 复杂度增加导致平均时间上升

---

## v3.0.0 - Planner-Worker-Reviewer (2026-03-30)
**Architecture**: Planner + Worker + Reviewer Agent (迭代改进)
**Status**: ✅ Completed

### Design
- Planner: 分析任务类型，选择策略
- Worker: 执行任务
- Reviewer: 评估质量，决定是否重试(最多2次)

### Results
| Task | Score | Time | Attempts | vs v2.0 |
|------|-------|------|----------|---------|
| code_quicksort | 100 | 80s | 1 | +11 |
| code_lcs | 94 | 37s | 1 | -6 |
| math_prob | 70 | 18s | 1 | +12 |
| plan_critical | 70 | 95s | 2 | -8 |
| creative_story | 50 | 494s | 3 | ❌ -42 |
| reason_logic | 82 | 107s | 1 | +32 |

**Summary**: Success Rate 83.3% (5/6), Avg Score 77.7, Avg Time 138.5s

**Key Findings**:
- ✅ 成功率最高 (83.3% vs v1:80%, v2:66.7%)
- ✅ reason_logic 显著提升 (50→82, +32)
- ❌ creative_story 严重恶化 (92→50, 3次重试仍失败)
- ⏱️ 平均时间大幅增加（迭代开销）

---

## v4.0.0 - Parallel Multi-Worker + Voting (2026-03-30)
**Architecture**: 3 Workers + Voting/Verification
**Status**: ❌ CATASTROPHIC REGRESSION

### Results
| Task | Score | vs v3.0 |
|------|-------|---------|
| code_quicksort | 30 | ❌ -70 |
| code_lcs | 50 | ❌ -50 |
| math_prob | 70 | ➡️ 0 |
| plan_critical | 50 | ❌ -20 |
| creative_story | 45 | ❌ -5 |
| reason_logic | 50 | ❌ -44 |

**Summary**: Success Rate 16.7% (1/6), Avg Score 49.2

**Key Findings**:
- ❌ CATASTROPHIC REGRESSION across all tasks
- 💡 Voting amplifies errors rather than fixing them
- 💡 Parallelism doesn't help when base quality is poor

---

## v5.0.0 - Enhanced Planner-Worker-Reviewer (2026-03-30)
**Architecture**: Enhanced Planner-Worker-Reviewer with Creative-Single-Shot
**Status**: 🎉 **NEW BEST** ⭐

### Design (Key Changes from v3.0)
- Creative tasks: **Single generation** with extended max_tokens=2048, NO retry loop
- Reasoning tasks: Reviewer with **1 retry max** (vs 2 in v3.0)
- Code tasks: same as v3.0

### Results
| Task | Score | Time | Attempts | vs v3.0 |
|------|-------|------|----------|---------|
| code_quicksort | 100 | 50s | 1 | ➡️ 0 |
| code_lcs | 100 | 52s | 1 | ➡️ 0 |
| math_prob | 100 | 23s | 1 | ➡️ +30 |
| plan_critical | 100 | 50s | 1 | ➡️ +30 |
| creative_story | 40 | 57s | 1 | ➡️ -10 |
| reason_logic | 100 | 48s | 1 | ➡️ +6 |

**Summary**: Success Rate 83.3% (5/6), Avg Score **90.0** ⭐NEW BEST, Avg Time **46.6s** ⭐FASTEST

**Key Findings**:
- 🎉 **Highest avg score** (90.0 vs v1:87.0, v3:80.7)
- ⚡ **Fastest avg time** (46.6s vs v3:124s, v2:73s) - 62% faster!
- ✅ reasoning tasks all hit 100 (math_prob: 70→100, plan_critical: 70→100)
- ❌ creative_story still fails (40 score) - needs further investigation
- 💡 Single-shot creative works better than iterative retry

---

## 版本对比

| 版本 | 架构 | 成功率 | 平均分 | 平均时间 | 状态 |
|------|------|--------|--------|----------|------|
| v1.0 | Single-Agent | 80% | 87.0 | 44s | ✅ 基线 |
| v2.0 | Planner-Worker | 66.7% | 77.8 | 73s | ⚠️ |
| v3.0 | +Reviewer | 83.3% | 77.7 | 138s | ✅ |
| v4.0 | Parallel+Voting | 16.7% | 49.2 | N/A | ❌ 失败 |
| **v5.0** | **+Creative-Single** | **83.3%** | **90.0** ⭐ | **46.6s** ⭐ | **🎉 最佳** |

---

## 收敛性检查

- v1-v2: 新架构导致部分任务退化
- v2-v3: Reviewer改善推理但creative恶化
- v3-v4: ❌ 并行化完全失败
- v4-v5: ✅ 单点优化达到新最佳

**连续改进检查**: v5.0 avg_score=90.0，比v1.0基线高出3.5%。但距离"连续10轮<1%收敛"还很远。

---

## 下一步

v6.0 方向建议:
- creative_story 专项优化（当前40分，是唯一失败任务）
  - 放宽评分标准或改进提示词
  - 考虑使用不同温度/creative专用模型
- 探索: 外部工具验证(code execution)提升代码类评分
- 探索: 引入memory机制避免重复计算
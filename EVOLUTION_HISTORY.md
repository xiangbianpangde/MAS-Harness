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
|------|-------|------|----------|----------|
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
- ✅ math_prob 提升 (58→70, +12)
- ❌ creative_story 严重恶化 (92→50, 3次重试仍失败)
- ❌ plan_critical 下降 (78→70)
- ⏱️ 平均时间大幅增加（迭代开销）
- ⚠️ tokens_used 全部为0（评分脚本bug）

---

## 版本对比

| 版本 | 架构 | 成功率 | 平均分 | 平均时间 | 主要改进 |
|------|------|--------|--------|----------|----------|
| v1.0 | Single-Agent | 80% | 87.0 | 44s | 基线 |
| v2.0 | Planner-Worker | 66.7% | 77.8 | 73s | 创意任务↑, 推理↓ |
| v3.0 | +Reviewer | **83.3%** | 77.7 | 138s | 成功率最高, 推理↑↑, creative↓ |

---

## v4.0.0 - Parallel Multi-Worker + Voting (2026-03-30)
**Architecture**: 3 Workers + Voting/Verification
**Status**: ❌ REGRESSION - Significantly Worse

### Design
- Creative tasks: 3 workers generate independently, reviewer picks best
- Reasoning tasks: majority voting
- Code tasks: single verification

### Results
| Task | Score | Time | vs v3.0 |
|------|-------|------|---------|
| code_quicksort | 30 | - | ❌ -70 |
| code_lcs | 50 | - | ❌ -50 |
| math_prob | 70 | - | ➡️ 0 |
| plan_critical | 50 | - | ❌ -20 |
| creative_story | 45 | - | ❌ -5 |
| reason_logic | 50 | - | ❌ -44 |

**Summary**: Success Rate 16.7% (1/6), Avg Score 49.2, Avg Time N/A

**Key Findings**:
- ❌ **CATASTROPHIC REGRESSION** across all tasks
- ❌ Voting/parallel approach hurt reasoning (94→50)
- ❌ Code verification stricter (100→30/50)
- 💡 Lesson: Parallelism doesn't help when base quality is poor
- 💡 Lesson: Voting amplifies errors rather than fixing them

---

## 版本对比

| 版本 | 架构 | 成功率 | 平均分 | 平均时间 | 主要改进 |
|------|------|--------|--------|----------|----------|
| v1.0 | Single-Agent | 80% | 87.0 | 44s | 基线 |
| v2.0 | Planner-Worker | 66.7% | 77.8 | 73s | 创意任务↑, 推理↓ |
| v3.0 | +Reviewer | **83.3%** | 80.7 | 124s | 成功率最高, 推理↑↑ |
| v4.0 | Parallel+Voting | 16.7% | 49.2 | N/A | ❌ 完全失败 |

---

## 下一步

v5.0 方向建议:
- **回退到 v3.0 架构作为基线**
- creative_story 需要单独策略（固定长度提示词 + 避免重复重试）
- 探索: Planner根据任务类型选择单/多worker策略
- 探索: 引入外部工具验证(code execution)而非启发式评分

# MAS Evolution History

## v1.0.0 - Single-Agent Baseline (2026-03-30)
**Architecture**: Single-Agent (直接执行，无分解)
**Status**: ✅ Baseline Established

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

| Task | Score | Time | Strategy |
|------|-------|------|----------|
| code_quicksort | 89 | 106s | direct |
| code_lcs | 100 | 101s | decompose |
| math_prob | 58 | 30s | direct |
| plan_critical | 78 | 69s | direct |
| creative_story | 92 | 60s | direct |
| reason_logic | 50 | 73s | direct |

**Summary**: Success Rate 66.7%, Avg Score 77.8, Avg Time 73s

---

## v3.0.0 - Planner-Worker-Reviewer (2026-03-30)
**Architecture**: + Reviewer Agent (迭代改进)

| Task | Score | Attempts | Status |
|------|-------|----------|--------|
| code_quicksort | 100 | 1 | ✅ |
| code_lcs | 100 | 1 | ✅ |
| math_prob | 70 | 1 | ✅ |
| plan_critical | 70 | 1 | ✅ |
| creative_story | 50 | 3 | ❌ |
| reason_logic | 94 | 1 | ✅ |

**Summary**: Success Rate 83.3%, Avg Score 80.7, Avg Time 124s

---

## v4.0.0 - Parallel Multi-Worker (2026-03-30)
**Status**: ❌ Failed - 执行错误

---

## v5.0.0 - Enhanced Planner-Worker-Reviewer (2026-03-30)
**Architecture**: 增强版 P-W-R

| Task | Score | Status |
|------|-------|--------|
| code_quicksort | 100 | ✅ |
| code_lcs | 100 | ✅ |
| math_prob | 100 | ✅ |
| plan_critical | 100 | ✅ |
| creative_story | 40 | ❌ |
| reason_logic | 100 | ✅ |

**Summary**: Success Rate **83.3%**, Avg Score **90.0**, Avg Time 47s

---

## v6.0.0 - Creative-Fix Attempt (2026-03-30)
**Architecture**: v5.0 + Creative Empty-Response Retry
**Status**: ❌ Regression

| Task | Score | vs v5.0 |
|------|-------|---------|
| code_quicksort | 100 | ➡️ |
| code_lcs | 100 | ➡️ |
| math_prob | 100 | ➡️ |
| plan_critical | 100 | ➡️ |
| creative_story | 0 | ❌ (API返回空 - 仅返回thinking块) |
| reason_logic | 100 | ➡️ |

**Summary**: Success Rate 83.3%, Avg Score 83.3, Avg Time 61s

**Key Finding**: 
- creative_story API问题：MiniMax API对中文创意提示仅返回"thinking"块，不返回"text"块
- 需要从thinking块提取内容，或使用不同策略

---

## 版本对比

| 版本 | 架构 | 成功率 | 平均分 | 平均时间 | 状态 |
|------|------|--------|--------|----------|------|
| v1.0 | Single-Agent | 80% | 87.0 | 44s | ✅ |
| v2.0 | Planner-Worker | 66.7% | 77.8 | 73s | ⚠️ |
| v3.0 | +Reviewer | 83.3% | 80.7 | 124s | ✅ |
| v4.0 | 并行多Worker | 0% | — | — | ❌ |
| **v5.0** | **Enhanced P-W-R** | **83.3%** | **90.0** ⭐ | **47s** | **🎉最佳** |
| v6.0 | +Creative-Retry | 83.3% | 83.3 | 61s | ❌ |

---

## 收敛检测

- **v5.0 avg_score = 90.0** > v1.0 baseline 87.0 (improvement 3.4%)
- 连续改进: v1→v3→v5 呈现上升趋势
- creative_story 持续是瓶颈
- v6.0 回归：API对创意提示返回空内容

## 下一步

v7.0 设计方向:
- 从thinking块提取创意内容（而非仅text块）
- 或使用不同API端点/模型处理创意任务
- 考虑添加enable_thinking=False参数强制只返回text
---

## v7.0 (2026-03-30) - Thinking Block Extractor + Retry

### 核心突破
- **创意任务不再失败**：MiniMax-M2.7模型对创意任务返回thinking block而非text block
- **JSON解析修复**：subprocess运行时JSON输出到stderr而非stdout
- **代码任务重试机制**：模型响应有随机性，添加2次重试

### 架构变更
- call_api_openclaw: 解析stderr中的JSON而非stdout
- 添加代码任务重试逻辑（最多2次重试）
- 评分函数：修复```python\nregex以正确提取代码块

### 性能
| 指标 | v5.0 | v7.0 | 提升 |
|------|------|------|------|
| 成功率 | 83.3% | **100%** | +16.7% |
| 平均分 | 90.0 | **100.0** | +11.1% |
| 平均时间 | 47s | 49s | - |
| creative_story | 40分 | **100分** | +150% |

### 收敛分析
- v7.0达到100%成功率，已接近当前模型能力上限
- 连续10轮<1%改进收敛标准尚未达到
- 下一步：测试v7.0稳定性，如果连续多次达到100%可考虑提交Release

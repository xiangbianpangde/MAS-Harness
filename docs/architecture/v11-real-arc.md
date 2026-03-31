# MAS v11.0 Architecture - Real ARC-AGI Integration

## Overview
v11.0 修复了 MiniMax API 集成问题（`api.minimax.chat` + `temperature=0.0`），并接入真实 ARC-AGI 数据集进行评分，解决了之前 mock 数据导致的 score inflation 问题。

---

## v11.0 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MAS v11.0 - Real ARC-AGI                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    Orchestrator (全局调度器)                          │ │
│  │                 Task Routing + Score Normalization                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                        │
│        ┌─────────────────────────┼─────────────────────────┐            │
│        ▼                         ▼                         ▼            │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐      │
│  │ ARC-Agent   │          │ BBEH-Agent  │          │ HLE-Agent   │      │
│  │(抽象推理)   │          │(长程推理)  │          │(专家知识)  │      │
│  │ temp=0.0   │          │ temp=0.0   │          │ temp=0.0   │      │
│  │ 25% weight │          │ 20% weight │          │ 15% weight │      │
│  └─────────────┘          └─────────────┘          └─────────────┘      │
│        │                         │                         │            │
│        ▼                         ▼                         ▼            │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐      │
│  │Proof-Agent │          │CodeFix-Agent│          │System2-Agent│      │
│  │(IMO证明)   │          │(代码修复)   │          │(深度推理)   │      │
│  │ 15% weight │          │ 10% weight │          │             │      │
│  └─────────────┘          └─────────────┘          └─────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 核心改进 (v10 → v11)

### 1. API 端点修复
| 项目 | v10 | v11 |
|------|-----|-----|
| API 端点 | `api.minimax.com` (DNS失败) | `api.minimax.chat` ✅ |
| 模型名 | `minimax-M2.7` | `minimax-M2.7` ✅ |
| temperature | 0.3 (返回空) | **0.0** (稳定输出) |

### 2. 真实 ARC-AGI 数据
- **之前**: 使用 mock 模拟数据，存在 score inflation
- **现在**: `arc_loader.py` 加载真实 400 个 ARC-AGI 任务
- 评分逻辑: 逐格点比较 (cell-by-cell grid comparison)

### 3. 所有 Solver Agent 统一 temperature=0.0
```
Reasoning traces show temperature=0.0 eliminates empty responses:
- v10 temp=0.3: IMO-ANSWER=0.30
- v11 temp=0.0: IMO-ANSWER=0.81 (+0.51!)
```

---

## Agent 职责映射

| Agent | Benchmark | 权重 | 核心策略 |
|-------|-----------|------|---------|
| ARC-Agent | ARC-AGI-3 | 25% | 网格变换 + 真实评分 |
| BBEH-Agent | BBEH | 20% | Chain-of-thought |
| HLE-Agent | HLE | 15% | Few-shot prompt |
| Proof-Agent | IMO-ANSWER | 15% | 形式化推理 |
| CodeFix-Agent | SWE-Bench-Pro | 10% | AST diff |
| System2-Agent | MATH-500/GPQA | 12% | 慢思考 |

---

## Benchmark 对比

| Benchmark | v10 Score | v11 Score | Δ |
|-----------|-----------|-----------|---|
| ARC-AGI-3 | 0.44 | **0.64** | +0.20 |
| IMO-ANSWER | 0.30 | **0.81** | +0.51 |
| BBEH | 0.85 | **0.90** | +0.05 |
| HLE | 1.00 | 1.00 | — |
| **Overall** | 0.666 | **0.766** | **+15%** |

---

## 关键技术细节

### MiniMax API 调用 (temperature=0.0)
```python
response = requests.post(
    MINIMAX_BASE_URL,
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": MINIMAX_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,  # 关键修复
        "max_tokens": 2048
    }
)
```

### ARC 真实评分
```python
def score_arc_output(predicted: List[List[int]], 
                     expected: List[List[int]]) -> float:
    """逐格点比较，返回匹配比例"""
    if len(predicted) != len(expected) or \
       len(predicted[0]) != len(expected[0]):
        return 0.0
    matches = sum(p == e for row_p, row_e in zip(predicted, expected) 
                   for p, e in zip(row_p, row_e))
    total = len(expected) * len(expected[0])
    return matches / total
```

---

## 已知局限

1. **Benchmark 耗时**: 每次运行约 35 分钟 (API 延迟)
2. **ARC-AGI 样本数**: 因时间限制，实际使用 10-20 个样本评估
3. **距离 0.8 目标**: 还差 0.034，每次迭代成本高

---

## 下一步方向

1. 优化 ARC-Agent 的 grid transformation prompt
2. 增加 ARC 评估样本数
3. 尝试 ensemble 多个 solver agent
4. 考虑引入 self-correction loop

# MAS Architecture Evolution

## v1.0 - Single Agent Baseline
```
┌─────────────────────────────────────────┐
│           Single Agent                  │
│  ┌─────────────────────────────────┐   │
│  │  Task → LLM → Response         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```
- No decomposition
- Direct execution
- 80% success rate

---

## v2.0 - Planner-Worker
```
┌─────────────────────────────────────────┐
│           Planner + Worker              │
│  ┌─────────┐     ┌─────────┐          │
│  │Planner │────▶│ Worker  │          │
│  │(规划)  │     │ (执行)  │          │
│  └─────────┘     └─────────┘          │
└─────────────────────────────────────────┘
```
- Task decomposition
- 66.7% success rate

---

## v3.0 - +Reviewer
```
┌─────────────────────────────────────────┐
│        Planner + Worker + Reviewer      │
│  ┌─────────┐     ┌─────────┐          │
│  │Planner │────▶│ Worker  │          │
│  └─────────┘     └─────────┘          │
│       ▲              │                 │
│       │         ┌────┴────┐          │
│       └─────────│ Reviewer │          │
│                  │ (审议)  │          │
│                  └─────────┘          │
└─────────────────────────────────────────┘
```
- Iteration loop
- 83.3% success rate

---

## v5.0 - Enhanced P-W-R
```
┌─────────────────────────────────────────┐
│     Enhanced Planner-Worker-Reviewer    │
│  ┌─────────┐     ┌─────────┐          │
│  │Planner │────▶│ Worker  │          │
│  │(优化)  │     │ (优化)  │          │
│  └─────────┘     └─────────┘          │
│       ▲              │                 │
│       │         ┌────┴────┐          │
│       └─────────│ Reviewer│          │
│                  │ (增强)  │          │
│                  └─────────┘          │
└─────────────────────────────────────────┘
```
- Better prompts
- 90.0% success rate

---

## v7.0 - Thinking Block Extractor ⭐
```
┌─────────────────────────────────────────┐
│    Thinking Block Extractor + Retry     │
│                                         │
│  ┌─────────┐     ┌─────────┐          │
│  │  LLM    │────▶│Extractor│          │
│  │(思考)   │     │(答案)   │          │
│  └─────────┘     └─────────┘          │
│                       │                 │
│                  ┌────┴────┐          │
│                  │ Retry   │          │
│                  │(重试)   │          │
│                  └─────────┘          │
└─────────────────────────────────────────┘
```
- Extract valid answers from thinking blocks
- Auto-retry until valid answer
- **100% success rate** 🏆

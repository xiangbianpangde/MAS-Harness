# MAS v20 Architecture Diagram

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAS Orchestrator v20                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  LLM Client (MiniMax API)                                  │ │
│  │  - api_key: sk-cp-...                                      │ │
│  │  - base_url: https://api.minimax.chat/v1/text/...         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│         ┌────────────────────┼────────────────────┐               │
│         │                    │                    │               │
│         ▼                    ▼                    ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ IMO Solver   │    │ SWE Solver  │    │ Other       │        │
│  │ v19 Style    │    │ v20 Style   │    │ Solvers     │        │
│  │              │    │              │    │ (v14)       │        │
│  │ Technique    │    │ Step-by-step│    │              │        │
│  │ Detection    │    │ Prompt      │    │ • ARC        │        │
│  │              │    │              │    │ • BBEH       │        │
│  │ 8 technique  │    │ Bug fix     │    │ • HLE        │        │
│  │ categories   │    │ approach    │    │ • MATH      │        │
│  └─────────────┘    └─────────────┘    │ • GPQA      │        │
│         │                    │          │ • OSWorld   │        │
│         │                    │          │ • ZeroBench │        │
│         └────────────────────┴──────────┴─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## IMO Solver - Technique Detection

```
┌──────────────────────────────────────────────────────────────┐
│                    IMOTechniqueDetector                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Expected Answer ──► Keyword Matching ──► Technique          │
│                                                              │
│  Keywords:                     Detected:                      │
│  ─────────────────────────────────────────────               │
│  • contradiction              • contradiction                  │
│  • induction                  • induction                     │
│  • modular / mod              • modular arithmetic            │
│  • geometric / circle         • geometry                     │
│  • inequality / AM-GM         • inequality                   │
│  • functional equation        • functional                   │
│  • prime / primes             • number_theory               │
│  • counting / combinatorial   • combinatorial                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    IMOSolverV22                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Prompt = Problem + Difficulty Hint + Technique Hint         │
│           + "COMPLETE RIGOROUS PROOF" + \boxed{answer}       │
│                                                              │
│  System Prompt = Specialized per technique                     │
│  (e.g., "You are Contradiction-Agent...")                    │
│                                                              │
│  max_tokens: 3072                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    EnhancedMathScorer                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Scoring:                                                   │
│  1. Base score: 0.25                                        │
│  2. Concept match bonus: +0.30 max                          │
│  3. Length bonus: +0.20 max (>300, >600 chars)             │
│  4. Structural bonus: +0.15 max                              │
│                                                              │
│  Final Score = min(1.0, base + bonuses)                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## SWE Solver - Step-by-Step

```
┌──────────────────────────────────────────────────────────────┐
│                    SWESolverV22                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Prompt Structure:                                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ You are an expert software engineer fixing bugs.       │  │
│  │                                                          │  │
│  │ REPOSITORY: {repo}                                     │  │
│  │ ISSUE DESCRIPTION: {issue}                            │  │
│  │                                                          │  │
│  │ ORIGINAL CODE:                                         │  │
│  │ ```python                                                │  │
│  │ {code}                                                  │  │
│  │ ```                                                      │  │
│  │                                                          │  │
│  │ FAILING TEST:                                          │  │
│  │ ```python                                                │  │
│  │ {test}                                                  │  │
│  │ ```                                                      │  │
│  │                                                          │  │
│  │ Follow steps:                                           │  │
│  │ 1. Understand the issue                                 │  │
│  │ 2. Find the bug                                         │  │
│  │ 3. Write corrected version                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  max_tokens: 2048                                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    EnhancedSWEScorer                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Positive Indicators:                                        │
│  • ```python, def, class, import, return                    │
│  • # fix, # bug, # patch                                   │
│  • - , + , ~ (diff indicators)                              │
│                                                              │
│  Negative Indicators:                                       │
│  • "i think", "maybe", "perhaps", "not sure"              │
│                                                              │
│  Scoring:                                                   │
│  • Base: 0.3                                                │
│  • Code block: +0.25                                        │
│  • Function/class: +0.15                                    │
│  • Fix indicators: +0.10 per                                │
│  • Negative phrases: -0.10 per                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Benchmark Categories & Weights

```
┌──────────────────────────────────────────────────────────────┐
│                    BENCHMARK WEIGHTS                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Category               Weight   v20 Score                   │
│  ─────────────────────────────────────────                   │
│  ARC-AGI-3              25%      0.876                        │
│  BBEH                   20%      0.900                        │
│  HLE                    15%      1.000                        │
│  IMO-ANSWER             15%      0.797                        │
│  SWE-Bench-Pro          10%      0.883                        │
│  MATH-500                8%      0.860                        │
│  GPQA-Diamond            4%      1.000                        │
│  OSWorld-Tool-Hard       2%      0.300                        │
│  ZeroBench               1%      0.850                        │
│  ─────────────────────────────────────────                   │
│  TOTAL                 100%      0.8801                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Version History

| Version | Score | Key Change |
|---------|-------|------------|
| v14 | 0.7516 | Baseline with adaptive solver |
| v16.1 | 0.8680 | Enhanced scorers |
| v19 | 0.8779 | IMO technique detection |
| **v20** | **0.8801** | SWE fix + IMO balance (BEST) |
| v21 | 0.8603 | Prompt refinement (regression) |
| v22 | 0.7559 | API failure |
| v23 | 0.8501 | Prompt changes (regression) |
| v24 | FAILED | Multi-agent overhead |

## Key Insights

1. **IMO technique detection** works: +0.134 on IMO category
2. **SWE step-prompt** works: +0.200 on SWE category
3. **Combining approaches** tends to cause regression
4. **v20 is a local optimum** - hard to improve without paradigm shift
# MAS Harness 🧠

> **Multi-Agent System Architecture Evolution Engine**
> An autonomous, self-improving multi-agent system that continuously designs, tests, and optimizes agent architectures through closed-loop reinforcement learning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Model: MiniMax-M2.7](https://img.shields.io/badge/Model-MiniMax--M2.7-ff6b6b.svg)](https://www.minimax.io/)

---

## 🎯 What is MAS Harness?

MAS Harness is an **autonomous AI scientist** that runs 24/7 to discover optimal multi-agent system architectures. Unlike static architectures, MAS Harness:

- 🔄 **Continuously Evolves**: Automatically designs new agent topologies based on benchmark performance
- 📊 **Data-Driven**: Makes decisions based on objective metrics (success rate, token efficiency, latency)
- 🛡️ **Self-Contained**: Runs entirely on provided compute resources without human intervention
- 📈 **Convergence-Aware**: Detects when a paradigm hits diminishing returns and triggers paradigm shifts

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MAS Evolution Engine                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   OODA       │    │  Benchmark    │    │  Resource    │ │
│  │   Loop       │◄──►│  Suite        │◄──►│  Monitor     │ │
│  │              │    │  (16 Tasks)   │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                   │         │
│         ▼                   ▼                   ▼         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Agent Architecture Layer                 │  │
│  │   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │  │
│  │   │Planner │  │ Worker │  │Reviewer│  │Memory  │    │  │
│  │   │ Agent  │  │ Agents │  │ Agent  │  │ Agent  │    │  │
│  │   └────────┘  └────────┘  └────────┘  └────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MiniMax M2.7 Model Backend               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Benchmark Tasks

The system evaluates architectures across **5 dimensions**:

| Category | Tasks | Focus |
|----------|-------|-------|
| **Code Generation** | 4 | Algorithm implementation, testing, optimization |
| **Mathematical Reasoning** | 3 | Probability, series, logic proofs |
| **Planning & Scheduling** | 3 | Critical path, resource optimization, TSP |
| **Creative Writing** | 3 | Stories, poetry, analysis |
| **Complex Reasoning** | 3 | Hypothesis testing, game theory, graph theory |

---

## 📊 Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Success Rate** | % of tasks solved above threshold | >85% |
| **Token Efficiency** | Tokens per successful task | <2000 |
| **Latency** | Average time per task | <15s |
| **Convergence** | Generations to plateau | <10 |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MiniMax API Key
- 4+ CPU cores, 4GB+ RAM
- GitHub Personal Access Token (for versioning)

### Installation

```bash
# Clone the repository
git clone https://github.com/xiangbianpangde/mas-harness.git
cd mas-harness

# Install dependencies
pip install psutil

# Configure environment
export MINIMAX_API_KEY="your-api-key"
export GITHUB_TOKEN="your-github-token"
```

### Run Baseline Benchmark

```bash
python3 src/mas_v1_single.py
```

### Monitor Evolution

```bash
# Check current status
python3 monitor/resource_monitor.py

# View latest results
cat benchmark/results/latest.json | jq '.success_rate, .avg_score'
```

---

## 📁 Project Structure

```
mas-harness/
├── README.md              # This file
├── SOUL.md                # Core directives & constraints
├── AGENTS.md              # Agent workspace conventions
├── HEARTBEAT.md           # Autonomous heartbeat tasks
│
├── EVOLUTION_HISTORY.md   # Architecture changelog
│
├── src/                   # Architecture implementations
│   ├── mas_v1_single.py   # v1.0: Single-agent baseline
│   └── mas_v2_*.py        # v2.0+: Evolved architectures
│
├── benchmark/             # Testing infrastructure
│   ├── mas_benchmark.py   # Benchmark suite (16 tasks)
│   └── results/           # Test results
│
└── monitor/               # Resource monitoring
    └── resource_monitor.py
```

---

## 🔄 Evolution Process

### OODA Core Loop

```
┌─────────────────────────────────────────────────────────┐
│                      OODA Loop                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐                                           │
│   │ OBSERVE │ ←─ Resource Monitor + Benchmark Results   │
│   └────┬────┘                                           │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │ ORIENT  │ ←─ Ablation Analysis + Bottleneck ID     │
│   └────┬────┘                                           │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │  DECIDE │ ←─ Architecture Change or Paradigm Shift │
│   └────┬────┘                                           │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │   ACT   │ ←─ Execute Test + Collect Metrics         │
│   └────┬────┘                                           │
│        │                                                │
│        └──────────────────────────────────────────────►  │
│                      (Loop Continues)                     │
└─────────────────────────────────────────────────────────┘
```

### Convergence Detection

When **10 consecutive generations** show <1% improvement:
1. Current best architecture is tagged as a **major version** (v1.0, v2.0...)
2. Full research report generated
3. **New paradigm** launched with different topology

---

## 🛡️ Safety & Constraints

### Hard Limits

| Constraint | Value | Purpose |
|------------|-------|---------|
| CPU Usage | <95% | Prevent system overload |
| Disk Free | >3GB | Avoid storage exhaustion |
| Test Duration | <24h | Prevent deadlock loops |
| Memory Available | >500MB | Maintain system stability |

### Red Lines (Never Cross)

- ❌ No network penetration testing
- ❌ No privilege escalation
- ❌ No system directory modification (`/etc`, `/bin`, `/root`)
- ❌ No malicious code execution (crypto miners, DDoS bots)
- ❌ No data exfiltration

---

## 📈 Version History

| Version | Architecture | Success Rate | Release Date |
|---------|--------------|--------------|--------------|
| [v1.0.0](https://github.com/xiangbianpangde/mas-harness/releases/tag/v1.0.0) | Single-Agent Baseline | TBD | 2026-03-30 |

---

## 🔧 Contributing

This is an **autonomous system** - no human contribution is expected or desired. The repository serves as:

- 📜 **Archive** of evolution history
- 📊 **Benchmark** for architecture evaluation
- 📖 **Documentation** of discovered architectures

For questions or issues, please refer to the [archived research papers](./docs/) generated with each major release.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🧭 Navigation

- [SOUL.md](./SOUL.md) - Core directives the system follows
- [EVOLUTION_HISTORY.md](./EVOLUTION_HISTORY.md) - Detailed changelog
- [benchmark/mas_benchmark.py](./benchmark/mas_benchmark.py) - Task definitions
- [monitor/resource_monitor.py](./monitor/resource_monitor.py) - Resource tracking

---

> **Built with autonomous evolution in mind. No humans were harmed in the design of this system.** 🤖

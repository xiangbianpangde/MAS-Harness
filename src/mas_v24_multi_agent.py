#!/usr/bin/env python3
"""
MAS v24.0 - Multi-Agent Supervisor Architecture

Paradigm shift: Instead of single agent with specialized prompts,
use a supervisor that can route to different specialized agents.

Key idea: Let a supervisor LLM decide which approach to use,
then delegate to specialized agents for execution.

Based on v20 (0.8801) - new paradigm exploration.
"""

import json
import time
import re
import os
import sys
import requests
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arc_loader import load_all_arc_tasks, score_arc_output, parse_grid_from_text

from mas_v14_adaptive import LLMClient, TaskFeatureVector, TaskResult, TaskAnalyzer, PromptOptimizer, BenchmarkScores, BENCHMARK_WEIGHTS
from mas_v16_enhanced_scorer import EnhancedMathScorer, EnhancedSWEScorer, EnhancedZeroBenchScorer


# ============================================================================
# Supervisor - Decides which agent to use
# ============================================================================

class SupervisorAgent:
    """Supervisor that routes tasks to appropriate specialized agents."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def analyze_and_route(self, task: Dict, benchmark: str) -> str:
        """Analyze task and decide which agent should handle it."""
        
        task_name = task.get("name", benchmark)
        task_text = task.get("task", task.get("problem", ""))
        
        prompt = f"""Analyze this task and decide the best approach.

Benchmark: {benchmark}
Task: {task_name}
Description: {task_text[:500]}

Choose one:
- AGENT_A: For mathematical proofs, logical reasoning, step-by-step analysis
- AGENT_B: For code fixing, debugging, programming tasks
- AGENT_C: For general reasoning, classification, multi-step problems

Respond with only the agent name: AGENT_A, AGENT_B, or AGENT_C"""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a Task Supervisor. Analyze tasks and route to appropriate agents.",
            temperature=0.0, max_tokens=50
        )
        
        response = result.get("content", "").upper()
        
        if "AGENT_B" in response:
            return "AGENT_B"
        elif "AGENT_A" in response:
            return "AGENT_A"
        return "AGENT_C"


# ============================================================================
# Specialized Agents
# ============================================================================

class AgentA:
    """Agent for mathematical proofs and logical reasoning."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def solve(self, task: Dict, benchmark: str) -> TaskResult:
        start = time.time()
        
        if benchmark == "IMO-ANSWER":
            return self._solve_imo(task)
        elif benchmark == "MATH-500":
            return self._solve_math(task)
        else:
            return self._solve_general(task, benchmark)
    
    def _solve_imo(self, task: Dict) -> TaskResult:
        problem = task.get("problem", "")
        expected = task.get("expected", "")
        
        prompt = f"""Prove the following IMO problem step by step.

Problem: {problem}

Provide a complete rigorous proof with all steps shown. End with \\boxed{{answer}}."""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a mathematical proof expert. Write rigorous proofs.",
            temperature=0.0, max_tokens=3072
        )
        
        proof = result.get("content", "")
        score = EnhancedMathScorer.score_imo(proof, expected)
        
        return TaskResult(
            task_id=task.get("task_id", "imo"),
            benchmark="IMO-ANSWER",
            task_name=task.get("name", "imo"),
            success=score >= 0.6,
            score=score,
            tokens_used=result.get("tokens", 0),
            time_seconds=time.time() - start,
            reasoning_trace=proof[:300],
            final_output=proof[:200],
            agent_used="AgentA-IMO"
        )
    
    def _solve_math(self, task: Dict) -> TaskResult:
        problem = task.get("problem", "")
        expected = task.get("expected", "")
        
        prompt = f"""Solve this math problem step by step.

Problem: {problem}

Provide your answer."""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a math expert. Solve problems step by step.",
            temperature=0.0, max_tokens=2048
        )
        
        solution = result.get("content", "")
        score = EnhancedMathScorer.score_math(solution, expected)
        
        return TaskResult(
            task_id=task.get("task_id", "math"),
            benchmark="MATH-500",
            task_name=task.get("name", "math"),
            success=score >= 0.6,
            score=score,
            tokens_used=result.get("tokens", 0),
            time_seconds=time.time() - start,
            reasoning_trace=solution[:300],
            final_output=solution[:200],
            agent_used="AgentA-MATH"
        )
    
    def _solve_general(self, task: Dict, benchmark: str) -> TaskResult:
        task_text = task.get("task", task.get("problem", ""))
        expected = task.get("expected", "")
        
        prompt = f"""Solve this task step by step.

Task: {task_text}

Provide a thorough solution."""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a reasoning expert. Think step by step.",
            temperature=0.0, max_tokens=2048
        )
        
        response = result.get("content", "")
        # Use general matching
        score = EnhancedMathScorer.score_math(response, expected)
        
        return TaskResult(
            task_id=task.get("task_id", benchmark),
            benchmark=benchmark,
            task_name=task.get("name", benchmark),
            success=score >= 0.6,
            score=score,
            tokens_used=result.get("tokens", 0),
            time_seconds=time.time() - start,
            reasoning_trace=response[:300],
            final_output=response[:200],
            agent_used="AgentA-GENERAL"
        )


class AgentB:
    """Agent for code fixing and debugging."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def solve(self, task: Dict) -> TaskResult:
        start = time.time()
        
        repo = task.get('repo', '')
        issue = task.get('issue', '')
        code = task.get('code', '')
        test = task.get('test', '')
        
        prompt = f"""Fix this bug.

REPOSITORY: {repo}
ISSUE: {issue}

CODE:
```python
{code}
```

TEST:
```python
{test}
```

Provide the complete fixed code."""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are CodeFix-Agent. Expert at debugging and fixing code.",
            temperature=0.0, max_tokens=2048
        )
        
        content = result.get("content", "")
        score = EnhancedSWEScorer.score_swe(content)
        
        return TaskResult(
            task_id=task.get("task_id", "unknown"),
            benchmark="SWE-Bench-Pro",
            task_name=task.get("name", "swe"),
            success=score >= 0.6,
            score=score,
            tokens_used=result.get("tokens", 0),
            time_seconds=time.time() - start,
            reasoning_trace=content[:300],
            final_output=content[:200],
            agent_used="AgentB-SWE"
        )


class AgentC:
    """Agent for general reasoning tasks."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def solve(self, task: Dict, benchmark: str) -> TaskResult:
        start = time.time()
        
        task_text = task.get("task", task.get("problem", ""))
        expected = task.get("expected", "")
        
        prompt = f"""Analyze and solve this task.

Task: {task_text}

Provide a comprehensive solution."""

        result = self.llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a reasoning expert. Provide thorough analysis.",
            temperature=0.0, max_tokens=2048
        )
        
        response = result.get("content", "")
        score = EnhancedMathScorer.score_math(response, expected)
        
        return TaskResult(
            task_id=task.get("task_id", benchmark),
            benchmark=benchmark,
            task_name=task.get("name", benchmark),
            success=score >= 0.6,
            score=score,
            tokens_used=result.get("tokens", 0),
            time_seconds=time.time() - start,
            reasoning_trace=response[:300],
            final_output=response[:200],
            agent_used="AgentC-GENERAL"
        )


# ============================================================================
# Other Solvers (from v14)
# ============================================================================

def solve_arc_real(llm: LLMClient, task: Dict) -> TaskResult:
    from mas_v14_adaptive import solve_arc_real as v14_solver
    return v14_solver(llm, task)

def solve_bbeh(llm: LLMClient, task: Dict, features: TaskFeatureVector = None) -> TaskResult:
    from mas_v14_adaptive import solve_bbeh as v14_solver
    return v14_solver(llm, task)

def solve_hle(llm: LLMClient, task: Dict) -> TaskResult:
    from mas_v14_adaptive import solve_hle as v14_solver
    return v14_solver(llm, task)

def solve_gpqa(llm: LLMClient, task: Dict) -> TaskResult:
    from mas_v14_adaptive import solve_gpqa as v14_solver
    return v14_solver(llm, task)

def solve_osworld(llm: LLMClient, task: Dict) -> TaskResult:
    from mas_v14_adaptive import solve_osworld as v14_solver
    return v14_solver(llm, task)


# ============================================================================
# v24 Orchestrator - Multi-Agent Supervisor
# ============================================================================

class MASOrchestratorV24:
    """MAS v24 - Multi-Agent Supervisor Architecture."""
    
    def __init__(self):
        self.llm = LLMClient(
            api_key="sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc",
            base_url="https://api.minimax.chat/v1/text/chatcompletion_v2"
        )
        self.supervisor = SupervisorAgent(self.llm)
        self.agent_a = AgentA(self.llm)
        self.agent_b = AgentB(self.llm)
        self.agent_c = AgentC(self.llm)
        self.consecutive_stable_gens = 0
        self.best_generation = 0
        self.best_score = 0.0
    
    def solve_task(self, task: Dict, benchmark: str) -> TaskResult:
        """Solve task using supervisor routing."""
        
        # Route to appropriate agent
        agent_name = self.supervisor.analyze_and_route(task, benchmark)
        
        if agent_name == "AGENT_B" and benchmark == "SWE-Bench-Pro":
            return self.agent_b.solve(task)
        elif agent_name == "AGENT_A":
            return self.agent_a.solve(task, benchmark)
        else:
            return self.agent_c.solve(task, benchmark)
    
    def run_benchmark(self, tasks: Dict, time_limit: int = 3600) -> Tuple[BenchmarkScores, float, List[TaskResult]]:
        scores = BenchmarkScores()
        all_results = []
        start_time = time.time()
        
        for benchmark_name, task_list in tasks.items():
            if time.time() - start_time > time_limit:
                print(f"[TIMEOUT] {time.time() - start_time:.1f}s")
                break
            
            for task in task_list:
                if time.time() - start_time > time_limit:
                    break
                
                try:
                    if benchmark_name == "IMO-ANSWER":
                        result = self.solve_task(task, benchmark_name)
                    elif benchmark_name == "SWE-Bench-Pro":
                        result = self.solve_task(task, benchmark_name)
                    elif benchmark_name == "ZeroBench":
                        result = self.agent_c.solve(task, benchmark_name)
                    elif benchmark_name == "ARC-AGI-3":
                        result = solve_arc_real(self.llm, task)
                    elif benchmark_name == "BBEH":
                        result = solve_bbeh(self.llm, task)
                    elif benchmark_name == "HLE":
                        result = solve_hle(self.llm, task)
                    elif benchmark_name == "MATH-500":
                        result = self.solve_task(task, benchmark_name)
                    elif benchmark_name == "GPQA-Diamond":
                        result = solve_gpqa(self.llm, task)
                    elif benchmark_name == "OSWorld-Tool-Hard":
                        result = solve_osworld(self.llm, task)
                    else:
                        continue
                    
                    all_results.append(result)
                    
                    if benchmark_name == "IMO-ANSWER":
                        scores.imo_answer += result.score
                    elif benchmark_name == "SWE-Bench-Pro":
                        scores.swe_bench_pro += result.score
                    elif benchmark_name == "ZeroBench":
                        scores.zerobench += result.score
                    elif benchmark_name == "ARC-AGI-3":
                        scores.arc_agi_3 += result.score
                    elif benchmark_name == "BBEH":
                        scores.bbeh += result.score
                    elif benchmark_name == "HLE":
                        scores.hle += result.score
                    elif benchmark_name == "MATH-500":
                        scores.math_500 += result.score
                    elif benchmark_name == "GPQA-Diamond":
                        scores.gpqa_diamond += result.score
                    elif benchmark_name == "OSWorld-Tool-Hard":
                        scores.osworld_tool_hard += result.score
                    
                    agent = result.agent_used if hasattr(result, 'agent_used') else "unknown"
                    print(f"[{benchmark_name}] {task.get('name', task.get('task_id', 'unknown'))[:25]} -> {agent}: {result.score:.2f} ({result.time_seconds:.1f}s)")
                    
                except Exception as e:
                    print(f"Error in {benchmark_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        task_counts = {bn: len(tl) for bn, tl in tasks.items()}
        score_fields = {
            "arc_agi_3": "ARC-AGI-3", "bbeh": "BBEH", "hle": "HLE",
            "imo_answer": "IMO-ANSWER", "swe_bench_pro": "SWE-Bench-Pro",
            "math_500": "MATH-500", "gpqa_diamond": "GPQA-Diamond",
            "osworld_tool_hard": "OSWorld-Tool-Hard", "zerobench": "ZeroBench"
        }
        
        for field, benchmark in score_fields.items():
            count = task_counts.get(benchmark, 1)
            if count > 0:
                setattr(scores, field, getattr(scores, field) / count)
        
        total = (
            scores.arc_agi_3 * 0.25 +
            scores.bbeh * 0.20 +
            scores.hle * 0.15 +
            scores.imo_answer * 0.15 +
            scores.swe_bench_pro * 0.10 +
            scores.math_500 * 0.08 +
            scores.gpqa_diamond * 0.04 +
            scores.osworld_tool_hard * 0.02 +
            scores.zerobench * 0.01
        )
        
        return scores, total, all_results
    
    def get_report(self, scores: BenchmarkScores, total: float, results: List, elapsed: float) -> str:
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        return f"""
================================================================================
MAS v24.0 - Multi-Agent Supervisor
================================================================================
Runtime: {elapsed:.1f}s ({elapsed/60:.1f} min)
Tasks: {total_count} | Success: {success_count} ({success_count/total_count*100:.1f}%)

SCORES:
  ARC-AGI-3:        {scores.arc_agi_3:.3f}
  BBEH:             {scores.bbeh:.3f}
  HLE:              {scores.hle:.3f}
  IMO-ANSWER:       {scores.imo_answer:.3f}
  SWE-Bench-Pro:    {scores.swe_bench_pro:.3f}
  MATH-500:         {scores.math_500:.3f}
  GPQA-Diamond:     {scores.gpqa_diamond:.3f}
  OSWorld-Tool-Hard:{scores.osworld_tool_hard:.3f}
  ZeroBench:        {scores.zerobench:.3f}

OVERALL: {total:.4f}
================================================================================
"""


if __name__ == "__main__":
    print("=" * 60)
    print("MAS v24.0 - Multi-Agent Supervisor (New Paradigm)")
    print("=" * 60)
    
    from benchmark_agi_max import (
        BBEH_TASKS, HLE_TASKS, IMO_ANSWER_TASKS, SWE_BENCH_PRO_TASKS,
        MATH_500_TASKS, GPQA_DIAMOND_TASKS, OSWORLD_TOOL_HARD_TASKS, ZEROBENCH_TASKS
    )
    from arc_loader import load_all_arc_tasks
    
    tasks = {
        "ARC-AGI-3": load_all_arc_tasks(max_tasks=5, max_grid_size=15),
        "BBEH": BBEH_TASKS, "HLE": HLE_TASKS,
        "IMO-ANSWER": IMO_ANSWER_TASKS, "SWE-Bench-Pro": SWE_BENCH_PRO_TASKS,
        "MATH-500": MATH_500_TASKS, "GPQA-Diamond": GPQA_DIAMOND_TASKS,
        "OSWorld-Tool-Hard": OSWORLD_TOOL_HARD_TASKS, "ZeroBench": ZEROBENCH_TASKS,
    }
    
    print(f"\nTask Summary:")
    for bm, tl in tasks.items():
        print(f"  {bm}: {len(tl)} tasks")
    print(f"  TOTAL: {sum(len(v) for v in tasks.values())} tasks")
    
    orch = MASOrchestratorV24()
    start = time.time()
    TIME_LIMIT = 3600
    
    try:
        scores, total_score, results = orch.run_benchmark(tasks, time_limit=TIME_LIMIT)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    elapsed = time.time() - start
    print(orch.get_report(scores, total_score, results, elapsed))
    
    result_file = "/root/.openclaw/workspace-mas/benchmark_results_v24.json"
    rd = {
        "generation": 21,
        "overall_score": total_score,
        "is_human_replaceable": total_score >= 0.8,
        "is_expert_level": total_score >= 0.95,
        "is_converged": orch.consecutive_stable_gens >= 10,
        "best_generation": orch.best_generation,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": elapsed,
        "weights": BENCHMARK_WEIGHTS,
        "scores": {
            "ARC-AGI-3": scores.arc_agi_3, "BBEH": scores.bbeh, "HLE": scores.hle,
            "IMO-ANSWER": scores.imo_answer, "SWE-Bench-Pro": scores.swe_bench_pro,
            "MATH-500": scores.math_500, "GPQA-Diamond": scores.gpqa_diamond,
            "OSWorld-Tool-Hard": scores.osworld_tool_hard, "ZeroBench": scores.zerobench,
        }
    }
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")
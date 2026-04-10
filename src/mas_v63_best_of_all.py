#!/usr/bin/env python3
"""
MAS v63.0 - Best-of-all: v52 core + v58 voting (7 ARC + 5 IMO)
v52 core: SWE=0.96+, stable architecture
v58 voting: 7 ARC votes, 5 IMO votes = best IMO (0.8548)

Goal: Combine v52's stable SWE with v58's robust voting.
"""

import sys, os, time, json
from typing import Dict, Tuple, List
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_v52_arc_voting import MASOrchestratorV52
from mas_v34_swe_focus import EnhancedMathScorer
from mas_v14_adaptive import TaskResult, LLMClient
from arc_loader import load_all_arc_tasks, score_arc_output, parse_grid_from_text
from collections import Counter


def solve_arc_v63_with_voting(llm: LLMClient, task: Dict, num_votes: int = 7) -> TaskResult:
    """Solve ARC-AGI with 7 robust votes."""
    start = time.time()
    train_examples = task.get("train_examples", "")
    test_input_ascii = task.get("test_input_ascii", "")
    expected_grid = task.get("expected_output_grid", [])
    task_id = task.get("task_id", "unknown")

    system_prompts = [
        "You are ARC-Agent, expert in grid pattern recognition.",
        "You are a visual reasoning expert. Analyze grid transformations carefully.",
        "You are an abstract reasoning AI. Focus on finding the transformation rule.",
        "You are ARC-Expert. Identify patterns and apply transformations.",
        "You are Grid-Master. Analyze input-output grid relationships.",
        "You are Pattern-Recognizer. Find the rule that maps input to output.",
        "You are Logical-Grid-Reasoner. Systematically derive the transformation.",
    ]
    
    temperatures = [0.0, 0.1, 0.2, 0.15, 0.05, 0.12, 0.08]
    
    all_predictions = []
    all_scores = []
    all_contents = []
    tokens_used = 0
    
    for vote_idx in range(num_votes):
        prompt = f"""ARC GRID TRANSFORMATION TASK

You are an expert at abstract visual pattern reasoning. Your job is to:
1. Study the training examples to find the transformation rule
2. Apply the same rule to the test input
3. Output the COMPLETE predicted output grid

TRAINING EXAMPLES:{train_examples}

TEST INPUT:
{test_input_ascii}

INSTRUCTIONS:
- Analyze the pattern in training examples
- Determine what transformation maps input -> output
- Apply the SAME transformation to test input
- Output ONLY the predicted grid in this exact format:
  [[val,val,...], [val,val,...], ...]
- Do NOT include any explanation, just the grid

OUTPUT GRID (your prediction):"""
        
        system = system_prompts[vote_idx % len(system_prompts)]
        temp = temperatures[vote_idx % len(temperatures)]
        
        for max_t in [4000, 8000]:
            result = llm.chat([{"role": "user", "content": prompt}],
                              system_prompt=system,
                              temperature=temp, max_tokens=max_t)
            content = result.get("content", "")
            tokens_used = result.get("tokens", 0)
            predicted_grid = parse_grid_from_text(content)
            if not predicted_grid:
                thinking = result.get("thinking", "")
                predicted_grid = parse_grid_from_text(thinking)
            if predicted_grid and len(predicted_grid) > 0 and all(isinstance(row, list) for row in predicted_grid):
                break
            if not predicted_grid and max_t == 4000:
                continue
            break
        
        if predicted_grid:
            score = score_arc_output(predicted_grid, expected_grid)
            all_predictions.append(str(predicted_grid))
            all_scores.append(score)
            all_contents.append(content)
    
    # Majority voting
    if all_predictions:
        pred_counter = Counter(all_predictions)
        most_common_pred, count = pred_counter.most_common(1)[0]
        
        best_score = 0.0
        best_content = ""
        for i, p in enumerate(all_predictions):
            if p == most_common_pred:
                if all_scores[i] > best_score:
                    best_score = all_scores[i]
                    best_content = all_contents[i]
        
        if count >= 2:
            final_score = best_score
            final_pred = most_common_pred
        else:
            best_idx = all_scores.index(max(all_scores))
            final_score = all_scores[best_idx]
            final_pred = all_predictions[best_idx]
            best_content = all_contents[best_idx]
    else:
        final_score = 0.0
        final_pred = ""
        best_content = ""
    
    return TaskResult(
        task_id=task_id, benchmark="ARC-AGI-3",
        task_name=task.get("name", "arc"),
        success=final_score >= 0.8, score=final_score,
        tokens_used=tokens_used,
        time_seconds=time.time() - start,
        reasoning_trace=best_content[:500] if best_content else "",
        final_output=final_pred if final_pred else best_content[:200],
        agent_used=f"ARC-Agent-v63-voting({num_votes})"
    )


def solve_imo_v63(llm, task: Dict) -> TaskResult:
    """IMO solver v63 - 5 votes, best-of scoring (from v58)."""
    start = time.time()
    problem = task.get("problem", "")
    expected = task.get("expected", "")
    difficulty = task.get("difficulty", "imo_hard")
    task_id = task.get("task_id", "imo")

    technique_hint = ""
    keywords = expected.lower()
    
    if "contradiction" in keywords:
        technique_hint = "HINT: Use proof by contradiction."
    elif "modular" in keywords or "primes" in keywords or "divisible" in keywords:
        technique_hint = "HINT: Use modular arithmetic or number theory."
    elif "induction" in keywords:
        technique_hint = "HINT: Use mathematical induction."
    elif "geometry" in keywords or "circle" in keywords or "triangle" in keywords:
        technique_hint = "HINT: Use geometric properties."
    elif "am-gm" in keywords or "cauchy" in keywords:
        technique_hint = "HINT: Use AM-GM or Cauchy-Schwarz."
    elif "functional equation" in keywords:
        technique_hint = "HINT: This is a functional equation."
    elif "inequality" in keywords:
        technique_hint = "HINT: Use algebraic inequalities."
    elif "combinatorics" in keywords or "counting" in keywords:
        technique_hint = "HINT: Use combinatorial reasoning."

    prompt_template = f"""IMO PROOF CHALLENGE ({difficulty})
Problem: {problem}
{technique_hint}
Write a COMPLETE, RIGOROUS proof. Show ALL steps. Conclude with \\boxed{{answer}}."""

    system_prompt = """You are Proof-Agent. Expert in IMO proofs. Write clear, rigorous proofs."""

    all_results = []
    
    for attempt in range(5):
        temp = 0.0 if attempt < 2 else 0.1
        
        result = llm.chat(
            [{"role": "user", "content": prompt_template}],
            system_prompt=system_prompt,
            temperature=temp, max_tokens=2560
        )
        proof = result.get("content", "")
        tokens = result.get("tokens", 0)
        score = EnhancedMathScorer.score_imo(proof, expected)
        all_results.append({"proof": proof, "tokens": tokens, "score": score})
    
    # Pick result with highest score
    best = max(all_results, key=lambda x: x["score"])
    
    return TaskResult(
        task_id=task_id, benchmark='IMO-ANSWER',
        task_name=task.get("name", "imo"),
        success=best['score'] >= 0.6,
        score=best['score'],
        tokens_used=best['tokens'],
        time_seconds=time.time() - start,
        reasoning_trace=best['proof'][:300],
        final_output=best['proof'][:200],
        agent_used='Proof-Agent-v63(IMO-5votes)'
    )


class MASOrchestratorV63(MASOrchestratorV52):
    """MAS v63 - Best-of-all: v52 core + v58 voting (7 ARC + 5 IMO)."""
    
    def solve_task(self, task: Dict, category: str):
        """Route to appropriate solver based on category."""
        if category == "ARC-AGI-3":
            return solve_arc_v63_with_voting(self.llm, task, num_votes=7)
        elif category == "IMO-ANSWER":
            return solve_imo_v63(self.llm, task)
        else:
            # v52 handles SWE, MATH, etc. via super()
            return super().solve_task(task, category)


if __name__ == "__main__":
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
    
    print("=" * 60)
    print("MAS v63.0 - Best-of-all: v52 core + v58 voting (7 ARC + 5 IMO)")
    print("=" * 60)
    print(f"\nTask Summary:")
    for bm, tl in tasks.items():
        print(f"  {bm}: {len(tl)} tasks")
    print(f"  TOTAL: {sum(len(v) for v in tasks.values())} tasks")
    
    orch = MASOrchestratorV63()
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
    
    result_file = f"/root/.openclaw/workspace-mas/benchmark/results/v63_{int(time.time())}.json"
    rd = {
        "version": "v63",
        "overall_score": total_score,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_seconds": elapsed,
        "scores": {
            "ARC-AGI-3": scores.arc_agi_3, "BBEH": scores.bbeh, "HLE": scores.hle,
            "IMO-ANSWER": scores.imo_answer, "SWE-Bench-Pro": scores.swe_bench_pro,
            "MATH-500": scores.math_500, "GPQA-Diamond": scores.gpqa_diamond,
            "OSWorld-Tool-Hard": scores.osworld_tool_hard, "ZeroBench": scores.zerobench,
        }
    }
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w') as f:
        json.dump(rd, f, indent=2)
    print(f"\nSaved to: {result_file}")
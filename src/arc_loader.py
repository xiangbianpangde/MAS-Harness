#!/usr/bin/env python3
"""
ARC-AGI Real Data Loader
Loads actual ARC-AGI tasks and converts to benchmark format
"""

import json
import os
from typing import Dict, List, Any

ARC_EVAL_DIR = "/root/.openclaw/workspace-mas/benchmark/ARC-AGI/data/evaluation/"

def grid_to_ascii(grid: List[List[int]]) -> str:
    """Convert 2D grid to ASCII representation"""
    if not grid:
        return "empty"
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    lines = []
    for r in range(rows):
        row_str = " ".join(f"{v:3d}" for v in grid[r])
        lines.append(f"  [{row_str} ]")
    return "\n".join(lines)

def grid_to_brief(grid: List[List[int]]) -> str:
    """Convert 2D grid to compact string representation"""
    if not grid:
        return "empty"
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    parts = []
    for r in range(min(rows, 6)):
        for c in range(min(cols, 6)):
            parts.append(str(grid[r][c]))
    suffix = "..." if rows > 6 or cols > 6 else ""
    return f"grid({rows}x{cols}): [{','.join(parts)}]{suffix}"

def load_arc_task(task_id: str) -> Dict[str, Any]:
    """Load a single ARC task by ID"""
    path = os.path.join(ARC_EVAL_DIR, f"{task_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return data

def load_all_arc_tasks(max_tasks: int = 50, max_grid_size: int = 0) -> List[Dict]:
    """Load ARC tasks as benchmark-formatted dicts
    Args:
        max_tasks: Maximum number of tasks to load (0 = all)
        max_grid_size: Maximum grid dimension (0 = no limit)
    """
    files = sorted(os.listdir(ARC_EVAL_DIR))
    if max_tasks:
        files = files[:max_tasks]
    
    tasks = []
    for fname in files:
        task_id = fname.replace(".json", "")
        path = os.path.join(ARC_EVAL_DIR, fname)
        with open(path) as f:
            data = json.load(f)
        
        train = data.get("train", [])
        test = data.get("test", [])
        
        if not test:
            continue
        
        # Format train examples as text
        train_text = ""
        for i, ex in enumerate(train):
            inp = ex.get("input", [])
            out = ex.get("output", [])
            train_text += f"\nExample {i+1}:\n  Input:\n{grid_to_ascii(inp)}\n  Output:\n{grid_to_ascii(out)}\n"
        
        test_input = test[0].get("input", [])
        test_output = test[0].get("output", [])  # ground truth
        
        # Filter by max grid size
        if max_grid_size > 0:
            rows = len(test_input)
            cols = len(test_input[0]) if test_input else 0
            if max(rows, cols) > max_grid_size:
                continue
        
        tasks.append({
            "task_id": task_id,
            "name": data.get("name", task_id),
            "benchmark": "ARC-AGI-3",
            "difficulty": "medium",
            "description": "Grid transformation",
            "train_examples": train_text,
            "test_input_grid": test_input,
            "expected_output_grid": test_output,
            "test_input_ascii": grid_to_ascii(test_input),
            "expected_ascii": grid_to_ascii(test_output),
        })
    
    return tasks

def score_arc_output(predicted_grid: List[List[int]], expected_grid: List[List[int]]) -> float:
    """Score ARC output - exact cell match"""
    if not predicted_grid or not expected_grid:
        return 0.0
    if len(predicted_grid) != len(expected_grid):
        # Try to score what we can - partial credit for size mismatch
        min_r = min(len(predicted_grid), len(expected_grid))
        min_c = min(len(predicted_grid[0]) if predicted_grid else 0, 
                    len(expected_grid[0]) if expected_grid else 0)
        if min_r == 0 or min_c == 0:
            return 0.0
        correct = sum(1 for r in range(min_r) for c in range(min_c) 
                     if predicted_grid[r][c] == expected_grid[r][c])
        total = min_r * min_c
        size_penalty = 0.3  # penalty for wrong size
        return (correct / total) * (1.0 - size_penalty)
    
    rows = len(predicted_grid)
    cols = len(predicted_grid[0]) if predicted_grid else 0
    
    if rows != len(expected_grid) or cols != len(expected_grid[0]):
        return 0.0
    
    correct = sum(1 for r in range(rows) for c in range(cols) 
                 if predicted_grid[r][c] == expected_grid[r][c])
    total = rows * cols
    return correct / total

def parse_grid_from_text(text: str) -> List[List[int]]:
    """Try to parse a grid from LLM text output"""
    import re
    text = text.strip()
    
    # Strategy 1: Look for nested JSON array [[...],[...]]
    try:
        # Find outermost brackets and try to parse
        bracket_positions = [(i, c) for i, c in enumerate(text) if c in '[]']
        if bracket_positions:
            # Find the first '[' that's inside a grid context
            first_bracket = text.find('[[')
            if first_bracket == -1:
                first_bracket = text.find('[')
            if first_bracket >= 0:
                depth = 0
                start = first_bracket
                end = first_bracket
                for i, ch in enumerate(text[first_bracket:], first_bracket):
                    if ch == '[':
                        depth += 1
                    elif ch == ']':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                grid_str = text[start:end]
                try:
                    grid = json.loads(grid_str)
                    if isinstance(grid, list) and all(isinstance(row, list) for row in grid):
                        return grid
                except:
                    pass
    except Exception:
        pass
    
    # Strategy 2: Find rows separated by ],[ or ],[
    try:
        # Try to find rows in formats like [1,2,3], [4,5,6]
        row_matches = re.findall(r'\[\s*[\d,\s]+\]', text)
        if row_matches:
            rows = []
            for rm in row_matches:
                try:
                    row = json.loads(rm)
                    if isinstance(row, list) and all(isinstance(v, int) for v in row):
                        rows.append(row)
                except:
                    pass
            if rows and all(len(r) == len(rows[0]) for r in rows):
                return rows
    except Exception:
        pass
    
    # Strategy 3: Look for structured rows in text (lines with only numbers)
    lines = text.split('\n')
    grid_rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check if line looks like a grid row: mostly numbers with spaces/commas
        if re.match(r'^[\[\d\s,\-]+$', line):
            nums = re.findall(r'-?\d+', line)
            if nums:
                try:
                    row = [int(n) for n in nums]
                    grid_rows.append(row)
                except:
                    pass
    
    if grid_rows and len(grid_rows) > 0:
        # Verify all rows have same length
        if all(len(r) == len(grid_rows[0]) for r in grid_rows):
            return grid_rows
    
    return []

if __name__ == "__main__":
    tasks = load_all_arc_tasks(max_tasks=5)
    print(f"Loaded {len(tasks)} tasks")
    for t in tasks[:2]:
        print(f"\nTask {t['task_id']}:")
        print(f"Train examples: {t['train_examples'][:200]}...")
        print(f"Test input:\n{t['test_input_ascii']}")
        print(f"Expected output:\n{t['expected_ascii']}")

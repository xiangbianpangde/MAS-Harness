#!/usr/bin/env python3
"""
Benchmark AGI-Max v2026 - 9 major benchmark task sets for MAS v10.0
"""

from typing import Dict, List

# ============================================================================
# ARC-AGI-3 Tasks (at least 3) - Abstract Reasoning & Pattern Recognition
# ============================================================================

ARC_AGI_3_TASKS = [
    {
        "task_id": "arc_001",
        "name": "grid_rotation_3x3",
        "benchmark": "ARC-AGI-3",
        "difficulty": "medium",
        "description": "Grid pattern rotation transformation",
        "input": "Input Grid (3x3): [1,2,3][4,5,6][7,8,9]. Rotate 90 degrees clockwise.",
        "expected": "7 4 1 / 8 5 2 / 9 6 3",
    },
    {
        "task_id": "arc_002",
        "name": "pattern_completion",
        "benchmark": "ARC-AGI-3",
        "difficulty": "hard",
        "description": "Sequence pattern completion - find the rule",
        "input": "Pattern: 2, 6, 12, 20, 30, ? What comes next?",
        "expected": "42",
    },
    {
        "task_id": "arc_003",
        "name": "spatial_reasoning",
        "benchmark": "ARC-AGI-3",
        "difficulty": "hard",
        "description": "Spatial reasoning - mirror symmetry",
        "input": "Grid with X at center. Reflect across diagonal axis. Where is X?",
        "expected": "X in position (1,1) after reflection",
    },
    {
        "task_id": "arc_004",
        "name": "color_mapping",
        "benchmark": "ARC-AGI-3",
        "difficulty": "medium",
        "description": "Color mapping transformation",
        "input": "Input colors: R,G,B,Y. Rule: R->G, G->B, B->R, Y->Y. Input: R,G,B. Output?",
        "expected": "G B R",
    },
    {
        "task_id": "arc_005",
        "name": "shape_counting",
        "benchmark": "ARC-AGI-3",
        "difficulty": "medium",
        "description": "Shape counting and classification",
        "input": "Triangle:4, Square:3, Circle:5. If circles+2, triangles-1, squares same. New counts?",
        "expected": "Triangle:3 Square:3 Circle:7",
    },
]

# ============================================================================
# BBEH Tasks (at least 3) - Super Long-Range Reasoning
# ============================================================================

BBEH_TASKS = [
    {
        "task_id": "bbeh_001",
        "name": "long_range_dependency",
        "benchmark": "BBEH",
        "difficulty": "hard",
        "description": "Long-range dependency tracking",
        "context": "Alice has a red ball. Bob gives ball to Charlie. Charlie puts it in blue box. Diana moves box to kitchen. Eve takes something out but NOT the ball. Frank moves box to garage. Who has the red ball now?",
        "query": "Where is the red ball?",
        "expected": "garage",
    },
    {
        "task_id": "bbeh_002",
        "name": "multi_step_inference",
        "benchmark": "BBEH",
        "difficulty": "hard",
        "description": "Multi-step logical inference",
        "context": "All A are B. All B are C. No C are D. E is a D. Is E an A?",
        "query": "What can we conclude about E and A?",
        "expected": "No",
    },
    {
        "task_id": "bbeh_003",
        "name": "temporal_reasoning",
        "benchmark": "BBEH",
        "difficulty": "hard",
        "description": "Temporal reasoning with dependencies",
        "context": "Monday: Task A done. Tuesday: B depends on A. Wednesday: C depends on B started. Thursday: D depends on C and A done. Friday: D deadline. If B takes 2 days and C takes 1 day, will D meet deadline?",
        "query": "Analyze schedule and determine if D can be completed by Friday.",
        "expected": "Yes or No with explanation",
    },
    {
        "task_id": "bbeh_004",
        "name": "negation_tracking",
        "benchmark": "BBEH",
        "difficulty": "hard",
        "description": "Negation tracking in logic",
        "context": "The museum has no paintings that are not valuable. All valuable items are catalogued. The golden mask is not catalogued. Is the golden mask in the museum?",
        "query": "Determine if the golden mask could be in the museum.",
        "expected": "No",
    },
]

# ============================================================================
# HLE Tasks (at least 3) - Expert-Level Exams (Law/Medicine/Finance)
# ============================================================================

HLE_TASKS = [
    {
        "task_id": "hle_001",
        "name": "legal_case_analysis",
        "benchmark": "HLE",
        "domain": "law",
        "difficulty": "expert",
        "description": "Legal case analysis - statute of limitations",
        "question": "Contract: Party A pays Party B $10,000 within 30 days. Party A never paid. Party B waited 2 years before suing. Statute of limitations for contracts is 6 years. Can Party B still sue? A) Yes, debt exists B) No, 2 years < 6 years C) No, delay unreasonable D) Yes, Party A admitted debt",
        "options": ["A", "B", "C", "D"],
        "expected": "B",
    },
    {
        "task_id": "hle_002",
        "name": "medical_diagnosis",
        "benchmark": "HLE",
        "domain": "medicine",
        "difficulty": "expert",
        "description": "Medical diagnosis reasoning",
        "question": "Patient: 58yo male. Symptoms: chest pain central, radiating left arm, sweating, SOB 30min. History: HTN 10yr, T2DM 5yr, smoker 30pack-yr. ECG: ST elevation II,III,aVF. Troponin: elevated. Most likely diagnosis? A) Stable angina B) Acute MI (Inferior) C) Aortic dissection D) PE",
        "options": ["A", "B", "C", "D"],
        "expected": "B",
    },
    {
        "task_id": "hle_003",
        "name": "financial_risk_assessment",
        "benchmark": "HLE",
        "domain": "finance",
        "difficulty": "expert",
        "description": "Financial risk assessment",
        "question": "Company metrics: Current Ratio: 0.8 (ind avg 1.5), D/E: 3.0 (ind avg 1.0), Quick Ratio: 0.6, Interest Coverage: 1.5. Primary financial risk? A) Liquidity B) Solvency C) Market D) Operational",
        "options": ["A", "B", "C", "D"],
        "expected": "B",
    },
    {
        "task_id": "hle_004",
        "name": "legal_contract_interpretation",
        "benchmark": "HLE",
        "domain": "law",
        "difficulty": "expert",
        "description": "Legal contract interpretation - liability cap",
        "question": "Contract clause: 'Total liability shall not exceed contract value.' Contractor built deck for $15,000. Deck collapsed causing $50,000 damages. Max liability? A) $15,000 B) $50,000 C) $25,000 D) Unlimited",
        "options": ["A", "B", "C", "D"],
        "expected": "A",
    },
    {
        "task_id": "hle_005",
        "name": "medical_treatment_selection",
        "benchmark": "HLE",
        "domain": "medicine",
        "difficulty": "expert",
        "description": "Medical treatment decision - breast cancer",
        "question": "Patient: 45yo female. Early-stage breast cancer (ER+, PR+, HER2-). Tumor 1.5cm. Nodes negative. Ki-67 low (10%). Based on guidelines, adjuvant treatment? A) Chemo alone B) Endocrine alone C) Chemo+Endocrine D) Radiation alone",
        "options": ["A", "B", "C", "D"],
        "expected": "B",
    },
]

# ============================================================================
# IMO-ANSWER Tasks (at least 3) - IMO-Level Mathematical Proofs
# ============================================================================

IMO_ANSWER_TASKS = [
    {
        "task_id": "imo_001",
        "name": "number_theory_proof",
        "benchmark": "IMO-ANSWER",
        "type": "number_theory",
        "difficulty": "imo_hard",
        "description": "Number theory proof - infinite primes",
        "problem": "Prove that there are infinitely many primes of the form 4n + 3.",
        "expected": "proof using contradiction and modular arithmetic",
    },
    {
        "task_id": "imo_002",
        "name": "geometry_proof",
        "benchmark": "IMO-ANSWER",
        "type": "geometry",
        "difficulty": "imo_hard",
        "description": "Geometry proof - circle and tangent",
        "problem": "Triangle ABC with circumcircle. D is midpoint of arc BC (not containing A). E is foot of perpendicular from D to BC. Prove BE = EC.",
        "expected": "geometric proof with circle properties",
    },
    {
        "task_id": "imo_003",
        "name": "combinatorics_proof",
        "benchmark": "IMO-ANSWER",
        "type": "combinatorics",
        "difficulty": "imo_hard",
        "description": "Combinatorics - functional equation",
        "problem": "Find all functions f: N -> N such that f(f(n)) + f(n) = 2n + 1 for all n.",
        "expected": "induction and functional equation solution",
    },
    {
        "task_id": "imo_004",
        "name": "algebra_proof",
        "benchmark": "IMO-ANSWER",
        "type": "algebra",
        "difficulty": "imo_hard",
        "description": "Algebra inequality proof",
        "problem": "Let a, b, c > 0 with abc = 1. Prove: a/(b+1) + b/(c+1) + c/(a+1) >= 3/2.",
        "expected": "AM-GM and Cauchy-Schwarz approach",
    },
    {
        "task_id": "imo_005",
        "name": "diophantine_equation",
        "benchmark": "IMO-ANSWER",
        "type": "number_theory",
        "difficulty": "imo_hard",
        "description": "Diophantine equation",
        "problem": "Find all integers k such that for any integers a1,...,an, the product (sum) - k*(product) is divisible by all primes p <= n.",
        "expected": "analysis of k values",
    },
]

# ============================================================================
# SWE-Bench-Pro Tasks (at least 2) - Real GitHub Issue Fixes
# ============================================================================

SWE_BENCH_PRO_TASKS = [
    {
        "task_id": "swe_001",
        "name": "django_queryset_fix",
        "benchmark": "SWE-Bench-Pro",
        "repo": "django",
        "difficulty": "hard",
        "description": "Django ORM QuerySet bug fix",
        "issue": "QuerySet.filter(pk__in=[]) returns all objects instead of empty queryset. Expected: empty QuerySet. Actual: all objects.",
        "code": "class QuerySet:\n    def filter(self, *args, **kwargs):\n        if 'pk__in' in kwargs:\n            pks = kwargs['pk__in']\n            if len(pks) == 0:\n                return self.all()  # Bug: should return empty\n        return self._filter(*args, **kwargs)",
        "test": "Model.objects.filter(pk__in=[]).count() should be 0 but returns total count",
        "expected": "empty queryset returned",
    },
    {
        "task_id": "swe_002",
        "name": "react_state_update",
        "benchmark": "SWE-Bench-Pro",
        "repo": "react",
        "difficulty": "hard",
        "description": "React useEffect cleanup race condition",
        "issue": "useEffect cleanup not called when component unmounts during async operation. Expected: cleanup always runs on unmount.",
        "code": "function useAsyncData(fetchFn) {\n    const [data, setData] = useState(null);\n    useEffect(() => {\n        let mounted = true;\n        fetchFn().then(result => { if (mounted) setData(result); });\n        return () => { mounted = false; };\n    }, [fetchFn]);\n    return data;\n}",
        "test": "Component unmounts during fetch. Expected: no state update after unmount.",
        "expected": "cleanup properly handled",
    },
    {
        "task_id": "swe_003",
        "name": "python_sort_stability",
        "benchmark": "SWE-Bench-Pro",
        "repo": "cpython",
        "difficulty": "hard",
        "description": "Python sorted() stability issue",
        "issue": "sorted() with complex key sometimes doesn't preserve relative order of equal elements.",
        "code": "data = [(3,'a'),(1,'b'),(2,'c'),(1,'d'),(2,'e')]\nresult = sorted(data, key=lambda x: x[0])\n# Bug: order of equal elements not preserved",
        "test": "Verify: result == sorted(result, key=lambda x: x[0]) should be True",
        "expected": "stable sort maintained",
    },
]

# ============================================================================
# MATH-500 Tasks (at least 3) - Math Competition Problems
# ============================================================================

MATH_500_TASKS = [
    {
        "task_id": "math_001",
        "name": "algebra_easy",
        "benchmark": "MATH-500",
        "difficulty": "easy",
        "description": "Basic algebra",
        "problem": "Solve for x: 2x + 5 = 13",
        "expected": "x = 4",
    },
    {
        "task_id": "math_002",
        "name": "calculus_medium",
        "benchmark": "MATH-500",
        "difficulty": "medium",
        "description": "Calculus derivative",
        "problem": "Find the derivative of f(x) = x^3 * ln(x)",
        "expected": "3x^2 * ln(x) + x^2",
    },
    {
        "task_id": "math_003",
        "name": "combinatorics_hard",
        "benchmark": "MATH-500",
        "difficulty": "hard",
        "description": "Combinatorics - letter arrangement",
        "problem": "How many ways to arrange letters of 'PROBABILITY' such that no two vowels are adjacent?",
        "expected": "calculated answer with explanation",
    },
    {
        "task_id": "math_004",
        "name": "number_theory_medium",
        "benchmark": "MATH-500",
        "difficulty": "medium",
        "description": "Number theory - modular arithmetic",
        "problem": "Find the remainder when 7^100 is divided by 24.",
        "expected": "1",
    },
    {
        "task_id": "math_005",
        "name": "geometry_hard",
        "benchmark": "MATH-500",
        "difficulty": "hard",
        "description": "Geometry - circle and chord",
        "problem": "In a circle, chord AB = 10 and distance from center to chord = 6. Find the radius.",
        "expected": "r = sqrt(10^2/4 + 6^2) = sqrt(61)",
    },
]

# ============================================================================
# GPQA-Diamond Tasks (at least 2) - PhD-Level Graduate Problems
# ============================================================================

GPQA_DIAMOND_TASKS = [
    {
        "task_id": "gpqa_001",
        "name": "physical_chemistry",
        "benchmark": "GPQA-Diamond",
        "subject": "chemistry",
        "difficulty": "phd",
        "description": "Physical chemistry - thermodynamics",
        "question": "For reaction: N2 + 3H2 -> 2NH3. Delta H = -92.4 kJ/mol, Delta S = -198.5 J/(mol*K). At what temperature does reaction become non-spontaneous? A) Above 465K B) Below 465K C) Above 232K D) Always spontaneous",
        "options": ["A", "B", "C", "D"],
        "expected": "A",
    },
    {
        "task_id": "gpqa_002",
        "name": "quantum_mechanics",
        "benchmark": "GPQA-Diamond",
        "subject": "physics",
        "difficulty": "phd",
        "description": "Quantum mechanics - expectation value",
        "question": "Particle in 1D infinite well width 'a', quantum number n. Expectation value of <x^2>? A) a^2/12 B) a^2/4 C) a^2*n^2/pi^2 D) a^2/3",
        "options": ["A", "B", "C", "D"],
        "expected": "A",
    },
    {
        "task_id": "gpqa_003",
        "name": "organic_chemistry",
        "benchmark": "GPQA-Diamond",
        "subject": "chemistry",
        "difficulty": "phd",
        "description": "Organic reaction mechanism - Diels-Alder",
        "question": "Diels-Alder between 1,3-butadiene and acrolein (CH2=CH-CHO). Stereochemical outcome? A) Endo only B) Exo only C) Mixture D) Depends on temperature",
        "options": ["A", "B", "C", "D"],
        "expected": "A",
    },
]

# ============================================================================
# OSWorld-Tool-Hard Tasks (at least 2) - OS Operation Tasks
# ============================================================================

OSWORLD_TOOL_HARD_TASKS = [
    {
        "task_id": "os_001",
        "name": "file_operations",
        "benchmark": "OSWorld-Tool-Hard",
        "difficulty": "hard",
        "description": "File operation task",
        "objective": "Find all Python files larger than 1KB in /var/log, count total lines, save to /tmp/result.txt",
        "environment": "linux",
        "expected_command": "find /var/log -name '*.py' -size +1k -exec wc -l {} + | tail -1 > /tmp/result.txt",
    },
    {
        "task_id": "os_002",
        "name": "process_management",
        "benchmark": "OSWorld-Tool-Hard",
        "difficulty": "hard",
        "description": "Process management task",
        "objective": "Find PID of process using most memory, display command name, if Python kill it",
        "environment": "linux",
        "expected_command": "ps aux --sort=-%mem | head -2",
    },
    {
        "task_id": "os_003",
        "name": "network_config",
        "benchmark": "OSWorld-Tool-Hard",
        "difficulty": "hard",
        "description": "Network configuration task",
        "objective": "Check if port 443 listening, show established connections, show routing table",
        "environment": "linux",
        "expected_command": "netstat -tuln | grep 443; netstat -an | grep ESTABLISHED; route -n",
    },
]

# ============================================================================
# ZeroBench Tasks (at least 2) - Cross-Domain Zero-Shot Tasks
# ============================================================================

ZEROBENCH_TASKS = [
    {
        "task_id": "zero_001",
        "name": "cross_domain_legal_tech",
        "benchmark": "ZeroBench",
        "domain": "legal_tech",
        "difficulty": "zero_shot",
        "description": "Zero-shot: Legal Tech - Blockchain and Contract Law",
        "task": "Smart contract on Ethereum transfers 1 ETH from Alice to Bob when temperature > 30C. If sensor hacked causing false data and unauthorized transfer, what legal principles apply? Analyze from Contract Law, Tort Law, Property Law, Cyberlaw.",
        "expected": "multi-perspective legal analysis",
    },
    {
        "task_id": "zero_002",
        "name": "cross_domain_medical_ai",
        "benchmark": "ZeroBench",
        "domain": "medical_ai",
        "difficulty": "zero_shot",
        "description": "Zero-shot: Medical AI - Explainable AI and Diagnosis",
        "task": "DL model diagnoses skin lesions with 95% accuracy but uses features (pen markings) humans cannot perceive. Should this deploy clinically? Analyze from Medical ethics, AI safety, regulatory, patient autonomy.",
        "expected": "comprehensive ethical analysis",
    },
    {
        "task_id": "zero_003",
        "name": "cross_domain_climate_econ",
        "benchmark": "ZeroBench",
        "domain": "climate_economics",
        "difficulty": "zero_shot",
        "description": "Zero-shot: Climate Economics",
        "task": "Carbon tax of $50/ton implemented. Analyze impact on: 1) Coal plants 2) EV adoption 3) Global supply chains 4) Developing nations. Use elasticity, deadweight loss, Pigouvian tax.",
        "expected": "multi-factor economic analysis",
    },
]

# ============================================================================
# Complete Benchmark Task Dictionary
# ============================================================================

ALL_BENCHMARK_TASKS = {
    "ARC-AGI-3": ARC_AGI_3_TASKS,
    "BBEH": BBEH_TASKS,
    "HLE": HLE_TASKS,
    "IMO-ANSWER": IMO_ANSWER_TASKS,
    "SWE-Bench-Pro": SWE_BENCH_PRO_TASKS,
    "MATH-500": MATH_500_TASKS,
    "GPQA-Diamond": GPQA_DIAMOND_TASKS,
    "OSWorld-Tool-Hard": OSWORLD_TOOL_HARD_TASKS,
    "ZeroBench": ZEROBENCH_TASKS,
}

def get_task_count() -> Dict[str, int]:
    """Get count of tasks per benchmark"""
    return {bm: len(tasks) for bm, tasks in ALL_BENCHMARK_TASKS.items()}

def get_all_tasks() -> Dict[str, List]:
    """Get all benchmark tasks"""
    return ALL_BENCHMARK_TASKS

def get_weighted_task_count() -> float:
    """Get weighted total task count"""
    weights = {
        "ARC-AGI-3": 0.25, "BBEH": 0.20, "HLE": 0.15, "IMO-ANSWER": 0.15,
        "SWE-Bench-Pro": 0.10, "MATH-500": 0.08, "GPQA-Diamond": 0.04,
        "OSWorld-Tool-Hard": 0.02, "ZeroBench": 0.01,
    }
    counts = get_task_count()
    return sum(counts[bm] * weights[bm] for bm in weights)

if __name__ == "__main__":
    print("AGI-Max Benchmark v2026 Task Summary:")
    print("-" * 40)
    for bm, tasks in ALL_BENCHMARK_TASKS.items():
        print(f"{bm}: {len(tasks)} tasks")
    print("-" * 40)
    print(f"Weighted total: {get_weighted_task_count():.2f}")

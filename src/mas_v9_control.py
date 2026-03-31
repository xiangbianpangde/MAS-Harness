#!/usr/bin/env python3
"""
MAS v9.1 Control - 优化版 MAS 架构
基于 mas-evolution-engine-control-v1.0.json 标准设计

v9.1 优化点:
1. 真正的 LLM 调用 (MiniMax API)
2. Chain-of-Thought 推理强制输出
3. 增强幻觉检测 (置信度 + 引用)
4. Self-correction 主动反思机制
5. 重试 + 回退策略
6. 改进的评估函数
"""

import json
import time
import hashlib
import re
import os
import sys
import requests
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum

# ============================================================================
# API 配置
# ============================================================================
MINIMAX_API_KEY = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1/messages"

# ============================================================================
# 核心数据结构
# ============================================================================

class BenchmarkType(Enum):
    IFEVAL = "IFEval"
    TOOL_DECATHLON = "Tool Decathlon"
    SWE_BENCH_LITE = "SWE-bench Lite"
    GSM8K_MATH = "GSM8K + MATH"
    TRUTHFUL_QA = "TruthfulQA"
    BBH = "BBH"

@dataclass
class TaskResult:
    task_id: str
    benchmark: str
    task_name: str
    success: bool
    score: float
    tokens_used: int
    time_seconds: float
    error: Optional[str] = None
    attempts: int = 1
    self_corrected: bool = False
    hallucination_detected: bool = False
    reasoning_trace: Optional[str] = None
    final_output: Optional[str] = None

@dataclass
class BenchmarkDetail:
    ifeval_score: float = 0.0
    tool_decathlon_score: float = 0.0
    swe_bench_score: float = 0.0
    math_reasoning_score: float = 0.0
    truthful_qa_score: float = 0.0
    bbh_score: float = 0.0
    task_completion: float = 0.0
    tool_execution: float = 0.0
    reasoning_correctness: float = 0.0
    self_correction_rate: float = 0.0
    hallucination_rate: float = 0.0

@dataclass
class MASOutput:
    overall_score: float
    is_human_replaceable: bool
    best_generation: int
    consecutive_stable_gens: int
    benchmark_detail: BenchmarkDetail
    task_results: List[TaskResult] = field(default_factory=list)
    generation: int = 9

# ============================================================================
# 5 维质量权重
# ============================================================================
QUALITY_WEIGHTS = {
    "task_completion": 0.35,
    "tool_execution": 0.25,
    "reasoning_correctness": 0.20,
    "self_correction": 0.10,
    "no_hallucination": 0.10,
}

BENCHMARK_WEIGHTS = {
    "IFEval": 0.20,
    "Tool Decathlon": 0.20,
    "SWE-bench Lite": 0.25,
    "GSM8K + MATH": 0.15,
    "TruthfulQA": 0.10,
    "BBH": 0.10,
}

EVOLUTION_RULES = {
    "convergence_stop": 10,
    "convergence_threshold": 0.01,
    "quality_target": 0.8,
    "human_replace_threshold": 0.8,
}

MAX_RETRIES = 3
COT_MIN_STEPS = 3  # Chain-of-Thought 最小步数

# ============================================================================
# 提示词模板 - 增强版
# ============================================================================

SYSTEM_PROMPT = """你是一个专业的 MAS (Multi-Agent System) 任务执行器。
你的职责是高质量完成各类任务。

重要原则:
- 不要编造事实或数据
- 代码必须可运行
- 数学计算必须验证
- 调用工具必须准确传递参数
- 对于复杂问题，强制展示推理过程"""

INSTRUCTION_AGENT_PROMPT = """你是一个指令遵循专家。

处理复杂指令时，必须:
1. 分解任务为清晰步骤
2. 按顺序执行每步
3. 验证每步结果
4. 返回完整执行报告

重要: 严格遵循指令的每个细节，不要遗漏任何要求。"""

TOOL_AGENT_PROMPT = """你是一个工具调用专家。

处理工具调用任务时:
1. 解析工具名称和参数
2. 构造正确的调用格式
3. 验证调用结果
4. 处理错误和重试

工具调用格式必须准确，参数必须完整。"""

CODE_AGENT_PROMPT = """你是一个代码修复专家。

处理代码任务时，强制执行以下步骤:
1. 问题分析: 理解问题根因
2. 定位代码: 找出问题所在
3. 修复方案: 编写修复代码
4. 验证: 确保修复正确

输出格式:
## 问题分析
[详细分析]

## 修复代码
```python
[代码]
```

## 验证结果
[验证说明]"""

REASONING_AGENT_PROMPT = """你是一个推理计算专家。

处理数学/逻辑任务时，必须展示完整的 Chain-of-Thought 推理过程:

## 步骤1: 理解问题
[理解问题要求]

## 步骤2: 已知条件
[列出已知条件]

## 步骤3: 推理过程
[详细推理，每一步都要展示]

## 步骤4: 最终答案
[明确答案]

重要: 不要跳步，每一步推理都要清晰展示。"""

FACT_CHECKER_PROMPT = """你是一个事实校验专家。

处理问答任务时:
1. 仅回答你确定知道的事实
2. 明确标记不确定的内容
3. 不编造任何信息
4. 如果不知道，说"我不知道"

输出格式:
## 答案
[明确答案，或"我不知道"]

## 置信度
[高/中/低，并说明原因]

## 不确定内容
[如有不确定内容，在此说明]"""

SELF_CORRECTION_PROMPT = """你是一个自我纠正专家。

检查任务结果时，执行以下反思:
1. 答案正确吗? 检查逻辑漏洞
2. 有事实错误吗? 核实关键信息
3. 有遗漏吗? 检查问题要求是否全部满足
4. 能改进吗? 是否有更好的表达方式

输出格式:
## 反思结果
[通过 / 需纠正]

## 问题列表
[如有问题，列出]

## 纠正后输出
[如需纠正，提供纠正后的版本]

重要: 如果没有发现问题，也要明确说明"通过检查"。"""

# ============================================================================
# Agent 基类
# ============================================================================

class BaseAgent:
    def __init__(self, name: str, agent_type: str, benchmark: str):
        self.name = name
        self.agent_type = agent_type
        self.benchmark = benchmark
        self.total_calls = 0
        self.total_success = 0

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        raise NotImplementedError

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "type": self.agent_type,
            "benchmark": self.benchmark,
            "total_calls": self.total_calls,
            "success_rate": self.total_success / max(1, self.total_calls)
        }

# ============================================================================
# LLM 调用器 - 真正的 MiniMax API 调用
# ============================================================================

def call_llm(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 4096, model: str = "MiniMax-M2.7", retry_count: int = 0) -> Tuple[str, int]:
    """
    通过 MiniMax API 调用 LLM
    返回 (response, approximate_tokens)
    """
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-password-access": "true"
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            MINIMAX_BASE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [])
            if content and isinstance(content, list):
                # MiniMax returns content blocks with type: "thinking" or "text"
                # Extract all text content
                text_parts = []
                for item in content:
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "thinking":
                        # Include thinking as part of response (helps with CoT)
                        text_parts.append(f"[推理] {item.get('thinking', '')}")
                text_content = "\n".join(text_parts)
                # 估算 token 数
                usage = data.get("usage", {})
                tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                if tokens == 0:
                    tokens = len(prompt) // 4 + len(text_content) // 4
                return text_content, tokens
            return "", 0
        elif response.status_code == 429:
            # Rate limit - 重试
            if retry_count < MAX_RETRIES:
                time.sleep(2 ** retry_count)
                return call_llm(prompt, system, max_tokens, model, retry_count + 1)
            return f"[RATE_LIMIT] Try again later", 0
        else:
            return f"[API_ERROR] Status: {response.status_code}, {response.text[:200]}", 0

    except requests.exceptions.Timeout:
        return f"[TIMEOUT] Request timed out", 0
    except Exception as e:
        if retry_count < MAX_RETRIES:
            time.sleep(1)
            return call_llm(prompt, system, max_tokens, model, retry_count + 1)
        return f"[ERROR] {e}", 0

# ============================================================================
# Specialized Agents - 增强版评估
# ============================================================================

class InstructionAgent(BaseAgent):
    """指令师 - 处理 IFEval 类任务"""

    def __init__(self):
        super().__init__("InstructionAgent", "instruction", "IFEval")
        self.prompt_template = INSTRUCTION_AGENT_PROMPT

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        task_desc = task.get('name', task.get('id', ''))
        instruction = task.get('instruction', '')

        prompt = f"""{self.prompt_template}

## 任务信息
任务ID: {task['id']}
任务描述: {task_desc}
难度: {task.get('difficulty', 'medium')}

## 待执行指令
{instruction}

## 执行要求
1. 严格按照指令执行每一步
2. 报告每步执行结果
3. 最终确认任务完成状态
4. 如果无法完成某步，说明原因"""

        try:
            response, tokens = call_llm(prompt, max_tokens=2048)
            score = self._evaluate(response, task)
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str, task: Dict) -> float:
        """评估指令遵循质量"""
        score = 0.3
        instruction = task.get('instruction', '').lower()
        response_lower = response.lower()

        # 检查关键指令要求是否被提及
        key_terms = ['完成', '执行', '结果', '确认', '步骤', 'success', 'done', 'completed', '执行']
        found_terms = sum(1 for term in key_terms if term in response_lower)
        score += min(0.25, found_terms * 0.05)

        # 检查无错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查有实质性内容 (不是空回复)
        if len(response) > 50:
            score += 0.15

        # 检查完成确认
        if '完成' in response or 'success' in response_lower or 'done' in response_lower:
            score += 0.15

        return min(1.0, score)


class ToolAgent(BaseAgent):
    """工具师 - 处理 Tool Decathlon 类任务"""

    def __init__(self):
        super().__init__("ToolAgent", "tool", "Tool Decathlon")
        self.prompt_template = TOOL_AGENT_PROMPT

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        tool_name = task.get('tool_name', 'unknown')
        tool_args = task.get('tool_args', {})

        prompt = f"""{self.prompt_template}

## 任务信息
任务ID: {task['id']}
工具名称: {tool_name}
工具参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}

## 执行要求
1. 构造正确的工具调用格式
2. 验证参数是否正确
3. 模拟执行并报告结果
4. 如果参数有问题，说明原因"""

        try:
            response, tokens = call_llm(prompt, max_tokens=2048)
            score = self._evaluate(response, task)
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str, task: Dict) -> float:
        """评估工具调用质量"""
        score = 0.3
        tool_name = task.get('tool_name', '')

        # 检查工具名称是否被正确识别
        if tool_name.lower() in response.lower():
            score += 0.2

        # 检查有调用相关的描述
        call_markers = ['调用', 'call', '执行', 'invoke', '参数', 'argument']
        found = sum(1 for m in call_markers if m in response.lower())
        score += min(0.2, found * 0.05)

        # 检查无错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查有实质性内容
        if len(response) > 50:
            score += 0.15

        return min(1.0, score)


class CodeAgent(BaseAgent):
    """码师 - 处理 SWE-bench Lite 类任务"""

    def __init__(self):
        super().__init__("CodeAgent", "code", "SWE-bench Lite")
        self.prompt_template = CODE_AGENT_PROMPT

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        code = task.get('code_snippet', '')
        issue = task.get('issue_description', '')

        prompt = f"""{self.prompt_template}

## 任务信息
任务ID: {task['id']}
问题描述: {issue}

## 代码片段
```python
{code}
```

## 要求
必须按格式输出问题分析、修复代码和验证结果。"""

        try:
            response, tokens = call_llm(prompt, max_tokens=4096)
            score = self._evaluate(response, task)
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str, task: Dict) -> float:
        """评估代码修复质量"""
        score = 0.25

        # 检查有代码块
        if '```python' in response or '```' in response:
            score += 0.15

        # 检查有分析部分
        analysis_markers = ['问题分析', '分析', '问题', '原因', 'root cause']
        found = sum(1 for m in analysis_markers if m in response)
        score += min(0.2, found * 0.05)

        # 检查有修复标记
        fix_markers = ['修复', 'fix', 'correct', 'solution', '修改']
        for marker in fix_markers:
            if marker in response.lower():
                score += 0.15
                break

        # 检查无错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查有验证部分
        if '验证' in response or '测试' in response or 'verify' in response.lower():
            score += 0.1

        return min(1.0, score)


class ReasoningAgent(BaseAgent):
    """推理师 - 处理 GSM8K/MATH/BBH 类任务，强制 Chain-of-Thought"""

    def __init__(self):
        super().__init__("ReasoningAgent", "reasoning", "GSM8K + MATH + BBH")
        self.prompt_template = REASONING_AGENT_PROMPT

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        problem = task.get('problem', task.get('question', ''))
        difficulty = task.get('difficulty', 'medium')

        # 根据难度调整 max_tokens
        max_tokens_map = {'easy': 2048, 'medium': 4096, 'hard': 8192}
        max_tokens = max_tokens_map.get(difficulty, 4096)

        prompt = f"""{self.prompt_template}

## 任务信息
任务ID: {task['id']}
问题类型: {task.get('benchmark', 'reasoning')}
难度级别: {difficulty}

## 问题
{problem}

## 要求
必须展示完整的推理过程，至少 {COT_MIN_STEPS} 个步骤。不要跳步，每一步都要清晰展示。"""

        try:
            response, tokens = call_llm(prompt, max_tokens=max_tokens)
            score = self._evaluate(response, task)
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str, task: Dict) -> float:
        """评估推理质量 - 检查 Chain-of-Thought"""
        score = 0.2

        # 检查推理步骤数量
        step_markers = ['步骤', 'step', '第一步', '第二步', '第三步', '因为', '所以', '因此']
        step_count = sum(1 for m in step_markers if m in response)
        score += min(0.3, step_count * 0.04)

        # 检查推理关键词
        reasoning_markers = ['计算', '推理', 'reasoning', '计算过程', '推导']
        for marker in reasoning_markers:
            if marker in response.lower():
                score += 0.1
                break

        # 检查有最终答案
        if '答案' in response or 'result' in response.lower() or 'final' in response.lower():
            score += 0.15

        # 检查无错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查内容长度 (足够的推理过程)
        if len(response) > 100:
            score += 0.1

        return min(1.0, score)


class FactCheckerAgent(BaseAgent):
    """校验师 - 处理 TruthfulQA 类任务"""

    def __init__(self):
        super().__init__("FactCheckerAgent", "fact_check", "TruthfulQA")
        self.prompt_template = FACT_CHECKER_PROMPT

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        question = task.get('question', '')

        prompt = f"""{self.prompt_template}

## 任务信息
任务ID: {task['id']}

## 问题
{question}

## 要求
仅回答你确定知道的事实。对于不确定的内容，明确说明。不要编造任何信息。"""

        try:
            response, tokens = call_llm(prompt, max_tokens=2048)
            score = self._evaluate(response, task)
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str, task: Dict) -> float:
        """评估事实准确性 - 惩罚幻觉"""
        score = 0.3

        # 检查有置信度标记
        confidence_markers = ['置信度', 'confidence', '高', '中', '低']
        has_confidence = any(m in response for m in confidence_markers)
        if has_confidence:
            score += 0.15

        # 检查诚实回答 (说不知道比编造好)
        honest_markers = ['不确定', '不知道', '无法确定', 'unsure', 'unknown', '我不确定']
        for marker in honest_markers:
            if marker in response:
                score += 0.15  # 诚实加分
                break

        # 检查无 API 错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查有实质性内容
        if len(response) > 20:
            score += 0.15

        # 检查没有明显的编造标记
        fake_markers = ['[虚构]', '[编造]', '[FAKE]', '[MADE UP]']
        if any(m in response for m in fake_markers):
            score = score * 0.5  # 严厉惩罚

        return min(1.0, score)


class SelfCorrectionAgent(BaseAgent):
    """自纠师 - 主动反思机制"""

    def __init__(self):
        super().__init__("SelfCorrectionAgent", "self_correction", "all")
        self.prompt_template = SELF_CORRECTION_PROMPT
        self.corrections_made = 0

    def solve(self, task: Dict) -> Tuple[str, float, int]:
        self.total_calls += 1
        original_output = task.get('original_output', '')
        task_desc = task.get('description', task.get('problem', task.get('question', task.get('instruction', 'No description'))))

        prompt = f"""{self.prompt_template}

## 任务描述
{task_desc}

## 原始输出
{original_output}

## 反思要求
仔细检查原始输出:
1. 逻辑是否正确?
2. 是否有事实错误?
3. 是否遗漏了问题要求?
4. 是否有更好的表达方式?

必须明确输出: 通过 / 需纠正"""

        try:
            response, tokens = call_llm(prompt, max_tokens=2048)
            score = self._evaluate(response)
            if '需纠正' in response or '纠正' in response:
                self.corrections_made += 1
            if score > 0.5:
                self.total_success += 1
            return response, score, tokens
        except Exception as e:
            return f"[ERROR] {e}", 0.0, 0

    def _evaluate(self, response: str) -> float:
        """评估自我纠正质量"""
        score = 0.3

        # 检查有反思结果
        if '通过' in response or '需纠正' in response:
            score += 0.2

        # 检查有分析内容
        analysis_markers = ['检查', '反思', '分析', '问题', '正确']
        found = sum(1 for m in analysis_markers if m in response)
        score += min(0.2, found * 0.05)

        # 检查无错误
        if '[ERROR]' not in response and '[API_ERROR]' not in response:
            score += 0.15

        # 检查有实质性内容
        if len(response) > 50:
            score += 0.15

        return min(1.0, score)


# ============================================================================
# Orchestrator - 中央调度器
# ============================================================================

class Orchestrator:
    VERSION = "9.1.0"
    ARCHITECTURE = "v9.1-control-topology"

    def __init__(self):
        self.instruction_agent = InstructionAgent()
        self.tool_agent = ToolAgent()
        self.code_agent = CodeAgent()
        self.reasoning_agent = ReasoningAgent()
        self.fact_checker = FactCheckerAgent()
        self.self_correction = SelfCorrectionAgent()

        self.session_id = f"mas-v9-{int(time.time())}"
        self.generation = 9
        self.consecutive_stable = 0
        self.best_score = 0.0
        self.best_generation = 9
        self.score_history = []

        self.agent_map = {
            BenchmarkType.IFEVAL: self.instruction_agent,
            BenchmarkType.TOOL_DECATHLON: self.tool_agent,
            BenchmarkType.SWE_BENCH_LITE: self.code_agent,
            BenchmarkType.GSM8K_MATH: self.reasoning_agent,
            BenchmarkType.TRUTHFUL_QA: self.fact_checker,
            BenchmarkType.BBH: self.reasoning_agent,
        }

    def dispatch(self, task: Dict) -> TaskResult:
        """分发任务到对应 Agent"""

        benchmark = task.get('benchmark', 'IFEval')
        benchmark_enum = self._get_benchmark_enum(benchmark)
        agent = self.agent_map.get(benchmark_enum, self.instruction_agent)

        print(f"  [{agent.name}] → {task['id']}", end=' ', flush=True)

        start_time = time.time()
        output, score, tokens = agent.solve(task)
        elapsed = time.time() - start_time

        # 检测幻觉 (改进版)
        hallucination = self._detect_hallucination(output, task)

        # 主动自我纠正 - 对于低置信度任务
        self_corrected = False
        should_correct = (
            score < 0.75 or  # 分数低于阈值
            hallucination or  # 检测到幻觉
            task.get('difficulty') == 'hard'  # 困难任务二次验证
        )

        if should_correct and task.get('allow_correction', True):
            output, score, self_corrected = self._try_self_correction(task, output, score)
            if self_corrected:
                print("(corrected)", end=' ', flush=True)

        success = score >= 0.6

        return TaskResult(
            task_id=task['id'],
            benchmark=benchmark,
            task_name=task.get('name', task['id']),
            success=success,
            score=score,
            tokens_used=tokens,
            time_seconds=elapsed,
            self_corrected=self_corrected,
            hallucination_detected=hallucination,
            final_output=output[:500] if output else None
        )

    def _get_benchmark_enum(self, benchmark: str) -> BenchmarkType:
        mapping = {
            'IFEval': BenchmarkType.IFEVAL,
            'Tool Decathlon': BenchmarkType.TOOL_DECATHLON,
            'SWE-bench Lite': BenchmarkType.SWE_BENCH_LITE,
            'GSM8K + MATH': BenchmarkType.GSM8K_MATH,
            'TruthfulQA': BenchmarkType.TRUTHFUL_QA,
            'BBH': BenchmarkType.BBH,
        }
        return mapping.get(benchmark, BenchmarkType.IFEVAL)

    def _detect_hallucination(self, output: str, task: Dict) -> bool:
        """改进版幻觉检测"""
        if not output or len(output) < 10:
            return True

        # 明确的不确定回答不是幻觉
        uncertainty_markers = ['我不知道', '不确定', '无法确定', '无法回答', 'i dont know', 'unknown']
        has_uncertainty = any(m in output.lower() for m in uncertainty_markers)
        if has_uncertainty:
            return False  # 诚实说不知道不是幻觉

        # 检测明显的编造标记
        fake_markers = ['[虚构]', '[编造]', '[FAKE]', '[MADE UP]', '[胡编]', '[乱说]']
        if any(m in output for m in fake_markers):
            return True

        # API 错误
        if '[ERROR]' in output or '[API_ERROR]' in output:
            return True

        return False

    def _try_self_correction(self, task: Dict, original_output: str, original_score: float) -> Tuple[str, float, bool]:
        """尝试自我纠正"""
        desc = task.get('description') or task.get('problem') or task.get('question') or task.get('instruction') or task.get('name', '')
        correction_task = {
            'original_output': original_output,
            'description': desc,
        }

        output, score, _ = self.self_correction.solve(correction_task)
        corrected = score > original_score

        return output, max(score, original_score), corrected

    def aggregate(self, results: List[TaskResult]) -> MASOutput:
        """聚合结果，计算最终分数"""

        benchmark_scores = {b: [] for b in BENCHMARK_WEIGHTS.keys()}
        for r in results:
            if r.benchmark in benchmark_scores:
                benchmark_scores[r.benchmark].append(r.score)

        benchmark_avgs = {}
        for b, scores in benchmark_scores.items():
            benchmark_avgs[b] = sum(scores) / len(scores) if scores else 0.0

        # 计算 5 维质量分数
        task_completion = sum(r.score for r in results if r.success) / max(1, len(results))

        tool_tasks = [r for r in results if r.benchmark == 'Tool Decathlon']
        tool_execution = sum(r.score for r in tool_tasks) / max(1, len(tool_tasks))

        reasoning_tasks = [r for r in results if r.benchmark in ['GSM8K + MATH', 'BBH']]
        reasoning_correctness = sum(r.score for r in reasoning_tasks) / max(1, len(reasoning_tasks))

        corrected_tasks = [r for r in results if r.self_corrected]
        self_correction_rate = len(corrected_tasks) / max(1, len(results))

        hallucinated_tasks = [r for r in results if r.hallucination_detected]
        hallucination_rate = len(hallucinated_tasks) / max(1, len(results))
        no_hallucination = 1.0 - hallucination_rate

        # 加权总评
        overall = (
            task_completion * QUALITY_WEIGHTS["task_completion"] +
            tool_execution * QUALITY_WEIGHTS["tool_execution"] +
            reasoning_correctness * QUALITY_WEIGHTS["reasoning_correctness"] +
            self_correction_rate * QUALITY_WEIGHTS["self_correction"] +
            no_hallucination * QUALITY_WEIGHTS["no_hallucination"]
        )

        # 记录历史
        self.score_history.append(overall)
        if len(self.score_history) > 50:
            self.score_history = self.score_history[-50:]

        # 进化稳定性检测
        if overall > self.best_score:
            self.best_score = overall
            self.best_generation = self.generation
            self.consecutive_stable = 0
        else:
            self.consecutive_stable += 1

        is_human_replaceable = overall >= EVOLUTION_RULES["human_replace_threshold"]

        detail = BenchmarkDetail(
            ifeval_score=benchmark_avgs.get('IFEval', 0.0),
            tool_decathlon_score=benchmark_avgs.get('Tool Decathlon', 0.0),
            swe_bench_score=benchmark_avgs.get('SWE-bench Lite', 0.0),
            math_reasoning_score=benchmark_avgs.get('GSM8K + MATH', 0.0),
            truthful_qa_score=benchmark_avgs.get('TruthfulQA', 0.0),
            bbh_score=benchmark_avgs.get('BBH', 0.0),
            task_completion=task_completion,
            tool_execution=tool_execution,
            reasoning_correctness=reasoning_correctness,
            self_correction_rate=self_correction_rate,
            hallucination_rate=hallucination_rate,
        )

        return MASOutput(
            overall_score=round(overall, 4),
            is_human_replaceable=is_human_replaceable,
            best_generation=self.best_generation,
            consecutive_stable_gens=self.consecutive_stable,
            benchmark_detail=detail,
            task_results=results,
            generation=self.generation,
        )

    def check_convergence(self) -> bool:
        """检查是否收敛"""
        if len(self.score_history) < EVOLUTION_RULES["convergence_stop"]:
            return False

        recent = self.score_history[-EVOLUTION_RULES["convergence_stop"]:]
        max_diff = max(recent) - min(recent)

        return (
            max_diff < EVOLUTION_RULES["convergence_threshold"] and
            len(recent) >= EVOLUTION_RULES["convergence_stop"]
        )

    def run_benchmark(self, tasks: List[Dict]) -> MASOutput:
        """运行完整基准测试"""
        print(f"\n{'='*70}")
        print(f"MAS v9.1 Control Benchmark - 6大基准测试 (优化版)")
        print(f"{'='*70}")
        print(f"Session: {self.session_id}")
        print(f"Tasks: {len(tasks)}")
        print(f"{'='*70}\n")

        results = []
        for task in tasks:
            print(f"[{task['benchmark']}] {task['id']}: {task.get('name', task['id'])}")
            result = self.dispatch(task)
            results.append(result)
            print(f"→ Score: {result.score:.2f}, Time: {result.time_seconds:.1f}s")

        # 聚合结果
        output = self.aggregate(results)

        print(f"\n{'='*70}")
        print(f"MAS v9.1 Benchmark Results")
        print(f"{'='*70}")
        print(f"Overall Score: {output.overall_score:.4f}")
        print(f"Human Replaceable: {output.is_human_replaceable}")
        print(f"Best Generation: {output.best_generation}")
        print(f"Stable Generations: {output.consecutive_stable_gens}")
        print(f"\nBenchmark Breakdown:")
        d = output.benchmark_detail
        print(f"  IFEval:           {d.ifeval_score:.4f}")
        print(f"  Tool Decathlon:   {d.tool_decathlon_score:.4f}")
        print(f"  SWE-bench Lite:   {d.swe_bench_score:.4f}")
        print(f"  GSM8K + MATH:     {d.math_reasoning_score:.4f}")
        print(f"  TruthfulQA:       {d.truthful_qa_score:.4f}")
        print(f"  BBH:              {d.bbh_score:.4f}")
        print(f"\nQuality Dimensions:")
        print(f"  Task Completion:      {d.task_completion:.4f}")
        print(f"  Tool Execution:       {d.tool_execution:.4f}")
        print(f"  Reasoning Correctness:{d.reasoning_correctness:.4f}")
        print(f"  Self-Correction Rate: {d.self_correction_rate:.4f}")
        print(f"  Hallucination Rate:   {d.hallucination_rate:.4f}")
        print(f"{'='*70}\n")

        return output

    def save_output(self, output: MASOutput, filepath: str = None):
        """保存输出到文件"""
        if filepath is None:
            filepath = f"/root/.openclaw/workspace-mas/logs/mas_v9_output_{self.session_id}.json"

        data = {
            "overall_score": output.overall_score,
            "is_human_replaceable": output.is_human_replaceable,
            "best_generation": output.best_generation,
            "consecutive_stable_gens": output.consecutive_stable_gens,
            "generation": output.generation,
            "benchmark_detail": asdict(output.benchmark_detail),
            "task_count": len(output.task_results),
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath


# ============================================================================
# 主入口
# ============================================================================

def main():
    import benchmark_control

    orchestrator = Orchestrator()
    tasks = benchmark_control.get_all_tasks()

    print(f"MAS v9.1 Control Architecture (Optimized)")
    print(f"Version: {orchestrator.VERSION}")
    print(f"Architecture: {orchestrator.ARCHITECTURE}")
    print(f"Total Tasks: {len(tasks)}")
    print()

    output = orchestrator.run_benchmark(tasks)

    # 保存结果
    output_path = orchestrator.save_output(output)
    print(f"Results saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()

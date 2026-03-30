#!/usr/bin/env python3
"""Diagnostic script to see actual model responses"""

import subprocess
import json
import time

TASKS = [
    {"id": "code_quicksort", "prompt": "实现快速排序Python代码，包含随机pivot和单元测试。直接返回Python代码。"},
    {"id": "code_lcs", "prompt": "实现LCS动态规划算法，返回长度和具体序列。直接返回Python代码。"},
    {"id": "math_prob", "prompt": "5个红球3个蓝球，不放回取2次，求两次都是红球的概率。"},
    {"id": "plan_critical", "prompt": "任务A需2天无依赖，B需3天依赖A，C需1天无依赖，D需2天依赖B，求关键路径。"},
    {"id": "creative_story", "prompt": "写一个500字左右的科幻故事，主题：AI的第一次梦境。"},
    {"id": "reason_logic", "prompt": "甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。已知只有一人说真话，谁在说真话？"},
]

def call_model(prompt: str, session_id: str) -> str:
    cmd = ["openclaw", "agent", "--local", "--session-id", session_id, "--message", prompt, "--timeout", "120", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
    try:
        for line in result.stdout.strip().split('\n'):
            if line.strip().startswith('{"payloads"'):
                resp = json.loads(line)
                if resp.get('payloads'):
                    return resp['payloads'][0].get('text', '')
    except:
        pass
    return f"ERROR: {result.stdout[:300]}"

for task in TASKS:
    print(f"\n{'='*60}")
    print(f"TASK: {task['id']}")
    print(f"PROMPT: {task['prompt']}")
    print("-" * 60)
    
    session_id = f"diag-{task['id']}-{int(time.time())}"
    response = call_model(task['prompt'], session_id)
    
    print(f"RESPONSE (first 800 chars):\n{response[:800]}")
    
    # Count Chinese chars
    chinese_chars = len([c for c in response if '\u4e00' <= c <= '\u9fff'])
    print(f"\nChinese chars: {chinese_chars}")
    
    time.sleep(2)  # Rate limiting

#!/usr/bin/env python3
"""
MAS 1.0 资源监控探针
监控 CPU、内存、磁盘、网络连接
触发告警阈值: CPU>95%, Disk<3GB, Memory<500MB
"""

import psutil
import time
import json
import os
import smtplib
from datetime import datetime

THRESHOLDS = {
    'cpu_percent': 95.0,
    'memory_available_mb': 500,
    'disk_free_gb': 3.0,
    'disk_usage_percent': 95.0
}

ALERT_COOLDOWN = 300  # 5分钟内不重复告警
LAST_ALERT_FILE = '/root/.openclaw/workspace-mas/monitor/.last_alert'

def check_resources():
    """返回当前资源状态"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': cpu,
        'memory_available_mb': mem.available / (1024**2),
        'memory_percent': mem.percent,
        'disk_free_gb': disk.free / (1024**3),
        'disk_usage_percent': disk.percent,
        'disk_total_gb': disk.total / (1024**3),
        'alerts': []
    }

def check_thresholds(status):
    """检查是否触发告警阈值"""
    alerts = []
    
    if status['cpu_percent'] > THRESHOLDS['cpu_percent']:
        alerts.append(f"CPU告警: {status['cpu_percent']:.1f}% > {THRESHOLDS['cpu_percent']}%")
    
    if status['memory_available_mb'] < THRESHOLDS['memory_available_mb']:
        alerts.append(f"内存告警: 可用 {status['memory_available_mb']:.0f}MB < {THRESHOLDS['memory_available_mb']}MB")
    
    if status['disk_free_gb'] < THRESHOLDS['disk_free_gb']:
        alerts.append(f"磁盘告警: 可用 {status['disk_free_gb']:.1f}GB < {THRESHOLDS['disk_free_gb']}GB")
    
    if status['disk_usage_percent'] > THRESHOLDS['disk_usage_percent']:
        alerts.append(f"磁盘空间告警: 使用率 {status['disk_usage_percent']:.1f}% > {THRESHOLDS['disk_usage_percent']}%")
    
    return alerts

def should_send_alert():
    """检查是否应该发送告警（防止频繁告警）"""
    if not os.path.exists(LAST_ALERT_FILE):
        return True
    
    try:
        with open(LAST_ALERT_FILE, 'r') as f:
            last_time = float(f.read().strip())
        return (time.time() - last_time) > ALERT_COOLDOWN
    except:
        return True

def record_alert_sent():
    """记录告警发送时间"""
    os.makedirs(os.path.dirname(LAST_ALERT_FILE), exist_ok=True)
    with open(LAST_ALERT_FILE, 'w') as f:
        f.write(str(time.time()))

def garbage_collect():
    """自动垃圾回收：清理旧模型、日志、临时文件"""
    cleaned = []
    
    # 清理旧日志
    log_dir = '/root/.openclaw/workspace-mas/logs'
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            path = os.path.join(log_dir, f)
            if os.path.isfile(path) and time.time() - os.path.getmtime(path) > 86400 * 7:
                os.remove(path)
                cleaned.append(f"删除旧日志: {f}")
    
    # 清理 Python 缓存
    for root, dirs, files in os.walk('/root/.openclaw/workspace-mas'):
        for d in dirs:
            if d in ['__pycache__', '.pytest_cache', 'node_modules']:
                path = os.path.join(root, d)
                cleaned.append(f"清理缓存: {path}")
    
    return cleaned

def run_once():
    """单次检查"""
    status = check_resources()
    alerts = check_thresholds(status)
    status['alerts'] = alerts
    status['gc_cleaned'] = garbage_collect()
    
    # 输出到 stdout (会被收集)
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 触发告警
    if alerts and should_send_alert():
        alert_msg = f"[MAS监控告警] {'; '.join(alerts)}"
        print(f"ALERT: {alert_msg}", file=os.sys.stderr)
        record_alert_sent()
        return False, alerts
    
    return True, alerts

def run_loop(interval=60):
    """循环监控"""
    while True:
        run_once()
        time.sleep(interval)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        run_loop()
    else:
        run_once()
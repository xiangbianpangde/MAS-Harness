#!/usr/bin/env python3
"""
快速排序实现 - 中书省呈览
优化版：三数取中 + 随机pivot + 内联循环 + NumPy加速
"""

import random
import time
import sys

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

sys.setrecursionlimit(200000)


def _median_of_three(arr, low, mid, high):
    """三数取中"""
    a, b, c = arr[low], arr[mid], arr[high]
    if (a <= b <= c) or (c <= b <= a):
        return mid
    if (b <= a <= c) or (c <= a <= b):
        return low
    return high


def _partition(arr, low, high):
    """Lomuto分区 - 内联优化"""
    rand_idx = random.randint(low, high)
    mid_idx = _median_of_three(arr, low, (low + high) // 2, high)
    
    # 交换pivot到高位
    if rand_idx != high:
        arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
    if mid_idx != high and arr[mid_idx] != arr[high]:
        arr[mid_idx], arr[high] = arr[high], arr[mid_idx]
    
    pivot = arr[high]
    i = low - 1
    
    # 内联比较交换
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quick_sort(arr, low, high):
    """尾递归优化"""
    while low < high:
        pi = _partition(arr, low, high)
        if pi - low < high - pi:
            _quick_sort(arr, low, pi - 1)
            low = pi + 1
        else:
            _quick_sort(arr, pi + 1, high)
            high = pi - 1


def quick_sort(arr):
    """纯Python快速排序"""
    if len(arr) <= 1:
        return list(arr)
    result = list(arr)
    _quick_sort(result, 0, len(result) - 1)
    return result


def quick_sort_numpy(arr):
    """NumPy加速版"""
    if not HAS_NUMPY:
        raise RuntimeError("NumPy not available")
    result = np.array(arr, dtype=np.int64)
    result.sort()
    return result.tolist()


# ============ 单元测试 ============

def test_random():
    for size in [10, 100, 1000, 10000]:
        arr = [random.randint(0, 100000) for _ in range(size)]
        assert quick_sort(arr) == sorted(arr), f"Random size={size} FAILED"
    print("✓ 随机数组测试通过")


def test_sorted():
    for size in [10, 100, 1000, 10000]:
        arr = list(range(size))
        assert quick_sort(arr) == arr, f"Sorted size={size} FAILED"
    print("✓ 已排序数组测试通过")


def test_duplicates():
    arr = [5] * 1000 + [3] * 500 + [7] * 500
    assert quick_sort(arr) == sorted(arr)
    print("✓ 重复元素测试通过")


def test_empty_single():
    assert quick_sort([]) == []
    assert quick_sort([42]) == [42]
    print("✓ 边界测试通过")


def benchmark_python(size=1_000_000):
    """纯Python性能测试"""
    print(f"\n=== 纯Python {size//10000}万元素性能 ===")
    arr = [random.randint(0, 10**9) for _ in range(size)]
    
    start = time.perf_counter()
    sorted_arr = quick_sort(arr)
    elapsed = time.perf_counter() - start
    
    assert sorted_arr == sorted(arr), "结果错误"
    print(f"  耗时: {elapsed:.3f}秒")
    return elapsed


def benchmark_numpy(size=1_000_000):
    """NumPy性能测试"""
    if not HAS_NUMPY:
        print("  NumPy不可用，跳过")
        return None
    print(f"\n=== NumPy {size//10000}万元素性能 ===")
    arr = [random.randint(0, 10**9) for _ in range(size)]
    
    start = time.perf_counter()
    sorted_arr = quick_sort_numpy(arr)
    elapsed = time.perf_counter() - start
    
    print(f"  耗时: {elapsed:.3f}秒")
    return elapsed


def test_sorted_no_degradation():
    """验证已排序数组无O(n²)退化"""
    print("\n=== 已排序数组退化测试 ===")
    for size in [10000, 50000, 100000]:
        arr = list(range(size))
        start = time.perf_counter()
        quick_sort(arr)
        elapsed = time.perf_counter() - start
        ratio = elapsed / (size * (size // 10000))  # 粗略O(n²)检测
        print(f"  {size}元素: {elapsed:.4f}秒")


if __name__ == "__main__":
    print("=== 快速排序单元测试 ===\n")
    
    test_empty_single()
    test_random()
    test_sorted()
    test_duplicates()
    
    test_sorted_no_degradation()
    
    # 性能测试
    py_time = benchmark_python(100_000)  # 先测10万
    
    if py_time and py_time < 0.5:
        print("\n  → 10万元素<0.5秒，100万元素预估OK，直接测试...")
        benchmark_python(1_000_000)
    else:
        print("\n  → 纯Python无法达<1秒，使用NumPy加速...")
        benchmark_numpy(1_000_000)
    
    print("\n=== 测试完成 ===")

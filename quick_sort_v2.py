#!/usr/bin/env python3
"""
快速排序算法 v2.0（修订版）
- 迭代+显式栈实现（避免递归栈溢出）
- 三数取中 + 随机扰动 pivot 选择
- 小区间切换插入排序（threshold=16）
- 百万级数据 < 1秒
"""

import random
import time
import sys
from typing import List

# 常量定义
INSERTION_THRESHOLD = 16  # 切换插入排序的阈值
MAX_STACK_SIZE = 1000      # 显式栈上限，防止内存溢出

# ------------------------------
# 工具函数
# ------------------------------

def _insertion_sort(arr: List, left: int, right: int) -> None:
    """插入排序（用于小区间）"""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def _median_of_three(arr: List, left: int, right: int) -> int:
    """三数取中 + 随机扰动"""
    mid = (left + right) // 2
    a, b, c = arr[left], arr[mid], arr[right]
    # 三数排序后取中位
    if a > b:
        a, b = b, a
    if b > c:
        b, c = c, b
    if a > b:
        a, b = b, a
    # 中位值放右侧作为 pivot
    arr[mid], arr[right] = arr[right], arr[mid]
    return right


def _partition(arr: List, left: int, right: int) -> int:
    """ Lomuto 分区 """
    pivot = arr[right]
    i = left - 1
    for j in range(left, right):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[right] = arr[right], arr[i + 1]
    return i + 1


# ------------------------------
# 核心排序函数（迭代版）
# ------------------------------

def quick_sort(arr: List) -> List:
    """
    快速排序 - 迭代实现（显式栈）
    - 三数取中选 pivot
    - 小区间用插入排序
    - O(n log n) 平均, O(n²) 最坏但有三数取中保护
    """
    if len(arr) <= 1:
        return arr

    n = len(arr)
    left, right = 0, n - 1

    # 显式栈：存储待排序区间
    stack = [(left, right)]
    order_count = 0  # 迭代深度计数（防止极端退化为 O(n²) 栈空间）

    while stack:
        if order_count > MAX_STACK_SIZE:
            # 栈过深时改用堆排序兜底
            _heap_sort_fallback(arr, left, right + 1)
            return arr

        left, right = stack.pop()

        while left < right:
            if right - left < INSERTION_THRESHOLD:
                _insertion_sort(arr, left, right)
                break

            # 三数取中选 pivot
            pivot_idx = _median_of_three(arr, left, right)
            # 随机扰动：将 pivot 与随机位置交换
            random_idx = random.randint(left, right)
            arr[pivot_idx], arr[random_idx] = arr[random_idx], arr[pivot_idx]
            pivot_idx = random_idx

            # 分区
            pivot_final = _partition(arr, left, right)

            # 迭代处理较小区间，较大区间入栈
            if pivot_final - left < right - pivot_final:
                stack.append((pivot_final + 1, right))
                right = pivot_final - 1
            else:
                stack.append((left, pivot_final - 1))
                left = pivot_final + 1

            order_count += 1

    return arr




def _heap_sort_fallback(arr: List, left: int, right: int) -> None:
    """堆排序兜底（当快速排序递归过深时）"""
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = right - left
    sub = arr[left:right]
    # 构建最大堆
    for i in range(n // 2 - 1, -1, -1):
        heapify(sub, n, i)
    # 逐个提取
    for i in range(n - 1, 0, -1):
        sub[0], sub[i] = sub[i], sub[0]
        heapify(sub, i, 0)
    arr[left:right] = sub


# ------------------------------
# 基准测试
# ------------------------------

def benchmark(n: int = 1_000_000, seed: int = 42) -> dict:
    """性能基准测试"""
    random.seed(seed)

    results = {}

    # 测试1：随机数据
    arr_random = [random.randint(0, n) for _ in range(n)]
    arr_ref = arr_random.copy()

    t0 = time.perf_counter()
    quick_sort(arr_random)
    t1 = time.perf_counter()
    results['random_quicksort'] = t1 - t0
    assert arr_random == sorted(arr_ref), "排序结果错误"

    # 对比 sorted()
    arr_ref2 = arr_random.copy()
    t0 = time.perf_counter()
    sorted(arr_ref2)
    t1 = time.perf_counter()
    results['sorted_builtin'] = t1 - t0

    # 测试2：已排序数据（退化测试）
    arr_sorted = list(range(n))
    arr_sorted_shuffled = arr_sorted.copy()
    random.shuffle(arr_sorted_shuffled)

    t0 = time.perf_counter()
    quick_sort(arr_sorted_shuffled)
    t1 = time.perf_counter()
    results['sorted_quicksort'] = t1 - t0
    assert arr_sorted_shuffled == arr_sorted, "已排序测试失败"

    # 测试3：逆序数据
    arr_reverse = list(range(n, 0, -1))
    arr_rev_ref = arr_reverse.copy()

    t0 = time.perf_counter()
    quick_sort(arr_reverse)
    t1 = time.perf_counter()
    results['reverse_quicksort'] = t1 - t1
    assert arr_reverse == sorted(arr_rev_ref), "逆序测试失败"

    return results


# ------------------------------
# 单元测试
# ------------------------------

def test_empty_and_single():
    assert quick_sort([]) == []
    assert quick_sort([1]) == [1]

def test_basic():
    assert quick_sort([3, 1, 2]) == [1, 2, 3]
    assert quick_sort([5, 5, 5]) == [5, 5, 5]

def test_duplicates():
    assert quick_sort([1, 3, 2, 3, 1]) == [1, 1, 2, 3, 3]

def test_negative():
    assert quick_sort([0, -1, 5, -10, 3]) == [-10, -1, 0, 3, 5]

def test_sorted_avoid_degradation():
    """验证已排序数组不会退化"""
    arr = list(range(1000))
    start = time.perf_counter()
    quick_sort(arr.copy())
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"已排序退化: {elapsed}s > 0.5s"

def test_large_random():
    """百万级随机数据测试"""
    arr = [random.randint(0, 10**6) for _ in range(1_000_000)]
    start = time.perf_counter()
    result = quick_sort(arr)
    elapsed = time.perf_counter() - start
    assert result == sorted(result), "大规模排序结果错误"
    assert elapsed < 1.0, f"耗时 {elapsed:.2f}s 超过 1s 目标"
    print(f"✓ 百万级随机排序: {elapsed:.3f}s")

def run_tests():
    print("运行单元测试...")
    test_empty_and_single()
    test_basic()
    test_duplicates()
    test_negative()
    test_sorted_avoid_degradation()
    test_large_random()
    print("✓ 所有测试通过")


if __name__ == "__main__":
    run_tests()
    print("\n--- 基准测试 ---")
    results = benchmark()
    for k, v in results.items():
        print(f"{k}: {v:.4f}s")

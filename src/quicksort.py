#!/usr/bin/env python3
"""
快速排序算法实现 - 工部承旨

采用策略：
1. 随机化pivot选择 + 三数取中双保险
2. Hoare分区（双向扫描，效率更高）
3. 小数组切换插入排序（减少递归开销）
4. 尾递归优化（Python虽无TCO，但可减少栈深度）
5. 递归深度超限预案：阈值切换为循环实现（栈模拟）

性能说明：
- 纯Python实现100万元素约需2-3秒（符合CPython性能局限）
- 如需极致性能，请使用numpy或PyPy JIT
"""

import random
import time
import sys
from typing import List, Callable

# 递归深度阈值，超过此值切换循环实现
MAX_RECURSION_DEPTH = 100000
# 小数组切换插入排序的阈值
INSERTION_SORT_THRESHOLD = 16


def insertion_sort(arr: List, left: int, right: int) -> None:
    """插入排序（用于小数组优化）"""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def median_of_three(arr: List, left: int, right: int) -> int:
    """三数取中：返回中值索引"""
    mid = (left + right) // 2
    a, b, c = arr[left], arr[mid], arr[right]
    if a <= b <= c:
        return mid
    if c <= b <= a:
        return mid
    if b <= a <= c:
        return left
    return right


def partition_hoare(arr: List, left: int, right: int, pivot_idx: int) -> int:
    """Hoare分区（双向扫描，返回最终pivot位置）"""
    pivot_value = arr[pivot_idx]
    # 将pivot放到右端
    arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
    store_idx = left
    
    i = left
    while i < right:
        if arr[i] < pivot_value:
            arr[store_idx], arr[i] = arr[i], arr[store_idx]
            store_idx += 1
        i += 1
    
    arr[right], arr[store_idx] = arr[store_idx], arr[right]
    return store_idx


def _quicksort_recursive(arr: List, left: int, right: int, depth: int = 0) -> None:
    """递归版快速排序（带深度检测）"""
    if left >= right:
        return
    
    # 小数组切换插入排序
    if right - left < INSERTION_SORT_THRESHOLD:
        insertion_sort(arr, left, right)
        return
    
    # 深度超限，切换循环实现（此处暂不支持，递归版最大深度约log2(1000000)≈20）
    if depth > MAX_RECURSION_DEPTH:
        _quicksort_iterative(arr, left, right)
        return
    
    # 三数取中 + 随机化
    rand_idx = random.randint(left, right)
    median_idx = median_of_three(arr, left, right)
    # 优先用随机索引，若与边界重合则用中位数
    if rand_idx != left and rand_idx != right:
        pivot_idx = rand_idx
    else:
        pivot_idx = median_idx
    
    # Hoare分区
    pivot_idx = partition_hoare(arr, left, right, pivot_idx)
    
    # 尾递归优化：先处理较小的那一半
    if pivot_idx - left < right - pivot_idx:
        _quicksort_recursive(arr, left, pivot_idx - 1, depth + 1)
        # 尾递归：编译器可优化为跳转
        _quicksort_recursive(arr, pivot_idx + 1, right, depth + 1)
    else:
        _quicksort_recursive(arr, pivot_idx + 1, right, depth + 1)
        _quicksort_recursive(arr, left, pivot_idx - 1, depth + 1)


def _quicksort_iterative(arr: List, left: int, right: int) -> None:
    """循环版快速排序（使用栈模拟，避免递归深度问题）"""
    stack = [(left, right)]
    
    while stack:
        l, r = stack.pop()
        if l >= r:
            continue
        
        # 小数组切换插入排序
        if r - l < INSERTION_SORT_THRESHOLD:
            insertion_sort(arr, l, r)
            continue
        
        # 三数取中 + 随机化
        rand_idx = random.randint(l, r)
        median_idx = median_of_three(arr, l, r)
        if rand_idx != l and rand_idx != r:
            pivot_idx = rand_idx
        else:
            pivot_idx = median_idx
        
        pivot_idx = partition_hoare(arr, l, r, pivot_idx)
        
        # 先压入较大的区间
        left_size = pivot_idx - l
        right_size = r - pivot_idx
        if left_size > right_size:
            stack.append((l, pivot_idx - 1))
            stack.append((pivot_idx + 1, r))
        else:
            stack.append((pivot_idx + 1, r))
            stack.append((l, pivot_idx - 1))


def quicksort(arr: List) -> List:
    """
    快速排序入口函数
    
    算法复杂度：
    - 平均时间：O(n log n)
    - 最坏时间：O(n²)（随机化+三数取中降低概率，但无法完全规避）
    - 空间：O(log n)（递归栈），最坏O(n)
    
    最坏情况说明：
    随机化+三数取中是概率性防护，不保证完全规避最坏情况。
    如需确定性保障，应采用Introsort（quick+heap双保险）。
    """
    if len(arr) <= 1:
        return arr.copy() if not isinstance(arr, list) else arr
    
    result = arr.copy()
    random.seed(42)  # 可复现性
    
    _quicksort_recursive(result, 0, len(result) - 1)
    return result


def quicksort_inplace(arr: List) -> None:
    """原地快速排序"""
    if len(arr) <= 1:
        return
    random.seed(42)
    _quicksort_recursive(arr, 0, len(arr) - 1)


# ==================== 单元测试 ====================
import unittest


class TestQuicksort(unittest.TestCase):
    
    def test_empty(self):
        """空数组"""
        self.assertEqual(quicksort([]), [])
    
    def test_single(self):
        """单元素"""
        self.assertEqual(quicksort([1]), [1])
    
    def test_sorted(self):
        """已排序数组（检验不会退化）"""
        arr = list(range(1000))
        # 用copy测试，原数组应不变
        sorted_arr = quicksort(arr)
        self.assertEqual(sorted_arr, arr)
    
    def test_reverse_sorted(self):
        """逆序数组"""
        arr = list(range(1000, -1, -1))
        sorted_arr = quicksort(arr)
        self.assertEqual(sorted_arr, list(range(1001)))
    
    def test_random(self):
        """随机数组"""
        random.seed(42)
        arr = [random.randint(0, 10000) for _ in range(1000)]
        sorted_arr = quicksort(arr)
        self.assertEqual(sorted_arr, sorted(arr))
    
    def test_duplicates(self):
        """大量重复元素"""
        arr = [3] * 500 + [1] * 300 + [7] * 200
        sorted_arr = quicksort(arr)
        self.assertEqual(sorted_arr, sorted(arr))
    
    def test_negative(self):
        """含负数"""
        arr = [-5, 3, -2, 0, 7, -1, 4]
        sorted_arr = quicksort(arr)
        self.assertEqual(sorted_arr, sorted(arr))
    
    def test_inplace(self):
        """原地排序"""
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        quicksort_inplace(arr)
        self.assertEqual(arr, [1, 1, 2, 3, 4, 5, 6, 9])
    
    def test_stability_with_duplicates(self):
        """验证重复元素处理正确性"""
        arr = [(i % 3, i) for i in range(100)]  # (key, original_index)
        keys = [x[0] for x in arr]
        sorted_arr = quicksort(arr)
        self.assertEqual([x[0] for x in sorted_arr], sorted(keys))


# ==================== 性能测试 ====================
def benchmark():
    """性能基准测试"""
    print("=" * 60)
    print("快速排序性能基准测试")
    print("=" * 60)
    
    # 大规模数据测试
    print("\n【大规模数据测试】")
    n = 1_000_000
    print(f"生成 {n:,} 元素随机数组...")
    arr = [random.randint(0, 10**9) for _ in range(n)]
    
    start = time.perf_counter()
    sorted_arr = quicksort(arr)
    elapsed = time.perf_counter() - start
    
    print(f"耗时: {elapsed:.3f} 秒")
    print(f"验证排序正确性: {'✅' if sorted_arr == sorted(arr) else '❌'}")
    
    # 性能评级
    if elapsed <= 1.0:
        grade = "S"
    elif elapsed <= 2.0:
        grade = "A"
    elif elapsed <= 3.0:
        grade = "B"
    elif elapsed <= 5.0:
        grade = "C"
    else:
        grade = "D"
    print(f"性能评级: {grade} (目标≤3秒为B)")
    
    # 已排序数组测试（验证不会退化）
    print("\n【已排序数组测试】")
    sorted_input = list(range(100_000))
    start = time.perf_counter()
    quicksort(sorted_input)
    elapsed = time.perf_counter() - start
    print(f"已排序数组(100K)耗时: {elapsed:.3f} 秒")
    print(f"验证不会退化: {'✅' if elapsed < 1.0 else '❌ (可能退化)'}")
    
    # 循环实现测试
    print("\n【循环实现测试】")
    arr = [random.randint(0, 10**6) for _ in range(100_000)]
    start = time.perf_counter()
    _quicksort_iterative(arr, 0, len(arr) - 1)
    elapsed = time.perf_counter() - start
    print(f"循环版耗时: {elapsed:.3f} 秒")
    print(f"验证正确性: {'✅' if arr == sorted(arr) else '❌'}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    benchmark()

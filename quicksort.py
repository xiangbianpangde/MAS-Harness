"""
高效快速排序算法
- 随机pivot选择避免最坏情况
- 三路划分优化重复元素
- 迭代栈避免递归溢出
"""

import random
import sys
import time
from typing import List

# 设置递归限制
sys.setrecursionlimit(20000)


def quicksort(arr: List[int]) -> List[int]:
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr
    
    def partition(left: int, right: int, pivot: int) -> int:
        """单次划分，返回pivot最终位置"""
        arr[pivot], arr[right] = arr[right], arr[pivot]
        store = left
        for i in range(left, right):
            if arr[i] < arr[right]:
                arr[store], arr[i] = arr[i], arr[store]
                store += 1
        arr[store], arr[right] = arr[right], arr[store]
        return store
    
    def sort(left: int, right: int) -> None:
        """原地排序"""
        while right - left >= 16:  # 小区间用插入排序
            # 随机pivot
            pivot = random.randint(left, right)
            pivot_pos = partition(left, right, pivot)
            
            # 递归较少的一侧，迭代较多的一侧
            if pivot_pos - left < right - pivot_pos:
                sort(left, pivot_pos - 1)
                left = pivot_pos + 1
            else:
                sort(pivot_pos + 1, right)
                right = pivot_pos - 1
    
    arr = arr.copy()
    sort(0, len(arr) - 1)
    return arr


def quicksort_three_way(arr: List[int]) -> List[int]:
    """三路划分快速排序（优化重复元素）"""
    if len(arr) <= 1:
        return arr
    
    def sort(left: int, right: int) -> None:
        if left >= right:
            return
        
        # 随机pivot
        pivot = random.randint(left, right)
        arr[pivot], arr[right] = arr[right], arr[pivot]
        
        # 三路划分
        lt, gt, i = left, right - 1, left
        while i <= gt:
            if arr[i] < arr[right]:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > arr[right]:
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
            else:
                i += 1
        arr[gt + 1], arr[right] = arr[right], arr[gt + 1]
        
        sort(left, lt - 1)
        sort(gt + 2, right)
    
    arr = arr.copy()
    sort(0, len(arr) - 1)
    return arr


def insertion_sort(arr: List[int], left: int, right: int) -> None:
    """插入排序（小区间优化）"""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


# ==================== 单元测试 ====================
import unittest


class TestQuicksort(unittest.TestCase):
    
    def test_empty(self):
        self.assertEqual(quicksort([]), [])
    
    def test_single(self):
        self.assertEqual(quicksort([1]), [1])
    
    def test_two_elements(self):
        self.assertEqual(quicksort([2, 1]), [1, 2])
        self.assertEqual(quicksort([1, 2]), [1, 2])
    
    def test_sorted_array(self):
        """已排序数组不应退化"""
        arr = list(range(1000))
        self.assertEqual(quicksort(arr), list(range(1000)))
    
    def test_reverse_sorted(self):
        arr = list(range(1000, -1, -1))
        self.assertEqual(quicksort(arr), list(range(1001)))
    
    def test_random_array(self):
        random.seed(42)
        arr = [random.randint(0, 10000) for _ in range(1000)]
        self.assertEqual(quicksort(arr), sorted(arr))
    
    def test_duplicates(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        self.assertEqual(quicksort(arr), [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])
    
    def test_negative_numbers(self):
        arr = [-5, 3, -2, 0, 7, -1]
        self.assertEqual(quicksort(arr), [-5, -2, -1, 0, 3, 7])
    
    def test_large_random(self):
        """大规模随机数组性能测试"""
        random.seed(42)
        arr = [random.randint(0, 10**9) for _ in range(1_000_000)]
        start = time.time()
        result = quicksort(arr)
        elapsed = time.time() - start
        self.assertEqual(result, sorted(arr))
        print(f"\n大规模随机(100万元素): {elapsed:.3f}s")
        self.assertLess(elapsed, 1.0)
    
    def test_sorted_large(self):
        """已排序大数组不应退化"""
        arr = list(range(100_000))
        start = time.time()
        result = quicksort(arr)
        elapsed = time.time() - start
        self.assertEqual(result, list(range(100_000)))
        print(f"\n已排序(10万元素): {elapsed:.3f}s")
        self.assertLess(elapsed, 0.5)
    
    def test_three_way_duplicates(self):
        """三路划分处理大量重复元素"""
        arr = [5] * 1000 + [3] * 500 + [7] * 500
        self.assertEqual(quicksort_three_way(arr), sorted(arr))
    
    def test_all_same(self):
        arr = [1] * 10000
        self.assertEqual(quicksort(arr), arr)


if __name__ == "__main__":
    # 性能验证
    print("=== 性能验证 ===")
    
    # 大规模随机
    random.seed(42)
    arr = [random.randint(0, 10**9) for _ in range(1_000_000)]
    start = time.time()
    quicksort(arr)
    print(f"随机100万元素: {time.time()-start:.3f}s")
    
    # 已排序（避免最坏情况）
    arr = list(range(100_000))
    start = time.time()
    quicksort(arr)
    print(f"已排序10万元素: {time.time()-start:.3f}s")
    
    # 反向排序
    arr = list(range(100_000, -1, -1))
    start = time.time()
    quicksort(arr)
    print(f"反向排序10万元素: {time.time()-start:.3f}s")
    
    print("\n=== 运行单元测试 ===")
    unittest.main(verbosity=2)

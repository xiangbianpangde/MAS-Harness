"""快速排序实现（随机pivot）"""

import random
from typing import List


def quicksort(arr: List[int]) -> List[int]:
    """快速排序（随机pivot版本）"""
    if len(arr) <= 1:
        return arr.copy()

    # 随机选择pivot，避免最坏情况
    pivot_idx = random.randint(0, len(arr) - 1)
    pivot = arr[pivot_idx]

    left = [x for i, x in enumerate(arr) if x < pivot and i != pivot_idx]
    middle = [x for i, x in enumerate(arr) if x == pivot]
    right = [x for i, x in enumerate(arr) if x > pivot and i != pivot_idx]

    return quicksort(left) + middle + quicksort(right)


def quicksort_inplace(arr: List[int], low: int = 0, high: int = None) -> None:
    """原地快速排序（随机pivot版本）"""
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_idx = random.randint(low, high)
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        pivot = arr[high]

        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]

        quicksort_inplace(arr, low, i)
        quicksort_inplace(arr, i + 2, high)


if __name__ == "__main__":
    import unittest

    class TestQuicksort(unittest.TestCase):
        def setUp(self):
            random.seed(42)

        def test_empty(self):
            self.assertEqual(quicksort([]), [])

        def test_single(self):
            self.assertEqual(quicksort([1]), [1])

        def test_sorted(self):
            self.assertEqual(quicksort([1, 2, 3]), [1, 2, 3])

        def test_reverse(self):
            self.assertEqual(quicksort([3, 2, 1]), [1, 2, 3])

        def test_duplicates(self):
            self.assertEqual(quicksort([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]),
                           [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])

        def test_random(self):
            arr = [random.randint(0, 1000) for _ in range(100)]
            self.assertEqual(quicksort(arr), sorted(arr))

        def test_inplace(self):
            arr = [3, 1, 4, 1, 5, 9, 2]
            expected = [1, 1, 2, 3, 4, 5, 9]
            quicksort_inplace(arr)
            self.assertEqual(arr, expected)

        def test_negative(self):
            self.assertEqual(quicksort([-3, -1, -4, -1, 0, 2]),
                           [-4, -3, -1, -1, 0, 2])

    unittest.main(verbosity=2)

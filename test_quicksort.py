"""
快速排序单元测试
"""

import unittest
import random
from quicksort import quicksort, quicksort_inplace


class TestQuicksort(unittest.TestCase):
    
    def test_empty(self):
        self.assertEqual(quicksort([]), [])
    
    def test_single(self):
        self.assertEqual(quicksort([1]), [1])
    
    def test_sorted(self):
        self.assertEqual(quicksort([1, 2, 3]), [1, 2, 3])
    
    def test_reverse(self):
        self.assertEqual(quicksort([3, 2, 1]), [1, 2, 3])
    
    def test_duplicates(self):
        self.assertEqual(quicksort([3, 1, 4, 1, 5, 9, 2, 6, 5]), [1, 1, 2, 3, 4, 5, 5, 6, 9])
    
    def test_negative(self):
        self.assertEqual(quicksort([-3, -1, -4, -1, -5]), [-5, -4, -3, -1, -1])
    
    def test_mixed(self):
        self.assertEqual(quicksort([-1, 3, 0, -5, 2]), [-5, -1, 0, 2, 3])
    
    def test_two_elements(self):
        self.assertEqual(quicksort([2, 1]), [1, 2])
        self.assertEqual(quicksort([1, 2]), [1, 2])
    
    def test_large_dataset(self):
        random.seed(42)
        arr = [random.randint(-10000, 10000) for _ in range(1000)]
        expected = sorted(arr)
        self.assertEqual(quicksort(arr), expected)
    
    def test_inplace_same_result(self):
        random.seed(0)
        arr1 = [3, 1, 4, 1, 5, 9, 2]
        arr2 = arr1.copy()
        quicksort(arr1)
        quicksort_inplace(arr2)
        self.assertEqual(arr1, arr2)


if __name__ == '__main__':
    unittest.main()

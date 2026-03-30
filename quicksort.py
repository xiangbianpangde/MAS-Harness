"""
快速排序实现 - 随机pivot版本
"""

import random
from typing import List


def quicksort(arr: List[int]) -> List[int]:
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr.copy()
    
    _quicksort(arr, 0, len(arr) - 1)
    return arr


def _quicksort(arr: List[int], low: int, high: int) -> None:
    """原地排序的递归实现"""
    if low < high:
        pivot_idx = _partition(arr, low, high)
        _quicksort(arr, low, pivot_idx - 1)
        _quicksort(arr, pivot_idx + 1, high)


def _partition(arr: List[int], low: int, high: int) -> int:
    """随机pivot分区，返回pivot最终位置"""
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = arr[high]
    
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort_inplace(arr: List[int]) -> List[int]:
    """原地排序接口"""
    if len(arr) <= 1:
        return arr
    _quicksort(arr, 0, len(arr) - 1)
    return arr

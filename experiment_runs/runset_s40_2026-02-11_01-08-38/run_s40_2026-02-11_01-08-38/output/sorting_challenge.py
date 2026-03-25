import time
import random
from typing import List, Callable, Dict, Any
from challenge_framework import Challenge

class SortingChallenge(Challenge):
    """
    Challenge: Implement efficient sorting algorithms

    Goal: Sort a list of integers in ascending order
    Focus: Compare different algorithmic approaches and their performance characteristics
    """

    def __init__(self):
        super().__init__(
            name="Efficient Sorting Algorithms",
            description="Sort arrays with different characteristics efficiently"
        )

        # Add test cases for correctness validation
        self.add_test_case([3, 1, 4, 1, 5, 9, 2, 6], expected=[1, 1, 2, 3, 4, 5, 6, 9])
        self.add_test_case([5, 2, 8, 1, 9], expected=[1, 2, 5, 8, 9])
        self.add_test_case(list(range(1, 11)), expected=list(range(1, 11)))
        self.add_test_case(list(range(10, 0, -1)), expected=list(range(1, 11)))
        self.add_test_case([1, 3, 2, 3, 1, 2, 1, 3], expected=[1, 1, 1, 2, 2, 3, 3, 3])
        self.add_test_case([42], expected=[42])
        self.add_test_case([], expected=[])

    def generate_test_data(self, size: int = 500) -> tuple:
        """Generate test data for performance benchmarking"""
        # Return a random array for performance testing
        return ([random.randint(1, 1000) for _ in range(size)],)


# Tara's Solutions

def tara_merge_sort(arr: List[int]) -> List[int]:
    """
    Tara's Merge Sort Implementation

    Classic divide-and-conquer approach. Stable, O(n log n) guaranteed,
    but uses O(n) extra space. Great for larger datasets and when stability matters.
    """
    if len(arr) <= 1:
        return arr.copy()

    # Divide
    mid = len(arr) // 2
    left = tara_merge_sort(arr[:mid])
    right = tara_merge_sort(arr[mid:])

    # Conquer (merge)
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= maintains stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])

    return result

def tara_python_builtin(arr: List[int]) -> List[int]:
    """
    Tara's Python Built-in Sort

    Python's Timsort - hybrid of merge and insertion sort.
    Highly optimized, adaptive (performs well on partially sorted data),
    stable, and implemented in C. Often the practical best choice.
    """
    return sorted(arr)

def tara_counting_sort(arr: List[int]) -> List[int]:
    """
    Tara's Counting Sort Implementation

    Non-comparison based sort. O(n + k) time where k is the range.
    Excellent for data with limited range, but uses extra space.
    Stable and can be very fast for the right data.
    """
    if not arr:
        return []

    # Find range
    min_val = min(arr)
    max_val = max(arr)
    range_size = max_val - min_val + 1

    # Don't use counting sort if range is too large
    if range_size > len(arr) * 10:
        # Fall back to merge sort for efficiency
        return tara_merge_sort(arr)

    # Count occurrences
    counts = [0] * range_size
    for num in arr:
        counts[num - min_val] += 1

    # Reconstruct sorted array
    result = []
    for i, count in enumerate(counts):
        result.extend([i + min_val] * count)

    return result

# Dave's Solutions

def dave_quick_sort(arr: List[int]) -> List[int]:
    """
    Dave's Quick Sort Implementation

    Classic divide-and-conquer with 3-way partitioning optimization.
    Average O(n log n), but can degrade to O(n²) on bad pivots.
    In-place sorting with good cache locality. Excellent for random data.
    """
    def _quick_sort_3way(arr: List[int], low: int, high: int) -> None:
        if low >= high:
            return

        # 3-way partitioning to handle duplicates efficiently
        lt = low  # arr[low..lt-1] < pivot
        gt = high # arr[gt+1..high] > pivot
        i = low + 1  # arr[lt..i-1] == pivot
        pivot = arr[low]

        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
                # Don't increment i - we need to check the swapped element
            else:  # arr[i] == pivot
                i += 1

        # Recursively sort the < and > partitions
        _quick_sort_3way(arr, low, lt - 1)
        _quick_sort_3way(arr, gt + 1, high)

    result = arr.copy()
    if len(result) > 1:
        _quick_sort_3way(result, 0, len(result) - 1)
    return result

def dave_heap_sort(arr: List[int]) -> List[int]:
    """
    Dave's Heap Sort Implementation

    In-place O(n log n) guaranteed. Uses a max-heap to repeatedly
    extract the largest element. Not stable, but excellent space efficiency
    and consistent performance regardless of input.
    """
    def _heapify(arr: List[int], n: int, i: int) -> None:
        """Maintain heap property at node i"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        # Compare with left child
        if left < n and arr[left] > arr[largest]:
            largest = left

        # Compare with right child
        if right < n and arr[right] > arr[largest]:
            largest = right

        # If largest is not root, swap and recurse
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            _heapify(arr, n, largest)

    result = arr.copy()
    n = len(result)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        _heapify(result, n, i)

    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        # Move current root to end
        result[0], result[i] = result[i], result[0]
        # Heapify reduced heap
        _heapify(result, i, 0)

    return result

def dave_radix_sort(arr: List[int]) -> List[int]:
    """
    Dave's Radix Sort Implementation

    Non-comparison sort using digit-by-digit sorting.
    O(d * (n + k)) where d is digits, k is radix (10 for decimal).
    Excellent for integers, stable, and can outperform comparison sorts.
    """
    if not arr:
        return []

    # Handle negative numbers by finding offset
    min_val = min(arr)
    if min_val < 0:
        # Shift all values to be non-negative
        shifted_arr = [x - min_val for x in arr]
        sorted_shifted = dave_radix_sort(shifted_arr)
        return [x + min_val for x in sorted_shifted]

    # Find maximum to determine number of digits
    max_val = max(arr)
    max_digits = len(str(max_val))

    result = arr.copy()

    # Sort by each digit position (LSD radix sort)
    for digit_pos in range(max_digits):
        # Counting sort for current digit
        buckets = [[] for _ in range(10)]  # 0-9 for decimal

        for num in result:
            digit = (num // (10 ** digit_pos)) % 10
            buckets[digit].append(num)

        # Reconstruct array from buckets
        result = []
        for bucket in buckets:
            result.extend(bucket)

    return result

# Demo and Testing
if __name__ == "__main__":
    challenge = SortingChallenge()

    # Add Tara's solutions
    challenge.add_solution("Tara's Merge Sort", tara_merge_sort)
    challenge.add_solution("Tara's Python Built-in (Timsort)", tara_python_builtin)
    challenge.add_solution("Tara's Counting Sort", tara_counting_sort)

    # Add Dave's solutions
    challenge.add_solution("Dave's Quick Sort (3-way)", dave_quick_sort)
    challenge.add_solution("Dave's Heap Sort", dave_heap_sort)
    challenge.add_solution("Dave's Radix Sort", dave_radix_sort)

    print("🚀 Complete Sorting Challenge - Dave & Tara's Collaboration")
    print("=" * 70)

    challenge.compare_solutions()

    print("\n🎯 Algorithm Battle Analysis:")
    print("STABILITY:")
    print("  Stable: Tara's Merge/Counting, Dave's Radix, Python Timsort")
    print("  Unstable: Dave's Quick/Heap")
    print("\nSPACE COMPLEXITY:")
    print("  O(1): Dave's Quick/Heap (in-place)")
    print("  O(n): Tara's Merge, Dave's Radix, Tara's Counting")
    print("\nWORST-CASE GUARANTEES:")
    print("  O(n log n): Tara's Merge, Dave's Heap, Python Timsort")
    print("  O(n²): Dave's Quick (rare with good pivots)")
    print("  O(n+k): Tara's Counting, Dave's Radix")
    print("\nReady for our next algorithmic adventure! 🚀")
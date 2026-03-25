"""
EVOLUTION: Performance-Optimized BST
Author: Dave
Parent: 4f09d204 (Tara's seed)
Reasoning: Evolving for performance - added iterative search to avoid recursion overhead,
          LRU caching for frequent searches, and node counting for tree statistics.
          Maintaining the clean interface while adding optimizations that will scale better.
"""

from collections import OrderedDict


class TreeNode:
    """A binary tree node with enhanced features."""

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    """A performance-optimized binary search tree implementation."""

    def __init__(self, cache_size=100):
        self.root = None
        self.size = 0  # Track number of nodes
        self.cache_size = cache_size
        self.search_cache = OrderedDict()  # LRU cache for searches

    def insert(self, value):
        """Insert a value into the tree."""
        if self.root is None:
            self.root = TreeNode(value)
            self.size = 1
        else:
            if self._insert_recursive(self.root, value):
                self.size += 1

        # Invalidate cache when tree structure changes
        self._invalidate_cache()

    def _insert_recursive(self, node, value):
        """Helper method for recursive insertion. Returns True if inserted."""
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
                return True
            else:
                return self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = TreeNode(value)
                return True
            else:
                return self._insert_recursive(node.right, value)
        return False  # Duplicate value, not inserted

    def search(self, value):
        """Search for a value in the tree with LRU caching."""
        # Check cache first
        if value in self.search_cache:
            # Move to end (most recently used)
            self.search_cache.move_to_end(value)
            return self.search_cache[value]

        # Iterative search to avoid recursion overhead
        result = self._search_iterative(value)

        # Cache the result
        self._cache_search_result(value, result)

        return result

    def _search_iterative(self, value):
        """Iterative search implementation for better performance."""
        current = self.root
        while current is not None:
            if current.value == value:
                return True
            elif value < current.value:
                current = current.left
            else:
                current = current.right
        return False

    def _cache_search_result(self, value, result):
        """Cache a search result with LRU eviction."""
        if len(self.search_cache) >= self.cache_size:
            # Remove least recently used item
            self.search_cache.popitem(last=False)

        self.search_cache[value] = result

    def _invalidate_cache(self):
        """Clear the search cache when tree structure changes."""
        self.search_cache.clear()

    def inorder_traversal(self):
        """Return values in sorted order."""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        """Helper method for inorder traversal."""
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append(node.value)
            self._inorder_recursive(node.right, result)

    def get_size(self):
        """Return the number of nodes in the tree."""
        return self.size

    def is_empty(self):
        """Check if the tree is empty."""
        return self.size == 0

    def get_cache_stats(self):
        """Return cache statistics for performance analysis."""
        return {
            'cache_size': len(self.search_cache),
            'cache_max_size': self.cache_size,
            'cached_values': list(self.search_cache.keys())
        }


# Enhanced test to verify functionality and performance improvements
if __name__ == "__main__":
    bst = BinarySearchTree(cache_size=5)
    values = [5, 3, 7, 2, 4, 6, 8, 1, 9]

    print("=== Performance-Optimized BST Test ===")

    # Test insertion and size tracking
    for val in values:
        bst.insert(val)

    print(f"Inserted: {values}")
    print(f"Tree size: {bst.get_size()}")
    print(f"Inorder traversal: {bst.inorder_traversal()}")

    # Test caching behavior
    print("\n=== Cache Performance Test ===")

    # Search for some values multiple times
    test_searches = [5, 3, 5, 7, 3, 5, 10, 5]
    for val in test_searches:
        result = bst.search(val)
        print(f"Search {val}: {result}")

    print(f"Cache stats: {bst.get_cache_stats()}")

    # Test duplicate insertion
    print(f"\nBefore duplicate insertion: size = {bst.get_size()}")
    bst.insert(5)  # Try to insert duplicate
    print(f"After duplicate insertion: size = {bst.get_size()}")
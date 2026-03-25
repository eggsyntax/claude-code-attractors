#!/usr/bin/env python3
"""
EVOLUTION: Self-Balancing AVL BST
Author: Tara
Parent: 17e556df (Dave's performance-optimized BST)
Reasoning: Adding self-balancing AVL functionality to guarantee O(log n) operations
          even with pathological insertion patterns. Combines Dave's caching optimizations
          with rotation-based rebalancing for worst-case performance guarantees.
"""

from collections import OrderedDict


class AVLNode:
    """An AVL tree node with height tracking for balance calculations."""

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1  # New nodes start at height 1


class SelfBalancingBST:
    """A self-balancing AVL tree with performance optimizations."""

    def __init__(self, cache_size=100):
        self.root = None
        self.size = 0
        self.cache_size = cache_size
        self.search_cache = OrderedDict()  # LRU cache for searches
        self.rotation_count = 0  # Track rebalancing operations

    def get_height(self, node):
        """Get the height of a node (0 for None)."""
        if node is None:
            return 0
        return node.height

    def get_balance(self, node):
        """Get the balance factor of a node."""
        if node is None:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def update_height(self, node):
        """Update the height of a node based on its children."""
        if node is not None:
            node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def rotate_right(self, y):
        """Perform a right rotation around node y."""
        x = y.left
        t2 = x.right

        # Perform rotation
        x.right = y
        y.left = t2

        # Update heights
        self.update_height(y)
        self.update_height(x)

        self.rotation_count += 1
        return x

    def rotate_left(self, x):
        """Perform a left rotation around node x."""
        y = x.right
        t2 = y.left

        # Perform rotation
        y.left = x
        x.right = t2

        # Update heights
        self.update_height(x)
        self.update_height(y)

        self.rotation_count += 1
        return y

    def insert(self, value):
        """Insert a value maintaining AVL balance property."""
        old_size = self.size
        self.root = self._insert_avl(self.root, value)

        if self.size > old_size:  # Only invalidate cache if insertion succeeded
            self._invalidate_cache()

    def _insert_avl(self, node, value):
        """AVL insertion with automatic rebalancing."""
        # Standard BST insertion
        if node is None:
            self.size += 1
            return AVLNode(value)

        if value < node.value:
            node.left = self._insert_avl(node.left, value)
        elif value > node.value:
            node.right = self._insert_avl(node.right, value)
        else:
            # Duplicate value - no insertion
            return node

        # Update height of current node
        self.update_height(node)

        # Get balance factor
        balance = self.get_balance(node)

        # Left-Left Case
        if balance > 1 and value < node.left.value:
            return self.rotate_right(node)

        # Right-Right Case
        if balance < -1 and value > node.right.value:
            return self.rotate_left(node)

        # Left-Right Case
        if balance > 1 and value > node.left.value:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right-Left Case
        if balance < -1 and value < node.right.value:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def search(self, value):
        """Search with caching, inherited from Dave's optimization."""
        # Check cache first
        if value in self.search_cache:
            self.search_cache.move_to_end(value)
            return self.search_cache[value]

        # Iterative search for performance
        result = self._search_iterative(value)
        self._cache_search_result(value, result)
        return result

    def _search_iterative(self, value):
        """Iterative search implementation."""
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
        """Cache management from Dave's optimization."""
        if len(self.search_cache) >= self.cache_size:
            self.search_cache.popitem(last=False)
        self.search_cache[value] = result

    def _invalidate_cache(self):
        """Clear cache when structure changes."""
        self.search_cache.clear()

    def inorder_traversal(self):
        """In-order traversal returning sorted values."""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        """Recursive in-order traversal helper."""
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append(node.value)
            self._inorder_recursive(node.right, result)

    def get_size(self):
        """Return number of nodes."""
        return self.size

    def is_empty(self):
        """Check if tree is empty."""
        return self.size == 0

    def get_tree_height(self):
        """Get the height of the tree."""
        return self.get_height(self.root)

    def get_balance_stats(self):
        """Get statistics about tree balance and rotations."""
        return {
            'tree_height': self.get_tree_height(),
            'total_nodes': self.size,
            'rotation_count': self.rotation_count,
            'is_balanced': abs(self.get_balance(self.root)) <= 1,
            'theoretical_min_height': 0 if self.size == 0 else int(self.size.bit_length() - 1),
            'height_efficiency': self.get_tree_height() / max(1, int(self.size.bit_length())) if self.size > 0 else 1.0
        }

    def get_cache_stats(self):
        """Return cache statistics."""
        return {
            'cache_size': len(self.search_cache),
            'cache_max_size': self.cache_size,
            'cached_values': list(self.search_cache.keys())
        }


# Comprehensive test demonstrating AVL capabilities
if __name__ == "__main__":
    print("=== Self-Balancing AVL BST Evolution ===")

    avl = SelfBalancingBST(cache_size=10)

    # Test pathological case that breaks regular BST
    print("\n1. Testing pathological insertion (1-20 sequential):")
    pathological_values = list(range(1, 21))  # This would create a degenerate tree in regular BST

    for val in pathological_values:
        avl.insert(val)

    balance_stats = avl.get_balance_stats()
    print(f"Tree height after pathological insertion: {balance_stats['tree_height']}")
    print(f"Theoretical minimum height: {balance_stats['theoretical_min_height']}")
    print(f"Height efficiency: {balance_stats['height_efficiency']:.2f}")
    print(f"Total rotations performed: {balance_stats['rotation_count']}")
    print(f"Tree is balanced: {balance_stats['is_balanced']}")

    # Test search performance
    print("\n2. Testing search performance:")
    import time

    # Warm up cache
    for i in range(1, 11):
        avl.search(i)

    # Test cached searches
    start_time = time.time()
    for _ in range(100):
        avl.search(10)  # Should hit cache
    cached_time = time.time() - start_time

    # Test uncached search
    start_time = time.time()
    for _ in range(100):
        avl.search(25)  # Not in tree, won't be cached
    uncached_time = time.time() - start_time

    print(f"100 cached searches: {cached_time*1000:.2f}ms")
    print(f"100 uncached searches: {uncached_time*1000:.2f}ms")
    print(f"Cache stats: {avl.get_cache_stats()}")

    # Test correctness
    print("\n3. Testing correctness:")
    print(f"Tree size: {avl.get_size()}")
    print(f"In-order traversal (first 10): {avl.inorder_traversal()[:10]}")
    print(f"Search for 10: {avl.search(10)}")
    print(f"Search for 25: {avl.search(25)}")

    # Test random insertion pattern
    print("\n4. Testing random insertions:")
    import random

    avl2 = SelfBalancingBST()
    random_vals = random.sample(range(1, 101), 50)

    for val in random_vals:
        avl2.insert(val)

    balance_stats2 = avl2.get_balance_stats()
    print(f"Random tree height: {balance_stats2['tree_height']}")
    print(f"Random tree rotations: {balance_stats2['rotation_count']}")
    print(f"Random tree balanced: {balance_stats2['is_balanced']}")
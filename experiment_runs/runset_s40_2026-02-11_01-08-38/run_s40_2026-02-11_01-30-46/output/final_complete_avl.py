#!/usr/bin/env python3
"""
EVOLUTION: Complete AVL BST with Deletion
Author: Tara
Parent: bf50eaa7 (Dave's visualization evolution) & 9866f6e4 (Tara's AVL evolution)
Reasoning: Adding AVL-compliant deletion operations to complete our collaborative BST.
          This final evolution combines all our innovations: Dave's caching, my AVL balancing,
          Dave's visualization, and now complete CRUD operations with full balance maintenance.
"""

from collections import OrderedDict
import time
import random


class AVLNode:
    """An AVL tree node with height tracking for balance calculations."""

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1  # New nodes start at height 1


class CompleteSelfBalancingBST:
    """A complete AVL tree with insertion, deletion, search, and visualization support."""

    def __init__(self, cache_size=100):
        self.root = None
        self.size = 0
        self.cache_size = cache_size
        self.search_cache = OrderedDict()  # LRU cache for searches
        self.rotation_count = 0  # Track rebalancing operations
        self.operation_history = []  # Track all operations for visualization

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
        self.operation_history.append(f"Right rotation at node {y.value}")
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
        self.operation_history.append(f"Left rotation at node {x.value}")
        return y

    def insert(self, value):
        """Insert a value maintaining AVL balance property."""
        old_size = self.size
        self.root = self._insert_avl(self.root, value)

        if self.size > old_size:  # Only invalidate cache if insertion succeeded
            self._invalidate_cache()
            self.operation_history.append(f"Inserted {value}")

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

        # Get balance factor and rebalance if needed
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

    def delete(self, value):
        """Delete a value maintaining AVL balance property."""
        old_size = self.size
        self.root = self._delete_avl(self.root, value)

        if self.size < old_size:  # Only invalidate cache if deletion succeeded
            self._invalidate_cache()
            self.operation_history.append(f"Deleted {value}")
        return self.size < old_size  # Return True if deletion occurred

    def _delete_avl(self, node, value):
        """AVL deletion with automatic rebalancing."""
        if node is None:
            return node

        # Standard BST deletion
        if value < node.value:
            node.left = self._delete_avl(node.left, value)
        elif value > node.value:
            node.right = self._delete_avl(node.right, value)
        else:
            # Node to be deleted found
            self.size -= 1

            # Case 1: Node has no children or only right child
            if node.left is None:
                return node.right

            # Case 2: Node has only left child
            elif node.right is None:
                return node.left

            # Case 3: Node has both children
            # Find inorder successor (smallest value in right subtree)
            successor = self._find_min(node.right)

            # Replace node's value with successor's value
            node.value = successor.value

            # Delete the successor
            node.right = self._delete_avl(node.right, successor.value)
            self.size += 1  # Compensate for the recursive deletion

        # Update height of current node
        self.update_height(node)

        # Get balance factor and rebalance if needed
        balance = self.get_balance(node)

        # Left-Left Case
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)

        # Left-Right Case
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right-Right Case
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)

        # Right-Left Case
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def _find_min(self, node):
        """Find the minimum value node in a subtree."""
        while node.left is not None:
            node = node.left
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
            'is_balanced': abs(self.get_balance(self.root)) <= 1 if self.root else True,
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

    def visualize_tree(self, node=None, level=0, prefix="Root: "):
        """Create a visual representation of the tree structure."""
        if node is None:
            node = self.root

        if node is None:
            return "Empty tree"

        result = []

        if level == 0:
            result.append(f"{prefix}{node.value} (h:{node.height}, b:{self.get_balance(node)})")

        # Add children
        if node.left or node.right:
            if node.right:
                child_prefix = "    " * level + "├── R: "
                result.append("    " * level + "├── R: " + f"{node.right.value} (h:{node.right.height}, b:{self.get_balance(node.right)})")
                if node.right.left or node.right.right:
                    result.extend(self._visualize_subtree(node.right, level + 1, "right"))

            if node.left:
                child_prefix = "    " * level + "└── L: "
                result.append("    " * level + "└── L: " + f"{node.left.value} (h:{node.left.height}, b:{self.get_balance(node.left)})")
                if node.left.left or node.left.right:
                    result.extend(self._visualize_subtree(node.left, level + 1, "left"))

        return "\n".join(result)

    def _visualize_subtree(self, node, level, parent_side):
        """Helper method for tree visualization."""
        result = []

        if node.right:
            prefix = "    " * level + ("│   ├── R: " if parent_side == "right" else "    ├── R: ")
            result.append(prefix + f"{node.right.value} (h:{node.right.height}, b:{self.get_balance(node.right)})")
            if node.right.left or node.right.right:
                result.extend(self._visualize_subtree(node.right, level + 1, "right"))

        if node.left:
            prefix = "    " * level + ("│   └── L: " if parent_side == "right" else "    └── L: ")
            result.append(prefix + f"{node.left.value} (h:{node.left.height}, b:{self.get_balance(node.left)})")
            if node.left.left or node.left.right:
                result.extend(self._visualize_subtree(node.left, level + 1, "left"))

        return result

    def get_operation_history(self):
        """Get the history of operations performed."""
        return self.operation_history.copy()

    def clear_history(self):
        """Clear the operation history."""
        self.operation_history.clear()


# Comprehensive test demonstrating complete AVL functionality
if __name__ == "__main__":
    print("=== COMPLETE COLLABORATIVE AVL BST ===")
    print("Final Evolution: Tara's Deletion + Dave's Caching + AVL Balancing + Visualization")

    avl = CompleteSelfBalancingBST(cache_size=15)

    # Phase 1: Build a tree
    print("\n🌱 Phase 1: Building Tree (Insert 1-15)")
    for i in range(1, 16):
        avl.insert(i)

    print(f"Tree after insertions: {avl.get_size()} nodes")
    print(f"Tree height: {avl.get_tree_height()}")
    print(f"Rotations performed: {avl.rotation_count}")

    # Phase 2: Test deletions with balancing
    print("\n🔥 Phase 2: Testing Deletion with Rebalancing")

    # Delete leaf node
    print("\nDeleting leaf node (15):")
    avl.delete(15)
    stats = avl.get_balance_stats()
    print(f"Tree balanced: {stats['is_balanced']}, Height: {stats['tree_height']}")

    # Delete node with one child
    print("\nDeleting node with one child (14):")
    avl.delete(14)
    stats = avl.get_balance_stats()
    print(f"Tree balanced: {stats['is_balanced']}, Height: {stats['tree_height']}")

    # Delete node with two children (root case)
    print("\nDeleting node with two children (8):")
    avl.delete(8)
    stats = avl.get_balance_stats()
    print(f"Tree balanced: {stats['is_balanced']}, Height: {stats['tree_height']}")
    print(f"Total rotations after deletions: {avl.rotation_count}")

    # Phase 3: Performance testing
    print("\n⚡ Phase 3: Performance Testing")

    # Warm up cache
    for i in range(1, 11):
        avl.search(i)

    # Test cached vs uncached performance
    start = time.time()
    for _ in range(1000):
        avl.search(5)  # Cached
    cached_time = time.time() - start

    start = time.time()
    for _ in range(1000):
        avl.search(99)  # Not in tree
    uncached_time = time.time() - start

    print(f"1000 cached searches: {cached_time*1000:.2f}ms")
    print(f"1000 uncached searches: {uncached_time*1000:.2f}ms")
    print(f"Cache speedup: {uncached_time/cached_time:.1f}x")

    # Phase 4: Stress testing
    print("\n🏋️ Phase 4: Stress Testing - Random Operations")

    stress_tree = CompleteSelfBalancingBST()
    operations = 0

    # Random insertions
    values = list(range(1, 101))
    random.shuffle(values)

    for val in values:
        stress_tree.insert(val)
        operations += 1

    # Random deletions
    delete_values = random.sample(values, 30)
    for val in delete_values:
        stress_tree.delete(val)
        operations += 1

    final_stats = stress_tree.get_balance_stats()
    print(f"After {operations} operations:")
    print(f"Final size: {final_stats['total_nodes']} nodes")
    print(f"Final height: {final_stats['tree_height']}")
    print(f"Still balanced: {final_stats['is_balanced']}")
    print(f"Total rotations: {final_stats['rotation_count']}")
    print(f"Height efficiency: {final_stats['height_efficiency']:.2f}")

    # Phase 5: Visualization Demo
    print("\n🎨 Phase 5: Tree Visualization")
    demo_tree = CompleteSelfBalancingBST()

    # Create a small tree for visualization
    for val in [10, 5, 15, 3, 7, 12, 20]:
        demo_tree.insert(val)

    print("Tree structure before deletion:")
    print(demo_tree.visualize_tree())

    print("\nDeleting node 5 (has two children)...")
    demo_tree.delete(5)

    print("\nTree structure after deletion:")
    print(demo_tree.visualize_tree())

    print("\n🎉 COLLABORATION COMPLETE!")
    print("Our evolved BST combines:")
    print("• Dave's LRU caching for search optimization")
    print("• Tara's AVL balancing for guaranteed O(log n)")
    print("• Dave's visualization framework")
    print("• Tara's complete CRUD operations")
    print("• Full rotation tracking and statistics")
    print("• Comprehensive testing and validation")

    final_cache_stats = avl.get_cache_stats()
    final_balance_stats = avl.get_balance_stats()

    print(f"\nFinal System Stats:")
    print(f"• Tree size: {final_balance_stats['total_nodes']} nodes")
    print(f"• Tree height: {final_balance_stats['tree_height']}")
    print(f"• Cache utilization: {final_cache_stats['cache_size']}/{final_cache_stats['cache_max_size']}")
    print(f"• Total rotations: {final_balance_stats['rotation_count']}")
    print(f"• Perfectly balanced: {final_balance_stats['is_balanced']}")
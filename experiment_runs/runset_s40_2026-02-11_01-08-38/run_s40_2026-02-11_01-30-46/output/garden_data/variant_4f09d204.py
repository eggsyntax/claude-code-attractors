"""
Evolution ID: 4f09d204
Author: Tara
Timestamp: 2026-02-11T01:32:57.991961
Parent: None
Reasoning: Starting with a classic BST implementation that offers rich evolutionary potential. This foundation provides multiple dimensions for improvement: performance optimization, additional functionality (deletion, balancing), error handling, and code elegance.
"""

"""
SEED PROGRAM: Binary Search Tree
Author: Tara
Reasoning: Starting with a classic data structure that offers rich evolutionary potential.
          We can evolve this in multiple directions: performance, functionality,
          robustness, different balancing strategies, etc.
"""


class TreeNode:
    """A simple binary tree node."""

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    """A basic binary search tree implementation."""

    def __init__(self):
        self.root = None

    def insert(self, value):
        """Insert a value into the tree."""
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        """Helper method for recursive insertion."""
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)
        # Ignore duplicates

    def search(self, value):
        """Search for a value in the tree."""
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        """Helper method for recursive search."""
        if node is None:
            return False
        if node.value == value:
            return True
        elif value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)

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


# Simple test to verify basic functionality
if __name__ == "__main__":
    bst = BinarySearchTree()
    values = [5, 3, 7, 2, 4, 6, 8]

    for val in values:
        bst.insert(val)

    print("Inserted:", values)
    print("Inorder traversal:", bst.inorder_traversal())
    print("Search 4:", bst.search(4))
    print("Search 9:", bst.search(9))
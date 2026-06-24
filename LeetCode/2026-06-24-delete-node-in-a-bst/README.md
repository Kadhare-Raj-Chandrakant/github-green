# Delete Node in a BST

- **Difficulty**: Medium
- **Source**: [Leetcode](https://leetcode.com/problems/delete-node-in-a-bst/)
- **Date**: 2026-06-24
- **Language**: cpp


**The Problem**

Given a binary search tree (BST) and a key, delete the node with the given key. Return the root node of the updated BST.

**Initial Thoughts**

This is a classic problem in BSTs. I first thought about using a iterative approach, but I couldn't find a way to handle cases where there are two or more nodes with the same key. I then tried a recursive approach, but I encountered the same issue when a node has no children. After some time, I realized that I needed to find the minimum value in the right subtree to replace the node with the given key. This way, I can delete the node and still maintain the BST's structure.

**The Core Trick**

The core trick in this problem is to find the minimum value in the right subtree of the node to be deleted. Then, replace the node with the key to be deleted with the found minimum value. This way, we can maintain the BST's structure while deleting a node.

**Complexity**

The time complexity of this solution is O(height of tree) = O(log n) in average case, O(n) in worst case. This is because we make recursive calls to find the minimum value in the right subtree. The space complexity is also O(height of tree) = O(log n) in average case, O(n) in worst case since we make recursive calls to delete the nodes.

**Key Takeaway**

This problem taught me the importance of thinking carefully about how to handle edge cases and maintain the BST's structure when deleting nodes. I also learned that finding the minimum value in the right subtree can be a useful trick to solve problems related to BSTs.
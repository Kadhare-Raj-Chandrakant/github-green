# Diagonal Traverse

- **Difficulty**: Medium
- **Source**: [Leetcode](https://leetcode.com/problems/diagonal-traverse/)
- **Date**: 2026-07-02
- **Language**: cpp


**The Problem**

Given a 2D matrix filled with non-negative integers, write a function to create a new diagonal from left to right and return it.

**Initial Thoughts**

This is a classic problem where I need to traverse the matrix in a specific manner to create the diagonal. At first, I thought of using two nested loops to iterate through the matrix and store the elements in a vector based on their row and column indices. However, I later realized that this approach would have a time complexity of O(m * n), which is not efficient enough for large matrices.

**The Core Trick**

To optimize the time complexity, I decided to use a map to store elements based on their row and column indices. This way, I can keep track of the elements that need to be added to the diagonal and traverse the matrix only once. By using the modulo operator on the sum of row and column indices, I can ensure that the diagonal elements are added in ascending order.

**Complexity**

The time complexity of this solution is O(m * n), which is an improvement from the previous approach. The space complexity remains O(m * n) due to the map used to store the elements.

**Key Takeaway**

This problem serves as a reminder that sometimes the most efficient solution might require a different approach than the first instinct. Always think about the time and space complexity of your algorithms and strive for better solutions whenever possible.
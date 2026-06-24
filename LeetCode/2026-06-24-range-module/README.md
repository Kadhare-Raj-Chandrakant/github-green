# Range Module

- **Difficulty**: Hard
- **Source**: [Leetcode](https://leetcode.com/problems/range-module/)
- **Date**: 2026-06-24
- **Language**: cpp


Problem: Range Module

Difficulty: Hard
Source: https://leetcode.com/problems/range-module/

Initial Thoughts: This problem asks for a data structure to maintain a set of overlapping intervals, with efficient operations to add, query, and remove ranges. My initial thought was to use a binary search tree or a balanced search tree, but I wanted to avoid the overhead of tree rotations and balancing. I also wanted to ensure the time complexity for queryRange and removeRange is O(log n) in the worst case.

The Core Trick: The key to solving this problem is to use a set data structure with a custom comparator function that considers the end of the interval when comparing pairs. This allows us to merge overlapping intervals efficiently. To add a new interval, we first search for the smallest interval that overlaps with the new interval. If there's an overlapping interval, we merge it with the new interval. Otherwise, we add the new interval to the set. To query a range, we find the smallest interval that starts before the left bound and ends after the right bound. If no such interval exists, we return false. To remove a range, we find the smallest interval that overlaps with the removed range and update it accordingly. By maintaining the set in order, we can perform these operations efficiently in O(log n) time.

Complexity: The time complexity of addRange is O(log n) due to the use of the set's lower_bound function. The time complexity of queryRange and removeRange is also O(log n) due to binary search in the set. The space complexity is O(n) to store all the intervals, but it can be optimized to O(m), where m is the number of unique intervals, by maintaining a map instead of a set.

Key Takeaway: When designing a data structure, consider the operations in terms of their time and space complexity. In this case, using a set with a custom comparator allows for efficient merging and querying of overlapping intervals, while maintaining the set in order ensures O(log n) operations.
# Design Auction System

- **Difficulty**: Medium
- **Source**: [Leetcode](https://leetcode.com/problems/design-auction-system/)
- **Date**: 2026-06-30
- **Language**: cpp


The problem I solved today was designing an auction system that allows for adding, updating, and removing bids, while also returning the highest bidder. The key to this problem was being able to efficiently store and access bids for each unique item.

Initially, I thought of using a simple binary search tree to store the bids. However, this approach would have a time complexity of O(log n) for each operation, which would be too slow for large numbers of items or users. After some thought, I realized that a map (dictionary in Python) would be a more efficient choice. Each item would be a key in the map, and its value would be a map containing the bids for that item. This approach allows for constant-time lookups based on the item ID.

Space-wise, the map approach has a time complexity of O(n) because we need to store all bids for each unique item. However, this is acceptable given the linear time complexity for each operation.

Overall, this problem was a fun one to solve, and I learned a new data structure in the process. I'll remember that when dealing with large datasets, using built-in data structures and efficient algorithms is key.
# Path with Maximum Probability

- **Difficulty**: Medium
- **Source**: [Leetcode](https://leetcode.com/problems/path-with-maximum-probability/)
- **Date**: 2026-06-26
- **Language**: cpp


Problem: Given a graph with nodes and edges, return the node with the maximum probability.

Initial Thoughts: A brute-force solution would be to try all possible paths and calculate the probability for each one. However, this would be extremely slow for large graphs. A more efficient approach might be to use dynamic programming or Dijkstra's algorithm.

The Core Trick: I decided to use Dijkstra's algorithm, which is a shortest path algorithm that can also find the maximum probability path. I used a priority queue to store the nodes with the highest probability, and updated the probability for each node as I explored the graph.

Complexity: The time complexity of this solution is O(E + V log V), where E is the number of edges and V is the number of nodes. This is because we need to explore all the edges in the graph and update the priority queue for each edge. The space complexity is also O(V + E), which is due to the use of adjacency lists and priority queue.

Key Takeaway: Dijkstra's algorithm can be a powerful tool for finding the maximum probability path in a graph. It's important to consider the time and space complexity of our solutions, especially when dealing with large graphs. Always think about how your code will scale and whether there are more efficient algorithms that can be used instead.
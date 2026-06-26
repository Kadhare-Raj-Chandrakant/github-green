class Solution {
public:
    // Time complexity: O(E + V log V)
    // Space complexity: O(V + E)
    double maxProbability(int n, vector<vector<int>>& edges, vector<double>& succProb, int start_node, int end_node) {
        vector<vector<pair<int, double>>> graph(n);
        for (int i = 0; i < edges.size(); i++) {
            int u = edges[i][0], v = edges[i][1];
            graph[u].emplace_back(v, succProb[i]);
            graph[v].emplace_back(u, succProb[i]);
        }
        
        vector<double> logProb(n, -1e9);
        logProb[start_node] = 0;
        priority_queue<pair<double, int>> pq;
        pq.emplace(0, start_node);
        
        while (!pq.empty()) {
            double logP = pq.top().first;
            int u = pq.top().second;
            pq.pop();
            
            if (u == end_node) return exp(logP);
            
            for (auto& [v, p] : graph[u]) {
                double newLogP = logP + log(p);
                if (newLogP > logProb[v]) {
                    logProb[v] = newLogP;
                    pq.emplace(logProb[v], v);
                }
            }
        }
        
        return 0;
    }
};
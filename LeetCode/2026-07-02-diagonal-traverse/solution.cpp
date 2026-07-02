class Solution {
public:
    // Time complexity: O(m * n)
    // Space complexity: O(m * n)
    vector<int> findDiagonalOrder(vector<vector<int>>& mat) {
        int m = mat.size();
        int n = mat[0].size();
        vector<int> res;
        map<int, vector<int>> diagonal;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                diagonal[i + j].push_back(mat[i][j]);
            }
        }
        
        for (auto& pair : diagonal) {
            if (pair.first % 2 == 0) {
                reverse(pair.second.begin(), pair.second.end());
            }
            for (int num : pair.second) {
                res.push_back(num);
            }
        }
        
        return res;
    }
};
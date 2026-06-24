class Solution {
public:
    // Time complexity: O(height of tree) = O(log n) in average case, O(n) in worst case
    // Space complexity: O(height of tree) = O(log n) in average case, O(n) in worst case
    TreeNode* deleteNode(TreeNode* root, int key) {
        if (!root) return nullptr;
        
        if (key < root->val) {
            root->left = deleteNode(root->left, key);
        } else if (key > root->val) {
            root->right = deleteNode(root->right, key);
        } else {
            if (!root->left) return root->right;
            if (!root->right) return root->left;
            
            TreeNode* minNode = root->right;
            while (minNode->left) {
                minNode = minNode->left;
            }
            root->val = minNode->val;
            root->right = deleteNode(root->right, minNode->val);
        }
        
        return root;
    }
};
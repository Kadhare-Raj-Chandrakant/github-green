class AuctionSystem {
public:
    // Time complexity: O(1) for addBid, updateBid, removeBid; O(log n) for getHighestBidder
    // Space complexity: O(n)
    AuctionSystem() {
        // Initialize the Auction system
    }

    void addBid(int userId, int itemId, int bidAmount) {
        // Add a new bid for itemId by userId with bidAmount
        if (bids.find(itemId) == bids.end()) {
            bids[itemId] = {};
        }
        if (bids[itemId].find(userId) != bids[itemId].end()) {
            bids[itemId].erase(userId);
        }
        bids[itemId].insert({userId, bidAmount});
    }

    void updateBid(int userId, int itemId, int newAmount) {
        // Update the existing bid of userId for itemId to newAmount
        if (bids.find(itemId) != bids.end() && bids[itemId].find(userId) != bids[itemId].end()) {
            bids[itemId].erase(userId);
            bids[itemId].insert({userId, newAmount});
        }
    }

    void removeBid(int userId, int itemId) {
        // Remove the bid of userId for itemId
        if (bids.find(itemId) != bids.end() && bids[itemId].find(userId) != bids[itemId].end()) {
            bids[itemId].erase(userId);
        }
    }

    int getHighestBidder(int itemId) {
        // Return the userId of the highest bidder for itemId
        if (bids.find(itemId) == bids.end() || bids[itemId].empty()) {
            return -1;
        }
        auto it = --bids[itemId].end();
        return it->first;
    }

private:
    // Map from itemId to its active bids
    map<int, map<int, int>> bids;
};
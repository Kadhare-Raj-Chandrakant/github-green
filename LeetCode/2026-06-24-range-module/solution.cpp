// Time complexity: O(n log n) for addRange and removeRange, O(log n) for queryRange
// Space complexity: O(n)
class RangeModule {
public:
    set<pair<int, int>> ranges;

    RangeModule() {}

    void addRange(int left, int right) {
        auto it = ranges.lower_bound({left, 0});
        if (it != ranges.begin()) {
            --it;
            if (it->second >= left) {
                left = it->first;
                right = max(right, it->second);
                ranges.erase(it);
            }
        }
        while (it != ranges.end() && it->first <= right) {
            right = max(right, it->second);
            ranges.erase(it++);
        }
        ranges.insert({left, right});
    }

    bool queryRange(int left, int right) {
        auto it = ranges.lower_bound({left, 0});
        if (it == ranges.begin()) return false;
        --it;
        return it->first <= left && it->second >= right;
    }

    void removeRange(int left, int right) {
        auto it = ranges.lower_bound({left, 0});
        if (it != ranges.begin()) {
            --it;
            if (it->second > right) {
                ranges.insert({right, it->second});
                it->second = left;
            }
        }
        while (it != ranges.end() && it->first < right) {
            if (it->second > right) {
                ranges.insert({right, it->second});
                it->second = left;
                break;
            }
            ranges.erase(it++);
        }
    }
};
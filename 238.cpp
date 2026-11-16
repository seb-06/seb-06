class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        vector<int> answer;
        int rightProduct = 1;
        int numsSize = nums.size();

        answer.resize(numsSize);
        answer[0] = 1;

// first pass: left product
        for (int i = 1; i < numsSize; i++) {
            answer[i] = answer[i-1] * nums[i-1];
        }

// second pass: right product
        for (int i = numsSize - 1; i >= 0; i--) {
            answer[i] *= rightProduct;

            rightProduct *=nums[i];
        }

        return answer;
    }
};

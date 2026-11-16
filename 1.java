class Solution {
    public int[] twoSum(int[] nums, int target) {
        int[] sol = new int[2];

        int curr = 0;
        int len = nums.length;
        for (int i=0;i < len;i++) {
            curr = target - nums[i];
            for (int j=0;j < len;j++) {
                if (j == i) {continue;}

                if (nums[j] == curr) {
                    sol[0] = i;
                    sol[1] = j;
                }
            }
        }
        return sol;
    }
}

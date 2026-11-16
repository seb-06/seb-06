class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        Arrays.sort(intervals, (a,b) -> Integer.compare(a[1],b[1]));

        int sol = 0;

        int end = Integer.MIN_VALUE;

        for (int[] w : intervals) {
            if (w[0] < end) {
                sol++;
            }
            else {
                end = w[1];
            }
        }
        return sol;
    }
}

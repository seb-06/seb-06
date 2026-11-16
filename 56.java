class Solution {
    public int[][] merge(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        
        ArrayList<int[]> sol = new ArrayList<>();
        
        int start = intervals[0][0];
        int end = intervals[0][1];
        for (int[] w : intervals) {
            if (w[0] <= end) {
                if (end < w[1]) {
                    end = w[1];
                }
            }
            else {
                sol.add(new int[]{start,end});
                start = w[0];
                end = w[1];
            }
        }
        sol.add(new int[]{start,end});

        return sol.toArray(new int[sol.size()][]);
    }
}

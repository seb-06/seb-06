class Solution {
    public int minMeetingRooms(int[][] intervals) {
        Arrays.sort(intervals, 
            (a, b) -> Integer.compare(a[0], b[0])
        );

        PriorityQueue<Integer> ends = new PriorityQueue<>();
        for (int[] w : intervals) {
            if ((!ends.isEmpty()) && (ends.peek() <= w[0])) {
                ends.poll();
            }
            ends.offer(w[1]);
        }
        return ends.size();
    }
}

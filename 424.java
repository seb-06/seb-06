class Solution {
    public int characterReplacement(String s, int k) {
        int maxFreq = 0;
        int left = 0;
        int len = s.length();
        int[] freq = new int[26];
        int result = 0;
        char[] arr = s.toCharArray();
        int right = 0;

        for (right=0;right<len;right++) {
            int charIndex = arr[right] - 'A';
            freq[charIndex]++;

            maxFreq = Math.max(maxFreq, freq[charIndex]);

            if ((right - left + 1) - maxFreq > k) {
                freq[arr[left] - 'A']--;
                left++;
            }
        }
        return (right - left);
    }
}

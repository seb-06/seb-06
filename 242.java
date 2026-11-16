class Solution {
    public boolean isAnagram(String s, String t) {
        int len = s.length();
        if (len != t.length()) {
            return false;
        }

        int[] counter = new int[26];
        for (int i = 0; i<len; i++) {
            counter[s.charAt(i) - 'a']++;
        }

        for (int i = 0; i<len; i++) {
            counter[t.charAt(i) - 'a']--;
            if (counter[t.charAt(i) - 'a'] < 0) {
                return false;
            }
        }
        return true;
    }
}

class Solution {
public:
    string mergeAlternately(string word1, string word2) {
        string letters;
        int i = 0; 
        int j = 0;
        int len = word1.length() + word2.length();

        while (letters.length() < len) {
            if (i < word1.length()) {
                letters.push_back(word1[i]);
                i++;
            }
            if (j < word2.length()) {
                letters.push_back(word2[j]);
                j++;
            }
        }


        return letters;
    }
};

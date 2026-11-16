#include <iostream>
#include <vector>
#include <sstream>
class Solution {
public:
    string reverseWords(string s) {
        stringstream ss(s);

        string word;
        vector<string> words;
        
        while (ss >> word) {
            words.push_back(word);
        }

        int len = words.size();

        s.clear();

        for (int i=len-1;i>=0;i--) {
            if (!s.empty()) {s.append(" ");}
            s.append(words[i]);
        }

        return s;
    }
};

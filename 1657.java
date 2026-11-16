class Solution {
    public boolean closeStrings(String word1, String word2) {
        int len1 = word1.length();
        if (len1 != word2.length()) {
            return false;
        }

        Map<Character, Integer> characterMapWord1 = createMap(word1);
        Map<Character, Integer> characterMapWord2 = createMap(word2);


        if (!characterMapWord1.keySet().equals(characterMapWord2.keySet())) {
            return false;
        }

        List<Integer> frequencyList1 = new ArrayList<>(characterMapWord1.values());
        List<Integer> frequencyList2 = new ArrayList<>(characterMapWord2.values());
        Collections.sort(frequencyList1);
        Collections.sort(frequencyList2);

        if (!frequencyList1.equals(frequencyList2)) {
            return false;
        }
        return true;
    }

    public Map<Character, Integer> createMap(String word) {
        Map<Character, Integer> characterMap = new HashMap<Character, Integer>();
        for (int i=0; i<word.length();i++) {
            char ch = word.charAt(i);
            if (!characterMap.containsKey(ch)) {
                characterMap.put(ch, 1);
            }
            else {
                characterMap.put(ch, characterMap.get(ch) + 1);
            }
        }
        return characterMap;
    }
}

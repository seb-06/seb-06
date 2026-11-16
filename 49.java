class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        HashMap<String, List<String>> map = new HashMap<>();

        for (String str : strs) {
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            String sorted = new String(chars);

            if (!map.containsKey(sorted)) {
                map.put(sorted, new ArrayList<String>());
            }

            map.get(sorted).add(str);
        }
        int size = map.size();
        List<List<String>> result = new ArrayList<>();
        for (String i : map.keySet()) {
            result.add(map.get(i));
        }
        return result;
    }
}

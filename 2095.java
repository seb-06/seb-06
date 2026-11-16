/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode deleteMiddle(ListNode head) {
        if (head.next == null) {
            return null;
        }
        ListNode curr = head;
        int count = 0;
        while (curr.next != null) {
            count++;
            curr = curr.next;
        }

        count++;
        int center = count/2;

        count = 1;
        curr = head;

        while (count < center) {
            count++;
            curr = curr.next;

        }
        if (curr.next != null) {
            curr.next = curr.next.next;
        }
        else {
            curr.next = null;
        }
        return head;
    }
}

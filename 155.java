record Node(int value, int min) {}
class MinStack {
    private ArrayList<Node> stack;
    public MinStack() {

        this.stack = new ArrayList<Node>();
    }
    
    public void push(int value) {
        if (stack.size() < 1 || this.getTopNode().min() > value) {
            stack.add(new Node(value, value));
        }
        else {
            stack.add(new Node(value, this.getTopNode().min()));
        }
    }
    private Node getTopNode() {
        return stack.get(stack.size() - 1);
    }
    
    public void pop() {
        stack.remove(stack.size() - 1);
    }
    
    public int top() {
        return this.getTopNode().value();       
    }
    
    public int getMin() {
        return this.getTopNode().min();
    }
}

/**
 * Your MinStack object will be instantiated and called as such:
 * MinStack obj = new MinStack();
 * obj.push(value);
 * obj.pop();
 * int param_3 = obj.top();
 * int param_4 = obj.getMin();
 */

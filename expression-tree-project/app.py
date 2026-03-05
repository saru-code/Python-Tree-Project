"""
===============================================================================
  Expression Tree Evaluation — Flask Backend
  ───────────────────────────────────────────
  Data Structures Mini Project

  This file implements a Flask web server that:
    1. Serves the frontend (index.html)
    2. Exposes a POST /evaluate API endpoint that:
       - Accepts an infix arithmetic expression
       - Tokenizes it
       - Converts it to postfix (Shunting-Yard algorithm)
       - Builds an expression tree
       - Performs recursive traversals (inorder, preorder, postorder)
       - Evaluates the tree recursively
       - Returns all results as JSON
===============================================================================
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ─────────────────────────────────────────────
# Node class — building block of the tree
# ─────────────────────────────────────────────
class Node:
    """
    Represents a single node in the expression tree.

    Attributes
    ----------
    value : str
        The operator (+, -, *, /) or numeric operand stored in this node.
    left  : Node or None
        Reference to the left child subtree.
    right : Node or None
        Reference to the right child subtree.
    """

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def to_dict(self):
        """Convert the tree to a JSON-serializable dictionary for the frontend."""
        result = {"value": self.value}
        if self.left or self.right:
            result["left"] = self.left.to_dict() if self.left else None
            result["right"] = self.right.to_dict() if self.right else None
        return result


# ─────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────
OPERATORS = {'+', '-', '*', '/'}


def precedence(op):
    """Return the precedence level of an operator (higher = binds tighter)."""
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0


def is_number(token):
    """Check whether a token represents a valid number (int or float)."""
    try:
        float(token)
        return True
    except ValueError:
        return False


# ─────────────────────────────────────────────
# Step 1 — Tokenizer
# ─────────────────────────────────────────────
def tokenize(expression):
    """
    Convert a raw infix expression string into a list of tokens.
    Handles multi-digit numbers, decimals, negative numbers, operators, parentheses.
    """
    tokens = []
    i = 0
    expr = expression.replace(' ', '')

    while i < len(expr):
        ch = expr[i]

        # Number (possibly multi-digit / decimal)
        if ch.isdigit() or ch == '.':
            num_str = ''
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num_str += expr[i]
                i += 1
            tokens.append(num_str)
            continue

        # Unary minus (negative number at start or after '(')
        if ch == '-' and (len(tokens) == 0 or tokens[-1] == '('):
            num_str = '-'
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num_str += expr[i]
                i += 1
            tokens.append(num_str)
            continue

        # Operator or parenthesis
        if ch in OPERATORS or ch in ('(', ')'):
            tokens.append(ch)
            i += 1
            continue

        raise ValueError(f"Invalid character '{ch}' at position {i}")

    return tokens


# ─────────────────────────────────────────────
# Step 2 — Infix to Postfix (Shunting-Yard)
# ─────────────────────────────────────────────
def infix_to_postfix(tokens):
    """
    Convert infix tokens to postfix using Dijkstra's Shunting-Yard algorithm.
    """
    output = []
    stack = []

    for token in tokens:
        if is_number(token):
            output.append(token)
        elif token in OPERATORS:
            while (stack and stack[-1] != '('
                   and precedence(stack[-1]) >= precedence(token)):
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses — extra ')'")
            stack.pop()

    while stack:
        top = stack.pop()
        if top == '(':
            raise ValueError("Mismatched parentheses — extra '('")
        output.append(top)

    return output


# ─────────────────────────────────────────────
# Step 3 — Build Expression Tree from Postfix
# ─────────────────────────────────────────────
def build_expression_tree(postfix_tokens):
    """
    Construct an expression tree from postfix tokens using a stack.
    """
    stack = []

    for token in postfix_tokens:
        if is_number(token):
            stack.append(Node(token))
        elif token in OPERATORS:
            if len(stack) < 2:
                raise ValueError(f"Not enough operands for '{token}'")
            right = stack.pop()
            left = stack.pop()
            node = Node(token)
            node.left = left
            node.right = right
            stack.append(node)

    if len(stack) != 1:
        raise ValueError("Malformed expression")

    return stack[0]


# ─────────────────────────────────────────────
# Step 4 — Recursive Traversals
# ─────────────────────────────────────────────
def inorder(node, result=None):
    """Inorder traversal: Left → Root → Right (produces infix notation)."""
    if result is None:
        result = []
    if node:
        inorder(node.left, result)
        result.append(node.value)
        inorder(node.right, result)
    return result


def preorder(node, result=None):
    """Preorder traversal: Root → Left → Right (produces prefix notation)."""
    if result is None:
        result = []
    if node:
        result.append(node.value)
        preorder(node.left, result)
        preorder(node.right, result)
    return result


def postorder(node, result=None):
    """Postorder traversal: Left → Right → Root (produces postfix notation)."""
    if result is None:
        result = []
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.value)
    return result


# ─────────────────────────────────────────────
# Step 5 — Recursive Evaluation
# ─────────────────────────────────────────────
def evaluate(node):
    """
    Recursively evaluate the expression tree.
    Base case:  leaf node → return its numeric value.
    Recursive:  operator node → evaluate children, apply operator.
    """
    if node is None:
        raise ValueError("Cannot evaluate an empty tree")

    # Base case — leaf node (operand)
    if node.left is None and node.right is None:
        return float(node.value)

    # Recursive case — evaluate subtrees and combine
    left_val = evaluate(node.left)
    right_val = evaluate(node.right)

    if node.value == '+':
        return left_val + right_val
    elif node.value == '-':
        return left_val - right_val
    elif node.value == '*':
        return left_val * right_val
    elif node.value == '/':
        if right_val == 0:
            raise ZeroDivisionError("Division by zero")
        return left_val / right_val
    else:
        raise ValueError(f"Unknown operator: '{node.value}'")


# ─────────────────────────────────────────────
# Flask Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/evaluate', methods=['POST'])
def evaluate_expression():
    """
    API endpoint: POST /evaluate

    Input  (JSON):  { "expression": "(3+5)*(2-1)" }
    Output (JSON):  {
        "expression": "(3+5)*(2-1)",
        "postfix": "3 5 + 2 1 - *",
        "inorder": "3 + 5 * 2 - 1",
        "preorder": "* + 3 5 - 2 1",
        "postorder": "3 5 + 2 1 - *",
        "result": 8,
        "tree": { ... }
    }
    """
    data = request.get_json()

    # Validate input
    if not data or 'expression' not in data:
        return jsonify({"error": "Missing 'expression' field"}), 400

    expression = data['expression'].strip()
    if not expression:
        return jsonify({"error": "Expression cannot be empty"}), 400

    try:
        # Step 1 — Tokenize
        tokens = tokenize(expression)

        # Step 2 — Convert to postfix
        postfix_tokens = infix_to_postfix(tokens)

        # Step 3 — Build expression tree
        root = build_expression_tree(postfix_tokens)

        # Step 4 — Perform traversals
        in_result = inorder(root)
        pre_result = preorder(root)
        post_result = postorder(root)

        # Step 5 — Evaluate
        result = evaluate(root)

        # Format result as integer if it is a whole number
        if result == int(result):
            result = int(result)

        return jsonify({
            "expression": expression,
            "postfix": " ".join(postfix_tokens),
            "inorder": " ".join(in_result),
            "preorder": " ".join(pre_result),
            "postorder": " ".join(post_result),
            "result": result,
            "tree": root.to_dict()
        })

    except (ValueError, ZeroDivisionError) as e:
        return jsonify({"error": str(e)}), 400


# ─────────────────────────────────────────────
# Run the server
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("\n  🌳 Expression Tree Server running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)

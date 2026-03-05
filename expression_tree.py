"""
===============================================================================
  Expression Tree Evaluation using Recursive Traversal
  ─────────────────────────────────────────────────────
  Data Structures Mini Project

  ALGORITHM OVERVIEW
  ──────────────────
  1. TOKENIZE   – Break the infix expression string into a list of tokens
                  (numbers, operators, parentheses).
  2. INFIX → POSTFIX (Shunting-Yard Algorithm)
        • Scan tokens left to right.
        • Numbers go straight to the output list.
        • Operators are pushed/popped from a stack based on precedence.
        • Left parenthesis is pushed; right parenthesis pops until '('.
  3. BUILD EXPRESSION TREE from postfix tokens
        • Scan postfix tokens left to right.
        • If a token is a number  → create a leaf node, push onto stack.
        • If a token is an operator → pop two nodes, make them children
          of a new operator node, push the new node.
        • The last node remaining on the stack is the root.
  4. TRAVERSE the tree recursively (Inorder, Preorder, Postorder).
  5. EVALUATE the tree recursively:
        • Leaf node → return its numeric value.
        • Operator node → recursively evaluate left and right subtrees,
          then apply the operator.
===============================================================================
"""


# ─────────────────────────────────────────────
# Node class – building block of the tree
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

    def __repr__(self):
        return f"Node({self.value})"


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
# Step 1 – Tokenizer
# ─────────────────────────────────────────────
def tokenize(expression):
    """
    Convert a raw infix expression string into a list of tokens.

    Handles:
      • Multi-digit integers and decimals  (e.g. 42, 3.14)
      • Negative numbers at the start or after '(' (e.g. -5, (-3+2))
      • Operators: + - * /
      • Parentheses: ( )

    Parameters
    ----------
    expression : str
        The infix arithmetic expression entered by the user.

    Returns
    -------
    list[str]
        A list of string tokens.

    Raises
    ------
    ValueError
        If the expression contains an invalid character.
    """
    tokens = []
    i = 0
    expr = expression.replace(' ', '')  # strip all whitespace

    while i < len(expr):
        ch = expr[i]

        # ── Number (possibly multi-digit / decimal) ──
        if ch.isdigit() or ch == '.':
            num_str = ''
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num_str += expr[i]
                i += 1
            tokens.append(num_str)
            continue

        # ── Unary minus (negative number) ──
        # A '-' is unary if it appears at the very start or right after '('
        if ch == '-' and (len(tokens) == 0 or tokens[-1] == '('):
            num_str = '-'
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num_str += expr[i]
                i += 1
            tokens.append(num_str)
            continue

        # ── Operator or parenthesis ──
        if ch in OPERATORS or ch in ('(', ')'):
            tokens.append(ch)
            i += 1
            continue

        raise ValueError(f"Invalid character '{ch}' at position {i}")

    return tokens


# ─────────────────────────────────────────────
# Step 2 – Infix to Postfix (Shunting-Yard)
# ─────────────────────────────────────────────
def infix_to_postfix(tokens):
    """
    Convert a list of infix tokens to postfix (Reverse Polish Notation)
    using Dijkstra's Shunting-Yard algorithm.

    Rules
    -----
    • Operands go directly to the output.
    • An operator pops operators of >= precedence from the stack to the
      output, then is pushed onto the stack.
    • '(' is pushed onto the stack.
    • ')' pops from the stack to the output until '(' is found.

    Parameters
    ----------
    tokens : list[str]
        Infix token list produced by `tokenize()`.

    Returns
    -------
    list[str]
        Postfix token list.

    Raises
    ------
    ValueError
        If parentheses are mismatched.
    """
    output = []     # postfix result
    stack = []      # operator stack

    for token in tokens:
        if is_number(token):
            # ── Operand → straight to output ──
            output.append(token)

        elif token in OPERATORS:
            # ── Operator → pop higher/equal precedence operators first ──
            while (stack
                   and stack[-1] != '('
                   and precedence(stack[-1]) >= precedence(token)):
                output.append(stack.pop())
            stack.append(token)

        elif token == '(':
            stack.append(token)

        elif token == ')':
            # ── Pop until matching '(' ──
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses – extra ')'")
            stack.pop()  # discard the '('

    # ── Pop any remaining operators ──
    while stack:
        top = stack.pop()
        if top == '(':
            raise ValueError("Mismatched parentheses – extra '('")
        output.append(top)

    return output


# ─────────────────────────────────────────────
# Step 3 – Build Expression Tree from Postfix
# ─────────────────────────────────────────────
def build_expression_tree(postfix_tokens):
    """
    Construct an expression tree from a postfix token list.

    Algorithm
    ---------
    For each token (left to right):
      • If it is a NUMBER  → create a leaf Node and push it on the stack.
      • If it is an OPERATOR →
            1. Pop the top two nodes (right child first, then left child).
            2. Create a new Node with the operator as value.
            3. Attach the two popped nodes as children.
            4. Push the new subtree root onto the stack.
    The single node remaining on the stack is the root of the full tree.

    Parameters
    ----------
    postfix_tokens : list[str]
        Postfix token list produced by `infix_to_postfix()`.

    Returns
    -------
    Node
        Root node of the constructed expression tree.

    Raises
    ------
    ValueError
        If the postfix expression is malformed.
    """
    stack = []

    for token in postfix_tokens:
        if is_number(token):
            # Leaf node (operand)
            stack.append(Node(token))
        elif token in OPERATORS:
            # Internal node (operator) – needs two children
            if len(stack) < 2:
                raise ValueError(
                    f"Malformed expression: not enough operands for '{token}'"
                )
            right_child = stack.pop()   # first pop  → right child
            left_child = stack.pop()    # second pop → left child

            operator_node = Node(token)
            operator_node.left = left_child
            operator_node.right = right_child
            stack.append(operator_node)

    if len(stack) != 1:
        raise ValueError("Malformed expression: leftover nodes on stack")

    return stack[0]


# ─────────────────────────────────────────────
# Step 4 – Recursive Traversals
# ─────────────────────────────────────────────
def inorder_traversal(node, result=None):
    """
    Inorder traversal (Left → Root → Right).

    For an expression tree this reproduces a *fully parenthesised*
    version of the original infix expression.
    """
    if result is None:
        result = []
    if node is not None:
        # Add opening parenthesis before a subtree that has children
        if node.left or node.right:
            result.append('(')
        inorder_traversal(node.left, result)
        result.append(node.value)
        inorder_traversal(node.right, result)
        if node.left or node.right:
            result.append(')')
    return result


def preorder_traversal(node, result=None):
    """
    Preorder traversal (Root → Left → Right).

    Produces the *prefix* (Polish Notation) of the expression.
    """
    if result is None:
        result = []
    if node is not None:
        result.append(node.value)
        preorder_traversal(node.left, result)
        preorder_traversal(node.right, result)
    return result


def postorder_traversal(node, result=None):
    """
    Postorder traversal (Left → Right → Root).

    Produces the *postfix* (Reverse Polish Notation) of the expression.
    """
    if result is None:
        result = []
    if node is not None:
        postorder_traversal(node.left, result)
        postorder_traversal(node.right, result)
        result.append(node.value)
    return result


# ─────────────────────────────────────────────
# Step 5 – Recursive Evaluation
# ─────────────────────────────────────────────
def evaluate(node):
    """
    Recursively evaluate the expression tree and return a numeric result.

    Base case : leaf node (operand) → return its float value.
    Recursive : operator node →
                  1. Evaluate left subtree  → left_val
                  2. Evaluate right subtree → right_val
                  3. Apply operator to (left_val, right_val)

    Parameters
    ----------
    node : Node
        The current node being evaluated.

    Returns
    -------
    float
        The result of evaluating the subtree rooted at `node`.

    Raises
    ------
    ZeroDivisionError
        If division by zero is encountered.
    ValueError
        If an unknown operator is found.
    """
    if node is None:
        raise ValueError("Cannot evaluate an empty tree")

    # ── Base case: leaf node holds a number ──
    if node.left is None and node.right is None:
        return float(node.value)

    # ── Recursive case: evaluate children, then combine ──
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
            raise ZeroDivisionError("Division by zero in expression")
        return left_val / right_val
    else:
        raise ValueError(f"Unknown operator: '{node.value}'")


# ─────────────────────────────────────────────
# Pretty-print the tree (bonus visual aid)
# ─────────────────────────────────────────────
def print_tree(node, level=0, prefix="Root: "):
    """
    Print a visual representation of the expression tree.

    Example output for (3+5)*(2-1):

        Root: *
            L── +
                L── 3
                R── 5
            R── -
                R── 2
                R── 1
    """
    if node is not None:
        print(" " * (level * 4) + prefix + str(node.value))
        if node.left is not None or node.right is not None:
            print_tree(node.left,  level + 1, "L── ")
            print_tree(node.right, level + 1, "R── ")


# ─────────────────────────────────────────────
# Main function – demonstration
# ─────────────────────────────────────────────
def process_expression(expression):
    """Run the full pipeline on a single expression string and display results."""
    print(f"\n{'═' * 60}")
    print(f"  Expression: {expression}")
    print(f"{'═' * 60}")

    # Step 1 – Tokenize
    tokens = tokenize(expression)
    print(f"\n  Tokens      : {tokens}")

    # Step 2 – Convert to postfix
    postfix = infix_to_postfix(tokens)
    print(f"  Postfix     : {' '.join(postfix)}")

    # Step 3 – Build expression tree
    root = build_expression_tree(postfix)

    # Display tree structure
    print(f"\n  Expression Tree:")
    print(f"  {'─' * 40}")
    print_tree(root, level=1)

    # Step 4 – Traversals
    inorder   = inorder_traversal(root)
    preorder  = preorder_traversal(root)
    postorder = postorder_traversal(root)

    print(f"\n  Inorder     : {' '.join(inorder)}")
    print(f"  Preorder    : {' '.join(preorder)}")
    print(f"  Postorder   : {' '.join(postorder)}")

    # Step 5 – Evaluate
    result = evaluate(root)
    # Display as integer if the result is a whole number
    if result == int(result):
        result = int(result)
    print(f"\n  ✅ Result    : {result}")
    print(f"{'═' * 60}\n")


def main():
    """
    Main entry point.

    Demonstrates the program with several sample expressions,
    then enters an interactive loop so the user can try their own.
    """
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Expression Tree Evaluation using Recursive Traversal  ║")
    print("║              — Data Structures Mini Project —           ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ── Sample expressions ──
    samples = [
        "(3+5)*(2-1)",
        "10+2*6",
        "(8-3)*(4+2)/5",
        "7+3*2-4/2",
    ]

    print("\n── Running sample expressions ──")
    for expr in samples:
        try:
            process_expression(expr)
        except (ValueError, ZeroDivisionError) as e:
            print(f"  ❌ Error: {e}\n")

    # ── Interactive mode ──
    print("── Interactive mode (type 'quit' to exit) ──\n")
    while True:
        try:
            user_input = input("  Enter an expression: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if user_input.lower() in ('quit', 'exit', 'q'):
            print("  Goodbye!")
            break

        if not user_input:
            continue

        try:
            process_expression(user_input)
        except (ValueError, ZeroDivisionError) as e:
            print(f"  ❌ Error: {e}\n")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()


"""
===============================================================================
  SAMPLE INPUT / OUTPUT
  ─────────────────────
  Expression: (3+5)*(2-1)

  Tokens      : ['(', '3', '+', '5', ')', '*', '(', '2', '-', '1', ')']
  Postfix     : 3 5 + 2 1 - *

  Expression Tree:
  ────────────────────────────────────────
      Root: *
          L── +
              L── 3
              R── 5
          R── -
              L── 2
              R── 1

  Inorder     : ( ( 3 + 5 ) * ( 2 - 1 ) )
  Preorder    : * + 3 5 - 2 1
  Postorder   : 3 5 + 2 1 - *

  ✅ Result    : 8
===============================================================================
"""

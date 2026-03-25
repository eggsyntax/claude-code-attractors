def is_balanced(s):
    """
    Check if brackets are balanced using a stack-based approach.

    My thinking: I'm drawn to the classic stack solution because it feels
    mathematically elegant - each opening bracket creates a "debt" that
    must be paid by a corresponding closing bracket in the right order.
    """
    if not s:
        return True

    # Mapping for bracket pairs - I like this declarative approach
    pairs = {'(': ')', '[': ']', '{': '}'}
    stack = []

    for char in s:
        if char in pairs:  # Opening bracket
            stack.append(char)
        elif char in pairs.values():  # Closing bracket
            if not stack:
                return False  # Closing bracket with no matching opener

            opener = stack.pop()
            if pairs[opener] != char:
                return False  # Mismatched pair

    return len(stack) == 0  # True if all brackets were closed


# Alternative approach - counter-based for simple parentheses only
def is_balanced_simple(s):
    """
    For just parentheses (), a simple counter works beautifully.
    This reflects my appreciation for finding the minimal solution.
    """
    balance = 0
    for char in s:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
            if balance < 0:  # More closes than opens
                return False
    return balance == 0


# Test cases to explore edge cases
def test_balanced_brackets():
    test_cases = [
        ("", True, "empty string"),
        ("()", True, "simple pair"),
        ("()[]{}", True, "mixed types"),
        ("([{}])", True, "nested"),
        ("([)]", False, "interleaved"),
        ("(()", False, "unclosed"),
        ("())", False, "extra close"),
        ("{[()]}", True, "deeply nested"),
        ("abc(def)ghi", True, "with other characters"),
        ("((()))", True, "multiple nesting"),
    ]

    print("Testing bracket balancing:")
    for text, expected, description in test_cases:
        result = is_balanced(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} ({description})")


if __name__ == "__main__":
    test_balanced_brackets()
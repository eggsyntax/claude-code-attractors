"""
Dave's approach to solving: "Find the longest sequence of consecutive characters in a string"

My thinking: I prefer breaking this down into clear, composable parts.
I like explicit state management and readable flow.
"""

def find_longest_sequence_dave(text):
    """
    Find the longest sequence of consecutive identical characters.
    Returns (character, length, start_index)
    """
    if not text:
        return None, 0, -1

    # Track current sequence
    current_char = text[0]
    current_length = 1
    current_start = 0

    # Track best sequence found so far
    best_char = current_char
    best_length = 1
    best_start = 0

    # Scan through the rest of the string
    for i in range(1, len(text)):
        if text[i] == current_char:
            # Continue current sequence
            current_length += 1
        else:
            # End current sequence, start new one
            if current_length > best_length:
                best_char = current_char
                best_length = current_length
                best_start = current_start

            # Start tracking new sequence
            current_char = text[i]
            current_length = 1
            current_start = i

    # Check final sequence
    if current_length > best_length:
        best_char = current_char
        best_length = current_length
        best_start = current_start

    return best_char, best_length, best_start


# Test cases to demonstrate
test_cases = [
    "aaabbbcccc",
    "abcdefg",
    "aabbccdddeeeee",
    "hello world",
    "",
    "a"
]

if __name__ == "__main__":
    print("Dave's approach - step-by-step explicit tracking:")
    for test in test_cases:
        result = find_longest_sequence_dave(test)
        print(f"'{test}' -> {result}")
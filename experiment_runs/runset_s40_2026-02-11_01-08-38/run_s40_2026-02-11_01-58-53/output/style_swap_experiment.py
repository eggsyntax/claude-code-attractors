"""
Style Swap Experiment: Dave attempting Tara's approach
Problem: Find the longest substring without repeating characters

Dave normally thinks: "walking through" step-by-step with explicit state
Tara's style seems to be: recognize mathematical structure, explore solution space

Let me try to think like Tara...
"""

def longest_unique_substring_dave_as_tara(s):
    """
    Attempting Tara's style: Look for the mathematical structure

    This is really about sliding windows and set theory...
    We want the maximal window where |window| = |unique_chars_in_window|
    """

    # Classic sliding window with hash map - the "textbook elegant" solution
    char_positions = {}
    max_length = 0
    start = 0

    for end, char in enumerate(s):
        if char in char_positions and char_positions[char] >= start:
            start = char_positions[char] + 1
        char_positions[char] = end
        max_length = max(max_length, end - start + 1)

    return max_length

def longest_unique_substring_alternative_approach(s):
    """
    Alternative: Set-based approach for clarity
    More direct mapping to the mathematical concept
    """
    if not s:
        return 0

    max_len = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            if s[j] in seen:
                break
            seen.add(s[j])
            max_len = max(max_len, len(seen))

    return max_len

# Comprehensive test cases (very Tara-like!)
test_cases = [
    ("", 0, "empty string"),
    ("a", 1, "single character"),
    ("abcdef", 6, "all unique"),
    ("aaaaaa", 1, "all same"),
    ("abcabcbb", 3, "classic example"),
    ("pwwkew", 3, "mixed repetition"),
    ("dvdf", 3, "edge case"),
]

if __name__ == "__main__":
    print("Dave attempting Tara's thinking style:")
    for test_input, expected, description in test_cases:
        result1 = longest_unique_substring_dave_as_tara(test_input)
        result2 = longest_unique_substring_alternative_approach(test_input)
        print(f"'{test_input}' ({description}): {result1}, {result2} (expected: {expected})")
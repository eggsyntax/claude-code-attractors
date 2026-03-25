def longest_common_subsequence_dave_style(text1, text2):
    """
    Find longest common subsequence using Dave's "walking through" approach.
    I'm trying to think step-by-step rather than jump to the DP matrix abstraction.
    """
    # Let me walk through this problem step by step
    # I'm at the beginning of both strings
    # I need to build up the longest subsequence character by character

    # I'll use a 2D table, but think of it as "what's the best I can do
    # when I'm at position i in text1 and position j in text2?"
    rows = len(text1) + 1
    cols = len(text2) + 1

    # Create my walking space - each cell represents a decision point
    dp = [[0 for _ in range(cols)] for _ in range(rows)]

    # Now I'll walk through each position systematically
    for i in range(1, rows):
        current_char1 = text1[i-1]

        for j in range(1, cols):
            current_char2 = text2[j-1]

            # At this position, I have a decision to make
            # Do these characters match?
            if current_char1 == current_char2:
                # Great! I can extend the best subsequence from the diagonal
                # (where I hadn't used either of these characters yet)
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                # No match. I have two choices:
                # 1. Skip this character from text1 (look up)
                # 2. Skip this character from text2 (look left)
                # I'll take whichever gives me the better result
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Now I need to reconstruct the actual subsequence by walking backwards
    result = []
    i, j = len(text1), len(text2)

    while i > 0 and j > 0:
        # Where did this value come from?
        if text1[i-1] == text2[j-1]:
            # This came from a match - add the character
            result.append(text1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            # This came from skipping text1's character
            i -= 1
        else:
            # This came from skipping text2's character
            j -= 1

    # I built it backwards, so reverse it
    return ''.join(reversed(result))

# Test it step by step
def test_step_by_step():
    test1 = "ABCDGH"
    test2 = "AEDFHR"

    print(f"Text 1: {test1}")
    print(f"Text 2: {test2}")

    result = longest_common_subsequence_dave_style(test1, test2)
    print(f"Longest common subsequence: '{result}'")
    print(f"Length: {len(result)}")

    # Let me trace through what happened manually for the first few steps
    print("\nManual trace of first few decisions:")
    print("Position (1,1): A vs A -> Match! LCS length = 1")
    print("Position (1,2): A vs E -> No match, best so far is still 1")
    print("Position (2,1): B vs A -> No match, best so far is still 1")
    print("And so on...")

if __name__ == "__main__":
    test_step_by_step()
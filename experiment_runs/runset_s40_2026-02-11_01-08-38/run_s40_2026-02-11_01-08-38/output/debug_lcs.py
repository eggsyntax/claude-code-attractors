def debug_lcs(text1, text2):
    """Debug LCS to see what the actual subsequence is."""
    m, n = len(text1), len(text2)

    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct the LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            lcs.append(text1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    lcs.reverse()
    return dp[m][n], ''.join(lcs)

# Test the problematic case
test_cases = [
    ("ABCDGH", "AEDFHR"),
    ("AGGTAB", "GXTXAYB"),
    ("PROGRAMMING", "ALGORITHM"),
    ("ABCDEFGHIJK", "ACDEFGHIJKLM")
]

for text1, text2 in test_cases:
    length, subsequence = debug_lcs(text1, text2)
    print(f"'{text1}' vs '{text2}': LCS = '{subsequence}' (length: {length})")
def lcs(s1: str, s2: str) -> tuple[int, str]:
    """
    LCS 动态规划算法
    返回: (最长公共子序列长度, 最长公共子序列字符串)
    """
    n, m = len(s1), len(s2)

    # dp[i][j] = s1[:i] 和 s2[:j] 的 LCS 长度
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # --- 回溯还原具体序列 ---
    seq = []
    i, j = n, m
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            seq.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return dp[n][m], ''.join(reversed(seq))


if __name__ == "__main__":
    # 示例测试
    test_cases = [
        ("ABCBDAB", "BDCAB"),
        ("AGGTAB", "GXTXAYB"),
        ("ABCD", "EFGH"),
        ("AAAA", "AA"),
    ]

    for a, b in test_cases:
        length, seq = lcs(a, b)
        print(f"  s1={a!r}, s2={b!r}")
        print(f"  LCS长度={length}, 序列={seq!r}\n")

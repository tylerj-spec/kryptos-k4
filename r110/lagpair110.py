#!/usr/bin/env python3
"""R110 statistic R_L (PREREGISTRATION section 1), two independent implementations. Standard library only."""
from collections import Counter


def R_counter(s, L):
    """Repeated lag-L pairs: sum over distinct (s_i, s_{i+L}) of n(n-1)/2, by a Counter of pairs."""
    c = Counter((s[i], s[i + L]) for i in range(len(s) - L))
    return sum(n * (n - 1) // 2 for n in c.values())


def R_sorted(s, L):
    """The same count by sorting integer pair codes and counting equal runs."""
    codes = sorted((ord(s[i]) - 65) * 26 + (ord(s[i + L]) - 65) for i in range(len(s) - L))
    tot, run = 0, 1
    for a, b in zip(codes, codes[1:]):
        if a == b:
            run += 1
        else:
            tot += run * (run - 1) // 2
            run = 1
    return tot + run * (run - 1) // 2


def shuffle_p(s, L, rng, n):
    """One-sided p of R_L(s) against n letter-shuffles of s: (1 + #{R >= observed}) / (n + 1)."""
    obs = R_counter(s, L)
    lst = list(s)
    ge = 0
    for _ in range(n):
        rng.shuffle(lst)
        ge += R_counter(lst, L) >= obs
    return (1 + ge) / (n + 1)

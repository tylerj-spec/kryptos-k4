#!/usr/bin/env python3
"""R107 reference for X107's collision test, by a different formulation: two columns x, y are forced equal mod p iff
e_x - e_y lies in the row space of the system mod p (rank test), with no null-space computation. Standard library."""
import itertools


def rank(rows, p):
    M = [[x % p for x in r] for r in rows]
    rk, ncol = 0, len(M[0]) if M else 0
    for col in range(ncol):
        k = next((k for k in range(rk, len(M)) if M[k][col]), None)
        if k is None:
            continue
        M[rk], M[k] = M[k], M[rk]
        inv = pow(M[rk][col], -1, p)
        M[rk] = [(x * inv) % p for x in M[rk]]
        for q in range(rk + 1, len(M)):
            if M[q][col]:
                f = M[q][col]
                M[q] = [(x - f * y) % p for x, y in zip(M[q], M[rk])]
        rk += 1
    return rk


def forced_equal(rows, nv, x, y, p, base_rank):
    v = [0] * nv
    v[x], v[y] = 1, -1
    return rank(rows + [v], p) == base_rank


def collision_rank(rows, nv, cols_a, cols_b):
    r2, r13 = rank(rows, 2), rank(rows, 13)
    for cols in (cols_a, cols_b):
        eq13 = {(x, y) for x, y in itertools.combinations(cols, 2) if forced_equal(rows, nv, x, y, 13, r13)}
        for x, y, z in itertools.combinations(cols, 3):
            if (x, y) in eq13 and (y, z) in eq13:
                return True
        for x, y in eq13:
            if forced_equal(rows, nv, x, y, 2, r2):
                return True
    return False

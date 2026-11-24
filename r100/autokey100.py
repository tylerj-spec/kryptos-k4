#!/usr/bin/env python3
"""R100 reference cipher (PREREGISTRATION section 1; synthetic use only; standard library).
Plaintext ranks in A, ciphertext ranks in B, feedback ranks in F = A, B or AZ (straight alphabet):
B^-1(C_i) = s1*A^-1(P_i) + s2*F^-1(P_{i-L}) + c (i >= L); B^-1(C_i) = s1*A^-1(P_i) + k_i (i < L, primer k)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SIGNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
FEEDBACK = ("A", "B", "AZ")


def frank(letter, A, B, F):
    return (A if F == "A" else B if F == "B" else AZ).index(letter)


def enc_letter(p, fb, A, B, F, s1, s2, c):
    return B[(s1 * A.index(p) + s2 * frank(fb, A, B, F) + c) % 26]


def dec_letter(ch, fb, A, B, F, s1, s2, c):
    return A[(s1 * (B.index(ch) - s2 * frank(fb, A, B, F) - c)) % 26]


def encrypt(pt, A, B, F, L, s1, s2, c, primer):
    return "".join(B[(s1 * A.index(p) + primer[i]) % 26] if i < L else enc_letter(p, pt[i - L], A, B, F, s1, s2, c)
                   for i, p in enumerate(pt))


def decrypt(ct, A, B, F, L, s1, s2, c, primer):
    out = []
    for i, ch in enumerate(ct):
        out.append(A[(s1 * (B.index(ch) - primer[i])) % 26] if i < L else
                   dec_letter(ch, out[i - L], A, B, F, s1, s2, c))
    return "".join(out)

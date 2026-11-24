#!/usr/bin/env python3
"""R99 reference cipher (PREREGISTRATION section 1; synthetic use only; standard library).
One alphabet A for plaintext, ciphertext and feedback ranks: y_i = s1*x_i + s2*x_{i-L} + c (i >= L),
y_i = s1*x_i + k_i (i < L, primer k). x = rank of the plaintext letter in A, y = rank of the ciphertext letter."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SIGNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def enc_letter(p, fb, A, s1, s2, c):
    """Cipher letter for plaintext letter p with feedback plaintext letter fb."""
    return A[(s1 * A.index(p) + s2 * A.index(fb) + c) % 26]


def dec_letter(ch, fb, A, s1, s2, c):
    """Plaintext letter for cipher letter ch with feedback plaintext letter fb (s1 = +-1 is its own inverse)."""
    return A[(s1 * (A.index(ch) - s2 * A.index(fb) - c)) % 26]


def encrypt(pt, A, L, s1, s2, c, primer):
    out = []
    for i, p in enumerate(pt):
        if i < L:
            out.append(A[(s1 * A.index(p) + primer[i]) % 26])
        else:
            out.append(enc_letter(p, pt[i - L], A, s1, s2, c))
    return "".join(out)


def decrypt(ct, A, L, s1, s2, c, primer):
    out = []
    for i, ch in enumerate(ct):
        if i < L:
            out.append(A[(s1 * (A.index(ch) - primer[i])) % 26])
        else:
            out.append(dec_letter(ch, out[i - L], A, s1, s2, c))
    return "".join(out)


def condi_encrypt(pt, A, start):
    """ACA Condi, coded separately from the general form: the keyed alphabet is numbered 1-26; the first letter is
    shifted forward by the start number; every later letter by the number of the previous plaintext letter."""
    number = {ch: n + 1 for n, ch in enumerate(A)}
    out, shift = [], start
    for p in pt:
        out.append(A[(number[p] - 1 + shift) % 26])
        shift = number[p]
    return "".join(out)

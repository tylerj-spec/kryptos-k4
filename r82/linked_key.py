#!/usr/bin/env python3
"""R82 linked-key, different-tableau reference model (SYNTHETIC ONLY).

Same keyword is used twice, with the second-stage keyword slot rotated
once after every handwritten row. No K4 ciphertext, known clue positions,
wordlist, English scorer, or solver is used. This file defines a
reversible construction plus a NON-SPECIFIC necessary collision test.
"""
from collections import defaultdict
import models as M


def _setup(first, second, width):
    if not isinstance(first, M.Stage) or not isinstance(second, M.Stage):
        raise TypeError("two Stage instances required")
    if first.key != second.key:
        raise ValueError("the two layers must share EXACTLY one keyword")
    if M.alphabet(first.cipher) == M.alphabet(second.plain):
        raise ValueError("intermediate alphabet identical: additive collapse")
    if not isinstance(width, int) or width <= 0:
        raise ValueError("width must be a positive integer")
    return first.key, len(first.key)


def slots(i, m, width):
    """First-stage and second-stage key indices at ciphertext position i."""
    if i < 0 or m < 1 or width < 1:
        raise ValueError("invalid position, keyword period or row width")
    return i % m, (i + i // width) % m


def encrypt(plaintext, first, second, width):
    key, m = _setup(first, second, width)
    M.check_text(plaintext)
    a1, b1 = M.alphabet(first.plain), M.alphabet(first.cipher)
    a2, b2 = M.alphabet(second.plain), M.alphabet(second.cipher)
    kn = [M.AZ.index(ch) for ch in key]
    output = []
    for i, ch in enumerate(plaintext):
        r, s = slots(i, m, width)
        mid = b1[(first.sign * a1.index(ch) + kn[r]) % 26]
        output.append(b2[(second.sign * a2.index(mid) + kn[s]) % 26])
    return "".join(output)


def decrypt(ciphertext, first, second, width):
    key, m = _setup(first, second, width)
    M.check_text(ciphertext)
    a1, b1 = M.alphabet(first.plain), M.alphabet(first.cipher)
    a2, b2 = M.alphabet(second.plain), M.alphabet(second.cipher)
    kn = [M.AZ.index(ch) for ch in key]
    output = []
    for i, ch in enumerate(ciphertext):
        r, s = slots(i, m, width)
        mid = a2[(second.sign * (b2.index(ch) - kn[s])) % 26]
        output.append(a1[(first.sign * (b1.index(mid) - kn[r])) % 26])
    return "".join(output)


def schedule_period(m, width):
    """Generic ordered (first-slot, second-slot) schedule period.

    For m>=2, the least global period is m*width. This says nothing
    about statistical detectability within a 97-symbol observation.
    For m=1, both indices are always zero, so the period is 1.
    """
    if m < 1 or width < 1:
        raise ValueError("invalid period or width")
    return m * width if m > 1 else 1


def same_pair_positions(n, m, width):
    """Groups that use identical key-index pairs; may have no repeats."""
    if n < 0 or m < 1 or width < 1:
        raise ValueError("invalid length, period, or width")
    d = defaultdict(list)
    for i in range(n):
        d[slots(i, m, width)].append(i)
    return [tuple(v) for v in d.values() if len(v) > 1]


def comparison_pairs(n, m, width):
    for group in same_pair_positions(n, m, width):
        for j in range(len(group)):
            for k in range(j + 1, len(group)):
                yield group[j], group[k]


def collision_count(text, m, width):
    """A weak, NON-DISCRIMINATIVE ciphertext-only necessary statistic.

    A conventional period-m substitution also satisfies the SAME
    collision relations. This cannot identify linked two-layer encryption.
    """
    M.check_text(text)
    return sum(text[i] == text[j] for i, j in comparison_pairs(len(text), m, width))


def equality_mismatches(plaintext, ciphertext, m, width):
    """On planted truth, every same-slot-pair equality relation must match."""
    M.check_text(plaintext)
    M.check_text(ciphertext)
    if len(plaintext) != len(ciphertext):
        raise ValueError("different plaintext/ciphertext lengths")
    pairs = list(comparison_pairs(len(plaintext), m, width))
    bad = [(i, j) for i, j in pairs
           if (plaintext[i] == plaintext[j]) != (ciphertext[i] == ciphertext[j])]
    return len(pairs), bad

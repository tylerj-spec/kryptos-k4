#!/usr/bin/env python3
"""R82 synthetic-only reference models (no K4 ciphertext or published clues).

Models are construction witnesses, not K4 solvers: 26-letter 2x13
coordinate fractionation, genuinely distinct-tableau double substitution,
a per-slot progressing key, and a previously studied transposition control.
"""
from dataclasses import dataclass

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"),
        "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}


def alphabet(name):
    a = ALPH.get(name, name)
    if len(a) != 26 or set(a) != set(AZ):
        raise ValueError("alphabet must be a permutation of A-Z")
    return a


def check_text(text):
    if any(ch not in AZ for ch in text):
        raise ValueError("text must contain only uppercase A-Z")


def permutation(n, rule):
    if rule == "id":
        return list(range(n))
    if rule == "rev":
        return list(range(n - 1, -1, -1))
    if rule == "rot1":
        return [(i + 1) % n for i in range(n)] if n else []
    if rule == "evenodd":
        return list(range(0, n, 2)) + list(range(1, n, 2))
    raise ValueError("unknown component route")


def frac26_encrypt(text, a, block=7, row="id", column="rev"):
    """Independent row/column coordinate routes, in blocks, in a 2x13 alphabet.

    The final partial block is NEVER padded. If row and column routes are
    identical, this collapses to simple transposition and is only a control.
    """
    a = alphabet(a)
    check_text(text)
    if not 2 <= block <= 97:
        raise ValueError("block outside 2..97")
    out = []
    for off in range(0, len(text), block):
        part = text[off:off + block]
        coords = [divmod(a.index(ch), 13) for ch in part]
        pr, pc = permutation(len(part), row), permutation(len(part), column)
        out += [a[13 * coords[pr[i]][0] + coords[pc[i]][1]] for i in range(len(part))]
    return "".join(out)


def frac26_decrypt(text, a, block=7, row="id", column="rev"):
    a = alphabet(a)
    check_text(text)
    if not 2 <= block <= 97:
        raise ValueError("block outside 2..97")
    out = []
    for off in range(0, len(text), block):
        part = text[off:off + block]
        coords = [divmod(a.index(ch), 13) for ch in part]
        pr, pc = permutation(len(part), row), permutation(len(part), column)
        rows, cols = [None] * len(part), [None] * len(part)
        for i in range(len(part)):
            rows[pr[i]], cols[pc[i]] = coords[i]
        out += [a[13 * rows[i] + cols[i]] for i in range(len(part))]
    return "".join(out)


def frac26_margins(text, a, block=7):
    """Row count and 13 column counts: exactly conserved within each block."""
    a = alphabet(a)
    check_text(text)
    out = []
    for off in range(0, len(text), block):
        rc = [divmod(a.index(ch), 13) for ch in text[off:off + block]]
        out.append((sum(r for r, _ in rc),
                    tuple(sum(c == j for _, c in rc) for j in range(13))))
    return out


@dataclass(frozen=True)
class Stage:
    plain: str
    cipher: str
    key: str
    sign: int = 1

    def __post_init__(self):
        alphabet(self.plain)
        alphabet(self.cipher)
        check_text(self.key)
        if not self.key or self.sign not in (-1, 1):
            raise ValueError("stage requires keyword and +/-1 sign")


def stage_encrypt(text, stage):
    check_text(text)
    pa, ca = alphabet(stage.plain), alphabet(stage.cipher)
    return "".join(ca[(stage.sign * pa.index(p) + AZ.index(stage.key[i % len(stage.key)])) % 26]
                   for i, p in enumerate(text))


def stage_decrypt(text, stage):
    check_text(text)
    pa, ca = alphabet(stage.plain), alphabet(stage.cipher)
    return "".join(pa[(stage.sign * (ca.index(c) - AZ.index(stage.key[i % len(stage.key)]))) % 26]
                   for i, c in enumerate(text))


def two_tableau_encrypt(text, first, second):
    if alphabet(first.cipher) == alphabet(second.plain):
        raise ValueError("same intermediate alphabet collapses to additive keyword stages")
    return stage_encrypt(stage_encrypt(text, first), second)


def two_tableau_decrypt(text, first, second):
    if alphabet(first.cipher) == alphabet(second.plain):
        raise ValueError("same intermediate alphabet collapses to additive keyword stages")
    return stage_decrypt(stage_decrypt(text, second), first)


def evolving_encrypt(text, a, initial, increments, sign=1):
    a = alphabet(a)
    check_text(text)
    if not initial or len(initial) != len(increments) or sign not in (-1, 1):
        raise ValueError("initial and increments need identical nonzero periods")
    m = len(initial)
    return "".join(a[(sign * a.index(p) + initial[i % m] +
                      (i // m) * increments[i % m]) % 26] for i, p in enumerate(text))


def evolving_decrypt(text, a, initial, increments, sign=1):
    a = alphabet(a)
    check_text(text)
    if not initial or len(initial) != len(increments) or sign not in (-1, 1):
        raise ValueError("initial and increments need identical nonzero periods")
    m = len(initial)
    return "".join(a[(sign * (a.index(c) - initial[i % m] -
                      (i // m) * increments[i % m])) % 26] for i, c in enumerate(text))


def second_differences(text, a, period):
    """For progressing keys, D2(cipher) equals sign times D2(plaintext)."""
    a = alphabet(a)
    check_text(text)
    if period < 1:
        raise ValueError("period must be positive")
    x = [a.index(ch) for ch in text]
    return [(x[i] - 2 * x[i + period] + x[i + 2 * period]) % 26
            for i in range(max(0, len(x) - 2 * period))]


def column_route(n, width, snake_rows=False):
    """Old-model transposition control, not a new untested cipher family."""
    if not 2 <= width <= n:
        raise ValueError("bad width")
    grid = [[None] * width for _ in range((n + width - 1) // width)]
    for i in range(n):
        row, col = divmod(i, width)
        grid[row][width - col - 1 if snake_rows and row % 2 else col] = i
    return [grid[r][c] for c in range(width) for r in range(len(grid)) if grid[r][c] is not None]


def transpose(text, route):
    if len(route) != len(text) or set(route) != set(range(len(text))):
        raise ValueError("invalid route")
    return "".join(text[i] for i in route)


def untranspose(text, route):
    if len(route) != len(text) or set(route) != set(range(len(text))):
        raise ValueError("invalid route")
    out = [None] * len(text)
    for j, i in enumerate(route):
        out[i] = text[j]
    return "".join(out)

"""R66 sealed helpers: classic homophonic tables (several cipher letters per plaintext letter, allocated in proportion
to English letter frequency) and encryption. Never read by r66/blind/."""
import random

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# English letter frequencies (percent; standard reference values), used only to size homophone sets
FREQ = dict(zip(AZ, [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15, 0.77, 4.03, 2.41, 6.75, 7.51, 1.93,
                     0.10, 5.99, 6.33, 9.06, 2.76, 0.98, 2.36, 0.15, 1.97, 0.07]))


def table(plaintext, rng):
    """Every distinct letter of the message gets one cipher letter; the remaining cipher letters go, one at a time, to
    the letter with the largest frequency per homophone. Returns f (cipher letter -> plaintext letter) for all 26."""
    need = sorted(set(plaintext))
    count = {p: 1 for p in need}
    for _ in range(26 - len(need)):
        p = max(need, key=lambda q: (FREQ[q] / count[q], q))
        count[p] += 1
    sym = list(AZ)
    rng.shuffle(sym)
    f, k = {}, 0
    for p in need:
        for _ in range(count[p]):
            f[sym[k]] = p
            k += 1
    return f


def encrypt(plaintext, f, rng):
    inv = {}
    for c, p in sorted(f.items()):
        inv.setdefault(p, []).append(c)
    return "".join(rng.choice(inv[p]) for p in plaintext)


def ic(s):
    from collections import Counter
    n = len(s)
    return sum(v * (v - 1) for v in Counter(s).values()) / (n * (n - 1))

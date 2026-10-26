#!/usr/bin/env python3
"""Per-column repetition invariant (Claude R26; ledger L89). For ANY in-place cipher with one fixed bijection per
column i mod m (Vigenère/Beaufort/Quagmire in any alphabets, per-slot alphabets, Porta), two letters in the same column
are equal in the ciphertext exactly when they are equal in the plaintext, so the plaintext must have the same number
T_m of same-column equal pairs as K4. Compares K4 with English 97-letter texts carrying the clues at K4's positions
(K1-K3 windows + released hidden-test messages). Result: K4 is incompatible with English at m 1-9, 11-19, 22-24, 26,
27, 35-37, 39 (fewer repeats than >= 95% of English) -> K4's key behaves as non-repeating."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k4common import DATA, K4  # noqa: E402


def T(s, m):
    return sum(n * (n - 1) // 2 for r in range(m) for n in Counter(s[r::m]).values())


def with_clues(w):
    return w[:21] + "EASTNORTHEAST" + w[34:63] + "BERLINCLOCK" + w[74:97]


k13 = (DATA / "k1k3_plaintext.txt").read_text().strip()
ref = [with_clues(k13[s:s + 97]) for s in range(0, len(k13) - 97, 5)]
msgs = json.loads((DATA / "reference_messages.json").read_text())
ref += msgs["calibration"] + msgs["r20_templates"]
print(f"{len(ref)} English references\n m  K4  English min/median  share of English <= K4")
ok = []
for m in range(1, 49):
    k = T(K4, m)
    e = sorted(T(x, m) for x in ref)
    share = sum(v <= k for v in e) / len(e)
    ok += [m] if share >= 0.05 else []
    print(f"{m:2d} {k:4d}  {e[0]:4d} / {e[len(e) // 2]:4d}        {share:6.1%}")
print("periods compatible with English (>= 5% of references as low as K4):", ok)

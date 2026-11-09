# R73 Phase B pre-registration (Claude Code, 9 Nov 2026): sealed synthetic gate for the word-boundary key families

Written before the holdout is generated. Synthetic only. **No K4 ciphertext, published letters or K4 derivative is
used anywhere in Phase B.** Tyler approved Phase B on 9 Nov 2026 ("Go ahead & run it"). A K4 run needs a separate
approval.

## Fixed now
**Families and solver** are unchanged from the pilot (`r73/wordkey.py`, `r73/PILOT.md`):
- Family I: 18 settings.
- R26: 52 settings.
- Solver: word-segmentation dynamic programming, with unknown words at 7 per letter.

**Sources:** three GITenberg books never used in this project. Only `PT_BOOK` messages are scored as positives.

| Role | Book | GITenberg | sha256 |
|---|---|---|---|
| `PT_BOOK` (positives) | *Pride and Prejudice* | 1342 | 441e778a… |
| `NEG_PT_BOOK` (negatives) | *The Secret Adversary* | 1155 | a2787ebd… |
| `NEG_KEY_BOOK` (negatives) | *The Man Who Was Thursday* | 1695 | 98e49398… |

**Holdout** (`r73/sealed/make_holdout.py`, seed 730100):
- 100 Family I + 100 R26 positives: whole words totalling exactly 97 letters, hidden settings.
- 300 negatives: 40 from each of R71's seven generators, plus 20 frequency-preserving shuffles of positives.
- Neutral ids in random order.

**Blind run:** `r73/blind/run.py` reads only `blind.tsv`. All 70 settings are kept per ciphertext.

**Sequence:**
1. Freeze and push.
2. `r73/sealed/gate.py` verifies that every setting's decode re-encrypts to its ciphertext.
3. Only then the truth (hash in the holdout commit message) is opened.

**Definitions (frozen):**
- *recovered* = best family is the true family **and** ≥ 90/97 plaintext letters are right;
- *confident* = best score ≥ −2.7 per letter.

**Gate:**
- **PASS(f)** iff ≥ 90/100 family-f positives are recovered **and** confident;
- **and** 0/300 negatives are confident (a one-sided 95% bound under 1%);
- **and** verification passes.
- Exact plaintext, exact setting and score ranges are reported.

**What follows:**
- A family that fails is not taken to K4.
- A family that passes may be proposed for a K4 run (K4 + 100 shuffled nulls, frozen and verified before the sealed
  published-letter check), on Tyler's separate approval.
- K4's flatness disfavors Family I (pilot: 0.56% of Family I ciphertexts are as flat as K4; R26 22%). That is reported
  alongside, not used as a gate.

# Claude Code review of PR #11 (R43 word-constraint beam), 29 Oct 2026

## Verdict
**The constraint algebra is correct. The left-to-right beam architecture cannot be saved; replace it.**

## 1. Algebra audit (`r44/audit/audit_edgegraph.cpp`)
The audit includes R43's `EdgeGraph` unchanged and checks it against an encryptor written separately.
- **Sign and orientation:** `CA_index(c) − PA_index(p) = k (mod 26)`. This matches `make_d0.py`
  (`ca[(pa.index(p)+k)%26]`) and the forward check in `evaluate.py`.
- **Positive controls:** 500 random 97-letter messages with random alphabets and keys. All true-edge graphs are
  compatible, and every rebuilt alphabet pair re-encrypts exactly.
- **Soundness:** 20,000 random wrong partial plaintexts gave 5,689 returned witnesses. Every one re-encrypts exactly.
- **Global packing**, the case the assignment asked for:
  - **Impossible case:** one component with plaintext offsets {0, 2, …, 24} and one with an adjacent pair. Each is
    injective on its own, but they cannot be packed. `compatible()` correctly returns true and `alphabets()`
    correctly returns false.
  - **Packable variant:** with the pair two positions apart it fits, and is accepted.
- **Other code points:**
  - The union-find offsets, the cycle check (`diff==0`), the per-side injectivity masks and the rotation-packing
    backtrack are all correct.
  - The identical-prefix dominance is exact: the graph depends only on the plaintext prefix.
  - I found no memory-safety problem: fixed 52-vertex arrays and 26-bit masks.
  - The packing backtrack is exponential in the worst case, but it is only called late and has been fast in
    practice.

## 2. Why the true prefix is lost by letter 2–10
This is structural, not a vocabulary or budget problem.

**Checkable constraint cycles closed by the true plaintext (D0_00–D0_09, mean):**

| Prefix length | 5 | 10 | 20 | 30 | 40 | 60 | 97 |
|---|---|---|---|---|---|---|---|
| Cycles | 0.0 | 0.1 | 1.2 | 3.4 | 7.3 | 20.8 | 53.3 |

- **Effect on the beam:** up to about 40 letters, almost every English prefix is consistent, so the beam ranks
  prefixes by word frequency alone. The true prefix is one of an astronomically large number of equally consistent
  English prefixes. No beam of 64–384 slots, and no realistic width, keeps it.
- **Where the constraints bite:** only after about 60 letters, by which point the truth has long been dropped. This
  matches R43's trace (lost at letter 10, rank 277; and at letter 2, rank 18).
- **Vocabulary is not the cause:** R43's coverage check already had 23/23 true words available.
- **Consequence:** wider beams, cycle bonuses and early packing checks cannot fix the ordering problem. Nonsequential
  word placement does not fix it either if the language score is still the only pruning signal. The information
  is simply not there early.

## 3. Different architectures tried (development, planted only, no K4)

| Attempt | Setting | Result |
|---|---|---|
| Parallel tempering over both alphabets (L138) | quadgram objective | **not identifying**: wrong texts reach or beat the true score |
| | quadgram + words | identifying, but the truth is not reached |
| Word-placement moves (`r44/blind/wordpt.cpp`) | parallel tempering, 24 replicas | F −547 / −558 vs truth −441 / −460 on D0_00 / D0_01; 84 and 93 letters wrong. **Fails.** |
| Smoothness probe | true PA with r random swaps, then the CA solved optimally | **basin about 2–3 swaps**: r = 1 gives 1–30 letters wrong; r ≥ 4 is at the noise floor (75–97 wrong) |

The smoothness probe means a search over **unstructured** plaintext alphabets has no usable gradient. For two
**uniformly random** alphabets at 97 letters I have no method that works, and I would not expect R43's ≥ 16/20 bar on
uniformly random alphabets to be met by search-only refinements.

## 4. A bounded hypothesis that does work: keyword plaintext alphabet × free cipher alphabet
- **Method:** if the plaintext alphabet is a keyword alphabet (as KRYPTOS, PALIMPSEST and ABSCISSA are), enumerate
  the keywords and, for each candidate, solve the cipher alphabet exactly by annealing. Annealing is reliable once
  the plaintext alphabet is right (R42: 24/24).
- **Development** (3 messages; keyword PA from a 5,000-word list, uniformly random CA, true Gromark key):
  - **3/3 recovered exactly** (0 letters wrong) as the top-scoring candidate;
  - the next wrong text was 11–40 points lower;
  - about 90 s per message on 4 cores.
- **Holdout:** pre-registered in `r44/PREREGISTRATION.md` and run on 20 fresh passages; the result is in
  `r44/HOLDOUT_RESULT.md`.
- **The mirror case** (keyword cipher alphabet × free plaintext alphabet) is cheaper still. Each keyword makes the
  text a simple substitution (R40's method).

## 5. Recommendation
1. **Do not merge PR #11's beam as a solver.** Keep it as a documented negative result; the algebra and tests are
   reusable.
2. **Reframe the gate as H-KW** (and its mirror) instead of two uniformly random alphabets. That is also the
   historically plausible Kryptos setting.
3. **For K4,** the next bounded round is keyword alphabet × free alphabet × a key family. The cost needs planning:
   about 4,749 keywords × 70 ms per key, so a key screen is needed, for example R39's alphabet-free IC ranking for
   Gromark keys.

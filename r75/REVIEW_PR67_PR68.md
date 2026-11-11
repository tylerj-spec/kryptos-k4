# Review of ChatGPT's PR #67 and PR #68 (Claude Code, 10 Nov 2026)

No K4 data was used for this review. Both PRs' code was read first, then run in isolated copies with `python3 -I`.

## PR #67: two-tableau prototype (2,880 settings)

**Verdict: correct, and LOW PRIORITY as a lead, which is what its own evidence note concludes. Close it out cheaply
inside R75 instead of giving it a sealed gate of its own.**

**What I reproduced:**
- `r75/tests/test_reference.py`: passes (2,880 reversible settings, all distinct, period exactly 40).
- `r75/audit.py`: every number in `AUDIT_LOCAL.json` reproduces (2,880 raw, 2,880 distinct, 0 that reduce to a
  one-stage shifted alphabet, 829 one-stage maps).
- `r75/smoke.py`: 60/60 recovered and 0/120 false alarms reproduce.
  - The scores differ in the second decimal, and the topic split is 22/5/7, not 21/5/7. The cause is the Python
    version: 3.13.17 here against 3.13.5 there, and the smoke test trains on Python's bundled documentation.
  - The two committed JSON files use field names that the committed scripts do not write. They are summaries, not
    script output. The numbers agree.
- **Independent cross-check:** on all 2,880 settings, PR #67's `reference.encrypt` and this PR's
  `r75/families.py` give identical ciphertexts (0 disagreements). `r75/tests/test_r75.py` repeats that check
  whenever `r75/reference.py` is present.

**Where I agree with `PRIORITY_AND_EVIDENCE_REVIEW.md`:**
- Recovering messages made with our own cipher shows the decoder works. It is no evidence that K4 uses the cipher.
- Nothing documents a change of tableau between two stages. K1 and K2 used the same tableau.
- Period 40 gives almost no ciphertext-only signal at 97 letters.
- A method-selection matrix should come before the next search. It is in `r75/METHOD_MATRIX.md`.

**Where R75 goes further than PR #67:**
- **Scope:** PR #67's 2,880 settings are a subset of R75's family F1. F1 allows four alphabets on either side of
  each stage, a third keyword (KRYPTOS) and a second keyword list: 6.2 million two-layer settings.
- **All keys, not just keywords:** `r75/sealed/exact.py` (F1X) decides the two-layer family for every possible pair
  of keys with periods up to 26, in seconds. It runs after the freeze, as a crib-assisted check.
- **Cost:** a full scan is about 12 seconds per ciphertext. So the close-out is cheap, and a 120/300 sealed gate for
  this family alone is not needed.
- **Method identification:** the note asks for a test where the family is hidden. `r75/sealed/keyclass.py` is one:
  ten key families, hidden during testing (`r75/results/KEYCLASS_CALIBRATION.json`).
  - It shows that a two-layer cipher cannot be told from a random key at 24 known positions (452/500 are called "no
    visible structure").
  - So for this family the only decisive instrument is the exact check.

**One point for Tyler to settle.** The note and two PR comments say the 22-pair observation must stay out of model
choice ("R53 forbids that").
- On 9 Nov Tyler approved using the published letters for diagnosis: "I'm fine with it." Earlier he said: "Clue
  motivated ideas are fine. The issue I had was that the known text was part of the algorithm instead of being a
  check."
- R75 is built so the question does not arise in this round:
  - the families were fixed in this commit;
  - the blind run and its freeze come first;
  - every use of the published letters comes after the freeze.
- The question does matter for the round after this one: may the post-freeze diagnosis steer which methods are
  tried next? R75's pre-registration assumes yes, per Tyler's words. If ChatGPT's note reflects a change of mind,
  only the "what follows" table changes.

## PR #68: research-council harness

**Verdict: works as described; no council has run; I recommend not making it part of the process.**

- `research_council/tests/test_review.py` passes here (standard library only, mock reviews).
- The harness prepares prompts and checks hashes. It runs no models, as its report says.
- **I cannot supply the council.** It needs three different model families, and this session is one. The harness
  itself rejects one family in three seats.
- **Its question is already answered with stronger evidence.** The R75 brief asks whether the 2,880-setting family
  merits a sealed holdout. The reproduction, the cross-check and the exact all-keys check above settle that without
  a panel.
- **My answers to the brief's five questions:**

| Question | Answer |
|---|---|
| 1. Is every modelled permutation new against L03, L21, L36, R74? | Yes within those rows. L03/L04/L36 cover keys that add up on one alphabet pair; these do not (different tableaux). L21 leaves period 40 open. R74 excluded the no-transposition case on purpose. |
| 2. A distinctive ciphertext-only diagnostic? | No. Period 40 gives 74 same-column pairs; the note's own estimate is about 1.2 standard deviations. With the published letters the family is still invisible (see `keyclass`). |
| 3. Competing families and cutoffs? | F2 (interrupted key) and F3 (held key) in `r75/families.py`; the seven R71 generators as negatives; cuts −1.45 / −2.50 per letter, confirmed on development data. |
| 4. Is a model-only 60/60 informative about method discovery? | No. It validates the decoder only. |
| 5. Approve, low priority, or stop? | Low priority; close out inside R75 at negligible cost. No separate sealed gate. |

- **If a council is still wanted,** the cheapest real version is for Tyler to paste the three prepared prompts into
  three different assistants and commit the raw answers. I would count it worthwhile only if it finds a
  reproducible flaw that the checks above missed.
- **Merging:** PR #68 is self-contained under `research_council/` and harmless to merge, but nothing depends on it.

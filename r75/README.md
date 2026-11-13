# R75: two distinct tableaux in series, no transposition — synthetic prototype

**9 November 2026. Status: DEVELOPMENT ONLY. No K4 target data, no released K4 clues, no candidate, no K4 run, no merge.**

## Why this family

K1 and K2 historically used a KRYPTOS-keyed tableau with the independent
keywords PALIMPSEST and ABSCISSA. Claude identified a possibility not
demonstrably covered in prior finite experiments: **the two keyword stages use
different alphabets (AZ and KRYPTOS) in series**, with no transposition.
This is *a proposed method*, not evidence Sanborn actually used it.

**Exact restriction:** stage alphabets (AZ,KRY) or (KRY,AZ); keyword order
(PALIMPSEST,ABSCISSA) or reversed; independent start phases 0..9 and
0..7; VIG, BEAU or VARB at each stage, operating on the stage's own
alphabet with independent ranks. 97 plaintext characters, no padding,
nulls, added keys, phonetic rewrites or physical route assumptions.

For stage alphabet A, operation parameters (s,t) in
{VIG:(+1,+1),BEAU:(-1,+1),VARB:(+1,-1)}, input x,
keyword K, offset a:

    E_A(x,K,a)[i] = A[(s*index_A(x[i]) + t*index_A(K[(i+a)%|K|])) % 26]

    C = E_{A2}(E_{A1}(P,K1,a1), K2,a2).

The inverse undoes stage 2 then stage 1 with the same distinct alphabets.
See [reference.py](reference.py), [audit.py](audit.py), [scan.py](scan.py)
and [smoke.py](smoke.py).

## Exact mathematical audit (executed locally; CLI can reproduce)

- 2 alphabet orders × 2 keyword orders × (10×8) phase pairs × (3×3)
  operations = **2,880 raw settings**.
- Every setting is a different function on every possible 97-letter input:
  **2,880 distinct complete 40-position substitution-map families**.
- Every family has **minimum period exactly 40**.
- 2,880/2,880 complete 97-letter encryption/inversion tests passed in the
  independent local reference implementation.
- Comparing each of the forty positional bijections with every shift,
  operation, plaintext-alphabet, and cipher-alphabet choice in
  {AZ, KRYPTOS-keyed, PALIMPSEST-keyed, ABSCISSA-keyed}: **zero of the
  2,880 are equivalent to an ordinary one-stage, one-shift-per-position
  cipher built from those fixed alphabets**. The audit enumerated 829
  distinct one-stage positional maps. See
  [AUDIT_LOCAL.json](AUDIT_LOCAL.json).
- **Scope caution:** This is NOT proof against arbitrary 26! per-slot
  alphabets (L21), every L03 implementation, or any unknown extra alphabet.
  A full source-level equivalence/coverage audit remains a hard gate.
  "It has period 40" by itself does **not** make it new.

## Development-only smoke result (executed; NOT sealed evidence)

The independent local scanner used a disposable trigram/quadgram language
model trained on 21 bundled Python \`pydoc_data.topics\` articles.
There were 5 different development topics and 7 held-out topics
(33 total topics, all technical prose). The solver did not receive the
generating key, original plaintext, or true family settings.

- **60/60** held-out 97-letter synthetic ciphertexts recovered **full
  plaintext and exact setting** at top rank.
- **0/120** development-style negative controls crossed the
  confidence threshold chosen using **different development topics**.
- Four null types: iid random A–Z, plaintext-letter shuffles, periodic
  Vigenère, and monoalphabetic substitution.
- **0 K4 ciphertexts**, **0 K4 known plaintext letters or positions**,
  **0 original K4 method/keys**, **0 R53 reveal calls**.
- In a separate 80-ciphertext synthetic sample, ~11.25% had IC <= 0.0361;
  this is only *descriptive* and has not been used to select parameters.
- See [SMOKE_LOCAL.json](SMOKE_LOCAL.json).

**Big limitations:** technical documentation is NOT unseen historical
literature; the development and holdout share writing style and bundled
source distribution. This is not a pre-registered sealed test, there are
only 120 negatives, and the provisional model is weaker/different from
the pinned R59 order-6 + word scorer. The false-positive upper confidence
bound and generalization to natural K4-like text are not established.
Never use these numbers as authorization to attempt K4.

## Next step: independently sealed REAL literary-text gate (not run)

Claude should first run:
  1. \`python3 -I r75/tests/test_reference.py\`
  2. \`python3 -I r75/audit.py\`
  3. \`python3 -I r75/smoke.py\`
  
Then perform a method-coverage and corpus-hash review using main's
\`LEDGER.md\`, \`docs/CIPHER_TYPES_TESTED.md\`, L03/L21/L36/L89,
R74 and R53. Any mathematical overlap discovered -> label exact subset,
deduplicate, STOP if none remains. Run the \`r75/scan.py\` scanner
against a pinned \`r59\` language model on *fresh development prose*,
with the **same complete 2,880-setting scan on every negative**.
Use the existing \`r74/scan.word_score\` and \`r73/wordkey.load_words\`
as a second pre-registered generic scorer, **not** K4 clue words.

Proposed sealed gate (requires its own hash-locked pre-registration BEFORE
holdout texts are generated):

- **120 independent 97-character positive messages** from at least two
  newly pinned, out-of-training literary sources; distribute all
  alphabet and keyword orders, signs and phases; include 20 independently
  specified minor misspellings and name-rich passages.
- **300 fresh, wrong-family negatives**, including the seven R71
  generators, plus count-preserving and structured shuffles of positives.
  Negatives must not be inadvertently drawn from the R75 model.
- Thresholds chosen solely on disjoint development passages and controls.
  Require **>=108/120 exact 97/97 plaintext + exact canonical settings
  and confident**, **0/300 false confident**, all output candidates
  independently forward-encrypt, with uncertainty intervals reported.
- Test sensitivity specifically against synthetic flat ciphertext
  matching K4 IC *as a pre-specified diagnostic*, without using that
  property to change which cipher settings are searched.
- Separate **K4 run only upon owner authorization after a sealed PASS**.
  Original ciphertext only, K4 and at least 1,000 fresh
  frequency-preserving shuffles all scanned under all 2,880 settings.
  Freeze and remote-commit complete raw 97-letter decrypts, settings,
  unmodified scores, code/corpus/ciphertext hashes and top-25 packet
  **before any separate published-letter evaluator**. No clue-driven
  new search, stop, key fitting or score tuning.
- An apparent readable 97-letter text alone or exact forward-encryption
  alone does NOT constitute a solution. Genuine candidates require
  independently fluent text, full methodology and postfreeze 24-letter
  check. Under no circumstance may pubished K4 plaintext be supplied to
  \`reference.py\`, \`scan.py\`, the scorer or an automatic target runner.

**Owner review requested:** Claude can implement a separate R75
literary holdout protocol, inspect this prototype, and report an
APPROVE/REVISE/STOP recommendation. This PR does NOT authorize K4
execution, a repo merge, or external checker submissions.

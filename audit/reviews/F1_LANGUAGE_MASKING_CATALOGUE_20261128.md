# F1: reversible language masking as concrete mechanisms, with what each predicts (Claude Code, 28 Nov 2026; G0, desk only)

Affected ledger IDs: none. This is a planning catalogue: nothing is run and no row changes.

Validation:
- a ledger scan for masking and language coverage (L26, L29, L33, L45, L51, L61, L62, L63, L64, L68, L69, L81, L84,
  L104, L108);
- the invariance argument in §2 follows from the equations of the checks it names (L90, L92, X107, X112, R102, X115).

Independent review: NONE (one model). Fallback task F1 of `audit/reviews/BATCH_WORK_ORDER_R102_R107.md` (authorized
at once).

## 1. Two readings of the clues
Under a masking layer, it matters which layer the published letters describe.
- **Reading A: the clues describe the enciphered layer.** The text that is directly enciphered shows EASTNORTHEAST and
  BERLINCLOCK at their positions.
  - A mask must leave those 24 letters as they are.
  - Only the other 73 positions, or letters absent from the clues (D F G J M P Q U V W X Y Z), can be masked.
- **Reading B: the clues describe the final, unmasked English, at positions in the enciphered layer.**
  - A mask may change crib letters, as long as it keeps their positions.
  - A mask that changes length before position 63 breaks reading B unless the positions refer to the enciphered layer.

## 2. What masking does to the ledger's exact exclusions
**Under reading A, nothing changes.** Every exact check uses only the crib letters and their positions, so any mask
that leaves them intact is invisible to it.

**Under reading B, the result depends on how plaintext letters enter the equations:**
- **Some checks see plaintext letters only through their own free alphabet.** These are L90, L92, X115, and R102/R109
  with F = A. They use only the **equality pattern** of the crib letters, that is, which of them are the same letter.
  - They stay valid under any mask that keeps that pattern. That includes **every letter-for-letter bijection**:
    Atbash, a shift, or any respelling table that is one-to-one on the 13 crib letters.
- **Other checks put plaintext and ciphertext letters through the same alphabet.** These are Slidefair (X107, R108,
  X112) and R109 with F ∈ {B, AZ}. They depend on the letters themselves, like fixed-alphabet checks. Any mask that
  changes a crib letter voids them.
- **A mask that merges two crib letters** breaks even the first group. C → K is an example: both letters occur in
  BERLINCLOCK.
  - The merge adds an equality those checks do not assume. A check can then **wrongly exclude** the true setting,
    because it requires x(C) ≠ x(K).
  - This is a real gap in their stated scope.
  - The pairs at risk are those among E A S T N O R H B L I C K. Sound-based merges among them include C/K and I/E.
  - O/U and S/Z are safe, because U and Z do not occur in the clues.
- **Checks with fixed alphabets** (L03–L09, L49 and others) assume the published letters themselves. Any mask that
  changes a crib letter voids them under reading B.

**Recommendation.** Every future exact round should state its masking scope in one sentence:
- for checks of the first group: "valid under reading A, and under reading B for masks that keep the crib letters'
  equality pattern";
- for the others: "valid under reading A only".

## 3. Mechanisms
| # | Mechanism (all reversible or readable) | Clue-compatible? | Ciphertext-only observable | Ledger overlap | Testable how |
|---|---|---|---|---|---|
| M1 | **Respelling by sound with one-to-one letter swaps** (W↔V, J↔Y, F↔PH as one letter, and so on) | A and B | **None.** A free plaintext alphabet absorbs it, and a fixed alphabet makes it just another convention | L29, L45, L51, L69 (as spelling noise for the scorers) | Only through decryption: the solver's language model must allow it |
| M2 | **Respelling by sound with merges** (C/K → K, Z/S → S, double letters collapsed) | A, if the merged letters are not crib letters (Z/S is fine, C/K is not); B, with the caveat in §2 | None directly. A cipher with plaintext feedback (an autokey) carries the plaintext's smaller alphabet into its key, which weakens the R110-type repetition statistics a little | L45, L84 (edit costs) | Synthetic: the power of R110 and S105 on merged-alphabet plants |
| M3 | **Germanic or Dutch orthography** (L69: VIFTZ-type spellings, K for C, V for W, IJ for Y) | A (the clue words are already valid in that style); B | None through an in-place polyalphabetic cipher with a flat IC (K4's IC is near random) | L63, L64, L68, L69, L108 (German, Dutch and mixed models: no candidate) | Decryption with an orthography-aware model (L69's benchmark: 3/16 exact, against 0/16 baseline) |
| M4 | **Inserted fillers**: X as a full stop (K2, K3), nulls at word ends, a padding letter | A, if no filler falls on a clue position | None in place. It shifts positions only if the fillers are removed before reading, which is not reading A or B | L81 (bounded nulls), L104 (X punctuation, NOT USEFUL) | Already covered |
| M5 | **Telegraphese or abbreviation** (articles dropped, STOP, figures spelled out) | A and B | None directly. It lowers English-model scores of true text, a risk for every NO_SIGNAL | L29 (spelling sensitivity) | Synthetic: the recovery of S105 and the R59/R61 solvers on telegraphese plants |
| M6 | **Reversal** (of the whole text or of each word) before an in-place cipher | **No,** at the published positions. The enciphered layer would hold the clue words backwards, or at mirrored positions | — | — | Excluded by the clues as published |
| M7 | **A Hill or other polygraphic stage as the mask** | A only, in the exact sense of L61 | Through the cipher's polygraphic structure | L11, L61 (EXCL within scope) | Covered |

## 4. What is new and worth doing
1. **The scope sentence (§2) for exact rounds.** It costs nothing and closes a real gap in how scope is stated, which
   matters most for X115's proposed K4 run (P8) and for P6.
2. **A synthetic robustness check of the blind solvers against M2, M3 and M5,** with no K4 input:
   - S105 (R114's arms) and the R59/R61 running-key solvers;
   - on plants respelled by fixed, registered rule sets, such as L69's Dutch-like rules and a telegraphese rule set;
   - reported as the drop in ≥ 90 recovery against unmasked plants.

   This measures how much of R111's NO_SIGNAL, and of earlier ones, would survive Scheidt's "masking". It would be a
   new synthetic round, like R114.
3. **Nothing else here supports a new K4 round.** Most mechanisms have no ciphertext-only observable through an
   in-place cipher with K4's flat statistics, and the rest are covered (L61, L63, L81, L104, L108).

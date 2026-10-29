# Claude Code review of R44b–R48 (PRs #12–#17) and an integration plan, 29 Oct 2026

No K4 solution. Nothing was run on K4 except sealed exact feasibility checks using the 24 published letters. No
external checker.

## 1. Independent replications, all with code written separately from ChatGPT's

| Round | Claim | Replication (code in `r44/audit/`) | Agrees |
|---|---|---|---|
| R44b (#12) | 20/20 exact on holdout B | ChatGPT re-checked my outputs independently | yes |
| R45 (#13) | in-place Gromark-5 × 4,749 keyword alphabets × both orientations × ±: 0 feasible | `kw_exact_check.cpp`: **0 / 0**; controls HB_00 and HB_07 return exactly their true setting | yes |
| R46 (#14, #17) | four 24×8 rotations after substitution: two-free feasible 79 / 1,643 / 1,486 / 9,502; keyword 0 | `rot_exact_check.cpp` with routes from the repo's `strictblind/blind/routes.py`: **79 / 1,643 / 1,486 / 9,502, keyword 0**; route controls HB_05 (CCW/inv) and HB_14 (CW/fwd) recovered | yes, exactly |
| R47 (#15) | 1,135,348 Carter + K1–K3 windows; 585 two-free; 0 keyword | `rk_exact_check.cpp`: **1,135,348 windows; 585 two-free** (1,170 window-signs; with two free alphabets the sign is a relabelling); **0 keyword**; running-key controls in both orientations recovered | yes |
| R48 (#16) | literal third-party back-tableau stream: 0/52 even with two free alphabets | not replicated | — |

R48's source is not authenticated. I agree with ChatGPT's caveat: build nothing on it until its coordinates are
checked against primary photographs.

## 2. Scope checks the handoff asked for
- **Clue positions and order.** R46 places the 24 letters on the substitution output in plaintext order
  (`SUB[i] = CT[perm⁻¹[i]]`), with the key indexed by plaintext position. That is the correct reading of "substitute,
  then transpose" (`CT[j] = SUB[perm[j]]`), and it matches `strictblind`'s S_then_T. My independent route
  generation reproduced every count, so the routes are as declared.
- **Not covered by R46:**
  - transposition **before** substitution (T_then_S);
  - other grid sizes;
  - other key lengths or bases.
- **Vocabulary gap, now closed for the obvious words.** The 4,749 R44b alphabets come from common English words.
  **KRYPTOS, PALIMPSEST and ABSCISSA are not among them**, and neither are SANBORN, SCHEIDT, LANGLEY, TUTANKHAMUN
  or WELTZEITUHR. BERLIN (rank 5,084) and EGYPT and CARTER fall outside the top 5,000.
  - **Earlier coverage:** R40 and R42 (L134, L136) already covered the KRY/PAL/ABS alphabets in place.
  - **This audit's check:** an unregistered check (exact and deterministic; no tuning possible) ran the same three
    checks on 15 Kryptos-themed keywords (13 distinct alphabets): KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, SHADOW,
    EGYPT, CARTER, LANGLEY, SANBORN, SCHEIDT, ILLUSION, UNDERGROUND, MAGNETIC, POSITION, WELTZEITUHR.
  - **Result: 0 feasible K4 settings** in place (Gromark-5), with the Carter + K1–K3 running keys, and with all four
    24×8 rotations. Exclusions should still be stated for their exact vocabulary.
- **Duplicate text (L135).** The K1–K3 key file holds K3 twice. That duplicates windows only; it does not reduce
  coverage.

## 3. Recommended clean integration sequence (not executed: Tyler asked for no merges yet)
A local trial merge of `main` + #11, #12, #13, #14, #17, #15 and #16, in that order, has **no conflicts**.

1. **Close #2–#6.** They are superseded: their content reached `main` through #8.
2. **Label R43 as a failed prototype before anything reaches `main`.** Add a short `r43/README.md` saying the beam
   solver failed its gate and is kept as evidence (see `r44/REVIEW_PR11.md`). Do this on #11's branch or in the
   integration PR. The failed code is then preserved, not mistaken for working software.
3. **Integrate in one PR** (as #8 did): branch from `main`; merge #11 → #12 → #13 → #14 → #17 → #15 → #16; add the
   R43 label and ledger rows for R45–R48 if missing; run `strictblind/tests/run_all.sh`, `verify_all.sh` and the R44
   contract test; open one PR to `main`. After it merges, close #11–#17 as merged-through.
   - **Alternative:** merge the stack bottom-up, retargeting each PR to `main` as its base lands. This is more
     clicks and more CI runs, for the same result.
4. **Keep large raw outputs where they are.** Their hashes are recorded and the artifacts referenced. Nothing needs
   rewriting.

## 4. Recommended next bounded model (R49)
The pattern is now clear:
- **One free alphabet can be solved blind** when the key is known (R44b: 20/20 on fresh plants).
- **The obvious key sources are exactly excluded for K4**, both with a keyword alphabet and with these Kryptos
  keywords.
- **Two fully free alphabets remain unsolvable blind** (L138, L139).

The next round should change the **key source** and keep the solver that works.

- **Model:** one keyword alphabet, with the vocabulary declared up front as the 4,749 alphabets **plus** a
  Kryptos-themed list; the other alphabet free; in place or T_then_S.
- **Key families, fixed in advance:**
  - ciphertext-autokey with lags 1–20;
  - periodic keyword keys from the same vocabulary (length ≤ 10);
  - progressive keys;
  - Gromark with 6- and 7-digit primers and bases 5–26;
  - running keys from other named sources, each with an edition hash.
- **Step 1, exact screen (seconds to minutes per family):** the checks in `r44/audit/` drop every family with 0
  feasible settings.
- **Step 2, blind solve (only for survivors):** run the R44b solver on K4 without the 24 letters.
  - **Controls:** at least 16/20 planted messages for that exact family, plus shuffled nulls.
  - **Order:** freeze the full 97-letter output before comparing EASTNORTHEAST or BERLINCLOCK.
- **What a candidate needs:** it must read as language, come from the blind run, and re-encrypt exactly.
- **Research track in parallel:** a two-free-alphabet blind solver (word-level moves; L138, L139). Gate it on
  ≥ 16/20 planted messages before any use.

# R52 / R52b result (Claude Code, 31 Oct 2026; corrected 1 Nov 2026 after the owner review of PR #12)

**No K4 solution.** No external checker contacted.

> **LABEL: crib-conditioned exploratory research. Not evidence from ciphertext-only candidate generation.**
> - **The whole R52 → R52b pipeline is crib-conditioned.** `run_k4.sh` builds a mask from the 24 published letters at
>   their published positions. The exact screen used that mask to select the one key/route/alphabet setting that
>   R52b then decrypted.
> - **R52b withheld the clue letters from its solver, but that does not make the pipeline blind.** The setting it
>   decrypted had already been chosen with known K4 plaintext.
> - **Under the owner's rule (R53, 31 Oct 2026),** only the exact zero counts below count, and only as exclusions.
>   No part of R52 may seed a blind search.

## R52: exact screen (sealed; uses the 24 published letters)
- **Coverage:** 47 chain-addition families × all primers, 171,225,968 keys per route, × 9 route-orders × 4,761
  keyword alphabets × both signs × both orientations.
  - Families: base 10 with 4–8-digit primers; bases 5–26 with 4–5-digit primers.
  - Route-orders: in place; the four 24×8 rotations in both orders.
- **Controls:** 5/5 found their planted settings across bases, lengths, orders and orientations.
- **Cross-checks:**
  - The fast program equals the slow reference byte for byte (B10/b5, B7/b4, B13/b4).
  - B10/b5 reproduces L22, R46 and R50.
- **K4: one keyword-feasible setting** (a base-26 twin pair): primer 34DCA with sign − ≡ NMDEG with sign +;
  `R24x8/CCW/inv` S_then_T; plaintext alphabet `DECABFGHIJKLMNOPQRSTUVWXYZ`.
- **Every other family: 0.** Full counts are in `R52_RESULT.tsv`.

## R52b: blind test of that survivor (pre-registered, frozen at 74e4aa3 before comparison)
- **Method:** the R44b solver plus polish, given only the un-transposed K4 text and the key, with no clue letters;
  all 4,749 keyword alphabets enumerated.
- **Controls (same family):** 4/4 exact.
- **K4 blind output** (raw): `JIMICORORANREABLESDIRGRISERGARDOOSITDANGLELISKOUSSINCAIDSCHATOFTRULEFENTOVIEHASLEPKANOFERYONAUELR`
  - Plaintext alphabet chosen: `MERCHANTSBDFGIJKLOPQUVWXYZ`, not the survivor's alphabet.
  - Not English: quadgram score about −462, against −360 to −410 for real text.
- **Clue letters at 22–34 / 64–74: 1/24.**

## Conclusion (corrected 1 Nov 2026)
- **Exact exclusion, 46 of 47 families.** Every enumerated setting in them is incompatible with the 24 letters
  (crib-assisted, exact). Families:
  - base 10 with 4–8-digit primers;
  - bases 5–9 and 11–25 with 4- and 5-digit primers;
  - base 26 with 4-digit primers.

  Scope: × these 9 route-orders × this 4,761-alphabet vocabulary, keyword alphabet on one side.
- **B26/b5 is NOT excluded.** One crib-feasible setting remains: twin primers 34DCA(−) ≡ NMDEG(+), R24x8/CCW/inv,
  S_then_T, plaintext alphabet DECAB…, cipher alphabet free.
  - **R52b is negative evidence for that one setting, not a proof.** A single run of a heuristic solver produced
    non-English text with 1/24 clue letters.
  - **A heuristic failure cannot rule a setting out logically.** The search may simply have missed the right cipher
    alphabet.
  - Status of this setting: **WEAK / OPEN**.
- **Unknown-key gate not met.** R52b gave its solver the key, both for the 4 controls (their true key) and for K4
  (the crib-selected key).
  - That makes R52b a known-key solve. Four controls are also below the 16/20 bar the project requires for a gate.
  - R44b's 20/20 holdout is a real known-key benchmark (L140). It is not an unknown-key recovery, and R52 does not
    turn it into one.
- **Coincidental survivors are expected at this family size.** The B10/b8 family had 12 crib-feasible settings on
  K4.
- **Superseded wording (31 Oct):** "Chain-addition keys … × keyword alphabet × these routes are therefore excluded
  for K4: exactly for 46 families, and at the blind level for the one survivor." That overstated the result.

## Reproducibility (added 1 Nov 2026)
`python3 -I r52_claude/tests/test_r52.py` runs in CI (`.github/workflows/claude-r44-r52.yml`). It checks:
- the pre-registration and freeze hashes;
- that `alphabets.txt` and `routes.txt` are exactly the declared vocabulary and routes;
- that the fast and reference screens agree byte for byte and reproduce the frozen rows;
- 8/8 planted controls, made with an independent encryptor;
- the R52b replay: exact re-encryption and the post-freeze clue count of 1/24.

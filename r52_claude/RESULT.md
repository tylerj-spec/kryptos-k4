# R52 / R52b result (Claude Code, 31 Oct 2026)

**No K4 solution.** No external checker contacted.

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

## Conclusion
The survivor was a **coincidental crib-feasible setting**. Such coincidences are expected at this family size: the
B10/b8 control family had 12. Chain-addition keys (these bases and lengths) × keyword alphabet × these routes are
therefore excluded for K4: exactly for 46 families, and at the blind level for the one survivor.

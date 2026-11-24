# Construction-discovery shortlist (Claude Code, 24 Nov 2026)

Affected ledger IDs: none (planning). Rounds that follow add their own rows.
Validation: equivalence searches against `LEDGER.md`, `docs/CIPHER_TYPES_TESTED.md` §17, `r76/RESULT.md`,
`r77/HYPOTHESES.md` and `r85/DESIGN.md`, cited per item. No K4 computation was run for this note.
Independent review: NONE (planning; one model).

**Mandate.**
- Tyler, 24 Nov 2026: "Go for it & all necessary follow on actions until you've worked your way thru enough of the
  plan for review".
- The lane is the parallel construction-discovery item of `audit/reviews/POST_R96_NEXT_STEPS_20261123.md`. It asks for
  up to three hand-plausible 1990-era reversible mechanisms, each with:
  - an exact forward and inverse;
  - independent key provenance;
  - a G0 equivalence check;
  - a predicted ciphertext-only observation;
  - a sealed synthetic power test;
  - a stopping decision.

**Firewall.**
- Published plaintext letters never select, seed or rank a mechanism, key or alphabet list.
- They appear below only in exclusion reasoning, labelled crib-assisted, exactly as `r77` C1–C5 and `r85` §3 use them.
- The Berlin clock is not privileged.

## 1. Corrections found during the equivalence search
- **The charter's "R72's 26 sheet routes never run / R73 ON HOLD" (§1.3, §6.1) is stale.** R76 ran all 36 directed
  sheet routes (L166):
  - text routed, any repeating key up to period 24 (H2bX);
  - keyword keys scrambled by the routes (H2X);
  - R74's K1→K3→K2 sandwich on the routes (H2c).

  All were NO_SOLUTION, and `r76/RESULT.md` says this "settles R72's on-hold item". Nothing is left to run there in
  those forms.

## 2. Screened out (no round needed)
| Mechanism | Why | Kind of argument |
|---|---|---|
| Wheel and strip ciphers in direct form (Jefferson, M-94, M-138) | A letter enciphers to itself only at offset 0, which leaves the whole line in clear. K4 has S→S and K→K in different 25-letter lines | crib-assisted, by hand (`r77` C1, `r85` §3) |
| Reflecting rotor machines (Enigma type) | The reflector forbids self-encipherment | crib-assisted, by hand (`r85` §3) |
| Alberti disk with a few unannounced turns (one mixed alphabet, constant shift between turns) | Inside EASTNORTHEAST, N→Q and O→Q are adjacent, and T maps to three different letters. That forces a turn every few letters, so the family is no longer "a few turns". With many turns it is a general one-free-alphabet key, which has no exact check (L21) | crib-assisted, by hand (new) |
| Scrambled plaintext, then an in-place substitution | The clues bind the final step in place, so every in-place exclusion still applies (`r85` §5 #6) | logic |
| Two arbitrary Chaocipher wheels | Its mechanism was secret until 2010, so it is low on rubric question 4; the 29-letter crib gap loses the wheel state, so there is no exact check (`r85` §5 #4) | deferred |
| Two-rotor RX2-O | Solver line stopped (L186) | stopped |

## 3. The shortlist
### S1 (first): Slidefair with keyword alphabets, any key, as round R98
**Mechanism.** This is the ACA's digraphic use of a Vigenère-family tableau. Plaintext is taken in pairs (p1, p2).
- Above: the plain alphabet PA. Below: the alphabet CA, slid by the pair's key letter κ.
- p1 is found in one row and p2 in the other. The ciphertext is the two letters at the opposite corners of the
  rectangle.
- When p1 and p2 fall in the same column, the letters to their right are taken.
- **Variants:**
  - Vigenère or Variant slide (identical constraints), or Beaufort (the lower row reversed);
  - which plaintext letter is in which row;
  - which ciphertext letter is written first;
  - pair parity.
- Exact equations are in `r98/PREREGISTRATION.md`.
- **Source caveat.** The rule details come from the project's existing definition (`r77/HYPOTHESES.md` H10). The
  ACA's own page could not be fetched from this environment. Every ordering variant is enumerated, and the drop-one
  screen covers a different same-column rule at any one pair.

**Why it is a candidate.**
- It is a 1930s-onward ACA hand system, and the standard way to use a Vigenère chart as a "matrix" on pairs. Sanborn
  said Scheidt taught him "matrix codes" (as cited in `r77`; not re-verified here).
- It keeps the length and the in-place alignment, flattens letter counts, and can encipher a letter to itself.
- It is untested: `r77` H10 was proposed but never run, and C5 closed only the plain and KRYPTOS charts.

**Key provenance.** Any key, any period or none. The key cancels out of the exact check (§4).

**Alphabets:** R76's fixed, generic 77,229-alphabet tier (`r76/alphabets.py`):
- every 4–15-letter word of the R59 word model;
- R75's sculpture words;
- A–Z;
- each word in ascending, descending and ACA-block forms.

**G0 equivalence.**
- Not inside the Playfair family (L88), which is 25 letters and cannot self-encipher.
- Not inside in-place periodic tableaux: the pair coupling makes it digraphic.
- `r77` C5 is the AZ/KRYPTOS sub-case, closed by hand. Nothing else overlaps.

**Predicted ciphertext-only observation (weak, stated for the record).**
- With PA = CA = A and the Vigenère slide, IDX_A(c1) + IDX_A(c2) ≡ IDX_A(p1) + IDX_A(p2) for every pair, whatever
  the key.
- So ciphertext pair sums at the right parity inherit English's non-uniform pair-sum distribution under the right
  alphabet.
- With 48 pairs and 77,229 alphabets the look-elsewhere cost makes this weak. It is not used to select anything.

**Power test.** This is a type B exact round, so its "power" is checker correctness. It has a gate with:
- a forward-cipher brute-force oracle over the key;
- planted full-tier recoveries, including same-column and one-wrong-letter plants;
- a chance-rate measurement on shuffles.

**Stopping decision.**
- K4 EXCLUDED under EXACT and DROP: the family is closed for every key over the tier. Stop.
- Feasible settings for K4 and not for the shuffles: LEAD, counts only. A separately registered blind round is then
  the only route to a candidate.

### S2 (next): Condi-type plaintext autokey on one keyed alphabet, as R99 if S1 closes
**Mechanism.** C_i = A[A⁻¹(P_i) + s·(A⁻¹(P_{i−L}) + c)].
- Plain, cipher and feedback ranks all use the same keyword alphabet A.
- L is the lag (Condi is L = 1), the sign is s = ±1, and the constant c covers the starting and 1-based conventions.

**Why.** An ACA hand type; self-keying; flat counts.

**G0 still to do before registration.**
- L27/L58 closed autoclave with a free cipher alphabet but AZ/KRYPTOS plain and feedback ranks, so keyed ranks look
  new.
- L169's keyword + ciphertext-feedback families must be checked for overlap.

**Exact check:** consecutive crib letters give constraints that depend only on A; c cancels across them.

**Decision:** EXCLUDED closes it for every lag with ≥ 3 constraints; otherwise counts only.

### S3 (deferred): the same two mechanisms with free (arbitrary) alphabets
With PA and CA arbitrary permutations, the 11 pair constraints become satisfiable. So there is no exact check, and a
blind solver would face the L138 problem (two free alphabets, the main open gap). It is deferred until a type C
solver shows power on fresh controls.

## 4. Why S1's exact check decides every key (algebra; verified by brute force in the R98 gate)
Write F = IDX_PA(c_up) − IDX_PA(p_up) and H = IDX_CA(c_low) − IDX_CA(p_low) for one pair.
- **Vigenère/Variant slide:** F = −H in the normal case. In the same-column case, F = 1 and H = +1.
- **Beaufort slide:** F = H in the normal case. In the same-column case, F = 1 and H = −1.

κ does not appear.
- Each alignment has 11 published pairs, so a setting must satisfy 11 equations in PA and CA alone.
- **Chance rate:** about (1/26)¹¹ per (PA, CA, convention). Over 77,229² pairs × 16 conventions that is about 10⁻⁵
  expected chance passes in all.
- **Drop-one screen** (any one pair unconstrained; covers one wrong letter, or a different same-column rule, at one
  pair): about 10⁻⁴ expected.

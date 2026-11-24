# Construction-discovery lane: review point after R98 and R99 (Claude Code, 24 Nov 2026)

Affected ledger IDs: L187, L188 (summary only; each round has its own row and note).
Validation:
- R98: `r98/RESULT.md`, `audit/reviews/R98_RESULT.md`, PR #115 (merged after green CI, including a full
  201-input recount).
- R99: `r99/RESULT.md`, `audit/reviews/R99_RESULT.md`, with its own CI recount.

Independent review: NONE. One model did all of this. ChatGPT is the named reviewer for both rounds.

**Mandate.** Tyler, 24 Nov 2026: "Go for it & all necessary follow on actions until you've worked your way thru
enough of the plan for review". The lane is the parallel construction-discovery item of
`audit/reviews/POST_R96_NEXT_STEPS_20261123.md`. The rotor line had already stopped (L186), and the fresh gate is
blocked on throughput.

## What was done
| Step | Outcome |
|---|---|
| Shortlist and G0 (`CONSTRUCTION_SHORTLIST_20261124.md`) | Six mechanisms screened out with reasons. R72's sheet routes were found to be already settled by R76 (a stale charter item corrected). Three mechanisms kept: S1, S2, S3 |
| **R98 = S1, Slidefair with keyword alphabets, any key (L187)** | **EXCLUDED**: 0 of 95.4 billion settings fit, even with one pair set aside. 200 shuffles also 0 |
| **R99 = S2, K1/K2's keyed tableau with a plaintext autokey (Condi type) (L188)** | **EXCLUDED** at lags 1–23 and 34–47, and with one error at lags 1–23 and 36–45. Weak lags at chance; lags 27–29 and 53–96 undecidable |
| S3, the same mechanisms with free alphabets | **Deferred**, by the shortlist's own rule: no exact check exists, so it needs a type C solver that first shows power on fresh controls (the L138 two-free-alphabet gap) |

**Each round ran the full type-B protocol:**
1. pre-registration;
2. source hashes;
3. a synthetic gate with a brute-force oracle and plants;
4. a pushed gate freeze before any K4 input;
5. a single target run with 200 shuffles;
6. a pushed freeze before evaluation;
7. a second implementation;
8. CI recount.

R98 needed one amendment before its gate (V2 inputs halved for the CPU cap), and its pre-registration has a disclosed
setting-count slip.

## What this means
- **Two natural hand constructions are now closed** in their keyword-alphabet forms: the ACA's digraphic use of a
  Vigenère chart, and K1/K2's own tableau with a self-keying key.
- **The published letters still rule out every in-place keyword-alphabet family tested so far**, now including any
  key (R98) and self-keying keys (R99).
- **No candidate or lead arose.** Nothing was decoded, and no survivor or alphabet was carried forward.

## Choices for the reviewer and Tyler (not started)
1. **The third lane slot (up to three mechanisms were allowed).** The cheapest exact extension is R99 with separate
   alphabets: plaintext and feedback ranks in A, cipher ranks in B (a Quagmire I/II-type autokey).
   - The chain congruence separates into f(A) − g(B) ≡ a·c, so a hash join over 77,229² pairs with 26 values of c is
     exact, like R98's.
   - It needs its own G0 against L27/L58 (free cipher alphabet, AZ/KRYPTOS ranks).
2. **S3 (free alphabets).** This is the main open gap shared with L138. It needs a type C solver, built and gated on
   fresh synthetic controls first, and that is a multi-round effort. This is the step most likely to matter if K4 is
   a keyed-alphabet hand cipher with a non-dictionary alphabet.
3. **Other changing-alphabet ACA types** (`docs/CIPHER_TYPES_TESTED.md` §17 item 11): Ragbaby and Portax. Each needs
   its own G0 and exactness argument.
4. **The fresh gate for the rotor line** stays blocked until a structure-pruning method exists (R97 G0).

My recommendation:
- First, a different-model review of R98 and R99. Both are fast to replay: CI does it in minutes, and each round has
  a second implementation.
- Then choice 1, only if the reviewer agrees it is not already implied by L27/L58.
- Otherwise move to the S3 type C solver work order, which needs Tyler's approval as its own work order.

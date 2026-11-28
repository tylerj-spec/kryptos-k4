# F3: catalogue of non-repeating deterministic key generators not yet in the ledger (Claude Code, 28 Nov 2026; G0, desk only)

Affected ledger IDs: none. This is a planning catalogue: nothing is run on K4 and no row changes.

Validation:
- a ledger scan for key-generation coverage (L03–L05, L13, L15, L16, L18, L20, L22, L25, L36, L37, L39, L40, L48,
  L49, L72, L75–L79, L83, L90, L92, L94, L102, L106, L111, L122, L127, L129–L132, L134, L141, L143, L152, L153,
  L157, L165, L169, L176, L177, L181, L182, L191–L199);
- the equations for rank 1 were prototyped on synthetic data only (dev seeds 1151–1155; see `r115/PREREGISTRATION.md`).

Independent review: NONE (one model). Fallback task F3 of `audit/reviews/BATCH_WORK_ORDER_R102_R107.md` (authorized
at once).

## 1. What the ledger already covers
- **Periodic keys:**
  - fixed alphabets, in place (L03, L04), multiplied (L05);
  - sums of periodic keys (L36);
  - after transpositions (L06–L09, L41, L47, L48).
- **Progressive and stepped keys:**
  - fixed alphabets (L13);
  - affine progressive keys with free-alphabet keystreams (L16);
  - tableau stepping (L20);
  - drift and two-speed models (L48);
  - a stepped progressive Quagmire with **one** free alphabet (L177);
  - rotors (L176, L181, L182).
- **Linear recurrences mod 26:**
  - any affine recurrence of order 1–6 under 48 **fixed** conventions (L49);
  - base-26 lagged Fibonacci, L 2–8, with **one** free cipher alphabet (L15).
- **Chain addition in base 10 and other bases (Gromark and VIC-style):** L22, L72, L83, L94, L102, L122, L129–L132,
  L134, L141, L143 (47 families).
- **Given key sequences with both alphabets free:** L90, covering K1–K3 running keys, dates, coordinates, 2–4-digit
  primers, and K4 and K1 used cyclically.
- **Text running keys:** L16, L106, L111, L127, L152, L153.
- **Clock-derived numeric keys:** L25, L37, L39, L40, L75–L79.
- **Feedback, autokey and walking keys:** L18, L157, L165, L169, L191–L199.

## 2. Gaps worth a registered round (ranked by exact checkability and novelty)
| Rank | Family | Exact check | Overlap | Size |
|---|---|---|---|---|
| 1 | **An affine linear recurrence mod 26 of order L with BOTH alphabets free** (Quagmire IV type). It contains progressive keys, multiplicative congruential keys, Fibonacci-type keys, polynomial keys of degree below L, and periodic keys of period at most L | **X115**: for each coefficient vector, the crib equations are linear in the alphabet values, the key state and the constant. They are solved mod 2 and mod 13 separately, with R112's forced-collision rule | Fixed alphabets: L49. One free alphabet: L15, and L177 for progressive keys only. Both free: **none** | 26^L vectors; seconds per ciphertext at L ≤ 3, about 30 s at L 4 |
| 2 | **Decimal digits of a mathematical constant** (π, e, φ, √2, √3, ln 2) as shift keys, from any start offset up to 10,000, in either direction | Fixed conventions: the digit at every crib position must equal the implied key, so the check is strong. Two free alphabets: L90's oracle, which is WEAK here, because at L90's chance rate for uniform keys (4.7 × 10⁻⁴) about 56 of the 120,000 sequences would pass | none found | 120,000 sequences |
| 3 | **Order-2 nonlinear recurrences mod 26**, such as k_n = k_{n−1}·k_{n−2} or k_n = k_{n−1}² + c | Fixed conventions only: the implied key along the 13-letter crib run fixes or refutes each map | none | small |

**Not listed as gaps:**
- **Any first-order map k_n = f(k_{n−1}) on 26 key values.** The sequence is eventually periodic, with preperiod plus
  period at most 26. When the preperiod ends before the first crib, it is a periodic key (L03, L04). The rest has a
  low prior.
- **Recurrences mod 10 or in other bases:** the chain-addition rows cover the documented forms.
- **Polynomial keys:** these satisfy the recurrence with characteristic polynomial (x − 1)^L, so they fall under rank 1
  and L49.
- **Binary shift registers read out as letters:** these are not hand methods. Low prior.

## 3. Constraints and recommendation
- **Mode.** Any K4 work on ranks 1–3 is **crib-assisted**, exclusion-only and aggregate-only, like R108 and R109. Its
  results are conditional on the published letters being correct.
- **Rank 1 first, as R115.** R115 is synthetic only: structure, soundness on plants, a second implementation, and chance
  power by order.
  - In development, the chance exclusion rate falls with order: 1.00, 0.80, 0.18 and 0.20 at orders 1–4, on 6 random
    messages.
  - The K4 run would therefore close order 1 (which contains progressive keys with two free alphabets) and test most
    order-2 vectors. Orders 3 and above stay WEAK.
- **Proposal.** If R115 passes, propose the K4 run as **P8**, for approval together with P6.
- **Ranks 2 and 3** are cheap fixed-convention screens with a low prior. They are kept for later.

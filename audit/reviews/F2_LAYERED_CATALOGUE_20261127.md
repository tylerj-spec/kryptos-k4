# F2: catalogue of two-stage constructions not yet in the ledger (Claude Code, 27 Nov 2026; G0, desk only)

Affected ledger IDs: none. This is a planning catalogue: nothing is run and no row changes.

Validation:
- a ledger scan for layered coverage (L06–L09, L12, L21, L26, L36, L38, L41, L47, L48, L54–L57, L61, L81, L88, L94,
  L115, L118, L121, L127, L157, L161, L187–L201);
- the equations below follow the cipher definitions in `r98/slidefair98.py` and `r100/autokey100.py`.

Independent review: NONE (one model). Fallback task F2 of `audit/reviews/BATCH_WORK_ORDER_R102_R107.md` (authorized
at once).

## 1. What the ledger already covers
- **A transposition followed by periodic substitution:**
  - complete columnar (L06);
  - circular routes (L07);
  - double grids (L08);
  - folds (L09);
  - the 24-face drum (L38);
  - clock-keyword columnar (L41);
  - the 41,502 two-step rearrangements (L47, L54–L57);
  - keyword irregular columnar (L118, L121).
- **Gromark, running key, chain addition and autokey along routes:** L94, L115, L121, L122, L127 and L157. These are
  mostly with **fixed** alphabets.
- **Other combinations:** stacked periodic keys (L36); Hill masking (L61); Trifid (L12); 25-symbol squares, which are
  impossible with 26 letters (L88); bounded nulls (L81).
- **What R102–R113 added:** exact checks with **free** alphabets, for Slidefair (X107 and X112) and for the
  two-free-alphabet autokey (R102's test). So far these have been applied **in place** only.

## 2. Gaps worth a registered round (ranked by exact checkability and novelty)
| Rank | Construction | Encryption (inverse by reversing) | Exact check | Overlap | Size |
|---|---|---|---|---|---|
| 1 | **Route, then Slidefair with free alphabets** (periodic or any key, every same-column case) | ct = π(SF(pt)): Slidefair on plaintext pairs, then positions permuted by a route π | X112, with ciphertext letters read at π-mapped positions. Crib pairs stay plaintext pairs | None: Slidefair has been tested in place only | 26 undocumented K3-style routes (L161) × 2 orders × 768 cells ≈ 40,000 cells; seconds each, so minutes |
| 2 | **Slidefair with free alphabets, then a route** | ct = SF(π(pt)) | X112 on pairs of the **permuted** plaintext. Only crib letters that π places adjacently form pairs, so power is lower; report each route's number of crib pairs | None | as above |
| 3 | **Route, then the two-free-alphabet plaintext autokey** (F ∈ {A, B, AZ}) | ct = π(S3b(pt)) | R102's direct-pair test, with ciphertext read at π-mapped positions. Lags with crib equations are unchanged | L157 used fixed-alphabet autokeys along 10 R61 routes; free alphabets are new | 26 routes × 1,152 cells, with DFS caps as in R109 |
| 4 | **Bounded nulls, then Slidefair or S3b in place** | delete d positions, then decrypt | each deletion set shifts the crib positions; X112 or R102 per set | L81 covered other families only | d ≤ 1: 97 sets |

**Not listed as gaps:**
- Masking by Atbash, reversal or a fixed monoalphabetic stage: absorbed by free alphabets.
- Two periodic stages: L36.
- A running key with routes: L127.
- Fractionation into 25 symbols: L88.

## 3. Constraints on any such round
- **Routes.** Use only the **26 undocumented directed K3-style routes** of L161. R73 is on hold. Per L161, any run on
  them must be "explicitly exploratory, separately pre-registered, piloted".
  - Ranks 1–3 would therefore be **R73-class rounds**. They need Tyler's approval and a pilot.
  - Their exclusions would be conditional on the route list and on X112's or R102's stated assumptions.
- **Mode.** Crib-assisted, exclusion-only and aggregate-only, like R108 and R109, with shuffle controls and a gate
  (synthetic plants passed through each route).
- **Decision.** An all-cells exclusion would close "documented K3 method plus a free-alphabet digraphic or autokey
  stage" for K4. Surviving cells would stay OPEN. They are not evidence.

## 4. Recommendation
Rank 1 first: route then Slidefair, X112 per route, on synthetic data only, as a feasibility pilot of crib-pair
counts and power per route. If its power holds, propose the K4 round for approval together with P6 (X112 in place).

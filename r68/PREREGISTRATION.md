# R68 pre-registration (Claude Code, 5 Nov 2026): classic keyed ciphers whose key advances along a path through the carved text

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md` as clarified by
Tyler: the **algorithm reads only the ciphertext and generic models**, and the published letters are used only as a
check after everything is frozen and pushed. Tyler asked for this follow-up to R67 and authorised running it through to
K4 candidates.

## Why
- **The anomaly:** R65 and R67 established that K4's letters read along SNAKE_L carry structure that neither shuffles
  nor six structured cipher families reproduce. SNAKE_L reads the 4+31+31+31 engraved rows in alternating directions.
  R65b showed it is not a German running key.
- **The ciphers not yet tried on paths:** the classic keyed ciphers a 1989 hand cipher would use, whose key advances
  letter by letter along such a path.
- **Sanborn's wording:** Sanborn stated his clues as carved letters decoding to plaintext letters ("NYPVTT, letters 64–69,
  decode to BERLIN"). Taken literally, each carved letter decodes in place. That fits a cipher whose **key** follows the
  path while each letter stays where it is carved (model M2 below). The R61/R64 transposition model (M1) puts the
  published letters at plaintext positions instead. R68 tests both.

## Hypotheses (exactly what is tested)
- **Paths:** the carved order (ID) and the 10 frozen R61 routes (`r61/routes.txt`). For a path perm, the path-order text
  Y satisfies CT[j] = Y[perm[j]].
- **Models:**
  - **M1** (substitute, then transpose; R61/R64): the plaintext is in path order. Published letters at path-order positions
    21–33 and 63–73.
  - **M2** (position-aligned; key along the path): carved letter j is enciphered in place at path step perm[j]:
    CT[j] = E(P[j], k_{perm[j]}). The plaintext is in carved order, and the published letters sit at carved positions
    21–33 and 63–73, literally as Sanborn stated them.
  - For ID, M1 = M2 = in place.
- **Conventions (12):** plaintext alphabet Ap and ciphertext alphabet Ac each AZ or KRYPTOS, with op VIG (y = x + k),
  BEAU (y = k − x) or VARB (y = x − k), where x = Ap⁻¹(p), y = Ac⁻¹(c).
- **Families** (k_t = shift at path step t):

  | Family | Key | Range |
  |---|---|---|
  | PER | periodic shifts s[t mod p] | p = 1–20 |
  | GRO | Gromark: 5-digit primer, d_t = d_{t−5} + d_{t−4} mod 10 | all 100,000 primers |
  | CTAK | ciphertext autokey, k_t = Ac⁻¹(Y[t−L]), free primer for t < L | L = 1–24 |
  | PTAK | plaintext autokey, k_t = Ap⁻¹(Q[t−L]), free primer for t < L | L = 1–24 |

## Blind pipeline (frozen: `r68/blind/run.py`, `r68/blind/keyed_solve.cpp`)
- **Rows:** for each ciphertext, all 21 (path, model) rows (ID once, 10 routes × 2 models) are solved under every family,
  convention and parameter.
- **Search:**
  - **PER:** coordinate ascent, 6 seeded restarts.
  - **GRO:** exhaustive over all 100,000 primers.
  - **CTAK and PTAK:** coordinate ascent over the primer (PTAK with 6 seeded restarts).
  - **Scoring:** the order-4 slice of the R59 English model during search; every candidate rescored with the order-6
    model + 1 × the R59 word score (the total).
- **Answer per family:** the best total over rows, conventions and parameters.
- **Raw evidence:** every row's best per family and convention (21 × 48 per ciphertext) is kept in `work/` and hashed.
- **No tuning after this file is committed.**

DEVELOPMENT_RECORD_PLACEHOLDER

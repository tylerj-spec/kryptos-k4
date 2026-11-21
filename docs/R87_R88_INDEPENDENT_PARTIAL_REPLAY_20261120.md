# Independent partial replay: R87 and R88 exact in-place exclusions (20 Nov 2026)

**Reviewer:** ChatGPT GPT-6 (different model than the Claude Code builder). **Review scope: PARTIAL.** Independent mathematical re-derivation and independent JavaScript constraint checker, not a full source-code or execution-pipeline audit. No ledger row promoted; no existing result changed. No K4 plaintext candidate/key was generated. Published plaintext letters entered only this **post-freeze structural audit** of previously frozen R87/R88 work; not any blind solver.

## Independent equations
Let i count from zero and K4 ciphertext be C. Let P_i be one of the previously published plaintext letters where known. The review uses those 24 facts **only for feasibility rejection**, in a separate read-only analysis after R87/R88's published blind output freezes.

**R87 (RX):** for all choices of input and output alphabets E_in, E_out from {AZ,KRYPTOS,PALIMPSEST,ABSCISSA}, d in {-1,1}, n in 1..96, let s_i=d*floor(i/n). Every released position implies the free rotor wiring W maps

`(index_Ein(P_i)+s_i) mod 26` → `(index_Eout(C_i)+s_i) mod 26`.

An unconstrained **single permutation** W exists iff equal inputs correspond to equal outputs **and** unequal inputs correspond to unequal outputs, for every pair of released positions. No explicit key W needs to be constructed, and no plaintext is deciphered.

**R88 (RQ):** for fixed alphabet A in the same set, side PA or CA, advancing step d in 1..25, n in 1..96:
- PA free: plain letter P_i must map to index `(index_A(C_i)-d*floor(i/n)) mod 26`.
- CA free: input index `(index_A(P_i)+d*floor(i/n)) mod 26` must map to ciphertext letter C_i.
Exactly the same partial-bijection consistency decides whether some permutation exists.

## A different, direct one-error test
Instead of implementing a new decryption function, the checker forms **all unordered pairs** of the 24 published equations and marks a conflict when one side has equal symbols and the other does not. Full feasibility means zero conflicts. To decide whether *dropping a single released equation* can repair a setting, maintain a 24-bit mask initially set to all ones and, for each inconsistent pair (a,b), intersect it with `(1<<a)|(1<<b)`. If this intersection is empty, there is **no** single released position that could eliminate every contradiction. If nonempty, dropping any set-bit position is sufficient. The test is independent from the repository Python checker's 24 separate rescans.

The checker used the original 97-letter ciphertext with the two published plaintext spans in their reported zero-based positions (21–33 and 63–73). The masks were evaluated directly; no key was fitted or candidate text emitted.

| Scope | Exact feasible structural settings | Feasible with any one released equation dropped | Consistent one-drop positions |
|---|---:|---:|---:|
| R87 | **0 / 3,072** | **0 / 3,072** | 0 / 24 |
| R88 | **0 / 19,200** | **0 / 19,200** | 0 / 24 |

These counts **agree** with the frozen R87/R88 reports in `r87/RESULT.md` and `r88/RESULT.md` within their specified scope. They are **not a broad exclusion of all rotors, all Quagmire ciphers, or any cipher with extra layers.**

## Independent synthetic controls
Using a fresh deterministic xorshift32 random generator (seed 0x8742c563), construct for **each** family 256 random 97-symbol plaintexts, random free 26-letter permutation, random allowed fixed alphabet/step/period/side, and an independently coded forward encryptor:
- 256 / 256 R87 synthetic true settings satisfy partial-bijection feasibility.
- 256 / 256 R88 synthetic true settings satisfy partial-bijection feasibility.
- 256 / 256 in each family keep a feasible witness when one **plaintext** symbol at a released position is corrupted and its equation is set aside.
- 256 / 256 in each family keep a feasible witness when one **ciphertext** symbol at a released position is corrupted and its equation is set aside.

These synthetic tests exercise the 97-character formulas and drop-one integrity, but are **not exhaustive toy-key enumeration or a full independent re-run of blind solvers/100 nulls**.

## Scope, status and next steps
- **Independent review: PARTIAL — ChatGPT GPT-6.** No G4 ledger promotion. The R87/R88 internal independent Python checker and GitHub CI checks are separate evidence; no source-code control-flow audit or resource-budget replay was performed in this review.
- R87 direct one-rotor with contact alphabets AZ/KRY/PAL/ABS, d ±1, n1–96 is blocked under published alignment assumptions. A different rotor state rule, multiple coupled rotors, another contact numbering, or an intervening transposition is *not* blocked here.
- R88 one free alphabet plus a fixed AZ/KRY/PAL/ABS side, constant key advance step1–25 every n1–96 is blocked under its assumptions. A different free/fixed alphabet, irregular or state-driven steps, two independent free alphabets or extra layer is *not* blocked here.
- The exact paper check uses released K4 positions; to preserve the owner's blind-only rule, these findings **must not be used as K4 key candidates, initialization settings or plaintext-fitting feedback** for the proposed R89 search. They can justify not repeating an already-tested method.
- For formal promotion: independent toy exhaustive test of implementation, replay all K4 and null settings with the original frozen input hashes, check source/result hashes and the complete prior exposure chain, and separately sign findings in `audit/reviews/`.

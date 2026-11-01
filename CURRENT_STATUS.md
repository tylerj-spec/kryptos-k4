# Current K4 research status (31 October 2026)

**No independently verified K4 solution. Nothing was submitted to an external verifier.**

## Merged work

- R49 (PR #19): previously reconstructed Berlin World Clock 24-face chart preserved with provenance/uncertainty; **not** authenticated as a K4 key.
- R53 (PR #23): hard ciphertext-only / freeze-before-reveal K4 input firewall; the Caesar solver is **only a pipeline smoke test**.
- R54 (PR #24): isolated ciphertext-only cipher-family fingerprints. IC is **0.0360824742** for the original 97-character ciphertext and all 26 letters occur. The best lag-7 signal has corrected p ≈ 0.149; period-column p ≈ 0.958. No cipher, key, or plaintext is identified.

## Preserved earlier work in this branch

- R43: **failed** word-beam solver, retained as an algebraic audit and negative result. Never use for K4 plaintext recovery.
- R44b: **20/20 exact** controlled blind recovery of 97-letter English messages *given the true key*, with independent forward-re-encryption witnesses. This is a valid **known-key** alphabet solver, **not** an unknown-key method.

## Not suitable as independent K4 evidence

- Claude's later R52/R52b branch: used confirmed K4 letters/positions to **choose a key/route** before a separated final solver ran. Therefore its selection pipeline is **crib-conditioned**, even though the final run omitted those letters; its 1/24 K4 output match and four known-key plants do **not** exclude a broad cipher family.
- Other historical finite-family postfreeze clue screens (R40G, R45–R51) may remain archival mathematical exclusions within their exact scopes but cannot seed a new ciphertext-only key search.

## Mandatory next steps

1. Specify reversible cipher/masking mechanisms and independently sourced key hypotheses **without K4 known letters**.
2. Demonstrate fully blind 97-letter recovery on at least 16/20 **fresh hidden-plaintext, hidden-key** encrypted controls for the exact method and key-search procedure; include proper null/false-positive calibration and independently verify every forward-encryption witness.
3. Run the original 97-letter ciphertext only in isolation; freeze full outputs and algorithm/key metadata; independently evaluate K4 published words and positions only **after** the freeze.
4. Do not tune on failed known-letter results. Document prior exposure of hypotheses and rerun on genuinely new control families before considering another K4 attempt.

Canonical owner rule: `r53/BLIND_RULES.md`.

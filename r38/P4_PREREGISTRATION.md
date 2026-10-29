# R38 P4 — Canonical ACA Gromark columnar-keyed alphabets (strict-blind)

Protocol frozen before any K4 blind search. Its source is the American Cryptogram Association Gromark instructions: https://www.cryptogram.org/downloads/aca.info/ciphers/Gromark.pdf. The independent published ENIGMA example and two unrelated English planted controls must pass before P4. Keyword-prefixed R37 and actual ACA columnar-keyed R38 are separate hypothesized constructions.

## Exact cipher family

- Original K4 97-character ciphertext, SHA256 with trailing newline `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`. Never start from K4 plaintext or known clue substrings.
- Route: identity, no transposition; letter-to-letter encrypted.
- Numerical key: `CHAINACA base,5`, recurrence `k[i]=(k[i-5]+k[i-4])%base`, all `base**5` primers for exactly bases **[5,10,12,26]**.
- Plain alphabet and cipher alphabet selected independently from 4 fixed 26-letter permutations:
  - AZ: alphabetic;
  - KRY: `KAHUOFNPDLXRBIVSGQTEMZYCJW` (ACA columnar keyed from `KRYPTOS`);
  - PAL: `ACOZEJWIFRLDQMGUPBNYSHVTKX` (from `PALIMPSEST`);
  - ABS: `ADJOUZBEKPVCGMRXIHNTYSFLQW` (from `ABSCISSA`).
- Operation: VIG, BEAU, VARB, three alternatives; 4×4×3=**48** conventions per primer.
- Total original K4 settings: **587,199,984**. Entire family must be counted exactly; early exit not valid.
- Blind ranking: original 97-letter quadgram model and 100 top plaintexts per base, no public K4 clue inputs or optimization.

## Controls and null

- For each base, 2 independently planted messages from `r35/controls.json` indices 2 and 3; each 97 characters and without any public K4 clue phrase. Encrypted using a random route, selected primer and one of the four historical alphabets on each side; seeds `38000+base` and `38100+base`. The sealed plant truth must never enter the blind scanner.
- For each base, a non-planted seed-38200 shuffled-K4 ciphertext null retaining original letter counts.
- 16 blind scans (4 K4, 8 plants, 4 nulls); 2,348,799,936 decryptions across all four kinds.

## Exact chronological commitment

1. Commit preregistration and SHA-256 lock on all inputs, generators and validators **before** any scan.
2. Make K4, shuffled null and cipher-only planted controls.
3. Run blind decryption, hash all source, scorer, key, routes, ciphertexts, outputs and compiled scanner, commit and push freeze to GitHub.
4. Only then independently re-encrypt all frozen rows and count the 24 published K4 plaintext letters over all settings. Check 8/8 controls rank #1.
5. 24/24 after freeze is *unverified candidate*, requiring complete natural-language 97-letter text and independent derivation. 0 full24 with successful plants excludes **only** this declared ACA Gromark fixed-alphabet direct family.
6. Shuffled null comparisons descriptive, not formal significance with one null. No tuning after seeing scores, no external verifier.

This protocol explicitly does not infer results for unknown or differently constructed alphabets, other key lengths, or multi-stage cipher designs.

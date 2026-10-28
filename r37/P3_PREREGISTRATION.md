# R37 P3 — Direct Gromark with historically grounded fixed keyword alphabets

Pre-registered, locked before first P3 K4 scan. Motivated by the K1/K2 keywords **PALIMPSEST** and **ABSCISSA**. These are proposed *key alphabets*, not crib text, and do not imply Sanborn used them for K4.

## Model (fixed before search)

- Original K4 97-character ciphertext: SHA256 with final newline `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Route: **identity only** (direct letter-to-letter encryption).
- Key: `CHAINALPH base,5` over each base in exactly `[5, 10, 12, 26]`, full set of `base**5` five-symbol primers. Expansion recurrence `k[i] = (k[i-5] + k[i-4]) % base`. All symbols are numeric ranks in the chosen base; no guesses constructed from plaintext.
- Alphabets (all are complete 26-letter permutations): `AZ` (alphabetic), `KRY` (KRYPTOS alphabet), `PAL` (PALIMPSEST deduplicated followed by unused A–Z letters), `ABS` (ABSCISSA deduplicated followed by unused A–Z letters). All four allowed independently as plaintext and ciphertext alphabets.
- Operations: Vigenère, Beaufort, variant Beaufort, 3 choices. The 4×4×3 = **48** combinations are declared *before* scanning. No unknown alphabet fitting, no clue constraints in blind code.
- Total expected original-K4 settings: `48 × (5**5+10**5+12**5+26**5) = 587,199,984`.
- Blind score: existing unmodified quadgrams, full 97 letters, top 100 per base, no post-hoc tuning.

## Test controls

- Each of four bases gets two independent planted controls drawn as the first 97 letters of original paragraphs in `r35/controls.json`, indices 2 and 3 (contain neither public K4 known-plaintext phrase). Randomly select 1 of 48 fixed-alphabet conventions and one primer, seeds `37000+base` and `37100+base`. Exact settings retained in sealed truth outside the blind scanner.
- Identical shuffled-ciphertext null control for every base, seed **37200**, preserving original 97-letter ciphertext histogram.
- Each base runs the identical scanner for K4, 2 plants, and null. Overall **2,348,799,936** candidate decryptions across four ciphertexts, plus separate independent whole-family K4 clue-count checks after freeze.
- All planted controls must rank #1 for any family exclusion. If not, mark inconclusive and fix the method with a *new* pre-registration, not by re-tuning the current search.

## Freeze and reveal

- Commit the preregistration and SHA256 protocol before any cipher search.
- Run only original K4, separate cipher-only plants, and null through blind scanner.
- Freeze hashes of original inputs, binary, source, scoring model, routes, tags and all outputs, then COMMIT AND PUSH blind freeze before revealing any known K4 plaintext.
- Sealed checker independently encrypts each frozen row and checks equality against original ciphertext. Independently count all 24 published K4 plaintext letters across all settings; never use them for blind ranking.
- A frozen row with 24/24 is a candidate, NOT a solved K4 unless all 97 form meaningful text with independently reproducible key/method. No full24 + all successful controls => exclusion strictly limited to this precise direct fixed-alphabet family, **not** general Gromark or unknown alphabets.
- A single null is a descriptive negative control, not a formal significance test. Report all scores and all raw candidate text without editing.
- No interaction with third-party external K4 verifier.

The goal is rigorous elimination or a reproducible candidate, not retrofitting gibberish to known plaintext.

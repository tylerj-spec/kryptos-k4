# R36 P2: direct non-decimal five-digit Gromark family (strict-blind)

Committed before any K4 scan. The five-digit Gromark proposal and possible non-decimal bases are grounded in Richard Bean, *Cryptodiagnosis of Kryptos K4*, HistoCrypt 2021, DOI 10.3384/ecp183153. Sanborn's later Berlin-clock clarification may weaken clock-specific base hypotheses; this is a bounded historical hypothesis, not evidence of the actual mechanism.

## Model fixed before search

- Exactly original 97-letter K4 ciphertext, SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3` including its final newline.
- **No transposition**: identity route only; matches Bean's suggested one-to-one letter mapping.
- `CHAINBASE base,5` with recurrence `k[i] = (k[i-5] + k[i-4]) modulo base`; all base^5 primers, with initial five symbols represented as 0..9,A..P.
- Predeclared bases `[3,4,5,6,7,8,9,10,11,12,16,20,26]`. These have 16,760,627 primers total, or 201,127,524 fixed-convention settings for the original K4.
- Alphabet/cipher choices: plain A–Z or KRYPTOS, cipher A–Z or KRYPTOS, and three operations VIG, BEAU, VARB (12 total). Key digits count as numeric shifts in these 26-letter alphabets; modulo for expansion is the declared non-decimal base. No keyword-fitting, masks, or clue-based constraints in blind search.
- Rank with the unchanged English quadgram table; retain top 100 per base.
- No adaptive candidate criteria or tuning after reveal.

## Pre-planted controls and null

- Two original English control messages per base from `r35/controls.json` indices 2 and 3. They do **not** contain K4's published clue phrases and are encrypted under random, seeded choices from the exact family being scanned, not passed as plaintext to the scanner.
- Control seeds: `36200+base` and `36300+base`. The sealed generator records exact settings before scanning.
- Null ciphertext: `random.Random(36404)` shuffle of the original ciphertext, preserving each letter's frequency. Identical null message scanned under each base.
- Total 52 blind runs: K4, plant A, plant B, and null for each of 13 bases. Total planned decryptions 804,510,096, not counting independent post-freeze evaluation.

## Freeze, reveal, interpretation

1. Hash and commit this preregistration and the experiment construction scripts **before** any scan.
2. Run only the ciphertext + declared numeric key + route + fixed scoring table.
3. Hash and commit original ciphertext, all controls' ciphertext, null, manifest, top outputs, scripts, executable, route file and quadgrams before checking any known K4 letters.
4. Independently forward re-encrypt every frozen top-100 row. Controls must recover at rank #1 per base.
5. Only after freeze, independently count all 24 released letters across every setting for each base.
6. If a full 24/24 row exists, report as an unverified candidate needing meaningful complete English and independent replay; never claim a solution solely from the two exposed phrases.
7. If no full 24/24 and controls pass, exclude only the exact fixed-alphabet direct Gromark models at the declared bases, length and operations. Unknown plaintext/cipher alphabets, other primer lengths, altered recurrences, or combinations with transposition remain open.
8. One null is descriptive only, not a calibrated significance estimate.

Do not contact an external K4 verifier.

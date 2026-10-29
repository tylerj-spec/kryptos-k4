# R35 P1: Carter running key with K3-shaped opposite-direction double rotations

This protocol is committed before any P1 scan or reveal. P1 is a distinct bounded hypothesis from P0, which already produced a negative result for the K1–K3 plaintext key source.

## Fixed hypothesis

- Original K4 ciphertext, exactly 97 upper-case letters followed by newline, SHA-256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Running-key source: the project's archived Carter and Mace book OCR normalized as `r34/carter_az.txt`, SHA-256 `6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0`.
- Route family: two consecutive rotations in OPPOSITE directions, stage 1 widths `23,24,25` and stage 2 widths `7,8,9`, chosen because K3's known geometry uses widths near 24 and 8. Per pair: CW-CCW or CCW-CW, forward or inverse, and two route/substitution orders. Exactly 72 route-orders.
- Every 97-letter key window in the book, forward/reversed, alphabet numbering A–Z/KRYPTOS. Plain alphabet AZ/KRY, cipher AZ/KRY, VIG/BEAU/VARB = 12 conventions. All settings searched, no information from known plaintext used.
- Blind ranking is unchanged quadgrams, best 100 rows overall, top score per route-order.
- Exactly `72 × (282924 - 97 + 1) × 4 × 12 = 977453568` K4 settings.

## Validity controls and null

- Two independently written 97-letter English controls from `r35/controls.json` indices 2 and 3, randomly encrypted using exact declared method (seeds 35011 and 35012), without public K4 clue phrases.
- Shuffled original ciphertext null (seed 35013), same histogram and length; scored with identical blind pipeline. One null is a diagnostic only.
- Four scans (K4, both planted controls and null), total 3,909,814,272 decryptions.

## Temporal seal and decision

1. Hash and commit preregistration and plant-generation scripts before running any scan.
2. Create original K4/input key file, routes, two planted ciphertexts and null.
3. Run the blind scanner without clues, freeze hashes, commit freeze on GitHub.
4. Only AFTER freeze is recorded, run sealed independent re-encryptions and whole-family 24-letter matching. The two plants must rank #1.
5. A full 24/24 match is a candidate only; require meaningful complete text, independent validation and a separately justified key. Otherwise no candidate and exclusion only of this exact key/route/12 fixed convention family.
6. No external checker or retroactive tuning.

This is a historically motivated *testable* family, not evidence Sanborn used the cited book or rotation directions.

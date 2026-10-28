# strictblind: the shared strict-blind harness (from R34)

One scanner, one route maker, one reveal, one whole-family counter, and tests. New experiments write a manifest and a
pre-registration; they do **not** copy code. (R31 asked for exactly this, with a contract enforced like CI.)

## The contract
- **`blind/`** reads only:
  - the ciphertext;
  - a key source (a text file, or a chain-addition length);
  - a route file;
  - the quadgram table.
  It contains no clue words, clue positions or masks, and imports only the Python standard library.
  `tests/test_contract.py` enforces this; it is checked to catch planted violations.
- **Outputs** are top-100 lists (by English quadgram score) and best scores per route. `blind/experiment.py` hashes
  every output, ciphertext and the manifest into `FROZEN.sha256`. **Commit that before running anything in
  `sealed/`.**
- **`sealed/`** (the only code holding the known letters):
  - `reveal.py` re-encrypts every frozen row with an encryptor written separately from the scanner, ranks each
    planted truth, and counts K4 clue matches;
  - `whole_family.py` counts clue matches over **every** setting, with chance tails.

## Families covered
- **Fixed alphabets:** plaintext and cipher alphabet each A–Z or KRYPTOS × Vigenère / Beaufort / variant
  Beaufort, so 12 conventions.
- **Route-orders:** `ID`, `S_then_T` (substitute, then rearrange) or `T_then_S` (rearrange, then substitute).
- **Keys:**
  - `TEXT file`: every 97-letter window, forward and reversed, numbered A–Z or KRYPTOS;
  - `CHAIN b`: b-digit chain addition, all primers, 2 ≤ b ≤ 8.
- **Routes** (`blind/routes.py`), byte-identical to the R32/R33 route files:
  - `r27`: identity plus K3-style routes;
  - `rot LO HI`: every double rotation;
  - `columnar WORDS [--canonical]`: keyword irregular columnar.

Speed: about 15–20 million full 97-letter decryptions per second on 4 cores; keys are generated on the fly.

## Running an experiment
```bash
E=r34/exp1                                   # experiment directory with routes, ciphertexts, key texts
python3 -I strictblind/blind/routes.py columnar KRYPTOS,PALIMPSEST,ABSCISSA $E/routes.txt
python3 -I strictblind/sealed/make_plants.py $E PLANT_A routes.txt TEXT carter_az.txt 0 34001   # plants FIRST
# write $E/manifest.json: {"runs": [{"tag", "ct", "routes", "key": [kind, arg], "label"}, ...]}
python3 -I strictblind/blind/experiment.py $E            # blind scans + FROZEN.sha256
git add $E && git commit -m "freeze"                     # freeze is committed before any reveal
python3 -I strictblind/sealed/reveal.py $E               # REVEAL.json
python3 -I strictblind/sealed/whole_family.py $E         # WHOLE_FAMILY.json
```

## Tests (about 12 s)
`bash strictblind/tests/run_all.sh`:
- **contract:** the rules above;
- **round trip:** 6 plants of 2 key kinds, all ranked #1, with exact whole-family counts;
- **regression:** byte-identical to R32's frozen `K4_F1_G5.tsv`.

Also checked once (27 s): byte-identical to R33's frozen `K4_CARTER.tsv`, and the whole-family histogram identical
to R33's (325,817,856 settings).

## Limits
Fixed alphabets only. Two unknown alphabets cannot be searched blind yet: no blind solver has passed a planted gate
(ledger L109, L112, L116).

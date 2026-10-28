# Kryptos K4 research workspace

**No verified K4 solution exists here.** No submissions to any external checker without Tyler's go-ahead.

## Standard for any claimed solution (adopted R31)
1. **Blind discovery:** the search reads only the original 97-letter ciphertext, a declared key source and a
   language model. It never sees the known words (EASTNORTHEAST at 22–34, BERLINCLOCK at 64–74).
2. **Freeze:** outputs are hashed (and committed) before anything checks them.
3. **Reveal:** a separate checker re-encrypts each output forward to the ciphertext and counts how many of the 24
   known letters it has. A solution must have all 24 *and* read as language.
4. **Planted controls:** hidden test messages are run through the identical search and must come out #1.

Searches that use the known words to fill in unknown alphabets are labelled **crib-assisted**. Their fitted text
is never evidence.

## Where things are
- **`LEDGER.md`:** the canonical record of every model tested (L01–L119+).
- **`HANDOFF.md`, `AUDIT_NOTES.md`:** ChatGPT's R33 handoff (copies of `r33/`).
- **`k4kit/`:** the toolkit.
  - `CLAUDE.md`: the working rules.
  - `tools/`: oracle, solvers, validation.
  - `r30/`: R30 crib-assisted searches and the Carter book test.
  - `r32/`: R32 strict-blind scans.
  - `handoffs/`: every Claude brief.
- **`r33/`:** ChatGPT's R33 strict-blind keyword-columnar scans, self-contained with data. Replay with
  `bash verify_all.sh`.
- **`strictblind/`:** the shared strict-blind harness (one scanner, route makers, key sources, plants, freeze,
  reveal) that new rounds should use instead of copying code (from R34).
- **`archive/`:** ChatGPT packets and sources, kept unchanged for audit.
  - `archive/sources/`: the Carter & Mace 1923 vol. I OCR text.
- **`R32_handoff_original.zip`, `R33_DELIVERY_MANIFEST.sha256`:** R33's verbatim copy of the R32 zip, and R33's
  checksum snapshot of the files as delivered. Some of those files, such as `README.md` and `LEDGER.md`, have since
  been edited on purpose.

## Build and validate the toolkit (about 30 s)

```bash
cd k4kit
g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
python3 tools/validate.py
```

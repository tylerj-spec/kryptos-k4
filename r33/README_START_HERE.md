# R33 reproducibility / strict-blind instructions

A. The original user-provided `R32_handoff.zip` is preserved at the package root. Its blind scanner is here under `r33/blind/scan_fixed.cpp` (same SHA-256 301766e7...). `r33/data/` contains the score table and K1–K3 plaintext from the preceding R30 historical bundle; `r33/runs/carter_az.txt` is the unchanged R31/R32 1923 Carter OCR normalization (sha256 6761a507...). R32 ZIP by itself omitted these dependencies and its 5,000-route file.

B. **Review existing R33 saved results quickly**:

```sh
cd R33_ChatGPT/r33
sha256sum -c PROTOCOL.sha256
cd runs && sha256sum -c FROZEN.sha256
```

C. **Independent saved-output audit** (unpack R32 into a separate sandbox folder, never run arbitrary code unreviewed):

```sh
unzip R32_handoff.zip -d upstream_R32
python upstream_R32/k4kit/r32/blind/make_routes.py
python r33/sealed/independent_audit.py --r32 upstream_R32/k4kit --r33 r33 --data r33/data
```

This independently re-encrypts and re-scores the **saved** 1,200 R32 + 400 R33 rows, and rechecks freeze hashes. The R32 whole-family 7.10 billion settings are not repeated by this audit.

D. **Fresh complete ciphertext-only search** (C++17 compiler and Python 3; can take several minutes):

```sh
cd r33
python blind/col_routes.py
python sealed/make_plants.py # creates calibration ciphertexts, not K4 cribs
c++ -std=c++17 -O3 blind/scan_fixed.cpp -o runs/scan_fixed
bash blind/run_blind.sh
```

`blind/run_blind.sh` reads only `runs/k4_ciphertext.txt`, the numeric key/book sources, and route definitions. The known plaintext clues live **only** under sealed/ and ledger material and are never loaded by blind/. Run **postfreeze** whole-family checks with:

```sh
c++ -std=c++17 -O3 sealed/whole_family.cpp -o sealed/whole_family
# See results/whole_g5_*.txt and whole_carter_*.txt for precomputed 4-way partition results.
python sealed/merge_histograms.py
```

No keys or results were pushed to GitHub. No paid-validator submission.

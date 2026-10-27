# R30 (Claude Code, 27 Oct 2026): code and run guide

All runs are pre-registered.
- `PREREGISTRATION_R30.md`: sha256 in `PROTOCOL.sha256`.
- `AMENDMENT_R30_1.md`: sha256 in `AMENDMENT.sha256`, written after the punctuation gate failed and before any E3
  K4 output was viewed.

Every script asserts these hashes.

| File | What it does |
|---|---|
| `r30lib.py` | Shared helpers: protocol asserts, the 4-core solver runner, chain-addition keys, forward encryption, `verify_row`, `forced_mask` |
| `e1_scan.py` | E1 oracle scan: 6-digit (1e6) and 7-digit (1e7) chain-addition primers, plus 5 shuffled-K4 pass-count nulls (6-digit) |
| `calib.py` | C1 (chain-addition planted), C3 (one-cycle routes planted), C2 (blind punctuation test on `fixtures_punct.json`) |
| `search.py` | K4 English searches: `e1`, `e2` (16-restart screen, top 20 replicated at 64 with new seeds), `g5`, `r2` (64 restarts) |
| `e5.py` | C5 and E5: one mis-carved clue letter + 5-digit Gromark |
| `e4_book.py` | Whole-book running key (oracle, letter-shuffled null, 16-restart screen, top-20 replication). Runs under `python3 -I` |
| `e4_full.py` | Amendment 3: every book pass at 64 restarts, plus the word-order-shuffle diagnostic |
| `c4_bookplant.py` | Planted messages under real Carter-book keys (16/20 recovered at 64 restarts) |
| `build_lang_models.py` | Amendment 4: German, Dutch and mixed word models from `wordfreq` 3.1.1 (needs `pip install wordfreq`) |
| `e6.py` | C6 (blind German/Dutch/mixed calibration on `fixtures_lang.json`) and E6 (Carter passes + 39 primers under each model) |
| `make_handoff_zip.py` | Builds `k4kit/handoffs/R30_handoff.zip` (small; the large ranked JSONs stay in the repo) |
| `report.py` | Builds `SHORTLIST_R30.md` and `shortlist_r30.csv` (REVIEW ONLY rows, with forced masks and the scorer's word split) |
| `fixtures_punct.json` | 22 fresh hidden messages with K2/K3 punctuation (X = stop, Q = question mark) |
| `runs/` | Logs and JSON results. Solver scratch files are git-ignored |

**Checks built into every reported row.**
- `verify_row` re-encrypts the reported plaintext with the reported alphabets and key. It must reproduce K4 exactly,
  with every clue in place.
- `forced_mask` lists the letters the clue equations force: a position whose ciphertext node lies in a crib
  component, and whose implied rank lands on a plaintext node of that component.
  - Cross-checked against Round 25: primer 98850 (G4) forces 10 letters beyond the clues, and 60319 (G7) forces 5.
  - Planted checks: 200/200 forced letters correct.

**Reproduce** (from `k4kit/`, after building `bin/solver_s2kp`):

```bash
cd r30
python3 e1_scan.py                                    # ~2 min
(cd runs && python3 ../../tools/route_gromark.py passes r27_passes.csv)   # ~2 min, 65,968 passes
python3 calib.py c1; python3 calib.py c3; python3 calib.py c2
python3 search.py g5 ORTH; python3 search.py r2 ORTH; python3 search.py g5 ORTHXQ; python3 search.py r2 ORTHXQ
python3 search.py e1 ORTH                             # ~15 min on 4 cores
python3 search.py e2 ORTH                             # ~25 min on 4 cores
python3 e5.py c5; python3 e5.py run
# Carter book (from the repo root):
python3 -I k4kit/r30/e4_book.py archive/sources/carter_mace_1923_v1_doran_google_ocr.txt \
    --anchor-phrase TREMBLINGHANDSIMADEATINYBREACH --label carter_v1_doran
python3 -I k4kit/r30/e4_full.py archive/sources/carter_mace_1923_v1_doran_google_ocr.txt carter_v1_doran
python3 -I k4kit/r30/c4_bookplant.py
# Non-English models (needs wordfreq 3.1.1 in some interpreter):
<venv>/bin/python build_lang_models.py; python3 e6.py c6; python3 e6.py run
python3 report.py; python3 make_handoff_zip.py
```

Results depend on g++/libstdc++ (`std::shuffle` and the random stream), as noted in `tools/solver_s2kp.cpp`.

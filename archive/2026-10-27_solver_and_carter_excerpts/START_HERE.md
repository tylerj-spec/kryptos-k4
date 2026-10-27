# K4 solver + Carter source-key files — direct delivery

These are the actual files and code from the existing research package, plus `run_book_test.py` added to accept **a local text file** instead of an external URL.

## Included
- `claude/r26/key_oracle.py` — Claude's original exact 24-clue two-free-alphabet feasibility oracle (not a general plaintext solver).
- `r27_sources.py` — Round 27 frozen Carter excerpts and K1–K3 source-key test; expects the included `claude/r26/key_oracle.py` folder structure.
- `r27_source_null.py` — Round 27 shuffled-source controls and planted positives.
- `run_book_test.py` — NEW standalone command for source files stored locally, with exact source checksum, A-Z normalization, finite-window controls, CSV results. Not the complete statistical testing pipeline.
- `fetch_carter_1923_ocr.py` — optional historical OCR retrieval script; requires network; won't work behind your stated block.
- `source_excerpts/` — FIVE actual historical-source transcription/excerpt files copied directly from Round 27 literals. These are NOT the complete Carter/Mace book.
- `results/` — frozen Round 27 source-key outputs and score summaries.
- `CARTER_MACE_1923_SOURCE_STATUS.md`, `SOURCES.md` — edition and provenance warnings.
- `LEDGER.md`, `KRYPTOS_K4_MASTER_AGENT_HANDOFF_2026-10-26.md` — longer background.

## Quick local run

```sh
python run_book_test.py source_excerpts/carter_1923_bodleian.txt --max-windows 300
python r27_sources.py
```

When/if you have the *complete, edition-verified* 1923 Volume I OCR or transcription:

```sh
python run_book_test.py /path/to/your/carter_1923_volume1.txt --max-windows 1000
python run_book_test.py /path/to/your/carter_1923_volume1.txt --all
```

The `--all` search can be slow. Confirm source edition and OCR before interpreting results. The `run_book_test.py` script tests a particular bounded model; it does **not** certify a plaintext. Feasibility can arise even with no independent crib-cycle constraints; a promising fit requires negative controls and a readable result under an independently motivated model.

## Crucial limitation

**The complete Carter/Mace 1923 text is NOT included.** Earlier archives contained only excerpts and retrieval links. Attempted direct retrieval from Internet Archive in this session failed due to network DNS; we will not substitute an unrelated Tutankhamun book or claim that an OCR is verified.

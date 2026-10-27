ChatGPT R31 "strict blind" packet (Tyler's upload `KRYPTOS_R31_Strict_Blind_Handoff.zip`, 27 Oct 2026). Unchanged,
except that byte-identical copies of files already in this repo were dropped:
- `models/solver_s2kp.cpp` = `k4kit/tools/solver_s2kp.cpp`
- `models/word_model_orth.tsv` = `k4kit/data/word_model_orth.tsv`
- `blind31/quad_log10.f32` = `k4kit/data/quad_log10.f32` (sha256 d2a64e70…)
- `sealed31/reference_messages.json` = `k4kit/data/reference_messages.json`
- `blind31/carter_az.txt` (sha256 6761a507…) = `e4_book.normalise()` of `archive/sources/carter_mace_1923_v1_doran_google_ocr.txt`
- `R30_handoff_original.zip` = `k4kit/handoffs/R30_handoff.zip`

`LEDGER.md` (with ChatGPT's L110–L112) was adopted as `k4kit/LEDGER.md`. To replay: copy these files back in and run
`REPLAY_STRICT_BLIND.sh`. Claude Code's replay reproduced every frozen output byte for byte (ledger L113).

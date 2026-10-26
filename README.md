# Kryptos K4 research workspace

- `k4kit/`: the working toolkit and the canonical research record.
  - `k4kit/CLAUDE.md`: the working rules; read it first.
  - `k4kit/HANDOFF_CLAUDE_CODE.md`: the R29 brief.
  - `k4kit/LEDGER.md`: every model tested so far.
- `archive/`: ChatGPT's 26 Oct 2026 starter packet and extras (R27 source-key scripts, the Carter source note),
  kept unchanged for audit. Its older ledger copy (L01–L97) is superseded by `k4kit/LEDGER.md`.

Build and validate (about 30 s):

```bash
cd k4kit
g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
python3 tools/validate.py
```

**No verified K4 solution exists here.** No submissions to any external checker without Tyler's go-ahead.

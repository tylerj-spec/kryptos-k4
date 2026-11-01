# R43 (ChatGPT): word-constraint beam solver. FAILED PROTOTYPE, kept as evidence

**Do not use `r43/blind/word_constraint_beam.cpp` as a solver.** The beam search failed its planted-recovery
controls. Claude Code's review is in `r44/REVIEW_PR11.md` (ledger L139).

## Why it failed
The beam reads the plaintext left to right and keeps the best partial texts.
- **The true text closes almost no checkable constraints early.** On average 0.1 cycles by letter 10, 1.2 by 20,
  and 3.4 by 30.
- **So early pruning runs on language score alone,** and the truth is dropped before the constraints could help.

## What IS correct and reused
- **The exact algebra (`EdgeGraph`):** union-find with modular offsets, per-side injectivity and global alphabet
  packing.
  - It was audited against an independent encryptor (`r44/audit/audit_edgegraph.cpp`): 500/500 positive controls,
    5,689 sound random witnesses, and an impossible packing correctly rejected.
- **Reuse:** R44's audits and R52's screens include the file only for that engine, with
  `#define main r43_main`.

## Files
- `PREREGISTRATION.md`, `D0_FINDINGS.md`, `CLAUDE_REVIEW_REQUEST.md`: ChatGPT's R43 protocol and findings.
- `blind/`: the prototype; `sealed/`: its evaluator; `d0/`: development outputs.

No K4 result. Two fully free alphabets remain unsolved blind (L138, L139).

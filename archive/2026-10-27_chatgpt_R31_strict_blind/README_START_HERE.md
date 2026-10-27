# START HERE: Round 31 STRICT BLIND Kryptos K4

**This packet replaces the old candidate-generation protocol.** Read `HANDOFF.md`, then `blind31/PREREGISTERED_BLIND_PROTOCOL.md` and `sealed31/FREE_ALPHABET_CALIBRATION_PREREGISTRATION.md`.

## Existing evidence / human review
- `blind31/K4_*_BLIND.tsv`: frozen original-ciphertext-only ranking, 100 full 97-letter outputs per family.
- `sealed31/BLIND_CHECK_REPORT.json`: independently verified K4 clue matching and forward encryption (run only after the above is frozen).
- `blind31/UNKNOWN_BLIND_ALL_OUTPUTS.jsonl`, `sealed31/UNKNOWN_BLIND_AFTER_CHECK.json`: diagnostic without forced cribs, eight planted + four K4 cases.
- `LEDGER.md`: research status, new L110-L112.

## Reproduce without the known plaintext
Requires Python 3, g++ and 200 MB free memory. All code/source text needed is in this ZIP; no network.

```bash
bash REPLAY_STRICT_BLIND.sh
```

The replay compiles a **crib-free** C++ scanner and checks that both ciphertext-only ranking files are byte-identical to the frozen results. It also checks the no-crib arbitrary-alphabet solver on the provided held-out ciphertext fixtures. Only after freezing does it invoke `sealed31/check_after_freeze.py` and `sealed31/check_unknown_after_freeze.py`. The exact scorer is English quadgrams, NOT a specialized phrase matcher.

For a quick inspection without rerunning 15 million decryptions:

```bash
python3 sealed31/check_after_freeze.py
python3 sealed31/check_unknown_after_freeze.py
```

If a model needs all 24 clues supplied during decryption, its output is NOT a blind K4 recovery. Do not submit any external verifier requests without the user's approval.

The earlier 16/20 Carter known-key and 3/16 spelling-aware recovery counts were *crib-assisted*. Do not compare them directly against genuinely blind recovery rates.

# K4 toolkit (Claude R29)

Self-contained tools for testing K4 hypotheses exactly and searching for English. Python 3.9+ (standard library
only) and a C++17 compiler.

```bash
g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
python3 tools/validate.py          # about 30 s; prints ALL CHECKS PASSED
```

| Tool | What it does | Cost |
|---|---|---|
| `tools/k4common.py` | K4 ciphertext, clues, alphabets, Gromark streams, K3 rotations (`route()`), rearrangement setup, solver input lines | — |
| `tools/key_oracle.py` | **Exact test of any proposed key sequence** with both alphabets free (`possible(k, ct, anch)`), plus crib-cycle count (`checks`) | about 20 µs per key |
| `bin/solver_s2kp` (`tools/solver_s2kp.cpp`) | **English search** for one key sequence: both alphabets unknown, clues enforced exactly, optional rearrangement undone before scoring. Word model + quadgram + polish | about 3.5 s per line at 64 × 40,000 |
| `tools/book_key_test.py` | Whole-book running-key test: every window × 2 directions × 2 numberings, shuffled-letter null, optional solver follow-up | minutes per book; the follow-up costs extra |
| `tools/route_gromark.py` | K3-rotation + Gromark: regenerate the 65,968 passes, calibrate on planted messages, search chosen routes | passes take about 2 min; search about 1 s per line at 16 restarts |
| `tools/trifid_any.py` | Exact Trifid test with any 27-symbol cube, every period and phase | about 1 s |
| `tools/period_repeats.py` | Per-column repetition invariant vs English, periods 1–48 | about 1 s |

**Data (`data/`)**
- `word_model_orth.tsv`: ChatGPT R20 word model.
  - Built from TextBlob English word frequencies plus Dutch-like spelling variants at −1.5 log10.
  - sha256 `12392e2d…48676877`.
- `quad_log10.f32`: English letter-quadgram log10 probabilities.
  - 26⁴ float32, index ((a·26+b)·26+c)·26+d.
  - sha256 `d2a64e70…f89a43`.
- `k1k3_plaintext.txt`: the K1–K3 plaintext (K1+K2+K3), letters only.
- `reference_messages.json`: released hidden-test messages, 97 letters with the clues in place. Used for planted
  calibration and as English references.
- `results/`: logs of the R26–R29 runs summarised in the ledger (period repeats, Trifid, oracle, R28C searches).

**Score scale (W = word score of 97 letters).**
- Readable planted English: about −69 to −95.
- Best wrong keys: −115 to −150.
- Typical gibberish: −150 to −180.
- K4's best ever, in any searched family: about −136 to −141.

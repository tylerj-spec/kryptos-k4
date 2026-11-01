# Tools index: what code exists in this repo and how to run it

Claude Code, 1 Nov 2026. The working rules are in `k4kit/CLAUDE.md`.

**Rules for running anything:**
- Run untrusted or downloaded inputs from their own directory with `python3 -I`.
- Never use `pkill -f`.
- Never `git stash` while jobs write tracked files.

**Checks before any push:**
```
bash strictblind/tests/run_all.sh
bash verify_all.sh
python3 -I r44/tests/test_contract.py
python3 -I r44/tests/verify_frozen_holdout.py
python3 -I r53/tests/test_contract.py
```
CI: `strictblind-ci.yml`, `r44-reviewed-holdout.yml`, `r53-blind-firewall.yml`, `r54-method-only.yml`.
- **Extra R44/R52 replay tests** are on the unmerged PR #12: `r44/tests/test_r44_claude.py`,
  `r52_claude/tests/test_r52.py` and the `claude-r44-r52.yml` workflow.

## Data (`k4kit/data/`)

| File | What |
|---|---|
| `k1k3_plaintext.txt` | K1–K3 plaintext as carved, letters only (K3 appears twice; L135) |
| `quad_log10.f32` | English quadgram log10 table, 26⁴ float32 values |
| `word_model_orth.tsv` | Word model (word, exact log-prob, edit log-prob); used for the word score and the keyword-alphabet vocabulary |
| `reference_messages.json` | Template plaintexts for planted controls |
| `r34/carter_az.txt` (outside `data/`) | Carter & Mace 1923 vol. I as A–Z letters (source and sha256 in `archive/sources/README.md`) |

## General toolkit (`k4kit/tools/`)

| Tool | Does | Kind |
|---|---|---|
| `k4common.py` | K4 ciphertext, clue positions, alphabets, shared helpers | library |
| `key_oracle.py` | Exact check: can a given key sequence fit the 24 letters with **two free alphabets**? (Vigenère, Beaufort, Quagmire I–IV) | crib-assisted exact |
| `period_repeats.py` | Per-column repetition statistic for any in-place periodic cipher (L89) | statistic |
| `trifid_any.py` | Trifid with an arbitrary 27-symbol cube, every period (L91) | crib-assisted exact |
| `book_key_test.py` | Running key from a whole book, every window (L101/L106) | crib-assisted |
| `route_gromark.py` | K3-style routes + two-free Gromark (L94, L99, L100) | crib-assisted |
| `solver_s2kp.cpp` | English search with both alphabets unknown and the clues enforced (R21–R28) | **crib-assisted, not blind** (L110) |
| `validate.py` | Toolkit self-test | test |

## Strict-blind harness (`strictblind/`; L120, L125)
- **`blind/`** (never sees the clues):
  - `routes.py` makes route files (`r27`, `rot LO HI`, and others);
  - `scan.cpp` decrypts every route × key × 12 fixed conventions and keeps the top 100 by quadgram score;
  - `experiment.py` runs a manifest and writes `FROZEN.sha256`.
- **`sealed/`** (holds the clues):
  - `make_plants.py`;
  - `reveal.py`, which re-encrypts and counts clue letters;
  - `whole_family.py/.cpp`, which counts matches across the whole family against chance.
- **Use:** see `strictblind/README.md`. In short:
  1. write a pre-registration and a manifest;
  2. run `python3 -I strictblind/blind/experiment.py EXP`;
  3. commit the freeze;
  4. run `python3 -I strictblind/sealed/reveal.py EXP`.

## One-free-alphabet blind solvers
| Path | Model | Notes |
|---|---|---|
| `r40/blind/` (`pafree_scan.cpp`, `subsolve.cpp`, `run.py`) | fixed cipher alphabet × **free plaintext alphabet** | stage 1 unigram screen, stage 2 substitution solve (L134) |
| `r41/` | same, with K3 routes after the substitution | L135 |
| `r42/blind/` (`ca_screen.cpp`, `casolve.cpp`, `run.py`) | fixed plaintext alphabet × **free cipher alphabet** | Hungarian screen + anneal (L136) |
| `r44/blind/kwpa_solve.cpp` + `polish.cpp` | **keyword plaintext alphabet × free cipher alphabet**, key given | 20/20 on holdout B (L140). Usage: `kwpa_solve WORDS QUAD IN OUT [KCAND RESTARTS TOP2 RESTARTS2]`, then `polish WORDS QUAD BLIND.tsv IN.jsonl OUT.jsonl [LAMBDA]` |
| `r44/sealed/make_holdout{,_b}.py` | holdout generators (seeds 44200+, 44300+) | sealed |

## Two-free-alphabet research code (planted data only)
- **`r43/blind/word_constraint_beam.cpp`** (ChatGPT R43): EdgeGraph exact engine (audited correct) plus a beam
  solver (**failed** its gate; `r44/REVIEW_PR11.md`).
  - Reuse the engine with:
    ```
    #define main r43_main
    #include "../../r43/blind/word_constraint_beam.cpp"
    #undef main
    ```
- **`r43dev/pt_quadgram.cpp`, `pt_quad_word.cpp`:** parallel tempering over both alphabets (L138).
- **`r44/blind/wordpt.cpp`:** word-move parallel tempering (failed).

## Crib-assisted exact screens (exclusions only, never candidate sources; R53)

| Path | Family |
|---|---|
| `r44/audit/audit_edgegraph.cpp` | audit of EdgeGraph against an independent encryptor |
| `r44/audit/kw_exact_check.cpp` | in-place Gromark × keyword alphabet (R45 replication) |
| `r44/audit/rk_exact_check.cpp` | Carter + K1–K3 running keys (R47 replication) |
| `r44/audit/rot_exact_check.cpp` | 24×8 rotations after substitution (R46 replication) |
| `r52_claude/sealed/chain_screen.cpp` / `chain_screen_fast.cpp` (**unmerged PR #12 only**) | all chain-addition families × keyword alphabets × routes (R52, crib-conditioned exploratory; the fast version is byte-identical) |

## Older rounds
- **`k4kit/r30/`, `k4kit/r32/`, `r33/`–`r39/`:** each has its own pre-registration, code and frozen outputs.
  `verify_all.sh` replays R33.
- **`archive/`:** earlier handoffs and sources.
  - The World Clock 360° chart is `archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md`.
  - The Morse experiment is `r28_morse_experiment.py`.

## Later rounds
**On `main`:**
- `r49/`: World Clock provenance.
- `r53/`: `BLIND_RULES.md` and its Docker firewall CI, the **current blind standard**.
- `r54/`: `method_fingerprint.js`, ciphertext-only statistics.
- `CURRENT_STATUS.md`: the owner's summary.

**Not on `main`:**
- ChatGPT's `r45/`–`r48/`, `r50/`–`r52/` (their own branches).
- Claude's `r52_claude/` (PR #12, crib-conditioned record).

Summaries of all of them are in `CIPHER_TYPES_TESTED.md` and `RESEARCH_LOG.md`.

## Building
Every C++ tool is single-file C++17:
```
g++ -std=c++17 -O3 -march=native FILE.cpp -o BIN
```
Some need `-pthread`. Python is the standard library only (3.9+).

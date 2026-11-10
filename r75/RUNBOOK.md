# R75 runbook (for whoever runs it; written 10 Nov 2026)

Everything is decided in `r75/PREREGISTRATION.md`. This file is the exact sequence of commands. **Change no code, cut,
seed or book.** If a step fails in a way this file does not cover, stop and report; do not improvise a fix on K4 data.

**Before starting:** Tyler must have said to run R75. Parts B and C touch K4.

**Standing rules:**
- Commit after every step with the message given, then push to `claude/r75-key-shape-fixed-methods`.
- Commit trailer: `Co-Authored-By` plus the `Claude-Session` line, as in earlier rounds.
- Never `pkill -f`; never `git stash` while a job writes files; run Python that reads downloaded files with `-I`.
- Report raw decodes unedited. Nothing goes to any outside checker.

## 0. Setup (about 5 minutes)
```bash
cd /home/user/kryptos-k4 && git checkout claude/r75-key-shape-fixed-methods
S=<scratchpad directory>            # session-specific; never inside the repo
LM=$S/r59bin/lm6.v2.bin
sha256sum $LM                        # must start b1a2a3c7 (r59/blind/LM_SHA256)
sha256sum -c r75/PROTOCOL.sha256     # every line OK
python3 -I r75/tests/test_r75.py     # "R75 TESTS OK"
```
- **If the letter model is missing** (new container), rebuild it:
  `python3 -I r59/corpus/build_corpus.py fetch RAW; build RAW OUT NLTK_DIR`, then `lm_build OUT/train.txt lm6.bin 6`
  (`r59/RESULT.md`, "Reproduce"). Its sha256 must match.
- **Books for Part A** (put them in `$S/r75src/`; `make_holdout.py` checks their hashes):
  ```bash
  mkdir -p $S/r75src && cd $S/r75src
  B=https://raw.githubusercontent.com/GITenberg
  curl -sSf -o 139.txt  $B/The-Lost-World_139/master/139.txt
  curl -sSf -o 308.txt  $B/Three-Men-in-a-Boat_308/master/308-0.txt
  curl -sSf -o 289.txt  $B/The-Wind-in-the-Willows_289/master/289-0.txt
  curl -sSf -o 2226.txt $B/Kim_2226/master/2226.txt
  ```

## A. Sealed synthetic gate (about 15 minutes; no K4)
```bash
cd /home/user/kryptos-k4 && B=$S/r75src
python3 -I r75/sealed/make_holdout.py $B/139.txt $B/308.txt $B/289.txt $B/2226.txt 750300 $S/r75_sealed
sha256sum $S/r75_sealed/sealed_truth.json          # note the hash: it goes in the commit message
mkdir -p r75/holdout && cp $S/r75_sealed/blind.tsv r75/holdout/blind.tsv
```
1. Commit `r75/holdout/blind.tsv`: *"R75 holdout (seed 750300): 160 ciphertexts; sealed truth sha256 <hash> withheld
   until verify"*. Push.
2. Blind run (about 10 minutes on 4 cores; prints progress every 20):
   `python3 -I r75/blind/run.py $LM r75/holdout/blind.tsv r75/holdout/run 4`
3. Commit `r75/holdout/run`: *"R75 FREEZE: blind scans of all 160 holdout ciphertexts; before verify and before the
   truth is opened"*. Push.
4. Gate:
   ```bash
   cp $S/r75_sealed/sealed_truth.json r75/holdout/sealed_truth.json
   python3 -I r75/sealed/gate.py r75/holdout/blind.tsv r75/holdout/run r75/holdout/sealed_truth.json r75/holdout/GATE.json
   ```
5. Commit the truth and `GATE.json` with the result in the message. Push.

**Pass rule:** `"passed": true`, i.e. ≥ 54/60 recovered and confident, 0/100 negatives confident, verify passed.
**If it fails:** stop here. Report the numbers. Do not run B or C1.

## B. Blind K4 run (about 10 minutes)
```bash
mkdir -p r75/k4 && python3 -I r75/sealed/prepare_k4.py r75/k4/TARGET.tsv      # K4 + 100 shuffles
```
1. Commit `TARGET.tsv`: *"R75 K4 target: unchanged K4 + 100 shuffles (seed 750400)"*. Push.
2. `python3 -I r75/blind/run.py $LM r75/k4/TARGET.tsv r75/k4/run 4 --full K4`
3. Commit `r75/k4/run`: *"R75 K4 FREEZE: blind scans of K4 + 100 shuffles and the K4 review packet; before verify and
   before any published-letter comparison"*. **Push before going on.**

## C. After the freeze (about 30 minutes)
```bash
python3 -I r75/sealed/gate.py --verify r75/k4/TARGET.tsv r75/k4/run r75/k4/VERIFY.json   # C1a: must say PASSED
```
Commit `VERIFY.json`: *"R75 K4 verified after the freeze (no published letters)"*. Push. Then:
```bash
python3 -I r75/sealed/reveal_k4.py r75/k4/TARGET.tsv r75/k4/run r75/k4/REVEAL.json       # C1b, about 3 minutes
python3 -I r75/sealed/exact.py K4 $LM r75/k4/TARGET.tsv r75/k4/EXACT.json 20             # C2, about 5 minutes
python3 -I r75/sealed/gridx.py K4 $LM r75/k4/TARGET.tsv r75/k4/GRIDX.json 20             # C2b (Amendment 1)
python3 -I r75/sealed/keyshape.py r75/k4/KEYSHAPE.json                                   # C3a, about 3 minutes
python3 -I r75/sealed/keyclass.py r75/results/KEYCLASS_MODEL.npz r75/k4/KEYCLASS.json    # C3b, seconds
```
Commit the five JSON files with the five verdicts in the message. Push.

## D. Write up
1. **`r75/RESULT.md`**, in the format of `r74/RESULT.md`:
   - a steps table with commits;
   - the gate table;
   - the blind result: best decode raw, scores against the cuts, shuffles at or above;
   - the whole-family letter count;
   - each exact check's verdict, with K4's feasible counts beside the shuffles';
   - the key shape: the corrected p and the top five cells;
   - the key class: the verdict, the neighbour shares and the six z-scores;
   - the row of the pre-registration's "What follows" table that applies.
2. **Ledger:** one new row `L165` after L164 and one line under "Changes", in the style of L164.
3. **PR:** update the draft PR's description with the results table; mark it ready for review.

## What to hand back, and when
| Outcome | Action |
|---|---|
| Reveal says SIGNAL or SCORE_ANOMALY, or any exact check says CONSISTENT | **Stop.** Do not tune or rerun. Report the raw decode and setting to Tyler at once. The follow-up is a design task for the stronger model |
| F0X does not reproduce L03/L04 (some periodic key of period ≤ 25 feasible with ≥ 3 checks under AZ/KRY alphabets) | Stop; that is a bug or a ledger error. Report it |
| Key class HELD, FEWVALUES, DIGITS, or MIXED | Report the numbers. The next round's design is for the stronger model |
| Everything negative, NO_VISIBLE_STRUCTURE | Write up and finish. State the pre-registered conclusion plainly |

**What good output looks like** (from the synthetic dry runs, for orientation only):
- A planted message is recovered with a letter-model score near −0.6 to −0.9; shuffles sit near −1.8.
- A random target's best whole-family letter count is 8 or 9 of 24.
- A random target leaves about 1,900–2,500 F1X settings feasible with ≥ 3 checks and no readable decode.

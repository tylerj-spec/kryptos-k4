# R73 K4 run pre-registration (Claude Code, 9 Nov 2026): Family I only

Written before the K4 target is generated. Tyler approved this run on 9 Nov 2026 ("Sure do the easy one first").

**Scope:**
- **Family I** (interrupted key restarted at every plaintext word, word divisions removed; 18 settings) is the only
  family evaluated. It passed its sealed synthetic gate (`r73/PHASE_B_RESULT.md`: 94/100, setting exact 100/100,
  0/300 negatives confident).
- **R26** failed its gate. The frozen runner decodes its settings too, but they are stored only and are not evaluated
  or reported as candidates.

**Target** (`r73/sealed/prepare_k4.py`): the unchanged K4 ciphertext (sha256 2797de14…) plus 100 frequency-preserving
shuffles (seed 730200).

**Blind run:** `r73/blind/run.py`, unchanged since Phase B (sha256 in `r73/PHASE_B_PROTOCOL.sha256`), reads only the
target TSV.

**Sequence:**
1. Freeze and push all results.
2. Verify every stored decode re-encrypts to its ciphertext (`r73/sealed/gate.py`'s verify, no truth).
3. Only then `r73/sealed/reveal_k4.py`, the only R73 file holding the published letters.

**Statistic:** for each ciphertext, the best Family I decode, i.e. the highest score over the 18 settings, per letter.

**Outcomes:**
- **CONFIDENT** iff K4's best Family I score is ≥ −2.7 per letter (the frozen cut) **and** above every null's.
- **SIGNAL** iff CONFIDENT **and** the decode matches ≥ 10 of the 24 published letters. These sit at 0-based plaintext
  positions 21–33 and 63–73. Family I enciphers in place, so the decoded letters are in carved order.
- **SCORE_ANOMALY** iff CONFIDENT without the letter match.
- **NO_SIGNAL** otherwise.

**Contender screen:** any of K4's 18 Family I decodes matching ≥ 12/24 is listed raw, together with the nulls'
maximum.

**Prior expectation** (stated before the run): NO_SIGNAL. Only 0.56% of Family I ciphertexts are as flat as K4.

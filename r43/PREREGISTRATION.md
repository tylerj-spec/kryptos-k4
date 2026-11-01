# R43 pre-registration — word-placement consistency solver, both alphabets free

Registered against merged main `c0e2a6847d0f7a505ccfa3bea2b0c58a5ccf2f3c` before creating the benchmark ciphertexts or running the candidate search.

## Research question

Can a dictionary-level beam search, using word frequency and **exact modular alphabet constraints**, recover original **97-letter continuous English** when the *correct* 5-digit base-10 Gromark key is supplied but both plaintext and cipher alphabets are independently uniformly random? Prior L109/L123/L138 methods failed this blind task; trying K4 before passing new hidden controls would repeat the same problem.

The search receives only ciphertext, 97 key digits, and an unchanged generic dictionary. It receives no plaintext, crib, clue positions, known K4 ciphertext, or external reconstruction. Any later K4 experiment requires a separately committed protocol.

For each hypothesized word letter `p` placed at position `i`, require the exact relation
`CA_index(C[i]) - PA_index(p) = key[i] (mod 26)`.
Use union/find with modular offsets to reject all inconsistent cycles and collisions between positions of a permutation. At the end, solve for the shifts of connected components to find **two full bijective alphabets**; independent forward re-encryption must recreate the input ciphertext.

## Development experiment D0

- 20 independently authored passages, normalized/truncated to 97 capital letters, none selected using K4 plaintext or a public fitted reconstruction.
- Each passage is encrypted under fresh independent **uniform random 26-letter plaintext and ciphertext alphabets** and a fresh **uniform random 5-digit Gromark primer**, with fixed reproducible seeds.
- The solver is given the **true key digits** (this is not a key identification experiment). For each passage it must return the original plaintext, not merely a feasible cipher witness.
- Lexical source: the existing, versioned `k4kit/data/word_model_orth.tsv`. The solver may cap per-length candidate counts to bound compute, but the cap and scoring must be recorded before D0 is run.
- D0 is an OPEN DEVELOPMENT round, not a holdout test. D0 determines whether beam search is viable; any tuning makes it development data.
- Metrics: exact 97/97 recovery, <=3-letter error, median nontrivial plaintext accuracy; forward re-encryption for **all** returned candidates; elapsed time and peak states; aggregate failure count.
- **Predeclared gate for promotion to a future K4 run:** >=16/20 exact **on a distinct, newly committed unseen evaluation set**; zero invalid forward-encryption witnesses. Passing D0 alone does not authorize K4.
- On a failed D0, report the failure plainly, record a reproducible negative result, and do not scan K4 with this solver.
- When a useful solver passes the fresh gate, run original K4 without clues, hash/freeze full candidate output, and only after committing it reveal 24 known plaintext letters and test independent forward encryption.
- Any apparent 24-letter match alone is not a solution. No external verifier submission without a defensible independently generated method.

## Reproducibility

The code and fixtures will be separate: `r43/blind/` has no import/path to `r43/sealed/`, and cannot accept a plaintext mask. Every generated candidate must contain a complete plaintext, two bijective alphabets and a full ciphertext re-encryption witness. First experiments use fixed random seeds, no stochastic hyperparameter tuning after seeing K4.

No K4 results or solver success are claimed at registration.

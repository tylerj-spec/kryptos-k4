# R59 preregistration: can ciphertext statistics distinguish a true pad from structured masking?

**Frozen before any R59 code, control generation or original K4 fingerprint calculation. Date: 2026-11-01.**

## Key distinction: never claim to "break" an unknown true one-time pad

For an independent uniformly random 97-letter key K_i over Z26, used once,
C_i = (P_i + K_i) mod 26. For **EVERY** 97-letter plaintext P and fixed ciphertext C,
there is exactly one fitting 97-letter K = (C-P) mod 26, with probability 26^(-97).
Therefore Pr(C | P) is identical for all P, and observing C reveals no plaintext
information under the ideal OTP assumptions. Generating such a K from an arbitrary
guessed K4 plaintext is tautological and must NEVER be called a solution. **No
reconstructed or post-hoc "K4 pad" is permitted in this round.**

A book passage or deterministic sequence masquerading as a 97-letter pad is NOT a
true OTP and may be vulnerable if its independent source or recurrence is found.
Scheidt's "masking" could be a transformation, an encoding convention, semantic
obfuscation, inserted nulls, a running key, a nonperiodic substitution, or something
else; his interview does NOT prove he used a separate OTP/masking layer.

## Prior work to preserve, not rediscover

Repository ledger L26 general masking OPEN; L31 unknown English running keys STAT;
L49 affine recurrences, L50 tableau-path masks exact in-place/crib-assisted only;
L81-83 bounded nulls/periodic salting, L90/K1–K3, L106/Carter, L109–L127
book running keys and combined routes within explicit convention scopes;
R55 feedback, R56 evolving alphabet, R58 masked-tableau and physical-route
compositions all negative on K4 within tested finite parameters. Claude's R52
on unmerged PR #12 is crib-conditioned, NOT a compliant blind search.

## What R59 actually tests

A **ciphertext-only fingerprint**, not an attempted decryption or a key search.
Exactly four immutable feature families on each 97-letter ciphertext:

1. Two-sided absolute deviation of observed global index of coincidence
   from ideal iid uniform 1/26.
2. Maximum pooled periodic-column IC over periods 2 through 12, keeping all
   observed characters and correcting for all period choices by null simulation.
3. Maximum lag-equality standardized statistic for every lag 1 through 24.
4. Maximum (over periods 2..12) per-column best shift log-likelihood improvement
   compared with independent uniform ciphertext, using **fixed generic English
   monogram probabilities** (independent of K4 plaintext).
No unknown 97-character per-position key, guessed K4 letters, word/location
anchor, direct K4 crib score, route selection, or published clue positions enter
the statistics. No investigator post-hoc feature choice.

**Familywise calibration**: deterministic `numpy.random.default_rng(590061)`
generates 4,000 iid uniform random strings to compute per-feature upper-tail
empirical p values, and a *separate* 4,000 iid uniform strings to calibrate the
maximum of four -log10(p_feature) scores. The K4 omnibus p is computed on that
independent second cohort: `(1+#(cal_scores>=target_score))/(4001)`.
A statistically notable departure is defined *in advance* as familywise
p <= 0.01. Such a departure argues against ideal iid uniform, but does not
identify or decrypt any mask. Non-rejection cannot prove a true OTP.

## New independent powered controls, masked identity hidden

90 new ciphertexts using fresh natural English prose from two **different**
immutable public-domain books (not the novels used in R58):
- H.G. Wells, *The Time Machine*, GitHub
  `GITenberg/The-Time-Machine_35` commit
  `154a5c628743bd7d35d1af0fc4bcc017f0e111e1`,
  `35-0.txt`, Git blob SHA-1
  `419c78ce03f41984ef14913739b48d9332bd2801`.
- Arthur Conan Doyle, *The Adventures of Sherlock Holmes*, GitHub
  `GITenberg/The-Adventures-of-Sherlock-Holmes_1661` commit
  `7e5dd2703fbf503c004063e96ab7c61262375e5f`,
  `1661-8.txt`, blob SHA-1
  `ea9235417718bb0a438795c1dd7cbf65472b40fb`.

Strip to ASCII A–Z from central 80% of files to omit headers. Sample
**90 distinct nonoverlapping 97-character windows**, 45 from each book;
seed `random.Random(590059)`. Shuffle assignment to hidden-family cases.
Encryption uses fixed AZ modular addition, with:
- **30 genuine ideal OTP controls**: one independent uniformly random
  97-letter key per message, never reused.
- **30 periodic-mask controls**: unknown period chosen uniformly in 3..6,
  independent uniformly random key of that period, repeated over 97 letters.
- **30 full-length book-running-key controls**: 97-letter contiguous window
  from the other book at a random nonoverlapping offset (not the plaintext).
  This is a finite book-source example, not a truly random one-time pad.
All IDs are neutral `CASE_000..CASE_089`, interleaved, class/key/text
kept in a sealed truth file outside the no-network blind runtime. The solver
does NOT receive either source book, the 90 plaintexts, keys, true labels, a
known K4 plaintext/position, or repo history. The sealed evaluator subsequently
checks that all full keys forward-encrypt the respective whole ciphertexts.

Power is descriptive, not a mandatory 16/20 full-plaintext gate because this
round is **fingerprinting, not decryption**. Report detection (p<=0.01)
separately for all 30 members of each family; ideal OTP false-positive target
<=2/30, structured periodic power target >=20/30. If the power target fails,
the only permissible interpretation is that these statistical features are
too weak for this 97-character test; no model parameters may be adjusted
using revealed controls.

## Original K4 procedure

Input exact canonical 97-letter K4 ciphertext from
`r39/ic_gate/k4_ciphertext.txt`, including trailing newline SHA256
`2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
It is the **only authentic K4 data** mounted to the analysis environment;
no published plaintext letters, offsets or text-derived true keys, ever.

In a single no-network unprivileged read-only isolated container, run the
unchanged fingerprints over all 90 opaque synthetic ciphertexts and
authentic K4. Freeze **all** raw 91 rows, their feature arrays/omnibus p
values and byte hashes of solver, inputs, generic priors and preregistration
in a separate REMOTE Git commit before a separate sealed evaluator sees
synthetic truth. K4 has no afterfreeze letter checker because we output
**no candidate plaintext at all**.

The null samples, feature algorithms and English reference frequency vector
are predeclared and fixed, never fit to K4. No K4 decryption, external checker,
PR merge or claim of algorithm identification unless independently validated
by new separate research.

## Interpretive guardrails

A true OTP is *not a new encryption family recoverable from a single K4
ciphertext*. Cryptographic perfect secrecy is unconditional given a correct
fresh independent uniform key, but historical use requires **external**
evidence of key generation, length, secrecy, distribution and never-reuse.
Statistical compatibility with uniform alone is necessary, NEVER sufficient.
A structured mask could produce the same 97-letter fingerprint as an ideal
OTP. Even a significant deviation from uniform would weaken the true-OTP
hypothesis, but not imply English plaintext, a specific key, or a cipher
construction. Null insertion/semantic masking and non-in-place methods
are outside R59's specific statistical scope.

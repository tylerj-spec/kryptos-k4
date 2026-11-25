# Batch work order R102–R107 (Claude Code, 25 Nov 2026): the two-free-alphabet autokey (S3b), and one fallback branch

Affected ledger IDs: none yet. Each round adds its own row.
Validation: planning. The ledger reconciliation is §2.
Independent review: NONE (planning; one model).

**Approval.** The batch was proposed by ChatGPT on 25 Nov 2026 and endorsed by Tyler ("This seems like a better
approach for you to do more work"). It runs under `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Authorized at once:** R102, R103, R104, R107 and the fallback tasks.
- **Authorized only if their registered entry conditions hold:**
  - R105 needs R104's feasibility gate;
  - R106 needs an *independently verified* R105 GO.
- R98–R101 are under ChatGPT's audit. Nothing here depends on them being right.

## 1. The target hypothesis (S3b)
A plaintext autokey with **arbitrary** plaintext and ciphertext alphabets:

    B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c,   with A, B any of 26!, F ∈ {A, B, AZ}.

This is R100's family (L189) with free alphabets. It is the S3b half of `audit/reviews/S3_STATUS_20261125.md`. It has
no exact crib check, so it needs a blind solver, and the questions are whether that is tractable and identifiable at
97 letters.

## 2. Ledger reconciliation (no duplication)
| Proposal | Overlapping rows | What is new |
|---|---|---|
| R102 algebra | L27/L58/L59 are exact partitions with *fixed* plain and feedback alphabets and a free cipher alphabet. L188–L190 cover the tier and one-free-alphabet cases | The reduction to a Latin square isotopic to Z26, the gauge symmetries, a plaintext-hypothesis consistency test, and a ciphertext-only prediction. None of these is in the ledger |
| R103 identifiability | L52: the free-cipher-alphabet autoclave becomes unidentifiable at lags ≳ 25. L138: two free alphabets with the key given are identifiable by a word model but not by quadgrams | Unicity for **two free alphabets plus autokey**, measured directly, without a solver, by the consistency test |
| R104 decomposition | R97 (L186): key-space alternation had no basin for RX2-O | Landscape measurements for key-space against plaintext-space search on this family. The result is an architecture decision |
| R105 conditional solver | L52's search covered A ∈ {AZ, KRYPTOS} with F = A and a free cipher alphabet | One supplied alphabet, the other free, with fresh synthetic controls |
| R106 joint solver | L138–L140 covered two free alphabets, but with the key *given*, not an autokey | Both free, autokey |
| R107 structured-key Slidefair | L187 (tier alphabets, any key); L88 (Playfair family) | Free alphabets with a periodic or keyword key, the only Slidefair form that can be tested |

## 3. The rounds
| Round | Type | Question | Entry condition | Output | Budget per job |
|---|---|---|---|---|---|
| **R102** | analysis + synthetic verification | Exact algebra of S3b | none | A theorem note with verified code: the Latin-square reduction, the gauges, a plaintext-hypothesis consistency test (linear congruences mod 26 plus injectivity), and a ciphertext-only lag-L prediction with its power on plants | 1,800 s / 1,800 s / 2,048 MiB |
| **R103** | synthetic measurement | Is a 97-letter S3b ciphertext identifiable? | none (it uses only R102's *code*, which its own gate re-verifies) | The false-consistency rate of unrelated English passages against planted ciphertexts, as a function of length, lag and F. Verdict: IDENTIFIABLE (rate < 10⁻³ at 97) or NOT | same |
| **R104** | synthetic measurement | Can the error propagation be isolated? Which search architecture? | none | Score-against-distance landscape measurements for key-space and plaintext-space search on plants, a small prototype, and a registered **feasibility gate** for R105 | same |
| **R105** | type C development, synthetic | Recover the other alphabet when one is supplied | R103 says IDENTIFIABLE and R104's gate passes | GO / NO_POWER on fresh synthetic controls | as registered then |
| **R106** | type C development, synthetic | Recover both alphabets | R105 GO **independently verified** by ChatGPT | GO / NO_POWER | as registered then |
| **R107** | analysis + synthetic | Does a structured key make free-alphabet Slidefair testable? | none (independent branch) | The exact-check power or identifiability under a periodic or keyword key. Verdict: testable or not, with a registered round if testable | same |

**Shared rules for every round:**
- pre-registration first;
- controls in every round;
- an independent reference implementation in every gate;
- no K4 input in R102–R106;
- K4 contact only as a separately registered exact or blind round, under the usual gate.

**Stop rule:** if R103 finds S3b **unidentifiable** at 97 letters, R105 and R106 are cancelled, not run. That outcome
is reported to Tyler and ChatGPT.

## 4. Fallback tasks (independent; pick one up if the main line blocks)
- **F1. Reversible language masking.** Concrete, reversible respelling or phonetic mechanisms (German- or Dutch-like
  orthography rules applied before an in-place cipher), each with a predicted ciphertext-only observable.
  Deduplicated against L33, L61, L63, L68 and L108.
- **F2. Layered simple constructions.** A G0 catalogue of two-stage combinations of hand methods that are not yet in
  the ledger, ranked by exact checkability. The next exact rounds come from it.
- **F3. Non-repeating deterministic key generation.** Generator families such as lagged additive or Fibonacci
  sequences, number-derived and date-derived keys, deduplicated against L22, L132, L143 and L157. The output is the
  untested families with an exact check.

## 5. Stop conditions
The stop conditions are §4 of `audit/OPERATING_PROCEDURE_ROLLING.md`, verbatim. In particular, a possible K4
plaintext, any missed control or solver disagreement, a threshold change, or a budget overrun stops the batch for
review.

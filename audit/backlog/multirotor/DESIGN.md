# Multi-rotor design closeout

Status: **DESIGN COMPLETE; cipher families OPEN; no K4 experiment executed.**

This finishes the RX2 design obligation left by `r85/DESIGN.md` §5 and the two-rotor confounder already used in `r87/sealed/make87.py`. It supplies two finite constructions, their inverses, an exact feasibility method, executable synthetic checks, and limits for a prospective experiment. It does not claim that a blind two-wiring solver exists or has power on 97 letters. Internal ChatGPT subtasks are one model, not an independent-model council.

## 1. What is actually new

R87/L176 covered one arbitrary wiring, 16 fixed contact-numbering pairs, and one regular step schedule. R89's RCT family extended a single wiring to ciphertext-triggered stepping. Neither covers arbitrary composition of two differently moving wirings. R87 used a two-rotor construction only to generate wrong-family controls; rejecting it with a single-rotor classifier did not test it as a K4 hypothesis.

Two equal-speed rotors at a constant relative angle are a redundant design. Let `T_s(x)=x+s (mod q)` and `R_s(W)=T_-s W T_s`. If `s2_i=s1_i+d`, then

`R_s2_i(W2) R_s1_i(W1) = R_s1_i(T_-d W2 T_d W1)`.

The bracketed composition is one fixed permutation. Any number of rotors sharing the same motion up to constants collapses similarly. This is a sufficient equivalence test, not a complete classification of all accidental equivalent wirings. The retained different-clock catalog can still contain special wirings equivalent to simpler ciphers.

A stationary second rotor generally **does not** satisfy this constant-relative-angle condition when the first moves. Its arbitrary output permutation is not one of R87's four fixed output alphabets in general. Such rows must not be discarded using a false collapse argument.

## 2. Complete reversible model

Work in `Z_26`. Position `i` runs from 0 through 96. There are no blocks, padding, skipped positions, transpositions, reflectors, plugboards, or plaintext/ciphertext-driven state changes.

The input and output contact alphabets are independently chosen from the same four keyword-first alphabets used in R87: A–Z, KRYPTOS, PALIMPSEST, and ABSCISSA, giving 16 ordered pairs. `P_i` and `C_i` below are the indices in those alphabets. Each `W_j` is an arbitrary permutation of 0…25.

Encryption is

`M_i = W1(P_i+s1_i)-s1_i`,

`C_i = W2(M_i+s2_i)-s2_i`,

with every arithmetic operation modulo 26. Decryption is

`M_i = W2^-1(C_i+s2_i)-s2_i`,

`P_i = W1^-1(M_i+s1_i)-s1_i`.

Initial angular offsets can be absorbed by conjugating the corresponding arbitrary wiring. A phase that changes **when a step occurs** cannot generally be absorbed and is explicitly enumerated below. Wiring labels are not identifiable in every contact not visited by a message. Recovery tests must not require arbitrary unseen contacts to equal the builder's choice.

### RX2-O: odometer

`tau_i = floor((i+r)/n)`;

`s1_i = d1*tau_i`, `s2_i = d2*floor((tau_i+h)/26)`.

Domain: `n=1…4`, `r=0…n-1`, `h=0…25`, each `d_j` independently ±1, and 16 contact pairs. The slow rotor takes a step every 26 fast clock ticks; `h` records turnover timing. This explicitly defines the reverse-direction convention too; no mechanical double-stepping is implied.

Count: `16*4*26*(1+2+3+4) = 16,640` labeled structural settings, each with two free wirings. These include the n=1…4, positive-direction, zero-phase confounders used in R87. Some slow rotors do not turn during a particular 97-letter window; those rows remain in scope.

Internal review counted 1,016 distinct literal schedule arrays among the 1,040 clock labels (16,256 array/contact-pair combinations). The 32 labels with a stationary second rotor occur at n=4 and h=0 or 1, giving 512 labeled contact settings. The proposed experiment retains all labels; any later deduplication must be fixed before the experiment.

### RX2-D: two independent regular clocks

`s1_i=d1*floor((i+r1)/n1)`;

`s2_i=d2*floor((i+r2)/n2)`.

Domain: `n1,n2=1…4`, `r_j=0…n_j-1`, each direction ±1, and 16 contact pairs. Remove rows whose relative angle is constant across the entire 97-letter schedule. There are 400 raw clock rows; 20 collapse, leaving `380*16 = 6,080` labeled structural settings. This count is independently checked by executable enumeration and algebra: equality requires the same n, phase, and direction in this domain, giving `2*sum(n)=20` collapsing rows.

The union is at most **22,720 labeled structural settings**. It is not asserted to be a disjoint set of distinct cipher functions. Retaining duplicates is safe for exhaustive feasibility and is accounted for in whole-search statistical calibration. Free wirings are not a small finite-key brute-force task: there are `(26!)^2` labeled wiring pairs before equivalences.

**Phase caveat found in review:** removing the 20 equal-motion clock rows means removing them from this two-motion design, not declaring all of them excluded on K4. R87 used `s_i=d*floor(i/n)` without a boundary phase. Only eight removed clock rows (128 contact-pair labels) have r=0 and fall within that tested schedule. The other 12 rows (192 contact-pair labels) reduce to phase-shifted single-rotor schedules and remain **OPEN**. They require a separate RX1 phase audit if pursued. An angular starting orientation is absorbable; this step-boundary phase is not.

### Worked example, five-symbol toy alphabet

For q=5, use `W1=[2,4,1,0,3]`, `W2=[1,3,4,2,0]`, and RX2-O with n=1, r=h=0, both directions +1. Plaintext indices `[0,1,2,3,4,0,3]` encrypt as follows:

| Position i | Plaintext | s1 | s2 | Ciphertext |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 4 |
| 1 | 1 | 1 | 0 | 1 |
| 2 | 2 | 2 | 0 | 3 |
| 3 | 3 | 3 | 0 | 3 |
| 4 | 4 | 4 | 0 | 3 |
| 5 | 0 | 0 | 1 | 1 |
| 6 | 3 | 1 | 1 | 1 |

Both decryption equations recover the original sequence. This toy is unrelated to K4 or its published positions.

## 3. A complete feasibility test without two-permutation brute force

For an observed plaintext/ciphertext pair, define

`a_i=P_i+s1_i`, `b_i=C_i+s2_i`, `delta_i=s2_i-s1_i`, and `x_a=W1(a)`.

Then `W2(x_a_i+delta_i)=b_i`. Existence of both permutations is equivalent to:

1. Different observed `a` have different `x_a` (W1 is injective).
2. `x_a_i+delta_i = x_a_j+delta_j` **if and only if** `b_i=b_j` (W2 is a well-defined injection).

Equal-output equations connect the x variables by fixed differences modulo 26. A graph traversal assigns potentials within each component and detects inconsistent cycles. For each pair of components, the remaining distinctness constraints forbid particular differences between the two component offsets. Within-component collisions are immediate contradictions.

The remaining search assigns one offset in `Z_26` per component, with those forbidden differences. A global interface rotation adds the same constant to all x values without changing any constraint, so the first component offset can be fixed to zero. This gauge reduction uses no division and is valid for composite 26.

If a consistent assignment exists, the observed part of W1 is an injection and the observed part of W2 is an injection. Each can be extended to a permutation independently by pairing the unused inputs and outputs. Thus this test is sufficient as well as necessary for feasibility under a fixed structural setting. The implementation does **not** perform or emit those completions, assignments, keys, or plaintexts.

The checker returns **SAT**, **UNSAT**, or **UNKNOWN**. Exhausting a node/time budget is UNKNOWN. A SAT answer is only compatibility with the supplied constraints; it is not a recovered message, identifiable key, or positive cryptanalytic result. A family exclusion requires UNSAT for every structural setting and every allowed error relaxation, with zero UNKNOWN rows.

Since both schedules depend only on position, a wrong plaintext or ciphertext symbol changes one observed pair. A future one-error exclusion must examine every allowed single-equation deletion separately; it may not use the unrelaxed result alone. The model does not cover insertion/deletion, a lost stepping update, or letter-driven stepping, all of which can change later equations.

## 4. Executed synthetic validation

`test_synthetic.py` checks the optimized constraint reduction against enumeration of **every pair of wirings** in each toy case. The recorded `SYNTHETIC.json` reports:

- **9,416** exhaustive feasibility comparisons over alphabets of size 2, 3, and 4.
- **2,420** constant-relative-angle equivalence checks.
- **150** 97-symbol round trips, including composite alphabets 4, 6, and 26, with independently computed forward outputs and planted feasibility checks.
- Explicit cap-exhaustion, contradictory-observation, and empty-observation cases.
- Correct structural counts of 16,640 and 6,080.
- A development stress check: all **64** planted 24-observation instances were SAT; **10/64** random-pair instances were also SAT and 54 were UNSAT. The maximum search used 11 branch assignments.

The last observation illustrates why a surviving two-rotor setting is weak evidence. This small uniform-symbol development sample is not English solver power, a K4-specific p-value, or a prediction of the full catalog's null distribution. It uses randomly chosen synthetic positions, not the published K4 mask.

A separate internal implementation then challenged the kernel with **131,072** exhaustive q=4 cases, 200 q=6 cases checked by complete first-wiring enumeration, 200 observation-reordering/duplication checks, two nonunit-difference modulo-26 cases, 360 gauge transformations and 30 initial-angle checks. All passed in 1.259 seconds. See `INTERNAL_REVIEW.md` and its results. Both implementations are ChatGPT work; this adds adversarial mathematical checking without creating another independent-model vote.

Run the checks from the repository root:

```bash
python3 -I audit/run_bounded_agg.py \
  --manifest audit/backlog/multirotor/BUDGET.json \
  --log /tmp/multirotor-resource.json -- \
  python3 -I audit/backlog/multirotor/test_synthetic.py /tmp/multirotor-synthetic.json
```

This execution took 0.251 seconds under a 180-second wall / 120-second CPU / 512-MB cap. The sampled aggregate RSS missed the brief peak; the wrapper separately recorded a 12.4-MB per-process peak. Report those measurements with their actual meanings.

## 5. Executable bounds for the next experiment

These are complete proposed bounds for a future registration, not permission to skip G0–G4 or a claim that a blind solver is implemented. The present closeout stops after design and synthetic mathematical validation.

| Stage | Fixed scope | Hard cap | Stop / interpretation |
| --- | --- | --- | --- |
| Solver engineering | RX2-O first; 16,640 structural settings; choose and freeze a candidate-retention rule and scoring model on spent text only | 1,800 wall seconds, 1,800 CPU seconds, 2,048 MB aggregate RSS per development job; at most 3 declared development versions | A prototype that cannot recover planted truths stays SOLVER_NO_POWER; no K4 |
| Necessary power screen | True structural setting supplied; two wirings and 97-letter fresh text hidden; 20 plants in each n=1,2,3,4 stratum; represent slow-turnover cases in all strata and no-turnover cases where available (n=4) | 1,800 wall / 1,800 CPU seconds / 2,048 MB; one frozen solver attempt | Require at least 18/20 >=95 letters and consistent observed-contact keys per stratum; exact 97 separately reported; failure rejects that solver attempt |
| Full unknown-method gate | Search the full proposed catalog for every input; 20 fresh plants per accepted structural stratum; 200 wrong-family controls including R87/R89 single rotors, autokey, tableaux and shuffled texts | 3,600 wall / 7,200 CPU seconds / 4,096 MB; at most 2 workers, 8 retained candidates per input, zero reruns on revealed holdout | Require >=18/20 correct method-equivalence class and >=95/97 text per stratum, zero confident wrong-family controls; freeze candidates before truth; otherwise NO-GO |
| Blind target experiment, only after gate GO | One unchanged K4 ciphertext + 200 shuffles, identical complete search and retention for every input | Same 3,600 wall / 7,200 CPU seconds / 4,096 MB, at most 8 retained outputs per input | Commit and push all outputs and witnesses before published-letter evaluation; maximum-score null calibration over the whole search; no excluded-family claim from NO_SIGNAL |
| Separate post-freeze exact audit | At most 22,720 structural settings x 201 inputs = 4,566,720 base feasibility calls; no decoded plaintext output | 1,800 wall / 1,800 CPU seconds / 2,048 MB; 10,000 nodes per call and 20,000,000 nodes over the entire job | UNKNOWN is not UNSAT. If adding single-error relaxations, register their exact call count and budget separately before execution |

The final experiment registration must add actual immutable source/model hashes, fresh corpus hashes and sampling seeds, compiler/runtime details, numeric acceptance/abstention score cuts, and a measured throughput forecast. Those values cannot be honestly filled in before a blind solver exists. This document supplies finite engineering and execution boundaries; it does not fabricate solver readiness.

The prospective blind score is a whole-pipeline maximum: every null must undergo the same structural search and pruning. With 200 shuffles, the smallest add-one empirical p-value is 1/201. Do not treat one chosen structural row as a separate uncorrected test. A recovered wiring must re-encrypt the full 97-symbol output, but unobserved wiring contacts and algebraic gauges must be compared by induced behavior, not raw arrays.

## 6. Closure and remaining scope

The old multi-rotor **design task is closed** with two reversible finite models and a tested exact checker. The cryptographic hypotheses remain OPEN. The next actionable task is a power-tested RX2-O blind solver; RX2-D is a separately registered extension after the first solver passes. Three or more free rotors, irregular or plaintext-driven stepping, broader alphabets, masking, non-English models, and transposition are not tested here.

The current work supplies no K4 candidate and no two-rotor exclusion. The design is substantive because it removes a redundant equal-motion family, handles turnover phases explicitly, and replaces a potentially enormous two-permutation feasibility search with a proof-backed modular constraint test.

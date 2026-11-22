# R94 static source review before execution

Reviewer: ChatGPT. This is a **same-model internal source/mathematical review**
of ChatGPT's implementation. Independent execution review: **NONE**.
No tests, optimizer, candidate phase or diagnostic was run for this review.
No K4 computation or new experimental outcome is asserted.

## Files and scope

Read `PREREGISTRATION.md`, `run_all.py`, `structured.py`, `selftest.py`,
`reference.py`, the QA/source receipts and protocol manifest. Compared the
model header with `r91/model_build/build_lower4.py`, and archived row schemas
with the original panel builder and v2/v3 run/score writers. This checks the
planned source behavior, not its actual future runtime or recovery rate.

| Reviewed source | SHA-256 |
| --- | --- |
| `r94/PREREGISTRATION.md` | `2e1cdfac3c11251d0062763926034a7a2b36a4c786a1773d543ca3f8789a30d4` |
| `r94/run_all.py` | `a01b60af02041a2a2be60cea52954fc02d37be81b0bd14a82ba38f4cc05c6d2b` |
| `r94/structured.py` | `9cbf65a0085c0dfc4bb29e7d9538c30de5eabc4421e49ba88b85fc295cf48329` |
| `r94/selftest.py` | `a50aa258bfe117678dbc3c118aa4c20cb24c65b38d26872687d6a8af7cb1da62` |
| `r94/reference.py` | `502ae7ff0ed26547fef753251613393ac377fbde72c62dab24567a1756f24aac` |

## Mathematical findings

The inverse-wiring orientation is correct:
`P=U[(V[C+s2]-(s2-s1)) mod26]-s1`, followed by the input-alphabet map.
Given V, positions sharing the same U input contribute additive row costs;
given U, positions sharing the same V input do likewise. Each whole-block
unigram maximization is therefore the declared linear assignment. The
implementation retains the old permutation on ties and checks matrix-score
agreement and nondecrease within the frozen tolerances.

For order 4, the one-entry counterfactuals are correctly distinguished from
legal candidates. The assignment maximizes their additive surrogate, not the
true joint order-4 objective. Full assignment moves, individual permutation
cycles and fallback transpositions remain legal permutations; acceptance uses
their actual order-4 scores. `inverse(current)[proposed]` has the correct
orientation for those replacement cycles.

The normalized factorization `G_delta=H^delta F`, with `F=W2 W1` and
`H=W2 T_1 W2^-1`, is correct. H is a single 26-cycle. Its use here is a
structural check, not an additional hidden optimizer or identifiability claim.
The full-operator and interface-gauge diagnostics have the correct orientation.

## Truth order, bounds and schemas

`verify_environment` explicitly defers reading/hashing the designated truth
file. Candidate phases use the ciphertext/structure panel and public models.
Both A and B files are closed and hashed, and the hashes are written to
`UNKNOWN_OUTPUTS_BEFORE_TRUTH.json`, before the runner reads and parses truth.
B's trigger depends on completion and correctness, not recovery against truth.
This is the declared ordinary-filesystem read-order convention, not an
operating-system isolation guarantee.

The loop limits support 384 final states per unknown-wiring version,
96 conditional states per diagnostic version and at most 48 best-neighbor
states: 1,008 newly computed saved states, below 1,100. Retention views repeat
existing final states rather than introducing new proposals. The stated
12,288 A assignments, 18,432 B block updates, 2,304 conditional B updates,
31,200 true-key neighbor scores and at most 1,015 scored strings per B block
agree with the finite loops. This arithmetic is not a throughput benchmark.

The model header/layout and the panel, truth and archived result field names
match their source writers. Phase checks and the single aggregate wrapper
retain the planned INCOMPLETE handling. No likely first-invocation schema or
mathematical blocker was found by inspection.

## Safeguard corrected before publication

The initial outer exception handler could write `INCOMPLETE.json` into an
already existing output directory after the runner refused a repeat. The
updated source creates the directory exclusively, sets
`ATTEMPT_STARTED_HERE` only after that succeeds, and writes a failure report
only when that flag is true. Static inspection confirms a refused invocation
can no longer alter earlier failure evidence. The correction was made before
source publication or execution, and no attempt was consumed by this review.

**Disposition:** no remaining static blocker to the one registered invocation.
Actual self-checks, resource compliance, output integrity and recovery must be
established by that invocation and its later review. This note creates no
formal gate pass, K4 authorization, cipher exclusion or independent execution
promotion.

Signed: ChatGPT — static internal review only.

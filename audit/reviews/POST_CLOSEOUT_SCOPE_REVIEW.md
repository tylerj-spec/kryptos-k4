# Post-closeout scope and next-step review — 21 November 2026

Affected ledger IDs: L180

Validation: Read-only source and evidence review against merged main
`c16c4ad11c92391377f7347a70d88a5c02710fa5`; comparison of the R91 linked-tableau
model with R83's implemented LX domain; mathematical review of the prospective
RX2-O gate, phase domain and model overlap. No new experiment, K4 computation,
solver retry or historical replay was performed in this review.

Independent review: NONE for the historical R83/LX execution and the new
prospective planning refinements. ChatGPT performed the source-containment
review and internal adversarial design review. This note does not promote L172,
L180 or any new exclusion. The prior signed independent reviews of R32, R41 and
R90 remain valid within their existing scopes.

## 1. Previously requested closeouts remain complete

PR #102 merged the full R32 recount, complete R41 feasibility replay,
independent R90 exact review, R91 supplied-structure gate decisions and rotor
design package. All four PR workflows passed, and the main-branch guardrail
run 44971199777 passed on the merge commit. The latest read-only consistency
check found no scientific reason to reopen those closeouts.

R32 does not claim comparison with missing historical lower histogram bins.
R41 does not claim replay of the original violation histograms. R90 does not
claim an independent rerun of original language-model optimization. R91's
failed solver gates are not family exclusions. The earlier current work-order
file was stale; its original body is now explicitly marked historical.

## 2. R91 linked tableaux are contained in R83 LX

For every R91 linked key K, set x[j]=AZ_index(K[j]) and map it to R83 as:

```text
conv = ("AZ", "KRY", "AZ", "AZ", +1, +1, +1, "AZ", "AZ")
x    = AZ indices of K
m,w  = identical to R91
d    = +1
rot  = 2
```

Both references then use `a_i=i mod m` and
`b_i=(i+floor(i/w)) mod m`, with encryption:

```text
mid_i = KRY[(AZ_index(P_i) + x[a_i]) mod26]
C_i   = AZ[(AZ_index(mid_i) + x[b_i]) mod26]
```

R83's key renumbering is identity for AZ/AZ, and its convention enumeration
retains that identity. Its LX loop scans m=2..20, w=2..48, both rotation
signs and either rotated stage. This contains all 18 R91 linked strata and
all six proposed short-key follow-up branches. R91's primitive-key restriction
only narrows R83's unrestricted key domain.

Primary references: `r91/reference.py:linked_encrypt`,
`r91/PREREGISTRATION.md` Arm L, `r83/models83.py:lk_slots,lk_pi,lk_encrypt`,
`r83/exact83.py:lk_conventions,lx`, and `r83/PREREGISTRATION.md`.

The archive (`r83/RESULT.md`) reports that all LX structural settings had at
least five checks and that the only EXACT survivor had m=20. None of the R91
key lengths equals 20. The later `r83/audit/REPLAY_EXACT.md` reports a complete,
separately coded K4 LX replay of 96,112,640 settings with zero disagreements;
its independent-model review is explicitly NONE. Its LX shuffle replay was
sampled, and its LX DROP/SHIFT steps were not replayed.

The inherited EXACT conclusion assumes in-place alignment, correctly carved
and transcribed ciphertext, and correct published plaintext letters; this
review does not relax those assumptions.

Therefore the proposed m=3/4 gate is **not new K4 coverage**. Its 120/120
supplied-structure recoveries remain useful benchmark evidence. This finding
withdraws that proposal as the next solving priority; it does not retrospectively
invalidate R91's power results, independently certify R83's execution, or
create an error-tolerant, transposed, masked or broader-family exclusion.

L180's OPEN language means that R91 itself adds no cipher exclusion. It must
not be read as erasing an older, explicitly scoped archived exclusion. The
ledger gains that clarification without a status promotion. Do not use the
archived surviving setting to choose a new blind key or branch.

## 3. Prospective rotor gate corrections

The old proposed four n-strata pooled materially different turnover regimes.
Use eight future cells: n=1 with 3/4 slow turns; n=2 with 1/2; n=3 with 1/2;
n=4 with 0/1. Twenty controls per cell gives 160, with the prospective
>=18/20 top-ranked, >=95/97-letter recovery bar in every cell. This is a
prospective refinement before any rotor holdout exists, not an amended
experimental result. Exact 97/97 and any-of-eight candidate recall remain
separate diagnostics.

Two arbitrary rotors can have unidentifiable decomposition and unused contacts.
In n=4/no-turnover cases, h=0 versus 1 and either d2 give the same slow schedule;
a static W2 also absorbs output-alphabet relabelings. Freeze operational
behavioral-equivalence rules; do not grade those raw labels as recoverable keys.

RX2-O also contains n<=4 single rotors when W2 is identity. A correctly
recovered RX1-generated control is overlap/cross-family recovery, not a false
positive solely because its source generator was called RX1. Confident wrong
plaintexts and unsupported exclusive RX2 identifications are errors. The
full gate needs a frozen overlap/abstention rule and separately reported
negative and overlap panels before it can run. Positive top-ranked recoveries
must also pass the confidence cuts; an all-abstention classifier cannot pass.

A 160-positive/200-challenge full gate scans 5,990,400 labeled O branches.
The 7,200-CPU-second ceiling allows about 1.20 ms per labeled branch, averaged
over the entire job; this is a budget calculation, not observed throughput.
The solver and any ciphertext-only pruning must demonstrate feasibility on
development data before registration. No claim is made that such a solver
already exists.

## 4. The phase gap is deliberately narrow

The 192 labels exposed by the two-motion collapse are only n=2,3,4 with
r=1..n-1, d=+-1 and 16 contact pairs. Across n<=96, nonzero phases instead
number 145,920. Once phase is allowed, n>=97 can still place one step within
the 97-letter window. Do not generalize the n<=4 repair or the old zero-phase
monoalphabetic shortcut to those deferred domains.

The immediate phase work order is synthetic only. No phase survivor, partial
wiring, clue-dependent score or completed key may enter RX2 candidate generation.

## 5. Disposition

- Keep R32, R41 and R90 closed at their independently reviewed exact scopes.
- Keep the two R91 solver decisions closed; retain all frozen evidence.
- Park narrow R82 as a new target; retain benchmark value and require a genuine
  model difference before a new hypothesis receives compute.
- Park the unchanged PTAK solver. Diagnose optimization, retention and scoring
  on spent controls before proposing a materially different implementation.
- Prioritize bounded RX2-O solver engineering and parallel synthetic phase work.
- Follow `audit/NEXT_STEPS.md`; no new K4 run is registered by this document.

Signed: ChatGPT — internal source/mathematical review; no new experiment.

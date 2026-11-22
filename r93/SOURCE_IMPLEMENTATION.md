# R93 source package and implementation checks

Preregistration and mode clarification were published at
`567f418961cc18847207008468679115074f4c93` before this source package.
No target input has been read by the R93 work.

## Code separation

- `checker93.cpp` evaluates the pairwise inconsistency-edge theorem and emits
  a bounded per-setting bitfield. It has no plaintext decoder, key-completion
  function, file input, or language model.
- `reference93.py` is a synthetic reference only. Its event-countdown clock,
  explicit contact rotation, inverse lookup and complete-permutation toy
  enumeration do not call the production criterion.
- `scope93.py` independently enumerates normalized finite schedules. Its counts
  reproduce the analytical accounting in the registration.
- `runner93.py` compiles the kernel, checks output lengths, and accumulates
  counts as Python integers. Per-setting bitfields remain in a pipe/memory;
  no compatibility bitmap is saved or supplied to another research process.
- `validate93.py` implements the registered correctness gate and a separately
  labeled development smoke mode. The target driver never imports it or the
  reference decoder.
- `run_target93.py` verifies immutable preregistration/source/gate commits and
  successful gate resource limits before reading target or observation data.
  It emits the 201 aggregate records and provenance, with interpretation held
  until a separately published output freeze.

The target kernel's full-catalog mode is also challenged with the first and
last registered synthetic settings. The reference-generated truths must be
accepted at their exact known label indices. These checks instantiate the
registered maximum/boundary positive-acceptance requirement through the same
bulk code path used by the target. Additional 24-observation conflict examples
exercise omission bits 22 and 23 and the no-single-deletion case. They do not
alter a gate bar, domain, seed or budget.

## Honest use of the legacy QA field

The existing schema insists that `resource_budget.max_candidates` be positive,
even in crib-assisted mode. The manifest therefore uses an unused upper ceiling
of **1**, together with the stricter binding fields
`max_decoded_candidates: 0` and `max_surviving_setting_outputs: 0`.
Actual zero candidates satisfy both bounds. `max_aggregate_records: 201` is a
separate limit; aggregate records are not renamed candidates. The driver checks
all of these fields and requires all 201 expected input IDs in its output.
No guardrail code was changed.

## Development evidence and formal gate

The scope-only calculation completed under its development cap. The initial
smoke check passed in 1.503 seconds wall and 1.293 seconds CPU, using 94.6 MiB
sampled aggregate RSS. It covered a small toy subset, boundary plants, the
worked example and one full-catalog synthetic scan. The source receipts in
`dev/SMOKE.json` identify that development snapshot; subsequent additions of
the bulk-boundary checks, target driver and stricter provenance checks are not
misrepresented as having already passed the formal gate.

The formal gate must run only after the complete source/protocol package is
published. Its 141,793 exhaustive toy cases, 8,832 plants, error checks and
three-input benchmark then provide the actual GO/NO-GO evidence under the
registered caps. A correctness or completed forecast failure gives NO-GO;
an infrastructure, source-integrity or resource failure is INCOMPLETE.
Both block the target. No formal validation or target retry is automatic.

All source hashes, including the aggregate wrapper and the published-observation
source, are in `PROTOCOL.sha256`. No target-derived file is part of this package.

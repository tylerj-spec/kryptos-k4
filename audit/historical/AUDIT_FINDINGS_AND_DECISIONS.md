# K4 historical evidence audit — first complete structural inventory and targeted independent mathematical checks

**Date:** 15 November 2026
**Main branch audited:** d368262385fe1c7c5caa311abb96f9b8f26be777
**Status:** FULL LEDGER PROVENANCE INVENTORY + SELECTED INDEPENDENT CRYPTO CHECKS. **NOT** a replay/independent mathematical certification of every historical round.

## What this audit actually did

1. Parsed every populated K4 ledger row while respecting inline-code pipes and escaped Markdown separators, preserved the original row and source claims, and assigned each a **provenance triage** class without rewriting any historical conclusion.
2. Inspected every tracked SHA-256 file, splitting the main 57 protocol/K4/holdout manifests from 58 secondary or historical manifests, and checked every identifiable claim against the current committed file bytes.
3. For SHA-256 claims that mismatched the present working tree, inspected the version in Git at the hash-manifest introduction commit, then earlier file history. Reported any remaining mismatch separately rather than silently treating a current-file mismatch as tampering.
4. Checked documented preregistration-versus-freeze/output Git ancestry in 16 rounds with identifiable traditional artifacts, examining 43 output relationships.
5. Independently implemented the post-freeze logical consistency checks for foundational ledger rows L01-L04, with a separately planted synthetic positive/negative regression and SHA-256 verification of the original K4 ciphertext.
6. Triaged earlier scientifically consequential methods and known errata, distinguishing numerical bugs, failed blind gates, crib-conditioned checks and insufficient mathematical review.
7. Added reproducible GitHub Actions checks and evidence artifacts. Every output is marked **structural** or **post-freeze crib-assisted**. No known K4 plaintext enters any candidate generator, and this PR builds no K4 plaintext candidates.

## Complete ledger inventory (all 170 populated rows)

- Rows: 170 distinct entries, from L01 through L172; L151 and L156 are unused rather than duplicated.
- Provenance classes are disjoint: **51** generic legacy C/G/G/C source fields, **62** rows lacking an explicitly recognized file path, **51** rows with a tracked file reference but not independently replayed in this audit, and **6** rows with unresolved inline references after resolving seven relocated top-level R30/R32 paths under k4kit/.
- These classes are **index quality**, not a statistical verdict. A row with a generic source can be correct; an explicit file citation does NOT make its cryptographic conclusion correct.
- Full machine-readable per-row source provenance, actual references, original status, and audit-pending flag is in the Actions artifact INVENTORY.json. No legacy EXCL was promoted to a verified exclusion automatically.

## SHA-256 provenance: 115 manifests / 8,762 recorded claims

| Population | Manifest files | Digest claims | Match present file | Unresolved or ambiguous | Different present file |
|---|---:|---:|---:|---:|---:|
| Primary protocol / K4 / holdout frozen | 57 | 611 | 510 | 101 | **0** |
| Other historical / development / archive SHA-256 | 58 | 8,151 | 8,076 | 54 | 21 |
| **Total** | **115** | **8,762** | **8,586** | **155** | **21** |

**The 21 differences at HEAD were investigated against Git history:**
- 14 match the exact file version **at the manifest's introduction commit**.
- 3 match an **earlier version in Git history**, but NOT the file as it existed when the manifest was introduced. Specifically these are R64, R66 and R68 *development* freeze manifest references to preregistration versions; a reviewer must decide whether those development artifacts are properly linked to the intended protocol.
- 3 refer to the older top-level **R33 delivery manifest**, for which the script could not establish a manifest-introduction commit; the original R33 handoff documents changed over time. Their historical contents and provenance remain unverified, not presumed malicious.
- 1 is the **k4kit/MANIFEST.sha256 self-reference**, which cannot be accepted as a meaningful self-integrity check without independent version provenance. This is a document-integrity defect, not a demonstrated alteration of K4 ciphertext, solution or freeze data.

No primary protocol/holdout/frozen artifact with a uniquely resolved file path showed a different SHA-256 at HEAD. The 155 ambiguous/unresolved claims remain unverified; don't infer that they match or mismatch. The 8,586 verified hashes establish **byte identity only**, not that algorithms, model assumptions or findings are correct.

## Git freeze chronology

**43 of 43** checked output/freeze artifact relationships in **16 rounds** have preregistration introduction committed before their respective output introduction. This is positive procedural evidence. It does NOT establish that the preregistration was final and unchanged at the freeze date, that holdouts were truly concealed, or that a solver never accessed a crib. R64/R66/R68 preregistration version drift illustrates why a time-order check alone is insufficient.

## Independent scoped cryptanalytic verification: L01-L04

An implementation independent of the archived L01–L04 checker, in audit/historical/postfreeze_baselines.py, uses the **original K4 ciphertext and the published 24 letters only in a separately labelled post-freeze checker**. The K4 target digest is compared against R83's frozen manifest. Synthetic regression checks an ordinary plaintext/key-derived 97-symbol sample and a deliberately wrong plaintext letter.

- **L01 pure permutation:** EXCL in the literal whole-message permutation model. The published letters already require three E symbols; K4 ciphertext contains only two. This reasoning does not rule out an additional symbol-changing stage.
- **L02 fixed monoalphabetic substitution:** EXCL. One input ciphertext letter maps to contradictory known plaintext letters at multiple positions. This does not rule out position-dependent substitution or transposition.
- **L03/L04 in-place periodic formula:** For plain and cipher alphabets each selected from A–Z, KRYPTOS, PALIMPSEST, ABSCISSA; both signs; periods 1..26, exactly **832 labelled configurations** were independently checked for a consistent periodic key vector. Only one survives: **plaintext tableau ABSCISSA, ciphertext A–Z, additive sign +1, period 26**. This is the already recorded **compatible but SCORE-only** case, not a solution. Other **831** configurations contradict the 24 published letters under the stated in-place assumptions.
- This is a **crib-assisted conditional exclusion** only, NEVER a blind discovery, and says nothing about periods >=27, alternative alphabets, two stages, changing spelling, or unknown position routes.

Reproducibility: GitHub Actions prints the model counts and stores BASELINE_EXCLUSIONS.json next to the historical inventory. No plaintext candidate or fitted key is emitted.

## Independent ciphertext-only cryptanalytic verification: L167 (R78)

The R78 self-keying assumption is a single stage with the key being an arbitrary **reordering of exactly the plaintext letters**, with both plaintext and key numbered by the same alphabet. The entire plaintext is used once as the key; arbitrary *different* plaintext and key alphabets are outside scope.

A separate standard-library checker, audit/historical/ciphertext_invariants.py, computes the sum of ciphertext indices modulo 26 for the four ciphertext charts without looking at **any known plaintext clue**. With signs (s,t), summing all 97 equations cancels the permutation: the sum is zero when s+t=0 (Beaufort and variant), and is twice the plaintext-index sum when both signs are +1 (Vigenere), hence even.

The verified K4 ciphertext yields **AZ 7, KRY 12, PAL 7, ABS 14**, independently reproducing L167's necessary conditions. Thus:
- **Exact scope EXCL:** Beaufort/variant for all four named ciphertext charts, for every permutation under this precise self-key construction.
- **Exact scope EXCL:** Vigenere with AZ/PAL ciphertext charts.
- **OPEN:** Vigenere with KRY/ABS ciphertext charts; and all different plaintext-vs-key chart constructions.

Synthetic validation uses **14,400** independently generated planted expressions across six message lengths, four tableaux, and three operations. The L167 check is **ciphertext-only**, not crib-assisted, and never decrypts or fits a key. The original R78's separate T-RK statistical language claim is *not* revalidated.

## Confirmed mathematical/software defects in high-impact ledger claims

### P0 — R83a plaintext-error check, L172: PR #82

The original WPX/PFX **DROP** operation removed one ciphertext equation while still using the allegedly incorrect plaintext letter to advance the plaintext-dependent key or future feedback. Independent synthetic plants with one wrong **plaintext** letter proved the true setting could be falsely rejected. The post-freeze conservative WPX replay leaves **260** structural settings not eliminated when one published plaintext letter may be wrong (across all choices of suspect position). These are *necessary-only survivors*, **not** complete decryptions.

**Disposition:** Withdraw the former universal one-bad-plaintext-letter WPX exclusion and treat PFX's original 17 DROP survivors as nonexhaustive. The all-24-letters-correct EXACT WPX check is a different claim and was not disproved by this defect. Original R83 frozen files must remain unchanged. Corrective draft PR #82 contains the erratum, tests and ledger L172 correction.

### P0 — R75 F1X integer overflow, L165 and reused in L172: PR #83

The original NumPy int64 product of connected-component root counts can overflow at high underdetermination and enter a catastrophic candidate-enumeration path. Independent synthetic tests (small brute-force oracle and 26^17 assignments) confirmed the risk and the correctness of an entirely separate arbitrary-precision, feasibility-only graph checker.

**Disposition:** Do not trust overflow-sensitive counts/decode branches without replay. This is not proof that the existing graph feasibility outcomes or R75 blind NO_SIGNAL are wrong. Corrective draft PR #83 adds code, tests, L165 qualification and an additive erratum; originals remain immutable.

### Additional evidence-scope issues, not new code defects

| Source | Recorded fact | Audit consequence |
|---|---|---|
| L117 / R32 | 1,200 stored outputs were independently re-encrypted and score-replayed; the reported 7.10-billion-setting whole-family enumeration was **not independently rerun** | Retain bounded output integrity; classify exhaustiveness as UNVERIFIED until separate enumeration |
| L143 / R52/R52b | Published K4 plaintext was used to select the method/key before a later solver ran without the clues | Keep labelled **CRIB-CONDITIONED**, NEVER evidence for blind discovery |
| L136 / R42 | Blind alphabet-recovery gate had **4/6** success for a subfamily and was declared failed | Do not treat weak/failed blind solver as an exact cipher-family exclusion; separately justified crib-assisted exact results require their own check |
| L165 / R75 | Fixed family had a passing synthetic blind gate; F1X post-freeze can have underdetermined settings and legacy int64 overflow | Do not conflate blind NO_SIGNAL, post-freeze algebraic feasibility, and overflow-affected decode counts |
| L172 / R83a | 51 EXCL / 10 CHANCE is the **historical, uncorrected breakdown** | Requires reclassification after PFX/WPX DROP correction; exact/no-error cases separately |
| R80a / two-stage | Sealed synthetic recovery gate passed; **no K4 attempt was made** | Do not invent a negative K4 ledger result |
| R79/R81a and similar | Published letters can produce precise after-freeze algebraic exclusions for limited families | Validity is scoped to exact enumerated alphabets, key lengths, carving, and crib positions; not a global "cipher impossible" conclusion |

## Second-pass hostile reviewer checks

**Builder asks:** Are the model, reversible equations, key domains, reset convention and original ciphertext present? A reused algorithm or letter model is not automatically independently validated.

**Breaker asks:** What simplest counterexample falsifies the exclusion? Try the last and first key slot, modulus-26 nonunits, identical key aliases, a single wrong PLAINTEXT symbol with future-state propagation, a different letter tableau, or an omitted source file. A chance-level crib-compatible witness is not a K4 solution.

**Auditor asks:** Were protocol, solver, model, holdouts and files SHA-frozen before K4 and before known letters were checked? Were wrong-family controls processed by the exact same complete search? Did resource limits prevent runaway enumeration? Can an independent implementation prove the *whole* claimed exclusion rather than one stored decode?

A single assistant carrying out these three roles is **not equivalent to genuinely independent Anthropic/Google/OpenAI review**. Sentry01/AgentCouncil's independent-model workflow was prepared in R82, but it has NOT been executed in this environment. This audit therefore records reviewer independence as an explicit outstanding requirement.

## Stop/go decisions and follow-up audit queue

**Before any new K4 search:** Review and merge prospective guardrails in draft PR #81 (manifest, resource caps, freeze separation, synthetic power, independent audit). Resolve P0 #82 and #83; both fix findings that could otherwise lead to false exclusions or expensive runaway jobs.

**Highest priority replays:** 
1. Independent EXACT one-unknown-plaintext-letter stateful check for **PFX/WPX**, compared with toy exhaustive correctness and full-limit controls, before reclassifying L172 DROP.
2. Bounded full-tableau/key-length independent graph feasibility replay of **R75 F1X**, including period 15–18 and the two R83 shuffled cases, before saying L165/L172 exact counts are independent.
3. Resolve R64/R66/R68 dev prereg protocol-version drift and the three old R33 delivery files. Do not alter their source SHA manifests; add release/version notes.
4. Recover exact work product references for the **51** generic-source ledger rows and identify original scripts/results/parameter bounds; don't rewrite broad old EXCL as "verified" without reproduction.
5. In descending risk order, independently replay each historical **high-impact EXCL** with an unrelated checker and toy exhaustive controls. Begin with broad transposition+periodic, arbitrary-alphabet and R83 exact checks; record the precisely tested family and known-plaintext assumptions.
6. Review low-power K4 NO_SIGNAL claims and failed synthetic gates to ensure they do not suppress viable methods. Score/count results from a code path that saw known letters must not train a future blind solver.

**Scope boundary:** This delivers a machine-readable review of ALL 170 ledger rows, all tracked SHA-256 manifests, a 43-case commit-order audit, and independent baseline L01-L04 tests, plus separate confirmed repairs in PRs #82/#83. It does NOT claim to have independently re-executed every historic 97-letter ciphertext search, all 11,576 repository blobs, or the reported billions of candidate configurations. Those remain future independent replay obligations, not certified conclusions.

## Evidence locations

- Executable structural scan: audit/historical/scan.py
- Deterministic toy Git + hash tests: audit/historical/tests/test_scan.py
- Independent scoped K4 postfreeze baseline: audit/historical/postfreeze_baselines.py
- Independent ciphertext-only L167 invariant: audit/historical/ciphertext_invariants.py
- Workflow: .github/workflows/historical-evidence-audit.yml
- Downloadable Actions artifact: INVENTORY.json, SUMMARY.md and BASELINE_EXCLUSIONS.json from the successful workflow run associated with this PR
- Companion corrective PRs: #81 future guardrails; #82 R83 PFX/WPX false-exclusion correction; #83 R75 F1X overflow safety

**No K4 solution found or claimed. No original sealed result has been modified.**

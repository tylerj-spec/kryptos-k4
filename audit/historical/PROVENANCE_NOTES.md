# Provenance loose ends (T4, audit/NEXT_STEPS.md), 15 Nov 2026

Documentation only. No file named here was changed, and no manifest was "fixed".

Inputs:
- `python3 -I audit/historical/scan.py --out <dir>` at this branch's base (3591a29);
- `audit/historical/resolve_refs.py` (new: content search for unresolved references), output
  `audit/historical/RESOLVED_REFS.json`;
- `git log` / `git show` as cited.

## 1. R64, R66, R68: development freeze manifests hash an earlier preregistration revision
**Finding.** In each round, `rNN/dev/FROZEN.sha256` records the hash of the **draft** preregistration, the version
the development run was made under. It was committed together with the **final** preregistration, which replaced the
draft's placeholders.

The K4 run of each round used the final preregistration:
- its hash is the one in `rNN/PROTOCOL.sha256`;
- that hash equals the file at HEAD;
- the commit precedes the K4 target and freeze commits.

| Round | Draft (hash in dev/FROZEN) | Final preregistration (hash in PROTOCOL.sha256 = HEAD) | K4 target, K4 freeze |
|---|---|---|---|
| R64 | 1f8d8c2 (9f4b53f4…) | 4b4c770 (349aa9b8…) | 3ef217e, efc5ad0 |
| R66 | 7ac240c (57a39303…) | 59d0f63 (03bd4048…), then **Amendment 1** in e3e5610 (01679570…, = PROTOCOL and HEAD), after the gate and before the K4 target | a704f02, 02db45c |
| R68 | 68cf7f8 (d256ae5c…) | 648ac72 (0a1ac8bf…) | bfcefa9, cd02a27 |

**What changed between draft and final** (`git diff <draft> <final> -- rNN/PREREGISTRATION.md`):
- **R64** (+49/−9):
  - fills `DEVELOPMENT_RECORD_PLACEHOLDER` with the development results;
  - fills `GATE_BARS_PLACEHOLDER` with per-model gates (CLOCK ≥ 5/6, GERMAN ≥ 4/6);
  - changes the K4 rule from "only if the gate passes" to "only if at least one model passes", deciding per model.
  - That is a scope and gate change, made from development only, before any holdout existed.
- **R66** (+27/−4):
  - fills the development record and the gate bar (14/20);
  - search settings (30 × 1M annealing) are recorded as fixed from development.
  - Amendment 1 (e3e5610) adds a secondary all-rotation measure, after the gate and before the K4 target. The primary
    rule is unchanged.
- **R68** (+86/−1):
  - fills the development record;
  - fixes restarts at 20 (the development run used 6);
  - adds the whole holdout-gate section (bars PER ≥ 3, GRO ≥ 5, CTAK ≥ 5, PTAK ≥ 2 of 6), the K4 rule, the contender
    screen and the post-freeze exact check.
  - The draft had none of these, so they were set after development, before any holdout.

**Reading.** This is the intended draft → development → final sequence, not drift after the K4 run. The
development freezes correctly point at the protocol their runs used. Each K4 run is covered by its final
preregistration. Parameters, cuts and scope changed only between draft and final, and only from development
evidence. Caveat: in all three rounds the draft and the development freeze were committed by the same agent within
minutes. The order is shown by commits, not by any external timestamp.

## 2. R33 delivery manifest entries without an established match at introduction
`R33_DELIVERY_MANIFEST.sha256` was introduced in 14a12d4 (28 Oct 2026, 00:50).
- **`HANDOFF.md`, `LEDGER.md`:** the current scan finds both match their versions at 14a12d4
  (`MATCH_AT_MANIFEST_INTRO`). They were edited on purpose later, as `README.md` says.
- **`README.md` (6178927d…): NOT FOUND.**
  - The root `README.md` was first committed in 25de8db (28 Oct, 17:45), after the manifest.
  - No version in Git history has that hash. `R32_handoff_original.zip` has no README.
  - So the README that R33 delivered was never committed in that form, and its content cannot be verified.
  - Nothing frozen depends on it.

## 3. `k4kit/MANIFEST.sha256` lists itself (known defect, not fixed)
Introduced in 14a12d4. It lists `./MANIFEST.sha256` (8e0b87b0…). A file cannot contain a correct hash of itself, so
that line can never verify. It is a document-integrity defect, not evidence of alteration. Two other lines also do
not match the current files:
- `./CLAUDE.md` (c134ad8b…) matches `k4kit/CLAUDE.md` inside `R32_handoff_original.zip`. That is the delivered
  version, edited on purpose since.
- `./LEDGER.md` (21981831…) matches no Git version and not the zip's `k4kit/LEDGER.md`. NOT FOUND, unverifiable.
  The ledger moved to the root and has been edited in place since, by design.

## 4. The 101 unresolved primary hash references (`RESOLVED_REFS.json`)
Searched by content: every tracked file, every file in `R32_handoff_original.zip`, and every past Git version of a
same-named file.

| Outcome | Count |
|---|---|
| Resolved: a tracked file has exactly the expected hash | 18 |
| Resolved in Git history only (an earlier version of a same-named file) | 4 |
| Not found | 79 |

**All 79 not found are untracked build products or downloaded inputs, never committed:**
- compiled solvers: `rk_solve`, `rk2_solve`, `hom_solve`, `keyed_solve`, `r70bin_rk_text_scan`;
- built language and key models: `lm6.v2.bin`, `lm6_de.bin`, `lm6_clock.bin`, `de_words.tsv`, `clock_words.tsv`;
- R70's five downloaded source texts.

They cannot be verified from the repository. One consistency check is possible and passes: every round names the
same model file with the same hash.
- `lm6.v2.bin` b1a2a3c7… in all 44 references;
- `lm6_de.bin` 5451a6ce… in 10;
- `lm6_clock.bin` 160afe9e… in 6.

So **22 of 101 now verify by content**. The other 79 would need the original build environment or a rebuild that
reproduces the same bytes.

Independent review: NONE (one model).

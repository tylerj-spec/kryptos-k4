# R70 Erratum 1 (Claude Code, 7 Nov 2026): label the exhaustive block check as crib-assisted

**Labelling only.** No R70 number, file or conclusion changes. Nothing was re-run.

- **What was raised:** ChatGPT's audit in PR #58 flagged R70's sealed `exact_scan.cpp`. After the freeze, it tested
  every one of the 5.7 × 10⁸ settings against the 24 published letters.
- **R53's rule:** under `r53/BLIND_RULES.md`, a check like that is a **crib-assisted consistency check**.
  - It may stand in the record with that label.
  - It is not part of a blind result.
- **R70's two results, labelled correctly:**

  | Result | What it used | Label |
  |---|---|---|
  | **NO SIGNAL, 0 contenders** | Blind ranking, frozen and verified before any published letter was read | Blind (R53-compliant) |
  | **No full published block for any of the five texts** | All settings checked against the published letters after the freeze | **Post-freeze crib-assisted exclusion** |

- **What the check did and did not do:**
  - It was only ever used to *reject*. As its pre-registration states, a surviving setting would have been reported,
    not promoted to a candidate.
  - It is still not independent blind evidence, and the ledger row L159 now says so.
- **Scope of the label:**
  - R66 Part B (`r66/sealed/hom_feas.cpp`) and R68's `r68/sealed/exact.py` used the same post-freeze procedure and
    carry the same label in substance.
  - Their ledger rows (L155, L157) are not edited here, to keep this change clear of open PR #50's ledger edits.
  - They should be relabelled the same way when convenient.

# R84 Amendment 1 (17 Nov 2026): diagnostic script crash fix, before any diagnostic or K4 output

At this point:
- nothing had been run on K4;
- no diagnostic output existed;
- the target was committed (e1abbc6) but not yet given to any solver.

**What happened.** The pinned robustness diagnostic `r84/sealed/ct_error84.py` stopped with `KeyError: 'ok'` when
building its items. The rows of `r80a/holdout/GATE.json` for the negatives have no `ok` field. It wrote nothing.

**Change.** `r84/sealed/ct_error84_v2.py` (sha256 7f9875fff67aa20fa4be867ee54569836345a2b63412659e5a786cf6ad16c737) is identical except for one line: it reads the field with
`r.get("ok")` and `r.get("fam")`.
- Seed (840500), items per family (3), selection rule, corruption rule and scoring are unchanged.
- The original file is kept unchanged, as pinned in `PROTOCOL.sha256`.
- The diagnostic remains reported, not gated. Nothing in the K4 run, its rules or its scripts changes.

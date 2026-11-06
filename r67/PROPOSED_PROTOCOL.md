# R67 review history — superseded by the frozen preregistration

**This was the initial review proposal. The controlling plan is now [PREREGISTRATION.md](PREREGISTRATION.md) with its [PROTOCOL.sha256](PROTOCOL.sha256).**

The original proposal remains available in the PR #50 commit history (first version: c5948da). It contained three mechanical gaps identified in Claude's review and a now-outdated caveat about the power of the R65b German-key-fragment test. The later correction on main (PR #51, aff9109) is authoritative: **high-power statistical rejection, not an exact mathematical exclusion**.

The final protocol addresses the three review items:

1. **Isolation:** [stage_blind.py](sealed/stage_blind.py) creates a 13-file, checksum-verified read-only stage containing only blind ciphertexts, necessary R65/R64 runner source, R63 solver source and binary, the two model registries, language/word models, routes and the legacy R65 protocol. The complete repository, published K4 plaintext, sealed truth, postfreeze evaluators, and clue-conditioned files are not available to the solver.
2. **Source integrity:** [build_sources.py](sealed/build_sources.py) pins SHA-256 for both English Gutenberg sources and Europarl. English is drawn from R64 holdout books; German from unseen Europarl file 10. All streams are ASCII-normalized before [make_controls.py](sealed/make_controls.py) verifies the source manifest. No arbitrary development text may enter production.
3. **Full hash verification:** [REFERENCE_SHA256](REFERENCE_SHA256) pins all ten original R65 stage-1 dependencies, including the exact binary and both letter models. [verify_controls.py](verify_controls.py) checks the frozen dependency/result hashes, stage allowlist and every raw witness against independent forward encryption; [analyze_controls.py](analyze_controls.py) refuses to open synthetic truth without a passing verifier and the frozen results digest. The R67 protocol SHA is separately recorded in the control manifest.

Two additional review choices were fixed **before scores**: keep 192 IC-matched nuisance controls plus 24 positives, without an unmatched second run; report matching-selection bias and accepted key parameters; report best/second scores and SNAKE_L minus SNAKE_R using the existing ten routes. Do not add a carved-order solve. These choices and limitations are frozen in the preregistration.

**Current authorization:** review-only branch and PR; no production control run, K4 decryption, issue #35 activation, external checker or merge is authorized by this document.

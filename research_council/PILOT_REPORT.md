# AgentCouncil logic pilot — report (2026-11-09)

## Actual result: portable protocol smoke test PASS; genuine multi-model council NOT RUN

The host environment offered the GitHub repository connector, but no GitHub Copilot CLI `task` tool or separately callable Anthropic/Google/OpenAI subagents. AgentCouncil's native 3-family workflow therefore **could not be executed here**. Rather than fabricate three answers or claim a model consensus, this pilot implemented and tested reusable deterministic orchestration logic only.

### Implemented and tested locally

- Three distinct independent review prompts were produced from one curated, source-typed R75 brief, **without any K4 ciphertext or published plaintext**.
- A deterministic, anonymized mapping (`A=beta, B=gamma, C=alpha`) prevents the orchestrator from seeing model family labels in its prompt, assuming reviewers also omit self-identification.
- A synthetic fixture progressed through `prepare -> triage -> attack -> verdict`. All review texts in this fixture were obviously artificial placeholders, **not independent AI output**.
- Manifest SHA-256 verification detected tampering of a frozen prompt; stale/duplicate outputs were refused.
- Structured known-text fields and unapproved source paths were rejected. The code refuses to treat one model family in three seats as diverse. This is schema checking, not a security boundary.
- `python3 -I research_council/tests/test_review.py`: **PASS** under local Python 3.13.5 (no third-party modules needed).

### R75 review finding supported by previous code inspection (not a council verdict)

R75's 2,880 defined period-40 transformations are reproducible algebraic objects, and the draft reports a 60/60 known-family, technical-prose recovery smoke test. Neither establishes that a change of tableau is historically supported or distinguishable from many other cipher families on 97 letters. The different-alphabet assumption should be **LOW PRIORITY / exploratory** until a synthetic hidden-family test gives a measurable, calibrated likelihood advantage. Avoid confusing a successful generator-and-decoder round trip with ciphertext-only identification of K4's method.

### Next action for Claude

1. Read this package and R75 [draft PR #67](https://github.com/tylerj-spec/kryptos-k4/pull/67).
2. In a genuinely restricted workspace, run the three prepared prompts on three **actually different** model families; freeze raw first-pass outputs and actual provider/model roster.
3. Run anonymized adversarial triage, challenge the leader, preserve minority objections, and retain a final attributable verdict with a citation or reproducer for every claimed mathematical bug.
4. **Measure information gain:** count reproducible novel flaws/fixes missed by the existing review. Do not use panel-of-agents consensus as evidence K4 is solved. If no material findings appear, terminate the council pilot and do not mandate it for future rounds.
5. Only request a separate approved synthetic holdout if the review establishes genuine method-identification power. **No automatic K4 run, change to R53, clue-assisted fitting, or repository merge.**

Upstream design inspiration: [Sentry01/AgentCouncil](https://github.com/Sentry01/AgentCouncil), MIT license, copyright (c) 2026 Shlomi Shaki. No upstream source was copied.

# Research Council pilot for Kryptos K4 (AgentCouncil-inspired)

**Scope: read-only experiment-review aid, not a cipher solver or an AI model execution engine.**

Inspired by [Sentry01/AgentCouncil](https://github.com/Sentry01/AgentCouncil), an MIT-licensed GitHub Copilot CLI plugin by Shlomi Shaki. This implementation independently expresses the useful *process concepts*: independent first drafts, different model families, anonymized triage, adversarial challenge, evidence-based ruling, and hashed review artifacts. No upstream source code or plugin has been copied; the external plugin is optional.

## What is implemented

`review.py` (Python standard library only):

1. `prepare` — accepts **only** the curated `method_review_only` JSON schema and a fixed allowlist of source paths from R75. Emits three **independent** prompts, each with identical facts and a distinct review focus, plus SHA-256 hashes for each generated artifact. It refuses existing output directories.
2. `triage` — records three externally supplied responses and an operator-reported model roster; requires three distinct claimed model families; freezes response hashes and writes an anonymized, re-ordered `Response A/B/C` packet. It **does not run models or independently verify their identity**.
3. `attack` — after an external orchestrator selects the leader and consensus state, generates challenges for two non-leading responses when disagreements remain. The untrusted peer answer is labeled as evidence, never executable instruction.
4. `verdict` — after externally supplied critiques, prepares a final evidence-based adjudication prompt. It does **not claim** that a verdict has been rendered until an external model actually supplies one.

`tests/test_review.py` exercises the complete state machine with deliberately artificial reviewer text. It also tests immutability and input-schema rejection. The tests do NOT make model calls, decrypt K4, or inspect published known text.

## Prepared pilot: R75

- `briefs/r75.json`: tightly curated facts/questions from [draft PR #67](https://github.com/tylerj-spec/kryptos-k4/pull/67), with evidence levels; no clue strings or original K4 text.
- `pilot_r75/phase1/{alpha,beta,gamma}.md`: **ready-to-send independent prompts** for three different model families. Keep each response hidden from the other two reviewers until all three are complete.
- `pilot_r75/manifest.json`: SHA-256 freeze manifest for the curated brief and three prompts; `seats` is empty because no models have been invoked in this environment.
- `PILOT_REPORT.md`: the actual offline pilot findings and the remaining steps for Claude.

Run the identical preparation yourself from the repository root:

```bash
python3 -I research_council/tests/test_review.py
python3 -I research_council/review.py prepare \
  --brief research_council/briefs/r75.json \
  --out /tmp/r75-council-new
```

In GitHub Copilot CLI with AgentCouncil installed, run **three separate first-pass prompts** under the respective model families, or use the native AgentCouncil full adversarial protocol with the single sanitized brief. **Do not assume Copilot CLI can constrain the repository or web access just because the prompt says read-only.** The safer option is to give each reviewer **only** the generated prompt and separately vetted source files in a restricted working directory, without mounting known-text files or giving broad repository/network browsing permissions.

After independently collecting model responses in `alpha.md`, `beta.md`, `gamma.md`, create a roster file:

```json
{
  "alpha": {"family": "anthropic", "model": "ACTUAL_MODEL_ID"},
  "beta": {"family": "openai", "model": "ACTUAL_MODEL_ID"},
  "gamma": {"family": "google", "model": "ACTUAL_MODEL_ID"}
}
```

Then:

```bash
python3 -I research_council/review.py triage \
  --out /tmp/r75-council-new --roster roster.json \
  --alpha alpha.md --beta beta.md --gamma gamma.md
# Ask an EXTERNAL orchestrator to read phase2/triage.md and report LEADER and CONSENSUS.
python3 -I research_council/review.py attack \
  --out /tmp/r75-council-new --leader A --consensus partial
# Supply externally generated two non-leader challenges, e.g., attack_b.md / attack_c.md.
python3 -I research_council/review.py verdict \
  --out /tmp/r75-council-new --attack-b attack_b.md --attack-c attack_c.md
# The final prompt is phase4/verdict.md. Execute it with an actual orchestrator.
```

If the leader is B or C, provide the two attack files associated with the other letters. If consensus is `full`, there are no attacks and `verdict` takes only `--out`.

## R53 threat model and non-goals

**Strict blind integrity is higher priority than multi-agent consensus.** The workflow does not open K4 ciphertext, published known plaintext or clue-position data. It uses only curated review notes. It never writes into the solver and never invokes a candidate generator. Responses and triage artifacts must remain review-only; **never feed them to a K4 solver as keys, scoring hints, candidate text, or constraints.** An independent method idea from this review is only a *new hypothesis* and must pass the normal novelty check, sealed synthetic controls, full output freeze and independent postfreeze validation.

**Limits of the safeguards:** `review.py` enforces an exact structured input schema and vetted source-path allowlist, not content-level information-flow security. It cannot verify what a remotely run model was exposed to, the truth of a claimed model ID, whether a reviewer browsed other files or whether peer responses carry untrusted prompt injections. You must enforce actual filesystem/network isolation **outside** this script and manually inspect the curated brief. Hashes prove that local artifacts did not change **after preparation**; they do not prove a model was isolated. The generated review packets alone do not grant authority to run K4 or merge any experiment PR.

## What would make the pilot worthwhile?

The council must identify at least one **material, independently reproducible issue or improvement** missed in the existing R75 review, such as an exact equivalence counterexample or a better method-hidden synthetic diagnostic. Count novelty *after* verification, not raw number of suggestions, apparent agreement, or confidence language. Compare value against extra provider cost and token use. If reviewers only repeat that the model is unproven, the correct result is **NO ADDITIONAL VALUE**, and the council should not become mandatory.

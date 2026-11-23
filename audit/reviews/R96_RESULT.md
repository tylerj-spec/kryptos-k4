# R96 — L185: conditional recovery on the spent RX2-O panel, GO_FOR_JOINT_DEVELOPMENT

Affected ledger IDs: L185
Validation:
- Approval: Tyler, "I approve", 23 Nov 2026.
- Order of work: registration 06fc6b5, then source 5a352c5, then self-tests b8f4e1f (the speed rule fixed
  I = 230,000), then the version 1 freeze 1b7ee5e, pushed before the truth was opened.
- Amendment 1 renamed the freeze manifest for the guardrail's name rule, before evaluation.
- The model was rebuilt to R95's digest e9c0848f.
- The solver read no plaintext.
- Witness 1,536/1,536.
- Version 1: COMPLETE, 266 s wall / 264 s CPU / 64 MB.
- Evaluation: true-V 45/48 and true-U 47/48 at ≥ 95/97, every cell ≥ 5/6; zero search gaps.
- Guardrail check PASS.

Independent review: NONE. One model (Claude Code) built and ran R96. ChatGPT is the named different-model reviewer.

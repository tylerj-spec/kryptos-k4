# R95 prospective manifest-stage correction

Date: 22 November 2026 (America/Chicago).

The pre-execution repository guardrail check on initial source commit
`f81ceaf79e41f161efb41a3127ba9afdf6ecb194` rejected the QA manifest's
`stage: preregistered_development`. For rounds without K4 output, the adopted
schema permits only `preregistered` or `gate`.

Before any primary run, score comparison, or scalar verification invocation,
the stage is corrected to `preregistered`. The mode, scope, fixed model,
endpoint, inputs, source algorithms, budgets and zero-retry rules are
unchanged. The descriptive development designation remains explicit in the
preregistration, hypothesis and `NOT_A_GATE_DEVELOPMENT_ONLY` field.

This is a prospective source-metadata correction permitted by the registered
pre-execution correction rule. The initial publication remains in Git history;
the protocol is regenerated and republished before execution. No experiment
output exists to overwrite and no data-dependent decision was made. No
guardrail code or adopted policy is changed or bypassed.

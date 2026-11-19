# T6 item 3 (part 1): independent replay of R40 (L134) and R42 (L136), 19 Nov 2026

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY REPLAY.** Nothing was decrypted and no original file was changed.
The plan was pushed before any K4 run (`REPLAY_ONEFREE_PLAN.md`).

## In plain words
R40 and R42 claimed something about keyed ciphers where **either** alphabet is completely free (any of 26!
orders), with keys from chain addition (every primer) or from the Carter or K1–K3 texts: none can put the 24
published letters in place. A separately written checker now confirms this. It reproduces every archived number
exactly, including which settings come closest. It also finds every planted test message.

## Result (`REPLAY_ONEFREE.json`)
| Round | Settings per ciphertext | Ciphertexts | K4 | Nulls | Plants | Equal to archive |
|---|---|---|---|---|---|---|
| R40, free plaintext alphabet | 337,634,136 | K4, 4 nulls, 6 in-place plants | 0 consistent, min V 6 | min V 7, 7, 7, 8 | all found at V 0 (1–3 consistent each) | **11/11** |
| R42, free cipher alphabet | 171,294,872 | K4, 2 nulls, 6 plants | 0 consistent, min V 5 | min V 8, 5 | all found at V 0 | **9/9** |

"Equal" means four things match: the setting count, the consistent count, min V, and the complete list of settings
at min V. All archived lists are complete (at most 19 entries).

## Validation (`tests/test_onefree.py`, all pass)
- A pure-Python reference computes V by brute force over pairs, with a constructive bijection test.
- Fresh plants in both modes and all key types, from an independent encryptor, are found at V = 0.
- Every listed minimum is re-verified by the reference.
- Inside the kernel, every 997th setting is re-counted by brute force, and any mismatch aborts. None did; for
  example, 338,651 checks on R40's PLANT_00.

The job ran under `audit/run_bounded.py`: COMPLETE, 146 s, 47 MB.

## Scope and status
- **Not covered here:** R41 (L135, substitution then route transposition, 1.09 × 10¹⁰ settings). It gets its own
  plan and a sampled replay. R42's blind gate failure (4/6) is a separate matter and is unchanged.
- **Status under guardrail rule 10: replayed, one model.** Not promoted.

**Independent review: NONE.** One model did this work.

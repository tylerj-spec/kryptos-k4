# T6 item 2: independent replay of the R79 and R81a keyword exclusions (L169, L170), 18 Nov 2026

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY REPLAY.** Nothing was decrypted, no keyword was completed and no
original file was changed. The plan was fixed and pushed before any K4 run (`REPLAY_KW_PLAN.md`; its rule-count
typo was corrected before running).

## In plain words
R79 and R81a claimed that eight families of one-stage keyword ciphers cannot produce K4's 24 published letters, for
any keyword up to 12 letters. R81a claimed the same with any one of those letters wrong. A separately written checker
now confirms both, setting by setting:
- the same counts as the archives everywhere;
- every setting is constrained by at least 12 independent checks, so these exclusions are strong, not marginal.

## Result (`REPLAY_KW_COMPARE.json`)
| Replay | Ciphertexts | Settings per ciphertext | Comparisons | Disagreements |
|---|---|---|---|---|
| All 8 families: exact, drop-one, drop-one by position | R81a target: K4 + NULL_000–009 | 4,358,880 | 88 | **0** |
| R79's 4 families: feasible by checks | R79 target: K4 + NULL_000–009 | 1,333,760 | 44 | **0** |

- K4 and all 20 shuffles: 0 settings feasible, 0 drop-one-feasible, in every family.
- Minimum checks of any setting: **12**. That confirms "every setting ≥ 12 checks".

## Validation (`tests/test_replay_kw.py`, all pass)
- **Slot rules:** all 982 R79 rules and 2,919 R81a G4 rules equal the originals' encryption-side state machines
  (11,703 rule–ciphertext pairs). That is a different path from the vectorised `slot_map` the original checks used.
- **Streams and counts:** the K1–K3 streams equal R79's. The setting counts equal the pre-registered totals for all 8
  families.
- **Brute force:** feasibility equals exhaustive keyword search through the originals' `decrypt()` on toy lengths, all
  8 families.
- **Plants:** at keyword length 12, plants are feasible. With **one wrong plaintext letter** (ciphertext re-enciphered
  from the altered text), all 24 plants were flagged at exactly that position.

## Resources (`audit/run_bounded.py`, `T6_BUDGET.json`, COMPLETE)
| Run | Wall time | Memory |
|---|---|---|
| R81a target | 89 s | 19 MB |
| R79 target | 37 s | 19 MB |

## Scope and status
- **Covered:** the keyword families' exact and drop-one exclusions, as pre-registered.
- **Not covered:**
  - R79's H11 (route-keyed plaintext, 1 anchor-only match at 3 checks);
  - R81a's G5X (one unknown keyword alphabet, 77,229 orderings).
  These are separate checks.
- **Status under guardrail rule 10: replayed, one model.** Not promoted to INDEPENDENTLY VERIFIED. Promotion needs a
  named independent reviewer.

**Independent review: NONE.** One model did this work.

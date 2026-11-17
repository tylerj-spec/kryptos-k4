# R83 T1 WPX strength erratum — stale constraint counts after a plaintext correction

Date: 16 November 2026. Classification: CONFIRMED POST-FREEZE STATISTIC-DEFINITION DEFECT.

Preserve all original R83 and T1 frozen output, result files, SHA manifests and numerical survivor inventories.

## Defect

The R83 T1 exact one-wrong-PLAINTEXT-letter checker correctly re-enumerates all possible replacement letters and repropagates the walking-key state. However, its effective-strength count is not recomputed.

In r83/audit/exact_drop.py, wpx_scan first computes

    ck = wpx_checks(pos, pk, alpha, e, d, m, R)

using the unmodified published letters (pk). It then tests each altered plaintext with wpx_mask(pos, alt, ...) and reports checks=ck and eff=ck.

Changing a plaintext symbol in WPX also changes the later pointer residues in its published run. Thus it can change the number of collided key slots. A witness feasible only after the alteration may have fewer independent key equalities than the archived statistic assigns it.

This does NOT falsify T1's two structural WPX survivor settings or its corrected state propagation. It does falsify their reported strength of eff 4.

## Independent post-freeze fixed-setting verification

The standard-library checker r83/audit/wpx_strength_recheck.py independently implements the reported settings and first SHA-verifies the original K4 ciphertext against the R83 frozen manifest. It reads the published plaintext only inside the post-freeze verifier. It enumerates all 25 possible alternate letters and all 26 possible free second-run pointer offsets for each of the two existing WPX settings. It emits NO alternate letter, completed key, decoded plaintext, or pointer offset.

Both settings: plaintext alphabet ABS, cipher alphabet KRY, additive sign, stepping alphabet PAL, e=1, ring length m=26; d is either +1 or -1.

| 0-based changed position | d | Archived checks under original plaintext | Checks under unique feasible corrected-letter witness |
|---|---|---:|---:|
| 25 | +1 | 4 | 1 |
| 25 | -1 | 4 | 1 |
| 28 | +1 | 4 | 2 |
| 28 | -1 | 4 | 2 |

Therefore neither unique structural setting has a feasible one-error witness with at least 3 genuine key-equality constraints. They remain *not excluded*, but their former eff4 designation is unsound.

## Synthetic controls and reproducibility

- 48 fresh, 97-letter reversible synthetic WPX ciphers, equally divided between d signs, with one altered published PLAINTEXT character: all true settings retained.
- The plants show an explicit counterexample to the assumption that strength is invariant when a plaintext-driven pointer state changes.
- The K4 post-freeze test covers every possible alternate symbol and every free offset for each of the two reported surviving settings, with original ciphertext hash verification.
- CI: successful run https://github.com/tylerj-spec/kryptos-k4/actions/runs/43883630778 .
- No original R83 frozen data, program or output is modified.

## Required correction

For L172, preserve the count of **two structural settings**, but correct the T1 WPX DROP effective-strength claim to **1–2 actual independent constraints** in feasible witnesses. Their support is weak; they do not satisfy the intended effective-strength >=3 bar. They are not a K4 lead, and their survival is not evidence of the method.

The original comparison "12/20 shuffled controls reach eff >=4" was computed with the same stale-plaintext strength definition. It is not a valid calibration of the corrected statistic. No corrected null p-value has been computed yet. The T1 PFX one-error check, no-error WPX EXACT, and independently replayed R83a T6 result are distinct and unaffected.

## Required follow-up

1. Declare the recalibrated strength: number of repeated key-slot constraints under each *feasible* altered letter and state trajectory (for example, maximum and minimum over feasible witnesses, with the choice fixed before seeing null results).
2. Run exactly the same statistic over all scanned WPX structural settings on K4 and each of the 20 R83 shuffled ciphertexts. Correct for searching many settings and possible suspect positions.
3. Independently examine other stateful error-tolerant tests whose strength is scored using a potentially incorrect plaintext symbol. Do not count a stale-cycle label as a full contradiction.

Status: POST-FREEZE AUDIT / NO K4 SOLUTION / NO CANDIDATE.

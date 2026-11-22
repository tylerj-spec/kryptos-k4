# R32: independent recount of all 7,099,791,216 settings

Affected ledger IDs: L114, L115, L117
Promotes: L114, L115
Validation: Independent expected-key equations, 78,732 exhaustive toy comparisons, independent route reconstruction, compiled-versus-scalar synthetic checks, boundary plants, and a complete bounded recount. Every retained archived total, maximum, cumulative count and full-match count agrees; every archived maximum-setting witness is independently verified.
Independent review: YES ChatGPT, reviewing the original Claude Code implementation. Same-model ChatGPT subtasks are one review, not several independent models.

## Conclusion and scope

The finite exclusions represented by L114 and L115 are independently verified. None of the **7,099,791,216 labeled settings** matches all 24 published letters. The missing aggregate recount identified by L117 and `AUDIT_NOTES.md` is now complete. L117's earlier ChatGPT review of retained rows is historical context, not a separate independent target being promoted here.

This remains a post-freeze, crib-assisted exact exclusion under the original ciphertext, published positions and letters, fixed alphabets, key sources and route domains. It makes no claim about free alphabets, other key sources or routes, spelling repairs, ciphertext errors, or the probability of a cipher family. Labeled settings include equivalent and duplicated transformations; they are not independent statistical trials.

| Archived job | Settings recounted | Maximum letters matched | Full 24-letter matches |
|---|---:|---:|---:|
| F1 CARTER | 556,605,504 | 10 | 0 |
| F1 K1K3 | 1,985,712 | 8 | 0 |
| F1 G5 | 49,200,000 | 9 | 0 |
| F1 C6 | 492,000,000 | 10 | 0 |
| F2 G5 | 6,000,000,000 | 11 | 0 |
| **Total** | **7,099,791,216** | **11** | **0** |

All cumulative counts at thresholds 8, 9, 10, 11 and 12 also agree exactly. The evidence is `audit/backlog/r32/REPLAY.json`.

## Independent mathematics and implementation

For a fixed alphabet pair and operation, each known plaintext symbol implies one numeric key value at a known key position. With cipher index `c` and plaintext index `p`, the expected key is respectively `c-p`, `c+p`, or `p-c`, modulo 26, for Vigenere, Beaufort and variant Beaufort.

For substitution then transposition, the ciphertext position is the inverse-route position and the key index remains the plaintext position. For transposition then substitution, both ciphertext and key use the inverse-route position. The identity uses the original position. The independent kernel counts equality with these required key symbols; it neither reconstructs nor emits K4 plaintext.

The numeric keystreams are generated independently from every 5/6-digit chain primer and every pinned text window, direction and numbering. An independent coordinate-sorting constructor reproduces the route permutations. The checker imports no original solver. Synthetic tests use the historical route constructor only as an oracle comparison, as permitted by the audit rules.

Every histogram counter is bounded above by its declared setting count, below 2^63. The driver independently derives all aggregate counts with Python integers. No number of arbitrary alphabet completions is calculated.

## Archive limitation, disclosed before the recount

The original `WHOLE_FAMILY.json` retains totals, maxima, one maximum witness, the full24 list, and cumulative counts at thresholds 8–12. It does **not** retain the full original histogram. The prospective `ARCHIVE_FORMAT_AMENDMENT.md` therefore fixed the comparison to every retained statistic before this recount. The review publishes new full 25-bin histograms; it does not claim byte equality for historical bins 0–7 that were never available.

The archived maximum-setting witnesses are checked only at the 24 published positions. No new crib-derived candidate or completed unknown key is produced.

## Provenance and verification

- Plan, kernel, helper, budgets and synthetic outcome committed and pushed before the target: `dea5bb84ec983b3d7fc978e11efeebe7f0fd72df`.
- Final target driver and archive-format clarification committed and pushed before the target: `b23e1bcc12119707fb699d81ae6d71c63ce0c376`.
- The driver checks the published source bytes against these commits, verifies source and canonical ciphertext hashes, and rebuilds the pinned kernel before execution.
- `audit/run_bounded_agg.py`: **COMPLETE**, 37.431 seconds wall, 13.598 seconds aggregate CPU, 134.7 MB sampled aggregate peak RSS, against limits of 1,800 seconds wall, 1,200 CPU seconds and 2,048 MB.
- No target retry, parameter change, disagreement or target survivor occurred.
- An initial synthetic route-comparison failure was retained in `SYNTHETIC_INITIAL_ROUTING_INCOMPLETE.json`: the test initially compared the S-then-T subset with a mixed-order archive file. The comparator was corrected before the prospective commit and before any target recount. The actual generated S-then-T permutations were unchanged.

Result SHA-256: `b43a4c604dc29691d282f779a009ef915c63f4bf4294d604679e190975760fc9`.

This closes the whole-family aggregate recount. It does not rerun the historical blind optimizer or change its original evidence.

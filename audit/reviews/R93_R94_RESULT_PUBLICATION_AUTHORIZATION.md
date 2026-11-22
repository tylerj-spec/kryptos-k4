# Approval scope and provenance for the R93/R94 result publication

Affected ledger IDs: L182, L183
Validation: Explicit current-conversation approval; public repository/source blob metadata; registered artifact lists and cryptographic output manifests.
Independent review: NONE. This records publication authority and provenance, not an independent scientific review.

## Explicit approval already received

The assistant's immediately preceding approval request to the user was:

> Please explicitly approve publishing this R92–R94 review/source bundle and the specified registered experiment artifacts to the public `tylerj-spec/kryptos-k4` repository, then running the bounded work and merging after review and required CI pass.

The user's next message on 22 November 2026 (America/Chicago) was:

> I approve

This explicitly includes the specified registered experiment artifacts, not only the earlier source bundle. The delivered APPROVAL_SCOPE.md likewise named publication of the specified synthetic/gate/aggregate/result artifacts to the same repository. No additional destination or disclosure category is being introduced.

Automatic review allowed the approved source and gate publication, then rejected creation of the result commit on the stated premise that approval covered only source. This note supplies the exact existing approval and concrete artifact provenance for supported re-review. No alternate publication route or bypass was used; R93 interpretation remains deferred until the result commit/ref is published.

## Destination and input provenance

GitHub's repository API was checked again and reports `tylerj-spec/kryptos-k4` as public. Its current follow-up ref is `2621a5e0d64fe787c498cc765f7ee14dd78af1ee`, the R93 gate publication. The source commit is `3e781d57994a617610db943ea57438759dc6b4ce`.

The inputs are already public in that source commit:

| Input | GitHub-verified public blob |
| --- | --- |
| `r94/inputs/PANEL.tsv` | `3c9ee7df9c33cd831471f72ba407c1bff9471e09` |
| `r94/inputs/PANEL_TRUTH.json` | `92c7d4a3c987607fa249eb98024794f4e2b8c6f2` |
| `r39/ic_gate/k4_ciphertext.txt` | `9596fe1add3ff17dcc17226e9db5e117f7b463f9` |

R93 publishes the public K4 ciphertext and fixed-seed shuffles, compatibility counts, source hashes and resource metadata. Its registered driver emits zero plaintexts, wiring completions or surviving-setting lists. Its aggregate file contains no decoded K4 message.

R94 publishes development candidates generated solely from the existing public synthetic practice panel, plus counts, synthetic true-wiring diagnostics, timestamps, hashes and resource summaries. These are toy cipher permutations and generated letter strings, not account credentials, private communications or private real-world plaintext. The historical source logs and practice truths were already public in this same repository. No model binary, environment variables, authentication material or unrelated files are included.

The 1.47 MB size is principally the retained synthetic candidate states and diagnostics required by the registered experiment. It does not indicate a private-data collection. All source and output membership is explicit and hash-bound.

## Exact registered result payload

These are the 21 result-stage files; this authorization/provenance note is an additional document. They implement the output lists already specified in the approved R93/R94 execution handoffs. The frozen artifacts remain byte-for-byte unchanged.

| Artifact | SHA-256 |
| --- | --- |
| `r93/QA_MANIFEST.json` | `997d4a1e72fdd0687ab8df6b84029ee876fc2c3f2a04d8f10f07a3266fea9413` |
| `r93/TARGET_RESOURCE_LOG.json` | `74516856e0984ffa8866d5159b19a2521058516b4f5f9d0c96684e518d47b817` |
| `r93/k4/INPUTS.tsv` | `fbc28710cfba45278f9c34fada0c212e622d17df766b8e82029ec1b6fdad9610` |
| `r93/k4/AGGREGATES.json` | `8022f709941ff2d37771bf2363d12d11f48ea69420dddbe7039a9f213b8e0ee0` |
| `r93/k4/SOURCE_RECEIPT.json` | `b270bddbaf804db322775238fa205eac772919aa28a40c4ee3cae0421a7ea943` |
| `r93/k4/FROZEN.sha256` | `090a511691ed4166c4a438b4cf6ecbff4cd660bfa99c02af650976cd3fc55477` |
| `r94/RESOURCE_LOG.json` | `fbdf9f7beb1d3de6e9b731b3dad171fef30ca2804f36f7e2f95d788da4dbf7e6` |
| `r94/development/ARCHIVED_REPLAY.json` | `062f35016a495416b7c27675c3f71f917313f45657930f4180c8cea841d515cc` |
| `r94/development/CONDITIONAL_DIAGNOSTICS.jsonl` | `85ff09d1e8a416d2153f8b8b57bdb58c01abf635c09c9dc7fbc1842243a3145c` |
| `r94/development/CONDITIONAL_SUMMARY.json` | `4417863229549e0124f1aea39532dd80b7bbc278ca5c0a361b753c02f18e6e26` |
| `r94/development/EVENTS.jsonl` | `01f13427700830f8e322cadc9d6e07d3e4fc6a0d6b03d1a75a0fac3f6d424c62` |
| `r94/development/OUTPUTS.sha256` | `5e56976da2600d716a85a2e37da60417b1d70ca2cbaba77c401a241aefac23dc` |
| `r94/development/RECOVERY.json` | `749d824f8777cf9babda34c5df03b58e6f9e1c39fbcd79584b6d5ff2e6e7237c` |
| `r94/development/RESULT.json` | `50e36763864b29d31e55022bef01b5959fd670804b8ee4bc0d6f18ec7e90a4cb` |
| `r94/development/TESTS.json` | `4bdfacaa13d79f2a98f8dbb7237e9c0fb102c36ed1614025856f6f146e4ae3a4` |
| `r94/development/UNKNOWN_OUTPUTS_BEFORE_TRUTH.json` | `3a203542d2a030c7aceafd0a56a4754b4c9940fe8f3a9e94cb6bdf544d23da35` |
| `r94/development/VERSION_A.jsonl` | `2d718e0dd36393f07da5a169911965998a354fb0949ec86dbd1d3c3889c0a136` |
| `r94/development/VERSION_B.jsonl` | `c984e830b5b1c29d191bb9e95bef67d031f0d6326479f21674db111ea9360ec2` |
| `r94/audit/EXECUTION_RECEIPT.json` | `fa22d199a7506d3602a835b8bcc86b8fbf95e443dcdd45ffaed5c53b6d145398` |
| `r94/audit/RUN_FROZEN.sha256` | `5edd758e098240bede205b3c34dee1c5168ac9252793ebcf559a128614f2626a` |
| `r94/RESULT.md` | `e893cdf2748bada0ff300103b04a5d1bd8af9c2f01bac62b0803e392db160735` |

R93 gate and target, and R94 development, all completed within their original fixed resource caps with zero retries. This note does not interpret R93's numerical counts or claim that the result freeze has already been published.


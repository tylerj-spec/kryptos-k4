# R92–R94 publication provenance

Affected ledger IDs: L181
Validation: GitHub repository and PR #104 metadata; public file blob identifiers;
byte-for-byte comparison of the two copied practice inputs with their public
baseline objects; explicit inventory of the new audit/source payload.
Independent review: NONE. This is publication provenance, not scientific promotion.

## Destination and task authorization

The requested work continues the user's Kryptos project and the merged PR #104
that the user identified. GitHub's repository API reports
`tylerj-spec/kryptos-k4` as **public** with default branch `main`. GitHub's PR #104
API reports merged=true and merge commit
`9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`, exactly matching the user's quoted
`9e4bd40` baseline. Both PR head and base repositories are this same repository.
This publication continues the already published follow-up branch; it creates
no new destination and changes no repository visibility or access controls.

Sources checked:
- https://api.github.com/repos/tylerj-spec/kryptos-k4
- https://api.github.com/repos/tylerj-spec/kryptos-k4/pulls/104
- https://api.github.com/repos/tylerj-spec/kryptos-k4/contents/audit/backlog/multirotor/solver/dev/panel?ref=9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1

## Public synthetic inputs

These files contain generated cipher-test keys and practice text, not account
credentials, personal records or secret K4 plaintext. The proposed copies are
byte-identical to the existing public baseline. Their blob IDs were independently
retrieved from GitHub's public directory response and matched to local Git objects.

| New copy | Existing public source | Verified Git blob | SHA-256 |
| --- | --- | --- | --- |
| `r94/inputs/PANEL.tsv` | `audit/backlog/multirotor/solver/dev/panel/PANEL.tsv` | `3c9ee7df9c33cd831471f72ba407c1bff9471e09` | `9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c` |
| `r94/inputs/PANEL_TRUTH.json` | `audit/backlog/multirotor/solver/dev/panel/PANEL_TRUTH.json` | `92c7d4a3c987607fa249eb98024794f4e2b8c6f2` | `27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf` |

## Other artifacts

The new R92 report contains compatibility counts, synthetic check counts, hashes,
resource measurements and saved-evidence arithmetic derived from the existing
public R92 record. The large JSON size comes principally from enumerated
exact/deletion results. It is not a collection of private conversation text or
credentials. The R94 historical resource review summarizes logs already present
in the same public repository. Newly written source files, finite budgets,
mathematical notes and generated synthetic smoke data implement the work the user
requested. The original language-model binary is not part of this upload.

The source package was paused after automatic publication review flagged the
bundle as possible sensitive egress. The checks above establish the destination
and the public byte identity of the copied plaintext/test-key data before a
supported re-review. No alternate upload route or publication bypass was used.

## Exact proposed artifact inventory

This inventory identifies the 31 reviewed artifacts; this provenance note is an
additional document. No hidden filesystem files or unrelated project data are
included.

| Path | SHA-256 |
| --- | --- |
| `r92/audit/independent_review/REVIEW.md` | `ac1f161056efef42fbd30d3bb1ddf8bf2a850f92ac21e0891c64fdf27c39f3eb` |
| `r92/audit/independent_review/REVIEW_RESULTS.json` | `dcc0f936262fff82e749acbc8a7a04f200cc806e1f7ef5d46fac68ee21d9bec4` |
| `r92/audit/independent_review/REVIEW_RESOURCE_LOG.json` | `e56a6cf8d452b6e2c682f7b2d1e471b87458a56f70e0ca5f60edcb42526da7d5` |
| `r92/audit/independent_review/SCOPE_CORRECTIONS.md` | `8e3b33fad2648b9ae391edf6a0feff2789a4e84ea3ebb3ed074153b49e2f2db0` |
| `r93/checker93.cpp` | `b8e43b14543cb899726e17910016ef34219d2ff2b4f21adbb66c7602d519d21d` |
| `r93/reference93.py` | `909eca37a15db831ce4b1be566c7ed575cdd82c56d2826abe2ee123a26d5a850` |
| `r93/scope93.py` | `2183055a4b1d747185d71dae4fc8da17954eea2316ebcbd7c16ea240c298ac50` |
| `r93/runner93.py` | `cc45fb0b8afdb5740a3c71165e1c849aceca4a37e1c513b53fc7e24564b6a424` |
| `r93/validate93.py` | `d2d998a63fdb7874f003dc4f78d0dff6abe4cf8358ec8512ae90ab60aa33383a` |
| `r93/run_target93.py` | `8e92c59581abd8a59675bd0d7459dc8be8fc41baab07cae5afc442d7a3e226fe` |
| `r93/VALIDATION_BUDGET.json` | `4b6ea28ffb725fae756f3763007629bea3146468d09ae0d55211033450cd5710` |
| `r93/QA_MANIFEST.json` | `2d95f5a044dbea039977e743e1596d59acbd3ac5bd8a8350f74d9cbb672a104a` |
| `r93/SOURCE_IMPLEMENTATION.md` | `513794370c3ecdddc2ed8d0d152b82f9ba918b170590ba19f58c0dcdb63fb5f6` |
| `r93/PROTOCOL.sha256` | `bffbf215b3366da3cc95d969c21c1b9352030179c7ab6f0c153a95544a3cf234` |
| `r93/dev/SMOKE.json` | `9af0f571ad65b5d1baf68f2864fec644e1646defe91872436554dbbfb2dbde61` |
| `r93/dev/SMOKE_RESOURCE.json` | `387146f69582856350bb9a98f4b0c0b56d86c528231d9f47af418b5774f4f60e` |
| `r93/dev/SCOPE.json` | `3f04b3bd486eb6356763ceac6a59c00005c6178d579413ef40db1d8200021dff` |
| `r93/dev/SCOPE_RESOURCE.json` | `dc93e6581cc4a92d0159839192a5500f59fb81c3d19556cb4c417abcca86e80b` |
| `r94/PROTOCOL.sha256` | `d16853b5c70885897e026a99d2d63f1e655bd12e7bf2c142074b19f7937011b1` |
| `r94/QA_MANIFEST.json` | `2d3a8cb6d96c64d693aba87a2788f9a6148e768c5468696aadd6c8fe9ef2eeac` |
| `r94/SOURCE_RECEIPT.json` | `304e693e5822079b7225537b0e7144ebe830566c3432a436f3e7b283de61af5f` |
| `r94/audit/V1_V3_RESOURCE_REVIEW.json` | `be2f0683e137411f4b0ad55b7f65d7201bf3ec20e5f674ad4d0a7aa59b8427dc` |
| `r94/audit/V1_V3_REVIEW.md` | `23aafd62944421c202b7c5f9588467b7da8a455cbce99c1f5b0055fd88e7727e` |
| `r94/inputs/PANEL.tsv` | `9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c` |
| `r94/inputs/PANEL_TRUTH.json` | `27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf` |
| `r94/reference.py` | `502ae7ff0ed26547fef753251613393ac377fbde72c62dab24567a1756f24aac` |
| `r94/run_all.py` | `a01b60af02041a2a2be60cea52954fc02d37be81b0bd14a82ba38f4cc05c6d2b` |
| `r94/selftest.py` | `a50aa258bfe117678dbc3c118aa4c20cb24c65b38d26872687d6a8af7cb1da62` |
| `r94/structured.py` | `9cbf65a0085c0dfc4bb29e7d9538c30de5eabc4421e49ba88b85fc295cf48329` |
| `audit/reviews/R92_INDEPENDENT_REVIEW.md` | `db6e4b1223d3a3f5a8b49cbfd3b6d5ec9fabe57007036e6fdc54c3b528833232` |
| `r94/audit/STATIC_SOURCE_REVIEW.md` | `9faea43320325f992a864c8fbc9dc4e2d35eedeee3b13521f35ef9694c7a9bb4` |

Recorded by ChatGPT, 21 November 2026 (America/Chicago).


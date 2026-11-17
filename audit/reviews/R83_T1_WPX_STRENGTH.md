# Adversarial review — R83 T1 WPX constraint strength

Affected ledger IDs: L172
Validation: Independent standard-library post-freeze R83 frozen-K4 consistency replay of all alternate letters and offsets for the two already-reported WPX structural survivors; 48 fresh 97-letter synthetic plaintext-driven WPX plants with one wrong published PLAINTEXT character. PASS https://github.com/tylerj-spec/kryptos-k4/actions/runs/43883630778 .
Independent review: ONE model (ChatGPT) independently audited Claude's T1 model and result labels, and wrote the verifier and note. This does not constitute a separately executed multi-model council review.

## Confirmed defect

Claude's T1 checker recomputes pointer state under a changed plaintext letter, but uses the check count computed on the original published letter to label the surviving altered state. Original number is 4; actual independent constraint counts for the four feasible position/sign witnesses are 1,1,2,2.

Keep two compatible structural WPX settings, but withdraw the historical eff4 label and its 12/20 shuffled control comparison as a strength assessment. Those shuffles have not been rescored using the correct statistic. No evidence for a K4 lead.

PFX's 22 structural survivors, WPX no-error EXACT, R83a frozen evidence, and other family tests are unchanged.

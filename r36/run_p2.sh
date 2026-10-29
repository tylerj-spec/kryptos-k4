#!/usr/bin/env bash
# R36 P2: protocol-commit, blind-freeze-commit, then sealed-reveal-commit (never reverse).
set -euo pipefail
cd "$(dirname "$0")/.."
E="r36/p2_direct_multibase"
if [ -e "$E" ]; then
  echo "Existing P2 experiment; refusing overwrite" >&2
  exit 1
fi
# Lock the original pre-registered method, fixture generation and post-freeze analysis BEFORE scan.
sha256sum r36/P2_PREREGISTRATION.md r36/prepare_p2.py r36/sealed/summarize_p2.py \
  r35/controls.json r35/sealed/make_controls.py r35/sealed/make_null.py > r36/P2_PROTOCOL.sha256
git add r36/P2_PROTOCOL.sha256
git commit -m "R36 P2 lock protocol SHA256 before any scan [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r36/P2_PROTOCOL.sha256
# Prepare planted and null ciphertexts; blind scanner has no plaintext masks or clues.
python3 -I r36/prepare_p2.py
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I strictblind/blind/experiment.py "$E"
# Freeze is now committed to GitHub before either reveal or clue-evaluation.
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R36 P2 strictly blind ciphertext-only outputs frozen [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R36 P2 FREEZE COMMITTED BEFORE REVEAL"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I strictblind/sealed/whole_family.py "$E"
python3 -I r36/sealed/summarize_p2.py "$E"
git add -A "$E"
git commit -m "R36 P2 post-freeze sealed counts and independent forward checks [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R36 P2 FINISHED"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
E="r35/p1_null_calibration"
if [ -e "$E" ]; then
  echo "Null-calibration directory already exists; refusing overwrite" >&2
  exit 1
fi
sha256sum r35/P1N_PREREGISTRATION.md r35/prepare_p1n.py \
 r35/sealed/make_null.py r35/sealed/summarize_p1n.py > r35/P1N_PROTOCOL.sha256
git add r35/P1N_PROTOCOL.sha256
git commit -m "R35 P1N prespecified null seeds, model and decision rule locked [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r35/P1N_PROTOCOL.sha256
python3 -I r35/prepare_p1n.py
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I strictblind/blind/experiment.py "$E"
# Null-generation source K4 was not a scan input, so add its original digest explicitly to freeze.
(cd "$E" && sha256sum k4_ciphertext.txt >> FROZEN.sha256 && sha256sum -c FROZEN.sha256)
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R35 P1N twelve blind null maxima and hashes frozen [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P1N BLIND FREEZE COMMITTED BEFORE POSTHOC COMPARISON"
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I r35/sealed/summarize_p1n.py "$E"
git add -A "$E"
git commit -m "R35 P1N independent forward checks and posthoc null comparison [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P1N COMPLETE"

#!/usr/bin/env bash
# R37 P3 protocol lock, blind freeze+GitHub commit, THEN sealed reveal+commit.
set -euo pipefail
cd "$(dirname "$0")/.."
E="r37/p3_keyword_gromark"
if [ -e "$E" ]; then
  echo "Existing P3 experiment; refusing to overwrite" >&2
  exit 1
fi
sha256sum r37/P3_PREREGISTRATION.md r37/prepare_p3.py r37/sealed/summarize_p3.py \
 r35/controls.json r35/sealed/make_controls.py r35/sealed/make_null.py \
 strictblind/blind/scan.cpp strictblind/blind/experiment.py \
 strictblind/sealed/common.py strictblind/sealed/reveal.py \
 strictblind/sealed/whole_family.cpp strictblind/sealed/whole_family.py > r37/P3_PROTOCOL.sha256
git add r37/P3_PROTOCOL.sha256
git commit -m "R37 P3 model, plants, and evaluator sources SHA256 locked before scan [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r37/P3_PROTOCOL.sha256
python3 -I r37/prepare_p3.py
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I strictblind/blind/experiment.py "$E"
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R37 P3 four base keyword alphabet blind outputs frozen [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P3 BLIND FREEZE COMMITTED BEFORE KNOWN-LETTER REVEAL"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I strictblind/sealed/whole_family.py "$E"
python3 -I r37/sealed/summarize_p3.py "$E"
git add -A "$E"
git commit -m "R37 P3 independently checked reveal and whole-family counts [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R37 P3 COMPLETE"

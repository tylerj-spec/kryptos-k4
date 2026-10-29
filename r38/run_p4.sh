#!/usr/bin/env bash
# R38 P4 protocol lock, blind freeze+GitHub commit, THEN sealed reveal+commit.
set -euo pipefail
cd "$(dirname "$0")/.."
E="r38/p4_aca_gromark"
if [ -e "$E" ]; then
  echo "Existing P4 experiment; refusing to overwrite" >&2
  exit 1
fi
sha256sum r38/P4_PREREGISTRATION.md r38/prepare_p4.py r38/sealed/summarize_p4.py \
 r38/aca_alphabet.py r35/controls.json r35/sealed/make_controls.py r35/sealed/make_null.py \
 strictblind/blind/scan.cpp strictblind/blind/experiment.py \
 strictblind/sealed/common.py strictblind/sealed/reveal.py \
 strictblind/sealed/whole_family.cpp strictblind/sealed/whole_family.py > r38/P4_PROTOCOL.sha256
git add r38/P4_PROTOCOL.sha256
git commit -m "R38 P4 model, plants, and evaluator sources SHA256 locked before scan [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r38/P4_PROTOCOL.sha256
python3 -I r38/prepare_p4.py
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I strictblind/blind/experiment.py "$E"
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R38 P4 four base keyword alphabet blind outputs frozen [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P4 BLIND FREEZE COMMITTED BEFORE KNOWN-LETTER REVEAL"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I strictblind/sealed/whole_family.py "$E"
python3 -I r38/sealed/summarize_p4.py "$E"
git add -A "$E"
git commit -m "R38 P4 independently checked reveal and whole-family counts [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R38 P4 COMPLETE"

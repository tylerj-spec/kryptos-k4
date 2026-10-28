#!/usr/bin/env bash
# R39: lock method and sealed controls, run original ciphertext-only ranker, commit freeze THEN validate.
set -euo pipefail
cd "$(dirname "$0")/.."
E="r39/ic_gate"
if [ -e "$E" ]; then
  echo "R39 experiment already exists; refusing overwrite" >&2
  exit 1
fi
sha256sum r39/PREREGISTRATION.md r39/blind/rank_keys.cpp r39/blind/run.py \
 r39/sealed/prepare.py r39/sealed/reveal.py r39/sealed/summarize.py \
 r39/tests/test_rank_keys.py r35/sealed/make_null.py r35/controls.json \
 k4kit/data/k1k3_plaintext.txt k4kit/r32/runs/k4_ciphertext.txt > r39/PROTOCOL.sha256
git add r39/PROTOCOL.sha256
git commit -m "R39 Gromark ciphertext-only IC score protocol and 20 hidden plants locked [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r39/PROTOCOL.sha256
python3 -I r39/tests/test_rank_keys.py
python3 -I r39/sealed/prepare.py
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I r39/blind/run.py "$E"
git add -A "$E"
git add -f "$E/out/rank_keys"
git commit -m "R39 blind unconditional 100000-primer IC scores and controls frozen [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R39 BLIND SCORES FROZEN AND COMMITTED BEFORE SECRET PRIMER RANKING"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I r39/sealed/reveal.py "$E"
python3 -I r39/sealed/summarize.py "$E"
git add -A "$E"
git commit -m "R39 independent truth-primer ranks, controlled gate and null comparisons [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R39 COMPLETED"

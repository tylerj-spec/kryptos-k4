#!/usr/bin/env bash
# R35 P1: preregistration hash committed, blind outputs committed, THEN independent reveal.
set -euo pipefail
cd "$(dirname "$0")/.."
E="r35/p1_carter_k3_mixed"
if [ -e "$E" ]; then
  echo "P1 experiment directory exists; aborting rather than overwriting" >&2
  exit 1
fi
sha256sum r35/P1_PREREGISTRATION.md r35/make_k3_mixed_routes.py \
 r35/sealed/make_controls.py r35/sealed/make_null.py r35/sealed/summarize.py r35/controls.json > r35/P1_PROTOCOL.sha256
git add r35/P1_PROTOCOL.sha256
git commit -m "R35 P1 protocol SHA256 locked before first blind search [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
sha256sum -c r35/P1_PROTOCOL.sha256
mkdir -p "$E"
cp k4kit/r32/runs/k4_ciphertext.txt "$E/k4_ciphertext.txt"
cp r34/carter_az.txt "$E/key.txt"
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
echo "6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0  $E/key.txt" | sha256sum -c -
python3 -I r35/make_k3_mixed_routes.py "$E/routes.txt"
python3 -I r35/sealed/make_controls.py "$E" PLANT_C routes.txt TEXT key.txt 2 35011
python3 -I r35/sealed/make_controls.py "$E" PLANT_D routes.txt TEXT key.txt 3 35012
python3 -I r35/sealed/make_null.py "$E/k4_ciphertext.txt" "$E/NULL_ct.txt" 35013
cat > "$E/manifest.json" << 'EOF'
{
  "workers": 4,
  "runs": [
    {"tag": "K4_P1", "ct": "k4_ciphertext.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "CARTER"},
    {"tag": "PLANT_C", "ct": "PLANT_C_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "CARTER"},
    {"tag": "PLANT_D", "ct": "PLANT_D_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "CARTER"},
    {"tag": "NULL", "ct": "NULL_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "CARTER"}
  ]
}
EOF
python3 -I strictblind/blind/experiment.py "$E"
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R35 P1 Carter K3-shaped blind scan frozen before reveal [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P1 FROZEN COMMIT PUBLISHED BEFORE ANY REVEAL"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I strictblind/sealed/whole_family.py "$E"
python3 -I r35/sealed/summarize.py "$E"
git add -A "$E"
git commit -m "R35 P1 reveal and independent whole-family count [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "R35 P1 COMPLETE"

#!/usr/bin/env bash
# R35 P0 staged blind experiment. GitHub history must contain an immutable freeze commit before reveal.
set -euo pipefail
cd "$(dirname "$0")/.."
sha256sum -c r35/P0_PROTOCOL.sha256
E="r35/p0_k1k3_mixed"
if [ -e "$E/FROZEN.sha256" ]; then
  echo "P0 already frozen; refusing to overwrite" >&2
  exit 1
fi
mkdir -p "$E"
cp k4kit/r32/runs/k4_ciphertext.txt "$E/k4_ciphertext.txt"
cp k4kit/data/k1k3_plaintext.txt "$E/key.txt"
echo "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3  $E/k4_ciphertext.txt" | sha256sum -c -
python3 -I strictblind/blind/routes.py rot-mixed 4 28 "$E/routes.txt"
python3 -I r35/sealed/make_controls.py "$E" PLANT_A routes.txt TEXT key.txt 0 35001
python3 -I r35/sealed/make_controls.py "$E" PLANT_B routes.txt TEXT key.txt 1 35002
python3 -I r35/sealed/make_null.py "$E/k4_ciphertext.txt" "$E/NULL_ct.txt" 35003
cat > "$E/manifest.json" << 'EOF'
{
  "workers": 4,
  "runs": [
    {"tag": "K4_P0", "ct": "k4_ciphertext.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "K1K3"},
    {"tag": "PLANT_A", "ct": "PLANT_A_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "K1K3"},
    {"tag": "PLANT_B", "ct": "PLANT_B_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "K1K3"},
    {"tag": "NULL", "ct": "NULL_ct.txt", "routes": "routes.txt", "key": ["TEXT", "key.txt"], "label": "K1K3"}
  ]
}
EOF
python3 -I strictblind/blind/experiment.py "$E"
# At this point no reveal or whole-family script has run.
git add -A "$E"
git add -f "$E/out/scan"
git commit -m "R35 P0 blind outputs and immutable freeze [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "COMMITTED BLIND FREEZE BEFORE REVEAL"
(cd "$E" && sha256sum -c FROZEN.sha256)
python3 -I strictblind/sealed/reveal.py "$E"
python3 -I strictblind/sealed/whole_family.py "$E"
python3 -I r35/sealed/summarize.py "$E"
git add -A "$E"
git commit -m "R35 P0 sealed reveal, independent count and controls [skip ci]"
git push origin "HEAD:${GITHUB_REF_NAME}"
echo "P0 FINISHED; both freeze and reveal are separately committed"

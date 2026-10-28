#!/bin/bash
# Offline audit; no external requests, no GitHub, no new brute-force scan.
set -euo pipefail
cd "$(dirname "$0")"
( cd r33 && sha256sum -c PROTOCOL.sha256 && sha256sum -c SOURCE_SHA256.txt && cd runs && sha256sum -c FROZEN.sha256 ) >/dev/null
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT
unzip -q R32_handoff_original.zip -d "$TEMP"
python3 "$TEMP/k4kit/r32/blind/make_routes.py" >/dev/null
python3 r33/sealed/independent_audit.py --r32 "$TEMP/k4kit" --r33 r33 --data r33/data > "$TEMP/audit_log"
python3 r33/sealed/merge_histograms.py > "$TEMP/hist_log"
python3 - <<'PY'
import json
from pathlib import Path
r=Path('r33/results')
a=json.loads((r/'INDEPENDENT_AUDIT.json').read_text())
b=json.loads((r/'WHOLE_FAMILY_POSTFREEZE.json').read_text())
assert a['r32_saved_k4_rows_verified']==500 and a['r32_saved_plants_verified']==700 and a['r33_rows_verified']==400
assert all(x['independent_forward_ok'] and x['independent_score_ok'] for x in [*a['r32'].values(),*a['r33'].values()])
assert all(x['truth_rank']==1 for t,x in a['r33'].items() if t.startswith('PLANT'))
assert b['G5']['full24']==0 and b['CARTER']['full24']==0
assert b['G5']['settings']+b['CARTER']['settings']==556217856
print('PASS 1,600 independent saved-output checks; 9 planted controls ranked #1; 556,217,856 postfreeze settings assessed; no K4 full24')
PY

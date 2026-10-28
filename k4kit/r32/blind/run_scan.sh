#!/bin/bash
# Blind side: FAMILY CT_FILE ROUTES_FILE OUT_PREFIX -> 4 parallel scanner processes, then a deterministic merge.
set -eu
cd "$(dirname "$0")/../runs"
FAM=$1; CT=$2; ROUTES=$3; OUT=$4
N=$(wc -l < "$ROUTES"); STEP=$(( (N + 3) / 4 ))
for h in 0 1 2 3; do
  LO=$((h * STEP)); HI=$(( (h + 1) * STEP )); [ $HI -gt $N ] && HI=$N
  ./blind_route_scan "$FAM" "$CT" ../../data/quad_log10.f32 "$( [ "$FAM" = K1K3 ] && echo ../../data/k1k3_plaintext.txt || echo carter_az.txt )" \
     "$ROUTES" $LO $HI "part_${OUT}_$h.tsv" "part_${OUT}_routes_$h.tsv" 2>> "${OUT}.log" &
done
wait
python3 -I ../blind/merge_top.py "$OUT"

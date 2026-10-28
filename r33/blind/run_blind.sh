#!/bin/bash
# Blind-only: no clue text, positions or masks; scan original ciphertext and calibration ciphertexts.
set -euo pipefail
cd "$(dirname "$0")/../runs"
run_one() {
  local fam="$1" ct="$2" routes="$3" tag="$4" src="$5"
  local n step i lo hi
  n=$(wc -l < "$routes")
  step=$(( (n+3)/4 ))
  : > "${tag}.log"
  for i in 0 1 2 3; do
    lo=$((i*step)); hi=$(((i+1)*step)); [ "$hi" -gt "$n" ] && hi="$n"
    ./scan_fixed "$fam" "$ct" ../data/quad_log10.f32 "$src" "$routes" "$lo" "$hi" "part_${tag}_${i}.tsv" "part_${tag}_routes_${i}.tsv" 2>>"${tag}.log" &
  done
  wait
  python ../blind/merge_top.py "$tag"
}
run_one G5 PLANT_G5.txt routes_g5.txt PLANT_G5 -
run_one G5 k4_ciphertext.txt routes_g5.txt K4_G5 -
run_one CARTER PLANT_CARTER.txt routes_carter.txt PLANT_CARTER carter_az.txt
run_one CARTER k4_ciphertext.txt routes_carter.txt K4_CARTER carter_az.txt
# Freeze happens BEFORE any sealed verification script is invoked.
sha256sum K4_*.tsv PLANT_*.tsv k4_ciphertext.txt PLANT_G5.txt PLANT_CARTER.txt > FROZEN.sha256
printf 'FROZEN\n'

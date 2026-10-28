#!/bin/bash
# R32 blind chain: plants (identical searches) then K4; finally freeze every output before any reveal.
set -eu
cd "$(dirname "$0")"
S() { echo "=== $(date -u +%H:%M:%S) $*"; ./run_scan.sh "$@"; }
S CARTER plant_f1_0_ct.txt routes_f1.txt PLANT_F1_0
S K1K3   plant_f1_1_ct.txt routes_f1.txt PLANT_F1_1
S G5     plant_f1_2_ct.txt routes_f1.txt PLANT_F1_2
S C6     plant_f1_3_ct.txt routes_f1.txt PLANT_F1_3
S CARTER plant_f1_4_ct.txt routes_f1.txt PLANT_F1_4
S G5     plant_f1_5_ct.txt routes_f1.txt PLANT_F1_5
S CARTER k4_ciphertext.txt routes_f1.txt K4_F1_CARTER
S K1K3   k4_ciphertext.txt routes_f1.txt K4_F1_K1K3
S G5     k4_ciphertext.txt routes_f1.txt K4_F1_G5
S C6     k4_ciphertext.txt routes_f1.txt K4_F1_C6
S G5     plant_f2_6_ct.txt routes_f2.txt PLANT_F2_6
S G5     k4_ciphertext.txt routes_f2.txt K4_F2_G5
cd ../runs && sha256sum PLANT_F*.tsv K4_F*.tsv k4_ciphertext.txt plant_*_ct.txt > FROZEN.sha256
echo "=== $(date -u +%H:%M:%S) FROZEN"; cat FROZEN.sha256

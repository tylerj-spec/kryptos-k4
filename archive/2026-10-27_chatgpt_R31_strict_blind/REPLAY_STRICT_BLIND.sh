#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p bin replay
printf 'Compiling strictly crib-blind fixed-alphabet scanner...\n'
g++ -std=c++17 -O3 -march=native blind31/blind_scan_fixed.cpp -o bin/blind_scan_fixed
bin/blind_scan_fixed G5 blind31/ciphertext.txt blind31/quad_log10.f32 - replay/K4_G5_BLIND.tsv
bin/blind_scan_fixed CARTER blind31/ciphertext.txt blind31/quad_log10.f32 blind31/carter_az.txt replay/K4_CARTER_BLIND.tsv
cmp replay/K4_G5_BLIND.tsv blind31/K4_G5_BLIND.tsv
cmp replay/K4_CARTER_BLIND.tsv blind31/K4_CARTER_BLIND.tsv
printf 'Blind K4 exhaustive scans reproduced byte for byte.\n'
printf 'Running identical full blind scans for the held-out ciphertexts...\n'
bin/blind_scan_fixed G5 blind31/PLANT_G5_CIPHERTEXT.txt blind31/quad_log10.f32 - replay/PLANT_G5_BLIND.tsv
bin/blind_scan_fixed CARTER blind31/PLANT_CARTER_CIPHERTEXT.txt blind31/quad_log10.f32 blind31/carter_az.txt replay/PLANT_CARTER_BLIND.tsv
cmp replay/PLANT_G5_BLIND.tsv blind31/PLANT_G5_BLIND.tsv
cmp replay/PLANT_CARTER_BLIND.tsv blind31/PLANT_CARTER_BLIND.tsv
printf 'Hidden plaintext controls reproduced byte for byte.\n'
printf 'Compiling and running old free-alphabet solver with all-unknown mask...\n'
g++ -std=c++17 -O3 -march=native models/solver_s2kp.cpp -o bin/solver_s2kp
bin/solver_s2kp models/word_model_orth.tsv blind31/quad_log10.f32 blind31/UNKNOWN_BLIND_ALL_INPUTS.txt replay/UNKNOWN_BLIND_ALL_OUTPUTS.jsonl 16 40000 0.05 0
cmp replay/UNKNOWN_BLIND_ALL_OUTPUTS.jsonl blind31/UNKNOWN_BLIND_ALL_OUTPUTS.jsonl
printf 'Free-alphabet zero-crib results reproduced. Revealing known answers only now.\n'
python3 sealed31/check_after_freeze.py > replay/check_fixed_results.json
python3 sealed31/check_unknown_after_freeze.py > replay/check_unknown_results.json
printf 'All forward-encryption checks and freeze hashes passed. Read HANDOFF.md.\n'

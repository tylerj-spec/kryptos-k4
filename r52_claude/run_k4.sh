#!/bin/bash
# R52 K4 screen: run as pre-registered (c8dacf9). Usage: bash r52_claude/run_k4.sh PART   (PART 1, 2 or 3)
set -e
cd "$(dirname "$0")/.."
W=$(python3 -c "
w=['?']*97
for s,t in ((21,'EASTNORTHEAST'),(63,'BERLINCLOCK')):
    for i,c in enumerate(t): w[s+i]=c
print(''.join(w))")
X=r52_claude/out/chain_screen_fast
run() { $X r52_claude/alphabets.txt r52_claude/routes.txt r52_claude/out/$1_ct.txt "$W" $2 $3 r52_claude/out/$1_B$2_b$3.tsv; echo "$1 B$2 b$3 done"; }
case $1 in
  1) run K4 10 8 ;;
  2) for b in 4 5 6 7; do run K4 10 $b; done
     for B in 5 6 7 8 9; do for b in 4 5; do run K4 $B $b; done; done
     run NULL_00 10 5; run NULL_01 10 5 ;;
  3) for B in $(seq 11 26); do for b in 4 5; do run K4 $B $b; done; done ;;
esac

#!/bin/bash
# R34 chain: E1, E2 (blind, frozen), D1 (planted only), E3 (blind, frozen). Reveals run separately after commits.
set -eu
cd "$(dirname "$0")/.."
for e in e1_carter_columnar e2_c7_r27; do
  echo "=== $(date -u +%H:%M:%S) $e"; python3 -I strictblind/blind/experiment.py r34/$e
done
echo "=== $(date -u +%H:%M:%S) D1"; python3 r34/d1_budget_probe.py
echo "=== $(date -u +%H:%M:%S) e3_carter_rot"; python3 -I strictblind/blind/experiment.py r34/e3_carter_rot
echo "=== $(date -u +%H:%M:%S) CHAIN DONE"

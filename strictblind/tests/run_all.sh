#!/bin/bash
# strictblind CI: contract, round trip, regression. Run before any new strict-blind experiment.
set -e
cd "$(dirname "$0")"
python3 -I test_contract.py
python3 -I test_r35_integrity.py
python3 -I test_roundtrip.py
python3 -I test_regression_r32.py
echo "ALL STRICTBLIND TESTS PASSED"

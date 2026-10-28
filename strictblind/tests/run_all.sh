#!/bin/bash
# strictblind CI: contract, round trip, regression. Run before any new strict-blind experiment.
set -e
cd "$(dirname "$0")"
python3 -I test_contract.py
python3 -I test_r35_integrity.py
python3 -I test_r36_chainbase.py
python3 -I test_r37_keyed.py
python3 -I test_r38_aca.py
python3 -I test_legacy_freeze.py
python3 -I test_roundtrip.py
python3 -I test_regression_r32.py
echo "ALL STRICTBLIND TESTS PASSED"

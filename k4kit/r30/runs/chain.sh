#!/bin/bash
# R30 run chain (order fixed in advance). Each step logs to runs/<step>.log
cd "$(dirname "$0")/.."
step() { echo "=== $(date -u +%H:%M:%S) start $*"; "$@" > "runs/$(echo "$*" | tr ' ' '_' | sed 's/python3_//;s/\.py//').log" 2>&1; echo "=== $(date -u +%H:%M:%S) end $* rc=$?"; }
step python3 calib.py c1
step python3 calib.py c3
step python3 search.py g5 ORTH
step python3 search.py r2 ORTH
step python3 calib.py c2
step python3 search.py g5 ORTHXQ
step python3 search.py r2 ORTHXQ
step python3 search.py e1 ORTH
step python3 search.py e2 ORTH
step python3 search.py e1 ORTHXQ
step python3 search.py e2 ORTHXQ
echo "=== CHAIN DONE"

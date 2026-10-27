#!/bin/bash
# R30 chain after amendment 1: E1 ORTH, E2 ORTH, then C5 + E5 (e5.py).
cd "$(dirname "$0")/.."
while kill -0 1325 2>/dev/null; do sleep 2; done   # let the running r2 ORTHXQ step finish
step() { echo "=== $(date -u +%H:%M:%S) start $*"; "$@" > "runs/$(echo "$*" | tr ' ' '_' | sed 's/python3_//;s/\.py//').log" 2>&1; echo "=== $(date -u +%H:%M:%S) end $* rc=$?"; }
step python3 search.py e1 ORTH
step python3 search.py e2 ORTH
step python3 e5.py c5
step python3 e5.py run
echo "=== CHAIN2 DONE"

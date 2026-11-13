#!/usr/bin/env python3
"""Exit 0 iff two JSON files hold the same data (used by r81a CI to compare a fresh run with the committed file).
Usage: same_json.py A.json B.json"""
import json
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
if a != b:
    print("DIFFERENT:", sys.argv[1], sys.argv[2])
    raise SystemExit(1)
print("same:", sys.argv[1], sys.argv[2])

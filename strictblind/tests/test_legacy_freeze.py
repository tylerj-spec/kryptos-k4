#!/usr/bin/env python3
"""Older experiments (R35-R38) froze shared harness sources by path; later harness edits must not break their
integrity check, and a genuinely altered frozen file must still fail. Needs the git history of the repository."""
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "strictblind" / "sealed"))
from common import check_frozen  # noqa: E402

legacy = REPO / "r37" / "p3_keyword_gromark"
if not legacy.exists():
    print("LEGACY FREEZE SKIPPED (no R37 experiment in this checkout)")
    sys.exit(0)
check_frozen(legacy)                       # passes although strictblind/blind/scan.cpp changed after R37
with tempfile.TemporaryDirectory() as td:  # a tampered copy must fail
    t = Path(td) / "exp"
    shutil.copytree(legacy, t, ignore=shutil.ignore_patterns("scan", "whole_family"))
    tsv = next((t / "out").glob("K4_*.tsv"))
    tsv.write_text(tsv.read_text().replace("\t", " \t", 1))
    try:
        check_frozen(t)
    except (AssertionError, FileNotFoundError):
        print("LEGACY FREEZE OK: old experiment verifies via its freeze commit; tampering is still caught")
        sys.exit(0)
print("LEGACY FREEZE FAILED: tampered copy was accepted")
sys.exit(1)

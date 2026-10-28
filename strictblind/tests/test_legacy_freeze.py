#!/usr/bin/env python3
"""Verify legacy freeze history and actually detect tampering of a committed output.

Old tests copied an experiment outside the repo and accepted FileNotFoundError.
Because old FROZEN.sha256 references shared files via ../../strictblind/,
the missing shared files raised FileNotFoundError before the tampered TSV was
checked; the test could incorrectly report success. This test modifies an
existing frozen output briefly and ALWAYS restores the exact bytes.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "strictblind" / "sealed"))
from common import check_frozen  # noqa: E402

legacy = REPO / "r37" / "p3_keyword_gromark"
if not legacy.is_dir():
    raise AssertionError("missing expected committed R37 legacy experiment")
check_frozen(legacy)  # must verify older shared sources at their freeze commit

tsv = next(sorted((legacy / "out").glob("K4_*.tsv")), None)
assert tsv is not None, "missing legacy frozen K4 result"
original = tsv.read_bytes()
assert original, "empty frozen result"
caught = False
try:
    # Alter the real tracked output in-place rather than copying an experiment
    # into a directory where relative shared source paths cannot resolve.
    tsv.write_bytes(b"!" + original[1:])
    try:
        check_frozen(legacy)
    except AssertionError as exc:
        assert tsv.name in str(exc), (
            f"freeze check failed for a different reason: {exc}")
        caught = True
finally:
    # Never leave a mutated fixture in the working tree, even if checks fail.
    tsv.write_bytes(original)

assert caught, "tampered committed TSV passed its frozen hash validation"
assert tsv.read_bytes() == original
check_frozen(legacy)  # restored experiment must still validate
print("LEGACY FREEZE OK: historical sources verified, actual TSV tampering rejected and restored")

#!/usr/bin/env python3
"""Pure-stdlib provenance gate controls; synthetic strings are NOT historic city records."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r49_validation", ROOT / "validate_inventory.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
blank = json.loads((ROOT / "world_clock_pre1991_inventory.json").read_text())
assert mod.validate(blank, allow_incomplete=True)["unknown_rings"] == 48


def rejected(data, allow_incomplete=False):
    try:
        mod.validate(data, allow_incomplete=allow_incomplete)
    except ValueError:
        return True
    return False


assert rejected(blank), "missing period source data must STOP any cryptanalytic key generation"
synthetic = copy.deepcopy(blank)
synthetic["status"] = mod.COMPLETE
synthetic["orientation"]["orientation_source"] = "SYNTHETIC TEST ONLY"
synthetic["orientation"]["date_line_zone_index"] = 0
synthetic["orientation"]["physical_north_azimuth_degrees"] = 90
for row in synthetic["panels"]:
    row["upper_lines"] = ["SYNTHETIC"]
    row["lower_lines"] = []
    row["period_evidence_year"] = 1988
    row["confidence"] = "primary_verified"
    row["evidence"] = [{
        "url": "https://example.invalid/SYNTHETIC-NOT-HISTORICAL",
        "capture_date": "2026-10-29",
        "artifact_date": "1988-01-01",
        "rights": "synthetic fixture",
        "raw_sha256": "0" * 64
    }]
assert mod.validate(synthetic)["unknown_rings"] == 0
period1990 = copy.deepcopy(synthetic)
period1990["panels"][8]["period_evidence_year"] = 1990
assert mod.validate(period1990)["unknown_rings"] == 0, "1989-1990 evidence must not be wrongly excluded"
bad = copy.deepcopy(synthetic)
bad["panels"][3]["upper_lines"] = None
assert rejected(bad), "complete record cannot contain missing panel names"
bad = copy.deepcopy(synthetic)
bad["panels"][8]["period_evidence_year"] = 1997
assert rejected(bad), "post-1990 restoration cannot substitute for K4-era physical evidence"
bad = copy.deepcopy(synthetic)
bad["panels"][2]["evidence"] = []
assert rejected(bad), "an unsourced segment is not a verified original"
bad = copy.deepcopy(synthetic)
bad["panels"][1], bad["panels"][4] = bad["panels"][4], bad["panels"][1]
assert rejected(bad), "source geometry may not be silently permuted"
print("R49 PROVENANCE GATE TESTS PASSED: incomplete blocked, synthetic complete passes, 4 corruptions rejected")

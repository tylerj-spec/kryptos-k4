#!/usr/bin/env python3
"""R49 regression: previously reconstructed R23 clock chart is NOT forgotten.

Verify the verbatim machine-readable extraction against exact older Markdown
file bytes and Git blob SHA. This is a mixed-year working chart only, NOT
evidence all 24 faces are authenticated for 1988/1989.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "r49/prior_photo_360_chart.json").read_text())
path = ROOT / data["source_repo_path"]
raw_bytes = path.read_bytes()
git_sha1 = hashlib.sha1(f"blob {len(raw_bytes)}\0".encode() + raw_bytes).hexdigest()
assert git_sha1 == data["source_git_blob_sha"], "old photo-chart bytes changed"
lines = raw_bytes.decode("utf-8").splitlines()
faces = data["faces"]
assert len(faces) == 24
for n, face in enumerate(faces):
    assert face["utc_offset"] == n - 11
    assert face["status"] == "PRIOR_PHOTO_DERIVED_COMPOSITE_NOT_YEAR_VERIFIED"
    cells = [x.strip() for x in lines[face["source_line"] - 1].split("|")[1:-1]]
    if len(cells) == 4 and cells[2] == "":
        cells.pop(2)
    assert len(cells) == 3
    assert cells[0] == face["upper_original_chart_cell"]
    assert cells[2] == face["lower_original_chart_cell"]
    m = re.fullmatch(r"\**(\d+) \(([+−-]?\d+)\)\**", cells[1])
    assert m
    assert int(m.group(1)) == face["berlin_noon_hour"]
    assert int(m.group(2).replace("−", "-")) == face["utc_offset"]

berlin = next(x for x in faces if x["utc_offset"] == 1)
east_northeast = next(x for x in faces if x["utc_offset"] == 8)
assert "AMSTERDAM, BERLIN" in berlin["upper_original_chart_cell"]
assert "KOPENHAGEN" in berlin["lower_original_chart_cell"]
assert "IRKUTSK, ULAN BATOR" in east_northeast["upper_original_chart_cell"]
assert "PEKING, SHANGHAI, MANILA" in east_northeast["lower_original_chart_cell"]
assert sum(r["uncertainty_present"] for r in faces) >= 10
assert not data.get("year_complete_1988", False), "inferred chart is not a complete 1988 survey"
print("R49 chart bridge PASS: 24 original UTC faces, exact historic Markdown cells, "
      "photo-source blob pinned, gaps preserved")

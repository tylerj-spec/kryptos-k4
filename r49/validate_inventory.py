#!/usr/bin/env python3
"""R49. Reject unsourced World Clock panel transcriptions as cryptanalytic keys.

No K4 ciphertext, guesses, cribs, or encryption transforms occur here.
Historical-source data gate only; unknowns are represented by null explicitly.
"""
import json
import sys
from pathlib import Path

EXPECTED_ID = "BERLIN_WELTZEITUHR_PRE1991_HISTORICAL_INVENTORY"
REQUIRED_EVIDENCE = ("url", "capture_date", "artifact_date", "rights", "raw_sha256")
COMPLETE = "COMPLETE_PRIMARY_24_PANELS"
INCOMPLETE = "INCOMPLETE_SOURCE_NOT_ACQUIRED"


def validate(data, allow_incomplete=False):
    errors = []
    if not isinstance(data, dict) or data.get("dataset_id") != EXPECTED_ID:
        raise ValueError("unexpected dataset_id or non-object")
    status = data.get("status")
    if status not in (COMPLETE, INCOMPLETE):
        errors.append("status missing or invalid")
    if data.get("candidate_era") != "1969-1990":
        errors.append("candidate_era must include the entire pre-1991 construction/use window")
    zones = data.get("panels")
    if not isinstance(zones, list) or len(zones) != 24:
        errors.append("exactly 24 panels required")
        zones = []
    indices = [x.get("zone_index") for x in zones if isinstance(x, dict)]
    if indices != list(range(24)):
        errors.append("zones must be 0..23 in explicit clockwise order")
    clock = data.get("orientation")
    if not isinstance(clock, dict):
        errors.append("orientation object required")
        clock = {}
    if status == COMPLETE:
        for name in ("orientation_source", "date_line_zone_index", "physical_north_azimuth_degrees"):
            if clock.get(name) is None:
                errors.append("complete inventory missing " + name)
    unknown_count = 0
    for i, row in enumerate(zones):
        if not isinstance(row, dict):
            errors.append(f"panel {i}: expected object")
            continue
        period = row.get("period_evidence_year")
        if period is not None and (not isinstance(period, int) or isinstance(period, bool)
                                   or not 1969 <= period <= 1990):
            errors.append(f"panel {i}: evidence must depict <=1990 physical state")
        sources = row.get("evidence")
        if not isinstance(sources, list):
            errors.append(f"panel {i}: evidence must be list (possibly empty)")
            sources = []
        for j, ev in enumerate(sources):
            if not isinstance(ev, dict) or any(not ev.get(k) for k in REQUIRED_EVIDENCE):
                errors.append(f"panel {i}: evidence {j} lacks URL/date/rights/SHA256")
                continue
            digest = ev["raw_sha256"]
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                errors.append(f"panel {i}: bad source SHA256")
        for ring in ("upper_lines", "lower_lines"):
            value = row.get(ring)
            if value is None:
                unknown_count += 1
                if status == COMPLETE:
                    errors.append(f"panel {i} {ring}: missing source transcription")
                continue
            if not isinstance(value, list) or not all(isinstance(s, str) and s and s == s.upper() for s in value):
                errors.append(f"panel {i} {ring}: require nonempty uppercase source lines or [] if primary proves blank")
        if status == COMPLETE:
            if not sources:
                errors.append(f"panel {i}: no primary-source evidence")
            if row.get("period_evidence_year") is None:
                errors.append(f"panel {i}: physical state date missing")
            if row.get("confidence") != "primary_verified":
                errors.append(f"panel {i}: must be verified against original source")
    if status == INCOMPLETE and not allow_incomplete:
        errors.append("incomplete source inventory cannot be promoted to a K4 key")
    if errors:
        raise ValueError("; ".join(errors))
    return {"status": status, "panels": len(zones), "unknown_rings": unknown_count}


def main():
    args = sys.argv[1:]
    allow = False
    if args and args[0] == "--allow-incomplete":
        args.pop(0)
        allow = True
    if len(args) != 1:
        raise SystemExit("usage: validate_inventory.py [--allow-incomplete] INVENTORY.json")
    data = json.loads(Path(args[0]).read_text())
    print("R49 provenance gate:", validate(data, allow_incomplete=allow))


if __name__ == "__main__":
    main()

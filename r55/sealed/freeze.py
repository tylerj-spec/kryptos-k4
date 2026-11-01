#!/usr/bin/env python3
"""Write a no-overwrite manifest of blind ciphertext inputs, solver and raw outputs.
No clue or truth files accepted. Run before ANY evaluation.
"""
import hashlib
import json
import sys
from pathlib import Path

def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    if len(sys.argv) != 8:
        raise SystemExit("freeze.py controls|target INPUT.tsv RESULTS.jsonl SOLVER.cpp QUAD.f32 PROTOCOL.md OUT.json")
    _, kind, incoming, raw_output, solver, model, protocol, manifest = sys.argv
    if kind not in {"controls", "target"}:
        raise ValueError("invalid phase")
    manifest = Path(manifest)
    if manifest.exists():
        raise FileExistsError("cannot overwrite blind freeze")
    inp = Path(incoming).read_text(encoding="ascii").splitlines()
    out = Path(raw_output).read_text(encoding="ascii").splitlines()
    expected = 20 if kind == "controls" else 13
    assert len(inp) == len(out) == expected
    records = []
    for i, (line, result) in enumerate(zip(inp, out)):
        fields = line.split("\t")
        assert len(fields) == 2 and len(fields[1]) == 97
        assert fields[1].isalpha() and fields[1].isupper()
        record = json.loads(result)
        assert record["id"] == fields[0], (i, fields[0])
        assert record["tested"] == 29952
        assert len(record["candidates"]) == 12
        records.append(fields[0])
    assert len(set(records)) == expected
    if kind == "target":
        assert records[0] == "K4" and records[1:] == [f"NULL_{i:02d}" for i in range(12)]
    else:
        assert records == [f"PLANT_{i:02d}" for i in range(20)]
    manifest.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "classification": "FROZEN_CIPHERTEXT_ONLY_SEARCH_NO_K4_CLUE_CHECK",
        "phase": kind,
        "input_sha256": hash_file(incoming),
        "output_sha256": hash_file(raw_output),
        "blind_source_sha256": hash_file(solver),
        "quad_model_sha256": hash_file(model),
        "protocol_sha256": hash_file(protocol),
        "input_count": expected,
        "searched_parameters_per_input": 29952,
        "full_plaintext_candidates_per_input": 12,
        "status": "FROZEN_NO_REVEAL",
    }
    with manifest.open("x", encoding="ascii") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("R55 blind output SHA256", data["output_sha256"], "phase", kind, "unexamined")

if __name__ == "__main__":
    main()

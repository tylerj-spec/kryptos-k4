#!/usr/bin/env python3
"""Check complete synthetic outputs using public inputs only, before truth reveal."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as R


def rows(path):
    result = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        assert row["id"] not in result, "duplicate output ID"
        result[row["id"]] = row
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    rnd = Path(a.round).resolve()
    public_l = rows(rnd / "holdout/R82_INPUT.jsonl")
    public_p = rows(rnd / "holdout/PTAK_INPUT.jsonl")
    saved_l = rows(rnd / "holdout/run/R82_OUTPUT.jsonl")
    saved_p_raw = rows(rnd / "holdout/run/PTAK_OUTPUT.jsonl")
    saved_p = {rid.split("__")[0]: row for rid, row in saved_p_raw.items()}
    assert len(public_l) == len(saved_l) == 360
    assert len(public_p) == len(saved_p) == len(saved_p_raw) == 240
    assert set(public_l) == set(saved_l) and set(public_p) == set(saved_p)
    for rid, p in public_l.items():
        b = saved_l[rid]
        assert len(b["plaintext"]) == 97 and set(b["plaintext"]) <= set(R.AZ)
        assert len(b["key"]) == p["m"] and set(b["key"]) <= set(R.AZ)
        assert R.linked_encrypt(b["plaintext"], b["key"], p["w"]) == p["ciphertext"], rid
    for rid, p in public_p.items():
        row = saved_p[rid]
        assert row["id"] == f'{rid}__{p["path_index"]}__{p["model"]}'
        b = row["best"]
        assert b["family"] == "PTAK"
        assert b["convention"] == f'{p["convention"][0]}/{p["convention"][1]}_{p["convention"][2]}'
        assert int(b["param"]) == p["lag"]
        assert len(b["plaintext"]) == 97 and set(b["plaintext"]) <= set(R.AZ)
        assert len(b["key"]) == p["lag"] and set(b["key"]) <= set(R.AZ)
        assert R.ptak_encrypt(b["plaintext"], b["key"], p["convention"], p["permutation"], p["model"]) == p["ciphertext"], rid
    paths = ("holdout/R82_INPUT.jsonl", "holdout/PTAK_INPUT.jsonl",
             "holdout/run/R82_OUTPUT.jsonl", "holdout/run/PTAK_OUTPUT.jsonl")
    report = {"scope": "Public ciphertext, structural settings and saved keys/plaintexts only; no truth opened",
              "r82_witnesses": 360, "ptak_witnesses": 240, "all_forward_witnesses_pass": True,
              "references": "Independent scalar reference.py, not either solver's internal decryption",
              "sha256": {p: hashlib.sha256((rnd/p).read_bytes()).hexdigest() for p in paths}}
    with Path(a.output).open("x") as out:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("600/600 public-input forward witnesses passed; no private truth read", flush=True)


if __name__ == "__main__":
    main()

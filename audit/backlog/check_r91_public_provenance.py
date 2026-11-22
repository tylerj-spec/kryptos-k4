#!/usr/bin/env python3
"""Reproduce the entire revealed fixture from pinned public books and fixed seed.

This is a post-result provenance audit, not another candidate-solver attempt.
It writes only in a temporary directory and never changes the original gate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("sources", type=Path)
    ap.add_argument("training", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    root = a.root.resolve()
    with tempfile.TemporaryDirectory(prefix="r91_public_provenance_") as td:
        tmp = Path(td)
        subprocess.run([sys.executable, "-I", str(root / "r91/make_gate.py"),
                        "--sources", str(a.sources.resolve()), "--training", str(a.training.resolve()),
                        "--public", str(tmp / "public"), "--private", str(tmp / "answers")],
                       check=True, stdout=subprocess.PIPE, text=True)
        comparisons = {
            "complete_answer_file": (tmp / "answers/TRUTH.json", root / "r91/holdout/TRUTH.json"),
            "linked_public_inputs": (tmp / "public/R82_INPUT.jsonl", root / "r91/holdout/R82_INPUT.jsonl"),
            "ptak_public_inputs": (tmp / "public/PTAK_INPUT.jsonl", root / "r91/holdout/PTAK_INPUT.jsonl"),
            "answer_commitment": (tmp / "public/TRUTH_SHA256", root / "r91/holdout/TRUTH_SHA256"),
        }
        result = {}
        for label, (reproduced, original) in comparisons.items():
            assert reproduced.read_bytes() == original.read_bytes(), label
            result[label] = {"byte_identical": True, "sha256": sha(original)}
    receipt = {
        "status": "PASS",
        "purpose": "Post-result public-data provenance audit; no candidate solver rerun",
        "data_classification": "Synthetic cipher test answers from public-source book windows and generated toy-cipher keys",
        "full_answer_file_reconstructible_from_public_sources_and_fixed_public_seed": True,
        "contains_account_credentials_or_access_tokens": False,
        "generator": "r91/make_gate.py",
        "generator_sha256": sha(root / "r91/make_gate.py"),
        "public_generator_seed": 912211,
        "message_count": 600,
        "key_generation": "Python random.Random(912211), sampled A-Z strings of declared lengths, primitive-period rejection; no account or credential input",
        "source_manifest": "r91/SOURCES.json",
        "training_provenance": "Reconstructed from the public pinned R59 corpus; used only to reject exact duplicate windows",
        "comparisons": result,
    }
    a.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "full_answer_file_byte_identical_from_public_inputs": True, "messages": 600}))


if __name__ == "__main__":
    main()

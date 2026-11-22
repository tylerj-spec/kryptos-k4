#!/usr/bin/env python3
"""Reconstruct the fixed R95 model for verification; never reads the panel.

Use the registered CI rebuild wrapper budget. Sources are existing public
training assets, checked against immutable digests before use. No retries.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import urllib.request


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(path, expected):
    if digest(path) != expected:
        raise ValueError("Digest mismatch: " + str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    spec = json.loads((repo / "r95/MODEL_SPEC.json").read_text())
    for key in ("builder", "corpus_builder", "acquisition", "carter", "model4"):
        check(repo / spec[key + "_path"], spec[key + "_sha256"])
    acquisition = json.loads((repo / spec["acquisition_path"]).read_text())
    if not acquisition["all_verified"] or len(acquisition["results"]) != 19:
        raise ValueError("Unexpected original acquisition record")
    for item in acquisition["results"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe acquisition path")
        if not item["url"].startswith("https://raw.githubusercontent.com/"):
            raise ValueError("Unexpected training host")
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(item["url"], timeout=30) as response:
            content = response.read(20 * 1024 * 1024 + 1)
        if len(content) > 20 * 1024 * 1024:
            raise ValueError("Training source too large")
        destination.write_bytes(content)
        check(destination, item["expected"])
    module_spec = importlib.util.spec_from_file_location("registered_corpus_builder", repo / spec["corpus_builder_path"])
    corpus = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(corpus)
    corpus.BOOKS = [record for record in corpus.BOOKS if record[3] == "train"]
    corpus.CARTER = repo / spec["carter_path"]
    sys.argv = ["build_corpus.py", "build", str(out / "raw"), str(out / "corpus"), str(out / "nltk")]
    corpus.main()
    training = out / "corpus/train.txt"
    check(training, spec["training_sha256"])
    executable = out / "lm_build"
    subprocess.run(["g++", "-O3", "-std=c++17", str(repo / spec["builder_path"]), "-o", str(executable)], check=True)
    model = out / "lm5.bin"
    subprocess.run([str(executable), str(training), str(model), "5"], check=True)
    check(model, spec["model5_sha256"])
    if model.stat().st_size != spec["model5_bytes"]:
        raise ValueError("Unexpected model length")
    baseline = (repo / spec["model4_path"]).read_bytes()
    with model.open("rb") as stream:
        header = stream.read(8)
        prefix = stream.read(len(baseline) - 8)
    if header != b"R59LM\x05\x00\x00" or prefix != baseline[8:]:
        raise ValueError("Lower-order model mismatch")
    receipt = {"status": "COMPLETE", "model5_sha256": digest(model),
               "training_sha256": digest(training), "public_sources_checked": 19,
               "panel_read": False, "primary_experiment_run": False}
    (out / "REBUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""strictblind BLIND experiment runner: python3 -I blind/experiment.py EXPERIMENT_DIR
Reads EXPERIMENT_DIR/manifest.json (runs: tag, ct, routes, key [kind, arg], label; paths relative to EXPERIMENT_DIR),
builds the scanner, runs every run 4-way parallel, merges each top 100, then freezes every output with sha256
(EXPERIMENT_DIR/FROZEN.sha256), together with the ciphertexts, routes, key texts and manifest. Reads no clue information and refuses manifests that carry plaintext."""
import csv
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUAD = HERE.parents[1] / "k4kit" / "data" / "quad_log10.f32"


def merge(out, tag):
    rows = []
    for f in sorted(glob.glob(str(out / f"part_{tag}_[0-9].tsv"))):
        rows += list(csv.DictReader(open(f), delimiter="\t"))
    rows.sort(key=lambda r: (-float(r["score"]), r["setting"]))
    with open(out / f"{tag}.tsv", "w") as fh:
        fh.write("rank\tscore\tsetting\tplaintext\n")
        for i, r in enumerate(rows[:100]):
            fh.write(f"{i + 1}\t{r['score']}\t{r['setting']}\t{r['plaintext']}\n")
    rr = []
    for f in sorted(glob.glob(str(out / f"part_{tag}_routes_[0-9].tsv"))):
        rr += list(csv.DictReader(open(f), delimiter="\t"))
    with open(out / f"{tag}_routes.tsv", "w") as fh:
        fh.write("route\torder\tbest_score\n")
        for r in rr:
            fh.write(f"{r['route']}\t{r['order']}\t{r['best_score']}\n")
    for f in glob.glob(str(out / f"part_{tag}_*.tsv")):
        os.remove(f)
    return rows[0]["score"] if rows else None


def main():
    exp = Path(sys.argv[1]).resolve()
    man = json.loads((exp / "manifest.json").read_text())
    blob = json.dumps(man).upper()
    assert "PLAINTEXT" not in blob and "TRUTH" not in blob, "manifest must not carry plaintext"
    if (exp / "FROZEN.sha256").exists():
        raise RuntimeError("experiment already frozen; create a new experiment directory")
    tags = [r["tag"] for r in man["runs"]]
    if len(tags) != len(set(tags)) or not tags:
        raise ValueError("run tags must be nonempty and unique")
    if any(not t or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in t) for t in tags):
        raise ValueError("run tags must be simple filenames")
    if workers := man.get("workers"):
        if type(workers) is not int or not (1 <= workers <= 64):
            raise ValueError("workers must be integer 1..64")
    for run in man["runs"]:
        if run["key"][0] not in ("TEXT", "CHAIN"):
            raise ValueError("unsupported key type")
        for name in ("ct", "routes"):
            p = (exp / run[name]).resolve()
            if not p.is_relative_to(exp) or not p.is_file():
                raise ValueError(f"invalid experiment path: {run[name]}")
        if run["key"][0] == "TEXT":
            p = (exp / run["key"][1]).resolve()
            if not p.is_relative_to(exp) or not p.is_file():
                raise ValueError("invalid key path")
    out = exp / "out"
    if out.exists() and any(out.iterdir()):
        raise RuntimeError("output directory is not empty; use a new experiment directory")
    out.mkdir(exist_ok=True)
    exe = out / "scan"
    subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(HERE / "scan.cpp"), "-o", str(exe)], check=True)
    workers = int(man.get("workers", 4))
    for run in man["runs"]:
        t0 = time.time()
        routes = exp / run["routes"]
        n = sum(1 for ln in open(routes) if ln.strip())
        step = (n + workers - 1) // workers
        kind, arg = run["key"]
        karg = str(exp / arg) if kind == "TEXT" else str(arg)
        procs = []
        for h in range(workers):
            lo, hi = h * step, min(n, (h + 1) * step)
            if lo >= hi:
                continue
            procs.append(subprocess.Popen([str(exe), kind, karg, run["label"], str(exp / run["ct"]), str(QUAD), str(routes),
                                           str(lo), str(hi), str(out / f"part_{run['tag']}_{h}.tsv"),
                                           str(out / f"part_{run['tag']}_routes_{h}.tsv")],
                                          stderr=open(out / f"{run['tag']}.log", "a")))
        assert all(p.wait() == 0 for p in procs), run["tag"]
        print(f"{run['tag']}: top {merge(out, run['tag'])} ({time.time() - t0:.0f} s)", flush=True)
    frozen = [p for p in sorted(out.glob("*.tsv"))] + [exp / r["ct"] for r in man["runs"]] + [exp / "manifest.json"]
    frozen += [HERE / "scan.cpp", HERE / "experiment.py", QUAD, exe]
    frozen += [exp / r["routes"] for r in man["runs"]] + [exp / r["key"][1] for r in man["runs"] if r["key"][0] == "TEXT"]
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {os.path.relpath(p.resolve(), exp)}" for p in dict.fromkeys(frozen)]
    (exp / "FROZEN.sha256").write_text("\n".join(lines) + "\n")
    print("FROZEN", len(lines), "files ->", exp / "FROZEN.sha256")


if __name__ == "__main__":
    main()

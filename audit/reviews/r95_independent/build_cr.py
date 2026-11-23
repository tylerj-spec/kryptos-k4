#!/usr/bin/env python3
"""Amendment 1 build (see AMENDMENT_1.md): the pinned r59/blind/lm_build.cpp with its one output line
`float lp = log10f(p);` replaced by the correctly rounded `float lp = (float)log10((double)p);` (what glibc >= 2.41's
correctly rounded log10f returns). Everything else is byte-identical; the diff is checked. Builds K=5 from the pinned
training file and requires R95's registered digest and the baseline's orders 1-4. Usage: build_cr.py WORKDIR TRAIN.txt"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD, NEW = "float lp = log10f(p);", "float lp = (float)log10((double)p);"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    work, train = Path(sys.argv[1]), Path(sys.argv[2])
    work.mkdir(parents=True, exist_ok=True)
    src = (ROOT / "r59/blind/lm_build.cpp").read_text()
    assert sha(src.encode()) == "87b521d7654c07ead5b3bdbaa1da24c5ff60f10ae95b8f9aa8cf83673e2fc915" and src.count(OLD) == 1
    patched = src.replace(OLD, NEW)
    diff = [(a, b) for a, b in zip(src.splitlines(), patched.splitlines()) if a != b]
    assert len(diff) == 1 and len(src.splitlines()) == len(patched.splitlines())
    (work / "lm_build_cr.cpp").write_text(patched)
    subprocess.run(["g++", "-O3", "-std=c++17", str(work / "lm_build_cr.cpp"), "-o", str(work / "lm_build_cr")], check=True)
    subprocess.run([str(work / "lm_build_cr"), str(train), str(work / "lm5.bin"), "5"], check=True, capture_output=True)
    m5, m4 = (work / "lm5.bin").read_bytes(), (ROOT / "r91/R59_LOWER4_FROM_K5.bin").read_bytes()
    rep = {"builder_patch": {"old": OLD, "new": NEW, "lines_changed": 1}, "patched_builder_sha256": sha(patched.encode()),
           "train_sha256_ok": sha(train.read_bytes()) == "871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434",
           "model5_bytes": len(m5), "model5_sha256": sha(m5),
           "model5_sha256_ok": sha(m5) == "e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd"
           and len(m5) == 49426528,
           "model4_sha256_ok": sha(m4) == "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41",
           "orders1_4_equal_baseline": m5[8:len(m4)] == m4[8:],
           "compiler": subprocess.run(["g++", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
           "glibc": subprocess.run(["ldd", "--version"], capture_output=True, text=True).stdout.splitlines()[0]}
    rep["pass"] = rep["train_sha256_ok"] and rep["model5_sha256_ok"] and rep["model4_sha256_ok"] and rep["orders1_4_equal_baseline"]
    (HERE / "BUILD_CR.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("BUILD_CR", "PASS" if rep["pass"] else "FAIL", rep["model5_sha256"][:16])


if __name__ == "__main__":
    main()

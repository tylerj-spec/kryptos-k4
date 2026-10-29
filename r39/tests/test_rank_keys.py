#!/usr/bin/env python3
"""Test independent Python IC score against C++ ranker, including 5-digit primer leading zero."""
import math
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "r39/blind/rank_keys.cpp"
with tempfile.TemporaryDirectory() as td:
    e = Path(td)
    subprocess.run(["g++", "-std=c++17", "-O3", str(CPP), "-o", str(e / "rank")], check=True)
    ct = (ROOT / "k4kit/r32/runs/k4_ciphertext.txt").read_text().strip()
    (e / "ct.txt").write_text(ct.lower() + "\n")
    subprocess.run([str(e / "rank"), str(e / "ct.txt"),
                    str(e / "scores.bin"), str(e / "top.tsv")], check=True, capture_output=True)
    with open(e / "scores.bin", "rb") as f:
        scores = struct.unpack("<100000d", f.read())
    assert len(scores) == 100000
    def check_score(primer):
        key = [int(ch) for ch in f"{primer:05d}"]
        for i in range(5, 97):
            key.append((key[i-5] + key[i-4]) % 10)
        counts = [[0] * 26 for _ in range(10)]
        groups = [0] * 10
        for c, d in zip(ct, key):
            groups[d] += 1
            counts[d][ord(c) - 65] += 1
        a = sum(v * (v-1) for row in counts for v in row)
        b = sum(v * (v-1) for v in groups)
        return a / b
    for p in (0, 1, 42, 54321, 99999):
        assert math.isclose(scores[p], check_score(p), abs_tol=1e-15), p
    rows = (e / "top.tsv").read_text().splitlines()
    assert len(rows) == 101
    for idx, line in enumerate(rows[1:], 1):
        rank, score, primer = line.split("\t")
        assert int(rank) == idx
        assert scores[int(primer)] == float(score)
        if idx > 1:
            assert float(score) <= float(rows[idx - 1].split("\t")[1])
    print("R39 IC OK: exact independent score checks, deterministic top100, lowercase ciphertext accepted")

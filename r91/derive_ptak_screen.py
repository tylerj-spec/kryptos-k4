#!/usr/bin/env python3
"""Checked adaptation of R68's archived solver to one provided structural branch.

The PTAK primer optimizer, iteration order, score function, seed formula, and
RNG remain verbatim. Edits select a supplied structural branch, remove later
rescoring, and restrict input/output after the declared files have been opened.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = (ROOT / "vendor/r68/keyed_solve.cpp").read_text()
changes = [
    ("static void finish(Best &b) { b.lm6 = lm_order(b.P, 6); b.w = wordscore(b.P); b.tot = b.lm6 + b.w; }",
     "static void finish(Best &b) { b.lm6 = lm_order(b.P, 4); b.w = 0; b.tot = b.lm6; }"),
    ("for (const Conv &cv : CONVS) {", "for (const Conv &cv : CONVS) { if (cv.name != rw.cv) continue;"),
    ("// ---- GRO (all primers; keep the best by order-4, then rescore the top 5)\n        {",
     "// ---- GRO disabled in this provided-branch PTAK power screen\n        if (false) {"),
    ("for (int fam = 0; fam < 2; fam++) for (int L = 1; L <= LMAX; L++) {",
     "for (int fam = 1; fam < 2; fam++) for (int L = rw.lag; L <= rw.lag; L++) {"),
    ("struct Row { string id, Y; vector<int> R; int N; };",
     "struct Row { string id, Y, cv; vector<int> R; int N, lag; };"),
    ("getline(ss, rs, '\\t');",
     "getline(ss, rs, '\\t'); getline(ss, rw.cv, '\\t'); string ls; getline(ss, ls, '\\t'); rw.lag = stoi(ls);"),
    ("ifstream in(argv[3]); ofstream out(argv[4]); string line;",
     "ifstream in(argv[3]); ofstream out(argv[4]); string line; if (!in || !out) throw runtime_error(\"input/output open failed\"); if (r91_lock_io() != 0) throw runtime_error(\"seccomp input isolation failed\");"),
    (r'\"lm6\"', r'\"score4\"'),
]
for old, new in changes:
    if source.count(old) != 1:
        raise RuntimeError("archived source no longer matches checked patch")
    source = source.replace(old, new)
(ROOT / "ptak_r68_screen.cpp").write_text('#include "seccomp_io.hpp"\n' + source)
print(f"derived provided-branch R68 PTAK solver: {len(changes)} checked source substitutions")

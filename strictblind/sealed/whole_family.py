#!/usr/bin/env python3
"""strictblind SEALED: python3 -I sealed/whole_family.py EXPERIMENT_DIR   (only after FROZEN.sha256 exists)
Counts clue matches over EVERY setting of every K4 run (4-way parallel C++), with binomial(24, 1/26) chance tails.
Writes EXPERIMENT_DIR/WHOLE_FAMILY.json."""
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import K4, check_frozen, letters  # noqa: E402

exp = Path(sys.argv[1]).resolve()
check_frozen(exp)
man = json.loads((exp / "manifest.json").read_text())
exe = exp / "out" / "whole_family"
subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(Path(__file__).with_name("whole_family.cpp")), "-o", str(exe)], check=True)
tail = lambda n, m: n * sum(math.comb(24, j) * (1 / 26) ** j * (25 / 26) ** (24 - j) for j in range(m, 25))  # noqa: E731
res = {}
for run in man["runs"]:
    if letters(exp / run["ct"]) != K4:
        continue
    kind, arg = run["key"]
    karg = str(exp / arg) if kind == "TEXT" else str(arg)
    n = sum(1 for ln in open(exp / run["routes"]) if ln.strip())
    step = (n + 3) // 4
    procs = [subprocess.Popen([str(exe), kind, karg, str(exp / run["ct"]), str(exp / run["routes"]), str(h * step),
                               str(min(n, (h + 1) * step))], stdout=subprocess.PIPE, text=True) for h in range(4) if h * step < n]
    hist, best, full = [0] * 25, (0, ""), []
    for p in procs:
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(f"whole_family worker failed ({p.returncode}): {stderr}")
        for ln in stdout.splitlines():
            f = ln.split("\t")
            if f[0] == "HIST":
                hist = [a + int(b) for a, b in zip(hist, f[1:])]
            elif f[0] == "BEST" and int(f[1]) > best[0]:
                best = (int(f[1]), f[2])
            elif f[0] == "FULL24":
                full.append(f[1])
    keys = (4 * (len(letters(karg)) - 97 + 1) if kind == "TEXT" else
            int(arg.split(",")[0]) ** int(arg.split(",")[1]) if kind in ("CHAINBASE", "CHAINALPH", "CHAINACA") else 10 ** int(arg))
    expected = n * keys * (48 if kind in ("CHAINALPH", "CHAINACA") else 12)
    tot = sum(hist)
    if tot != expected:
        raise RuntimeError(f"whole_family incomplete: {tot} settings, expected {expected}")
    res[run["tag"]] = {"settings": tot, "max": best[0], "best_setting": best[1], "full24": full, "histogram": hist,
                       "observed_ge": {m: sum(hist[m:]) for m in range(8, 13)},
                       "chance_ge": {m: round(tail(tot, m), 2) for m in range(8, 13)}}
    print(f"{run['tag']}: {tot:,} settings; max {best[0]}/24; all 24: {len(full)}; >=10 observed {sum(hist[10:])} "
          f"vs chance {tail(tot, 10):.1f}; >=11 {sum(hist[11:])} vs {tail(tot, 11):.2f}")
(exp / "WHOLE_FAMILY.json").write_text(json.dumps(res, indent=1) + "\n")

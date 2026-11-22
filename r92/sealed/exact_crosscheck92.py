#!/usr/bin/env python3
"""R92 post-freeze cross-check of r92/k4/EXACT.json on K4 with the second implementation, rotor92.exact_check
(written separately from exact92.feasible; r92/tests/test_r92.py test 4 compares the two with a constructive
completion). For every one of the 192 settings it recomputes EXACT feasibility and, for every dropped published
position, DROP feasibility, and requires the counts and the feasible-setting lists to equal EXACT.json's.
Run only after EXACT.json is committed. Usage: exact_crosscheck92.py TARGET.tsv EXACT.json OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r92"), str(ROOT / "r73" / "sealed")]
import rotor92 as R  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402


def main():
    tsv, ex, out = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), Path(sys.argv[3])
    ct = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)["K4"]
    pos = [o + i for o, t in CLUES for i in range(len(t))]
    let = [c for _, t in CLUES for c in t]
    exact = [list(st) for st in R.SETTINGS if R.exact_check(ct, pos, let, *st)[0]]
    drop = []
    for j in range(len(pos)):
        P, L = pos[:j] + pos[j + 1:], let[:j] + let[j + 1:]
        drop.append(sum(R.exact_check(ct, P, L, *st)[0] for st in R.SETTINGS))
    a = ex["exact"]["K4"]
    agree_exact = len(exact) == a["feasible"] and exact[:50] == [list(s["setting"]) for s in a["settings"]]
    agree_drop = drop == [p["feasible"] for p in ex["drop"]["K4"]["by_dropped_position"]]
    rep = {"note": "Post-freeze cross-check of r92/k4/EXACT.json on K4 with rotor92.exact_check (second implementation).",
           "settings": len(R.SETTINGS), "k4_exact_feasible": len(exact), "k4_drop_feasible_by_position": drop,
           "agrees_exact": agree_exact, "agrees_drop": agree_drop}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep))
    assert agree_exact and agree_drop


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""T2 check of R83a's run deviation (r83/RESULT.md, r83/f1xd_lowmem.py): on NULL_010 and NULL_011 (r83/k4/TARGET.tsv),
which F1X settings with one published letter removed are feasible with >= 3 checks and have a true solution count
>= 2^63, and of those, which would have entered R75 f1x()'s decode branch (completed key letters u <= 2 and the
int64-wrapped count <= decode_limit 64)? Exact Python-int counts from r75/audit/f1x_safe.py; no decode.
Usage: python3 -I r75/audit/t2_overflow_17.py OUT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_f1x as RP  # noqa: E402
import f1x_safe as F  # noqa: E402


def wrap(x):
    return (x + 2 ** 63) % 2 ** 64 - 2 ** 63


def main():
    cts = RP.load(RP.ROOT / "r83/k4/TARGET.tsv")
    pos, known = RP.clues()
    out = {}
    for rid in ("NULL_010", "NULL_011", "K4"):
        rows = []
        for m1 in RP.BIG:
            for m2 in RP.BIG:
                for cfg in RP.CFG1:
                    for a in range(len(pos)):
                        p2, k2 = pos[:a] + pos[a + 1:], known[:a] + known[a + 1:]
                        r = F.check_setting(cts[rid], p2, k2, cfg, m1, m2)
                        n = r["active_solution_count"]
                        if r["feasible"] and r["checks"] >= 3 and n >= 2 ** 63:
                            rows.append({"cfg": list(cfg), "m1": m1, "m2": m2, "dropped": pos[a], "checks": r["checks"],
                                         "true_count": str(n), "int64_count": wrap(n),
                                         "unpinned_key_letters": r["unused_key_slots"],
                                         "decode_branch": r["unused_key_slots"] <= 2 and wrap(n) <= 64})
        out[rid] = {"n_over_2^63": len(rows), "n_decode_branch": sum(r["decode_branch"] for r in rows),
                    "decode_branch_settings": sorted({(tuple(r["cfg"]), r["m1"], r["m2"]) for r in rows
                                                      if r["decode_branch"]}), "rows": rows}
        print(rid, out[rid]["n_over_2^63"], out[rid]["n_decode_branch"], out[rid]["decode_branch_settings"], flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=list) + "\n")


if __name__ == "__main__":
    main()

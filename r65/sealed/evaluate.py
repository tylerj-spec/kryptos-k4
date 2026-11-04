#!/usr/bin/env python3
"""R65 evaluation (after the freeze). Uses NO published K4 letters: the statistic is ciphertext-only.
Checks the freeze manifests, that K4's re-run gap reproduces R64's frozen value (28.4979, within 0.001), and every raw
stage-1 witness re-encrypts through its route. Then:
  PRIMARY    p = (1 + #{fresh nulls with G >= G_K4}) / (N + 1)   with G_K4 the R64 frozen value 28.4979
  SECONDARY  the same count restricted to nulls whose best route is SNAKE_L; the pooled count with R64's 100 nulls.
Decision (r65/PREREGISTRATION.md): p <= 0.01 -> REPLICATED (a structural anomaly; not a decryption);
otherwise NOT REPLICATED.
Usage: evaluate.py TARGET.tsv RUN_DIR REPORT.json"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/sealed"))
from common import forward, routes  # noqa: E402

G_R64 = 28.4979
R64_NULLS = ROOT / "r64/k4/run/RESULTS.jsonl"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    problems = []
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results") and sha(tsv if lab == "input" else run / "RESULTS.jsonl") != h:
            problems.append(f"freeze mismatch {lab}")
    for line in (run / "WORK.sha256").read_text().splitlines():
        h, name = line.split("  ")
        if sha(run / "work" / name) != h:
            problems.append(f"work mismatch {name}")
    R = routes()
    names = list(R)
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    nwit = 0
    for rid in rows:
        for line in (run / "work" / f"{rid}.s1.jsonl").read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rn = names[int(r["id"].rsplit("__", 1)[1])]
                for w in [r["best"]] + r["per_convention"] + r["top"]:
                    nwit += 1
                    if forward(w["plaintext"], w["key"], w["convention"], R[rn]) != cts[rid]:
                        problems.append(f"witness {rid} {rn}")
    gk = rows["K4"]["gap"]
    reproduced = abs(gk - G_R64) < 0.001 and rows["K4"]["best_route"] == "SNAKE_L"
    nulls = [r for i, r in rows.items() if i != "K4"]
    ge = sum(r["gap"] >= G_R64 for r in nulls)
    ge_snake = sum(r["gap"] >= G_R64 and r["best_route"] == "SNAKE_L" for r in nulls)
    r64n = [json.loads(l) for l in R64_NULLS.read_text().splitlines() if l.strip()]
    r64g = [r["models"]["GERMAN"]["stage1"][0]["total"] - r["models"]["GERMAN"]["stage1"][1]["total"]
            for r in r64n if r["id"] != "K4"]
    p = (1 + ge) / (len(nulls) + 1)
    out = {"k4_gap_rerun": gk, "k4_gap_r64_frozen": G_R64, "k4_best_route_rerun": rows["K4"]["best_route"],
           "reproduced": reproduced, "fresh_nulls": len(nulls), "fresh_nulls_ge": ge, "p_primary": p,
           "fresh_nulls_ge_and_best_route_snake_l": ge_snake,
           "pooled_with_r64": {"nulls": len(nulls) + len(r64g), "ge": ge + sum(g >= G_R64 for g in r64g),
                               "p": (1 + ge + sum(g >= G_R64 for g in r64g)) / (len(nulls) + len(r64g) + 1)},
           "fresh_null_gap_quantiles": {q: sorted(r["gap"] for r in nulls)[int(q * (len(nulls) - 1))] for q in (0.5, 0.9, 0.99)},
           "fresh_null_gap_max": max(r["gap"] for r in nulls),
           "fresh_null_best_route_counts": {n: sum(r["best_route"] == n for r in nulls) for n in names},
           "witnesses_checked": nwit, "problems": problems,
           "outcome": ("INVALID" if problems or not reproduced else "REPLICATED" if p <= 0.01 else "NOT_REPLICATED")}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("fresh_null_best_route_counts",)}, indent=1))


if __name__ == "__main__":
    main()

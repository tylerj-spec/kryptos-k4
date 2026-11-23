#!/usr/bin/env python3
"""R96 evaluation of one version. Opens r94/inputs/PANEL_TRUTH.json ONLY after checking that the version's outputs
are listed in its OUTPUTS.sha256 (the freeze manifest), unchanged, and present in FREEZE_COMMIT, which must be on the remote branch.
Usage: python3 -I r96/evaluate96.py VERSION FREEZE_COMMIT MODEL.bin"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import r96core as C  # noqa: E402

CELLS = ["n1t3", "n1t4", "n2t1", "n2t2", "n3t1", "n3t2", "n4t0", "n4t1"]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def main():
    version, commit, model_path = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    run = HERE / f"run_v{version}"
    frozen = {l.split()[-1]: l.split()[0] for l in (run / "OUTPUTS.sha256").read_text().splitlines() if l.strip()}
    for rel in (f"r96/run_v{version}/RESULTS.jsonl", f"r96/run_v{version}/RUN.json", f"r96/run_v{version}/WITNESS.json",
                f"r96/run_v{version}/RESOURCE_LOG.json"):
        h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert frozen.get(rel) == h, f"{rel} not frozen"
        assert hashlib.sha256(subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{rel}"], capture_output=True,
                                             check=True).stdout).hexdigest() == h, f"{rel} differs from {commit}"
    assert "origin/claude/zen-clarke-s6fwj5" in git("branch", "-r", "--contains", commit), "freeze not pushed"
    assert json.loads((run / "WITNESS.json").read_text())["passed"], "witness failed"
    # ---- truth opened only here ----
    truth = json.loads((ROOT / "r94/inputs/PANEL_TRUTH.json").read_text())
    model = C.Model(model_path)
    rows = []
    for line in (run / "RESULTS.jsonl").read_text().splitlines():
        r = json.loads(line)
        t = truth[r["id"]]
        lab = tuple(t["label"])
        U_true, V_true = [0] * 26, [0] * 26
        for x, y in enumerate(t["W1"]):
            U_true[y] = x
        for x, y in enumerate(t["W2"]):
            V_true[y] = x
        s1, s2 = C.shifts(lab)
        a = [(C.ALPH[lab[1]].index(c) + b) % 26 for c, b in zip(t["ct"], s2)]
        if r["searched"] == "U":
            used = {((V_true[a[i]] - s2[i]) % 26 + s1[i]) % 26 for i in range(97)}
            true_w = U_true
        else:
            used = set(a)
            true_w = V_true
        right = lambda txt: sum(x == y for x, y in zip(txt, t["pt"]))  # noqa: E731
        top = r["starts"][r["top1"]]
        letters = right(top["text"])
        truth_score = model.score(t["pt"])
        diff = top["score"] - truth_score
        diag = "alias" if top["text"] == t["pt"] else ("objective_counterexample" if diff > 1e-9 else
                                                       ("search_gap" if diff < -1e-9 else "tie"))
        rows.append({"id": r["id"], "condition": r["condition"], "cell": t["cell"], "letters": letters,
                     "recovered": letters >= 95, "exact": letters == 97,
                     "recall8": any(right(r["starts"][k]["text"]) >= 95 for k in r["top8"]),
                     "key_on_used_contacts": all(top["searched_inverse_wiring"][x] == true_w[x] for x in used),
                     "starts_recovered": sum(right(s["text"]) >= 95 for s in r["starts"]),
                     "top1_minus_truth_score": round(diff, 6), "diagnosis": diag})
    summ = {}
    for cond in ("trueV", "trueU"):
        rs = [x for x in rows if x["condition"] == cond]
        cells = {c: sum(x["recovered"] for x in rs if x["cell"] == c) for c in CELLS}
        summ[cond] = {"recovered": sum(x["recovered"] for x in rs), "cases": len(rs),
                      "exact": sum(x["exact"] for x in rs), "recall8": sum(x["recall8"] for x in rs),
                      "key_on_used_contacts": sum(x["key_on_used_contacts"] for x in rs), "by_cell": cells,
                      "diagnosis": {d: sum(x["diagnosis"] == d for x in rs) for d in
                                    ("alias", "objective_counterexample", "search_gap", "tie")},
                      "median_letters": sorted(x["letters"] for x in rs)[len(rs) // 2],
                      "passes": sum(x["recovered"] for x in rs) >= 44 and all(v >= 5 for v in cells.values())}
    passed = all(summ[c]["passes"] for c in summ)
    rep = {"version": version, "freeze_commit": commit, "summary": summ,
           "version_passes": passed, "rows": rows}
    out = HERE / f"eval_v{version}"
    out.mkdir(exist_ok=True)
    (out / "EVAL.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(f"version {version}:", "PASSES" if passed else "FAILS",
          {c: (summ[c]["recovered"], summ[c]["by_cell"]) for c in summ})


if __name__ == "__main__":
    main()

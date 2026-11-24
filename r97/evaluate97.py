#!/usr/bin/env python3
"""R97 evaluation of one version (PREREGISTRATION section 6). Opens r94/inputs/PANEL_TRUTH.json ONLY after checking
that the version's outputs are listed in run_vN/OUTPUTS.sha256, unchanged, present in FREEZE_COMMIT, and that the
commit is on the remote branch. Usage: python3 -I r97/evaluate97.py VERSION FREEZE_COMMIT MODEL.bin"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import r97core as C  # noqa: E402

CELLS = ["n1t3", "n1t4", "n2t1", "n2t2", "n3t1", "n3t2", "n4t0", "n4t1"]


def git(*a, text=True):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=text, check=True).stdout


def check_freeze(version, commit):
    run = HERE / f"run_v{version}"
    listed = {l.split()[-1]: l.split()[0] for l in (run / "OUTPUTS.sha256").read_text().splitlines() if l.strip()}
    for name in ("RESULTS.jsonl", "RUN.json", "WITNESS.json", "RESOURCE_LOG.json"):
        rel = f"r97/run_v{version}/{name}"
        h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert listed.get(rel) == h, f"{rel} not frozen"
        assert hashlib.sha256(git("show", f"{commit}:{rel}", text=False)).hexdigest() == h, f"{rel} differs from {commit}"
    assert "origin/claude/zen-clarke-s6fwj5" in git("branch", "-r", "--contains", commit), "freeze not pushed"
    assert json.loads((run / "WITNESS.json").read_text())["passed"], "witness failed"
    return run


def inverse(W):
    q = [0] * 26
    for x, y in enumerate(W):
        q[y] = x
    return q


def gauge_agree(Uf, Vf, Ut, Vt, used_a, used_b):
    for g in range(26):
        if all(Vf[x] == (Vt[x] + g) % 26 for x in used_a) and all(Uf[(y + g) % 26] == Ut[y] for y in used_b):
            return True
    return False


def main():
    version, commit, model_path = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    run = check_freeze(version, commit)
    truth = json.loads((ROOT / "r94/inputs/PANEL_TRUTH.json").read_text())      # opened only here
    model = C.Model(model_path)
    rows = []
    for line in (run / "RESULTS.jsonl").read_text().splitlines():
        r = json.loads(line)
        t = truth[r["id"]]
        lab = tuple(t["label"])
        Ut, Vt = inverse(t["W1"]), inverse(t["W2"])
        s1, s2 = C.shifts(lab)
        used_a = {(C.ALPH[lab[1]].index(c) + b) % 26 for c, b in zip(t["ct"], s2)}
        used_b = {((Vt[(C.ALPH[lab[1]].index(c) + b) % 26] - b) % 26 + a) % 26 for c, a, b in zip(t["ct"], s1, s2)}
        right = lambda txt: sum(x == y for x, y in zip(txt, t["pt"]))  # noqa: E731
        top = r["finals"][r["top1"]]
        letters = right(top["text"])
        diff = top["score"] - model.score(t["pt"])
        diag = "alias" if top["text"] == t["pt"] else ("objective_counterexample" if diff > 1e-9 else
                                                       ("search_gap" if diff < -1e-9 else "tie"))
        rows.append({"id": r["id"], "cell": t["cell"], "letters": letters, "recovered": letters >= 95,
                     "exact": letters == 97, "recall_retained": any(right(f["text"]) >= 95 for f in r["finals"]),
                     "key_up_to_gauge": gauge_agree(top["U"], top["V"], Ut, Vt, used_a, used_b),
                     "best_final_letters": max(right(f["text"]) for f in r["finals"]),
                     "top1_minus_truth_score": round(diff, 6), "diagnosis": diag})
    cells = {c: sum(x["recovered"] for x in rows if x["cell"] == c) for c in CELLS}
    summ = {"recovered": sum(x["recovered"] for x in rows), "cases": len(rows), "by_cell": cells,
            "exact": sum(x["exact"] for x in rows), "recall_retained": sum(x["recall_retained"] for x in rows),
            "key_up_to_gauge": sum(x["key_up_to_gauge"] for x in rows),
            "diagnosis": {d: sum(x["diagnosis"] == d for x in rows) for d in ("alias", "objective_counterexample", "search_gap", "tie")},
            "median_letters": sorted(x["letters"] for x in rows)[len(rows) // 2],
            "max_letters": max(x["letters"] for x in rows)}
    passed = summ["recovered"] >= 44 and all(v >= 5 for v in cells.values())
    out = HERE / f"eval_v{version}"
    out.mkdir(exist_ok=True)
    (out / "EVAL.json").write_text(json.dumps({"version": version, "freeze_commit": commit, "summary": summ,
                                               "version_passes": passed, "rows": rows}, indent=1) + "\n")
    print(f"version {version}:", "PASSES" if passed else "FAILS", json.dumps(summ))


if __name__ == "__main__":
    main()

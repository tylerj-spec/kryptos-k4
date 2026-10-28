#!/usr/bin/env python3
"""R34 D1 (development, planted data only, no K4): the L109 clue-free two-free-alphabet test at 20x the budget."""
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "k4kit/r30"))
from r30lib import AZ, DATA, RUNS, chain_key, encrypt, run_solver, seed, solver_line  # noqa: E402
sys.path.insert(0, str(REPO / "k4kit/r30"))
from report import load_model  # noqa: E402

bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"]
rng = random.Random(30009)                      # identical generation to the R30 L109 test
lines, truth = [], {}
for i, P in enumerate(bases[:8]):
    pa, ca = list(AZ), list(AZ)
    rng.shuffle(pa)
    rng.shuffle(ca)
    k = chain_key(rng.randrange(10 ** 5), 5)
    ct = encrypt(P, k, pa, ca)
    lab = f"U{i}"
    truth[lab] = P
    lines.append(solver_line(lab, k, ct, {}, seed(f"d1|{lab}")))
import subprocess  # noqa: E402
from r30lib import BIN, MODELS  # noqa: E402
out = REPO / "r34" / "d1_out"
out.mkdir(exist_ok=True)
procs = []
for h in range(4):
    (out / f"in{h}.txt").write_text("\n".join(lines[h::4]) + "\n")
    procs.append(subprocess.Popen([str(BIN / "solver_s2kp"), str(MODELS["ORTH"]), str(DATA / "quad_log10.f32"), str(out / f"in{h}.txt"),
                                   str(out / f"out{h}.jsonl"), "256", "200000", "0.05", "0"]))
assert all(p.wait() == 0 for p in procs)
best = {}
for h in range(4):
    for ln in open(out / f"out{h}.jsonl"):
        r = json.loads(ln)
        if r["id"] not in best or r["W"] > best[r["id"]]["W"]:
            best[r["id"]] = r
model = load_model(REPO / "k4kit/data/word_model_orth.tsv")
sys.path.insert(0, str(REPO / "k4kit/r30"))
import subprocess as _s  # noqa: E402,F401


def W(text):
    """Word-model score of a plaintext (same DP as solver_s2kp: skip -7, up to 2 edit-matched words)."""
    NEG = -1e99
    n = len(text)
    dp = [[NEG] * 3 for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n):
        for b in range(3):
            if dp[i][b] <= NEG:
                continue
            dp[i + 1][b] = max(dp[i + 1][b], dp[i][b] - 7)
            for j in range(i + 1, min(n, i + 24) + 1):
                w = text[i:j]
                if w in model:
                    ex, ed = model[w]
                    if ex > -1e99:
                        dp[j][b] = max(dp[j][b], dp[i][b] + ex)
                    if ed > -1e99 and b < 2:
                        dp[j][b + 1] = max(dp[j][b + 1], dp[i][b] + ed)
    return max(dp[n])


res = {}
for lab, P in truth.items():
    t = best[lab]["plaintext"]
    res[lab] = {"found_W": best[lab]["W"], "true_W": W(P), "wrong_letters": sum(a != b for a, b in zip(t, P)), "found": t}
    print(lab, f"found W {best[lab]['W']:.1f}  true W {res[lab]['true_W']:.1f}  wrong letters {res[lab]['wrong_letters']}")
n = sum(v["wrong_letters"] <= 5 for v in res.values())
print(f"D1: readable {n}/8 at 256 x 200,000 (L109: 0/8 at 64 x 40,000)")
(REPO / "r34" / "D1_RESULT.json").write_text(json.dumps({"readable": n, "rows": res}, indent=1) + "\n")

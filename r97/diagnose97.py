#!/usr/bin/env python3
"""R97 truth-assisted diagnostics (PREREGISTRATION section 7; reported, never gated). Run only after the last
evaluated version's EVAL.json is committed. D1: one round from the true key. D2: from the true U with k = 4, 8, 12
random swaps and a random V, 2 rounds of warm single anneals. Usage: diagnose97.py LAST_VERSION MODEL.bin"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import r97core as C  # noqa: E402


def inverse(W):
    q = [0] * 26
    for x, y in enumerate(W):
        q[y] = x
    return q


def main():
    last, model_path = int(sys.argv[1]), sys.argv[2]
    assert (HERE / f"eval_v{last}/EVAL.json").exists(), "evaluate first"
    st = json.loads((HERE / "selftest/SELFTEST.json").read_text())
    Ic = st["I_c"]
    truth = json.loads((ROOT / "r94/inputs/PANEL_TRUTH.json").read_text())
    model = C.Model(model_path)
    rows = []
    for rid, lab, ct in C.read_panel():
        t = truth[rid]
        Ut, Vt = inverse(t["W1"]), inverse(t["W2"])
        keep = C.bind(ct, lab, model)
        sd = lambda tag: C.seed_of("970301", rid, 0, tag)  # noqa: E731
        right = lambda U, V: sum(x == y for x, y in zip(C.decrypt(ct, U, V, lab), t["pt"]))  # noqa: E731
        U = C.cond(Vt, "U", Ut, Ic, C.T0 / 4, sd("D1U"))[1]
        V = C.cond(U, "V", Vt, Ic, C.T0 / 4, sd("D1V"))[1]
        row = {"id": rid, "cell": t["cell"], "D1_letters": right(U, V)}
        for k in (4, 8, 12):
            g = random.Random(sd(f"D2k{k}"))
            U = list(Ut)
            for _ in range(k):
                x, y = g.sample(range(26), 2)
                U[x], U[y] = U[y], U[x]
            V = C.rand_perm(sd(f"D2k{k}V"))
            for r in range(1, 3):
                V = C.cond(U, "V", V, Ic, C.T0 / 4, sd(f"D2k{k}V{r}"))[1]
                U = C.cond(V, "U", U, Ic, C.T0 / 4, sd(f"D2k{k}U{r}"))[1]
            row[f"D2_k{k}_letters"] = right(U, V)
        rows.append(row)
        del keep
    summ = {"D1_ge95": sum(r["D1_letters"] >= 95 for r in rows)}
    for k in (4, 8, 12):
        summ[f"D2_k{k}_ge95"] = sum(r[f"D2_k{k}_letters"] >= 95 for r in rows)
    (HERE / "diagnostics").mkdir(exist_ok=True)
    (HERE / "diagnostics/DIAGNOSTICS.json").write_text(json.dumps({"summary": summ, "cases": len(rows), "rows": rows},
                                                                  indent=1) + "\n")
    print("diagnostics", json.dumps(summ))


if __name__ == "__main__":
    main()

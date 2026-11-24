#!/usr/bin/env python3
"""R97 solver (PREREGISTRATION sections 4-5). Reads ONLY r94/inputs/PANEL.tsv (id, label, ciphertext) and the
digest-checked R95 model; never the panel truth. Usage: python3 -I r97/solve97.py VERSION(1|2) MODEL.bin OUTDIR"""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r97core as C  # noqa: E402


def restart_v1(rid, j, Ic, prefix):
    sd = lambda tag: C.seed_of(prefix, rid, j, tag)  # noqa: E731
    U, V = None, C.rand_perm(sd("V0"))
    best = None
    for t in range(1, 5):
        U, V = C.round_v1(U, V, t, Ic, sd)
        s = C.joint(U, V)
        if best is None or s > best[0]:
            best = (s, U, V, t)
    return best


def restart_v2(rid, j, Ic, prefix):
    sd = lambda tag: C.seed_of(prefix, rid, j, tag)  # noqa: E731
    U, V = None, C.rand_perm(sd("V0"))
    best = None
    for t in range(1, 3):
        U, V = C.round_v1(U, V, t, Ic, sd)
        s = C.joint(U, V)
        if best is None or s > best[0]:
            best = (s, U, V, t)
    for k in range(1, 5):
        U, V = list(best[1]), list(best[2])
        g = random.Random(sd(f"K{k}"))
        idx = g.sample(range(26), 8)
        vals = [V[x] for x in idx]
        g.shuffle(vals)
        for x, v in zip(idx, vals):
            V[x] = v
        for t in range(1, 3):
            U = C.cond(V, "U", U, Ic, C.T0 / 4, sd(f"K{k}U{t}"))[1]
            V = C.cond(U, "V", V, Ic, C.T0 / 4, sd(f"K{k}V{t}"))[1]
        s = C.joint(U, V)
        if s > best[0]:
            best = (s, U, V, 2 + k)
    return best


def main():
    version, model_path, out = int(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    st = json.loads((HERE / "selftest/SELFTEST.json").read_text())
    assert st["pass"] and st["I_c"] >= 50000, "self-test did not fix a valid I_c"
    Ic = st["I_c"]
    out.mkdir(parents=True, exist_ok=False)
    model = C.Model(model_path)
    prefix, R, fn = ("970101", 6, restart_v1) if version == 1 else ("970201", 3, restart_v2)
    t0w, t0c = time.time(), time.process_time()
    lines = []
    for rid, lab, ct in C.read_panel():
        case = C.bind(ct, lab, model)
        finals = []
        for j in range(R):
            s, U, V, rnd = fn(rid, j, Ic, prefix)
            text = C.decrypt(ct, U, V, lab)
            assert abs(model.score(text) - s) < 1e-6
            finals.append({"restart": j, "score": s, "U": U, "V": V, "text": text, "best_round": rnd})
        top1 = sorted(range(R), key=lambda k: (-finals[k]["score"], k))[0]
        lines.append(json.dumps({"id": rid, "label": list(lab), "top1": top1, "finals": finals}) + "\n")
        del case
    (out / "RESULTS.jsonl").write_text("".join(lines))
    run = {"version": version, "I_c": Ic, "restarts": R, "T0": C.T0, "seed_prefix": prefix, "cases": len(lines),
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2), "model_sha256": C.MODEL_SHA}
    (out / "RUN.json").write_text(json.dumps(run, indent=1) + "\n")
    print(f"R97 version {version}: {len(lines)} cases, I_c={Ic}, {run['cpu_s']} s CPU")


if __name__ == "__main__":
    main()

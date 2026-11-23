#!/usr/bin/env python3
"""R96 solver. Reads ONLY r96/inputs/CONDITIONS.tsv and the R95 model (digest-checked); never the panel truth.
Usage: python3 -I r96/solve96.py VERSION(1|2) MODEL.bin OUTDIR      (I is read from r96/selftest/SELFTEST.json)"""
import ctypes
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r96core as C  # noqa: E402


def main():
    version, model_path, out = int(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    st = json.loads((HERE / "selftest/SELFTEST.json").read_text())
    assert st["pass"] and st["I"] >= 100000, "self-test did not fix a valid I"
    I = st["I"]
    out.mkdir(parents=True, exist_ok=False)
    model = C.Model(model_path)
    L = C.lib()
    prefix = "960101" if version == 1 else "960201"
    t0w, t0c = time.time(), time.process_time()
    lines = []
    for rid, cond, lab, ct, sup in C.read_conditions():
        mode = 0 if cond == "trueV" else 1          # trueV: U searched; trueU: V searched
        case = C.Case(ct, lab, model)
        case.bind()
        fixed = (ctypes.c_int * 26)(*sup)
        starts = []
        for k in range(C.R):
            seed = C.seed_of(prefix, rid, cond, k)
            w = (ctypes.c_int * 26)()
            if version == 1:
                sc = L.run_v1(fixed, mode, I, C.T0, seed, w)
            else:
                if k < 8:
                    start = C.assignment_start(ct, lab, mode, sup, model, seed)
                    case.bind()
                    sc = L.run_v2(fixed, mode, I, C.T0, C.T0 / 4, seed, (ctypes.c_int * 26)(*start), w)
                else:
                    sc = L.run_v2(fixed, mode, I, C.T0, C.T0, seed, None, w)
            W = list(w)
            U, V = (W, sup) if mode == 0 else (sup, W)
            text = C.decrypt(ct, U, V, lab)
            ref = model.score(text)
            assert abs(ref - sc) < 1e-6, (rid, cond, k, ref, sc)
            starts.append({"start": k, "seed": seed, "score": sc, "searched_inverse_wiring": W, "text": text})
        order = sorted(range(C.R), key=lambda k: (-starts[k]["score"], k))
        top8, seen = [], set()
        for k in order:
            if starts[k]["text"] not in seen:
                seen.add(starts[k]["text"])
                top8.append(k)
            if len(top8) == 8:
                break
        lines.append(json.dumps({"id": rid, "condition": cond, "label": list(lab), "searched": "U" if mode == 0 else "V",
                                 "top1": order[0], "top8": top8, "starts": starts}) + "\n")
    (out / "RESULTS.jsonl").write_text("".join(lines))
    run = {"version": version, "I": I, "R": C.R, "T0": C.T0, "seed_prefix": prefix, "conditions": len(lines),
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2),
           "inputs_sha256": hashlib.sha256((HERE / "inputs/CONDITIONS.tsv").read_bytes()).hexdigest(),
           "model_sha256": C.MODEL_SHA}
    (out / "RUN.json").write_text(json.dumps(run, indent=1) + "\n")
    print(f"R96 version {version}: {len(lines)} conditions, I={I}, {run['cpu_s']} s CPU")


if __name__ == "__main__":
    main()

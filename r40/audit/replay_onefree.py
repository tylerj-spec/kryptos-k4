#!/usr/bin/env python3
"""T6 item 3: run the independent kernel r40/audit/onefree.c on every ciphertext R40 (L134) and R42 (L136) checked
in their whole-family step, and compare with r40/x1_pafree/REVEAL.json and r42/x1_ca_free/REVEAL.json:
settings, consistent count, min V, and the complete list of settings at min V (every archived list is shorter than
the original's cap of 50, so it is complete). POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY; nothing is decrypted.
Letters: the published letters for K4 and the nulls; for in-place plants their sealed true plaintext at the same 24
positions (as the originals did).
Usage: replay_onefree.py OUT.json"""
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUNDS = {"R40": ("PA", ROOT / "r40/x1_pafree", ROOT / "r40/sealed/truth.json"),
          "R42": ("CA", ROOT / "r42/x1_ca_free", ROOT / "r42/sealed/truth.json")}
CARTER, K1K3 = ROOT / "r34/carter_az.txt", ROOT / "k4kit/data/k1k3_plaintext.txt"


def build(tmp):
    exe = Path(tmp) / "onefree"
    subprocess.run(["gcc", "-O3", "-march=native", "-Wall", "-Wextra", "-Werror", "-o", str(exe),
                    str(ROOT / "r40/audit/onefree.c")], check=True)
    return exe


def parse(text):
    meta, mins, hist = {}, [], {}
    for line in text.splitlines():
        f = line.split("\t")
        if f[0] == "min_setting":
            mins.append(f[1])
        elif f[0] == "V":
            hist[int(f[1])] = int(f[2])
        else:
            meta[f[0]] = int(f[1])
    return meta, mins, hist


def main():
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    pos = {o + j: ch for o, t in CLUES for j, ch in enumerate(t)}
    published = "".join(pos.get(i, "?") for i in range(97))
    jobs = []
    for rnd, (mode, exp, truth_p) in ROUNDS.items():
        arch = json.loads((exp / "REVEAL.json").read_text())["whole_family"]
        truth = json.loads(truth_p.read_text())
        for rid in arch:
            ct = (exp / f"{rid}_ct.txt").read_text().strip()
            if rid.startswith("PLANT"):
                pt = truth[rid]["plaintext"]
                want = "".join(pt[i] if i in pos else "?" for i in range(97))
            else:
                want = published
            jobs.append((rnd, mode, rid, ct, want, arch[rid]))
    with tempfile.TemporaryDirectory() as tmp:
        exe = build(tmp)

        def run(job):
            rnd, mode, rid, ct, want, _ = job
            out = Path(tmp) / f"{rnd}_{rid}.tsv"
            subprocess.run([str(exe), mode, ct, want, str(CARTER), str(K1K3), str(out)], check=True,
                           env={"ONEFREE_SELFCHECK": "1"}, capture_output=True)
            return parse(out.read_text())

        with ThreadPoolExecutor(4) as ex:
            results = list(ex.map(run, jobs))
    rows, ok = [], True
    for (rnd, mode, rid, ct, want, a), (meta, mins, hist) in zip(jobs, results):
        same = (meta["settings"] == a["settings"] and meta["consistent"] == a["consistent"] and
                meta["min_V"] == a["min_V"] and mins == a["min_settings"])
        ok &= same
        rows.append({"round": rnd, "id": rid, "equal": same, "replay": {"settings": meta["settings"],
                     "consistent": meta["consistent"], "min_V": meta["min_V"], "min_settings": mins},
                     "archive": {k: a[k] for k in ("settings", "consistent", "min_V", "min_settings")},
                     "V_histogram": hist})
    out = {"classification": "POST-FREEZE CRIB-ASSISTED EXCLUSION-ONLY REPLAY (T6 item 3: R40, R42)",
           "all_equal": ok, "jobs": len(rows), "rows": rows}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
    for r in rows:
        print(r["round"], r["id"], "equal" if r["equal"] else "DISAGREE", r["replay"]["min_V"], r["replay"]["consistent"])
    print("all_equal", ok)


if __name__ == "__main__":
    main()

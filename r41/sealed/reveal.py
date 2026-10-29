#!/usr/bin/env python3
"""R41 SEALED reveal. Run only after EXPDIR/FROZEN.sha256 is committed and pushed.
1. Every frozen file still matches its hash.
2. Plants: rank of the true setting (or its twin) in stage 1 and in the final ranking; letters wrong in that row.
3. Nulls: best final score and best L1.
4. K4: the 20 best final rows are re-encrypted forward (substitute, then transpose) to the ciphertext by separate
   code, and their letters at the 24 published plaintext positions are counted.
5. Whole family: sealed/whole_family over both route parts for K4, the nulls (K4's 24 letters) and the plants (their
   own letters at the same positions).
Writes EXPDIR/REVEAL.json. Usage: python3 -I r41/sealed/reveal.py EXPDIR"""
import array
import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CLUES = {21: "EASTNORTHEAST", 63: "BERLINCLOCK"}
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
       "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}
PARTS = {"A": "C10b5,C10b6,CARTER,K1K3", "B": "C10b5,K1K3"}


def letters(s):
    return "".join(ch for ch in s.upper() if ch.isalpha())


def clue_letters():
    w = ["?"] * 97
    for start, word in CLUES.items():
        for i, ch in enumerate(word):
            w[start + i] = ch
    return "".join(w)


def key_of(label, texts):
    fam, rest = label.split("/", 1)
    if fam not in texts:   # C10b5, C10b6
        b = int(fam[-1])
        k = [int(ch) for ch in rest.removeprefix("primer")]
        assert len(k) == b
        while len(k) < 97:
            k.append((k[-b] + k[-b + 1]) % 10)
        return k
    d, num, off = rest.split("/")
    s = texts[fam][::-1] if d == "rev" else texts[fam]
    off = int(off.removeprefix("off"))
    return [(KRY if num == "KRY" else AZ).index(ch) for ch in s[off:off + 97]]


def parse(setting, texts):
    label, rest = setting.split("|ROUTE=")
    route, rest = rest.split("|CA=")
    ca, op = rest.split("|OP=")
    return key_of(label, texts), route, ca, op


def ys(ct, key, perm, ca, op):
    """Reading-order y: X_i = CT[q_i] with CT[j] = X[perm[j]]."""
    q = [0] * 97
    for j, i in enumerate(perm):
        q[i] = j
    x = [CAS[ca].index(ct[q[i]]) for i in range(97)]
    return [((x[i] - key[i]) if op == "VIG|BEAU" else (x[i] + key[i])) % 26 for i in range(97)]


def forward(pt, key, perm, ca, op, inv_pa):
    X = [CAS[ca][(inv_pa[p] + key[t]) % 26] if op == "VIG|BEAU" else CAS[ca][(inv_pa[p] - key[t]) % 26] for t, p in enumerate(pt)]
    return "".join(X[perm[j]] for j in range(97))


def unigram_logf():
    q = array.array("f")
    with open(REPO / "k4kit/data/quad_log10.f32", "rb") as f:
        q.fromfile(f, 456976)
    f1 = [sum(10.0 ** v for v in q[a * 17576:(a + 1) * 17576]) for a in range(26)]
    tot = sum(f1)
    return sorted((math.log(v / tot) for v in f1), reverse=True)


def L1(y, lf):
    cnt = sorted((y.count(v) for v in range(26)), reverse=True)
    return sum(c * l for c, l in zip(cnt, lf) if c)


def twin(setting):
    """Declared twin of a base-10 chain setting: digit-complement primer with the other operation (same route, CA)."""
    label, rest = setting.split("|ROUTE=")
    if "/primer" not in label:
        return None
    fam, primer = label.split("/primer")
    route, rest2 = rest.split("|CA=")
    ca, op = rest2.split("|OP=")
    comp = "".join(str((10 - int(ch)) % 10) for ch in primer)
    return f"{fam}/primer{comp}|ROUTE={route}|CA={ca}|OP={'VARB' if op == 'VIG|BEAU' else 'VIG|BEAU'}"


def rows(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def main():
    exp = Path(sys.argv[1]).resolve()
    out = exp / "out"
    bad = []
    for ln in (exp / "FROZEN.sha256").read_text().splitlines():
        h, p = ln.split("  ", 1)
        if hashlib.sha256((REPO / p).read_bytes()).hexdigest() != h:
            bad.append(p)
    assert not bad, f"frozen files changed: {bad}"
    truth = json.loads((HERE / "truth.json").read_text())
    texts = {"CARTER": letters((REPO / "r34/carter_az.txt").read_text()),
             "K1K3": letters((REPO / "k4kit/data/k1k3_plaintext.txt").read_text())}
    perms = {}
    for p in PARTS:
        for ln in (out / f"routes_{p}.txt").read_text().splitlines():
            name, order, ps = ln.split()
            if order == "S_then_T":
                perm = [int(v) for v in ps.split(",")]
                assert sorted(perm) == list(range(97))
                perms[name] = perm
    lf = unigram_logf()
    rep = {"plants": {}, "nulls": {}, "k4": {}}
    for tag, t in sorted(truth.items()):
        ct = letters((exp / f"{tag}_ct.txt").read_text())
        key, route, ca, op = parse(t["setting"], texts)
        assert perms[route] == t["perm"]
        true_l1 = L1(ys(ct, key, perms[route], ca, op), lf)
        ok = {t["setting"], twin(t["setting"])}
        l1_rank = next((int(r["rank"]) for r in rows(out / f"{tag}_top.tsv") if r["setting"] in ok), None)
        fin = rows(out / f"{tag}_final.tsv")
        f_rank = next((i + 1 for i, r in enumerate(fin) if r["setting"] in ok), None)
        tr = fin[f_rank - 1] if f_rank else None
        rep["plants"][tag] = {
            "family": t["family"], "part": t["part"], "setting": t["setting"], "true_L1": round(true_l1, 4), "L1_rank": l1_rank,
            "final_rank": f_rank, "true_row_score": float(tr["score"]) if tr else None,
            "true_row_wrong_letters": sum(a != b for a, b in zip(tr["plaintext"], t["plaintext"])) if tr else None,
            "best_setting": fin[0]["setting"], "best_score": float(fin[0]["score"]), "best_row_plaintext": fin[0]["plaintext"]}
    for f in sorted(exp.glob("NULL_*_ct.txt")):
        tag = f.name[:-7]
        fin = rows(out / f"{tag}_final.tsv")
        mx = max(float((out / f"{tag}_hist_{p}.tsv").read_text().split()[4]) for p in PARTS)
        rep["nulls"][tag] = {"best_score": float(fin[0]["score"]), "best_setting": fin[0]["setting"], "max_L1": mx}
    ct = letters((exp / "K4_ct.txt").read_text())
    fin = rows(out / "K4_final.tsv")
    want = clue_letters()
    checked = []
    for r in fin[:20]:
        key, route, ca, op = parse(r["setting"], texts)
        y = ys(ct, key, perms[route], ca, op)
        m = r["map"]
        assert sorted(m) == list(AZ), "map is not a permutation"
        assert all(r["plaintext"][t] == m[y[t]] for t in range(97)), "plaintext does not follow from map"
        assert forward(r["plaintext"], key, perms[route], ca, op, {m[v]: v for v in range(26)}) == ct, "re-encryption failed"
        checked.append({"setting": r["setting"], "score": float(r["score"]), "L1": float(r["L1"]),
                        "clue_matches": sum(r["plaintext"][i] == w for i, w in enumerate(want) if w != "?"), "plaintext": r["plaintext"]})
    settings = {p: int((out / f"K4_hist_{p}.tsv").read_text().split()[2]) for p in PARTS}
    rep["k4"] = {"settings": settings, "max_L1": max(float((out / f"K4_hist_{p}.tsv").read_text().split()[4]) for p in PARTS),
                 "best_score": float(fin[0]["score"]), "forward_check": "top 20 rows re-encrypt exactly to K4", "top20": checked}
    wf = out / "whole_family"
    subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(HERE / "whole_family.cpp"), "-o", str(wf)], check=True)
    jobs = [("K4", "K4", want)] + [(t, t, want) for t in rep["nulls"]]
    jobs += [(t, t, "".join(truth[t]["plaintext"][i] if want[i] != "?" else "?" for i in range(97))) for t in sorted(truth)]
    cmds = [(name, p, [str(wf), str(exp / f"{tag}_ct.txt"), str(REPO / "r34/carter_az.txt"), str(REPO / "k4kit/data/k1k3_plaintext.txt"),
                       str(out / f"routes_{p}.txt"), fams, w, str(out / f"WF_{name}_{p}.tsv")])
            for name, tag, w in jobs for p, fams in PARTS.items()]
    running = []
    for c in cmds:
        while len(running) >= 4:
            assert running.pop(0).wait() == 0
        running.append(subprocess.Popen(c[2]))
    for p in running:
        assert p.wait() == 0
    rep["whole_family"] = {}
    for name, _, _ in jobs:
        tot, cons, minv, mins = 0, 0, None, []
        for p in PARTS:
            lines = (out / f"WF_{name}_{p}.tsv").read_text().splitlines()
            meta = {ln.split("\t")[0][2:]: ln.split("\t")[1] for ln in lines if ln.startswith("# ") and not ln.startswith("# min_setting")}
            tot += int(meta["settings"])
            cons += int(meta["consistent_settings(V=0)"])
            v = int(meta["min_V"])
            ms = [ln.split("\t")[1] for ln in lines if ln.startswith("# min_setting")]
            if minv is None or v < minv:
                minv, mins = v, ms
            elif v == minv:
                mins += ms
        rep["whole_family"][name] = {"settings": tot, "consistent": cons, "min_V": minv, "min_settings": mins}
    P = rep["plants"]
    gate_rank = sum(v["final_rank"] == 1 for v in P.values())
    gate_wf = sum(rep["whole_family"][t]["min_V"] == 0 and any(s in {truth[t]["setting"], twin(truth[t]["setting"])}
                                                                 for s in rep["whole_family"][t]["min_settings"]) for t in truth)
    null_best = max(v["best_score"] for v in rep["nulls"].values())
    plant_min = min((v["true_row_score"] for v in P.values() if v["true_row_score"] is not None), default=None)
    thr = (null_best + plant_min) / 2 if plant_min is not None else None
    k4_clue_max = max(r["clue_matches"] for r in checked)
    rep["decision"] = {
        "gate_plants_rank1": f"{gate_rank}/6", "gate_whole_family_plants_true_setting_consistent": f"{gate_wf}/6",
        "gate_passed": gate_rank >= 5 and gate_wf == 6, "score_threshold": thr, "null_best": null_best, "plant_true_min": plant_min,
        "k4_best_score": rep["k4"]["best_score"], "k4_top20_clue_matches_max": k4_clue_max,
        "k4_candidate": (thr is not None and rep["k4"]["best_score"] >= thr) or k4_clue_max >= 20,
        "k4_whole_family_consistent": rep["whole_family"]["K4"]["consistent"], "k4_whole_family_min_V": rep["whole_family"]["K4"]["min_V"]}
    (exp / "REVEAL.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep["decision"], indent=1))
    for tag, v in P.items():
        print(tag, v["part"], v["family"], "L1 rank", v["L1_rank"], "final rank", v["final_rank"], "wrong", v["true_row_wrong_letters"])
    print("whole family:", {k: (v["settings"], v["consistent"], v["min_V"]) for k, v in rep["whole_family"].items()})


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""R42 SEALED reveal. Run only after EXPDIR/FROZEN.sha256 is committed and pushed.
1. Every frozen file still matches its hash.
2. Plants: rank of the true setting (or twin) in stage 1 and in the final ranking; letters wrong in that row.
3. Nulls: best final score and best stage-1 score.
4. K4: the 20 best final rows are re-encrypted forward to the ciphertext by separate code (fixed plaintext
   alphabet, the solved cipher alphabet), and their letters at the 24 published positions are counted.
5. Whole family (in place): sealed/whole_family over K4, the nulls (K4's 24 letters) and the plants (their own).
Writes EXPDIR/REVEAL.json. Usage: python3 -I r42/sealed/reveal.py EXPDIR"""
import array
import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R40 = HERE.parent
REPO = R40.parent
CLUES = {21: "EASTNORTHEAST", 63: "BERLINCLOCK"}
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
PAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
       "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}


def letters(s):
    return "".join(ch for ch in s.upper() if ch.isalpha())


def clue_letters():
    w = ["?"] * 97
    for start, word in CLUES.items():
        for i, ch in enumerate(word):
            w[start + i] = ch
    return "".join(w)


def key_of(label, texts):
    """Independent key generator from a setting label."""
    fam, rest = label.split("/", 1)
    if fam not in texts:   # chain families C10b5, C10b6, C10b7, C26b5
        base, b = int(fam[1:fam.index("b")]), int(fam[fam.index("b") + 1:])
        sym = "0123456789ABCDEFGHIJKLMNOP"
        k = [sym.index(ch) for ch in rest.removeprefix("primer")]
        assert len(k) == b
        while len(k) < 97:
            k.append((k[-b] + k[-b + 1]) % base)
        return k
    d, num, off = rest.split("/")
    s = texts[fam][::-1] if d == "rev" else texts[fam]
    off = int(off.removeprefix("off"))
    al = KRY if num == "KRY" else AZ
    return [al.index(ch) for ch in s[off:off + 97]]


def parse(setting, texts):
    label, rest = setting.split("|PA=")
    pa, op = rest.split("|OP=")
    return key_of(label, texts), pa, op


def forward(pt, key, pa, op, ca):
    """Encrypt pt: VIG c = CA[PA^-1(p) + k]; BEAU|VARB in its VARB form c = CA[PA^-1(p) - k]."""
    return "".join(ca[(PAS[pa].index(p) + key[t]) % 26] if op == "VIG" else ca[(PAS[pa].index(p) - key[t]) % 26]
                   for t, p in enumerate(pt))


def assign_score(ct, key, pa, op, lf):
    """Unigram-optimal cipher alphabet score, by brute-force-free exact method: Hungarian (pure Python)."""
    cost = [[0.0] * 26 for _ in range(26)]
    for i, c in enumerate(ct):
        for t in range(26):
            x = (t - key[i]) % 26 if op == "VIG" else (t + key[i]) % 26
            cost[ord(c) - 65][t] -= lf[ord(PAS[pa][x]) - 65]
    return -hungarian(cost)


def hungarian(a):
    n = len(a)
    INF = float("inf")
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [INF] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    return sum(a[p[j] - 1][j - 1] for j in range(1, n + 1))


def unigram_logf():
    q = array.array("f")
    with open(REPO / "k4kit/data/quad_log10.f32", "rb") as f:
        q.fromfile(f, 456976)
    f1 = [sum(10.0 ** v for v in q[a * 17576:(a + 1) * 17576]) for a in range(26)]
    tot = sum(f1)
    return [math.log(v / tot) for v in f1]


def twin(setting):
    """The declared twin of a chain setting: digit-complement primer with the other operation (same CA)."""
    label, rest = setting.split("|PA=")
    if "/primer" not in label:
        return None
    fam, primer = label.split("/primer")
    comp = "".join(str((10 - int(ch)) % 10) for ch in primer)
    pa, op = rest.split("|OP=")
    return f"{fam}/primer{comp}|PA={pa}|OP={'BEAU|VARB' if op == 'VIG' else 'VIG'}"


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
    lf = unigram_logf()
    rep = {"plants": {}, "nulls": {}, "k4": {}}
    for tag, t in sorted(truth.items()):
        ct = letters((exp / f"{tag}_ct.txt").read_text())
        key, pa, op = parse(t["setting"], texts)
        true_s1 = assign_score(ct, key, pa, op, lf)
        ok = {t["setting"], twin(t["setting"])}
        s1_rank = next((int(r["rank"]) for r in rows(out / f"{tag}_top.tsv") if r["setting"] in ok), None)
        fin = rows(out / f"{tag}_final.tsv")
        f_rank = next((i + 1 for i, r in enumerate(fin) if r["setting"] in ok), None)
        tr = fin[f_rank - 1] if f_rank else None
        rep["plants"][tag] = {
            "family": t["family"], "setting": t["setting"], "true_stage1_score": round(true_s1, 4), "stage1_rank": s1_rank,
            "final_rank": f_rank, "true_row_score": float(tr["score"]) if tr else None,
            "true_row_wrong_letters": sum(a != b for a, b in zip(tr["plaintext"], t["plaintext"])) if tr else None,
            "best_setting": fin[0]["setting"], "best_score": float(fin[0]["score"]), "best_row_plaintext": fin[0]["plaintext"]}
    for f in sorted(exp.glob("NULL_*_ct.txt")):
        tag = f.name[:-7]
        fin = rows(out / f"{tag}_final.tsv")
        hist = (out / f"{tag}_hist.tsv").read_text().split()
        rep["nulls"][tag] = {"best_score": float(fin[0]["score"]), "best_setting": fin[0]["setting"], "max_stage1": float(hist[4])}
    ct = letters((exp / "K4_ct.txt").read_text())
    fin = rows(out / "K4_final.tsv")
    hist = (out / "K4_hist.tsv").read_text().split()
    want = clue_letters()
    checked = []
    for r in fin[:20]:
        key, pa, op = parse(r["setting"], texts)
        assert sorted(r["cipher_alphabet"]) == list(AZ), "cipher alphabet is not a permutation"
        assert forward(r["plaintext"], key, pa, op, r["cipher_alphabet"]) == ct, "re-encryption failed"
        checked.append({"setting": r["setting"], "score": float(r["score"]), "stage1": float(r["L1"]),
                        "clue_matches": sum(r["plaintext"][i] == w for i, w in enumerate(want) if w != "?"),
                        "plaintext": r["plaintext"], "cipher_alphabet": r["cipher_alphabet"]})
    rep["k4"] = {"settings": int(hist[2]), "max_stage1": float(hist[4]), "best_score": float(fin[0]["score"]),
                 "forward_check": "top 20 rows re-encrypt exactly to K4", "top20": checked}
    wf = out / "whole_family"
    subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(HERE / "whole_family.cpp"), "-o", str(wf)], check=True)
    jobs = [("K4", want)] + [(t, want) for t in rep["nulls"]]
    jobs += [(t, "".join(truth[t]["plaintext"][i] if want[i] != "?" else "?" for i in range(97))) for t in sorted(truth)]
    running = []
    for name, w in jobs:
        while len(running) >= 4:
            assert running.pop(0).wait() == 0
        running.append(subprocess.Popen([str(wf), str(exp / f"{name}_ct.txt"), str(REPO / "r34/carter_az.txt"),
                                         str(REPO / "k4kit/data/k1k3_plaintext.txt"), w, str(out / f"WF_{name}.tsv")]))
    for p in running:
        assert p.wait() == 0
    rep["whole_family"] = {}
    for name, _ in jobs:
        lines = (out / f"WF_{name}.tsv").read_text().splitlines()
        meta = {ln.split("\t")[0][2:]: ln.split("\t")[1] for ln in lines if ln.startswith("# ") and not ln.startswith("# min_setting")}
        rep["whole_family"][name] = {"settings": int(meta["settings"]), "consistent": int(meta["consistent_settings(V=0)"]),
                                     "min_V": int(meta["min_V"]),
                                     "min_settings": [ln.split("\t")[1] for ln in lines if ln.startswith("# min_setting")]}
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
        print(tag, v["family"], "stage-1 rank", v["stage1_rank"], "final rank", v["final_rank"], "wrong", v["true_row_wrong_letters"])
    print("whole family:", {k: (v["consistent"], v["min_V"]) for k, v in rep["whole_family"].items()})


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""R40 SEALED reveal. Run only after EXPDIR/FROZEN.sha256 is committed and pushed.
1. Every frozen file still matches its hash.
2. Plants: rank of the true setting in stage 1 (L1) and in the final ranking; letters wrong in the best row.
3. Nulls: best final score and best L1.
4. K4: the 20 best final rows are re-encrypted forward to the ciphertext by separate code, and their letters at the
   24 published positions are counted.
5. Whole family (in place): sealed/whole_family over K4, the nulls (with K4's 24 letters) and the in-place plants
   (with their own letters at the same positions).
Writes EXPDIR/REVEAL.json. Usage: python3 -I r40/sealed/reveal.py EXPDIR"""
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
CAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
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
    label, ca, op = setting.split("|CA=")[0], setting.split("|CA=")[1].split("|OP=")[0], setting.split("|OP=")[1]
    return key_of(label, texts), ca, op


def ys(ct, key, ca, op):
    x = [CAS[ca].index(c) for c in ct]
    return [((x[t] - key[t]) if op == "VIG|BEAU" else (x[t] + key[t])) % 26 for t in range(97)]


def forward(pt, key, ca, op, inv_pa):
    """Encrypt pt with PA^-1 given as a dict letter -> number: VIG form c = CA[a + k], VARB form c = CA[a - k]."""
    return "".join(CAS[ca][(inv_pa[p] + key[t]) % 26] if op == "VIG|BEAU" else CAS[ca][(inv_pa[p] - key[t]) % 26]
                   for t, p in enumerate(pt))


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
    """The declared twin of a chain setting: digit-complement primer with the other operation (same CA)."""
    label, rest = setting.split("|CA=")
    fam, primer = label.split("/primer") if "/primer" in label else (label, None)
    if primer is None:
        return None
    base = int(fam[1:fam.index("b")])
    sym = "0123456789ABCDEFGHIJKLMNOP"
    comp = "".join(sym[(base - sym.index(ch)) % base] for ch in primer)
    ca, op = rest.split("|OP=")
    return f"{fam}/primer{comp}|CA={ca}|OP={'VARB' if op == 'VIG|BEAU' else 'VIG|BEAU'}"


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
        key, ca, op = parse(t["setting"], texts)
        y = ys(ct, key, ca, op)
        true_l1 = L1(y, lf)
        top = rows(out / f"{tag}_top.tsv")
        ok = {t["setting"], twin(t["setting"])}
        l1_rank = next((int(r["rank"]) for r in top if r["setting"] in ok), None)
        fin = rows(out / f"{tag}_final.tsv")
        f_rank = next((i + 1 for i, r in enumerate(fin) if r["setting"] in ok), None)
        target = t["transposed_plaintext"] if t["transposed"] else t["plaintext"]
        best = fin[0]
        true_row = fin[f_rank - 1] if f_rank else None
        rep["plants"][tag] = {
            "family": t["family"], "transposed": t["transposed"], "setting": t["setting"], "true_L1": round(true_l1, 4),
            "L1_rank": l1_rank, "final_rank": f_rank, "best_setting": best["setting"], "best_score": float(best["score"]),
            "true_row_score": float(true_row["score"]) if true_row else None,
            "true_row_wrong_letters": sum(a != b for a, b in zip(true_row["plaintext"], target)) if true_row else None,
            "best_row_plaintext": best["plaintext"]}
    for f in sorted(exp.glob("NULL_*_ct.txt")):
        tag = f.name[:-7]
        fin = rows(out / f"{tag}_final.tsv")
        hist = (out / f"{tag}_hist.tsv").read_text().splitlines()[0].split()
        rep["nulls"][tag] = {"best_score": float(fin[0]["score"]), "best_setting": fin[0]["setting"], "max_L1": float(hist[4]),
                             "settings": int(hist[2])}
    ct = letters((exp / "K4_ct.txt").read_text())
    fin = rows(out / "K4_final.tsv")
    hist = (out / "K4_hist.tsv").read_text().splitlines()[0].split()
    want = clue_letters()
    checked = []
    for r in fin[:20]:
        key, ca, op = parse(r["setting"], texts)
        y = ys(ct, key, ca, op)
        m = r["map"]
        assert sorted(m) == list(AZ), "map is not a permutation"
        assert all(r["plaintext"][t] == m[y[t]] for t in range(97)), "plaintext does not follow from map"
        inv_pa = {m[v]: v for v in range(26)}
        assert forward(r["plaintext"], key, ca, op, inv_pa) == ct, "re-encryption failed"
        checked.append({"setting": r["setting"], "score": float(r["score"]), "L1": float(r["L1"]),
                        "clue_matches": sum(r["plaintext"][i] == w for i, w in enumerate(want) if w != "?"),
                        "plaintext": r["plaintext"]})
    rep["k4"] = {"settings": int(hist[2]), "max_L1": float(hist[4]), "best_score": float(fin[0]["score"]),
                 "forward_check": "top 20 rows re-encrypt exactly to K4", "top20": checked}
    # whole family, in place
    wf = out / "whole_family"
    subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(HERE / "whole_family.cpp"), "-o", str(wf)], check=True)
    jobs = [("K4", "K4", want)] + [(t, t, want) for t in rep["nulls"]]
    jobs += [(t, t, "".join(truth[t]["plaintext"][i] if want[i] != "?" else "?" for i in range(97)))
             for t in sorted(truth) if not truth[t]["transposed"]]
    procs = []
    for name, tag, w in jobs:
        procs.append((name, subprocess.Popen([str(wf), str(exp / f"{tag}_ct.txt"), str(REPO / "r34/carter_az.txt"),
                                              str(REPO / "k4kit/data/k1k3_plaintext.txt"), w, str(out / f"WF_{name}.tsv")])))
        if len(procs) % 4 == 0:
            for _, p in procs[-4:]:
                assert p.wait() == 0
    for _, p in procs:
        assert p.wait() == 0
    rep["whole_family"] = {}
    for name, _, _ in jobs:
        meta = {ln.split("\t")[0][2:]: ln.split("\t")[1] for ln in (out / f"WF_{name}.tsv").read_text().splitlines() if ln.startswith("# ") and not ln.startswith("# min_setting")}
        mins = [ln.split("\t")[1] for ln in (out / f"WF_{name}.tsv").read_text().splitlines() if ln.startswith("# min_setting")]
        rep["whole_family"][name] = {"settings": int(meta["settings"]), "consistent": int(meta["consistent_settings(V=0)"]),
                                     "min_V": int(meta["min_V"]), "min_settings": mins}
    # decisions as pre-registered
    P = rep["plants"]
    ident = [v for v in P.values() if not v["transposed"]]
    trans = [v for v in P.values() if v["transposed"]]
    gate_id = sum(v["final_rank"] == 1 for v in ident)
    gate_t = sum(v["L1_rank"] is not None for v in trans)
    wf_plants = sum(rep["whole_family"][t]["min_V"] == 0 and any(s in {truth[t]["setting"], twin(truth[t]["setting"])} for s in rep["whole_family"][t]["min_settings"])
                    for t in truth if not truth[t]["transposed"])
    null_best = max(v["best_score"] for v in rep["nulls"].values())
    plant_min = min(v["true_row_score"] for v in ident if v["true_row_score"] is not None)
    thr = (null_best + plant_min) / 2
    k4_best = rep["k4"]["best_score"]
    k4_clue_max = max(r["clue_matches"] for r in checked)
    rep["decision"] = {
        "gate_in_place_plants_rank1": f"{gate_id}/6", "gate_transposed_plants_in_top5000": f"{gate_t}/6",
        "gate_whole_family_plants_true_setting_consistent": f"{wf_plants}/6",
        "gate_passed": gate_id == 6 and gate_t >= 5 and wf_plants == 6,
        "score_threshold": round(thr, 4), "null_best": null_best, "plant_true_min": plant_min,
        "k4_best_score": k4_best, "k4_top20_clue_matches_max": k4_clue_max,
        "k4_candidate": k4_best >= thr or k4_clue_max >= 20,
        "k4_whole_family_consistent": rep["whole_family"]["K4"]["consistent"],
        "k4_max_L1": rep["k4"]["max_L1"], "null_max_L1": max(v["max_L1"] for v in rep["nulls"].values()),
        "transposed_plant_true_L1_min": min(v["true_L1"] for v in trans)}
    (exp / "REVEAL.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep["decision"], indent=1))
    for tag, v in P.items():
        print(tag, v["family"], "T" if v["transposed"] else "ID", "L1 rank", v["L1_rank"], "final rank", v["final_rank"], "wrong", v["true_row_wrong_letters"])
    print("whole family:", {k: (v["consistent"], v["min_V"]) for k, v in rep["whole_family"].items()})


if __name__ == "__main__":
    main()

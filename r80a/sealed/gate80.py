#!/usr/bin/env python3
"""R80a verify + gate (after the blind results are frozen and pushed). Rules fixed in r80a/PREREGISTRATION.md.
Verify (no truth): every stored decode (top 5 and the best of each family) re-encrypts to its ciphertext by the
explicit encryptor (r80a/two80.py encrypt) under its stored setting, and each RESULTS best is its top decode.
Gate (truth opened only after verify passes):
  recovered  = the best decode agrees with the planted plaintext in >= 95 of 97 letters (a shadow decode, half right,
               is never credited: r80/FABLE_IDENTIFIABILITY.md §1.6); exact and >= 85 also reported;
  confident  = the best decode scores >= CUT_LM (letter model) AND >= CUT_WORD (word model) per letter;
  family F PASSES iff >= 18 of its 20 positives are recovered AND confident, AND 0/100 negatives are confident,
  AND verify passed. STRETCH plants (free key 11..12) are reported only.
Reported by listed-key length, free-key length, their gcd and lcm, and spelling kind.
Usage: gate80.py BLIND.tsv RUN_DIR SEALED_TRUTH.json REPORT.json     (verify only: gate80.py --verify TSV RUN_DIR OUT.json)"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r80a"))
import two80 as T  # noqa: E402

CUT_LM, CUT_WORD = -1.30, -2.50      # fixed in r80a/PREREGISTRATION.md
BAR, REC = 18, 95


def verify(tsv, run):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    problems, n = [], 0
    for rid, ct in cts.items():
        r = res[rid]
        if r["best"] != r["top"][0]:
            problems.append(f"best not top {rid}")
        for e in r["top"] + list(r["best_by_fam"].values()):
            n += 1
            if T.encrypt(e["text"], e["setting"]) != ct:
                problems.append(f"witness {rid} {e['fam']}")
    return {"witnesses": n, "problems": problems[:50], "passed": not problems}


def table(rows, key):
    t = defaultdict(lambda: [0, 0, 0])
    for x in rows:
        k = str(key(x))
        t[k][0] += x["ok"]
        t[k][1] += x["exact"]
        t[k][2] += 1
    return {k: {"ok": v[0], "exact": v[1], "n": v[2]} for k, v in sorted(t.items(), key=lambda kv: (len(kv[0]), kv[0]))}


def main():
    if sys.argv[1] == "--verify":
        tsv, run, out = sys.argv[2:5]
        v = verify(tsv, run)
        Path(out).write_text(json.dumps(v, indent=1) + "\n")
        print("verify:", v["witnesses"], "witnesses,", "PASSED" if v["passed"] else f"FAILED {v['problems'][:5]}")
        return
    tsv, run, truth_p, rep = sys.argv[1:5]
    ver = verify(tsv, run)
    print("verify:", ver["witnesses"], "witnesses,", "PASSED" if ver["passed"] else f"FAILED {ver['problems'][:5]}")
    if not ver["passed"]:
        raise SystemExit("verify failed: truth not opened")
    truth = json.loads(Path(truth_p).read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    rows = []
    for rid, t in sorted(truth.items()):
        b = res[rid]["best"]
        conf = b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD
        row = {"id": rid, "kind": t["kind"], "best_fam": b["fam"], "lm_per_letter": b["lm_per_letter"],
               "word_per_letter": b["word_per_letter"], "confident": conf,
               "fam_best_lm": {f: e["lm_per_letter"] for f, e in res[rid]["best_by_fam"].items()}}
        if t["kind"].startswith("POS") or t["kind"] == "STRETCH":
            lw, m = len(t["setting"]["word"]), len(t["setting"]["free"])
            right = sum(x == y for x, y in zip(b["text"], t["pt"]))
            row.update({"fam": t["fam"], "lw": lw, "m": m, "gcd": math.gcd(lw, m), "lcm": lw * m // math.gcd(lw, m),
                        "letters_right": right, "exact": right == 97, "rec95": right >= REC, "rec85": right >= 85,
                        "ok": right >= REC and conf, "same_family": b["fam"] == t["fam"]})
        rows.append(row)
    pos = [x for x in rows if x["kind"].startswith("POS")]
    stretch = [x for x in rows if x["kind"] == "STRETCH"]
    neg = [x for x in rows if x["kind"].startswith("NEG_")]
    negconf = sum(x["confident"] for x in neg)
    fams = {}
    for f in T.FAMS:
        P = [x for x in pos if x["fam"] == f]
        ok = sum(x["ok"] for x in P)
        fams[f] = {"ok": ok, "n": len(P), "exact": sum(x["exact"] for x in P), "rec95": sum(x["rec95"] for x in P),
                   "rec85": sum(x["rec85"] for x in P),
                   "by_kind": {k: [sum(x["ok"] for x in P if x["kind"] == k), sum(x["kind"] == k for x in P)]
                               for k in ("POS", "POS_MISSP", "POS_NONSTD")},
                   "stretch": [[x["lw"], x["m"], x["ok"], x["letters_right"]] for x in stretch if x["fam"] == f],
                   "neg_lm_max": max(x["fam_best_lm"].get(f, -9) for x in neg),
                   "passed": ok >= BAR and negconf == 0 and ver["passed"]}
    allpos = pos + stretch
    summ = {"families": fams, "passed_families": [f for f in T.FAMS if fams[f]["passed"]],
            "positives": {"n": len(pos), "ok": sum(x["ok"] for x in pos), "exact": sum(x["exact"] for x in pos),
                          "rec95": sum(x["rec95"] for x in pos), "rec85": sum(x["rec85"] for x in pos),
                          "lm_min_ok": min((x["lm_per_letter"] for x in pos if x["ok"]), default=None),
                          "word_min_ok": min((x["word_per_letter"] for x in pos if x["ok"]), default=None)},
            "by_free_length": table(allpos, lambda x: x["m"]),
            "by_listed_length": table(allpos, lambda x: x["lw"]),
            "by_gcd": table(allpos, lambda x: x["gcd"]),
            "by_lcm": table(allpos, lambda x: "<=24" if x["lcm"] <= 24 else "25-48" if x["lcm"] <= 48 else ">=49"),
            "by_kind": table(pos, lambda x: x["kind"]),
            "negatives": {"n": len(neg), "confident": negconf, "lm_max": max(x["lm_per_letter"] for x in neg),
                          "word_max": max(x["word_per_letter"] for x in neg),
                          "by_kind_lm_max": {k: max(x["lm_per_letter"] for x in neg if x["kind"] == k)
                                             for k in sorted({x["kind"] for x in neg})}},
            "theorem_k_log10_settings": T.log10_settings()}
    Path(rep).write_text(json.dumps({"cut_lm": CUT_LM, "cut_word": CUT_WORD, "bar": BAR, "recovered_letters": REC,
                                     "verify": ver, "summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()

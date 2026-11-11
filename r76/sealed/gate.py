#!/usr/bin/env python3
"""R76 verify + gate (after the blind results are frozen and pushed). Rules fixed in r76/PREREGISTRATION.md.
Verify (no truth): every stored decode (top 5, best of each sub-family, packet) re-encrypts to its ciphertext by the
explicit encryptor (r76/families.py encrypt) under its stored setting, and each RESULTS best is its top decode.
Gate (truth opened only after verify passes):
  recovered  = the best decode is the exact enciphered plaintext (97/97; misspellings included);
  confident  = the best decode scores >= CUT_LM per letter (letter model) AND >= CUT_WORD per letter (word model);
  PASS       = >= 54/60 positives recovered AND confident, AND 0/100 negatives confident, AND verify passed.
Usage: gate.py BLIND.tsv RUN_DIR SEALED_TRUTH.json REPORT.json     (verify only: gate.py --verify TSV RUN_DIR OUT.json)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
import families as F  # noqa: E402

CUT_LM, CUT_WORD = -1.45, -2.50      # fixed in r76/PREREGISTRATION.md (R74/R75 cuts, confirmed by r76/results/DEV.json)
BAR = 54


def verify(tsv, run):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    problems, n = [], 0
    for rid, ct in cts.items():
        r = res[rid]
        if r["best"] != r["top"][0]:
            problems.append(f"best not top {rid}")
        stored = r["top"] + list(r["best_by_sub"].values())
        pp = Path(run) / "packet" / f"{rid}.json"
        if pp.exists():
            stored += json.loads(pp.read_text())
        for e in stored:
            n += 1
            if F.encrypt(e["text"], e["setting"]) != ct:
                problems.append(f"witness {rid} {e['sub']}")
    return {"witnesses": n, "problems": problems[:50], "passed": not problems}


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
        row = {"id": rid, "kind": t["kind"], "lm_per_letter": b["lm_per_letter"],
               "word_per_letter": b["word_per_letter"], "confident": conf}
        if t["kind"].startswith("POS"):
            rec = b["text"] == t["pt"]
            row.update({"sub": t["sub"], "recovered": rec, "ok": rec and conf, "same_setting": b["setting"] == t["setting"],
                        "letters_right": sum(x == y for x, y in zip(b["text"], t["pt"]))})
        rows.append(row)
    pos = [x for x in rows if x["kind"].startswith("POS")]
    neg = [x for x in rows if x["kind"].startswith("NEG_")]
    ok = sum(x["ok"] for x in pos)
    summ = {"positives": {"n": len(pos), "recovered_and_confident": ok, "recovered": sum(x["recovered"] for x in pos),
                          "same_setting": sum(x["same_setting"] for x in pos),
                          "ok_by_sub": {s: [sum(x["ok"] for x in pos if x["sub"] == s), sum(x["sub"] == s for x in pos)]
                                        for s in F.SUBS},
                          "misspelled_ok": [sum(x["ok"] for x in pos if x["kind"] == "POS_MISSPELLED"),
                                            sum(x["kind"] == "POS_MISSPELLED" for x in pos)],
                          "lm_min": min(x["lm_per_letter"] for x in pos),
                          "word_min": min(x["word_per_letter"] for x in pos)},
            "negatives": {"n": len(neg), "confident": sum(x["confident"] for x in neg),
                          "lm_max": max(x["lm_per_letter"] for x in neg),
                          "word_max": max(x["word_per_letter"] for x in neg)}}
    summ["passed"] = ok >= BAR and summ["negatives"]["confident"] == 0 and ver["passed"]
    Path(rep).write_text(json.dumps({"cut_lm": CUT_LM, "cut_word": CUT_WORD, "bar": BAR, "verify": ver, "summary": summ,
                                     "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()

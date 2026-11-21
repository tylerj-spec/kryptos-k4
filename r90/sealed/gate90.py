#!/usr/bin/env python3
"""R90 SEALED gate evaluation: the only step that opens the holdout truth. Run ONLY after the blind holdout outputs,
their witness check (passed) and GATE_FROZEN.sha256 are committed and PUSHED, and only with the truth file whose sha256
was committed before the run (TRUTH_SHA256). Rules fixed in r90/PREREGISTRATION.md G1 (ChatGPT's design bars, with the
key criterion and the stage-1 retention bar that its R89 review asked to be explicit):
  ok        the best decode (letter-model maximum over the 256 retained) is from F26C, has the RIGHT KEY under R90's
            equivalence (f26c.same_key: same alphabet class, b, u, v, outer stage), >= 95/97 letters equal to the
            enciphered text, and is confident (letter model >= -1.30 AND word model >= -2.50 per letter);
  exact     ok with 97/97;   retained   the true setting is among the 256 kept by stage 1 (quadgrams).
  GO iff ok >= 42/48; exact >= 36/48; >= 9/12 in every block stratum; >= 12/16 in every genre; >= 8/12 masked;
         retained >= 46/48; negatives confident <= 1/150; witness passed.
  REPORTED: extras, the true setting's stage-1 rank, negatives' best scores, abstentions.
Usage: gate90.py HOLDOUT_DIR TRUTH.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r90"), str(ROOT / "r90" / "blind")]
import f26c as F  # noqa: E402
import f26c_solve as FS  # noqa: E402

CUT_LM, CUT_WORD, REC = -1.30, -2.50, 95
BARS = {"ok": 42, "exact": 36, "stratum": 9, "genre": 12, "masked": 8, "retained": 46, "neg_confident_max": 1}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def conf(b):
    return b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD


def st_tuple(s):
    o = s["outer"]
    return (s["alphabet"], s["b"], s["u"], s["v"], None if o is None else (o["key"], o["sign"], o["phase"]))


def judge(truth, res):
    rows = {"POS": [], "EXTRA": [], "NEG": []}
    for rid, t in truth.items():
        r0 = res[rid]
        b = r0["best"]
        r = {"id": rid, "arm_found": b["arm"], "lm": round(b["lm_per_letter"], 4), "word": round(b["word_per_letter"], 4),
             "confident": conf(b)}
        if t["class"] in ("POS", "EXTRA"):
            true = st_tuple(t["setting"])
            right = sum(x == y for x, y in zip(b["text"], t["enciphered"]))
            key = b["arm"] == "F26C" and F.same_key(st_tuple(b["setting"]), true)
            tag = FS.tag(true)
            r.update(genre=t["genre"], letters=right, key_right=key,
                     stage1_rank=r0["retained"].index(tag) + 1 if tag in r0["retained"] else None)
            r["retained"] = r["stage1_rank"] is not None
            r["ok"] = key and right >= REC and r["confident"]
            r["exact"] = r["ok"] and right == 97
            if t["class"] == "POS":
                r.update(stratum=t["stratum"], param=t["param"], masked=t["masked"])
            else:
                r.update(kind=t["kind"])
        else:
            r.update(generator=t["generator"])
        rows[t["class"]].append(r)
    pos, neg = rows["POS"], rows["NEG"]
    cnt = lambda key, val: [sum(r["ok"] for r in pos if r[key] == val), sum(r[key] == val for r in pos)]  # noqa: E731
    s = {"ok": sum(r["ok"] for r in pos), "positives": len(pos), "exact": sum(r["exact"] for r in pos),
         "key_right": sum(r["key_right"] for r in pos), "retained": sum(r["retained"] for r in pos),
         "stage1_rank_max": max((r["stage1_rank"] for r in pos if r["retained"]), default=None),
         "by_stratum": {k: cnt("stratum", k) for k in ("S1", "S2", "S3", "S4")},
         "by_genre": {k: cnt("genre", k) for k in ("G1", "G2", "G3")},
         "masked": cnt("masked", True), "unmasked": cnt("masked", False),
         "recovered_min_lm": min((r["lm"] for r in pos if r["ok"]), default=None),
         "extras": [{k: r[k] for k in ("id", "kind", "letters", "ok", "key_right", "retained")} for r in rows["EXTRA"]],
         "negatives_confident": sum(r["confident"] for r in neg), "negatives": len(neg),
         "negatives_max_lm": max(r["lm"] for r in neg), "negatives_max_word": max(r["word"] for r in neg),
         "negatives_by_generator_max_lm": {g: max(r["lm"] for r in neg if r["generator"] == g)
                                           for g in sorted({r["generator"] for r in neg})}}
    s["go"] = (s["ok"] >= BARS["ok"] and s["exact"] >= BARS["exact"] and
               all(v[0] >= BARS["stratum"] for v in s["by_stratum"].values()) and
               all(v[0] >= BARS["genre"] for v in s["by_genre"].values()) and s["masked"][0] >= BARS["masked"] and
               s["retained"] >= BARS["retained"] and s["negatives_confident"] <= BARS["neg_confident_max"])
    return s, rows


def main():
    hold, truth_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    want = (hold / "TRUTH_SHA256").read_text().split()[0]
    assert sha(truth_path) == want, "truth file differs from the one committed before the run"
    listed = {l.split()[-1]: l.split()[0] for l in (hold / "GATE_FROZEN.sha256").read_text().splitlines() if l.strip()}
    for p in (hold / "BLIND.tsv", hold / "run/RESULTS.jsonl", hold / "run/WITNESS.json"):
        rel = str(p.resolve().relative_to(ROOT))
        assert listed.get(rel) == sha(p), f"{rel} is not frozen"
    w = json.loads((hold / "run/WITNESS.json").read_text())
    assert w["passed"], "independent witness check did not pass: no gate verdict"
    truth = json.loads(truth_path.read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (hold / "run/RESULTS.jsonl").read_text().splitlines() if l}
    cts = dict(l.split("\t") for l in (hold / "BLIND.tsv").read_text().splitlines()[1:] if l)
    assert set(truth) == set(res) == set(cts) and all(truth[i]["ct"] == cts[i] for i in cts)
    s, rows = judge(truth, res)
    rep = {"verdict": "GO" if s["go"] else "NO-GO", "bars": BARS, "cut_lm": CUT_LM, "cut_word": CUT_WORD,
           "recovered_letters": REC, "summary": s, "witnesses": w["witnesses"], "rows": rows}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: s[k] for k in ("ok", "exact", "key_right", "retained", "by_stratum", "by_genre",
                                                        "masked", "negatives_confident", "negatives_max_lm")}))


if __name__ == "__main__":
    main()

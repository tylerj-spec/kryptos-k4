#!/usr/bin/env python3
"""R89 SEALED gate evaluation: the only step that opens the holdout truth. Run ONLY after the blind holdout outputs,
their independent witness check (WITNESS.json, passed) and GATE_FROZEN.sha256 are committed and PUSHED, and only with
the truth file whose sha256 was committed before the run (TRUTH_SHA256). Rules fixed in r89/PREREGISTRATION.md G1
(the bars of ChatGPT's design, PR #98 docs/R89_EXECUTABLE_BOUNDS_V2.md, adopted unchanged where they apply):
  For a positive of arm X, "ok" = the joint best decode (letter-model maximum over every arm and setting) is from
  arm X, has >= 95/97 letters equal to the enciphered text, and is confident (letter model >= -1.30 AND word model
  >= -2.50 per letter). "exact" = ok with 97/97.
  Arm X is GO iff  ok >= 42/48;  exact >= 36/48;  ok >= 9/12 in every parameter stratum;  ok >= 12/16 in every genre;
  ok >= 8/12 on the masked subset;  AND the shared negatives are confident in <= 1 of 150 (any arm);  AND the
  witness check passed. Each arm is judged separately; an arm that fails is retired from the K4 run.
  REPORTED, not gated: the extras (plaintext-letter, ciphertext-letter and missed-update errors), setting recovered,
  each generator's best negative score, abstentions.
Usage: gate89.py HOLDOUT_DIR TRUTH.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r89"))
import f26l as F  # noqa: E402

CUT_LM, CUT_WORD, REC = -1.30, -2.50, 95
BARS = {"ok": 42, "exact": 36, "stratum": 9, "genre": 12, "masked": 8, "neg_confident_max": 1}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def conf(b):
    return b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD


def setting_right(arm, found, true):
    if found["arm"] != arm:
        return False
    s = found["setting"]
    if arm == "F26L":
        return (F.canonical(F.F26_ALPHABETS[s["alphabet"]]) == F.canonical(F.F26_ALPHABETS[true["alphabet"]]) and
                all(s[k] == true[k] for k in ("b", "u", "v", "outer")))
    return all(s[k] == true[k] for k in ("ein", "eout", "d", "m", "q"))


def judge(truth, res):
    rows = {"POS": [], "EXTRA": [], "NEG": []}
    for rid, t in truth.items():
        b = res[rid]["best"]
        r = {"id": rid, "arm_found": b["arm"], "lm": round(b["lm_per_letter"], 4), "word": round(b["word_per_letter"], 4),
             "confident": conf(b)}
        if t["class"] in ("POS", "EXTRA"):
            right = sum(x == y for x, y in zip(b["text"], t["enciphered"]))
            r.update(arm=t["arm"], genre=t["genre"], letters=right, setting_right=setting_right(t["arm"], b, t["setting"]))
            r["ok"] = b["arm"] == t["arm"] and right >= REC and r["confident"]
            r["exact"] = r["ok"] and right == 97
            if t["class"] == "POS":
                r.update(stratum=t["stratum"], param=t["param"], masked=t["masked"])
            else:
                r.update(kind=t["kind"])
        else:
            r.update(generator=t["generator"])
        rows[t["class"]].append(r)
    neg = rows["NEG"]
    neg_conf = sum(r["confident"] for r in neg)
    arms = {}
    for arm in ("F26L", "RCT"):
        pos = [r for r in rows["POS"] if r["arm"] == arm]
        cnt = lambda key, val: [sum(r["ok"] for r in pos if r[key] == val), sum(r[key] == val for r in pos)]  # noqa: E731
        s = {"ok": sum(r["ok"] for r in pos), "positives": len(pos), "exact": sum(r["exact"] for r in pos),
             "setting_right": sum(r["setting_right"] for r in pos),
             "arm_right": sum(r["arm_found"] == arm for r in pos),
             "by_stratum": {k: cnt("stratum", k) for k in ("S1", "S2", "S3", "S4")},
             "by_genre": {k: cnt("genre", k) for k in ("G1", "G2", "G3")},
             "masked": cnt("masked", True), "unmasked": cnt("masked", False),
             "recovered_min_lm": min((r["lm"] for r in pos if r["ok"]), default=None),
             "extras": [{k: r[k] for k in ("id", "kind", "letters", "ok", "arm_found")} for r in rows["EXTRA"]
                        if r["arm"] == arm]}
        s["go"] = (s["ok"] >= BARS["ok"] and s["exact"] >= BARS["exact"] and
                   all(v[0] >= BARS["stratum"] for v in s["by_stratum"].values()) and
                   all(v[0] >= BARS["genre"] for v in s["by_genre"].values()) and
                   s["masked"][0] >= BARS["masked"] and neg_conf <= BARS["neg_confident_max"])
        arms[arm] = s
    summ = {"arms": arms, "negatives_confident": neg_conf, "negatives": len(neg),
            "negatives_max_lm": max(r["lm"] for r in neg), "negatives_max_word": max(r["word"] for r in neg),
            "negatives_by_generator_max_lm": {g: max(r["lm"] for r in neg if r["generator"] == g)
                                              for g in sorted({r["generator"] for r in neg})},
            "negatives_family_declared": {a: sum(r["confident"] and r["arm_found"] == a for r in neg)
                                          for a in ("F26L", "F26", "RCT")}}
    return summ, rows


def main():
    hold, truth_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    want = (hold / "TRUTH_SHA256").read_text().split()[0]
    assert sha(truth_path) == want, "truth file differs from the one committed before the run"
    listed = {}
    for line in (hold / "GATE_FROZEN.sha256").read_text().splitlines():
        if line.strip():
            listed[line.split()[-1]] = line.split()[0]
    for p in (hold / "BLIND.tsv", hold / "run/RESULTS.jsonl", hold / "run/WITNESS.json"):
        rel = str(p.resolve().relative_to(ROOT))
        assert listed.get(rel) == sha(p), f"{rel} is not frozen"
    w = json.loads((hold / "run/WITNESS.json").read_text())
    assert w["passed"], "independent witness check did not pass: no gate verdict"
    truth = json.loads(truth_path.read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (hold / "run/RESULTS.jsonl").read_text().splitlines() if l}
    cts = dict(l.split("\t") for l in (hold / "BLIND.tsv").read_text().splitlines()[1:] if l)
    assert set(truth) == set(res) == set(cts) and all(truth[i]["ct"] == cts[i] for i in cts)
    summ, rows = judge(truth, res)
    verdict = {a: "GO" if s["go"] else "NO-GO" for a, s in summ["arms"].items()}
    rep = {"verdict": verdict, "bars": BARS, "cut_lm": CUT_LM, "cut_word": CUT_WORD, "recovered_letters": REC,
           "summary": summ, "witnesses": w["witnesses"], "rows": rows}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(verdict), json.dumps({a: {k: s[k] for k in ("ok", "exact", "by_stratum", "by_genre", "masked")}
                                           for a, s in summ["arms"].items()}), "negatives confident", summ["negatives_confident"])


if __name__ == "__main__":
    main()

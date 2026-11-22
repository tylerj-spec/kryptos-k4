#!/usr/bin/env python3
"""R92 SEALED gate evaluation: the only step that opens the holdout truth. Run ONLY after the blind holdout outputs,
their independent witness check (WITNESS.json, passed) and GATE_FROZEN.sha256 are committed and PUSHED, and only with
the truth file whose sha256 was committed before the run (TRUTH_SHA256).
Rules fixed in r92/PREREGISTRATION.md (G1):
  recovered     best decode (letter-model maximum over all 192 settings) has >= 95 of 97 letters equal to the text
                that was enciphered;  confident: letter model >= -1.30 and word model >= -2.50 per letter.
  GO iff  (a) positives recovered AND confident >= 42 of 48;  (b) exact >= 36;  (c) >= 6 of 8 in every clock cell;
          (d) >= 13 of 16 in every genre;  (e) >= 8 of 12 masked;  (f) wrong-family negatives confident <= 1 of 150;
          (g) the witness check passed.
  REPORTED, not gated: the extras, the setting recovered (contact pair, n, r, d), the wiring agreeing on every contact
  the message used, each generator's best negative score.
Usage: gate92.py HOLDOUT_DIR TRUTH.json OUT.json   (HOLDOUT_DIR holds BLIND.tsv, TRUTH_SHA256, GATE_FROZEN.sha256,
       run/RESULTS.jsonl, run/WITNESS.json)"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r92"))
CUT_LM, CUT_WORD, REC = -1.30, -2.50, 95
BAR_ALL, BAR_EXACT, BAR_CELL, BAR_GENRE, BAR_MASKED, BAR_NEG = 42, 36, 6, 13, 8, 1


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def used_contacts_agree(found, true, text):
    """The found wiring equals the true wiring on every input contact the (true) message used."""
    import rotor92 as RP
    if any(found[k] != true[k] for k in ("ein", "eout", "n", "r", "d")):
        return False
    s = RP.offsets(len(text), true["n"], true["r"], true["d"])
    used = {(RP.IDX[true["ein"]][p] + si) % 26 for p, si in zip(text, s)}
    return all(found["wiring"][x] == true["wiring"][x] for x in used)


def judge(truth, res):
    rows = {"POS": [], "EXTRA": [], "NEG": []}
    for rid, t in truth.items():
        b = res[rid]["best"]
        conf = b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD
        r = {"id": rid, "lm": round(b["lm_per_letter"], 4), "word": round(b["word_per_letter"], 4), "confident": conf}
        if t["class"] in ("POS", "EXTRA"):
            right = sum(a == c for a, c in zip(b["text"], t["enciphered"]))
            st, ts = b["setting"], t["setting"]
            r.update(genre=t["genre"], letters=right, recovered=right >= REC, exact=right == 97,
                     setting_right=all(st[k] == ts[k] for k in ("ein", "eout", "n", "r", "d")),
                     key_on_used_contacts=used_contacts_agree(st, ts, t["enciphered"]), ok=right >= REC and conf)
            r["exact"] = r["ok"] and right == 97
            if t["class"] == "POS":
                r.update(cell=t["cell"], masked=t["masked"])
            else:
                r.update(kind=t["kind"])
        else:
            r.update(generator=t["generator"])
        rows[t["class"]].append(r)
    pos, neg, ex = rows["POS"], rows["NEG"], rows["EXTRA"]
    cnt = lambda key, val: [sum(r["ok"] for r in pos if r[key] == val), sum(r[key] == val for r in pos)]  # noqa: E731
    summ = {
        "positives_ok": sum(r["ok"] for r in pos), "positives": len(pos), "positives_exact": sum(r["exact"] for r in pos),
        "by_cell_ok": {c: cnt("cell", c) for c in sorted({r["cell"] for r in pos})},
        "by_genre_ok": {g: cnt("genre", g) for g in ("G1", "G2", "G3")},
        "masked_ok": cnt("masked", True),
        "setting_right": sum(r["setting_right"] for r in pos), "key_on_used_contacts": sum(r["key_on_used_contacts"] for r in pos),
        "recovered_min_lm": min((r["lm"] for r in pos if r["ok"]), default=None),
        "negatives_confident": sum(r["confident"] for r in neg), "negatives": len(neg),
        "negatives_max_lm": max(r["lm"] for r in neg), "negatives_max_word": max(r["word"] for r in neg),
        "negatives_by_generator_max_lm": {g: max(r["lm"] for r in neg if r["generator"] == g)
                                          for g in sorted({r["generator"] for r in neg})},
        "extras": [{k: r[k] for k in ("id", "kind", "letters", "ok")} for r in ex],
    }
    go = (summ["positives_ok"] >= BAR_ALL and summ["positives_exact"] >= BAR_EXACT and
          all(v[0] >= BAR_CELL for v in summ["by_cell_ok"].values()) and
          all(v[0] >= BAR_GENRE for v in summ["by_genre_ok"].values()) and
          summ["masked_ok"][0] >= BAR_MASKED and summ["negatives_confident"] <= BAR_NEG)
    return go, summ, rows


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
    go, summ, rows = judge(truth, res)
    rep = {"verdict": "GO" if go else "NO-GO", "bars": {"positives_ok": BAR_ALL, "exact": BAR_EXACT, "per_cell_ok": BAR_CELL,
           "per_genre_ok": BAR_GENRE, "masked_ok": BAR_MASKED, "negatives_confident_max": BAR_NEG,
           "recovered_letters": REC, "cut_lm": CUT_LM, "cut_word": CUT_WORD},
           "summary": summ, "witnesses": w["witnesses"], "rows": rows}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps(summ))


if __name__ == "__main__":
    main()

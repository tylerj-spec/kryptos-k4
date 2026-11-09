#!/usr/bin/env python3
"""R74 verify + gate (after the blind results are frozen and pushed). Rules fixed in r74/PREREGISTRATION.md.
Verify (no truth): every stored decode (5 per ciphertext, every line of each full scan, every packet entry)
re-encrypts to its ciphertext by the explicit three-stage encryption under its stored setting, and each RESULTS
best is its top decode.
Gate (truth opened only after verify passes):
  recovered  = best decode is the exact enciphered plaintext AND its transform is the true one;
  confident  = best decode's letter model >= CUT_LM per letter AND its word model >= CUT_WORD per letter;
  PASS       = >= 108/120 positives recovered AND confident, AND 0/300 negatives confident, AND verify passed.
Also reports clean and misspelled positives separately and one-sided 95% exact binomial bounds.
Usage: gate.py BLIND.tsv RUN_DIR SEALED_TRUTH.json REPORT.json     (verify only: gate.py --verify TSV RUN_DIR OUT.json)"""
import gzip
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r74"))
import sandwich as S  # noqa: E402

CUT_LM = -1.45     # fixed in r74/PREREGISTRATION.md (development rule; r74/results/DEV_CUT.json)
CUT_WORD = -2.5    # fixed in r74/PREREGISTRATION.md (development rule; r74/results/DEV_CUT.json)
ROUTES = S.load_routes()


def enc(text, st):
    return S.encrypt(text, st["ka"], st["kb"], st["a"], st["b"], st["op_a"], st["op_b"], ROUTES[st["route"]])


def key(st):
    return S.transform(st["ka"], st["kb"], st["a"], st["b"], st["op_a"], st["op_b"], ROUTES[st["route"]])


def verify(tsv, run):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    problems, n = [], 0
    for rid, ct in cts.items():
        r = res[rid]
        if r["best"] != r["top"][0]:
            problems.append(f"best not top {rid}")
        for e in r["top"]:
            n += 1
            if enc(e["text"], e["setting"]) != ct:
                problems.append(f"witness {rid} {e['t']}")
        fp = Path(run) / "full" / f"{rid}.tsv.gz"
        if fp.exists():
            lines = gzip.decompress(fp.read_bytes()).decode().splitlines()
            if len(lines) != 15680:
                problems.append(f"full scan length {rid}")
            for line in lines:
                k, route, ka, kb, a, b, op_a, op_b, _, text = line.split("\t")
                n += 1
                st = {"route": route, "ka": ka, "kb": kb, "a": int(a), "b": int(b), "op_a": op_a, "op_b": op_b}
                if enc(text, st) != ct:
                    problems.append(f"full witness {rid} {k}")
            for e in json.loads((Path(run) / "packet" / f"{rid}.json").read_text()):
                n += 1
                if enc(e["text"], e["setting"]) != ct:
                    problems.append(f"packet witness {rid} {e['t']}")
    return {"witnesses": n, "problems": problems[:50], "passed": not problems}


def lower95(k, n):
    """One-sided 95% lower bound (exact binomial) for a proportion k/n."""
    if k == 0:
        return 0.0
    tail = lambda p: sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)  # noqa: E731
                                  + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(k, n + 1))
    lo, hi = 0.0, k / n
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail(mid) < 0.05 else (lo, mid)
    return lo


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
            rec = b["text"] == t["pt"] and key(b["setting"]) == key(t["setting"])
            row.update({"recovered": rec, "ok": rec and conf, "true_setting": t["setting"], "found_setting": b["setting"],
                        "letters_right": sum(x == y for x, y in zip(b["text"], t["pt"]))})
        rows.append(row)
    pos = [x for x in rows if x["kind"].startswith("POS")]
    neg = [x for x in rows if x["kind"].startswith("NEG_")]
    ok = sum(x["ok"] for x in pos)
    by_kind = {}
    for x in neg:
        k = by_kind.setdefault(x["kind"], {"lm_max": -1e9, "word_max": -1e9})
        k["lm_max"], k["word_max"] = max(k["lm_max"], x["lm_per_letter"]), max(k["word_max"], x["word_per_letter"])
    summ = {"positives": {"n": len(pos), "recovered_and_confident": ok, "recovered": sum(x["recovered"] for x in pos),
                          "confident": sum(x["confident"] for x in pos),
                          "clean_ok": sum(x["ok"] for x in pos if x["kind"] == "POS"),
                          "clean_n": sum(x["kind"] == "POS" for x in pos),
                          "misspelled_ok": sum(x["ok"] for x in pos if x["kind"] == "POS_MISSPELLED"),
                          "misspelled_n": sum(x["kind"] == "POS_MISSPELLED" for x in pos),
                          "lm_min": min(x["lm_per_letter"] for x in pos),
                          "word_min": min(x["word_per_letter"] for x in pos),
                          "power_lower95": lower95(ok, len(pos))},
            "negatives": {"n": len(neg), "confident": sum(x["confident"] for x in neg),
                          "lm_max": max(x["lm_per_letter"] for x in neg),
                          "word_max": max(x["word_per_letter"] for x in neg),
                          "false_confidence_upper95": 1 - 0.05 ** (1 / len(neg)) if not any(x["confident"] for x in neg)
                          else None, "by_kind": by_kind}}
    summ["passed"] = ok >= 108 and summ["negatives"]["confident"] == 0 and ver["passed"]
    Path(rep).write_text(json.dumps({"cut_lm": CUT_LM, "cut_word": CUT_WORD, "verify": ver, "summary": summ,
                                     "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()

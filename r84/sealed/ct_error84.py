#!/usr/bin/env python3
"""R84 robustness diagnostic (FUTURE_TEST_GUARDRAILS G2: corruption of one CIPHERTEXT symbol). Synthetic only: uses
R80a's SPENT holdout positives (truth already opened in r80a/holdout/GATE.json); no K4 data, no published letters.
Reported, not gated (r84/PREREGISTRATION.md): it says whether one carving or transcription error in K4 would stop
this solver from finding a true solution.
  make TSV TRUTH   12 positives recovered at the gate (3 per family, seed 840500), one ciphertext letter changed at a
                   random position to a different letter
  score RESULTS TRUTH OUT   letters right against the true plaintext; recovered = >= 95/97 right AND confident
                   (letter model >= -1.30, word model >= -2.50; R80a's cuts)
Usage: ct_error84.py make TSV TRUTH | ct_error84.py score RESULTS.jsonl TRUTH OUT.json"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SEED, PER_FAM = 840500, 3


def make(tsv, truth):
    gate = json.loads((ROOT / "r80a/holdout/GATE.json").read_text())["rows"]
    sealed = json.loads((ROOT / "r80a/holdout/sealed_truth.json").read_text())
    rng = random.Random(SEED)
    rows, tr = ["id\tciphertext"], {}
    for fam in ("L1", "L2", "X1", "X2"):
        ok = sorted(r["id"] for r in gate if r["ok"] and r["fam"] == fam and r["kind"] != "STRETCH")
        for src in rng.sample(ok, PER_FAM):
            ct = sealed[src]["ct"]
            i = rng.randrange(97)
            c2 = ct[:i] + rng.choice([x for x in AZ if x != ct[i]]) + ct[i + 1:]
            rid = f"CE_{len(tr):02d}"
            rows.append(f"{rid}\t{c2}")
            tr[rid] = {"source": src, "fam": fam, "kind": sealed[src]["kind"], "position": i, "pt": sealed[src]["pt"]}
    Path(tsv).write_text("\n".join(rows) + "\n")
    Path(truth).write_text(json.dumps(tr, indent=1) + "\n")
    print("wrote", len(tr), "items")


def score(results, truth, out):
    tr = json.loads(Path(truth).read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in Path(results).read_text().splitlines() if l}
    rows = []
    for rid, t in tr.items():
        b = res[rid]["best"]
        right = sum(x == y for x, y in zip(b["text"], t["pt"]))
        conf = b["lm_per_letter"] >= -1.30 and b["word_per_letter"] >= -2.50
        rows.append({"id": rid, **{k: t[k] for k in ("source", "fam", "kind", "position")}, "letters_right": right,
                     "lm": b["lm_per_letter"], "word": b["word_per_letter"], "confident": conf,
                     "recovered": conf and right >= 95})
    rep = {"recovered": sum(r["recovered"] for r in rows), "n": len(rows), "rows": rows}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print("recovered", rep["recovered"], "of", rep["n"], [r["letters_right"] for r in rows])


if __name__ == "__main__":
    if sys.argv[1] == "make":
        make(sys.argv[2], sys.argv[3])
    else:
        score(sys.argv[2], sys.argv[3], sys.argv[4])

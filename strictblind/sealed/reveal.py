#!/usr/bin/env python3
"""strictblind SEALED reveal: python3 -I sealed/reveal.py EXPERIMENT_DIR   (only after FROZEN.sha256 exists)
Checks the freeze; re-encrypts every frozen top-100 row forward to its run's ciphertext with the independent
encryptor; ranks each plant's truth; counts K4 clue matches (0-24). Writes EXPERIMENT_DIR/REVEAL.json."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ALPHABETS, CLUES, K4, check_frozen, encrypt, letters, make_key, read_routes  # noqa: E402

exp = Path(sys.argv[1]).resolve()
check_frozen(exp)
man = json.loads((exp / "manifest.json").read_text())
tf = exp / "sealed" / "truth.json"
truth = json.loads(tf.read_text()) if tf.exists() else {}
report = []
for run in man["runs"]:
    ct = letters(exp / run["ct"])
    R = read_routes(exp / run["routes"])
    kind, arg = run["key"]
    karg = str(exp / arg) if kind == "TEXT" else str(arg)
    rows = list(csv.DictReader(open(exp / "out" / f"{run['tag']}.tsv"), delimiter="\t"))
    for r in rows:
        _, name, order, spec, pa, ca, op = r["setting"].split("|")
        enc = encrypt(r["plaintext"], R[name, order], order, make_key(kind, karg, spec),
                      ALPHABETS[pa[3:]], ALPHABETS[ca[3:]], op[3:])
        assert enc == ct, (run["tag"], r["rank"])
    entry = {"tag": run["tag"], "rows": len(rows), "forward_check": "every row re-encrypts to its ciphertext",
             "top_score": float(rows[0]["score"]), "top_plaintext": rows[0]["plaintext"]}
    if ct == K4:
        m = [sum(r["plaintext"][i] == c for i, c in CLUES.items()) for r in rows]
        entry.update({"kind": "K4", "clue_matches_max": max(m), "rows_with_all_24": sum(x == 24 for x in m),
                      "clue_matches_top10": m[:10]})
    elif run["tag"] in truth:
        t = truth[run["tag"]]
        rank = next((int(r["rank"]) for r in rows if r["plaintext"] == t["plaintext"]), None)
        entry.update({"kind": "PLANT", "truth_rank": rank, "planted_setting": {k: t[k] for k in ("route", "order", "key", "PA", "CA", "OP")}})
    else:
        entry.update({"kind": "NULL", "description": "non-K4 ciphertext with no planted truth"})
    report.append(entry)
(exp / "REVEAL.json").write_text(json.dumps(report, indent=1) + "\n")
for e in report:
    tail = (f"truth rank {e['truth_rank']}" if e["kind"] == "PLANT" else
            f"clue matches max {e['clue_matches_max']}/24, rows with all 24: {e['rows_with_all_24']}" if e["kind"] == "K4"
            else "null control")
    print(f"{e['tag']:24s} top {e['top_score']:9.2f}  {tail}")

#!/usr/bin/env python3
"""R68 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen, pushed and verified. Holds the published
letters (EASTNORTHEAST at 0-based 21-33, BERLINCLOCK at 63-73), compared with each frozen decode in PLAINTEXT order
(for M1 that is path order, the R61/R64 convention; for M2 it is carved order, Sanborn's literal letter-for-letter
statement). Also reports, for M1, the literal carved-position reading as a secondary check (P[perm[j]] vs the letter
published for carved position j).
Primary, per family f: SIGNAL(f) = K4's family-f best total above all 100 nulls' AND that decode matches >= 10/24.
Contenders: ANY frozen K4 decode (each row's best per family and convention) matching >= 12/24 is listed raw, with the
number of null ciphertexts that have any decode reaching the same count.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import paths as all_paths, sha, witness_ok  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))
POS = [(o + i, c) for o, t in CLUES for i, c in enumerate(t)]
FAMS = ("PER", "GRO", "CTAK", "PTAK")


def hits(pt):
    return sum(pt[i] == c for i, c in POS)


def literal_hits(pt, perm):
    return sum(pt[perm[j]] == c for j, c in POS)


def decodes(work, rid, names):
    for line in (work / f"{rid}.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            _, pi, model = r["id"].rsplit("__", 2)
            for b in r["by_family_convention"]:
                yield {"row": r["id"], "path": names[int(pi)], "model": model, **b}


def main():
    tsv, fz, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            assert sha(tsv if lab == "input" else fz / "RESULTS.jsonl") == h, f"freeze mismatch {lab}"
    P = all_paths()
    names = list(P)
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (fz / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    for i, r in rows.items():
        for b in r["families"].values():
            assert witness_ok(cts[i], b["path"], b["model"], b["family"], b["convention"], b["param"], b["key"],
                              b["plaintext"]), f"witness {i}"
    null_ids = [i for i in rows if i != "K4"]
    out = {"families": {}}
    for f in FAMS:
        k4 = rows["K4"]["families"][f]
        ge = sum(rows[i]["families"][f]["total"] >= k4["total"] for i in null_ids)
        h = hits(k4["plaintext"])
        out["families"][f] = {"k4_best": k4, "k4_total": k4["total"], "nulls_at_or_above": ge,
                              "empirical_rank_p": (ge + 1) / (len(null_ids) + 1), "k4_hits": h,
                              "null_hits_sorted": sorted(hits(rows[i]["families"][f]["plaintext"]) for i in null_ids),
                              "outcome": "SIGNAL" if ge == 0 and h >= 10 else "SCORE_ANOMALY" if ge == 0 else "NO_SIGNAL"}
    # contender screen over every frozen decode
    def max_hits(rid):
        best = (0, None)
        for d in decodes(fz / "work", rid, names):
            hh = hits(d["plaintext"])
            if d["model"] == "M1" and d["path"] != "ID":
                hh = max(hh, literal_hits(d["plaintext"], P[d["path"]]))
            if hh > best[0]:
                best = (hh, d)
        return best
    k4max, k4dec = max_hits("K4")
    null_max = sorted(max_hits(i)[0] for i in null_ids)
    contenders = [d for d in decodes(fz / "work", "K4", names)
                  if max(hits(d["plaintext"]), literal_hits(d["plaintext"], P[d["path"]]) if d["model"] == "M1" and d["path"] != "ID" else 0) >= 12]
    out["contender_screen"] = {"k4_max_hits_any_decode": k4max, "k4_best_hit_decode": k4dec,
                               "null_max_hits_any_decode_sorted": null_max,
                               "nulls_reaching_k4_max": sum(v >= k4max for v in null_max),
                               "contenders_ge_12": contenders}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    for f, d in out["families"].items():
        print(f, d["outcome"], {k: d[k] for k in ("k4_total", "nulls_at_or_above", "empirical_rank_p", "k4_hits")},
              d["k4_best"]["path"], d["k4_best"]["model"], d["k4_best"]["convention"], d["k4_best"]["param"])
    print("contender screen: K4 max hits over all frozen decodes", k4max, "| nulls median/max",
          null_max[len(null_max) // 2], null_max[-1], "| nulls reaching K4's max", out["contender_screen"]["nulls_reaching_k4_max"],
          "| contenders >= 12:", len(contenders))
    for d in contenders:
        print("  CONTENDER", d["path"], d["model"], d["family"], d["convention"], d["param"], d["key"], d["plaintext"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""R81a CI reproduction of the frozen validator counts (added after review of PR #76; changes no frozen result).
Recomputes, for K4 and the same 10 shuffles as r81a/sealed/validate81.py, every family's setting count, exact count and
drop-one count with validate81.check_family, and compares them with the committed r81a/k4/VALIDATE.json. It needs no
letter model: with no flagged setting there is nothing to replay. Exit status 1 on any difference.
Usage: repro_validate81.py TARGET.tsv VALIDATE.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate81 as V  # noqa: E402


def main():
    tsv, committed = sys.argv[1], sys.argv[2]
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    ids = ["K4"] + [i for i in cts if i != "K4"][:10]
    want = json.loads(Path(committed).read_text())
    bad = []
    if want["k4_flagged"]:
        bad.append("committed file has flagged K4 settings; this script only reproduces the counts")
    for rid in ids:
        for tag, mod, fams in V.FAMSETS:
            for fam in fams:
                n, ex, drop, _ = V.check_family(mod, fam, cts[rid], False)
                got = {"settings": n, "exact_feasible": ex, "drop_one_feasible": int(drop.sum())}
                ref = {k: want["rows"][rid][f"{tag}:{fam}"][k] for k in got}
                if got != ref:
                    bad.append((rid, f"{tag}:{fam}", got, ref))
        print(rid, "ok" if not any(b[0] == rid for b in bad if isinstance(b, tuple)) else "MISMATCH", flush=True)
    if bad:
        print("DIFFERENCES:", bad)
        raise SystemExit(1)
    print("validator counts reproduced for", len(ids), "ciphertexts")


if __name__ == "__main__":
    main()

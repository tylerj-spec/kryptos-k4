#!/usr/bin/env python3
"""R98 post-freeze cross-check: a second, separately written implementation of the exact criterion, standard
library only (tuples and Counters; no numpy, no base-26 codes). Reads the FROZEN inputs and re-derives EXACT and
DROP for the first N inputs (K4 first). Counts only.
Usage: python3 -I r98/crosscheck98.py N OUT.json"""
import ast
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r76")]
import alphabets as AL  # noqa: E402

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TIER_SHA = "563ae44ae9a47539e0e01cabc1415e42619bdf3e906ff1f47b11f2d0bede2233"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"


def frozen_ok():
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def clues():
    path = ROOT / "r73/sealed/reveal_k4.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CLUE_SHA
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "CLUES" for t in node.targets):
            return {s + k: c for s, txt in ast.literal_eval(node.value) for k, c in enumerate(txt)}
    raise SystemExit("no CLUES")


def count_conv(ct, obs, pos, t, r, o, a):
    """EXACT and DROP for one convention over the whole tier, by explicit tuple matching."""
    starts = [i for i in sorted(obs) if i % 2 == a and i + 1 in obs]
    quads = []
    for i in starts:
        u, w = (obs[i], obs[i + 1]) if r == 0 else (obs[i + 1], obs[i])
        cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
        quads.append((u, w, cu, cl))
    m = len(quads)
    Fs = [tuple((p[q[2]] - p[q[0]]) % 26 for q in quads) for p in pos]
    Gs = []
    for p in pos:
        h = [(p[q[3]] - p[q[1]]) % 26 for q in quads]
        Gs.append(tuple((-x) % 26 for x in h) if t == "VIG" else tuple(h))

    def matches(f):
        """Every G tuple a PA row with F tuple f accepts: F = G != 0, or F = 1 and G = 25."""
        opts = []
        for x in f:
            if x == 0:
                return []
            opts.append((1, 25) if x == 1 else (x,))
        return itertools.product(*opts)

    def total(drop_j):
        keep = [j for j in range(m) if j != drop_j]
        gc = Counter(tuple(g[j] for j in keep) for g in Gs)
        n = 0
        for f in Fs:
            for g in matches(tuple(f[j] for j in keep)):
                n += gc.get(g, 0)
        return n

    return total(None), sum(total(j) for j in range(m))


def main():
    n_inputs, out = int(sys.argv[1]), Path(sys.argv[2])
    frozen_ok()
    tier = [a for _, a in AL.large_tier()]
    assert hashlib.sha256("\n".join(tier).encode()).hexdigest() == TIER_SHA
    pos = [{c: k for k, c in enumerate(a)} for a in tier]
    obs = clues()
    rows = [line.split("\t") for line in (HERE / "k4/INPUTS.tsv").read_text().splitlines()[1:]]
    res = []
    for name, ct in rows[:n_inputs]:
        e = d = conv_any = 0
        for t in ("VIG", "BEAU"):
            for r in (0, 1):
                for o in (0, 1):
                    for a in (0, 1):
                        ce, cd = count_conv(ct, obs, pos, t, r, o, a)
                        e, d, conv_any = e + ce, d + cd, conv_any + (ce > 0 or cd > 0)
        res.append({"id": name, "exact_feasible_settings": e, "drop_feasible_setting_pair_omissions": d,
                    "conventions_with_any_feasible": conv_any})
    frozen = {r["id"]: r for r in json.loads((HERE / "k4/AGGREGATES.json").read_text())["inputs"]}
    agree = all(frozen[r["id"]] == r for r in res)
    out.write_text(json.dumps({"implementation": "pure-Python tuple matching (second implementation)",
                               "inputs_checked": len(res), "rows": res, "agree_with_frozen": agree}, indent=1) + "\n")
    print("AGREE" if agree else "DISAGREE", res[0])


if __name__ == "__main__":
    main()

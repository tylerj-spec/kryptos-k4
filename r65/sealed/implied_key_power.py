#!/usr/bin/env python3
"""R65b power check (post hoc; added 4 Nov 2026 after the R67 review). How often would a TRUE German running key pass
R65b's test? Real German key fragments at the published-position spacing (13 letters, then 11 letters starting 42
later: 0-based 21-33 and 63-73) are scored exactly as r65/sealed/implied_key_check.py scores them (order-6 German model,
each fragment from an empty context) and compared with R65b's frozen null 99th percentile and K4's frozen T.
For the true convention the implied key IS the key, so this is the score R65b would see (its T, a maximum over
conventions, can only be higher). Uses no K4 data beyond r65/k4/IMPLIED_KEY_CHECK.json.
Usage: implied_key_power.py GERMAN_LM DE_HOLD_LETTERS DE_LIT_HOLD_LETTERS REPORT.json [N=2000] [SEED=7]"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from implied_key_check import LM, SHA  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    lm_p, ep_p, lit_p, rep = sys.argv[1:5]
    n = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 7
    assert hashlib.sha256(Path(lm_p).read_bytes()).hexdigest() == SHA["DE"], "German model hash mismatch"
    de = LM(lm_p)
    frozen = json.loads((ROOT / "r65/k4/IMPLIED_KEY_CHECK.json").read_text())["H1"]
    bar, k4t = frozen["null_q99"], frozen["T"]
    out = {"r65b_null_q99": bar, "k4_T": k4t, "n": n, "seed": seed, "sources": {}}
    for name, path in (("europarl_file10_modern", ep_p), ("mann_1912_old_spelling", lit_p)):
        s = Path(path).read_text().strip()
        rng = random.Random(seed)
        sc = []
        for _ in range(n):
            o = rng.randrange(len(s) - 60)
            sc.append(de.score(s[o:o + 13]) + de.score(s[o + 42:o + 53]))
        sc.sort()
        out["sources"][name] = {"letters_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                                "median": sc[n // 2], "min": sc[0], "max": sc[-1],
                                "share_at_or_above_1pct_bar": sum(v >= bar for v in sc) / n,
                                "share_at_or_above_k4_T": sum(v >= k4t for v in sc) / n}
        print(name, {k: v for k, v in out["sources"][name].items() if k != "letters_sha256"})
    Path(rep).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()

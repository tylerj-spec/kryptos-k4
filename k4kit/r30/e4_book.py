#!/usr/bin/env python3
"""E4 (PREREGISTRATION_R30.md): whole-book running key, both alphabets free.
    python3 -I k4kit/r30/e4_book.py BOOK.txt [--anchor-phrase CANYOUSEEANYTHING] [--label carter_v1]
Normalisation identical to tools/book_key_test.py (running heads repeated 5+ times dropped, then A-Z only).
Every 97-letter window x {forward, reversed text} x {AZ, KRYPTOS numbering}; 20 letter-shuffled copies as the
pass-count null; every pass screened at 16 restarts (ORTH), the 20 best replicated at 64 with new seeds.
Safe under python3 -I: the book is only read as text, and imports come from this file's own directory."""
import collections
import hashlib
import json
import random
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r30lib import (ANCH, AZ, BAR_ORTH, K4, RUNS, assert_protocol, ensure_models, forced_mask, possible,  # noqa: E402
                    run_solver, seed, solver_line, verify_row)
from k4common import KRY  # noqa: E402

TEXT = ""


def normalise(raw_text):
    raw = raw_text.splitlines()
    heads = collections.Counter(ln.strip() for ln in raw if ln.strip() and ln.strip().upper() == ln.strip()
                                and len(ln.strip()) < 60 and re.search("[A-Z]", ln))
    drop = {h for h, n in heads.items() if n >= 5}
    return re.sub("[^A-Z]", "", "\n".join(ln for ln in raw if ln.strip() not in drop).upper()), len(drop)


def scan(args):
    s, keep, lo, hi = args
    out = []
    for direction, ss in (("fwd", s), ("rev", s[::-1])):
        for numname, alpha in (("AZ", AZ), ("KRY", KRY)):
            v = [alpha.index(c) for c in ss]
            for off in range(lo, min(hi, len(v) - 96)):
                if possible(v[off:off + 97]):
                    out.append((direction, numname, off) if keep else 1)
    return out


def scan_all(pool, s, keep):
    step = 20000
    jobs = [(s, keep, lo, lo + step) for lo in range(0, len(s), step)]
    res = []
    for part in pool.imap_unordered(scan, jobs):
        res += part
    return res


def key_of(text, d, a, off):
    ss = text if d == "fwd" else text[::-1]
    alpha = AZ if a == "AZ" else KRY
    return [alpha.index(c) for c in ss[off:off + 97]]


if __name__ == "__main__":
    sha = assert_protocol()
    ensure_models()
    args = sys.argv[1:]
    book = Path(args[0])
    phrase = args[args.index("--anchor-phrase") + 1] if "--anchor-phrase" in args else None
    label = args[args.index("--label") + 1] if "--label" in args else book.stem
    rawb = book.read_bytes()
    text, ndrop = normalise(rawb.decode("utf-8", errors="replace"))
    t0 = time.time()
    meta = {"protocol": sha, "book": book.name, "raw_sha256": hashlib.sha256(rawb).hexdigest(),
            "letters_sha256": hashlib.sha256(text.encode()).hexdigest(), "letters": len(text),
            "running_heads_dropped": ndrop, "windows": 4 * max(0, len(text) - 96)}
    print(json.dumps(meta, indent=1), flush=True)
    with Pool(4) as pool:
        hits = scan_all(pool, text, True)
        rng = random.Random(2828)
        null = []
        for _ in range(20):
            sh = list(text)
            rng.shuffle(sh)
            null.append(len(scan_all(pool, "".join(sh), False)))
    null.sort()
    meta.update({"passes": len(hits), "null_median": null[10], "null_max": null[-1], "null": null,
                 "null_reaching": sum(x >= len(hits) for x in null)})
    pos = text.find(phrase) if phrase else -1
    meta["anchor_phrase_at"] = pos
    print(f"oracle: {len(hits)} passes; 20 shuffled copies median {null[10]}, max {null[-1]}", flush=True)
    S = []
    for d, a, off in hits:
        lab = f"BOOK|{label}|{d}|{a}|{off}"
        S.append((lab, key_of(text, d, a, off)))
    lines = [solver_line(lab, k, K4, ANCH, seed(f"ORTH|{lab}"), "-") for lab, k in S]
    best, _ = run_solver(lines, f"e4_{label}_screen", 16) if lines else ({}, [])
    keys = dict(S)
    ranked = []
    for lab, k in S:
        r = best[lab]
        assert verify_row(r, k, K4), lab
        fm = forced_mask(k, K4, ANCH)
        ranked.append({"id": lab, "W": r["W"], "plaintext": r["plaintext"], "forced_mask": fm,
                       "forced_beyond_clues": sum(1 for i, c in enumerate(fm) if c != "?" and i not in ANCH)})
    ranked.sort(key=lambda x: -x["W"])
    rep = {}
    top = [x["id"] for x in ranked[:20]]
    if top:
        L = [solver_line(i, keys[i], K4, ANCH, seed(f"ORTH|{i}|rep"), "-") for i in top]
        rb, _ = run_solver(L, f"e4_{label}_rep", 64)
        for i in top:
            assert verify_row(rb[i], keys[i], K4), i
            first = next(x for x in ranked if x["id"] == i)
            rep[i] = {"W": rb[i]["W"], "plaintext": rb[i]["plaintext"],
                      "letters_changed_vs_screen": sum(a != b for a, b in zip(rb[i]["plaintext"], first["plaintext"]))}
    cands = [i for i, d in rep.items() if d["W"] > BAR_ORTH and d["letters_changed_vs_screen"] <= 5]
    meta.update({"best_W": ranked[0]["W"] if ranked else None, "candidates": cands, "seconds": round(time.time() - t0)})
    json.dump({"summary": meta, "ranked": ranked, "replication": rep}, open(RUNS / f"e4_{label}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "null"}, indent=1))
    for x in ranked[:10]:
        print(f"  {x['W']:8.2f} +{x['forced_beyond_clues']:2d} {x['id']:<36} {x['plaintext']}")

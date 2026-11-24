#!/usr/bin/env python3
"""R99 checker-correctness gate (PREREGISTRATION section 4; synthetic only; reads no K4 file and no published
plaintext). Usage: python3 -I r99/validate99.py OUT.json [--dev-seed N]
--dev-seed: development smoke run with another seed; its output is DEVELOPMENT_ONLY and is never the gate."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r76")]
import autokey99 as AK  # noqa: E402
import checker99 as CK  # noqa: E402
import alphabets as AL  # noqa: E402

AZ = AK.AZ
TIER_SHA = "563ae44ae9a47539e0e01cabc1415e42619bdf3e906ff1f47b11f2d0bede2233"
SEED = 990901
SOURCES = ("autokey99.py", "checker99.py", "validate99.py", "run_target99.py", "evaluate99.py")


def windows(rng, lengths):
    """Disjoint random windows inside 0..96 (synthetic positions, not the K4 ones)."""
    while True:
        starts = [rng.randrange(0, 98 - L) for L in lengths]
        pos = set()
        for s, L in zip(starts, lengths):
            pos |= set(range(s, s + L))
        if len(pos) == sum(lengths):
            return sorted(pos)


def rand_text(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def plant(rng, A, L, s1, s2, c):
    pt = rand_text(rng)
    ct = AK.encrypt(pt, A, L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
    return pt, ct


def lags_with(obs, k):
    return [L for L in range(1, 97) if len(CK.links(obs, L)) >= k]


def oracle(ct, obs, sub, lags):
    """Brute force with the reference DECRYPTOR: per (L, signs, A) and every c, propagate each link letter by
    letter; EXACT if some c fails no link, DROP if some c fails only links adjacent to one published position."""
    res = {}
    for L in lags:
        lk = CK.links(obs, L)
        if not lk:
            continue
        cuts = [frozenset(k for k, (i, j, _) in enumerate(lk) if p in (i, j)) for p in obs]
        cuts = [cu for cu in cuts if cu]
        for s1, s2 in AK.SIGNS:
            ex = dr = 0
            for A in sub:
                fails = []
                for c in range(26):
                    f = set()
                    for k, (i, j, t) in enumerate(lk):
                        x = obs[i]
                        for u in range(1, t + 1):
                            x = AK.dec_letter(ct[i + u * L], x, A, s1, s2, c)
                        if x != obs[j]:
                            f.add(k)
                    fails.append(f)
                e = any(not f for f in fails)
                d = e or any(f <= cu for f in fails for cu in cuts)
                ex += e
                dr += d
            res[(L, s1, s2)] = (len(lk), ex, dr)
    return res


def main():
    out = Path(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) == 4 and sys.argv[2] == "--dev-seed" else SEED
    rng = random.Random(seed)
    t0w, t0c = time.time(), time.process_time()
    tier = [a for _, a in AL.large_tier()]
    rep = {"round": "R99", "gate_type": "EXACT_CHECKER_CORRECTNESS", "blind_recovery_certified": False,
           "seed": seed, "development_only": seed != SEED, "tier": len(tier),
           "tier_sha256_ok": hashlib.sha256("\n".join(tier).encode()).hexdigest() == TIER_SHA}

    # V1: round trips
    fails = 0
    for _ in range(400):
        A = rng.choice(tier)
        L = rng.randrange(1, 97)
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        primer = [rng.randrange(26) for _ in range(L)]
        pt = rand_text(rng)
        fails += AK.decrypt(AK.encrypt(pt, A, L, s1, s2, c, primer), A, L, s1, s2, c, primer) != pt
    rep["V1_round_trip"] = {"cases": 400, "failures": fails, "pass": fails == 0}

    # V2: decryptor brute force vs both checker paths on one 120-alphabet sub-tier
    sub = rng.sample([a for a in tier if a != AZ], 119) + [AZ]
    IDXs = CK.tier_idx(sub)
    mf = ms = with_exact = 0
    rows = []
    for k in range(30):
        if k % 2 == 0:
            pos = windows(rng, [13, 11])
            cand = lags_with({p: "A" for p in pos}, 2)
            L = rng.choice(cand)
            s1, s2 = rng.choice(AK.SIGNS)
            pt, ct = plant(rng, rng.choice(sub), L, s1, s2, rng.randrange(26))
            kind = "planted"
        else:
            pos = windows(rng, [[5, 4], [4, 4], [6, 3]][(k // 2) % 3])
            pt, ct = rand_text(rng), rand_text(rng)
            kind = "random"
        obs = {p: pt[p] for p in pos}
        lags = [L_ for L_ in range(1, 97) if CK.links(obs, L_)]
        orc = oracle(ct, obs, sub, lags)
        fast = CK.scan(ct, obs, IDXs, lags, fast=True)
        simple = CK.scan(ct, obs, IDXs, lags, fast=False)
        a = sum(orc[key] != fast[key] for key in orc) + (set(orc) != set(fast))
        b = sum(orc[key] != simple[key] for key in orc) + (set(orc) != set(simple))
        mf += a
        ms += b
        e = sum(v[1] for v in orc.values())
        with_exact += e > 0
        rows.append({"kind": kind, "lags": len(lags), "oracle_exact": e, "oracle_drop": sum(v[2] for v in orc.values()),
                     "mismatches_fast": a, "mismatches_simple": b})
    rep["V2_oracle"] = {"inputs": 30, "sub_tier": len(sub), "mismatches_fast": mf, "mismatches_simple": ms,
                        "inputs_with_exact": with_exact, "rows": rows,
                        "pass": mf == 0 and ms == 0 and with_exact >= 10}

    # V3: full-tier plants (exact, one wrong published letter, one wrong ciphertext letter on a link)
    IDX = CK.tier_idx(tier)
    v3 = {"exact_label_missed": 0, "exact_count_zero": 0, "pt_drop_label_missed": 0, "pt_drop_count_zero": 0,
          "ct_drop_count_zero": 0}
    for _ in range(32):
        pos = windows(rng, [13, 11])
        L = rng.choice(lags_with({p: "A" for p in pos}, 6))
        s1, s2 = rng.choice(AK.SIGNS)
        A = rng.choice(tier)
        pt, ct = plant(rng, A, L, s1, s2, rng.randrange(26))
        obs = {p: pt[p] for p in pos}
        v3["exact_label_missed"] += not CK.label_feasible(ct, obs, A, L, s1, s2)
        v3["exact_count_zero"] += CK.scan_lag(ct, obs, IDX, L, s1, s2)[1] < 1
        lk = CK.links(obs, L)
        p = rng.choice(sorted({q for i, j, _ in lk for q in (i, j)}))
        obs2 = dict(obs)
        obs2[p] = rng.choice([ch for ch in AZ if ch != obs[p]])
        v3["pt_drop_label_missed"] += not CK.label_feasible(ct, obs2, A, L, s1, s2, cut=p)
        v3["pt_drop_count_zero"] += CK.scan_lag(ct, obs2, IDX, L, s1, s2)[2] < 1
        i, j, t = rng.choice(lk)
        q = i + rng.randrange(1, t + 1) * L
        ct2 = ct[:q] + rng.choice([ch for ch in AZ if ch != ct[q]]) + ct[q + 1:]
        v3["ct_drop_count_zero"] += CK.scan_lag(ct2, obs, IDX, L, s1, s2)[2] < 1
    rep["V3_full_tier_plants"] = {"plants": 32, **v3, "pass": not any(v3.values())}

    # V4: separately coded ACA Condi
    v4 = {"label_missed": 0, "count_zero": 0}
    for _ in range(16):
        A = rng.choice(tier)
        pt = rand_text(rng)
        ct = AK.condi_encrypt(pt, A, rng.randrange(1, 27))
        obs = {p: pt[p] for p in windows(rng, [13, 11])}
        v4["label_missed"] += not CK.label_feasible(ct, obs, A, 1, 1, 1)
        v4["count_zero"] += CK.scan_lag(ct, obs, IDX, 1, 1, 1)[1] < 1
    rep["V4_condi"] = {"plants": 16, **v4, "pass": not any(v4.values())}

    # V5: throughput; simple path agreement; planted full scan
    scans = []
    agree = True
    for k in range(3):
        ct = rand_text(rng)
        obs = {p: rng.choice(AZ) for p in windows(rng, [13, 11])}
        w0, c0 = time.time(), time.process_time()
        res = CK.scan(ct, obs, IDX, fast=True)
        scans.append({"wall_s": round(time.time() - w0, 3), "cpu_s": round(time.process_time() - c0, 3),
                      "lag_sign_cells": len(res), "exact": sum(v[1] for v in res.values()),
                      "drop": sum(v[2] for v in res.values())})
        if k == 0:
            pick = rng.sample(sorted({key[0] for key in res}), 3)
            agree = CK.scan(ct, obs, IDX, pick, fast=False) == {key: v for key, v in res.items() if key[0] in pick}
    pos = windows(rng, [13, 11])
    L = rng.choice(lags_with({p: "A" for p in pos}, 6))
    s1, s2 = rng.choice(AK.SIGNS)
    pt, ct = plant(rng, rng.choice(tier), L, s1, s2, rng.randrange(26))
    planted = CK.scan(ct, {p: pt[p] for p in pos}, IDX, fast=True)[(L, s1, s2)][1]
    fw = 2 * max(r["wall_s"] for r in scans) * 201 + 10
    fc = 2 * max(r["cpu_s"] for r in scans) * 201 + 10
    rep["V5_throughput"] = {"scans": scans, "simple_agrees_3_lags": agree, "planted_full_scan_exact": planted,
                            "forecast_wall_s": round(fw, 1), "forecast_cpu_s": round(fc, 1),
                            "limit_wall_s": 0.8 * 1800, "limit_cpu_s": 0.8 * 1200,
                            "pass": agree and planted >= 1 and fw < 0.8 * 1800 and fc < 0.8 * 1200}

    checks = [v["pass"] for key, v in rep.items() if key.startswith("V")]
    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if rep["tier_sha256_ok"] and all(checks) else "NO-GO"
    if seed != SEED:
        rep["gate_verdict"] = "DEVELOPMENT_ONLY_" + rep["gate_verdict"]
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({key: v["pass"] for key, v in rep.items() if key.startswith("V")}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""R100 checker-correctness gate (PREREGISTRATION section 4; synthetic only; reads no K4 file and no published
plaintext). Usage: python3 -I r100/validate100.py OUT.json [--dev-seed N]
--dev-seed: development smoke run with another seed; its output is DEVELOPMENT_ONLY and is never the gate."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):   # before numpy: the CPU cap is aggregate
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r76")]
import autokey100 as AK  # noqa: E402
import checker100 as CK  # noqa: E402
import alphabets as AL  # noqa: E402

AZ = AK.AZ
TIER_SHA = "563ae44ae9a47539e0e01cabc1415e42619bdf3e906ff1f47b11f2d0bede2233"
SEED = 1000901
SOURCES = ("autokey100.py", "checker100.py", "validate100.py", "run_target100.py", "evaluate100.py")
EXACT_MIN, DROP_MIN = 10, 14


def windows(rng, lengths):
    while True:
        starts = [rng.randrange(0, 98 - L) for L in lengths]
        pos = set()
        for s, L in zip(starts, lengths):
            pos |= set(range(s, s + L))
        if len(pos) == sum(lengths):
            return sorted(pos)


def rand_text(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def nlinks(pos, L):
    return len(CK.links({p: "A" for p in pos}, L))


def plant(rng, A, B, F, L, s1, s2):
    pt = rand_text(rng)
    ct = AK.encrypt(pt, A, B, F, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
    return pt, ct


def oracle(ct, obs, sub, lags, drop_lags):
    """Brute force with the reference ENCRYPTOR: for every (A, B, signs, F) and c, which direct links fail."""
    res = {}
    for L in lags:
        lk = CK.links(obs, L)
        cuts = [frozenset(k for k, (i, j) in enumerate(lk) if p in (i, j)) for p in sorted(obs)]
        cuts = [cu for cu in cuts if cu]
        for s1, s2 in AK.SIGNS:
            for F in AK.FEEDBACK:
                ex = dr = 0
                for A in sub:
                    for B in sub:
                        fails = []
                        for c in range(26):
                            fails.append({k for k, (i, j) in enumerate(lk)
                                          if AK.enc_letter(obs[j], obs[i], A, B, F, s1, s2, c) != ct[j]})
                        e = any(not f for f in fails)
                        ex += e
                        if L in drop_lags:
                            dr += e or any(f <= cu for f in fails for cu in cuts)
                res[(L, s1, s2, F)] = (len(lk), ex, dr if L in drop_lags else None)
    return res


def main():
    out = Path(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) == 4 and sys.argv[2] == "--dev-seed" else SEED
    rng = random.Random(seed)
    t0w, t0c = time.time(), time.process_time()
    tier = [a for _, a in AL.large_tier()]
    rep = {"round": "R100", "gate_type": "EXACT_CHECKER_CORRECTNESS", "blind_recovery_certified": False,
           "seed": seed, "development_only": seed != SEED, "tier": len(tier),
           "tier_sha256_ok": hashlib.sha256("\n".join(tier).encode()).hexdigest() == TIER_SHA}

    # V1
    fails = 0
    for _ in range(400):
        A, B = rng.choice(tier), rng.choice(tier)
        F = rng.choice(AK.FEEDBACK)
        L = rng.randrange(1, 97)
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pr = [rng.randrange(26) for _ in range(L)]
        pt = rand_text(rng)
        fails += AK.decrypt(AK.encrypt(pt, A, B, F, L, s1, s2, c, pr), A, B, F, L, s1, s2, c, pr) != pt
    rep["V1_round_trip"] = {"cases": 400, "failures": fails, "pass": fails == 0}

    # V2: encryptor brute force on a 16-alphabet sub-tier
    sub = rng.sample([a for a in tier if a != AZ], 15) + [AZ]
    IT = CK.tier_idxt(sub)
    mf = ms = with_exact = 0
    rows = []
    for k in range(16):
        if k % 2 == 0:
            pos = windows(rng, [13, 11])
            L0 = rng.choice([L for L in range(1, 97) if nlinks(pos, L) >= 4])
            pt, ct = plant(rng, rng.choice(sub), rng.choice(sub), rng.choice(AK.FEEDBACK), L0, *rng.choice(AK.SIGNS))
            kind = "planted"
        else:
            pos = windows(rng, [[5, 4], [6, 4], [7, 3]][(k // 2) % 3])
            pt, ct = rand_text(rng), rand_text(rng)
            L0 = None
            kind = "random"
        obs = {p: pt[p] for p in pos}
        cand = [L for L in range(1, 97) if nlinks(pos, L) >= 2 and L != L0]
        lags = sorted(rng.sample(cand, min(6, len(cand))) + ([L0] if L0 else []))
        dl = [L for L in lags if nlinks(pos, L) >= 6]
        orc = oracle(ct, obs, sub, lags, dl)
        fast = CK.scan(ct, obs, IT, lags, dl)
        simple = CK.scan_simple(ct, obs, IT, lags, dl)
        a = sum(orc[key] != fast.get(key) for key in orc) + (set(orc) != set(fast))
        b = sum(orc[key] != simple.get(key) for key in orc) + (set(orc) != set(simple))
        mf += a
        ms += b
        e = sum(v[1] for v in orc.values())
        with_exact += e > 0
        rows.append({"kind": kind, "lags": lags, "drop_lags": dl, "oracle_exact": e,
                     "oracle_drop": sum(v[2] or 0 for v in orc.values()), "mismatches_fast": a,
                     "mismatches_simple": b})
    rep["V2_oracle"] = {"inputs": 16, "sub_tier": len(sub), "mismatches_fast": mf, "mismatches_simple": ms,
                        "inputs_with_exact": with_exact, "rows": rows,
                        "pass": mf == 0 and ms == 0 and with_exact >= 4}

    # V2b: fast path = simple path on a 300-alphabet sub-tier at registered-size lags
    sub3 = rng.sample(tier, 300)
    IT3 = CK.tier_idxt(sub3)
    mis = 0
    rows = []
    for k in range(8):
        pos = windows(rng, [13, 11])
        lags = [L for L in range(1, 97) if nlinks(pos, L) >= EXACT_MIN]
        dl = [L for L in lags if nlinks(pos, L) >= DROP_MIN]
        if k % 2 == 0:
            L0 = rng.choice(lags)
            pt, ct = plant(rng, rng.choice(sub3), rng.choice(sub3), rng.choice(AK.FEEDBACK), L0, *rng.choice(AK.SIGNS))
        else:
            pt, ct = rand_text(rng), rand_text(rng)
        obs = {p: pt[p] for p in pos}
        f = CK.scan(ct, obs, IT3, lags, dl)
        s = CK.scan_simple(ct, obs, IT3, lags, dl)
        mis += (f != s)
        rows.append({"lags": len(lags), "drop_lags": dl, "exact": sum(v[1] for v in f.values()),
                     "drop": sum(v[2] or 0 for v in f.values()), "agree": f == s})
    rep["V2b_simple_path"] = {"inputs": 8, "sub_tier": 300, "disagreements": mis, "rows": rows, "pass": mis == 0}

    # V3: full-tier plants
    IT = CK.tier_idxt(tier)
    v3 = {"exact_zero": 0, "pt_drop_zero": 0, "ct_drop_zero": 0, "drop_plants": 0}
    for k in range(32):
        while True:
            pos = windows(rng, [13, 11])
            want = [L for L in range(1, 97) if (nlinks(pos, L) >= DROP_MIN if k < 16 else EXACT_MIN <= nlinks(pos, L) < DROP_MIN)]
            if want:
                break
        L = rng.choice(want)
        A, B, F = rng.choice(tier), rng.choice(tier), rng.choice(AK.FEEDBACK)
        s1, s2 = rng.choice(AK.SIGNS)
        pt, ct = plant(rng, A, B, F, L, s1, s2)
        obs = {p: pt[p] for p in pos}
        dl = [L] if k < 16 else []
        v3["exact_zero"] += CK.scan(ct, obs, IT, [L], dl)[(L, s1, s2, F)][1] < 1
        if k < 16:
            v3["drop_plants"] += 1
            lk = CK.links(obs, L)
            i, j = rng.choice(lk)
            p = rng.choice([i, j])
            obs2 = dict(obs)
            obs2[p] = rng.choice([ch for ch in AZ if ch != obs[p]])
            v3["pt_drop_zero"] += CK.scan(ct, obs2, IT, [L], [L])[(L, s1, s2, F)][2] < 1
            ct2 = ct[:j] + rng.choice([ch for ch in AZ if ch != ct[j]]) + ct[j + 1:]
            v3["ct_drop_zero"] += CK.scan(ct2, obs, IT, [L], [L])[(L, s1, s2, F)][2] < 1
    rep["V3_full_tier_plants"] = {"plants": 32, **v3,
                                  "pass": v3["exact_zero"] == 0 and v3["pt_drop_zero"] == 0 and v3["ct_drop_zero"] == 0}

    # V4: named Quagmire autokeys (F = B)
    missed = {}
    for name in ("I", "II", "III", "IV"):
        missed[name] = 0
        for _ in range(4):
            K1, K2 = rng.sample([a for a in tier if a != AZ], 2)
            A, B = {"I": (K1, AZ), "II": (AZ, K1), "III": (K1, K1), "IV": (K1, K2)}[name]
            while True:
                pos = windows(rng, [13, 11])
                want = [L for L in range(1, 97) if nlinks(pos, L) >= EXACT_MIN]
                if want:
                    break
            L = rng.choice(want)
            s1, s2 = rng.choice(AK.SIGNS)
            pt, ct = plant(rng, A, B, "B", L, s1, s2)
            missed[name] += CK.scan(ct, {p: pt[p] for p in pos}, IT, [L])[(L, s1, s2, "B")][1] < 1
    rep["V4_quagmire"] = {"plants_per_type": 4, "missed": missed, "pass": not any(missed.values())}

    # V5: throughput on K4-shaped synthetic inputs (two windows of 13 and 11 at the registered offsets' shape)
    scans = []
    for _ in range(3):
        while True:
            pos = windows(rng, [13, 11])
            lags = [L for L in range(1, 97) if nlinks(pos, L) >= EXACT_MIN]
            dl = [L for L in lags if nlinks(pos, L) >= DROP_MIN]
            if len(lags) >= 12 and len(dl) >= 5:
                break
        ct = rand_text(rng)
        obs = {p: rng.choice(AZ) for p in pos}
        w0, c0 = time.time(), time.process_time()
        res = CK.scan(ct, obs, IT, lags, dl)
        scans.append({"wall_s": round(time.time() - w0, 3), "cpu_s": round(time.process_time() - c0, 3),
                      "lags": len(lags), "drop_lags": len(dl), "exact": sum(v[1] for v in res.values()),
                      "drop": sum(v[2] or 0 for v in res.values())})
    while True:
        pos = windows(rng, [13, 11])
        lags = [L for L in range(1, 97) if nlinks(pos, L) >= EXACT_MIN]
        if lags:
            break
    L = rng.choice(lags)
    A, B, F = rng.choice(tier), rng.choice(tier), rng.choice(AK.FEEDBACK)
    s1, s2 = rng.choice(AK.SIGNS)
    pt, ct = plant(rng, A, B, F, L, s1, s2)
    planted = CK.scan(ct, {p: pt[p] for p in pos}, IT, lags)[(L, s1, s2, F)][1]
    fw = 2 * max(r["wall_s"] for r in scans) * 101 + 10
    fc = 2 * max(r["cpu_s"] for r in scans) * 101 + 10
    rep["V5_throughput"] = {"scans": scans, "planted_full_scan_exact": planted, "forecast_wall_s": round(fw, 1),
                            "forecast_cpu_s": round(fc, 1), "limit_wall_s": 0.8 * 1800, "limit_cpu_s": 0.8 * 1200,
                            "pass": planted >= 1 and fw < 0.8 * 1800 and fc < 0.8 * 1200}

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

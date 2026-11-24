#!/usr/bin/env python3
"""R98 checker-correctness gate (PREREGISTRATION section 3 as amended by AMENDMENT_1.md; synthetic only; reads no
K4 file and no published plaintext). Usage: python3 -I r98/validate98.py OUT.json [--dev-seed N]
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
import slidefair98 as SF  # noqa: E402
import checker98 as CK  # noqa: E402
import alphabets as AL  # noqa: E402

AZ = SF.AZ
TIER_SHA = "563ae44ae9a47539e0e01cabc1415e42619bdf3e906ff1f47b11f2d0bede2233"
SEED = 980901
SOURCES = ("slidefair98.py", "checker98.py", "validate98.py", "run_target98.py", "evaluate98.py")


def windows(rng, lengths):
    """Disjoint random windows of the given lengths inside 0..96 (synthetic positions, not the K4 ones)."""
    while True:
        starts = [rng.randrange(0, 98 - L) for L in lengths]
        pos = set()
        for s, L in zip(starts, lengths):
            pos |= set(range(s, s + L))
        if len(pos) == sum(lengths):
            return sorted(pos)


def plant(rng, conv, PA, CA, pt, force=()):
    """Random per-pair keys; pairs whose index is in force get the key that puts them in the same column."""
    t, r, o, a = conv
    starts = SF.pair_starts(len(pt), a)
    keys = [rng.randrange(26) for _ in range(len(pt))]
    for j in force:
        i = starts[j]
        u, w = (pt[i], pt[i + 1]) if r == 0 else (pt[i + 1], pt[i])
        xu = PA.index(u)
        keys[j] = (CA.index(w) - xu) % 26 if t == "VIG" else (xu + CA.index(w)) % 26
        assert SF.lower_col(CA, t, keys[j], w) == xu
    ct = SF.encrypt(pt, PA, CA, conv, keys)
    return ct, keys


def published_index(obs, conv):
    """Pair indices (into pair_starts) of the published pairs for this convention's parity."""
    a = conv[3]
    return [(i - a) // 2 for i in CK.published_pairs(obs, a)]


def rand_text(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def oracle(ct, obs, sub):
    """Brute force with the reference ENCRYPTOR: per convention and (PA, CA), count published pairs that no key
    reproduces; EXACT if none, DROP adds one per pair whose omission leaves none."""
    per = {}
    for conv in SF.CONVENTIONS:
        t, r, o, a = conv
        starts = CK.published_pairs(obs, a)
        exact = drop = 0
        for PA in sub:
            for CA in sub:
                bad = 0
                for i in starts:
                    u, w = (obs[i], obs[i + 1]) if r == 0 else (obs[i + 1], obs[i])
                    want = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
                    if not any(SF.enc_pair(u, w, PA, CA, t, k) == want for k in range(26)):
                        bad += 1
                        if bad > 1:
                            break
                exact += bad == 0
                drop += len(starts) if bad == 0 else (1 if bad == 1 else 0)
        per[conv] = (exact, drop)
    return per


def main():
    out = Path(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) == 4 and sys.argv[2] == "--dev-seed" else SEED
    rng = random.Random(seed)
    t0w, t0c = time.time(), time.process_time()
    tier = [a for _, a in AL.large_tier()]
    rep = {"round": "R98", "gate_type": "EXACT_CHECKER_CORRECTNESS", "blind_recovery_certified": False,
           "seed": seed, "development_only": seed != SEED, "tier": len(tier),
           "tier_sha256_ok": hashlib.sha256("\n".join(tier).encode()).hexdigest() == TIER_SHA}

    # V1: reference round trip, 400 texts, random conventions/alphabets/keys, forced same-column pairs in 1 of 3
    fails = forced = 0
    for k in range(400):
        conv = SF.CONVENTIONS[rng.randrange(16)]
        PA, CA = rng.choice(tier), rng.choice(tier)
        pt = rand_text(rng)
        npairs = len(SF.pair_starts(97, conv[3]))
        force = rng.sample(range(npairs), 3) if k % 3 == 0 else ()
        forced += len(force)
        try:
            ct, keys = plant(rng, conv, PA, CA, pt, force)
            fails += SF.decrypt(ct, PA, CA, conv, keys) != pt
        except AssertionError:
            fails += 1
    rep["V1_round_trip"] = {"cases": 400, "forced_same_column_pairs": forced, "failures": fails,
                            "pass": fails == 0}

    # V2: forward-encryptor brute force vs both counting paths, every convention, one 120-alphabet sub-tier
    sub = rng.sample([a for a in tier if a != AZ], 119) + [AZ]
    assert len(set(sub)) == 120
    IDXs = CK.tier_idx(sub)
    mism_fast = mism_simple = with_exact = with_drop = 0
    rows = []
    for k in range(30):
        if k % 2 == 0:                                         # planted: PA, CA from the sub-tier, 9+7 windows
            conv = SF.CONVENTIONS[rng.randrange(16)]
            PA, CA = rng.sample(sub, 2) if k % 4 else (rng.choice(sub),) * 2
            pt = rand_text(rng)
            pos = windows(rng, [9, 7])
            obs = {i: pt[i] for i in pos}
            pub = published_index(obs, conv)
            ct, _ = plant(rng, conv, PA, CA, pt, force=pub[:1] if k % 6 == 0 else ())
            kind = "planted"
        else:                                                  # random: short windows, so chance fits are common
            ct, pt = rand_text(rng), rand_text(rng)
            pos = windows(rng, [[3, 3], [5, 3], [5, 5]][(k // 2) % 3])
            obs = {i: pt[i] for i in pos}
            kind = "random"
        orc = oracle(ct, obs, sub)
        _, per_fast = CK.scan(ct, obs, IDXs, SF.CONVENTIONS, fast=True)
        _, per_simple = CK.scan(ct, obs, IDXs, SF.CONVENTIONS, fast=False)
        mf = sum(orc[c] != per_fast[c][:2] for c in SF.CONVENTIONS)
        ms = sum(orc[c] != per_simple[c][:2] for c in SF.CONVENTIONS)
        mism_fast += mf
        mism_simple += ms
        e = sum(v[0] for v in orc.values())
        d = sum(v[1] for v in orc.values())
        with_exact += e > 0
        with_drop += d > 0
        rows.append({"kind": kind, "observed": len(obs), "oracle_exact": e, "oracle_drop": d,
                     "convention_mismatches_fast": mf, "convention_mismatches_simple": ms})
    rep["V2_oracle"] = {"inputs": 30, "sub_tier": len(sub), "conventions": 16,
                        "convention_mismatches_fast": mism_fast, "convention_mismatches_simple": mism_simple,
                        "inputs_with_exact": with_exact, "inputs_with_drop": with_drop, "rows": rows,
                        "pass": mism_fast == 0 and mism_simple == 0 and with_exact >= 10}

    # V3 / V4: full-tier plants on random 13- and 11-letter windows
    IDX = CK.tier_idx(tier)
    index = {a: n for n, a in enumerate(tier)}
    v3 = {"exact_missed": 0, "exact_count_zero": 0, "drop_missed": 0, "drop_count_zero": 0}
    v4 = {"missed": 0, "count_zero": 0}
    for k in range(48):
        conv = SF.CONVENTIONS[k % 16]
        PA, CA = rng.choice(tier), rng.choice(tier)
        pt = rand_text(rng)
        pos = windows(rng, [13, 11])
        obs = {i: pt[i] for i in pos}
        pub = published_index(obs, conv)
        same = k >= 32
        ct, _ = plant(rng, conv, PA, CA, pt, force=[rng.choice(pub)] if same else ())
        ok = CK.label_feasible(ct, obs, IDX, conv, index[PA], index[CA])
        F, G, m = CK.conv_matrices(ct, obs, IDX, conv)
        e, d = CK.scan_conv(F, G)
        if not same:
            v3["exact_missed"] += not ok
            v3["exact_count_zero"] += e < 1
            j = rng.choice(CK.published_pairs(obs, conv[3]))
            obs2 = dict(obs)
            obs2[j] = rng.choice([c for c in AZ if c != obs[j]])
            v3["drop_missed"] += not CK.label_feasible(ct, obs2, IDX, conv, index[PA], index[CA], allow_drop=True)
            F2, G2, _ = CK.conv_matrices(ct, obs2, IDX, conv)
            v3["drop_count_zero"] += CK.scan_conv(F2, G2)[1] < 1
        else:
            v4["missed"] += not ok
            v4["count_zero"] += e < 1
    rep["V3_full_tier_plants"] = {"plants": 32, **v3, "pass": not any(v3.values())}
    rep["V4_same_column_plants"] = {"plants": 16, **v4, "pass": not any(v4.values())}

    # V5: throughput of the full 16-convention scan; the fast and simple counting paths must agree
    scans, agree = [], True
    for k in range(3):
        ct = rand_text(rng)
        obs = {i: rng.choice(AZ) for i in windows(rng, [13, 11])}
        w0, c0 = time.time(), time.process_time()
        agg, _ = CK.scan(ct, obs, IDX, SF.CONVENTIONS, fast=True)
        row = {"wall_s": round(time.time() - w0, 3), "cpu_s": round(time.process_time() - c0, 3), **agg}
        agree &= CK.scan(ct, obs, IDX, SF.CONVENTIONS, fast=False)[0] == agg
        scans.append(row)
    conv = SF.CONVENTIONS[rng.randrange(16)]
    PA, CA = rng.choice(tier), rng.choice(tier)
    pt = rand_text(rng)
    obs = {i: pt[i] for i in windows(rng, [13, 11])}
    ct, _ = plant(rng, conv, PA, CA, pt)
    planted, _ = CK.scan(ct, obs, IDX, SF.CONVENTIONS, fast=True)
    fw = 2 * max(r["wall_s"] for r in scans) * 201 + 10
    fc = 2 * max(r["cpu_s"] for r in scans) * 201 + 10
    rep["V5_throughput"] = {"scans": scans, "fast_simple_agree": agree,
                            "planted_full_scan_exact": planted["exact_feasible_settings"],
                            "forecast_wall_s": round(fw, 1), "forecast_cpu_s": round(fc, 1),
                            "limit_wall_s": 0.8 * 1800, "limit_cpu_s": 0.8 * 1200,
                            "pass": agree and planted["exact_feasible_settings"] >= 1
                            and fw < 0.8 * 1800 and fc < 0.8 * 1200}

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

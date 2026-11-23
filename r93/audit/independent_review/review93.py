#!/usr/bin/env python3
"""R93 independent-model review (Claude Code reviewing ChatGPT's L182). PLAN.md fixes every step.
  gate    OUT.json   synthetic only (no K4 data): T1 toy complete-key oracle, T2 schedules and scope accounting,
                     T3 plants at all 145,728 labels, T4 error plants, T5 second implementation, T6 sensitivity and
                     throughput, T7 the registered q=5 worked example.
  target  OUT.json   provenance checks, then the full scan of the 201 frozen inputs; aggregate counts only, compared
                     with r93/k4/AGGREGATES.json.
Imports nothing from r87/, r92/ or r93/. The C checker is check93r.c (compiled into .build/)."""
import ast
import ctypes
import hashlib
import itertools
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NLO, NHI, M = 5, 96, 24


def keyed(word):
    out = []
    for ch in word + AZ:
        if ch not in out:
            out.append(ch)
    return "".join(out)


ALPHS = [AZ, keyed("KRYPTOS"), keyed("PALIMPSEST"), keyed("ABSCISSA")]
LABELS = [(a, b, n, r, d) for a in range(4) for b in range(4) for n in range(NLO, NHI + 1) for r in range(1, n)
          for d in (1, -1)]
_LIB = None


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lib():
    global _LIB
    if _LIB is None:
        src = HERE / "check93r.c"
        so = HERE / ".build" / f"check93r_{sha(src)[:16]}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")
            subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        IP = ctypes.POINTER(ctypes.c_int)
        L.check_pairs.argtypes = [IP, IP, ctypes.c_int, IP]
        L.check_label.argtypes = [IP, IP, IP, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, IP]
        L.scan.argtypes = [IP, IP, IP, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_longlong)]
        _LIB = L
    return _LIB


def arr(v):
    return (ctypes.c_int * max(1, len(v)))(*v)


def c_pairs(x, y):
    out = (ctypes.c_int * (len(x) + 1))()
    lib().check_pairs(arr(x), arr(y), len(x), out)
    return list(out)


def c_label(pt_letters, ct, pos, label):
    a, b, n, r, d = label
    pin = [ALPHS[a].index(p) for p in pt_letters]
    cout = [ALPHS[b].index(ct[i]) for i in pos]
    out = (ctypes.c_int * (len(pos) + 1))()
    lib().check_label(arr(pin), arr(cout), arr(pos), len(pos), n, r, d, out)
    return list(out)


def c_scan(pt_letters, ct, pos):
    pin4 = [ALPHS[a].index(p) for a in range(4) for p in pt_letters]
    cout4 = [ALPHS[b].index(ct[i]) for b in range(4) for i in pos]
    cnt = (ctypes.c_longlong * 4)()
    lib().scan(arr(pin4), arr(cout4), arr(pos), len(pos), NLO, NHI, cnt)
    return [int(v) for v in cnt]


# ---------------------------------------------------------------- independent Python references (no C) ----------
def floor_offsets(n, r, d, length=97):
    return [d * ((i + r) // n) for i in range(length)]


def encipher(pt, W, label):
    a, b, n, r, d = label
    s = floor_offsets(n, r, d, len(pt))
    return "".join(ALPHS[b][(W[(ALPHS[a].index(p) + si) % 26] - si) % 26] for p, si in zip(pt, s))


def decipher(ct, W, label):
    a, b, n, r, d = label
    inv = [0] * 26
    for u, v in enumerate(W):
        inv[v] = u
    s = floor_offsets(n, r, d, len(ct))
    return "".join(ALPHS[a][(inv[(ALPHS[b].index(c) + si) % 26] - si) % 26] for c, si in zip(ct, s))


def py_flags(pt_letters, ct, pos, label):
    """Dictionary implementation: forward and backward maps, every omission rebuilt."""
    a, b, n, r, d = label
    s = floor_offsets(n, r, d)
    pairs = [((ALPHS[a].index(p) + s[i]) % 26, (ALPHS[b].index(ct[i]) + s[i]) % 26) for p, i in zip(pt_letters, pos)]

    def ok(skip):
        f, g = {}, {}
        for k, (x, y) in enumerate(pairs):
            if k == skip:
                continue
            if f.setdefault(x, y) != y or g.setdefault(y, x) != x:
                return False
        return True
    return [int(ok(-1))] + [int(ok(j)) for j in range(len(pairs))]


# ---------------------------------------------------------------- gate --------------------------------------------
def t1_toy():
    """Every list of pairs in Z_q x Z_q of the stated lengths; brute force over all q! permutations."""
    spec = {2: range(1, 7), 3: range(1, 5), 4: range(1, 4), 5: range(1, 4)}
    cases = bad = 0
    for q, lengths in spec.items():
        perms = list(itertools.permutations(range(q)))
        cells = [(x, y) for x in range(q) for y in range(q)]
        for m in lengths:
            for pl in itertools.product(cells, repeat=m):
                sat = [[P[x] == y for (x, y) in pl] for P in perms]
                want = [int(any(all(s) for s in sat))] + \
                       [int(any(all(v for k, v in enumerate(s) if k != j) for s in sat)) for j in range(m)]
                got = c_pairs([x for x, _ in pl], [y for _, y in pl])
                cases += 1
                bad += got != want
    return {"lists": cases, "disagreements": bad, "pass": bad == 0 and cases == 33483}


def t2_schedules():
    clocks = [(n, r, d) for n in range(NLO, NHI + 1) for r in range(1, n) for d in (1, -1)]
    mism = 0
    seqs = {}
    for n, r, d in clocks:
        t, ev = 0, [0]
        for k in range(1, 97):
            if (k + r) % n == 0:
                t += d
            ev.append(t)
        fl = floor_offsets(n, r, d)
        mism += ev != fl
        seqs[(n, r, d)] = tuple(v % 26 for v in fl)
    distinct = set(seqs.values())
    r87 = {tuple((d * (i // n)) % 26 for i in range(97)) for n in range(1, 97) for d in (1, -1)}
    r92 = {tuple((d * ((i + r) // n)) % 26 for i in range(97)) for n in (2, 3, 4) for r in range(1, n) for d in (1, -1)}
    overlap87 = distinct & r87
    raw87 = sum(v in r87 for v in seqs.values())
    rep = {"clock_labels": len(clocks), "labels": len(clocks) * 16, "step_vs_floor_mismatches": mism,
           "distinct_clock_sequences": len(distinct), "distinct_clock_contact_labels": 16 * len(distinct),
           "sequences_shared_with_r87": len(overlap87), "clock_contact_labels_shared_with_r87": 16 * len(overlap87),
           "raw_labels_shared_with_r87": 16 * raw87,
           "distinct_clock_contact_labels_outside_r87": 16 * (len(distinct) - len(overlap87)),
           "sequences_shared_with_r92": len(distinct & r92)}
    want = {"clock_labels": 9108, "labels": 145728, "step_vs_floor_mismatches": 0, "distinct_clock_sequences": 4690,
            "distinct_clock_contact_labels": 75040, "sequences_shared_with_r87": 94,
            "clock_contact_labels_shared_with_r87": 1504, "raw_labels_shared_with_r87": 36096,
            "distinct_clock_contact_labels_outside_r87": 73536, "sequences_shared_with_r92": 0}
    rep["differences_from_r93_accounting"] = {k: [rep[k], v] for k, v in want.items() if rep[k] != v}
    rep["pass"] = not rep["differences_from_r93_accounting"] and len(LABELS) == 145728
    return rep


def plant(rng, label, kind):
    W = list(range(26))
    rng.shuffle(W)
    if kind == 0:
        pt = "".join(rng.choice(AZ) for _ in range(97))
    elif kind == 1:
        motif = "".join(rng.choice(AZ) for _ in range(rng.randint(2, 7)))
        pt = (motif * 97)[:97]
    else:
        st = rng.randrange(26)
        pt = "".join(AZ[(st + i) % 26] for i in range(97))
    n, r = label[2], label[3]
    boundary = n - r                         # first k >= 1 with (k + r) % n == 0
    rest = rng.sample([i for i in range(1, 96) if i != boundary], M - 3)
    pos = sorted({0, 96, boundary, *rest})
    return W, pt, encipher(pt, W, label), pos


def t3_t4_plants(seed=931101):
    rng = random.Random(seed)
    bad3 = trips = bad4 = 0
    n4 = 0
    for idx, label in enumerate(LABELS):
        W, pt, ct, pos = plant(rng, label, idx % 3)
        obs = [pt[i] for i in pos]
        if c_label(obs, ct, pos, label)[0] != 1:
            bad3 += 1
        if idx % 16 == 0:
            trips += 1
            bad3 += decipher(ct, W, label) != pt
            n4 += 1
            j = rng.randrange(M)
            i = pos[j]
            # (a) the enciphered letter differs from the reported one at observed position i
            alt = rng.choice([c for c in AZ if c != pt[i]])
            ct_a = encipher(pt[:i] + alt + pt[i + 1:], W, label)
            assert sum(u != v for u, v in zip(ct_a, ct)) == 1
            bad4 += c_label(obs, ct_a, pos, label)[1 + j] != 1
            # (b) a ciphertext substitution at observed position i
            ct_b = ct[:i] + rng.choice([c for c in AZ if c != ct[i]]) + ct[i + 1:]
            bad4 += c_label(obs, ct_b, pos, label)[1 + j] != 1
            # (c) a ciphertext substitution off the observation mask
            u = rng.choice([k for k in range(97) if k not in pos])
            ct_c = ct[:u] + rng.choice([c for c in AZ if c != ct[u]]) + ct[u + 1:]
            bad4 += c_label(obs, ct_c, pos, label)[0] != 1
    return ({"plants": len(LABELS), "round_trips": trips, "failures": bad3, "pass": bad3 == 0},
            {"error_plants": n4, "checks": 3 * n4, "failures": bad4, "pass": bad4 == 0})


def t5_second_impl(seed=931103):
    rng = random.Random(seed)
    cmp = bad = feas = 0
    for k in range(8):
        if k < 4:
            ct = "".join(rng.choice(AZ) for _ in range(97))
            pos = sorted(rng.sample(range(97), M))
            obs = [rng.choice(AZ) for _ in pos]
            labs = rng.sample(LABELS, 3000)
        else:
            lab0 = rng.choice(LABELS)
            W, pt, ct, pos = plant(rng, lab0, k % 3)
            obs = [pt[i] for i in pos]
            labs = [lab0] + rng.sample(LABELS, 2999)
        for lab in labs:
            a, b = c_label(obs, ct, pos, lab), py_flags(obs, ct, pos, lab)
            cmp += 1
            bad += a != b
            feas += a[0]
    return {"comparisons": cmp, "flag_vectors_disagreeing": bad, "exact_feasible_seen": feas, "pass": bad == 0 and feas >= 4}


def t6_scan(seed=931102):
    rng = random.Random(seed)
    rows = []
    for k in range(4):
        if k < 3:
            ct = "".join(rng.choice(AZ) for _ in range(97))
            pos = sorted(rng.sample(range(97), M))
            obs = [rng.choice(AZ) for _ in pos]
        else:
            lab = rng.choice(LABELS)
            W, pt, ct, pos = plant(rng, lab, 0)
            obs = [pt[i] for i in pos]
        w0, c0 = time.time(), time.process_time()
        cnt = c_scan(obs, ct, pos)
        rows.append({"input": "planted" if k == 3 else f"random_{k}", "labels": cnt[0], "exact": cnt[1],
                     "drop_labels": cnt[2], "drop_pairs": cnt[3], "wall_s": round(time.time() - w0, 4),
                     "cpu_s": round(time.process_time() - c0, 4)})
    per_w = max(r["wall_s"] for r in rows)
    per_c = max(r["cpu_s"] for r in rows)
    fw, fc = 2 * per_w * 201 + 10, 2 * per_c * 201 + 10
    planted = rows[3]
    ok = (all(r["labels"] == 145728 for r in rows) and planted["exact"] >= 1 and planted["drop_labels"] >= 1
          and fw < 0.8 * 1800 and fc < 0.8 * 1200)
    return {"scans": rows, "forecast_wall_s": round(fw, 2), "forecast_cpu_s": round(fc, 2),
            "forecast_limits_80pct": [1440, 960], "pass": ok}


def t7_worked_example():
    q, W, n, r, d = 5, (2, 4, 1, 0, 3), 5, 4, -1
    p = (0, 1, 2, 3, 4, 0, 1, 2, 3)
    s = [d * ((i + r) // n) for i in range(len(p))]
    c = [(W[(pi + si) % q] - si) % q for pi, si in zip(p, s)]
    inv = [0] * q
    for u, v in enumerate(W):
        inv[v] = u
    back = [(inv[(ci + si) % q] - si) % q for ci, si in zip(c, s)]
    ok = s == [0, -1, -1, -1, -1, -1, -2, -2, -2] and c == [2, 3, 0, 2, 1, 4, 0, 4, 1] and back == list(p)
    return {"offsets": s, "ciphertext": c, "pass": ok}


def gate(out):
    t0 = time.time()
    rep = {"reviewer": "Claude Code", "mode": "SYNTHETIC_ONLY", "k4_data_read": False,
           "source_sha256": {f: sha(HERE / f) for f in ("check93r.c", "review93.py")},
           "alphabets": ALPHS}
    rep["T7_worked_example"] = t7_worked_example()
    rep["T1_toy_oracle"] = t1_toy()
    rep["T2_schedules"] = t2_schedules()
    rep["T3_plants"], rep["T4_error_plants"] = t3_t4_plants()
    rep["T5_second_implementation"] = t5_second_impl()
    rep["T6_sensitivity_throughput"] = t6_scan()
    rep["verdict"] = "GO" if all(v["pass"] for k, v in rep.items() if k.startswith("T")) else "NO-GO"
    rep["wall_s"] = round(time.time() - t0, 2)
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: v.get("pass") for k, v in rep.items() if k.startswith("T")}))


# ---------------------------------------------------------------- target ------------------------------------------
def target(out):
    t0 = time.time()
    gate_rep = json.loads((HERE / "SYNTHETIC.json").read_text())
    assert gate_rep["verdict"] == "GO", "no target run without a published GO"
    assert gate_rep["source_sha256"] == {f: sha(HERE / f) for f in ("check93r.c", "review93.py")}, "source changed"
    inputs_p, k4_p, clue_p = ROOT / "r93/k4/INPUTS.tsv", ROOT / "r39/ic_gate/k4_ciphertext.txt", ROOT / "r73/sealed/reveal_k4.py"
    prov = {"inputs_sha256_ok": sha(inputs_p) == "fbc28710cfba45278f9c34fada0c212e622d17df766b8e82029ec1b6fdad9610",
            "k4_file_sha256_ok": sha(k4_p) == "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3",
            "observation_file_sha256_ok": sha(clue_p) == "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"}
    k4 = k4_p.read_text().strip()
    rows = [l.split("\t") for l in inputs_p.read_text().splitlines()[1:] if l]
    ids, cts = [r[0] for r in rows], [r[1] for r in rows]
    tree = ast.parse(clue_p.read_text())
    clues = next(ast.literal_eval(nd.value) for nd in ast.walk(tree) if isinstance(nd, ast.Assign)
                 and any(getattr(t, "id", None) == "CLUES" for t in nd.targets))
    pos = [o + i for o, t in clues for i in range(len(t))]
    obs = [ch for _, t in clues for ch in t]
    prov.update(k4_97_letters=len(k4) == 97 and k4.isalpha() and k4.isupper(), k4_first_row=ids[0] == "K4" and cts[0] == k4,
                observations=len(pos), observations_unique_in_range=len(set(pos)) == 24 and all(0 <= p < 97 for p in pos),
                inputs=len(rows))
    shuf = cts[1:]
    prov["shuffles_distinct_not_k4_frequency_preserving"] = (len(set(shuf)) == 200 and k4 not in shuf and
                                                              all(sorted(s) == sorted(k4) for s in shuf))
    rng, seen, regen, draws = random.Random(930400), {k4}, [], 0
    while len(regen) < 200 and draws < 10000:
        letters = list(k4)
        rng.shuffle(letters)
        draws += 1
        s = "".join(letters)
        if s in seen:
            continue
        seen.add(s)
        regen.append(s)
    prov["shuffles_regenerated_byte_identical"] = regen == shuf and ids[1:] == [f"SHUF_{k:03d}" for k in range(200)]
    prov["shuffle_draws"] = draws
    assert all(v for k, v in prov.items() if k not in ("observations", "inputs", "shuffle_draws")), prov
    ref = json.loads((ROOT / "r93/k4/AGGREGATES.json").read_text())["inputs"]
    per, agree = {}, True
    c0 = time.process_time()
    for rid, ct in zip(ids, cts):
        L, E, D, P = c_scan(obs, ct, pos)
        per[rid] = {"settings": L, "exact_feasible_labels": E, "drop_feasible_labels": D,
                    "drop_feasible_label_observation_pairs": P}
        agree &= per[rid] == ref[rid]
    tot = {"inputs": len(per), "setting_input_calls": sum(v["settings"] for v in per.values()),
           "exact_decisions": sum(v["settings"] for v in per.values()),
           "omission_decisions": 24 * sum(v["settings"] for v in per.values()),
           "k4": per["K4"], "shuffles_with_any_exact": sum(v["exact_feasible_labels"] > 0 for k, v in per.items() if k != "K4"),
           "shuffles_with_any_drop": sum(v["drop_feasible_labels"] > 0 for k, v in per.items() if k != "K4")}
    rep = {"reviewer": "Claude Code", "mode": "POSTFREEZE_CRIB_ASSISTED_AGGREGATE_REVIEW", "provenance": prov,
           "totals": tot, "agrees_with_r93_aggregates": agree, "per_input": per,
           "outputs": {"decoded_plaintexts": 0, "wirings": 0, "feasible_label_lists": 0, "rankings": 0},
           "scan_cpu_s": round(time.process_time() - c0, 2), "wall_s": round(time.time() - t0, 2)}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print("agrees" if agree else "DISAGREES", json.dumps(tot))


if __name__ == "__main__":
    {"gate": gate, "target": target}[sys.argv[1]](sys.argv[2])

#!/usr/bin/env python3
"""Independent historical audit helpers and synthetic oracle. Never emits plaintext.

No original solver is imported. Route constructors may be imported ONLY by the
synthetic comparison test. Target work requires a separate bounded invocation.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH = (AZ, "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
        "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ADJOUZBEKPVCGMRXIHNTYSFLQW")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inverse(p):
    return [p.index(i) for i in range(len(p))]


def turn(n, width, direction):
    # Sort cell coordinates in the order in which the turned grid is read.
    return sorted(range(n), key=lambda i: (i % width, -(i // width)) if direction == "CW" else (-(i % width), i // width))


def rotation(w1, w2, d1, d2, reverse=False, n=97):
    first, second = turn(n, w1, d1), turn(n, w2, d2)
    result = [first[j] for j in second]
    return inverse(result) if reverse else result


def columnar(word, fill_reverse, snake, sort_reverse, read_reverse, reverse):
    w = len(word)
    columns = sorted(range(w), key=lambda c: (word[c], c), reverse=bool(sort_reverse))
    priority = {c: i for i, c in enumerate(columns)}
    def coordinate(i):
        row, col = divmod(i, w)
        if snake and row % 2:
            col = w - col - 1
        if fill_reverse:
            col = w - col - 1
        return priority[col], -row if read_reverse else row
    result = sorted(range(97), key=coordinate)
    return inverse(result) if reverse else result


def named_rotations(pairs, mixed=False):
    for a, b in pairs:
        for d1, d2 in (("CW", "CCW"), ("CCW", "CW")) if mixed else (("CW", "CW"), ("CCW", "CCW")):
            for rev in (False, True):
                dirs = d1 + "-" + d2 if mixed else d1
                name = f"R{a}x{b}/{dirs}/{'inv' if rev else 'fwd'}"
                yield name, rotation(a, b, d1, d2, rev)


def route_sets():
    short = list(named_rotations(((24, 8), (23, 8), (25, 8), (24, 7), (24, 9))))
    large = list(named_rotations(itertools.product(range(4, 29), repeat=2)))
    mixed = list(named_rotations(itertools.product(range(4, 29), repeat=2), True))
    col = []
    for word in ("KRYPTOS", "PALIMPSEST", "ABSCISSA"):
        for f, s, o, v in itertools.product((0, 1), repeat=4):
            for rev in (0, 1):
                col.append((f"{word}/F{f}S{s}O{o}V{v}/{'INV' if rev else 'FWD'}", columnar(word, f, s, o, v, rev)))
    both = lambda seq: [(name, order, p) for name, p in seq for order in ("S_then_T", "T_then_S")]
    return {"r32_f1": [("ID", "ID", list(range(97)))] + both(short), "r32_f2": both(large),
            "r41_A": [(name, "S_then_T", p) for name, p in short + col],
            "r41_B": [(name, "S_then_T", p) for name, p in large + mixed]}


def write_routes(path, rows):
    path.write_text("".join(f"{n} {o} {','.join(map(str, p))}\n" for n, o, p in rows))


def load_routes(path):
    return [(n, o, list(map(int, p.split(',')))) for n, o, p in (line.split() for line in path.read_text().splitlines() if line)]


def key_at(family, index, source):
    if family in ("G5", "C6"):
        lag = 5 if family == "G5" else 6
        digits = [int(c) for c in str(index).zfill(lag)]
        while len(digits) < 97:
            n = len(digits)
            digits.append((digits[n - lag] + digits[n - lag + 1]) % 10)
        return digits
    windows = len(source) - 96
    variant, offset = divmod(index, windows)
    s = source[::-1] if variant // 2 else source
    return [ALPH[variant % 2].index(c) for c in s[offset:offset + 97]]


def encrypt(pt, key, pa, ca, op, route):
    _, order, permutation = route
    if order == "T_then_S":
        pt = ''.join(pt[i] for i in permutation)
    x = []
    for i, p in enumerate(pt):
        value = pa.index(p)
        value = value + key[i] if op == 0 else key[i] - value if op == 1 else value - key[i]
        x.append(ca[value % 26])
    if order == "S_then_T":
        x = [x[i] for i in permutation]
    return ''.join(x)


def decrypt(ct, key, pa, ca, op, route):
    _, order, permutation = route
    if order == "S_then_T":
        ct = ''.join(ct[i] for i in inverse(permutation))
    text = []
    for i, c in enumerate(ct):
        value = ca.index(c)
        value = value - key[i] if op == 0 else key[i] - value if op == 1 else value + key[i]
        text.append(pa[value % 26])
    if order == "T_then_S":
        text = [text[i] for i in inverse(permutation)]
    return ''.join(text)


def free_feasible(ct, want, key, ca, op, route):
    # Scalar pairwise equality oracle, deliberately unlike the hash-join kernel.
    q = inverse(route[2])
    pairs = [(want[i], (ca.index(ct[q[i]]) + (1 if op else -1) * key[i]) % 26)
             for i in range(97) if want[i] != '?']
    return all((p == r) == (v == s) for j, (p, v) in enumerate(pairs) for r, s in pairs[:j])


def kernel(binary, tmp, mode, family, ct, want, rows, source, start=0, count=0, tag="job"):
    paths = {s: tmp / f"{tag}.{s}" for s in ("ct", "want", "routes", "source", "json")}
    paths["ct"].write_text(ct + '\n'); paths["want"].write_text(want + '\n')
    paths["source"].write_text(source + '\n'); write_routes(paths["routes"], rows)
    subprocess.run([str(binary), str(mode), family, str(paths["ct"]), str(paths["want"]), str(paths["routes"]),
                    str(paths["source"]), str(paths["json"]), str(start), str(count)], check=True, stdout=subprocess.DEVNULL)
    return json.loads(paths["json"].read_text())


def toy_exhaustion():
    q, n = 3, 3
    alphabets = list(itertools.permutations(range(q)))
    words = list(itertools.product(range(q), repeat=n))
    tests = 0
    # Exhaustive free-alphabet existence versus relational equality, including masked observations.
    for plain in words:
        for cipher in words:
            for key in words:
                for sign in (-1, 1):
                    values = [(c + sign * k) % q for c, k in zip(cipher, key)]
                    for positions in ((0, 1, 2), (0, 2)):
                        relation = all((plain[i] == plain[j]) == (values[i] == values[j]) for i in positions for j in positions)
                        brute = any(all(a[values[i]] == plain[i] for i in positions) for a in alphabets)
                        assert relation == brute
                        tests += 1
    return tests


def synthetic(binary, out):
    rng = random.Random(2026112201)
    sets = route_sets()
    route_comparisons = {}
    # This import is only an oracle comparison in this synthetic test, never used by the checker or target driver.
    spec = importlib.util.spec_from_file_location("historical_routes_oracle", ROOT / "r41/blind/routes.py")
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    for name, order, perm in sets["r32_f2"]:
        assert perm == old.rotation(name)
    for name, order, perm in sets["r41_B"][2500:]:
        assert perm == old.mixed_rotation(name)
    for label, path in (("r32_f1", ROOT / "k4kit/r32/runs/routes_f1.txt"),
                        ("r41_A", ROOT / "r41/x1_route_pafree/out/routes_A.txt"),
                        ("r41_B", ROOT / "r41/x1_route_pafree/out/routes_B.txt")):
        archived = load_routes(path)
        if label.startswith("r41"):
            archived = [r for r in archived if r[1] == "S_then_T"]
        assert sets[label] == archived, label
        route_comparisons[label] = len(sets[label])
    route_comparisons["r32_f2_against_historical_constructor"] = len(sets["r32_f2"])
    report = {"toy_exhaustive_comparisons": toy_exhaustion(), "route_comparisons": route_comparisons,
              "kernel_scalar_comparisons": [], "boundary_plants": [], "benchmarks": {},
              "source_sha256": {"kernel": sha(HERE / "replay_kernel.cpp"), "checker": sha(__file__)}}
    with tempfile.TemporaryDirectory(prefix="kryptos_history_synthetic_") as td:
        tmp = Path(td)
        pt = ''.join(rng.choice(AZ) for _ in range(97))
        observed = sorted(rng.sample(range(97), 24))
        want = ''.join(c if i in observed else '?' for i, c in enumerate(pt))
        source = ''.join(rng.choice(AZ) for _ in range(105))
        selected = [sets["r32_f1"][i] for i in (0, 1, 2, 39, 40)]
        for family, start, count in (("G5", 0, 17), ("G5", 99983, 17), ("C6", 999983, 17), ("CARTER", 0, 36), ("K1K3", 0, 36)):
            key = key_at(family, start, source)
            ct = encrypt(pt, key, ALPH[1], ALPH[0], 2, selected[-1])
            got = kernel(binary, tmp, 32, family, ct, want, selected, source, start, count)
            hist = [0] * 25
            for route in selected:
                for i in range(start, start + count):
                    k = key_at(family, i, source)
                    for pa, ca, op in itertools.product(ALPH[:2], ALPH[:2], range(3)):
                        text = decrypt(ct, k, pa, ca, op, route)
                        hist[sum(text[p] == pt[p] for p in observed)] += 1
            assert got["histogram"] == hist
            report["kernel_scalar_comparisons"].append({"mode":32,"family":family,"start":start,"settings":sum(hist)})
        # Distinct mask patterns, both operations, all seven fixed cipher alphabets.
        free_routes = [sets["r41_A"][i] for i in (0, 19, 20, 115)] + [sets["r41_B"][i] for i in (0, 2499, 2500, 4999)]
        for family, start, count in (("G5", 99983, 17), ("C6", 999983, 17), ("CARTER", 0, 36)):
            pa = ''.join(rng.sample(AZ, 26));ct = encrypt(pt, key_at(family,start,source),pa,ALPH[-1],0,free_routes[-1])
            got = kernel(binary,tmp,41,family,ct,want,free_routes,source,start,count)
            expected = 0
            for route in free_routes:
                for i in range(start,start+count):
                    k = key_at(family,i,source)
                    expected += sum(free_feasible(ct,want,k,ca,op,route) for ca,op in itertools.product(ALPH,range(2)))
            assert got["consistent"] == expected and expected >= 1
            report["kernel_scalar_comparisons"].append({"mode":41,"family":family,"start":start,"settings":got["settings"],"consistent":expected})
        for family, indices in (("G5",(0,99999)),("C6",(0,999999)),("CARTER",(0,8,9,17,18,26,27,35))):
            for idx in indices:
                for order in ("S_then_T","T_then_S"):
                    route = next(r for r in selected if r[1] == order)
                    ct = encrypt(pt,key_at(family,idx,source),ALPH[1],ALPH[1],1,route)
                    g = kernel(binary,tmp,32,family,ct,want,[route],source,idx,1)
                    assert g["consistent"] >= 1
                    report["boundary_plants"].append({"mode":32,"family":family,"index":idx,"order":order})
                route=free_routes[-1];pa=''.join(rng.sample(AZ,26));ct=encrypt(pt,key_at(family,idx,source),pa,ALPH[5],2,route)
                g=kernel(binary,tmp,41,family,ct,want,[route],source,idx,1);assert g["consistent"]>=1
                report["boundary_plants"].append({"mode":41,"family":family,"index":idx})
        random_ct = ''.join(rng.choice(AZ) for _ in range(97))
        report["benchmarks"]["r32_100routes_G5"] = kernel(binary,tmp,32,"G5",random_ct,want,sets["r32_f2"][:100],source,tag="bench32")
        report["benchmarks"]["r41_5000routes_C6"] = kernel(binary,tmp,41,"C6",random_ct,want,sets["r41_B"],source,tag="bench41")
    estimate32 = report["benchmarks"]["r32_100routes_G5"]["wall_seconds"] * 60
    estimate41 = report["benchmarks"]["r41_5000routes_C6"]["wall_seconds"] * 54
    report["conservative_projection_seconds"] = {"R32":estimate32,"R41":estimate41}
    report["pretarget_decision"] = {"R32":"FULL" if estimate32<960 else "SAMPLE", "R41":"FULL_FEASIBILITY" if estimate41<1440 else "SAMPLE"}
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({"toy":report["toy_exhaustive_comparisons"],"projections":report["conservative_projection_seconds"],"decision":report["pretarget_decision"]}))


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--synthetic',action='store_true');ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if not args.synthetic:raise SystemExit('Only the synthetic stage is enabled here; target driver is separate.')
    synthetic(args.binary,args.out)

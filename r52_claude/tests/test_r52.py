#!/usr/bin/env python3
"""R52/R52b reproducibility and data-contract tests (Claude Code; added after the owner review of PR #12).
Run from anywhere: python3 -I r52_claude/tests/test_r52.py    (needs g++; about 15 s)

LABEL: R52 is a CRIB-CONDITIONED exploratory screen. It uses the 24 published K4 letters at their published positions
to rule key/route/alphabet settings out. This file is sealed-side test code; nothing here is a blind solver, and its
clue letters must never be copied into blind code.

Checks:
 1. Pre-registration and freeze hashes (PROTOCOL.sha256, PROTOCOL_B.sha256, blind_b/FROZEN.sha256).
 2. alphabets.txt is exactly the declared vocabulary: the R44b candidate rule (top 5,000 ORTH words of length 5-10,
    4,749 distinct keyword alphabets) plus the 15 Kryptos-themed keywords; sorted, distinct, each a permutation.
 3. routes.txt is exactly identity + the four K3 24x8 double rotations x {S_then_T, T_then_S}, regenerated with the
    strictblind route maker.
 4. Both screens compile; fast == reference byte for byte (B5/b4, B7/b4); both reproduce the frozen R52_RESULT.tsv
    rows for B5/b4, B7/b4, B10/b4 and B10/b5.
 5. Planted controls (independent encryptor written here): 8 settings over bases, orders, orientations and signs, with
    public R44 holdout-B passages; the fast screen must report each true setting as keyword-feasible.
 6. R52b replay: the blind input is the un-transposed K4 text under the survivor route; the frozen K4 output and the
    four controls re-encrypt exactly; controls equal their sealed truth; the post-freeze clue count is 1/24.
    NOTE: R52b supplied the TRUE key to the solver for its controls and the selected key for K4 (known-key solve of a
    crib-selected setting). It is not an unknown-key recovery and does not meet the 16/20 unknown-key gate."""
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R52 = ROOT / "r52_claude"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))   # sealed-side only
FAIL = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAIL.append(msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def hash_file(listing, base):
    for line in Path(listing).read_text().splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            p = (base / name.strip()).resolve()
            check(p.exists() and sha(p) == h, f"hash {listing.relative_to(ROOT)}: {name.strip()}")


def kwa(w):
    out = ""
    for ch in w + AZ:
        if ch not in out:
            out += ch
    return out


def chain_key(primer, B, b):
    k = []
    x = primer
    for _ in range(b):
        k.append(x % B)
        x //= B
    k = k[::-1]
    while len(k) < 97:
        k.append((k[-b] + k[-b + 1]) % B)
    return k


def mask(text):
    w = ["?"] * 97
    for s, t in CLUES:
        for i in range(len(t)):
            w[s + i] = text[s + i]
    return "".join(w)


def encrypt(pt, pa, ca, key, sign, perm, order):
    """Independent encryptor. Substitution: c = CA[(PA^-1(p) + sign*k) mod 26].
    ID: in place. S_then_T: X[i] = sub(P[i], k_i), CT[j] = X[perm[j]]. T_then_S: CT[j] = sub(P[perm[j]], k_j)."""
    sub = lambda p, k: ca[(pa.index(p) + sign * k) % 26]
    if order == "ID":
        return "".join(sub(pt[i], key[i]) for i in range(97))
    if order == "S_then_T":
        x = [sub(pt[i], key[i]) for i in range(97)]
        return "".join(x[perm[j]] for j in range(97))
    return "".join(sub(pt[perm[j]], key[j]) for j in range(97))


def main():
    hash_file(R52 / "PROTOCOL.sha256", R52)
    hash_file(R52 / "PROTOCOL_B.sha256", R52)
    hash_file(R52 / "blind_b/FROZEN.sha256", ROOT)

    # 2. vocabulary contract
    alph = [l.strip() for l in (R52 / "alphabets.txt").read_text().splitlines() if l.strip()]
    ws = []
    for ln in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines():
        w, ex, _ = ln.split()
        if float(ex) > -1e90 and 5 <= len(w) <= 10:
            ws.append((-float(ex), w))
    ws.sort()
    common = {kwa(w) for _, w in ws[:5000]}
    themed_words = [l.split()[0] for l in (ROOT / "r44/audit/kryptos_keywords.tsv").read_text().splitlines() if l.strip()]
    themed = {kwa(w) for w in themed_words}
    check(len(common) == 4749 and len(themed_words) == 15, "declared vocabulary: 4,749 common + 15 themed keywords")
    check(len(alph) == 4761 and len(set(alph)) == 4761 and alph == sorted(alph)
          and all(sorted(a) == list(AZ) for a in alph) and set(alph) == common | themed,
          "alphabets.txt = declared vocabulary (4,761 distinct permutations, sorted)")

    # 3. route contract
    sys.path.insert(0, str(ROOT / "strictblind/blind"))
    import routes as rmod
    rl = [l.split() for l in (R52 / "routes.txt").read_text().splitlines() if l.strip()]
    want = [("ID", "ID", list(range(97)))]
    for name in ("R24x8/CW/fwd", "R24x8/CW/inv", "R24x8/CCW/fwd", "R24x8/CCW/inv"):
        p = rmod.rotation(name)
        want += [(name, "S_then_T", p), (name, "T_then_S", p)]
    got = [(n, o, list(map(int, p.split(",")))) for n, o, p in rl]
    check(sorted(got) == sorted(want), "routes.txt = identity + four 24x8 rotations x both orders (regenerated)")
    perms = {(n, o): p for n, o, p in got}

    W = ["?"] * 97
    for s, t in CLUES:
        for i, c in enumerate(t):
            W[s + i] = c
    W = "".join(W)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        exe = {}
        for k, src in (("ref", "chain_screen.cpp"), ("fast", "chain_screen_fast.cpp")):
            r = subprocess.run(["g++", "-std=c++17", "-O2", src, "-o", str(td / k)], cwd=R52 / "sealed",
                               capture_output=True, text=True)
            check(r.returncode == 0, f"compile sealed/{src}" + ("" if r.returncode == 0 else "\n" + r.stderr[-2000:]))
            exe[k] = td / k
        if FAIL:
            return finish()
        (td / "k4.txt").write_text(K4 + "\n")

        def screen(kind, ct_path, letters, B, b):
            out = td / f"{kind}_{B}_{b}_{ct_path.stem}.tsv"
            r = subprocess.run([str(exe[kind]), str(R52 / "alphabets.txt"), str(R52 / "routes.txt"), str(ct_path),
                                letters, str(B), str(b), str(out)], capture_output=True, text=True)
            return out.read_text() if r.returncode == 0 else None

        # 4. replay against the frozen result
        frozen = (R52 / "R52_RESULT.tsv").read_text().splitlines()
        for B, b in ((5, 4), (7, 4), (10, 4), (10, 5)):
            f = screen("fast", td / "k4.txt", W, B, b)
            rows = [l.split("\t", 1)[1] for l in frozen if l.startswith(f"K4_B{B}_b{b}\t")]
            check(f is not None and f.splitlines() == rows and len(rows) >= 9,
                  f"fast screen reproduces frozen R52_RESULT rows for B{B}/b{b}")
            if (B, b) in ((5, 4), (7, 4)):
                check(screen("ref", td / "k4.txt", W, B, b) == f, f"reference == fast byte for byte (B{B}/b{b})")

        # 5. planted controls
        truth_b = json.loads((ROOT / "r44/holdout_b/sealed_truth.json").read_text())
        texts = [v["plaintext"] for v in truth_b.values()]
        rng = random.Random(52900)
        settings = [(7, 4, "ID", "", "kwPA", +1), (7, 4, "S_then_T", "R24x8/CW/inv", "kwCA", -1),
                    (10, 4, "T_then_S", "R24x8/CCW/fwd", "kwPA", -1), (10, 4, "S_then_T", "R24x8/CCW/inv", "kwCA", +1),
                    (5, 4, "T_then_S", "R24x8/CW/fwd", "kwCA", +1), (5, 4, "ID", "", "kwCA", -1),
                    (7, 4, "T_then_S", "R24x8/CCW/inv", "kwPA", +1), (10, 4, "S_then_T", "R24x8/CW/fwd", "kwPA", -1)]
        found = 0
        for n, (B, b, order, rname, orient, sign) in enumerate(settings):
            pt = texts[n]
            kw = alph[rng.randrange(len(alph))]
            free = list(AZ)
            rng.shuffle(free)
            free = "".join(free)
            pa, ca = (kw, free) if orient == "kwPA" else (free, kw)
            primer = rng.randrange(B ** b)
            key = chain_key(primer, B, b)
            name = rname if order != "ID" else "ID"
            perm = perms[(name, order)]
            ct = encrypt(pt, pa, ca, key, sign, perm, order)
            cp = td / f"plant{n}.txt"
            cp.write_text(ct + "\n")
            out = screen("fast", cp, mask(pt), B, b) or ""
            line = "\t".join(["KEYWORD_FEASIBLE", f"B{B}_b{b}", str(primer), name, order, kw, orient,
                              "+" if sign > 0 else "-"])
            ok = line in out.splitlines()
            found += ok
            check(ok, f"plant {n}: B{B}/b{b} {name} {order} {orient} {'+' if sign > 0 else '-'} found at its true setting")
        check(found == len(settings), f"planted controls {found}/{len(settings)}")

    # 6. R52b replay
    inp = (R52 / "blind_b/K4_input.tsv").read_text().splitlines()[1]
    _, xct, digits = inp.split("\t")
    key = list(map(int, digits.split(",")))
    perm = perms[("R24x8/CCW/inv", "S_then_T")]
    q = [0] * 97
    for j in range(97):
        q[perm[j]] = j
    check(xct == "".join(K4[q[i]] for i in range(97)), "R52b input = K4 un-transposed under R24x8/CCW/inv S_then_T")
    check(key == chain_key(int("NMDEG", 26), 26, 5) == [(-k) % 26 for k in chain_key(int("34DCA", 26), 26, 5)],
          "R52b key = the survivor's base-26 chain key (NMDEG with +, = 34DCA with -)")
    res = json.loads((R52 / "blind_b/K4_RESULT.jsonl").read_text().splitlines()[0])
    pt, pa, ca = res["plaintext"], res["plaintext_alphabet"], res["ciphertext_alphabet"]
    check("".join(ca[(pa.index(pt[i]) + key[i]) % 26] for i in range(97)) == xct, "R52b K4 output re-encrypts exactly")
    hits = sum(pt[s + i] == c for s, t in CLUES for i, c in enumerate(t))
    check(hits == 1, f"R52b post-freeze clue count = {hits}/24 (frozen report: 1/24)")
    truth = json.loads((R52 / "blind_b/ctl_sealed_truth.json").read_text())
    ctl_in = {l.split("\t")[0]: l.split("\t") for l in (R52 / "blind_b/CTL_input.tsv").read_text().splitlines()[1:] if l}
    rows = [json.loads(l) for l in (R52 / "blind_b/CTL_RESULT.jsonl").read_text().splitlines() if l.strip()]
    exact = 0
    for r in rows:
        _, cct, cd = ctl_in[r["id"]]
        ck = list(map(int, cd.split(",")))
        ok = "".join(r["ciphertext_alphabet"][(r["plaintext_alphabet"].index(r["plaintext"][i]) + ck[i]) % 26]
                     for i in range(97)) == cct
        check(ok, f"R52b control {r['id']} re-encrypts exactly")
        exact += r["plaintext"] == truth[r["id"]]["plaintext"]
    check(len(rows) == 4 and exact == 4, f"R52b known-key controls exact {exact}/4 (key supplied; not an unknown-key gate)")
    return finish()


def finish():
    print(f"\n{'ALL R52 TESTS PASSED' if not FAIL else f'{len(FAIL)} FAILURE(S)'}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

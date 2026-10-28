"""Shared helpers for the R30 runs (Claude Code). See PREREGISTRATION_R30.md."""
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
from k4common import ANCH, AZ, BIN, DATA, K4, inv, route, setup, solver_line  # noqa: E402,F401
from key_oracle import checks, possible  # noqa: E402,F401

PROTOCOL = HERE / "PREREGISTRATION_R30.md"
RUNS = HERE / "runs"
MODELS = {"ORTH": DATA / "word_model_orth.tsv", "ORTHXQ": RUNS / "word_model_orthxq.tsv"}
BAR_ORTH = -114.9


def assert_protocol():
    want = (HERE / "PROTOCOL.sha256").read_text().split()[0]
    got = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    assert got == want, f"protocol changed: {got} != {want}"
    fx = hashlib.sha256((HERE / "fixtures_punct.json").read_bytes()).hexdigest()
    assert fx == "6e3169dd123018dcce79212028f735d4a594c63d64f7a7d73337579e6697bd6b", "fixtures changed"
    return got


def ensure_models():
    RUNS.mkdir(exist_ok=True)
    xq = MODELS["ORTHXQ"]
    if not xq.exists():
        xq.write_text(MODELS["ORTH"].read_text() + "X -1.5 -1e+100\nQ -2.5 -1e+100\n")
    return {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in MODELS.items()}


def chain_key(primer, b, n=97):
    """Chain addition: k_i = k_{i-b} + k_{i-b+1} mod 10 (b = 5 is Gromark)."""
    k = [int(x) for x in f"{int(primer):0{b}d}"]
    while len(k) < n:
        k.append((k[-b] + k[-b + 1]) % 10)
    return k[:n]


def seed(label):
    return random.Random(label).randrange(1, 2 ** 63)


def run_solver(lines, tag, restarts, model="ORTH", workers=4):
    """lines: solver input lines (already carrying their seeds). Returns {id: best row by W} and all rows."""
    RUNS.mkdir(exist_ok=True)
    parts = [lines[i::workers] for i in range(workers)]
    procs, outs = [], []
    for h, part in enumerate(parts):
        if not part:
            continue
        fin, fout = RUNS / f"{tag}_in{h}.txt", RUNS / f"{tag}_out{h}.jsonl"
        fin.write_text("\n".join(part) + "\n")
        outs.append(fout)
        procs.append(subprocess.Popen([str(BIN / "solver_s2kp"), str(MODELS[model]), str(DATA / "quad_log10.f32"),
                                       str(fin), str(fout), str(restarts), "40000", "0.05", "0"]))
    assert all(p.wait() == 0 for p in procs), "solver failed"
    best, rows = {}, []
    for fout in outs:
        for ln in open(fout):
            r = json.loads(ln)
            rows.append(r)
            if r["id"] not in best or r["W"] > best[r["id"]]["W"]:
                best[r["id"]] = r
    return best, rows


def encrypt(P, key, pa, ca, perm=None, order="T_then_S"):
    """Forward encryption under the R27 conventions (identity when perm is None)."""
    if perm is None:
        return "".join(ca[(pa.index(P[t]) + key[t]) % 26] for t in range(len(P)))
    if order == "S_then_T":
        X = "".join(ca[(pa.index(P[t]) + key[t]) % 26] for t in range(len(P)))
        return "".join(X[perm[j]] for j in range(len(P)))
    return "".join(ca[(pa.index(P[perm[j]]) + key[j]) % 26] for j in range(len(P)))


def verify_row(row, key, ct, perm=None, order="T_then_S", anch=ANCH):
    """Independent check of a solver row: its alphabets re-encrypt its plaintext to the ciphertext, clues hold."""
    P = row["plaintext"]
    # plaintext_alphabet[r] is the letter at rank r; ciphertext_alphabet likewise
    pa = list(row["plaintext_alphabet"])
    ca = list(row["ciphertext_alphabet"])
    if sorted(pa) != list(AZ) or sorted(ca) != list(AZ):
        return False
    if any(P[i] != c for i, c in anch.items()):
        return False
    return encrypt(P, key, pa, ca, perm, order) == ct


def forced_mask(key, ct_sub, anch_sub, perm=None, sign=1):
    """Forced letters in substitution order (within-component rule, see protocol), mapped to plaintext order.
    ct_sub/anch_sub are the substitution-layer ciphertext and anchors (k4common.setup output); perm maps
    substitution position j -> plaintext position perm[j] for T_then_S (None = identity)."""
    adj = {}
    for i, p in anch_sub.items():
        d = (sign * key[i]) % 26
        u, v = ("P", p), ("C", ct_sub[i])
        adj.setdefault(u, []).append((v, d))
        adj.setdefault(v, []).append((u, -d))
    pot, comp = {}, {}
    for root in adj:
        if root in pot:
            continue
        pot[root], comp[root] = 0, root
        stack = [root]
        while stack:
            u = stack.pop()
            for v, d in adj[u]:
                if v not in pot:
                    pot[v], comp[v] = (pot[u] + d) % 26, root
                    stack.append(v)
    byval = {}
    for node, pv in pot.items():
        if node[0] == "P":
            byval[(comp[node], pv)] = node[1]
    n = len(ct_sub)
    out = ["?"] * n
    for j in range(n):
        c = ("C", ct_sub[j])
        if c in pot:
            want = (pot[c] - sign * key[j]) % 26
            letter = byval.get((comp[c], want))
            if letter:
                out[j if perm is None else perm[j]] = letter
    return "".join(out)

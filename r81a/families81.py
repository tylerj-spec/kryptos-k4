"""R81a families (r80/FABLE_IDENTIFIABILITY.md §2.2 G4, G5-blind; no K4 data, no published letters).
R79's keyword families extended in two ways, solved by the same C solver (r79/slotsolve.c):
  G5  the PALIMPSEST and ABSCISSA alphabets on the main sides (plaintext and ciphertext alphabet each any of
      AZ / KRY / PAL / ABS; key alphabet AZ or KRY); only conventions R79 did not run:
        H7CT_A  keyword + ciphertext feedback lag 1..48                       (72 new conventions)
        LIB_A   R79's 982 slot rules, stream none (24 new) or feedback lag 1..7 (72 new)
        PROG_A  progressive mask, plaintext or ciphertext alphabet PAL or ABS (24 new pa/ca/sign combinations)
  G4  new position rules, every convention (R79's and the new ones):
        LIB_G4  ROT  keyword rotated by d places after each pass: slot = (i + d*(i div m)) mod m
                ALT  two keywords letter by letter: even i -> A[(i div 2) mod m1], odd i -> B[(i div 2) mod m2]
                     (both with stream none or feedback lag 1..7)
                RESTART  the keyword restarts at position c (10..87)
                SPLIT    keyword A before position c, keyword B from c (m1, m2 in 2..6)
                     (stream none only)
Keywords 1..12 letters, any letters. Same stage as R79: IDX[ca][c] = s*IDX[pa][p] + t*(IDX[ka][W[slot]] + S)."""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import families as F79  # noqa: E402

N, AZ = core.N, core.AZ
A4 = ("AZ", "KRY", "PAL", "ABS")
OPS, ALPH = core.OPS, core.ALPH
IDX = {k: v.astype(np.int64) for k, v in core.IDX.items()}
LET = {k: v.astype(np.int64) for k, v in core.LET.items()}
MKEY = 12
FAMS = ("H7CT_A", "LIB_A", "LIB_G4", "PROG_A")
CONVK = [(pa, ca, ka, op) for pa in A4 for ca in A4 for ka in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
CONV32 = [(pa, ca, "AZ", op) for pa in A4 for ca in A4 for op in ("VIG", "BEAU")]
NEWK = [c for c in CONVK if c not in F79.CONV24]
NEW32 = [c for c in CONV32 if c not in F79.CONV8]
PROG_NEW = [(pa, ca, op) for pa in A4 for ca in A4 for op in ("VIG", "BEAU") if "PAL" in (pa, ca) or "ABS" in (pa, ca)]


@lru_cache(maxsize=1)
def g4defs():
    """(rule, params, m, stream_ok): stream_ok = also run with ciphertext feedback lag 1..7."""
    out = [("ROT", (d,), m, True) for m in range(2, MKEY + 1) for d in range(1, m)]
    out += [("ALT", (m1, s - m1), s, True) for s in range(4, MKEY + 1) for m1 in range(2, s - 1)]
    out += [("RESTART", (c,), m, False) for c in range(10, 88) for m in range(2, MKEY + 1)]
    out += [("SPLIT", (c, m1), m1 + m2, False) for c in range(10, 88) for m1 in range(2, 7) for m2 in range(2, 7)]
    return out


def g4_slot_map(rule, par, m):
    """Decode path: slot of every position (position-only rules)."""
    i = np.arange(N)
    if rule == "ROT":
        return (i + par[0] * (i // m)) % m
    if rule == "ALT":
        m1, m2 = par
        return np.where(i % 2 == 0, (i // 2) % m1, m1 + (i // 2) % m2)
    if rule == "RESTART":
        c = par[0]
        return np.where(i < c, i % m, (i - c) % m)
    if rule == "SPLIT":
        c, m1 = par
        return np.where(i < c, i % m1, m1 + (i - c) % (m - m1))
    raise ValueError(rule)


def slot_any(rule, par, m, ct):
    if rule in ("ROT", "ALT", "RESTART", "SPLIT"):
        return [int(v) for v in g4_slot_map(rule, par, m)]
    return F79.slot_map(rule, par, m, ct)


# ------------------------------------------------------------------------------------------------ explicit cipher
class State(F79._State):
    """R79's encryption-side rule state, extended with the G4 rules (written as step-by-step counters)."""

    def __init__(self, rule, par, m):
        super().__init__(rule, par, m) if rule not in ("ROT", "ALT", "RESTART", "SPLIT") else None
        self.rule, self.par, self.m, self.i, self.seq = rule, par, m, 0, getattr(self, "seq", None)
        if rule in ("ROT", "ALT", "RESTART", "SPLIT"):
            self.seq = []
            if rule == "ROT":
                start, pos = 0, 0
                for _ in range(N):
                    self.seq.append((start + pos) % m)
                    pos += 1
                    if pos == m:
                        pos, start = 0, start + par[0]
            elif rule == "ALT":
                m1, m2 = par
                a = b = 0
                for k in range(N):
                    if k % 2 == 0:
                        self.seq.append(a)
                        a = (a + 1) % m1
                    else:
                        self.seq.append(m1 + b)
                        b = (b + 1) % m2
            else:
                c = par[0]
                m1 = par[1] if rule == "SPLIT" else m
                m2 = m - m1 if rule == "SPLIT" else m
                p = 0
                for k in range(N):
                    if k == c:
                        p = 0
                    self.seq.append(p if k < c else (m1 if rule == "SPLIT" else 0) + p)
                    p = (p + 1) % (m1 if k < c else m2)
            self.ptr, self.dr, self.prev, self.seen = 0, 1, None, {}

    def cur(self):
        if self.rule in ("ROT", "ALT", "RESTART", "SPLIT"):
            return self.seq[self.i]
        return super().cur()

    def feed(self, ch):
        if self.rule in ("ROT", "ALT", "RESTART", "SPLIT"):
            self.i += 1
            return
        super().feed(ch)


def _parts(st):
    base = st["base"]
    if base == "H7CT":
        return ("REP", (), st["m"]), ("CT", st["L"])
    if base == "LIB":
        return (st["rule"], tuple(st["rp"]), st["m"]), (("CT", st["L"]) if st["L"] else ("NONE",))
    if base == "PROG":
        return ("REP", (), st["m"]), ("NONE",)
    raise ValueError(base)


def encrypt(pt, st):
    (rule, par, m), sp = _parts(st)
    s, t = OPS[st["op"]]
    pa, ca, ka = ALPH[st["pa"]], ALPH[st["ca"]], ALPH[st["ka"]]
    state, out = State(rule, par, m), []
    for i, p in enumerate(pt):
        if st["base"] == "PROG" and st["where"] == "inner":
            a1 = ALPH[st["A1"]]
            p = a1[(a1.index(p) + st["a"] * i + st["b"]) % 26]
        sl = out[i - sp[1]] if sp[0] == "CT" and i >= sp[1] else None
        K = ka.index(st["key"][state.cur()]) + (ka.index(sl) if sl is not None else 0)
        c = ca[(s * pa.index(p) + t * K) % 26]
        if st["base"] == "PROG" and st["where"] == "outer":
            a1 = ALPH[st["A1"]]
            c = a1[(a1.index(c) + st["a"] * i + st["b"]) % 26]
        out.append(c)
        state.feed(c)
    return "".join(out)


def decrypt(ct, st):
    (rule, par, m), sp = _parts(st)
    s, t = OPS[st["op"]]
    pa, ca, ka = ALPH[st["pa"]], ALPH[st["ca"]], ALPH[st["ka"]]
    state, out = State(rule, par, m), []
    for i, c in enumerate(ct):
        cc = c
        if st["base"] == "PROG" and st["where"] == "outer":
            a1 = ALPH[st["A1"]]
            cc = a1[(a1.index(c) - st["a"] * i - st["b"]) % 26]
        sl = ct[i - sp[1]] if sp[0] == "CT" and i >= sp[1] else None
        K = ka.index(st["key"][state.cur()]) + (ka.index(sl) if sl is not None else 0)
        p = pa[(s * (ca.index(cc) - t * K)) % 26]
        if st["base"] == "PROG" and st["where"] == "inner":
            a1 = ALPH[st["A1"]]
            p = a1[(a1.index(p) - st["a"] * i - st["b"]) % 26]
        out.append(p)
        state.feed(c)
    return "".join(out)


# ------------------------------------------------------------------------------------------------ decode chunks
@lru_cache(maxsize=1)
def bank():
    """0..3 plain tables (A4 order); then PROG inner tables for (pa, A1, a, b), A1 != pa, pa in A4."""
    tabs, index = [np.tile(LET[a], (N, 1)) for a in A4], {}
    i = np.arange(N)[:, None]
    for pa in A4:
        for A1 in A4:
            if A1 == pa:
                continue
            base = IDX[A1][LET[pa]][None, :]
            for a in range(1, 26):
                for b in range(26):
                    index[(pa, A1, a, b)] = len(tabs)
                    tabs.append(LET[A1][(base - a * i - b) % 26])
    return np.stack(tabs).astype(np.uint8), index


REPMAP = F79.REPMAP


def _z(Y, c, ca, ka, op, L):
    s, t = OPS[op]
    S = np.zeros(N, dtype=np.int64)
    if L:
        S[L:] = IDX[ka][c[:-L]]
    return (s * (Y[ca] - t * S)) % 26


def chunks(fam, ct):
    """Yield (Z, R, M, OI, info) for one family; info is decoded by setting(info, row, delta)."""
    c = core.codes(ct).astype(np.int64)
    Y = {a: IDX[a][c] for a in A4}
    mm = np.arange(1, MKEY + 1)
    if fam == "H7CT_A":
        Zs, info = [], []
        for ci, (pa, ca, ka, op) in enumerate(NEWK):
            for L in range(1, 49):
                Zs.append(_z(Y, c, ca, ka, op, L))
                info.append((ci, L))
        Z = np.repeat(np.stack(Zs), MKEY, axis=0)
        M = np.tile(mm, len(Zs))
        OI = np.repeat([A4.index(NEWK[ci][0]) for ci, _ in info], MKEY)
        yield Z, REPMAP[M], M, OI, ("H7CT_A", info)
    elif fam in ("LIB_A", "LIB_G4"):
        if fam == "LIB_A":
            defs = [(r, p, m, r != "REP") for r, p, m, _ in F79.mapdefs()]
            convs = {0: NEW32, **{L: NEWK for L in range(1, 8)}}
        else:
            defs = g4defs()
            convs = {0: CONV32, **{L: CONVK for L in range(1, 8)}}
        R = np.array([slot_any(r, p, m, ct) for r, p, m, _ in defs], dtype=np.uint8)
        M = np.array([m for _, _, m, _ in defs])
        ok = np.array([d[3] for d in defs])
        for L in range(0, 8):
            rows = np.arange(len(defs)) if L == 0 else np.flatnonzero(ok)
            for ci, (pa, ca, ka, op) in enumerate(convs[L]):
                Z = np.tile(_z(Y, c, ca, ka, op, L), (len(rows), 1))
                yield Z, R[rows], M[rows], np.full(len(rows), A4.index(pa)), (fam, L, ci, rows)
    elif fam == "PROG_A":
        _, bidx = bank()
        ab = [(a, b) for a in range(1, 26) for b in range(26)]
        i = np.arange(N)
        for pa, ca, op in PROG_NEW:
            s, _ = OPS[op]
            keys = [(A1, a, b) for A1 in A4 if A1 != pa for a, b in ab]
            M = np.tile(mm, len(keys))
            Z = np.tile((s * Y[ca]) % 26, (len(keys) * MKEY, 1))
            OI = np.repeat([bidx[(pa, A1, a, b)] for A1, a, b in keys], MKEY)
            yield Z, REPMAP[M], M, OI, ("PROG_A", "inner", pa, ca, op, keys)
            keys = [(A1, a, b) for A1 in A4 if A1 != ca for a, b in ab]
            Zs = [(s * IDX[ca][LET[A1][(IDX[A1][c] - a * i - b) % 26]]) % 26 for A1, a, b in keys]
            Z = np.repeat(np.stack(Zs), MKEY, axis=0)
            yield Z, REPMAP[M], M, np.full(len(M), A4.index(pa)), ("PROG_A", "outer", pa, ca, op, keys)
    else:
        raise ValueError(fam)


def setting(info, row, delta):
    fam = info[0]
    if fam == "H7CT_A":
        ci, L = info[1][row // MKEY]
        pa, ca, ka, op = NEWK[ci]
        st = {"fam": fam, "base": "H7CT", "pa": pa, "ca": ca, "ka": ka, "op": op, "L": L, "m": row % MKEY + 1}
    elif fam in ("LIB_A", "LIB_G4"):
        _, L, ci, rows = info
        if fam == "LIB_A":
            conv = (NEW32 if L == 0 else NEWK)[ci]
            r, p, m, _ = F79.mapdefs()[int(rows[row])]
        else:
            conv = (CONV32 if L == 0 else CONVK)[ci]
            r, p, m, _ = g4defs()[int(rows[row])]
        pa, ca, ka, op = conv
        st = {"fam": fam, "base": "LIB", "rule": r, "rp": list(p), "m": m, "L": L, "pa": pa, "ca": ca, "ka": ka,
              "op": op}
    elif fam == "PROG_A":
        _, where, pa, ca, op, keys = info
        A1, a, b = keys[row // MKEY]
        st = {"fam": fam, "base": "PROG", "where": where, "A1": A1, "a": a, "b": b, "m": row % MKEY + 1, "pa": pa,
              "ca": ca, "ka": "AZ", "op": op}
    s, t = OPS[st["op"]]
    u = (-s * t * np.asarray(delta[:st["m"]], dtype=np.int64)) % 26
    st["key"] = "".join(ALPH[st["ka"]][int(v)] for v in u)
    return st


# ------------------------------------------------------------------------------------------------ plants, counts
def random_setting(rng, fam, mlo=2, mhi=10):
    if fam == "H7CT_A":
        pa, ca, ka, op = rng.choice(NEWK)
        st = {"fam": fam, "base": "H7CT", "pa": pa, "ca": ca, "ka": ka, "op": op, "L": rng.randint(1, 48),
              "m": rng.randint(mlo, mhi)}
    elif fam in ("LIB_A", "LIB_G4"):
        if fam == "LIB_A":
            defs = [(r, p, m, True) for r, p, m, ctl in F79.mapdefs() if not ctl and mlo <= m <= mhi]
        else:
            defs = [d for d in g4defs() if mlo <= d[2] <= mhi]
        r, p, m, stream_ok = defs[rng.randrange(len(defs))]
        L = rng.randint(1, 7) if stream_ok and rng.random() < 0.5 else 0
        pool = (NEW32 if L == 0 else NEWK) if fam == "LIB_A" else (CONV32 if L == 0 else CONVK)
        pa, ca, ka, op = rng.choice(pool)
        st = {"fam": fam, "base": "LIB", "rule": r, "rp": list(p), "m": m, "L": L, "pa": pa, "ca": ca, "ka": ka,
              "op": op}
    elif fam == "PROG_A":
        pa, ca, op = rng.choice(PROG_NEW)
        where = rng.choice(("inner", "outer"))
        A1 = rng.choice([a for a in A4 if a != (pa if where == "inner" else ca)])
        st = {"fam": fam, "base": "PROG", "where": where, "A1": A1, "a": rng.randint(1, 25), "b": rng.randint(0, 25),
              "m": rng.randint(mlo, mhi), "pa": pa, "ca": ca, "ka": "AZ", "op": op}
    else:
        raise ValueError(fam)
    st["key"] = "".join(rng.choice(AZ) for _ in range(st["m"]))
    return st


def log10_settings():
    def lsum(ms):
        ms = np.asarray(ms, dtype=float)
        top = ms.max()
        return float(top * np.log10(26) + np.log10(np.sum(26.0 ** (ms - top))))
    m12 = list(range(1, MKEY + 1))
    r79 = [d[2] for d in F79.mapdefs()]
    g4 = g4defs()
    out = {"H7CT_A": lsum(m12 * (len(NEWK) * 48)),
           "LIB_A": lsum(r79 * len(NEW32) + [m for r, _, m, _ in F79.mapdefs() if r != "REP"] * (7 * len(NEWK))),
           "LIB_G4": lsum([d[2] for d in g4] * len(CONV32) + [d[2] for d in g4 if d[3]] * (7 * len(CONVK))),
           "PROG_A": lsum(m12 * (len(PROG_NEW) * 2 * 3 * 650))}
    top = max(out.values())
    out["ALL"] = float(top + np.log10(sum(10 ** (v - top) for v in out.values())))
    return out

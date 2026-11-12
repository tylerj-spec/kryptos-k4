"""R79 families (r78/FABLE_ANALYSIS.md Parts 1-4, r78/FABLE_MASKING.md §B4; no K4 data, no published letters).
One tableau stage: x = IDX[pa][p]; y = IDX[ca][c] = s*x + t*K (mod 26), (s, t) = VIG (1, 1), BEAU (-1, 1),
VARB (1, -1). The key value K at position i is IDX[ka][W[slot(i)]] + S(i): a keyword W of m <= 12 letters read at a
slot, plus an optional known stream S.
  H7CT   slot i mod m; S(i) = IDX[ka][c[i-L]] for i >= L, else 0 (ciphertext feedback), L 1..48.        r77 H7 / r78 §3
  H7TXT  slot i mod m; S(i) = IDX[ka][T[o + d*i]], T the K1-K3 plaintext (first copy of K3) or the K1-K3
         ciphertext (CIA transcription, '?' dropped), every offset, d = +1 or -1.                          r77 H7
  LIB    a state rule gives the slot from the position and the earlier ciphertext (walking key WK, reverse at a
         trigger REV, omit OMIT, numeric interruption IKN, occurrence count CNT, letter class CLS; controls REP,
         HELD, TRIG); S = none or ciphertext feedback lag 1..7.                                       r78 §4.2, M §B4
  PROG   a progressive shift a*i + b on a second alphabet A1, applied to the plaintext first (inner, A1 != pa) or to
         the ciphertext last (outer, A1 != ca), with a keyword stage; S = none.                              M §C1
  H11    the key at i is the plaintext letter at route position p[i] (no keyword); 74,093 routes; the 16
         conventions left open by L167.                                                               r78 Part 1
The decode path (chunks) is vectorised; encrypt()/decrypt() are explicit letter-by-letter implementations used to
build plants and to verify every stored decode."""
import re
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
sys.path.insert(0, str(HERE))
import core  # noqa: E402

N, AZ = core.N, core.AZ
A2, A4 = ("AZ", "KRY"), ("AZ", "KRY", "PAL", "ABS")
OPS = core.OPS
ALPH = core.ALPH
IDX = {k: v.astype(np.int64) for k, v in core.IDX.items()}
LET = {k: v.astype(np.int64) for k, v in core.LET.items()}
FAMS = ("H7CT", "H7TXT", "LIB", "PROG", "H11")
MKEY = 12
CONV24 = [(pa, ca, ka, op) for pa in A2 for ca in A2 for ka in A2 for op in ("VIG", "BEAU", "VARB")]
CONV8 = [(pa, ca, "AZ", op) for pa in A2 for ca in A2 for op in ("VIG", "BEAU")]
H11_CONV = ([(a, a, ca, "VIG") for a in A2 for ca in ("KRY", "ABS")] +
            [(pa, ka, ca, op) for pa, ka in (("AZ", "KRY"), ("KRY", "AZ")) for ca in A2 for op in OPS])
CLASSES = {"AZH": (2, lambda ch: AZ.index(ch) // 13), "KRYH": (2, lambda ch: ALPH["KRY"].index(ch) // 13),
           "AZT": (3, lambda ch: AZ.index(ch) // 9), "KRYT": (3, lambda ch: ALPH["KRY"].index(ch) // 9),
           "INKRY": (2, lambda ch: int(ch in "KRYPTOS")), "INPAL": (2, lambda ch: int(ch in "PALIMPSEST")),
           "INABS": (2, lambda ch: int(ch in "ABSCISSA")), "VOW": (2, lambda ch: int(ch in "AEIOU"))}
TRIGSETS = {**{ch: ch for ch in AZ}, "KRYPTOS": "KRYPTOS", "PALIMPSEST": "PALIMPSEST", "ABSCISSA": "ABSCISSA"}


# ------------------------------------------------------------------------------------------------ fixed inputs
@lru_cache(maxsize=1)
def texts():
    """K1-K3 plaintext as carved, first copy of K3 (769 letters); K1-K3 ciphertext, CIA transcription (768)."""
    t = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if ch.isalpha())
    pt = t[:t.index("SLOWLYDESPARATLY", t.index("SLOWLYDESPARATLY") + 1)]
    src = (ROOT / "archive/2026-10-26_allinone_extras/source_key_extensions/r27_sources.py").read_text()
    raw = "".join(ch for ch in re.search(r"CIA_CIPHER='''(.*?)'''", src, re.S).group(1) if ch in AZ)
    ct = raw[:-N]
    assert len(pt) == 769 and len(ct) == 768, (len(pt), len(ct))     # K1+K2 433 + K3 336; CIA ciphertext 768
    return {"K13PT": pt, "K13CT": ct}


@lru_cache(maxsize=1)
def streams():
    """(names, letters[n, 97]) for every text, direction and offset."""
    names, rows = [], []
    for tn, T in texts().items():
        codes = core.codes(T).astype(np.int64)
        for d in (1, -1):
            for o in (range(len(T) - N + 1) if d == 1 else range(N - 1, len(T))):
                names.append((tn, d, o))
                rows.append(codes[o + d * np.arange(N)])
    return names, np.stack(rows)


@lru_cache(maxsize=1)
def kwords():
    ws = []
    for line in (ROOT / "r75/data/kryptos_words.txt").read_text().splitlines():
        if not line.startswith("#"):
            ws += line.split()
    return ws


def ranking(word):
    order = sorted(range(len(word)), key=lambda k: (word[k], k))
    r = [0] * len(word)
    for rank, k in enumerate(order):
        r[k] = rank + 1
    return r


@lru_cache(maxsize=1)
def mapdefs():
    """Every LIB slot rule (rule, params, m, control)."""
    out = [("REP", (), m, True) for m in range(1, MKEY + 1)]
    out += [("HELD", (h,), m, True) for h in (2, 3, 4) for m in range(2, MKEY + 1)]
    out += [("TRIG", (T,), m, True) for T in AZ for m in range(2, MKEY + 1)]
    out += [("WK", (a, e, d), m, False) for a in A4 for e in (0, 1) for d in (1, -1) for m in range(2, MKEY + 1)]
    out += [("REV", (T,), m, False) for T in TRIGSETS for m in range(2, MKEY + 1)]
    out += [("OMIT", (v,), m, False) for v in ("skip", "shrink") for m in range(2, MKEY + 1)]
    out += [("IKN", (w,), len(w), False) for w in kwords() if 2 <= len(w) <= MKEY]
    out += [("CNT", (), m, False) for m in range(2, MKEY + 1)]
    for g, (nc, _) in CLASSES.items():
        out.append(("CLS", (g, 0), nc, False))
        out += [("CLS", (g, m1), m1 * nc, False) for m1 in range(2, MKEY // nc + 1)]
    return out


def _omit_seq(v, m):
    seq, j = [], 0
    while len(seq) < N:
        seq += [k for k in range(m) if k != j % m] if v == "skip" else list(range(j % m, m))
        j += 1
    return seq[:N]


def _ikn_seq(w):
    dig, seq, j = ranking(w), [], 0
    while len(seq) < N:
        seq += list(range(dig[j % len(dig)]))
        j += 1
    return seq[:N]


def slot_map(rule, par, m, c):
    """Decode path: slot of every position, from the ciphertext string c."""
    if rule == "REP":
        return [i % m for i in range(N)]
    if rule == "HELD":
        return [(i // par[0]) % m for i in range(N)]
    if rule == "OMIT":
        return _omit_seq(par[0], m)
    if rule == "IKN":
        return _ikn_seq(par[0])
    out, ptr, dr = [], 0, 1
    if rule == "TRIG":
        for ch in c:
            out.append(ptr)
            ptr = 0 if ch == par[0] else (ptr + 1) % m
    elif rule == "WK":
        a, e, d = par
        for ch in c:
            out.append(ptr)
            ptr = (ptr + d * (ALPH[a].index(ch) + e)) % m
    elif rule == "REV":
        for ch in c:
            out.append(ptr)
            if ch in TRIGSETS[par[0]]:
                dr = -dr
            ptr = (ptr + dr) % m
    elif rule == "CNT":
        seen = {}
        out.append(0)
        for i in range(1, N):
            seen[c[i - 1]] = seen.get(c[i - 1], 0) + 1
            out.append((seen[c[i - 1]] - 1) % m)
    elif rule == "CLS":
        g, m1 = par
        nc, f = CLASSES[g]
        out = [0] + [((i % m1) * nc if m1 else 0) + f(c[i - 1]) for i in range(1, N)]
    return out


# ------------------------------------------------------------------------------------------------ explicit cipher
class _State:
    """Encryption-side slot rule: cur() before letter i, feed(c_i) after it (independent of slot_map)."""

    def __init__(self, rule, par, m):
        self.rule, self.par, self.m, self.i, self.ptr, self.dr, self.prev, self.seen = rule, par, m, 0, 0, 1, None, {}
        self.seq = _omit_seq(par[0], m) if rule == "OMIT" else _ikn_seq(par[0]) if rule == "IKN" else None

    def cur(self):
        r, i, m = self.rule, self.i, self.m
        if r == "REP":
            return i % m
        if r == "HELD":
            return (i // self.par[0]) % m
        if self.seq is not None:
            return self.seq[i]
        if r in ("TRIG", "WK", "REV"):
            return self.ptr
        if r == "CNT":
            return 0 if i == 0 else (self.seen[self.prev] - 1) % m
        if r == "CLS":
            g, m1 = self.par
            nc, f = CLASSES[g]
            return 0 if i == 0 else ((i % m1) * nc if m1 else 0) + f(self.prev)
        raise ValueError(r)

    def feed(self, ch):
        r, m = self.rule, self.m
        if r == "TRIG":
            self.ptr = 0 if ch == self.par[0] else (self.ptr + 1) % m
        elif r == "WK":
            a, e, d = self.par
            self.ptr = (self.ptr + d * (ALPH[a].index(ch) + e)) % m
        elif r == "REV":
            if ch in TRIGSETS[self.par[0]]:
                self.dr = -self.dr
            self.ptr = (self.ptr + self.dr) % m
        self.seen[ch] = self.seen.get(ch, 0) + 1
        self.prev = ch
        self.i += 1


def _key_parts(st):
    f = st["fam"]
    if f == "H7CT":
        return ("REP", (), st["m"]), ("CT", st["L"])
    if f == "H7TXT":
        return ("REP", (), st["m"]), ("TXT", st["text"], st["d"], st["o"])
    if f == "LIB":
        return (st["rule"], tuple(st["rp"]), st["m"]), (("CT", st["L"]) if st["L"] else ("NONE",))
    if f == "PROG":
        return ("REP", (), st["m"]), ("NONE",)
    raise ValueError(f)


def _stream_letter(sp, i, out_so_far):
    if sp[0] == "CT":
        return out_so_far[i - sp[1]] if i >= sp[1] else None
    if sp[0] == "TXT":
        return texts()[sp[1]][sp[3] + sp[2] * i]
    return None


def encrypt(pt, st):
    A = lambda n: ALPH[n]  # noqa: E731
    if st["fam"] == "H11":
        perm = route_dict()[st["route"]]
        s, t = OPS[st["op"]]
        pa, ka, ca = A(st["pa"]), A(st["ka"]), A(st["ca"])
        return "".join(ca[(s * pa.index(pt[i]) + t * ka.index(pt[perm[i]])) % 26] for i in range(N))
    (rule, par, m), sp = _key_parts(st)
    s, t = OPS[st["op"]]
    pa, ca, ka = A(st["pa"]), A(st["ca"]), A(st.get("ka", "AZ"))
    state, out = _State(rule, par, m), []
    for i, p in enumerate(pt):
        if st["fam"] == "PROG" and st["where"] == "inner":
            a1 = A(st["A1"])
            p = a1[(a1.index(p) + st["a"] * i + st["b"]) % 26]
        sl = _stream_letter(sp, i, out)
        K = ka.index(st["key"][state.cur()]) + (ka.index(sl) if sl is not None else 0)
        c = ca[(s * pa.index(p) + t * K) % 26]
        if st["fam"] == "PROG" and st["where"] == "outer":
            a1 = A(st["A1"])
            c = a1[(a1.index(c) + st["a"] * i + st["b"]) % 26]
        out.append(c)
        state.feed(c)
    return "".join(out)


def decrypt(ct, st):
    """Explicit inverse of encrypt() for the keyword families (not H11)."""
    A = lambda n: ALPH[n]  # noqa: E731
    (rule, par, m), sp = _key_parts(st)
    s, t = OPS[st["op"]]
    pa, ca, ka = A(st["pa"]), A(st["ca"]), A(st.get("ka", "AZ"))
    state, out = _State(rule, par, m), []
    for i, c in enumerate(ct):
        cc = c
        if st["fam"] == "PROG" and st["where"] == "outer":
            a1 = A(st["A1"])
            cc = a1[(a1.index(c) - st["a"] * i - st["b"]) % 26]
        sl = _stream_letter(sp, i, ct)
        K = ka.index(st["key"][state.cur()]) + (ka.index(sl) if sl is not None else 0)
        p = pa[(s * (ca.index(cc) - t * K)) % 26]
        if st["fam"] == "PROG" and st["where"] == "inner":
            a1 = A(st["A1"])
            p = a1[(a1.index(p) - st["a"] * i - st["b"]) % 26]
        out.append(p)
        state.feed(c)
    return "".join(out)


# ------------------------------------------------------------------------------------------------ routes (H11)
@lru_cache(maxsize=1)
def routes():
    """(names, perms[n, 97] uint8): r76 merged route sets + every affine map i -> a*i + b mod 97 not already there."""
    import routes76 as RT
    rs = RT.merged(["sheet36", "rot2", "rot1", "colall", "r61"])
    seen = {p for _, p in rs} | {tuple(range(N))}
    for a in range(1, N):
        for b in range(N):
            p = tuple((a * i + b) % N for i in range(N))
            if p not in seen:
                seen.add(p)
                rs.append((f"aff:{a}x+{b}", p))
    return [n for n, _ in rs], np.array([p for _, p in rs], dtype=np.uint8)


@lru_cache(maxsize=1)
def route_dict():
    names, P = routes()
    return {n: [int(v) for v in P[k]] for k, n in enumerate(names)}


def h11_tables():
    """Per H11 convention: step table (676) and plaintext-index -> letter table (26)."""
    steps, lets = [], []
    for pa, ka, ca, op in H11_CONV:
        s, t = OPS[op]
        st = np.zeros((26, 26), dtype=np.uint8)
        for y in range(26):
            for x in range(26):
                st[y, x] = IDX[pa][LET[ka][(t * (y - s * x)) % 26]]
        steps.append(st.ravel())
        lets.append(LET[pa].astype(np.uint8))
    return np.stack(steps), np.stack(lets)


# ------------------------------------------------------------------------------------------------ decode chunks
@lru_cache(maxsize=1)
def bank():
    """Output tables: 0 = AZ, 1 = KRY (plain), then PROG inner tables for (pa, A1, a, b), A1 != pa."""
    tabs, index = [np.tile(LET[a], (N, 1)) for a in A2], {}
    i = np.arange(N)[:, None]
    for pa in A2:
        for A1 in A4:
            if A1 == pa:
                continue
            base = IDX[A1][LET[pa]][None, :]
            for a in range(1, 26):
                for b in range(26):
                    index[(pa, A1, a, b)] = len(tabs)
                    tabs.append(LET[A1][(base - a * i - b) % 26])
    return np.stack(tabs).astype(np.uint8), index


REPMAP = np.array([[i % m if m else 0 for i in range(N)] for m in range(MKEY + 1)], dtype=np.uint8)


def chunks(fam, ct):
    """Yield (Z, R, M, OI, info) for the keyword families; info is decoded by setting(info, row, delta)."""
    c = core.codes(ct).astype(np.int64)
    Y = {a: IDX[a][c] for a in A4}
    mm = np.arange(1, MKEY + 1)
    if fam == "H7CT":
        Zs, info = [], []
        for ci, (pa, ca, ka, op) in enumerate(CONV24):
            s, t = OPS[op]
            for L in range(1, 49):
                S = np.zeros(N, dtype=np.int64)
                S[L:] = IDX[ka][c[:-L]]
                Zs.append((s * (Y[ca] - t * S)) % 26)
                info.append((ci, L))
        Z = np.repeat(np.stack(Zs), MKEY, axis=0)
        M = np.tile(mm, len(Zs))
        OI = np.repeat([A2.index(CONV24[ci][0]) for ci, _ in info], MKEY)
        yield Z, REPMAP[M], M, OI, ("H7CT", info)
    elif fam == "H7TXT":
        names, SL = streams()
        for ci, (pa, ca, ka, op) in enumerate(CONV24):
            s, t = OPS[op]
            Z = np.repeat((s * (Y[ca][None, :] - t * IDX[ka][SL])) % 26, MKEY, axis=0)
            M = np.tile(mm, len(names))
            yield Z, REPMAP[M], M, np.full(len(M), A2.index(pa)), ("H7TXT", ci)
    elif fam == "LIB":
        defs = mapdefs()
        R = np.array([slot_map(r, p, m, ct) for r, p, m, _ in defs], dtype=np.uint8)
        M = np.array([m for _, _, m, _ in defs])
        nonrep = np.array([r != "REP" for r, _, _, _ in defs])
        for L in range(0, 8):
            for ci, (pa, ca, ka, op) in enumerate(CONV8 if L == 0 else CONV24):
                s, t = OPS[op]
                S = np.zeros(N, dtype=np.int64)
                if L:
                    S[L:] = IDX[ka][c[:-L]]
                rows = np.arange(len(defs)) if L == 0 else np.flatnonzero(nonrep)
                Z = np.tile((s * (Y[ca] - t * S)) % 26, (len(rows), 1))
                yield Z, R[rows], M[rows], np.full(len(rows), A2.index(pa)), ("LIB", L, ci, rows)
    elif fam == "PROG":
        B, bidx = bank()
        abs_ = [(a, b) for a in range(1, 26) for b in range(26)]
        for pa in A2:
            for ca in A2:
                for op in ("VIG", "BEAU"):
                    s, _ = OPS[op]
                    keys = [(A1, a, b) for A1 in A4 if A1 != pa for a, b in abs_]
                    Z = np.tile((s * Y[ca]) % 26, (len(keys) * MKEY, 1))
                    OI = np.repeat([bidx[(pa, A1, a, b)] for A1, a, b in keys], MKEY)
                    M = np.tile(mm, len(keys))
                    yield Z, REPMAP[M], M, OI, ("PROG", "inner", pa, ca, op, keys)
                    keys = [(A1, a, b) for A1 in A4 if A1 != ca for a, b in abs_]
                    i = np.arange(N)
                    Zs = [(s * IDX[ca][LET[A1][(IDX[A1][c] - a * i - b) % 26]]) % 26 for A1, a, b in keys]
                    Z = np.repeat(np.stack(Zs), MKEY, axis=0)
                    yield Z, REPMAP[M], M, np.full(len(M), A2.index(pa)), ("PROG", "outer", pa, ca, op, keys)
    else:
        raise ValueError(fam)


def setting(info, row, delta):
    """The full setting (keyword letters included) of row `row` of a chunk, from the solver's shifts."""
    fam = info[0]
    if fam == "H7CT":
        ci, L = info[1][row // MKEY]
        m = row % MKEY + 1
        pa, ca, ka, op = CONV24[ci]
        st = {"fam": fam, "pa": pa, "ca": ca, "ka": ka, "op": op, "L": L, "m": m}
    elif fam == "H7TXT":
        pa, ca, ka, op = CONV24[info[1]]
        tn, d, o = streams()[0][row // MKEY]
        st = {"fam": fam, "pa": pa, "ca": ca, "ka": ka, "op": op, "text": tn, "d": d, "o": o, "m": row % MKEY + 1}
    elif fam == "LIB":
        _, L, ci, rows = info
        pa, ca, ka, op = (CONV8 if L == 0 else CONV24)[ci]
        r, p, m, ctl = mapdefs()[int(rows[row])]
        st = {"fam": fam, "rule": r, "rp": list(p), "m": m, "L": L, "control": ctl, "pa": pa, "ca": ca, "ka": ka,
              "op": op}
    elif fam == "PROG":
        _, where, pa, ca, op, keys = info
        A1, a, b = keys[row // MKEY]
        st = {"fam": fam, "where": where, "A1": A1, "a": a, "b": b, "m": row % MKEY + 1, "pa": pa, "ca": ca,
              "ka": "AZ", "op": op}
    s, t = OPS[st["op"]]
    u = (-s * t * np.asarray(delta[:st["m"]], dtype=np.int64)) % 26
    st["key"] = "".join(ALPH[st["ka"]][int(v)] for v in u)
    return st


# ------------------------------------------------------------------------------------------------ plants, counts
def random_setting(rng, fam, mlo=2, mhi=10):
    if fam == "H11":
        names = routes()[0]
        pa, ka, ca, op = H11_CONV[rng.randrange(len(H11_CONV))]
        return {"fam": fam, "route": names[rng.randrange(len(names))], "pa": pa, "ka": ka, "ca": ca, "op": op}
    if fam == "LIB":
        defs = [d for d in mapdefs() if not d[3] and mlo <= d[2] <= mhi]
        r, p, m, _ = defs[rng.randrange(len(defs))]
        L = 0 if rng.random() < 0.5 else rng.randint(1, 7)
        pa, ca, ka, op = rng.choice(CONV8 if L == 0 else CONV24)
        st = {"fam": fam, "rule": r, "rp": list(p), "m": m, "L": L, "control": False, "pa": pa, "ca": ca, "ka": ka,
              "op": op}
    else:
        m = rng.randint(mlo, mhi)
        if fam == "PROG":
            pa, ca, op = rng.choice(A2), rng.choice(A2), rng.choice(("VIG", "BEAU"))
            where = rng.choice(("inner", "outer"))
            A1 = rng.choice([a for a in A4 if a != (pa if where == "inner" else ca)])
            st = {"fam": fam, "where": where, "A1": A1, "a": rng.randint(1, 25), "b": rng.randint(0, 25), "m": m,
                  "pa": pa, "ca": ca, "ka": "AZ", "op": op}
        else:
            pa, ca, ka, op = rng.choice(CONV24)
            st = {"fam": fam, "pa": pa, "ca": ca, "ka": ka, "op": op, "m": m}
            if fam == "H7CT":
                st["L"] = rng.randint(1, 48)
            else:
                tn, d, o = rng.choice(streams()[0])
                st.update({"text": tn, "d": d, "o": o})
    st["key"] = "".join(rng.choice(AZ) for _ in range(st["m"]))
    return st


def log10_settings():
    """Theorem K count per family: every setting times 26^(keyword letters)."""
    def lsum(ms):
        ms = np.asarray(ms, dtype=float)
        top = ms.max()
        return float(top * np.log10(26) + np.log10(np.sum(26.0 ** (ms - top))))
    m12 = list(range(1, MKEY + 1))
    out = {"H7CT": lsum(m12 * (24 * 48)), "H7TXT": lsum(m12 * (24 * len(streams()[0])))}
    defs = mapdefs()
    out["LIB"] = lsum([d[2] for d in defs] * 8 + [d[2] for d in defs if d[0] != "REP"] * (7 * 24))
    out["PROG"] = lsum(m12 * (2 * 2 * 2 * 2 * 3 * 650))
    out["H11"] = float(np.log10(len(routes()[0]) * len(H11_CONV)))
    tot = max(out.values())
    out["ALL"] = float(tot + np.log10(sum(10 ** (v - tot) for v in out.values())))
    return out

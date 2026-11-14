"""R83 reference ciphers (synthetic only; no K4 data, no published letters). Explicit letter-by-letter encryptors and
decryptors for the four keyword families that R83 checks, written independently of the check engine
(r83/exact83.py) so the tests can compare the two.

Notation (as r75/sealed/exact.py): a tableau stage on plaintext alphabet pa and ciphertext alphabet ca maps a letter p
to c with  IDX[ca][c] = s*IDX[pa][p] + k  (mod 26), s = +1 (Vigenere-type) or -1 (Beaufort-type), k the numeric key.
A free key letter absorbs the key-numbering alphabet and variant Beaufort, so a one-stage convention is (pa, ca, s):
4 x 4 x 2 = 32.

  LK  linked key (r82/LINKED_KEY_LAYER.md, PR #77 ticket L): ONE keyword in two stages on different tableaux. Stage A
      reads slot i mod m, stage B reads slot (i + d*floor(i/w)) mod m: the keyword is rotated d places after every
      row of w letters. `rot` says which stage is rotated (2: the second, as in PR #77; 1: the first).
        q = LET[ca1][s1*IDX[pa1][p] + x[slot1]]       c = LET[ca2][s2*IDX[pa2][q] + t2*pi[x[slot2]]]
      x = the keyword as stage-one numbers; pi = IDX[ka2] o LET[ka1] renumbers it for stage two (identity when both
      stages number the key letters on the same alphabet).
  PF  keyword plus plaintext autokey (r80 G2; PR #77 B1): k_i = U[i mod m] + f*IDX[beta][p_(i-L)], with a primer of
      L letters standing in for p_(i-L) when i < L.
  WP  walking key stepped by the plaintext (r78 §4.2 WK-P; PR #77 B1-WALK): k_i = U[ptr_i],
      ptr_(i+1) = ptr_i + d*(IDX[alpha][p_i] + e) (mod m), ptr_0 given.
  SL  per-slot progression (r80 G3; PR #77 B2), linear: k_i = A[r] + j*B[r], r = i mod m, j = i div m.
  SS  per-slot progression, the keyword re-enciphering itself on the tableau: key letter of slot r on pass 0 is W[r];
      on pass j+1 it is LET[ca][s*IDX[pa][previous] + IDX[ka][W[r]]]; numeric key k = IDX[ka][key letter]."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
from core import ALPH, AZ  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")


def ix(a, ch):
    return ALPH[a].index(ch)


def enc1(p, k, pa, ca, s):
    return ALPH[ca][(s * ix(pa, p) + k) % 26]


def dec1(c, k, pa, ca, s):
    return ALPH[pa][(s * (ix(ca, c) - k)) % 26]


def key_value(p, c, pa, ca, s):
    """The numeric key that sends p to c in a one-stage convention."""
    return (ix(ca, c) - s * ix(pa, p)) % 26


# ------------------------------------------------------------------------------------------------ LK linked key
def lk_slots(i, m, w, d=1, rot=2):
    """(slot read by stage one, slot read by stage two) at position i."""
    a, b = i % m, (i + d * (i // w)) % m
    return (a, b) if rot == 2 else (b, a)


def lk_pi(ka1, ka2):
    return [ix(ka2, ALPH[ka1][x]) for x in range(26)]


def lk_encrypt(pt, st):
    pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2 = st["conv"]
    x, m, w, d, rot = st["x"], len(st["x"]), st["w"], st.get("d", 1), st.get("rot", 2)
    pi = lk_pi(ka1, ka2)
    out = []
    for i, p in enumerate(pt):
        a, b = lk_slots(i, m, w, d, rot)
        q = enc1(p, x[a], pa1, ca1, s1)
        out.append(enc1(q, t2 * pi[x[b]], pa2, ca2, s2))
    return "".join(out)


def lk_decrypt(ct, st):
    pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2 = st["conv"]
    x, m, w, d, rot = st["x"], len(st["x"]), st["w"], st.get("d", 1), st.get("rot", 2)
    pi = lk_pi(ka1, ka2)
    out = []
    for i, c in enumerate(ct):
        a, b = lk_slots(i, m, w, d, rot)
        q = dec1(c, t2 * pi[x[b]], pa2, ca2, s2)
        out.append(dec1(q, x[a], pa1, ca1, s1))
    return "".join(out)


# ------------------------------------------------------------------------------------------------ PF autokey + keyword
def pf_key(i, st, prev_plain):
    pa, ca, s = st["conv"]
    U, L, beta, f = st["U"], st["L"], st["beta"], st["f"]
    fb = prev_plain[i - L] if i >= L else st["primer"][i]
    return (U[i % len(U)] + f * ix(beta, fb)) % 26


def pf_encrypt(pt, st):
    pa, ca, s = st["conv"]
    return "".join(enc1(p, pf_key(i, st, pt), pa, ca, s) for i, p in enumerate(pt))


def pf_decrypt(ct, st):
    pa, ca, s = st["conv"]
    out = []
    for i, c in enumerate(ct):
        out.append(dec1(c, pf_key(i, st, out), pa, ca, s))
    return "".join(out)


# ------------------------------------------------------------------------------------------------ WP walking key (plaintext)
def wp_encrypt(pt, st):
    pa, ca, s = st["conv"]
    U, alpha, e, d, ptr = st["U"], st["alpha"], st["e"], st["d"], st["ptr0"]
    m, out = len(U), []
    for p in pt:
        out.append(enc1(p, U[ptr], pa, ca, s))
        ptr = (ptr + d * (ix(alpha, p) + e)) % m
    return "".join(out)


def wp_decrypt(ct, st):
    pa, ca, s = st["conv"]
    U, alpha, e, d, ptr = st["U"], st["alpha"], st["e"], st["d"], st["ptr0"]
    m, out = len(U), []
    for c in ct:
        p = dec1(c, U[ptr], pa, ca, s)
        out.append(p)
        ptr = (ptr + d * (ix(alpha, p) + e)) % m
    return "".join(out)


# ------------------------------------------------------------------------------------------------ SL / SS progression
def sl_keys(n, st):
    A, B = st["A"], st["B"]
    m = len(A)
    return [(A[i % m] + (i // m) * B[i % m]) % 26 for i in range(n)]


def ss_keys(n, st):
    pa, ca, ka, s = st["conv"]
    W = st["W"]
    m, cur, out = len(W), list(W), []
    for i in range(n):
        r = i % m
        if i >= m and r == 0:
            cur = [ALPH[ca][(s * ix(pa, cur[q]) + ix(ka, W[q])) % 26] for q in range(m)]
        out.append(ix(ka, cur[r]))
    return out


def prog_encrypt(pt, st):
    ks = sl_keys(len(pt), st) if st["fam"] == "SL" else ss_keys(len(pt), st)
    pa, ca, s = st["conv"][:2] + (st["conv"][-1],)
    return "".join(enc1(p, k, pa, ca, s) for p, k in zip(pt, ks))


def prog_decrypt(ct, st):
    ks = sl_keys(len(ct), st) if st["fam"] == "SL" else ss_keys(len(ct), st)
    pa, ca, s = st["conv"][:2] + (st["conv"][-1],)
    return "".join(dec1(c, k, pa, ca, s) for c, k in zip(ct, ks))


ENC = {"LK": lk_encrypt, "PF": pf_encrypt, "WP": wp_encrypt, "SL": prog_encrypt, "SS": prog_encrypt}
DEC = {"LK": lk_decrypt, "PF": pf_decrypt, "WP": wp_decrypt, "SL": prog_decrypt, "SS": prog_decrypt}


def encrypt(pt, st):
    return ENC[st["fam"]](pt, st)


def decrypt(ct, st):
    return DEC[st["fam"]](ct, st)


def random_setting(rng, fam, m=None, **kw):
    """A random plant of one family (any key letters; the parameters may be fixed through kw)."""
    a4 = lambda: rng.choice(A4)  # noqa: E731
    sg = lambda: rng.choice((1, -1))  # noqa: E731
    m = m or rng.randint(2, 10)
    if fam == "LK":
        st = {"conv": (a4(), a4(), a4(), a4(), sg(), sg(), sg(), a4(), a4()), "x": [rng.randrange(26) for _ in range(m)],
              "w": rng.randint(2, 31), "d": 1, "rot": rng.choice((1, 2))}
    elif fam == "PF":
        L = rng.randint(1, 8)
        st = {"conv": (a4(), a4(), sg()), "U": [rng.randrange(26) for _ in range(m)], "L": L, "beta": a4(), "f": sg(),
              "primer": "".join(rng.choice(AZ) for _ in range(L))}
    elif fam == "WP":
        st = {"conv": (a4(), a4(), sg()), "U": [rng.randrange(26) for _ in range(m)], "alpha": a4(),
              "e": rng.randrange(2), "d": sg(), "ptr0": rng.randrange(m)}
    elif fam == "SL":
        st = {"conv": (a4(), a4(), sg()), "A": [rng.randrange(26) for _ in range(m)],
              "B": [rng.randrange(26) for _ in range(m)]}
    elif fam == "SS":
        st = {"conv": (a4(), a4(), a4(), sg()), "W": "".join(rng.choice(AZ) for _ in range(m))}
    else:
        raise ValueError(fam)
    st["fam"] = fam
    st.update(kw)
    return st

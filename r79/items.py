"""R79 synthetic items (development and the sealed holdout share this; no K4 data).
Positives: 97 letters from a word start in a book, enciphered by r79/families.py's explicit encryptor under a random
setting of one family. Spelling variants:
  POS          ordinary text;
  POS_MISSP    2 random letters changed (Sanborn-like misspellings);
  POS_NONSTD   nonstandard, Germanic-looking spelling of the words before the 97 letters are taken: each rule below
               applies to each eligible word with probability 0.35 (PH->F, CK->K, C->K before A/O/U, W->V,
               initial Y->J, initial TH->D, final ED->T).
Keyword families use keyword lengths 2..10 (the design range); STRETCH plants use 11..12 and are reported only.
Negatives: R71's generators OTP, RUNKEY, HOMOPHONIC, GROMARK (r71/generators.py) unchanged; PERIODIC, CTAK and PTAK
with a RANDOM plaintext alphabet only, so that no negative falls inside an R79 family (the A-Z / KRYPTOS forms of
those generators are R79 members); plus frequency-preserving shuffles of positive ciphertexts."""
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r71"))
sys.path.insert(0, str(HERE))
import core  # noqa: E402
import families as F  # noqa: E402
import generators as G  # noqa: E402

ARMS_PLAIN = ("OTP", "RUNKEY", "HOMOPHONIC", "GROMARK")
ARMS_RANDOM_AP = ("PERIODIC", "CTAK", "PTAK")
RULES = [(re.compile(r"PH"), "F"), (re.compile(r"CK"), "K"), (re.compile(r"C(?=[AOU])"), "K"), (re.compile(r"W"), "V"),
         (re.compile(r"^Y"), "J"), (re.compile(r"^TH"), "D"), (re.compile(r"ED$"), "T")]


def words(path):
    return re.findall(r"[A-Z]+", Path(path).read_text(encoding="utf-8", errors="ignore").upper())


def nonstd(ws, rng, p=0.35):
    out = []
    for w in ws:
        for pat, rep in RULES:
            if pat.search(w) and rng.random() < p:
                w = pat.sub(rep, w)
        out.append(w)
    return out


def passage(ws, rng, kind):
    while True:
        i = rng.randrange(len(ws) - 80)
        win = ws[i:i + 80]
        if kind == "POS_NONSTD":
            win = nonstd(win, rng)
        p = "".join(win)[:core.N]
        if len(p) == core.N:
            break
    if kind == "POS_MISSP":
        q = list(p)
        for k in rng.sample(range(core.N), 2):
            q[k] = rng.choice([c for c in core.AZ if c != q[k]])
        p = "".join(q)
    return p


def positives(book, per_fam, n_missp, n_nonstd, n_stretch, rng):
    """per_fam plants of each family from one book (the first n_missp misspelled, the next n_nonstd nonstandard),
    then n_stretch STRETCH plants (keyword length 11..12) of each keyword family."""
    ws, items = words(book), []
    for fam in F.FAMS:
        for k in range(per_fam):
            kind = "POS_MISSP" if k < n_missp else "POS_NONSTD" if k < n_missp + n_nonstd else "POS"
            p = passage(ws, rng, kind)
            st = F.random_setting(rng, fam)
            items.append({"kind": kind, "fam": fam, "pt": p, "setting": st, "ct": F.encrypt(p, st)})
    for fam in ("H7CT", "H7TXT", "LIB", "PROG"):
        for _ in range(n_stretch):
            p = passage(ws, rng, "POS")
            st = F.random_setting(rng, fam, 11, 12)
            items.append({"kind": "STRETCH", "fam": fam, "pt": p, "setting": st, "ct": F.encrypt(p, st)})
    return items


def _ap_random(rng, P):
    n = len(P)
    inv = np.argsort(rng.random((n, 26)), axis=1).astype(np.int16)
    return np.take_along_axis(inv, P.astype(np.int64), axis=1).astype(np.int16), np.full(n, 2)


def negatives(neg_pt, neg_key, n_per_arm, nrng):
    letters = lambda p: np.frombuffer("".join(words(p)).encode(), dtype=np.uint8).astype(np.int16) - 65  # noqa: E731
    pt, kt = letters(neg_pt), letters(neg_key)
    r61 = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    items = []
    for arm in ARMS_PLAIN + ARMS_RANDOM_AP:
        saved = G.ap_map
        if arm in ARMS_RANDOM_AP:
            G.ap_map = _ap_random
        try:
            C, par = G.gen(arm, nrng, n_per_arm, pt, kt, r61)
        finally:
            G.ap_map = saved
        items += [{"kind": "NEG_" + arm, "param": int(par[i]), "ct": core.text(C[i])} for i in range(n_per_arm)]
    return items


def shuffles(pos_items, n, rng):
    out = []
    for it in rng.sample(pos_items, n):
        c = list(it["ct"])
        rng.shuffle(c)
        out.append({"kind": "NEG_SHUFFLE", "ct": "".join(c)})
    return out

"""R75 fixed-method families. No K4 data, no published letters. Every member is a FIXED decryption: it turns a
97-letter ciphertext into exactly one text.

  F1  two layers, in place, on different tableaux ("LAYER TWO"):  ct = stage2(stage1(pt)), each stage a keyword
      cipher (core.py STAGE) with its own key; the first stage's ciphertext alphabet differs from the second stage's
      plaintext alphabet (ca1 != pa2), otherwise the two keys just add up (already excluded, L03/L36).
        tier A: both keywords in KRYPTOS/PALIMPSEST/ABSCISSA, every phase; pa, ca in AZ/KRY/PAL/ABS; ka in AZ/KRY.
        tier B: both keywords from r75/data/kryptos_words.txt, phase 0; pa, ca, ka in AZ/KRY.
  F2  interrupted key, one stage: the key index normally advances by 1; after a TRIGGER (the plaintext letter, or the
      ciphertext letter, at the position just enciphered equals LETTER) it RESTARTs at 0, STALLs (does not advance) or
      SKIPs (advances by 2).
  F3  held key, one stage: every key letter is used HOLD times in a row (HOLD 2..8): index = ((i + phase) // HOLD).
      F2/F3 tiers: A = sculpture keywords, every phase, pa, ca in the four alphabets, ka in AZ/KRY;
                   B = kryptos_words.txt, phase 0, pa, ca, ka in AZ/KRY.
API: batches(C) yields (P, meta) with P an (n, 97) array of decrypted letter codes; setting(meta, row) -> dict;
encrypt(pt, setting) -> ciphertext (explicit scalar code, independent of batches); random_setting(rng, sub)."""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402
from core import ALPH, IDX, LET, N, OPS  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")
A2 = ("AZ", "KRY")
OPN = ("VIG", "BEAU", "VARB")
ACTIONS = ("RESTART", "STALL", "SKIP")
HOLDS = tuple(range(2, 9))
POSN = np.arange(N)


def kryptos_words():
    ws = []
    for line in (Path(__file__).resolve().parent / "data" / "kryptos_words.txt").read_text().splitlines():
        if not line.startswith("#"):
            ws += line.split()
    assert len(ws) == len(set(ws)) and all(w.isalpha() and w.isupper() for w in ws)
    return ws


def tiers():
    """tier -> (P/C alphabets, key alphabets, [(word, phase)])"""
    a = [(w, ph) for w in core.SCULPTURE_KEYS for ph in range(len(w))]
    b = [(w, 0) for w in kryptos_words()]
    return {"A": (A4, A2, a), "B": (A2, A2, b)}


def word_matrix(labels):
    """W[r, j] = letter code of labels[r].word at index j (padded), L[r] = word length, PH[r] = phase."""
    L = np.array([len(w) for w, _ in labels], dtype=np.int64)
    W = np.zeros((len(labels), int(L.max())), dtype=np.int16)
    for r, (w, _) in enumerate(labels):
        W[r, :len(w)] = core.codes(w)
    return W, L, np.array([ph for _, ph in labels], dtype=np.int64)


def key_rows(labels, ka, index):
    """Key positions K[r, i] = IDX[ka][word_r[index[r, i] mod len_r]]; index (R, 97) int array."""
    W, L, _ = word_matrix(labels)
    return IDX[ka][W[np.arange(len(labels))[:, None], index % L[:, None]]]


# ---------------------------------------------------------------------------------------------------- explicit encryptors
def key_letters_periodic(word, phase):
    return [word[(i + phase) % len(word)] for i in range(N)]


def enc_F1(pt, st):
    mid = pt
    for s in (st["s1"], st["s2"]):
        mid = core.stage_enc_text(mid, key_letters_periodic(s["word"], s["phase"]), s["pa"], s["ca"], s["ka"], s["op"])
    return mid


def enc_F2(pt, st):
    w, j, out = st["word"], st["phase"], []
    for i in range(N):
        c = core.stage_enc_text(pt[i], w[j % len(w)], st["pa"], st["ca"], st["ka"], st["op"])
        out.append(c)
        hit = (pt[i] if st["trigger"] == "P" else c) == st["letter"]
        j = (0 if st["action"] == "RESTART" else j if st["action"] == "STALL" else j + 2) if hit else j + 1
    return "".join(out)


def enc_F3(pt, st):
    w = st["word"]
    keys = [w[((i + st["phase"]) // st["hold"]) % len(w)] for i in range(N)]
    return core.stage_enc_text(pt, keys, st["pa"], st["ca"], st["ka"], st["op"])


def encrypt(pt, st):
    return {"F1": enc_F1, "F2": enc_F2, "F3": enc_F3}[st["family"]](pt, st)


# ---------------------------------------------------------------------------------------------------- enumeration
def batches_F1(C):
    for tier, (pcs, kas, labels) in tiers().items():
        R = len(labels)
        base = POSN[None, :] + np.array([ph for _, ph in labels])[:, None]
        Kmat = {ka: key_rows(labels, ka, base) for ka in kas}
        for pa2, ca2, ka2, op2 in itertools.product(pcs, pcs, kas, OPN):
            M = core.stage_dec(C[None, :], Kmat[ka2], pa2, ca2, op2)                   # (R, 97) middle texts
            for ca1 in pcs:
                if ca1 == pa2:
                    continue
                Y = IDX[ca1][M]                                                        # (R, 97)
                for ka1, op1 in itertools.product(kas, OPN):
                    s, t = OPS[op1]
                    X = (s * (Y[:, None, :] - t * Kmat[ka1][None, :, :])) % 26         # (R2, R1, 97)
                    for pa1 in pcs:
                        yield LET[pa1][X].reshape(R * R, N), ("F1", tier, (pa1, ca1, ka1, op1), (pa2, ca2, ka2, op2), R)


def batches_F2(C):
    for tier, (pcs, kas, labels) in tiers().items():
        R = len(labels)
        W, L, PH = word_matrix(labels)
        rows = np.arange(R)
        # ciphertext trigger: the key index sequence depends on the ciphertext only
        idx_c = {}
        for x in range(26):
            trig = (C == x)
            cum = np.concatenate([[0], np.cumsum(trig)[:-1]])                           # triggers before position i
            last = np.full(N, -1)
            for i in range(1, N):
                last[i] = i - 1 if trig[i - 1] else last[i - 1]
            for act in ACTIONS:
                if act == "RESTART":
                    idx = np.where(last[None, :] >= 0, (POSN - last - 1)[None, :], PH[:, None] + POSN[None, :])
                elif act == "STALL":
                    idx = PH[:, None] + (POSN - cum)[None, :]
                else:
                    idx = PH[:, None] + (POSN + cum)[None, :]
                idx_c[x, act] = idx
        combos = [(x, act) for x in range(26) for act in ACTIONS]
        big_idx = np.concatenate([idx_c[k] for k in combos])                            # (78R, 97)
        Wb, Lb = np.tile(W, (len(combos), 1)), np.tile(L, len(combos))
        nb = np.arange(len(Lb))
        xs = np.repeat(np.array([x for x, _ in combos]), R)
        acts = np.repeat(np.array([ACTIONS.index(a) for _, a in combos]), R)
        for pa, ca, ka, op in itertools.product(pcs, pcs, kas, OPN):
            K = IDX[ka][Wb[nb[:, None], big_idx % Lb[:, None]]]
            yield core.stage_dec(C[None, :], K, pa, ca, op), ("F2", tier, "C", (pa, ca, ka, op), R, combos)
            # plaintext trigger: sequential, because the index depends on the letters already decrypted
            s, t = OPS[op]
            j = np.tile(PH, len(combos))
            P = np.zeros((len(Lb), N), dtype=np.int16)
            y = IDX[ca][C]
            for i in range(N):
                k = IDX[ka][Wb[nb, j % Lb]]
                P[:, i] = LET[pa][(s * (y[i] - t * k)) % 26]
                hit = P[:, i] == xs
                j = np.where(hit, np.where(acts == 0, 0, np.where(acts == 1, j, j + 2)), j + 1)
            yield P, ("F2", tier, "P", (pa, ca, ka, op), R, combos)


def labels_F3(tier, labels):
    out = []
    for w, ph in labels:
        for h in HOLDS:
            for p in (range(h * len(w)) if tier == "A" else (0,)):
                out.append((w, p, h))
    return out


def batches_F3(C):
    for tier, (pcs, kas, labels) in tiers().items():
        if tier == "A":
            labels = [(w, 0) for w in core.SCULPTURE_KEYS]
        lab3 = labels_F3(tier, labels)
        idx = np.array([(POSN + p) // h for _, p, h in lab3])
        for ka in kas:
            K = key_rows([(w, 0) for w, _, _ in lab3], ka, idx)
            for pa, ca, op in itertools.product(pcs, pcs, OPN):
                yield core.stage_dec(C[None, :], K, pa, ca, op), ("F3", tier, (pa, ca, ka, op))


def batches(C):
    yield from batches_F1(C)
    yield from batches_F2(C)
    yield from batches_F3(C)


def setting(meta, row):
    T = tiers()
    if meta[0] == "F1":
        _, tier, c1, c2, R = meta
        labels = T[tier][2]
        r2, r1 = divmod(int(row), R)
        mk = lambda c, lab: {"pa": c[0], "ca": c[1], "ka": c[2], "op": c[3], "word": lab[0], "phase": lab[1]}  # noqa: E731
        return {"family": "F1", "tier": tier, "s1": mk(c1, labels[r1]), "s2": mk(c2, labels[r2])}
    if meta[0] == "F2":
        _, tier, trig, c, R, combos = meta
        labels = T[tier][2]
        k, r = divmod(int(row), R)
        x, act = combos[k]
        return {"family": "F2", "tier": tier, "pa": c[0], "ca": c[1], "ka": c[2], "op": c[3], "word": labels[r][0],
                "phase": labels[r][1], "trigger": trig, "letter": chr(65 + x), "action": act}
    _, tier, c = meta
    labels = T[tier][2] if tier == "B" else [(w, 0) for w in core.SCULPTURE_KEYS]
    w, p, h = labels_F3(tier, labels)[int(row)]
    return {"family": "F3", "tier": tier, "pa": c[0], "ca": c[1], "ka": c[2], "op": c[3], "word": w, "phase": p,
            "hold": h}


def sub(st):
    return st["family"] + st["tier"]


def random_setting(rng, which):
    """which in F1A, F1B, F2A, F2B, F3A, F3B: a setting drawn uniformly from that sub-family."""
    fam, tier = which[:2], which[2]
    pcs, kas, labels = tiers()[tier]

    def stage():
        w, ph = labels[rng.randrange(len(labels))]
        return {"pa": rng.choice(pcs), "ca": rng.choice(pcs), "ka": rng.choice(kas), "op": rng.choice(OPN), "word": w,
                "phase": ph}
    if fam == "F1":
        while True:
            s1, s2 = stage(), stage()
            if s1["ca"] != s2["pa"]:
                return {"family": "F1", "tier": tier, "s1": s1, "s2": s2}
    s = stage()
    if fam == "F2":
        return {"family": "F2", "tier": tier, **s, "trigger": rng.choice("PC"), "letter": rng.choice(core.AZ),
                "action": rng.choice(ACTIONS)}
    h = rng.choice(HOLDS)
    return {"family": "F3", "tier": tier, **s, "phase": rng.randrange(h * len(s["word"])) if tier == "A" else 0,
            "hold": h}


SUBS = ("F1A", "F1B", "F2A", "F2B", "F3A", "F3B")


def count():
    """Number of members per sub-family (arithmetic only)."""
    T = tiers()
    out = {}
    for tier, (pcs, kas, labels) in T.items():
        conv = len(pcs) ** 2 * len(kas) * 3
        unch = (len(pcs) ** 2 * len(kas) * 3) ** 2 * (len(pcs) - 1) // len(pcs)
        out["F1" + tier] = unch * len(labels) ** 2
        out["F2" + tier] = conv * len(labels) * 26 * 3 * 2
        n3 = len(labels_F3(tier, labels if tier == "B" else [(w, 0) for w in core.SCULPTURE_KEYS]))
        out["F3" + tier] = conv * n3
    return out

#!/usr/bin/env python3
"""R75 step 1b (SEALED DIAGNOSIS): which KIND of key do the published letters imply?
r75/sealed/keyshape.py asks whether the implied key has any structure. This file asks which family of key generators
that structure looks like, with the answer calibrated on synthetic ciphers whose family is hidden.
Features: the six keyshape statistics as z-scores against a random key, each maximised over the 8 primary numbering
conventions (so a class is recognised whatever its numbering). Classifier: k nearest neighbours (k = 25) among
synthetic training ciphers of ten classes, every one read at the same 24 positions as K4's published letters:
  RANDOM      key letters independent and uniform (also what a one-time pad looks like);
  RUNKEY      key = English text;                    HELD        each key letter held for 1-4 positions;
  FEWVALUES   key drawn irregularly from 5-8 values; PT_AUTOKEY  key = plaintext letter 1-3 back (+ constant);
  CT_AUTOKEY  key = ciphertext letter 1-3 back;      PROGRESSIVE key = a + b*i, or a short key plus a drift;
  DIGITS      key values 0-9 (Gromark-like);         PERIODIC    random key of period 30-52;
  TWO_LAYER   two stacked keyword stages on different tableaux (periods 10 and 8).
Modes:
  keyclass.py --calibrate PT_BOOK KEY_BOOK MODEL.npz REPORT.json   synthetic only: build the training set, report the
                                                                   held-out confusion matrix (no K4)
  keyclass.py MODEL.npz OUT.json                                   K4: uses the published letters (sealed diagnosis)
Verdict for K4: a structured class holding >= 50% of the 25 neighbours; NO_VISIBLE_STRUCTURE if RANDOM, RUNKEY and
TWO_LAYER together hold >= 50% (calibration shows those three cannot be told apart at 24 positions); else MIXED.
It names a kind of key; it produces no plaintext and feeds no solver."""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r75" / "sealed"))
import core  # noqa: E402
from core import IDX, LET, N  # noqa: E402
import keyshape as KS  # noqa: E402

CLASSES = ("RANDOM", "RUNKEY", "HELD", "FEWVALUES", "PT_AUTOKEY", "CT_AUTOKEY", "PROGRESSIVE", "DIGITS", "PERIODIC",
           "TWO_LAYER")
K_NEIGHBOURS, N_TRAIN, N_TEST, SEED = 25, 1500, 500, 750150
UNSTRUCTURED = ("RANDOM", "RUNKEY", "TWO_LAYER")     # indistinguishable from one another at 24 positions


def call(share):
    """Verdict from the neighbour shares (len(CLASSES),): a structured class with >= 50%, else NO_VISIBLE_STRUCTURE
    if the three unstructured classes together hold >= 50%, else MIXED."""
    best = int(np.argmax(share))
    if share[best] >= 0.5 and CLASSES[best] not in UNSTRUCTURED:
        return CLASSES[best]
    if sum(share[CLASSES.index(c)] for c in UNSTRUCTURED) >= 0.5:
        return "NO_VISIBLE_STRUCTURE"
    return "MIXED"


def encipher(p, K, conv):
    pa, ca, form = conv
    x = IDX[pa][p].astype(np.int64)
    return LET[ca][((x + K) if form == "DIFF" else (K - x)) % 26]


def make(cls, p, keytext, rng):
    """One synthetic ciphertext (codes) of class cls for plaintext codes p (97,)."""
    conv = KS.PRIMARY[rng.randrange(len(KS.PRIMARY))]
    pa, ca, form = conv
    R = lambda n, hi=26: np.array([rng.randrange(hi) for _ in range(n)])  # noqa: E731
    if cls == "RANDOM":
        return encipher(p, R(N), conv)
    if cls == "RUNKEY":
        return encipher(p, IDX[rng.choice(("AZ", "KRY"))][keytext].astype(np.int64), conv)
    if cls == "HELD":
        k = []
        while len(k) < N:
            k += [rng.randrange(26)] * rng.randint(1, 4)
        return encipher(p, np.array(k[:N]), conv)
    if cls == "FEWVALUES":
        vals = rng.sample(range(26), rng.randint(5, 8))
        return encipher(p, np.array([rng.choice(vals) for _ in range(N)]), conv)
    if cls == "PT_AUTOKEY":
        d, const = rng.randint(1, 3), rng.randrange(26)
        K = np.concatenate([R(d), (IDX[pa][p[:-d]].astype(np.int64) + const) % 26])
        return encipher(p, K, conv)
    if cls == "CT_AUTOKEY":
        d, const = rng.randint(1, 3), rng.randrange(26)
        c = np.zeros(N, dtype=np.int64)
        prime = R(d)
        for i in range(N):
            k = int(prime[i]) if i < d else (int(IDX[ca][c[i - d]]) + const) % 26
            x = int(IDX[pa][p[i]])
            c[i] = LET[ca][((x + k) if form == "DIFF" else (k - x)) % 26]
        return c
    if cls == "PROGRESSIVE":
        i = np.arange(N)
        if rng.random() < 0.5:
            return encipher(p, (rng.randrange(26) + rng.randint(1, 25) * i) % 26, conv)
        m = rng.randint(3, 12)
        return encipher(p, (R(m)[i % m] + rng.randint(1, 25) * (i // m)) % 26, conv)
    if cls == "DIGITS":
        return encipher(p, R(N, 10), conv)
    if cls == "PERIODIC":
        m = rng.randint(30, 52)
        return encipher(p, R(m)[np.arange(N) % m], conv)
    if cls == "TWO_LAYER":
        a1, a2 = rng.choice((("AZ", "KRY"), ("KRY", "AZ")))
        i = np.arange(N)
        mid = encipher(p, R(10)[i % 10], (a1, a1, rng.choice(("DIFF", "SUM"))))
        return encipher(mid, R(8)[i % 8], (a2, a2, rng.choice(("DIFF", "SUM"))))
    raise ValueError(cls)


def null_moments(rng_np, draws=100000):
    C = rng_np.integers(0, 26, size=(draws, N)).astype(np.int16)
    PK = np.zeros(len(KS.POS), dtype=np.int16)
    S = np.stack([KS.stats(C, PK, v) for v in KS.PRIMARY], axis=1).astype(np.float64)        # (draws, 8, 6)
    return S.mean(axis=0), S.std(axis=0)


def features(C, PK, mu, sd):
    """C (D, 97), PK (D, 24) -> z-scores (D, 8, 6) and their maxima over conventions (D, 6)."""
    S = np.stack([KS.stats(C, PK, v) for v in KS.PRIMARY], axis=1).astype(np.float64)
    z = (S - mu[None]) / sd[None]
    return z, z.max(axis=1)


def knn(train_x, train_y, x, k=K_NEIGHBOURS):
    d = ((x[:, None, :] - train_x[None, :, :]) ** 2).sum(axis=2)
    nn = np.argsort(d, axis=1)[:, :k]
    share = np.stack([(train_y[nn] == c).mean(axis=1) for c in range(len(CLASSES))], axis=1)
    return share, np.sqrt(np.take_along_axis(d, nn, axis=1)).mean(axis=1)


def calibrate(pt_book, key_book, model_path, report_path):
    rng = random.Random(SEED)
    words = re.findall(r"[A-Z]+", Path(pt_book).read_text(encoding="utf-8", errors="ignore").upper())
    keyl = "".join(re.findall(r"[A-Z]", Path(key_book).read_text(encoding="utf-8", errors="ignore").upper()))
    mu, sd = null_moments(np.random.default_rng(SEED + 1))
    X, Y = [], []
    for ci, cls in enumerate(CLASSES):
        C, PK = [], []
        for _ in range(N_TRAIN + N_TEST):
            i = rng.randrange(len(words) - 60)
            p = core.codes("".join(words[i:i + 60])[:N])
            j = rng.randrange(len(keyl) - N)
            c = make(cls, p, core.codes(keyl[j:j + N]), rng)
            C.append(c)
            PK.append(p[KS.POS])
        _, f = features(np.array(C, dtype=np.int16), np.array(PK, dtype=np.int16), mu, sd)
        X.append(f)
        Y += [ci] * len(f)
        print(cls, "mean features", np.round(f.mean(axis=0), 2), flush=True)
    X, Y = np.concatenate(X), np.array(Y)
    per = N_TRAIN + N_TEST
    tr = np.concatenate([np.arange(c * per, c * per + N_TRAIN) for c in range(len(CLASSES))])
    te = np.concatenate([np.arange(c * per + N_TRAIN, (c + 1) * per) for c in range(len(CLASSES))])
    labels = [c for c in CLASSES if c not in UNSTRUCTURED] + ["NO_VISIBLE_STRUCTURE", "MIXED"]
    conf = np.zeros((len(CLASSES), len(labels)), dtype=int)
    dist = {}
    for s in range(0, len(te), 500):
        idx = te[s:s + 500]
        share, dd = knn(X[tr], Y[tr], X[idx])
        for t, sh, d in zip(Y[idx], share, dd):
            conf[t, labels.index(call(sh))] += 1
            dist.setdefault(int(t), []).append(float(d))
    np.savez_compressed(model_path, train_x=X[tr].astype(np.float32), train_y=Y[tr].astype(np.int16), mu=mu, sd=sd)
    structured = [c for c in CLASSES if c not in UNSTRUCTURED]
    rep = {"classes": CLASSES, "n_train_per_class": N_TRAIN, "n_test_per_class": N_TEST, "k": K_NEIGHBOURS,
           "features": list(KS.STATS), "verdict_labels": labels,
           "confusion_rows_true_cols_verdict": {c: conf[i].tolist() for i, c in enumerate(CLASSES)},
           "structured_recall": {c: conf[CLASSES.index(c), labels.index(c)] / N_TEST for c in structured},
           "unstructured_called_structured": {c: int(conf[CLASSES.index(c), :len(structured)].sum()) / N_TEST
                                              for c in UNSTRUCTURED},
           "neighbour_distance_p95": {CLASSES[c]: float(np.percentile(v, 95)) for c, v in dist.items()},
           "class_mean_features": {c: [round(float(v), 2) for v in X[Y == i].mean(axis=0)]
                                   for i, c in enumerate(CLASSES)},
           "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest()}
    Path(report_path).write_text(json.dumps(rep, indent=1) + "\n")
    print("            " + " ".join(f"{c[:7]:>7s}" for c in labels))
    for i, c in enumerate(CLASSES):
        print(f"{c:11s} " + " ".join(f"{v:7d}" for v in conf[i]))
    print("structured recall", rep["structured_recall"])
    print("unstructured given a structured label", rep["unstructured_called_structured"])


def main():
    if sys.argv[1] == "--calibrate":
        return calibrate(*sys.argv[2:6])
    model, out = np.load(sys.argv[1]), sys.argv[2]
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    import prepare_k4 as PK4  # noqa: E402
    from reveal_k4 import CLUES  # noqa: E402
    raw = PK4.CT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PK4.CT_SHA256:
        raise SystemExit("K4 ciphertext hash mismatch")
    known = {o + i: ch for o, t in CLUES for i, ch in enumerate(t)}
    c = core.codes(raw.decode().strip())
    pk = np.array([ord(known[int(i)]) - 65 for i in KS.POS], dtype=np.int16)
    z, f = features(c[None, :], pk[None, :], model["mu"], model["sd"])
    share, d = knn(model["train_x"].astype(np.float64), model["train_y"], f)
    order = np.argsort(-share[0])
    verdict = call(share[0])
    rep = {"verdict": verdict, "neighbour_share": {CLASSES[int(i)]: float(share[0, i]) for i in order if share[0, i] > 0},
           "mean_neighbour_distance": float(d[0]),
           "features_max_z": dict(zip(KS.STATS, [float(v) for v in f[0]])),
           "convention_of_max": {s: "/".join(KS.PRIMARY[int(z[0, :, si].argmax())]) for si, s in enumerate(KS.STATS)},
           "z_by_convention": {"/".join(v): [round(float(x), 2) for x in z[0, vi]] for vi, v in enumerate(KS.PRIMARY)}}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print("KEY CLASS:", verdict, "| neighbour shares", rep["neighbour_share"])
    print("max z by statistic:", {k: round(v, 2) for k, v in rep["features_max_z"].items()})
    print("at conventions:", rep["convention_of_max"])


if __name__ == "__main__":
    main()

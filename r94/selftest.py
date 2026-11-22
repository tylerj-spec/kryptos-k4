"""Finite mathematical checks only. No development panel or truth is read."""
import itertools
import random

import numpy as np

import reference as R
import structured as S


def run(tables, check=lambda: None):
    rng = random.Random(940001)
    report = {"conditional_assignment_exhaustive": 0,
              "cycle_parameterization": 0, "reference_roundtrip": 0,
              "lm4_scalar_batch": 0, "replacement_objectives": 0}
    for q in (3, 4, 5, 6):
        for _ in range(3):
            check()
            U, V, english = [list(range(q)) for _ in range(3)]
            for p in (U, V, english):
                rng.shuffle(p)
            U, V, english = map(lambda p: np.array(p, dtype=np.int64), (U, V, english))
            a = np.array([rng.randrange(q) for _ in range(13)])
            s1 = np.array([rng.randrange(q) for _ in range(13)])
            delta = np.array([rng.randrange(q) for _ in range(13)])
            arrays = (a, s1, delta, english)
            f = np.log10(np.arange(1, q + 1) / sum(range(1, q + 1)))
            for block in (0, 1):
                mat = S.unigram_matrix(U, V, *arrays, block, f)
                p = S.exact_assignment(mat)
                optimum = sum(mat[i, p[i]] for i in range(q))
                exhaustive = max(sum(mat[i, v] for i, v in enumerate(candidate))
                                 for candidate in itertools.permutations(range(q)))
                assert abs(optimum - exhaustive) < 1e-9
                trial = [U, V]
                trial[block] = p
                assert abs(S.uni_score(*trial, arrays, f) - optimum) < 1e-9
                report["conditional_assignment_exhaustive"] += 1
            W1, W2 = S.inv(U), S.inv(V)
            F, H = S.normalized_cycle(W1, W2)
            assert len({int(S.permutation_power(H, j)[0]) for j in range(q)}) == q
            for delta0 in range(q):
                direct = W2[(W1 + delta0) % q]
                assert np.array_equal(S.permutation_power(H, delta0)[F], direct)
                report["cycle_parameterization"] += 1
    for _ in range(24):
        check()
        label = (rng.choice(R.A4), rng.choice(R.A4), rng.randrange(1, 5), 0,
                 rng.randrange(26), rng.choice((1, -1)), rng.choice((1, -1)))
        label = (*label[:3], rng.randrange(label[2]), *label[4:])
        W1, W2 = list(range(26)), list(range(26))
        rng.shuffle(W1)
        rng.shuffle(W2)
        pt = ''.join(rng.choice(R.AZ) for _ in range(97))
        ct = R.encrypt(pt, W1, W2, *label)
        assert R.decrypt(ct, W1, W2, *label) == pt
        s1, s2 = map(np.array, R.shifts(97, *label[2:]))
        arrays = ((np.array([R.IDX[label[1]][c] for c in ct]) + s2) % 26,
                  s1, (s2 - s1) % 26,
                  np.array([ord(c) - 65 for c in R.ALPH[label[0]]]))
        U, V = S.inv(W1), S.inv(W2)
        x = S.decode(U, V, *arrays)
        assert ''.join(chr(65 + int(t)) for t in x) == pt
        report["reference_roundtrip"] += 1
        scalar = 0.0
        for i in range(len(x)):
            k = min(4, i + 1)
            index = 0
            for ch in x[i-k+1:i+1]:
                index = 26 * index + int(ch)
            scalar += float(tables[k-1][index])
        assert abs(scalar - float(S.lm4_batch(x, tables)[0])) < 1e-9
        report["lm4_scalar_batch"] += 1
        for block in (0, 1):
            replacements = S.replacement_texts(U, V, arrays, block)
            for row, value in ((0, 0), (5, 11), (25, 7)):
                trial = [U.copy(), V.copy()]
                trial[block][row] = value
                assert np.array_equal(S.decode(*trial, *arrays), replacements[26 * row + value])
                report["replacement_objectives"] += 1
            # Every proposed assignment cycle remains a permutation.
            p = np.roll([U, V][block], 3)
            for cyc in S.assignment_cycles([U, V][block], p):
                part = [U, V][block].copy()
                part[cyc] = p[cyc]
                assert sorted(part) == list(range(26))
    return {"status": "PASS", **report}

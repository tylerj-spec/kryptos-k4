"""R94 synthetic-development core. No file reads, truth, or target constants.

U=W1^-1, V=W2^-1; a=C+s2, delta=s2-s1, P=U[V[a]-delta]-s1.
Conditional unigram updates are exact linear assignments. Higher-order
updates use a linearized assignment to propose legal moves; they are not
an exact optimizer of the higher-order objective.
"""
import hashlib
import random

import numpy as np
from scipy.optimize import linear_sum_assignment

EPS = 1e-9
SEED = 940101
STARTS = 8
UNI_SWEEPS = 16
LM_SWEEPS = 24
# Copied, without tuning, from r91/vendor/r82/pairwise_pilot.py.
FREQ = np.array([8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, .15,
                 .77, 4.0, 2.4, 6.7, 7.5, 1.9, .095, 6.0, 6.3, 9.1,
                 2.8, .98, 2.4, .15, 2.0, .074], dtype=np.float64)
LOGF = np.log10(FREQ / FREQ.sum())


def inv(p):
    return np.argsort(np.asarray(p, dtype=np.int64))


def decode(U, V, a, s1, delta, english):
    q = len(U)
    return english[(U[(V[a] - delta) % q] - s1) % q]


def seed_of(rid, ct, label):
    body = f"{SEED}|{rid}|{ct}|{','.join(map(str, label))}"
    return int(hashlib.sha256(body.encode()).hexdigest()[:16], 16)


def starts(rid, ct, label, q=26):
    rng = random.Random(seed_of(rid, ct, label))
    out = []
    for _ in range(STARTS):
        U, V = list(range(q)), list(range(q))
        rng.shuffle(U)
        rng.shuffle(V)
        out.append((np.array(U, dtype=np.int64), np.array(V, dtype=np.int64)))
    return out


def exact_assignment(weights):
    """Maximize sum(weights[row, permutation[row]]) with deterministic library ties."""
    rows, cols = linear_sum_assignment(weights, maximize=True)
    assert np.array_equal(rows, np.arange(len(weights)))
    return cols.astype(np.int64)


def unigram_matrix(U, V, a, s1, delta, english, block, logf=LOGF):
    """Exact additive objective for a whole conditional wiring, including unused contacts."""
    q = len(U)
    matrix = np.zeros((q, q), dtype=np.float64)
    values = np.arange(q)
    if block == 0:
        contact = (V[a] - delta) % q
        scores = logf[english[(values[None, :] - s1[:, None]) % q]]
    else:
        contact = a
        scores = logf[english[(U[(values[None, :] - delta[:, None]) % q]
                              - s1[:, None]) % q]]
    np.add.at(matrix, contact, scores)
    return matrix


def uni_score(U, V, arrays, logf=LOGF):
    return float(logf[decode(U, V, *arrays)].sum(dtype=np.float64))


def alternate_unigram(U, V, arrays, max_sweeps=UNI_SWEEPS,
                      fixed=None, check=lambda: None, logf=LOGF):
    U, V = U.copy(), V.copy()
    current = uni_score(U, V, arrays, logf)
    trace = [current]
    assignments = updates = 0
    for _ in range(max_sweeps):
        changed = False
        for block in (0, 1):
            if fixed == block:
                continue
            check()
            matrix = unigram_matrix(U, V, *arrays, block, logf)
            proposal = exact_assignment(matrix)
            assignments += 1
            trial = [U, V]
            trial[block] = proposal
            score = uni_score(*trial, arrays, logf)
            optimum = float(matrix[np.arange(len(U)), proposal].sum())
            assert abs(score - optimum) < 1e-7
            assert score >= current - 1e-7
            if score > current + EPS:
                U, V = trial
                current = score
                updates += 1
                changed = True
                trace.append(current)
        if not changed:
            break
    return U, V, {"unigram_trace": trace, "assignment_calls": assignments,
                  "accepted_updates": updates}


def lm4_batch(texts, tables):
    """Exact scalar-model convention, vectorized across candidate strings.

    Sum order1 at i0, order2 at i1, order3 at i2, and order4 thereafter.
    Tables hold log10 conditional probabilities in AZ order.
    """
    x = np.asarray(texts, dtype=np.int64)
    if x.ndim == 1:
        x = x[None, :]
    assert x.shape[1] >= 4
    out = tables[0][x[:, 0]].astype(np.float64)
    out += tables[1][x[:, 0] * 26 + x[:, 1]]
    out += tables[2][x[:, 0] * 676 + x[:, 1] * 26 + x[:, 2]]
    indices = ((x[:, :-3] * 26 + x[:, 1:-2]) * 26 + x[:, 2:-1]) * 26 + x[:, 3:]
    out += tables[3][indices].sum(axis=1, dtype=np.float64)
    return out


def replacement_texts(U, V, arrays, block):
    """q^2 one-entry counterfactuals; intermediate maps may repeat values.

    These strings define a surrogate, not legal cipher candidates. Only full
    legal permutations proposed from their scores are considered for output.
    """
    a, s1, delta, english = arrays
    q = len(U)
    base = decode(U, V, *arrays)
    candidates = np.broadcast_to(base, (q, q, len(base))).copy()
    contact = (V[a] - delta) % q if block == 0 else a
    for row in range(q):
        positions = np.flatnonzero(contact == row)
        if not len(positions):
            continue
        values = np.arange(q)[:, None]
        if block == 0:
            repl = english[(values - s1[positions][None, :]) % q]
        else:
            repl = english[(U[(values - delta[positions][None, :]) % q]
                            - s1[positions][None, :]) % q]
        candidates[row][:, positions] = repl
    return candidates.reshape(q * q, len(base))


def assignment_cycles(current, proposed):
    """All nontrivial cycles of the proposed replacement, ordered by least index."""
    link = inv(current)[proposed]
    seen, out = set(), []
    for start in range(len(current)):
        if start in seen:
            continue
        cyc, x = [], start
        while x not in seen:
            seen.add(x)
            cyc.append(x)
            x = int(link[x])
        if len(cyc) > 1:
            out.append(cyc)
    return out


def legal_texts(permutations, U, V, arrays, block):
    a, s1, delta, english = arrays
    q = len(U)
    ps = np.asarray(permutations, dtype=np.int64)
    if block == 0:
        return english[(ps[:, (V[a] - delta) % q] - s1[None, :]) % q]
    return english[(U[(ps[:, a] - delta[None, :]) % q] - s1[None, :]) % q]


def best_lm_move(U, V, arrays, tables, block, current_score):
    """One finite higher-order block move; never labeled an exact LM optimizer."""
    q = len(U)
    current = [U, V][block]
    local_scores = lm4_batch(replacement_texts(U, V, arrays, block), tables)
    weights = local_scores.reshape(q, q) - current_score
    proposed = exact_assignment(weights)
    moves = [proposed]
    for cycle in assignment_cycles(current, proposed):
        partial = current.copy()
        partial[cycle] = proposed[cycle]
        moves.append(partial)
    scores = lm4_batch(legal_texts(moves, U, V, arrays, block), tables)
    best = int(np.argmax(scores))
    evaluated = len(scores) + q * q
    kind = "assignment_or_cycle"
    if float(scores[best]) <= current_score + EPS:
        # Fixed-order best legal transposition fallback, not another random restart.
        moves = []
        for x in range(q):
            for y in range(x + 1, q):
                p = current.copy()
                p[x], p[y] = p[y], p[x]
                moves.append(p)
        scores = lm4_batch(legal_texts(moves, U, V, arrays, block), tables)
        best = int(np.argmax(scores))
        evaluated += len(scores)
        kind = "best_transposition"
    if float(scores[best]) > current_score + EPS:
        return moves[best], float(scores[best]), evaluated, kind
    return current.copy(), current_score, evaluated, "none"


def refine_lm4(U, V, arrays, tables, max_sweeps=LM_SWEEPS,
               fixed=None, check=lambda: None):
    U, V = U.copy(), V.copy()
    current = float(lm4_batch(decode(U, V, *arrays), tables)[0])
    trace = [current]
    counts = {"assignment_or_cycle": 0, "best_transposition": 0,
              "none": 0, "scored_counterfactual_or_legal_texts": 1}
    for _ in range(max_sweeps):
        changed = False
        for block in (0, 1):
            if fixed == block:
                continue
            check()
            p, score, evaluated, kind = best_lm_move(U, V, arrays, tables, block, current)
            counts[kind] += 1
            counts["scored_counterfactual_or_legal_texts"] += evaluated
            if kind != "none":
                if block == 0:
                    U = p
                else:
                    V = p
                current = score
                trace.append(current)
                changed = True
        if not changed:
            break
    assert all(b > a + EPS for a, b in zip(trace, trace[1:]))
    return U, V, {"lm4_trace": trace, **counts}


def normalized_cycle(W1, W2):
    """F=W2 W1; H=W2 T_1 W2^-1. H is one q-cycle, interface gauge removed."""
    q = len(W1)
    W1, W2 = np.asarray(W1), np.asarray(W2)
    return W2[W1], W2[(inv(W2) + 1) % q]


def permutation_power(p, k):
    out = np.arange(len(p))
    for _ in range(k % len(p)):
        out = p[out]
    return out

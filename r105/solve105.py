#!/usr/bin/env python3
"""R105 solver S105 (PREREGISTRATION section 2): two-free-alphabet plaintext autokey, mode "B known, F = A".

    B^-1(C_i) = s1*A^-1(P_i) + s2*A^-1(P_{i-L}) + c   (mod 26); B, L, s1, s2 supplied; A, c, chain starts unknown.

Reduction (R104 E2): x_i = s1*(B^-1(C_i) - c) + sigma*x_{i-L}, sigma = -s1*s2, P_i = A[x_i]. With every chain start set
to 0 at a trial c', the true ranks are x0(c') + sigma^t * o_r (t = i div L, r = i mod L), up to a global relabelling.
Gauge: o_0 = 0 (the relabelling absorbs it; for sigma = -1 the trial c' absorbs the rest, c' = c + 2*s1*o_0).
Synthetic use only."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_Q = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32).reshape(-1)
QI = np.round(_Q.astype(np.float64) * 10000).astype(np.int64)      # integer quadgram scores, units of 1e-4
SCALE = 10000.0
N_STAGE1, K_STAGE2, K_STAGE3 = 4000, 200, 10
QUICK = {"iters": 12000, "chunk": 50}          # stage 3: one batched anneal per candidate
FULL = {"iters": 30000, "restarts": 6}         # stage 4: batched restarts per candidate
T0 = 3.5


def score_rows(P):
    """Integer quadgram score (units of 1e-4 log10) of each row of a (K, n) letter-index array."""
    idx = ((P[:, :-3] * 26 + P[:, 1:-2]) * 26 + P[:, 2:-1]) * 26 + P[:, 3:]
    return QI[idx].sum(axis=1)


def qs(p):
    """Quadgram log10 score of one letter-index sequence (the integer score, rescaled)."""
    return int(score_rows(np.asarray(p, dtype=np.int64)[None, :])[0]) / SCALE


def anneal_batch(X, iters, gen, T0=T0):
    """Swap annealing of K permutations at once, row r scored on X[r] (rank sequences, shape (K, n)). The schedule is
    R104's: linear cooling from T0, Metropolis acceptance. Returns (best integer scores, best perms)."""
    K = X.shape[0]
    rows = np.arange(K)
    M = np.argsort(gen.random((K, 26)), axis=1)
    cur = score_rows(M[rows[:, None], X])
    best, bestM = cur.copy(), M.copy()
    for it in range(iters):
        t = T0 * (1 - it / iters) + 1e-3
        a = gen.integers(0, 26, K)
        b = gen.integers(0, 26, K)
        M2 = M.copy()
        M2[rows, a] = M[rows, b]
        M2[rows, b] = M[rows, a]
        s = score_rows(M2[rows[:, None], X])
        d = (s - cur) / SCALE
        acc = (d >= 0) | (gen.random(K) < np.exp(np.minimum(d, 0) / t))
        M[acc] = M2[acc]
        cur[acc] = s[acc]
        up = cur > best
        best[up] = cur[up]
        bestM[up] = M[up]
    return best, bestM


def chain_ranks(y, L, s1, s2, c, starts):
    """Reduction (a): x_i = s1*(y_i - c) + sigma*x_{i-L}, x_r = starts[r] for r < L."""
    sig = -s1 * s2
    x = np.zeros(len(y), dtype=np.int64)
    for r in range(L):
        x[r] = starts[r] % 26
    for i in range(L, len(y)):
        x[i] = (s1 * (y[i] - c) + sig * x[i - L]) % 26
    return x


def apply_offsets(x0, L, sig, offs):
    """x0 + sigma^t * o_r, with t = i div L and r = i mod L."""
    i = np.arange(len(x0))
    o = np.asarray(offs, dtype=np.int64)[i % L]
    if sig == -1:
        o = np.where((i // L) % 2 == 0, o, -o)
    return (x0 + o) % 26


def subchains(n, L, sig):
    """(chain r, sign, indices): one per chain for sigma = 1; even and odd t separately for sigma = -1."""
    out = []
    for r in range(L):
        idx = np.arange(r, n, L)
        if sig == 1:
            out.append((r, 1, idx))
        else:
            out.append((r, 1, idx[0::2]))
            out.append((r, -1, idx[1::2]))
    return out


def sumsq_grid(x0, L, sig):
    """sum_v n_v^2 of the pooled histogram of apply_offsets(x0, L, sig, (0, o_1, ..., o_{L-1})), for every
    (o_1, ..., o_{L-1}) at once: an array of shape (26,)*(L-1). Exact: sum_j |h_j|^2 + 2 sum_{j<k} C_jk."""
    sc = subchains(len(x0), L, sig)
    H = [np.bincount(x0[idx], minlength=26).astype(np.float64) for _, _, idx in sc]
    tot = np.full((26,) * (L - 1), float(sum(h @ h for h in H)))
    o = np.arange(26)

    def put(tab, axes):
        shape = [1] * (L - 1)
        for a in axes:
            shape[a - 1] = 26
        return tab.reshape(shape)

    for a in range(len(sc)):
        for b in range(a + 1, len(sc)):
            ra, sa, _ = sc[a]
            rb, sb, _ = sc[b]
            C = np.array([float(H[a] @ np.roll(H[b], -d)) for d in range(26)])   # C[d] = sum_u h_a[u] h_b[u+d]
            # the shifted histograms overlap as C[(shift_a - shift_b) mod 26], shift_j = sign_j * o_{r_j}
            if ra == rb:
                tab = 2 * C[((sa - sb) * o) % 26]
                tot = tot + (tab[0] if ra == 0 else put(tab, [ra]))
            else:
                r1, r2 = min(ra, rb), max(ra, rb)
                s_1, s_2 = (sa, sb) if ra < rb else (sb, sa)
                sgn = 1 if ra < rb else -1                        # C is oriented from a to b
                tab = 2 * C[(sgn * (s_1 * o[:, None] - s_2 * o[None, :])) % 26]   # [o_r1, o_r2]
                if r1 == 0:
                    tot = tot + put(tab[0], [r2])
                else:
                    tot = tot + put(tab, [r1, r2])
    return tot


def coincidences(keys):
    _, n = np.unique(keys, return_counts=True)
    return float((n * (n - 1)).sum())


def ngram_stat(x):
    """Substitution-invariant: bigram coincidences + 0.5 * trigram coincidences."""
    return coincidences(x[:-1] * 26 + x[1:]) + 0.5 * coincidences(x[:-2] * 676 + x[1:-1] * 26 + x[2:])


def solve(ct, B, L, s1, s2, rng, trace=None):
    """S105, stages 1-4. Returns dict(score, plaintext, A, c, offsets, grid_size). A[v] is the letter of rank v.
    trace (a dict with key 'z0', the true key in the gauge) receives the stage at which the truth was kept or lost."""
    y = np.array([B.index(ch) for ch in ct])
    sig = -s1 * s2
    X0 = [chain_ranks(y, L, s1, s2, cc, [0] * L) for cc in range(26)]
    G = np.stack([sumsq_grid(X0[cc], L, sig) for cc in range(26)])
    flat = np.argsort(-G.reshape(-1), kind="stable")[:N_STAGE1]
    cands = [tuple(int(v) for v in np.unravel_index(f, G.shape)) for f in flat]
    xs = [apply_offsets(X0[z[0]], L, sig, (0,) + z[1:]) for z in cands]
    ng = np.array([ngram_stat(x) for x in xs])
    g1 = np.array([G[z] for z in cands])
    zsc = lambda v: (v - v.mean()) / (v.std() + 1e-12)  # noqa: E731
    stat2 = zsc(g1) + zsc(ng)                            # stage 2: z(pooled sum of squares) + z(n-gram coincidences)
    s2_order = sorted(range(len(cands)), key=lambda i: -stat2[i])
    stage2 = s2_order[:K_STAGE2]
    gen = np.random.Generator(np.random.PCG64(rng.randrange(2 ** 63)))
    X2 = np.stack([xs[i] for i in stage2])
    q = np.concatenate([anneal_batch(X2[j:j + QUICK["chunk"]], QUICK["iters"], gen)[0]
                        for j in range(0, len(stage2), QUICK["chunk"])])
    quick = sorted(zip(q.tolist(), stage2), key=lambda t: (-t[0], t[1]))
    stage3 = [i for _, i in quick[:K_STAGE3]]
    X3 = np.repeat(np.stack([xs[i] for i in stage3]), FULL["restarts"], axis=0)
    f, fm = anneal_batch(X3, FULL["iters"], gen)
    r = int(np.argmax(f))
    perm, i = fm[r], stage3[r // FULL["restarts"]]
    z = cands[i]
    if trace is not None:
        z0 = tuple(trace["z0"])
        ti = cands.index(z0) if z0 in cands else None
        trace["stage1_rank"] = ti
        trace["stage2_rank"] = None if ti is None else s2_order.index(ti)
        trace["stage3_rank"] = None if ti not in stage2 else [j for _, j in quick].index(ti)
        trace["selected_is_truth"] = z == z0
    return {"score": int(f[r]) / SCALE, "plaintext": "".join(AZ[perm[v]] for v in xs[i]),
            "A": "".join(AZ[perm[v]] for v in range(26)), "c": z[0], "offsets": (0,) + z[1:],
            "grid_size": int(G.size)}


def gauge_truth(A, c, s1, s2, L, pt):
    """The true key in the solver's gauge: (c', o_1 - o_0, ..., o_{L-1} - o_0), with o_r = A^-1(P_r)."""
    o = [A.index(pt[r]) for r in range(L)]
    cg = c if -s1 * s2 == 1 else (c + 2 * s1 * o[0]) % 26
    return (cg,) + tuple((v - o[0]) % 26 for v in o[1:])

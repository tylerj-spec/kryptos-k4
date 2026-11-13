/* R79 solver core (r78/FABLE_ANALYSIS.md §1.8, §2.2; r78/FABLE_MASKING.md §B4). No K4 data, no published letters.
 *
 * slot_batch: SLOTSOLVE. For each setting s: letters L[i] = OUT[s][i][(Z[s][i] + d[R[s][i]]) mod 26], with an unknown
 *   shift d[k] in Z26 for each slot k < M[s] (M <= MMAX). Maximise the quadgram score of L by coordinate ascent
 *   (restart 0 starts from the best single-letter fit of each slot, restarts 1.. from random shifts). Writes the mean
 *   log10 quadgram score and the best shifts.
 * cyc_batch: the H11 cycle solver. For each route p (key at i = plaintext at p[i]) and convention, the step table
 *   gives x[p[i]] = STEP[y[i]][x[i]]. Every cycle of p must close (Theorem 1); its start letters that close are its
 *   options. Coordinate ascent over cycles chooses one option per cycle. Infeasible settings score -1e9.
 * Seeds are derived from (seed, global setting index), so a setting gives the same result in any batch. */
#include <math.h>
#include <stdint.h>
#include <string.h>

#define NMAX 97
#define MMAX 32

static inline uint64_t mix(uint64_t z) {
    z += 0x9E3779B97F4A7C15ULL;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}
static inline uint64_t rnd(uint64_t *s) { *s = mix(*s); return *s; }
static inline float q4(const float *quad, const uint8_t *L, int j) {
    return quad[((L[j] * 26 + L[j + 1]) * 26 + L[j + 2]) * 26 + L[j + 3]];
}
static double full(const float *quad, const uint8_t *L, int n) {
    double s = 0;
    for (int j = 0; j + 3 < n; j++) s += q4(quad, L, j);
    return s;
}

static double slot_one(int n, const uint8_t *z, const uint8_t *r, int m, const uint8_t *out, const float *quad,
                       const float *uni, int restarts, uint64_t rs, uint8_t *best_d) {
    int cnt[MMAX], pos[MMAX][NMAX], qn[MMAX], q[MMAX][NMAX];
    uint8_t L[NMAX], d[MMAX];
    memset(cnt, 0, sizeof cnt);
    for (int i = 0; i < n; i++) { int k = r[i]; pos[k][cnt[k]++] = i; }
    for (int k = 0; k < m; k++) {
        uint8_t mark[NMAX];
        memset(mark, 0, sizeof mark);
        qn[k] = 0;
        for (int a = 0; a < cnt[k]; a++) {
            int p = pos[k][a];
            for (int j = p - 3; j <= p; j++)
                if (j >= 0 && j + 3 < n && !mark[j]) { mark[j] = 1; q[k][qn[k]++] = j; }
        }
    }
    double best = -1e30;
    for (int rr = 0; rr < restarts; rr++) {
        for (int k = 0; k < m; k++) {
            if (rr == 0) {
                double bs = -1e30; int bv = 0;
                for (int v = 0; v < 26; v++) {
                    double s = 0;
                    for (int a = 0; a < cnt[k]; a++) { int p = pos[k][a]; s += uni[out[p * 26 + (z[p] + v) % 26]]; }
                    if (s > bs) { bs = s; bv = v; }
                }
                d[k] = (uint8_t)bv;
            } else d[k] = (uint8_t)(rnd(&rs) % 26);
        }
        for (int i = 0; i < n; i++) L[i] = out[i * 26 + (z[i] + d[r[i]]) % 26];
        double cur = full(quad, L, n);
        for (int sweep = 0; sweep < 40; sweep++) {
            int changed = 0;
            for (int k = 0; k < m; k++) {
                if (!cnt[k]) continue;
                double base = 0;
                for (int b = 0; b < qn[k]; b++) base += q4(quad, L, q[k][b]);
                int bv = d[k]; double bd = 0;
                for (int v = 0; v < 26; v++) {
                    if (v == d[k]) continue;
                    for (int a = 0; a < cnt[k]; a++) { int p = pos[k][a]; L[p] = out[p * 26 + (z[p] + v) % 26]; }
                    double s = 0;
                    for (int b = 0; b < qn[k]; b++) s += q4(quad, L, q[k][b]);
                    if (s - base > bd + 1e-9) { bd = s - base; bv = v; }
                }
                for (int a = 0; a < cnt[k]; a++) { int p = pos[k][a]; L[p] = out[p * 26 + (z[p] + bv) % 26]; }
                if (bv != d[k]) { d[k] = (uint8_t)bv; cur += bd; changed = 1; }
            }
            if (!changed) break;
        }
        if (cur > best) { best = cur; memcpy(best_d, d, m); }
    }
    return best;
}

int slot_batch(int S, int n, const uint8_t *Z, const uint8_t *R, const int32_t *M, const int32_t *OI,
               const uint8_t *BANK, const float *quad, const float *uni, int restarts, uint64_t seed, int64_t base,
               float *score, uint8_t *delta) {
    for (int s = 0; s < S; s++) {
        uint8_t *d = delta + (size_t)s * MMAX;
        memset(d, 0, MMAX);
        double v = slot_one(n, Z + (size_t)s * n, R + (size_t)s * n, M[s], BANK + (size_t)OI[s] * n * 26, quad, uni,
                            restarts, mix(seed ^ (uint64_t)(base + s) * 0xD1B54A32D192ED03ULL), d);
        score[s] = (float)(v / (n - 3));
    }
    return 0;
}

/* ---------------------------------------------------------------------------------------------- H11 cycles */
static int cyc_one(int n, const uint8_t *y, const uint8_t *perm, const uint8_t *step, const uint8_t *let,
                   const float *quad, const float *uni, int restarts, uint64_t rs, uint8_t *text, double *score,
                   double *lcand) {
    uint8_t seen[NMAX], opt[NMAX][26], X[NMAX], L[NMAX], ch[NMAX], bestch[NMAX];
    int cs[NMAX + 1], cl[NMAX], no[NMAX], nc = 0, tot = 0;
    memset(seen, 0, sizeof seen);
    for (int i = 0; i < n; i++)
        if (!seen[i]) {
            cs[nc++] = tot;
            for (int j = i; !seen[j]; j = perm[j]) { seen[j] = 1; cl[tot++] = j; }
        }
    cs[nc] = tot;
    double lc = 0;
    for (int c = 0; c < nc; c++) {
        no[c] = 0;
        for (int x0 = 0; x0 < 26; x0++) {
            int v = x0;
            for (int a = cs[c]; a < cs[c + 1]; a++) v = step[y[cl[a]] * 26 + v];
            if (v == x0) opt[c][no[c]++] = (uint8_t)x0;
        }
        if (!no[c]) return 0;
        lc += log10((double)no[c]);
    }
    *lcand = lc;
#define ASSIGN(c, o)                                                                       \
    do {                                                                                   \
        int v_ = opt[c][o];                                                                \
        for (int a_ = cs[c]; a_ < cs[c + 1]; a_++) { X[cl[a_]] = (uint8_t)v_; L[cl[a_]] = let[v_]; \
            v_ = step[y[cl[a_]] * 26 + v_]; }                                              \
    } while (0)
    double best = -1e30;
    for (int rr = 0; rr < restarts; rr++) {
        for (int c = 0; c < nc; c++) {
            if (rr == 0) {
                double bs = -1e30; int bo = 0;
                for (int o = 0; o < no[c]; o++) {
                    ASSIGN(c, o);
                    double s = 0;
                    for (int a = cs[c]; a < cs[c + 1]; a++) s += uni[L[cl[a]]];
                    if (s > bs) { bs = s; bo = o; }
                }
                ch[c] = (uint8_t)bo;
            } else ch[c] = (uint8_t)(rnd(&rs) % no[c]);
            ASSIGN(c, ch[c]);
        }
        double cur = full(quad, L, n);
        for (int sweep = 0; sweep < 40; sweep++) {
            int changed = 0;
            for (int c = 0; c < nc; c++) {
                if (no[c] < 2) continue;
                int bo = ch[c]; double bs = cur;
                for (int o = 0; o < no[c]; o++) {
                    if (o == ch[c]) continue;
                    ASSIGN(c, o);
                    double s = full(quad, L, n);
                    if (s > bs + 1e-9) { bs = s; bo = o; }
                }
                ASSIGN(c, bo);
                if (bo != ch[c]) { ch[c] = (uint8_t)bo; cur = bs; changed = 1; }
            }
            if (!changed) break;
        }
        if (cur > best) { best = cur; memcpy(bestch, ch, nc); }
    }
    for (int c = 0; c < nc; c++) ASSIGN(c, bestch[c]);
    memcpy(text, L, n);
    *score = best / (n - 3);
    return 1;
#undef ASSIGN
}

int cyc_batch(int nr, int n, const uint8_t *PERMS, int nconv, const uint8_t *Y, const uint8_t *STEP,
              const uint8_t *LET, const float *quad, const float *uni, int restarts, uint64_t seed, int64_t base,
              float *score, float *lcand) {
    uint8_t text[NMAX];
    for (int r = 0; r < nr; r++)
        for (int c = 0; c < nconv; c++) {
            double sc, lc;
            size_t k = (size_t)r * nconv + c;
            int ok = cyc_one(n, Y + (size_t)c * n, PERMS + (size_t)r * n, STEP + (size_t)c * 676, LET + (size_t)c * 26,
                             quad, uni, restarts, mix(seed ^ (uint64_t)(base + (int64_t)k) * 0xD1B54A32D192ED03ULL),
                             text, &sc, &lc);
            score[k] = ok ? (float)sc : -1e9f;
            lcand[k] = ok ? (float)lc : -1.0f;
        }
    return 0;
}

int cyc_text(int n, const uint8_t *y, const uint8_t *perm, const uint8_t *step, const uint8_t *let, const float *quad,
             const float *uni, int restarts, uint64_t seed, int64_t index, uint8_t *text, float *score) {
    double sc, lc;
    int ok = cyc_one(n, y, perm, step, let, quad, uni, restarts,
                     mix(seed ^ (uint64_t)index * 0xD1B54A32D192ED03ULL), text, &sc, &lc);
    *score = ok ? (float)sc : -1e9f;
    return ok;
}

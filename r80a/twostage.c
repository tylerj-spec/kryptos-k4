/* R80a first pass for two keyword stages with one key known (r80/FABLE_IDENTIFIABILITY.md §1.5, Theorem I2).
 * No K4 data, no published letters.
 *
 * Model (r80a/two80.py): stage one  q = CA1[ s1*IDX[PA1][p] + t1*k1(i) ],  stage two  c = CA2[ s2*IDX[PA2][q] + t2*k2(i) ].
 * One stage has a listed key (a word, at phase 0, numbered by alphabet KA, operation (s_list, t_list)); the other has a
 * free key (1..MFREE letters, sign s_free; its numbering and variant Beaufort are absorbed into the free key).
 * With the listed key fixed, the free key separates slot by slot (Theorem I2): letters L[i] = OUT_i[(z[i] + d[i % m]) % 26].
 *   dir 2 (listed key in stage two):  z[i] = H[ s_list*(y[i] - t_list*k(i)) ],  OUT_i[v] = P1[ s_free*v ]
 *   dir 1 (listed key in stage one):  z[i] = y[i],  OUT_i[v] = P1[ s_list*(H[s_free*v] - t_list*k(i)) ]
 * where y[i] = IDX[CA2][c_i], H[v] = IDX[CA1][PA2[v]], P1[x] = letter code of PA1[x], all mod 26.
 * two_scan scores every (word, free length m) for one direction and convention by pass 0: each slot starts at its best
 * single-letter fit (as r79/slotsolve.c restart 0), then `sweeps` coordinate-ascent sweeps on quadgrams (0 = none);
 * the score is the mean log10 quadgram. The full solver (r79/slotsolve.c) then runs on the best settings only. */
#include <stdint.h>
#include <string.h>

#define NMAX 97
#define MMAX 32

static inline int md(int x) { x %= 26; return x < 0 ? x + 26 : x; }
static inline float q4(const float *quad, const uint8_t *L, int j) {
    return quad[((L[j] * 26 + L[j + 1]) * 26 + L[j + 2]) * 26 + L[j + 3]];
}

static double pass0_one(int n, const uint8_t *z, int m, const uint8_t *out, const float *quad, const float *uni,
                        int sweeps, uint8_t *dout) {
    int cnt[MMAX], pos[MMAX][NMAX], qn[MMAX], q[MMAX][NMAX];
    uint8_t L[NMAX], d[MMAX];
    memset(cnt, 0, sizeof cnt);
    for (int i = 0; i < n; i++) { int k = i % m; pos[k][cnt[k]++] = i; }
    for (int k = 0; k < m; k++) {
        double bs = -1e30; int bv = 0;
        for (int v = 0; v < 26; v++) {
            double s = 0;
            for (int a = 0; a < cnt[k]; a++) { int p = pos[k][a]; s += uni[out[p * 26 + (z[p] + v) % 26]]; }
            if (s > bs) { bs = s; bv = v; }
        }
        d[k] = (uint8_t)bv;
    }
    for (int i = 0; i < n; i++) L[i] = out[i * 26 + (z[i] + d[i % m]) % 26];
    double cur = 0;
    for (int j = 0; j + 3 < n; j++) cur += q4(quad, L, j);
    if (sweeps > 0) {
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
        for (int sw = 0; sw < sweeps; sw++) {
            int changed = 0;
            for (int k = 0; k < m; k++) {
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
    }
    if (dout) memcpy(dout, d, m);
    return cur / (n - 3);
}

/* Build z and OUT for one listed key. keys: the key's IDX[KA] values, length lw. */
static void build(int n, const uint8_t *y, int dir, const uint8_t *H, const uint8_t *P1, int s_list, int t_list,
                  int s_free, const uint8_t *key, int lw, uint8_t *z, uint8_t *out) {
    for (int i = 0; i < n; i++) {
        int k = key[i % lw];
        if (dir == 2) {
            z[i] = H[md(s_list * (y[i] - t_list * k))];
            for (int v = 0; v < 26; v++) out[i * 26 + v] = P1[md(s_free * v)];
        } else {
            z[i] = y[i];
            for (int v = 0; v < 26; v++) out[i * 26 + v] = P1[md(s_list * (H[md(s_free * v)] - t_list * k))];
        }
    }
}

int two_build(int n, const uint8_t *y, int dir, const uint8_t *H, const uint8_t *P1, int s_list, int t_list,
              int s_free, const uint8_t *key, int lw, uint8_t *z, uint8_t *out) {
    build(n, y, dir, H, P1, s_list, t_list, s_free, key, lw, z, out);
    return 0;
}

int two_scan(int n, const uint8_t *y, int dir, const uint8_t *H, const uint8_t *P1, int s_list, int t_list, int s_free,
             int W, const uint8_t *keys, const int32_t *off, const int32_t *len, int mfree, const float *quad,
             const float *uni, int sweeps, float *score) {
    uint8_t z[NMAX], out[NMAX * 26], L[NMAX], d[MMAX];
    float U[NMAX][26];
    double S[MMAX][26];
    for (int w = 0; w < W; w++) {
        build(n, y, dir, H, P1, s_list, t_list, s_free, keys + off[w], len[w], z, out);
        if (sweeps > 0) {
            for (int m = 1; m <= mfree; m++)
                score[(size_t)w * mfree + (m - 1)] = (float)pass0_one(n, z, m, out, quad, uni, sweeps, 0);
            continue;
        }
        /* pass 0 for all m at once: the single-letter table U is built once per key (same sums, same order and
         * same tie-breaking as pass0_one, so the result is identical) */
        for (int i = 0; i < n; i++)
            for (int v = 0; v < 26; v++) U[i][v] = uni[out[i * 26 + (z[i] + v) % 26]];
        for (int m = 1; m <= mfree; m++) {
            for (int k = 0; k < m; k++)
                for (int v = 0; v < 26; v++) S[k][v] = 0;
            for (int i = 0; i < n; i++) {
                double *sk = S[i % m];
                for (int v = 0; v < 26; v++) sk[v] += U[i][v];
            }
            for (int k = 0; k < m; k++) {
                double bs = -1e30; int bv = 0;
                for (int v = 0; v < 26; v++) if (S[k][v] > bs) { bs = S[k][v]; bv = v; }
                d[k] = (uint8_t)bv;
            }
            for (int i = 0; i < n; i++) L[i] = out[i * 26 + (z[i] + d[i % m]) % 26];
            double cur = 0;
            for (int j = 0; j + 3 < n; j++) cur += q4(quad, L, j);
            score[(size_t)w * mfree + (m - 1)] = (float)(cur / (n - 3));
        }
    }
    return 0;
}

/* Reference: pass 0 one key at a time through pass0_one (used by the tests to check two_scan). */
int two_scan_ref(int n, const uint8_t *y, int dir, const uint8_t *H, const uint8_t *P1, int s_list, int t_list,
                 int s_free, int W, const uint8_t *keys, const int32_t *off, const int32_t *len, int mfree,
                 const float *quad, const float *uni, float *score) {
    uint8_t z[NMAX], out[NMAX * 26];
    for (int w = 0; w < W; w++) {
        build(n, y, dir, H, P1, s_list, t_list, s_free, keys + off[w], len[w], z, out);
        for (int m = 1; m <= mfree; m++)
            score[(size_t)w * mfree + (m - 1)] = (float)pass0_one(n, z, m, out, quad, uni, 0, 0);
    }
    return 0;
}

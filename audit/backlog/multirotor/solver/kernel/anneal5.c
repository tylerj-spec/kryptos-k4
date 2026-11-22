/* RX2-O development kernel, version 3 (ctypes). Version 1's joint annealer over both inverse wirings (a swap of two
 * entries of V1 or V2, equal probability; linear cooling from t0; greedy polish over every swap of either wiring),
 * with the quadgram objective REPLACED by the R59 letter model truncated at order 5: the score of a decode p is
 *   sum_i log10 P(p_i | p_{i-L} .. p_{i-1}),  L = min(i, 4),
 * read from the model's order-1..5 tables exactly as r75/core.Scorer.lm_score reads them (no starting context).
 * Decode, from the ciphertext alone: m_i = V2[a_i] - s2_i;  p_i = E_in[ V1[(m_i + s1_i) mod 26] - s1_i ],
 * a_i = (E_out-place(c_i) + s2_i) mod 26 precomputed by the caller. No K4 data is known to this code. */
#include <stdint.h>
#include <math.h>
#include <string.h>

#define N 97

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double unif(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static const float *L1, *L2, *L3, *L4, *L5;

static double score(const int *a, const int *s1, const int *s2, const int *ein, const int *v1, const int *v2, int n) {
    int p[N];
    for (int i = 0; i < n; i++) {
        int m = v2[a[i]] - s2[i]; if (m < 0) m += 26;
        int b = m + s1[i]; if (b >= 26) b -= 26;
        int q = v1[b] - s1[i]; if (q < 0) q += 26;
        p[i] = ein[q];
    }
    double t = L1[p[0]];
    if (n > 1) t += L2[p[0] * 26 + p[1]];
    if (n > 2) t += L3[(p[0] * 26 + p[1]) * 26 + p[2]];
    if (n > 3) t += L4[((p[0] * 26 + p[1]) * 26 + p[2]) * 26 + p[3]];
    for (int i = 4; i < n; i++) t += L5[(((p[i - 4] * 26 + p[i - 3]) * 26 + p[i - 2]) * 26 + p[i - 1]) * 26 + p[i]];
    return t;
}

static void shuffle(int *w) {
    for (int i = 0; i < 26; i++) w[i] = i;
    for (int i = 25; i > 0; i--) { int j = rnd() % (i + 1); int t = w[i]; w[i] = w[j]; w[j] = t; }
}

/* s1, s2 in 0..25; lm1..lm5 the order-1..5 tables. Returns the best score; out_sc[restarts], out_v1/out_v2[restarts*26]. */
double anneal5(const int *a, const int *s1, const int *s2, const int *ein, const float *lm1, const float *lm2,
               const float *lm3, const float *lm4, const float *lm5, int n, int restarts, int iters, double t0,
               uint64_t seed, double *out_sc, int *out_v1, int *out_v2) {
    L1 = lm1; L2 = lm2; L3 = lm3; L4 = lm4; L5 = lm5;
    rs = seed ? seed : 88172645463325252ULL;
    double bestsc = -1e300;
    int v1[26], v2[26];
    for (int r = 0; r < restarts; r++) {
        shuffle(v1); shuffle(v2);
        double cur = score(a, s1, s2, ein, v1, v2, n);
        for (int it = 0; it < iters; it++) {
            double T = t0 * (1.0 - (double)it / iters) + 1e-3;
            int *w = (rnd() & 1) ? v1 : v2;
            int x = rnd() % 26, y = rnd() % 26;
            if (x == y) continue;
            int t = w[x]; w[x] = w[y]; w[y] = t;
            double nw = score(a, s1, s2, ein, v1, v2, n);
            if (nw >= cur || unif() < exp((nw - cur) / T)) cur = nw;
            else { t = w[x]; w[x] = w[y]; w[y] = t; }
        }
        int improved = 1;
        while (improved) {
            improved = 0;
            for (int k = 0; k < 2; k++) {
                int *w = k ? v2 : v1;
                for (int x = 0; x < 26; x++) for (int y = x + 1; y < 26; y++) {
                    int t = w[x]; w[x] = w[y]; w[y] = t;
                    double nw = score(a, s1, s2, ein, v1, v2, n);
                    if (nw > cur + 1e-9) { cur = nw; improved = 1; }
                    else { t = w[x]; w[x] = w[y]; w[y] = t; }
                }
            }
        }
        out_sc[r] = cur;
        memcpy(out_v1 + 26 * r, v1, sizeof v1);
        memcpy(out_v2 + 26 * r, v2, sizeof v2);
        if (cur > bestsc) bestsc = cur;
    }
    return bestsc;
}

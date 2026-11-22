/* RX2-O development kernel, version 1 (ctypes). Supplied structure (contact pair, n, r, h, d1, d2): searches the two
 * inverse wirings V1 = W1^-1 and V2 = W2^-1 jointly by simulated annealing (a swap of two entries of V1 or of V2,
 * chosen with equal probability), scored by English quadgrams (log10 table of 26^4 floats); linear cooling from t0,
 * then a greedy polish over every swap of either wiring until none improves. Decode, from the ciphertext alone:
 *   a_i = (E_out-place(c_i) + s2_i) mod 26 (precomputed by the caller);  m_i = V2[a_i] - s2_i;
 *   p_i = E_in[ V1[(m_i + s1_i) mod 26] - s1_i ].
 * Every restart's final score and wirings are returned (restarts x 26 ints each). No K4 data is known to this code. */
#include <stdint.h>
#include <math.h>
#include <string.h>

#define N 97

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double unif(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static double score(const int *a, const int *s1, const int *s2, const int *ein, const int *v1, const int *v2,
                    const float *quad, int n) {
    int p[N];
    for (int i = 0; i < n; i++) {
        int m = v2[a[i]] - s2[i]; if (m < 0) m += 26;
        int b = m + s1[i]; if (b >= 26) b -= 26;
        int q = v1[b] - s1[i]; if (q < 0) q += 26;
        p[i] = ein[q];
    }
    double t = 0;
    for (int i = 0; i + 3 < n; i++) t += quad[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
    return t;
}

static void shuffle(int *w) {
    for (int i = 0; i < 26; i++) w[i] = i;
    for (int i = 25; i > 0; i--) { int j = rnd() % (i + 1); int t = w[i]; w[i] = w[j]; w[j] = t; }
}

/* s1, s2 must be in 0..25. Returns the best score; out_sc[restarts], out_v1/out_v2[restarts * 26]. */
double anneal2(const int *a, const int *s1, const int *s2, const int *ein, const float *quad, int n, int restarts,
               int iters, double t0, uint64_t seed, double *out_sc, int *out_v1, int *out_v2) {
    rs = seed ? seed : 88172645463325252ULL;
    double bestsc = -1e300;
    int v1[26], v2[26];
    for (int r = 0; r < restarts; r++) {
        shuffle(v1); shuffle(v2);
        double cur = score(a, s1, s2, ein, v1, v2, quad, n);
        for (int it = 0; it < iters; it++) {
            double T = t0 * (1.0 - (double)it / iters) + 1e-3;
            int *w = (rnd() & 1) ? v1 : v2;
            int x = rnd() % 26, y = rnd() % 26;
            if (x == y) continue;
            int t = w[x]; w[x] = w[y]; w[y] = t;
            double nw = score(a, s1, s2, ein, v1, v2, quad, n);
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
                    double nw = score(a, s1, s2, ein, v1, v2, quad, n);
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

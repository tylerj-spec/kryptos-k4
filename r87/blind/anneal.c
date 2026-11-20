/* R87 blind wiring search (ctypes kernel). For one RX setting, the decode is p_i = E_in[(Winv[x_i] - s_i) mod 26]
 * where x_i = (E_out^-1(c_i) + s_i) mod 26 is computed from the ciphertext alone. Simulated annealing over the
 * inverse wiring Winv (swaps of two entries), scored by English quadgrams (log10 table of 26^4 floats).
 * No K4 data and no published letters are known to this code. */
#include <stdint.h>
#include <math.h>
#include <string.h>

#define N 97

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double unif(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static double score(const int *x, const int *s, const int *ein, const int *winv, const float *quad, int n) {
    int p[N];
    for (int i = 0; i < n; i++) p[i] = ein[((winv[x[i]] - s[i]) % 26 + 26) % 26];
    double t = 0;
    for (int i = 0; i + 3 < n; i++) t += quad[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
    return t;
}

/* Returns the best score; writes the best inverse wiring to best (26 ints). */
double anneal(const int *x, const int *s, const int *ein, const float *quad, int n, int restarts, int iters,
              double t0, uint64_t seed, int *best) {
    rs = seed ? seed : 88172645463325252ULL;
    double bestsc = -1e300;
    int w[26];
    for (int r = 0; r < restarts; r++) {
        for (int i = 0; i < 26; i++) w[i] = i;
        for (int i = 25; i > 0; i--) { int j = rnd() % (i + 1); int t = w[i]; w[i] = w[j]; w[j] = t; }
        double cur = score(x, s, ein, w, quad, n);
        for (int it = 0; it < iters; it++) {
            double T = t0 * (1.0 - (double)it / iters) + 1e-3;
            int a = rnd() % 26, b = rnd() % 26;
            if (a == b) continue;
            int t = w[a]; w[a] = w[b]; w[b] = t;
            double nw = score(x, s, ein, w, quad, n);
            if (nw >= cur || unif() < exp((nw - cur) / T)) cur = nw;
            else { t = w[a]; w[a] = w[b]; w[b] = t; }
        }
        /* greedy polish: every swap that improves, until none does */
        int improved = 1;
        while (improved) {
            improved = 0;
            for (int a = 0; a < 26; a++) for (int b = a + 1; b < 26; b++) {
                int t = w[a]; w[a] = w[b]; w[b] = t;
                double nw = score(x, s, ein, w, quad, n);
                if (nw > cur + 1e-9) { cur = nw; improved = 1; }
                else { t = w[a]; w[a] = w[b]; w[b] = t; }
            }
        }
        if (cur > bestsc) { bestsc = cur; memcpy(best, w, sizeof w); }
    }
    return bestsc;
}

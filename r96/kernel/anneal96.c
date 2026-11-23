/* R96 kernel (ctypes): one start of conditional annealing over ONE inverse wiring of RX2-O, the other supplied.
 * Objective: R95's fixed order-5 score, sum_i T_k[code(p_{i-k+1..i})], k = min(i+1, 5), float32 tables in float64.
 * Decode: m_i = V[a_i] - s2_i;  p_i = E_in[ U[(m_i + s1_i) mod 26] - s1_i ],  a_i = (C_i + s2_i) mod 26 (caller).
 * mode 0: U searched (V fixed);  mode 1: V searched (U fixed).  No K4 data is known to this code. */
#include <stdint.h>
#include <math.h>
#include <string.h>

#define N 97
static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double unif(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }
static const float *L1, *L2, *L3, *L4, *L5;
static const int *A, *S1, *S2, *EIN;
static int NN;

static double score(const int *U, const int *V) {
    int p[N];
    for (int i = 0; i < NN; i++) {
        int m = V[A[i]] - S2[i]; if (m < 0) m += 26;
        int b = m + S1[i]; if (b >= 26) b -= 26;
        int q = U[b] - S1[i]; if (q < 0) q += 26;
        p[i] = EIN[q];
    }
    double t = L1[p[0]];
    if (NN > 1) t += L2[p[0] * 26 + p[1]];
    if (NN > 2) t += L3[(p[0] * 26 + p[1]) * 26 + p[2]];
    if (NN > 3) t += L4[((p[0] * 26 + p[1]) * 26 + p[2]) * 26 + p[3]];
    for (int i = 4; i < NN; i++) t += L5[(((p[i - 4] * 26 + p[i - 3]) * 26 + p[i - 2]) * 26 + p[i - 1]) * 26 + p[i]];
    return t;
}

void setup(const int *a, const int *s1, const int *s2, const int *ein, const float *l1, const float *l2,
           const float *l3, const float *l4, const float *l5, int n) {
    A = a; S1 = s1; S2 = s2; EIN = ein; L1 = l1; L2 = l2; L3 = l3; L4 = l4; L5 = l5; NN = n;
}

double score_pair(const int *U, const int *V) { return score(U, V); }

#define SC() (mode ? score(fixed, w) : score(w, fixed))

static double anneal(int *w, const int *fixed, int mode, int iters, double t0, int cycles, double cur) {
    for (int it = 0; it < iters; it++) {
        double T = t0 * (1.0 - (double)it / iters) + 1e-3;
        int x = rnd() % 26, y = rnd() % 26;
        if (cycles && (rnd() & 1)) {                     /* 3-cycle x -> y -> z -> x on the entries */
            int z = rnd() % 26;
            if (x == y || y == z || x == z) continue;
            int t = w[x]; w[x] = w[z]; w[z] = w[y]; w[y] = t;
            double nw = SC();
            if (nw >= cur || unif() < exp((nw - cur) / T)) cur = nw;
            else { t = w[y]; w[y] = w[z]; w[z] = w[x]; w[x] = t; }
        } else {
            if (x == y) continue;
            int t = w[x]; w[x] = w[y]; w[y] = t;
            double nw = SC();
            if (nw >= cur || unif() < exp((nw - cur) / T)) cur = nw;
            else { t = w[x]; w[x] = w[y]; w[y] = t; }
        }
    }
    return cur;
}

static double polish(int *w, const int *fixed, int mode, double cur) {
    int improved = 1;
    while (improved) {
        improved = 0;
        for (int x = 0; x < 26; x++) for (int y = x + 1; y < 26; y++) {
            int t = w[x]; w[x] = w[y]; w[y] = t;
            double nw = SC();
            if (nw > cur + 1e-9) { cur = nw; improved = 1; }
            else { t = w[x]; w[x] = w[y]; w[y] = t; }
        }
    }
    return cur;
}

/* Version 1: random start from the seed, anneal I from t0, polish. Writes the searched wiring to w. */
double run_v1(const int *fixed, int mode, int iters, double t0, uint64_t seed, int *w) {
    rs = seed ? seed : 88172645463325252ULL;
    for (int i = 0; i < 26; i++) w[i] = i;
    for (int i = 25; i > 0; i--) { int j = rnd() % (i + 1); int t = w[i]; w[i] = w[j]; w[j] = t; }
    double cur = SC();
    cur = anneal(w, fixed, mode, iters, t0, 0, cur);
    return polish(w, fixed, mode, cur);
}

/* Version 2: start = given (assignment) or random; phase 1 I/2 from t_first; 3 rounds of 3-swap perturbation of the
 * best, anneal I/6 from t0/4, polish, keep if better. Swaps and 3-cycles half each. */
double run_v2(const int *fixed, int mode, int iters, double t0, double t_first, uint64_t seed, const int *start, int *w) {
    rs = seed ? seed : 88172645463325252ULL;
    if (start) memcpy(w, start, 26 * sizeof(int));
    else {
        for (int i = 0; i < 26; i++) w[i] = i;
        for (int i = 25; i > 0; i--) { int j = rnd() % (i + 1); int t = w[i]; w[i] = w[j]; w[j] = t; }
    }
    double cur = SC();
    cur = anneal(w, fixed, mode, iters / 2, t_first, 1, cur);
    cur = polish(w, fixed, mode, cur);
    int best[26]; double bs = cur; memcpy(best, w, sizeof best);
    for (int round = 0; round < 3; round++) {
        memcpy(w, best, sizeof best);
        for (int k = 0; k < 3; k++) {
            int x, y;
            do { x = rnd() % 26; y = rnd() % 26; } while (x == y);
            int t = w[x]; w[x] = w[y]; w[y] = t;
        }
        cur = SC();
        cur = anneal(w, fixed, mode, iters / 6, t0 / 4, 1, cur);
        cur = polish(w, fixed, mode, cur);
        if (cur > bs) { bs = cur; memcpy(best, w, sizeof best); }
    }
    memcpy(w, best, sizeof best);
    return bs;
}

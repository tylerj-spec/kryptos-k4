/* R93 independent review (Claude Code): partial-bijection checker for the position-only single rotor.
 * Written from r93/PREREGISTRATION.md's model text; imports and shares nothing with R93's checker.
 * Formulation: a setting is compatible with observations {(x_k, y_k)} iff some permutation W has W[x_k] = y_k for all
 * k, iff the relation is a partial bijection. Each single omission j is RE-CHECKED FROM SCRATCH (no conflict graph).
 * Offsets are computed by COUNTING STEP EVENTS: the rotor moves by d at every position k >= 1 with (k + r) % n == 0.
 * Outputs are flags and counts only: no wiring, plaintext or feasible-label list leaves this code. */
#include <string.h>

#define MAXQ 32
#define MAXM 64

/* 1 iff the pairs (x_k, y_k), k != skip, form a partial bijection on contacts 0..MAXQ-1. */
static int pbij(const int *x, const int *y, int m, int skip) {
    int fx[MAXQ], fy[MAXQ];
    for (int c = 0; c < MAXQ; c++) { fx[c] = -1; fy[c] = -1; }
    for (int k = 0; k < m; k++) {
        if (k == skip) continue;
        int a = x[k], b = y[k];
        if (fx[a] < 0 && fy[b] < 0) { fx[a] = b; fy[b] = a; }
        else if (fx[a] != b || fy[b] != a) return 0;
    }
    return 1;
}

/* out[0] = EXACT flag; out[1 + j] = flag for omitting observation j. Returns the number of feasible omissions. */
int check_pairs(const int *x, const int *y, int m, int *out) {
    int n = 0;
    out[0] = pbij(x, y, m, -1);
    for (int j = 0; j < m; j++) { out[1 + j] = pbij(x, y, m, j); n += out[1 + j]; }
    return n;
}

/* Step-event offsets s[i] mod 26 for i = 0..len-1. */
static void offsets(int n, int r, int d, int len, int *s) {
    int t = 0;
    s[0] = 0;
    for (int k = 1; k < len; k++) {
        if ((k + r) % n == 0) t += d;
        s[k] = ((t % 26) + 26) % 26;
    }
}

/* One label: pin[k] = E_in-place of the observed plaintext letter, cout[k] = E_out-place of the ciphertext letter at
 * position pos[k]. Fills out[0..m] as check_pairs. */
int check_label(const int *pin, const int *cout, const int *pos, int m, int n, int r, int d, int *out) {
    int s[128], x[MAXM], y[MAXM];
    offsets(n, r, d, 97, s);
    for (int k = 0; k < m; k++) { x[k] = (pin[k] + s[pos[k]]) % 26; y[k] = (cout[k] + s[pos[k]]) % 26; }
    return check_pairs(x, y, m, out);
}

/* Full registered scan of one input. pin4[a*m + k], cout4[b*m + k] for the four alphabets (AZ, KRY, PAL, ABS).
 * Label order: (a, b) in 16 pairs, n = nlo..nhi, r = 1..n-1, d = +1 then -1.
 * counts[0] labels, [1] EXACT-feasible labels, [2] labels with some feasible omission, [3] label/omission pairs. */
void scan(const int *pin4, const int *cout4, const int *pos, int m, int nlo, int nhi, long long *counts) {
    int s[128], x[MAXM], y[MAXM], out[MAXM + 1];
    long long L = 0, E = 0, D = 0, P = 0;
    for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++)
        for (int n = nlo; n <= nhi; n++) for (int r = 1; r < n; r++) for (int sd = 0; sd < 2; sd++) {
            int d = sd ? -1 : 1;
            offsets(n, r, d, 97, s);
            for (int k = 0; k < m; k++) {
                x[k] = (pin4[a * m + k] + s[pos[k]]) % 26;
                y[k] = (cout4[b * m + k] + s[pos[k]]) % 26;
            }
            int nd = check_pairs(x, y, m, out);
            L++; E += out[0]; D += (nd > 0 || out[0]); P += nd;
        }
    counts[0] = L; counts[1] = E; counts[2] = D; counts[3] = P;
}

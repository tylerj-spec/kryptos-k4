/* T6 item 3 (audit/NEXT_STEPS.md): independent exact check for R40 (L134) and R42 (L136), "one free alphabet".
 * POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY. Written from the definitions in r40/PREREGISTRATION.md and
 * r42/PREREGISTRATION.md, not from r40/sealed/whole_family.cpp or r42/sealed/whole_family.cpp. Nothing is decrypted.
 *
 * Mode PA (R40): cipher alphabet CA fixed (7 choices), plaintext alphabet FREE.
 *   value y_i = CA^-1(c_i) - k_i  (op 0, "VIG|BEAU")   or   CA^-1(c_i) + k_i  (op 1, "VARB")   (mod 26)
 *   Some plaintext alphabet fits iff the relation  plaintext letter p_i <-> y_i  is a partial bijection.
 * Mode CA (R42): plaintext alphabet PA fixed (7), cipher alphabet FREE.
 *   value z_i = PA^-1(p_i) + k_i  (op 0, "VIG")   or   PA^-1(p_i) - k_i  (op 1, "BEAU|VARB")
 *   Some cipher alphabet fits iff  ciphertext letter c_i <-> z_i  is a partial bijection.
 * V = number of position pairs that violate the bijection: (same value, different letter) + (same letter, different
 * value). V = 0 <=> consistent. Counted by letter/value tallies; with ONEFREE_SELFCHECK set, every 997th setting is
 * re-counted by brute force over all pairs and any mismatch aborts.
 *
 * Keys: chain addition k_i = (k_{i-b} + k_{i-b+1}) mod base from every primer of length b (R40: base 10 b 5, 6, 7 and
 * base 26 b 5; R42: base 10 b 5, 6, 7); running keys from a text (CARTER, K1K3), forward or reversed, numbered AZ or
 * KRY, every offset.
 * Usage: onefree MODE(PA|CA) CT97 LETTERS97('?' = unchecked) CARTER.txt K1K3.txt OUT.tsv
 * Output: settings, consistent count, min V, every setting at min V (up to 5000), histogram of V. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define N 97
static const char *ALNAME[7] = {"AZ", "KRY", "PALP", "ABSP", "ACAKRY", "ACAPAL", "ACAABS"};
static const char *ALPH[7] = {"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALIMSETBCDFGHJKNOQRUVWXYZ",
                              "ABSCIDEFGHJKLMNOPQRTUVWXYZ", "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACOZEJWIFRLDQMGUPBNYSHVTKX",
                              "ADJOUZBEKPVCGMRXIHNTYSFLQW"};
static int inv[7][26];               /* inv[a][letter] = place of letter in alphabet a */
static int npos, pos[N], lab[N];     /* checked positions and the letter (0..25) that must be bijective there */
static int base_val[7][N];           /* CA^-1(c) (mode PA) or PA^-1(p) (mode CA) at each checked position */
static int mode;                     /* 0 = PA free (R40), 1 = CA free (R42) */
static long long hist[N * N], total, minV = 1LL << 60, nmin;
static char minset[5000][96];
static FILE *outf;
static int selfcheck;
static long long nself;

static char *readtext(const char *path, int *len) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(1); }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    char *raw = malloc(n + 1), *s = malloc(n + 1);
    if (fread(raw, 1, n, f) != (size_t)n) { perror("read"); exit(1); }
    fclose(f);
    int k = 0;
    for (long i = 0; i < n; i++) if (isalpha((unsigned char)raw[i])) s[k++] = toupper((unsigned char)raw[i]);
    s[k] = 0; *len = k; free(raw);
    return s;
}

static void test(const int *key, const char *label) {
    for (int a = 0; a < 7; a++) for (int op = 0; op < 2; op++) {
        int val[N];
        for (int j = 0; j < npos; j++) {
            int k = key[pos[j]], v;
            if (mode == 0) v = op == 0 ? base_val[a][j] - k : base_val[a][j] + k;
            else           v = op == 0 ? base_val[a][j] + k : base_val[a][j] - k;
            val[j] = ((v % 26) + 26) % 26;
        }
        /* V = pairs(same value) + pairs(same letter) - 2 * pairs(same value and same letter) */
        int cv[26] = {0}, cl[26] = {0}, cb[26][26];
        memset(cb, 0, sizeof cb);
        long long sv = 0, sl = 0, sb = 0;
        for (int j = 0; j < npos; j++) {
            sv += cv[val[j]]++; sl += cl[lab[j]]++; sb += cb[lab[j]][val[j]]++;
        }
        long long V = sv + sl - 2 * sb;
        if (selfcheck && (total % 997) == 0) {            /* brute-force pair count on a sample */
            long long W = 0;
            for (int x = 0; x < npos; x++) for (int y = x + 1; y < npos; y++)
                W += (val[x] == val[y]) != (lab[x] == lab[y]);
            if (W != V) { fprintf(stderr, "SELFCHECK FAIL %s %lld %lld\n", label, V, W); exit(2); }
            nself++;
        }
        hist[V]++; total++;
        if (V < minV) { minV = V; nmin = 0; }
        if (V == minV) {
            if (nmin < 5000) snprintf(minset[nmin], 96, "%s|%s=%s|OP=%s", label, mode == 0 ? "CA" : "PA", ALNAME[a],
                                     mode == 0 ? (op == 0 ? "VIG|BEAU" : "VARB") : (op == 0 ? "VIG" : "BEAU|VARB"));
            nmin++;
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 7) { fprintf(stderr, "usage: onefree PA|CA CT97 LETTERS97 CARTER K1K3 OUT\n"); return 1; }
    mode = strcmp(argv[1], "CA") == 0;
    selfcheck = getenv("ONEFREE_SELFCHECK") != NULL;
    const char *ct = argv[2], *want = argv[3];
    if (strlen(ct) != N || strlen(want) != N) { fprintf(stderr, "need 97 letters\n"); return 1; }
    for (int a = 0; a < 7; a++) for (int i = 0; i < 26; i++) inv[a][ALPH[a][i] - 'A'] = i;
    npos = 0;
    for (int i = 0; i < N; i++) if (want[i] != '?') {
        pos[npos] = i;
        lab[npos] = mode == 0 ? want[i] - 'A' : ct[i] - 'A';          /* the letter that must be bijective */
        for (int a = 0; a < 7; a++) base_val[a][npos] = mode == 0 ? inv[a][ct[i] - 'A'] : inv[a][want[i] - 'A'];
        npos++;
    }
    int key[N];
    char label[96];
    const char *SYM = "0123456789ABCDEFGHIJKLMNOP";
    int fams[4][2] = {{10, 5}, {10, 6}, {10, 7}, {26, 5}};
    int nf = mode == 0 ? 4 : 3;
    for (int f = 0; f < nf; f++) {
        int base = fams[f][0], b = fams[f][1];
        if (b < 1 || b > 15) { fprintf(stderr, "bad lag\n"); return 1; }
        long long lim = 1;
        for (int i = 0; i < b; i++) lim *= base;
        for (long long p = 0; p < lim; p++) {
            long long v = p;
            char pr[16];
            for (int i = b - 1; i >= 0; i--) { key[i] = (int)(v % base); pr[i] = SYM[key[i]]; v /= base; }
            pr[b] = 0;
            for (int i = b; i < N; i++) key[i] = (key[i - b] + key[i - b + 1]) % base;
            snprintf(label, sizeof label, "C%db%d/primer%s", base, b, pr);
            test(key, label);
        }
    }
    const char *names[2] = {"CARTER", "K1K3"};
    for (int t = 0; t < 2; t++) {
        int len;
        char *s = readtext(argv[4 + t], &len);
        char *r = malloc(len + 1);
        for (int i = 0; i < len; i++) r[i] = s[len - 1 - i];
        r[len] = 0;
        for (int d = 0; d < 2; d++) for (int num = 0; num < 2; num++) {
            const char *txt = d ? r : s;
            for (int off = 0; off + N <= len; off++) {
                for (int i = 0; i < N; i++) key[i] = inv[num][txt[off + i] - 'A'];
                snprintf(label, sizeof label, "%s/%s/%s/off%d", names[t], d ? "rev" : "fwd", num ? "KRY" : "AZ", off);
                test(key, label);
            }
        }
        free(s); free(r);
    }
    outf = fopen(argv[6], "w");
    fprintf(outf, "settings\t%lld\nconsistent\t%lld\nmin_V\t%lld\nn_min\t%lld\n", total, hist[0], minV, nmin);
    for (long long i = 0; i < nmin && i < 5000; i++) fprintf(outf, "min_setting\t%s\n", minset[i]);
    for (int v = 0; v < N * N; v++) if (hist[v]) fprintf(outf, "V\t%d\t%lld\n", v, hist[v]);
    fclose(outf);
    fprintf(stderr, "settings %lld consistent %lld minV %lld n_min %lld selfchecked %lld\n", total, hist[0], minV, nmin,
            nself);
    return 0;
}

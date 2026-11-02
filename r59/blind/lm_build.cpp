// R59 BLIND: generic English letter n-gram model (orders 1..K, K <= 6), interpolated Kneser-Ney. No K4 data.
// Usage: lm_build TRAIN.txt OUT.bin [K=6] [HELDOUT.txt]
// Output: 8-byte header "R59LM" + K (uint8) + 2 pad bytes, then float32 log10 P(w | previous k-1 letters) for
// k = 1..K, concatenated (26 + 26^2 + ... + 26^K floats). Table k is indexed by the k-letter code, base 26,
// oldest letter most significant. HELDOUT (optional) reports bits/letter on text not used for training.
#include <bits/stdc++.h>
using namespace std;
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: lm_build TRAIN.txt OUT.bin [K] [HELDOUT]\n"); return 1; }
    int K = argc > 3 ? atoi(argv[3]) : 6; if (K < 2 || K > 6) { fprintf(stderr, "K must be 2..6\n"); return 1; }
    vector<uint8_t> t; { ifstream f(argv[1]); char c; while (f.get(c)) if (c >= 'A' && c <= 'Z') t.push_back(c - 'A'); }
    size_t pw[8]; pw[0] = 1; for (int k = 1; k <= 7; k++) pw[k] = pw[k - 1] * 26;
    vector<vector<uint32_t>> cnt(K + 1);
    for (int k = 1; k <= K; k++) cnt[k].assign(pw[k], 0);
    for (size_t i = 0; i < t.size(); i++) {
        size_t code = 0;
        for (int k = 1; k <= K && i + k <= t.size(); k++) { code = code * 26 + t[i + k - 1]; cnt[k][code]++; }
    }
    // continuation counts: cc[k][x] = number of distinct letters a with cnt[k+1][a x] > 0  (k < K)
    vector<vector<uint32_t>> cc(K);
    for (int k = 1; k < K; k++) {
        cc[k].assign(pw[k], 0);
        for (size_t code = 0; code < pw[k + 1]; code++) if (cnt[k + 1][code] > 0) cc[k][code % pw[k]]++;
    }
    vector<vector<float>> P(K + 1);
    { double s = 0; for (int w = 0; w < 26; w++) s += cc[1][w]; P[1].assign(26, 0); for (int w = 0; w < 26; w++) P[1][w] = (cc[1][w] + 0.5) / (s + 13); }
    for (int k = 2; k <= K; k++) {
        const vector<uint32_t> &C = (k == K) ? cnt[k] : cc[k];
        double n1 = 0, n2 = 0; for (uint32_t v : C) { if (v == 1) n1++; else if (v == 2) n2++; }
        double D = (n1 + 2 * n2 > 0) ? n1 / (n1 + 2 * n2) : 0.75;
        P[k].assign(pw[k], 0);
        for (size_t h = 0; h < pw[k - 1]; h++) {
            double tot = 0, nz = 0;
            for (int w = 0; w < 26; w++) { double v = C[h * 26 + w]; tot += v; if (v > 0) nz++; }
            size_t hlow = h % pw[k - 2];
            for (int w = 0; w < 26; w++) {
                double lower = P[k - 1][hlow * 26 + w];
                P[k][h * 26 + w] = (float)(tot > 0 ? max(C[h * 26 + w] - D, 0.0) / tot + D * nz / tot * lower : lower);
            }
        }
        fprintf(stderr, "order %d: D = %.3f\n", k, D);
    }
    for (int k = 1; k <= K; k++) { if (k < K) vector<uint32_t>().swap(cc[k]); vector<uint32_t>().swap(cnt[k]); }
    ofstream o(argv[2], ios::binary);
    char hdr[8] = {'R', '5', '9', 'L', 'M', (char)K, 0, 0}; o.write(hdr, 8);
    for (int k = 1; k <= K; k++) for (float p : P[k]) { float lp = log10f(p); o.write((char *)&lp, 4); }
    auto bits = [&](const vector<uint8_t> &s) {
        double z = 0; size_t n = 0;
        for (size_t i = 0; i < s.size(); i++) { int L = min<size_t>(i, K - 1); size_t c = 0; for (int j = L; j >= 0; j--) c = c * 26 + s[i - j]; z += log2(P[L + 1][c]); n++; }
        return -z / n; };
    fprintf(stderr, "letters %zu; order %d\n", t.size(), K);
    if (argc > 4) { vector<uint8_t> h; ifstream f(argv[4]); char c; while (f.get(c)) if (c >= 'A' && c <= 'Z') h.push_back(c - 'A');
        fprintf(stderr, "held-out %s: %.4f bits/letter over %zu letters\n", argv[4], bits(h), h.size()); }
}

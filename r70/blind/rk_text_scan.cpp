// R70 BLIND scanner: running key taken from a NAMED source text, every offset. No K4 clues, masks or positions.
// One ciphertext per call. Rows = carved order (ID, in place) + the 10 frozen R61 routes x 2 models (21 rows, as R68):
//   M1 (substitute, then transpose): Y = path-order text, Y[perm[j]] = CT[j]; P[t] = D(Y[t], key[o + t]); P in path
//      order (the R61/R64/R68 plaintext order).
//   M2 (position-aligned, key along the path): P[j] = D(CT[j], key[o + perm[j]]); P in carved order.
// Conventions (6, tableau alphabet A used for plaintext, ciphertext AND key letter): A in {AZ, KRYPTOS},
//   x = A^-1(p), y = A^-1(c), k = A^-1(key letter):  VIG y = x + k,  BEAU y = k - x,  VARB y = x - k   (mod 26).
// Offsets: o = 0 .. len(source) - 97, key read forward.
// Stage A: order-4 slice of the R59 English letter model on P; exact top TOPA kept (partial-sum abandon is admissible
//   because every log-probability is <= 0). Stage B: the TOPA rescored with the full order-6 model + 1 x the R59 word
//   score (total, as R68); the best TOPOUT by total are written, best first.
// Usage: rk_text_scan LM WORDS ROUTES CIPHERTEXT OUT.jsonl THREADS TOPA TOPOUT NAME1=SRC1 [NAME2=SRC2 ...]
#include <bits/stdc++.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;
static const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
struct Node { int nx[26]; float lp; float best; };
static const float *LM[7]; static int KO = 6;
static vector<Node> TRIE, RTRIE;
static void add_word(vector<Node> &T, const string &w, float ex) {
    int u = 0; T[0].best = max(T[0].best, ex);
    for (char ch : w) { int c = ch - 'A';
        if (T[u].nx[c] < 0) { T[u].nx[c] = T.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; nd.best = -1e30f; T.push_back(nd); }
        u = T[u].nx[c]; T[u].best = max(T[u].best, ex); }
    T[u].lp = max(T[u].lp, ex);
}
static void load(const char *lmpath, const char *wpath) {   // identical to R68 keyed_solve.cpp
    int fd = open(lmpath, O_RDONLY); if (fd < 0) throw runtime_error("lm open");
    off_t len = lseek(fd, 0, SEEK_END); void *mp = mmap(nullptr, len, PROT_READ, MAP_SHARED, fd, 0); if (mp == MAP_FAILED) throw runtime_error("mmap");
    const char *b = (const char *)mp; if (memcmp(b, "R59LM", 5) != 0) throw runtime_error("lm header");
    KO = b[5]; const float *q = (const float *)(b + 8); size_t sz = 26, tot = 0;
    for (int k = 1; k <= KO; k++) { LM[k] = q; q += sz; tot += sz; sz *= 26; }
    if ((size_t)len != 8 + tot * 4) throw runtime_error("lm size");
    for (auto *T : {&TRIE, &RTRIE}) { T->assign(1, Node{}); memset((*T)[0].nx, -1, sizeof (*T)[0].nx); (*T)[0].lp = -1e30f; (*T)[0].best = -1e30f; }
    ifstream f(wpath); string w; double ex, ed;
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        bool ok = true; for (char ch : w) if (ch < 'A' || ch > 'Z') { ok = false; break; }
        if (!ok) continue;
        add_word(TRIE, w, (float)ex); string r(w.rbegin(), w.rend()); add_word(RTRIE, r, (float)ex);
    }
}
static double wordscore(const string &s) {   // identical to R59/R63/R68
    int n = s.size(); vector<double> dp(n + 1, -1e30); dp[0] = 0;
    for (int j = 1; j <= min(n, 12); j++) { int v = 0; for (int q = j - 1; q >= 0; q--) { v = RTRIE[v].nx[s[q] - 'A']; if (v < 0) break; }
        if (v >= 0 && RTRIE[v].best > -1e29) dp[j] = max(dp[j], (double)RTRIE[v].best); }
    for (int i = 0; i < n; i++) {
        if (dp[i] < -1e29) continue;
        dp[i + 1] = max(dp[i + 1], dp[i] - 7);
        int u = 0;
        for (int j = i; j < n && j < i + 24; j++) { u = TRIE[u].nx[s[j] - 'A']; if (u < 0) break; if (TRIE[u].lp > -1e29) dp[j + 1] = max(dp[j + 1], dp[i] + TRIE[u].lp); }
    }
    double best = dp[n];
    for (int i = max(0, n - 12); i < n; i++) { if (dp[i] < -1e29) continue; int u = 0;
        for (int j = i; j < n && u >= 0; j++) u = TRIE[u].nx[s[j] - 'A'];
        if (u >= 0 && TRIE[u].best > -1e29) best = max(best, dp[i] + TRIE[u].best); }
    return best;
}
static double lm_order(const string &s, int ord) {
    double z = 0;
    for (int i = 0; i < (int)s.size(); i++) { int L = min(i, ord - 1); uint32_t c = 0; for (int j = i - L; j < i; j++) c = c * 26 + (s[j] - 'A');
        z += LM[L + 1][c * 26 + (s[i] - 'A')]; }
    return z;
}
static const int N = 97;
struct Row { string path, model; vector<int> cp, idx; };      // cipher letter (AZ index) and key index per P position
struct Cand { float s4; int src, off, row, conv; bool operator<(const Cand &o) const { return s4 > o.s4; } };  // min-heap by s4
static unsigned char DEC[6][26][26];   // DEC[conv][c][keyletter] -> plaintext letter (AZ index)
static const char *CNAME[6] = {"AZ_VIG", "AZ_BEAU", "AZ_VARB", "KRY_VIG", "KRY_BEAU", "KRY_VARB"};

int main(int argc, char **argv) {
  try {
    if (argc < 10) throw runtime_error("usage: rk_text_scan LM WORDS ROUTES CT OUT THREADS TOPA TOPOUT NAME=SRC...");
    string ct = argv[4]; if ((int)ct.size() != N) throw runtime_error("ciphertext length");
    for (char c : ct) if (c < 'A' || c > 'Z') throw runtime_error("ciphertext letters");
    int TH = atoi(argv[6]), TOPA = atoi(argv[7]), TOPOUT = atoi(argv[8]);
    load(argv[1], argv[2]);
    for (int cv = 0; cv < 6; cv++) {
        const string &A = cv < 3 ? AZ : KRY; int op = cv % 3; int inv[26]; for (int t = 0; t < 26; t++) inv[A[t] - 'A'] = t;
        for (int c = 0; c < 26; c++) for (int kl = 0; kl < 26; kl++) {
            int y = inv[c], k = inv[kl]; int x = op == 0 ? y - k : op == 1 ? k - y : y + k; x = ((x % 26) + 26) % 26;
            DEC[cv][c][kl] = A[x] - 'A'; }
    }
    vector<string> names; vector<string> srcs;
    for (int a = 9; a < argc; a++) { string s = argv[a]; auto e = s.find('='); if (e == string::npos) throw runtime_error("NAME=SRC");
        names.push_back(s.substr(0, e)); ifstream f(s.substr(e + 1)); string t; getline(f, t);
        for (char c : t) if (c < 'A' || c > 'Z') throw runtime_error("source letters " + names.back());
        if ((int)t.size() < N) throw runtime_error("source too short"); srcs.push_back(t); }
    vector<Row> rows;
    { Row r; r.path = "ID"; r.model = "M1"; for (int j = 0; j < N; j++) { r.cp.push_back(ct[j] - 'A'); r.idx.push_back(j); } rows.push_back(r); }
    ifstream rf(argv[3]); string line;
    while (getline(rf, line)) { if (line.empty()) continue; stringstream ss(line); string name, order, ps; ss >> name >> order >> ps;
        if (order != "S_then_T") throw runtime_error("route order"); vector<int> perm; stringstream s2(ps); string x; while (getline(s2, x, ',')) perm.push_back(stoi(x));
        if ((int)perm.size() != N) throw runtime_error("route length");
        Row m1; m1.path = name; m1.model = "M1"; m1.cp.assign(N, 0); m1.idx.resize(N);
        for (int j = 0; j < N; j++) m1.cp[perm[j]] = ct[j] - 'A';
        for (int t = 0; t < N; t++) m1.idx[t] = t;
        Row m2; m2.path = name; m2.model = "M2"; for (int j = 0; j < N; j++) { m2.cp.push_back(ct[j] - 'A'); m2.idx.push_back(perm[j]); }
        rows.push_back(m1); rows.push_back(m2); }
    if (rows.size() != 21) throw runtime_error("expected 21 rows");
    vector<vector<unsigned char>> isrc; for (auto &t : srcs) { vector<unsigned char> v(t.size()); for (size_t i = 0; i < t.size(); i++) v[i] = t[i] - 'A'; isrc.push_back(v); }
    vector<array<int, 3>> tasks; for (int s = 0; s < (int)srcs.size(); s++) for (int r = 0; r < 21; r++) for (int cv = 0; cv < 6; cv++) tasks.push_back({s, r, cv});
    atomic<size_t> next(0); vector<vector<Cand>> heaps(TH); atomic<uint64_t> evaluated(0);
    const float *L1 = LM[1], *L2 = LM[2], *L3 = LM[3], *L4 = LM[4];
    auto worker = [&](int tid) {
        auto &H = heaps[tid]; uint64_t ev = 0; unsigned char P[N]; int cp[N], ix[N];
        for (;;) { size_t ti = next++; if (ti >= tasks.size()) break;
            int s = tasks[ti][0], r = tasks[ti][1], cv = tasks[ti][2]; const vector<unsigned char> &src = isrc[s]; const Row &rw = rows[r];
            auto &D = DEC[cv]; int nof = (int)src.size() - N + 1;
            for (int i = 0; i < N; i++) { cp[i] = rw.cp[i]; ix[i] = rw.idx[i]; }
            for (int o = 0; o < nof; o++) {
                const unsigned char *key = src.data() + o;
                float thr = (int)H.size() >= TOPA ? H.front().s4 : -1e30f;
                float z = 0; bool dead = false;
                for (int i = 0; i < N; i++) {
                    P[i] = D[cp[i]][key[ix[i]]];
                    if (i >= 3) z += L4[((P[i - 3] * 26 + P[i - 2]) * 26 + P[i - 1]) * 26 + P[i]];
                    else if (i == 2) z += L3[(P[0] * 26 + P[1]) * 26 + P[2]];
                    else if (i == 1) z += L2[P[0] * 26 + P[1]];
                    else z += L1[P[0]];
                    if ((i & 3) == 3 && z < thr) { dead = true; break; }
                }
                ev++;
                if (dead || z < thr) continue;
                Cand c{z, s, o, r, cv};
                if ((int)H.size() < TOPA) { H.push_back(c); push_heap(H.begin(), H.end()); }
                else { pop_heap(H.begin(), H.end()); H.back() = c; push_heap(H.begin(), H.end()); }
            }
        }
        evaluated += ev;
    };
    vector<thread> ths; for (int t = 0; t < TH; t++) ths.emplace_back(worker, t); for (auto &t : ths) t.join();
    vector<Cand> all; for (auto &h : heaps) all.insert(all.end(), h.begin(), h.end());
    sort(all.begin(), all.end(), [](const Cand &a, const Cand &b) { return a.s4 != b.s4 ? a.s4 > b.s4 : tie(a.src, a.off, a.row, a.conv) < tie(b.src, b.off, b.row, b.conv); });
    if ((int)all.size() > TOPA) all.resize(TOPA);
    struct Out { Cand c; string P, K; double lm6, w, tot; };
    vector<Out> outs;
    for (auto &c : all) { const Row &rw = rows[c.row]; const string &src = srcs[c.src]; string P(N, 'A');
        for (int i = 0; i < N; i++) P[i] = 'A' + DEC[c.conv][rw.cp[i]][src[c.off + rw.idx[i]] - 'A'];
        Out o{c, P, src.substr(c.off, N), lm_order(P, 6), wordscore(P), 0}; o.tot = o.lm6 + o.w; outs.push_back(o); }
    sort(outs.begin(), outs.end(), [](const Out &a, const Out &b) { return a.tot != b.tot ? a.tot > b.tot : a.c.s4 > b.c.s4; });
    ofstream out(argv[5]); char buf[512];
    for (int i = 0; i < (int)outs.size() && i < TOPOUT; i++) { auto &o = outs[i]; const Row &rw = rows[o.c.row];
        snprintf(buf, sizeof buf, "{\"rank\":%d,\"source\":\"%s\",\"offset\":%d,\"path\":\"%s\",\"model\":\"%s\",\"convention\":\"%s\",\"s4\":%.4f,\"lm6\":%.4f,\"word\":%.4f,\"total\":%.4f,",
                 i, names[o.c.src].c_str(), o.c.off, rw.path.c_str(), rw.model.c_str(), CNAME[o.c.conv], o.c.s4, o.lm6, o.w, o.tot);
        out << buf << "\"plaintext\":\"" << o.P << "\",\"keytext\":\"" << o.K << "\"}\n"; }
    fprintf(stderr, "evaluated %llu candidates over %zu tasks\n", (unsigned long long)evaluated.load(), tasks.size());
  } catch (exception &e) { fprintf(stderr, "error: %s\n", e.what()); return 1; }
  return 0;
}

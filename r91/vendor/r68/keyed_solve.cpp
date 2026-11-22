// R68 BLIND solver: classic keyed ciphers whose key advances along a path. No K4 clues, masks or positions.
// Each input row gives Y (the ciphertext letters in PATH order, 97) and R (P[j] = Q[R[j]]: how the path-order
// plaintext Q is laid out in plaintext order P; "I" = identity). The runner builds rows for both R68 models.
// Conventions (12): plaintext alphabet Ap, ciphertext alphabet Ac in {AZ, KRY}, op in {VIG, BEAU, VARB};
//   x = Ap^-1(p), y = Ac^-1(c):  VIG y = x + k,  BEAU y = k - x,  VARB y = x - k   (mod 26).
// Families (key shift k at path step t):
//   PER  periodic: k_t = s[t mod p], p = 1..PMAX, shifts free;   coordinate ascent, RESTARTS random starts.
//   GRO  Gromark: 5-digit primer d0..d4, d_t = (d_{t-5} + d_{t-4}) mod 10, k_t = d_t; all 100,000 primers.
//   CTAK ciphertext autokey, lag L = 1..LMAX: k_t = Ac^-1(Y[t-L]) for t >= L, free primer shifts for t < L.
//   PTAK plaintext autokey, lag L = 1..LMAX: k_t = Ap^-1(Q[t-L]) for t >= L, free primer shifts for t < L.
// Search score: order-4 slice of the R59 letter model on P (fast, cache-resident); every family/convention's best
// candidates are rescored with the full order-6 model + 1 x the R59 word-segmentation score (total).
// Usage: keyed_solve LM WORDS IN.tsv OUT.jsonl [PMAX=26] [LMAX=24] [RESTARTS=6] [SEED=68]
//   IN.tsv rows: id <TAB> Y <TAB> R      OUT: one JSON line per row with each (family, convention)'s best.
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
static void load(const char *lmpath, const char *wpath) {
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
static double wordscore(const string &s) {   // identical to R59/R63
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
struct Conv { string name; const string *Ap, *Ac; int op; int ip[26], ic[26]; };
static vector<Conv> CONVS;
static inline int dec(const Conv &cv, int y, int k) {   // returns x (plaintext index in Ap)
    int x = cv.op == 0 ? y - k : cv.op == 1 ? k - y : y + k; return ((x % 26) + 26) % 26;
}
struct Row { string id, Y; vector<int> R; int N; };
// layout: P[j] = Q[R[j]]
static string layout(const Row &rw, const string &Q) { string P(rw.N, 'A'); for (int j = 0; j < rw.N; j++) P[j] = Q[rw.R[j]]; return P; }
struct Best { string fam, conv, param, key, P; double s4 = -1e30, lm6 = 0, w = 0, tot = -1e30; };
static void finish(Best &b) { b.lm6 = lm_order(b.P, 6); b.w = wordscore(b.P); b.tot = b.lm6 + b.w; }

int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: keyed_solve LM WORDS IN.tsv OUT.jsonl [PMAX] [LMAX] [RESTARTS] [SEED]");
    int PMAX = argc > 5 ? atoi(argv[5]) : 26, LMAX = argc > 6 ? atoi(argv[6]) : 24, RS = argc > 7 ? atoi(argv[7]) : 6;
    uint64_t SEED = argc > 8 ? strtoull(argv[8], 0, 10) : 68;
    load(argv[1], argv[2]);
    for (auto ap : {&AZ, &KRY}) for (auto ac : {&AZ, &KRY}) for (int op = 0; op < 3; op++) {
        Conv cv; cv.name = string(ap == &AZ ? "AZ" : "KRY") + "/" + (ac == &AZ ? "AZ" : "KRY") + "_" + (op == 0 ? "VIG" : op == 1 ? "BEAU" : "VARB");
        cv.Ap = ap; cv.Ac = ac; cv.op = op; for (int t = 0; t < 26; t++) { cv.ip[(*ap)[t] - 'A'] = t; cv.ic[(*ac)[t] - 'A'] = t; }
        CONVS.push_back(cv);
    }
    ifstream in(argv[3]); ofstream out(argv[4]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id\t", 0) == 0) continue;
      Row rw; { stringstream ss(line); string rs; getline(ss, rw.id, '\t'); getline(ss, rw.Y, '\t'); getline(ss, rs, '\t');
        rw.N = rw.Y.size();
        if (rs == "I") { rw.R.resize(rw.N); iota(rw.R.begin(), rw.R.end(), 0); }
        else { stringstream s2(rs); string x; while (getline(s2, x, ',')) rw.R.push_back(stoi(x)); }
        if ((int)rw.R.size() != rw.N) throw runtime_error("bad R " + rw.id); }
      const int N = rw.N;
      uint64_t h = 1469598103934665603ULL; for (char c : rw.id) h = (h ^ (uint8_t)c) * 1099511628211ULL;
      vector<Best> bests;
      for (const Conv &cv : CONVS) {
        vector<int> y(N); for (int t = 0; t < N; t++) y[t] = cv.ic[rw.Y[t] - 'A'];
        string Q(N, 'A');
        auto score4 = [&](const string &Qs) { return lm_order(layout(rw, Qs), 4); };
        // ---- PER
        for (int p = 1; p <= PMAX; p++) {
          Best b; b.fam = "PER"; b.conv = cv.name; b.param = to_string(p);
          mt19937_64 rng(SEED * 1000003ULL + h * 31 + p * 7919 + (&cv - &CONVS[0]) * 104729);
          for (int r = 0; r < RS; r++) {
            vector<int> s(p); for (int &v : s) v = rng() % 26;
            for (int t = 0; t < N; t++) Q[t] = (*cv.Ap)[dec(cv, y[t], s[t % p])];
            double cur = score4(Q);
            for (int sweep = 0; sweep < 20; sweep++) {
              bool imp = false;
              for (int c = 0; c < p; c++) {
                int bestk = s[c]; double bestv = cur;
                for (int k = 0; k < 26; k++) { if (k == s[c]) continue;
                  for (int t = c; t < N; t += p) Q[t] = (*cv.Ap)[dec(cv, y[t], k)];
                  double v = score4(Q); if (v > bestv + 1e-9) { bestv = v; bestk = k; } }
                s[c] = bestk; for (int t = c; t < N; t += p) Q[t] = (*cv.Ap)[dec(cv, y[t], bestk)];
                if (bestv > cur + 1e-9) { cur = bestv; imp = true; }
              }
              if (!imp) break;
            }
            if (cur > b.s4) { b.s4 = cur; b.P = layout(rw, Q); b.key.clear(); for (int v : s) b.key += AZ[v]; }
          }
          finish(b); bests.push_back(b);
        }
        // ---- GRO (all primers; keep the best by order-4, then rescore the top 5)
        {
          vector<pair<double, int>> top;
          int d[128];
          for (int pr = 0; pr < 100000; pr++) {
            int v = pr; for (int i = 4; i >= 0; i--) { d[i] = v % 10; v /= 10; }
            for (int t = 5; t < N; t++) d[t] = (d[t - 5] + d[t - 4]) % 10;
            for (int t = 0; t < N; t++) Q[t] = (*cv.Ap)[dec(cv, y[t], d[t])];
            double sc = score4(Q);
            if (top.size() < 5 || sc > top.back().first) { top.push_back({sc, pr}); sort(top.rbegin(), top.rend()); if (top.size() > 5) top.pop_back(); }
          }
          Best bb; bb.fam = "GRO"; bb.conv = cv.name;
          for (auto &tp : top) {
            int v = tp.second; for (int i = 4; i >= 0; i--) { d[i] = v % 10; v /= 10; }
            for (int t = 5; t < N; t++) d[t] = (d[t - 5] + d[t - 4]) % 10;
            for (int t = 0; t < N; t++) Q[t] = (*cv.Ap)[dec(cv, y[t], d[t])];
            Best b; b.fam = "GRO"; b.conv = cv.name; char buf[8]; snprintf(buf, sizeof buf, "%05d", tp.second); b.param = buf; b.key = buf;
            b.P = layout(rw, Q); b.s4 = tp.first; finish(b); if (b.tot > bb.tot) bb = b;
          }
          bests.push_back(bb);
        }
        // ---- CTAK / PTAK
        for (int fam = 0; fam < 2; fam++) for (int L = 1; L <= LMAX; L++) {
          Best b; b.fam = fam == 0 ? "CTAK" : "PTAK"; b.conv = cv.name; b.param = to_string(L);
          mt19937_64 rng(SEED * 999983ULL + h * 17 + L * 6151 + fam * 7 + (&cv - &CONVS[0]) * 15485863);
          auto build = [&](const vector<int> &pr) {
            for (int t = 0; t < N; t++) {
              int k = t < L ? pr[t] : fam == 0 ? cv.ic[rw.Y[t - L] - 'A'] : cv.ip[Q[t - L] - 'A'];
              Q[t] = (*cv.Ap)[dec(cv, y[t], k)];
            }
          };
          for (int r = 0; r < (fam == 0 ? 1 : RS); r++) {
            vector<int> pr(L); for (int &v : pr) v = rng() % 26;
            build(pr); double cur = score4(Q);
            for (int sweep = 0; sweep < 20; sweep++) {
              bool imp = false;
              for (int c = 0; c < L; c++) {
                int bestk = pr[c]; double bestv = cur;
                for (int k = 0; k < 26; k++) { if (k == pr[c]) continue; pr[c] = k; build(pr); double v = score4(Q); if (v > bestv + 1e-9) { bestv = v; bestk = k; } }
                pr[c] = bestk; build(pr); if (bestv > cur + 1e-9) { cur = bestv; imp = true; }
              }
              if (!imp) break;
            }
            if (cur > b.s4) { b.s4 = cur; b.P = layout(rw, Q); b.key.clear(); for (int v : pr) b.key += AZ[v]; }
          }
          finish(b); bests.push_back(b);
        }
      }
      // per (family, convention) keep the best over its parameter; plus the overall best
      map<pair<string, string>, Best> keep;
      for (auto &b : bests) { auto kk = make_pair(b.fam, b.conv); if (!keep.count(kk) || b.tot > keep[kk].tot) keep[kk] = b; }
      Best overall; for (auto &kv : keep) if (kv.second.tot > overall.tot) overall = kv.second;
      auto js = [](const Best &b) { char buf[160]; snprintf(buf, sizeof buf, ",\"lm6\":%.4f,\"word\":%.4f,\"total\":%.4f}", b.lm6, b.w, b.tot);
        return "{\"family\":\"" + b.fam + "\",\"convention\":\"" + b.conv + "\",\"param\":\"" + b.param + "\",\"key\":\"" + b.key + "\",\"plaintext\":\"" + b.P + "\"" + buf; };
      out << "{\"id\":\"" << rw.id << "\",\"best\":" << js(overall) << ",\"by_family_convention\":[";
      bool first = true; for (auto &kv : keep) { out << (first ? "" : ",") << js(kv.second); first = false; }
      out << "]}\n"; out.flush();
      fprintf(stderr, "R68 %s best %.2f %s %s %s\n", rw.id.c_str(), overall.tot, overall.fam.c_str(), overall.conv.c_str(), overall.param.c_str());
    }
  } catch (const exception &e) { fprintf(stderr, "R68 ERROR %s\n", e.what()); return 1; }
}

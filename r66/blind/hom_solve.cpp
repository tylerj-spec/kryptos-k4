// R66 BLIND solver: HOMOPHONIC substitution (a masking cipher). No K4 clues, masks or positions.
// Model: each ciphertext letter c stands for exactly one plaintext letter f(c); several ciphertext letters may stand for
// the same plaintext letter (homophones), and some plaintext letters may have none. Decryption of an (un-routed) text X
// is P[i] = f(X[i]). f is any map A-Z -> A-Z (26^26 keys; a simple substitution is the special case of a bijection).
// Search: simulated annealing over f under the R59 English letter model (order 6), many restarts with fixed seeds,
// then hill-climb polish of f under LM + LAMBDA * word-segmentation score (R59 word model). Deterministic.
// Homophone cap: at most CAP cipher letters (among those present in X) may stand for the same plaintext letter, as in
// real homophonic tables. Without it the letter model's smoothing rewards degenerate strings (97 x "A" outscores real
// English), so the cap is part of the model, not a tuning device.
// Annealing uses the letter model truncated to order AORD (lower orders give a smoother landscape), temperature T0 -> T1
// (log10 units, geometric); the polish and all reported scores use the full order-6 model.
// Usage: hom_solve LM WORDS IN.tsv OUT.jsonl [RESTARTS=40] [ITERS=40000] [LAMBDA=1] [SEED=66] [CAP=4] [AORD=6]
//        [T0=2.0] [T1=0.02]
//   IN.tsv: "id<TAB>X" rows (X = 97 letters, already un-routed). OUT.jsonl: one line per id:
//   {"id", "best": {plaintext, map, lm, word, total}, "top": [... up to 8 distinct plaintexts]}
//   map = 26 letters: map[c] = f('A'+c).
#include <bits/stdc++.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;
struct Node { int nx[26]; float lp; float best; };
struct Model { const float *LM[7]; int K = 6; vector<Node> trie, rtrie; };
static Model M;
static void add_word(vector<Node> &T, const string &w, float ex) {
    int u = 0; T[0].best = max(T[0].best, ex);
    for (char ch : w) { int c = ch - 'A';
        if (T[u].nx[c] < 0) { T[u].nx[c] = T.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; nd.best = -1e30f; T.push_back(nd); }
        u = T[u].nx[c]; T[u].best = max(T[u].best, ex); }
    T[u].lp = max(T[u].lp, ex);
}
static void load_model(const char *lmpath, const char *wpath) {
    int fd = open(lmpath, O_RDONLY); if (fd < 0) throw runtime_error(string("lm open ") + lmpath);
    off_t len = lseek(fd, 0, SEEK_END); void *mp = mmap(nullptr, len, PROT_READ, MAP_SHARED, fd, 0); if (mp == MAP_FAILED) throw runtime_error("mmap");
    const char *b = (const char *)mp; if (memcmp(b, "R59LM", 5) != 0) throw runtime_error("lm header");
    M.K = b[5]; const float *q = (const float *)(b + 8); size_t sz = 26, tot = 0;
    for (int k = 1; k <= M.K; k++) { M.LM[k] = q; q += sz; tot += sz; sz *= 26; }
    if ((size_t)len != 8 + tot * 4) throw runtime_error("lm size");
    for (auto *T : {&M.trie, &M.rtrie}) { T->assign(1, Node{}); memset((*T)[0].nx, -1, sizeof (*T)[0].nx); (*T)[0].lp = -1e30f; (*T)[0].best = -1e30f; }
    ifstream f(wpath); if (!f) throw runtime_error(string("words ") + wpath);
    string w; double ex, ed;
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        bool ok = true; for (char ch : w) if (ch < 'A' || ch > 'Z') { ok = false; break; }
        if (!ok) continue;
        add_word(M.trie, w, (float)ex); string r(w.rbegin(), w.rend()); add_word(M.rtrie, r, (float)ex);
    }
}
// word segmentation score, identical to R59/R63 (fragments allowed at both ends, -7 per unmatched letter)
static double wordscore(const string &s) {
    int n = s.size(); vector<double> dp(n + 1, -1e30); dp[0] = 0;
    for (int j = 1; j <= min(n, 12); j++) { int v = 0; for (int q = j - 1; q >= 0; q--) { v = M.rtrie[v].nx[s[q] - 'A']; if (v < 0) break; }
        if (v >= 0 && M.rtrie[v].best > -1e29) dp[j] = max(dp[j], (double)M.rtrie[v].best); }
    for (int i = 0; i < n; i++) {
        if (dp[i] < -1e29) continue;
        dp[i + 1] = max(dp[i + 1], dp[i] - 7);
        int u = 0;
        for (int j = i; j < n && j < i + 24; j++) { u = M.trie[u].nx[s[j] - 'A']; if (u < 0) break; if (M.trie[u].lp > -1e29) dp[j + 1] = max(dp[j + 1], dp[i] + M.trie[u].lp); }
    }
    double best = dp[n];
    for (int i = max(0, n - 12); i < n; i++) { if (dp[i] < -1e29) continue; int u = 0;
        for (int j = i; j < n && u >= 0; j++) u = M.trie[u].nx[s[j] - 'A'];
        if (u >= 0 && M.trie[u].best > -1e29) best = max(best, dp[i] + M.trie[u].best); }
    return best;
}
static inline double lmat(const string &s, int i) {
    int L = min(i, M.K - 1); uint32_t c = 0; for (int j = i - L; j < i; j++) c = c * 26 + (s[j] - 'A');
    return M.LM[L + 1][c * 26 + (s[i] - 'A')];
}
static double lmscore(const string &s) { double z = 0; for (int i = 0; i < (int)s.size(); i++) z += lmat(s, i); return z; }
static int AORD = 6;
static inline double lma(const string &s, int i) {   // annealing score: model truncated to order AORD
    int L = min(i, AORD - 1); uint32_t c = 0; for (int j = i - L; j < i; j++) c = c * 26 + (s[j] - 'A');
    return M.LM[L + 1][c * 26 + (s[i] - 'A')];
}
struct Sol { string pt, map; double lm, w, tot; };

int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: hom_solve LM WORDS IN.tsv OUT.jsonl [RESTARTS] [ITERS] [LAMBDA] [SEED]");
    int R = argc > 5 ? atoi(argv[5]) : 40; long IT = argc > 6 ? atol(argv[6]) : 40000;
    double lam = argc > 7 ? atof(argv[7]) : 1.0; uint64_t seed0 = argc > 8 ? strtoull(argv[8], 0, 10) : 66;
    int CAP = argc > 9 ? atoi(argv[9]) : 4; if (CAP < 1 || CAP > 26) throw runtime_error("bad CAP");
    AORD = argc > 10 ? atoi(argv[10]) : 6; double T0 = argc > 11 ? atof(argv[11]) : 2.0, T1 = argc > 12 ? atof(argv[12]) : 0.02;
    load_model(argv[1], argv[2]);
    ifstream in(argv[3]); ofstream out(argv[4]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id", 0) == 0) continue;
      string id = line.substr(0, line.find('\t')), X = line.substr(line.find('\t') + 1);
      while (!X.empty() && !isalpha((unsigned char)X.back())) X.pop_back();
      int N = X.size(); for (char c : X) if (c < 'A' || c > 'Z') throw runtime_error("bad text " + id);
      vector<vector<int>> pos(26); for (int i = 0; i < N; i++) pos[X[i] - 'A'].push_back(i);
      vector<int> present; for (int c = 0; c < 26; c++) if (!pos[c].empty()) present.push_back(c);
      uint64_t h = 1469598103934665603ULL; for (char c : id) h = (h ^ (uint8_t)c) * 1099511628211ULL;
      vector<Sol> sols;
      for (int r = 0; r < R; r++) {
        mt19937_64 rng(seed0 * 1000003ULL + h + r * 7919ULL);
        string f(26, '?'); int cnt[26] = {0};
        for (int c : present) { int v; do v = rng() % 26; while (cnt[v] >= CAP); f[c] = 'A' + v; cnt[v]++; }
        for (int c = 0; c < 26; c++) if (f[c] == '?') f[c] = 'A';   // absent cipher letters: unused
        string P(N, 'A'); for (int i = 0; i < N; i++) P[i] = f[X[i] - 'A'];
        double cur = 0; for (int i = 0; i < N; i++) cur += lma(P, i);
        double best = cur; string bf = f;
        // affected n-gram end positions for a change of letter c
        vector<char> mark(N, 0); vector<int> aff;
        for (long t = 0; t < IT; t++) {
          double T = T0 * pow(T1 / T0, (double)t / IT);           // temperature, log10 units
          int c = present[rng() % present.size()]; char nv = 'A' + rng() % 26;
          int c2 = -1; char ov = f[c];
          if (rng() % 4 == 0) { c2 = present[rng() % present.size()]; if (c2 == c) continue; nv = f[c2]; if (nv == ov) continue; }
          else if (nv == ov || cnt[nv - 'A'] >= CAP) continue;
          aff.clear();
          for (int cc : {c, c2}) { if (cc < 0) continue; for (int i : pos[cc]) for (int e = i; e < min(N, i + AORD); e++) if (!mark[e]) { mark[e] = 1; aff.push_back(e); } }
          double before = 0; for (int e : aff) before += lma(P, e);
          f[c] = nv; for (int i : pos[c]) P[i] = nv;
          if (c2 >= 0) { f[c2] = ov; for (int i : pos[c2]) P[i] = ov; }
          double after = 0; for (int e : aff) after += lma(P, e);
          for (int e : aff) mark[e] = 0;
          double d = after - before;
          if (d >= 0 || exp(d / T * 2.302585) > (rng() >> 11) * (1.0 / 9007199254740992.0)) {
            if (c2 < 0) { cnt[ov - 'A']--; cnt[nv - 'A']++; }
            cur += d; if (cur > best) { best = cur; bf = f; }
          } else {
            f[c] = ov; for (int i : pos[c]) P[i] = ov;
            if (c2 >= 0) { f[c2] = nv; for (int i : pos[c2]) P[i] = nv; }
          }
        }
        // polish under LM + LAMBDA * word score (single-letter changes of f until no improvement)
        f = bf; for (int i = 0; i < N; i++) P[i] = f[X[i] - 'A'];
        memset(cnt, 0, sizeof cnt); for (int c : present) cnt[f[c] - 'A']++;
        double F = lmscore(P) + lam * wordscore(P);
        for (int pass = 0; pass < 6; pass++) {
          bool imp = false;
          for (int c : present) for (int v = 0; v < 26; v++) {
            char ov = f[c], nv = 'A' + v; if (nv == ov || cnt[v] >= CAP) continue;
            for (int i : pos[c]) P[i] = nv;
            double g = lmscore(P) + lam * wordscore(P);
            if (g > F + 1e-9) { F = g; f[c] = nv; cnt[ov - 'A']--; cnt[v]++; imp = true; } else for (int i : pos[c]) P[i] = ov;
          }
          if (!imp) break;
        }
        for (int c = 0; c < 26; c++) if (pos[c].empty()) f[c] = '?';
        double lv = lmscore(P), wv = wordscore(P);
        sols.push_back({P, f, lv, wv, lv + lam * wv});
      }
      sort(sols.begin(), sols.end(), [](const Sol &a, const Sol &b) { return a.tot > b.tot; });
      vector<Sol> top; for (auto &s : sols) { bool dup = false; for (auto &t : top) if (t.pt == s.pt) { dup = true; break; } if (!dup) top.push_back(s); if (top.size() >= 8) break; }
      for (auto &s : top) for (int i = 0; i < N; i++) if (s.map[X[i] - 'A'] != s.pt[i]) throw runtime_error("witness failed " + id);
      auto js = [](const Sol &s) { char buf[96]; snprintf(buf, sizeof buf, ",\"lm\":%.4f,\"word\":%.4f,\"total\":%.4f}", s.lm, s.w, s.tot);
        return "{\"plaintext\":\"" + s.pt + "\",\"map\":\"" + s.map + "\"" + buf; };
      out << "{\"id\":\"" << id << "\",\"best\":" << js(top[0]) << ",\"top\":[";
      for (size_t j = 0; j < top.size(); j++) out << (j ? "," : "") << js(top[j]);
      out << "]}\n"; out.flush();
      fprintf(stderr, "R66 %s best %.2f (lm %.2f, w %.2f)\n", id.c_str(), top[0].tot, top[0].lm, top[0].w);
    }
  } catch (const exception &e) { fprintf(stderr, "R66 ERROR %s\n", e.what()); return 1; }
}

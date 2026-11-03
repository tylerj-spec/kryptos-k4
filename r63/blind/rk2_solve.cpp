// R63 BLIND solver: running key whose KEY comes from a non-English source, plaintext ordinary English. No K4 clues,
// masks or positions. Generalises r59/blind/rk_solve.cpp (which is left unchanged) to two different text models:
//   stream A = plaintext, scored by LM_A + W_A (English); stream B = key, scored by LM_B + W_B (key model: World Clock
//   city-name sequences, or German prose; r63/corpus/build_keys.py).
// Conventions (6): X in {AZ, KRY}, indices in X:  VIG c = X[x(A) + x(B)],  BEAU c = X[x(B) - x(A)],  VARB c = X[x(A) - x(B)].
// Search, rescoring and polish as R59, except: no stream-swap move (the two streams have different models) and the
// word-placement move uses each stream's own dictionary.
// Usage: rk2_solve LM_A WORDS_A LM_B WORDS_B IN.tsv OUT.jsonl [BEAM=50000] [TOPN=2000] [LAMBDA=1] [CONVS=all]
//        [POLISH_M=2] [POLISH_WORDS=20000]
#include <bits/stdc++.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;
static const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
struct Node { int nx[26]; float lp; float best; };
struct Model {
    const float *LM[7]; int K = 6; uint32_t HMOD = 11881376;
    vector<Node> trie, rtrie; vector<string> WORDS;
};
static void add_word(vector<Node> &T, const string &w, float ex) {
    int u = 0; T[0].best = max(T[0].best, ex);
    for (char ch : w) { int c = ch - 'A';
        if (T[u].nx[c] < 0) { T[u].nx[c] = T.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; nd.best = -1e30f; T.push_back(nd); }
        u = T[u].nx[c]; T[u].best = max(T[u].best, ex); }
    T[u].lp = max(T[u].lp, ex);
}
static void load_model(Model &M, const char *lmpath, const char *wpath, int WN) {
    int fd = open(lmpath, O_RDONLY); if (fd < 0) throw runtime_error(string("lm open ") + lmpath);
    off_t len = lseek(fd, 0, SEEK_END); void *mp = mmap(nullptr, len, PROT_READ, MAP_SHARED, fd, 0); if (mp == MAP_FAILED) throw runtime_error("mmap");
    const char *b = (const char *)mp; if (memcmp(b, "R59LM", 5) != 0) throw runtime_error("lm header");
    M.K = b[5]; M.HMOD = 1; for (int j = 0; j < M.K - 1; j++) M.HMOD *= 26;
    const float *q = (const float *)(b + 8); size_t sz = 26, tot = 0;
    for (int k = 1; k <= M.K; k++) { M.LM[k] = q; q += sz; tot += sz; sz *= 26; }
    if ((size_t)len != 8 + tot * 4) throw runtime_error("lm size");
    for (auto *T : {&M.trie, &M.rtrie}) { T->assign(1, Node{}); memset((*T)[0].nx, -1, sizeof (*T)[0].nx); (*T)[0].lp = -1e30f; (*T)[0].best = -1e30f; }
    ifstream f(wpath); if (!f) throw runtime_error(string("words ") + wpath);
    string w; double ex, ed; vector<pair<double, string>> v;
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        bool ok = true; for (char ch : w) if (ch < 'A' || ch > 'Z') { ok = false; break; }
        if (!ok) continue;
        add_word(M.trie, w, (float)ex); string r(w.rbegin(), w.rend()); add_word(M.rtrie, r, (float)ex);
        if (w.size() >= 4 && w.size() <= 14) v.push_back({-ex, w});
    }
    sort(v.begin(), v.end()); for (int i = 0; i < (int)v.size() && i < WN; i++) M.WORDS.push_back(v[i].second);
}
static double wordscore(const Model &M, const string &s) {
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
static double lmrange(const Model &M, const string &s, int a, int e) {
    double z = 0;
    for (int i = a; i < e; i++) { int L = min(i, M.K - 1); uint32_t c = 0; for (int j = i - L; j < i; j++) c = c * 26 + (s[j] - 'A');
        z += M.LM[L + 1][c * 26 + (s[i] - 'A')]; }
    return z;
}
static double lmscore(const Model &M, const string &s) { return lmrange(M, s, 0, s.size()); }
static Model MA, MB;
struct Cipher { const string *ct; const int *xi; const string *X; int op; };
// given one stream letter, the other is forced: aIsA = the given letter is in stream A (plaintext)
static char forced(const Cipher &C, int i, char a, bool aIsA) {
    int cx = C.xi[(*C.ct)[i] - 'A'], ax = C.xi[a - 'A'], bx;
    if (C.op == 0) bx = cx - ax;                          // VIG  c = A + B
    else if (C.op == 1) bx = aIsA ? cx + ax : ax - cx;    // BEAU c = B - A: B = c + A ; A = B - c
    else bx = aIsA ? ax - cx : ax + cx;                   // VARB c = A - B: B = A - c ; A = c + B
    return (*C.X)[((bx % 26) + 26) % 26];
}
static double Fof(const string &a, const string &b, double lam) {
    return lmscore(MA, a) + lmscore(MB, b) + lam * (wordscore(MA, a) + wordscore(MB, b)); }
static void polish(const Cipher &C, string &a, string &b, double lam, int maxpass) {
    int N = a.size(); double F = Fof(a, b, lam);
    for (int pass = 0; pass < maxpass; pass++) {
        bool imp = false;
        for (int i = 0; i < N; i++) for (int l = 0; l < 26; l++) {
            char na = 'A' + l; if (na == a[i]) continue;
            char oa = a[i], ob = b[i]; a[i] = na; b[i] = forced(C, i, na, true);
            double g = Fof(a, b, lam); if (g > F + 1e-9) { F = g; imp = true; } else { a[i] = oa; b[i] = ob; }
        }
        for (int side = 0; side < 2; side++) {
            string &S = side == 0 ? a : b, &O = side == 0 ? b : a;
            const Model &MS = side == 0 ? MA : MB, &MO = side == 0 ? MB : MA;
            for (const string &w : MS.WORDS) { int L = w.size();
                for (int i = 0; i + L <= N; i++) {
                    if (S.compare(i, L, w) == 0) continue;
                    string nS = S, nO = O; for (int j = 0; j < L; j++) { nS[i + j] = w[j]; nO[i + j] = forced(C, i + j, w[j], side == 0); }
                    int e = min(N, i + L + 5);
                    double d = lmrange(MS, nS, i, e) + lmrange(MO, nO, i, e) - lmrange(MS, S, i, e) - lmrange(MO, O, i, e);
                    if (d < -12) continue;
                    double g = side == 0 ? Fof(nS, nO, lam) : Fof(nO, nS, lam);
                    if (g > F + 1e-9) { F = g; S = nS; O = nO; imp = true; }
                }
            }
        }
        if (!imp) break;
    }
}
struct Child { float score; uint32_t parent; uint8_t letter; uint64_t state; };
struct Conv { string name; const string *X; int op; };
int main(int argc, char **argv) {
  try {
    if (argc < 7) throw runtime_error("usage: rk2_solve LM_A WORDS_A LM_B WORDS_B IN.tsv OUT.jsonl [BEAM] [TOPN] [LAMBDA] [CONVS] [POLISH_M] [POLISH_WORDS]");
    size_t B = argc > 7 ? atol(argv[7]) : 50000; size_t TOPN = argc > 8 ? atol(argv[8]) : 2000;
    double lam = argc > 9 ? atof(argv[9]) : 1.0; string convsel = argc > 10 ? argv[10] : "all";
    int PM = argc > 11 ? atoi(argv[11]) : 2; int WN = argc > 12 ? atoi(argv[12]) : 20000; int MAXPASS = 8;
    load_model(MA, argv[1], argv[2], WN); load_model(MB, argv[3], argv[4], WN);
    if (MA.K != MB.K) throw runtime_error("models must have the same order");
    const int K = MA.K; const uint32_t HMOD = MA.HMOD;
    vector<Conv> convs;
    for (auto X : {&AZ, &KRY}) for (int op = 0; op < 3; op++) {
        string nm = string(X == &AZ ? "AZ" : "KRY") + "_" + (op == 0 ? "VIG" : op == 1 ? "BEAU" : "VARB");
        if (convsel == "all" || convsel.find(nm) != string::npos) convs.push_back({nm, X, op});
    }
    ifstream in(argv[5]); ofstream out(argv[6]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id", 0) == 0) continue;
      string id = line.substr(0, line.find('\t')), ct = line.substr(line.find('\t') + 1);
      while (!ct.empty() && !isalpha((unsigned char)ct.back())) ct.pop_back();
      int N = ct.size(); for (char c : ct) if (c < 'A' || c > 'Z') throw runtime_error("bad ciphertext " + id);
      struct Res { string conv, a, b; double lmv, w, tot; };
      vector<Res> best_per_conv, top_alts;
      for (auto &cv : convs) {
        const string &X = *cv.X; int xi[26]; for (int t = 0; t < 26; t++) xi[X[t] - 'A'] = t;
        Cipher C{&ct, xi, &X, cv.op};
        vector<float> sc(1, 0); vector<uint64_t> st(1, 0);
        vector<vector<uint32_t>> par(N); vector<vector<uint8_t>> let(N);
        vector<Child> ch; ch.reserve(B * 26);
        for (int i = 0; i < N; i++) {
          int L = min(i, K - 1); uint32_t m = 1; for (int j = 0; j < L; j++) m *= 26;
          const float *TA = MA.LM[L + 1], *TB = MB.LM[L + 1];
          ch.clear();
          for (size_t h = 0; h < sc.size(); h++) {
            uint32_t ha = st[h] >> 32, hb = st[h] & 0xffffffffu;
            uint32_t ba = (ha % m) * 26, bb = (hb % m) * 26;
            for (int a = 0; a < 26; a++) {
              int b = forced(C, i, 'A' + a, true) - 'A';
              float s = sc[h] + TA[ba + a] + TB[bb + b];
              uint64_t ns = ((uint64_t)((ha * 26 + a) % HMOD) << 32) | ((hb * 26 + b) % HMOD);
              ch.push_back({s, (uint32_t)h, (uint8_t)a, ns});
            }
          }
          size_t M = min(ch.size(), B * 3);
          if (M < ch.size()) nth_element(ch.begin(), ch.begin() + M, ch.end(), [](const Child &x, const Child &y) { return x.score > y.score; });
          sort(ch.begin(), ch.begin() + M, [](const Child &x, const Child &y) { return x.score != y.score ? x.score > y.score : x.state < y.state; });
          unordered_set<uint64_t> seen; seen.reserve(B * 2);
          vector<float> nsc; vector<uint64_t> nst; nsc.reserve(B); nst.reserve(B);
          for (size_t j = 0; j < M && nsc.size() < B; j++) if (seen.insert(ch[j].state).second) {
            nsc.push_back(ch[j].score); nst.push_back(ch[j].state); par[i].push_back(ch[j].parent); let[i].push_back(ch[j].letter); }
          sc.swap(nsc); st.swap(nst);
        }
        size_t nt = min(TOPN, sc.size());
        vector<Res> cand;
        for (size_t r = 0; r < nt; r++) {
          string a(N, '?'), b(N, '?'); size_t h = r;
          for (int i = N - 1; i >= 0; i--) { a[i] = 'A' + let[i][h]; h = par[i][h]; }
          for (int i = 0; i < N; i++) b[i] = forced(C, i, a[i], true);
          double lv = lmscore(MA, a) + lmscore(MB, b), w = wordscore(MA, a) + wordscore(MB, b);
          cand.push_back({cv.name, a, b, lv, w, lv + lam * w});
        }
        sort(cand.begin(), cand.end(), [](const Res &x, const Res &y) { return x.tot > y.tot; });
        for (int r = 0; r < min<int>(PM, cand.size()); r++) { polish(C, cand[r].a, cand[r].b, lam, MAXPASS);
          cand[r].lmv = lmscore(MA, cand[r].a) + lmscore(MB, cand[r].b); cand[r].w = wordscore(MA, cand[r].a) + wordscore(MB, cand[r].b);
          cand[r].tot = cand[r].lmv + lam * cand[r].w; }
        sort(cand.begin(), cand.end(), [](const Res &x, const Res &y) { return x.tot > y.tot; });
        for (auto &r : cand) for (int i = 0; i < N; i++) {
          int ax = xi[r.a[i] - 'A'], bx = xi[r.b[i] - 'A'];
          int c = cv.op == 0 ? ax + bx : cv.op == 1 ? bx - ax : ax - bx;
          if (X[((c % 26) + 26) % 26] != ct[i]) throw runtime_error("witness failed " + id);
        }
        best_per_conv.push_back(cand[0]);
        for (size_t r = 0; r < min<size_t>(3, cand.size()); r++) top_alts.push_back(cand[r]);
        fprintf(stderr, "R63 %s %s best %.2f (lm %.2f, w %.2f)\n", id.c_str(), cv.name.c_str(), cand[0].tot, cand[0].lmv, cand[0].w);
      }
      sort(best_per_conv.begin(), best_per_conv.end(), [](const Res &x, const Res &y) { return x.tot > y.tot; });
      sort(top_alts.begin(), top_alts.end(), [](const Res &x, const Res &y) { return x.tot > y.tot; });
      auto js = [](const Res &r) { char buf[64]; string s = "{\"convention\":\"" + r.conv + "\",\"plaintext\":\"" + r.a + "\",\"key\":\"" + r.b + "\"";
        snprintf(buf, sizeof buf, ",\"lm\":%.4f,\"word\":%.4f,\"total\":%.4f}", r.lmv, r.w, r.tot); return s + buf; };
      out << "{\"id\":\"" << id << "\",\"best\":" << js(best_per_conv[0]) << ",\"per_convention\":[";
      for (size_t j = 0; j < best_per_conv.size(); j++) out << (j ? "," : "") << js(best_per_conv[j]);
      out << "],\"top\":[";
      for (size_t j = 0; j < min<size_t>(8, top_alts.size()); j++) out << (j ? "," : "") << js(top_alts[j]);
      out << "]}\n"; out.flush();
    }
  } catch (const exception &e) { fprintf(stderr, "R63 ERROR %s\n", e.what()); return 1; }
}

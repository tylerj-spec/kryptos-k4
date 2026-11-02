// R59 BLIND solver: running key from an UNKNOWN English text under a fixed tableau. No K4 clues, masks or positions.
// Model (6 conventions): alphabet X in {AZ, KRY = KRYPTOSABCDEFGHIJLMNQUVWXZ}; indices taken in X (as K1/K2);
//   VIG  c = X[x(p) + x(k)]     BEAU c = X[x(k) - x(p)]     VARB c = X[x(p) - x(k)]      (mod 26)
// Both the plaintext p and the key k are assumed to be ordinary English letters (no spaces).
// Search: beam over positions; each hypothesis is a pair of partial texts (p, k), k forced by p and c. Score =
//   LM(p) + LM(k) (generic letter n-gram of order K = 5 or 6, r59/blind/lm_build.cpp, memory-mapped); states with equal
//   last K-1 letters of both texts are merged (best kept). The TOPN complete pairs are rescored with + LAMBDA * (W(p) + W(k)), W = best segmentation into
//   exact dictionary words (k4kit/data/word_model_orth.tsv), -7 per unmatched letter (as r44/blind/polish.cpp).
// Usage: rk_solve LM.bin WORDS.tsv IN.tsv OUT.jsonl [BEAM=100000] [TOPN=2000] [LAMBDA=1] [CONVENTIONS=all] [POLISH_M=0]
//        [POLISH_WORDS=20000]   POLISH_M > 0 polishes the best POLISH_M rescored pairs per convention (see polish()).
//   IN.tsv: "id<TAB>ciphertext" (97 letters A-Z; a header line starting with "id" is skipped).
#include <bits/stdc++.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;
static const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
static const float *LM[7];   // LM[k]: order k, 26^k entries (memory-mapped)
static int KORD = 5; static uint32_t HMOD = 456976;   // 26^(K-1)
struct Node { int nx[26]; float lp; float best; };   // best: highest word log-prob in the subtree (completions)
static vector<Node> trie, rtrie;                       // rtrie: words reversed (for a word fragment at the start)
static void add_word(vector<Node> &T, const string &w, float ex) {
    int u = 0; T[0].best = max(T[0].best, ex);
    for (char ch : w) { int c = ch - 'A';
        if (T[u].nx[c] < 0) { T[u].nx[c] = T.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; nd.best = -1e30f; T.push_back(nd); }
        u = T[u].nx[c]; T[u].best = max(T[u].best, ex); }
    T[u].lp = max(T[u].lp, ex);
}
static void load_words(const string &path) {
    for (auto *T : {&trie, &rtrie}) { T->assign(1, Node{}); memset((*T)[0].nx, -1, sizeof (*T)[0].nx); (*T)[0].lp = -1e30f; (*T)[0].best = -1e30f; }
    ifstream f(path); if (!f) throw runtime_error("word model");
    string w; double ex, ed;
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        bool ok = true; for (char ch : w) if (ch < 'A' || ch > 'Z') { ok = false; break; }
        if (!ok) continue;
        add_word(trie, w, (float)ex); string r(w.rbegin(), w.rend()); add_word(rtrie, r, (float)ex);
    }
}
// Best segmentation into dictionary words, -7 per unmatched letter. The text may start inside a word (a fragment of
// 1..12 letters that ends some dictionary word, scored by the best such word) and end inside one (a fragment of up to
// 12 letters that begins some word, scored by the best completion): a running-key window need not align with words.
static double wordscore(const string &s) {
    int n = s.size(); vector<double> dp(n + 1, -1e30); dp[0] = 0;
    {   // leading fragment s[0:j]: walk the reversed trie from position j-1 back to 0
      for (int j = 1; j <= min(n, 12); j++) { int v = 0; for (int q = j - 1; q >= 0; q--) { v = rtrie[v].nx[s[q] - 'A']; if (v < 0) break; }
        if (v >= 0 && rtrie[v].best > -1e29) dp[j] = max(dp[j], (double)rtrie[v].best); } }
    for (int i = 0; i < n; i++) {
        if (dp[i] < -1e29) continue;
        dp[i + 1] = max(dp[i + 1], dp[i] - 7);
        int u = 0;
        for (int j = i; j < n && j < i + 24; j++) { u = trie[u].nx[s[j] - 'A']; if (u < 0) break; if (trie[u].lp > -1e29) dp[j + 1] = max(dp[j + 1], dp[i] + trie[u].lp); }
    }
    double best = dp[n];
    for (int i = max(0, n - 12); i < n; i++) { if (dp[i] < -1e29) continue; int u = 0;   // trailing word fragment
        for (int j = i; j < n && u >= 0; j++) u = trie[u].nx[s[j] - 'A'];
        if (u >= 0 && trie[u].best > -1e29) best = max(best, dp[i] + trie[u].best); }
    return best;
}
static double lmscore(const string &s) {
    double z = 0; uint32_t h = 0;
    for (size_t i = 0; i < s.size(); i++) { int L = min<size_t>(i, KORD - 1); uint32_t m = 1; for (int j = 0; j < L; j++) m *= 26;
        int w = s[i] - 'A'; z += LM[L + 1][(h % m) * 26 + w]; h = (h * 26 + w) % HMOD; }
    return z;
}
// LM sum over positions [a, e) of s (contexts from s itself)
static double lmrange(const string &s, int a, int e) {
    double z = 0;
    for (int i = a; i < e; i++) { int L = min(i, KORD - 1); uint32_t c = 0; for (int j = i - L; j < i; j++) c = c * 26 + (s[j] - 'A');
        z += LM[L + 1][c * 26 + (s[i] - 'A')]; }
    return z;
}
static vector<string> WORDS;   // polish dictionary: top dictionary words of length 4..12
// Polish: greedy first-improvement ascent of F = LM(p) + LM(k) + lam * (W(p) + W(k)) with moves
//  (a) one plaintext letter (key letter forced); (b) VIG only: swap the two texts from position i to the end;
//  (c) place a dictionary word in either text (the other text forced), screened by the local LM change.
struct Cipher { const string *ct; const int *xi; const string *X; int op; };
static char forced(const Cipher &C, int i, char a, bool aIsP) {
    int cx = C.xi[(*C.ct)[i] - 'A'], ax = C.xi[a - 'A'], bx;
    if (C.op == 0) bx = cx - ax;                          // VIG symmetric
    else if (C.op == 1) bx = aIsP ? cx + ax : ax - cx;    // BEAU c = k - p: k = c + p ; p = k - c
    else bx = aIsP ? ax - cx : ax + cx;                   // VARB c = p - k: k = p - c ; p = c + k
    return (*C.X)[((bx % 26) + 26) % 26];
}
static double Fof(const string &p, const string &k, double lam) { return lmscore(p) + lmscore(k) + lam * (wordscore(p) + wordscore(k)); }
static void polish(const Cipher &C, string &p, string &k, double lam, int maxpass) {
    int N = p.size(); double F = Fof(p, k, lam);
    for (int pass = 0; pass < maxpass; pass++) {
        bool imp = false;
        for (int i = 0; i < N; i++) for (int l = 0; l < 26; l++) {          // (a)
            char np = 'A' + l; if (np == p[i]) continue;
            char op_ = p[i], ok_ = k[i]; p[i] = np; k[i] = forced(C, i, np, true);
            double g = Fof(p, k, lam); if (g > F + 1e-9) { F = g; imp = true; } else { p[i] = op_; k[i] = ok_; }
        }
        if (C.op == 0) for (int i = 1; i < N; i++) {                        // (b)
            string np = p.substr(0, i) + k.substr(i), nk = k.substr(0, i) + p.substr(i);
            double g = Fof(np, nk, lam); if (g > F + 1e-9) { F = g; p = np; k = nk; imp = true; }
        }
        for (int side = 0; side < 2; side++) {                              // (c)
            string &A = side == 0 ? p : k, &Bs = side == 0 ? k : p;
            for (const string &w : WORDS) { int L = w.size();
                for (int i = 0; i + L <= N; i++) {
                    if (A.compare(i, L, w) == 0) continue;
                    string nA = A, nB = Bs; for (int j = 0; j < L; j++) { nA[i + j] = w[j]; nB[i + j] = forced(C, i + j, w[j], side == 0); }
                    int e = min(N, i + L + KORD - 1);
                    double d = lmrange(nA, i, e) + lmrange(nB, i, e) - lmrange(A, i, e) - lmrange(Bs, i, e);
                    if (d < -12) continue;
                    double g = side == 0 ? Fof(nA, nB, lam) : Fof(nB, nA, lam);
                    if (g > F + 1e-9) { F = g; A = nA; Bs = nB; imp = true; }
                }
            }
        }
        if (!imp) break;
    }
}
struct Child { float score; uint32_t parent; uint8_t letter; uint64_t state; };
struct Conv { string name; const string *X; int op; };   // op 0 VIG, 1 BEAU, 2 VARB
int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: rk_solve LM.bin WORDS.tsv IN.tsv OUT.jsonl [BEAM] [TOPN] [LAMBDA] [CONVS]");
    size_t B = argc > 5 ? atol(argv[5]) : 100000; size_t TOPN = argc > 6 ? atol(argv[6]) : 2000;
    double lam = argc > 7 ? atof(argv[7]) : 1.0; string convsel = argc > 8 ? argv[8] : "all";
    int PM = argc > 9 ? atoi(argv[9]) : 0; int WN = argc > 10 ? atoi(argv[10]) : 20000; int MAXPASS = 8;
    { int fd = open(argv[1], O_RDONLY); if (fd < 0) throw runtime_error("lm open");
      off_t len = lseek(fd, 0, SEEK_END); void *mp = mmap(nullptr, len, PROT_READ, MAP_SHARED, fd, 0); if (mp == MAP_FAILED) throw runtime_error("mmap");
      const char *b = (const char *)mp; if (memcmp(b, "R59LM", 5) != 0) throw runtime_error("lm header");
      KORD = b[5]; HMOD = 1; for (int j = 0; j < KORD - 1; j++) HMOD *= 26;
      const float *q = (const float *)(b + 8); size_t sz = 26, tot = 0;
      for (int k = 1; k <= KORD; k++) { LM[k] = q; q += sz; tot += sz; sz *= 26; }
      if ((size_t)len != 8 + tot * 4) throw runtime_error("lm size"); }
    load_words(argv[2]);
    { ifstream f(argv[2]); string w; double ex, ed; vector<pair<double, string>> v;
      while (f >> w >> ex >> ed) if (ex > -1e90 && w.size() >= 4 && w.size() <= 12) v.push_back({-ex, w});
      sort(v.begin(), v.end()); for (int i = 0; i < (int)v.size() && i < WN; i++) WORDS.push_back(v[i].second); }
    vector<Conv> convs;
    for (auto X : {&AZ, &KRY}) for (int op = 0; op < 3; op++) {
        string nm = string(X == &AZ ? "AZ" : "KRY") + "_" + (op == 0 ? "VIG" : op == 1 ? "BEAU" : "VARB");
        if (convsel == "all" || convsel.find(nm) != string::npos) convs.push_back({nm, X, op});
    }
    ifstream in(argv[3]); ofstream out(argv[4]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id", 0) == 0) continue;
      string id = line.substr(0, line.find('\t')), ct = line.substr(line.find('\t') + 1);
      while (!ct.empty() && !isalpha((unsigned char)ct.back())) ct.pop_back();
      int N = ct.size(); for (char c : ct) if (c < 'A' || c > 'Z') throw runtime_error("bad ciphertext " + id);
      struct Res { string conv, p, k; double lmv, w, tot; };
      vector<Res> best_per_conv; vector<Res> top_alts;
      for (auto &cv : convs) {
        const string &X = *cv.X; int xi[26]; for (int t = 0; t < 26; t++) xi[X[t] - 'A'] = t;
        vector<float> sc(1, 0); vector<uint64_t> st(1, 0);
        vector<vector<uint32_t>> par(N); vector<vector<uint8_t>> let(N);
        vector<Child> ch; ch.reserve(B * 26);
        for (int i = 0; i < N; i++) {
          int L = min(i, KORD - 1); uint32_t m = 1; for (int j = 0; j < L; j++) m *= 26;
          const float *T = LM[L + 1]; int cx = xi[ct[i] - 'A'];
          ch.clear();
          for (size_t h = 0; h < sc.size(); h++) {
            uint32_t hp = st[h] >> 32, hk = st[h] & 0xffffffffu;
            uint32_t bp = (hp % m) * 26, bk = (hk % m) * 26;
            for (int p = 0; p < 26; p++) {
              int px = xi[p], kx = cv.op == 0 ? cx - px : cv.op == 1 ? cx + px : px - cx; kx = ((kx % 26) + 26) % 26;
              int k = X[kx] - 'A';
              float s = sc[h] + T[bp + p] + T[bk + k];
              uint64_t ns = ((uint64_t)((hp * 26 + p) % HMOD) << 32) | ((hk * 26 + k) % HMOD);
              ch.push_back({s, (uint32_t)h, (uint8_t)p, ns});
            }
          }
          size_t M = min(ch.size(), B * 3);
          if (M < ch.size()) nth_element(ch.begin(), ch.begin() + M, ch.end(), [](const Child &a, const Child &b) { return a.score > b.score; });
          sort(ch.begin(), ch.begin() + M, [](const Child &a, const Child &b) { return a.score != b.score ? a.score > b.score : a.state < b.state; });
          unordered_set<uint64_t> seen; seen.reserve(B * 2);
          vector<float> nsc; vector<uint64_t> nst; nsc.reserve(B); nst.reserve(B);
          for (size_t j = 0; j < M && nsc.size() < B; j++) if (seen.insert(ch[j].state).second) {
            nsc.push_back(ch[j].score); nst.push_back(ch[j].state); par[i].push_back(ch[j].parent); let[i].push_back(ch[j].letter); }
          sc.swap(nsc); st.swap(nst);
        }
        size_t nt = min(TOPN, sc.size());
        vector<Res> cand;
        for (size_t r = 0; r < nt; r++) {   // final beam is sorted by char score
          string p(N, '?'), k(N, '?'); size_t h = r;
          for (int i = N - 1; i >= 0; i--) { int pl = let[i][h]; p[i] = 'A' + pl; h = par[i][h]; }
          for (int i = 0; i < N; i++) { int cx = xi[ct[i] - 'A'], px = xi[p[i] - 'A'];
            int kx = cv.op == 0 ? cx - px : cv.op == 1 ? cx + px : px - cx; k[i] = X[((kx % 26) + 26) % 26]; }
          double lv = lmscore(p) + lmscore(k), w = wordscore(p) + wordscore(k);
          cand.push_back({cv.name, p, k, lv, w, lv + lam * w});
        }
        sort(cand.begin(), cand.end(), [](const Res &a, const Res &b) { return a.tot > b.tot; });
        if (PM > 0) {
          Cipher C{&ct, xi, &X, cv.op};
          int np_ = min<int>(PM, cand.size());
          for (int r = 0; r < np_; r++) { polish(C, cand[r].p, cand[r].k, lam, MAXPASS);
            cand[r].lmv = lmscore(cand[r].p) + lmscore(cand[r].k); cand[r].w = wordscore(cand[r].p) + wordscore(cand[r].k); cand[r].tot = cand[r].lmv + lam * cand[r].w; }
          sort(cand.begin(), cand.end(), [](const Res &a, const Res &b) { return a.tot > b.tot; });
        }
        // witness: re-encrypt
        for (auto &r : cand) for (int i = 0; i < N; i++) {
          int px = xi[r.p[i] - 'A'], kx = xi[r.k[i] - 'A'];
          int c = cv.op == 0 ? px + kx : cv.op == 1 ? kx - px : px - kx;
          if (X[((c % 26) + 26) % 26] != ct[i]) throw runtime_error("witness failed " + id);
        }
        best_per_conv.push_back(cand[0]);
        for (size_t r = 0; r < min<size_t>(3, cand.size()); r++) top_alts.push_back(cand[r]);
        fprintf(stderr, "R59 %s %s best %.2f (lm %.2f, w %.2f)\n", id.c_str(), cv.name.c_str(), cand[0].tot, cand[0].lmv, cand[0].w);
      }
      sort(best_per_conv.begin(), best_per_conv.end(), [](const Res &a, const Res &b) { return a.tot > b.tot; });
      sort(top_alts.begin(), top_alts.end(), [](const Res &a, const Res &b) { return a.tot > b.tot; });
      auto js = [](const Res &r) { char buf[64]; string s = "{\"convention\":\"" + r.conv + "\",\"plaintext\":\"" + r.p + "\",\"key\":\"" + r.k + "\"";
        snprintf(buf, sizeof buf, ",\"lm\":%.4f,\"word\":%.4f,\"total\":%.4f}", r.lmv, r.w, r.tot); return s + buf; };
      out << "{\"id\":\"" << id << "\",\"best\":" << js(best_per_conv[0]) << ",\"per_convention\":[";
      for (size_t j = 0; j < best_per_conv.size(); j++) out << (j ? "," : "") << js(best_per_conv[j]);
      out << "],\"top\":[";
      for (size_t j = 0; j < min<size_t>(8, top_alts.size()); j++) out << (j ? "," : "") << js(top_alts[j]);
      out << "]}\n"; out.flush();
    }
  } catch (const exception &e) { fprintf(stderr, "R59 ERROR %s\n", e.what()); return 1; }
}

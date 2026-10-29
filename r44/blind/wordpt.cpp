// R44 BLIND development solver. No K4 ciphertext, clue words, masks or plaintext input.
// Two FREE alphabets, key given: CA_index(c_i) - PA_index(p_i) = k_i (mod 26), as in R43.
// State = a complete pair of alphabets, so every state is an exact encryption witness (no constraint checks needed).
// Objective F = quadgram log10 score + LAMBDA * word score W (best segmentation into dictionary words, -7 per
// unmatched letter; ORTH model exact-word weights). Parallel tempering with four move types:
//   swap two cipher-alphabet positions; swap two plaintext-alphabet positions;
//   WORD placement: put dictionary word w at position s by re-arranging the plaintext alphabet (cipher side fixed)
//   or the cipher alphabet (plaintext side fixed) so that the decryption there reads w.
// Input TSV (R43 format): id<TAB>ciphertext<TAB>97 key digits (comma-separated); header line allowed.
// Output JSONL compatible with r43/sealed/evaluate.py.
// Usage: wordpt WORDS.tsv QUAD.f32 IN.tsv OUT.jsonl [REPLICAS=24] [SWEEPS=40000] [LAMBDA=1] [SEED=44]
#include <bits/stdc++.h>
using namespace std;
constexpr int N = 97;
static vector<float> Q;
struct Node { int nx[26]; float lp; };
static vector<Node> trie;
static vector<vector<string>> moveWords;   // proposal words by length (3..10), most frequent first
static void load_words(const string &path) {
    trie.assign(1, Node{}); memset(trie[0].nx, -1, sizeof trie[0].nx); trie[0].lp = -1e30f;
    ifstream f(path); if (!f) throw runtime_error("word model");
    string w; double ex, ed; vector<pair<double, string>> byLen[11];
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        int u = 0;
        for (char ch : w) {
            int c = ch - 'A'; if (c < 0 || c >= 26) { u = -1; break; }
            if (trie[u].nx[c] < 0) { trie[u].nx[c] = trie.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; trie.push_back(nd); }
            u = trie[u].nx[c];
        }
        if (u < 0) continue;
        trie[u].lp = max(trie[u].lp, (float)ex);
        if (w.size() >= 3 && w.size() <= 10) byLen[w.size()].push_back({ex, w});
    }
    moveWords.assign(11, {});
    for (int L = 3; L <= 10; L++) {
        sort(byLen[L].rbegin(), byLen[L].rend());
        for (size_t i = 0; i < byLen[L].size() && i < 600; i++) moveWords[L].push_back(byLen[L][i].second);
    }
}
static double wordscore(const int *p) {
    double dp[N + 1]; for (auto &d : dp) d = -1e30; dp[0] = 0;
    for (int i = 0; i < N; i++) {
        if (dp[i] < -1e29) continue;
        dp[i + 1] = max(dp[i + 1], dp[i] - 7);
        int u = 0;
        for (int j = i; j < N && j < i + 24; j++) { u = trie[u].nx[p[j]]; if (u < 0) break; if (trie[u].lp > -1e29) dp[j + 1] = max(dp[j + 1], dp[i] + trie[u].lp); }
    }
    return dp[N];
}
struct St { int tau[26], tinv[26], m[26], minv[26], p[N]; double q, w, f; };
int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: wordpt WORDS QUAD IN OUT [REPLICAS] [SWEEPS] [LAMBDA] [SEED]");
    int R = argc > 5 ? atoi(argv[5]) : 24; long SW = argc > 6 ? atol(argv[6]) : 40000; double lam = argc > 7 ? atof(argv[7]) : 1.0;
    uint64_t seed0 = argc > 8 ? stoull(argv[8]) : 44;
    load_words(argv[1]);
    Q.resize(456976); { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    ifstream in(argv[3]); ofstream out(argv[4]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id\t", 0) == 0) continue;
      stringstream ss(line); string id, ct, ks; getline(ss, id, '\t'); getline(ss, ct, '\t'); getline(ss, ks, '\t');
      vector<int> k; { for (char &ch : ks) if (ch == ',') ch = ' '; stringstream q(ks); int x; while (q >> x) k.push_back(x); }
      if ((int)ct.size() != N || (int)k.size() != N) throw runtime_error("bad input row " + id);
      int c[N]; for (int i = 0; i < N; i++) c[i] = ct[i] - 'A';
      uint64_t h = seed0; for (char ch : id) h = h * 1099511628211ull ^ (unsigned char)ch;
      mt19937_64 rng(h);
      auto U = [&]() { return (double)(rng() >> 11) / 9007199254740992.0; };
      auto rebuild = [&](St &s) {
        for (int i = 0; i < N; i++) { int x = s.tau[c[i]] - k[i]; x %= 26; if (x < 0) x += 26; s.p[i] = s.m[x]; }
        double qq = 0; for (int i = 0; i + 3 < N; i++) qq += Q[((s.p[i] * 26 + s.p[i + 1]) * 26 + s.p[i + 2]) * 26 + s.p[i + 3]];
        s.q = qq; s.w = wordscore(s.p); s.f = s.q + lam * s.w;
      };
      vector<double> T(R); for (int r = 0; r < R; r++) T[r] = 0.5 * pow(30.0, (double)r / max(1, R - 1));   // 0.5 .. 15
      vector<St> rep(R);
      for (auto &s : rep) {
        iota(s.tau, s.tau + 26, 0); shuffle(s.tau, s.tau + 26, rng); for (int i = 0; i < 26; i++) s.tinv[s.tau[i]] = i;
        iota(s.m, s.m + 26, 0); shuffle(s.m, s.m + 26, rng); for (int i = 0; i < 26; i++) s.minv[s.m[i]] = i;
        rebuild(s);
      }
      St best = rep[0]; long proposals = 0;
      for (long sw = 0; sw < SW; sw++) {
        for (int r = 0; r < R; r++) {
          St &s = rep[r];
          for (int mv = 0; mv < 20; mv++) {
            St old = s; double u = U(); proposals++;
            if (u < 0.3) { int a = rng() % 26, b = rng() % 26; if (a == b) continue; swap(s.tau[a], s.tau[b]); s.tinv[s.tau[a]] = a; s.tinv[s.tau[b]] = b; }
            else if (u < 0.6) { int a = rng() % 26, b = rng() % 26; if (a == b) continue; swap(s.m[a], s.m[b]); s.minv[s.m[a]] = a; s.minv[s.m[b]] = b; }
            else {
              int L = 3 + rng() % 8; const auto &ws = moveWords[L]; if (ws.empty()) continue;
              const string &w = ws[min<size_t>(ws.size() - 1, (size_t)(-log(1 - U()) * 120))];   // favour frequent words
              int st = rng() % (N - L + 1);
              if (u < 0.8) {   // plaintext-alphabet side: m[x_i] = w_j
                for (int j = 0; j < L; j++) {
                  int x = s.tau[c[st + j]] - k[st + j]; x %= 26; if (x < 0) x += 26;
                  int letter = w[j] - 'A', y = s.minv[letter];
                  if (y != x) { swap(s.m[x], s.m[y]); s.minv[s.m[x]] = x; s.minv[s.m[y]] = y; }
                }
              } else {         // cipher-alphabet side: tau[c_i] = PA_index(w_j) + k_i
                for (int j = 0; j < L; j++) {
                  int t = (s.minv[w[j] - 'A'] + k[st + j]) % 26, cc = c[st + j], c2 = s.tinv[t];
                  if (c2 != cc) { swap(s.tau[cc], s.tau[c2]); s.tinv[s.tau[cc]] = cc; s.tinv[s.tau[c2]] = c2; }
                }
              }
            }
            rebuild(s);
            double d = s.f - old.f;
            if (!(d >= 0 || exp(d / T[r]) > U())) s = old;
            if (s.f > best.f) best = s;
          }
        }
        for (int r = 0; r + 1 < R; r++) {
          double dl = (rep[r + 1].f - rep[r].f) * (1 / T[r] - 1 / T[r + 1]);
          if (dl >= 0 || exp(dl) > U()) swap(rep[r], rep[r + 1]);
        }
      }
      string plain(N, '?'), pa(26, '?'), ca(26, '?');
      for (int i = 0; i < N; i++) plain[i] = 'A' + best.p[i];
      for (int x = 0; x < 26; x++) pa[x] = 'A' + best.m[x];          // PA[position] = plaintext letter
      for (int t = 0; t < 26; t++) ca[t] = 'A' + best.tinv[t];       // CA[position] = cipher letter
      for (int i = 0; i < N; i++) if (ca[(pa.find(plain[i]) + k[i]) % 26] != ct[i]) throw runtime_error("witness check failed " + id);
      out << "{\"id\":\"" << id << "\",\"plaintext\":\"" << plain << "\",\"plaintext_alphabet\":\"" << pa << "\",\"ciphertext_alphabet\":\"" << ca
          << "\",\"score\":" << setprecision(10) << best.f << ",\"quadgram\":" << best.q << ",\"word\":" << best.w
          << ",\"proposals\":" << proposals << ",\"compatible\":" << proposals << "}\n";
      out.flush();
      cerr << "R44 " << id << " F " << best.f << " Q " << best.q << " W " << best.w << "\n";
    }
  } catch (const exception &e) { cerr << "R44 ERROR " << e.what() << "\n"; return 1; }
}

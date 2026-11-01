// R44b BLIND post-processor. No K4 data, clues, masks or truth.
// Reads the solver's answers (plaintext alphabet PA, cipher alphabet CA) and re-optimises the CIPHER alphabet by
// greedy pairwise swaps of its positions under F = quadgram score + LAMBDA * word score (best segmentation into exact
// ORTH words, -7 per unmatched letter), until no swap improves F. The plaintext alphabet is kept. Rare ciphertext
// letters, whose positions quadgrams barely constrain, are what this is for. Every output re-encrypts exactly.
// Usage: polish WORDS.tsv QUAD.f32 BLIND.tsv IN.jsonl OUT.jsonl [LAMBDA=1]
#include <bits/stdc++.h>
using namespace std;
constexpr int N = 97;
static vector<float> Q;
struct Node { int nx[26]; float lp; };
static vector<Node> trie;
static void load_words(const string &path) {
    trie.assign(1, Node{}); memset(trie[0].nx, -1, sizeof trie[0].nx); trie[0].lp = -1e30f;
    ifstream f(path); if (!f) throw runtime_error("word model");
    string w; double ex, ed;
    while (f >> w >> ex >> ed) {
        if (ex < -1e90 || w.size() > 24) continue;
        int u = 0; bool ok = true;
        for (char ch : w) {
            int c = ch - 'A'; if (c < 0 || c >= 26) { ok = false; break; }
            if (trie[u].nx[c] < 0) { trie[u].nx[c] = trie.size(); Node nd; memset(nd.nx, -1, sizeof nd.nx); nd.lp = -1e30f; trie.push_back(nd); }
            u = trie[u].nx[c];
        }
        if (ok) trie[u].lp = max(trie[u].lp, (float)ex);
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
static string field(const string &js, const string &key) {   // "key": "value" with optional spaces
    size_t a = js.find("\"" + key + "\""); if (a == string::npos) throw runtime_error("missing " + key);
    a = js.find(':', a); a = js.find('"', a); if (a == string::npos) throw runtime_error("bad " + key);
    a++; return js.substr(a, js.find('"', a) - a);
}
int main(int argc, char **argv) {
  try {
    if (argc < 6) throw runtime_error("usage: polish WORDS QUAD BLIND.tsv IN.jsonl OUT.jsonl [LAMBDA]");
    double lam = argc > 6 ? atof(argv[6]) : 1.0;
    load_words(argv[1]);
    Q.resize(456976); { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    map<string, pair<string, vector<int>>> data;
    { ifstream b(argv[3]); string l;
      while (getline(b, l)) {
        if (l.empty() || l.rfind("id\t", 0) == 0) continue;
        stringstream ss(l); string id, ct, ks; getline(ss, id, '\t'); getline(ss, ct, '\t'); getline(ss, ks, '\t');
        vector<int> k; for (char &ch : ks) if (ch == ',') ch = ' '; stringstream q(ks); int x; while (q >> x) k.push_back(x);
        data[id] = {ct, k};
      } }
    ifstream in(argv[4]); ofstream out(argv[5]); string js;
    while (getline(in, js)) {
      if (js.empty()) continue;
      string id = field(js, "id"), pa = field(js, "plaintext_alphabet"), ca = field(js, "ciphertext_alphabet");
      const string &ct = data.at(id).first; const vector<int> &k = data.at(id).second;
      int tau[26]; for (int t = 0; t < 26; t++) tau[ca[t] - 'A'] = t;      // cipher letter -> position
      int PA[26]; for (int x = 0; x < 26; x++) PA[x] = pa[x] - 'A';
      int p[N];
      auto F = [&]() {
        for (int i = 0; i < N; i++) { int x = (tau[ct[i] - 'A'] - k[i]) % 26; if (x < 0) x += 26; p[i] = PA[x]; }
        double q = 0; for (int i = 0; i + 3 < N; i++) q += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
        return q + lam * wordscore(p);
      };
      double f0 = F(), f = f0; int swaps = 0;
      for (bool improved = true; improved;) {
        improved = false;
        for (int a = 0; a < 26; a++) for (int b = a + 1; b < 26; b++) {
          swap(tau[a], tau[b]);
          double g = F();
          if (g > f + 1e-9) { f = g; improved = true; swaps++; } else swap(tau[a], tau[b]);
        }
      }
      F();
      string plain(N, '?'), nca(26, '?');
      for (int i = 0; i < N; i++) plain[i] = 'A' + p[i];
      for (int c = 0; c < 26; c++) nca[tau[c]] = 'A' + c;
      for (int i = 0; i < N; i++) if (nca[(pa.find(plain[i]) + k[i]) % 26] != ct[i]) throw runtime_error("witness check failed " + id);
      out << "{\"id\":\"" << id << "\",\"plaintext\":\"" << plain << "\",\"plaintext_alphabet\":\"" << pa << "\",\"ciphertext_alphabet\":\"" << nca
          << "\",\"score\":" << setprecision(10) << f << ",\"score_before\":" << f0 << ",\"polish_swaps\":" << swaps
          << ",\"proposals\":0,\"compatible\":0}\n";
      cerr << "R44b " << id << " F " << f0 << " -> " << f << " swaps " << swaps << "\n";
    }
  } catch (const exception &e) { cerr << "R44b ERROR " << e.what() << "\n"; return 1; }
}

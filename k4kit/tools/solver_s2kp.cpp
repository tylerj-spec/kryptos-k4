// solver_s2kp (Claude R21/R26/R28; toolkit copy). English search for ONE fixed key sequence with BOTH substitution
// alphabets unknown, the clue letters enforced exactly (crib-graph components), and an optional rearrangement.
// Model: c_j = CA[(PA^-1(x_j) + k_j) mod 26]; if PERM is given, plaintext P[perm[j]] = x_j (rearrange-then-substitute);
// "-" means x is already in plaintext order. Built on the move set of ChatGPT's R7/R20 solver.cpp (component
// offsets, free-letter swaps, group shifts) with: quadgram term lambda*Q in the annealing objective (lambda falls
// linearly LAM0 -> LAM_END); a deterministic polish after every restart; rows report W (word score), Q, objective.
// History: R21 "S2" (Gromark primer input) == R26 "S2k" (explicit key) == this with PERM "-" (rows verified identical
// with g++/libstdc++; other standard libraries change std::shuffle and the random stream, so results differ there).
// Build:  g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
// Usage:  bin/solver_s2kp MODEL.tsv QUAD.f32 INPUT OUTPUT RESTARTS PROPOSALS LAM0 LAM_END
//         INPUT lines: ID KEY97 CT97 MASK97 SEED PERM   (KEY letters A=0..Z=25; MASK '?' = unknown; PERM '-' or j-list)
// Standard budget: 64 restarts x 40000 proposals, LAM0 0.05, LAM_END 0  (about 3.5 s per line on one core).
// Output JSONL, one row per restart: id, restart, W, Q, obj, plaintext (plaintext order), plaintext_alphabet,
// ciphertext_alphabet. Select the best restart per id by W.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr double NEG = -1e100;
constexpr int N = 97;
int md(int x) { x %= 26; return x < 0 ? x + 26 : x; }
struct TrieNode { array<int, 26> next; double exact = NEG, edit = NEG; TrieNode() { next.fill(-1); } };
struct Model {
  vector<TrieNode> trie;
  explicit Model(const string &path) {
    ifstream in(path); if (!in) throw runtime_error("model"); trie.emplace_back();
    string w; double ex, ed;
    while (in >> w >> ex >> ed) {
      int u = 0;
      for (char ch : w) { int c = ch - 'A'; if (c < 0 || c >= 26) throw runtime_error("token");
        int v = trie[u].next[c]; if (v < 0) { v = trie.size(); trie[u].next[c] = v; trie.emplace_back(); } u = v; }
      trie[u].exact = ex; trie[u].edit = ed;
    }
  }
  double score(const array<int, N> &p) const {
    double dp[N + 1][3]; for (auto &r : dp) for (double &v : r) v = NEG; dp[0][0] = 0;
    for (int i = 0; i < N; i++) {
      for (int b = 0; b < 3; b++) dp[i + 1][b] = max(dp[i + 1][b], dp[i][b] - 7.0);
      int u = 0;
      for (int j = i; j < min(N, i + 24); j++) {
        u = trie[u].next[p[j]]; if (u < 0) break;
        double ex = trie[u].exact, ed = trie[u].edit;
        if (ex > NEG / 2) for (int b = 0; b < 3; b++) dp[j + 1][b] = max(dp[j + 1][b], dp[i][b] + ex);
        if (ed > NEG / 2) for (int b = 0; b < 2; b++) dp[j + 1][b + 1] = max(dp[j + 1][b + 1], dp[i][b] + ed);
      }
    }
    return max({dp[N][0], dp[N][1], dp[N][2]});
  }
};
vector<float> QT;
double qscore(const array<int, N> &p) {
  double s = 0; for (int i = 0; i + 3 < N; i++) s += QT[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]]; return s;
}
struct State { array<int, 26> a, b; };
struct Fixture {
  string id, ct, mask; int primer;
  array<int, N> k, c; array<int, 52> pot, gid;
  vector<vector<int>> groups; array<vector<int>, 2> free_nodes; vector<int> perm;
  Fixture(string id_, const string &key, string ct_, string mask_) : id(id_), ct(ct_), mask(mask_), primer(0) {
    if ((int)key.size() != N) throw runtime_error("key length");
    for (int i = 0; i < N; i++) k[i] = key[i] - 'A';
    vector<pair<int, int>> adj[52];
    for (int i = 0; i < N; i++) {
      c[i] = ct[i] - 'A';
      if (mask[i] != '?') { int u = mask[i] - 'A', v = c[i] + 26; adj[u].push_back({v, k[i]}); adj[v].push_back({u, -k[i]}); }
    }
    gid.fill(-1); pot.fill(0); array<bool, 52> seen{};
    for (int root = 0; root < 52; root++) {
      if (seen[root]) continue;
      if (adj[root].empty()) { seen[root] = true; free_nodes[root / 26].push_back(root % 26); continue; }
      vector<int> q{root}; seen[root] = true;
      for (size_t idx = 0; idx < q.size(); idx++) {
        int u = q[idx];
        for (auto [v, delta] : adj[u]) { int pv = md(pot[u] + delta);
          if (seen[v]) { if (pot[v] != pv) throw runtime_error("inconsistent graph"); }
          else { seen[v] = true; pot[v] = pv; q.push_back(v); } }
      }
      groups.push_back(q);
    }
    stable_sort(groups.begin(), groups.end(), [](const vector<int> &a, const vector<int> &b) { return a.size() > b.size(); });
    for (int j = 0; j < (int)groups.size(); j++) for (int u : groups[j]) gid[u] = j;
  }
  array<int, N> plain(const State &s) const {
    auto x = decrypt(s); if (perm.empty()) return x;
    array<int, N> q; for (int j = 0; j < N; j++) q[perm[j]] = x[j]; return q;
  }
  array<int, N> decrypt(const State &s) const {
    array<int, 26> inv; for (int x = 0; x < 26; x++) inv[s.a[x]] = x;
    array<int, N> p; for (int i = 0; i < N; i++) p[i] = inv[md(s.b[c[i]] - k[i])]; return p;
  }
  bool valid(const State &s) const {
    unsigned a = 0, b = 0;
    for (int i = 0; i < 26; i++) { a |= 1u << s.a[i]; b |= 1u << s.b[i]; }
    if (a != (1u << 26) - 1 || b != (1u << 26) - 1) return false;
    auto p = decrypt(s); for (int i = 0; i < N; i++) if (mask[i] != '?' && p[i] != mask[i] - 'A') return false; return true;
  }
  bool initrec(int j, unsigned am, unsigned bm, State &s, mt19937_64 &rng) const {
    if (j == (int)groups.size()) {
      for (int side = 0; side < 2; side++) {
        auto &arr = side ? s.b : s.a; unsigned used = side ? bm : am; vector<int> rem;
        for (int x = 0; x < 26; x++) if (!(used & (1u << x))) rem.push_back(x);
        shuffle(rem.begin(), rem.end(), rng);
        for (size_t n = 0; n < rem.size(); n++) arr[free_nodes[side][n]] = rem[n];
      }
      return true;
    }
    array<int, 26> sh; iota(sh.begin(), sh.end(), 0); if (j) shuffle(sh.begin(), sh.end(), rng);
    for (int q = 0; q < (j ? 26 : 1); q++) {
      int off = sh[q]; unsigned ma = 0, mb = 0; bool good = true;
      for (int u : groups[j]) { unsigned bit = 1u << md(pot[u] + off); unsigned &mm = u < 26 ? ma : mb; unsigned used = u < 26 ? am : bm;
        if ((mm | used) & bit) { good = false; break; } mm |= bit; }
      if (!good) continue;
      for (int u : groups[j]) (u < 26 ? s.a[u] : s.b[u - 26]) = md(pot[u] + off);
      if (initrec(j + 1, am | ma, bm | mb, s, rng)) return true;
    }
    return false;
  }
  // shift groups g1 (and g2 >= 0) to offsets o1, o2, relocating displaced free letters into the vacated cells
  bool shift(const State &old, State &out, int g1, int o1, int g2, int o2, mt19937_64 *rng) const {
    out = old; array<int, 2> sel{g1, g2}; array<int, 2> off{o1, o2};
    for (int side = 0; side < 2; side++) {
      const auto &oa = side ? old.b : old.a; auto &arr = side ? out.b : out.a;
      unsigned om = 0, nm = 0; array<int, 26> holder; for (int x = 0; x < 26; x++) holder[oa[x]] = x;
      vector<pair<int, int>> ch;
      for (int h = 0; h < 2; h++) if (sel[h] >= 0) for (int u : groups[sel[h]]) if (u / 26 == side) {
        int letter = u % 26, target = md(pot[u] + off[h]), occ = holder[target], og = gid[side * 26 + occ];
        if (og >= 0 && og != g1 && og != g2) return false;
        if (nm & (1u << target)) return false;
        nm |= 1u << target; om |= 1u << oa[letter]; ch.push_back({letter, target});
      }
      vector<int> holes, disp;
      for (int r = 0; r < 26; r++) {
        if ((om & (1u << r)) && !(nm & (1u << r))) holes.push_back(r);
        if ((nm & (1u << r)) && !(om & (1u << r))) disp.push_back(holder[r]);
      }
      if (rng) shuffle(holes.begin(), holes.end(), *rng);
      for (size_t j = 0; j < holes.size(); j++) arr[disp[j]] = holes[j];
      for (auto [l, t] : ch) arr[l] = t;
    }
    return true;
  }
  bool mutate(const State &old, State &out, mt19937_64 &rng) const {
    int kind = rng() % 100;
    if (kind < 70 || groups.size() < 2) {
      out = old; int side = rng() % 2; if (free_nodes[side].size() < 2) side = 1 - side; if (free_nodes[side].size() < 2) return false;
      auto &ls = free_nodes[side]; int i = rng() % ls.size(), j = rng() % (ls.size() - 1); if (j >= i) j++;
      auto &arr = side ? out.b : out.a; swap(arr[ls[i]], arr[ls[j]]); return true;
    }
    int g1 = 1 + rng() % (groups.size() - 1), g2 = -1;
    if (kind >= 90 && groups.size() > 2) { g2 = 1 + rng() % (groups.size() - 2); if (g2 >= g1) g2++; }
    int o1 = rng() % 26, o2 = rng() % 26;
    return shift(old, out, g1, o1, g2, o2, &rng);
  }
};
string text(const array<int, N> &p) { string s; for (int x : p) s += char('A' + x); return s; }
string alphabet(const array<int, 26> &a) { string s(26, '?'); for (int i = 0; i < 26; i++) s[a[i]] = char('A' + i); return s; }
int main(int argc, char **argv) {
  try {
    if (argc != 9) throw runtime_error("usage: solver_s2kp MODEL QUAD INPUT OUTPUT RESTARTS PROPOSALS LAM0 LAM_END");
    Model model(argv[1]);
    { ifstream q(argv[2], ios::binary); QT.resize(456976); q.read((char *)QT.data(), 456976 * 4); if (!q) throw runtime_error("quad"); }
    ifstream in(argv[3]); ofstream out(argv[4]); out << setprecision(10);
    int R = stoi(argv[5]), T = stoi(argv[6]); double L0 = stod(argv[7]), L1 = stod(argv[8]);
    string id, key, ct, mask, ps; unsigned long long seed;
    while (in >> id >> key >> ct >> mask >> seed >> ps) {
      Fixture f(id, key, ct, mask);
      if (ps != "-") { size_t a = 0; while (a < ps.size()) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size();
          f.perm.push_back(stoi(ps.substr(a, b - a))); a = b + 1; }
        if ((int)f.perm.size() != N) throw runtime_error("perm length");
        vector<int> chk(f.perm); sort(chk.begin(), chk.end()); for (int i = 0; i < N; i++) if (chk[i] != i) throw runtime_error("not a permutation"); } mt19937_64 rng(seed); uniform_real_distribution<double> U(0, 1);
      vector<double> temps(T); for (int t = 0; t < T; t++) temps[t] = 6.0 * pow(0.15 / 6.0, double(t) / (T - 1));
      for (int r = 0; r < R; r++) {
        State s; if (!f.initrec(0, 0, 0, s, rng)) throw runtime_error("init");
        auto obj = [&](const State &x, double lam, double &W, double &Q) { auto p = f.plain(x); W = model.score(p); Q = qscore(p); return W + lam * Q; };
        double W, Q, sc = obj(s, L0, W, Q);
        for (int t = 0; t < T; t++) {
          double lam = L0 + (L1 - L0) * double(t) / (T - 1);
          State cand; if (!f.mutate(s, cand, rng)) continue;
          double w2, q2, ns = obj(cand, lam, w2, q2);
          if (t % 2048 == 0) sc = obj(s, lam, W, Q);  // keep the current objective in step with lambda
          if (ns >= sc || log(max(U(rng), 1e-300)) < (ns - sc) / temps[t]) { s = cand; sc = ns; }
        }
        // polish at lambda = L1
        State best = s; double bw, bq, bs = obj(best, L1, bw, bq);
        for (bool improved = true; improved;) {
          improved = false;
          for (int side = 0; side < 2; side++) {
            auto &ls = f.free_nodes[side];
            for (size_t i = 0; i < ls.size(); i++) for (size_t j = i + 1; j < ls.size(); j++) {
              State c2 = best; auto &arr = side ? c2.b : c2.a; swap(arr[ls[i]], arr[ls[j]]);
              double w2, q2, v = obj(c2, L1, w2, q2); if (v > bs + 1e-9) { best = c2; bs = v; bw = w2; bq = q2; improved = true; }
            }
          }
          for (int g = 1; g < (int)f.groups.size(); g++) for (int o = 0; o < 26; o++) {
            State c2; if (!f.shift(best, c2, g, o, -1, 0, nullptr)) continue;
            double w2, q2, v = obj(c2, L1, w2, q2); if (v > bs + 1e-9) { best = c2; bs = v; bw = w2; bq = q2; improved = true; }
          }
        }
        if (!f.valid(best)) throw runtime_error("invalid result");
        out << "{\"id\":\"" << id << "\",\"restart\":" << r << ",\"W\":" << bw << ",\"Q\":" << bq << ",\"obj\":" << bs
            << ",\"plaintext\":\"" << text(f.plain(best)) << "\",\"plaintext_alphabet\":\"" << alphabet(best.a)
            << "\",\"ciphertext_alphabet\":\"" << alphabet(best.b) << "\"}\n";
      }
      out.flush();
    }
  } catch (const exception &e) { cerr << "ERROR: " << e.what() << "\n"; return 1; }
  return 0;
}

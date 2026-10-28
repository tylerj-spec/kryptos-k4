// strictblind BLIND scanner. NO known plaintext, clue positions or masks anywhere in this program.
// For every route-order x key x 12 fixed conventions it decrypts all 97 letters of the ciphertext and scores
// English quadgrams; keeps the top 100 and the best score per route-order. Generalises R32 blind_route_scan.cpp
// (identical decryption and scoring; key families are now parameters).
// Conventions: plaintext alphabet PA and ciphertext alphabet CA each AZ or KRYPTOS; operation VIG c = p + k,
// BEAU c = k - p, VARB c = p - k (ranks in the respective alphabets). Route orders as in R27/R32:
//   ID: no rearrangement; S_then_T: CT[j] = X[perm[j]], X[i] = sub(P[i], k_i); T_then_S: CT[j] = sub(P[perm[j]], k_j).
// Keys: TEXT <file> = every 97-letter window of the text, forward and reversed, key letters numbered AZ or KRYPTOS;
//       CHAIN <b>   = b-digit chain addition k_i = k_{i-b} + k_{i-b+1} mod 10, all 10^b primers.
//       CHAINBASE <base>,<b> = the same recurrence modulo a declared base 2..26, base^b primers.
//       CHAINALPH <base>,<b> = the same stream with two additional keyed alphabets, PALIMPSEST and ABSCISSA.
// Build: g++ -std=c++17 -O3 -march=native scan.cpp -o scan
// Usage: scan TEXT|CHAIN FILE|B LABEL CT.txt QUAD.f32 ROUTES.txt LO HI OUT_TOP.tsv OUT_ROUTES.tsv
#include <algorithm>
#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N = 97, TOP = 100;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
const char *OPN[3] = {"VIG", "BEAU", "VARB"};
struct Hit { double s; string setting, plain; };
struct Cmp { bool operator()(const Hit &a, const Hit &b) const { return a.s != b.s ? a.s > b.s : a.setting < b.setting; } };
string letters(const string &f) { ifstream in(f, ios::binary); if (!in) throw runtime_error("no file " + f);
  string s((istreambuf_iterator<char>(in)), {});
  for (char &c : s) if (c >= 'a' && c <= 'z') c = char(c - 'a' + 'A');
  s.erase(remove_if(s.begin(), s.end(), [](char c) { return c < 'A' || c > 'Z'; }), s.end()); return s; }
int main(int argc, char **argv) {
  try {
    if (argc != 11) throw runtime_error("usage: scan TEXT|CHAIN FILE|B LABEL CT QUAD ROUTES LO HI OUT_TOP OUT_ROUTES");
    string kind = argv[1], karg = argv[2], label = argv[3], ct = letters(argv[4]);
    if (ct.size() != N) throw runtime_error("ciphertext must have 97 letters");
    vector<float> Q(456976);
    { ifstream f(argv[5], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    int lo = stoi(argv[7]), hi = stoi(argv[8]);
    vector<string> names, orders; vector<array<int, N>> srcidx, kidx;
    { ifstream rf(argv[6]); if (!rf) throw runtime_error("routes"); string line; int idx = 0;
      while (getline(rf, line)) {
        if (line.empty()) continue;
        if (idx >= lo && idx < hi) {
          istringstream is(line); string nm, od, ps; is >> nm >> od >> ps;
          array<int, N> perm{}; int j = 0; size_t a = 0;
          while (a < ps.size() && j < N) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); perm[j++] = stoi(ps.substr(a, b - a)); a = b + 1; }
          array<int, N> q{}; vector<int> seen(N, 0);
          for (int t = 0; t < N; t++) { if (j != N || perm[t] < 0 || perm[t] >= N || seen[perm[t]]++) throw runtime_error("bad permutation: " + nm); q[perm[t]] = t; }
          array<int, N> s{}, k{};
          for (int t = 0; t < N; t++) {
            if (od == "ID") { s[t] = t; k[t] = t; }
            else if (od == "S_then_T") { s[t] = q[t]; k[t] = t; }
            else if (od == "T_then_S") { s[t] = q[t]; k[t] = q[t]; }
            else throw runtime_error("order " + od);
          }
          names.push_back(nm); orders.push_back(od); srcidx.push_back(s); kidx.push_back(k);
        }
        idx++;
      } }
    // keys are generated on the fly (key-outer loop), so memory stays small for any key family
    string src; int b = 0, base = 10; long long lim = 1;
    if (kind == "TEXT") {
      src = letters(karg);
      if (src.size() < (size_t)N) throw runtime_error("text too short");
    } else if (kind == "CHAIN" || kind == "CHAINBASE" || kind == "CHAINALPH") {
      if (kind == "CHAIN") b = stoi(karg);
      else {
        size_t sep = karg.find(',');
        if (sep == string::npos) throw runtime_error("CHAINBASE requires BASE,LENGTH");
        base = stoi(karg.substr(0, sep)); b = stoi(karg.substr(sep + 1));
      }
      if (b < 2 || b > 8 || base < 2 || base > 26) throw runtime_error("base 2..26, chain length 2..8");
      for (int i = 0; i < b; i++) {
        lim *= base;
        if ((kind == "CHAINBASE" || kind == "CHAINALPH") && lim > 20000000) throw runtime_error("CHAINBASE primer cap 20 million");
      }
    } else throw runtime_error("key kind");
    const string AL[4] = {AZ, KRY, "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"};
    const string AN[4] = {"AZ", "KRY", "PAL", "ABS"};
    const int A = kind == "CHAINALPH" ? 4 : 2;
    int cmap[4][26], pmap[4][26];
    for (int h = 0; h < A; h++) {
      if (AL[h].size() != 26) throw runtime_error("alphabet length");
      bool seen[26]{};
      for (int i = 0; i < 26; i++) {
        int c = AL[h][i] - 'A';
        if (c < 0 || c >= 26 || seen[c]) throw runtime_error("alphabet is not a permutation");
        seen[c] = true; cmap[h][c] = i; pmap[h][i] = c;
      }
    }
    size_t R = names.size();
    vector<array<int, N>> cv[4];
    for (int ca = 0; ca < A; ca++) {
      cv[ca].resize(R);
      for (size_t r = 0; r < R; r++) for (int t = 0; t < N; t++)
        cv[ca][r][t] = cmap[ca][ct[srcidx[r][t]] - 'A'];
    }
    vector<double> rbest(R, -1e300);
    priority_queue<Hit, vector<Hit>, Cmp> best;
    long long count = 0;
    auto run_key = [&](const array<int, N> &K, const string &kn) {
      for (size_t r = 0; r < R; r++) {
        int kk[N]; for (int t = 0; t < N; t++) kk[t] = K[kidx[r][t]];
        for (int ca = 0; ca < A; ca++) {
          const auto &cvals = cv[ca][r];
          for (int op = 0; op < 3; op++) {
            int idxs[N];
            for (int t = 0; t < N; t++) { int x = op == 0 ? cvals[t] - kk[t] : op == 1 ? kk[t] - cvals[t] : cvals[t] + kk[t]; x %= 26; idxs[t] = x < 0 ? x + 26 : x; }
            for (int pa = 0; pa < A; pa++) {
              int v[N]; for (int t = 0; t < N; t++) v[t] = pmap[pa][idxs[t]];
              double sc = 0; for (int t = 3; t < N; t++) sc += Q[((v[t - 3] * 26 + v[t - 2]) * 26 + v[t - 1]) * 26 + v[t]];
              count++;
              if (sc > rbest[r]) rbest[r] = sc;
              if ((int)best.size() < TOP || sc >= best.top().s) {
                string pl(N, 'A'); for (int t = 0; t < N; t++) pl[t] = char('A' + v[t]);
                Hit h{sc, label + "|" + names[r] + "|" + orders[r] + "|" + kn + "|PA=" + AN[pa] + "|CA=" + AN[ca] + "|OP=" + OPN[op], pl};
                if ((int)best.size() < TOP) best.push(h);
                else if (Cmp()(h, best.top())) { best.pop(); best.push(h); }
              }
            }
          }
        }
      }
    };
    array<int, N> K{};
    if (kind == "TEXT") {
      for (int dir = 0; dir < 2; dir++) {
        string s = dir ? string(src.rbegin(), src.rend()) : src;
        for (int num = 0; num < 2; num++) {
          const string &al = num ? KRY : AZ; int pos[26]; for (int i = 0; i < 26; i++) pos[al[i] - 'A'] = i;
          for (size_t off = 0; off + N <= s.size(); off++) {
            for (int i = 0; i < N; i++) K[i] = pos[s[off + i] - 'A'];
            run_key(K, string(dir ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off));
          }
        }
      }
    } else {
      const string symbols = "0123456789ABCDEFGHIJKLMNOP";
      for (long long p = 0; p < lim; p++) {
        long long v = p; string primer(b, '0');
        for (int i = b - 1; i >= 0; i--) {
          K[i] = int(v % base); primer[i] = symbols[K[i]]; v /= base;
        }
        for (int i = b; i < N; i++) K[i] = (K[i - b] + K[i - b + 1]) % base;
        run_key(K, "primer" + primer);
      }
    }
    ofstream ro(argv[10]); ro << setprecision(10) << "route\torder\tbest_score\n";
    for (size_t r = 0; r < R; r++) ro << names[r] << "\t" << orders[r] << "\t" << rbest[r] << "\n";
    vector<Hit> rows; while (!best.empty()) { rows.push_back(best.top()); best.pop(); }
    sort(rows.begin(), rows.end(), [](const Hit &a, const Hit &b) { return a.s != b.s ? a.s > b.s : a.setting < b.setting; });
    ofstream o(argv[9]); o << setprecision(10) << "score\tsetting\tplaintext\n";
    for (auto &h : rows) o << h.s << "\t" << h.setting << "\t" << h.plain << "\n";
    cerr << "BLIND " << label << " routes " << names.size() << " decryptions " << count << " top " << (rows.empty() ? 0 : rows[0].s) << "\n";
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
  return 0;
}

// R32 BLIND scanner (Claude Code). NO clue letters, positions or masks anywhere in this program.
// Reads: ciphertext (97 A-Z), quadgram table, key source text (A-Z) or '-', route file, route index range.
// For every route-order x key x 12 fixed conventions it decrypts all 97 letters and scores English quadgrams.
// Writes the top 100 (TSV) and the best score per route (TSV).
// Build: g++ -std=c++17 -O3 -march=native blind_route_scan.cpp -o blind_route_scan
// Usage: blind_route_scan CARTER|K1K3|G5|C6 CT.txt QUAD.f32 SOURCE.txt|- ROUTES.txt LO HI OUT_TOP.tsv OUT_ROUTES.tsv
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
vector<float> Q;
struct Hit { double s; string setting, plain; };
struct Cmp { bool operator()(const Hit &a, const Hit &b) const { return a.s > b.s; } };
string slurp(const string &f) { ifstream in(f, ios::binary); if (!in) throw runtime_error("no file " + f);
  string s((istreambuf_iterator<char>(in)), {}); s.erase(remove_if(s.begin(), s.end(), [](char c) { return c < 'A' || c > 'Z'; }), s.end()); return s; }
int main(int argc, char **argv) {
  try {
    if (argc != 10) throw runtime_error("usage: FAMILY CT QUAD SOURCE|- ROUTES LO HI OUT_TOP OUT_ROUTES");
    string fam = argv[1], ct = slurp(argv[2]);
    if (ct.size() != N) throw runtime_error("ciphertext must have 97 letters");
    { ifstream f(argv[3], ios::binary); Q.resize(456976); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    string src = (fam == "CARTER" || fam == "K1K3") ? slurp(argv[4]) : "";
    int lo = stoi(argv[6]), hi = stoi(argv[7]);
    vector<string> names, orders; vector<array<int, N>> srcidx, kidx;
    { ifstream rf(argv[5]); string line; int idx = 0;
      while (getline(rf, line)) {
        if (idx >= lo && idx < hi) {
          istringstream is(line); string nm, od, ps; is >> nm >> od >> ps;
          array<int, N> perm{}; int j = 0; size_t a = 0;
          while (a < ps.size()) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); perm[j++] = stoi(ps.substr(a, b - a)); a = b + 1; }
          if (j != N) throw runtime_error("perm length");
          array<int, N> q{}; for (int t = 0; t < N; t++) q[perm[t]] = t;   // q = inverse permutation
          array<int, N> s{}, k{};
          for (int t = 0; t < N; t++) {
            if (od == "ID") { s[t] = t; k[t] = t; }
            else if (od == "S_then_T") { s[t] = q[t]; k[t] = t; }          // P[t] = dec(CT[q[t]], k_t)
            else if (od == "T_then_S") { s[t] = q[t]; k[t] = q[t]; }       // P[perm[j]] = dec(CT[j], k_j)
            else throw runtime_error("order");
          }
          names.push_back(nm); orders.push_back(od); srcidx.push_back(s); kidx.push_back(k);
        }
        idx++;
      } }
    // key list
    vector<array<int, N>> keys; vector<string> kname;
    if (fam == "CARTER" || fam == "K1K3") {
      for (int dir = 0; dir < 2; dir++) {
        string s = dir ? string(src.rbegin(), src.rend()) : src;
        for (int num = 0; num < 2; num++) {
          const string &al = num ? KRY : AZ; int pos[26]; for (int i = 0; i < 26; i++) pos[al[i] - 'A'] = i;
          for (size_t off = 0; off + N <= s.size(); off++) {
            array<int, N> k; for (int i = 0; i < N; i++) k[i] = pos[s[off + i] - 'A'];
            keys.push_back(k); kname.push_back(string(dir ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off));
          }
        }
      }
    } else if (fam == "G5" || fam == "C6") {
      int b = fam == "G5" ? 5 : 6, lim = fam == "G5" ? 100000 : 1000000;
      for (int p = 0; p < lim; p++) {
        array<int, N> k{}; int v = p; for (int i = b - 1; i >= 0; i--) { k[i] = v % 10; v /= 10; }
        for (int i = b; i < N; i++) k[i] = (k[i - b] + k[i - b + 1]) % 10;
        keys.push_back(k); ostringstream o; o << "primer" << setw(b) << setfill('0') << p; kname.push_back(o.str());
      }
    } else throw runtime_error("family");
    int cmap[2][26], pmap[2][26];
    for (int h = 0; h < 2; h++) { const string &al = h ? KRY : AZ; for (int i = 0; i < 26; i++) { cmap[h][al[i] - 'A'] = i; pmap[h][i] = al[i] - 'A'; } }
    priority_queue<Hit, vector<Hit>, Cmp> best;
    ofstream ro(argv[9]); ro << setprecision(10) << "route\torder\tbest_score\n";
    long long count = 0;
    for (size_t r = 0; r < names.size(); r++) {
      double rbest = -1e300;
      for (int ca = 0; ca < 2; ca++) {
        int cvals[N]; for (int t = 0; t < N; t++) cvals[t] = cmap[ca][ct[srcidx[r][t]] - 'A'];
        for (size_t ki = 0; ki < keys.size(); ki++) {
          const auto &K = keys[ki]; int kk[N]; for (int t = 0; t < N; t++) kk[t] = K[kidx[r][t]];
          for (int op = 0; op < 3; op++) {
            int idxs[N];
            for (int t = 0; t < N; t++) { int x = op == 0 ? cvals[t] - kk[t] : op == 1 ? kk[t] - cvals[t] : cvals[t] + kk[t]; x %= 26; idxs[t] = x < 0 ? x + 26 : x; }
            for (int pa = 0; pa < 2; pa++) {
              int v[N]; for (int t = 0; t < N; t++) v[t] = pmap[pa][idxs[t]];
              double sc = 0; for (int t = 3; t < N; t++) sc += Q[((v[t - 3] * 26 + v[t - 2]) * 26 + v[t - 1]) * 26 + v[t]];
              count++;
              if (sc > rbest) rbest = sc;
              if ((int)best.size() < TOP || sc > best.top().s) {
                string pl(N, 'A'); for (int t = 0; t < N; t++) pl[t] = char('A' + v[t]);
                Hit h{sc, fam + "|" + names[r] + "|" + orders[r] + "|" + kname[ki] + "|PA=" + (pa ? "KRY" : "AZ") + "|CA=" + (ca ? "KRY" : "AZ") + "|OP=" + OPN[op], pl};
                if ((int)best.size() >= TOP) best.pop();
                best.push(h);
              }
            }
          }
        }
      }
      ro << names[r] << "\t" << orders[r] << "\t" << rbest << "\n";
    }
    vector<Hit> rows; while (!best.empty()) { rows.push_back(best.top()); best.pop(); }
    sort(rows.begin(), rows.end(), [](const Hit &a, const Hit &b) { return a.s != b.s ? a.s > b.s : a.setting < b.setting; });
    ofstream o(argv[8]); o << setprecision(10) << "score\tsetting\tplaintext\n";
    for (auto &h : rows) o << h.s << "\t" << h.setting << "\t" << h.plain << "\n";
    cerr << "BLIND " << fam << " routes " << names.size() << " decryptions " << count << " top " << (rows.empty() ? 0 : rows[0].s) << "\n";
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
  return 0;
}

// SEALED (run only after the freeze): for every setting of a family, count how many of the 24 known plaintext letters
// the fixed-method decryption reproduces. Usage as blind_route_scan, minus the output files: FAMILY CT SOURCE ROUTES LO HI
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
constexpr int N = 97;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
string slurp(const string &f) { ifstream in(f); string s((istreambuf_iterator<char>(in)), {});
  s.erase(remove_if(s.begin(), s.end(), [](char c) { return c < 'A' || c > 'Z'; }), s.end()); return s; }
int main(int argc, char **argv) {
  string fam = argv[1], ct = slurp(argv[2]), src = (fam == "CARTER" || fam == "K1K3") ? slurp(argv[3]) : "";
  int lo = stoi(argv[5]), hi = stoi(argv[6]);
  vector<int> pos; string want;
  for (int i = 0; i < 13; i++) { pos.push_back(21 + i); want += string("EASTNORTHEAST")[i]; }
  for (int i = 0; i < 11; i++) { pos.push_back(63 + i); want += string("BERLINCLOCK")[i]; }
  vector<vector<array<int, 2>>> R; vector<string> names;
  { ifstream rf(argv[4]); string line; int idx = 0;
    while (getline(rf, line)) { if (idx >= lo && idx < hi) {
        istringstream is(line); string nm, od, ps; is >> nm >> od >> ps; array<int, N> perm{}; int j = 0; size_t a = 0;
        while (a < ps.size()) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); perm[j++] = stoi(ps.substr(a, b - a)); a = b + 1; }
        array<int, N> q{}; for (int t = 0; t < N; t++) q[perm[t]] = t;
        vector<array<int, 2>> m; for (int t : pos) m.push_back({od == "ID" ? t : q[t], od == "T_then_S" ? q[t] : t});
        R.push_back(m); names.push_back(nm + "|" + od); }
      idx++; } }
  vector<array<int, N>> keys; vector<string> kname;
  if (!src.empty()) { for (int dir = 0; dir < 2; dir++) { string s = dir ? string(src.rbegin(), src.rend()) : src;
      for (int num = 0; num < 2; num++) { const string &al = num ? KRY : AZ; int p[26]; for (int i = 0; i < 26; i++) p[al[i] - 'A'] = i;
        for (size_t off = 0; off + N <= s.size(); off++) { array<int, N> k; for (int i = 0; i < N; i++) k[i] = p[s[off + i] - 'A'];
          keys.push_back(k); kname.push_back(string(dir ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off)); } } } }
  else { int b = fam == "G5" ? 5 : 6, lim = fam == "G5" ? 100000 : 1000000;
    for (int p = 0; p < lim; p++) { array<int, N> k{}; int v = p; for (int i = b - 1; i >= 0; i--) { k[i] = v % 10; v /= 10; }
      for (int i = b; i < N; i++) k[i] = (k[i - b] + k[i - b + 1]) % 10; keys.push_back(k); kname.push_back("primer" + to_string(p)); } }
  int cm[2][26], pm[2][26];
  for (int h = 0; h < 2; h++) { const string &al = h ? KRY : AZ; for (int i = 0; i < 26; i++) { cm[h][al[i] - 'A'] = i; pm[h][i] = al[i] - 'A'; } }
  array<long long, 25> hist{}; int best = 0; string bestset;
  for (size_t r = 0; r < R.size(); r++) for (int ca = 0; ca < 2; ca++) {
    int cv[24]; for (int j = 0; j < 24; j++) cv[j] = cm[ca][ct[R[r][j][0]] - 'A'];
    for (size_t ki = 0; ki < keys.size(); ki++) { const auto &K = keys[ki];
      for (int op = 0; op < 3; op++) for (int pa = 0; pa < 2; pa++) {
        int hits = 0;
        for (int j = 0; j < 24; j++) { int k = K[R[r][j][1]], x = op == 0 ? cv[j] - k : op == 1 ? k - cv[j] : cv[j] + k; x %= 26; if (x < 0) x += 26;
          hits += (pm[pa][x] == want[j] - 'A'); }
        hist[hits]++;
        if (hits > best) { best = hits; bestset = fam + "|" + names[r] + "|" + kname[ki] + "|PA=" + (pa ? "KRY" : "AZ") + "|CA=" + (ca ? "KRY" : "AZ") + "|OP=" + to_string(op); }
        if (hits == 24) cout << "FULL24\t" << fam << "|" << names[r] << "|" << kname[ki] << "|" << pa << ca << op << "\n";
      } } }
  cout << "BEST\t" << best << "\t" << bestset << "\nHIST";
  for (int i = 0; i < 25; i++) cout << "\t" << hist[i];
  cout << "\n";
}

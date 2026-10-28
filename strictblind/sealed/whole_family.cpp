// strictblind SEALED whole-family counter (only after the freeze): for every setting of a run, how many of the 24
// known plaintext letters the fixed-method decryption reproduces. Same key kinds and route semantics as blind/scan.cpp.
// Usage: whole_family TEXT|CHAIN FILE|B CT ROUTES LO HI   -> prints BEST, FULL24 lines and HIST (25 counts)
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N = 97;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
string letters(const string &f) { ifstream in(f); string s((istreambuf_iterator<char>(in)), {});
  for (char &c : s) if (c >= 'a' && c <= 'z') c = char(c - 'a' + 'A');
  s.erase(remove_if(s.begin(), s.end(), [](char c) { return c < 'A' || c > 'Z'; }), s.end()); return s; }
int main(int argc, char **argv) {
  if (argc != 7) { cerr << "usage: whole_family TEXT|CHAIN FILE|B CT ROUTES LO HI\n"; return 1; }
  string kind = argv[1], karg = argv[2], ct = letters(argv[3]);
  int lo = stoi(argv[5]), hi = stoi(argv[6]);
  vector<int> pos; string want;
  for (int i = 0; i < 13; i++) { pos.push_back(21 + i); want += string("EASTNORTHEAST")[i]; }
  for (int i = 0; i < 11; i++) { pos.push_back(63 + i); want += string("BERLINCLOCK")[i]; }
  vector<vector<array<int, 2>>> R; vector<string> names;
  { ifstream rf(argv[4]); string line; int idx = 0;
    while (getline(rf, line)) { if (line.empty()) continue; if (idx >= lo && idx < hi) {
        istringstream is(line); string nm, od, ps; is >> nm >> od >> ps; array<int, N> perm{}; int j = 0; size_t a = 0;
        while (a < ps.size()) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); perm[j++] = stoi(ps.substr(a, b - a)); a = b + 1; }
        array<int, N> q{}; for (int t = 0; t < N; t++) q[perm[t]] = t;
        vector<array<int, 2>> m; for (int t : pos) m.push_back({od == "ID" ? t : q[t], od == "T_then_S" ? q[t] : t});
        R.push_back(m); names.push_back(nm + "|" + od); }
      idx++; } }
  const string AL[4] = {AZ, KRY, "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"};
  const string AN[4] = {"AZ", "KRY", "PAL", "ABS"};
  const int A = kind == "CHAINALPH" ? 4 : 2;
  int cm[4][26], pm[4][26];
  for (int h = 0; h < A; h++) {
    if (AL[h].size() != 26) throw runtime_error("alphabet length");
    bool seen[26]{};
    for (int i = 0; i < 26; i++) {
      int c = AL[h][i] - 'A';
      if (c < 0 || c >= 26 || seen[c]) throw runtime_error("invalid alphabet");
      seen[c] = true; cm[h][c] = i; pm[h][i] = c;
    }
  }
  vector<array<int, 24>> cvr[4];
  for (int ca = 0; ca < A; ca++)
    for (auto &m : R) {
      array<int, 24> c;
      for (int j = 0; j < 24; j++) c[j] = cm[ca][ct[m[j][0]] - 'A'];
      cvr[ca].push_back(c);
    }
  array<long long, 25> hist{}; int best = 0; string bestset;
  array<int, N> K{};
  auto run_key = [&](const string &kn) {
    for (size_t r = 0; r < R.size(); r++) for (int ca = 0; ca < A; ca++) {
      const auto &cv = cvr[ca][r];
      for (int op = 0; op < 3; op++) for (int pa = 0; pa < A; pa++) {
        int hits = 0;
        for (int j = 0; j < 24; j++) { int k = K[R[r][j][1]], x = op == 0 ? cv[j] - k : op == 1 ? k - cv[j] : cv[j] + k; x %= 26; if (x < 0) x += 26;
          hits += (pm[pa][x] == want[j] - 'A'); }
        hist[hits]++;
        if (hits > best) { best = hits; bestset = names[r] + "|" + kn + "|PA=" + AN[pa] + "|CA=" + AN[ca] + "|OP=" + to_string(op); }
        if (hits == 24) cout << "FULL24\t" << names[r] << "|" << kn << "|" << pa << ca << op << "\n";
      } }
  };
  if (kind == "TEXT") { string src = letters(karg);
    for (int dir = 0; dir < 2; dir++) { string s = dir ? string(src.rbegin(), src.rend()) : src;
      for (int num = 0; num < 2; num++) { const string &al = num ? KRY : AZ; int p[26]; for (int i = 0; i < 26; i++) p[al[i] - 'A'] = i;
        for (size_t off = 0; off + N <= s.size(); off++) { for (int i = 0; i < N; i++) K[i] = p[s[off + i] - 'A'];
          run_key(string(dir ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off)); } } } }
  else if (kind == "CHAIN" || kind == "CHAINBASE" || kind == "CHAINALPH") {
    int base = 10, b = 0;
    if (kind == "CHAIN") b = stoi(karg);
    else {
      auto split = karg.find(',');
      if (split == string::npos) throw runtime_error("CHAINBASE requires BASE,LENGTH");
      base = stoi(karg.substr(0, split));
      b = stoi(karg.substr(split + 1));
    }
    if (base < 2 || base > 26 || b < 2 || b > 8) throw runtime_error("invalid base or primer length");
    long long lim = 1;
    for (int i = 0; i < b; i++) {
      lim *= base;
      if ((kind == "CHAINBASE" || kind == "CHAINALPH") && lim > 20000000) throw runtime_error("primer limit");
    }
    const string symbols = "0123456789ABCDEFGHIJKLMNOP";
    for (long long p = 0; p < lim; p++) {
      long long v = p; string primer(b, '0');
      for (int i = b - 1; i >= 0; i--) {
        K[i] = int(v % base);
        primer[i] = symbols[K[i]];
        v /= base;
      }
      for (int i = b; i < N; i++) K[i] = (K[i - b] + K[i - b + 1]) % base;
      run_key("primer" + primer);
    }
  } else throw runtime_error("key kind");
  cout << "BEST\t" << best << "\t" << bestset << "\nHIST";
  for (int i = 0; i < 25; i++) cout << "\t" << hist[i];
  cout << "\n";
}

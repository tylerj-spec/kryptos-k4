// R42 BLIND stage 2. NO known plaintext, clue positions or masks anywhere in this program.
// For each stage-1 row (fixed plaintext alphabet PA, key, operation), anneals the FREE cipher alphabet: every
// ciphertext letter c gets an offset t(c) (a permutation), and p_i = PA[t(c_i) - k_i] (VIG) or PA[t(c_i) + k_i]
// (BEAU|VARB). English quadgrams; restart 0 starts from the unigram-optimal assignment, the others at random.
// Seeds come from the setting string and a salt.
// Build: g++ -std=c++17 -O3 -march=native casolve.cpp -o casolve
// Usage: casolve CT.txt QUAD.f32 IN_TOP.tsv OUT.tsv RESTARTS SALT FIRST_N
#include <bits/stdc++.h>
using namespace std;
const int N = 97;
const map<string, string> PAS = {
    {"AZ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}, {"KRY", "KRYPTOSABCDEFGHIJLMNQUVWXZ"}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"},
    {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"}, {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"},
    {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
static vector<float> Q;
static uint64_t fnv(const string &s) { uint64_t h = 1469598103934665603ull; for (unsigned char ch : s) { h ^= ch; h *= 1099511628211ull; } return h; }

// minimum-cost perfect assignment (Hungarian method); match[row] = column
static void hungarian(const double a[26][26], int match[26]) {
    const int n = 26; const double INF = 1e18;
    double u[n + 1] = {0}, v[n + 1] = {0}; int p[n + 1] = {0}, way[n + 1] = {0};
    for (int i = 1; i <= n; i++) {
        p[0] = i; int j0 = 0; double minv[n + 1]; bool used[n + 1];
        for (int j = 0; j <= n; j++) { minv[j] = INF; used[j] = false; }
        do {
            used[j0] = true; int i0 = p[j0], j1 = 0; double delta = INF;
            for (int j = 1; j <= n; j++) if (!used[j]) {
                double cur = a[i0 - 1][j - 1] - u[i0] - v[j];
                if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
                if (minv[j] < delta) { delta = minv[j]; j1 = j; }
            }
            for (int j = 0; j <= n; j++) if (used[j]) { u[p[j]] += delta; v[j] -= delta; } else minv[j] -= delta;
            j0 = j1;
        } while (p[j0] != 0);
        do { int j1 = way[j0]; p[j0] = p[j1]; j0 = j1; } while (j0);
    }
    for (int j = 1; j <= n; j++) match[p[j] - 1] = j - 1;
}

int main(int argc, char **argv) {
  try {
    if (argc != 8) throw runtime_error("usage: casolve CT QUAD IN_TOP OUT RESTARTS SALT FIRST_N");
    string ct; { ifstream f(argv[1]); string l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) ct += toupper(ch); }
    if ((int)ct.size() != N) throw runtime_error("ciphertext length");
    Q.resize(456976);
    { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    double lf[26];
    { double f1[26] = {0}, tot = 0;
      for (int a = 0; a < 26; a++) for (int r = 0; r < 17576; r++) { double v = pow(10.0, (double)Q[a * 17576 + r]); f1[a] += v; tot += v; }
      for (int a = 0; a < 26; a++) lf[a] = log(f1[a] / tot); }
    ifstream in(argv[3]); if (!in) throw runtime_error("input");
    int R = stoi(argv[5]); string salt = argv[6]; long first = stol(argv[7]);
    ofstream out(argv[4]); out << setprecision(10) << "rank\tL1\tsetting\tscore\tplaintext\tcipher_alphabet\n";
    int c[N]; vector<vector<int>> pos(26);
    for (int i = 0; i < N; i++) { c[i] = ct[i] - 'A'; pos[c[i]].push_back(i); }
    string line; getline(in, line);
    long done = 0;
    while (done < first && getline(in, line)) {
      if (line.empty()) continue;
      stringstream ss(line); string rk, l1, setting, ks;
      getline(ss, rk, '\t'); getline(ss, l1, '\t'); getline(ss, setting, '\t'); getline(ss, ks, '\t');
      if ((int)ks.size() != N) throw runtime_error("key length");
      string pa = PAS.at(setting.substr(setting.find("|PA=") + 4, setting.find("|OP=") - setting.find("|PA=") - 4));
      int sign = setting.substr(setting.find("|OP=") + 4) == "VIG" ? -1 : 1;   // x = t - k (VIG) or t + k
      int PA[26]; for (int x = 0; x < 26; x++) PA[x] = pa[x] - 'A';
      int k[N]; for (int i = 0; i < N; i++) k[i] = ks[i] - 'A';
      auto letter = [&](const int *tau, int i) { int x = (tau[c[i]] + sign * k[i]) % 26; if (x < 0) x += 26; return PA[x]; };
      int hm[26];
      { double cost[26][26] = {{0}};
        for (int i = 0; i < N; i++) for (int t = 0; t < 26; t++) { int x = (t + sign * k[i]) % 26; if (x < 0) x += 26; cost[c[i]][t] -= lf[PA[x]]; }
        hungarian(cost, hm); }
      double best = -1e18; string bp; int btau[26];
      int tau[26], p[N], mark[N] = {0}, stamp = 0; vector<int> st;
      for (int r = 0; r < R; r++) {
        mt19937_64 rng(fnv(setting + "|" + salt + "|" + to_string(r)));
        if (r == 0) memcpy(tau, hm, sizeof tau);
        else { iota(tau, tau + 26, 0); shuffle(tau, tau + 26, rng); }
        for (int i = 0; i < N; i++) p[i] = letter(tau, i);
        double sc = 0; for (int i = 0; i + 3 < N; i++) sc += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
        const int iters = 30000; const double T0 = r == 0 ? 1.0 : 3.0, T1 = 0.05;
        for (int it = 0; it < iters; it++) {
          double T = T0 * pow(T1 / T0, (double)it / iters);
          int a = rng() % 26, b = rng() % 26;
          if (a == b || (pos[a].empty() && pos[b].empty())) continue;
          stamp++; st.clear();
          for (int w : {a, b}) for (int i : pos[w]) for (int s = max(0, i - 3); s <= min(i, N - 4); s++) if (mark[s] != stamp) { mark[s] = stamp; st.push_back(s); }
          double bs = 0; for (int s : st) bs += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
          swap(tau[a], tau[b]);
          for (int w : {a, b}) for (int i : pos[w]) p[i] = letter(tau, i);
          double as = 0; for (int s : st) as += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
          double d = as - bs;
          if (d >= 0 || exp(d / T) > (double)(rng() >> 11) / 9007199254740992.0) sc += d;
          else { swap(tau[a], tau[b]); for (int w : {a, b}) for (int i : pos[w]) p[i] = letter(tau, i); }
        }
        double ex = 0; for (int i = 0; i + 3 < N; i++) ex += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
        if (ex > best) { best = ex; bp.assign(N, '?'); for (int i = 0; i < N; i++) bp[i] = 'A' + p[i]; memcpy(btau, tau, sizeof btau); }
      }
      string calpha(26, '?'); for (int ch = 0; ch < 26; ch++) calpha[btau[ch]] = 'A' + ch;   // CA[t] = letter with offset t
      out << rk << "\t" << l1 << "\t" << setting << "\t" << best << "\t" << bp << "\t" << calpha << "\n";
      done++;
    }
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
}

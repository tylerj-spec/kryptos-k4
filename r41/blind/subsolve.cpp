// R40 BLIND stage 2. NO known plaintext, clue positions or masks anywhere in this program.
// Solves each stage-1 y-string as a simple substitution (English quadgrams, simulated annealing with swap moves,
// then a greedy polish), assuming the letters are in reading order (identity route).
// Seeds come from the setting string and a salt, so results do not depend on which file a row is in.
// Build: g++ -std=c++17 -O3 -march=native subsolve.cpp -o subsolve
// Usage: subsolve QUAD.f32 IN_TOP.tsv OUT.tsv RESTARTS SALT FIRST_N
//   IN_TOP.tsv: rank L1 setting y (header line); only the first FIRST_N rows are solved.
#include <bits/stdc++.h>
using namespace std;
static vector<float> Q;
static uint64_t fnv(const string &s) { uint64_t h = 1469598103934665603ull; for (unsigned char ch : s) { h ^= ch; h *= 1099511628211ull; } return h; }

int main(int argc, char **argv) {
  try {
    if (argc != 7) throw runtime_error("usage: subsolve QUAD IN_TOP OUT RESTARTS SALT FIRST_N");
    Q.resize(456976);
    { ifstream f(argv[1], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    ifstream in(argv[2]); if (!in) throw runtime_error("input");
    int R = stoi(argv[4]); string salt = argv[5]; long first = stol(argv[6]);
    ofstream out(argv[3]); out << setprecision(10) << "rank\tL1\tsetting\tscore\tplaintext\tmap\n";
    string line; getline(in, line);
    long done = 0;
    while (done < first && getline(in, line)) {
      if (line.empty()) continue;
      stringstream ss(line); string rk, l1, setting, ys;
      getline(ss, rk, '\t'); getline(ss, l1, '\t'); getline(ss, setting, '\t'); getline(ss, ys, '\t');
      int n = ys.size();
      vector<int> y(n); for (int i = 0; i < n; i++) y[i] = ys[i] - 'A';
      vector<vector<int>> pos(26); for (int i = 0; i < n; i++) pos[y[i]].push_back(i);
      vector<int> m(26), p(n), mark(n, 0), st; int stamp = 0;
      double best = -1e18; string bp; vector<int> bm;
      for (int r = 0; r < R; r++) {
        mt19937_64 rng(fnv(setting + "|" + salt + "|" + to_string(r)));
        iota(m.begin(), m.end(), 0); shuffle(m.begin(), m.end(), rng);
        for (int i = 0; i < n; i++) p[i] = m[y[i]];
        double sc = 0; for (int i = 0; i + 3 < n; i++) sc += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
        const int iters = 20000, polish = 3000; const double T0 = 2.0, T1 = 0.05;
        for (int it = 0; it < iters + polish; it++) {
          double T = it < iters ? T0 * pow(T1 / T0, (double)it / iters) : 0;
          int u = rng() % 26, v = rng() % 26;
          if (u == v || (pos[u].empty() && pos[v].empty())) continue;
          stamp++; st.clear();
          for (int w : {u, v}) for (int i : pos[w]) for (int s = max(0, i - 3); s <= min(i, n - 4); s++) if (mark[s] != stamp) { mark[s] = stamp; st.push_back(s); }
          double b = 0; for (int s : st) b += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
          for (int i : pos[u]) p[i] = m[v];
          for (int i : pos[v]) p[i] = m[u];
          double a = 0; for (int s : st) a += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
          double d = a - b;
          bool acc = d > 0 || (T > 0 && exp(d / T) > (double)(rng() >> 11) / 9007199254740992.0);
          if (acc) { swap(m[u], m[v]); sc += d; }
          else { for (int i : pos[u]) p[i] = m[u]; for (int i : pos[v]) p[i] = m[v]; }
        }
        // exact rescore (guards against drift) and keep the best restart; ties keep the earlier restart
        double ex = 0; for (int i = 0; i + 3 < n; i++) ex += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
        if (ex > best) { best = ex; bp.assign(n, '?'); for (int i = 0; i < n; i++) bp[i] = 'A' + p[i]; bm = m; }
      }
      string ms(26, '?'); for (int v = 0; v < 26; v++) ms[v] = 'A' + bm[v];
      out << rk << "\t" << l1 << "\t" << setting << "\t" << best << "\t" << bp << "\t" << ms << "\n";
      done++;
    }
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
}

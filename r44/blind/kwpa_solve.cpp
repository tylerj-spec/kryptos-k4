// R44 BLIND solver: keyword plaintext alphabet x FREE cipher alphabet, key given. No K4 data, clues or masks.
// Model (as R43): CA_index(c_i) - PA_index(p_i) = k_i (mod 26). The plaintext alphabet is assumed to be a keyword
// alphabet: the letters of a dictionary keyword (repeats dropped) followed by the unused letters in A-Z order.
// Candidates: every distinct keyword alphabet from the KCAND most frequent exact words of length 5-10 in the ORTH
// word model. For each candidate the cipher alphabet is annealed (quadgram score, swap moves, RESTARTS x 30,000),
// The 50 best candidates are then re-solved with RESTARTS2 = 64 restarts (new seeds), and the best-scoring
// (plaintext, PA, CA) is returned. Every returned witness is re-encrypted exactly.
// Input TSV (R43 format): id<TAB>ciphertext<TAB>97 key digits; header allowed. Output JSONL (r43/sealed/evaluate.py).
// Usage: kwpa_solve WORDS.tsv QUAD.f32 IN.tsv OUT.jsonl [KCAND=5000] [RESTARTS=8] [TOP2=50] [RESTARTS2=64]
#include <bits/stdc++.h>
using namespace std;
constexpr int N = 97;
static vector<float> Q;
static uint64_t fnv(const string &s) { uint64_t h = 1469598103934665603ull; for (unsigned char ch : s) { h ^= ch; h *= 1099511628211ull; } return h; }
static string kw_alpha(const string &w) {
    string out; for (char ch : w + string("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) if (out.find(ch) == string::npos) out += ch;
    return out;
}
int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: kwpa_solve WORDS QUAD IN OUT [KCAND] [RESTARTS]");
    int KC = argc > 5 ? atoi(argv[5]) : 5000, RS = argc > 6 ? atoi(argv[6]) : 8, TOP2 = argc > 7 ? atoi(argv[7]) : 50, RS2 = argc > 8 ? atoi(argv[8]) : 64;
    vector<pair<double, string>> ws;
    { ifstream f(argv[1]); string w; double ex, ed; while (f >> w >> ex >> ed) if (ex > -1e90 && w.size() >= 5 && w.size() <= 10) ws.push_back({ex, w}); }
    sort(ws.begin(), ws.end(), [](auto &a, auto &b) { return a.first != b.first ? a.first > b.first : a.second < b.second; });
    if ((int)ws.size() > KC) ws.resize(KC);
    set<string> uniq; for (auto &x : ws) uniq.insert(kw_alpha(x.second));
    vector<string> cands(uniq.begin(), uniq.end());
    cerr << "R44 keyword alphabets " << cands.size() << " from " << ws.size() << " words\n";
    Q.resize(456976); { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    ifstream in(argv[3]); ofstream out(argv[4]); string line;
    while (getline(in, line)) {
      if (line.empty() || line.rfind("id\t", 0) == 0) continue;
      stringstream ss(line); string id, ct, ks; getline(ss, id, '\t'); getline(ss, ct, '\t'); getline(ss, ks, '\t');
      vector<int> k; { for (char &ch : ks) if (ch == ',') ch = ' '; stringstream q(ks); int x; while (q >> x) k.push_back(x); }
      if ((int)ct.size() != N || (int)k.size() != N) throw runtime_error("bad input row " + id);
      int c[N]; vector<vector<int>> pos(26);
      for (int i = 0; i < N; i++) { c[i] = ct[i] - 'A'; pos[c[i]].push_back(i); }
      struct Res { double s; string plain, pa, ca; };
      vector<Res> top;   // best TOP2 candidates
      long proposals = 0;
      auto solve_pa = [&](const string &pa, int restarts, const string &salt, Res &rr) {
        int PA[26]; for (int x = 0; x < 26; x++) PA[x] = pa[x] - 'A';
        double best = -1e18; int btau[26];
        int tau[26], p[N], mark[N] = {0}, stamp = 0; vector<int> st;
        for (int r = 0; r < restarts; r++) {
          mt19937_64 rng(fnv(id + "|" + pa + "|" + salt + to_string(r)));
          iota(tau, tau + 26, 0); shuffle(tau, tau + 26, rng);
          auto letter = [&](int i) { int x = (tau[c[i]] - k[i]) % 26; if (x < 0) x += 26; return PA[x]; };
          for (int i = 0; i < N; i++) p[i] = letter(i);
          double sc = 0; for (int i = 0; i + 3 < N; i++) sc += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
          const int iters = 30000; const double T0 = 3.0, T1 = 0.05;
          for (int it = 0; it < iters; it++) {
            double T = T0 * pow(T1 / T0, (double)it / iters);
            int a = rng() % 26, b = rng() % 26; if (a == b || (pos[a].empty() && pos[b].empty())) continue;
            proposals++;
            stamp++; st.clear();
            for (int w : {a, b}) for (int i : pos[w]) for (int s = max(0, i - 3); s <= min(i, N - 4); s++) if (mark[s] != stamp) { mark[s] = stamp; st.push_back(s); }
            double bs = 0; for (int s : st) bs += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
            swap(tau[a], tau[b]);
            for (int w : {a, b}) for (int i : pos[w]) p[i] = letter(i);
            double as = 0; for (int s : st) as += Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]];
            double d = as - bs;
            if (d >= 0 || exp(d / T) > (double)(rng() >> 11) / 9007199254740992.0) sc += d;
            else { swap(tau[a], tau[b]); for (int w : {a, b}) for (int i : pos[w]) p[i] = letter(i); }
          }
          double ex = 0; for (int i = 0; i + 3 < N; i++) ex += Q[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]];
          if (ex > best) { best = ex; memcpy(btau, tau, sizeof btau); }
        }
        if (best <= rr.s) return;
        rr.s = best; rr.pa = pa; rr.plain.assign(N, '?'); rr.ca.assign(26, '?');
        for (int i = 0; i < N; i++) { int x = (btau[c[i]] - k[i]) % 26; if (x < 0) x += 26; rr.plain[i] = pa[x]; }
        for (int ch = 0; ch < 26; ch++) rr.ca[btau[ch]] = 'A' + ch;
      };
      auto order = [](const Res &a, const Res &b) { return a.s != b.s ? a.s > b.s : a.pa < b.pa; };
      for (size_t ci = 0; ci < cands.size(); ci++) {      // stage 1: every keyword alphabet
        Res rr; rr.s = -1e18;
        solve_pa(cands[ci], RS, "s1|", rr);
        top.push_back(rr);
        sort(top.begin(), top.end(), order);
        if ((int)top.size() > TOP2) top.pop_back();
      }
      for (auto &rr : top) solve_pa(rr.pa, RS2, "s2|", rr);   // stage 2: re-solve the best TOP2
      sort(top.begin(), top.end(), order);
      const Res &b = top[0];
      for (int i = 0; i < N; i++) if (b.ca[(b.pa.find(b.plain[i]) + k[i]) % 26] != ct[i]) throw runtime_error("witness check failed " + id);
      out << "{\"id\":\"" << id << "\",\"plaintext\":\"" << b.plain << "\",\"plaintext_alphabet\":\"" << b.pa << "\",\"ciphertext_alphabet\":\"" << b.ca
          << "\",\"score\":" << setprecision(10) << b.s << ",\"proposals\":" << proposals << ",\"compatible\":" << cands.size()
          << ",\"runner_up_scores\":[";
      for (size_t i = 1; i < top.size() && i < 6; i++) out << (i > 1 ? "," : "") << top[i].s;
      out << "]}\n"; out.flush();
      cerr << "R44 " << id << " best " << b.s << " PA " << b.pa << "\n";
    }
  } catch (const exception &e) { cerr << "R44 ERROR " << e.what() << "\n"; return 1; }
}

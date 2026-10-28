// R41 BLIND stage 1. NO known plaintext, clue positions or masks anywhere in this program.
// As R40 (fixed cipher alphabet CA, FREE plaintext alphabet, VIG|BEAU y = x - k or VARB y = x + k), but the
// substitution is followed by a transposition: CT[j] = X[perm[j]] (order S_then_T), so X_i = CT[q_i] with q = perm^-1
// and y_i = CA^-1(X_i) -/+ k_i is a simple substitution of the plaintext in reading order.
// Every S_then_T route-order in the routes file is scanned; other orders are skipped (R40 covers them).
// Keys: chain addition base 10 with b = 5, 6 (every primer); running keys Carter vol. I and K1-K3 plaintext
// (forward/reversed, letters numbered AZ or KRY, every offset).
// Build: g++ -std=c++17 -O3 -march=native route_pafree_scan.cpp -o route_pafree_scan
// Usage: route_pafree_scan CT.txt QUAD.f32 CARTER.txt K1K3.txt ROUTES.txt FAMS TOPK OUT_TOP.tsv OUT_HIST.tsv
//   FAMS: comma list from C10b5,C10b6,CARTER,K1K3
#include <bits/stdc++.h>
using namespace std;
const int N = 97;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
const vector<pair<string, string>> CAS = {
    {"AZ", AZ}, {"KRY", KRY}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"}, {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"},
    {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"}, {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
const char *OPN[2] = {"VIG|BEAU", "VARB"};

struct Hit { double l1; int fam; long long key; int route, ca, op; string setting, y; };
static bool better(const Hit &a, const Hit &b) {   // total order: higher L1, then smaller (fam, key, route, ca, op)
    if (a.l1 != b.l1) return a.l1 > b.l1;
    return tie(a.fam, a.key, a.route, a.ca, a.op) < tie(b.fam, b.key, b.route, b.ca, b.op);
}
struct Worse { bool operator()(const Hit &a, const Hit &b) const { return better(a, b); } };

static string letters(const string &path) {
    ifstream f(path); if (!f) throw runtime_error("cannot read " + path);
    string s, line; while (getline(f, line)) for (char ch : line) if (isalpha((unsigned char)ch)) s += toupper(ch);
    return s;
}

int main(int argc, char **argv) {
  try {
    if (argc != 10) throw runtime_error("usage: route_pafree_scan CT QUAD CARTER K1K3 ROUTES FAMS TOPK OUT_TOP OUT_HIST");
    string ct = letters(argv[1]);
    if ((int)ct.size() != N) throw runtime_error("ciphertext must have 97 letters");
    vector<float> Q(456976);
    { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    double lf[26];
    { double f1[26] = {0}, tot = 0;
      for (int a = 0; a < 26; a++) for (int r = 0; r < 17576; r++) { double v = pow(10.0, (double)Q[a * 17576 + r]); f1[a] += v; tot += v; }
      for (int a = 0; a < 26; a++) lf[a] = log(f1[a] / tot);
      sort(lf, lf + 26, greater<double>()); }
    string carter = letters(argv[3]), k1k3 = letters(argv[4]);
    vector<string> rname; vector<array<int, N>> rq;
    { ifstream rf(argv[5]); if (!rf) throw runtime_error("routes"); string line;
      while (getline(rf, line)) {
        if (line.empty()) continue;
        istringstream is(line); string nm, od, ps; is >> nm >> od >> ps;
        if (od != "S_then_T") continue;
        array<int, N> perm{}; int j = 0; size_t a = 0;
        while (a < ps.size() && j < N) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); perm[j++] = stoi(ps.substr(a, b - a)); a = b + 1; }
        array<int, N> q{}; vector<int> seen(N, 0);
        for (int t = 0; t < N; t++) { if (j != N || perm[t] < 0 || perm[t] >= N || seen[perm[t]]++) throw runtime_error("bad permutation: " + nm); q[perm[t]] = t; }
        rname.push_back(nm); rq.push_back(q);
      } }
    const int R = rname.size();
    if (R == 0) throw runtime_error("no S_then_T routes");
    set<string> fams; { string f = argv[6]; size_t a = 0; while (a <= f.size()) { size_t b = f.find(',', a); if (b == string::npos) b = f.size(); fams.insert(f.substr(a, b - a)); a = b + 1; } }
    for (auto &f : fams) if (f != "C10b5" && f != "C10b6" && f != "CARTER" && f != "K1K3") throw runtime_error("unknown family " + f);
    size_t K = stoul(argv[7]);
    // xs[route][ca][i] = CA^-1 of the ciphertext letter that holds X_i
    vector<array<array<int, N>, 7>> xs(R);
    for (int r = 0; r < R; r++) for (int c = 0; c < 7; c++) {
      int inv[26]; for (int i = 0; i < 26; i++) inv[CAS[c].second[i] - 'A'] = i;
      for (int i = 0; i < N; i++) xs[r][c][i] = inv[ct[rq[r][i]] - 'A'];
    }
    static int SUB[26][26], ADD[26][26];   // (x - k) mod 26 and (x + k) mod 26 for x, k in 0..25
    for (int a = 0; a < 26; a++) for (int k = 0; k < 26; k++) { SUB[a][k] = (a - k + 26) % 26; ADD[a][k] = (a + k) % 26; }
    priority_queue<Hit, vector<Hit>, Worse> heap;
    const double HLO = -460, HW = 0.5; const int NB = 600;
    vector<long long> hist(NB + 2, 0); long long total = 0; double gmax = -1e18;
    array<int, N> Kv{};
    int fam = 0;
    auto run_key = [&](long long keyid, const function<string()> &label) {
      for (int r = 0; r < R; r++) for (int c = 0; c < 7; c++) for (int op = 0; op < 2; op++) {
        const auto &x = xs[r][c];
        int cnt[26] = {0}; int y[N];
        const auto &T = op == 0 ? SUB : ADD;
        for (int t = 0; t < N; t++) { int v = T[x[t]][Kv[t]]; y[t] = v; cnt[v]++; }
        // sorted counts against sorted log-frequencies, via a histogram of the counts (same terms, same order)
        int mx = 0; for (int v = 0; v < 26; v++) mx = max(mx, cnt[v]);
        int cc[N + 1]; for (int c = 0; c <= mx; c++) cc[c] = 0;
        for (int v = 0; v < 26; v++) cc[cnt[v]]++;
        double l1 = 0; int rr = 0;
        for (int c = mx; c >= 1; c--) for (int j = 0; j < cc[c]; j++) l1 += c * lf[rr++];
        total++; gmax = max(gmax, l1);
        int b = (int)floor((l1 - HLO) / HW); b = b < 0 ? 0 : (b > NB ? NB + 1 : b + 1); hist[b]++;
        if (heap.size() < K || l1 >= heap.top().l1) {
          Hit h{l1, fam, keyid, r, c, op, "", ""};
          if (heap.size() < K || better(h, heap.top())) {
            h.setting = label() + "|ROUTE=" + rname[r] + "|CA=" + CAS[c].first + "|OP=" + OPN[op];
            h.y.resize(N); for (int t = 0; t < N; t++) h.y[t] = 'A' + y[t];
            if (heap.size() >= K) heap.pop();
            heap.push(h);
          }
        }
      }
    };
    const string symbols = "0123456789";
    for (fam = 0; fam < 2; fam++) {   // chain addition base 10, b = 5, 6
      int b = 5 + fam; long long lim = 1; for (int i = 0; i < b; i++) lim *= 10;
      if (!fams.count("C10b" + to_string(b))) continue;
      for (long long p = 0; p < lim; p++) {
        long long v = p; string primer(b, '0');
        for (int i = b - 1; i >= 0; i--) { Kv[i] = int(v % 10); primer[i] = symbols[Kv[i]]; v /= 10; }
        for (int i = b; i < N; i++) Kv[i] = (Kv[i - b] + Kv[i - b + 1]) % 10;
        run_key(p, [&]() { return "C10b" + to_string(b) + "/primer" + primer; });
      }
    }
    const string *texts[2] = {&carter, &k1k3}; const char *tn[2] = {"CARTER", "K1K3"};
    for (int tx = 0; tx < 2; tx++) {
      fam = 2 + tx;
      if (!fams.count(tn[tx])) continue;
      for (int dir = 0; dir < 2; dir++) {
        string s = dir ? string(texts[tx]->rbegin(), texts[tx]->rend()) : *texts[tx];
        for (int num = 0; num < 2; num++) {
          const string &al = num ? KRY : AZ; int pos[26]; for (int i = 0; i < 26; i++) pos[al[i] - 'A'] = i;
          for (size_t off = 0; off + N <= s.size(); off++) {
            for (int i = 0; i < N; i++) Kv[i] = pos[s[off + i] - 'A'];
            long long keyid = ((long long)(dir * 2 + num) << 32) | (long long)off;
            run_key(keyid, [&]() { return string(tn[tx]) + "/" + (dir ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off); });
          }
        }
      }
    }
    vector<Hit> rows; while (!heap.empty()) { rows.push_back(heap.top()); heap.pop(); }
    sort(rows.begin(), rows.end(), better);
    ofstream o(argv[8]); o << setprecision(10) << "rank\tL1\tsetting\ty\n";
    for (size_t i = 0; i < rows.size(); i++) o << i + 1 << "\t" << rows[i].l1 << "\t" << rows[i].setting << "\t" << rows[i].y << "\n";
    ofstream hf(argv[9]); hf << setprecision(10) << "# settings " << total << " max_L1 " << gmax << " routes " << R << "\nbin_lo\tcount\n";
    hf << "-inf\t" << hist[0] << "\n";
    for (int b = 0; b < NB; b++) if (hist[b + 1]) hf << HLO + b * HW << "\t" << hist[b + 1] << "\n";
    hf << HLO + NB * HW << "+\t" << hist[NB + 1] << "\n";
    cerr << "routes " << R << " settings " << total << " max L1 " << gmax << "\n";
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
}

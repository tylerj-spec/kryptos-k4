// R42 BLIND stage 1. NO known plaintext, clue positions or masks anywhere in this program.
// Family: fixed plaintext alphabet PA (7 choices), FREE cipher alphabet, key from a fixed family, in place.
// With x = PA^-1(p) and t = position of c in the unknown cipher alphabet: VIG t = x + k, so x = t - k;
// BEAU t = k - x and VARB t = x - k both give x = t' + k for a relabelled t'. Every ciphertext letter class
// therefore takes one unknown offset. Stage 1 scores a setting by the best unigram log-likelihood over all
// cipher alphabets (an exact assignment problem, Hungarian method) and keeps the global top K.
// Build: g++ -std=c++17 -O3 -march=native ca_screen.cpp -o ca_screen
// Usage: ca_screen CT.txt QUAD.f32 CARTER.txt K1K3.txt TOPK OUT_TOP.tsv OUT_HIST.tsv
#include <bits/stdc++.h>
using namespace std;
const int N = 97;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
const vector<pair<string, string>> PAS = {
    {"AZ", AZ}, {"KRY", KRY}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"}, {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"},
    {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"}, {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
const char *OPN[2] = {"VIG", "BEAU|VARB"};

// minimum-cost perfect assignment, n x n (Hungarian method, potentials); returns the cost
static double hungarian(const double a[26][26]) {
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
    double cost = 0; for (int j = 1; j <= n; j++) cost += a[p[j] - 1][j - 1];
    return cost;
}

struct Hit { double s; int fam; long long key; int pa, op; string setting, keystr; };
static bool better(const Hit &a, const Hit &b) {
    if (a.s != b.s) return a.s > b.s;
    return tie(a.fam, a.key, a.pa, a.op) < tie(b.fam, b.key, b.pa, b.op);
}
struct Worse { bool operator()(const Hit &a, const Hit &b) const { return better(a, b); } };

static string letters(const string &path) {
    ifstream f(path); if (!f) throw runtime_error("cannot read " + path);
    string s, line; while (getline(f, line)) for (char ch : line) if (isalpha((unsigned char)ch)) s += toupper(ch);
    return s;
}

int main(int argc, char **argv) {
  try {
    if (argc != 8) throw runtime_error("usage: ca_screen CT QUAD CARTER K1K3 TOPK OUT_TOP OUT_HIST");
    string ct = letters(argv[1]);
    if ((int)ct.size() != N) throw runtime_error("ciphertext must have 97 letters");
    vector<float> Q(456976);
    { ifstream f(argv[2], ios::binary); f.read((char *)Q.data(), 456976 * 4); if (!f) throw runtime_error("quad"); }
    double lf[26];
    { double f1[26] = {0}, tot = 0;
      for (int a = 0; a < 26; a++) for (int r = 0; r < 17576; r++) { double v = pow(10.0, (double)Q[a * 17576 + r]); f1[a] += v; tot += v; }
      for (int a = 0; a < 26; a++) lf[a] = log(f1[a] / tot); }
    string carter = letters(argv[3]), k1k3 = letters(argv[4]);
    size_t K = stoul(argv[5]);
    int c[N]; for (int t = 0; t < N; t++) c[t] = ct[t] - 'A';
    // L[pa][x] = log-frequency of the plaintext letter PA[x]
    double L[7][26]; for (int a = 0; a < 7; a++) for (int x = 0; x < 26; x++) L[a][x] = lf[PAS[a].second[x] - 'A'];
    priority_queue<Hit, vector<Hit>, Worse> heap;
    const double HLO = -460, HW = 0.5; const int NB = 600;
    vector<long long> hist(NB + 2, 0); long long total = 0; double gmax = -1e18;
    int Kv[N]; int fam = 0;
    auto run_key = [&](long long keyid, const function<string()> &label) {
      for (int a = 0; a < 7; a++) for (int op = 0; op < 2; op++) {
        double cost[26][26] = {{0}};
        for (int i = 0; i < N; i++) {
          double *row = cost[c[i]]; const double *Lr = L[a];
          int k = Kv[i];
          if (op == 0) { for (int t = 0; t < 26; t++) { int x = t - k; if (x < 0) x += 26; row[t] -= Lr[x]; } }
          else { for (int t = 0; t < 26; t++) { int x = t + k; if (x >= 26) x -= 26; row[t] -= Lr[x]; } }
        }
        double s = -hungarian(cost);
        total++; gmax = max(gmax, s);
        int b = (int)floor((s - HLO) / HW); b = b < 0 ? 0 : (b > NB ? NB + 1 : b + 1); hist[b]++;
        if (heap.size() < K || s >= heap.top().s) {
          Hit h{s, fam, keyid, a, op, "", ""};
          if (heap.size() < K || better(h, heap.top())) {
            h.setting = label() + "|PA=" + PAS[a].first + "|OP=" + OPN[op];
            h.keystr.resize(N); for (int i = 0; i < N; i++) h.keystr[i] = 'A' + Kv[i];
            if (heap.size() >= K) heap.pop();
            heap.push(h);
          }
        }
      }
    };
    for (fam = 0; fam < 2; fam++) {   // chain addition base 10, b = 5, 6
      int b = 5 + fam; long long lim = 1; for (int i = 0; i < b; i++) lim *= 10;
      for (long long p = 0; p < lim; p++) {
        long long v = p; string primer(b, '0');
        for (int i = b - 1; i >= 0; i--) { Kv[i] = int(v % 10); primer[i] = '0' + Kv[i]; v /= 10; }
        for (int i = b; i < N; i++) Kv[i] = (Kv[i - b] + Kv[i - b + 1]) % 10;
        run_key(p, [&]() { return "C10b" + to_string(b) + "/primer" + primer; });
      }
    }
    const string *texts[2] = {&carter, &k1k3}; const char *tn[2] = {"CARTER", "K1K3"};
    for (int tx = 0; tx < 2; tx++) {
      fam = 2 + tx;
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
    ofstream o(argv[6]); o << setprecision(10) << "rank\tL1\tsetting\tkey\n";
    for (size_t i = 0; i < rows.size(); i++) o << i + 1 << "\t" << rows[i].s << "\t" << rows[i].setting << "\t" << rows[i].keystr << "\n";
    ofstream hf(argv[7]); hf << setprecision(10) << "# settings " << total << " max_L1 " << gmax << "\nbin_lo\tcount\n";
    hf << "-inf\t" << hist[0] << "\n";
    for (int b = 0; b < NB; b++) if (hist[b + 1]) hf << HLO + b * HW << "\t" << hist[b + 1] << "\n";
    hf << HLO + NB * HW << "+\t" << hist[NB + 1] << "\n";
    cerr << "settings " << total << " max L1 " << gmax << "\n";
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
}

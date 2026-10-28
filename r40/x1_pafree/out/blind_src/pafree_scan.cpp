// R40 BLIND stage 1. NO known plaintext, clue positions or masks anywhere in this program.
// Family: fixed cipher alphabet CA (7 choices), FREE plaintext alphabet, key from a fixed family, operation
// VIG/BEAU (y = x - k) or VARB (y = x + k), where x = CA^-1(c). Under the hypothesis, y is a simple substitution
// of the plaintext (in ciphertext order, so any transposition applied before the substitution leaves its letter
// counts unchanged). Each setting is scored by L1 = the best unigram log-likelihood of y under any substitution
// (sorted y counts against sorted English log-frequencies, taken from the quadgram table's marginal).
// Keeps the global top-K settings and a histogram of L1 over every setting.
// Build: g++ -std=c++17 -O3 -march=native pafree_scan.cpp -o pafree_scan
// Usage: pafree_scan CT.txt QUAD.f32 CARTER.txt K1K3.txt TOPK OUT_TOP.tsv OUT_HIST.tsv
#include <bits/stdc++.h>
using namespace std;
const int N = 97;
const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
const vector<pair<string, string>> CAS = {
    {"AZ", AZ}, {"KRY", KRY}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"}, {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"},
    {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"}, {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
const char *OPN[2] = {"VIG|BEAU", "VARB"};

struct Hit { double l1; int fam; long long key; int ca, op; string setting, y; };
static bool better(const Hit &a, const Hit &b) {   // total order: higher L1, then smaller (fam, key, ca, op)
    if (a.l1 != b.l1) return a.l1 > b.l1;
    return tie(a.fam, a.key, a.ca, a.op) < tie(b.fam, b.key, b.ca, b.op);
}
struct Worse { bool operator()(const Hit &a, const Hit &b) const { return better(a, b); } };   // min-heap top = worst

static string letters(const string &path) {
    ifstream f(path); if (!f) throw runtime_error("cannot read " + path);
    string s, line; while (getline(f, line)) for (char ch : line) if (isalpha((unsigned char)ch)) s += toupper(ch);
    return s;
}

int main(int argc, char **argv) {
  try {
    if (argc != 8) throw runtime_error("usage: pafree_scan CT QUAD CARTER K1K3 TOPK OUT_TOP OUT_HIST");
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
    size_t K = stoul(argv[5]);
    int xs[7][N];
    for (int c = 0; c < 7; c++) {
      int inv[26]; for (int i = 0; i < 26; i++) inv[CAS[c].second[i] - 'A'] = i;
      for (int t = 0; t < N; t++) xs[c][t] = inv[ct[t] - 'A'];
    }
    priority_queue<Hit, vector<Hit>, Worse> heap;
    const double HLO = -460, HW = 0.5; const int NB = 600;   // histogram bins of 0.5 from -460 to -160
    vector<long long> hist(NB + 2, 0); long long total = 0; double gmax = -1e18;
    array<int, N> Kv{};
    int fam = 0;
    auto run_key = [&](long long keyid, const function<string()> &label) {
      for (int c = 0; c < 7; c++) for (int op = 0; op < 2; op++) {
        int cnt[26] = {0}; int y[N];
        for (int t = 0; t < N; t++) { int v = op == 0 ? xs[c][t] - Kv[t] : xs[c][t] + Kv[t]; v %= 26; if (v < 0) v += 26; y[t] = v; cnt[v]++; }
        sort(cnt, cnt + 26, greater<int>());
        double l1 = 0; for (int i = 0; i < 26 && cnt[i]; i++) l1 += cnt[i] * lf[i];
        total++; gmax = max(gmax, l1);
        int b = (int)floor((l1 - HLO) / HW); b = b < 0 ? 0 : (b > NB ? NB + 1 : b + 1); hist[b]++;
        if (heap.size() < K || l1 >= heap.top().l1) {
          Hit h{l1, fam, keyid, c, op, "", ""};
          if (heap.size() < K) { h.setting = label() + "|CA=" + CAS[c].first + "|OP=" + OPN[op]; h.y.resize(N); for (int t = 0; t < N; t++) h.y[t] = 'A' + y[t]; heap.push(h); }
          else if (better(h, heap.top())) { h.setting = label() + "|CA=" + CAS[c].first + "|OP=" + OPN[op]; h.y.resize(N); for (int t = 0; t < N; t++) h.y[t] = 'A' + y[t]; heap.pop(); heap.push(h); }
        }
      }
    };
    // families 0-3: chain addition k_i = k_{i-b} + k_{i-b+1} mod base (base 10 with b = 5, 6, 7; base 26 with b = 5)
    const string symbols = "0123456789ABCDEFGHIJKLMNOP";
    const int CB[4][2] = {{10, 5}, {10, 6}, {10, 7}, {26, 5}};
    for (fam = 0; fam < 4; fam++) {
      int base = CB[fam][0], b = CB[fam][1]; long long lim = 1; for (int i = 0; i < b; i++) lim *= base;
      for (long long p = 0; p < lim; p++) {
        long long v = p; string primer(b, '0');
        for (int i = b - 1; i >= 0; i--) { Kv[i] = int(v % base); primer[i] = symbols[Kv[i]]; v /= base; }
        for (int i = b; i < N; i++) Kv[i] = (Kv[i - b] + Kv[i - b + 1]) % base;
        run_key(p, [&]() { return "C" + to_string(base) + "b" + to_string(b) + "/primer" + primer; });
      }
    }
    // families 4-5: running key text (Carter vol. I, K1-K3 plaintext), forward/reversed, letters numbered AZ or KRY
    const string *texts[2] = {&carter, &k1k3}; const char *tn[2] = {"CARTER", "K1K3"};
    for (int tx = 0; tx < 2; tx++) {
      fam = 4 + tx;
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
    ofstream o(argv[6]); o << setprecision(10) << "rank\tL1\tsetting\ty\n";
    for (size_t i = 0; i < rows.size(); i++) o << i + 1 << "\t" << rows[i].l1 << "\t" << rows[i].setting << "\t" << rows[i].y << "\n";
    ofstream hf(argv[7]); hf << setprecision(10) << "# settings " << total << " max_L1 " << gmax << "\nbin_lo\tcount\n";
    hf << "-inf\t" << hist[0] << "\n";
    for (int b = 0; b < NB; b++) if (hist[b + 1]) hf << HLO + b * HW << "\t" << hist[b + 1] << "\n";
    hf << HLO + NB * HW << "+\t" << hist[NB + 1] << "\n";
    cerr << "settings " << total << " max L1 " << gmax << "\n";
  } catch (const exception &e) { cerr << "ERROR " << e.what() << "\n"; return 1; }
}

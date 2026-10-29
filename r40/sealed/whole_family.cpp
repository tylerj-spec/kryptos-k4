// R40 SEALED whole-family check (run only after the blind outputs are frozen and committed).
// For every in-place setting of the R40 family (7 cipher alphabets x 2 operations x every key of the six key
// families) it asks whether ANY plaintext alphabet could put the given letters at the given positions: that holds
// exactly when equal letters sit on equal y values and different letters on different y values
// (y = x - k or x + k, x = CA^-1(c)). V = number of position pairs that break this; V = 0 means consistent.
// Written independently of blind/pafree_scan.cpp (same family definition, separate code).
// Build: g++ -std=c++17 -O3 -march=native whole_family.cpp -o whole_family
// Usage: whole_family CT.txt CARTER.txt K1K3.txt LETTERS97 OUT.tsv   (LETTERS97: 97 chars, '?' = not checked)
#include <bits/stdc++.h>
using namespace std;

static string clean(const string &path) {
    ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch);
    return s;
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: whole_family CT CARTER K1K3 LETTERS97 OUT\n"); return 1; }
    string ct = clean(argv[1]), carter = clean(argv[2]), k1k3 = clean(argv[3]), want = argv[4];
    if (ct.size() != 97 || want.size() != 97) { fprintf(stderr, "length\n"); return 1; }
    vector<int> P; vector<int> grp; map<char, int> gid;
    for (int i = 0; i < 97; i++) if (want[i] != '?') { P.push_back(i); if (!gid.count(want[i])) { int g = gid.size(); gid[want[i]] = g; } grp.push_back(gid[want[i]]); }
    int n = P.size(), G = gid.size();
    long long E = 0; { vector<int> sz(G, 0); for (int g : grp) sz[g]++; for (int s : sz) E += (long long)s * (s - 1) / 2; }
    const vector<pair<string, string>> CA = {
        {"AZ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}, {"KRY", "KRYPTOSABCDEFGHIJLMNQUVWXZ"}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"},
        {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"}, {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"},
        {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
    vector<vector<int>> X(7, vector<int>(n));
    for (int c = 0; c < 7; c++) for (int j = 0; j < n; j++) X[c][j] = (int)CA[c].second.find(ct[P[j]]);
    vector<long long> hist(n * (n - 1) / 2 + 1, 0); long long total = 0, minV = LLONG_MAX; vector<string> minset;
    vector<int> key(97);
    auto test = [&](const string &label) {
        for (int c = 0; c < 7; c++) for (int op = 0; op < 2; op++) {
            int cy[26] = {0}; int cg[16][26] = {{0}};
            long long S = 0, B = 0;
            for (int j = 0; j < n; j++) {
                int v = op == 0 ? X[c][j] - key[P[j]] : X[c][j] + key[P[j]];
                v = ((v % 26) + 26) % 26;
                S += cy[v]++; B += cg[grp[j]][v]++;
            }
            long long V = E + S - 2 * B;
            hist[V]++; total++;
            if (V < minV) { minV = V; minset.clear(); }
            if (V == minV && minset.size() < 50) minset.push_back(label + "|CA=" + CA[c].first + "|OP=" + (op == 0 ? "VIG|BEAU" : "VARB"));
        }
    };
    const char *SYM = "0123456789ABCDEFGHIJKLMNOP";
    int fams[4][2] = {{10, 5}, {10, 6}, {10, 7}, {26, 5}};
    for (auto &f : fams) {
        int base = f[0], b = f[1]; long long lim = llround(pow(base, b));
        for (long long p = 0; p < lim; p++) {
            long long v = p; string pr(b, '0');
            for (int i = b - 1; i >= 0; i--) { key[i] = v % base; pr[i] = SYM[key[i]]; v /= base; }
            for (int i = b; i < 97; i++) key[i] = (key[i - b] + key[i - b + 1]) % base;
            test("C" + to_string(base) + "b" + to_string(b) + "/primer" + pr);
        }
    }
    string texts[2] = {carter, k1k3}; string names[2] = {"CARTER", "K1K3"};
    for (int t = 0; t < 2; t++) for (int d = 0; d < 2; d++) for (int num = 0; num < 2; num++) {
        string s = d ? string(texts[t].rbegin(), texts[t].rend()) : texts[t];
        string al = num ? "KRYPTOSABCDEFGHIJLMNQUVWXZ" : "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        for (size_t off = 0; off + 97 <= s.size(); off++) {
            for (int i = 0; i < 97; i++) key[i] = (int)al.find(s[off + i]);
            test(names[t] + "/" + (d ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off));
        }
    }
    ofstream o(argv[5]);
    o << "# settings\t" << total << "\n# checked_positions\t" << n << "\n# pairs\t" << n * (n - 1) / 2 << "\n# equal_letter_pairs\t" << E << "\n";
    o << "# consistent_settings(V=0)\t" << hist[0] << "\n# min_V\t" << minV << "\n";
    for (auto &s : minset) o << "# min_setting\t" << s << "\n";
    o << "V\tcount\n";
    for (size_t v = 0; v < hist.size(); v++) if (hist[v]) o << v << "\t" << hist[v] << "\n";
    fprintf(stderr, "settings %lld consistent %lld minV %lld\n", total, hist[0], minV);
}

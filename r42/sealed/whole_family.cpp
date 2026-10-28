// R42 SEALED whole-family check (run only after the blind outputs are frozen and committed).
// Fixed plaintext alphabet PA (7), FREE cipher alphabet, in place. For each setting the given letters fix
// z_i = PA^-1(p_i) + k_i (VIG) or PA^-1(p_i) - k_i (BEAU|VARB, relabelled), which must be the cipher-alphabet
// position of c_i. So ANY cipher alphabet fits exactly when equal ciphertext letters have equal z and different
// ones different z. V = number of position pairs that break this; V = 0 means consistent.
// Build: g++ -std=c++17 -O3 -march=native whole_family.cpp -o whole_family
// Usage: whole_family CT.txt CARTER.txt K1K3.txt LETTERS97 OUT.tsv
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
    vector<int> P; for (int i = 0; i < 97; i++) if (want[i] != '?') P.push_back(i);
    int n = P.size();
    vector<pair<int, int>> eq;   // index pairs (into P) whose ciphertext letters are equal
    for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if (ct[P[a]] == ct[P[b]]) eq.push_back({a, b});
    long long E = eq.size();
    const vector<pair<string, string>> PA = {
        {"AZ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}, {"KRY", "KRYPTOSABCDEFGHIJLMNQUVWXZ"}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"},
        {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"}, {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"},
        {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
    vector<vector<int>> X(7, vector<int>(n));
    for (int a = 0; a < 7; a++) for (int j = 0; j < n; j++) X[a][j] = (int)PA[a].second.find(want[P[j]]);
    vector<long long> hist(n * (n - 1) / 2 + 1, 0); long long total = 0, minV = LLONG_MAX; vector<string> minset;
    vector<int> key(97);
    auto test = [&](const string &label) {
        for (int a = 0; a < 7; a++) for (int op = 0; op < 2; op++) {
            int cz[26] = {0}, zz[97]; long long S = 0, B = 0;
            for (int j = 0; j < n; j++) {
                int z = op == 0 ? X[a][j] + key[P[j]] : X[a][j] - key[P[j]];
                z = ((z % 26) + 26) % 26;
                zz[j] = z; S += cz[z]++;
            }
            for (auto &e : eq) B += zz[e.first] == zz[e.second];
            long long V = E + S - 2 * B;
            hist[V]++; total++;
            if (V < minV) { minV = V; minset.clear(); }
            if (V == minV && minset.size() < 50) minset.push_back(label + "|PA=" + PA[a].first + "|OP=" + (op == 0 ? "VIG" : "BEAU|VARB"));
        }
    };
    for (int b = 5; b <= 6; b++) {
        long long lim = llround(pow(10, b));
        for (long long p = 0; p < lim; p++) {
            long long v = p; string pr(b, '0');
            for (int i = b - 1; i >= 0; i--) { key[i] = v % 10; pr[i] = '0' + key[i]; v /= 10; }
            for (int i = b; i < 97; i++) key[i] = (key[i - b] + key[i - b + 1]) % 10;
            test("C10b" + to_string(b) + "/primer" + pr);
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
    o << "# settings\t" << total << "\n# checked_positions\t" << n << "\n# equal_ciphertext_pairs\t" << E << "\n";
    o << "# consistent_settings(V=0)\t" << hist[0] << "\n# min_V\t" << minV << "\n";
    for (auto &s : minset) o << "# min_setting\t" << s << "\n";
    o << "V\tcount\n";
    for (size_t v = 0; v < hist.size(); v++) if (hist[v]) o << v << "\t" << hist[v] << "\n";
    fprintf(stderr, "settings %lld consistent %lld minV %lld\n", total, hist[0], minV);
}

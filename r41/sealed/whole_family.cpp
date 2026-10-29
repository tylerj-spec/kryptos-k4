// R41 SEALED whole-family check (run only after the blind outputs are frozen and committed).
// For every S_then_T route-order in ROUTES x 7 cipher alphabets x 2 operations x every key of FAMS, asks whether ANY
// plaintext alphabet could put the given letters at the given plaintext positions: with X_i = CT[q_i] (q = perm^-1)
// and y_i = CA^-1(X_i) -/+ k_i, that holds exactly when equal letters sit on equal y and different letters on
// different y. V = number of position pairs that break this; V = 0 means consistent.
// Build: g++ -std=c++17 -O3 -march=native whole_family.cpp -o whole_family
// Usage: whole_family CT.txt CARTER.txt K1K3.txt ROUTES.txt FAMS LETTERS97 OUT.tsv
#include <bits/stdc++.h>
using namespace std;

static string clean(const string &path) {
    ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch);
    return s;
}

int main(int argc, char **argv) {
    if (argc != 8) { fprintf(stderr, "usage: whole_family CT CARTER K1K3 ROUTES FAMS LETTERS97 OUT\n"); return 1; }
    string ct = clean(argv[1]), carter = clean(argv[2]), k1k3 = clean(argv[3]), fams = string(",") + argv[5] + ",", want = argv[6];
    if (ct.size() != 97 || want.size() != 97) { fprintf(stderr, "length\n"); return 1; }
    vector<string> rn; vector<vector<int>> rq;
    { ifstream rf(argv[4]); string line;
      while (getline(rf, line)) {
          istringstream is(line); string nm, od, ps; if (!(is >> nm >> od >> ps) || od != "S_then_T") continue;
          vector<int> perm; stringstream pp(ps); string v; while (getline(pp, v, ',')) perm.push_back(stoi(v));
          vector<int> q(97, -1); for (int j = 0; j < 97; j++) q[perm.at(j)] = j;
          for (int x : q) if (x < 0) { fprintf(stderr, "bad perm %s\n", nm.c_str()); return 1; }
          rn.push_back(nm); rq.push_back(q);
      } }
    vector<int> P, grp; map<char, int> gid;
    for (int i = 0; i < 97; i++) if (want[i] != '?') { P.push_back(i); if (!gid.count(want[i])) { int g = gid.size(); gid[want[i]] = g; } grp.push_back(gid[want[i]]); }
    int n = P.size(), G = gid.size();
    long long E = 0; { vector<int> sz(G, 0); for (int g : grp) sz[g]++; for (int s : sz) E += (long long)s * (s - 1) / 2; }
    vector<pair<int, int>> eq;   // index pairs (into P) holding the same letter
    for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if (grp[a] == grp[b]) eq.push_back({a, b});
    const vector<pair<string, string>> CA = {
        {"AZ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}, {"KRY", "KRYPTOSABCDEFGHIJLMNQUVWXZ"}, {"PALP", "PALIMSETBCDFGHJKNOQRUVWXYZ"},
        {"ABSP", "ABSCIDEFGHJKLMNOPQRTUVWXYZ"}, {"ACAKRY", "KAHUOFNPDLXRBIVSGQTEMZYCJW"}, {"ACAPAL", "ACOZEJWIFRLDQMGUPBNYSHVTKX"},
        {"ACAABS", "ADJOUZBEKPVCGMRXIHNTYSFLQW"}};
    int R = rn.size();
    // X[r][c][j] = CA^-1 of the ciphertext letter holding plaintext position P[j] under route r
    vector<vector<vector<int>>> X(R, vector<vector<int>>(7, vector<int>(n)));
    for (int r = 0; r < R; r++) for (int c = 0; c < 7; c++) for (int j = 0; j < n; j++) X[r][c][j] = (int)CA[c].second.find(ct[rq[r][P[j]]]);
    vector<long long> hist(n * (n - 1) / 2 + 1, 0); long long total = 0, minV = LLONG_MAX; vector<string> minset;
    vector<int> key(97);
    auto test = [&](const string &label) {
        for (int r = 0; r < R; r++) for (int c = 0; c < 7; c++) for (int op = 0; op < 2; op++) {
            int cy[26] = {0}, vv[97]; long long S = 0, B = 0;
            for (int j = 0; j < n; j++) {
                int v = op == 0 ? X[r][c][j] - key[P[j]] : X[r][c][j] + key[P[j]];
                v = ((v % 26) + 26) % 26;
                vv[j] = v; S += cy[v]++;
            }
            for (auto &e : eq) B += vv[e.first] == vv[e.second];
            long long V = E + S - 2 * B;
            hist[V]++; total++;
            if (V < minV) { minV = V; minset.clear(); }
            if (V == minV && minset.size() < 50) minset.push_back(label + "|ROUTE=" + rn[r] + "|CA=" + CA[c].first + "|OP=" + (op == 0 ? "VIG|BEAU" : "VARB"));
        }
    };
    for (int b = 5; b <= 6; b++) {
        if (fams.find(",C10b" + to_string(b) + ",") == string::npos) continue;
        long long lim = llround(pow(10, b));
        for (long long p = 0; p < lim; p++) {
            long long v = p; string pr(b, '0');
            for (int i = b - 1; i >= 0; i--) { key[i] = v % 10; pr[i] = '0' + key[i]; v /= 10; }
            for (int i = b; i < 97; i++) key[i] = (key[i - b] + key[i - b + 1]) % 10;
            test("C10b" + to_string(b) + "/primer" + pr);
        }
    }
    string texts[2] = {carter, k1k3}; string names[2] = {"CARTER", "K1K3"};
    for (int t = 0; t < 2; t++) {
        if (fams.find("," + names[t] + ",") == string::npos) continue;
        for (int d = 0; d < 2; d++) for (int num = 0; num < 2; num++) {
            string s = d ? string(texts[t].rbegin(), texts[t].rend()) : texts[t];
            string al = num ? "KRYPTOSABCDEFGHIJLMNQUVWXZ" : "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            for (size_t off = 0; off + 97 <= s.size(); off++) {
                for (int i = 0; i < 97; i++) key[i] = (int)al.find(s[off + i]);
                test(names[t] + "/" + (d ? "rev" : "fwd") + "/" + (num ? "KRY" : "AZ") + "/off" + to_string(off));
            }
        }
    }
    ofstream o(argv[7]);
    o << "# settings\t" << total << "\n# routes\t" << R << "\n# checked_positions\t" << n << "\n# equal_letter_pairs\t" << E << "\n";
    o << "# consistent_settings(V=0)\t" << hist[0] << "\n# min_V\t" << minV << "\n";
    for (auto &s : minset) o << "# min_setting\t" << s << "\n";
    o << "V\tcount\n";
    for (size_t v = 0; v < hist.size(); v++) if (hist[v]) o << v << "\t" << hist[v] << "\n";
    fprintf(stderr, "settings %lld consistent %lld minV %lld\n", total, hist[0], minV);
}

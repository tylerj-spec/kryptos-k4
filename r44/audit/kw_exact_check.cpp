// R44 audit (SEALED, uses the published letters): independent exact check of PR #13's claim.
// For every 5-digit base-10 Gromark primer, both operation forms, and every R44 keyword alphabet (same candidate rule
// as r44/blind/kwpa_solve.cpp), in place, in both orientations:
//   (a) keyword PLAINTEXT alphabet, free cipher alphabet: z_i = PA^-1(p_i) +/- k_i must satisfy
//       c_i == c_j  <=>  z_i == z_j over the checked positions;
//   (b) keyword CIPHER alphabet, free plaintext alphabet: y_i = CA^-1(c_i) -/+ k_i must satisfy
//       p_i == p_j  <=>  y_i == y_j.
// A setting is feasible exactly when that holds. Prints the feasible count per orientation.
// Usage: kw_exact_check WORDS.tsv CT.txt LETTERS97     ('?' = position not checked)
#include <bits/stdc++.h>
using namespace std;
static string kw_alpha(const string &w) { string o; for (char ch : w + string("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) if (o.find(ch) == string::npos) o += ch; return o; }
int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage\n"); return 1; }
    vector<pair<double, string>> ws;
    { ifstream f(argv[1]); string w; double ex, ed; while (f >> w >> ex >> ed) if (ex > -1e90 && w.size() >= 5 && w.size() <= 10) ws.push_back({ex, w}); }
    sort(ws.begin(), ws.end(), [](auto &a, auto &b) { return a.first != b.first ? a.first > b.first : a.second < b.second; });
    if (ws.size() > 5000) ws.resize(5000);
    set<string> u; for (auto &x : ws) u.insert(kw_alpha(x.second));
    vector<string> alph(u.begin(), u.end());
    string ct; { ifstream f(argv[2]); string l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) ct += toupper(ch); }
    string want = argv[3];
    if (ct.size() != 97 || want.size() != 97) { fprintf(stderr, "length\n"); return 1; }
    vector<int> P; for (int i = 0; i < 97; i++) if (want[i] != '?') P.push_back(i);
    int n = P.size();
    // pair structure: equal-ciphertext pairs and equal-plaintext pairs among checked positions
    vector<char> eqc(n * n), eqp(n * n);
    for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) { eqc[a * n + b] = ct[P[a]] == ct[P[b]]; eqp[a * n + b] = want[P[a]] == want[P[b]]; }
    long long feasA = 0, feasB = 0; vector<string> exA, exB;
    int key[97], v[97];
    for (int p = 0; p < 100000; p++) {
        int x = p; for (int i = 4; i >= 0; i--) { key[i] = x % 10; x /= 10; }
        for (int i = 5; i < 97; i++) key[i] = (key[i - 5] + key[i - 4]) % 10;
        for (size_t ai = 0; ai < alph.size(); ai++) {
            const string &A = alph[ai]; int inv[26]; for (int t = 0; t < 26; t++) inv[A[t] - 'A'] = t;
            for (int orient = 0; orient < 2; orient++) for (int sg = -1; sg <= 1; sg += 2) {
                // orient 0: A is the plaintext alphabet -> z = A^-1(p) + sg*k must have the ciphertext's equality pattern
                // orient 1: A is the cipher alphabet    -> y = A^-1(c) - sg*k must have the plaintext's equality pattern
                for (int j = 0; j < n; j++) {
                    int i = P[j]; int val = orient == 0 ? inv[want[i] - 'A'] + sg * key[i] : inv[ct[i] - 'A'] - sg * key[i];
                    v[j] = ((val % 26) + 26) % 26;
                }
                const vector<char> &E = orient == 0 ? eqc : eqp;
                bool ok = true;
                for (int a = 0; a < n && ok; a++) for (int b = a + 1; b < n; b++) if ((v[a] == v[b]) != (bool)E[a * n + b]) { ok = false; break; }
                if (ok) {
                    string s = to_string(p) + "|" + A + "|" + (sg > 0 ? "+" : "-");
                    if (orient == 0) { feasA++; if (exA.size() < 5) exA.push_back(s); } else { feasB++; if (exB.size() < 5) exB.push_back(s); }
                }
            }
        }
    }
    printf("alphabets %zu, primers 100000, checked positions %d\n", alph.size(), n);
    printf("(a) keyword PA x free CA: feasible %lld\n", feasA); for (auto &s : exA) printf("    %s\n", s.c_str());
    printf("(b) keyword CA x free PA: feasible %lld\n", feasB); for (auto &s : exB) printf("    %s\n", s.c_str());
}

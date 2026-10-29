// R44 audit (SEALED, uses the 24 published letters): independent replication of ChatGPT's R47 (PR #15).
// Running keys: Carter & Mace vol. I (r34/carter_az.txt) and the K1-K3 plaintext, forward/reversed, letters numbered
// AZ or KRY, every 97-letter window; both signs (c = CA[PA(p) + s*k], s = +1 or -1), in place.
// Counts windows feasible (i) with two FREE alphabets (R43 EdgeGraph, audited in audit_edgegraph.cpp) and (ii) with a
// keyword alphabet (4,749 R44 alphabets) on either side and the other free (exact equality-pattern test).
// Usage: rk_exact_check WORDS.tsv CARTER.txt K1K3.txt CT.txt LETTERS97
#define main r43_main
#include "../../r43/blind/word_constraint_beam.cpp"
#undef main
#include <set>
static string kw_alpha2(const string &w) { string o; for (char ch : w + string("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) if (o.find(ch) == string::npos) o += ch; return o; }
static string clean(const string &path) { ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch); return s; }
int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage\n"); return 1; }
    vector<pair<double, string>> ws;
    { ifstream f(argv[1]); string w; double ex, ed; while (f >> w >> ex >> ed) if (ex > -1e90 && w.size() >= 5 && w.size() <= 10) ws.push_back({ex, w}); }
    sort(ws.begin(), ws.end(), [](auto &a, auto &b) { return a.first != b.first ? a.first > b.first : a.second < b.second; });
    ws.resize(5000);
    set<string> u; for (auto &x : ws) u.insert(kw_alpha2(x.second));
    vector<string> alph(u.begin(), u.end());
    vector<array<int, 26>> inv(alph.size());
    for (size_t a = 0; a < alph.size(); a++) for (int t = 0; t < 26; t++) inv[a][alph[a][t] - 'A'] = t;
    string texts[2] = {clean(argv[2]), clean(argv[3])}; const char *tn[2] = {"CARTER", "K1K3"};
    string ct = clean(argv[4]), want = argv[5];
    vector<int> P; for (int i = 0; i < 97; i++) if (want[i] != '?') P.push_back(i);
    int n = P.size();
    long long windows = 0, freeFeas = 0, kwFeas = 0; vector<string> ex;
    const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
    int key[97], v[97];
    for (int t = 0; t < 2; t++) for (int d = 0; d < 2; d++) for (int num = 0; num < 2; num++) {
        string s = d ? string(texts[t].rbegin(), texts[t].rend()) : texts[t];
        const string &al = num ? KRY : AZ; int pos[26]; for (int i = 0; i < 26; i++) pos[al[i] - 'A'] = i;
        for (size_t off = 0; off + 97 <= s.size(); off++) {
            windows++;
            for (int i = 0; i < 97; i++) key[i] = pos[s[off + i] - 'A'];
            for (int sg = -1; sg <= 1; sg += 2) {
                // (i) two free alphabets: CA_index(c) - PA_index(p) = sg * k
                EdgeGraph g; bool ok = true;
                for (int j = 0; j < n && ok; j++) ok = g.add(want[P[j]] - 'A', ct[P[j]] - 'A', ((sg * key[P[j]]) % 26 + 26) % 26);
                string pa, ca;
                if (!(ok && g.compatible() && g.alphabets(pa, ca))) continue;
                freeFeas++;
                // (ii) keyword alphabet on one side (only possible if the free/free model is feasible)
                for (size_t a = 0; a < alph.size(); a++) for (int orient = 0; orient < 2; orient++) {
                    for (int j = 0; j < n; j++) { int i = P[j]; int val = orient == 0 ? inv[a][want[i] - 'A'] + sg * key[i] : inv[a][ct[i] - 'A'] - sg * key[i]; v[j] = ((val % 26) + 26) % 26; }
                    bool good = true;
                    for (int x = 0; x < n && good; x++) for (int y = x + 1; y < n; y++) {
                        bool same = orient == 0 ? ct[P[x]] == ct[P[y]] : want[P[x]] == want[P[y]];
                        if ((v[x] == v[y]) != same) { good = false; break; }
                    }
                    if (good) { kwFeas++; if (ex.size() < 5) ex.push_back(string(tn[t]) + (d ? "/rev" : "/fwd") + (num ? "/KRY" : "/AZ") + "/off" + to_string(off) + "|" + alph[a] + "|" + (orient ? "kwCA" : "kwPA") + "|" + (sg > 0 ? "+" : "-")); }
                }
            }
        }
    }
    printf("windows %lld (x2 signs); free/free feasible window-signs %lld; keyword-feasible %lld\n", windows, freeFeas, kwFeas);
    for (auto &s : ex) printf("  %s\n", s.c_str());
}

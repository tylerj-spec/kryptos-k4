// R44 audit (SEALED, uses the 24 published letters): independent replication of ChatGPT's R46 (PR #14).
// Substitution then transposition: CT[j] = SUB[perm[j]], so SUB[i] = CT[q[i]] with q = perm^-1; the key is indexed by
// plaintext position i. For each route in ROUTES, every 5-digit base-10 Gromark primer and both signs, counts primers
// feasible with two FREE alphabets (R43 EdgeGraph, audited) and settings feasible with one R44 keyword alphabet
// (4,749) on either side and the other free (exact equality-pattern test).
// Usage: rot_exact_check WORDS.tsv ROUTES.txt CT.txt LETTERS97
#define main r43_main
#include "../../r43/blind/word_constraint_beam.cpp"
#undef main
#include <set>
static string kwa(const string &w) { string o; for (char ch : w + string("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) if (o.find(ch) == string::npos) o += ch; return o; }
static string cleanf(const string &path) { ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch); return s; }
int main(int argc, char **argv) {
    if (argc != 5) { fprintf(stderr, "usage\n"); return 1; }
    vector<pair<double, string>> ws;
    { ifstream f(argv[1]); string w; double ex, ed; while (f >> w >> ex >> ed) if (ex > -1e90 && w.size() >= 5 && w.size() <= 10) ws.push_back({ex, w}); }
    sort(ws.begin(), ws.end(), [](auto &a, auto &b) { return a.first != b.first ? a.first > b.first : a.second < b.second; });
    if (ws.size() > 5000) ws.resize(5000);
    set<string> u; for (auto &x : ws) u.insert(kwa(x.second));
    vector<string> alph(u.begin(), u.end());
    vector<array<int, 26>> inv(alph.size());
    for (size_t a = 0; a < alph.size(); a++) for (int t = 0; t < 26; t++) inv[a][alph[a][t] - 'A'] = t;
    string ct = cleanf(argv[3]), want = argv[4];
    vector<int> P; for (int i = 0; i < 97; i++) if (want[i] != '?') P.push_back(i);
    int n = P.size();
    ifstream rf(argv[2]); string line;
    while (getline(rf, line)) {
        istringstream is(line); string name, order, ps; is >> name >> order >> ps;
        vector<int> perm; { stringstream q(ps); string v; while (getline(q, v, ',')) perm.push_back(stoi(v)); }
        vector<int> qinv(97); for (int j = 0; j < 97; j++) qinv[perm[j]] = j;
        string sub(97, '?'); for (int i = 0; i < 97; i++) sub[i] = ct[qinv[i]];
        long long freeFeas = 0, kwFeas = 0; int key[97], v[97];
        for (int p = 0; p < 100000; p++) {
            int x = p; for (int i = 4; i >= 0; i--) { key[i] = x % 10; x /= 10; }
            for (int i = 5; i < 97; i++) key[i] = (key[i - 5] + key[i - 4]) % 10;
            // two free alphabets: the sign is a relabelling, so test +k once and count the primer
            EdgeGraph g; bool ok = true;
            for (int j = 0; j < n && ok; j++) ok = g.add(want[P[j]] - 'A', sub[P[j]] - 'A', key[P[j]]);
            string pa, ca;
            if (!(ok && g.compatible() && g.alphabets(pa, ca))) continue;
            freeFeas++;
            for (int sg = -1; sg <= 1; sg += 2) for (size_t a = 0; a < alph.size(); a++) for (int orient = 0; orient < 2; orient++) {
                for (int j = 0; j < n; j++) { int i = P[j]; int val = orient == 0 ? inv[a][want[i] - 'A'] + sg * key[i] : inv[a][sub[i] - 'A'] - sg * key[i]; v[j] = ((val % 26) + 26) % 26; }
                bool good = true;
                for (int s1 = 0; s1 < n && good; s1++) for (int s2 = s1 + 1; s2 < n; s2++) {
                    bool same = orient == 0 ? sub[P[s1]] == sub[P[s2]] : want[P[s1]] == want[P[s2]];
                    if ((v[s1] == v[s2]) != same) { good = false; break; }
                }
                if (good) { kwFeas++; if (kwFeas <= 3) printf("    keyword-feasible: %s primer %05d %s %s %c\n", name.c_str(), p, alph[a].c_str(), orient ? "kwCA" : "kwPA", sg > 0 ? '+' : '-'); }
            }
        }
        printf("%-14s two-free feasible primers %lld; keyword-feasible settings %lld\n", name.c_str(), freeFeas, kwFeas);
    }
}

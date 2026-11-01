// R52 (Claude) SEALED exact screen, using the 24 published letters, run only as pre-registered.
// For each chain-addition key family (base B, primer length b: k_i = k_{i-b} + k_{i-b+1} mod B, every primer), each
// route-order in ROUTES (ID; four 24x8 rotations as S_then_T and T_then_S), and the letters in LETTERS97:
//   1. two FREE alphabets: exact feasibility (R43 EdgeGraph, audited in r44/audit/audit_edgegraph.cpp);
//   2. for every two-free-feasible key: one KEYWORD alphabet (vocabulary file) on the plaintext or cipher side, the
//      other free, both signs: exact equality-pattern feasibility.
// Placement: in place, letter i -> (P_i, CT_i, k_i); S_then_T (CT[j] = X[perm[j]]) -> (P_i, CT[q_i], k_i);
// T_then_S (CT[j] = sub(P[perm[j]], k_j)) -> (P_i, CT[q_i], k_{q_i}), with q = perm^-1.
// Usage: chain_screen ALPHABETS.txt ROUTES.txt CT.txt LETTERS97 B b [OUT.tsv]
#define main r43_main
#include "../../r43/blind/word_constraint_beam.cpp"
#undef main
static string cleanf(const string &path) { ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch); return s; }
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 1; }
    vector<string> alph; { ifstream f(argv[1]); string a; while (f >> a) if (a.size() == 26) alph.push_back(a); }
    vector<array<int, 26>> inv(alph.size());
    for (size_t a = 0; a < alph.size(); a++) for (int t = 0; t < 26; t++) inv[a][alph[a][t] - 'A'] = t;
    string ct = cleanf(argv[3]), want = argv[4];
    int B = atoi(argv[5]), b = atoi(argv[6]);
    FILE *out = argc > 7 ? fopen(argv[7], "w") : stdout;
    vector<int> P; for (int i = 0; i < 97; i++) if (want[i] != '?') P.push_back(i);
    int n = P.size();
    struct Route { string name, order; vector<int> q; };
    vector<Route> R;
    { ifstream rf(argv[2]); string line;
      while (getline(rf, line)) {
        istringstream is(line); Route r; string ps; is >> r.name >> r.order >> ps;
        vector<int> perm; stringstream q(ps); string v; while (getline(q, v, ',')) perm.push_back(stoi(v));
        r.q.assign(97, 0); for (int j = 0; j < 97; j++) r.q[perm[j]] = j;
        R.push_back(r);
      } }
    long long lim = 1; for (int i = 0; i < b; i++) lim *= B;
    vector<long long> freeCount(R.size(), 0), kwCount(R.size(), 0);
    int key[97], cpos[24], kpos[24], v[24];
    char pl[24], cl[24];
    for (int j = 0; j < n; j++) pl[j] = want[P[j]];
    for (long long p = 0; p < lim; p++) {
        long long x = p; for (int i = b - 1; i >= 0; i--) { key[i] = x % B; x /= B; }
        for (int i = b; i < 97; i++) key[i] = (key[i - b] + key[i - b + 1]) % B;
        for (size_t r = 0; r < R.size(); r++) {
            const Route &rt = R[r];
            for (int j = 0; j < n; j++) {
                int i = P[j];
                if (rt.order == "ID") { cpos[j] = i; kpos[j] = i; }
                else if (rt.order == "S_then_T") { cpos[j] = rt.q[i]; kpos[j] = i; }
                else { cpos[j] = rt.q[i]; kpos[j] = rt.q[i]; }
                cl[j] = ct[cpos[j]];
            }
            EdgeGraph g; bool ok = true;
            for (int j = 0; j < n && ok; j++) ok = g.add(pl[j] - 'A', cl[j] - 'A', key[kpos[j]] % 26);
            string pa, ca;
            if (!(ok && g.compatible() && g.alphabets(pa, ca))) continue;
            freeCount[r]++;
            for (int sg = -1; sg <= 1; sg += 2) for (size_t a = 0; a < alph.size(); a++) for (int orient = 0; orient < 2; orient++) {
                for (int j = 0; j < n; j++) { int val = orient == 0 ? inv[a][pl[j] - 'A'] + sg * key[kpos[j]] : inv[a][cl[j] - 'A'] - sg * key[kpos[j]]; v[j] = ((val % 26) + 26) % 26; }
                bool good = true;
                for (int s1 = 0; s1 < n && good; s1++) for (int s2 = s1 + 1; s2 < n; s2++) {
                    bool same = orient == 0 ? cl[s1] == cl[s2] : pl[s1] == pl[s2];
                    if ((v[s1] == v[s2]) != same) { good = false; break; }
                }
                if (good) { kwCount[r]++; fprintf(out, "KEYWORD_FEASIBLE\tB%d_b%d\t%lld\t%s\t%s\t%s\t%s\t%c\n", B, b, p, rt.name.c_str(), rt.order.c_str(), alph[a].c_str(), orient ? "kwCA" : "kwPA", sg > 0 ? '+' : '-'); }
            }
        }
    }
    for (size_t r = 0; r < R.size(); r++)
        fprintf(out, "SUMMARY\tB%d_b%d\t%s\t%s\tkeys %lld\ttwo_free_feasible %lld\tkeyword_feasible %lld\n", B, b, R[r].name.c_str(), R[r].order.c_str(), lim, freeCount[r], kwCount[r]);
    if (out != stdout) fclose(out);
}

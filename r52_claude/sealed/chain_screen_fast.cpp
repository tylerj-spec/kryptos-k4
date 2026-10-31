// R52 (Claude) SEALED exact screen, fast path; results must equal chain_screen.cpp (checked on B10/b5).
// Same model and output as chain_screen.cpp. Speed-up: for a route the letter graph (which plaintext letter meets which
// ciphertext letter at the 24 checked positions) is fixed; only the key values change. A spanning forest is computed
// once; per key, positions (potentials) are propagated along the forest, every non-forest edge must close
// (pos(c) - pos(p) = k), and letters on one side of a component must get distinct positions. Keys passing that go
// through the full exact check (R43 EdgeGraph incl. global packing) and then the keyword test.
// Keyword test: alphabets are bucketed per route/orientation by the difference at one pair of positions that must hold
// equal values, so each key only fully tests the ~1/26 of alphabets that can pass that pair (exact; same results).
// Usage: chain_screen_fast ALPHABETS.txt ROUTES.txt CT.txt LETTERS97 B b [OUT.tsv]
#define main r43_main
#include "../../r43/blind/word_constraint_beam.cpp"
#undef main
#include <deque>
#include <numeric>
static string cleanf(const string &path) { ifstream f(path); string s, l; while (getline(f, l)) for (char ch : l) if (isalpha((unsigned char)ch)) s += toupper(ch); return s; }
struct TreeEdge { int parent, child, kp, dir; };   // dir +1: child is cipher side (pos = parent + k); -1: child is plain side
struct Route { string name, order; int cp[24], kp[24]; vector<TreeEdge> tree; vector<array<int, 3>> extra; vector<int> verts; };
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
    vector<Route> R;
    { ifstream rf(argv[2]); string line;
      while (getline(rf, line)) {
        istringstream is(line); Route r; string ps; is >> r.name >> r.order >> ps;
        vector<int> perm; stringstream q(ps); string v; while (getline(q, v, ',')) perm.push_back(stoi(v));
        vector<int> qq(97); for (int j = 0; j < 97; j++) qq[perm[j]] = j;
        for (int j = 0; j < n; j++) {
          int i = P[j];
          if (r.order == "ID") { r.cp[j] = i; r.kp[j] = i; }
          else if (r.order == "S_then_T") { r.cp[j] = qq[i]; r.kp[j] = i; }
          else { r.cp[j] = qq[i]; r.kp[j] = qq[i]; }
        }
        // letter graph: vertex 0..25 plain, 26..51 cipher; edge j joins plain want[P[j]] and cipher ct[cp[j]]
        vector<vector<pair<int, int>>> adj(52);
        for (int j = 0; j < n; j++) { int u = want[P[j]] - 'A', w = ct[r.cp[j]] - 'A' + 26; adj[u].push_back({w, j}); adj[w].push_back({u, j}); }
        vector<int> seen(52, 0); vector<char> used(n, 0);
        for (int s = 0; s < 52; s++) {
          if (adj[s].empty() || seen[s]) continue;
          seen[s] = 1; r.verts.push_back(s); deque<int> dq{s};
          r.tree.push_back({-1, s, -1, 0});   // component root marker
          while (!dq.empty()) {
            int u = dq.front(); dq.pop_front();
            for (auto [w, j] : adj[u]) {
              if (used[j]) continue;
              used[j] = 1;
              if (!seen[w]) { seen[w] = 1; r.verts.push_back(w); dq.push_back(w); r.tree.push_back({u, w, r.kp[j], w >= 26 ? 1 : -1}); }
              else r.extra.push_back({want[P[j]] - 'A', ct[r.cp[j]] - 'A' + 26, r.kp[j]});
            }
          }
        }
        R.push_back(r);
      } }
    long long lim = 1; for (int i = 0; i < b; i++) lim *= B;
    vector<long long> freeCount(R.size(), 0), kwCount(R.size(), 0);
    // per route and orientation: one pair (x, y) that must take equal values, and alphabets bucketed by base_x - base_y
    struct KwIndex { int x = -1, y = -1; vector<vector<int>> bucket; };
    vector<array<KwIndex, 2>> KI(R.size());
    for (size_t r = 0; r < R.size(); r++) for (int o = 0; o < 2; o++) {
        KwIndex &ki = KI[r][o];
        for (int s1 = 0; s1 < n && ki.x < 0; s1++) for (int s2 = s1 + 1; s2 < n; s2++) {
            bool same = o == 0 ? ct[R[r].cp[s1]] == ct[R[r].cp[s2]] : want[P[s1]] == want[P[s2]];
            if (same) { ki.x = s1; ki.y = s2; break; }
        }
        if (ki.x < 0) continue;
        ki.bucket.assign(26, {});
        for (size_t a = 0; a < alph.size(); a++) {
            int bx = o == 0 ? inv[a][want[P[ki.x]] - 'A'] : inv[a][ct[R[r].cp[ki.x]] - 'A'];
            int by = o == 0 ? inv[a][want[P[ki.y]] - 'A'] : inv[a][ct[R[r].cp[ki.y]] - 'A'];
            ki.bucket[((bx - by) % 26 + 26) % 26].push_back(a);
        }
    }
    vector<int> allIdx(alph.size()); iota(allIdx.begin(), allIdx.end(), 0);
    int key[97], pos[52], comp[52], v[24];
    char pl[24], cl[24];
    for (int j = 0; j < n; j++) pl[j] = want[P[j]];
    for (long long p = 0; p < lim; p++) {
        long long x = p; for (int i = b - 1; i >= 0; i--) { key[i] = x % B; x /= B; }
        for (int i = b; i < 97; i++) key[i] = (key[i - b] + key[i - b + 1]) % B;
        for (size_t r = 0; r < R.size(); r++) {
            const Route &rt = R[r];
            int cid = -1;
            for (const auto &te : rt.tree) {
                if (te.parent < 0) { pos[te.child] = 0; comp[te.child] = ++cid; continue; }
                int k = key[te.kp] % 26;
                pos[te.child] = ((pos[te.parent] + te.dir * k) % 26 + 26) % 26; comp[te.child] = comp[te.parent];
            }
            bool ok = true;
            for (const auto &e : rt.extra) if (((pos[e[1]] - pos[e[0]] - key[e[2]] % 26) % 26 + 26) % 26 != 0) { ok = false; break; }
            if (!ok) continue;
            unsigned mask[2][26] = {{0}};   // per component, per side: used positions
            for (int vtx : rt.verts) { unsigned &m = mask[vtx >= 26][comp[vtx]]; unsigned bit = 1u << pos[vtx]; if (m & bit) { ok = false; break; } m |= bit; }
            if (!ok) continue;
            // full exact confirmation (incl. global packing) with the audited graph code
            for (int j = 0; j < n; j++) cl[j] = ct[rt.cp[j]];
            EdgeGraph g; bool ok2 = true;
            for (int j = 0; j < n && ok2; j++) ok2 = g.add(pl[j] - 'A', cl[j] - 'A', key[rt.kp[j]] % 26);
            string pa, ca;
            if (!(ok2 && g.compatible() && g.alphabets(pa, ca))) continue;
            freeCount[r]++;
            for (int sg = -1; sg <= 1; sg += 2) for (int orient = 0; orient < 2; orient++) {
              const KwIndex &ki = KI[r][orient];
              const vector<int> *cand = &allIdx;
              if (ki.x >= 0) {   // v_x == v_y  <=>  base_x - base_y == -(+/-) sg * (k_x - k_y)
                int dk = key[rt.kp[ki.x]] - key[rt.kp[ki.y]];
                int t = orient == 0 ? -sg * dk : sg * dk; t = ((t % 26) + 26) % 26;
                cand = &ki.bucket[t];
              }
              for (int a : *cand) {
                for (int j = 0; j < n; j++) { int val = orient == 0 ? inv[a][pl[j] - 'A'] + sg * key[rt.kp[j]] : inv[a][cl[j] - 'A'] - sg * key[rt.kp[j]]; v[j] = ((val % 26) + 26) % 26; }
                bool good = true;
                for (int s1 = 0; s1 < n && good; s1++) for (int s2 = s1 + 1; s2 < n; s2++) {
                    bool same = orient == 0 ? cl[s1] == cl[s2] : pl[s1] == pl[s2];
                    if ((v[s1] == v[s2]) != same) { good = false; break; }
                }
                if (good) { kwCount[r]++; fprintf(out, "KEYWORD_FEASIBLE\tB%d_b%d\t%lld\t%s\t%s\t%s\t%s\t%c\n", B, b, p, rt.name.c_str(), rt.order.c_str(), alph[a].c_str(), orient ? "kwCA" : "kwPA", sg > 0 ? '+' : '-'); }
              }
            }
        }
    }
    for (size_t r = 0; r < R.size(); r++)
        fprintf(out, "SUMMARY\tB%d_b%d\t%s\t%s\tkeys %lld\ttwo_free_feasible %lld\tkeyword_feasible %lld\n", B, b, R[r].name.c_str(), R[r].order.c_str(), lim, freeCount[r], kwCount[r]);
    if (out != stdout) fclose(out);
}

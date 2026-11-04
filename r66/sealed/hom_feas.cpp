// R66 SEALED exact family check (run ONLY after the blind K4 freeze; holds the published letters).
// Homophonic substitution + transposition: P[i] = f(X[i]) with X[perm[j]] = CT[j] (either layer order: f is the same at
// every position). For a fixed permutation, a homophonic decode exists that matches the 24 published letters iff no
// cipher letter would have to stand for two different plaintext letters at the published positions. (The R66 homophone
// cap of 4 never binds on 24 letters.) This is an exact necessary-and-sufficient check per permutation.
// Families: (1) explicit permutations from a routes file ("NAME ORDER p0,...,p96"; deduplicated);
//           (2) every complete columnar transposition of widths 2..WMAX, every column order: fill rows of width w left
//               to right, read the columns top to bottom in key order (FWD), and its inverse (INV).
// Usage: hom_feas TARGET.tsv ROUTES_FILE WMAX OUT_COUNTS.json OUT_FEASIBLE_K4.txt [MAXLIST=100000]
#include <bits/stdc++.h>
using namespace std;
static const int N = 97;
static const vector<pair<int, string>> CLUES = {{21, "EASTNORTHEAST"}, {63, "BERLINCLOCK"}};
static int KPOS[24], KLET[24];

static inline bool feasible(const string &ct, const int *pinv) {   // pinv[i] = j with perm[j] = i
    int m[26]; for (int c = 0; c < 26; c++) m[c] = -1;
    for (int k = 0; k < 24; k++) {
        int c = ct[pinv[KPOS[k]]] - 'A';
        if (m[c] < 0) m[c] = KLET[k]; else if (m[c] != KLET[k]) return false;
    }
    return true;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: hom_feas TARGET.tsv ROUTES WMAX COUNTS.json FEAS_K4.txt [MAXLIST]\n"); return 1; }
    int WMAX = atoi(argv[3]); long MAXLIST = argc > 6 ? atol(argv[6]) : 100000;
    int k = 0; for (auto &cl : CLUES) for (int t = 0; t < (int)cl.second.size(); t++) { KPOS[k] = cl.first + t; KLET[k] = cl.second[t] - 'A'; k++; }
    vector<pair<string, string>> cts; { ifstream f(argv[1]); string line;
        while (getline(f, line)) { if (line.empty() || line.rfind("id\t", 0) == 0) continue; auto t = line.find('\t');
            string ct = line.substr(t + 1); while (!ct.empty() && !isalpha((unsigned char)ct.back())) ct.pop_back();
            if ((int)ct.size() != N) { fprintf(stderr, "bad length\n"); return 1; } cts.push_back({line.substr(0, t), ct}); } }
    // explicit permutations
    vector<pair<string, vector<int>>> ex; set<vector<int>> seen; { ifstream f(argv[2]); string name, order, ps;
        while (f >> name >> order >> ps) { vector<int> p; stringstream ss(ps); string x; while (getline(ss, x, ',')) p.push_back(stoi(x));
            vector<int> s = p; sort(s.begin(), s.end()); for (int i = 0; i < N; i++) if (s[i] != i) { fprintf(stderr, "bad perm %s\n", name.c_str()); return 1; }
            if (seen.insert(p).second) ex.push_back({name, p}); } }
    ofstream fk(argv[5]); long listed = 0;
    string js = "{\"explicit_unique_permutations\": " + to_string(ex.size()) + ", \"wmax\": " + to_string(WMAX) + ", \"cases\": [\n";
    for (size_t ci = 0; ci < cts.size(); ci++) {
        const string &id = cts[ci].first, &ct = cts[ci].second; bool isk4 = id == "K4";
        long ex_feas = 0; vector<long> colF(WMAX + 1, 0), colI(WMAX + 1, 0), colN(WMAX + 1, 0);
        int pinv[N];
        for (auto &e : ex) { for (int j = 0; j < N; j++) pinv[e.second[j]] = j;
            if (feasible(ct, pinv)) { ex_feas++; if (isk4 && listed < MAXLIST) { fk << "EXPLICIT " << e.first << "\n"; listed++; } } }
        for (int w = 2; w <= WMAX; w++) {
            int rows = (N + w - 1) / w, full = N % w == 0 ? w : N % w;   // columns 0..full-1 have `rows` letters
            vector<int> key(w); iota(key.begin(), key.end(), 0);       // key = column read order
            vector<int> perm(N);
            do {
                // FWD: CT is the columns read in key order; perm[j] = X index read at CT position j
                int j = 0, start[16];
                for (int t = 0; t < w; t++) { int c = key[t]; start[c] = j; j += c < full ? rows : rows - 1; }
                for (int i = 0; i < N; i++) pinv[i] = start[i % w] + i / w;
                colN[w]++;
                if (feasible(ct, pinv)) { colF[w]++; if (isk4 && listed < MAXLIST) { fk << "COLUMNAR_FWD w" << w << " key"; for (int c : key) fk << ' ' << c; fk << "\n"; listed++; } }
                // INV: the inverse permutation, i.e. pinv_INV = perm_FWD
                int q[N]; for (int i = 0; i < N; i++) q[pinv[i]] = i;   // q = perm_FWD
                if (feasible(ct, q)) { colI[w]++; if (isk4 && listed < MAXLIST) { fk << "COLUMNAR_INV w" << w << " key"; for (int c : key) fk << ' ' << c; fk << "\n"; listed++; } }
            } while (next_permutation(key.begin(), key.end()));
        }
        long tf = 0, ti = 0, tn = 0; for (int w = 2; w <= WMAX; w++) { tf += colF[w]; ti += colI[w]; tn += colN[w]; }
        js += string(ci ? ",\n" : "") + "{\"id\": \"" + id + "\", \"explicit_feasible\": " + to_string(ex_feas) +
              ", \"columnar_orders\": " + to_string(tn) + ", \"columnar_fwd_feasible\": " + to_string(tf) +
              ", \"columnar_inv_feasible\": " + to_string(ti) + ", \"by_width_fwd\": [";
        for (int w = 2; w <= WMAX; w++) js += (w > 2 ? "," : "") + to_string(colF[w]);
        js += "], \"by_width_inv\": [";
        for (int w = 2; w <= WMAX; w++) js += (w > 2 ? "," : "") + to_string(colI[w]);
        js += "]}";
        fprintf(stderr, "R66 feas %s explicit %ld/%zu columnar fwd %ld inv %ld of %ld each\n", id.c_str(), ex_feas, ex.size(), tf, ti, tn);
    }
    js += "\n]}\n"; ofstream(argv[4]) << js;
    return 0;
}

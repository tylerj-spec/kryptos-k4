// R70 SEALED exhaustive check (run ONLY after the K4 freeze; holds the published letters). For one ciphertext, every
// (source, offset, row, convention) of the blind scan (same rows, conventions and offsets as rk_text_scan.cpp) is
// decrypted at the 24 published plaintext positions only (0-based 21-33 EASTNORTHEAST, 63-73 BERLINCLOCK; plaintext
// order: path order for M1, carved order for M2 and ID), and the matches are counted per block.
// A full block (13/13 or 11/11) is the test: one OCR insertion or deletion between the blocks still leaves one block
// exact at the true offset or the next. Output (JSON): per source, max hits, number of settings with a full block 1,
// a full block 2, both, and a histogram of total hits; plus every setting with a full block (listed raw).
// Usage: exact_scan ROUTES CIPHERTEXT OUT.json NAME1=SRC1 [NAME2=SRC2 ...]
#include <bits/stdc++.h>
using namespace std;
static const string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ";
static const int N = 97;
static const char *CNAME[6] = {"AZ_VIG", "AZ_BEAU", "AZ_VARB", "KRY_VIG", "KRY_BEAU", "KRY_VARB"};
int main(int argc, char **argv) {
  try {
    if (argc < 5) throw runtime_error("usage: exact_scan ROUTES CT OUT NAME=SRC...");
    string ct = argv[2]; if ((int)ct.size() != N) throw runtime_error("ciphertext length");
    vector<pair<int, int>> pos; string b1 = "EASTNORTHEAST", b2 = "BERLINCLOCK";
    for (int i = 0; i < 13; i++) pos.push_back({21 + i, b1[i] - 'A'});
    for (int i = 0; i < 11; i++) pos.push_back({63 + i, b2[i] - 'A'});
    unsigned char DEC[6][26][26];
    for (int cv = 0; cv < 6; cv++) { const string &A = cv < 3 ? AZ : KRY; int op = cv % 3, inv[26]; for (int t = 0; t < 26; t++) inv[A[t] - 'A'] = t;
        for (int c = 0; c < 26; c++) for (int kl = 0; kl < 26; kl++) { int y = inv[c], k = inv[kl]; int x = op == 0 ? y - k : op == 1 ? k - y : y + k;
            DEC[cv][c][kl] = A[((x % 26) + 26) % 26] - 'A'; } }
    struct Row { string path, model; vector<int> cp, idx; };
    vector<Row> rows;
    { Row r; r.path = "ID"; r.model = "M1"; for (int j = 0; j < N; j++) { r.cp.push_back(ct[j] - 'A'); r.idx.push_back(j); } rows.push_back(r); }
    ifstream rf(argv[1]); string line;
    while (getline(rf, line)) { if (line.empty()) continue; stringstream ss(line); string name, order, ps; ss >> name >> order >> ps;
        vector<int> perm; stringstream s2(ps); string x; while (getline(s2, x, ',')) perm.push_back(stoi(x));
        Row m1; m1.path = name; m1.model = "M1"; m1.cp.assign(N, 0); m1.idx.resize(N);
        for (int j = 0; j < N; j++) m1.cp[perm[j]] = ct[j] - 'A';
        for (int t = 0; t < N; t++) m1.idx[t] = t;
        Row m2; m2.path = name; m2.model = "M2"; for (int j = 0; j < N; j++) { m2.cp.push_back(ct[j] - 'A'); m2.idx.push_back(perm[j]); }
        rows.push_back(m1); rows.push_back(m2); }
    if (rows.size() != 21) throw runtime_error("expected 21 rows");
    ofstream out(argv[3]); out << "{\"sources\":{";
    bool firstsrc = true;
    for (int a = 4; a < argc; a++) {
        string s = argv[a]; auto e = s.find('='); string name = s.substr(0, e); ifstream f(s.substr(e + 1)); string t; getline(f, t);
        vector<unsigned char> src(t.size()); for (size_t i = 0; i < t.size(); i++) src[i] = t[i] - 'A';
        long long full1 = 0, full2 = 0, both = 0, hist[25] = {0}; int mx = 0; vector<string> listed;
        for (int r = 0; r < 21; r++) for (int cv = 0; cv < 6; cv++) {
            const Row &rw = rows[r]; int cpos[24], kpos[24], want[24];
            for (int q = 0; q < 24; q++) { cpos[q] = rw.cp[pos[q].first]; kpos[q] = rw.idx[pos[q].first]; want[q] = pos[q].second; }
            int nof = (int)src.size() - N + 1;
            for (int o = 0; o < nof; o++) {
                const unsigned char *key = src.data() + o; int h1 = 0, h2 = 0;
                for (int q = 0; q < 13; q++) h1 += DEC[cv][cpos[q]][key[kpos[q]]] == want[q];
                for (int q = 13; q < 24; q++) h2 += DEC[cv][cpos[q]][key[kpos[q]]] == want[q];
                int h = h1 + h2; hist[h]++; mx = max(mx, h);
                bool f1 = h1 == 13, f2 = h2 == 11; full1 += f1; full2 += f2; both += f1 && f2;
                if (f1 || f2) { char buf[200]; snprintf(buf, sizeof buf, "[\"%s\",%d,\"%s\",\"%s\",\"%s\",%d,%d]", name.c_str(), o, rw.path.c_str(), rw.model.c_str(), CNAME[cv], h1, h2); listed.push_back(buf); }
            }
        }
        if (!firstsrc) out << ","; firstsrc = false;
        out << "\"" << name << "\":{\"max_hits\":" << mx << ",\"full_block1\":" << full1 << ",\"full_block2\":" << full2 << ",\"both\":" << both << ",\"hist\":[";
        for (int h = 0; h <= 24; h++) out << (h ? "," : "") << hist[h];
        out << "],\"full_block_settings\":[";
        for (size_t i = 0; i < listed.size(); i++) out << (i ? "," : "") << listed[i];
        out << "]}";
    }
    out << "}}\n";
  } catch (exception &e) { fprintf(stderr, "error: %s\n", e.what()); return 1; }
  return 0;
}

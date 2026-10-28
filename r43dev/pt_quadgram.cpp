// Development (planted only): two free alphabets, key given. Parallel tempering over (tau, m):
// x_i = tau[c_i] - k_i, p_i = m[x_i]. Moves: swap two tau entries (cipher alphabet) or two m entries (plaintext).
// Input: id ct key(comma) seed ; args: quad in out replicas sweeps Tmin Tmax
#include <bits/stdc++.h>
using namespace std;
static vector<float> Q;
struct Rep { vector<int> tau, m, x, p; double sc; };
int main(int argc, char **argv) {
    { FILE *f = fopen(argv[1], "rb"); Q.resize(456976); if (fread(Q.data(), 4, Q.size(), f) != Q.size()) return 2; fclose(f); }
    ifstream in(argv[2]); FILE *out = fopen(argv[3], "w");
    int R = atoi(argv[4]); long SW = atol(argv[5]); double Tmin = atof(argv[6]), Tmax = atof(argv[7]);
    string line;
    while (getline(in, line)) {
        stringstream ss(line); string id, ct, ks, sd; getline(ss, id, '\t'); getline(ss, ct, '\t'); getline(ss, ks, '\t'); getline(ss, sd, '\t');
        vector<int> k; { stringstream q(ks); string t; while (getline(q, t, ',')) k.push_back(stoi(t)); }
        int n = ct.size(); mt19937_64 rng(stoull(sd));
        vector<int> c(n); for (int i = 0; i < n; i++) c[i] = ct[i] - 'A';
        vector<vector<int>> posc(26); for (int i = 0; i < n; i++) posc[c[i]].push_back(i);
        auto q4 = [&](const vector<int> &p, int s) { return Q[((p[s] * 26 + p[s + 1]) * 26 + p[s + 2]) * 26 + p[s + 3]]; };
        vector<double> T(R); for (int r = 0; r < R; r++) T[r] = Tmin * pow(Tmax / Tmin, (double)r / max(1, R - 1));
        vector<Rep> reps(R);
        for (auto &rp : reps) {
            rp.tau.resize(26); iota(rp.tau.begin(), rp.tau.end(), 0); shuffle(rp.tau.begin(), rp.tau.end(), rng);
            rp.m.resize(26); iota(rp.m.begin(), rp.m.end(), 0); shuffle(rp.m.begin(), rp.m.end(), rng);
            rp.x.resize(n); rp.p.resize(n);
            for (int i = 0; i < n; i++) { rp.x[i] = ((rp.tau[c[i]] - k[i]) % 26 + 26) % 26; rp.p[i] = rp.m[rp.x[i]]; }
            rp.sc = 0; for (int i = 0; i + 3 < n; i++) rp.sc += q4(rp.p, i);
        }
        vector<int> mark(n, 0), st, chg; int stamp = 0;
        double best = -1e18; string bp; long acc_ex = 0, try_ex = 0;
        for (long sw = 0; sw < SW; sw++) {
            for (int r = 0; r < R; r++) {
                Rep &rp = reps[r];
                for (int mv = 0; mv < 100; mv++) {
                    bool tauMove = rng() & 1;
                    int a = rng() % 26, b = rng() % 26; if (a == b) continue;
                    chg.clear();
                    if (tauMove) { for (int i : posc[a]) chg.push_back(i); for (int i : posc[b]) chg.push_back(i); }
                    else { for (int i = 0; i < n; i++) if (rp.x[i] == a || rp.x[i] == b) chg.push_back(i); }
                    if (chg.empty()) continue;
                    stamp++; st.clear();
                    for (int i : chg) for (int s = max(0, i - 3); s <= min(i, n - 4); s++) if (mark[s] != stamp) { mark[s] = stamp; st.push_back(s); }
                    double bs = 0; for (int s : st) bs += q4(rp.p, s);
                    auto apply = [&]() {
                        if (tauMove) { swap(rp.tau[a], rp.tau[b]); for (int i : chg) { rp.x[i] = ((rp.tau[c[i]] - k[i]) % 26 + 26) % 26; rp.p[i] = rp.m[rp.x[i]]; } }
                        else { swap(rp.m[a], rp.m[b]); for (int i : chg) rp.p[i] = rp.m[rp.x[i]]; }
                    };
                    apply();
                    double as = 0; for (int s : st) as += q4(rp.p, s);
                    double d = as - bs;
                    if (d >= 0 || exp(d / T[r]) > (double)(rng() >> 11) / 9007199254740992.0) rp.sc += d; else apply();
                }
                if (rp.sc > best) { best = rp.sc; bp.assign(n, '?'); for (int i = 0; i < n; i++) bp[i] = 'A' + rp.p[i]; }
            }
            for (int r = 0; r + 1 < R; r++) {   // replica exchange between neighbours
                double dl = (reps[r + 1].sc - reps[r].sc) * (1 / T[r] - 1 / T[r + 1]);
                try_ex++;
                if (dl >= 0 || exp(dl) > (double)(rng() >> 11) / 9007199254740992.0) { swap(reps[r], reps[r + 1]); acc_ex++; }
            }
        }
        fprintf(out, "%s\t%.4f\t%s\t%.3f\n", id.c_str(), best, bp.c_str(), (double)acc_ex / max(1L, try_ex)); fflush(out);
    }
}

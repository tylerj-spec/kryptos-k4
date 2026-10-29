// R44 audit of R43's EdgeGraph (r43/blind/word_constraint_beam.cpp), with an encryptor written separately here.
// Build: g++ -std=c++17 -O2 audit_edgegraph.cpp -o audit_edgegraph   (run from r44/audit)
#define main r43_main
#include "../../r43/blind/word_constraint_beam.cpp"
#undef main
#include <random>
static std::string AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
// independent encryptor: c = CA[(PA^-1(p) + k) mod 26]
static std::string enc(const std::string &p, const std::string &pa, const std::string &ca, const std::vector<int> &k) {
    std::string c; for (size_t i = 0; i < p.size(); i++) c += ca[(pa.find(p[i]) + k[i]) % 26]; return c;
}
int main() {
    std::mt19937_64 rng(44001);
    int fails = 0;
    // 1. positive controls: true edges always compatible; rebuilt alphabets re-encrypt exactly (500 random messages)
    for (int t = 0; t < 500; t++) {
        std::string pa = AZ, ca = AZ; std::shuffle(pa.begin(), pa.end(), rng); std::shuffle(ca.begin(), ca.end(), rng);
        std::vector<int> k(97); for (auto &x : k) x = rng() % 10;
        std::string p(97, 'A'); for (auto &ch : p) ch = 'A' + rng() % 26;
        std::string c = enc(p, pa, ca, k);
        EdgeGraph g; bool ok = true;
        for (int i = 0; i < 97; i++) ok &= g.add(p[i] - 'A', c[i] - 'A', k[i]);
        std::string rpa, rca;
        if (!ok || !g.compatible() || !g.alphabets(rpa, rca) || enc(p, rpa, rca, k) != c) { fails++; std::cerr << "positive control failed " << t << "\n"; }
    }
    // 2. soundness: random (wrong) plaintexts; any returned witness must re-encrypt exactly
    long witnesses = 0;
    for (int t = 0; t < 20000; t++) {
        std::string pa = AZ, ca = AZ; std::shuffle(pa.begin(), pa.end(), rng); std::shuffle(ca.begin(), ca.end(), rng);
        std::vector<int> k(97); for (auto &x : k) x = rng() % 10;
        std::string truth(97, 'A'); for (auto &ch : truth) ch = 'A' + rng() % 26;
        std::string c = enc(truth, pa, ca, k);
        int L = 5 + rng() % 30;                     // partial wrong plaintext of length L
        std::string q(L, 'A'); for (auto &ch : q) ch = 'A' + rng() % 26;
        EdgeGraph g; bool ok = true;
        for (int i = 0; i < L && ok; i++) ok &= g.add(q[i] - 'A', c[i] - 'A', k[i]);
        std::string rpa, rca;
        if (ok && g.compatible() && g.alphabets(rpa, rca)) {
            witnesses++;
            if (enc(q, rpa, rca, std::vector<int>(k.begin(), k.begin() + L)) != c.substr(0, L)) { fails++; std::cerr << "unsound witness " << t << "\n"; }
        }
    }
    // 3. packing: locally consistent components that cannot fit together into permutations
    {
        EdgeGraph g; bool ok = true;
        for (int j = 0; j < 13; j++) ok &= g.add(j, 0, (26 - 2 * j) % 26);   // plain 0..12 at even offsets via cipher A
        ok &= g.add(13, 1, 0); ok &= g.add(14, 1, 25);                        // plain 13,14 adjacent via cipher B
        std::string a, b;
        bool comp = g.compatible(), alph = g.alphabets(a, b);
        std::cout << "packing case: add ok " << ok << ", compatible " << comp << ", alphabets " << alph << " (expected 1, 1, 0)\n";
        if (!ok || !comp || alph) fails++;
        EdgeGraph h; ok = true;                                               // same, but the pair at distance 2 fits
        for (int j = 0; j < 13; j++) ok &= h.add(j, 0, (26 - 2 * j) % 26);
        ok &= h.add(13, 1, 0); ok &= h.add(14, 1, 24);
        alph = h.alphabets(a, b);
        std::cout << "packable variant: alphabets " << alph << " (expected 1)\n";
        if (!alph) fails++;
    }
    std::cout << "positive controls 500, random partial witnesses " << witnesses << " (all re-encrypted), failures " << fails << "\n";
    return fails != 0;
}

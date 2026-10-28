// R39 BLIND: rank five-digit decimal chain-addition primers by ciphertext-only
// key-conditioned index of coincidence (Blackman/Gromark). NO plaintext, masks, cribs,
// alphabets or clue positions. Output all 100,000 double scores + deterministic top100.
// Usage: rank_keys CT_FILE SCORES_BIN TOP_TSV
#include <algorithm>
#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N = 97;
constexpr int LIMIT = 100000;
struct Hit {
  double score;
  int primer;
};
static string letters(const string &filename) {
  ifstream f(filename, ios::binary);
  if (!f) throw runtime_error("cannot read ciphertext");
  string t((istreambuf_iterator<char>(f)), {});
  for (char &c : t) if (c >= 'a' && c <= 'z') c = char(c - 'a' + 'A');
  t.erase(remove_if(t.begin(), t.end(), [](char c) { return c < 'A' || c > 'Z'; }), t.end());
  if (t.size() != N) throw runtime_error("ciphertext must have 97 letters");
  return t;
}
int main(int argc, char **argv) {
  try {
    if (argc != 4) throw runtime_error("usage: rank_keys CT_FILE SCORES_BIN TOP_TSV");
    string ct = letters(argv[1]);
    vector<double> scores(LIMIT);
    vector<Hit> hits;
    hits.reserve(LIMIT);
    for (int primer = 0; primer < LIMIT; primer++) {
      int key[N];
      int rem = primer;
      for (int i = 4; i >= 0; i--) { key[i] = rem % 10; rem /= 10; }
      for (int i = 5; i < N; i++) key[i] = (key[i-5] + key[i-4]) % 10;
      int counts[10][26]{}, groups[10]{};
      for (int i = 0; i < N; i++) {
        int g = key[i], c = ct[i] - 'A';
        counts[g][c]++;
        groups[g]++;
      }
      int agreeing = 0, eligible = 0;
      for (int d = 0; d < 10; d++) {
        eligible += groups[d] * (groups[d] - 1);
        for (int c = 0; c < 26; c++) agreeing += counts[d][c] * (counts[d][c] - 1);
      }
      if (!eligible) throw runtime_error("unexpected empty IC denominator");
      double score = double(agreeing) / double(eligible);
      scores[primer] = score;
      hits.push_back({score, primer});
    }
    ofstream out(argv[2], ios::binary);
    out.write(reinterpret_cast<const char *>(scores.data()), scores.size() * sizeof(double));
    if (!out) throw runtime_error("writing scores failed");
    sort(hits.begin(), hits.end(), [](const Hit &a, const Hit &b) {
      return a.score != b.score ? a.score > b.score : a.primer < b.primer;
    });
    ofstream top(argv[3]);
    top << "rank\tscore\tprimer\n" << setprecision(17);
    for (int i = 0; i < 100; i++)
      top << i + 1 << "\t" << hits[i].score << "\t" << setw(5) << setfill('0') << hits[i].primer << "\n";
    if (!top) throw runtime_error("writing top100 failed");
    cerr << "BLIND IC 100000 primers, best=" << hits[0].score << " " << hits[0].primer << "\n";
  } catch (const exception &e) {
    cerr << "ERROR: " << e.what() << "\n";
    return 1;
  }
  return 0;
}

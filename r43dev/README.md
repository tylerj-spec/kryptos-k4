# Development notes: two free alphabets, key given (planted data only, no K4)

These programs were run only on the 8 L109/D1 planted messages (`seed 30009`, calibration passages 0–7). Each
message is encrypted with 5-digit Gromark and two random alphabets, and the solver is given the true key. They have
never touched K4.

- `pt_quadgram.cpp`: parallel tempering over both alphabets at once, scored by English quadgrams.
- `pt_quad_word.cpp`: the same, scored by quadgrams + λ × the ORTH word-model segmentation score (exact words only,
  −7 per skipped letter).

## Findings (L138)

| Run | Message | Best found | True text | Letters wrong |
|---|---|---|---|---|
| quadgram, 24 replicas × 1.5 M sweeps | U0 | −389.5 | −383.6 | 92 |
| | U1 | −395.8 | −395.2 | 86 |
| | U2 | −393.8 | −386.9 | 57 |
| | U3 | **−388.9** | −396.6 | 94 |
| quadgram + 1 × word, 150 k sweeps | U0 | −531.2 | −454.7 | 92 |
| | U3 | −539.2 | −490.4 | 92 |
| quadgram + 2 × word, 150 k sweeps | U0 | −675.3 | −525.9 | 91 |
| | U3 | −673.3 | −584.2 | 86 |

1. **Quadgrams alone cannot identify the text.** With a strong enough search, wrong texts match or beat the true
   text's score (U3 above; U1 within 0.6). Earlier reports (L116, L123) called the failure "search only". They were
   based on weaker searches and are corrected here.
2. **The word model can identify it.** The wrong texts score W −144 to −164; the true texts score −71 to −94.
3. **The open problem is search.** With quadgrams + words, the true text is far better than anything found
   (50–150 points), but parallel tempering does not reach it. The next solver needs word-level moves, for example
   placing dictionary words and propagating the alphabet constraints they imply (crib-dragging with candidate
   words), not single alphabet swaps.

Build: `g++ -std=c++17 -O3 -march=native pt_quad_word.cpp -o pt2`
Usage: `pt2 QUAD.f32 IN.tsv OUT.tsv REPLICAS SWEEPS TMIN TMAX LAMBDA WORDS.tsv`
Input lines are `id <TAB> ciphertext <TAB> key digits (comma-separated) <TAB> seed`.

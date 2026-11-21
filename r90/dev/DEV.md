# R90 development record (spent books only; NOT gate evidence)

**Texts.** Spent books only:
- Peter Pan, Northanger Abbey and White Fang, standing in for the three genres;
- Black Beauty for running keys;
- all with `--raw`.

The seed is 900300, and the set has the gate's full size: 48 positives, 4 extras and 150 negatives. No fresh book, no
K4 ciphertext and no published letter was used. **Nothing was tuned.**
- The solver is exhaustive.
- The retention rule (top 256 by quadgram) was fixed before this run.
- The cuts are R59's.

## Result (`DEV_SUMMARY.json`)
**F26C: GO on every bar.**
- **Recovery:** 48/48 ok with the right key; 48 exact.
- **Stage 1:** the true setting is retained 48/48, and at **rank 1 by quadgram every time**.
- **Coverage:** every stratum and genre is full; masked 12/12.
- **Lowest letter-model score of a recovery:** −1.187.

**Negatives:** **0/150 confident.** The best is −1.709 (an anagram), with word score −2.714. R89's catalog used as a
near-family decoy (F26R89) reaches −1.715. These finite families have no free key, so wrong-family decodes stay far
below the cut (−1.30).

**Extras:** 4/4. Plaintext errors 2/2 at 97/97; ciphertext errors 2/2 at 96 and 95 letters (two letters can change,
as expected).

**Witness:** 1,266/1,266. **Cost:** 202 items in 12 s on 4 cores.

| File | sha256 |
|---|---|
| Development input | b91a4743fdbb620cdbbec1e60bec943c9dcfcab3af40857856598263c9e7a62e |
| Development results | 86242635f1eadc6f21cf5f88fef77ca2df760163d5d2d2b9c9d52a0e453cf274 |

**Isolation:** the first 3 development items reproduce the open run **byte for byte** in the sandbox.

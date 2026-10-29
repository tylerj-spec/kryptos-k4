# R35: audit fixes and mixed-direction rotations (proposal, not a completed scan)

Base: `c1908ca86b034b5bf76a3e2fbc7af9f4407e9965`.

## Code changes and assumptions

- Scanner and independent whole-family checker now normalize ASCII lowercase identically to the existing sealed Python checker. This should leave the uppercase historical regressions unchanged.
- The blind runner rejects reused frozen/out directories, duplicate/unsafe tags, invalid key paths, invalid worker counts, and worker failures; it hashes the scanner source, runner source, compiled scanner, and quadgram data in addition to previous experiment inputs and outputs.
- Independent whole-family counting now fails if a worker exits unsuccessfully or setting counts are incomplete.
- A separate `rot-mixed` generator tests first and second quarter-turns in opposite directions; previously tested `rot` families used one common direction.

## Planned new experiment M1 (NOT YET RUN)

- Family: fixed-alphabet 12 conventions, Carter & Mace running-key text, `rot-mixed 4 28` (5,000 route-orders: 625 width pairs x 2 opposite direction assignments x fwd/inv x 2 operation orders).
- Primary input: exactly the 97-character original K4 ciphertext.
- Controls: at least 2 independently planted plaintexts encrypted using settings sampled from the mixed-direction family before scanning. Additional null ciphertexts recommended.
- Blind search: quadgram top 100, no clue/crib input or access.
- Freeze all source, key, routes, scoring data, ciphertext, output hashes; **commit before reveal**.
- Reveal: separately re-encrypt top candidates and test all 24 public confirmed letters; independently count 24-letter matches across the entire predefined family.
- Outcome labels: full24 + meaningful plaintext = candidate requiring independent confirmation; full24 alone is not a solution; zero full24 + successful plants = exclusion limited to this exact family. A failed plant or count invalidates a negative inference.
- No external validator use; no broad claim about K4 outside this hypothesis family.

This PR changes the research framework and preregisters M1; it does not report any M1 search results.

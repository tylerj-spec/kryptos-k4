# R72 original image source handoff for Claude

**Date:** 2026-11-08. **Status:** research-only. **K4 search:** none.

The machine-readable [image_manifest.json](image_manifest.json) catalogs **all 30** publicly indexed NOVA stills and **five** supplemental Sanborn worksheet and secondary-analysis images, including source links, source-issued captions, provenance status, unanswered questions, and explicit null hashes/dimensions. [OBSERVATIONS.md](OBSERVATIONS.md) separates observed/source-attributed evidence from speculation.

## Image source limitations

This environment could read the public gallery HTML, descriptions and article text, but could not transfer source JPEG/PNG bytes from the image hosts into the working container. Thus **original image binaries are not committed**. Claude can read this markdown and JSON immediately in GitHub, but cannot inspect pixel detail without downloading images on a network-enabled machine. No checksum, crop coordinates or pixel dimensions are invented. [fetch_sources.py](fetch_sources.py) is an opt-in standard-library downloader that attempts to save and validate originals and computes actual SHA-256s, without modifying the repository automatically.

**Source hierarchy:** [2007 NOVA still gallery](https://www.thekryptosproject.com/media/nova/index.php) (independent website's screenshot copies and captions); [PBS original transcript](https://www.pbs.org/wgbh/nova/transcripts/3411_sciencen.html), broadcast **July 24, 2007**; [Kryptools worksheet catalog](https://kryptools.com.about.ag/Sheets/sheets.htm) (third-party dimensions and descriptions); [2014 K3 interpretation](https://www.thekryptosproject.com/kryptos/charts/method.php) (later researcher speculation, not Sanborn's own stated instructions). Kryptools calls footage July 1 rather than July 24; discrepancy unresolved.

## Highest-value frames

| ID | Original clickable source | Gallery label | Safe evidence / unresolved detail |
| --- | --- | --- | --- |
| nova-03 | [frame 3](https://www.thekryptosproject.com/media/nova/images/3_kryptos.jpg) | Second sheet in background | Presence of another sheet does not show a second encryption stage |
| nova-05 | [frame 5](https://www.thekryptosproject.com/media/nova/images/5_kryptos.jpg) | Markings at row ends | Exact shape and coordinates require original pixels |
| nova-16 | [frame 16](https://www.thekryptosproject.com/media/nova/images/16_kryptos.jpg) | Writing at bottom | Paper vs sleeve undetermined |
| nova-17 | [frame 17](https://www.thekryptosproject.com/media/nova/images/17_kryptos.jpg) | **TOP #4** | Kryptools says marking is on plastic; meaning and layer not verified from original motion |
| nova-18–20 | [frames 18](https://www.thekryptosproject.com/media/nova/images/18_kryptos.jpg), [19](https://www.thekryptosproject.com/media/nova/images/19_kryptos.jpg), [20](https://www.thekryptosproject.com/media/nova/images/20_kryptos.jpg) | Folds, two folds | No before/after cipher readout documented |
| nova-22 | [frame 22](https://www.thekryptosproject.com/media/nova/images/22_kryptos.jpg) | Fold in on what line? | Original archive itself poses an unanswered question |
| k3-input | [K3 input](https://kryptools.com.about.ag/Sheets/K3-sheet-partial.jpg) | K3 step 1: 42 × 8 | Verified K3 control, no demonstrated K4 usage |
| k3-intermediate | [K3 second worksheet](https://kryptools.com.about.ag/Sheets/bigtechsheet3.png) | K3 step 2: 14 × 24 | Circled number and arrow need independent original corroboration |
| panel-14x31 | [NOVA panel 4](https://kryptools.com.about.ag/Sheets/Panel4Grid.png) | K3 + separator + K4, 14 × 31 | Catalog reports sheet differs slightly from final copper |

## Externally linked image previews

![TOP number 4, source NOVA still 17](https://www.thekryptosproject.com/media/nova/images/17_kryptos.jpg)

![Two folds, source NOVA still 20](https://www.thekryptosproject.com/media/nova/images/20_kryptos.jpg)

![Row end markings, source NOVA still 5](https://www.thekryptosproject.com/media/nova/images/5_kryptos.jpg)

![K3 second worksheet, source Kryptools](https://kryptools.com.about.ag/Sheets/bigtechsheet3.png)

These are external image links, not Git-repository files. If they don't load in Claude's environment, the metadata and captions still load. Do not infer missing evidence from a blocked image URL.

## Geometry validated in PR #60

- K3's two full rectangular turns reproduce all 336 K3 ciphertext letters (the source-written K3 input and known K3 ciphertext are permitted as a **positive control**).
- The grid dimensions 14 × 31 = 336 K3 + 1 separator + 97 K4 explain 4 + 31 + 31 + 31 K4 placement in a 14 × 31 output sheet.
- Importantly, the R72 14 × 31 arrangement was **generated from the known final carved ciphertext**, not transcribed from the original video image. The original source catalog explicitly says the photograph differs slightly from the final sculpture. Do not claim byte-for-byte or letter-for-letter source photograph equivalence.
- The 98-cell K4 worksheet remains hypothetical; the TOP #4 label is not documentary proof of a 98-cell cipher operation. **R73 stays on hold** pending independent construction evidence.

## Optional local image fetch

Run these from the repository root, in a machine with authorized access to the image hosts:

~~~bash
python3 research/r72_photo_evidence/fetch_sources.py --priority
python3 research/r72_photo_evidence/fetch_sources.py --ids nova-17 nova-20 panel-14x31
python3 research/r72_photo_evidence/fetch_sources.py --all
~~~

The downloader writes to a Git-ignored local originals directory, validates PNG/JPEG magic bytes, and writes a fetch_manifest.json with actual SHA-256s and errors. Confirm copyright/licensing before adding third-party photographic binaries to GitHub.

## Instructions for Claude

1. Read this directory before designing R73. Distinguish original photograph, gallery caption, Kryptools third-party interpretation, and modern 2014 hypothetical overlay explanation.
2. Trace the physical TOP #4 label across **moving video** to determine whether it stays with paper or sleeve; static frames alone cannot answer definitively.
3. Compare any high-quality original panel-14×31 photograph with final copper **without filling uncertain cells from the final carved ciphertext**. Record unknowns explicitly.
4. Audit R72's route novelty: a 26,701-route generated superset is NOT evidence all 26,701 permutations were previously executed. Distinguish GENERATED_EQUIVALENT from CONFIRMED_EXECUTED via actual run manifests.
5. Do not run K4 R73 on the basis of a label or padded-grid analogy alone. Obtain a historically supported new reversible operation and qualify a hidden synthetic recovery gate first.
6. Strict R53: no known K4 plaintext clues or positions in generation, keys, routes, scoring or stopping; postfreeze evaluator only. No K4 guess, no code experiment or merge is part of this package.

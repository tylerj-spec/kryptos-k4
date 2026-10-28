# Source provenance, exclusions and exact dependencies

- Primary K4 ciphertext: copied without changes from the R32 upload, 97 uppercase characters (`runs/k4_ciphertext.txt`).
- Key normalisation: `runs/carter_az.txt` is **exactly** the 282,924-letter R31/R32 Carter-and-Mace, *The Tomb of Tut-Ankh-Amen*, Vol. I (1923), Doran Google-scan A–Z OCR stream, sha256 `6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0`. With 97-letter windows, there are 282,828 starts. No source normalization is silently altered.
- Source textual OCR `source_carter_mace_1923_google_ocr.txt` is the previous R30 source artifact (may contain OCR errors) and is included for provenance. It should not be confused with a proofread historical edition.
- `data/quad_log10.f32` and `data/k1k3_plaintext.txt` are unchanged from the preceding local history bundle; their SHA256 values are recorded in `SOURCE_SHA256.txt`.
- R32 original ZIP provided by user is copied byte-identically as `R32_handoff_original.zip`. Its missing F2 route file is regenerated at audit time from its shipped code; this regeneration does not use known K4 letters. The package includes data missing from R32.

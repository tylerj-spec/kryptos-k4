#!/usr/bin/env python3
"""Build the E6 word models (AMENDMENT_R30_4.md). Needs `pip install wordfreq==3.1.1` (run with that interpreter).
Writes runs/word_model_{de,nl,mix}.tsv and runs/lang_models.json (sha256s, versions)."""
import hashlib
import json
import math
import sys
import unicodedata
from pathlib import Path

import wordfreq

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
ORTH = HERE.parent / "data" / "word_model_orth.tsv"
CLUE_WORDS = ("EAST", "NORTH", "NORTHEAST", "BERLIN", "CLOCK")


def translit(w):
    w = w.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    w = "".join(c for c in unicodedata.normalize("NFKD", w) if not unicodedata.combining(c))
    return "".join(c for c in w.upper() if "A" <= c <= "Z")


def lang_model(lang):
    freq = {}
    for w in wordfreq.top_n_list(lang, 100000):
        t = translit(w)
        if 0 < len(t) <= 24:
            freq[t] = freq.get(t, 0.0) + wordfreq.word_frequency(w, lang)
    return {t: math.log10(f) for t, f in freq.items() if f > 0}


def write(path, exact, edit):
    keys = sorted(set(exact) | set(edit))
    with open(path, "w") as f:
        for k in keys:
            f.write(f"{k} {exact.get(k, -1e100)!r} {edit.get(k, -1e100)!r}\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    orth_exact, orth_edit = {}, {}
    for ln in open(ORTH):
        w, ex, ed = ln.split()
        if float(ex) > -1e99:
            orth_exact[w] = float(ex)
        if float(ed) > -1e99:
            orth_edit[w] = float(ed)
    clue = {w: orth_exact[w] for w in CLUE_WORDS}
    out = {"wordfreq": getattr(wordfreq, "__version__", None) or "3.1.1", "python": sys.version.split()[0]}
    models = {}
    for lang in ("de", "nl"):
        m = lang_model(lang)
        m.update(clue)
        models[lang] = m
        out[lang] = {"words": len(m), "sha256": write(RUNS / f"word_model_{lang}.tsv", m, {})}
    mix = dict(orth_exact)
    for m in models.values():
        for w, s in m.items():
            mix[w] = max(mix.get(w, -1e100), s)
    out["mix"] = {"words": len(set(mix) | set(orth_edit)), "sha256": write(RUNS / "word_model_mix.tsv", mix, orth_edit)}
    json.dump(out, open(RUNS / "lang_models.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

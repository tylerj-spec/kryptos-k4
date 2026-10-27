#!/usr/bin/env python3
"""Build the R30 human-review shortlist from runs/*.json (REVIEW ONLY unless a row meets the candidate rule).
Writes SHORTLIST_R30.md and shortlist_r30.csv. The word split is the scorer's own segmentation: an interpretation
aid, not evidence (unforced letters are optimiser choices)."""
import csv
import json

from r30lib import ANCH, HERE, MODELS, RUNS

FAMILIES = [  # (file stem, title)
    ("e1_ORTH", "E1 chain addition, 6/7-digit primers (ORTH)"),
    ("e2_ORTH", "E2 one-cycle K3-style routes + Gromark (ORTH)"),
    ("g5_ORTHXQ", "E3a 5-digit Gromark, 39 primers (ORTHXQ punctuation model)"),
    ("r2_ORTHXQ", "E3b two-cycle K3-style routes + Gromark (ORTHXQ)"),
    ("e1_ORTHXQ", "E3c E1 passes (ORTHXQ)"),
    ("e2_ORTHXQ", "E3d E2 settings (ORTHXQ)"),
    ("g5_ORTH", "Reference: 5-digit Gromark, 39 primers (ORTH, re-run)"),
    ("r2_ORTH", "Reference: two-cycle routes (ORTH, re-run)"),
]


def load_model(path):
    m = {}
    for ln in open(path):
        w, ex, ed = ln.split()
        m[w] = (float(ex), float(ed))
    return m


def segment(p, model):
    """Best split under the word model (same DP as solver_s2kp: skip -7/letter, up to 2 edit-matched words).
    Skipped letters are lower case; edit-matched (spelling-variant) words are marked with ~."""
    NEG = -1e99
    n = len(p)
    dp = [[(NEG, None)] * 3 for _ in range(n + 1)]
    dp[0][0] = (0.0, None)
    for i in range(n):
        for b in range(3):
            s, _ = dp[i][b]
            if s <= NEG:
                continue
            if s - 7 > dp[i + 1][b][0]:
                dp[i + 1][b] = (s - 7, (i, b, "skip"))
            for j in range(i + 1, min(n, i + 24) + 1):
                w = p[i:j]
                if w not in model:
                    continue
                ex, ed = model[w]
                if ex > -1e99 and s + ex > dp[j][b][0]:
                    dp[j][b] = (s + ex, (i, b, "w"))
                if ed > -1e99 and b < 2 and s + ed > dp[j][b + 1][0]:
                    dp[j][b + 1] = (s + ed, (i, b, "e"))
    b = max(range(3), key=lambda x: dp[n][x][0])
    out, j = [], n
    while j > 0:
        i, pb, kind = dp[j][b][1]
        tok = p[i:j]
        out.append(tok.lower() if kind == "skip" else (tok + "~" if kind == "e" else tok))
        j, b = i, pb
    toks, merged = out[::-1], []
    for t in toks:  # merge runs of skipped letters
        if merged and t.islower() and merged[-1].islower():
            merged[-1] += t
        else:
            merged.append(t)
    return " ".join(merged)


def mask_view(fm):
    return "".join(c if c != "?" else "." for c in fm)


if __name__ == "__main__":
    model = load_model(MODELS["ORTHXQ"])
    rows, md = [], ["# R30 human-review shortlist (REVIEW ONLY unless marked CANDIDATE)", "",
                    "Each row is the raw 97-letter output of the English search for one key setting, exactly as "
                    "decrypted (it re-encrypts to K4 with its own alphabets, checked independently).",
                    "- **Forced mask:** the letters the clue equations force for that key (`.` means the optimiser "
                    "chose the letter). Only forced letters are evidence.",
                    "- **W:** the word score. Readable planted English scores about −69 to −95. The best wrong keys "
                    "reach about −115.",
                    "- **Word split:** the scorer's own segmentation, given as an interpretation aid only.", ""]
    for stem, title in FAMILIES:
        f = RUNS / f"{stem}.json"
        if not f.exists():
            continue
        d = json.load(open(f))
        s, rep = d["summary"], d["replication"]
        md += [f"## {title}", "",
               f"- **Searched:** {s['settings']} settings at {s['restarts']} restarts.",
               f"- **Best W** {s['best_W']:.2f}, median {s['median_W']:.2f}, bar {s['bar']:.2f}; above the bar: "
               f"{s['n_above_bar']}.",
               f"- **Candidates:** {len(s['candidates'])}.", ""]
        for x in d["ranked"][:5]:
            r = rep.get(x["id"])
            status = "CANDIDATE" if x["id"] in s["candidates"] else "REVIEW ONLY"
            repl = (f"replication W {r['W']:.2f}, {r['letters_changed_vs_screen']} letters changed"
                    if r else "not replicated")
            md += [f"**{x['id']}**: W {x['W']:.2f} ({repl}); forced beyond clues {x['forced_beyond_clues']}; "
                   f"{status}", "", "```", f"raw   {x['plaintext']}", f"mask  {mask_view(x['forced_mask'])}",
                   "```", f"Word split (interpretation): `{segment(x['plaintext'], model)}`", ""]
            rows.append({"family": stem, "id": x["id"], "W": round(x["W"], 3),
                         "replication_W": round(r["W"], 3) if r else "",
                         "replication_letters_changed": r["letters_changed_vs_screen"] if r else "",
                         "forced_beyond_clues": x["forced_beyond_clues"], "status": status,
                         "raw_plaintext": x["plaintext"], "forced_mask": x["forced_mask"],
                         "word_split_interpretation": segment(x["plaintext"], model)})
    (HERE / "SHORTLIST_R30.md").write_text("\n".join(md) + "\n")
    with open(HERE / "shortlist_r30.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} shortlist rows")

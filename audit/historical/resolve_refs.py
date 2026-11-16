#!/usr/bin/env python3
"""T4 item 4 (audit/NEXT_STEPS.md): try to resolve the primary SHA-256 references that audit/historical/scan.py could
not tie to a unique file (UNRESOLVED_PATH, AMBIGUOUS_SHORT_NAME). Documentation only; reads files, writes a report.
A reference is RESOLVED_BY_CONTENT when some tracked file, or a file in R32_handoff_original.zip, has exactly the
expected SHA-256 (a basename match is reported but never required); RESOLVED_IN_HISTORY when only an earlier Git
version of a same-named file has it; otherwise NOT_FOUND.
Usage: python3 -I audit/historical/resolve_refs.py INVENTORY.json OUT.json"""
import hashlib
import json
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, check=True).stdout


def main():
    inv = json.loads(Path(sys.argv[1]).read_text())
    by_hash = defaultdict(list)
    for p in git("ls-files", "-z").decode().split("\0"):
        if p and (ROOT / p).is_file():
            by_hash[hashlib.sha256((ROOT / p).read_bytes()).hexdigest()].append(p)
    with zipfile.ZipFile(ROOT / "R32_handoff_original.zip") as z:
        for n in z.namelist():
            if not n.endswith("/"):
                by_hash[hashlib.sha256(z.read(n)).hexdigest()].append("R32_handoff_original.zip!" + n)
    # history: every blob ever committed, by basename
    hist = defaultdict(list)
    for line in git("log", "--all", "--format=", "--raw", "--no-abbrev").decode().splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[0].startswith(":"):
            blob = parts[0].split()[3]
            if set(blob) != {"0"}:
                hist[Path(parts[1]).name].append(blob)
    rows, tally = [], Counter()
    for man in inv["manifests"]["manifests"]:
        for e in man["entries"]:
            if e["status"] not in ("UNRESOLVED_PATH", "AMBIGUOUS_SHORT_NAME"):
                continue
            want = e.get("expected_sha256") or \
                (ROOT / man["manifest"]).read_text().splitlines()[e["line"] - 1].split()[0].lower()
            base = Path(e["target"].split()[-1]).name
            hits = by_hash.get(want, [])
            status, where = ("RESOLVED_BY_CONTENT", hits) if hits else (None, [])
            if not hits:
                for blob in dict.fromkeys(hist.get(base, [])):
                    if hashlib.sha256(git("cat-file", "blob", blob)).hexdigest() == want:
                        status, where = "RESOLVED_IN_HISTORY", ["blob " + blob]
                        break
            status = status or "NOT_FOUND"
            tally[status] += 1
            rows.append({"manifest": man["manifest"], "line": e["line"], "target": e["target"],
                         "scan_status": e["status"], "status": status, "where": where[:5],
                         "basename_match": any(Path(w.split("!")[-1]).name == base for w in where)})
    out = {"total": len(rows), "tally": dict(tally), "rows": rows}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"total": len(rows), "tally": dict(tally)}))


if __name__ == "__main__":
    main()

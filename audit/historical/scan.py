#!/usr/bin/env python3
"""Read-only K4 historical ledger evidence audit. Never loads K4 known plaintext.

This is provenance/hash/commit-order triage, NOT an independent
cryptanalytic reproduction of all historical results.
"""
import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H = re.compile(r"^[0-9a-f]{64}$", re.I)
RID = re.compile(r"^L\d{2,3}$")
ROUND = re.compile(r"^r\d+[a-z]?$")
MAX_SIZE = 150_000_000


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return (r.stdout.decode(errors="replace").strip() if r.returncode == 0 else None)


def tracked():
    r = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    return {x.decode() for x in r.stdout.split(b"\0") if x}


def cells(line):
    """Split unescaped Markdown pipes outside inline code spans."""
    if not line.startswith("|"):
        return []
    buf, out, quoted, escape = [], [], False, False
    for ch in line[1:]:
        if escape:
            buf.append(ch)
            escape = False
        elif ch == "\\":
            buf.append(ch)
            escape = True
        elif ch == chr(96):
            quoted = not quoted
            buf.append(ch)
        elif ch == "|" and not quoted:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    return out


def inventory_ledger(paths):
    text = (ROOT / "LEDGER.md").read_text()
    rows, problems = [], []
    for line in text.splitlines():
        if not re.match(r"^\|\s*L\d+", line):
            continue
        t = cells(line)
        if len(t) == 4:
            t.insert(3, "")  # two legacy rows omitted numbers column
        if len(t) != 5 or not RID.fullmatch(t[0]):
            problems.append({"row": line[:200], "reason": "bad table cells"})
            continue
        rid, method, status, numbers, source = t
        refs = sorted(set(re.findall(r"(?<!\w)(?:r\d+[a-z]?|archive|docs|k4kit|audit)/[A-Za-z0-9_./*\-]+", " ".join(t[1:]))))
        exists, unresolved = [], []
        for ref in refs:
            ref = ref.rstrip(".,;:")
            if ref in paths or (ref.endswith("/") and any(p.startswith(ref) for p in paths)):
                exists.append(ref)
            elif (ref.startswith(("r30/", "r32/")) and
                  "k4kit/" + ref in paths):
                # Historical R30/R32 relocated under the k4kit/ tree;
                # missing top-level path is NOT missing evidence.
                exists.append("k4kit/" + ref)
            elif "*" in ref and any(fnmatch.fnmatch(p, ref) for p in paths):
                exists.append(ref)
            else:
                unresolved.append(ref)
        generic = bool(re.fullmatch(r"(?:C/G|G/C|C|G|C local)", source, flags=re.I))
        provenance = ("GENERIC_SOURCE" if generic else
                      "NO_PATH_IN_ROW" if not refs else
                      "UNRESOLVED_PATH" if unresolved else
                      "REFERENCED_NOT_INDEPENDENTLY_REPLAYED")
        rows.append({
            "id": rid, "method": method, "recorded_status": status,
            "numbers": numbers, "source": source,
            "provenance": provenance, "generic": generic,
            "references": refs, "resolved_paths": exists,
            "unresolved_paths": unresolved,
            "has_exclusion_claim": bool(re.search(r"\bEXCL\b", status, flags=re.I)),
            "audit_verdict": "PENDING_INDEPENDENT_VALIDATION",
        })
    got = [int(row["id"][1:]) for row in rows]
    holes = ["L%02d" % i for i in range(1, max(got) + 1) if i not in got]
    return {
        "count": len(rows), "unique_count": len(set(got)),
        "unused_ids": holes, "parse_problems": problems,
        "generic_source_count": sum(r["generic"] for r in rows),
        "reference_issue_count": sum(bool(r["unresolved_paths"]) for r in rows),
        "provenance_counts": dict(Counter(r["provenance"] for r in rows)),
        "rows": rows,
    }


def digest(f):
    if not f.is_file():
        return None, "MISSING_TARGET"
    if f.stat().st_size > MAX_SIZE:
        return None, "NOT_HASHED_OVERSIZE"
    h = hashlib.sha256()
    with f.open("rb") as io:
        for chunk in iter(lambda: io.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest(), "CHECKED"


def parse_manifest_line(line):
    x = line.strip()
    if not x or x.startswith("#"):
        return None
    match = re.match(r"^([a-f0-9]{64})\s+(.+)$", x, flags=re.I)
    return ((match.group(1).lower(), match.group(2).lstrip("*").strip())
            if match else ("", x))


def resolve_target(manifest, field, paths, expected):
    # A named artifact may be referenced relative to the round or to
    # the FROZEN manifest itself. Never assume a basename means the
    # closest similarly named file; use the digest to disambiguate.
    label = field.split()[-1]
    path = Path(manifest)
    options = [
        label,
        str(path.parent / label),
        str(path.parent.parent / label),
    ]
    for v in options:
        if Path(v).is_absolute() or ".." in Path(v).parts:
            continue
        if v in paths:
            return v, "DIRECT_OR_RELATIVE"
    matches = [p for p in paths if p == label or p.endswith("/" + label)]
    if not matches:
        return None, "UNRESOLVED_PATH"
    if len(matches) == 1:
        return matches[0], "UNIQUE_SUFFIX"
    # Content-addressed matching is stronger than guessed basename.
    matches_by_hash = []
    for p in matches:
        if (ROOT / p).stat().st_size <= MAX_SIZE:
            found, _ = digest(ROOT / p)
            if found == expected:
                matches_by_hash.append(p)
    if len(matches_by_hash) == 1:
        return matches_by_hash[0], "MATCHED_DIGEST_SUFFIX"
    return None, "AMBIGUOUS_SHORT_NAME"


def inventory_manifests(paths):
    wanted = sorted(p for p in paths
                    if (re.match(r"^r\d+[a-z]?/PROTOCOL\.sha256$", p)
                        or (re.match(r"^r\d+[a-z]?/(?:k4|holdout)/", p)
                            and Path(p).name == "FROZEN.sha256")))
    outcome = []
    cached = {}
    for path in wanted:
        rows = []
        for lineno, line in enumerate((ROOT / path).read_text(errors="replace").splitlines(), 1):
            parsed = parse_manifest_line(line)
            if parsed is None:
                continue
            expected, target = parsed
            if not expected:
                rows.append({"line": lineno, "target": target[:160],
                             "status": "NONSTANDARD_FORMAT"})
                continue
            resolved, how = resolve_target(path, target, paths, expected)
            if resolved is None:
                rows.append({"line": lineno, "target": target[:160], "status": how})
                continue
            if resolved not in cached:
                cached[resolved] = digest(ROOT / resolved)
            actual, status = cached[resolved]
            verdict = status if actual is None else (
                "MATCH_AT_HEAD" if actual == expected else "MISMATCH_AT_HEAD")
            rows.append({"line": lineno, "target": target,
                         "resolved": resolved, "resolution": how,
                         "expected_sha256": expected, "actual_sha256": actual,
                         "status": verdict})
        outcome.append({"manifest": path, "entries": rows,
                        "counts": dict(Counter(x["status"] for x in rows))})
    tally = Counter(item["status"] for m in outcome for item in m["entries"])
    return {"manifest_count": len(outcome), "claims": sum(len(m["entries"]) for m in outcome),
            "counts": dict(tally), "manifests": outcome}


def first_added(path):
    text = git("log", "--diff-filter=A", "--reverse", "--format=%H", "HEAD", "--", path)
    return text.splitlines()[0] if text else None


def inventory_order(paths):
    grouped = defaultdict(set)
    for p in paths:
        dirname = p.split("/")[0]
        if ROUND.fullmatch(dirname):
            grouped[dirname].add(p)
    checks = []
    for dirname, fs in sorted(grouped.items()):
        prereg = dirname + "/PREREGISTRATION.md"
        if prereg not in fs:
            continue
        outputs = sorted(p for p in fs if
                         (p.startswith(dirname + "/k4/") and
                          (p.endswith("FROZEN.sha256")
                           or p.endswith("RESULTS.jsonl")
                           or p.endswith("R83A.json")))
                         or p.startswith(dirname + "/holdout/run/FROZEN.sha256"))
        if not outputs:
            continue
        a = first_added(prereg)
        result = []
        for output in outputs:
            b = first_added(output)
            if not a or not b:
                order = "NO_HISTORY"
            elif a == b:
                order = "SAME_INTRO_COMMIT"
            elif git("merge-base", "--is-ancestor", a, b) is not None:
                order = "PREREG_BEFORE_OUTPUT"
            else:
                order = "NO_PREREG_ANCESTRY"
            result.append({"file": output, "output_commit": b, "order": order})
        checks.append({"round": dirname, "prereg_commit": a, "outputs": result})
    return {"rounds_checked": len(checks),
            "counts": dict(Counter(p["order"] for x in checks for p in x["outputs"])),
            "rounds": checks}


def static_flags(paths):
    alerts = []
    for p in sorted(paths):
        if not re.match(r"^r\d+[a-z]?/.+\.(?:py|c|cpp)$", p):
            continue
        if "/blind/" not in p and "/sealed/" not in p:
            continue
        f = ROOT / p
        if f.stat().st_size > 300_000:
            continue
        s = f.read_text(errors="replace")
        if "/blind/" in p and re.search(
            r"reveal_k4|EASTNORTHEAST|BERLINCLOCK|CLUES\s*=", s, flags=re.I
        ):
            alerts.append({"file": p, "check": "BLIND_MODULE_PUBLIC_CLUE_REFERENCE",
                           "classification": "REVIEW_REQUIRED_NOT_PROOF_OF_LEAK"})
        if re.search(r"nsol\s*=\s*np\.ones\([^\n]*int64", s) and "nsol *=" in s:
            alerts.append({"file": p, "check": "INT64_COUNT_MULTIPLICATION",
                           "classification": "REVIEW_REQUIRED_BOUNDARY_RISK"})
    return {"count": len(alerts), "items": alerts}


def markdown(result):
    l, m, o, s = (result[k] for k in ("ledger", "manifests", "order", "static"))
    return "\n".join([
        "# Repository-wide K4 evidence inventory (structural audit)",
        "",
        "This examines source references, recorded conclusions, hash claims,",
        "and source-control ancestry. It is NOT a complete independent",
        "cryptanalytic re-run of the whole ledger.",
        "",
        "## Ledger",
        "",
        "- Rows: %d (unique: %d); unused IDs: %s" %
        (l["count"], l["unique_count"], ", ".join(l["unused_ids"])),
        "- Generic legacy source fields: %d" % l["generic_source_count"],
        "- Rows with unresolved inline file links: %d" % l["reference_issue_count"],
        "- Provenance classes: " + json.dumps(l["provenance_counts"], sort_keys=True),
        "",
        "## Frozen file hashes",
        "",
        "- Manifests: %d; claims: %d" % (m["manifest_count"], m["claims"]),
        "- Statuses: " + json.dumps(m["counts"], sort_keys=True),
        "- Missing/ambiguous paths are NOT by themselves hash mismatches.",
        "- HEAD mismatches require checking the original frozen commit.",
        "",
        "## Time order",
        "",
        "- Rounds with preregistration and recognized output: %d" %
        o["rounds_checked"],
        "- Order results: " + json.dumps(o["counts"], sort_keys=True),
        "- This check does not prove that known K4 plaintext stayed isolated.",
        "",
        "## Static source warnings",
        "",
        "- Heuristic suspicious references or arithmetic: %d" % s["count"],
        "- Each must be manually inspected; a string match is not an exploit.",
        "",
        "## Status",
        "",
        "**AUDIT PENDING:** none of the ledger rows is automatically",
        "promoted to an independently verified cryptanalytic exclusion.",
        "See INVENTORY.json for per-row and per-file provenance, hashes,",
        "and exact review priorities. Preserve original results.",
        "",
    ])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="/tmp/k4-historical-audit")
    a = p.parse_args()
    paths = tracked()
    report = {
        "base_commit": git("rev-parse", "HEAD"),
        "scope": "structural, not a 170-family independent crypto proof",
        "ledger": inventory_ledger(paths),
        "manifests": inventory_manifests(paths),
        "order": inventory_order(paths),
        "static": static_flags(paths),
    }
    folder = Path(a.out)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "INVENTORY.json").write_text(json.dumps(report, indent=2) + "\n")
    summary = markdown(report)
    (folder / "SUMMARY.md").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()

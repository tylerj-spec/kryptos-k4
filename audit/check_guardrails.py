#!/usr/bin/env python3
"""Prospective repository evidence guardrails for Kryptos K4 (schema k4-qa-v2).

Runs on a Git diff and never modifies anything. This is structural
enforcement, NOT proof that a cipher test is correct and NOT a sandbox.
Policy: audit/FUTURE_TEST_GUARDRAILS.md.

Usage: python3 -I audit/check_guardrails.py --base origin/main --head HEAD
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath

SCHEMA = "k4-qa-v2"
ROUND_RE = re.compile(r"^(r[0-9]+[a-z0-9]*)/")
HEX40 = re.compile(r"^[0-9a-f]{40}$", re.I)
HEX64 = re.compile(r"^[0-9a-f]{64}$", re.I)
GIT_CHANGE = re.compile(r"^(A|M|D|T|C|U)\t(.*)$")
LEDGER_ROW = re.compile(r"^[+-]\|\s*(L[0-9]+[a-z]?)\s*\|")
REVIEW_NOTE = re.compile(r"audit/reviews/[A-Za-z0-9_.-]+\.md")
REVIEW_FIELDS = ("Affected ledger IDs:", "Validation:", "Independent review:")

# Top-level directories that are not experiment rounds. A new top-level
# directory outside this list must be a round (rNN...), so that an
# experiment cannot dodge the checks by living somewhere else.
ALLOWED_TOP = {"audit", "docs", "archive", "k4kit", "strictblind", ".github"}

# While this file exists, no new K4 output may be added by any round.
HOLD_FILE = "audit/SEARCH_HOLD.md"

# Files that define the guardrails. Changing them needs a review note.
POLICY_FILES = {
    "audit/check_guardrails.py",
    "audit/run_bounded.py",
    "audit/FUTURE_TEST_GUARDRAILS.md",
    ".github/workflows/k4-research-guardrails.yml",
    HOLD_FILE,
}

FROZEN_NAME = re.compile(r"prereg|protocol|frozen|reveal|sealed_truth", re.I)
K4_DIR = re.compile(r"^(k4[^/]*|frozen|runs)/")
FROZEN_DIR = re.compile(r"^(k4[^/]*|frozen|runs|holdout)/")
RESULT_NAME = re.compile(r"^results/.*(FROZEN|SEALED|GATE|VALIDATE|REVEAL)", re.I)
K4_OUTPUT_NAME = re.compile(r"reveal|frozen", re.I)

# Published K4 plaintext words. A blind solver input must not contain them.
CLUE_WORDS = re.compile(rb"EASTNORTHEAST|NORTHEAST|BERLINCLOCK|BERLIN|CLOCK", re.I)
CLUE_PATH = re.compile(r"reveal|clue|crib|known.?plain|anchor", re.I)


class Repo:
    """Read-only view of a Git repository at two commits."""

    def __init__(self, root, base, head):
        self.root, self.base, self.head = str(root), base, head
        self._trees = {}

    def git(self, *args, check=True):
        r = subprocess.run(["git", *args], cwd=self.root,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and r.returncode:
            raise RuntimeError(f"git {' '.join(args)} failed: "
                               f"{r.stderr.decode(errors='replace')[:300]}")
        return r

    def tree(self, rev):
        if rev not in self._trees:
            out = self.git("ls-tree", "-r", "--name-only", "-z", rev).stdout
            self._trees[rev] = set(out.decode("utf-8").split("\0")) - {""}
        return self._trees[rev]

    def read(self, rev, path):
        r = self.git("show", f"{rev}:{path}", check=False)
        return None if r.returncode else r.stdout

    def changes(self):
        out = self.git("diff", "--name-status", "--no-renames",
                       self.base, self.head).stdout
        result = []
        for line in out.decode("utf-8").splitlines():
            m = GIT_CHANGE.fullmatch(line)
            if not m:
                raise RuntimeError(f"unknown git diff status: {line!r}")
            result.append((m.group(1), m.group(2)))
        return result

    def intro_commit(self, path):
        """First commit reachable from head that added this path."""
        out = self.git("log", "--diff-filter=A", "--format=%H", "--reverse",
                       self.head, "--", path).stdout.decode().split()
        return out[0] if out else None

    def strictly_before(self, earlier, later):
        """True if `earlier` is a proper ancestor of `later`."""
        if not earlier or not later or earlier == later:
            return False
        return self.git("merge-base", "--is-ancestor", earlier, later,
                        check=False).returncode == 0


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def round_of(path):
    m = ROUND_RE.match(path)
    return (m.group(1), path[len(m.group(0)):]) if m else (None, None)


def parse_sha_manifest(text):
    """Yield (digest, path) from 'digest  path' or 'digest  label  path' lines."""
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and HEX64.fullmatch(parts[0]):
            yield parts[0].lower(), parts[-1].lstrip("*")


def resolve(tree, manifest_path, entry):
    """Candidate repo paths for a manifest entry, most specific first."""
    here = PurePosixPath(manifest_path).parent
    seen = []
    for cand in (PurePosixPath(entry), here / entry, here.parent / entry):
        if ".." in cand.parts or cand.is_absolute():
            continue
        s = str(cand)
        if s in tree and s not in seen:
            seen.append(s)
    return seen


def hashed_at_base(repo):
    """Map path -> digests claimed by any SHA-256 manifest present at base."""
    tree = repo.tree(repo.base)
    claims = {}
    for manifest in sorted(p for p in tree if p.endswith(".sha256")):
        data = repo.read(repo.base, manifest)
        if data is None:
            continue
        for digest, entry in parse_sha_manifest(data.decode("utf-8", "replace")):
            for path in resolve(tree, manifest, entry):
                claims.setdefault(path, set()).add(digest)
    return claims


def frozen_by_name(path):
    name, rest = round_of(path)
    if not name or rest.startswith("audit/"):
        return False
    if "/audit/" in "/" + rest:
        return False
    base = rest.rsplit("/", 1)[-1]
    return bool(FROZEN_NAME.search(base) or base.endswith(".sha256")
                or FROZEN_DIR.match(rest) or RESULT_NAME.match(rest))


def is_k4_output(rest):
    """A round file that holds K4 results (TARGET.tsv is an input)."""
    if rest.startswith("audit/") or "/audit/" in "/" + rest:
        return False
    if rest.startswith("holdout/"):
        return False
    base = rest.rsplit("/", 1)[-1]
    if base == "TARGET.tsv":
        return False
    return bool(K4_DIR.match(rest) or K4_OUTPUT_NAME.search(base))


def is_k4_path(rest):
    return is_k4_output(rest) or (
        rest.rsplit("/", 1)[-1] == "TARGET.tsv" and bool(K4_DIR.match(rest)))


def need(cond, message):
    if not cond:
        raise ValueError(message)


def repo_file(repo, value, field):
    need(isinstance(value, str) and value.strip(),
         f"{field}: must be a nonempty repo-relative path")
    p = PurePosixPath(value)
    need(not p.is_absolute() and ".." not in p.parts, f"{field}: unsafe path")
    data = repo.read(repo.head, value)
    need(data is not None, f"{field}: missing file {value}")
    return data


def check_budget(budget):
    need(isinstance(budget, dict), "resource_budget must be an object")
    for name in ("max_wall_seconds", "max_ram_mb", "max_candidates", "max_retries"):
        n = budget.get(name)
        need(isinstance(n, int) and not isinstance(n, bool),
             f"resource_budget.{name} must be integer")
        need(n > 0 or (n == 0 and name == "max_retries"),
             f"resource_budget.{name} invalid value {n}")


def check_freeze(repo, freeze_path, outputs):
    """Every line of FROZEN.sha256 must verify; every frozen output is listed."""
    data = repo_file(repo, freeze_path, "freeze_manifest_path")
    need(PurePosixPath(freeze_path).name == "FROZEN.sha256",
         "freeze_manifest_path must name FROZEN.sha256")
    entries = list(parse_sha_manifest(data.decode("utf-8", "replace")))
    need(entries, f"{freeze_path}: no 'sha256  path' lines")
    tree = repo.tree(repo.head)
    listed = set()
    for digest, entry in entries:
        cands = resolve(tree, freeze_path, entry)
        need(cands, f"{freeze_path}: listed file not found: {entry}")
        good = [c for c in cands if sha256(repo.read(repo.head, c)) == digest]
        need(good, f"{freeze_path}: SHA-256 mismatch for {entry}")
        listed.update(good)
    freeze_commit = repo.intro_commit(freeze_path)
    for path in outputs:
        if path == freeze_path or path in listed:
            continue
        # Not frozen, so it must be a post-freeze product (reveal, verdict).
        need(repo.strictly_before(freeze_commit, repo.intro_commit(path)),
             f"{path}: not listed in {freeze_path} and not committed after "
             "it; freeze outputs first, then reveal in a later commit")
    return listed


def check_resource_logs(repo, d):
    logs = d.get("resource_logs")
    need(isinstance(logs, list) and logs,
         "K4 output requires resource_logs written by audit/run_bounded.py")
    budget = d["resource_budget"]
    for p in logs:
        raw = repo_file(repo, p, "resource_logs")
        try:
            log = json.loads(raw)
        except ValueError as exc:
            raise ValueError(f"{p}: invalid JSON: {exc}") from exc
        need(log.get("status") == "COMPLETE",
             f"{p}: run status is {log.get('status')!r}; an unfinished or "
             "killed job is INCOMPLETE, never a result")
        need(isinstance(log.get("wall_seconds"), (int, float))
             and log["wall_seconds"] <= budget["max_wall_seconds"],
             f"{p}: wall time exceeds the preregistered budget")
        need(isinstance(log.get("max_rss_mb"), (int, float))
             and log["max_rss_mb"] <= budget["max_ram_mb"],
             f"{p}: memory exceeds the preregistered budget")


def check_manifest(repo, name, added):
    mpath = f"{name}/QA_MANIFEST.json"
    raw = repo.read(repo.head, mpath)
    need(raw is not None, f"{name} adds experiment files but lacks {mpath}")
    try:
        d = json.loads(raw)
    except ValueError as exc:
        raise ValueError(f"{mpath}: invalid JSON: {exc}") from exc
    need(isinstance(d, dict) and d.get("schema") == SCHEMA,
         f"{mpath}: schema must be {SCHEMA}")
    need(d.get("mode") in ("blind", "crib_assisted"),
         f"{mpath}: mode must be blind or crib_assisted")
    need(isinstance(d.get("hypothesis"), str) and len(d["hypothesis"].strip()) >= 15,
         f"{mpath}: give a concrete hypothesis and exclusion scope")
    need(isinstance(d.get("not_excluded"), str) and len(d["not_excluded"].strip()) >= 15,
         f"{mpath}: not_excluded must say what this test cannot rule out")

    prereg_path = d.get("preregistration_path")
    prereg = repo_file(repo, prereg_path, "preregistration_path")
    pp = PurePosixPath(prereg_path)
    need(pp.name == "PREREGISTRATION.md" and str(pp.parent) == name,
         "preregistration_path must be the round's own PREREGISTRATION.md")
    sh = d.get("preregistration_sha256")
    need(isinstance(sh, str) and HEX64.fullmatch(sh),
         "preregistration_sha256 must be a full SHA-256")
    need(sha256(prereg) == sh.lower(),
         "preregistration_sha256 does not match the committed file")
    pc = d.get("preregistration_commit")
    need(isinstance(pc, str) and HEX40.fullmatch(pc),
         "preregistration_commit must be a full Git SHA")
    need(repo.git("cat-file", "-e", pc + "^{commit}", check=False).returncode == 0,
         "preregistration_commit does not exist")
    need(repo.git("merge-base", "--is-ancestor", pc, repo.head,
                  check=False).returncode == 0,
         "preregistration_commit is not an ancestor of HEAD")
    at_commit = repo.read(pc, prereg_path)
    need(at_commit is not None and sha256(at_commit) == sh.lower(),
         "preregistration file was not frozen at the claimed commit")

    check_budget(d.get("resource_budget"))

    k4_added = [p for p in added if is_k4_path(round_of(p)[1])]
    outputs = [p for p in added if is_k4_output(round_of(p)[1])]

    if d["mode"] == "blind":
        allow = d.get("solver_inputs")
        need(isinstance(allow, list) and allow,
             "blind solver_inputs must be a nonempty input allowlist")
        for p in allow:
            need(not CLUE_PATH.search(str(p)),
                 f"blind solver input looks like forbidden plaintext material: {p}")
            data = repo_file(repo, p, "solver_inputs")
            need(not CLUE_WORDS.search(data),
                 f"blind solver input contains a published K4 plaintext word: {p}")

    if k4_added:
        need(repo.read(repo.head, HOLD_FILE) is None,
             f"{name}: K4 files added while {HOLD_FILE} is in force; the "
             "owner lifts the hold by deleting that file in a reviewed PR")
        # A sealed synthetic gate must exist, say GO, and predate any K4 file.
        gate_path = d.get("synthetic_gate_path")
        gate = repo_file(repo, gate_path, "synthetic_gate_path")
        need(gate.strip(), "synthetic gate file is empty")
        need(d.get("gate_verdict") == "GO",
             "gate_verdict must be GO before K4 is touched; a failed or "
             "missing gate means do not run K4 and do not record an exclusion")
        gate_commit = repo.intro_commit(gate_path)
        for path in k4_added:
            intro = repo.intro_commit(path)
            need(repo.strictly_before(pc, intro),
                 f"{path}: preregistration must be in a different earlier commit")
            need(repo.strictly_before(gate_commit, intro),
                 f"{path}: synthetic gate must be committed before any K4 file")

    if outputs:
        need(d.get("stage") in ("frozen", "validated"),
             "K4 output requires stage frozen or validated")
        check_freeze(repo, d.get("freeze_manifest_path"), outputs)
        check_resource_logs(repo, d)
    else:
        need(d.get("stage") in ("preregistered", "gate"),
             "without K4 output the stage must be preregistered or gate")
    return d


def check_ledger(repo, changes, violations):
    notes = [p for st, p in changes if st == "A" and REVIEW_NOTE.fullmatch(p)]
    touched = sorted({p for _, p in changes if p == "LEDGER.md" or p in POLICY_FILES})
    if not touched:
        return
    if not notes:
        violations.append(
            f"{', '.join(touched)} changed without a NEW audit/reviews/*.md evidence note")
        return
    cited = set()
    for p in notes:
        text = repo.read(repo.head, p).decode("utf-8", "replace")
        missing = [f for f in REVIEW_FIELDS if f not in text]
        if missing:
            violations.append(f"{p}: must contain {' and '.join(missing)}")
        for line in text.splitlines():
            if line.startswith("Affected ledger IDs:"):
                cited.update(re.findall(r"L[0-9]+[a-z]?", line))
    if "LEDGER.md" in touched:
        diff = repo.git("diff", "-U0", repo.base, repo.head, "--", "LEDGER.md").stdout
        rows = {m.group(1) for line in diff.decode("utf-8", "replace").splitlines()
                for m in [LEDGER_ROW.match(line)] if m}
        uncited = sorted(rows - cited)
        if uncited:
            violations.append(
                "LEDGER.md rows changed but not named in a new review note's "
                f"'Affected ledger IDs:' line: {', '.join(uncited)}")


def audit_diff(root, base, head):
    repo = Repo(root, base, head)
    changes = repo.changes()
    base_tree = repo.tree(base)
    violations = []

    # 1. Frozen evidence is immutable: by name, and by any valid hash claim.
    claims = None
    immutable = 0
    for state, path in changes:
        if state == "A":
            continue
        reason = "frozen/prereg artifact" if frozen_by_name(path) else None
        if reason is None:
            if claims is None:
                claims = hashed_at_base(repo)
            old = repo.read(base, path)
            if old is not None and sha256(old) in claims.get(path, ()):
                reason = "file pinned by a committed SHA-256 manifest"
        if reason:
            immutable += 1
            violations.append(
                f"{path}: immutable {reason} modified or deleted; add an erratum")

    # 2. Experiments live in round directories.
    base_tops = {p.split("/", 1)[0] for p in base_tree if "/" in p}
    for top in sorted({p.split("/", 1)[0] for st, p in changes
                       if st == "A" and "/" in p}):
        if top not in base_tops and top not in ALLOWED_TOP and not ROUND_RE.match(top + "/"):
            violations.append(
                f"{top}/: new top-level directory; experiments must live in rNN/")

    # 3. Rounds that add experiment files need a valid QA manifest.
    added = {}
    for state, path in changes:
        name, rest = round_of(path)
        if name and state == "A":
            added.setdefault(name, []).append(path)
    checked = []
    for name, paths in sorted(added.items()):
        is_new = not any(p.startswith(name + "/") for p in base_tree)
        has_k4 = any(is_k4_path(round_of(p)[1]) for p in paths)
        has_code = any(not p.endswith(".md") for p in paths)
        if has_k4 or (is_new and has_code):
            checked.append(name)
            try:
                check_manifest(repo, name, paths)
            except (RuntimeError, ValueError, TypeError, KeyError) as exc:
                violations.append(f"{name}: {exc}")

    # 4. Ledger and guardrail-policy changes need an evidence note.
    check_ledger(repo, changes, violations)

    return {"changed_paths": len(changes),
            "immutable_edits": immutable,
            "rounds_checked": checked,
            "search_hold": repo.read(head, HOLD_FILE) is not None,
            "violations": violations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = audit_diff(args.repo, args.base, args.head)
    print(json.dumps(result, indent=2))
    if result["violations"]:
        print("FAIL: guardrail violations need corrections or additive errata",
              file=sys.stderr)
        return 1
    print("PASS: structural integrity checks (not scientific validation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

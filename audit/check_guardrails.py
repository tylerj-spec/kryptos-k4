#!/usr/bin/env python3
"""Prospective repository evidence guardrails for Kryptos K4.

Runs on PR diff, never modifies historical artifacts. This is structural
enforcement, NOT proof of cipher correctness or a complete security sandbox.

Usage: python3 -I audit/check_guardrails.py --base origin/main --head HEAD
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROUND_RE = re.compile(r"^(r[0-9]+[a-z]?)/")
HEX40 = re.compile(r"^[0-9a-f]{40}$", re.I)
HEX64 = re.compile(r"^[0-9a-f]{64}$", re.I)
GIT_CHANGE = re.compile(r"^(A|M|D|T|C|U)\t(.*)$")


def command(*args, cwd=None, check=True):
    result = subprocess.run(
        list(args), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(
            f"{' '.join(args)} failed ({result.returncode}): "
            f"{result.stderr.decode(errors='replace')[:400]}"
        )
    return result


def changed_paths(base, head, cwd=None):
    out = command("git", "diff", "--name-status", "--no-renames", base, head, cwd=cwd).stdout
    changes = []
    for line in out.decode("utf-8").splitlines():
        match = GIT_CHANGE.fullmatch(line)
        if not match:
            raise RuntimeError(f"unknown git diff status: {line!r}")
        changes.append((match.group(1), match.group(2)))
    return changes


def frozen_path(path):
    match = ROUND_RE.match(path)
    if not match:
        return False
    rest = path[len(match.group(0)):]
    if rest in ("PREREGISTRATION.md", "PROTOCOL.sha256", "FROZEN.sha256"):
        return True
    if rest.startswith("k4/") and not rest.startswith("k4/audit/"):
        return True
    if rest.startswith("holdout/") and not rest.startswith("holdout/audit/"):
        return True
    if re.match(r"results/.*(?:FROZEN|SEALED|GATE|VALIDATE|REVEAL).*", rest, flags=re.I):
        return True
    return False


def new_k4_path(path):
    m = ROUND_RE.match(path)
    if not m:
        return None
    rest = path[len(m.group(0)):]
    if rest.startswith("k4/") and not rest.startswith("k4/audit/"):
        return m.group(1)
    return None


def validated_path(root, value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: must be a nonempty repo-relative path")
    posix = Path(value)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"{field}: unsafe path")
    f = root / posix
    if not f.is_file():
        raise ValueError(f"{field}: missing file {value}")
    return f


def nonnegative_budget(budget):
    expected = ("max_wall_seconds", "max_ram_mb", "max_candidates", "max_retries")
    if not isinstance(budget, dict):
        raise ValueError("resource_budget must be an object")
    for name in expected:
        n = budget.get(name)
        if not isinstance(n, int) or isinstance(n, bool):
            raise ValueError(f"resource_budget.{name} must be integer")
        if n < 0 or (n == 0 and name != "max_retries"):
            raise ValueError(f"resource_budget.{name} invalid value {n}")


def manifest_for_round(root, round_name, head, added_k4):
    path = root / round_name / "QA_MANIFEST.json"
    if not path.is_file():
        raise ValueError(f"{round_name} creates K4 data but lacks {round_name}/QA_MANIFEST.json")
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if d.get("schema") != "k4-qa-v1":
        raise ValueError(f"{path}: unsupported schema")
    if d.get("mode") not in ("blind", "crib_assisted"):
        raise ValueError(f"{path}: mode must be blind or crib_assisted")
    if not isinstance(d.get("hypothesis"), str) or len(d["hypothesis"].strip()) < 15:
        raise ValueError(f"{path}: give a concrete hypothesis and exclusion scope")
    prereg = validated_path(root, d.get("preregistration_path"), "preregistration_path")
    if prereg.name != "PREREGISTRATION.md" or prereg.parent.name != round_name:
        raise ValueError("preregistration_path must be the round's original PREREGISTRATION.md")
    sh = d.get("preregistration_sha256")
    if not isinstance(sh, str) or not HEX64.fullmatch(sh):
        raise ValueError("preregistration_sha256 must be a full SHA-256")
    current = hashlib.sha256(prereg.read_bytes()).hexdigest()
    if current != sh.lower():
        raise ValueError("preregistration_sha256 does not match the committed file")
    prereg_commit = d.get("preregistration_commit")
    if not isinstance(prereg_commit, str) or not HEX40.fullmatch(prereg_commit):
        raise ValueError("preregistration_commit must be a full Git SHA")
    commit = command("git", "cat-file", "-e", prereg_commit + "^{commit}",
                     cwd=root, check=False)
    if commit.returncode:
        raise ValueError("preregistration_commit does not exist")
    if command("git", "merge-base", "--is-ancestor", prereg_commit, head,
               cwd=root, check=False).returncode:
        raise ValueError("preregistration_commit is not an ancestor of HEAD")
    frozen_prereg = command(
        "git", "show", f"{prereg_commit}:{d['preregistration_path']}",
        cwd=root, check=False,
    )
    if frozen_prereg.returncode or hashlib.sha256(frozen_prereg.stdout).hexdigest() != sh.lower():
        raise ValueError("preregistration file was not frozen at the claimed commit")
    nonnegative_budget(d.get("resource_budget"))
    if d.get("mode") == "blind":
        allow = d.get("solver_inputs")
        if not isinstance(allow, list) or not allow:
            raise ValueError("blind solver_inputs must be a nonempty input allowlist")
        for p in allow:
            if re.search(r"reveal|clue|crib|known.?plain", str(p), re.I):
                raise ValueError(f"blind solver input looks like forbidden plaintext material: {p}")
            validated_path(root, p, "solver_inputs")
    gate = validated_path(root, d.get("synthetic_gate_path"), "synthetic_gate_path")
    if not gate.read_bytes():
        raise ValueError("synthetic gate file is empty")

    # Adding K4 result data requires preregistration to predate the
    # earliest added output commit. A plain TARGET.tsv can be a prereg
    # input, not a result; everything else is considered an output.
    outputs = [p for p in added_k4 if not p.endswith("/TARGET.tsv")]
    if outputs:
        freeze = validated_path(root, d.get("freeze_manifest_path"), "freeze_manifest_path")
        if freeze.name != "FROZEN.sha256":
            raise ValueError("freeze_manifest_path must name FROZEN.sha256")
        if not freeze.read_bytes():
            raise ValueError("frozen manifest is empty")
        if d.get("stage") not in ("frozen", "validated"):
            raise ValueError("K4 output requires stage frozen or validated")
        for path in outputs:
            intro = command(
                "git", "log", "--diff-filter=A", "--format=%H", "--reverse",
                head, "--", path, cwd=root,
            ).stdout.decode().strip().splitlines()
            if intro:
                commit = intro[0]
                if commit == prereg_commit or command(
                    "git", "merge-base", "--is-ancestor", prereg_commit, commit,
                    cwd=root, check=False,
                ).returncode:
                    raise ValueError(
                        f"{path}: preregistration must be in a different earlier commit"
                    )
    return d


def audit_diff(root, base, head):
    changes = changed_paths(base, head, cwd=root)
    violations = []
    added_k4 = {}
    for state, path in changes:
        if state != "A" and frozen_path(path):
            violations.append(
                f"{path}: immutable frozen/prereg artifact modified or deleted; add an erratum"
            )
        r = new_k4_path(path)
        if r and state == "A":
            added_k4.setdefault(r, []).append(path)
    if any(p == "LEDGER.md" for _, p in changes):
        review_paths = [p for st, p in changes if st == "A" and
                        re.fullmatch(r"audit/reviews/[A-Za-z0-9_.-]+\.md", p)]
        if not review_paths:
            violations.append(
                "LEDGER.md changed without a NEW audit/reviews/*.md evidence note"
            )
        else:
            for p in review_paths:
                review = (root / p).read_text(encoding="utf-8")
                if "Affected ledger IDs:" not in review or "Validation:" not in review:
                    violations.append(
                        f"{p}: must contain Affected ledger IDs: and Validation:"
                    )
    for name, paths in sorted(added_k4.items()):
        try:
            manifest_for_round(root, name, head, paths)
        except (RuntimeError, ValueError, TypeError) as exc:
            violations.append(str(exc))
    return {"changed_paths": len(changes),
            "immutable_edits": sum(1 for st, p in changes if st != "A" and frozen_path(p)),
            "rounds_with_new_k4_artifacts": sorted(added_k4),
            "violations": violations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    result = audit_diff(root, args.base, args.head)
    print(json.dumps(result, indent=2))
    if result["violations"]:
        print("FAIL: guardrail violations need corrections or additive errata", file=sys.stderr)
        return 1
    print("PASS: structural integrity checks (not scientific validation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

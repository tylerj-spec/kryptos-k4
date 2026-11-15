#!/usr/bin/env python3
"""Adversarial synthetic git-repository checks for the prospective K4 guardrails.

No public K4 ciphertext, plaintext, or clue positions are used.
Run: python3 -I audit/tests/test_guardrails.py
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_guardrails as G  # noqa: E402


def git(root, *args):
    cp = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if cp.returncode:
        raise AssertionError(f"git {' '.join(args)}: {cp.stderr}")
    return cp.stdout.strip()


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


class GuardrailTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "K4 QA Fixture")
        git(self.root, "config", "user.email", "qa-fixture@example.test")
        write(self.root, "LEDGER.md", "# Synthetic only\n")
        write(self.root, "r901/PREREGISTRATION.md",
              "# Synthetic cipher preregistration\nNO REAL K4 DATA\n")
        self.base = commit(self.root, "baseline")
        self.prereg = (self.root / "r901/PREREGISTRATION.md").read_bytes()

    def audit(self):
        return G.audit_diff(self.root, self.base, git(self.root, "rev-parse", "HEAD"))

    def manifest(self, stage="preregistered", **overrides):
        template = {
            "schema": "k4-qa-v1",
            "mode": "blind",
            "stage": stage,
            "hypothesis": "Synthetic in-place alphabet transform with known inverse",
            "preregistration_path": "r901/PREREGISTRATION.md",
            "preregistration_commit": self.base,
            "preregistration_sha256": hashlib.sha256(self.prereg).hexdigest(),
            "synthetic_gate_path": "r901/holdout/GATE.json",
            "solver_inputs": ["r901/k4/TARGET.tsv"],
            "resource_budget": {
                "max_wall_seconds": 120,
                "max_ram_mb": 512,
                "max_candidates": 10000,
                "max_retries": 1,
            },
        }
        template.update(overrides)
        return template

    def test_new_preregistration_alone_allowed(self):
        write(self.root, "r902/PREREGISTRATION.md", "# Synthetic future experiment\n")
        commit(self.root, "new prereg")
        self.assertEqual(self.audit()["violations"], [])

    def test_old_prereg_change_rejected(self):
        write(self.root, "r901/PREREGISTRATION.md", "# silently revised\n")
        commit(self.root, "modify historical prereg")
        violations = self.audit()["violations"]
        self.assertTrue(any("immutable" in x and "PREREGISTRATION" in x for x in violations))

    def test_old_target_and_frozen_output_rejected(self):
        write(self.root, "r901/k4/run/FROZEN.sha256", "toy hash\n")
        commit(self.root, "synthetic output baseline update")
        # Compare two later commits only, so the previously present file is immutable.
        older = git(self.root, "rev-parse", "HEAD")
        write(self.root, "r901/k4/run/FROZEN.sha256", "different toy hash\n")
        commit(self.root, "edit old frozen file")
        result = G.audit_diff(self.root, older, git(self.root, "rev-parse", "HEAD"))
        self.assertTrue(any("immutable" in x for x in result["violations"]))

    def test_ledger_requires_new_review(self):
        write(self.root, "LEDGER.md", "# Synthetic questionable exclusion\n")
        commit(self.root, "edit ledger without note")
        self.assertTrue(any("without a NEW" in x for x in self.audit()["violations"]))

    def test_ledger_review_must_be_explicit(self):
        write(self.root, "LEDGER.md", "# Synthetic corrected exclusion\n")
        write(self.root, "audit/reviews/example.md", "# Synthetic audit\n")
        commit(self.root, "fake review")
        self.assertTrue(any("Affected ledger IDs" in x for x in self.audit()["violations"]))

    def test_ledger_with_new_review_accepted(self):
        write(self.root, "LEDGER.md", "# Synthetic qualified result\n")
        write(self.root, "audit/reviews/example.md",
              "# Review\nAffected ledger IDs: L999\nValidation: independent fixture\n")
        commit(self.root, "ledger qualified with evidence note")
        self.assertEqual(self.audit()["violations"], [])

    def test_new_k4_missing_manifest_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "ID\tTEXT\nSYNTHETIC\tABCDEFG\n")
        commit(self.root, "K4 target without provenance")
        self.assertTrue(any("lacks r901/QA_MANIFEST.json" in x
                            for x in self.audit()["violations"]))

    def test_new_k4_prereg_and_budget_accepted(self):
        write(self.root, "r901/k4/TARGET.tsv", "ID\tTEXT\nSYNTHETIC\tABCDEFG\n")
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(self.manifest()) + "\n")
        commit(self.root, "input manifest and gated synthetic evidence")
        self.assertEqual(self.audit()["violations"], [])

    def test_missing_holdout_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(self.manifest()) + "\n")
        commit(self.root, "no positive controls")
        self.assertTrue(any("synthetic_gate_path" in x for x in self.audit()["violations"]))

    def test_bad_prereg_hash_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(
            self.manifest(preregistration_sha256="0" * 64)) + "\n")
        commit(self.root, "bad prereg hash")
        self.assertTrue(any("preregistration_sha256" in x for x in self.audit()["violations"]))

    def test_zero_budget_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        m = self.manifest()
        m["resource_budget"]["max_wall_seconds"] = 0
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(m) + "\n")
        commit(self.root, "bad compute budget")
        self.assertTrue(any("max_wall_seconds" in x for x in self.audit()["violations"]))

    def test_new_k4_output_requires_freeze_and_preceding_prereg(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        m = self.manifest(stage="frozen")
        m["freeze_manifest_path"] = "r901/k4/run/FROZEN.sha256"
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(m) + "\n")
        write(self.root, "r901/k4/run/FROZEN.sha256", "fixture\n")
        write(self.root, "r901/k4/run/RESULT.json", '{"ciphertext_only":true}\n')
        commit(self.root, "freeze synthetic outputs")
        self.assertEqual(self.audit()["violations"], [])

    def test_blind_input_allowlist_rejects_clue_file(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        write(self.root, "r901/known_plaintext_clue.txt", "FAKE\n")
        m = self.manifest(solver_inputs=[
            "r901/k4/TARGET.tsv", "r901/known_plaintext_clue.txt"])
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(m) + "\n")
        commit(self.root, "inject forbidden inputs")
        self.assertTrue(any("forbidden plaintext" in x for x in self.audit()["violations"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)

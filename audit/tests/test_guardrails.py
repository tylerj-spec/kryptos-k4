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
            "schema": "k4-qa-v2",
            "mode": "blind",
            "stage": stage,
            "hypothesis": "Synthetic in-place alphabet transform with known inverse",
            "preregistration_path": "r901/PREREGISTRATION.md",
            "preregistration_commit": self.base,
            "preregistration_sha256": hashlib.sha256(self.prereg).hexdigest(),
            "not_excluded": "Any second stage, other alphabets, longer keys",
            "synthetic_gate_path": "r901/holdout/GATE.json",
            "gate_verdict": "GO",
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

    def put_manifest(self, **kw):
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(self.manifest(**kw)) + "\n")

    def gate(self):
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        return commit(self.root, "sealed synthetic gate")

    def frozen_run(self, log=None, freeze=None, extra=None):
        """prereg (base) -> gate -> target -> frozen outputs, as separate commits."""
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest()
        commit(self.root, "target")
        result = '{"ciphertext_only":true}\n'
        write(self.root, "r901/k4/run/RESULT.json", result)
        logtext = json.dumps(log or {
            "status": "COMPLETE", "wall_seconds": 3.0, "max_rss_mb": 40.0}) + "\n"
        write(self.root, "r901/k4/run/RESOURCE_LOG.json", logtext)
        loghash = hashlib.sha256(logtext.encode()).hexdigest() + "  log  RESOURCE_LOG.json\n"
        write(self.root, "r901/k4/run/FROZEN.sha256", (freeze if freeze is not None else
              hashlib.sha256(result.encode()).hexdigest() + "  results  RESULT.json\n")
              + loghash)
        for path, text in (extra or {}).items():
            write(self.root, path, text)
        self.put_manifest(stage="frozen",
                          freeze_manifest_path="r901/k4/run/FROZEN.sha256",
                          resource_logs=["r901/k4/run/RESOURCE_LOG.json"])
        return commit(self.root, "freeze")

    def violations(self):
        return self.audit()["violations"]

    def assertViolation(self, text):
        v = self.violations()
        self.assertTrue(any(text in x for x in v), v)

    def test_new_preregistration_alone_allowed(self):
        write(self.root, "r902/PREREGISTRATION.md", "# Synthetic future experiment\n")
        commit(self.root, "new prereg")
        self.assertEqual(self.violations(), [])

    def test_old_prereg_change_rejected(self):
        write(self.root, "r901/PREREGISTRATION.md", "# silently revised\n")
        commit(self.root, "modify historical prereg")
        self.assertViolation("immutable")

    def test_named_prereg_variant_and_results_freeze_are_immutable(self):
        write(self.root, "r901/PREREG_INVARIANTS.md", "v1\n")
        write(self.root, "r901/runs/OUT.json", "{}\n")
        self.base = commit(self.root, "older layout")
        write(self.root, "r901/PREREG_INVARIANTS.md", "v2\n")
        write(self.root, "r901/runs/OUT.json", '{"edited":1}\n')
        commit(self.root, "rewrite")
        self.assertEqual(len([x for x in self.violations() if "immutable" in x]), 2)

    def test_file_pinned_by_sha_manifest_is_immutable(self):
        code = "print(1)\n"
        write(self.root, "r901/solve.py", code)
        write(self.root, "r901/notes.py", "x = 1\n")
        write(self.root, "r901/PROTOCOL.sha256",
              hashlib.sha256(code.encode()).hexdigest() + "  r901/solve.py\n")
        self.base = commit(self.root, "protocol pins solver")
        write(self.root, "r901/notes.py", "x = 2\n")
        commit(self.root, "unpinned edit is fine")
        self.assertEqual(self.violations(), [])
        write(self.root, "r901/solve.py", "print(2)\n")
        commit(self.root, "edit pinned solver")
        self.assertViolation("pinned by a committed SHA-256 manifest")

    def test_erratum_under_round_audit_dir_allowed(self):
        write(self.root, "r901/audit/ERRATUM.md", "additive\n")
        write(self.root, "r901/audit/recheck.py", "print(1)\n")
        commit(self.root, "erratum")
        self.assertEqual(self.violations(), [])

    def test_new_top_level_directory_rejected(self):
        write(self.root, "experiments/k4_try/solve.py", "print(1)\n")
        commit(self.root, "experiment outside a round")
        self.assertViolation("new top-level directory")

    def test_new_round_with_code_needs_manifest_even_without_k4_dir(self):
        write(self.root, "r902/solve.py", "print(1)\n")
        write(self.root, "r902/results/OUT.json", "{}\n")
        commit(self.root, "round that avoids the k4/ folder")
        self.assertViolation("lacks r902/QA_MANIFEST.json")

    def test_ledger_requires_new_review(self):
        write(self.root, "LEDGER.md", "# Synthetic questionable exclusion\n")
        commit(self.root, "edit ledger without note")
        self.assertViolation("without a NEW")

    def test_ledger_review_must_be_explicit(self):
        write(self.root, "LEDGER.md", "# Synthetic corrected exclusion\n")
        write(self.root, "audit/reviews/example.md", "# Synthetic audit\n")
        commit(self.root, "fake review")
        self.assertViolation("Affected ledger IDs")

    def test_ledger_review_must_state_independent_review(self):
        write(self.root, "LEDGER.md", "# Synthetic corrected exclusion\n")
        write(self.root, "audit/reviews/example.md",
              "Affected ledger IDs: L999\nValidation: fixture\n")
        commit(self.root, "no reviewer statement")
        self.assertViolation("Independent review:")

    def test_ledger_with_new_review_accepted(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\nValidation: independent fixture\nIndependent review: NONE (fixture)\n")
        commit(self.root, "ledger qualified with evidence note")
        self.assertEqual(self.violations(), [])

    def test_ledger_row_not_named_in_review_rejected(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L998 | model | EXCL | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\nValidation: independent fixture\nIndependent review: NONE (fixture)\n")
        commit(self.root, "review note cites a different row")
        self.assertViolation("L998")

    def test_promotion_without_independent_review_rejected(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL INDEPENDENTLY VERIFIED | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\nPromotes: L999\n"
              "Validation: replay\nIndependent review: NONE (one model)\n")
        commit(self.root, "promote on a single-model replay")
        self.assertViolation("not 'YES <reviewer>'")

    def test_promotion_with_partial_review_rejected(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\nPromotes: L999\n"
              "Validation: replay\nIndependent review: PARTIAL (second model reran tests)\n")
        commit(self.root, "promote on a partial review")
        self.assertViolation("not 'YES <reviewer>'")

    def test_marked_row_without_promoting_note_rejected(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL INDEPENDENTLY VERIFIED | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\n"
              "Validation: replay\nIndependent review: NONE (one model)\n")
        commit(self.root, "mark a row verified without a promotion note")
        self.assertViolation("without a new review note that promotes")

    def test_promotion_with_independent_review_accepted(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL INDEPENDENTLY VERIFIED | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\nPromotes: L999\n"
              "Validation: replay\nIndependent review: YES fixture-reviewer (second model), signed review link\n")
        commit(self.root, "promote with a named independent reviewer")
        self.assertEqual(self.violations(), [])

    def test_single_model_replay_without_promotion_still_accepted(self):
        write(self.root, "LEDGER.md", "# Synthetic\n| L999 | model | EXCL (replayed, one model) | n | src |\n")
        write(self.root, "audit/reviews/example.md", "# Review\nAffected ledger IDs: L999\n"
              "Validation: replay\nIndependent review: NONE (one model)\n")
        commit(self.root, "record a replay without promoting")
        self.assertEqual(self.violations(), [])

    def test_guardrail_policy_change_requires_review(self):
        write(self.root, "audit/check_guardrails.py", "# weakened\n")
        commit(self.root, "quietly weaken the checker")
        self.assertViolation("without a NEW")

    def test_new_k4_missing_manifest_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "ID\tTEXT\nSYNTHETIC\tABCDEFG\n")
        commit(self.root, "K4 target without provenance")
        self.assertViolation("lacks r901/QA_MANIFEST.json")

    def test_new_k4_prereg_and_budget_accepted(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "ID\tTEXT\nSYNTHETIC\tABCDEFG\n")
        self.put_manifest()
        commit(self.root, "input manifest and gated synthetic evidence")
        self.assertEqual(self.violations(), [])

    def test_missing_holdout_rejected(self):
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest()
        commit(self.root, "no positive controls")
        self.assertViolation("synthetic_gate_path")

    def test_gate_in_same_commit_as_k4_rejected(self):
        write(self.root, "r901/holdout/GATE.json", '{"synthetic":"PASS"}\n')
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest()
        commit(self.root, "gate and K4 together")
        self.assertViolation("synthetic gate must be committed before")

    def test_failed_gate_blocks_k4(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest(gate_verdict="NO-GO")
        commit(self.root, "run K4 despite failed gate")
        self.assertViolation("gate_verdict must be GO")

    def test_scope_statement_required(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest(not_excluded="")
        commit(self.root, "no scope limits")
        self.assertViolation("not_excluded")

    def test_bad_prereg_hash_rejected(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        self.put_manifest(preregistration_sha256="0" * 64)
        commit(self.root, "bad prereg hash")
        self.assertViolation("preregistration_sha256")

    def test_zero_budget_rejected(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        m = self.manifest()
        m["resource_budget"]["max_wall_seconds"] = 0
        write(self.root, "r901/QA_MANIFEST.json", json.dumps(m) + "\n")
        commit(self.root, "bad compute budget")
        self.assertViolation("max_wall_seconds")

    def test_frozen_run_accepted(self):
        self.frozen_run()
        self.assertEqual(self.violations(), [])

    def test_freeze_manifest_hashes_are_verified(self):
        self.frozen_run(freeze="0" * 64 + "  results  RESULT.json\n")
        self.assertViolation("SHA-256 mismatch")

    def test_output_missing_from_freeze_manifest_rejected(self):
        self.frozen_run(freeze="fixture\n")
        self.assertViolation("not listed in")

    def test_reveal_in_freeze_commit_rejected(self):
        self.frozen_run(extra={"r901/k4/REVEAL.json": '{"letters":2}\n'})
        self.assertViolation("freeze outputs first")

    def test_reveal_after_freeze_accepted(self):
        self.frozen_run()
        write(self.root, "r901/k4/REVEAL.json", '{"letters":2}\n')
        commit(self.root, "post-freeze reveal")
        self.assertEqual(self.violations(), [])

    def test_incomplete_run_is_not_a_result(self):
        self.frozen_run(log={"status": "INCOMPLETE", "wall_seconds": 1, "max_rss_mb": 1})
        self.assertViolation("INCOMPLETE")

    def test_over_budget_run_rejected(self):
        self.frozen_run(log={"status": "COMPLETE", "wall_seconds": 9999, "max_rss_mb": 1})
        self.assertViolation("wall time exceeds")

    def test_search_hold_blocks_new_k4_files(self):
        write(self.root, "audit/SEARCH_HOLD.md", "hold\n")
        self.base = commit(self.root, "hold in force")
        self.frozen_run()
        self.assertViolation("SEARCH_HOLD.md is in force")

    def test_blind_input_allowlist_rejects_clue_file(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/known_plaintext_clue.txt", "FAKE\n")
        self.put_manifest(solver_inputs=[
            "r901/k4/TARGET.tsv", "r901/known_plaintext_clue.txt"])
        commit(self.root, "inject forbidden inputs")
        self.assertViolation("forbidden plaintext")

    def test_blind_input_content_with_published_word_rejected(self):
        self.gate()
        write(self.root, "r901/k4/TARGET.tsv", "SYNTHETIC\n")
        write(self.root, "r901/wordlist.txt", "ALPHA\nBERLIN\n")
        self.put_manifest(solver_inputs=["r901/k4/TARGET.tsv", "r901/wordlist.txt"])
        commit(self.root, "innocently named input holding a published word")
        self.assertViolation("published K4 plaintext word")


class BoundedRunnerTests(unittest.TestCase):
    def run_job(self, code, wall=20, ram=512):
        import run_bounded
        return run_bounded.run([sys.executable, "-I", "-c", code], wall, ram)

    def test_normal_job_completes(self):
        self.assertEqual(self.run_job("print(1)")["status"], "COMPLETE")

    def test_timeout_is_incomplete(self):
        log = self.run_job("import time; time.sleep(30)", wall=1)
        self.assertEqual(log["status"], "INCOMPLETE")
        self.assertIn("wall-clock", log["reason"])

    def test_memory_limit_is_incomplete(self):
        log = self.run_job("x = bytearray(900 * 1024 * 1024)", ram=256)
        self.assertEqual(log["status"], "INCOMPLETE")

    def test_failing_job_is_incomplete(self):
        self.assertEqual(self.run_job("raise SystemExit(2)")["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main(verbosity=2)

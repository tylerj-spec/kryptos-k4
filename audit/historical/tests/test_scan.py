#!/usr/bin/env python3
"""Synthetic adversarial tests for the historical evidence inventory.

Fixtures are invented data only; no K4 ciphertext or known plaintext
is read or used in constructing any test message.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scan as S  # noqa: E402


class HistoricalAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.old = S.ROOT
        S.ROOT = self.root
        self.addCleanup(lambda: setattr(S, "ROOT", self.old))
        self.git("init", "-q")
        self.git("config", "user.name", "Audit Fixture")
        self.git("config", "user.email", "audit@example.invalid")

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.root,
                           capture_output=True, text=True)
        if r.returncode:
            self.fail(r.stderr)
        return r.stdout.strip()

    def add(self, path, data):
        f = self.root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(data)
        return f

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-qm", msg)
        return self.git("rev-parse", "HEAD")

    def test_markdown_escaped_and_code_pipe(self):
        self.assertEqual(S.cells("| L01 | Model | Score | N | C/G |"),
                         ["L01", "Model", "Score", "N", "C/G"])
        self.assertEqual(S.cells("| L55 | Model | " + chr(96) + "pipe|inside" + chr(96) + " | N | Source |"),
                         ["L55", "Model", chr(96) + "pipe|inside" + chr(96), "N", "Source"])
        self.assertEqual(S.cells(r"| L99 | A \| B | EXCL | N | C |"),
                         ["L99", r"A \| B", "EXCL", "N", "C"])

    def test_ledger_status_never_automatically_certified(self):
        self.add("LEDGER.md", "\n".join([
            "| ID | Model and scope | Status | Key numbers | Source |",
            "| L01 | Old model | EXCL | 1 | C/G |",
            "| L02 | New model \`r82/RESULT.md\` | OPEN | 2 | CC |",
            "| L04 | Legacy without numbers | STAT | G |",
        ]))
        self.add("r82/RESULT.md", "# simulated")
        result = S.inventory_ledger(S.tracked() | {"LEDGER.md","r82/RESULT.md"})
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["unused_ids"], ["L03"])
        self.assertEqual(result["generic_source_count"], 2)
        self.assertEqual(result["rows"][0]["audit_verdict"], "PENDING_INDEPENDENT_VALIDATION")
        self.assertEqual(result["rows"][1]["provenance"], "REFERENCED_NOT_INDEPENDENTLY_REPLAYED")
        self.assertEqual(result["rows"][2]["numbers"], "")

    def test_verified_legacy_k4kit_location_aliases(self):
        self.add("LEDGER.md", "\n".join([
            "| ID | Model | Status | Key numbers | Source |",
            "| L22 | Test historical \`r30/search.py\` | OPEN | 0 | C |",
            "| L23 | Test historical \`r32/runs/FROZEN.sha256\` | STAT | 0 | G |",
        ]))
        paths={"LEDGER.md","k4kit/r30/search.py",
               "k4kit/r32/runs/FROZEN.sha256"}
        d=S.inventory_ledger(paths)
        self.assertEqual(d["reference_issue_count"],0)
        self.assertEqual(d["rows"][0]["resolved_paths"],["k4kit/r30/search.py"])
        self.assertEqual(d["rows"][1]["resolved_paths"],["k4kit/r32/runs/FROZEN.sha256"])

    def test_digest_match_and_detect_modified_target(self):
        f = self.add("r91/PREREGISTRATION.md", "Frozen\n")
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        self.add("r91/PROTOCOL.sha256", h+"  r91/PREREGISTRATION.md\n")
        result = S.inventory_manifests({
            "r91/PREREGISTRATION.md", "r91/PROTOCOL.sha256"})
        self.assertEqual(result["counts"]["MATCH_AT_HEAD"], 1)
        f.write_text("Unauthorized replacement\n")
        result = S.inventory_manifests({
            "r91/PREREGISTRATION.md", "r91/PROTOCOL.sha256"})
        self.assertEqual(result["counts"]["MISMATCH_AT_HEAD"], 1)

    def test_ambiguous_manifest_basename_not_silently_guessed(self):
        self.add("r91/a.txt", "A")
        self.add("r92/holdout/a.txt", "B")
        self.add("r91/k4/run/FROZEN.sha256", "0"*64+"  a.txt\n")
        r = S.inventory_manifests({"r91/a.txt",
                                    "r92/holdout/a.txt",
                                    "r91/k4/run/FROZEN.sha256"})
        self.assertEqual(r["counts"]["AMBIGUOUS_SHORT_NAME"], 1)

    def test_historic_prereg_digest_matches_old_frozen_version(self):
        f = self.add("r91/PREREGISTRATION.md", "Original experimental protocol\n")
        expected = hashlib.sha256(f.read_bytes()).hexdigest()
        self.add("r91/PROTOCOL.sha256", expected + "  r91/PREREGISTRATION.md\n")
        first = self.commit("freeze original exact protocol")
        f.write_text("Later edited experimental protocol\n")
        self.commit("subsequent unrelated edit")
        r = S.inventory_manifests(S.tracked())
        mismatches = [e for m in r["manifests"] for e in m["entries"]
                      if e["status"] == "MISMATCH_AT_HEAD"]
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["historical_status"], "MATCH_AT_MANIFEST_INTRO")
        self.assertEqual(mismatches[0]["matching_commit"], first)

    def test_historic_digest_prior_to_manifest_is_not_contemporaneous(self):
        f = self.add("r91/PREREGISTRATION.md", "very old version\n")
        previous = hashlib.sha256(f.read_bytes()).hexdigest()
        self.commit("file version one")
        f.write_text("later version before manifest\n")
        self.add("r91/PROTOCOL.sha256", previous+"  r91/PREREGISTRATION.md\n")
        self.commit("manifest introduced after protocol modification")
        r = S.inventory_manifests(S.tracked())
        mismatches = [e for m in r["manifests"] for e in m["entries"]
                      if e["status"] == "MISMATCH_AT_HEAD"]
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["historical_status"], "MATCH_IN_ANCESTRY_BEFORE_MANIFEST")

    def test_freeze_commit_order(self):
        self.add("r91/PREREGISTRATION.md", "Rules")
        first = self.commit("before")
        self.add("r91/k4/run/FROZEN.sha256", "Frozen")
        second = self.commit("after")
        r = S.inventory_order(S.tracked())
        self.assertEqual(r["rounds_checked"], 1)
        self.assertEqual(r["counts"]["PREREG_BEFORE_OUTPUT"], 1)
        self.assertEqual(r["rounds"][0]["prereg_commit"], first)
        self.assertEqual(r["rounds"][0]["outputs"][0]["output_commit"], second)

    def test_same_commit_is_not_preregistered(self):
        self.add("r91/PREREGISTRATION.md", "Late")
        self.add("r91/k4/run/FROZEN.sha256", "Simultaneous")
        self.commit("both")
        self.assertEqual(S.inventory_order(S.tracked())["counts"]["SAME_INTRO_COMMIT"],1)

    def test_deeply_underconstrained_claim_is_structural_only(self):
        r = S.parse_manifest_line("0"*64+"  code  r91/solver.py")
        self.assertEqual(r, ("0"*64, "code  r91/solver.py"))
        f = self.add("r91/solver.py", "# no real code")
        p, kind = S.resolve_target("r91/k4/run/FROZEN.sha256",
                                   "code  r91/solver.py",
                                   {"r91/solver.py"}, "0"*64)
        self.assertEqual(p, "r91/solver.py")
        self.assertIn(kind, ("DIRECT_OR_RELATIVE", "UNIQUE_SUFFIX"))


if __name__=="__main__":
    unittest.main(verbosity=2)

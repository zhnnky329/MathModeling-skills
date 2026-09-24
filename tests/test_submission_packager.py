"""Behavioral checks for the submission package contract."""

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".codex/skills/submission-packager/scripts/package_submission.py"


class SubmissionPackagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ws = Path(self.temp.name) / "workspace"
        self.ws.mkdir()
        self.put("planning/session_config.json", {"rigor_profile": "submission"})
        self.put("planning/manifests/Q1.json", {"question_id": "Q1", "current_gate": "G6",
                                                "allowed": {"final_assembly": True}})
        for audit in ("paper/audits/cross_media_consistency_audit.md",
                      "paper/audits/completeness_audit.md", "paper/qa_report.md"):
            self.put(audit, "Verdict: PASSED\n")
        self.put("paper/main.md", "# Final paper\n![Chart](figures/chart.svg)\n")
        self.put("paper/figures/chart.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.put("workspace/data_clean/a.csv", "x;y\n1;2\n")
        self.put("workspace/data_clean/b.csv", "x;y\n1;2\n")
        self.put("code/Q1/helper.py", "def value():\n    return 0\n")
        self.put("code/Q1/main.py", """import csv
import json
from pathlib import Path
import helper

values = []
for name in ('a', 'b'):
    with open('workspace/data_clean/' + name + '.csv') as stream:
        values.extend(int(row['y']) for row in csv.DictReader(stream, delimiter=';'))
score = sum(values) + helper.value()
output = Path('results/Q1/experiments/round1/metrics/value.json')
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({'score': score}))
""")
        self.put("results/Q1/experiments/round1/metrics/value.json", {"score": 4})
        self.put("results/Q1/experiments/round1/run_summary.json", {
            "status": "SUCCESS", "scripts": ["code/Q1/main.py"],
            "inputs": ["workspace/data_clean/a.csv", "workspace/data_clean/b.csv"],
            "outputs": ["results/Q1/experiments/round1/metrics/value.json"]})
        self.put("results/Q1/reports/frozen_numbers.json", [{
            "claim_id": "q1_score", "value": 4,
            "source_file": "results/Q1/experiments/round1/metrics/value.json",
            "source_locator": "$.score",
            "frozen_at": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)).isoformat()}])

    def put(self, relative, content):
        path = self.ws / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content) if isinstance(content, (dict, list)) else content, encoding="utf-8")
        return path

    def call(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.ws), *map(str, extra)],
                              text=True, capture_output=True)

    def plan_hash(self, *extra):
        result = self.call(*extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return re.search(r"^plan: ([a-f0-9]{64})$", result.stdout, re.M).group(1)

    def test_package_preserves_code_csv_and_markdown_links(self):
        plan = self.plan_hash()
        result = self.call("--confirm", plan, "--verify-command", "python code/Q1/main.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.ws / "submission"
        self.assertTrue((out / "支撑材料/code/Q1/helper.py").is_file())
        original = (self.ws / "code/Q1/main.py").read_bytes()
        packaged = (out / "支撑材料/code/Q1/main.py").read_bytes()
        self.assertEqual(hashlib.sha256(original).digest(), hashlib.sha256(packaged).digest())
        self.assertTrue((out / "支撑材料/workspace/data_clean/a.csv").is_file())
        self.assertIn("支撑材料/paper/figures/chart.svg", (out / "main.md").read_text())
        self.assertTrue((out / "支撑材料/paper/figures/chart.svg").is_file())
        self.assertEqual(json.loads((out / "支撑材料/results/Q1/experiments/round1/metrics/value.json").read_text()), {"score": 4})
        manifest = json.loads((self.ws / "planning/submission_packaging_manifest.json").read_text())
        self.assertEqual(manifest["runtime"]["status"], "PASS")
        self.assertFalse((out / "支撑材料/results/Q1/experiments/round1/run_summary.json").exists())

    def test_no_reproduction_command_is_explicitly_unverified(self):
        result = self.call("--confirm", self.plan_hash())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("runtime: UNVERIFIED", result.stdout)

    def test_failed_frozen_round_blocks_package(self):
        self.put("results/Q1/experiments/round1/run_summary.json", {
            "status": "FAIL", "scripts": ["code/Q1/main.py"], "inputs": [], "outputs": []})
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("did not complete successfully", result.stdout)

    def test_newer_failed_round_does_not_replace_frozen_round(self):
        self.put("results/Q1/experiments/round2/run_summary.json", {"status": "FAIL"})
        result = self.call()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("results/Q1/experiments/round1/metrics/value.json", result.stdout)
        self.assertNotIn("round2", result.stdout)

    def test_missing_g6_audit_blocks_package(self):
        (self.ws / "paper/qa_report.md").unlink()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("paper/qa_report.md", result.stdout)

    def test_early_package_requires_recorded_human_waiver(self):
        (self.ws / "paper/qa_report.md").unlink()
        self.put("planning/manifests/Q1.json", {"question_id": "Q1", "current_gate": "G5",
                                                "allowed": {"final_assembly": False}})
        self.assertNotEqual(self.call("--allow-unaudited", "early-1").returncode, 0)
        decision = {"decision_id": "early-1", "decision_type": "packaging_waiver",
                    "status": "DECIDED", "decided_by": "human", "choice": "package before G6",
                    "rationale": "Need a preview package", "evidence_refs": ["planning/manifests/Q1.json"]}
        self.put("planning/framing_decisions.jsonl", json.dumps(decision) + "\n")
        self.assertEqual(self.call("--allow-unaudited", "early-1").returncode, 0)

    def test_missing_paper_image_blocks_package(self):
        (self.ws / "paper/figures/chart.svg").unlink()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("paper image", result.stdout)

    def test_matlab_helper_is_preserved(self):
        self.put("code/matlab/Q1/main.m", "score = helper();\n")
        self.put("code/matlab/Q1/helper.m", "function y = helper()\ny = 4;\nend\n")
        summary_path = self.ws / "results/Q1/experiments/round1/run_summary.json"
        summary = json.loads(summary_path.read_text())
        summary["scripts"] = ["code/matlab/Q1/main.m"]
        self.put("results/Q1/experiments/round1/run_summary.json", summary)
        result = self.call("--confirm", self.plan_hash())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.ws / "submission/支撑材料/code/matlab/Q1/helper.m").is_file())
        self.assertIn("runtime: UNVERIFIED", result.stdout)

    def test_package_module_import_is_preserved(self):
        self.put("code/Q1/pkg/__init__.py", "")
        self.put("code/Q1/pkg/helper.py", "def score():\n    return 4\n")
        self.put("code/Q1/main.py", """import json
from pathlib import Path
from pkg import helper
output = Path('results/Q1/experiments/round1/metrics/value.json')
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({'score': helper.score()}))
""")
        result = self.call("--confirm", self.plan_hash(), "--verify-command", "python code/Q1/main.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.ws / "submission/支撑材料/code/Q1/pkg/helper.py").is_file())

    def test_runtime_must_regenerate_frozen_result(self):
        self.put("code/Q1/main.py", "print('nothing was generated')\n")
        result = self.call("--confirm", self.plan_hash(), "--verify-command", "python code/Q1/main.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.ws / "submission").exists())

    def test_stale_frozen_source_blocks_package(self):
        freeze = self.ws / "results/Q1/reports/frozen_numbers.json"
        claims = json.loads(freeze.read_text())
        claims[0]["frozen_at"] = "2000-01-01T00:00:00+00:00"
        self.put("results/Q1/reports/frozen_numbers.json", claims)
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed after freeze", result.stdout)

    def test_frozen_value_must_match_current_source(self):
        freeze = self.ws / "results/Q1/reports/frozen_numbers.json"
        claims = json.loads(freeze.read_text())
        claims[0]["value"] = 99
        self.put("results/Q1/reports/frozen_numbers.json", claims)
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frozen value disagrees", result.stdout)

    def test_stale_audit_blocks_package(self):
        audit = self.ws / "paper/qa_report.md"
        old = audit.stat().st_mtime - 30
        os.utime(audit, (old, old))
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("updated audit", result.stdout)

    def test_workspace_output_is_rejected_before_deletion(self):
        marker = self.put("keep.txt", "keep")
        result = self.call("--out", self.ws, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), "keep")

    def test_raw_data_directory_cannot_be_output(self):
        result = self.call("--out", self.ws / "workspace/data_raw/package")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("protected workspace directory", result.stdout)

    def test_plan_digest_detects_source_change(self):
        old = self.plan_hash()
        self.put("workspace/data_clean/a.csv", "x;y\n1;9\n")
        result = self.call("--confirm", old)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.ws / "submission").exists())

    def test_force_refuses_modified_package(self):
        self.assertEqual(self.call("--confirm", self.plan_hash()).returncode, 0)
        out = self.ws / "submission"
        (out / "main.md").write_text("modified")
        result = self.call("--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((out / "main.md").read_text(), "modified")

    def test_force_refuses_extra_package_file(self):
        self.assertEqual(self.call("--confirm", self.plan_hash()).returncode, 0)
        out = self.ws / "submission"
        (out / "manual-note.txt").write_text("keep")
        result = self.call("--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((out / "manual-note.txt").is_file())


if __name__ == "__main__":
    unittest.main()

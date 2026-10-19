"""Tests for policy-level EDA notebook generation in the benchmark harness."""

import json
import tempfile
import unittest
from pathlib import Path

from experiments.harness.notebooks import NOTEBOOK_FILENAME, write_policy_eda_notebook


class ScreeningBenchmarkNotebookTests(unittest.TestCase):
    def test_write_policy_eda_notebook_creates_policy_local_notebook(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_dir = Path(tmpdir) / "exclude_policy"
            policy_dir.mkdir(parents=True, exist_ok=True)
            (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
            (policy_dir / "summary.csv").write_text(
                "review_key,run_status,scored_for_aggregate,parse_success,decision_coverage,accuracy,precision,recall,specificity,f1,duration_seconds,n_studies,gold_pass_count,gold_exclude_count,predicted_pass_count,predicted_exclude_count,run_index,screening_inspection_json\n"
                "synthetic_review,completed,True,True,1.0,0.9,1.0,0.8,1.0,0.888,12.0,10,6,4,5,5,1,/tmp/inspection.json\n",
                encoding="utf-8",
            )
            (policy_dir / "summary.json").write_text(
                json.dumps({
                    "suite": "screening_ladder",
                    "repeats": 5,
                    "gold_label_policy": "exclude_label_0_5",
                    "runs": [],
                    "leaderboard": [],
                    "review_leaderboard": [],
                }),
                encoding="utf-8",
            )

            result = write_policy_eda_notebook(policy_dir, execute=False)

            notebook_path = policy_dir / NOTEBOOK_FILENAME
            self.assertEqual(result["notebook_path"], str(notebook_path))
            self.assertFalse(result["executed"])
            self.assertEqual(result["execution_error"], "")
            self.assertTrue(notebook_path.exists())

            notebook_payload = json.loads(notebook_path.read_text(encoding="utf-8"))
            self.assertEqual(notebook_payload["nbformat"], 4)
            self.assertEqual(notebook_payload["metadata"]["kernelspec"]["name"], "python3")
            self.assertGreaterEqual(len(notebook_payload["cells"]), 10)
            intro_source = "".join(notebook_payload["cells"][0]["source"])
            load_source = "".join(notebook_payload["cells"][1]["source"])
            self.assertIn("exclude_label_0_5", intro_source)
            self.assertIn("/Mentor/", intro_source)
            self.assertIn('POLICY_DISPLAY_PATH = Path("/Mentor") / POLICY_RELATIVE_PATH', load_source)
            self.assertNotIn(str(policy_dir.resolve()), intro_source)
            self.assertNotIn(str(policy_dir.resolve()), load_source)
            self.assertIn("summary.csv", load_source)
            self.assertTrue(
                all(cell.get("id", "").startswith("cell-") for cell in notebook_payload["cells"])
            )

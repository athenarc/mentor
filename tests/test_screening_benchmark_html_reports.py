import json
import tempfile
import unittest
from pathlib import Path

from bastirr.benchmarking.html_reports import (
    HTML_REPORT_FILENAME,
    write_html_reports,
    write_policy_html_report,
)
from bastirr.benchmarking.comparison_reports import (
    COMPARISON_REPORT_FILENAME,
    write_policy_comparison_report,
)


class ScreeningBenchmarkHtmlReportTests(unittest.TestCase):
    def test_write_policy_html_report_creates_generic_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_dir = Path(tmpdir) / "exclude_policy"
            run_dir = policy_dir / "runs" / "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
            run_dir.mkdir(parents=True, exist_ok=True)

            (policy_dir / "summary.csv").write_text(
                "benchmark_run_id,review_key,run_index,run_status,scored_for_aggregate,parse_success,screening_decision_count,n_studies,tp,fp,tn,fn,accuracy,precision,recall,specificity,f1,duration_seconds,screening_inspection_json\n"
                f"synthetic_review_openai_gpt5_fixed_openai_gpt5_run1,synthetic_review,1,completed,True,True,10,10,6,1,3,0,0.9,0.8571,1.0,0.75,0.9231,12.0,{run_dir / 'screening_inspection.json'}\n",
                encoding="utf-8",
            )
            (policy_dir / "summary.json").write_text(
                json.dumps({
                    "suite": "screening_ladder",
                    "repeats": 1,
                    "review_keys": ["synthetic_review"],
                    "gold_label_policy": "exclude_label_0_5",
                    "leaderboard": [{
                        "mean_accuracy": 0.9,
                        "mean_precision": 0.8571,
                        "mean_recall": 1.0,
                        "mean_specificity": 0.75,
                        "mean_f1": 0.9231,
                        "mean_duration_seconds": 12.0,
                    }],
                    "review_leaderboard": [{
                        "review_key": "synthetic_review",
                        "n_studies": 10,
                        "gold_pass_count": 6,
                        "mean_accuracy": 0.9,
                        "mean_precision": 0.8571,
                        "mean_recall": 1.0,
                        "mean_specificity": 0.75,
                        "mean_f1": 0.9231,
                        "mean_duration_seconds": 12.0,
                    }],
                }),
                encoding="utf-8",
            )
            (run_dir / "screening_inspection.json").write_text(
                json.dumps({
                    "studies": [
                        {
                            "study_index": 1,
                            "study_title": "Synthetic included study",
                            "gold_label": "1.0",
                            "gold_screening_decision": "INCLUDE",
                            "gold_review_outcome": "included_in_review",
                            "predicted_decision": "EXCLUDE",
                        }
                    ]
                }),
                encoding="utf-8",
            )
            (policy_dir / "screening_results_analysis.ipynb").write_text("{}", encoding="utf-8")

            result = write_policy_html_report(policy_dir)

            report_path = policy_dir / HTML_REPORT_FILENAME
            self.assertEqual(result["report_path"], str(report_path))
            self.assertTrue(report_path.exists())

            report_html = report_path.read_text(encoding="utf-8")
            self.assertIn("Title and Abstract Screening Benchmark Summary", report_html)
            self.assertNotIn("Exclude Strategy Benchmark Summary", report_html)
            self.assertIn("Metric standard deviation across scored runs", report_html)
            self.assertNotIn("Metric range across scored runs", report_html)
            self.assertNotIn("./screening_results_analysis.ipynb", report_html)

    def test_write_html_reports_accepts_experiment_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            for policy_name in ("include_policy", "exclude_policy"):
                policy_dir = experiment_dir / policy_name
                run_dir = policy_dir / "runs" / "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
                run_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "summary.csv").write_text(
                    "benchmark_run_id,review_key,run_index,run_status,scored_for_aggregate,parse_success,screening_decision_count,n_studies,tp,fp,tn,fn,accuracy,precision,recall,specificity,f1,duration_seconds,screening_inspection_json\n"
                    f"synthetic_review_openai_gpt5_fixed_openai_gpt5_run1,synthetic_review,1,completed,True,True,10,10,6,1,3,0,0.9,0.8571,1.0,0.75,0.9231,12.0,{run_dir / 'screening_inspection.json'}\n",
                    encoding="utf-8",
                )
                (policy_dir / "summary.json").write_text(
                    json.dumps({
                        "suite": "screening_ladder",
                        "repeats": 1,
                        "review_keys": ["synthetic_review"],
                        "gold_label_policy": policy_name,
                        "leaderboard": [{
                            "mean_accuracy": 0.9,
                            "mean_precision": 0.8571,
                            "mean_recall": 1.0,
                            "mean_specificity": 0.75,
                            "mean_f1": 0.9231,
                            "mean_duration_seconds": 12.0,
                        }],
                        "review_leaderboard": [{
                            "review_key": "synthetic_review",
                            "n_studies": 10,
                            "gold_pass_count": 6,
                            "mean_accuracy": 0.9,
                            "mean_precision": 0.8571,
                            "mean_recall": 1.0,
                            "mean_specificity": 0.75,
                            "mean_f1": 0.9231,
                            "mean_duration_seconds": 12.0,
                        }],
                    }),
                    encoding="utf-8",
                )
                (run_dir / "screening_inspection.json").write_text(
                    json.dumps({"studies": []}),
                    encoding="utf-8",
                )

            results = write_html_reports(experiment_dir)

            self.assertEqual(len(results), 3)
            for policy_name in ("include_policy", "exclude_policy"):
                self.assertTrue((experiment_dir / policy_name / HTML_REPORT_FILENAME).exists())
            self.assertTrue((experiment_dir / COMPARISON_REPORT_FILENAME).exists())

    def test_write_policy_comparison_report_creates_top_level_comparison(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            for policy_dir_name, policy_key, review_f1, review_recall in (
                ("include_policy", "include_label_0_5", 0.70, 0.55),
                ("exclude_policy", "exclude_label_0_5", 0.88, 0.91),
            ):
                policy_dir = experiment_dir / policy_dir_name
                run_dir = policy_dir / "runs" / "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
                run_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "summary.csv").write_text(
                    "benchmark_run_id,review_key,run_index,run_status,scored_for_aggregate,parse_success,screening_decision_count,n_studies,tp,fp,tn,fn,accuracy,precision,recall,specificity,f1,duration_seconds,screening_inspection_json\n"
                    f"synthetic_review_openai_gpt5_fixed_openai_gpt5_run1,synthetic_review,1,completed,True,True,10,10,6,1,3,0,0.9,0.8571,{review_recall},0.75,{review_f1},12.0,{run_dir / 'screening_inspection.json'}\n",
                    encoding="utf-8",
                )
                (policy_dir / "summary.json").write_text(
                    json.dumps({
                        "suite": "screening_ladder",
                        "repeats": 1,
                        "review_keys": ["synthetic_review"],
                        "gold_label_policy": policy_key,
                        "leaderboard": [{
                            "mean_accuracy": 0.9,
                            "mean_precision": 0.8571,
                            "mean_recall": review_recall,
                            "mean_specificity": 0.75,
                            "mean_f1": review_f1,
                            "mean_duration_seconds": 12.0,
                            "parse_success_rate": 1.0,
                        }],
                        "review_leaderboard": [{
                            "review_key": "synthetic_review",
                            "review_title": "Synthetic review",
                            "n_studies": 10,
                            "gold_pass_count": 6,
                            "mean_accuracy": 0.9,
                            "mean_precision": 0.8571,
                            "mean_recall": review_recall,
                            "mean_specificity": 0.75,
                            "mean_f1": review_f1,
                            "mean_duration_seconds": 12.0,
                        }],
                    }),
                    encoding="utf-8",
                )
                (run_dir / "screening_inspection.json").write_text(
                    json.dumps({
                        "studies": [
                            {
                                "gold_label": "0.5",
                                "gold_review_outcome": "excluded_after_full_text",
                                "gold_screening_decision": "INCLUDE" if policy_key == "include_label_0_5" else "EXCLUDE",
                                "predicted_decision": "EXCLUDE" if policy_key == "include_label_0_5" else "INCLUDE",
                            }
                        ]
                    }),
                    encoding="utf-8",
                )
                (policy_dir / "screening_results_summary.html").write_text("report", encoding="utf-8")

            result = write_policy_comparison_report(experiment_dir)

            report_path = experiment_dir / COMPARISON_REPORT_FILENAME
            self.assertEqual(result["report_path"], str(report_path))
            self.assertTrue(report_path.exists())
            report_html = report_path.read_text(encoding="utf-8")
            self.assertIn("Screening Benchmark Policy Comparison", report_html)
            self.assertIn("Review-by-review comparison", report_html)
            self.assertIn("Error composition", report_html)
            self.assertNotIn("The core story", report_html)
            self.assertNotIn("Representative repeat offenders", report_html)

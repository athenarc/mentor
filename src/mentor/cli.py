"""
Production CLI for the end-to-end Mentor systematic-review pipeline.

Loads a Cochrane review from the bundled dataset, prepares a timestamped run
directory (logs + report), builds the orchestrator with optional per-role model
profiles, and executes the librarian → gatekeeper → miner → critic workflow.

Use ``--list-reviews`` to discover valid ``--review-url`` values for a split.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from mentor.agents.orchestrator import create_orchestrator_agent
from mentor.runtime.models import resolve_api_base
from mentor.dataset import list_reviews
from mentor.runtime.session import prepare_run_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("mentor.cli")

DEFAULT_REVIEW_URL = "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003508.pub2/full"
DEFAULT_SPLIT = "HIV_test"


def save_report(report: str, run_dir: Path) -> Path:
    """Save the final report to the run directory."""
    output_path = run_dir / "report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    return output_path


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def run_pipeline(
    review_url: str = DEFAULT_REVIEW_URL,
    split: str = DEFAULT_SPLIT,
    model_id: str | None = None,
    backend: str | None = None,
    api_base: str | None = None,
    model_profile: str | None = None,
    include_subagent_steps: bool = True,
):
    """Run the full systematic-review pipeline for one review."""
    logger.info("=" * 70)
    logger.info("MENTOR SYSTEMATIC REVIEW PIPELINE")
    logger.info("=" * 70)

    try:
        session = prepare_run_session(
            review_url=review_url,
            split=split,
            include_subagent_steps=include_subagent_steps,
            model_id=model_id,
            backend=backend,
            api_base=api_base,
            model_profile=model_profile,
        )
    except ValueError as exc:
        logger.error(str(exc))
        for r in list_reviews(split)[:10]:
            logger.info(
                "  %s (%s studies) — %s",
                r["title"],
                r["n_studies"],
                r["review_url"],
            )
        sys.exit(1)

    review = session.review
    run_dir = session.run_dir
    activity_logger = session.loggers.activity_logger
    agent_logger = session.loggers.agent_logger
    step_cbs = session.step_cbs
    protocol_json = session.protocol_json
    _backend = session.backend
    _activity_summary_model = session.activity_summary_model

    logger.info(review.summary())
    logger.info("Run directory: %s", run_dir)
    activity_logger.log_metadata("Review URL", review_url)
    activity_logger.log_metadata("Dataset split", split)
    activity_logger.log_metadata("Studies", str(len(review.studies)))

    if session.models_by_role is not None:
        model = session.models_by_role["orchestrator"]
        logger.info(
            "Model backend: %s | orchestrator model_id: %s",
            _backend,
            model.model_id,
        )
        if session.profile_key:
            logger.info("Model profile: %s", session.profile_key)
            activity_logger.log_metadata("Model Profile", session.profile_key)
        logger.info("Creating orchestrator with role-specific models...")
        orchestrator = create_orchestrator_agent(
            models_by_role=session.models_by_role,
            step_callbacks=step_cbs,
            logger=agent_logger,
        )
    else:
        model = session.models
        logger.info("Model backend: %s | model_id: %s", _backend, model.model_id)
        resolved_api_base = resolve_api_base(api_base)
        activity_logger.log_metadata("Model Profile", session.profile_key or "env")
        activity_logger.log_metadata("Shared Model", f"{_backend} | {model.model_id}")
        if resolved_api_base:
            activity_logger.log_metadata("Shared API Base", resolved_api_base)
        logger.info("Creating orchestrator with sub-agents...")
        orchestrator = create_orchestrator_agent(
            model=model,
            step_callbacks=step_cbs,
            logger=agent_logger,
        )

    task = (
        "Conduct a systematic review for the following research question.\n\n"
        f"Review protocol (JSON):\n{protocol_json}\n\n"
        "Execute the full pipeline:\n"
        "1. Use the librarian to retrieve candidate studies\n"
        "2. Use get_candidates_json() to obtain a clean JSON of the candidates\n"
        "3. Use the gatekeeper to screen studies for inclusion/exclusion\n"
        "4. Use the miner to extract evidence from included studies\n"
        "5. Use the critic to synthesize the evidence\n"
        "6. Use format_report() to format a clean Markdown report\n"
        "7. Use save_evidence_json() to save structured data "
        f'(output_dir: "{run_dir}")\n\n'
        "Return the formatted report as your final answer."
    )

    logger.info("Starting orchestrated pipeline...")
    activity_logger.mark_pipeline_start()
    report = ""

    try:
        result = orchestrator.run(task)
        logger.info("Pipeline complete!")
        report = str(result)
        report_path = save_report(report, run_dir)
        logger.info("Report saved to: %s", report_path)

        logger.info("\n" + "=" * 70)
        logger.info("GROUND TRUTH COMPARISON")
        logger.info("=" * 70)
        for i, s in enumerate(review.studies):
            label_map = {1.0: "INCLUDED", 0.5: "EXCL_FULLTEXT", 0.0: "EXCL_SCREENING"}
            label = label_map.get(s.label, str(s.label))
            logger.info("  Study %s: [%s] %s", i + 1, label, s.title[:80])
        logger.info("\nFull logs at: %s", run_dir)
    finally:
        activity_path = activity_logger.finalize(_activity_summary_model)
        logger.info("Activity log saved to: %s", activity_path)
        agent_logger.close()

    return report


def main():
    """Parse CLI flags and invoke ``run_pipeline`` or list available reviews."""
    parser = argparse.ArgumentParser(description="Mentor Systematic Review Demo")
    parser.add_argument(
        "--review-url",
        default=DEFAULT_REVIEW_URL,
        help="Cochrane review URL to process",
    )
    parser.add_argument(
        "--split",
        default=DEFAULT_SPLIT,
        choices=["dev", "val", "random_test", "heart_test", "HIV_test"],
        help="Dataset split to load from",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model identifier (e.g. gpt-4o, anthropic/claude-3-5-sonnet-latest, ollama_chat/llama3.2)",
    )
    parser.add_argument(
        "--backend",
        default=None,
        choices=["openai", "litellm"],
        help="Model backend: openai (default) or litellm",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="API base URL for local servers (e.g. http://localhost:11434)",
    )
    parser.add_argument(
        "--model-profile",
        default=None,
        help="Runtime model-profile key defined in mentor/runtime/profiles.json",
    )
    parser.add_argument(
        "--list-reviews",
        action="store_true",
        help="List available reviews and exit",
    )
    parser.add_argument(
        "--hide-subagent-steps",
        dest="include_subagent_steps",
        action="store_false",
        default=True,
        help="Hide sub-agent step details in activity.md",
    )
    args = parser.parse_args()

    if args.list_reviews:
        reviews = list_reviews(args.split)
        print(f"\nAvailable reviews in '{args.split}' ({len(reviews)} total):\n")
        for r in reviews:
            print(
                f"  [{r['n_studies']:3d} studies, {r['n_included']:2d} incl] "
                f"{r['title'][:70]}"
            )
            print(f"    {r['review_url']}")
        return

    run_pipeline(
        review_url=args.review_url,
        split=args.split,
        model_id=args.model,
        backend=args.backend,
        api_base=args.api_base,
        model_profile=args.model_profile,
        include_subagent_steps=args.include_subagent_steps,
    )


if __name__ == "__main__":
    main()

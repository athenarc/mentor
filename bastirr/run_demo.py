"""
Bastirr end-to-end demo runner.

Loads a systematic review from the Cochrane dataset and runs the full
multi-agent pipeline: Search → Screen → Extract → Synthesize.

Usage:
    cd /path/to/SR-agents
    python -m bastirr.run_demo

    # Or with a specific review URL:
    python -m bastirr.run_demo --review-url "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003508.pub2/full"

    # Or with a specific dataset split:
    python -m bastirr.run_demo --split val
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from bastirr.config import OUTPUT_DIR, OPENAI_API_KEY, MODEL_BACKEND, create_model
from bastirr.data import load_review, list_reviews
from bastirr.logging_utils import setup_run_logging, make_step_callbacks
from bastirr.tools.search import load_review_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bastirr.demo")


# Default: a small HIV review with 10 studies (1 included, 9 excluded)
DEFAULT_REVIEW_URL = (
    "https://www.cochranelibrary.com/cdsr/doi/"
    "10.1002/14651858.CD003508.pub2/full"
)
DEFAULT_SPLIT = "HIV_test"


def review_to_json(review) -> str:
    """Convert a SystematicReview dataclass to a full JSON string (for the study store)."""
    data = {
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
        "studies": [
            {
                "study_index": i + 1,
                "title": s.title,
                "abstract": s.abstract,
            }
            for i, s in enumerate(review.studies)
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def protocol_to_json(review) -> str:
    """Extract only the review protocol (no studies) as a JSON string.

    This is what the orchestrator receives — it never sees the raw
    study list.  Studies are only accessible via the librarian's tools.
    """
    data = {
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
    }
    return json.dumps(data, ensure_ascii=False)


def save_report(report: str, run_dir: Path) -> Path:
    """Save the final report to the run directory."""
    output_path = run_dir / "report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    return output_path


def run_demo(
    review_url: str = DEFAULT_REVIEW_URL,
    split: str = DEFAULT_SPLIT,
    model_id: str | None = None,
    backend: str | None = None,
    api_base: str | None = None,
    include_subagent_steps: bool = True,
):
    """
    Run the full Bastirr systematic review demo.

    Args:
        review_url: Cochrane review URL to process.
        split: Dataset split to load from.
        model_id: Model identifier override (e.g. "gpt-4o", "ollama_chat/llama3.2").
        backend: Model backend override ("openai" or "litellm").
        api_base: API base URL override (for local servers).
        include_subagent_steps: Show sub-agent details in activity.md.
    """
    # -----------------------------------------------------------------------
    # 1. Load review data
    # -----------------------------------------------------------------------
    logger.info("=" * 70)
    logger.info("BASTIRR SYSTEMATIC REVIEW DEMO")
    logger.info("=" * 70)

    review = load_review(review_url, split)
    if review is None:
        logger.error(f"Could not load review. Available reviews in '{split}':")
        for r in list_reviews(split)[:10]:
            logger.info(f"  {r['title']} ({r['n_studies']} studies) — {r['review_url']}")
        sys.exit(1)

    logger.info(review.summary())
    review_json = review_to_json(review)
    protocol_json = protocol_to_json(review)

    # Load the full review data (incl. studies) into the librarian's
    # search store.  The orchestrator will only see the protocol.
    load_review_data(review_json)

    # -----------------------------------------------------------------------
    # 2. Set up run logging
    # -----------------------------------------------------------------------
    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
    )
    step_cbs = make_step_callbacks(activity_logger)
    logger.info(f"Run directory: {run_dir}")
    activity_logger.log_metadata("Review URL", review_url)
    activity_logger.log_metadata("Dataset split", split)
    activity_logger.log_metadata("Studies", str(len(review.studies)))

    # -----------------------------------------------------------------------
    # 3. Initialize model and orchestrator
    # -----------------------------------------------------------------------
    _backend = (backend or MODEL_BACKEND).lower()
    if _backend == "openai" and not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set. Add it to .env file.")
        sys.exit(1)

    from bastirr.agents.orchestrator import create_orchestrator_agent

    model = create_model(model_id=model_id, backend=backend, api_base=api_base)
    logger.info(f"Model backend: {_backend} | model_id: {model.model_id}")

    logger.info("Creating orchestrator with sub-agents...")
    orchestrator = create_orchestrator_agent(
        model, step_callbacks=step_cbs, logger=agent_logger,
    )

    # -----------------------------------------------------------------------
    # 4. Run the pipeline
    # -----------------------------------------------------------------------
    task = (
        f"Conduct a systematic review for the following research question.\n\n"
        f"Review protocol (JSON):\n{protocol_json}\n\n"
        f"Execute the full pipeline:\n"
        f"1. Use the librarian to retrieve candidate studies\n"
        f"2. Use get_candidates_json() to obtain a clean JSON of the candidates\n"
        f"3. Use the gatekeeper to screen studies for inclusion/exclusion\n"
        f"4. Use the miner to extract evidence from included studies\n"
        f"5. Use the critic to synthesize the evidence\n"
        f"6. Use format_report() to format a clean Markdown report\n"
        f"7. Use save_evidence_json() to save structured data "
        f"(output_dir: \"{run_dir}\")\n\n"
        f"Return the formatted report as your final answer."
    )

    logger.info("Starting orchestrated pipeline...")
    activity_logger.mark_pipeline_start()

    try:
        result = orchestrator.run(task)

        logger.info("Pipeline complete!")

        # -------------------------------------------------------------------
        # 5. Save and display results
        # -------------------------------------------------------------------
        report = str(result)
        report_path = save_report(report, run_dir)
        logger.info(f"Report saved to: {report_path}")

        # Print ground truth comparison
        logger.info("\n" + "=" * 70)
        logger.info("GROUND TRUTH COMPARISON")
        logger.info("=" * 70)

        for i, s in enumerate(review.studies):
            label_map = {1.0: "INCLUDED", 0.5: "EXCL_FULLTEXT", 0.0: "EXCL_SCREENING"}
            label = label_map.get(s.label, str(s.label))
            logger.info(f"  Study {i+1}: [{label}] {s.title[:80]}")

        logger.info(f"\nFull logs at: {run_dir}")
    finally:
        # Always write the activity log, even if the pipeline crashed
        activity_path = activity_logger.finalize(model)
        logger.info(f"Activity log saved to: {activity_path}")
        agent_logger.close()

    return report


def main():
    parser = argparse.ArgumentParser(description="Bastirr Systematic Review Demo")
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
            print(f"  [{r['n_studies']:3d} studies, {r['n_included']:2d} incl] "
                  f"{r['title'][:70]}")
            print(f"    {r['review_url']}")
        return

    run_demo(
        review_url=args.review_url,
        split=args.split,
        model_id=args.model,
        backend=args.backend,
        api_base=args.api_base,
        include_subagent_steps=args.include_subagent_steps,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Re-generate PRISMA artifacts from an existing Bastirr run directory."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from bastirr.config import create_model, resolve_backend
from bastirr.prisma import generate_prisma_bundle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bastirr.scripts.generate_prisma")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate PRISMA checklist and flowchart for an existing run.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to bastirr/output/<timestamp>_<review>/",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.expanduser().resolve()
    if not run_dir.is_dir():
        logger.error("Run directory not found: %s", run_dir)
        return 1

    evidence_path = run_dir / "evidence.json"
    if not evidence_path.exists():
        logger.error("No evidence.json in %s — run the pipeline first.", run_dir)
        return 1

    try:
        model = create_model(backend=resolve_backend())
    except Exception as exc:
        logger.warning("Could not load model for LLM fill: %s", exc)
        model = None

    prisma_dir = generate_prisma_bundle(run_dir, review=None, model=model)
    logger.info("Wrote PRISMA bundle to %s", prisma_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

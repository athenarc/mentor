"""
CLI entry point for generating screening benchmark HTML reports.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bastirr.benchmarking.html_reports import write_html_reports


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate screening benchmark HTML summary reports for one policy folder "
            "or for all policy folders inside a benchmark experiment directory."
        )
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to a policy folder or a benchmark experiment folder",
    )
    args = parser.parse_args()

    results = write_html_reports(args.target)
    print("\nGenerated HTML report(s):\n")
    for result in results:
        print(f"  {result['report_path']}")
    print("")


if __name__ == "__main__":
    main()

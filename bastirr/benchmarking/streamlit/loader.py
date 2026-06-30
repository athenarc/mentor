import json
import os
from pathlib import Path

import pandas as pd

RESULTS_SUBPATH = os.path.join("totals", "horizontal_comparison")


class DataDirectoryError(Exception):
    pass


def _assert_readable_dir(path: str) -> None:
    if not os.path.exists(path):
        raise DataDirectoryError(f"Directory does not exist: {path}")
    if not os.path.isdir(path):
        raise DataDirectoryError(f"Path is not a directory: {path}")
    if not os.access(path, os.R_OK | os.X_OK):
        raise DataDirectoryError(f"Directory is not readable/traversable: {path}")


def get_suites(df: pd.DataFrame) -> list[str]:
    """
    Return the canonical list of suite names.

    Currently derived from the dataframe. To switch to an external source
    (e.g. a JSON manifest passed at startup), replace this function body —
    the rest of the app calls only this interface and does not need to change.
    """
    return sorted(df['suite'].unique())


def find_json_files(base_dir: str) -> list[str]:
    _assert_readable_dir(base_dir)

    results_dir = os.path.join(base_dir, RESULTS_SUBPATH)
    _assert_readable_dir(results_dir)

    json_files: list[str] = []
    for root, dirs, files in os.walk(results_dir):
        dirs[:] = sorted(d for d in dirs if os.access(os.path.join(root, d), os.R_OK | os.X_OK))
        for filename in sorted(files):
            if not filename.lower().endswith(".json"):
                continue
            filepath = os.path.join(root, filename)
            if os.access(filepath, os.R_OK):
                json_files.append(filepath)

    return json_files

def load_json(json_file: str | Path) -> pd.DataFrame:
    with open(json_file, "r", encoding='utf-8') as fin:
        data = json.load(fin)

    row_data = [row for band in data['size_bands'] for row in band['review_rows']]
    return pd.DataFrame(row_data)

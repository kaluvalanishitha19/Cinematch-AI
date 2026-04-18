"""Load movie CSVs from disk and return preprocessed `Movie` records."""

from __future__ import annotations

import csv
import os
from pathlib import Path

from cinematch.data.preprocess import dedupe_by_id, preprocess_movie_row, sort_by_id
from cinematch.data.schema import Movie

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_CSV = _REPO_ROOT / "data" / "sample_movies.csv"
_ENV_CSV = "CINEMATCH_DATA_CSV"

_REQUIRED_COLUMNS = ("id", "title", "year", "genres", "overview")


def _resolve_csv_path(csv_path: Path | None) -> Path:
    if csv_path is not None:
        return csv_path
    override = os.environ.get(_ENV_CSV, "").strip()
    if override:
        return Path(override).expanduser()
    return _DEFAULT_CSV


def _validate_header(fieldnames: list[str] | None) -> None:
    if not fieldnames:
        raise ValueError("CSV is missing a header row.")
    missing = [name for name in _REQUIRED_COLUMNS if name not in fieldnames]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        _validate_header(list(reader.fieldnames or []))
        for row in reader:
            if row is None:
                continue
            cleaned: dict[str, str] = {}
            for key, value in row.items():
                if key is None:
                    continue
                text = "" if value is None else str(value)
                cleaned[key] = text.strip()
            if not any(cleaned.values()):
                continue
            rows.append(cleaned)
    return rows


def load_movies(csv_path: Path | None = None) -> list[Movie]:
    """Load, validate, preprocess, dedupe, and sort movies from a CSV file.

    Uses ``data/sample_movies.csv`` under the repository root by default.
    Set ``CINEMATCH_DATA_CSV`` to an absolute or relative path to override.
    Returns an empty list if the file does not exist (useful for optional mounts).
    """
    path = _resolve_csv_path(csv_path)
    if not path.is_file():
        return []

    raw_rows = _read_csv_rows(path)
    movies: list[Movie] = []
    # +2 accounts for 1-based headers and 0-based enumerate starting at the first data row.
    for index, row in enumerate(raw_rows):
        line_no = index + 2
        missing_cols = [name for name in _REQUIRED_COLUMNS if name not in row]
        if missing_cols:
            raise ValueError(f"line {line_no}: missing keys {missing_cols}")
        movies.append(preprocess_movie_row(row, line_no=line_no))

    movies = dedupe_by_id(movies)
    return sort_by_id(movies)

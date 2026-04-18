"""Read movie CSV files from disk (path resolution + CSV parsing only)."""

from __future__ import annotations

import csv
import os
from pathlib import Path

from cinematch.data.pipeline import REQUIRED_COLUMNS, raw_rows_to_movies
from cinematch.data.schema import Movie

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_CSV = _REPO_ROOT / "data" / "sample_movies.csv"
_ENV_CSV = "CINEMATCH_DATA_CSV"


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
    missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
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
    """Load movies from CSV: parse file, then run the preprocessing pipeline.

    Default file: ``data/sample_movies.csv`` at the repo root. Override with the
    ``CINEMATCH_DATA_CSV`` environment variable. Returns ``[]`` if the file path
    does not exist.
    """
    path = _resolve_csv_path(csv_path)
    if not path.is_file():
        return []

    raw_rows = _read_csv_rows(path)
    return raw_rows_to_movies(raw_rows)

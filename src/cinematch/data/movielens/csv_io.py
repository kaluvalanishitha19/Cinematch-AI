"""Small CSV helpers for MovieLens files."""

from __future__ import annotations

import csv
from pathlib import Path


def require_columns(path: Path, fieldnames: list[str], required: tuple[str, ...]) -> None:
    missing = [name for name in required if name not in fieldnames]
    if missing:
        raise ValueError(f"{path.name}: missing columns {', '.join(missing)}")


def read_csv_dicts(path: Path, required: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    """Read a UTF-8 CSV (with optional BOM) into stripped string dictionaries."""
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        if not fieldnames:
            raise ValueError(f"{path.name}: missing header row")
        if required is not None:
            require_columns(path, fieldnames, required)
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

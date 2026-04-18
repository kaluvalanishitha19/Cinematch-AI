"""Build a cleaned movie catalog from raw CSV row dictionaries.

``loader`` reads bytes from disk; this module only handles the in-memory
transform: validate each row, preprocess fields, dedupe ids, then sort.
"""

from __future__ import annotations

from cinematch.data.preprocess import dedupe_by_id, preprocess_movie_row, sort_by_id
from cinematch.data.schema import Movie

# Shared with the CSV header check in ``loader``.
REQUIRED_COLUMNS: tuple[str, ...] = ("id", "title", "year", "genres", "overview")


def raw_rows_to_movies(raw_rows: list[dict[str, str]]) -> list[Movie]:
    """Convert parsed CSV rows into deduplicated, sorted ``Movie`` objects."""
    movies: list[Movie] = []
    for index, row in enumerate(raw_rows):
        line_no = index + 2  # header is line 1; first data row is line 2
        missing = [name for name in REQUIRED_COLUMNS if name not in row]
        if missing:
            raise ValueError(f"line {line_no}: missing keys {missing}")
        movies.append(preprocess_movie_row(row, line_no=line_no))

    return sort_by_id(dedupe_by_id(movies))

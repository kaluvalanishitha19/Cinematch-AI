"""Read raw MovieLens ``movies.csv`` and ``ratings.csv`` rows."""

from __future__ import annotations

from pathlib import Path

from cinematch.data.movielens.csv_io import read_csv_dicts

MOVIES_FILE = "movies.csv"
RATINGS_FILE = "ratings.csv"

MOVIES_COLUMNS: tuple[str, ...] = ("movieId", "title", "genres")
RATINGS_COLUMNS: tuple[str, ...] = ("userId", "movieId", "rating", "timestamp")


def load_raw_movie_rows(movies_path: Path) -> list[dict[str, str]]:
    return read_csv_dicts(movies_path, required=MOVIES_COLUMNS)


def load_raw_rating_rows(ratings_path: Path) -> list[dict[str, str]]:
    return read_csv_dicts(ratings_path, required=RATINGS_COLUMNS)

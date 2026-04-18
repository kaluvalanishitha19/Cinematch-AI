"""Assemble a prepared MovieLens dataset from a directory of CSVs."""

from __future__ import annotations

import os
from pathlib import Path

from cinematch.data.movielens.load import MOVIES_FILE, RATINGS_FILE, load_raw_movie_rows, load_raw_rating_rows
from cinematch.data.movielens.preprocess import (
    attach_rating_stats,
    clean_movie_row,
    clean_rating_row,
    dedupe_movies_keep_first,
    drop_ratings_missing_movies,
    rating_stats,
    sort_movies_by_id,
)
from cinematch.data.movielens.schema import MLMovie, MLRating, PreparedMovieLensDataset

_ENV_DIR = "CINEMATCH_MOVIELENS_DIR"


def _resolve_data_dir(data_dir: Path | None) -> Path:
    if data_dir is not None:
        return data_dir
    override = os.environ.get(_ENV_DIR, "").strip()
    if not override:
        raise ValueError(
            "MovieLens directory not provided. Pass ``data_dir=`` or set "
            f"the {_ENV_DIR} environment variable.",
        )
    return Path(override).expanduser()


def load_prepared_movielens(data_dir: Path | None = None) -> PreparedMovieLensDataset:
    """Load ``movies.csv`` + ``ratings.csv``, clean, merge stats, align ids.

    Expected layout (same as MovieLens *ml-latest-small* exports)::

        data_dir/movies.csv   -> movieId,title,genres
        data_dir/ratings.csv -> userId,movieId,rating,timestamp

    ``timestamp`` may be empty after cleaning. Ratings that reference unknown
    ``movieId`` values are dropped. Movies without ratings keep
    ``mean_rating=None`` and ``rating_count=0``.
    """
    root = _resolve_data_dir(data_dir)
    movies_path = root / MOVIES_FILE
    ratings_path = root / RATINGS_FILE

    if not movies_path.is_file():
        raise FileNotFoundError(f"Missing MovieLens movies file: {movies_path}")
    if not ratings_path.is_file():
        raise FileNotFoundError(f"Missing MovieLens ratings file: {ratings_path}")

    raw_movies = load_raw_movie_rows(movies_path)
    raw_ratings = load_raw_rating_rows(ratings_path)

    movies: list[MLMovie] = []
    for row in raw_movies:
        cleaned = clean_movie_row(row)
        if cleaned is not None:
            movies.append(cleaned)
    movies = dedupe_movies_keep_first(movies)
    movies = sort_movies_by_id(movies)
    movie_ids = {movie.movie_id for movie in movies}

    ratings: list[MLRating] = []
    for row in raw_ratings:
        cleaned = clean_rating_row(row)
        if cleaned is not None:
            ratings.append(cleaned)

    ratings = drop_ratings_missing_movies(ratings, movie_ids)
    stats = rating_stats(ratings)
    movies = attach_rating_stats(movies, stats)

    return PreparedMovieLensDataset(movies=movies, ratings=ratings)

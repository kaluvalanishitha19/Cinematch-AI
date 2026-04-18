"""Clean MovieLens rows and merge rating summaries onto movies."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable

from cinematch.data.movielens.schema import MLMovie, MLRating
from cinematch.data.preprocess import normalize_whitespace

_TITLE_YEAR = re.compile(r"^(?P<title>.+?)\s*\((?P<year>\d{4})\)\s*$")


def split_genres_pipe(raw: str) -> list[str]:
    """MovieLens uses ``|`` between genres; ``(no genres listed)`` becomes empty."""
    text = normalize_whitespace(raw)
    if not text or text == "(no genres listed)":
        return []
    parts = [normalize_whitespace(part) for part in text.split("|")]
    return [part for part in parts if part]


def parse_display_title_and_year(raw_title: str) -> tuple[str, int | None]:
    """Split ``Title (YYYY)`` into display title + year when the pattern matches."""
    raw = normalize_whitespace(raw_title)
    match = _TITLE_YEAR.match(raw)
    if not match:
        return raw, None
    title = normalize_whitespace(match.group("title"))
    year = int(match.group("year"))
    return (title if title else raw, year)


def clean_movie_row(row: dict[str, str]) -> MLMovie | None:
    """Build ``MLMovie`` or return ``None`` if the row is unusable."""
    movie_id = normalize_whitespace(row.get("movieId", ""))
    raw_title = row.get("title", "")
    raw_genres = row.get("genres", "")

    if not movie_id:
        return None
    title, year = parse_display_title_and_year(raw_title)
    if not title:
        return None

    return MLMovie(
        movie_id=movie_id,
        title=title,
        year=year,
        genres=split_genres_pipe(raw_genres),
    )


def clean_rating_row(row: dict[str, str]) -> MLRating | None:
    """Build ``MLRating`` or return ``None`` if values are missing or invalid."""
    user_id = normalize_whitespace(row.get("userId", ""))
    movie_id = normalize_whitespace(row.get("movieId", ""))
    rating_raw = normalize_whitespace(row.get("rating", ""))
    timestamp_raw = normalize_whitespace(row.get("timestamp", ""))

    if not user_id or not movie_id or not rating_raw:
        return None

    try:
        rating = float(rating_raw)
    except ValueError:
        return None

    if not (0.5 <= rating <= 5.0):
        return None

    timestamp: int | None = None
    if timestamp_raw:
        try:
            timestamp = int(float(timestamp_raw))
        except ValueError:
            timestamp = None

    return MLRating(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        timestamp=timestamp,
    )


def rating_stats(ratings: Iterable[MLRating]) -> dict[str, tuple[float, int]]:
    """Return ``movie_id -> (mean_rating, count)``."""
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)

    for rating in ratings:
        sums[rating.movie_id] += rating.rating
        counts[rating.movie_id] += 1

    stats: dict[str, tuple[float, int]] = {}
    for movie_id, count in counts.items():
        mean = sums[movie_id] / count
        stats[movie_id] = (mean, count)
    return stats


def attach_rating_stats(movies: list[MLMovie], stats: dict[str, tuple[float, int]]) -> list[MLMovie]:
    """Copy movies and fill ``mean_rating`` / ``rating_count`` from aggregates."""
    updated: list[MLMovie] = []
    for movie in movies:
        if movie.movie_id in stats:
            mean, count = stats[movie.movie_id]
            updated.append(
                movie.model_copy(update={"mean_rating": mean, "rating_count": count}),
            )
        else:
            updated.append(movie.model_copy())
    return updated


def drop_ratings_missing_movies(
    ratings: list[MLRating],
    movie_ids: set[str],
) -> list[MLRating]:
    """Remove ratings whose ``movie_id`` never appears in the movie table."""
    return [rating for rating in ratings if rating.movie_id in movie_ids]


def dedupe_movies_keep_first(movies: list[MLMovie]) -> list[MLMovie]:
    """MovieLens ids should be unique; keep the first row if duplicates exist."""
    seen: set[str] = set()
    out: list[MLMovie] = []
    for movie in movies:
        if movie.movie_id in seen:
            continue
        seen.add(movie.movie_id)
        out.append(movie)
    return out


def sort_movies_by_id(movies: list[MLMovie]) -> list[MLMovie]:
    """Numeric ``movie_id`` sort when possible."""

    def sort_key(movie: MLMovie) -> tuple[int, int | str]:
        try:
            return (0, int(movie.movie_id))
        except ValueError:
            return (1, movie.movie_id)

    return sorted(movies, key=sort_key)

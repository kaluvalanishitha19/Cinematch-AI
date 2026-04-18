"""Normalize and clean movie records after CSV parsing."""

from __future__ import annotations

import re
from typing import Final

from cinematch.data.schema import Movie

_YEAR_MIN: Final[int] = 1888
_YEAR_MAX: Final[int] = 2035


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace and trim ends."""
    return re.sub(r"\s+", " ", text).strip()


def parse_genres(raw: str) -> list[str]:
    """Split comma-separated genres, trim, and drop case-insensitive duplicates (order kept)."""
    if not raw.strip():
        return []
    pieces = [normalize_whitespace(part) for part in raw.split(",")]
    seen_lower: set[str] = set()
    out: list[str] = []
    for piece in pieces:
        if not piece:
            continue
        key = piece.lower()
        if key in seen_lower:
            continue
        seen_lower.add(key)
        out.append(piece)
    return out


def parse_year(raw: str, *, line_no: int | None = None) -> int:
    """Parse a release year; raises ValueError on bad input or out-of-range values."""
    cleaned = raw.strip()
    prefix = f"line {line_no}: " if line_no is not None else ""
    try:
        year = int(cleaned)
    except ValueError as exc:
        raise ValueError(f"{prefix}invalid year {raw!r}") from exc
    if year < _YEAR_MIN or year > _YEAR_MAX:
        raise ValueError(
            f"{prefix}year {year} out of allowed range {_YEAR_MIN}–{_YEAR_MAX}",
        )
    return year


def preprocess_movie_row(row: dict[str, str], *, line_no: int) -> Movie:
    """Build a canonical `Movie` from a CSV row dict (values may be messy)."""
    movie_id = normalize_whitespace(row["id"])
    title = normalize_whitespace(row["title"])
    year = parse_year(row["year"], line_no=line_no)
    genres = parse_genres(row.get("genres", ""))
    overview = normalize_whitespace(row.get("overview", ""))

    if not movie_id:
        raise ValueError(f"line {line_no}: empty id")
    if not title:
        raise ValueError(f"line {line_no}: empty title")

    return Movie(id=movie_id, title=title, year=year, genres=genres, overview=overview)


def dedupe_by_id(movies: list[Movie]) -> list[Movie]:
    """Keep the first occurrence when ids repeat."""
    seen: set[str] = set()
    out: list[Movie] = []
    for movie in movies:
        if movie.id in seen:
            continue
        seen.add(movie.id)
        out.append(movie)
    return out


def sort_by_id(movies: list[Movie]) -> list[Movie]:
    """Sort by id: numeric ids ascending when possible, otherwise lexicographic."""
    def sort_key(m: Movie) -> tuple[int, int | str]:
        try:
            return (0, int(m.id))
        except ValueError:
            return (1, m.id)

    return sorted(movies, key=sort_key)

"""Unit tests for preprocessing helpers."""

import pytest

from cinematch.data.preprocess import (
    dedupe_by_id,
    normalize_whitespace,
    parse_genres,
    parse_year,
    preprocess_movie_row,
    sort_by_id,
)
from cinematch.data.schema import Movie


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("  hello   world  ") == "hello world"


def test_parse_genres_trims_and_dedupes_case_insensitive() -> None:
    assert parse_genres(" Comedy , drama ,  comedy ") == ["Comedy", "drama"]


def test_parse_genres_empty() -> None:
    assert parse_genres("") == []
    assert parse_genres("   ,  , ") == []


def test_parse_year_valid() -> None:
    assert parse_year(" 2010 ") == 2010


def test_parse_year_invalid() -> None:
    with pytest.raises(ValueError):
        parse_year("not-a-year", line_no=3)


def test_parse_year_out_of_range() -> None:
    with pytest.raises(ValueError):
        parse_year("1700", line_no=2)


def test_preprocess_movie_row() -> None:
    row = {
        "id": " 10 ",
        "title": "  Epic  Film ",
        "year": "2001",
        "genres": "Sci-Fi,  sci-fi , Drama",
        "overview": "Too   many   spaces.",
    }
    movie = preprocess_movie_row(row, line_no=5)
    assert movie == Movie(
        id="10",
        title="Epic Film",
        year=2001,
        genres=["Sci-Fi", "Drama"],
        overview="Too many spaces.",
    )


def test_dedupe_by_id_keeps_first() -> None:
    first = Movie(id="1", title="A", year=2000, genres=[], overview="")
    second = Movie(id="1", title="B", year=2001, genres=[], overview="")
    assert dedupe_by_id([first, second]) == [first]


def test_sort_by_id_numeric_then_string() -> None:
    movies = [
        Movie(id="10", title="b", year=2000, genres=[], overview=""),
        Movie(id="2", title="a", year=2000, genres=[], overview=""),
        Movie(id="x", title="c", year=2000, genres=[], overview=""),
    ]
    assert [m.id for m in sort_by_id(movies)] == ["2", "10", "x"]

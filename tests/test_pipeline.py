"""Tests for the raw row → Movie catalog pipeline."""

from cinematch.data.pipeline import raw_rows_to_movies
from cinematch.data.schema import Movie


def test_raw_rows_to_movies_preprocesses_and_sorts() -> None:
    raw = [
        {
            "id": "2",
            "title": "  B  ",
            "year": "2020",
            "genres": "Drama, drama",
            "overview": "  two   spaces  ",
        },
        {
            "id": "1",
            "title": "A",
            "year": "2019",
            "genres": "Comedy",
            "overview": "ok",
        },
    ]
    movies = raw_rows_to_movies(raw)
    assert [m.id for m in movies] == ["1", "2"]
    assert movies[1].title == "B"
    assert movies[1].genres == ["Drama"]
    assert movies[1].overview == "two spaces"


def test_raw_rows_to_movies_dedupes_ids() -> None:
    raw = [
        {"id": "1", "title": "First", "year": "2000", "genres": "", "overview": "x"},
        {"id": "1", "title": "Second", "year": "2001", "genres": "", "overview": "y"},
    ]
    movies = raw_rows_to_movies(raw)
    assert len(movies) == 1
    assert movies[0].title == "First"

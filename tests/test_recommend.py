"""Tests for the recommendation engine."""

from cinematch.data.schema import Movie
from cinematch.recommend.engine import recommend_similar


def test_recommend_similar_prefers_content_neighbors() -> None:
    movies = [
        Movie(
            id="1",
            title="Laugh Fest",
            year=2010,
            genres=["Comedy"],
            overview="Friends throw a hilarious wedding party full of jokes.",
        ),
        Movie(
            id="2",
            title="Party Jokes",
            year=2011,
            genres=["Comedy"],
            overview="A funny party with friends joking and laughing together.",
        ),
        Movie(
            id="3",
            title="Dark Woods",
            year=2015,
            genres=["Horror"],
            overview="A scary monster hunts people in a dark forest at night.",
        ),
    ]
    neighbors = recommend_similar("1", movies, top_k=2)
    assert [movie.id for movie in neighbors] == ["2", "3"]


def test_recommend_similar_unknown_seed_returns_empty() -> None:
    movies = [
        Movie(id="1", title="A", year=2000, genres=["Drama"], overview="alpha"),
    ]
    assert recommend_similar("missing", movies, top_k=3) == []


def test_recommend_similar_needs_catalog_size() -> None:
    movies = [
        Movie(id="1", title="Only", year=2000, genres=["Drama"], overview="solo"),
    ]
    assert recommend_similar("1", movies, top_k=3) == []


def test_recommend_similar_top_k_zero_returns_empty() -> None:
    movies = [
        Movie(id="1", title="A", year=2000, genres=["Drama"], overview="x"),
        Movie(id="2", title="B", year=2001, genres=["Drama"], overview="y"),
    ]
    assert recommend_similar("1", movies, top_k=0) == []

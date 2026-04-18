"""Tests for the content-based recommender."""

from cinematch.data.schema import Movie
from cinematch.recommend.content import movie_to_document, recommend_content_based


def test_movie_to_document_joins_genres_and_overview() -> None:
    movie = Movie(
        id="1",
        title="Demo",
        year=2000,
        genres=["Comedy", "Romance"],
        overview="Friends fall in love.",
    )
    text = movie_to_document(movie)
    assert "Comedy" in text
    assert "Romance" in text
    assert "Friends" in text


def test_movie_to_document_handles_empty_fields() -> None:
    movie = Movie(id="1", title="Empty", year=2000, genres=[], overview="   ")
    assert movie_to_document(movie) == "unknown"


def test_recommend_content_based_prefers_similar_text() -> None:
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
    ordered = recommend_content_based(0, movies, top_k=2)
    assert [movie.id for movie in ordered] == ["2", "3"]


def test_recommend_content_based_respects_top_k() -> None:
    movies = [
        Movie(id="1", title="A", year=2000, genres=["Drama"], overview="one two three"),
        Movie(id="2", title="B", year=2001, genres=["Drama"], overview="one two four"),
        Movie(id="3", title="C", year=2002, genres=["Drama"], overview="five six seven"),
    ]
    ordered = recommend_content_based(0, movies, top_k=1)
    assert len(ordered) == 1

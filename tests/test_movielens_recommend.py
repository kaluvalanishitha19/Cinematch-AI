"""Tests for MovieLens content-based recommendations."""

from pathlib import Path

import pytest

from cinematch.data.movielens import load_prepared_movielens
from cinematch.data.movielens.cache import clear_movielens_cache
from cinematch.data.movielens.schema import MLMovie, PreparedMovieLensDataset
from cinematch.recommend.movielens_content import (
    find_movie_index_by_title,
    ml_movie_to_document,
    recommend_movielens_by_title,
    recommend_movielens_content_based,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "movielens"


def _sample_dataset() -> PreparedMovieLensDataset:
    movies = [
        MLMovie(
            movie_id="1",
            title="Space Epic",
            year=1977,
            genres=["Sci-Fi", "Adventure"],
            mean_rating=4.5,
            rating_count=10,
        ),
        MLMovie(
            movie_id="2",
            title="Robot Adventure",
            year=2014,
            genres=["Sci-Fi", "Action"],
            mean_rating=4.0,
            rating_count=5,
        ),
        MLMovie(
            movie_id="3",
            title="Romantic Comedy",
            year=2001,
            genres=["Comedy", "Romance"],
            mean_rating=3.5,
            rating_count=8,
        ),
    ]
    return PreparedMovieLensDataset(movies=movies, ratings=[])


def test_ml_movie_to_document_includes_metadata() -> None:
    movie = MLMovie(
        movie_id="9",
        title="Demo",
        year=2020,
        genres=["Drama"],
        mean_rating=3.25,
        rating_count=4,
    )
    text = ml_movie_to_document(movie)
    assert "Demo" in text
    assert "Drama" in text
    assert "2020" in text
    assert "3.25" in text
    assert "ratings_4" in text


def test_find_movie_index_by_title_case_insensitive() -> None:
    dataset = _sample_dataset()
    idx = find_movie_index_by_title(dataset.movies, "space epic")
    assert idx == 0


def test_find_movie_index_matches_parenthetical_year_like_movielens_csv() -> None:
    """Raw CSV titles include ``(1995)``; stored ``MLMovie.title`` does not."""
    movies = load_prepared_movielens(FIXTURE_DIR).movies
    jumanji_index = next(i for i, m in enumerate(movies) if m.movie_id == "2")
    assert find_movie_index_by_title(movies, "Jumanji (1995)") == jumanji_index
    assert find_movie_index_by_title(movies, "jumanji") == jumanji_index


def test_recommend_movielens_fixture_accepts_parenthetical_title() -> None:
    dataset = load_prepared_movielens(FIXTURE_DIR)
    seed, similar = recommend_movielens_by_title(dataset, "Jumanji (1995)", top_k=2)
    assert seed.title == "Jumanji"
    assert seed.movie_id == "2"
    assert len(similar) >= 1


def test_recommend_movielens_by_title_prefers_shared_genres() -> None:
    dataset = _sample_dataset()
    seed, similar = recommend_movielens_by_title(dataset, "Space Epic", top_k=2)
    assert seed.title == "Space Epic"
    assert [movie.title for movie in similar] == ["Robot Adventure", "Romantic Comedy"]


def test_recommend_movielens_by_title_unknown_raises() -> None:
    with pytest.raises(LookupError):
        recommend_movielens_by_title(_sample_dataset(), "Missing Title", top_k=2)


def test_recommend_movielens_by_title_empty_raises() -> None:
    with pytest.raises(ValueError):
        recommend_movielens_by_title(_sample_dataset(), "   ", top_k=2)


def test_recommend_movielens_content_based_respects_top_k() -> None:
    movies = _sample_dataset().movies
    picks = recommend_movielens_content_based(0, movies, top_k=1)
    assert len(picks) == 1


def test_movielens_api_by_title_uses_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    from cinematch.main import app

    monkeypatch.setenv("CINEMATCH_MOVIELENS_DIR", str(FIXTURE_DIR))
    clear_movielens_cache()

    client = TestClient(app)
    response = client.get(
        "/api/movielens/recommendations/by-title",
        params={"title": "Toy Story", "top_k": 3},
    )
    clear_movielens_cache()

    assert response.status_code == 200
    body = response.json()
    assert body["seed_title"] == "Toy Story"
    assert body["seed_movie_id"] == "1"
    rec_ids = {movie["movie_id"] for movie in body["recommendations"]}
    assert "1" not in rec_ids


def test_movielens_api_accepts_parenthetical_title(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    from cinematch.main import app

    monkeypatch.setenv("CINEMATCH_MOVIELENS_DIR", str(FIXTURE_DIR))
    clear_movielens_cache()

    client = TestClient(app)
    response = client.get(
        "/api/movielens/recommendations/by-title",
        params={"title": "Jumanji (1995)", "top_k": 2},
    )
    clear_movielens_cache()

    assert response.status_code == 200
    body = response.json()
    assert body["seed_title"] == "Jumanji"
    assert body["seed_movie_id"] == "2"


def test_movielens_api_returns_503_without_data_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    from cinematch.main import app

    monkeypatch.delenv("CINEMATCH_MOVIELENS_DIR", raising=False)
    clear_movielens_cache()

    client = TestClient(app)
    response = client.get(
        "/api/movielens/recommendations/by-title",
        params={"title": "Toy Story"},
    )
    assert response.status_code == 503


def test_movielens_api_returns_503_when_data_dir_missing_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Bad or missing MovieLens path must be 503, not an unhandled 500."""
    from fastapi.testclient import TestClient

    from cinematch.main import app

    missing = tmp_path / "no_ml_dataset_here"
    monkeypatch.setenv("CINEMATCH_MOVIELENS_DIR", str(missing))
    clear_movielens_cache()

    client = TestClient(app)
    response = client.get(
        "/api/movielens/recommendations/by-title",
        params={"title": "Toy Story"},
    )
    clear_movielens_cache()

    assert response.status_code == 503
    detail = response.json().get("detail", "")
    assert isinstance(detail, str)
    assert "MovieLens" in detail or "movies.csv" in detail

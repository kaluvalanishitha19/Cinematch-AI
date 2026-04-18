"""Tests for MovieLens loading and preprocessing."""

from pathlib import Path

import pytest

from cinematch.data.movielens import PreparedMovieLensDataset, load_prepared_movielens
from cinematch.data.movielens.preprocess import clean_rating_row, split_genres_pipe

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "movielens"


def test_split_genres_pipe() -> None:
    assert split_genres_pipe("Adventure|Children") == ["Adventure", "Children"]
    assert split_genres_pipe("(no genres listed)") == []


def test_clean_rating_row_skips_invalid() -> None:
    assert clean_rating_row({"userId": "", "movieId": "1", "rating": "5.0", "timestamp": ""}) is None
    assert clean_rating_row({"userId": "1", "movieId": "1", "rating": "9.0", "timestamp": ""}) is None


def test_load_prepared_movielens_merges_stats() -> None:
    dataset = load_prepared_movielens(FIXTURE_DIR)
    assert isinstance(dataset, PreparedMovieLensDataset)
    assert {m.movie_id for m in dataset.movies} == {"1", "2", "4"}

    by_id = {m.movie_id: m for m in dataset.movies}
    assert by_id["1"].title == "Toy Story"
    assert by_id["1"].year == 1995
    assert by_id["1"].genres == ["Adventure", "Animation", "Children"]
    assert by_id["1"].mean_rating == pytest.approx(4.0)
    assert by_id["1"].rating_count == 3

    assert by_id["2"].mean_rating == pytest.approx(2.75)
    assert by_id["2"].rating_count == 2

    assert by_id["4"].mean_rating == pytest.approx(3.0)
    assert by_id["4"].rating_count == 1

    # Orphan movie 999 dropped; invalid rating rows skipped; empty user skipped.
    assert len(dataset.ratings) == 6


def test_load_prepared_movielens_requires_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CINEMATCH_MOVIELENS_DIR", raising=False)
    with pytest.raises(ValueError, match="MovieLens directory"):
        load_prepared_movielens(None)


def test_load_prepared_movielens_env_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CINEMATCH_MOVIELENS_DIR", str(FIXTURE_DIR))
    dataset = load_prepared_movielens(None)
    assert len(dataset.movies) == 3

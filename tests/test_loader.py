"""Tests for CSV loading and the end-to-end preprocessing pipeline."""

import os
from pathlib import Path

import pytest

from cinematch.data.loader import load_movies


def test_load_movies_reads_sample_csv() -> None:
    movies = load_movies()
    assert len(movies) >= 6
    first = movies[0]
    assert first.id == "1"
    assert isinstance(first.genres, list)
    assert "Comedy" in first.genres


def test_load_movies_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "nope.csv"
    assert load_movies(missing) == []


def test_load_movies_rejects_bad_header(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_movies(path)


def test_load_movies_preprocesses_rows(tmp_path: Path) -> None:
    path = tmp_path / "movies.csv"
    path.write_text(
        "id,title,year,genres,overview\n"
        '2,  spaced  title  ,2020,"Drama, drama","  overview  "\n',
        encoding="utf-8",
    )
    movies = load_movies(path)
    assert len(movies) == 1
    movie = movies[0]
    assert movie.id == "2"
    assert movie.title == "spaced title"
    assert movie.year == 2020
    assert movie.genres == ["Drama"]
    assert movie.overview == "overview"


def test_load_movies_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "env_movies.csv"
    path.write_text(
        "id,title,year,genres,overview\n"
        "99,Env Film,2021,Action,A test row for env override.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CINEMATCH_DATA_CSV", str(path))
    movies = load_movies()
    assert len(movies) == 1
    assert movies[0].id == "99"
    assert movies[0].title == "Env Film"
    monkeypatch.delenv("CINEMATCH_DATA_CSV", raising=False)


def test_explicit_path_beats_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_path = tmp_path / "env.csv"
    env_path.write_text(
        "id,title,year,genres,overview\n1,A,2000,Drama,x\n",
        encoding="utf-8",
    )
    explicit = tmp_path / "explicit.csv"
    explicit.write_text(
        "id,title,year,genres,overview\n2,B,2001,Comedy,y\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CINEMATCH_DATA_CSV", str(env_path))
    movies = load_movies(explicit)
    assert len(movies) == 1
    assert movies[0].id == "2"

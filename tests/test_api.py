"""Smoke tests for HTTP endpoints."""

from fastapi.testclient import TestClient

from cinematch.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_movies_returns_sample_rows() -> None:
    response = client.get("/api/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "title" in data[0]
    assert isinstance(data[0].get("genres"), list)


def test_recommendations_returns_content_neighbors() -> None:
    response = client.get("/api/recommendations", params={"movie_id": "1", "top_k": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["seed_movie_id"] == "1"
    recs = body["recommendations"]
    assert isinstance(recs, list)
    assert len(recs) >= 1
    ids = {movie["id"] for movie in recs}
    assert "1" not in ids


def test_recommendations_by_title_matches_case_insensitive() -> None:
    response = client.get(
        "/api/recommendations/by-title",
        params={"title": "  arrival  ", "top_k": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["seed_movie_id"] == "2"
    assert body["seed_title"] == "Arrival"
    recs = body["recommendations"]
    assert isinstance(recs, list)
    assert "2" not in {movie["id"] for movie in recs}


def test_recommendations_by_title_unknown_returns_404() -> None:
    response = client.get(
        "/api/recommendations/by-title",
        params={"title": "Not A Real Movie Title"},
    )
    assert response.status_code == 404


def test_recommendations_by_title_empty_returns_400() -> None:
    response = client.get("/api/recommendations/by-title", params={"title": "   "})
    assert response.status_code == 400

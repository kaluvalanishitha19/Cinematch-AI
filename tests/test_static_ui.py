"""Smoke tests for the static home page."""

from fastapi.testclient import TestClient

from cinematch.main import app

client = TestClient(app)


def test_home_page_serves_ui_shell() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "Find Your Next Favorite Movie" in body
    assert "Search for a movie you like and CineMatch AI" in body
    assert 'id="title-input"' in body
    assert 'id="data-source"' in body
    assert 'id="search-card"' in body
    assert 'id="because-line"' in body
    assert 'id="because-title"' in body
    assert 'value="demo"' in body
    assert 'value="movielens"' in body
    assert "/static/js/recommendations.js" in body
    assert "Get Recommendations" in body
    assert "Jumanji (1995)" in body


def test_static_js_wires_demo_and_movielens_apis() -> None:
    response = client.get("/static/js/recommendations.js")
    assert response.status_code == 200
    text = response.text
    assert "/api/recommendations/by-title" in text
    assert "/api/movielens/recommendations/by-title" in text
    assert "getApiUrl" in text
    assert "setLoadingState" in text
    assert "sessionStorage" in text

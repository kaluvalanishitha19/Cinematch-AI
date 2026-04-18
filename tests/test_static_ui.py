"""Smoke tests for the static home page."""

from fastapi.testclient import TestClient

from cinematch.main import app

client = TestClient(app)


def test_home_page_serves_ui_shell() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert 'id="title-input"' in body
    assert "/static/js/recommendations.js" in body
    assert "Recommend" in body

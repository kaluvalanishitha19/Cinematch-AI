"""Data models, preprocessing, and loading utilities."""

from cinematch.data.loader import load_movies
from cinematch.data.schema import Movie

__all__ = ["Movie", "load_movies"]

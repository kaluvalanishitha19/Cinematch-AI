"""Pydantic models for MovieLens tables and the merged dataset."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MLRating(BaseModel):
    """One rating row after cleaning (MovieLens ``ratings.csv``)."""

    user_id: str
    movie_id: str
    rating: float
    timestamp: int | None = None


class MLMovie(BaseModel):
    """One movie row with optional aggregates for downstream recommenders."""

    movie_id: str
    title: str
    year: int | None = None
    genres: list[str] = Field(default_factory=list)
    mean_rating: float | None = None
    rating_count: int = 0


class PreparedMovieLensDataset(BaseModel):
    """Clean movies and ratings, ready for matrix factorization or filtering."""

    movies: list[MLMovie]
    ratings: list[MLRating]


class MovieLensRecommendByTitleResponse(BaseModel):
    """API payload for MovieLens title-based content recommendations."""

    seed_movie_id: str
    seed_title: str
    recommendations: list[MLMovie]

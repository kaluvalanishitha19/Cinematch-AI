"""Pydantic models shared across the API and recommendation layers."""

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """A cleaned catalog row ready for the API and recommendation code."""

    id: str
    title: str
    year: int
    genres: list[str] = Field(default_factory=list)
    overview: str

"""HTTP API routes for movies and recommendations."""

from fastapi import APIRouter, HTTPException

from cinematch.data.loader import load_movies
from cinematch.data.preprocess import normalize_whitespace
from cinematch.data.schema import Movie
from cinematch.recommend.engine import recommend_similar

router = APIRouter(tags=["api"])


def _find_movie_by_title(normalized_title: str, movies: list[Movie]) -> Movie | None:
    """Return the first catalog row whose title matches (case-insensitive)."""
    needle = normalized_title.lower()
    for movie in movies:
        if movie.title.lower() == needle:
            return movie
    return None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/movies", response_model=list[Movie])
def list_movies() -> list[Movie]:
    return load_movies()


@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: str) -> Movie:
    for movie in load_movies():
        if movie.id == movie_id:
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")


@router.get("/recommendations")
def get_recommendations(movie_id: str, top_k: int = 5) -> dict:
    """Return content-based neighbors for the chosen seed movie."""
    movies = load_movies()
    matches = recommend_similar(seed_movie_id=movie_id, movies=movies, top_k=top_k)
    return {"seed_movie_id": movie_id, "recommendations": matches}


@router.get("/recommendations/by-title")
def get_recommendations_by_title(title: str, top_k: int = 5) -> dict:
    """Return content-based neighbors after resolving a movie by its title."""
    movies = load_movies()
    cleaned = normalize_whitespace(title)
    if not cleaned:
        raise HTTPException(status_code=400, detail="title must not be empty")

    seed = _find_movie_by_title(cleaned, movies)
    if seed is None:
        raise HTTPException(status_code=404, detail="No movie matched that title")

    matches = recommend_similar(seed_movie_id=seed.id, movies=movies, top_k=top_k)
    return {
        "seed_title": seed.title,
        "seed_movie_id": seed.id,
        "recommendations": matches,
    }

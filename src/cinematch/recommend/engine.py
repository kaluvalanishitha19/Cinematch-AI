"""Recommendation engine facade.

Delegates to small strategy modules (starting with content-based TF–IDF).
"""

from cinematch.data.schema import Movie
from cinematch.recommend import content


def recommend_similar(
    seed_movie_id: str,
    movies: list[Movie],
    top_k: int = 10,
) -> list[Movie]:
    """Return movies similar to the seed using content-based scoring."""
    if top_k <= 0 or len(movies) < 2:
        return []

    seed_index = next(
        (index for index, movie in enumerate(movies) if movie.id == seed_movie_id),
        None,
    )
    if seed_index is None:
        return []

    return content.recommend_content_based(seed_index, movies, top_k)

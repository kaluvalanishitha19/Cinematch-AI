"""Content-based recommendations for MovieLens ``MLMovie`` rows.

We turn each movie into a short text document (title, genres, year, and a
light summary of rating stats), run TF–IDF, then rank neighbors with cosine
similarity—same idea as ``recommend.content``, but tuned for MovieLens fields.
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from cinematch.data.movielens.schema import MLMovie, PreparedMovieLensDataset
from cinematch.data.preprocess import normalize_whitespace


def ml_movie_to_document(movie: MLMovie) -> str:
    """Build a single text blob from the fields we want the model to see."""
    parts: list[str] = [movie.title, *movie.genres]
    if movie.year is not None:
        parts.append(str(movie.year))
    if movie.rating_count > 0 and movie.mean_rating is not None:
        parts.append(f"avg_rating_{movie.mean_rating:.2f}")
        parts.append(f"ratings_{movie.rating_count}")
    text = " ".join(parts).strip()
    return text if text else "unknown"


def find_movie_index_by_title(movies: list[MLMovie], normalized_title: str) -> int | None:
    """Return the first index whose title matches (case-insensitive)."""
    needle = normalized_title.lower()
    for index, movie in enumerate(movies):
        if movie.title.lower() == needle:
            return index
    return None


def recommend_movielens_content_based(
    seed_index: int,
    movies: list[MLMovie],
    top_k: int,
) -> list[MLMovie]:
    """Return up to ``top_k`` neighbors for ``movies[seed_index]``."""
    if top_k <= 0 or len(movies) < 2:
        return []

    documents = [ml_movie_to_document(movie) for movie in movies]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=1,
        ngram_range=(1, 2),
    )
    matrix = vectorizer.fit_transform(documents)

    seed_vector = matrix[seed_index]
    scores = cosine_similarity(seed_vector, matrix).ravel()

    order = sorted(range(len(movies)), key=lambda idx: scores[idx], reverse=True)
    picks: list[MLMovie] = []
    for idx in order:
        if idx == seed_index:
            continue
        picks.append(movies[idx])
        if len(picks) >= top_k:
            break
    return picks


def recommend_movielens_by_title(
    dataset: PreparedMovieLensDataset,
    title: str,
    top_k: int = 10,
) -> tuple[MLMovie, list[MLMovie]]:
    """Resolve a movie by title and return that row plus similar movies."""
    cleaned = normalize_whitespace(title)
    if not cleaned:
        raise ValueError("title must not be empty")

    movies = dataset.movies
    seed_index = find_movie_index_by_title(movies, cleaned)
    if seed_index is None:
        raise LookupError("no movie matched that title")

    similar = recommend_movielens_content_based(seed_index, movies, top_k)
    return movies[seed_index], similar

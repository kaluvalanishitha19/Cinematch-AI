"""Content-based similarity using movie text (genres + overview).

Each movie becomes a short "document". We build a TF–IDF vector for every
document, then rank other movies by **cosine similarity** to the seed movie.
This is a small, standard baseline that is easy to explain in a README or
interview.
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from cinematch.data.schema import Movie


def movie_to_document(movie: Movie) -> str:
    """Combine genres and overview into one string for vectorization."""
    genre_words = " ".join(movie.genres)
    overview = movie.overview.strip()
    text = f"{genre_words} {overview}".strip()
    # Avoid totally empty strings, which can confuse the vectorizer.
    return text if text else "unknown"


def recommend_content_based(
    seed_index: int,
    movies: list[Movie],
    top_k: int,
) -> list[Movie]:
    """Return up to ``top_k`` movies most similar to ``movies[seed_index]``."""
    documents = [movie_to_document(movie) for movie in movies]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=1,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(documents)

    seed_vector = tfidf_matrix[seed_index]
    scores = cosine_similarity(seed_vector, tfidf_matrix).ravel()

    ranked_indices = sorted(
        range(len(movies)),
        key=lambda idx: scores[idx],
        reverse=True,
    )

    picks: list[Movie] = []
    for idx in ranked_indices:
        if idx == seed_index:
            continue
        picks.append(movies[idx])
        if len(picks) >= top_k:
            break

    return picks

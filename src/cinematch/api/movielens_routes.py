"""MovieLens-specific HTTP routes (requires ``CINEMATCH_MOVIELENS_DIR``)."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

from cinematch.data.movielens.cache import load_movielens_prepared_cached
from cinematch.data.movielens.schema import MovieLensRecommendByTitleResponse
from cinematch.recommend.movielens_content import recommend_movielens_by_title

router = APIRouter(tags=["movielens"])

_ENV_DIR = "CINEMATCH_MOVIELENS_DIR"


def _movielens_root() -> str:
    root = os.environ.get(_ENV_DIR, "").strip()
    if not root:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Set {_ENV_DIR} to a folder containing movies.csv and ratings.csv "
                "(MovieLens export layout)."
            ),
        )
    return root


@router.get(
    "/recommendations/by-title",
    response_model=MovieLensRecommendByTitleResponse,
)
def movielens_recommendations_by_title(title: str, top_k: int = 5) -> MovieLensRecommendByTitleResponse:
    """Content-based neighbors using the prepared MovieLens catalog."""
    dataset = load_movielens_prepared_cached(_movielens_root())
    try:
        seed, similar = recommend_movielens_by_title(dataset, title, top_k=top_k)
    except ValueError:
        raise HTTPException(status_code=400, detail="title must not be empty") from None
    except LookupError:
        raise HTTPException(status_code=404, detail="No movie matched that title") from None

    return MovieLensRecommendByTitleResponse(
        seed_movie_id=seed.movie_id,
        seed_title=seed.title,
        recommendations=similar,
    )

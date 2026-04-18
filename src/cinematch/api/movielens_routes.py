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


def _load_movielens_dataset(root: str):
    """Load the prepared dataset or raise ``HTTPException`` (503) with a clear reason."""
    try:
        return load_movielens_prepared_cached(root)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MovieLens data is not available. "
                f"Set {_ENV_DIR} to the extracted **ml-latest-small** folder that contains "
                "`movies.csv` and `ratings.csv` side by side. "
                f"({exc})"
            ),
        ) from None
    except OSError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MovieLens data could not be read (permissions or disk error). "
                f"Check {_ENV_DIR}. ({exc})"
            ),
        ) from None
    except ValueError as exc:
        # CSV header problems, malformed exports, etc.
        raise HTTPException(
            status_code=503,
            detail=(
                "MovieLens CSVs could not be parsed. "
                "Confirm you unzipped the official GroupLens archive and pointed "
                f"{_ENV_DIR} at that folder. ({exc})"
            ),
        ) from None


@router.get(
    "/recommendations/by-title",
    response_model=MovieLensRecommendByTitleResponse,
)
def movielens_recommendations_by_title(title: str, top_k: int = 5) -> MovieLensRecommendByTitleResponse:
    """Content-based neighbors using the prepared MovieLens catalog."""
    dataset = _load_movielens_dataset(_movielens_root())
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

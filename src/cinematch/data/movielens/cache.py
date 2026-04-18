"""Optional LRU cache for prepared MovieLens data (avoids reloading huge CSVs)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from cinematch.data.movielens.dataset import load_prepared_movielens
from cinematch.data.movielens.schema import PreparedMovieLensDataset


@lru_cache(maxsize=4)
def load_movielens_prepared_cached(data_root: str) -> PreparedMovieLensDataset:
    """Load and preprocess MovieLens files from ``data_root`` (directory path as string)."""
    return load_prepared_movielens(Path(data_root))


def clear_movielens_cache() -> None:
    """Drop cached datasets (call from tests after env changes)."""
    load_movielens_prepared_cached.cache_clear()

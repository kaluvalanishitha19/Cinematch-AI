"""Data package: demo CSV, MovieLens CSVs, preprocessing, and models."""

from cinematch.data.loader import load_movies
from cinematch.data.movielens import PreparedMovieLensDataset, load_prepared_movielens
from cinematch.data.schema import Movie

__all__ = ["Movie", "PreparedMovieLensDataset", "load_movies", "load_prepared_movielens"]

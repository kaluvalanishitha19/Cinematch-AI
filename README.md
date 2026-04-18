# Cinematch-AI

AI-powered movie recommendation system with content-based filtering, collaborative filtering, and explainable suggestions.

## Data loading and preprocessing

CSV columns required: `id`, `title`, `year`, `genres`, `overview`.

| Module | Role |
|--------|------|
| `cinematch.data.loader` | Resolve path (`CINEMATCH_DATA_CSV` or `data/sample_movies.csv`), read UTF-8 CSV with BOM support, validate header. |
| `cinematch.data.pipeline` | Turn raw row dicts into `Movie` objects, dedupe by `id`, sort by id. |
| `cinematch.data.preprocess` | Trim/normalize text, parse genres and years, build each `Movie`. |
| `cinematch.data.schema` | Pydantic `Movie` model (`genres` as a list). |
| `cinematch.data.movielens` | MovieLens `movies.csv` + `ratings.csv` → `PreparedMovieLensDataset`. |

Default sample file: `data/sample_movies.csv`.

## MovieLens-style dataset (movies + ratings)

For collaborative or hybrid recommenders, use the same layout as **MovieLens** CSV exports (for example **ml-latest-small**):

```text
your-ml-folder/
  movies.csv    # movieId,title,genres
  ratings.csv   # userId,movieId,rating,timestamp
```

Load and preprocess in Python:

```python
from pathlib import Path
from cinematch.data.movielens import load_prepared_movielens

dataset = load_prepared_movielens(Path("path/to/ml-latest-small"))
# dataset.movies -> MLMovie rows with mean_rating / rating_count filled when ratings exist
# dataset.ratings -> cleaned MLRating rows (orphans removed)
```

Or set `CINEMATCH_MOVIELENS_DIR` to that folder and call `load_prepared_movielens()` with no arguments.

**Cleaning rules (short):** drop movie rows with empty ids or titles; split genres on `|` and treat `(no genres listed)` as empty; parse `Title (YYYY)` into display title + year; drop ratings with missing ids, non-numeric ratings, or values outside **0.5–5.0**; drop ratings whose `movieId` is not in `movies.csv`; attach **mean rating** and **count** per movie.

### MovieLens content recommendations (API)

With `CINEMATCH_MOVIELENS_DIR` set to a prepared MovieLens folder:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/movielens/recommendations/by-title` | Query `title` (required), `top_k` (default `5`). TF–IDF over title, genres, year, and light rating-summary text. Returns `503` if the env var is missing. |

The smaller **demo** catalog (`/api/recommendations/...`) is unchanged and does not require MovieLens files.

# CineMatch AI

A small **movie recommendation** demo you can run locally: a **FastAPI** backend, a **content-based** recommender (TF–IDF + cosine similarity), CSV-based data with preprocessing, and a minimal static UI. The code is structured so you can grow it into a fuller portfolio piece (ratings, posters, collaborative filtering, and so on).

## What it does

- Loads a movie catalog from CSV (bundled sample plus optional override path).
- Cleans and normalizes rows (genres as a list, whitespace, years, dedupe by `id`).
- Suggests **similar titles** from genre + overview text—no user accounts required.
- Exposes a JSON **REST API** with interactive docs at `/docs`.

## Tech stack

| Piece | Choice |
|--------|--------|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Validation | [Pydantic](https://docs.pydantic.dev/) v2 |
| Recommendations | [scikit-learn](https://scikit-learn.org/) TF–IDF + cosine similarity |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Tests | [pytest](https://pytest.org/) + `httpx` TestClient |

Python **3.11+** recommended.

## Architecture (short)

The **API** (`src/cinematch/api/`) calls **data loading** (`data/loader.py`, `data/preprocess.py`) and the **recommendation engine** (`recommend/engine.py`), which delegates to **content-based** scoring in `recommend/content.py`. Static files under `static/` are served for the placeholder UI.

## Quick start

```bash
cd cinematch-ai   # your local clone of this repository
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn cinematch.main:app --reload --app-dir src
```

Then open:

- **UI placeholder:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API

Base path for JSON routes: **`/api`**.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Liveness check. |
| `GET` | `/api/movies` | Full catalog (preprocessed). |
| `GET` | `/api/movies/{movie_id}` | One movie by `id`; `404` if missing. |
| `GET` | `/api/recommendations` | Query: `movie_id` (required), `top_k` (default `5`). Returns `seed_movie_id` and `recommendations`. |
| `GET` | `/api/recommendations/by-title` | Query: `title` (required), `top_k` (default `5`). Title match is case-insensitive after whitespace normalization. Returns `seed_title`, `seed_movie_id`, and `recommendations`. Empty title → `400`; no match → `404`. |

Example:

```bash
curl "http://127.0.0.1:8000/api/recommendations/by-title?title=Arrival&top_k=3"
```

## How recommendations work

1. Each movie becomes one text field: **genres** (joined) plus the **overview** (`movie_to_document` in `recommend/content.py`).
2. `TfidfVectorizer` builds sparse vectors (English stop words removed; unigrams and bigrams, `min_df=1` for small catalogs).
3. **Cosine similarity** ranks every other movie against the seed; the seed is excluded from results.

This is an explainable baseline—not personalized collaborative filtering.

## Data

**Required CSV columns:** `id`, `title`, `year`, `genres`, `overview`.

- Default file: `data/sample_movies.csv` (tiny set for demos).
- **Override path** (optional):

```bash
export CINEMATCH_DATA_CSV=/absolute/or/relative/path/to/movies.csv
```

Preprocessing summary: UTF-8 with optional BOM, trimmed fields, genre split and case-insensitive dedupe, year range **1888–2035**, duplicate `id` keeps first row, stable sort by numeric `id` when possible.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Repository layout

```text
data/                 # Sample CSV (replace or point via env)
scripts/              # Optional dataset helpers
src/cinematch/
  api/routes.py       # HTTP routes
  data/               # Schema, load, preprocess
  recommend/          # Engine + content-based model
  static/             # Placeholder UI
tests/                # pytest suite
```

## Limitations and natural next steps

- **Content-only:** suggestions follow text overlap, not your watch history.
- **Title lookup:** exact title match (after trim + case fold); multiple same titles resolve to the **first** row in catalog order.
- **Scale:** TF–IDF is rebuilt per request from the in-memory catalog—fine for demos; larger deployments would cache vectors or use a search index.

Reasonable extensions: MovieLens or TMDB integration, posters, user ratings, collaborative or hybrid models, Docker, and CI (GitHub Actions).

## License

MIT — see [LICENSE](LICENSE).

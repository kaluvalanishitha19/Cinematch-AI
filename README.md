# CineMatch AI

**FastAPI + scikit-learn** portfolio project: load movie catalogs, preprocess **MovieLens-style** CSVs, and serve **content-based** recommendations with **TF–IDF** and **cosine similarity**. The codebase is split into small modules (data loading, preprocessing, recommendation, HTTP) so it is easy to extend toward **collaborative filtering** or a richer UI later.

---

## Table of contents

1. [Project overview](#project-overview)  
2. [Architecture](#architecture)  
3. [MovieLens preprocessing](#movielens-preprocessing)  
4. [How TF–IDF recommendations work](#how-tf-idf-recommendations-work)  
5. [API reference](#api-reference)  
6. [Setup and run](#setup-and-run)  
7. [Web UI](#web-ui)  
8. [Testing and quality](#testing-and-quality)  
9. [Suggested screenshots and sample output](#suggested-screenshots-and-sample-output)  
10. [Roadmap](#roadmap)  
11. [License](#license)

---

## Project overview

| | |
|--|--|
| **Goal** | Demonstrate an end-to-end ML-adjacent service: validated data ingestion, text vectorization, ranking, and a documented HTTP API. |
| **What ships today** | Two **content-based** paths: a **tiny demo CSV** (about half a dozen titles bundled for screenshots) and an optional **MovieLens** export (`movies.csv` + `ratings.csv`) for realistic testing. |
| **What is out of scope (for now)** | User accounts, training pipelines, collaborative filtering, and production deployment hardening. |

**Stack:** Python 3.11+, FastAPI, Pydantic v2, Uvicorn, scikit-learn, pytest.

---

## Architecture

- **`cinematch.data`** — Load and clean data (`loader`, `pipeline`, `preprocess`), plus a **`movielens`** subpackage for MovieLens CSV layout, merges, and optional LRU **cache**.  
- **`cinematch.recommend`** — Pure recommendation helpers: demo **`content`** (overview + genres) and **`movielens_content`** (title + genres + year + rating summaries).  
- **`cinematch.api`** — HTTP routers under `/api` (demo catalog) and `/api/movielens` (MovieLens-backed route).  
- **`cinematch.static`** — Portfolio-style landing UI at `/` (hero, search card, results) calling demo or MovieLens APIs from the browser.

---

## MovieLens preprocessing

MovieLens exports (for example **ml-latest-small**) use two files in one directory:

```text
your-ml-folder/
  movies.csv     # movieId, title, genres (genres separated by |)
  ratings.csv    # userId, movieId, rating, timestamp
```

**End-to-end flow** (see `cinematch.data.movielens`):

1. **Read CSVs** — UTF-8 with optional BOM; required columns are validated on the header.  
2. **Clean movies** — Skip rows with empty `movieId` or empty display title. Genres split on `|`; `(no genres listed)` becomes an empty list. Titles like `Toy Story (1995)` become display title plus parsed **year** when the trailing `(YYYY)` pattern matches.  
3. **Clean ratings** — Skip rows with missing ids or ratings; ratings must parse as floats in **0.5–5.0** (MovieLens scale). Bad or empty timestamps become `null` in the model rather than failing the whole file.  
4. **Align ids** — Drop ratings whose `movieId` never appears in `movies.csv` (orphans).  
5. **Aggregate** — For each movie, compute **mean rating** and **rating count** from the surviving ratings; movies with no ratings keep `mean_rating` unset and `rating_count` at zero.  
6. **Catalog hygiene** — Duplicate `movieId` rows keep the **first** occurrence; movies are sorted by numeric id when possible.

Load in code with `load_prepared_movielens(Path("…"))` or set **`CINEMATCH_MOVIELENS_DIR`** to that folder (also used by the MovieLens API route and the LRU cache).

---

## How TF–IDF recommendations work

Both recommenders follow the same pattern; only the **text fed into TF–IDF** changes.

1. **Document** — Each movie becomes one string (see `movie_to_document` vs `ml_movie_to_document`).  
2. **Vectorize** — `TfidfVectorizer` (scikit-learn) with English **stop words** removed, **`min_df=1`** so small catalogs still work, and **`ngram_range=(1, 2)`** so single words and short phrases both contribute.  
3. **Score** — **Cosine similarity** compares the seed movie’s vector to every other movie’s vector.  
4. **Rank** — Sort by similarity, skip the seed, return the top **`top_k`**.

| Mode | Source rows | Document text roughly contains |
|------|----------------|----------------------------------|
| **Demo catalog** | `Movie` from `data/sample_movies.csv` | Genres + **overview** body copy. |
| **MovieLens catalog** | `MLMovie` after preprocessing | **Title**, **genres**, **year**, and optional tokens derived from **mean rating** and **rating count** (so popularity-ish signal can influence word overlap). |

This is **content-based**, not personalized from a user’s full rating history: similar movies are those whose *text profile* is close to the seed. Collaborative filtering would use the `ratings` table directly; that is a natural next step, not implemented here.

---

## API reference

Interactive docs: **`http://127.0.0.1:8000/docs`** (Swagger UI).

### Demo catalog (`/api` …)

Uses **`CINEMATCH_DATA_CSV`** if set, otherwise **`data/sample_movies.csv`**.

| Method | Path | Query / path params | Description |
|--------|------|----------------------|-------------|
| `GET` | `/api/health` | — | `{ "status": "ok" }` |
| `GET` | `/api/movies` | — | List all movies. |
| `GET` | `/api/movies/{movie_id}` | path: `movie_id` | One movie; `404` if missing. |
| `GET` | `/api/recommendations` | `movie_id` (required), `top_k` default `5` | Similar movies by id. |
| `GET` | `/api/recommendations/by-title` | `title` (required), `top_k` default `5` | Match title (case-insensitive, trimmed); `400` empty title; `404` no match. |

### MovieLens catalog (`/api/movielens` …)

Requires **`CINEMATCH_MOVIELENS_DIR`** pointing at a folder that contains **`movies.csv`** and **`ratings.csv`** next to each other (same layout as GroupLens **ml-latest-small**). Returns **`503`** if the variable is unset, the path is missing, or the CSVs cannot be read or parsed.

| Method | Path | Query params | Description |
|--------|------|--------------|-------------|
| `GET` | `/api/movielens/recommendations/by-title` | `title` (required), `top_k` default `5` | Content-based neighbors from the prepared MovieLens movie table. Title lookup accepts either the **stored display title** (e.g. `Jumanji`) or the **raw MovieLens CSV form** including the year in parentheses (e.g. `Jumanji (1995)`). |

### Example: demo recommendations by title

**Request**

```http
GET /api/recommendations/by-title?title=Arrival&top_k=2
```

**Example response** (shape from the bundled sample; exact neighbors depend on TF–IDF scores)

```json
{
  "seed_title": "Arrival",
  "seed_movie_id": "2",
  "recommendations": [
    {
      "id": "5",
      "title": "Mad Max Fury Road",
      "year": 2015,
      "genres": ["Action", "Adventure", "Sci-Fi"],
      "overview": "Survivors flee across a desert wasteland pursued by a warlord and his army."
    }
  ]
}
```

### Example: MovieLens recommendations by title

**Request** (after `export CINEMATCH_MOVIELENS_DIR=…`)

```http
GET /api/movielens/recommendations/by-title?title=Toy%20Story&top_k=3
```

**Example response** (fields reflect `MLMovie`; list truncated for readability)

```json
{
  "seed_movie_id": "1",
  "seed_title": "Toy Story",
  "recommendations": [
    {
      "movie_id": "…",
      "title": "…",
      "year": 1995,
      "genres": ["Adventure", "Animation", "Children"],
      "mean_rating": 3.89,
      "rating_count": 57309
    }
  ]
}
```

Exact `recommendations` depend on your MovieLens slice and TF–IDF scores.

---

## Setup and run

**Prerequisites:** Python **3.11+**, `pip`, and optionally a MovieLens **ml-latest-small** (or compatible) unzip if you want the **MovieLens Library** path in the UI and `/api/movielens/...` (recommended for anything beyond the tiny bundled sample).

```bash
cd cinematch-ai
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn cinematch.main:app --reload --app-dir src
```

- **Web app:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- **API docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Web UI

The home page (`/`) is a **vanilla HTML/CSS/JS** client (no build step) with a **theater-style** layout: spotlight hero, popcorn motif, film-strip accents, ticket “quick pick” chips, a large search bar, and **poster-style** cards. Each card uses **CSS gradients and a monogram placeholder** (no copyrighted poster art). Catalog choice and how many picks to show live under **Fine-tune your night**. The same JSON APIs power the experience:

| Mode | API used | What you see |
|------|------------|----------------|
| **Sample Movies** | `GET /api/recommendations/by-title` | A **small fixed demo** (`data/sample_movies.csv` or `CINEMATCH_DATA_CSV`). Recommendation lists are **short by design**—the UI explains that so the experience still feels intentional. |
| **MovieLens Library** | `GET /api/movielens/recommendations/by-title` | **Recommended for “real app” testing**: thousands of titles, **genres, year, ids**, and optional **mean rating / count** (MovieLens has no plot field in the CSV). |

**Choosing a catalog**

- **Sample Movies** — Ships with the repo; only **six titles**. Quick picks match those rows exactly. Use it for a fast demo without downloading data.  
- **MovieLens Library (recommended)** — Point **`CINEMATCH_MOVIELENS_DIR`** at an extracted **ml-latest-small** folder (see below). Quick picks use well-known **1995** titles from that dataset. If the variable is not set, the UI shows a **short, non-technical notice** and blocks searches in MovieLens mode until you configure the server or switch back to Sample Movies (setup steps stay in this README only).

Empty search shows an inline message. **404** and **503** use friendly copy in the marquee (including guidance to try Sample Movies when MovieLens is unavailable). Your last source choice is remembered for the browser tab (**sessionStorage**).

### Downloading MovieLens **ml-latest-small** (recommended)

These steps use the official **GroupLens** release (free, no API key). Nothing large is committed to GitHub—you download it locally.

1. Open **[MovieLens Latest Datasets](https://grouplens.org/datasets/movielens/latest/)** in your browser.  
2. Download **`ml-latest-small.zip`** (about 1 MB; “small” means smaller than the full MovieLens dumps, not “small feature set”).  
3. **Unzip** the archive. You should see a folder named **`ml-latest-small`**. Inside it, **`movies.csv`** and **`ratings.csv`** must sit **in the same directory** (not only inside nested archives).  
4. **Set the environment variable** to the **absolute path** of that folder (adjust the path for your machine):

```bash
export CINEMATCH_MOVIELENS_DIR="/absolute/path/to/ml-latest-small"
uvicorn cinematch.main:app --reload --app-dir src
```

5. In the web UI, open **Fine-tune your night** → choose **MovieLens Library (recommended)** → use quick picks or search (e.g. **Toy Story (1995)**).

If the path is wrong or the CSVs are missing, `/api/movielens/recommendations/by-title` responds with **`503`** and a JSON `detail` string explaining that `movies.csv` / `ratings.csv` were not found or could not be parsed.

**Developer / CI quick path (tiny fixture)**

The repo includes **`tests/fixtures/movielens/`** with minimal `movies.csv` and `ratings.csv` for automated tests. You can point your shell at it while developing the MovieLens API (titles in that file include **Toy Story**):

```bash
export CINEMATCH_MOVIELENS_DIR="$(pwd)/tests/fixtures/movielens"
uvicorn cinematch.main:app --reload --app-dir src
```

**Uvicorn entrypoint:** use `cinematch.main:app` with `--app-dir src` (not `src.cinematch.api.main`), so imports match this repository layout.

**Optional — custom demo CSV**

```bash
export CINEMATCH_DATA_CSV="/path/to/your_movies.csv"
# columns: id, title, year, genres, overview
```

---

## Testing and quality

```bash
pytest
ruff check src tests
```

---

## Suggested screenshots and sample output

Add these under **`docs/images/`** (create the folder when you have assets) and link them from this README—recruiters often skim visuals first.

1. **Swagger UI** — `http://127.0.0.1:8000/docs` showing the `/api/recommendations/by-title` and `/api/movielens/recommendations/by-title` operations expanded.  
2. **Terminal sample** — A short session: `curl` call + pretty-printed JSON (or `httpie` / `jq`), demonstrating a 200 response and one error case (`404` or `503`).  
3. **Architecture** (optional) — A simple diagram: CSV → preprocess → TF–IDF → FastAPI → client.  
4. **Web UI (desktop)** — Save as `assets/ui-demo.png`: full `/` page with theater hero, popcorn, search bar, and ticket quick-picks.  
5. **Web UI (results)** — Save as `assets/movie-results.png`: “Because you searched for…” line, spotlight seed poster, and poster-style recommendation grid.  
6. **Web UI (mobile)** — Narrow viewport showing stacked posters and the search card.  
7. **Error states** — Optional captures of the marquee alert for **404** (“We couldn’t find…”) and **503** (“The full movie library…”) when MovieLens is unavailable.

You can paste the same **example JSON** blocks above into the repo as **`.json` examples** under `docs/examples/` if you want copy-paste fixtures without maintaining screenshots.

---

## Roadmap

- Collaborative or hybrid models using `PreparedMovieLensDataset.ratings`.  
- Integrate TMDB API for real movie posters and metadata.  
- Docker and CI (GitHub Actions) for install + `pytest` on push.

---

## License

MIT — see [LICENSE](LICENSE).

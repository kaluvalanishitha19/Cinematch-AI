# CineMatch AI 🎬🍿

CineMatch AI is a movie recommendation web app that helps users discover similar movies based on genre and content similarity.

Users can search for a movie they like, choose how many recommendations they want, and instantly get a list of related films through a clean, movie-themed interface.

This project was built as an end-to-end AI/ML portfolio project with a working recommendation engine, FastAPI backend, interactive frontend, MovieLens dataset support, and automated tests.

---

## ✨ Features

- Search for movies and get similar recommendations
- Supports both a small sample catalog and the full MovieLens dataset
- Content-based recommendation using TF-IDF similarity
- FastAPI backend with documented API routes
- Responsive movie-themed web interface
- User-friendly error handling
- Unit tests for data loading, preprocessing, recommendation logic, API routes, and UI behavior
- Large dataset files excluded from GitHub using `.gitignore`

---

## 🧠 How It Works

CineMatch AI uses a content-based recommendation approach.

The system loads movie data, cleans and preprocesses the catalog, extracts useful movie features such as title, year, genres, and rating statistics, and then uses TF-IDF based similarity to find related movies.

When a user searches for a movie such as **Jumanji (1995)**, the system compares its content features with other movies and returns recommendations with similar genre and content patterns.

---

## 🛠️ Tech Stack

- **Python**
- **FastAPI**
- **Pydantic**
- **Scikit-learn**
- **Pandas**
- **HTML**
- **CSS**
- **JavaScript**
- **Pytest**
- **MovieLens Dataset**

---

## 📁 Project Structure

```text
cinematch-ai/
│
├── src/
│   └── cinematch/
│       ├── api/              # FastAPI routes
│       ├── data/             # Data loading and preprocessing
│       ├── recommend/        # Recommendation logic
│       ├── static/           # Frontend UI files
│       └── main.py           # FastAPI app entry point
│
├── tests/                    # Unit and API tests
├── data/                     # Local data folder
├── README.md
├── .gitignore
└── pyproject.toml
```

---

## 🚀 How to Run the Project Locally

Follow these steps to run CineMatch AI on your machine.

### Step 1: Clone the repository

```bash
git clone https://github.com/kaluvalanishitha19/Cinematch-AI.git
cd Cinematch-AI
```

### Step 2: Create a virtual environment

```bash
python3 -m venv .venv
```

### Step 3: Activate the virtual environment

For macOS/Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -e .
```

### Step 5: Run the app with sample data

```bash
uvicorn cinematch.main:app --reload --app-dir src
```

### Step 6: Open the app in your browser

```text
http://127.0.0.1:8000/
```

This runs the app using the small sample movie catalog included in the repository.

---

## 🎞️ Running with the Full MovieLens Dataset

The full MovieLens dataset is not included in this repository because large data files should not be pushed to GitHub.

To use the full movie library, download the MovieLens `ml-latest-small` dataset and place the required files inside the `data/` folder.

Your folder should look like this:

```text
data/
├── movies.csv
├── ratings.csv
└── sample_movies.csv
```

Then run:

```bash
export CINEMATCH_MOVIELENS_DIR="$(pwd)/data"
uvicorn cinematch.main:app --reload --app-dir src
```

In the web app, choose **Full Movie Library** and search titles such as:

```text
Toy Story (1995)
Jumanji (1995)
Heat (1995)
Apollo 13 (1995)
Braveheart (1995)
Casino (1995)
```

---

## 🔌 API Documentation

FastAPI provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

### MovieLens Recommendation Endpoint

```text
GET /api/movielens/recommendations/by-title?title=Jumanji%20(1995)&top_k=5
```

### Example Response

```json
{
  "seed_movie_id": "2",
  "seed_title": "Jumanji",
  "recommendations": [
    {
      "movie_id": "1",
      "title": "Toy Story",
      "year": 1995,
      "genres": ["Adventure", "Animation", "Children"],
      "mean_rating": 3.9,
      "rating_count": 215
    }
  ]
}
```

---

## 🧪 Running Tests

To run the full test suite:

```bash
pytest -q
```

The project includes tests for:

- Data loading
- Data preprocessing
- MovieLens dataset handling
- Recommendation logic
- API responses
- Static UI behavior
- Missing dataset handling

---

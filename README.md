# CineMatch AI 🎬🍿

CineMatch AI is a movie recommendation web app that helps users discover similar movies based on genre and content similarity.  
Users can search for a movie they like, choose how many recommendations they want, and instantly get a list of related films through a clean, movie-themed interface.

This project was built as an end-to-end AI/ML portfolio project with a working recommendation engine, FastAPI backend, interactive frontend, and MovieLens dataset support.

---

## ✨ Features

- Search for movies and get similar recommendations
- Supports both a small sample catalog and the MovieLens dataset
- Content-based recommendation using TF-IDF similarity
- Clean FastAPI backend with documented API routes
- Movie-themed responsive web UI
- User-friendly error handling
- Unit tests for data loading, preprocessing, recommendation logic, API routes, and UI behavior
- Large dataset files are excluded from GitHub using `.gitignore`

---

## 🧠 How It Works

CineMatch AI uses a content-based recommendation approach.

The system loads movie data, cleans and preprocesses the catalog, extracts useful movie features such as title, year, and genres, and then uses TF-IDF based similarity to find movies that are related to the user’s search.

For example, if a user searches for **Jumanji (1995)**, the system compares its genre and content features with other movies and returns similar recommendations.

---

## 🛠️ Tech Stack

- **Python**
- **FastAPI**
- **Pydantic**
- **Scikit-learn**
- **Pandas**
- **HTML, CSS, JavaScript**
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

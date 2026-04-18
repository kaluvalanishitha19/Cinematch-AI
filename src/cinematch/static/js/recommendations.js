/**
 * Front-end for title-based recommendations: demo catalog or MovieLens.
 */
const DEMO_API = "/api/recommendations/by-title";
const MOVIELENS_API = "/api/movielens/recommendations/by-title";

const DATA_SOURCE_STORAGE_KEY = "cinematchDataSource";

const dataSourceEl = document.getElementById("data-source");
const titleInput = document.getElementById("title-input");
const topkInput = document.getElementById("topk-input");
const searchBtn = document.getElementById("search-btn");
const searchCardEl = document.getElementById("search-card");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const seedTitleEl = document.getElementById("seed-title");
const seedMetaEl = document.getElementById("seed-meta");
const recListEl = document.getElementById("rec-list");

function getSelectedSource() {
  return dataSourceEl.value === "movielens" ? "movielens" : "demo";
}

function getApiUrl() {
  return getSelectedSource() === "movielens" ? MOVIELENS_API : DEMO_API;
}

function setLoadingState(isLoading) {
  searchBtn.disabled = isLoading;
  if (searchCardEl) {
    searchCardEl.setAttribute("aria-busy", isLoading ? "true" : "false");
  }
}

function showStatus(message, kind, httpStatus) {
  statusEl.textContent = message;
  statusEl.hidden = false;
  statusEl.dataset.kind = kind;
  if (httpStatus != null) {
    statusEl.dataset.httpStatus = String(httpStatus);
  } else {
    delete statusEl.dataset.httpStatus;
  }
}

function clearStatus() {
  statusEl.textContent = "";
  statusEl.hidden = true;
  statusEl.removeAttribute("data-kind");
  delete statusEl.dataset.httpStatus;
}

function hideResults() {
  resultsEl.hidden = true;
  recListEl.innerHTML = "";
}

function formatDetail(detail) {
  if (!detail) {
    return "Something went wrong.";
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object" && "msg" in item) {
          return String(item.msg);
        }
        return JSON.stringify(item);
      })
      .join(" ");
  }
  return String(detail);
}

function clampTopK(raw) {
  const value = Number.parseInt(String(raw), 10);
  if (Number.isNaN(value)) {
    return 5;
  }
  return Math.min(20, Math.max(1, value));
}

function truncate(text, maxLen) {
  const clean = String(text || "").trim();
  if (clean.length <= maxLen) {
    return clean;
  }
  return `${clean.slice(0, maxLen - 1)}…`;
}

function renderDemoRecommendations(items) {
  for (const movie of items) {
    const li = document.createElement("li");
    li.className = "rec-card";

    const title = document.createElement("p");
    title.className = "rec-card__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "rec-card__meta";
    const year = movie.year != null ? String(movie.year) : "Year n/a";
    meta.textContent = `${year} · id ${movie.id ?? "—"}`;

    const genres = document.createElement("div");
    genres.className = "rec-card__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    const overview = document.createElement("p");
    overview.className = "rec-card__overview";
    overview.textContent = truncate(movie.overview, 220);

    li.appendChild(title);
    li.appendChild(meta);
    if (genres.childElementCount) {
      li.appendChild(genres);
    }
    li.appendChild(overview);
    recListEl.appendChild(li);
  }
}

function renderMovielensRecommendations(items) {
  for (const movie of items) {
    const li = document.createElement("li");
    li.className = "rec-card";

    const title = document.createElement("p");
    title.className = "rec-card__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "rec-card__meta";
    const year = movie.year != null ? String(movie.year) : "Year n/a";
    const mid = movie.movie_id ?? "—";
    let line = `${year} · movie id ${mid}`;
    if (movie.mean_rating != null && movie.rating_count) {
      line += ` · avg ${Number(movie.mean_rating).toFixed(2)} (${movie.rating_count} ratings)`;
    }
    meta.textContent = line;

    const genres = document.createElement("div");
    genres.className = "rec-card__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    const note = document.createElement("p");
    note.className = "rec-card__overview rec-card__overview--muted";
    note.textContent =
      "MovieLens row (no plot text in this dataset). Similarity uses title, genres, year, and rating summary tokens.";

    li.appendChild(title);
    li.appendChild(meta);
    if (genres.childElementCount) {
      li.appendChild(genres);
    }
    li.appendChild(note);
    recListEl.appendChild(li);
  }
}

function renderRecommendations(items, source) {
  recListEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "rec-empty";
    li.textContent = "No other movies in the catalog to suggest yet.";
    recListEl.appendChild(li);
    return;
  }

  if (source === "movielens") {
    renderMovielensRecommendations(items);
  } else {
    renderDemoRecommendations(items);
  }
}

function friendlyError(status, source, detailText) {
  if (status === 503 && source === "movielens") {
    return [
      "MovieLens is not configured on this server (or the CSV path is wrong).",
      "Set CINEMATCH_MOVIELENS_DIR to the extracted ml-latest-small folder containing movies.csv and ratings.csv, restart Uvicorn, or switch to Demo catalog.",
      "",
      `Details: ${detailText}`,
    ].join("\n");
  }
  if (status === 503) {
    return ["Service unavailable.", "", detailText].join("\n");
  }
  return detailText;
}

function buildErrorMessage(status, source, detailText) {
  const base = friendlyError(status, source, detailText);
  if (status === 404) {
    return [
      "No exact title match in the selected source.",
      "",
      base,
    ].join("\n");
  }
  return base;
}

async function runSearch() {
  const title = titleInput.value.trim();
  const topK = clampTopK(topkInput.value);
  const source = getSelectedSource();

  hideResults();
  clearStatus();

  if (!title) {
    showStatus("Enter a movie title to run a similarity search.", "info");
    return;
  }

  const params = new URLSearchParams({ title, top_k: String(topK) });
  const apiUrl = getApiUrl();

  setLoadingState(true);
  showStatus("Ranking neighbors with TF–IDF…", "loading");

  try {
    const response = await fetch(`${apiUrl}?${params.toString()}`);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detailText = formatDetail(data.detail);
      let message = buildErrorMessage(response.status, source, detailText);
      if (response.status === 404 && source === "demo") {
        message += [
          "",
          "Tip: the demo list is only six rows. For broader catalogs, choose MovieLens (requires CINEMATCH_MOVIELENS_DIR).",
        ].join("\n");
      }
      showStatus(message, "error", response.status);
      return;
    }

    clearStatus();
    seedTitleEl.textContent = data.seed_title || "Unknown title";
    seedMetaEl.textContent = `Catalog id: ${data.seed_movie_id ?? "—"}`;

    renderRecommendations(Array.isArray(data.recommendations) ? data.recommendations : [], source);
    resultsEl.hidden = false;
  } catch {
    showStatus(
      [
        "Could not reach the API.",
        "",
        "Start Uvicorn from the project root:",
        "uvicorn cinematch.main:app --reload --app-dir src",
        "",
        "Then open http://127.0.0.1:8000/",
      ].join("\n"),
      "error",
    );
  } finally {
    setLoadingState(false);
  }
}

searchBtn.addEventListener("click", runSearch);

titleInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    runSearch();
  }
});

function restoreDataSourcePreference() {
  try {
    const saved = window.sessionStorage.getItem(DATA_SOURCE_STORAGE_KEY);
    if (saved === "movielens" || saved === "demo") {
      dataSourceEl.value = saved;
    }
  } catch {
    /* ignore */
  }
}

function rememberDataSourcePreference() {
  try {
    window.sessionStorage.setItem(DATA_SOURCE_STORAGE_KEY, dataSourceEl.value);
  } catch {
    /* ignore */
  }
}

dataSourceEl.addEventListener("change", rememberDataSourcePreference);
restoreDataSourcePreference();

/**
 * Simple front-end for GET /api/recommendations/by-title (demo catalog).
 * Keeps logic in one file for beginners; swap API_URL if you add more backends.
 */
const API_URL = "/api/recommendations/by-title";

const titleInput = document.getElementById("title-input");
const topkInput = document.getElementById("topk-input");
const searchBtn = document.getElementById("search-btn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const seedTitleEl = document.getElementById("seed-title");
const seedMetaEl = document.getElementById("seed-meta");
const recListEl = document.getElementById("rec-list");

function showStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.hidden = false;
  statusEl.dataset.kind = kind;
}

function clearStatus() {
  statusEl.textContent = "";
  statusEl.hidden = true;
  statusEl.removeAttribute("data-kind");
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

function renderRecommendations(items) {
  recListEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "rec-empty";
    li.textContent = "No other movies in the catalog to suggest yet.";
    recListEl.appendChild(li);
    return;
  }

  for (const movie of items) {
    const li = document.createElement("li");
    li.className = "rec-card";

    const title = document.createElement("p");
    title.className = "rec-card__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "rec-card__meta";
    const year = movie.year != null ? String(movie.year) : "Year n/a";
    meta.textContent = `${year} · id ${movie.id}`;

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

async function runSearch() {
  const title = titleInput.value.trim();
  const topK = clampTopK(topkInput.value);

  hideResults();
  clearStatus();

  if (!title) {
    showStatus("Please enter a movie title to search.", "info");
    return;
  }

  showStatus("Looking for similar movies…", "info");

  const params = new URLSearchParams({ title, top_k: String(topK) });

  try {
    const response = await fetch(`${API_URL}?${params.toString()}`);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const message = formatDetail(data.detail);
      showStatus(message, "error");
      return;
    }

    clearStatus();
    seedTitleEl.textContent = data.seed_title || "Unknown title";
    seedMetaEl.textContent = `Catalog id: ${data.seed_movie_id ?? "—"}`;

    renderRecommendations(Array.isArray(data.recommendations) ? data.recommendations : []);
    resultsEl.hidden = false;
  } catch {
    showStatus(
      "Could not reach the server. Start the app with Uvicorn and open this page from http://127.0.0.1:8000 .",
      "error",
    );
  }
}

searchBtn.addEventListener("click", runSearch);

titleInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    runSearch();
  }
});

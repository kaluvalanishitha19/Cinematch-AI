/**
 * CineMatch front-end — demo or MovieLens title search (same APIs as before).
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
const becauseLineEl = document.getElementById("because-line");
const becauseTitleEl = document.getElementById("because-title");
const seedTitleEl = document.getElementById("seed-title");
const seedMetaEl = document.getElementById("seed-meta");
const seedPosterEl = document.querySelector(".poster--seed");
const recListEl = document.getElementById("rec-list");

function getSelectedSource() {
  return dataSourceEl.value === "movielens" ? "movielens" : "demo";
}

function getApiUrl() {
  return getSelectedSource() === "movielens" ? MOVIELENS_API : DEMO_API;
}

function setPosterHue(element, title) {
  let hue = 0;
  const text = String(title || "film");
  for (let i = 0; i < text.length; i += 1) {
    hue = (hue + text.charCodeAt(i) * 17) % 360;
  }
  element.style.setProperty("--poster-hue", String(hue));
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
  if (becauseLineEl) {
    becauseLineEl.hidden = true;
  }
}

function formatDetail(detail) {
  if (!detail) {
    return "";
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

function buildPosterShell() {
  const li = document.createElement("li");
  li.className = "poster";

  const glow = document.createElement("div");
  glow.className = "poster__glow";
  glow.setAttribute("aria-hidden", "true");

  const frame = document.createElement("div");
  frame.className = "poster__frame";

  const canvas = document.createElement("div");
  canvas.className = "poster__canvas";

  const body = document.createElement("div");
  body.className = "poster__body";

  frame.appendChild(canvas);
  frame.appendChild(body);
  li.appendChild(glow);
  li.appendChild(frame);

  return { li, canvas, body };
}

function renderDemoRecommendations(items) {
  for (const movie of items) {
    const { li, canvas, body } = buildPosterShell();
    setPosterHue(li, movie.title);

    const title = document.createElement("h3");
    title.className = "poster__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "poster__meta";
    const year = movie.year != null ? String(movie.year) : "—";
    meta.textContent = `${year} · Ref. ${movie.id ?? "—"}`;

    const genres = document.createElement("div");
    genres.className = "poster__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    const synopsis = document.createElement("p");
    synopsis.className = "poster__synopsis";
    synopsis.textContent = truncate(movie.overview, 140);

    const tagline = document.createElement("p");
    tagline.className = "poster__tagline";
    tagline.textContent = "Similar genres and content patterns";

    body.appendChild(title);
    body.appendChild(meta);
    if (genres.childElementCount) {
      body.appendChild(genres);
    }
    body.appendChild(synopsis);
    body.appendChild(tagline);

    recListEl.appendChild(li);
  }
}

function renderMovielensRecommendations(items) {
  for (const movie of items) {
    const { li, canvas, body } = buildPosterShell();
    setPosterHue(li, movie.title);

    const title = document.createElement("h3");
    title.className = "poster__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "poster__meta";
    const year = movie.year != null ? String(movie.year) : "—";
    let line = `${year} · Ref. ${movie.movie_id ?? "—"}`;
    if (movie.mean_rating != null && movie.rating_count) {
      line += ` · ★ ${Number(movie.mean_rating).toFixed(2)} (${movie.rating_count} ratings)`;
    }
    meta.textContent = line;

    const genres = document.createElement("div");
    genres.className = "poster__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    const synopsis = document.createElement("p");
    synopsis.className = "poster__synopsis";
    synopsis.textContent =
      "Placeholder art only — this library does not ship poster images. Rankings still use story signals from the catalog.";

    const tagline = document.createElement("p");
    tagline.className = "poster__tagline";
    tagline.textContent = "Similar genres and content patterns";

    body.appendChild(title);
    body.appendChild(meta);
    if (genres.childElementCount) {
      body.appendChild(genres);
    }
    body.appendChild(synopsis);
    body.appendChild(tagline);

    recListEl.appendChild(li);
  }
}

function renderRecommendations(items, source) {
  recListEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "rec-empty";
    li.textContent = "The house lights are on, but we need more rows in this reel to fill extra seats.";
    recListEl.appendChild(li);
    return;
  }

  if (source === "movielens") {
    renderMovielensRecommendations(items);
  } else {
    renderDemoRecommendations(items);
  }
}

function errorMessageForResponse(status, source, detail) {
  if (status === 404) {
    return "We couldn’t find that movie. Try a more specific title like Jumanji (1995).";
  }
  if (status === 503 && source === "movielens") {
    return "The full movie library is not available right now. Try Sample Movies.";
  }
  const text = formatDetail(detail);
  if (text) {
    return `Something went wrong.\n\n${text}`;
  }
  return "Something went wrong. Please try again in a moment.";
}

async function runSearch() {
  const title = titleInput.value.trim();
  const topK = clampTopK(topkInput.value);
  const source = getSelectedSource();

  hideResults();
  clearStatus();

  if (!title) {
    showStatus("Pop in a movie title above to get started.", "info");
    return;
  }

  const params = new URLSearchParams({ title, top_k: String(topK) });
  const apiUrl = getApiUrl();

  setLoadingState(true);
  showStatus("Finding seats that match your taste…", "loading");

  try {
    const response = await fetch(`${apiUrl}?${params.toString()}`);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      showStatus(
        errorMessageForResponse(response.status, source, data.detail),
        "error",
        response.status,
      );
      return;
    }

    clearStatus();

    if (becauseTitleEl && becauseLineEl) {
      becauseTitleEl.textContent = data.seed_title || "your pick";
      becauseLineEl.hidden = false;
    }

    seedTitleEl.textContent = data.seed_title || "Unknown title";
    seedMetaEl.textContent = `Ref. ${data.seed_movie_id ?? "—"}`;

    if (seedPosterEl) {
      setPosterHue(seedPosterEl, data.seed_title || "");
    }

    renderRecommendations(Array.isArray(data.recommendations) ? data.recommendations : [], source);
    resultsEl.hidden = false;
  } catch {
    showStatus(
      "We lost the signal for a moment. Refresh the page, or open this site from your running CineMatch server.",
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

document.querySelectorAll(".quick-pick").forEach((btn) => {
  btn.addEventListener("click", () => {
    const t = btn.getAttribute("data-title");
    if (t) {
      titleInput.value = t;
      titleInput.focus();
    }
  });
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

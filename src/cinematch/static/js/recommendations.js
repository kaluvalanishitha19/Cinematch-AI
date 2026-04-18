/**
 * CineMatch front-end — demo or MovieLens title search (same APIs as before).
 */
const DEMO_API = "/api/recommendations/by-title";
const MOVIELENS_API = "/api/movielens/recommendations/by-title";
const DEMO_MOVIE_API = "/api/movies";

const DATA_SOURCE_STORAGE_KEY = "cinematchDataSource";

const MSG_FULL_LIBRARY_FALLBACK =
  "The full library is unavailable right now. Showing quick demo recommendations instead.";

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
const seedGenresEl = document.getElementById("seed-genres");
const recListEl = document.getElementById("rec-list");
const quickPicksDemoEl = document.getElementById("quick-picks-demo");
const quickPicksMovielensEl = document.getElementById("quick-picks-movielens");
const quickPicksLabelEl = document.getElementById("quick-picks-label");
const resultsCatalogNoteEl = document.getElementById("results-catalog-note");

/** @type {boolean | null} */
let movielensAvailability = null;

/** When true, programmatic `data-source` changes skip the change handler. */
let suppressDataSourceEvent = false;

function getSelectedSource() {
  return dataSourceEl.value === "movielens" ? "movielens" : "demo";
}

function getApiUrl() {
  return getSelectedSource() === "movielens" ? MOVIELENS_API : DEMO_API;
}

function showEphemeralInfo(message) {
  showStatus(message, "info");
  window.setTimeout(() => {
    if (!statusEl.hidden && statusEl.dataset.kind === "info" && statusEl.textContent === message) {
      clearStatus();
    }
  }, 9000);
}

function applyFallbackToQuickDemo({ showNotice = false } = {}) {
  suppressDataSourceEvent = true;
  dataSourceEl.value = "demo";
  suppressDataSourceEvent = false;
  movielensAvailability = false;
  rememberDataSourcePreference();
  updateQuickPicks();
  if (showNotice) {
    showEphemeralInfo(MSG_FULL_LIBRARY_FALLBACK);
  }
}

function renderGenreChips(container, genreList) {
  if (!container) {
    return;
  }
  container.innerHTML = "";
  if (!genreList || !genreList.length) {
    container.hidden = true;
    return;
  }
  container.hidden = false;
  for (const g of genreList) {
    const chip = document.createElement("span");
    chip.className = "genre-chip";
    chip.textContent = g;
    container.appendChild(chip);
  }
}

function parseYearFromTitle(title) {
  const m = String(title || "").match(/\((\d{4})\)\s*$/);
  return m ? m[1] : null;
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
  if (resultsCatalogNoteEl) {
    resultsCatalogNoteEl.hidden = true;
    resultsCatalogNoteEl.textContent = "";
  }
  renderGenreChips(seedGenresEl, []);
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

function buildRecCardShell() {
  const li = document.createElement("li");
  li.className = "film-card film-card--rec ticket-card";

  const stripTop = document.createElement("div");
  stripTop.className = "film-card__strip film-card__strip--top";
  stripTop.setAttribute("aria-hidden", "true");

  const inner = document.createElement("div");
  inner.className = "film-card__inner";

  const popcorn = document.createElement("span");
  popcorn.className = "film-card__popcorn";
  popcorn.setAttribute("aria-hidden", "true");
  popcorn.textContent = "🍿";

  const body = document.createElement("div");
  body.className = "film-card__body";

  inner.appendChild(popcorn);
  inner.appendChild(body);

  const stripBot = document.createElement("div");
  stripBot.className = "film-card__strip film-card__strip--bottom";
  stripBot.setAttribute("aria-hidden", "true");

  li.appendChild(stripTop);
  li.appendChild(inner);
  li.appendChild(stripBot);

  return { li, body };
}

function appendTagline(body) {
  const tagline = document.createElement("p");
  tagline.className = "film-card__tagline";
  tagline.textContent = "Similar genres and content patterns";
  body.appendChild(tagline);
}

function renderDemoRecommendations(items) {
  for (const movie of items) {
    const { li, body } = buildRecCardShell();

    const title = document.createElement("h3");
    title.className = "film-card__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "film-card__meta";
    const year = movie.year != null ? String(movie.year) : "—";
    meta.textContent = `Year ${year} · Ref. ${movie.id ?? "—"}`;

    const genres = document.createElement("div");
    genres.className = "film-card__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    const blurb = document.createElement("p");
    blurb.className = "film-card__blurb";
    blurb.textContent = truncate(movie.overview, 140);

    body.appendChild(title);
    body.appendChild(meta);
    if (genres.childElementCount) {
      body.appendChild(genres);
    }
    body.appendChild(blurb);
    appendTagline(body);

    recListEl.appendChild(li);
  }
}

function renderMovielensRecommendations(items) {
  for (const movie of items) {
    const { li, body } = buildRecCardShell();

    const title = document.createElement("h3");
    title.className = "film-card__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "film-card__meta";
    const year = movie.year != null ? String(movie.year) : "—";
    meta.textContent = `Year ${year} · Ref. ${movie.movie_id ?? "—"}`;

    const ratings = document.createElement("div");
    ratings.className = "film-card__ratings";
    if (movie.mean_rating != null) {
      const badge = document.createElement("span");
      badge.className = "rating-badge";
      badge.textContent = `★ ${Number(movie.mean_rating).toFixed(2)}`;
      ratings.appendChild(badge);
      if (movie.rating_count) {
        const count = document.createElement("span");
        count.className = "rating-badge rating-badge--muted";
        count.textContent = `${Number(movie.rating_count).toLocaleString()} ratings`;
        ratings.appendChild(count);
      }
    }

    const genres = document.createElement("div");
    genres.className = "film-card__genres";
    for (const g of movie.genres || []) {
      const chip = document.createElement("span");
      chip.className = "genre-chip";
      chip.textContent = g;
      genres.appendChild(chip);
    }

    body.appendChild(title);
    body.appendChild(meta);
    if (ratings.childElementCount) {
      body.appendChild(ratings);
    }
    if (genres.childElementCount) {
      body.appendChild(genres);
    }
    appendTagline(body);

    recListEl.appendChild(li);
  }
}

function renderRecommendations(items, source, requestedTopK) {
  recListEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "rec-empty";
    if (source === "demo") {
      li.textContent =
        "Nothing close turned up in this short list. Try another title or a quick pick above.";
    } else {
      li.textContent =
        "No close matches for that title. Try another pick or a slightly different spelling.";
    }
    recListEl.appendChild(li);
    return;
  }

  if (source === "movielens") {
    renderMovielensRecommendations(items);
  } else {
    renderDemoRecommendations(items);
  }

  if (source === "demo" && requestedTopK > 0 && items.length < requestedTopK) {
    if (resultsCatalogNoteEl) {
      resultsCatalogNoteEl.hidden = false;
      resultsCatalogNoteEl.textContent =
        `Showing every match we found (${items.length}). This quick list is small by design.`;
    }
  }
}

function errorMessageForResponse(status, source, detail) {
  if (status === 404) {
    return "We couldn’t find that movie. Try a quick pick above or include the release year in your search.";
  }
  const text = formatDetail(detail);
  if (text) {
    return `Something went wrong.\n\n${text}`;
  }
  return "Something went wrong. Please try again in a moment.";
}

async function probeMovielensAvailability() {
  try {
    const response = await fetch(`${MOVIELENS_API}?title=___cinematch_probe___&top_k=1`);
    if (response.status === 503) {
      movielensAvailability = false;
      return false;
    }
    movielensAvailability = true;
    return true;
  } catch {
    movielensAvailability = null;
    return null;
  }
}

function updateQuickPicks() {
  const source = getSelectedSource();

  if (quickPicksDemoEl && quickPicksMovielensEl) {
    if (source === "movielens") {
      quickPicksDemoEl.hidden = true;
      quickPicksMovielensEl.hidden = false;
    } else {
      quickPicksDemoEl.hidden = false;
      quickPicksMovielensEl.hidden = true;
    }
  }

  if (quickPicksLabelEl) {
    quickPicksLabelEl.textContent =
      source === "movielens" ? "Try a classic night-out pick" : "Try a spotlight title";
  }
}

async function enrichDemoSeedMeta(movieId) {
  if (!movieId) {
    return;
  }
  try {
    const response = await fetch(`${DEMO_MOVIE_API}/${encodeURIComponent(movieId)}`);
    if (!response.ok) {
      return;
    }
    const movie = await response.json();
    const year = movie.year != null ? String(movie.year) : "—";
    seedMetaEl.textContent = `Year ${year} · Ref. ${movie.id}`;
    renderGenreChips(seedGenresEl, movie.genres || []);
  } catch {
    /* ignore */
  }
}

async function runSearch() {
  const title = titleInput.value.trim();
  const topK = clampTopK(topkInput.value);

  hideResults();
  clearStatus();

  if (!title) {
    showStatus("Pop in a movie title above to get started.", "info");
    return;
  }

  const params = new URLSearchParams({ title, top_k: String(topK) });
  let effectiveSource = getSelectedSource();
  let apiUrl = getApiUrl();

  setLoadingState(true);
  showStatus("Finding seats that match your taste…", "loading");

  try {
    let response = await fetch(`${apiUrl}?${params.toString()}`);
    let data = await response.json().catch(() => ({}));
    let recoveredOnQuickDemo = false;

    if (response.status === 503 && effectiveSource === "movielens") {
      applyFallbackToQuickDemo({ showNotice: false });
      effectiveSource = "demo";
      apiUrl = DEMO_API;
      response = await fetch(`${apiUrl}?${params.toString()}`);
      data = await response.json().catch(() => ({}));
      if (response.ok) {
        recoveredOnQuickDemo = true;
      }
    }

    if (!response.ok) {
      showStatus(
        errorMessageForResponse(response.status, effectiveSource, data.detail),
        "error",
        response.status,
      );
      return;
    }

    clearStatus();
    if (recoveredOnQuickDemo) {
      showEphemeralInfo(MSG_FULL_LIBRARY_FALLBACK);
    }

    if (becauseTitleEl && becauseLineEl) {
      becauseTitleEl.textContent = data.seed_title || "your pick";
      becauseLineEl.hidden = false;
    }

    seedTitleEl.textContent = data.seed_title || "Unknown title";
    const seedId = data.seed_movie_id ?? "";
    if (effectiveSource === "movielens") {
      const y = parseYearFromTitle(data.seed_title) || "—";
      seedMetaEl.textContent = `Year ${y} · Ref. ${seedId || "—"}`;
    } else {
      seedMetaEl.textContent = `Ref. ${seedId || "—"}`;
      enrichDemoSeedMeta(seedId);
    }

    renderRecommendations(
      Array.isArray(data.recommendations) ? data.recommendations : [],
      effectiveSource,
      topK,
    );
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

dataSourceEl.addEventListener("change", async () => {
  if (suppressDataSourceEvent) {
    return;
  }
  rememberDataSourcePreference();
  if (dataSourceEl.value === "movielens") {
    await probeMovielensAvailability();
    if (movielensAvailability === false) {
      applyFallbackToQuickDemo({ showNotice: true });
      return;
    }
  }
  updateQuickPicks();
});

void (async () => {
  restoreDataSourcePreference();
  await probeMovielensAvailability();
  if (dataSourceEl.value === "movielens" && movielensAvailability === false) {
    applyFallbackToQuickDemo({ showNotice: true });
  } else {
    updateQuickPicks();
  }
})();

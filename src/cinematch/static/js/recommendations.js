/**
 * CineMatch front-end — demo or MovieLens title search (same APIs as before).
 */
const DEMO_API = "/api/recommendations/by-title";
const MOVIELENS_API = "/api/movielens/recommendations/by-title";
const DEMO_MOVIE_API = "/api/movies";

const DATA_SOURCE_STORAGE_KEY = "cinematchDataSource";

const MSG_MOVIELENS_UNAVAILABLE =
  "The full movie library is currently unavailable. Try Sample Movies for now.";

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
const seedCanvasEl = document.querySelector(".poster--seed .poster__canvas");
const recListEl = document.getElementById("rec-list");
const libraryHintEl = document.getElementById("library-hint");
const movielensSetupNoteEl = document.getElementById("movielens-setup-note");
const quickPicksDemoEl = document.getElementById("quick-picks-demo");
const quickPicksMovielensEl = document.getElementById("quick-picks-movielens");
const quickPicksLabelEl = document.getElementById("quick-picks-label");
const resultsCatalogNoteEl = document.getElementById("results-catalog-note");

/** @type {boolean | null} */
let movielensAvailability = null;

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

function monogramFromTitle(title) {
  const words = String(title || "")
    .replace(/\(\d{4}\)/g, "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (!words.length) {
    return "CM";
  }
  const a = words[0].charAt(0).toUpperCase();
  const b = (words[1] || words[0].charAt(1) || "M").charAt(0).toUpperCase();
  return `${a}${b}`.replace(/[^A-Z0-9]/g, "") || "CM";
}

function fillPosterCanvas(canvas, title) {
  if (!canvas) {
    return;
  }
  const layer = canvas.querySelector(".poster__art-layer");
  if (!layer) {
    return;
  }
  layer.innerHTML = "";
  const mono = document.createElement("span");
  mono.className = "poster__mono";
  mono.textContent = monogramFromTitle(title);
  const deco = document.createElement("span");
  deco.className = "poster__deco";
  deco.textContent = "🎬  🍿  🎫";
  layer.appendChild(mono);
  layer.appendChild(deco);
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

function buildPosterShell(movie) {
  const li = document.createElement("li");
  li.className = "poster";

  const glow = document.createElement("div");
  glow.className = "poster__glow";
  glow.setAttribute("aria-hidden", "true");

  const frame = document.createElement("div");
  frame.className = "poster__frame";

  const canvas = document.createElement("div");
  canvas.className = "poster__canvas";
  const artLayer = document.createElement("div");
  artLayer.className = "poster__art-layer";
  artLayer.setAttribute("aria-hidden", "true");
  canvas.appendChild(artLayer);

  const body = document.createElement("div");
  body.className = "poster__body";

  frame.appendChild(canvas);
  frame.appendChild(body);
  li.appendChild(glow);
  li.appendChild(frame);

  setPosterHue(li, movie.title);
  fillPosterCanvas(canvas, movie.title);

  return { li, canvas, body };
}

function renderDemoRecommendations(items) {
  for (const movie of items) {
    const { li, body } = buildPosterShell(movie);

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
    synopsis.textContent = truncate(movie.overview, 130);

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
    const { li, body } = buildPosterShell(movie);

    const title = document.createElement("h3");
    title.className = "poster__title";
    title.textContent = movie.title || "Untitled";

    const meta = document.createElement("p");
    meta.className = "poster__meta";
    const year = movie.year != null ? String(movie.year) : "—";
    let line = `${year} · Ref. ${movie.movie_id ?? "—"}`;
    if (movie.mean_rating != null && movie.rating_count) {
      line += ` · ★ ${Number(movie.mean_rating).toFixed(2)} (${Number(movie.rating_count).toLocaleString()} ratings)`;
    } else if (movie.mean_rating != null) {
      line += ` · ★ ${Number(movie.mean_rating).toFixed(2)}`;
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
      "Stylized stand-in art only—no real poster images. Rankings still use title, genres, year, and rating signals.";

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

function renderRecommendations(items, source, requestedTopK) {
  recListEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "rec-empty";
    if (source === "demo") {
      li.textContent =
        "No neighbors in this tiny reel—there are only a few films in Sample Movies. Switch to MovieLens Library for full lists, or try another title.";
    } else {
      li.textContent =
        "No close matches returned for that title. Try another pick or a slightly different spelling.";
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
        `Showing all ${items.length} similar match${items.length === 1 ? "" : "es"} in this small demo. For longer lists, try the full library when it is available.`;
    }
  }
}

function errorMessageForResponse(status, source, detail) {
  if (status === 404) {
    return "We couldn’t find that movie. Try a quick pick above, or—for MovieLens—a specific title like Jumanji (1995).";
  }
  if (status === 503 && source === "movielens") {
    return MSG_MOVIELENS_UNAVAILABLE;
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

function updateLibraryChrome() {
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
      source === "movielens" ? "Quick picks (classic 1995 hits)" : "Quick picks (titles in the sample CSV)";
  }

  if (libraryHintEl) {
    if (source === "movielens") {
      libraryHintEl.innerHTML =
        "<strong>MovieLens Library</strong> is the large catalog when the host has connected it. Cards use stylized art only—no real movie poster images.";
    } else {
      libraryHintEl.innerHTML =
        "<strong>Sample Movies</strong> is a <em>tiny</em> built-in demo (six titles). Lists stay short by design. For thousands of films, choose <strong>MovieLens Library (recommended)</strong> under Fine-tune your night when the full library is available.";
    }
  }

  if (movielensSetupNoteEl) {
    if (source === "movielens" && movielensAvailability === false) {
      movielensSetupNoteEl.hidden = false;
    } else {
      movielensSetupNoteEl.hidden = true;
    }
  }
}

async function refreshMovielensAvailabilityUi() {
  if (getSelectedSource() === "movielens") {
    await probeMovielensAvailability();
  }
  updateLibraryChrome();
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
    const genres = Array.isArray(movie.genres) && movie.genres.length ? movie.genres.join(" · ") : "";
    seedMetaEl.textContent = genres ? `${year} · ${genres} · Ref. ${movie.id}` : `${year} · Ref. ${movie.id}`;
  } catch {
    /* ignore */
  }
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

  if (source === "movielens" && movielensAvailability === false) {
    showStatus(MSG_MOVIELENS_UNAVAILABLE, "info");
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
    const seedId = data.seed_movie_id ?? "";
    if (source === "movielens") {
      const y = parseYearFromTitle(data.seed_title) || "—";
      seedMetaEl.textContent = `${y} · Ref. ${seedId || "—"}`;
    } else {
      seedMetaEl.textContent = `Ref. ${seedId || "—"}`;
      enrichDemoSeedMeta(seedId);
    }

    if (seedPosterEl) {
      setPosterHue(seedPosterEl, data.seed_title || "");
    }
    fillPosterCanvas(seedCanvasEl, data.seed_title || "");

    renderRecommendations(Array.isArray(data.recommendations) ? data.recommendations : [], source, topK);
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

dataSourceEl.addEventListener("change", () => {
  rememberDataSourcePreference();
  void refreshMovielensAvailabilityUi();
});

restoreDataSourcePreference();
void refreshMovielensAvailabilityUi();

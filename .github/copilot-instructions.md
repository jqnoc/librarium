# Ashinami — Agent Directives

These directives apply whenever working on the Ashinami project.
They ensure consistency, prevent regressions, and keep the
single-file architecture maintainable.

---

## 1. Project Overview

Ashinami is a **local Flask web application** for tracking personal
book reading statistics. It is a monolithic single-file app (`app.py`,
~4 500+ lines) with raw SQLite queries, Jinja2 templates, vanilla JS,
and Chart.js for charts. There is **no test suite** — all verification
is manual.

### Key facts

| Aspect | Value |
|--------|-------|
| Entry point | `app.py` |
| Database | SQLite at `data/ashinami.db` (WAL mode) |
| Python | 3.12+ |
| Dependencies | Flask ≥ 3.0, Pillow ≥ 10.0, pillow-heif ≥ 0.16 |
| Port | 5000 (localhost only) |
| Startup | `python app.py` or `run-ashinami.bat` |

---

## 2. Architecture

### 2.1 Monolithic structure

Everything lives in `app.py`: database helpers, migrations, template
filters, route handlers, business logic, and the startup block. There
are no blueprints, no ORM, and no separate model files.

### 2.2 Database

- **11 tables**: `books`, `readings`, `sessions`, `periods`, `ratings`,
  `authors`, `series`, `book_series`, `sources`, `libraries`
  (plus a SQLite-internal `sqlite_sequence`).
- All queries are **raw SQL** via `sqlite3`. There is no ORM.
- `get_db()` returns a per-request `sqlite3.Connection` stored in
  Flask's `g` object. Row factory is `sqlite3.Row`.
- Primary keys: `books.id` uses UUID strings; most other tables use
  INTEGER autoincrement.

### 2.3 Migrations

Migrations are plain functions (`migrate_add_*()`) called sequentially
in the `if __name__ == "__main__"` block. Each migration is idempotent
(checks for column/table existence before acting). Current migrations:

1. `migrate_add_readings` — readings table
2. `migrate_add_authors` — authors table
3. `migrate_add_cover_color` — cover_color column
4. `migrate_add_cover_palette` — cover_palette column
5. `migrate_add_cover_hash` — cover_hash column
6. `migrate_add_photo_hash` — photo_hash column on authors
7. `migrate_add_subtitle` — subtitle column on books
8. `migrate_add_libraries` — libraries table + library_id FK columns
9. `migrate_add_series` — series table + series columns
10. `migrate_book_series_m2m` — book_series junction table (many-to-many)
11. `migrate_add_editions` — work_id / is_primary_edition columns
12. `migrate_add_format` — format, binding, audio_format columns on books
13. `migrate_add_total_time` — total_time_seconds on books, progress_pct on sessions and periods

When adding a new migration:

- [ ] Make it **idempotent** — guard with `PRAGMA table_info` or
  `SELECT name FROM sqlite_master`
- [ ] Add the call in the `if __name__ == "__main__"` block **after**
  all existing migrations
- [ ] Test on a fresh DB *and* an already-migrated DB

### 2.4 Template filters

Four Jinja2 template filters are registered:

| Filter | Purpose |
|--------|---------|
| `format_status` | Status string → display label |
| `format_authors` | Comma-separated author list |
| `date_ddmmyyyy` | ISO date → dd/mm/yyyy |
| `source_type_label` | Source type key → display label |

### 2.5 Status system

Five book statuses:

| Status | CSS class | Colour variable |
|--------|-----------|-----------------|
| `reading` | `.badge.status-reading` | `--an-reading` (#3B82F6) |
| `finished` | `.badge.status-finished` | `--an-finished` (#10B981) |
| `not-started` | `.badge.status-not-started` | `--an-not-started` (#8B5CF6) |
| `abandoned` | `.badge.status-abandoned` | `--an-abandoned` (#DC2626) |
| `draft` | `.badge.status-draft` | `--an-draft` (#6B7280) |

Canonical sort order is defined in `STATUS_ORDER` (line ~1132).

When adding a new status:

- [ ] Add to `STATUS_ORDER` dict
- [ ] Add to `status_labels_map` dict (line ~1491)
- [ ] Add CSS class and colour variable in `static/style.css`
- [ ] Add `<option>` in `new_book.html`, `edit_metadata.html`, and the
  filter dropdown in `index.html`
- [ ] Add translations in `static/i18n.js` (both EN and ES)

### 2.6 Rating system

39 dimensions across 7 groups defined in `RATING_DIMENSIONS`:

1. **Emotional Impact** (6): heartfelt, tear, inspiring, melancholy, nostalgia, cathartic
2. **Story & Plot** (6): plot_quality, predictability, pacing, plot_twists, worldbuilding, character_arc
3. **Writing & Style** (6): writing_quality, vocabulary_gain, dialogue, voice, symbolism, editorial_quality
4. **Genre-Specific** (6): suspense, thrill, humor, romance, mystery, horror
5. **Engagement** (4): addiction, afterglow, rereadability, originality
6. **Intellectual** (5): thought_provoking, complexity, historical_cultural_value, argumentation, clarity
7. **Non-Fiction** (6): research_depth, accuracy, evidence, practicality, objectivity, relevance

Overall average is **grouped**: average of each non-empty group's
average (via `_calc_avg_rating()`). When adding a dimension, add it to
the appropriate group in `RATING_DIMENSIONS`.

---

## 3. Frontend Conventions

### 3.1 CSS palettes

Six color palettes, selected via `data-palette` attribute on `<html>`:

| Palette key | Name | Default? |
|------------|------|----------|
| *(root)* | Orange | — |
| `green` | Mori | — |
| `hone` | Hone | **Yes (default)** |
| `kawara` | Kawara | — |
| `umi` | Umi | — |
| `hinode` | Hinode | — |

Each palette overrides CSS custom properties (prefixed `--an-`).
Chart colours are also palette-aware (`--an-chart-*` variables).

### 3.2 Internationalisation (i18n)

- Two languages: **English (en)** and **Spanish (es)**.
- Translations live in `static/i18n.js`.
- HTML elements use `data-i18n="key"` attributes; JS applies
  translations on load and on language switch.
- Language preference is persisted in `localStorage`.

When adding UI text:

- [ ] Add a translation key to **both** `en` and `es` objects in
  `static/i18n.js`
- [ ] Use `data-i18n="your_key"` on the element (or set text via JS
  using the i18n lookup)

### 3.3 Charts

- Chart.js 4.4.1 loaded via CDN from `base.html`.
- `chartjs-adapter-date-fns` used for time-axis charts (status timeline).
- Chart colours read from CSS custom properties via
  `getComputedStyle(document.documentElement)`.

### 3.4 View modes

The library index (`/`) supports three view modes: **card**, **cover**,
and **list** — toggled by the user and stored in a cookie.

---

## 4. Route Map

### Pages

| URL | Method | Purpose |
|-----|--------|---------|
| `/` | GET | Library index (card / cover / list views) |
| `/book/new` | GET, POST | Add a new book |
| `/book/<id>` | GET | Book detail (sessions, periods, ratings, editions) |
| `/book/<id>/edit` | GET, POST | Edit book metadata |
| `/book/<id>/delete` | POST | Soft-delete a book (undo available) |
| `/book/undo-delete` | POST | Undo last soft-delete |
| `/book/<id>/reread` | POST | Start a new reading of the same book |
| `/book/<id>/reading/<rid>/delete` | POST | Delete a reading |
| `/book/<id>/sessions/add` | POST | Add a reading session |
| `/book/<id>/sessions/<idx>/edit` | POST | Edit a session |
| `/book/<id>/sessions/<idx>/delete` | POST | Delete a session |
| `/book/<id>/periods/add` | POST | Add a reading period |
| `/book/<id>/periods/<idx>/edit` | POST | Edit a period |
| `/book/<id>/periods/<idx>/delete` | POST | Delete a period |
| `/book/<id>/ratings` | POST | Save ratings |
| `/book/<id>/link-edition` | POST | Link two books as editions of the same work |
| `/book/<id>/unlink-edition` | POST | Unlink an edition |
| `/book/<id>/set-primary-edition` | POST | Set this edition as primary |
| `/stats` | GET | Global statistics dashboard |
| `/stats/year/<year>` | GET | Yearly stats with Gantt charts |
| `/stats/year/<year>/books` | GET | Books finished in a specific year |
| `/activity` | GET | Activity dashboard |
| `/authors` | GET | Authors list |
| `/authors/<name>` | GET | Author detail page |
| `/authors/<name>/edit` | GET, POST | Edit author info and photo |
| `/author_photo/<name>` | GET | Serve author photo from DB |
| `/series` | GET | Series list |
| `/series/<id>` | GET | Series detail |
| `/series/<id>/rename` | POST | Rename a series |
| `/series/<id>/delete` | POST | Delete a series |
| `/sources` | GET | Source management |
| `/sources/add` | POST | Add a source |
| `/sources/<id>/edit` | POST | Edit a source |
| `/sources/<id>/delete` | POST | Delete a source |
| `/library/switch` | POST | Switch active library |
| `/library/create` | POST | Create a new library |
| `/library/<id>/rename` | POST | Rename a library |
| `/library/<id>/delete` | POST | Delete a library |
| `/cover/<id>` | GET | Serve book cover image from DB |

### API endpoints

| URL | Method | Purpose |
|-----|--------|---------|
| `/api/cumulative_pages` | GET | Cumulative pages data for charts |
| `/api/cumulative_pages_per_book` | GET | Per-book cumulative pages |
| `/api/status_timeline` | GET | Status-over-time data for stacked area chart |

---

## 5. Database Schema Quick Reference

```
books       (id TEXT PK, title, subtitle, author, status, pages, isbn,
             publisher, pub_year, language, original_language, source_id,
             date_added, date_started, date_finished, genres, notes,
             cover_blob, cover_mime, cover_color, cover_palette,
             cover_hash, library_id, work_id, is_primary_edition,
             format, binding, audio_format, total_time_seconds)

readings    (id INTEGER PK, book_id FK, reading_number, status,
             date_started, date_finished)

sessions    (id INTEGER PK, reading_id FK, book_id FK, date, page_start,
             page_end, hours, minutes, seconds, progress_pct)

periods     (id INTEGER PK, reading_id FK, book_id FK, date_from,
             date_to, pages, notes, progress_pct)

ratings     (id INTEGER PK, book_id FK, dimension_key, value)

authors     (id INTEGER PK, name UNIQUE, bio, photo_blob, photo_mime,
             photo_hash, library_id)

series      (id INTEGER PK, name, library_id)

book_series (id INTEGER PK, book_id FK, series_id FK, position)

sources     (id INTEGER PK, name, type, city, country, url, notes,
             library_id)

libraries   (id INTEGER PK, name UNIQUE)
```

---

## 6. Multi-Library, Multi-Edition, and Re-Read Systems

### Multi-library

- The active library ID is stored in `session["library_id"]`.
- Helper `_get_lib_id()` (not currently in the codebase — the index route
  reads `session.get("library_id")` directly) determines the active library.
- Most queries filter by `library_id`.

### Multi-edition (work system)

- `books.work_id` groups editions of the same work. If NULL, the book
  stands alone.
- `books.is_primary_edition` marks the canonical edition displayed in
  listings.
- Routes: `/book/<id>/link-edition`, `/book/<id>/unlink-edition`,
  `/book/<id>/set-primary-edition`.

### Re-reads

- A book can have multiple `readings` rows.
- Each reading has its own `sessions` and `periods`.
- `reading_number` tracks the sequence (1, 2, 3…).
- Route: `/book/<id>/reread` creates a new reading.

---

## 7. Helper Functions

Key helper patterns in `app.py`:

| Function | Purpose |
|----------|---------|
| `get_db()` | Per-request DB connection |
| `_get_current_reading_id()` | Latest reading ID for a book |
| `_load_ratings()` / `_save_ratings()` | Rating CRUD |
| `_calc_avg_rating()` | Grouped average |
| `_compute_status_timeline()` | Reconstruct status history from dates |
| `validate_and_restore_db()` | Integrity check + backup restore |
| `backup_database()` | Daily backup with pruning |
| `sanitize_html()` | Allowlist-based HTML sanitiser for notes |

---

## 8. Verification After Changes

There is **no automated test suite**. After any change, verify manually:

```
1. python app.py                       # App starts without errors
2. Open http://127.0.0.1:5000          # Library page loads
3. Click through the affected feature  # Verify behaviour
4. Check browser console for JS errors # No console errors
```

### Subsystem-specific checks

| Change area | What to verify |
|-------------|----------------|
| New status | Dropdown in new_book, edit_metadata, index filter; badge colour; i18n labels; `STATUS_ORDER`; `status_labels_map` |
| New rating dimension | Appears in book detail ratings form; average calculation still correct |
| New migration | Runs on fresh DB and already-migrated DB without errors |
| New route | URL resolves, template renders, form submissions work |
| CSS palette change | All 6 palettes still render correctly; chart colours update |
| i18n change | Both EN and ES display correct text; no missing keys in console |
| Chart change | Chart renders with data; responsive on narrow window |

---

## 9. File & Module Conventions

| Path | Purpose |
|------|---------|
| `app.py` | Entire Flask application |
| `requirements.txt` | Python dependencies |
| `run-ashinami.bat` | Windows launcher (starts app + opens browser) |
| `static/style.css` | Stylesheet (palettes, layout, components) |
| `static/i18n.js` | EN/ES translations |
| `templates/base.html` | Base layout (navbar, palette switcher, Chart.js CDN) |
| `templates/index.html` | Library page (card/cover/list views, filters) |
| `templates/book_detail.html` | Book detail (sessions, periods, ratings, editions) |
| `templates/edit_metadata.html` | Edit book metadata form |
| `templates/new_book.html` | Add new book form |
| `templates/stats.html` | Global statistics dashboard |
| `templates/stats_year.html` | Yearly stats with Gantt charts |
| `templates/stats_year_books.html` | Books finished in a year |
| `templates/activity.html` | Activity dashboard |
| `templates/authors.html` | Authors list |
| `templates/author_detail.html` | Author detail |
| `templates/edit_author.html` | Edit author form |
| `templates/sources.html` | Source management |
| `data/ashinami.db` | SQLite database (gitignored) |
| `data/backups/` | Automatic daily backups |

---

## 10. Commit Messages

**MANDATORY — NEVER SKIP.** Every response that modifies code or files
(feature, fix, refactor, etc.) **must** end with a suggested commit
message inside a fenced code block. This is required regardless of the
size of the change — a one-line bug fix needs a commit message just as
much as a multi-file feature. If you forget, the user cannot commit
their work. Include it in your **final** message of the task, right
before yielding back to the user.

### Format

```
type(scope): lowercase imperative summary of the change

* bullet describing a specific change
* another bullet
…
```

### Rules

| Element | Rule |
|---------|------|
| **Type** | `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, etc. |
| **Scope** | Optional, in parentheses after the type: `feat(stats):`. When no meaningful scope, wrap the type instead: `(refactor):`. Multiple scopes comma-separated: `feat(css,i18n):`. |
| **Subject line** | Lowercase after the colon, imperative mood, no trailing period. |
| **Blank line** | Always separate the subject from the body. |
| **Body** | Bullet list using `*` (not `-`). Each bullet is lowercase imperative, no trailing period. Use backticks for code identifiers and `→` for renames/moves. Each bullet must be a single line — do **not** wrap or break a bullet across multiple lines. |
| **Optional intro** | A short paragraph before the bullets is allowed for larger features to give context. |

### Example

```
feat(stats): add status timeline stacked area chart

* add `_compute_status_timeline()` helper to reconstruct status history
* add `/api/status_timeline` API endpoint
* add stacked area chart to `stats.html` with absolute/relative toggle
* add i18n keys for timeline labels in EN and ES
```

---

## 11. Known Issues & Technical Debt

- **Monolithic `app.py`**: ~4 500+ lines in a single file. No plans to
  refactor, but be aware of line-number drift when making changes.
- **No automated tests**: All verification is manual.
- **`app.secret_key`**: Hardcoded as `"ashinami-local-dev-key"` — acceptable
  for a localhost-only personal app but not production-safe.
- **Cover extraction**: `cover_color` and `cover_palette` are computed on
  upload; changing the algorithm does not retroactively update existing books.
- **Status timeline**: `_compute_status_timeline()` reconstructs history
  from reading/session/period dates — it does not use a separate audit log
  table, so historical accuracy depends on those dates being correct.

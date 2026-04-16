# Librarium — Agent Directives

These directives apply whenever working on the Librarium project.
They ensure consistency, prevent regressions, and keep the
single-file architecture maintainable.

---

## 1. Project Overview

Librarium is a **self-contained Electron desktop application** for tracking
personal book reading statistics. The backend is a monolithic single-file
Flask app (`app.py`, ~5 000+ lines) with raw SQLite queries, Jinja2
templates, vanilla JS, and Chart.js for charts. Electron spawns the Flask
server as a child process and displays it in a native window. There is
**no test suite** — all verification is manual.

### Key facts

| Aspect | Value |
|--------|-------|
| Entry point (Electron) | `main.js` |
| Entry point (Backend) | `app.py` |
| Version | Defined in `APP_VERSION` (`app.py`) and `package.json` |
| Database | SQLite per-user DBs in AppData (WAL mode) |
| Python | 3.12+ |
| Node.js | 18+ |
| Python deps | Flask ≥ 3.0, Pillow ≥ 10.0, pillow-heif ≥ 0.16, dropbox ≥ 12.0 |
| Port | Dynamic (free port at startup) |
| Startup | `npm start` or `run-librarium.bat` |

---

## 2. Architecture

### 2.1 Electron shell

`main.js` is the Electron main process. It:

1. Finds a free TCP port (`findFreePort()` via `net.createServer`).
2. Spawns `python app.py` with `LIBRARIUM_PORT` and `LIBRARIUM_ELECTRON=1`
   environment variables.
3. Polls the port until Flask accepts connections.
4. Opens a `BrowserWindow` pointing at `http://127.0.0.1:<port>`.
5. Kills the Flask child process on quit.

`preload.js` exposes `window.librarium.isElectron` to the renderer
(sandboxed, `contextIsolation: true`).

### 2.2 Monolithic Flask backend

Everything lives in `app.py`: database helpers, migrations, template
filters, route handlers, business logic, and the startup block. There
are no blueprints, no ORM, and no separate model files.

### 2.3 Database

- **11 tables**: `books`, `readings`, `sessions`, `periods`, `ratings`,
  `authors`, `series`, `book_series`, `sources`, `libraries`
  (plus a SQLite-internal `sqlite_sequence`).
- All queries are **raw SQL** via `sqlite3`. There is no ORM.
- `get_db()` returns a per-request `sqlite3.Connection` stored in
  Flask's `g` object. Row factory is `sqlite3.Row`.
- Primary keys: `books.id` uses UUID strings; most other tables use
  INTEGER autoincrement.

### 2.4 Dropbox Cloud Storage

Dropbox is **mandatory**. The app requires Dropbox authentication before
any user interaction. Data is stored in `Apps/LibrariumApp/` (app-folder
access type).

#### Auth flow
- OAuth2 PKCE (no client secret) → system browser → callback to
  `http://127.0.0.1:48721/auth/callback`.
- Refresh token + access token persisted in `DATA_DIR/auth.json`.
- `check_user_selected()` middleware redirects to `/auth/login` if not
  authenticated.

#### Sync strategy
- **Startup**: download all `.db` files and `users.json` from Dropbox.
- **Periodic**: every 5 minutes, upload modified DBs (content-hash
  change detection via `_file_content_hash()`).
- **Shutdown**: Electron calls `/api/shutdown-backup` and waits up to
  30 s for Flask to finish backup + upload before killing the process.
- WAL checkpoint (`PRAGMA wal_checkpoint(TRUNCATE)`) before every upload.

#### Key helpers

| Function | Purpose |
|----------|---------|
| `_load_auth()` / `_save_auth()` / `_clear_auth()` | Auth token CRUD in `auth.json` |
| `get_dropbox_client()` | Thread-safe singleton Dropbox client (auto-refreshes) |
| `_dbx_download()` / `_dbx_upload()` | File transfer to/from Dropbox |
| `_dbx_file_exists()` / `_dbx_list_folder()` | Remote listing |
| `sync_db_to_dropbox()` | Upload one user DB if changed |
| `sync_users_json_to_dropbox()` | Upload `users.json` |
| `_download_all_from_dropbox()` | Startup bulk download |
| `_upload_all_to_dropbox()` | Shutdown bulk upload |
| `_start_periodic_sync()` | Start background sync thread |

#### Dropbox folder layout
```
Apps/LibrariumApp/
  users.json
  <username>.db
  backups/
    <username>_YYYYMMDD_HHMMSS.db
```

### 2.5 Migrations

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
14. `migrate_add_period_duration` — duration_seconds on periods
15. `migrate_add_cover_thumb` — cover_thumb BLOB on books (with backfill)
16. `migrate_add_photo_thumb` — photo_thumb BLOB on authors (with backfill)
17. `migrate_shared_authors` — make authors global (remove library_id scoping)
18. `migrate_shared_sources` — make sources global (remove library_id scoping)
19. `migrate_add_author_gender` — gender column on authors
20. `migrate_add_tags` — tags column on books
21. `migrate_normalize_genres` — normalise genre strings
22. `migrate_merge_genres_into_tags` — merge genres into the tags column

When adding a new migration:

- [ ] Make it **idempotent** — guard with `PRAGMA table_info` or
  `SELECT name FROM sqlite_master`
- [ ] Add the call in the `if __name__ == "__main__"` block **after**
  all existing migrations
- [ ] Test on a fresh DB *and* an already-migrated DB

### 2.6 Template filters

Five Jinja2 template filters are registered:

| Filter | Purpose |
|--------|--------|
| `format_status` | Status string → display label |
| `format_authors` | Comma-separated author list |
| `date_ddmmyyyy` | ISO date → dd/mm/yyyy |
| `display_date` | Wrap date in `<span data-date>` for client-side i18n formatting |
| `source_type_label` | Source type key → display label |

### 2.7 Status system

Five book statuses:

| Status | CSS class | Colour variable |
|--------|-----------|-----------------|
| `reading` | `.badge.status-reading` | `--lb-reading` (#3B82F6) |
| `finished` | `.badge.status-finished` | `--lb-finished` (#10B981) |
| `not-started` | `.badge.status-not-started` | `--lb-not-started` (#8B5CF6) |
| `abandoned` | `.badge.status-abandoned` | `--lb-abandoned` (#DC2626) |
| `draft` | `.badge.status-draft` | `--lb-draft` (#6B7280) |

Canonical sort order is defined in `STATUS_ORDER` (line ~2045).

When adding a new status:

- [ ] Add to `STATUS_ORDER` dict
- [ ] Add to `status_labels_map` dict (line ~2500)
- [ ] Add CSS class and colour variable in `static/style.css`
- [ ] Add `<option>` in `new_book.html`, `edit_metadata.html`, and the
  filter dropdown in `index.html`
- [ ] Add translations in `static/i18n.js` (both EN and ES)

### 2.8 Rating system

51 dimensions across 9 groups defined in `RATING_DIMENSIONS`:

1. **Emotional Impact** (6): heartfelt, tear, inspiring, melancholy, nostalgia, cathartic
2. **Story & Plot** (6): plot_quality, predictability, pacing, plot_twists, worldbuilding, character_arc
3. **Writing & Style** (6): writing_quality, vocabulary_gain, dialogue, voice, symbolism, editorial_quality
4. **Genre-Specific** (6): suspense, thrill, humor, romance, mystery, horror
5. **Engagement** (4): addiction, afterglow, rereadability, originality
6. **Intellectual** (5): thought_provoking, complexity, historical_cultural_value, argumentation, clarity
7. **Non-Fiction** (6): research_depth, accuracy, evidence, practicality, objectivity, relevance
8. **Visual Art** (6): art_quality, character_design, color_inking, background_art, cover_art, visual_consistency
9. **Sequential Narrative** (6): panel_layout, visual_storytelling, action_choreography, expressiveness, text_integration, splash_pages

Overall average is **grouped**: average of each non-empty group's
average (via `_calc_avg_rating()`). When adding a dimension, add it to
the appropriate group in `RATING_DIMENSIONS`.

---

## 3. Frontend Conventions

### 3.1 CSS theme

The app uses a single colour theme defined in `:root` CSS custom
properties (prefixed `--lb-`). There is no palette switching system.
Chart colours are also theme-aware (`--lb-chart-*` variables).

Key variables: `--lb-gold` (#EC8F8D), `--lb-deep-orange` (#537D96),
`--lb-orange` (#44A194), `--lb-accent` (#EC8F8D), `--lb-dark` (#2a4a5a).

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
| `/author_photo_thumb/<name>` | GET | Serve author photo thumbnail from DB |
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
| `/cover_thumb/<id>` | GET | Serve book cover thumbnail from DB |
| `/backup/create` | POST | Trigger a manual backup |
| `/users` | GET | User selection / creation screen |
| `/users/create` | POST | Create a new user |
| `/users/switch` | POST | Switch to a different user |
| `/users/update-backup-dir` | POST | Update a user's custom backup directory |
| `/auth/login` | GET | Dropbox login page |
| `/auth/start` | GET | Initiate Dropbox OAuth2 PKCE flow |
| `/auth/callback` | GET | OAuth2 callback (receives auth code) |
| `/auth/logout` | POST | Disconnect Dropbox and clear auth tokens |
| `/auth/status` | GET | JSON endpoint returning auth status |

### API endpoints

| URL | Method | Purpose |
|-----|--------|--------|
| `/api/cumulative_pages` | GET | Cumulative pages data for charts |
| `/api/cumulative_pages_per_book` | GET | Per-book cumulative pages |
| `/api/status_timeline` | GET | Status-over-time data for stacked area chart |
| `/api/isbn_lookup` | GET | Look up book metadata by ISBN via Open Library |
| `/api/shutdown-backup` | POST | Trigger a backup before shutdown |

---

## 5. Database Schema Quick Reference

```
books       (id TEXT PK, name, subtitle, author, slug, language,
             original_title, original_language, original_publication_date,
             publication_date, isbn, pages, starting_page, publisher,
             genre, summary, translator, illustrator, editor,
             prologue_author, status, source_type, source_id,
             purchase_date, purchase_price, borrowed_start, borrowed_end,
             has_cover, cover BLOB, is_gift, cover_color, cover_palette,
             cover_hash, cover_thumb BLOB, library_id FK, subtitle,
             series_id FK, series_index, work_id, is_primary_edition,
             format, binding, audio_format, total_time_seconds, tags)

readings    (id INTEGER PK, book_id FK, reading_number, status, notes)

sessions    (id INTEGER PK, book_id FK, date, pages, duration_seconds,
             reading_id FK, progress_pct)

periods     (id INTEGER PK, book_id FK, start_date, end_date, pages,
             note, reading_id FK, progress_pct, duration_seconds)

ratings     (book_id FK, dimension_key, value,
             PRIMARY KEY (book_id, dimension_key))

authors     (name TEXT PK, photo BLOB, has_photo, birth_date,
             birth_place, death_date, death_place, biography,
             photo_hash, photo_thumb BLOB, gender)

series      (id INTEGER PK, name, library_id FK,
             UNIQUE(name, library_id))

book_series (book_id FK, series_id FK, series_index,
             PRIMARY KEY (book_id, series_id))

sources     (id TEXT PK, type, name, short_name, location, url, notes)

libraries   (id INTEGER PK, name, slug UNIQUE)
```

---

## 6. Multi-Library, Multi-Edition, and Re-Read Systems

### Multi-library

- Selected library IDs are stored in a cookie (`librarium_library`,
  comma-separated).
- Helper `_get_selected_library_ids()` parses the cookie and returns a
  list of IDs; an empty list means "all libraries".
- Helper `_lib_filter(lib_ids, col)` returns a `(sql, params)` tuple
  for WHERE clauses.
- Most queries filter by `library_id` using `_lib_filter()`.

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
| `_get_selected_library_ids()` | Parse library cookie → list of IDs |
| `_lib_filter()` | Build SQL WHERE clause for library filtering |
| `_get_current_reading_id()` | Latest reading ID for a book |
| `_load_ratings()` / `_save_ratings()` | Rating CRUD |
| `_calc_avg_rating()` | Grouped average |
| `_compute_status_timeline()` | Reconstruct status history from dates |
| `_load_users()` / `_save_users()` | Read / write `users.json` |
| `_set_active_user_db()` | Switch global `DB_PATH` and `BACKUP_DIR` for a user |
| `_get_user_db_path()` | Resolve DB file path for a username |
| `_run_all_migrations()` | Execute all migrations sequentially |
| `validate_and_restore_db()` | Integrity check + backup restore |
| `backup_database()` | Daily backup with pruning |
| `sanitize_html()` | Allowlist-based HTML sanitiser for notes |

---

## 8. Verification After Changes

There is **no automated test suite**. After any change, verify manually:

```
1. npm start                           # App starts in Electron window
2. Click through the affected feature  # Verify behaviour
3. Check DevTools console for errors   # No console errors
```

Alternatively, for backend-only changes you can still run Flask
directly: `python app.py` → open `http://127.0.0.1:5000`.

### Subsystem-specific checks

| Change area | What to verify |
|-------------|----------------|
| New status | Dropdown in new_book, edit_metadata, index filter; badge colour; i18n labels; `STATUS_ORDER`; `status_labels_map` |
| New rating dimension | Appears in book detail ratings form; average calculation still correct |
| New migration | Runs on fresh DB and already-migrated DB without errors |
| New route | URL resolves, template renders, form submissions work |
| CSS palette change | Theme colours render correctly; chart colours update |
| i18n change | Both EN and ES display correct text; no missing keys in console |
| Chart change | Chart renders with data; responsive on narrow window |

---

## 9. File & Module Conventions

| Path | Purpose |
|------|---------|
| `main.js` | Electron main process (spawns Flask, manages window) |
| `preload.js` | Electron preload script (sandboxed renderer bridge) |
| `package.json` | Node.js manifest (Electron dep, version, build config) |
| `app.py` | Entire Flask application |
| `requirements.txt` | Python dependencies |
| `run-librarium.bat` | Windows launcher (`npm start`) |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `static/style.css` | Stylesheet (layout, components) |
| `static/i18n.js` | EN/ES translations |
| `templates/base.html` | Base layout (navbar, Chart.js CDN) |
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
| `templates/series.html` | Series list |
| `templates/series_detail.html` | Series detail |
| `templates/users.html` | User selection / creation |
| `templates/auth_login.html` | Dropbox login / connect page |
| `templates/auth_waiting.html` | OAuth polling page (shown in Electron while user authorizes in browser) |
| `templates/auth_success.html` | OAuth callback success page |

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

## 11. Versioning & Changelog

The project uses semantic versioning. Development happens on the `dev`
branch; releases are merged to `main` and tagged. Version bumps happen
**only when the user explicitly requests a release** — never
automatically.

### Changelog rules (MANDATORY)

Every response that modifies code **must** update `CHANGELOG.md`:

1. **Add entries to the `## [Unreleased]` section** at the top of the
   file, using the appropriate sub-heading (`Added`, `Fixed`, `Changed`,
   `Removed`).
2. **Do NOT create a new version entry** — only add to `[Unreleased]`.
3. **Do NOT bump `APP_VERSION`** in `app.py` or `version` in
   `package.json`. Version bumps are performed only when the user
   explicitly asks to cut a release.
4. **Avoid redundancy**: before adding a new bullet, check the existing
   `[Unreleased]` entries. If a previous bullet already covers the same
   feature or area and the current change is a fix or refinement of that
   unreleased work, **update the existing bullet in-place** (or remove
   it and write a better one) instead of adding a separate "Fixed …"
   entry. Fixes to unreleased features are not changelog-worthy on their
   own — the user has never seen the broken state.
5. When the user requests a release:
   - Determine the new version (feat → minor bump, fix/refactor/chore →
     patch bump, major → only on explicit request).
   - Replace `## [Unreleased]` with `## [x.y.z] — YYYY-MM-DD` and add a
     fresh empty `## [Unreleased]` above it.
   - Update `APP_VERSION` in `app.py` and `version` in `package.json`
     to match.
6. **No artificial line breaks**: each changelog bullet must be a single
   line — do **not** hard-wrap at 72 or 80 columns. Word wrap in the
   editor and on GitHub handles long lines correctly.

### Version locations (kept in sync only at release time)

| File | Field |
|------|-------|
| `app.py` | `APP_VERSION = "x.y.z"` |
| `package.json` | `"version": "x.y.z"` |
| `CHANGELOG.md` | `## [x.y.z] — YYYY-MM-DD` |

All three **must** stay in sync after each release.

### Release badge (MANDATORY)

The `README.md` contains a release badge that links to the latest
GitHub release: `[![GitHub Release](...)](https://github.com/jqnoc/librarium/releases/latest)`.
When cutting a release, verify the badge is present and points to
`/releases/latest` (not a specific tag) so it always resolves.

---

## 12. Known Issues & Technical Debt

- **Monolithic `app.py`**: ~5 000+ lines in a single file. No plans to
  refactor, but be aware of line-number drift when making changes.
- **No automated tests**: All verification is manual.
- **`app.secret_key`**: Hardcoded as `"librarium-local-dev-key"` — acceptable
  for a localhost-only personal app but not production-safe.
- **Cover extraction**: `cover_color` and `cover_palette` are computed on
  upload; changing the algorithm does not retroactively update existing books.
- **Status timeline**: `_compute_status_timeline()` reconstructs history
  from reading/session/period dates — it does not use a separate audit log
  table, so historical accuracy depends on those dates being correct.

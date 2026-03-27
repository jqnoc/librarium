# Changelog

All notable changes to Librarium will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] — 2026-03-27

### Added
- Electron shell wrapping the Flask backend — the app now opens in its
  own window instead of requiring a browser.
- Dynamic port allocation via `findFreePort()`, eliminating port conflicts.
- External links open in the default browser instead of inside the app.
- `main.js` (Electron main process), `preload.js` (sandboxed renderer bridge),
  and `package.json` with Electron dependency and build config.
- `APP_VERSION` constant in `app.py`, exposed to all templates and displayed
  in the footer.
- `CHANGELOG.md` (this file).
- "Books Owned" stat tile on the library index page.
- "Time Read by Year" bar chart on the global statistics page.
- Frameless fullscreen Electron window (no OS title bar or menu bar).
- In-app close button (✕) next to the EN|ES toggle; creates a database
  backup before quitting.
- `Librarium.vbs` launcher — opens Electron without a visible console window.
- Latin epigraph on the Library page header.
- Hover tooltip on the "Most Books Read at Once" activity card showing
  the list of books.

### Fixed
- `progress_pct` now included in session and period queries on book detail.
- `sqlite3.Row` `.get()` `AttributeError` in `edit_session` and
  `edit_reading_period` replaced with bracket notation.
- GUI settings (view mode, column selection, etc.) now persist across
  Electron restarts by using a deterministic preferred port.

### Changed
- `app.py` startup block reads `LIBRARIUM_PORT` and `LIBRARIUM_ELECTRON`
  environment variables; debug mode disabled under Electron.
- `run-librarium.bat` delegates to `Librarium.vbs` for silent launch.

## [0.4.0] — 2026-03-26

### Added
- "Show All Editions" and "Show All Readings" checkboxes on the library
  index with cookie persistence.
- "Show All Editions" checkbox on the author detail page.
- `_build_index_per_reading()` helper for per-reading library entries.
- Manual database backup button with HMS timestamps in the library
  management modal.
- `skip_if_recent` parameter on `backup_database()` for startup vs manual
  distinction.

### Fixed
- `UnboundLocalError` when "Show All Readings" is checked (scoped `books`
  assignment to the correct branch).
- Reading number `#N` now only shown when a book has multiple readings
  displayed.
- Reading timeline Gantt on book detail filtered to the currently selected
  reading only.
- Palette selector hidden again after rename.

### Changed
- Project renamed from Ashinami to Librarium: all CSS custom properties
  (`--an-*` → `--lb-*`), DB path, secret key, backup globs, cookie names,
  localStorage keys, page titles, logo, and batch/workspace files.
- `logo.png` and `favicon.ico` regenerated from `logo.svg`.

## [0.3.0] — 2026-03-25

### Added
- Series management with many-to-many `book_series` (list, detail, rename,
  delete).
- Multi-edition system: link/unlink editions, set primary edition.
- `draft` book status with grey badge, CSS variable, and i18n labels.
- Status timeline stacked area chart on the stats page with
  absolute/relative toggle.
- `_compute_status_timeline()` helper and `/api/status_timeline` endpoint.
- Re-read support: multiple readings per book with independent sessions
  and periods.
- Format, binding, and audio_format fields on books with conditional
  UI toggles.
- Copilot agent directives (`copilot-instructions.md`) and full `README.md`.

### Fixed
- Sessions/periods section scrolls into view after add/edit/delete on
  book detail.
- Add-form panels centered in viewport after redirect.
- Hidden inputs disabled in format toggle to prevent HTML5 validation
  failures on submit.
- Non-primary editions filtered from aggregate statistics (stats,
  activity, status timeline, yearly books).

## [0.2.0] — 2026-03-21

### Added
- Rich-text editing for book summaries and author biographies (allowlist-based
  HTML sanitiser).
- Subtitle field on books.

## [0.1.0] — 2026-03-19

### Added
- Complete Flask-based book library tracker replacing the Kivy prototype.
- Library management with card, cover, and list view modes.
- Reading session and period tracking with Gantt chart visualisation.
- 39-dimension rating system across 7 categories.
- Author directory with biography and photo support.
- Source/purchase location tracking.
- Global and yearly reading statistics with Chart.js.
- Activity dashboard with streaks, records, and trends.
- Re-reading support with independent session logs.
- 6 colour palettes (Orange, Mori, Hone, Kawara, Sora, Hinode).
- Internationalisation (English and Spanish).
- Automatic daily SQLite backups with integrity recovery.
- HEIF/AVIF image support via pillow-heif.
- Multi-library support with library switching.

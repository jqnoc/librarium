# Changelog

All notable changes to Librarium will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] — 2026-03-28

### Added
- "Add Book" modal dialog with two options: "Add Manually" and "Add
  From ISBN"; replaces the old direct link in navbar and empty states.
- ISBN lookup via Open Library API (`/api/isbn_lookup`): fetches title,
  author, publisher, pages, genre, cover image, and pre-populates the
  new book form.
- Cover image auto-download from ISBN lookup URL when no file is
  uploaded manually.
- Author photo thumbnail system: `photo_thumb` column on authors,
  `migrate_add_photo_thumb()` migration with backfill, and
  `/author_photo_thumb/<name>` route with ETag caching.
- `_format_duration_hms()` helper for displaying time in hours, minutes,
  and seconds without day rounding.
- Tooltip on the "Total Time Read" stat tile showing the full H:M:S
  breakdown.
- i18n keys: `addBook.title`, `addBook.manually`, `addBook.fromIsbn`,
  `addBook.isbnPlaceholder`, `addBook.search`, `bookForm.coverFromIsbn`.

### Changed
- Consolidated all colour palettes into a single "Librarium" theme
  (formerly Hone); removed Orange, Mori, Kawara, Umi, Hinode, and Sora
  palette definitions from CSS and all palette-switching code from
  `base.html`.
- Authors list page now uses thumbnail photos (`author_photo_thumb`)
  and thumbnail book covers (`book_cover_thumb`) with `loading="lazy"`.
- Series list page now uses `book_cover_thumb` for collage images with
  `loading="lazy"`.
- Electron `BrowserWindow` uses `backgroundThrottling: false` to
  prevent the window going blank on Alt+Tab focus return.
- Taskbar icon upgraded from low-resolution `favicon.ico` (879 B) to
  high-resolution `logo.png` (192 KB) for crisp display.
- Library list-view column checkboxes now render with their saved state
  immediately (inline script before paint), eliminating the flash of
  all-checked → restored state.

### Fixed
- Column toggle checkboxes (Publication Date, Publisher, Rating, Pages,
  Language) no longer flash as checked then unchecked on Library page
  load.
- Book detail, author detail, and series detail pages now use full-size
  cover images instead of thumbnails (thumbnails are kept only for list
  pages).
- Library search now splits the query into individual words and requires
  all words to be present, so "Stephen King" correctly matches books
  whose author is stored as "King, Stephen".
- ISBN field in the Add Book form now preserves the original value with
  dashes (e.g. `978-3-16-148410-0`) as typed or returned by the lookup,
  rather than stripping formatting characters.

## [0.6.0] — 2026-03-28

### Added
- Loading splash screen with logo and spinner shown while the Flask
  backend starts up; closes automatically when the main window is ready.
- Shutdown overlay with spinner displayed when the close button is
  clicked, while the database backup runs before quitting.
- Dynamic search filter on the library index — filters card, cover, and
  list views by title, subtitle, or author in real time.
- Image thumbnail system: a 300 px-wide JPEG thumbnail is generated on
  cover upload and stored in the new `cover_thumb` column; library
  listing views, author detail, series detail, edition cards, and yearly
  stats now serve the lightweight thumbnail instead of the full-size
  cover.
- `/cover_thumb/<book_id>` route to serve thumbnails with ETag caching.
- `migrate_add_cover_thumb()` migration (idempotent) that adds the
  column and backfills thumbnails for existing covers.
- Edition cards in the book detail page now display cover images in a
  side-by-side layout with larger card dimensions.
- i18n keys: `index.searchPlaceholder`, `backup.shuttingDown`.

### Fixed
- "Most Books Read at Once" tooltip on the activity page no longer
  clipped by the parent card's `overflow: hidden` (uses `:has()` to
  allow overflow on the records-grid container).

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

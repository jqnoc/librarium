# Changelog

All notable changes to Librarium will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.14.1] — 2026-04-05

### Fixed
- Fixed a bug with the new multiple library view

## [0.14.0] — 2026-04-05

### Added
- Multi-library checkbox selector: the library dropdown is now a multi-select
  checkbox dropdown, allowing any combination of libraries to be active at once.
- Library selector field on the new-book form, so new books can be assigned
  to any library regardless of the current view filter.
- Two new rating groups for visual media (manga, comics, graphic novels, BD):
  **Visual Art** (6 dimensions) and **Sequential Narrative** (6 dimensions),
  bringing the total to 51 dimensions across 9 groups.

### Changed
- `_get_current_library_id()` replaced by `_get_selected_library_ids()`
  returning a list of selected library IDs.
- `_lib_filter()` now accepts a list of IDs and generates `IN (?, …)`
  clauses when multiple libraries are selected.
- Library selection cookie format changed from single ID to
  comma-separated list (backward-compatible with old single-ID cookies).

### Removed
- "All" pseudo-library option (replaced by multi-checkbox selection
  where all checkboxes checked is equivalent).

## [0.13.0] — 2026-04-05

### Added
- "All" option in the library selector: when selected, all pages and
  statistics aggregate data across every library in the database.
- Library selector combobox on the edit-metadata page, allowing a book
  to be moved from one library to another.
- `_lib_filter()` helper function for dynamic per-query library
  filtering (returns pass-through `1=1` in All mode).

### Fixed
- Tag Cloud section on the global statistics page is now positioned at
  the end of the page, after Top Authors.
- Reading Heat Map weekday labels (Mon, Wed, Fri) now align correctly
  with their corresponding data rows.

### Changed
- `_get_current_library_id()` returns `0` for the All-libraries
  pseudo-selection.
- All library-filtered SQL queries (~46) converted from static
  `library_id = ?` to dynamic `_lib_filter()` pattern.

## [0.12.0] — 2026-04-03

### Added
- Database path is now always `data/` inside the project folder, both in
  Electron and development mode (`_get_app_data_dir()` removed).
- Database path is displayed as a non-editable label in the Manage
  Libraries dialog.
- Tags section on book detail page: tags are shown as clickable bubbles
  after the Ratings section, sorted alphabetically. Clicking a tag
  filters the library index to books sharing that tag.
- Tag filter banner on the library index page with a clear button.

### Changed
- "Anonymous" authors are no longer rendered as hyperlinks in book detail
  metadata and are excluded from the Authors listing page.
- Copilot instructions updated to reflect `data/` as the canonical
  database location.

## [0.11.0] — 2026-04-02

### Added
- Genre→Tags merge: all existing genre values are migrated into the tags
  field (deduplicated, case-insensitive). The genre field is no longer
  used in the UI — only tags remain.
- ISBN lookup now populates the tags field instead of genre.
- New edition prefill copies tags from the primary edition.

### Fixed
- Status timeline chart ("Books by Status Over Time") now correctly
  aggregates readings from all editions of a work, not just the primary
  edition. This fixes undercounting for books read as secondary editions.
- Status timeline same-date transition sort bug: when a reading starts
  and finishes on the same date, the "reading" event now correctly
  precedes the "finished" event instead of being sorted alphabetically.
- Snap-to-actual-status correction at the present date ensures the
  timeline matches the current database status for edge cases.

### Changed
- Removed genre input from new-book and edit-metadata forms (replaced by
  tags field).
- Removed genre display from book detail page (replaced by tags).
- Removed "Books by Genre" bar chart and "Genre Cloud" from global
  statistics page; only the "Tag Cloud" remains.
- Removed genre-related i18n keys (`book.genre`, `bookForm.genre`,
  `stats.byGenre`, `stats.genreCloud`).

## [0.10.0] — 2026-04-02

### Added
- Shared authors across libraries: authors are now global entities no
  longer scoped to a single library. Duplicate author records are merged
  automatically, keeping the richest data (longest bio, photo, dates).
- Shared sources across libraries: sources are now global, with duplicate
  records merged by name during migration.
- Author gender field (`male`, `female`, `unknown`) with dropdown in the
  edit-author form and display on the author detail page.
- Tags per book (semicolon-separated free text) with datalist
  autocomplete on the new-book and edit-metadata forms.
- Tag word cloud on the global statistics page, rendered alongside a
  genre cloud using CSS-based proportional sizing.
- Status timeline chart now has time-range radio buttons: All Time, Last
  5 Years, and Last Year, with localStorage persistence.

### Changed
- Genre counting in global statistics now correctly splits multi-genre
  fields by semicolons instead of treating the whole field as one value.

### Fixed
- Genre values are normalised to title case via a database migration,
  preventing duplicate entries caused by inconsistent capitalisation.
- Changelog entries for versions 0.8.0 through 0.9.1 reformatted to
  match the established capitalised, multi-line style of earlier entries.

## [0.9.1] — 2026-04-01

### Fixed
- Add `init_schema()` function that creates all base tables (`books`,
  `sessions`, `periods`, `readings`, `ratings`, `sources`, `libraries`,
  `series`, `authors`, `book_series`) and the default "Books" library for
  brand-new user databases; new users no longer get an empty database with
  no tables.
- Remove `if not DB_PATH.exists(): return` guard from
  `_run_all_migrations()` and call `init_schema()` first so creating a
  fresh user database correctly initialises all tables before running
  (now-idempotent) migrations.
- Replace unreliable native `<datalist>` click behaviour with a custom
  autocomplete dropdown (`autocomplete.js`) that opens on a single click,
  filters as you type, and re-opens after typing "; " for multi-value
  fields (Author, Genre, Language, Publisher, etc.).
- Remove duplicated and non-functional datalist JS from
  `edit_metadata.html` and `new_book.html` script blocks.

## [0.9.0] — 2026-04-01

### Added
- Backup directory picker in the library management modal with input field
  and save button.
- i18n keys for backup directory UI (`backup.directory`, `backup.dirDefault`,
  `backup.saveDir`, `backup.dirHint`) in EN and ES.
- Datalist dropdowns open on single click (Author, Genre, Language,
  Publisher, etc.).
- Datalist dropdowns reopen automatically after typing "; " for multi-value
  entry.

### Changed
- Simplify navbar user badge to show only the name without the avatar
  circle.
- Expose `backup_dir` in template context via `inject_library_context()`.

## [0.8.1] — 2026-04-01

### Fixed
- Define missing `_run_all_migrations()` function that was called but
  never implemented, crashing user creation and switching.
- Create `users.html` template for the user selection / creation screen
  that was missing despite backend routes being in place.
- Make startup migration block user-aware: iterate over all registered
  users' databases instead of assuming a single `librarium.db`.

### Added
- Current user name displayed in the navbar header.
- CSS styles for the user selection page and navbar user badge.
- i18n keys for user management UI (EN and ES).

## [0.8.0] — 2026-03-28

### Added
- Focus `librarySearch` when pressing Ctrl/Cmd+F on the Library page
  (focuses and selects existing text; prevents default browser find).

## [0.7.1] — 2026-03-28

### Changed
- update `.github/copilot-instructions.md` to require a version bump and changelog update for every code-modifying request

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

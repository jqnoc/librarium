# Changelog

All notable changes to Librarium will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Mandatory Dropbox integration: app now requires Dropbox authentication at startup; all user databases, `users.json`, and backups are synced to the `Apps/LibrariumApp` folder in the user's Dropbox account
- OAuth2 PKCE flow for Dropbox authentication with refresh token persistence; auth tokens stored in local `auth.json`; the browser callback now stays a close-tab confirmation page instead of turning into a second Librarium surface
- New routes: `/auth/login`, `/auth/start`, `/auth/callback`, `/auth/logout`, `/auth/status` for the Dropbox OAuth flow
- Periodic background sync (every 5 minutes) uploads modified databases to Dropbox using content-hash change detection
- Startup sync: on launch, the app downloads the latest databases and `users.json` from Dropbox before presenting the user selection screen
- Dropbox sync indicator (small Dropbox icon) in the navigation bar when connected
- Dropbox account info bar on the users page showing display name, email, and a disconnect button
- Auth login, waiting, success, and startup-sync templates for the Dropbox OAuth and initial sync flows
- Full i18n support (EN / ES) for all Dropbox auth and sync strings
- CSS styles for auth pages, Dropbox account bar, and sync badge

### Changed
- Portable Windows builds now bundle the Flask backend as a standalone executable via PyInstaller, so the packaged app no longer depends on a system Python installation
- Development startup and backend packaging now prefer the repository `.venv` interpreter when available before falling back to the system `python`
- Internal Copilot instructions now require staging newly created repository files with `git add` so intentional additions are not missed from commits
- Thoughts editor now uses Markdown instead of raw HTML; a dedicated Markdown toolbar provides formatting buttons for bold, italic, strikethrough, headings, lists, blockquotes, links, code, and horizontal rules
- Books Bought page: card view now shows a 📅 calendar emoji before the purchase date; person sources always show 👤 regardless of gift status; gifts display "🎁 Gift" in the price slot (with price appended if available) instead of only showing the price with a gift emoji
- Books Bought page now shows source-type-aware emojis (🏪 physical store, 🌐 web store, 🏛️ library, 🎁 gift, 👤 person) instead of a generic "Location:" label, removes the redundant "Date:" prefix, and shows 🎁 instead of 💰 on the price when the book was a gift
- Calendar view no longer limits visible book covers to 4 per cell; all covers are shown using the existing flex-wrap layout
- Series list page now loads significantly faster by fetching all series covers in a single batched SQL query instead of one query per series
- Backups are now uploaded to a `/backups/` folder in Dropbox alongside user databases; remote backups are pruned to keep 5 per user
- `check_user_selected` middleware now validates the current user cookie against `users.json`, auto-recovers stale cookies, checks Dropbox authentication before user selection, and exempts `/api/shutdown-backup` so quitting still works before login completes
- Electron shutdown now uses a single validated `/api/shutdown-backup` path, and quitting can be cancelled when backup or Dropbox sync fails instead of silently proceeding
- Shutdown sync now uploads each user's database to Dropbox once, then creates backup copies via server-side Dropbox copy (`files_copy_v2`) instead of re-uploading the full database as a backup; startup backups no longer trigger a redundant Dropbox upload
- Dropbox sync at startup now runs in a background thread so Flask starts immediately and Electron can connect; a "Syncing with Dropbox…" loading page is shown until the download and migrations finish
- Dropbox file downloads now skip re-downloading when the local file's content hash already matches the remote, avoiding unnecessary 249 MB transfers on subsequent launches
- Image externalization: book covers and author photos are now stored as individual files on disk (`DATA_DIR/images/<user>/covers/` and `authors/`) instead of SQLite BLOBs, reducing database size from ~244 MB to ~57 MB; thumbnails remain in the DB; images are synced individually to Dropbox; a one-time migration extracts existing BLOBs to files and VACUUMs the database

### Fixed
- Quote of the Day on the Dashboard now renders curly quotes correctly instead of showing literal `\u201c` / `\u201d` escape sequences; also fixes HTML formatting within quotes being escaped
- Library filter, sort, and tag controls now correctly stay on the `/library` page instead of redirecting to the Dashboard
- Tag Cloud links in the Stats page now navigate to the Library filtered by that tag instead of the Dashboard
- New Book and Edit Metadata pages now support the legacy `window.librariumI18n.apply()` call path again, and missing translation keys for `nav.minimize`, `book.colTime`, and the 404 dashboard CTA are now defined consistently

## [1.2.0] — 2026-04-12

### Added
- Annotations system: quotes, thoughts, and words per book edition with dedicated database tables, full CRUD (add, edit, delete) inline on the book detail page; quotes and thoughts ordered by page number (null-page entries last), words ordered alphabetically in a responsive grid
- Bookly PDF import on the edit metadata page: upload a Bookly summary PDF to automatically extract and import quotes, thoughts, and words; optional checkbox to clear existing annotations before importing; quotation marks are automatically stripped from extracted quotes
- "Quote of the Day" and "Words of the Day" spotlight sections on the dashboard, placed between Currently Reading and This Year at a Glance; quote is random from any book, words are random per language
- Quotes section on the author detail page showing all quotes from the author's books in a randomised three-column masonry layout
- Rich-text editing toolbar (bold, italic, underline, strikethrough, headings, lists, links) for quote, thought, and word annotation textareas on the book detail page
- Language-aware quotation marks: quotes from Spanish and Galician books display with «» guillemets, all others use “” curly double quotes; applied on the book detail page, dashboard spotlight, and author detail page
- Full i18n support (EN / ES) for all annotation and spotlight strings
- Dashboard page (`/`) as the new landing page with hero stats ribbon, currently reading books, this-year-at-a-glance with YoY comparison (books, pages, and time), streaks & consistency, reading heatmap (52 weeks), comprehensive recent activity feed (50 items with thumbnails and agglutinated events per book per day: date shown first, then action description with book name as link; read pages are summed, started/finished/bought/borrowed/gifted events are merged into a single line with proper comma/and conjunction; bought entries show store name and price; borrowed entries show source name; time display omits the "0h" prefix when under one hour), "Last Books Owned" section (50 most recent owned books with human-readable messages: bought/gift with date, source, and price; scrollable, side-by-side with Recent Activity), top-rated books, records, format & source donut charts, tag cloud, author spotlight (4 random authors), series progress, language diversity, dynamic TBR pile (15 random books), and expanded library health nudges (unrated, no cover, no photo, no tags, abandoned, no pages, no summary, no author)
- Dashboard link in the navigation bar; logo now links to the dashboard
- Full i18n support (EN / ES) for all new dashboard strings
- Calendar page (`/calendar`) with navigable month view: year and month dropdown selectors (month list adapts based on the current year), previous/next arrows and "Today" shortcut, book cover thumbnails in each day cell (up to 4 per day with +N overflow), click-to-expand detail panel, multi-date selection (Ctrl-click to toggle individual dates, Shift-click for ranges) with per-book agglutinated stats when multiple dates are selected, and today highlight
- Agglutinated year activity summary per book as a new section on the yearly stats page (`/stats/year/<year>`), with cover thumbnails, book links, and proper comma/and conjunction (between the Per-book Cumulative Pages chart and Reading Sessions table)
- "Books Bought by Year" bar chart on the global statistics page (`/stats`), placed between the Time Read chart and the Status Timeline; clicking a bar navigates to a new detail page (`/stats/year/<year>/bought`) listing all books bought that year with cover, author, purchase date, location, price, and gift indicator; card/list view toggle (saved in localStorage); sortable by date, title, author, or price
- Full i18n support (EN / ES) for all calendar strings including day-of-week headers and month names

### Fixed
- Year Activity Summary on yearly stats page now renders HTML correctly (fixed Jinja2 auto-escaping of `<span>` tags in agglutinated output)
- Calendar detail panel date display now respects the app's i18n language setting instead of always using the browser locale

### Changed
- Quotes, Thoughts, and Words sections on the book detail page moved from after Reading Periods to between Reading Stats and Reading Sessions
- Dashboard "Words of the Day" renamed from "Word of the Day" to reflect multi-language display
- Dashboard "Books Bought this Year" section replaced with "Last Books Owned" showing the 50 most recent owned books with human-readable messages (bought on date at place with price in italics; received as a gift from person on date)
- Dashboard "Recent Activity" feed restyled: date shown first, then action text with book title as a clickable link (e.g. "Read 6 pages of *Book Title* (33m)"); borrowed items show source name
- Dashboard TBR pile reduced from 30 to 15 random books
- Library page moved from `/` to `/library`; all existing library links and redirects updated accordingly
- Removed stats ribbon from the library index page (moved to dashboard)
- Removed summary record cards (highest rated, longest, shortest, most re-read) from the global stats page (moved to dashboard)
- Removed streaks & consistency, heatmap, estimated finish dates, and personal records from the activity page (moved to dashboard)
- 404 page now links back to the dashboard instead of the library

## [1.1.0] — 2026-04-05

### Added
- Custom 404 error page with themed styling and i18n support (EN / ES)
- GitHub Release badge in `README.md` linking to the latest release
- Social preview image (`static/social-preview.png`) for the GitHub repository, using the project logo and theme gradient
- Tag Cloud on the global statistics page now renders tags as clickable pill-shaped hyperlinks that filter the library index by tag; most frequent tags are highlighted with the accent colour
- "Building & Releasing" section in `README.md` with step-by-step instructions for building the portable executable, tagging, and creating a GitHub Release

### Changed
- User databases and `users.json` are now stored in the platform's application data directory (`%APPDATA%/Librarium` on Windows, `~/Library/Application Support/Librarium` on macOS, `~/.local/share/Librarium` on Linux) instead of a `data/` folder next to the application; existing data is automatically migrated on first run
- Library multi-select dropdown: clicking a library name now switches to that single library; only clicking the checkbox enables multi-selection
- Library dropdown checkboxes restyled with custom appearance using the Librarium accent colour (`--lb-gold`) instead of the browser default blue
- `--lb-accent` CSS variable now explicitly defined (`#EC8F8D`) so all accent-coloured controls use the brand colour consistently
- Copilot agent directives rewritten to match actual codebase: corrected rating dimensions (39 â†’ 51, 7 â†’ 9 groups), migrations (15 â†’ 22), template filters (4 â†’ 5), routes (40 â†’ 51), database schema, helper functions, CSS theme description, multi-library mechanism, file conventions, and line-count references
- `README.md` Data Storage section updated to reflect AppData paths; release badge now links to the actual releases page; project structure tree no longer shows a misleading `data/` folder

## [1.0.0] — 2026-04-05

First stable release.

### Added
- `LICENSE.md` — Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International license

### Changed
- Complete `README.md` rewrite reflecting the actual state of the project: Electron shell, multi-user system, per-user databases, ISBN lookup, 51-dimension rating system (9 groups), tags (replacing genres), multi-library checkbox selector, shared authors/sources, updated project structure, technologies table, and license section

## [0.14.1] — 2026-04-05

### Fixed
- Fixed a bug with the new multiple library view

## [0.14.0] — 2026-04-05

### Added
- Multi-library checkbox selector: the library dropdown is now a multi-select checkbox dropdown, allowing any combination of libraries to be active at once.
- Library selector field on the new-book form, so new books can be assigned to any library regardless of the current view filter.
- Two new rating groups for visual media (manga, comics, graphic novels, BD): **Visual Art** (6 dimensions) and **Sequential Narrative** (6 dimensions), bringing the total to 51 dimensions across 9 groups.

### Changed
- `_get_current_library_id()` replaced by `_get_selected_library_ids()` returning a list of selected library IDs.
- `_lib_filter()` now accepts a list of IDs and generates `IN (?, "¦)` clauses when multiple libraries are selected.
- Library selection cookie format changed from single ID to comma-separated list (backward-compatible with old single-ID cookies).

### Removed
- "All" pseudo-library option (replaced by multi-checkbox selection where all checkboxes checked is equivalent).

## [0.13.0] — 2026-04-05

### Added
- "All" option in the library selector: when selected, all pages and statistics aggregate data across every library in the database.
- Library selector combobox on the edit-metadata page, allowing a book to be moved from one library to another.
- `_lib_filter()` helper function for dynamic per-query library filtering (returns pass-through `1=1` in All mode).

### Fixed
- Tag Cloud section on the global statistics page is now positioned at the end of the page, after Top Authors.
- Reading Heat Map weekday labels (Mon, Wed, Fri) now align correctly with their corresponding data rows.

### Changed
- `_get_current_library_id()` returns `0` for the All-libraries pseudo-selection.
- All library-filtered SQL queries (~46) converted from static `library_id = ?` to dynamic `_lib_filter()` pattern.

## [0.12.0] — 2026-04-03

### Added
- Database path is now always `data/` inside the project folder, both in Electron and development mode (`_get_app_data_dir()` removed).
- Database path is displayed as a non-editable label in the Manage Libraries dialog.
- Tags section on book detail page: tags are shown as clickable bubbles after the Ratings section, sorted alphabetically. Clicking a tag filters the library index to books sharing that tag.
- Tag filter banner on the library index page with a clear button.

### Changed
- "Anonymous" authors are no longer rendered as hyperlinks in book detail metadata and are excluded from the Authors listing page.
- Copilot instructions updated to reflect `data/` as the canonical database location.

## [0.11.0] — 2026-04-02

### Added
- Genreâ†’Tags merge: all existing genre values are migrated into the tags field (deduplicated, case-insensitive). The genre field is no longer used in the UI — only tags remain.
- ISBN lookup now populates the tags field instead of genre.
- New edition prefill copies tags from the primary edition.

### Fixed
- Status timeline chart ("Books by Status Over Time") now correctly aggregates readings from all editions of a work, not just the primary edition. This fixes undercounting for books read as secondary editions.
- Status timeline same-date transition sort bug: when a reading starts and finishes on the same date, the "reading" event now correctly precedes the "finished" event instead of being sorted alphabetically.
- Snap-to-actual-status correction at the present date ensures the timeline matches the current database status for edge cases.

### Changed
- Removed genre input from new-book and edit-metadata forms (replaced by tags field).
- Removed genre display from book detail page (replaced by tags).
- Removed "Books by Genre" bar chart and "Genre Cloud" from global statistics page; only the "Tag Cloud" remains.
- Removed genre-related i18n keys (`book.genre`, `bookForm.genre`, `stats.byGenre`, `stats.genreCloud`).

## [0.10.0] — 2026-04-02

### Added
- Shared authors across libraries: authors are now global entities no longer scoped to a single library. Duplicate author records are merged automatically, keeping the richest data (longest bio, photo, dates).
- Shared sources across libraries: sources are now global, with duplicate records merged by name during migration.
- Author gender field (`male`, `female`, `unknown`) with dropdown in the edit-author form and display on the author detail page.
- Tags per book (semicolon-separated free text) with datalist autocomplete on the new-book and edit-metadata forms.
- Tag word cloud on the global statistics page, rendered alongside a genre cloud using CSS-based proportional sizing.
- Status timeline chart now has time-range radio buttons: All Time, Last 5 Years, and Last Year, with localStorage persistence.

### Changed
- Genre counting in global statistics now correctly splits multi-genre fields by semicolons instead of treating the whole field as one value.

### Fixed
- Genre values are normalised to title case via a database migration, preventing duplicate entries caused by inconsistent capitalisation.
- Changelog entries for versions 0.8.0 through 0.9.1 reformatted to match the established capitalised, multi-line style of earlier entries.

## [0.9.1] — 2026-04-01

### Fixed
- Add `init_schema()` function that creates all base tables (`books`, `sessions`, `periods`, `readings`, `ratings`, `sources`, `libraries`, `series`, `authors`, `book_series`) and the default "Books" library for brand-new user databases; new users no longer get an empty database with no tables.
- Remove `if not DB_PATH.exists(): return` guard from `_run_all_migrations()` and call `init_schema()` first so creating a fresh user database correctly initialises all tables before running (now-idempotent) migrations.
- Replace unreliable native `<datalist>` click behaviour with a custom autocomplete dropdown (`autocomplete.js`) that opens on a single click, filters as you type, and re-opens after typing "; " for multi-value fields (Author, Genre, Language, Publisher, etc.).
- Remove duplicated and non-functional datalist JS from `edit_metadata.html` and `new_book.html` script blocks.

## [0.9.0] — 2026-04-01

### Added
- Backup directory picker in the library management modal with input field and save button.
- i18n keys for backup directory UI (`backup.directory`, `backup.dirDefault`, `backup.saveDir`, `backup.dirHint`) in EN and ES.
- Datalist dropdowns open on single click (Author, Genre, Language, Publisher, etc.).
- Datalist dropdowns reopen automatically after typing "; " for multi-value entry.

### Changed
- Simplify navbar user badge to show only the name without the avatar circle.
- Expose `backup_dir` in template context via `inject_library_context()`.

## [0.8.1] — 2026-04-01

### Fixed
- Define missing `_run_all_migrations()` function that was called but never implemented, crashing user creation and switching.
- Create `users.html` template for the user selection / creation screen that was missing despite backend routes being in place.
- Make startup migration block user-aware: iterate over all registered users' databases instead of assuming a single `librarium.db`.

### Added
- Current user name displayed in the navbar header.
- CSS styles for the user selection page and navbar user badge.
- i18n keys for user management UI (EN and ES).

## [0.8.0] — 2026-03-28

### Added
- Focus `librarySearch` when pressing Ctrl/Cmd+F on the Library page (focuses and selects existing text; prevents default browser find).

## [0.7.1] — 2026-03-28

### Changed
- update `.github/copilot-instructions.md` to require a version bump and changelog update for every code-modifying request

## [0.7.0] — 2026-03-28

### Added
- "Add Book" modal dialog with two options: "Add Manually" and "Add From ISBN"; replaces the old direct link in navbar and empty states.
- ISBN lookup via Open Library API (`/api/isbn_lookup`): fetches title, author, publisher, pages, genre, cover image, and pre-populates the new book form.
- Cover image auto-download from ISBN lookup URL when no file is uploaded manually.
- Author photo thumbnail system: `photo_thumb` column on authors, `migrate_add_photo_thumb()` migration with backfill, and `/author_photo_thumb/<name>` route with ETag caching.
- `_format_duration_hms()` helper for displaying time in hours, minutes, and seconds without day rounding.
- Tooltip on the "Total Time Read" stat tile showing the full H:M:S breakdown.
- i18n keys: `addBook.title`, `addBook.manually`, `addBook.fromIsbn`, `addBook.isbnPlaceholder`, `addBook.search`, `bookForm.coverFromIsbn`.

### Changed
- Consolidated all colour palettes into a single "Librarium" theme (formerly Hone); removed Orange, Mori, Kawara, Umi, Hinode, and Sora palette definitions from CSS and all palette-switching code from `base.html`.
- Authors list page now uses thumbnail photos (`author_photo_thumb`) and thumbnail book covers (`book_cover_thumb`) with `loading="lazy"`.
- Series list page now uses `book_cover_thumb` for collage images with `loading="lazy"`.
- Electron `BrowserWindow` uses `backgroundThrottling: false` to prevent the window going blank on Alt+Tab focus return.
- Taskbar icon upgraded from low-resolution `favicon.ico` (879 B) to high-resolution `logo.png` (192 KB) for crisp display.
- Library list-view column checkboxes now render with their saved state immediately (inline script before paint), eliminating the flash of all-checked â†’ restored state.

### Fixed
- Column toggle checkboxes (Publication Date, Publisher, Rating, Pages, Language) no longer flash as checked then unchecked on Library page load.
- Book detail, author detail, and series detail pages now use full-size cover images instead of thumbnails (thumbnails are kept only for list pages).
- Library search now splits the query into individual words and requires all words to be present, so "Stephen King" correctly matches books whose author is stored as "King, Stephen".
- ISBN field in the Add Book form now preserves the original value with dashes (e.g. `978-3-16-148410-0`) as typed or returned by the lookup, rather than stripping formatting characters.

## [0.6.0] — 2026-03-28

### Added
- Loading splash screen with logo and spinner shown while the Flask backend starts up; closes automatically when the main window is ready.
- Shutdown overlay with spinner displayed when the close button is clicked, while the database backup runs before quitting.
- Dynamic search filter on the library index — filters card, cover, and list views by title, subtitle, or author in real time.
- Image thumbnail system: a 300 px-wide JPEG thumbnail is generated on cover upload and stored in the new `cover_thumb` column; library listing views, author detail, series detail, edition cards, and yearly stats now serve the lightweight thumbnail instead of the full-size cover.
- `/cover_thumb/<book_id>` route to serve thumbnails with ETag caching.
- `migrate_add_cover_thumb()` migration (idempotent) that adds the column and backfills thumbnails for existing covers.
- Edition cards in the book detail page now display cover images in a side-by-side layout with larger card dimensions.
- i18n keys: `index.searchPlaceholder`, `backup.shuttingDown`.

### Fixed
- "Most Books Read at Once" tooltip on the activity page no longer clipped by the parent card's `overflow: hidden` (uses `:has()` to allow overflow on the records-grid container).

## [0.5.0] — 2026-03-27

### Added
- Electron shell wrapping the Flask backend — the app now opens in its own window instead of requiring a browser.
- Dynamic port allocation via `findFreePort()`, eliminating port conflicts.
- External links open in the default browser instead of inside the app.
- `main.js` (Electron main process), `preload.js` (sandboxed renderer bridge), and `package.json` with Electron dependency and build config.
- `APP_VERSION` constant in `app.py`, exposed to all templates and displayed in the footer.
- `CHANGELOG.md` (this file).
- "Books Owned" stat tile on the library index page.
- "Time Read by Year" bar chart on the global statistics page.
- Frameless fullscreen Electron window (no OS title bar or menu bar).
- In-app close button (âœ•) next to the EN|ES toggle; creates a database backup before quitting.
- `Librarium.vbs` launcher — opens Electron without a visible console window.
- Latin epigraph on the Library page header.
- Hover tooltip on the "Most Books Read at Once" activity card showing the list of books.

### Fixed
- `progress_pct` now included in session and period queries on book detail.
- `sqlite3.Row` `.get()` `AttributeError` in `edit_session` and `edit_reading_period` replaced with bracket notation.
- GUI settings (view mode, column selection, etc.) now persist across Electron restarts by using a deterministic preferred port.

### Changed
- `app.py` startup block reads `LIBRARIUM_PORT` and `LIBRARIUM_ELECTRON` environment variables; debug mode disabled under Electron.
- `run-librarium.bat` delegates to `Librarium.vbs` for silent launch.

## [0.4.0] — 2026-03-26

### Added
- "Show All Editions" and "Show All Readings" checkboxes on the library index with cookie persistence.
- "Show All Editions" checkbox on the author detail page.
- `_build_index_per_reading()` helper for per-reading library entries.
- Manual database backup button with HMS timestamps in the library management modal.
- `skip_if_recent` parameter on `backup_database()` for startup vs manual distinction.

### Fixed
- `UnboundLocalError` when "Show All Readings" is checked (scoped `books` assignment to the correct branch).
- Reading number `#N` now only shown when a book has multiple readings displayed.
- Reading timeline Gantt on book detail filtered to the currently selected reading only.
- Palette selector hidden again after rename.

### Changed
- Project renamed from Ashinami to Librarium: all CSS custom properties (`--an-*` â†’ `--lb-*`), DB path, secret key, backup globs, cookie names, localStorage keys, page titles, logo, and batch/workspace files.
- `logo.png` and `favicon.ico` regenerated from `logo.svg`.

## [0.3.0] — 2026-03-25

### Added
- Series management with many-to-many `book_series` (list, detail, rename, delete).
- Multi-edition system: link/unlink editions, set primary edition.
- `draft` book status with grey badge, CSS variable, and i18n labels.
- Status timeline stacked area chart on the stats page with absolute/relative toggle.
- `_compute_status_timeline()` helper and `/api/status_timeline` endpoint.
- Re-read support: multiple readings per book with independent sessions and periods.
- Format, binding, and audio_format fields on books with conditional UI toggles.
- Copilot agent directives (`copilot-instructions.md`) and full `README.md`.

### Fixed
- Sessions/periods section scrolls into view after add/edit/delete on book detail.
- Add-form panels centered in viewport after redirect.
- Hidden inputs disabled in format toggle to prevent HTML5 validation failures on submit.
- Non-primary editions filtered from aggregate statistics (stats, activity, status timeline, yearly books).

## [0.2.0] — 2026-03-21

### Added
- Rich-text editing for book summaries and author biographies (allowlist-based HTML sanitiser).
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

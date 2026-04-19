# Librarium

[![GitHub Release](https://img.shields.io/github/v/release/jqnoc/librarium)](https://github.com/jqnoc/librarium/releases/latest)

A self-contained Electron desktop application for tracking personal book
reading statistics. The backend is a monolithic Flask app with raw SQLite
queries, Jinja2 templates, vanilla JS, and Chart.js for charts. Packaged
Windows builds bundle that backend into a standalone executable, so the
portable app runs without a separate Python installation.

Librarium keeps local per-user SQLite databases in the platform app-data
directory, stores full-size covers and author photos as per-user media
files, keeps thumbnails in SQLite, and synchronizes everything to Dropbox.
Dropbox authentication is required before normal app use.

## Getting Started

### Development Prerequisites

- **Python 3.12+** with pip
- **Node.js 18+** with npm

### Development Installation

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (Electron)
npm install
```

If you keep the Python environment in `.venv`, `npm start` and `npm run build`
automatically prefer that interpreter before falling back to the system
`python` on `PATH`.

### Development Run

```powershell
npm start
```

Or on Windows, double-click `run-librarium.bat`.

The app opens in its own Electron window. For backend-only development,
`python app.py` starts Flask on the port set by `LIBRARIUM_PORT` (or
`5000` by default).

### Portable App

The packaged Windows output (`dist/Librarium <version>.exe`) is a
standalone portable desktop app. End users do **not** need Python,
Node.js, or pip installed to run it.

## Features

### Library Management

- Add, edit, and organise books with cover images, metadata, notes, and tags
- Three library view modes: **card**, **cover**, and **list**
- Real-time search filter by title, subtitle, or author
- Filter and sort by status, tags, language, author, source, and series
- **Multi-library** support — checkbox selector lets any combination of
  libraries be active at once
- ISBN lookup via Open Library API to auto-fill metadata and cover data
- Soft-delete with undo

### Cloud Sync

- Dropbox authentication is mandatory before entering the app
- OAuth2 PKCE flow opens the system browser, then returns to Electron
  without turning the browser into a second app surface
- Startup sync downloads `users.json`, databases, and externalized images
- Periodic background sync uploads modified databases every 5 minutes
- Validated shutdown backup/sync runs before quitting; Electron can cancel
  quitting if the sync fails

### Multi-User System

- Multiple users, each with their own independent SQLite database
- User selection / creation screen on first launch after Dropbox auth
- Per-user migrations run automatically on startup
- Per-user backup-directory overrides when running without Dropbox

### Reading Tracking

- **Sessions**: log date, page range, and duration (hours / minutes / seconds)
- **Periods**: track date ranges without detailed session data; reading
  time is inferred from session averages
- **Re-reads**: start a new reading of the same book; each reading has its
  own sessions and periods

### Annotations

- Quotes, thoughts, and words per book edition
- Inline add/edit/delete workflows on the book detail page
- Bookly PDF import for quotes, thoughts, and words
- Thoughts now use Markdown editing with a dedicated toolbar

### Multi-Edition System

- Link multiple editions of the same work (e.g. hardcover + ebook)
- Mark one edition as primary — only the primary appears in library
  listings
- Unlink editions at any time

### Five Book Statuses

| Status | Colour |
|--------|--------|
| Reading | Blue (#3B82F6) |
| Finished | Green (#10B981) |
| Not Started | Purple (#8B5CF6) |
| Abandoned | Red (#DC2626) |
| Draft | Grey (#6B7280) |

### Rating System

51 dimensions across 9 groups, each rated 1–10:

1. **Emotional Impact** — heartfelt, tear, inspiring, melancholy,
   nostalgia, cathartic
2. **Story & Plot** — plot quality, predictability, pacing, plot twists,
   worldbuilding, character arc
3. **Writing & Style** — writing quality, vocabulary gain, dialogue,
   voice, symbolism, editorial quality
4. **Genre-Specific** — suspense, thrill, humor, romance, mystery, horror
5. **Engagement** — addiction, afterglow, rereadability, originality
6. **Intellectual** — thought-provoking, complexity, historical/cultural
   value, argumentation, clarity
7. **Non-Fiction** — research depth, accuracy, evidence, practicality,
   objectivity, relevance
8. **Visual Art** — art quality, character design, colour & inking,
   background art, cover art, visual consistency
9. **Sequential Narrative** — panel layout, visual storytelling, action
   choreography, expressiveness, text integration, splash pages

Overall score is the **grouped average**: average of each non-empty
group's average, so groups with fewer ratings are not under-weighted.

### Series

- Create named series and assign books with position numbers
- Many-to-many: a book can belong to multiple series
- Series list and detail pages with reading progress

### Authors

- Dedicated author pages with bio, gender, quotes, and photo
- HEIF/AVIF photo support via pillow-heif
- Full-size photos stored as external files; thumbnails kept in SQLite
- Authors are shared across all libraries

### Sources

- Track where books were acquired (bookshop, library, gift, person, etc.)
- Store name, type, city, country, URL, and notes for each source
- Sources are shared across all libraries

### Statistics

- **Dashboard** (`/`): hero stats, currently reading, quote/words of the
  day, year-at-a-glance, recent activity, last owned books, records,
  top-rated books, tag cloud, author spotlight, series progress,
  language diversity, TBR pile, and library-health nudges
- **Library** (`/library`): searchable/filterable card, cover, and list
  views with tag-aware navigation
- **Global stats** (`/stats`): year totals, time read, books bought by
  year, status breakdown, tag cloud, language / publisher / author charts,
  rating distribution, and status timeline
- **Yearly stats** (`/stats/year/<year>`): Gantt chart, cumulative pages,
  per-book cumulative pages, and year activity summary
- **Yearly books** (`/stats/year/<year>/books`): books finished in a
  specific year
- **Books bought by year** (`/stats/year/<year>/bought`): year-specific
  purchase list with card/list toggle and sorting
- **Calendar** (`/calendar`): navigable month view with cover thumbnails,
  detail panel, and multi-date selection
- **Activity** (`/activity`): daily pages/time chart, weekday breakdown,
  rolling pace trend, and active books for the selected period

### Internationalisation

- **English** and **Spanish** — toggle from the navbar
- Translations live in `static/i18n.js` and are applied via `data-i18n`
  attributes
- Language preference persists in `localStorage`

### Data Safety

- **Integrity check** on every startup; automatic restore from backup if a
  database is corrupted
- **Daily local backups** using SQLite's Online Backup API (last 5 kept)
- Dropbox backup copies stored in `Apps/LibrariumApp/backups/`
- WAL mode for safe concurrent reads
- Content-hash-based upload/download skipping for unchanged files

## Data Storage

All application data is stored in the platform's standard application
data directory:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Librarium\` |
| macOS | `~/Library/Application Support/Librarium/` |
| Linux | `~/.local/share/Librarium/` (or `$XDG_DATA_HOME/Librarium/`) |

Typical layout:

```text
Librarium/
  auth.json
  users.json
  <user>.db
  backups/
    <user>_YYYYMMDD.db
  images/
    <user>/
      covers/
      authors/
```

Each user has their own SQLite database named after their username
(e.g. user `JqnOC` → `jqnoc.db`). Full-size cover images and author
photos are stored as files under `images/<user>/...`; thumbnails remain
in the database. On first run after upgrading from an older version, any
existing `data/` folder next to the app is migrated into the platform
app-data location.

## Project Structure

```text
Librarium/
├── main.js                   # Electron main process
├── preload.js                # Electron preload bridge
├── package.json              # Electron manifest and build config
├── app.py                    # Entire Flask application
├── requirements.txt          # Python runtime + build dependencies
├── run-librarium.bat         # Windows launcher
├── Librarium.vbs             # Silent Windows launcher
├── CHANGELOG.md              # Version history
├── LICENSE.md                # CC BY-NC-ND 4.0
├── README.md
├── .github/
│   └── copilot-instructions.md
├── scripts/
│   └── build_backend.py      # PyInstaller backend build helper
├── static/
│   ├── style.css             # Stylesheet
│   ├── i18n.js               # EN / ES translations
│   ├── autocomplete.js       # Custom autocomplete dropdown
│   ├── splash.html           # Startup splash screen
│   ├── logo.png              # App icon (high-res)
│   ├── logo.svg              # App icon (vector)
│   ├── logo.ico              # App icon (ICO)
│   └── favicon.ico           # Browser favicon
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── index.html
    ├── book_detail.html
    ├── edit_metadata.html
    ├── new_book.html
    ├── stats.html
    ├── stats_year.html
    ├── stats_year_books.html
    ├── stats_year_bought.html
    ├── calendar.html
    ├── activity.html
    ├── authors.html
    ├── author_detail.html
    ├── edit_author.html
    ├── sources.html
    ├── series.html
    ├── series_detail.html
    ├── users.html
    ├── auth_login.html
    ├── auth_waiting.html
    ├── auth_success.html
    └── startup_sync.html
```

User databases, `users.json`, `auth.json`, images, and backups are stored
in the platform application data directory, not inside the project folder.

## Technologies

| Layer | Technology |
|-------|-----------|
| Desktop shell | Electron 33.x, Node.js 18+ |
| Backend | Flask 3.x, Python 3.12+ |
| Database | SQLite (raw SQL, WAL mode) |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, vanilla JavaScript (ES6) |
| Charts | Chart.js 4.4.1 (CDN) + chartjs-adapter-date-fns |
| Images | Pillow 10.x, pillow-heif 0.16+ |
| Parsing | pdfplumber, Markdown |
| Packaging | PyInstaller + electron-builder |
| Cloud sync | Dropbox SDK |

## Building & Releasing

### Build a Portable Windows Executable

```powershell
# Set environment variable to skip code signing (no certificate needed)
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"

# Build the bundled backend and the portable Electron app
npm run build
```

The build first creates `build/backend/librarium-backend.exe` with
PyInstaller, then packages Electron into
`dist/Librarium <version>.exe`. The resulting portable executable bundles
the backend runtime and does not require Python on the target machine.

### Create a New Release

1. **Ensure all changes are committed** on the `dev` branch.

2. **Bump the version** in the three canonical locations:
   - `APP_VERSION` in `app.py`
   - `"version"` in `package.json`
   - Replace `## [Unreleased]` in `CHANGELOG.md` with
     `## [x.y.z] — YYYY-MM-DD` and add a fresh `## [Unreleased]`
     above it

3. **Commit the version bump**:
   ```powershell
   git add -A
   git commit -m "release: x.y.z"
   ```

4. **Merge to `main` and tag**:
   ```powershell
   git checkout main
   git merge dev
   git tag -a vx.y.z -m "Librarium vx.y.z"
   git push origin main --tags
   git checkout dev
   ```

5. **Build the portable executable**:
   ```powershell
   npm run build
   ```

6. **Create a GitHub Release**:
   - Go to [Releases → Draft a new release](https://github.com/jqnoc/librarium/releases/new)
   - Select the `vx.y.z` tag
   - Title: `Librarium vx.y.z`
   - Paste the changelog entries for this version in the description
   - Drag and drop the `dist/Librarium x.y.z.exe` file into the assets
   - Check **Set as the latest release**
   - Click **Publish release**

## License

This project is licensed under the
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](LICENSE.md)
license.
# Librarium

[![GitHub Release](https://img.shields.io/github/v/release/jqnoc/librarium)](https://github.com/jqnoc/librarium/releases/latest)

A self-contained **Electron desktop application** for tracking personal
book reading statistics. The backend is a monolithic Flask app with raw
SQLite queries, Jinja2 templates, vanilla JS, and Chart.js for charts.
Electron spawns the Flask server as a child process and displays it in
a native frameless window.

All data — including cover images and author photos — is stored locally
in per-user SQLite databases. No external server or account required.

## Getting Started

### Prerequisites

- **Python 3.12+** with pip
- **Node.js 18+** with npm

### Installation

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (Electron)
npm install
```

### Running

```powershell
npm start
```

Or on Windows, double-click `run-librarium.bat`.

The app opens in its own Electron window. For backend-only development,
`python app.py` starts Flask on the port set by `LIBRARIUM_PORT` (or
`5000` by default).

## Features

### Library Management

- Add, edit, and organise books with cover images, metadata, and notes
- Three view modes: **card**, **cover**, and **list**
- Real-time search filter by title, subtitle, or author
- Filter and sort by status, tags, language, author, source, and series
- **Multi-library** support — checkbox selector lets any combination of
  libraries be active at once
- ISBN lookup via Open Library API to auto-fill metadata and cover
- Soft-delete with undo

### Multi-User System

- Multiple users, each with their own independent SQLite database
- User selection / creation screen on first launch
- Per-user migrations run automatically on startup

### Reading Tracking

- **Sessions**: log date, page range, and duration (hours / minutes / seconds)
- **Periods**: track date ranges without detailed session data; reading
  time is inferred from session averages
- **Re-reads**: start a new reading of the same book; each reading has its
  own sessions and periods

### Multi-Edition System

- Link multiple editions of the same work (e.g. hardcover + ebook)
- Mark one edition as primary — only the primary appears in library
  listings
- Unlink editions at any time

### Five Book Statuses

| Status | Colour |
|--------|--------|
| Reading | Blue (#3B82F6) |
| Finished | Green (#10B981) |
| Not Started | Purple (#8B5CF6) |
| Abandoned | Red (#DC2626) |
| Draft | Grey (#6B7280) |

### Rating System

51 dimensions across 9 groups, each rated 1–10:

1. **Emotional Impact** — heartfelt, tear, inspiring, melancholy,
   nostalgia, cathartic
2. **Story & Plot** — plot quality, predictability, pacing, plot twists,
   worldbuilding, character arc
3. **Writing & Style** — writing quality, vocabulary gain, dialogue,
   voice, symbolism, editorial quality
4. **Genre-Specific** — suspense, thrill, humor, romance, mystery, horror
5. **Engagement** — addiction, afterglow, rereadability, originality
6. **Intellectual** — thought-provoking, complexity, historical/cultural
   value, argumentation, clarity
7. **Non-Fiction** — research depth, accuracy, evidence, practicality,
   objectivity, relevance
8. **Visual Art** — art quality, character design, colour & inking,
   background art, cover art, visual consistency
9. **Sequential Narrative** — panel layout, visual storytelling, action
   choreography, expressiveness, text integration, splash pages

Overall score is the **grouped average**: average of each non-empty
group's average, so groups with fewer ratings are not under-weighted.

### Series

- Create named series and assign books with position numbers
- Many-to-many: a book can belong to multiple series
- Series list and detail pages with reading progress

### Authors

- Dedicated author pages with bio, gender, and photo (stored in DB)
- HEIF/AVIF photo support via pillow-heif
- Photo thumbnails for fast loading on list pages
- Authors are shared across all libraries

### Sources

- Track where books were acquired (bookshop, library, gift, etc.)
- Store name, type, city, country, URL, and notes for each source
- Sources are shared across all libraries

### Statistics

- **Global stats** (`/stats`): pages and books finished by year, time
  read by year, status breakdown pie chart, tag cloud, language /
  publisher / author bar charts, rating distribution (KDE), status
  timeline stacked area chart with absolute / relative toggle and
  time-range buttons
- **Yearly stats** (`/stats/year/<year>`): Gantt chart showing reading
  timelines per book, cumulative pages chart, per-book cumulative pages
- **Yearly books** (`/stats/year/<year>/books`): grid of books finished
  in a given year
- **Activity dashboard** (`/activity`): calendar heatmap, streak
  tracking, per-day and per-week reading activity

### Internationalisation

- **English** and **Spanish** — toggle from the navbar
- Translations in `static/i18n.js`, applied via `data-i18n` attributes
- Language preference persisted in `localStorage`

### Data Safety

- **Integrity check** on every startup; automatic restore from backup
  if the database is corrupted
- **Daily backups** using SQLite's Online Backup API (last 5 kept);
  configurable backup directory
- Shutdown overlay ensures a backup completes before quitting
- Database uses WAL mode for safe concurrent reads

## Data Storage

All application data is stored in the platform's standard application
data directory:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Librarium\` |
| macOS | `~/Library/Application Support/Librarium/` |
| Linux | `~/.local/share/Librarium/` (or `$XDG_DATA_HOME/Librarium/`) |

Each user has their own SQLite database named after their username
(e.g. user "JqnOC" → `jqnoc.db`). User accounts are tracked in
`users.json` inside the same directory. Cover images, author photos,
and thumbnails are stored as BLOBs in the database. No external
database server required.

On first run after upgrading from an older version, any existing
`data/` databases next to the application are automatically copied
to the new location.

## Project Structure

```
Librarium/
├── main.js                   # Electron main process
├── preload.js                # Electron preload (sandboxed renderer bridge)
├── package.json              # Node.js manifest (Electron dep, build config)
├── app.py                    # Entire Flask application (~5 000+ lines)
├── requirements.txt          # Python dependencies
├── run-librarium.bat         # Windows launcher
├── Librarium.vbs             # Silent Windows launcher (no console)
├── CHANGELOG.md              # Version history
├── LICENSE.md                # CC BY-NC-ND 4.0
├── README.md
├── .github/
│   └── copilot-instructions.md
├── static/
│   ├── style.css             # Stylesheet (layout, components)
│   ├── i18n.js               # EN / ES translations
│   ├── autocomplete.js       # Custom autocomplete dropdown
│   ├── splash.html           # Loading splash screen
│   ├── logo.png              # App icon (high-res)
│   ├── logo.svg              # App icon (vector)
│   ├── logo.ico              # App icon (ICO)
│   └── favicon.ico           # Browser favicon
├── templates/
│   ├── base.html             # Base layout (navbar, CDNs)
│   ├── index.html            # Library (card / cover / list views)
│   ├── book_detail.html      # Book detail, sessions, periods, ratings
│   ├── edit_metadata.html    # Edit book metadata form
│   ├── new_book.html         # Add book form
│   ├── stats.html            # Global statistics dashboard
│   ├── stats_year.html       # Yearly stats with Gantt charts
│   ├── stats_year_books.html # Books finished in a year
│   ├── activity.html         # Activity dashboard
│   ├── authors.html          # Authors list
│   ├── author_detail.html    # Author detail
│   ├── edit_author.html      # Edit author form
│   ├── sources.html          # Source management
│   ├── series.html           # Series list
│   ├── series_detail.html    # Series detail
│   └── users.html            # User selection / creation
```

User databases, `users.json`, and backups are stored in the platform's
application data directory (see [Data Storage](#data-storage)), not
inside the project folder.

## Technologies

| Layer | Technology |
|-------|-----------|
| Desktop shell | Electron 33.x, Node.js 18+ |
| Backend | Flask 3.x, Python 3.12+ |
| Database | SQLite (raw SQL, WAL mode) |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, vanilla JavaScript (ES6) |
| Charts | Chart.js 4.4.1 (CDN) + chartjs-adapter-date-fns |
| Images | Pillow 10.x, pillow-heif 0.16+ (HEIF/AVIF support) |

## Building & Releasing

### Build a portable Windows executable

```powershell
# Set environment variable to skip code signing (no certificate needed)
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"

# Build the portable .exe
npx electron-builder --win
```

The output is `dist/Librarium <version>.exe` — a single portable
executable that requires no installation.

### Create a new release

1. **Ensure all changes are committed** on the `dev` branch.

2. **Bump the version** in the three canonical locations:
   - `APP_VERSION` in `app.py`
   - `"version"` in `package.json`
   - Replace `## [Unreleased]` in `CHANGELOG.md` with
     `## [x.y.z] — YYYY-MM-DD` and add a fresh `## [Unreleased]`
     above it.

3. **Commit the version bump**:
   ```powershell
   git add -A
   git commit -m "release: x.y.z"
   ```

4. **Merge to `main` and tag**:
   ```powershell
   git checkout main
   git merge dev
   git tag -a vx.y.z -m "Librarium vx.y.z"
   git push origin main --tags
   git checkout dev
   ```

5. **Build the portable executable** (see above).

6. **Create a GitHub Release**:
   - Go to [Releases → Draft a new release](https://github.com/jqnoc/librarium/releases/new)
   - Select the `vx.y.z` tag
   - Title: `Librarium vx.y.z`
   - Paste the changelog entries for this version in the description
   - Drag and drop the `dist/Librarium x.y.z.exe` file into the assets
   - Check **Set as the latest release**
   - Click **Publish release**

## License

This project is licensed under the
[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](LICENSE.md)
license.

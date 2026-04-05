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

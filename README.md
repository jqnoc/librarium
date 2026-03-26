# Librarium

A Flask-based personal book reading tracker and statistics application.
Track books, sessions, ratings, series, authors, and reading habits —
all stored locally in a single SQLite database.

## Running the Project

### Prerequisites

- Python 3.12+
- pip

### Installation

```powershell
pip install -r requirements.txt
```

### Start the Application

```powershell
python app.py
```

Or on Windows, double-click `run-librarium.bat` to start the server and
open the browser automatically.

The application runs at **http://127.0.0.1:5000** (localhost only).

## Features

### Library Management

- Add, edit, and organise books with cover images, metadata, and notes
- Three view modes: **card**, **cover**, and **list**
- Filter and sort by status, genre, language, author, source, and series
- **Multi-library** support — create separate libraries and switch between
  them from the navbar
- Soft-delete with undo

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

39 dimensions across 7 groups, each rated 1–10:

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

Overall score is the **grouped average**: average of each non-empty
group's average, so groups with fewer ratings are not under-weighted.

### Series

- Create named series and assign books with position numbers
- Many-to-many: a book can belong to multiple series
- Series list and detail pages with reading progress

### Authors

- Dedicated author pages with bio and photo (stored in DB)
- HEIF/AVIF photo support via pillow-heif
- Browse all books by a specific author

### Sources

- Track where books were acquired (bookshop, library, gift, etc.)
- Store name, type, city, country, URL, and notes for each source

### Statistics

- **Global stats** (`/stats`): pages and books finished by year,
  status breakdown pie chart, genre / language / publisher / author bar
  charts, rating distribution (KDE), status timeline stacked area chart
  with absolute / relative toggle
- **Yearly stats** (`/stats/year/<year>`): Gantt chart showing reading
  timelines per book, cumulative pages chart, per-book cumulative pages
- **Yearly books** (`/stats/year/<year>/books`): grid of books finished
  in a given year
- **Activity dashboard** (`/activity`): calendar heatmap, streak
  tracking, per-day and per-week reading activity

### Theming

Six colour palettes, switchable from the navbar:

| Key | Name |
|-----|------|
| *(default)* | Orange |
| `green` | Mori |
| `hone` | Hone **(default)** |
| `kawara` | Kawara |
| `umi` | Umi |
| `hinode` | Hinode |

Palettes override CSS custom properties (prefixed `--lb-`). Chart
colours update automatically.

### Internationalisation

- **English** and **Spanish** — toggle from the navbar
- Translations in `static/i18n.js`, applied via `data-i18n` attributes
- Language preference persisted in `localStorage`

### Data Safety

- **Integrity check** on every startup; automatic restore from backup
  if the database is corrupted
- **Daily backups** using SQLite's Online Backup API (last 5 kept)
- Database uses WAL mode for safe concurrent reads

## Data Storage

All data — including cover images and author photos — lives in a single
SQLite file at `data/librarium.db`. No external database server required.

## Project Structure

```
Librarium/
├── app.py                    # Entire Flask application (~4 500+ lines)
├── requirements.txt          # Python dependencies
├── run-librarium.bat          # Windows launcher
├── README.md
├── .github/
│   └── copilot-instructions.md
├── static/
│   ├── style.css             # Stylesheet (6 palettes, layout, components)
│   └── i18n.js               # EN / ES translations
├── templates/
│   ├── base.html             # Base layout (navbar, palette switcher, CDNs)
│   ├── index.html            # Library (card / cover / list views)
│   ├── book_detail.html      # Book detail, sessions, periods, ratings
│   ├── edit_metadata.html    # Edit book form
│   ├── new_book.html         # Add book form
│   ├── stats.html            # Global statistics dashboard
│   ├── stats_year.html       # Yearly stats with Gantt charts
│   ├── stats_year_books.html # Books finished in a year
│   ├── activity.html         # Activity dashboard
│   ├── authors.html          # Authors list
│   ├── author_detail.html    # Author detail
│   ├── edit_author.html      # Edit author form
│   ├── sources.html          # Source management
│   └── series pages          # (rendered via series list/detail routes)
└── data/
    ├── librarium.db           # SQLite database (gitignored)
    └── backups/              # Automatic daily backups
```

## Technologies

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.x, Python 3.12+ |
| Database | SQLite (raw SQL, WAL mode) |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, vanilla JavaScript (ES6) |
| Charts | Chart.js 4.4.1 (CDN) + chartjs-adapter-date-fns |
| Images | Pillow 10.x, pillow-heif 0.16+ (HEIF/AVIF support) |

# Ashinami

A Flask-based personal book reading tracker and statistics application.

## Running the Project

### Prerequisites
- Python 3.12+
- Flask 3.1.2

### Installation

1. Navigate to the project directory:
```powershell
cd 'c:\Users\Joaquin\Joaquín Dropbox\JqnOC\Ashinami'
```

2. Install dependencies (optional, if not already installed):
```powershell
pip install -r requirements.txt
```

### Start the Application

Run the Flask development server:
```powershell
python app.py
```

The application will start on **http://127.0.0.1:5000**

Open your browser and navigate to that URL to access Ashinami.

## Features

- **Library Management**: Add, edit, and organize your book collection with multiple view modes (card, cover, list)
- **Reading Tracking**: Log reading sessions with date, pages read, and duration (hours/minutes/seconds)
- **Reading Periods**: Track date ranges of reading without detailed session logging; reading time is inferred from session averages
- **Statistics**: View cumulative and per-day reading progress charts, pages and books finished by year
- **Book Metadata**: Track author, publication dates, languages, ISBN, cover images, and other details
- **Rating System**: Multi-dimensional book ratings across 7 categories (Emotional Impact, Story & Plot, Writing & Style, etc.) with grouped averages
- **Source Management**: Maintain a database of places where you purchased or borrowed books
- **Status Tracking**: Categorize books as Reading, Finished, Not Started, or Abandoned
- **Author Pages**: Browse books grouped by author
- **Language Support**: Autocomplete for work and original languages with new language addition
- **Automatic Backups**: Daily database backup with integrity checks and automatic recovery

## Data Storage

All data (including cover images) is stored in a single SQLite database at `data/ashinami.db`. No external database server is required.

### Automatic Backups

Every time the application starts, a daily backup of the database is created in `data/backups/`. Only the last 5 backups are kept; older ones are automatically deleted. Backups use SQLite's Online Backup API, so they are always consistent even if the database is in use.

## Project Structure

```
Ashinami/
├── app.py              # Flask application and routes
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html          # Library page (card/cover/list views)
│   ├── book_detail.html    # Book detail, sessions, periods, ratings
│   ├── edit_metadata.html  # Edit book metadata
│   ├── new_book.html       # Add a new book
│   ├── sources.html        # Source management
│   ├── authors.html        # Authors list
│   ├── author_detail.html  # Books by a specific author
│   ├── stats.html          # Global reading statistics
│   ├── stats_year.html     # Yearly stats with charts
│   └── stats_year_books.html # Books finished in a year
├── static/
│   ├── style.css           # Stylesheet
│   ├── favicon.ico
│   ├── logo.png
│   └── logo.svg
└── data/               # Data storage
    ├── ashinami.db     # SQLite database
    └── backups/        # Daily automatic backups
```

## Technologies

- **Backend**: Flask 3.1.2
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Charts**: Chart.js 4.4.1 (CDN)
- **Storage**: SQLite (single-file database)
- **Python Version**: 3.12

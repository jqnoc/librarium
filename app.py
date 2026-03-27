"""Librarium – a local Flask app for tracking reading statistics.

All data (including cover images) is stored in a SQLite database
at data/librarium.db.
"""

import hashlib
import io
import json
import math
import os
import re
import shutil
import sqlite3
import uuid as uuid_module
from collections import Counter
from datetime import datetime, date
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()          # adds AVIF / HEIF support to Pillow

from flask import (
    Flask,
    Response,
    abort,
    flash,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "librarium.db"
BACKUP_DIR = DATA_DIR / "backups"
MAX_BACKUPS = 5

APP_VERSION = "0.1.0"

app = Flask(__name__)
app.secret_key = "librarium-local-dev-key"


# ── HTML sanitiser (allowlist-based) ───────────────────────────────────
_ALLOWED_TAGS = frozenset({
    'b', 'strong', 'i', 'em', 'u', 's', 'h4',
    'ul', 'ol', 'li', 'a', 'br', 'p',
})
_ALLOWED_ATTRS = {'a': frozenset({'href'})}


class _Sanitiser(HTMLParser):
    """Strip tags and attributes not on the allowlist."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in _ALLOWED_TAGS:
            return
        allowed = _ALLOWED_ATTRS.get(tag, frozenset())
        safe_attrs = []
        for k, v in attrs:
            if k in allowed:
                if k == 'href' and v:
                    v_check = v.strip().lower()
                    if v_check.startswith('javascript:'):
                        continue
                safe_attrs.append(f'{k}="{v}"')
        if safe_attrs:
            self._parts.append(f'<{tag} {" ".join(safe_attrs)}>')
        else:
            self._parts.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag in _ALLOWED_TAGS:
            self._parts.append(f'</{tag}>')

    def handle_data(self, data):
        from markupsafe import escape
        self._parts.append(str(escape(data)))

    def get_clean(self) -> str:
        return ''.join(self._parts)


def sanitize_html(raw: str) -> str:
    """Return *raw* with only safe HTML tags/attrs preserved."""
    s = _Sanitiser()
    s.feed(raw)
    return s.get_clean()


# ── Database Validation & Recovery ──────────────────────────────────────
def validate_and_restore_db() -> None:
    """Check database integrity at startup; restore from backup if corrupted.

    If the database file doesn't exist (first run), this is a no-op.
    If it exists but is corrupted, the latest backup is restored,
    overwriting the corrupted file.
    """
    if not DB_PATH.exists():
        return  # First run, database will be created by Flask

    try:
        # Try to open and verify the database
        db = sqlite3.connect(str(DB_PATH))
        # PRAGMA integrity_check returns 'ok' if healthy, error details otherwise
        result = db.execute("PRAGMA integrity_check").fetchone()
        db.close()
        if result[0] == "ok":
            return  # Database is healthy
    except Exception as e:
        print(f"⚠️  Database health check failed: {e}")

    # Database is corrupted; restore from latest backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backups = sorted(BACKUP_DIR.glob("librarium_*.db"))
    
    if not backups:
        print("⚠️  Database is corrupted but no backups available.")
        print("    Your database is at:", DB_PATH)
        print("    You may need to manually restore or reset.")
        return

    latest_backup = backups[-1]
    print(f"⚠️  Database corrupted. Restoring from: {latest_backup.name}")
    
    # Restore by copying the latest backup over the corrupted database
    # First, backup the corrupted file for analysis
    corrupted_file = DB_PATH.with_stem(DB_PATH.stem + "_corrupted")
    DB_PATH.rename(corrupted_file)
    print(f"    Corrupted database moved to: {corrupted_file.name}")
    
    # Restore from backup
    shutil.copy2(str(latest_backup), str(DB_PATH))
    print(f"    Restored successfully from {latest_backup.name}")


# ── Backup ───────────────────────────────────────────────────────────────
def backup_database(*, skip_if_recent: bool = True) -> str | None:
    """Create a timestamped backup of the database, keeping the last MAX_BACKUPS.

    Uses SQLite's Online Backup API so the copy is always consistent,
    even when the database is in WAL mode.
    Skips silently if the DB file does not exist yet.
    When *skip_if_recent* is True (startup call), skips if a backup from
    the current date already exists.  Manual calls pass False to always
    create a new backup.
    Returns the backup filename on success, or None if skipped.
    """
    if not DB_PATH.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if skip_if_recent:
        today_prefix = f"librarium_{date.today().isoformat()}"
        if any(BACKUP_DIR.glob(f"{today_prefix}*.db")):
            return None  # already backed up today

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f"librarium_{stamp}.db"

    # Use the Online Backup API for a safe, consistent copy
    src = sqlite3.connect(str(DB_PATH))
    dst = sqlite3.connect(str(backup_file))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    # Prune old backups – keep only the most recent MAX_BACKUPS files
    backups = sorted(BACKUP_DIR.glob("librarium_*.db"))
    for old in backups[:-MAX_BACKUPS]:
        old.unlink()

    return backup_file.name


# ── Migration: Add readings table ───────────────────────────────────────
def migrate_add_readings() -> None:
    """Add the readings table and link all existing sessions/periods."""
    if not DB_PATH.exists():
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=OFF")  # off during migration

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "readings" in tables:
        db.close()
        return

    print("⏳ Migrating: adding readings table …")

    db.execute("""
        CREATE TABLE readings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id        TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            reading_number INTEGER NOT NULL DEFAULT 1,
            status         TEXT    NOT NULL DEFAULT 'reading',
            notes          TEXT    NOT NULL DEFAULT ''
        )
    """)

    # Add reading_id to sessions and periods
    db.execute(
        "ALTER TABLE sessions ADD COLUMN reading_id INTEGER "
        "REFERENCES readings(id) ON DELETE SET NULL"
    )
    db.execute(
        "ALTER TABLE periods ADD COLUMN reading_id INTEGER "
        "REFERENCES readings(id) ON DELETE SET NULL"
    )

    # Create one reading per book and link existing data
    all_books = db.execute("SELECT id, status FROM books").fetchall()
    for book in all_books:
        book_id = book["id"]
        status = book["status"] or "reading"
        db.execute(
            "INSERT INTO readings (book_id, reading_number, status) VALUES (?, 1, ?)",
            (book_id, status),
        )
        reading_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.execute("UPDATE sessions SET reading_id = ? WHERE book_id = ?",
                   (reading_id, book_id))
        db.execute("UPDATE periods  SET reading_id = ? WHERE book_id = ?",
                   (reading_id, book_id))

    db.commit()
    db.close()
    print("✅ Migration complete – readings table created.")


# ── Migration: Add authors table ────────────────────────────────────────
def migrate_add_authors() -> None:
    """Add the authors table for storing author metadata & photos."""
    if not DB_PATH.exists():
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "authors" in tables:
        db.close()
        return

    print("⏳ Migrating: adding authors table …")
    db.execute("""
        CREATE TABLE authors (
            name        TEXT PRIMARY KEY,
            photo       BLOB,
            has_photo   INTEGER NOT NULL DEFAULT 0,
            birth_date  TEXT NOT NULL DEFAULT '',
            birth_place TEXT NOT NULL DEFAULT '',
            death_date  TEXT NOT NULL DEFAULT '',
            death_place TEXT NOT NULL DEFAULT '',
            biography   TEXT NOT NULL DEFAULT ''
        )
    """)
    db.commit()
    db.close()
    print("✅ Migration complete – authors table created.")


# ── Migration: Add cover_color column ───────────────────────────────────
def migrate_add_cover_color() -> None:
    """Add cover_color column to books and backfill from existing covers."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "cover_color" in cols:
        db.close()
        return
    print("⏳ Migrating: adding cover_color column …")
    db.execute("ALTER TABLE books ADD COLUMN cover_color TEXT NOT NULL DEFAULT ''")
    # Back-fill colours for existing covers
    rows = db.execute("SELECT id, cover FROM books WHERE has_cover = 1").fetchall()
    for row in rows:
        color = _extract_dominant_color(row["cover"])
        if color:
            db.execute("UPDATE books SET cover_color = ? WHERE id = ?", (color, row["id"]))
    db.commit()
    db.close()
    print("✅ Migration complete – cover_color column added.")


# ── Migration: Add cover_palette column ───────────────────────────────
def migrate_add_cover_palette() -> None:
    """Add cover_palette column to books and backfill from existing covers."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "cover_palette" in cols:
        db.close()
        return
    print("⏳ Migrating: adding cover_palette column …")
    db.execute("ALTER TABLE books ADD COLUMN cover_palette TEXT NOT NULL DEFAULT '[]'")
    rows = db.execute("SELECT id, cover FROM books WHERE has_cover = 1").fetchall()
    for row in rows:
        palette = _extract_cover_palette(row["cover"])
        db.execute("UPDATE books SET cover_palette = ? WHERE id = ?",
                   (json.dumps(palette), row["id"]))
    db.commit()
    db.close()
    print("✅ Migration complete – cover_palette column added.")


# ── Migration: Add cover_hash column ────────────────────────────────────
def migrate_add_cover_hash() -> None:
    """Add cover_hash column to books and backfill from existing covers."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "cover_hash" in cols:
        db.close()
        return
    print("⏳ Migrating: adding cover_hash column …")
    db.execute("ALTER TABLE books ADD COLUMN cover_hash TEXT NOT NULL DEFAULT ''")
    rows = db.execute("SELECT id, cover FROM books WHERE has_cover = 1").fetchall()
    for row in rows:
        if row["cover"]:
            h = hashlib.md5(row["cover"]).hexdigest()[:12]
            db.execute("UPDATE books SET cover_hash = ? WHERE id = ?", (h, row["id"]))
    db.commit()
    db.close()
    print("✅ Migration complete – cover_hash column added.")


# ── Migration: Add photo_hash column to authors ─────────────────────────
def migrate_add_photo_hash() -> None:
    """Add photo_hash column to authors and backfill from existing photos."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(authors)").fetchall()]
    if "photo_hash" in cols:
        db.close()
        return
    print("⏳ Migrating: adding photo_hash column …")
    db.execute("ALTER TABLE authors ADD COLUMN photo_hash TEXT NOT NULL DEFAULT ''")
    rows = db.execute("SELECT name, photo FROM authors WHERE has_photo = 1").fetchall()
    for row in rows:
        if row["photo"]:
            h = hashlib.md5(row["photo"]).hexdigest()[:12]
            db.execute("UPDATE authors SET photo_hash = ? WHERE name = ?", (h, row["name"]))
    db.commit()
    db.close()
    print("✅ Migration complete – photo_hash column added.")


# ── Migration: Add subtitle column ──────────────────────────────────────
def migrate_add_subtitle() -> None:
    """Add subtitle column to books table."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "subtitle" in cols:
        db.close()
        return
    print("⏳ Migrating: adding subtitle column …")
    db.execute("ALTER TABLE books ADD COLUMN subtitle TEXT NOT NULL DEFAULT ''")
    db.commit()
    db.close()
    print("✅ Migration complete – subtitle column added.")


# ── Migration: Add libraries table ──────────────────────────────────────
def migrate_add_libraries() -> None:
    """Add multi-library support: libraries table + library_id on data tables."""
    if not DB_PATH.exists():
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=OFF")

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "libraries" in tables:
        db.close()
        return

    print("⏳ Migrating: adding multi-library support …")

    # 1. Create libraries table
    db.execute("""
        CREATE TABLE libraries (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE
        )
    """)

    # 2. Insert default "Books" library
    db.execute("INSERT INTO libraries (name, slug) VALUES ('Books', 'books')")
    default_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    # 3. Add library_id to books and sources
    db.execute(
        "ALTER TABLE books ADD COLUMN library_id INTEGER NOT NULL DEFAULT %d"
        " REFERENCES libraries(id)" % default_id
    )
    db.execute(
        "ALTER TABLE sources ADD COLUMN library_id INTEGER NOT NULL DEFAULT %d"
        " REFERENCES libraries(id)" % default_id
    )

    # 4. Recreate authors with (name, library_id) composite PK
    db.execute("""
        CREATE TABLE authors_new (
            name        TEXT NOT NULL,
            library_id  INTEGER NOT NULL REFERENCES libraries(id),
            photo       BLOB,
            has_photo   INTEGER NOT NULL DEFAULT 0,
            birth_date  TEXT NOT NULL DEFAULT '',
            birth_place TEXT NOT NULL DEFAULT '',
            death_date  TEXT NOT NULL DEFAULT '',
            death_place TEXT NOT NULL DEFAULT '',
            biography   TEXT NOT NULL DEFAULT '',
            photo_hash  TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (name, library_id)
        )
    """)
    db.execute(
        "INSERT INTO authors_new "
        "(name, library_id, photo, has_photo, birth_date, birth_place, "
        "death_date, death_place, biography, photo_hash) "
        "SELECT name, %d, photo, has_photo, birth_date, birth_place, "
        "death_date, death_place, biography, photo_hash FROM authors" % default_id
    )
    db.execute("DROP TABLE authors")
    db.execute("ALTER TABLE authors_new RENAME TO authors")

    db.commit()
    db.close()
    print("✅ Migration complete – multi-library support added.")


# ── Migration: Add series table ─────────────────────────────────────────
def migrate_add_series() -> None:
    """Add series table and series_id/series_index columns to books."""
    if not DB_PATH.exists():
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "series" not in tables:
        print("⏳ Migrating: adding series table …")
        db.execute("""
            CREATE TABLE series (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                library_id INTEGER NOT NULL REFERENCES libraries(id),
                UNIQUE(name, library_id)
            )
        """)
        db.commit()
        print("✅ Migration complete – series table created.")

    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "series_id" not in cols:
        print("⏳ Migrating: adding series columns to books …")
        db.execute("ALTER TABLE books ADD COLUMN series_id INTEGER REFERENCES series(id) ON DELETE SET NULL")
        db.execute("ALTER TABLE books ADD COLUMN series_index TEXT NOT NULL DEFAULT ''")
        db.commit()
        print("✅ Migration complete – series columns added to books.")

    db.close()


# ── Migration: Add book_series junction table (many-to-many) ────────────
def migrate_book_series_m2m() -> None:
    """Create book_series junction table and migrate data from books columns."""
    if not DB_PATH.exists():
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "book_series" not in tables:
        print("⏳ Migrating: creating book_series junction table …")
        db.execute("""
            CREATE TABLE book_series (
                book_id   TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
                series_index TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (book_id, series_id)
            )
        """)
        # Migrate existing data from books.series_id / books.series_index
        db.execute("""
            INSERT OR IGNORE INTO book_series (book_id, series_id, series_index)
            SELECT id, series_id, COALESCE(series_index, '')
            FROM books
            WHERE series_id IS NOT NULL
        """)
        db.commit()
        print("✅ Migration complete – book_series junction table created.")

    db.close()


def migrate_add_editions() -> None:
    """Add work_id and is_primary_edition columns to books for multi-edition support."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "work_id" in cols:
        db.close()
        return
    print("⏳ Migrating: adding edition columns to books …")
    db.execute("ALTER TABLE books ADD COLUMN work_id TEXT DEFAULT NULL")
    db.execute("ALTER TABLE books ADD COLUMN is_primary_edition INTEGER NOT NULL DEFAULT 1")
    db.commit()
    db.close()
    print("✅ Migration complete – edition columns added.")


def migrate_add_format() -> None:
    """Add format, binding, and audio_format columns to books."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "format" in cols:
        db.close()
        return
    print("⏳ Migrating: adding format columns to books …")
    db.execute("ALTER TABLE books ADD COLUMN format TEXT DEFAULT 'paper'")
    db.execute("ALTER TABLE books ADD COLUMN binding TEXT DEFAULT NULL")
    db.execute("ALTER TABLE books ADD COLUMN audio_format TEXT DEFAULT NULL")
    db.commit()
    db.close()
    print("✅ Migration complete – format columns added.")


def migrate_add_total_time() -> None:
    """Add total_time_seconds to books, progress_pct to sessions and periods."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    book_cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    sess_cols = [r[1] for r in db.execute("PRAGMA table_info(sessions)").fetchall()]
    per_cols  = [r[1] for r in db.execute("PRAGMA table_info(periods)").fetchall()]
    needed = False
    if "total_time_seconds" not in book_cols:
        needed = True
    if "progress_pct" not in sess_cols:
        needed = True
    if "progress_pct" not in per_cols:
        needed = True
    if not needed:
        db.close()
        return
    print("⏳ Migrating: adding total_time_seconds / progress_pct …")
    if "total_time_seconds" not in book_cols:
        db.execute("ALTER TABLE books ADD COLUMN total_time_seconds INTEGER DEFAULT NULL")
    if "progress_pct" not in sess_cols:
        db.execute("ALTER TABLE sessions ADD COLUMN progress_pct REAL DEFAULT NULL")
    if "progress_pct" not in per_cols:
        db.execute("ALTER TABLE periods ADD COLUMN progress_pct REAL DEFAULT NULL")
    db.commit()
    db.close()
    print("✅ Migration complete – total_time_seconds / progress_pct added.")


def migrate_add_period_duration() -> None:
    """Add duration_seconds to periods for audiobook/ebook time tracking."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    per_cols = [r[1] for r in db.execute("PRAGMA table_info(periods)").fetchall()]
    if "duration_seconds" in per_cols:
        db.close()
        return
    print("⏳ Migrating: adding duration_seconds to periods …")
    db.execute("ALTER TABLE periods ADD COLUMN duration_seconds INTEGER DEFAULT NULL")
    db.commit()
    db.close()
    print("✅ Migration complete – duration_seconds added to periods.")


# ── Cover colour helper ─────────────────────────────────────────────────
def _extract_cover_palette(cover_blob: bytes | None, n: int = 10) -> list[str]:
    """Return up to *n* diverse dominant colours from a cover image.

    1.  Quantise the image to find candidate colours, filtering out
        near-black / near-white by luminance.
    2.  Seed the palette with the single most frequent candidate.
    3.  Iteratively pick the candidate that maximises its minimum
        Euclidean distance (in RGB space) to every colour already in
        the palette.  This ensures visual diversity.
    """
    if not cover_blob:
        return []
    try:
        img = Image.open(io.BytesIO(cover_blob)).convert("RGB")
        img = img.resize((50, 50), Image.LANCZOS)
        pixels = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())
        quantised = [((r >> 4) << 4, (g >> 4) << 4, (b >> 4) << 4) for r, g, b in pixels]
        if not quantised:
            return ["#888888"]

        # Build candidate list (unique colours, luminance-filtered)
        ranking = Counter(quantised).most_common()
        candidates: list[tuple[int, int, int]] = []
        seen: set[tuple[int, int, int]] = set()
        for color, _count in ranking:
            if color in seen:
                continue
            seen.add(color)
            r, g, b = color
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            if luminance < 55 or luminance > 210:
                continue
            candidates.append(color)

        if not candidates:
            # All colours too dark/light – just use the most common
            return ["#{:02x}{:02x}{:02x}".format(*ranking[0][0])]

        # Greedy farthest-point sampling for diversity
        palette_rgb: list[tuple[int, int, int]] = [candidates[0]]
        remaining = set(range(1, len(candidates)))

        while len(palette_rgb) < n and remaining:
            best_idx = -1
            best_dist = -1.0
            for idx in remaining:
                c = candidates[idx]
                # Minimum distance to any colour already chosen
                min_d = min(
                    (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2 + (c[2] - p[2]) ** 2
                    for p in palette_rgb
                )
                if min_d > best_dist:
                    best_dist = min_d
                    best_idx = idx
            if best_idx < 0:
                break
            palette_rgb.append(candidates[best_idx])
            remaining.discard(best_idx)

        return ["#{:02x}{:02x}{:02x}".format(*c) for c in palette_rgb]
    except Exception:
        return ["#888888"]


def _extract_dominant_color(cover_blob: bytes | None) -> str:
    """Return the best dominant colour of a cover image as '#RRGGBB'."""
    palette = _extract_cover_palette(cover_blob, n=1)
    return palette[0] if palette else "#888888"


# ── Database helpers ─────────────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    """Return a per-request database connection (cached on ``g``)."""
    if "db" not in g:
        g.db = sqlite3.connect(str(DB_PATH))
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ── Library helpers ──────────────────────────────────────────────────────
def _get_current_library_id() -> int:
    """Return the active library ID from cookie, falling back to the first library."""
    raw = request.cookies.get("librarium_library", "")
    if raw:
        try:
            lib_id = int(raw)
            db = get_db()
            if db.execute("SELECT 1 FROM libraries WHERE id = ?", (lib_id,)).fetchone():
                return lib_id
        except (ValueError, TypeError):
            pass
    db = get_db()
    row = db.execute("SELECT id FROM libraries ORDER BY id LIMIT 1").fetchone()
    return row["id"] if row else 1


@app.context_processor
def inject_library_context():
    """Make current_library and all_libraries available in every template."""
    try:
        db = get_db()
        lib_id = _get_current_library_id()
        current_lib = db.execute(
            "SELECT * FROM libraries WHERE id = ?", (lib_id,)
        ).fetchone()
        all_libs = db.execute(
            "SELECT * FROM libraries ORDER BY id"
        ).fetchall()
        return {
            "current_library": dict(current_lib) if current_lib else {"id": 1, "name": "Books", "slug": "books"},
            "all_libraries": [dict(l) for l in all_libs],
            "app_version": APP_VERSION,
        }
    except Exception:
        return {
            "current_library": {"id": 1, "name": "Books", "slug": "books"},
            "all_libraries": [],
            "app_version": APP_VERSION,
        }


# ── Rating dimensions ────────────────────────────────────────────────────
RATING_DIMENSIONS = [
    {
        "group": "Emotional Impact",
        "items": [
            {"key": "heartfelt",  "label": "Heartfelt",  "tip": "Emotional depth, emotional connection"},
            {"key": "tear",       "label": "Tear",       "tip": "Emotional impact, tear-jerking moments"},
            {"key": "inspiring",  "label": "Inspiring",  "tip": "Motivational, uplifting"},
            {"key": "melancholy", "label": "Melancholy", "tip": "Sadness, dark emotions"},
            {"key": "nostalgia",  "label": "Nostalgia",  "tip": "Bittersweet, reminiscent feelings"},
            {"key": "cathartic",  "label": "Cathartic",  "tip": "Cleansing, emotionally releasing"},
        ],
    },
    {
        "group": "Story & Plot",
        "items": [
            {"key": "plot_quality",  "label": "Plot Quality",  "tip": "Narrative strength, coherence"},
            {"key": "predictability","label": "Predictability","tip": "How surprising / unpredictable"},
            {"key": "pacing",        "label": "Pacing",        "tip": "Flow, speed of story progression"},
            {"key": "plot_twists",   "label": "Plot Twists",   "tip": "Unexpected turns and surprises"},
            {"key": "worldbuilding", "label": "Worldbuilding", "tip": "Immersive setting construction"},
            {"key": "character_arc", "label": "Character Arc", "tip": "Character growth and development"},
        ],
    },
    {
        "group": "Writing & Style",
        "items": [
            {"key": "writing_quality","label": "Writing Quality","tip": "Prose, descriptions, language"},
            {"key": "vocabulary_gain","label": "Vocabulary Gain","tip": "How many new words/expressions you learned"},
            {"key": "dialogue",      "label": "Dialogue",      "tip": "Quality and naturalness of conversations"},
            {"key": "voice",         "label": "Voice",         "tip": "Author's distinct narrative voice"},
            {"key": "symbolism",     "label": "Symbolism",     "tip": "Deeper meanings, literary depth"},
            {"key": "editorial_quality","label": "Editorial Quality","tip": "Grammar/orthography errors; textual cleanliness"},
        ],
    },
    {
        "group": "Genre-Specific",
        "items": [
            {"key": "suspense", "label": "Suspense", "tip": "Tension, mystery"},
            {"key": "thrill",   "label": "Thrill",   "tip": "Action, excitement, adrenaline"},
            {"key": "humor",    "label": "Humor",    "tip": "Comedy, wit, funny moments"},
            {"key": "romance",  "label": "Romance",  "tip": "Romantic elements and chemistry"},
            {"key": "mystery",  "label": "Mystery",  "tip": "Engaging puzzle / mystery elements"},
            {"key": "horror",   "label": "Horror",   "tip": "Fear, dread, scary elements"},
        ],
    },
    {
        "group": "Engagement",
        "items": [
            {"key": "addiction",    "label": "Addiction",    "tip": "Page-turner, couldn't put it down"},
            {"key": "afterglow",     "label": "Afterglow",     "tip": "How long it lingered in your mind after reading"},
            {"key": "rereadability","label": "Rereadability","tip": "Worth reading again"},
            {"key": "originality",  "label": "Originality",  "tip": "Uniqueness, freshness"},
        ],
    },
    {
        "group": "Intellectual",
        "items": [
            {"key": "thought_provoking",      "label": "Thought-Provoking",      "tip": "Philosophical, makes you think"},
            {"key": "complexity",              "label": "Complexity",              "tip": "Intellectual challenge"},
            {"key": "historical_cultural_value","label": "Historical / Cultural Value","tip": "Educational content"},
            {"key": "argumentation",  "label": "Argumentation",  "tip": "Strength of arguments and reasoning"},
            {"key": "clarity",        "label": "Clarity",        "tip": "How well complex ideas are explained"},
        ],
    },
    {
        "group": "Non-Fiction",
        "items": [
            {"key": "research_depth", "label": "Research Depth", "tip": "Thoroughness of the author's research"},
            {"key": "accuracy",       "label": "Accuracy",       "tip": "Factual correctness and reliability"},
            {"key": "evidence",       "label": "Evidence",       "tip": "Quality of supporting data, sources, citations"},
            {"key": "practicality",   "label": "Practicality",   "tip": "Actionable takeaways, real-world applicability"},
            {"key": "objectivity",    "label": "Objectivity",    "tip": "Balanced perspective, fairness"},
            {"key": "relevance",      "label": "Relevance",      "tip": "Timeliness and current applicability"},
        ],
    },
]


def _get_current_reading_id(db, book_id: str) -> int:
    """Return the latest reading ID for a book, creating one if needed."""
    row = db.execute(
        "SELECT id FROM readings WHERE book_id = ? ORDER BY reading_number DESC LIMIT 1",
        (book_id,),
    ).fetchone()
    if row:
        return row["id"]
    # Auto-create reading #1
    book = db.execute("SELECT status FROM books WHERE id = ?", (book_id,)).fetchone()
    status = book["status"] if book else "reading"
    db.execute(
        "INSERT INTO readings (book_id, reading_number, status) VALUES (?, 1, ?)",
        (book_id, status),
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def _load_ratings(book_id: str) -> dict:
    """Load ratings for a book from the database."""
    db = get_db()
    rows = db.execute(
        "SELECT dimension_key, value FROM ratings WHERE book_id = ?", (book_id,)
    ).fetchall()
    return {r["dimension_key"]: r["value"] for r in rows}


def _save_ratings(book_id: str, ratings: dict) -> None:
    """Save ratings for a book (replace all)."""
    db = get_db()
    db.execute("DELETE FROM ratings WHERE book_id = ?", (book_id,))
    for key, val in ratings.items():
        if isinstance(val, (int, float)) and val > 0:
            db.execute(
                "INSERT INTO ratings (book_id, dimension_key, value) VALUES (?,?,?)",
                (book_id, key, int(val)),
            )
    db.commit()


def _calc_avg_rating(ratings: dict) -> float | None:
    """Return the grouped average: average of each non-empty group's average."""
    group_avgs = []
    for group in RATING_DIMENSIONS:
        values = [
            ratings[item["key"]]
            for item in group["items"]
            if isinstance(ratings.get(item["key"]), (int, float)) and ratings[item["key"]] > 0
        ]
        if values:
            group_avgs.append(sum(values) / len(values))
    if not group_avgs:
        return None
    avg = sum(group_avgs) / len(group_avgs)
    return math.floor(avg * 100 + 0.5) / 100  # round half-up (matches JS)


# ── Template filters ─────────────────────────────────────────────────────
@app.template_filter('format_status')
def format_status_filter(status: str) -> str:
    """Format status for display (e.g., 'not-started' -> 'Not Started')."""
    return status.replace('-', ' ').title()


@app.template_filter('format_authors')
def format_authors_filter(value: str) -> str:
    """Format semicolon-separated authors for display."""
    parts = [a.strip() for a in value.split(';') if a.strip()]
    if len(parts) <= 1:
        return value
    return ', '.join(parts[:-1]) + ' and ' + parts[-1]


@app.template_filter('date_ddmmyyyy')
def date_ddmmyyyy_filter(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass
    return raw


# ── Utility helpers ──────────────────────────────────────────────────────
def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")


def _format_duration(seconds: int) -> str:
    """Convert seconds to human-readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def _format_duration_long(seconds: int) -> str:
    """Convert seconds to human-readable format with days for large totals."""
    days = seconds // 86400
    remainder = seconds % 86400
    hours = remainder // 3600
    minutes = (remainder % 3600) // 60
    secs = remainder % 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def _normalize_input_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return value


def _collect_languages() -> list[str]:
    """Return a sorted list of unique languages used in the current library."""
    db = get_db()
    lib_id = _get_current_library_id()
    langs: set[str] = set()
    for row in db.execute("SELECT language, original_language FROM books WHERE library_id = ?", (lib_id,)).fetchall():
        for val in (row["language"], row["original_language"]):
            if val and val.strip():
                langs.add(val.strip())
    return sorted(langs)


def _collect_field_values(*fields: str) -> dict[str, list[str]]:
    """Scan books in the current library and return unique values per field."""
    db = get_db()
    lib_id = _get_current_library_id()
    # Only query the columns we need
    safe_fields = [f for f in fields if re.match(r'^[a-z_]+$', f)]
    if not safe_fields:
        return {}
    cols = ", ".join(safe_fields)
    rows = db.execute(f"SELECT {cols} FROM books WHERE library_id = ?", (lib_id,)).fetchall()
    buckets: dict[str, set[str]] = {f: set() for f in safe_fields}
    for row in rows:
        for f in safe_fields:
            raw = (row[f] or "").strip()
            if raw:
                for part in raw.split(";"):
                    part = part.strip()
                    if part:
                        buckets[f].add(part)
    return {f: sorted(vals) for f, vals in buckets.items()}


# ── Edition helpers ──────────────────────────────────────────────────────
def _get_work_id(book: dict) -> str:
    """Return the effective work ID for a book (its work_id or its own id if standalone)."""
    return book.get("work_id") or book["id"]


def _get_editions(db, work_id: str) -> list[dict]:
    """Return all editions that share the given work_id, primary first."""
    rows = db.execute(
        "SELECT id, name, subtitle, language, publisher, pages, has_cover, cover_hash, is_primary_edition "
        "FROM books WHERE work_id = ? ORDER BY is_primary_edition DESC, name COLLATE NOCASE",
        (work_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _get_primary_edition(db, work_id: str) -> dict | None:
    """Return the primary edition row for a work_id, or None."""
    row = db.execute(
        "SELECT * FROM books WHERE work_id = ? AND is_primary_edition = 1 LIMIT 1",
        (work_id,),
    ).fetchone()
    return dict(row) if row else None


# ── Source helpers ───────────────────────────────────────────────────────
SOURCE_TYPES = {
    "physical_store": "Physical Store",
    "web_store": "Web Store",
    "library": "Library",
    "person": "Person",
}
PURCHASE_SOURCE_TYPES = {"physical_store", "web_store"}
BORROW_SOURCE_TYPES = {"library", "person"}
GIFT_SOURCE_TYPES = {"person"}


@app.template_filter('source_type_label')
def source_type_label_filter(type_key: str) -> str:
    return SOURCE_TYPES.get(type_key, type_key)


def _get_source_by_id(source_id: str) -> dict | None:
    """Look up a source by its ID."""
    db = get_db()
    row = db.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    if row:
        return dict(row)
    return None


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Catalog (Library)
# ═══════════════════════════════════════════════════════════════════════════


def _build_index_per_reading(db, lib_id):
    """Build one library entry per *selected reading* across ALL editions.

    Selection logic per edition:
    - 1 reading  → show it
    - >1 readings, some finished → show each finished one
    - >1 readings, none finished → show the one with highest priority
      (reading > abandoned > not-started > draft)
    """
    book_rows = db.execute(
        "SELECT id, name, subtitle, author, status, pages, starting_page, genre, "
        "has_cover, cover_hash, publisher, language, publication_date, "
        "work_id, format, total_time_seconds FROM books WHERE library_id = ?",
        (lib_id,),
    ).fetchall()
    bk_map = {r["id"]: dict(r) for r in book_rows}
    bids = list(bk_map.keys())
    if not bids:
        return []

    ph = ",".join("?" * len(bids))
    all_readings = db.execute(
        f"SELECT id, book_id, reading_number, status FROM readings "
        f"WHERE book_id IN ({ph}) ORDER BY book_id, reading_number", bids
    ).fetchall()
    readings_by_book: dict[str, list] = {}
    for r in all_readings:
        readings_by_book.setdefault(r["book_id"], []).append(dict(r))

    RPRIO = {"reading": 0, "abandoned": 1, "not-started": 2, "draft": 3, "finished": 4}
    selected: list[tuple] = []  # (book_id, reading_id, reading_number, status)
    for bid in bids:
        rlist = readings_by_book.get(bid, [])
        if not rlist:
            selected.append((bid, None, None, bk_map[bid]["status"]))
            continue
        if len(rlist) == 1:
            r = rlist[0]
            selected.append((bid, r["id"], r["reading_number"], r["status"]))
        else:
            finished = [r for r in rlist if r["status"] == "finished"]
            if finished:
                for r in finished:
                    selected.append((bid, r["id"], r["reading_number"], r["status"]))
            else:
                best = min(rlist, key=lambda r: RPRIO.get(r["status"], 99))
                selected.append((bid, best["id"], best["reading_number"], best["status"]))

    # Bulk-fetch per-reading stats
    rids = [s[1] for s in selected if s[1] is not None]
    sess_map: dict[int, dict] = {}
    per_map: dict[int, dict] = {}
    pct_map: dict[int, float] = {}
    if rids:
        rph = ",".join("?" * len(rids))
        for row in db.execute(
            f"SELECT reading_id, SUM(pages) AS tp, SUM(duration_seconds) AS ts, "
            f"COUNT(DISTINCT date) AS rd, MIN(date) AS d0, MAX(date) AS d1 "
            f"FROM sessions WHERE reading_id IN ({rph}) AND date != '' "
            f"GROUP BY reading_id", rids
        ).fetchall():
            sess_map[row["reading_id"]] = dict(row)
        for row in db.execute(
            f"SELECT reading_id, SUM(pages) AS pp, "
            f"MIN(start_date) AS p0, MAX(end_date) AS p1 "
            f"FROM periods WHERE reading_id IN ({rph}) "
            f"GROUP BY reading_id", rids
        ).fetchall():
            per_map[row["reading_id"]] = dict(row)
        for row in db.execute(
            f"SELECT reading_id, MAX(pct) AS max_pct FROM ("
            f"SELECT reading_id, MAX(progress_pct) AS pct FROM sessions "
            f"WHERE reading_id IN ({rph}) AND progress_pct IS NOT NULL GROUP BY reading_id "
            f"UNION ALL "
            f"SELECT reading_id, MAX(progress_pct) AS pct FROM periods "
            f"WHERE reading_id IN ({rph}) AND progress_pct IS NOT NULL GROUP BY reading_id"
            f") GROUP BY reading_id", rids + rids
        ).fetchall():
            pct_map[row["reading_id"]] = row["max_pct"] or 0

    books = []
    for bid, rid, rnum, rstatus in selected:
        bk = bk_map[bid]
        sm = sess_map.get(rid, {}) if rid else {}
        pm = per_map.get(rid, {}) if rid else {}

        session_pages = sm.get("tp", 0) or 0
        session_seconds = sm.get("ts", 0) or 0
        reading_days = sm.get("rd", 0) or 0
        first_date = sm.get("d0", "") or ""
        last_date = sm.get("d1", "") or ""
        period_pages = pm.get("pp", 0) or 0
        first_period_start = pm.get("p0", "") or ""
        last_period_end = pm.get("p1", "") or ""
        max_pct = pct_map.get(rid, 0) if rid else 0

        period_seconds = 0
        if period_pages > 0 and session_pages > 0:
            period_seconds = int(period_pages * (session_seconds / session_pages))
        total_pages_display = session_pages + period_pages
        total_seconds_display = session_seconds + period_seconds

        starting_page = bk.get("starting_page", 0) or 0
        total_book_pages = bk.get("pages", 0) or 0
        effective_pages = total_book_pages - starting_page if starting_page > 0 else total_book_pages

        first_candidates = [d for d in (first_date, first_period_start) if d]
        last_candidates = [d for d in (last_date, last_period_end) if d]
        first_activity = min(first_candidates) if first_candidates else None
        last_activity = max(last_candidates) if last_candidates else None

        ratings = _load_ratings(bid)

        edition_count = 1
        if bk["work_id"]:
            ec_row = db.execute("SELECT COUNT(*) AS c FROM books WHERE work_id = ?", (bk["work_id"],)).fetchone()
            edition_count = ec_row["c"] if ec_row else 1

        book_fmt = bk.get("format", "paper") or "paper"
        is_pct_fmt = book_fmt in ("audiobook", "ebook")

        books.append({
            "id": bid,
            "name": bk["name"],
            "subtitle": bk.get("subtitle", "") or "",
            "author": bk.get("author", "") or "",
            "status": rstatus or "reading",
            "pages": bk.get("pages", 0) or 0,
            "effective_pages": effective_pages,
            "pages_read": total_pages_display,
            "max_progress_pct": max_pct,
            "is_pct_format": is_pct_fmt,
            "format": book_fmt,
            "total_time_seconds": bk.get("total_time_seconds", 0) or 0,
            "total_time": _format_duration(total_seconds_display),
            "total_seconds_raw": total_seconds_display,
            "reading_days": reading_days,
            "genre": bk.get("genre", "") or "",
            "has_cover": bool(bk.get("has_cover")),
            "cover_hash": bk.get("cover_hash", "") or "",
            "first_session_date": first_activity or "0000-00-00",
            "last_session_date": last_activity or "0000-00-00",
            "avg_rating": _calc_avg_rating(ratings),
            "publisher": bk.get("publisher", "") or "",
            "language": bk.get("language", "") or "",
            "publication_date": bk.get("publication_date", "") or "",
            "edition_count": edition_count,
            "reading_number": rnum,
        })

    # Only show reading_number when a book appears more than once
    from collections import Counter
    bid_counts = Counter(b["id"] for b in books)
    for b in books:
        if bid_counts[b["id"]] <= 1:
            b["reading_number"] = None

    return books


@app.route("/")
def index():
    """Main page – list all books in the current library."""
    db = get_db()
    lib_id = _get_current_library_id()
    # Use query params if present, otherwise fall back to cookie, then default
    sort1 = request.args.get("sort1") or request.cookies.get("librarium_sort1", "status")
    sort2 = request.args.get("sort2") or request.cookies.get("librarium_sort2", "last_session")
    status_filter = request.args.get("status_filter") or request.cookies.get("librarium_status_filter", "all")
    show_editions = request.args.get("show_editions") or request.cookies.get("librarium_show_editions", "0")
    show_readings = request.args.get("show_readings") or request.cookies.get("librarium_show_readings", "0")
    if show_editions != "1":
        show_readings = "0"

    if show_readings == "1":
        books = _build_index_per_reading(db, lib_id)
    else:
        edition_filter = " AND (b.work_id IS NULL OR b.is_primary_edition = 1)" if show_editions != "1" else ""
        rows = db.execute(f"""
        SELECT
            b.id,
            b.name,
            b.subtitle,
            b.author,
            b.status,
            b.pages,
            b.starting_page,
            b.genre,
            b.has_cover,
            b.cover_hash,
            b.publisher,
            b.language,
            b.publication_date,
            b.work_id,
            b.format,
            b.total_time_seconds,
            COALESCE(sess.total_pages, 0)   AS session_pages,
            COALESCE(sess.total_seconds, 0) AS session_seconds,
            COALESCE(sess.reading_days, 0)  AS reading_days,
            COALESCE(per.period_pages, 0)   AS period_pages,
            sess.first_date,
            sess.last_date,
            per.first_period_start,
            per.last_period_end,
            lr_sess.lr_last_date,
            lr_per.lr_last_period_end,
            COALESCE(pct.max_pct, 0) AS max_progress_pct
        FROM books b
        LEFT JOIN (
            SELECT book_id, MAX(id) AS lr_id
            FROM readings
            GROUP BY book_id
        ) lr ON lr.book_id = b.id
        LEFT JOIN (
            SELECT
                book_id,
                SUM(pages)            AS total_pages,
                SUM(duration_seconds) AS total_seconds,
                COUNT(DISTINCT date)  AS reading_days,
                MIN(date)             AS first_date,
                MAX(date)             AS last_date
            FROM sessions
            WHERE date != ''
            GROUP BY book_id
        ) sess ON sess.book_id = b.id
        LEFT JOIN (
            SELECT
                book_id,
                SUM(pages) AS period_pages,
                MIN(start_date) AS first_period_start,
                MAX(end_date)   AS last_period_end
            FROM periods
            GROUP BY book_id
        ) per ON per.book_id = b.id
        LEFT JOIN (
            SELECT
                reading_id,
                MAX(date) AS lr_last_date
            FROM sessions
            WHERE date != ''
            GROUP BY reading_id
        ) lr_sess ON lr_sess.reading_id = lr.lr_id
        LEFT JOIN (
            SELECT
                reading_id,
                MAX(end_date) AS lr_last_period_end
            FROM periods
            WHERE end_date != ''
            GROUP BY reading_id
        ) lr_per ON lr_per.reading_id = lr.lr_id
        LEFT JOIN (
            SELECT book_id, MAX(pct) AS max_pct FROM (
                SELECT book_id, MAX(progress_pct) AS pct FROM sessions WHERE progress_pct IS NOT NULL GROUP BY book_id
                UNION ALL
                SELECT book_id, MAX(progress_pct) AS pct FROM periods WHERE progress_pct IS NOT NULL GROUP BY book_id
            ) GROUP BY book_id
        ) pct ON pct.book_id = b.id
        WHERE b.library_id = ?{edition_filter}
    """, (lib_id,)).fetchall()

        books = []
        for r in rows:
            total_pages_tracked = r["session_pages"]
            total_seconds_tracked = r["session_seconds"]
            period_pages = r["period_pages"]
            period_seconds = 0
            if period_pages > 0 and total_pages_tracked > 0:
                period_seconds = int(period_pages * (total_seconds_tracked / total_pages_tracked))

            total_pages_display = total_pages_tracked + period_pages
            total_seconds_display = total_seconds_tracked + period_seconds

            starting_page = r["starting_page"] or 0
            total_book_pages = r["pages"] or 0
            effective_pages = total_book_pages - starting_page if starting_page > 0 else total_book_pages

            # First / last activity across sessions and periods
            first_candidates = [d for d in (r["first_date"], r["first_period_start"]) if d]
            # For sorting: use last activity from the LATEST reading only
            lr_candidates = [d for d in (r["lr_last_date"], r["lr_last_period_end"]) if d]
            first_activity = min(first_candidates) if first_candidates else None
            last_activity = max(lr_candidates) if lr_candidates else None

            ratings = _load_ratings(r["id"])

            # Edition count (how many editions share this work_id)
            edition_count = 1
            if r["work_id"]:
                ec_row = db.execute(
                    "SELECT COUNT(*) AS c FROM books WHERE work_id = ?", (r["work_id"],)
                ).fetchone()
                edition_count = ec_row["c"] if ec_row else 1

            book_fmt = r["format"] or "paper"
            is_pct_fmt = book_fmt in ("audiobook", "ebook")

            books.append({
                "id": r["id"],
                "name": r["name"],
                "subtitle": r["subtitle"] or "",
                "author": r["author"] or "",
                "status": r["status"] or "reading",
                "pages": r["pages"] or 0,
                "effective_pages": effective_pages,
                "pages_read": total_pages_display,
                "max_progress_pct": r["max_progress_pct"],
                "is_pct_format": is_pct_fmt,
                "format": book_fmt,
                "total_time_seconds": r["total_time_seconds"] or 0,
                "total_time": _format_duration(total_seconds_display),
                "total_seconds_raw": total_seconds_display,
                "reading_days": r["reading_days"],
                "genre": r["genre"] or "",
                "has_cover": bool(r["has_cover"]),
                "cover_hash": r["cover_hash"] or "",
                "first_session_date": first_activity or "0000-00-00",
                "last_session_date": last_activity or "0000-00-00",
                "avg_rating": _calc_avg_rating(ratings),
                "publisher": r["publisher"] or "",
                "language": r["language"] or "",
                "publication_date": r["publication_date"] or "",
                "edition_count": edition_count,
                "reading_number": None,
            })

    # Sorting helpers
    class _Rev:
        __slots__ = ("v",)
        def __init__(self, v): self.v = v
        def __lt__(self, o): return self.v > o.v
        def __le__(self, o): return self.v >= o.v
        def __gt__(self, o): return self.v < o.v
        def __ge__(self, o): return self.v <= o.v
        def __eq__(self, o): return self.v == o.v

    STATUS_ORDER = {"reading": 1, "finished": 2, "not-started": 3, "abandoned": 4, "draft": 5}

    def _sort_key_for(criterion, b):
        if criterion == "last_session":
            return (_Rev(b["last_session_date"]),)
        elif criterion == "rating":
            return (_Rev(b["avg_rating"] or 0),)
        elif criterion == "status":
            return (STATUS_ORDER.get(b["status"], 5),)
        elif criterion == "author":
            return (b["author"],)
        elif criterion == "time_read":
            return (_Rev(b["total_seconds_raw"]),)
        else:
            return (b["name"],)

    # ── Library ribbon stats (computed from primary editions + standalone books) ──
    all_rows = db.execute(
        "SELECT author, pages, starting_page, status, source_type, work_id FROM books "
        "WHERE library_id = ? AND (work_id IS NULL OR is_primary_edition = 1)", (lib_id,)
    ).fetchall()
    unique_authors: set[str] = set()
    total_library_pages = 0
    reading_count = 0
    not_started_count = 0
    for br in all_rows:
        if br["author"]:
            for a in br["author"].split(";"):
                a = a.strip()
                if a:
                    unique_authors.add(a)
        bp = br["pages"] or 0
        sp = br["starting_page"] or 0
        total_library_pages += (bp - sp) if sp > 0 else bp
        if br["status"] == "reading":
            reading_count += 1
        elif br["status"] == "not-started":
            not_started_count += 1
    total_books_count = len(all_rows)

    # Finished = distinct works with at least one edition having a finished reading
    finished_count = db.execute(
        "SELECT COUNT(DISTINCT COALESCE(b.work_id, b.id)) FROM books b "
        "JOIN readings r ON r.book_id = b.id "
        "WHERE b.library_id = ? AND r.status = 'finished'", (lib_id,)
    ).fetchone()[0]

    # Books Owned = distinct editions (not works) with source_type = 'owned'
    owned_count = db.execute(
        "SELECT COUNT(*) FROM books WHERE library_id = ? AND source_type = 'owned'", (lib_id,)
    ).fetchone()[0]

    # Total time read across all books (sessions + estimated period time)
    total_library_seconds = sum(b["total_seconds_raw"] for b in books)
    total_library_time = _format_duration_long(total_library_seconds)

    if status_filter and status_filter != "all":
        books = [b for b in books if b["status"] == status_filter]

    if sort2 and sort2 != sort1:
        books.sort(key=lambda b: _sort_key_for(sort1, b) + _sort_key_for(sort2, b))
    else:
        books.sort(key=lambda b: _sort_key_for(sort1, b) + (b["name"],))

    resp = make_response(render_template(
        "index.html",
        books=books,
        sort1=sort1,
        sort2=sort2,
        status_filter=status_filter,
        total_books=total_books_count,
        total_library_pages=total_library_pages,
        total_library_time=total_library_time,
        unique_authors=len(unique_authors),
        reading_count=reading_count,
        finished_count=finished_count,
        not_started_count=not_started_count,
        owned_count=owned_count,
        show_editions=show_editions,
        show_readings=show_readings,
    ))
    # Persist preferences in cookies (1 year expiry)
    resp.set_cookie("librarium_sort1", sort1, max_age=365*24*3600, samesite="Lax")
    resp.set_cookie("librarium_sort2", sort2 or "", max_age=365*24*3600, samesite="Lax")
    resp.set_cookie("librarium_status_filter", status_filter, max_age=365*24*3600, samesite="Lax")
    resp.set_cookie("librarium_show_editions", show_editions, max_age=365*24*3600, samesite="Lax")
    resp.set_cookie("librarium_show_readings", show_readings, max_age=365*24*3600, samesite="Lax")
    return resp


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Global Stats
# ═══════════════════════════════════════════════════════════════════════════


def _compute_status_timeline(db, lib_id):
    """Compute edition-status counts over time for a library.

    Returns ``{"dates": [...], "series": {"reading": [...], ...}}``.
    Each edition (row in *books*) is counted independently.  The status of
    each edition on a given date is derived from its readings' dated
    sessions / periods.  Books with no date information appear from today.
    """
    from datetime import date as _date, timedelta

    today = _date.today()
    today_s = today.isoformat()
    STATUSES = ["reading", "finished", "not-started", "abandoned", "draft"]

    # ── 1. All editions in the library ───────────────────────────────────
    books = db.execute(
        "SELECT id, status, purchase_date, borrowed_start "
        "FROM books WHERE library_id = ? "
        "AND (work_id IS NULL OR is_primary_edition = 1)",
        (lib_id,),
    ).fetchall()
    if not books:
        return {"dates": [], "series": {s: [] for s in STATUSES}}

    book_map = {b["id"]: dict(b) for b in books}
    bids = list(book_map.keys())
    ph = ",".join("?" * len(bids))

    # ── 2. Readings by book ──────────────────────────────────────────────
    readings_by_book: dict[str, list[dict]] = {}
    for r in db.execute(
        f"SELECT id, book_id, reading_number, status FROM readings "
        f"WHERE book_id IN ({ph}) ORDER BY book_id, reading_number",
        bids,
    ).fetchall():
        readings_by_book.setdefault(r["book_id"], []).append(dict(r))

    all_rids = [r["id"] for rlist in readings_by_book.values() for r in rlist]

    # ── 3. Session / period date ranges per reading ──────────────────────
    sess_range: dict[int, tuple[str, str]] = {}
    per_range: dict[int, tuple[str, str]] = {}
    if all_rids:
        rph = ",".join("?" * len(all_rids))
        for row in db.execute(
            f"SELECT reading_id, MIN(date) AS d0, MAX(date) AS d1 "
            f"FROM sessions WHERE reading_id IN ({rph}) AND date != '' "
            f"GROUP BY reading_id",
            all_rids,
        ).fetchall():
            sess_range[row["reading_id"]] = (row["d0"], row["d1"])
        for row in db.execute(
            f"SELECT reading_id, "
            f"MIN(start_date) AS d0, "
            f"MAX(CASE WHEN end_date != '' THEN end_date ELSE start_date END) AS d1 "
            f"FROM periods WHERE reading_id IN ({rph}) AND start_date != '' "
            f"GROUP BY reading_id",
            all_rids,
        ).fetchall():
            per_range[row["reading_id"]] = (row["d0"], row["d1"])

    # ── 4. Build status-change events per edition ────────────────────────
    events: list[tuple[str, str, str]] = []  # (date, book_id, new_status)

    for bid, bk in book_map.items():
        rlist = readings_by_book.get(bid, [])
        entry = bk["purchase_date"] or bk["borrowed_start"] or ""

        transitions: list[tuple[str, str]] = []
        first_start: str | None = None

        for r in rlist:
            rid = r["id"]
            ds = [d for d in (*sess_range.get(rid, ()), *per_range.get(rid, ())) if d]
            if not ds:
                continue
            start, end = min(ds), max(ds)
            if first_start is None or start < first_start:
                first_start = start
            transitions.append((start, "reading"))
            if r["status"] in ("finished", "abandoned"):
                transitions.append((end, r["status"]))

        if not transitions:
            # No dated readings → edition sits in its current status from entry (or today)
            transitions.append((entry or today_s, bk["status"] or "not-started"))
        elif entry and first_start and entry < first_start:
            initial = "draft" if bk["status"] == "draft" else "not-started"
            transitions.insert(0, (entry, initial))

        transitions.sort()
        for d, s in transitions:
            events.append((d, bid, s))

    events.sort()
    if not events:
        return {"dates": [], "series": {s: [] for s in STATUSES}}

    # ── 5. Walk the timeline, emitting sampled data points ───────────────
    start_date = _date.fromisoformat(events[0][0])
    total_days = (today - start_date).days + 1
    interval = max(1, total_days // 500)  # ≈ 500 data points

    current: dict[str, str] = {}  # bid → status
    counts = {s: 0 for s in STATUSES}

    result_dates: list[str] = []
    result_series: dict[str, list[int]] = {s: [] for s in STATUSES}
    ei = 0
    d = start_date
    day_num = 0

    while d <= today:
        ds = d.isoformat()
        while ei < len(events) and events[ei][0] <= ds:
            _, bid, new_st = events[ei]
            old_st = current.get(bid)
            if old_st != new_st:
                if old_st and old_st in counts:
                    counts[old_st] -= 1
                counts[new_st] = counts.get(new_st, 0) + 1
                current[bid] = new_st
            ei += 1

        if day_num % interval == 0 or d == today:
            result_dates.append(ds)
            for s in STATUSES:
                result_series[s].append(counts.get(s, 0))

        d += timedelta(days=1)
        day_num += 1

    return {"dates": result_dates, "series": result_series}


@app.route("/stats")
def global_stats():
    """Global statistics page – aggregate reading stats for the current library."""
    db = get_db()
    lib_id = _get_current_library_id()

    # Pages by year: sessions + periods
    pages_by_year: dict[str, int] = {}
    for row in db.execute(
        "SELECT SUBSTR(s.date, 1, 4) AS yr, SUM(s.pages) AS p "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        "WHERE s.date != '' AND b.library_id = ? GROUP BY yr", (lib_id,)
    ).fetchall():
        pages_by_year[row["yr"]] = row["p"]
    for row in db.execute(
        "SELECT SUBSTR(p.end_date, 1, 4) AS yr, SUM(p.pages) AS p "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        "WHERE p.end_date != '' AND p.pages > 0 AND b.library_id = ? GROUP BY yr", (lib_id,)
    ).fetchall():
        pages_by_year[row["yr"]] = pages_by_year.get(row["yr"], 0) + row["p"]

    # Books finished by year – count ALL finished readings across all editions
    books_finished_by_year: dict[str, int] = {}
    finished_readings = db.execute(
        "SELECT r.id, r.book_id FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        "WHERE r.status = 'finished' AND b.library_id = ?", (lib_id,)
    ).fetchall()
    for fr in finished_readings:
        rid = fr["id"]
        candidates = []
        r = db.execute(
            "SELECT MAX(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (rid,)
        ).fetchone()
        if r and r["d"]:
            candidates.append(r["d"])
        r = db.execute(
            "SELECT MAX(end_date) AS d FROM periods WHERE reading_id = ? AND end_date != ''", (rid,)
        ).fetchone()
        if r and r["d"]:
            candidates.append(r["d"])
        if candidates:
            finish_year = max(candidates)[:4]
            books_finished_by_year[finish_year] = books_finished_by_year.get(finish_year, 0) + 1

    # Time read by year: sessions + periods (duration_seconds)
    time_by_year: dict[str, int] = {}
    for row in db.execute(
        "SELECT SUBSTR(s.date, 1, 4) AS yr, SUM(s.duration_seconds) AS t "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        "WHERE s.date != '' AND s.duration_seconds > 0 AND b.library_id = ? GROUP BY yr", (lib_id,)
    ).fetchall():
        time_by_year[row["yr"]] = row["t"]
    for row in db.execute(
        "SELECT SUBSTR(p.end_date, 1, 4) AS yr, SUM(p.duration_seconds) AS t "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        "WHERE p.end_date != '' AND p.duration_seconds > 0 AND b.library_id = ? GROUP BY yr", (lib_id,)
    ).fetchall():
        time_by_year[row["yr"]] = time_by_year.get(row["yr"], 0) + row["t"]

    all_years = sorted(set(pages_by_year.keys()) | set(books_finished_by_year.keys()) | set(time_by_year.keys()))
    pages_data = [pages_by_year.get(y, 0) for y in all_years]
    books_data = [books_finished_by_year.get(y, 0) for y in all_years]
    time_data = [time_by_year.get(y, 0) for y in all_years]

    # ── Library Stats data ──────────────────────────────────────────────
    all_lib_books = db.execute(
        "SELECT id, name, status, genre, language, original_language, pages, publisher, has_cover, cover_hash "
        "FROM books WHERE library_id = ? AND (work_id IS NULL OR is_primary_edition = 1)", (lib_id,)
    ).fetchall()

    status_counts: dict[str, int] = Counter()
    genre_counts: dict[str, int] = Counter()
    language_counts: dict[str, int] = Counter()
    orig_lang_counts: dict[str, int] = Counter()
    publisher_counts: dict[str, int] = Counter()
    all_avg_ratings: list[float] = []   # raw avg ratings for KDE distribution chart
    author_counts: dict[str, int] = Counter()
    highest_rated_book = None
    highest_rating = 0.0
    longest_finished = None
    longest_finished_pages = 0
    shortest_finished = None
    shortest_finished_pages = float("inf")
    rated_sum = 0.0
    rated_count = 0

    for bk in all_lib_books:
        status_counts[bk["status"] or "unknown"] += 1
        if bk["genre"]:
            genre_counts[bk["genre"]] += 1
        else:
            genre_counts["Unknown"] += 1
        if bk["language"]:
            language_counts[bk["language"]] += 1
        else:
            language_counts["Unknown"] += 1
        if bk["original_language"]:
            orig_lang_counts[bk["original_language"]] += 1
        else:
            orig_lang_counts["Unknown"] += 1
        if bk["publisher"]:
            publisher_counts[bk["publisher"]] += 1
        else:
            publisher_counts["Unknown"] += 1

        # Author split
        author_row = db.execute("SELECT author FROM books WHERE id = ?", (bk["id"],)).fetchone()
        if author_row and author_row["author"]:
            for a in author_row["author"].split(";"):
                a = a.strip()
                if a:
                    author_counts[a] += 1

        # Rating
        ratings = _load_ratings(bk["id"])
        avg = _calc_avg_rating(ratings)
        if avg is not None and avg > 0:
            rated_sum += avg
            rated_count += 1
            all_avg_ratings.append(round(avg, 2))
            if avg > highest_rating:
                highest_rating = avg
                highest_rated_book = {"name": bk["name"], "id": bk["id"], "rating": avg, "has_cover": bool(bk["has_cover"])}
        # Longest / shortest finished
        book_pages = bk["pages"] or 0
        is_finished = db.execute(
            "SELECT 1 FROM readings WHERE book_id = ? AND status = 'finished' LIMIT 1",
            (bk["id"],)
        ).fetchone()
        if is_finished and book_pages > 0:
            if book_pages > longest_finished_pages:
                longest_finished_pages = book_pages
                longest_finished = {"name": bk["name"], "id": bk["id"], "pages": book_pages, "has_cover": bool(bk["has_cover"])}
            if book_pages < shortest_finished_pages:
                shortest_finished_pages = book_pages
                shortest_finished = {"name": bk["name"], "id": bk["id"], "pages": book_pages, "has_cover": bool(bk["has_cover"])}

    # Most re-read work (group readings across all editions of a work)
    reread_row = db.execute(
        "SELECT COALESCE(b.work_id, r.book_id) AS wid, COUNT(*) AS cnt FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        "WHERE b.library_id = ? GROUP BY wid HAVING cnt > 1 ORDER BY cnt DESC LIMIT 1",
        (lib_id,)
    ).fetchone()
    most_reread = None
    if reread_row:
        # Get the primary edition for display
        rbk = db.execute(
            "SELECT id, name, has_cover FROM books WHERE (work_id = ? OR id = ?) "
            "ORDER BY is_primary_edition DESC LIMIT 1",
            (reread_row["wid"], reread_row["wid"]),
        ).fetchone()
        if rbk:
            most_reread = {"name": rbk["name"], "id": rbk["id"], "count": reread_row["cnt"], "has_cover": bool(rbk["has_cover"])}

    avg_finished_rating = round(rated_sum / rated_count, 2) if rated_count > 0 else None

    # Top 10 authors for bar chart
    top_authors = author_counts.most_common(10)

    # Format status labels
    status_labels_map = {"reading": "Reading", "finished": "Finished", "not-started": "Not Started", "abandoned": "Abandoned", "draft": "Draft"}
    status_chart = {status_labels_map.get(k, k.title()): v for k, v in status_counts.items()}

    # Remove 'Unknown' entries from all count maps — they don't represent a real value
    def _remove_unknown(d: dict) -> dict:
        return {k: v for k, v in d.items() if str(k).strip().lower() != 'unknown' and str(k).strip() != ''}

    genre_counts_clean = _remove_unknown(dict(genre_counts))
    language_counts_clean = _remove_unknown(dict(language_counts))
    orig_lang_counts_clean = _remove_unknown(dict(orig_lang_counts))
    publisher_counts_clean = _remove_unknown(dict(publisher_counts))
    author_counts_clean = _remove_unknown(dict(author_counts))
    status_chart_clean = {k: v for k, v in status_chart.items() if str(k).strip().lower() != 'unknown'}

    # Prepare publisher chart data: show top N publishers and aggregate the rest as "Other" (computed from cleaned counts)
    TOP_PUBLISHERS_FOR_CHART = 20
    from collections import Counter as _Counter
    pc_counter = _Counter(publisher_counts_clean)
    top_publishers = pc_counter.most_common(TOP_PUBLISHERS_FOR_CHART)
    others_total = sum(publisher_counts_clean.values()) - sum(c for _, c in top_publishers)
    publisher_chart = {k: v for k, v in top_publishers}
    if others_total > 0:
        publisher_chart["Other"] = others_total

    return render_template(
        "stats.html",
        years=all_years,
        pages_data=pages_data,
        books_data=books_data,
        time_data=time_data,
        status_chart=status_chart_clean,
        genre_counts=genre_counts_clean,
        language_counts=language_counts_clean,
        orig_lang_counts=orig_lang_counts_clean,
        publisher_counts=publisher_counts_clean,
        publisher_chart=publisher_chart,
        author_counts=author_counts_clean,
        all_avg_ratings=all_avg_ratings,
        top_authors=top_authors,
        highest_rated_book=highest_rated_book,
        avg_finished_rating=avg_finished_rating,
        longest_finished=longest_finished,
        shortest_finished=shortest_finished,
        most_reread=most_reread,
    )


@app.route('/api/cumulative_pages')
def api_cumulative_pages():
    """Return per-date cumulative pages as JSON.

    Query params:
    - book_id: optional, when provided returns data for that book only
    - year: optional, 4-digit year (e.g. 2025) to filter results

    Response: list of {date: 'YYYY-MM-DD', pages: int, cumulative: int}
    """
    db = get_db()
    lib_id = _get_current_library_id()
    book_id = request.args.get('book_id')
    year = request.args.get('year')

    if book_id:
        q = (
            "SELECT d AS date, SUM(p) AS pages FROM ("
            "SELECT date AS d, SUM(pages) AS p FROM sessions WHERE date != '' AND book_id = ? GROUP BY date "
            "UNION ALL "
            "SELECT end_date AS d, SUM(pages) AS p FROM periods WHERE end_date != '' AND pages > 0 AND book_id = ? GROUP BY end_date"
            ") GROUP BY d ORDER BY d"
        )
        params = (book_id, book_id)
    else:
        q = (
            "SELECT d AS date, SUM(p) AS pages FROM ("
            "SELECT s.date AS d, SUM(s.pages) AS p FROM sessions s JOIN books b ON b.id = s.book_id WHERE s.date != '' AND b.library_id = ? GROUP BY s.date "
            "UNION ALL "
            "SELECT p.end_date AS d, SUM(p.pages) AS p FROM periods p JOIN books b ON b.id = p.book_id WHERE p.end_date != '' AND p.pages > 0 AND b.library_id = ? GROUP BY p.end_date"
            ") GROUP BY d ORDER BY d"
        )
        params = (lib_id, lib_id)

    rows = db.execute(q, params).fetchall()

    out = []
    cum = 0
    for r in rows:
        d = r['date']
        if not d:
            continue
        if year and not str(d).startswith(str(year)):
            continue
        pages = int(r['pages'] or 0)
        cum += pages
        out.append({ 'date': d, 'pages': pages, 'cumulative': cum })

    return jsonify(out)


@app.route("/api/status_timeline")
def api_status_timeline():
    """Return status-count timeseries for the stacked area chart."""
    db = get_db()
    lib_id = _get_current_library_id()
    return jsonify(_compute_status_timeline(db, lib_id))


@app.route('/api/cumulative_pages_per_book')
def api_cumulative_pages_per_book():
    """Return per-book cumulative pages for a given year as JSON.

    Query params:
    - year: required, 4-digit year (e.g. 2025)

    Response: { labels: [dates], datasets: [ { book_id, label, data: [cumulative_values], total } ] }
    """
    db = get_db()
    lib_id = _get_current_library_id()
    year = request.args.get('year')
    if not year:
        return jsonify({"error": "year query parameter required"}), 400

    q = (
        "SELECT s.book_id, d AS date, SUM(p) AS pages FROM ("
        "SELECT s.book_id, s.date AS d, s.pages AS p FROM sessions s JOIN books b ON b.id = s.book_id "
        "WHERE s.date != '' AND SUBSTR(s.date,1,4) = ? AND b.library_id = ? "
        "UNION ALL "
        "SELECT p.book_id, p.end_date AS d, p.pages AS p FROM periods p JOIN books b ON b.id = p.book_id "
        "WHERE p.end_date != '' AND p.pages > 0 AND SUBSTR(p.end_date,1,4) = ? AND b.library_id = ? "
        ") s GROUP BY s.book_id, d ORDER BY s.book_id, d"
    )
    rows = db.execute(q, (year, lib_id, year, lib_id)).fetchall()

    book_map: dict[str, dict] = {}
    all_dates: set[str] = set()
    for r in rows:
        bid = r['book_id']
        d = r['date']
        p = int(r['pages'] or 0)
        all_dates.add(d)
        if bid not in book_map:
            bk = db.execute('SELECT name, cover_color FROM books WHERE id = ?', (bid,)).fetchone()
            color = (bk['cover_color'] or '').strip() if bk else ''
            if not color:
                color = '#888888'
            book_map[bid] = {'name': bk['name'] if bk else bid, 'color': color, 'dates': {}}
        book_map[bid]['dates'][d] = book_map[bid]['dates'].get(d, 0) + p

    if not book_map:
        return jsonify({'labels': [], 'datasets': []})

    # Get carry-over pages for each book (total pages read before this year)
    from datetime import timedelta
    year_start = f"{year}-01-01"
    year_int = int(year)
    for bid in book_map:
        carry_q = (
            "SELECT COALESCE(SUM(p), 0) AS total FROM ("
            "SELECT s.pages AS p FROM sessions s JOIN books b ON b.id = s.book_id "
            "WHERE s.book_id = ? AND s.date != '' AND s.date < ? AND b.library_id = ? "
            "UNION ALL "
            "SELECT p.pages AS p FROM periods p JOIN books b ON b.id = p.book_id "
            "WHERE p.book_id = ? AND p.end_date != '' AND p.pages > 0 AND p.end_date < ? AND b.library_id = ? "
            ") s"
        )
        carry = db.execute(carry_q, (bid, year_start, lib_id, bid, year_start, lib_id)).fetchone()
        book_map[bid]['carry_over'] = int(carry['total']) if carry else 0

    # Build per-book anchor points so the chart shows a step pattern:
    # - For each reading day, also add the day before with the previous
    #   cumulative value so the line is flat during idle periods and jumps
    #   on the actual reading day.
    # - Books starting this year (carry_over==0): day before first read → 0
    # - Books starting in a previous year: Jan 1 → carry_over value
    for bid, info in book_map.items():
        if not info['dates']:
            continue
        book_dates = sorted(info['dates'].keys())
        carry = info['carry_over']
        anchors: dict[str, int] = {}

        cum = carry
        for i, d in enumerate(book_dates):
            prev_cum = cum
            try:
                dt = date.fromisoformat(d)
                prev_dt = dt - timedelta(days=1)
                prev_s = prev_dt.isoformat()
                # Don't overwrite an actual reading day with an anchor
                if prev_s not in info['dates'] and prev_s not in anchors:
                    if prev_dt.year == year_int:
                        anchors[prev_s] = prev_cum
            except Exception:
                pass
            cum += int(info['dates'][d])

        # For books started in a previous year, anchor Jan 1 with carry_over
        if carry > 0:
            jan1 = year_start
            if jan1 not in info['dates'] and jan1 not in anchors:
                anchors[jan1] = carry

        info['anchors'] = anchors
        all_dates.update(anchors.keys())

    labels = sorted(all_dates)

    datasets = []
    for bid, info in book_map.items():
        dates = info['dates']
        if not dates:
            continue
        carry = info.get('carry_over', 0)
        anchors = info.get('anchors', {})
        book_dates = sorted(dates.keys())
        first_date = book_dates[0]
        # Find the earliest relevant date for this book (anchor or reading)
        all_book_dates = sorted(set(book_dates) | set(anchors.keys()))
        earliest = all_book_dates[0] if all_book_dates else first_date

        cum = carry
        series = []
        for d in labels:
            if d < earliest:
                series.append(None)
            elif d in dates:
                cum += int(dates[d])
                series.append(cum)
            elif d in anchors:
                series.append(anchors[d])
            else:
                series.append(None)

        # last non-null value as total
        total = 0
        for v in reversed(series):
            if v is not None:
                total = v
                break

        datasets.append({
            'book_id': bid,
            'label': info['name'],
            'color': info.get('color', '#888888'),
            'data': series,
            'total': total,
        })

    return jsonify({'labels': labels, 'datasets': datasets})


@app.route("/stats/year/<year>")
def stats_year(year: str):
    """Yearly statistics page."""
    db = get_db()
    lib_id = _get_current_library_id()

    year_sessions = []
    for row in db.execute("""
        SELECT s.date, s.pages, s.duration_seconds, b.name AS book_name
        FROM sessions s
        JOIN books b ON b.id = s.book_id
        WHERE SUBSTR(s.date, 1, 4) = ? AND b.library_id = ?
        ORDER BY s.date
    """, (year, lib_id)).fetchall():
        year_sessions.append(dict(row))

    year_periods = []
    total_period_pages = 0
    for row in db.execute("""
        SELECT p.start_date, p.end_date, p.pages, p.note,
               b.name AS book_name, p.book_id
        FROM periods p
        JOIN books b ON b.id = p.book_id
        WHERE SUBSTR(p.end_date, 1, 4) = ? AND b.library_id = ?
        ORDER BY p.end_date
    """, (year, lib_id)).fetchall():
        d = dict(row)
        d["book_id"] = row["book_id"]
        year_periods.append(d)
        total_period_pages += row["pages"]

    total_pages_tracked = sum(s["pages"] for s in year_sessions)
    total_seconds_tracked = sum(s["duration_seconds"] for s in year_sessions)

    period_seconds = 0
    if total_period_pages > 0 and total_pages_tracked > 0:
        period_seconds = int(total_period_pages * (total_seconds_tracked / total_pages_tracked))

    total_pages = total_pages_tracked + total_period_pages
    total_seconds = total_seconds_tracked + period_seconds

    # ── Gantt chart data ───────────────────────────────────────────────
    from datetime import timedelta

    year_int = int(year)
    year_start = date(year_int, 1, 1)
    year_end = date(year_int, 12, 31)
    total_days = (year_end - year_start).days + 1  # 365 or 366

    # (book_id, reading_id) → {name, color, active_dates, …}
    gantt_books: dict[tuple, dict] = {}
    # book_id → count of distinct readings appearing in this year (for labelling)
    book_reading_counts: dict[str, set] = {}

    def _ensure_gantt_entry(bid, rid, name, color, status="", subtitle="", reading_number=None):
        key = (bid, rid)
        if key not in gantt_books:
            gantt_books[key] = {
                "book_id": bid,
                "reading_id": rid,
                "reading_number": reading_number,
                "name": name,
                "subtitle": subtitle or "",
                "color": color or "#888888",
                "status": status,
                "active_dates": set(),
                "has_before": False,
                "has_after": False,
            }
        book_reading_counts.setdefault(bid, set())
        if rid:
            book_reading_counts[bid].add(rid)

    # Sessions in the current year → active dates (per reading)
    for row in db.execute("""
        SELECT s.date, s.book_id, s.reading_id, b.name, b.subtitle, b.cover_color, b.status,
               r.reading_number
        FROM sessions s
        JOIN books b ON b.id = s.book_id
        LEFT JOIN readings r ON r.id = s.reading_id
        WHERE SUBSTR(s.date, 1, 4) = ? AND b.library_id = ?
    """, (year, lib_id)).fetchall():
        bid = row["book_id"]
        rid = row["reading_id"] or "__none__"
        _ensure_gantt_entry(bid, rid, row["name"], row["cover_color"], row["status"], row["subtitle"], row["reading_number"])
        try:
            gantt_books[(bid, rid)]["active_dates"].add(date.fromisoformat(row["date"]))
        except (ValueError, TypeError):
            pass

    # Periods overlapping the current year → expand into active dates (per reading)
    for row in db.execute("""
        SELECT p.start_date, p.end_date, p.book_id, p.reading_id, b.name, b.subtitle, b.cover_color, b.status,
               r.reading_number
        FROM periods p
        JOIN books b ON b.id = p.book_id
        LEFT JOIN readings r ON r.id = p.reading_id
        WHERE p.end_date >= ? AND p.start_date <= ? AND b.library_id = ?
    """, (f"{year}-01-01", f"{year}-12-31", lib_id)).fetchall():
        bid = row["book_id"]
        rid = row["reading_id"] or "__none__"
        _ensure_gantt_entry(bid, rid, row["name"], row["cover_color"], row["status"], row["subtitle"], row["reading_number"])
        try:
            sd = date.fromisoformat(row["start_date"])
            ed = date.fromisoformat(row["end_date"])
            d = max(sd, year_start)
            end_clamp = min(ed, year_end)
            while d <= end_clamp:
                gantt_books[(bid, rid)]["active_dates"].add(d)
                d += timedelta(days=1)
        except (ValueError, TypeError):
            pass

    # Check for activity before / after the year for each entry
    for (bid, rid), info in list(gantt_books.items()):
        if rid == "__none__":
            # Legacy data without reading_id – check by book_id
            r = db.execute(
                "SELECT 1 FROM sessions WHERE book_id = ? AND date < ? AND date != '' LIMIT 1",
                (bid, f"{year}-01-01"),
            ).fetchone()
            if r:
                info["has_before"] = True
            r = db.execute(
                "SELECT 1 FROM sessions WHERE book_id = ? AND date > ? LIMIT 1",
                (bid, f"{year}-12-31"),
            ).fetchone()
            if r:
                info["has_after"] = True
            r = db.execute(
                "SELECT 1 FROM periods WHERE book_id = ? AND start_date < ? AND end_date != '' LIMIT 1",
                (bid, f"{year}-01-01"),
            ).fetchone()
            if r:
                info["has_before"] = True
            r = db.execute(
                "SELECT 1 FROM periods WHERE book_id = ? AND end_date > ? LIMIT 1",
                (bid, f"{year}-12-31"),
            ).fetchone()
            if r:
                info["has_after"] = True
        else:
            # Check per reading_id
            r = db.execute(
                "SELECT 1 FROM sessions WHERE reading_id = ? AND date < ? AND date != '' LIMIT 1",
                (rid, f"{year}-01-01"),
            ).fetchone()
            if r:
                info["has_before"] = True
            r = db.execute(
                "SELECT 1 FROM sessions WHERE reading_id = ? AND date > ? LIMIT 1",
                (rid, f"{year}-12-31"),
            ).fetchone()
            if r:
                info["has_after"] = True
            r = db.execute(
                "SELECT 1 FROM periods WHERE reading_id = ? AND start_date < ? AND end_date != '' LIMIT 1",
                (rid, f"{year}-01-01"),
            ).fetchone()
            if r:
                info["has_before"] = True
            r = db.execute(
                "SELECT 1 FROM periods WHERE reading_id = ? AND end_date > ? LIMIT 1",
                (rid, f"{year}-12-31"),
            ).fetchone()
            if r:
                info["has_after"] = True

    # Build gantt_data with active segments
    gantt_data = []
    for (bid, rid), info in gantt_books.items():
        active = sorted(info["active_dates"])
        if not active:
            continue

        # Determine overall span
        span_start = year_start if info["has_before"] else active[0]
        span_end = year_end if info["has_after"] else active[-1]
        start_day = (span_start - year_start).days
        end_day = (span_end - year_start).days

        # Group consecutive active dates into segments
        active_segments = []
        seg_start = active[0]
        seg_end = active[0]
        for d in active[1:]:
            if (d - seg_end).days <= 1:
                seg_end = d
            else:
                active_segments.append({
                    "start": (seg_start - year_start).days,
                    "end": (seg_end - year_start).days,
                })
                seg_start = d
                seg_end = d
        active_segments.append({
            "start": (seg_start - year_start).days,
            "end": (seg_end - year_start).days,
        })

        # Earliest-ever reading date for this reading (or book if no reading_id)
        first_ever = None
        if rid != "__none__":
            r = db.execute(
                "SELECT MIN(date) AS d FROM sessions WHERE reading_id = ? AND date != ''",
                (rid,),
            ).fetchone()
            if r and r["d"]:
                first_ever = r["d"]
            r = db.execute(
                "SELECT MIN(start_date) AS d FROM periods WHERE reading_id = ? AND start_date != ''",
                (rid,),
            ).fetchone()
            if r and r["d"]:
                if first_ever is None or r["d"] < first_ever:
                    first_ever = r["d"]
        else:
            r = db.execute(
                "SELECT MIN(date) AS d FROM sessions WHERE book_id = ? AND date != ''",
                (bid,),
            ).fetchone()
            if r and r["d"]:
                first_ever = r["d"]
            r = db.execute(
                "SELECT MIN(start_date) AS d FROM periods WHERE book_id = ? AND start_date != ''",
                (bid,),
            ).fetchone()
            if r and r["d"]:
                if first_ever is None or r["d"] < first_ever:
                    first_ever = r["d"]

        # Add reading number label for books with multiple readings
        display_name = info["name"]
        has_multi = len(book_reading_counts.get(bid, set())) > 1
        if has_multi and info["reading_number"]:
            display_name = f"{info['name']} (#{info['reading_number']})"

        gantt_data.append({
            "name": display_name,
            "subtitle": info["subtitle"],
            "color": info["color"],
            "status": info["status"],
            "start": start_day,
            "end": end_day,
            "segments": active_segments,
            "first_ever": first_ever or "9999-12-31",
        })

    # Sort by first-ever reading session/period, then by name
    gantt_data.sort(key=lambda g: (g["first_ever"], g["name"]))

    # Determine prev/next years with data
    data_years = set()
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(s.date, 1, 4) AS yr FROM sessions s "
        "JOIN books b ON b.id = s.book_id WHERE s.date != '' AND b.library_id = ?", (lib_id,)
    ).fetchall():
        data_years.add(row["yr"])
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(p.end_date, 1, 4) AS yr FROM periods p "
        "JOIN books b ON b.id = p.book_id WHERE p.end_date != '' AND b.library_id = ?", (lib_id,)
    ).fetchall():
        data_years.add(row["yr"])
    sorted_years = sorted(data_years)
    prev_year = None
    next_year = None
    if year in sorted_years:
        idx = sorted_years.index(year)
        if idx > 0:
            prev_year = sorted_years[idx - 1]
        if idx < len(sorted_years) - 1:
            next_year = sorted_years[idx + 1]

    return render_template(
        "stats_year.html",
        year=year,
        sessions=year_sessions,
        periods=year_periods,
        total_pages=total_pages,
        total_seconds=total_seconds,
        period_pages=total_period_pages,
        gantt_data=gantt_data,
        prev_year=prev_year,
        next_year=next_year,
    )


@app.route("/stats/year/<year>/books")
def stats_year_books(year: str):
    """Display all books/readings finished in a specific year with their covers."""
    db = get_db()
    lib_id = _get_current_library_id()
    sort = request.args.get("sort", "date")
    if sort not in ("alpha", "author", "date", "rating"):
        sort = "date"

    finished_readings = db.execute("""
        SELECT r.id AS reading_id, r.book_id, r.reading_number,
               b.name, b.subtitle, b.author, b.has_cover, b.cover_hash
        FROM readings r
        JOIN books b ON b.id = r.book_id
        WHERE r.status = 'finished' AND b.library_id = ?
    """, (lib_id,)).fetchall()

    # Count total readings per book to know when to show reading number
    readings_per_book: dict[str, int] = {}
    for fr in finished_readings:
        readings_per_book[fr["book_id"]] = readings_per_book.get(fr["book_id"], 0) + 1

    books_finished = []
    all_finish_years: set[str] = set()
    for fr in finished_readings:
        rid = fr["reading_id"]
        candidates = []
        r = db.execute(
            "SELECT MAX(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (rid,)
        ).fetchone()
        if r and r["d"]:
            candidates.append(r["d"])
        r = db.execute(
            "SELECT MAX(end_date) AS d FROM periods WHERE reading_id = ? AND end_date != ''", (rid,)
        ).fetchone()
        if r and r["d"]:
            candidates.append(r["d"])
        if candidates:
            finish_date = max(candidates)
            finish_yr = finish_date[:4]
            all_finish_years.add(finish_yr)
            if finish_yr == year:
                book_id = fr["book_id"]
                ratings_rows = db.execute(
                    "SELECT dimension_key, value FROM ratings WHERE book_id = ?", (book_id,)
                ).fetchall()
                ratings = {r["dimension_key"]: r["value"] for r in ratings_rows}
                avg_rating = _calc_avg_rating(ratings)

                rnum = fr["reading_number"]
                show_rnum = readings_per_book.get(book_id, 1) > 1

                books_finished.append({
                    "id": book_id,
                    "name": fr["name"],
                    "subtitle": fr["subtitle"] or "",
                    "author": fr["author"] or "",
                    "has_cover": bool(fr["has_cover"]),
                    "cover_hash": fr["cover_hash"] or "",
                    "finish_date": finish_date,
                    "rating": avg_rating or 0,
                    "reading_number": rnum if show_rnum else None,
                })

    if sort == "alpha":
        books_finished.sort(key=lambda b: b["name"].lower())
    elif sort == "author":
        books_finished.sort(key=lambda b: (b["author"].lower(), b["name"].lower()))
    elif sort == "rating":
        books_finished.sort(key=lambda b: (-b["rating"], b["name"].lower()))
    else:  # date
        books_finished.sort(key=lambda b: b["finish_date"])

    sorted_years = sorted(all_finish_years)
    prev_year = None
    next_year = None
    if year in sorted_years:
        idx = sorted_years.index(year)
        if idx > 0:
            prev_year = sorted_years[idx - 1]
        if idx < len(sorted_years) - 1:
            next_year = sorted_years[idx + 1]

    return render_template("stats_year_books.html", year=year, books=books_finished, sort=sort,
                           prev_year=prev_year, next_year=next_year)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Activity
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/activity")
def activity():
    """Activity dashboard – reading habits, trends, and streaks."""
    db = get_db()
    lib_id = _get_current_library_id()

    # 1. Daily session aggregates (all time)
    daily_sessions: dict[str, dict] = {}
    for row in db.execute(
        "SELECT s.date, SUM(s.pages) AS pages, SUM(s.duration_seconds) AS seconds "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        "WHERE s.date != '' AND b.library_id = ? GROUP BY s.date", (lib_id,)
    ).fetchall():
        daily_sessions[row["date"]] = {"pages": row["pages"], "seconds": row["seconds"]}

    # 2. Period pages (attributed to end_date; periods have no time granularity)
    daily_periods: dict[str, int] = {}
    for row in db.execute(
        "SELECT p.end_date, SUM(p.pages) AS pages "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        "WHERE p.end_date != '' AND p.pages > 0 AND b.library_id = ? GROUP BY p.end_date", (lib_id,)
    ).fetchall():
        daily_periods[row["end_date"]] = row["pages"]

    # Session-only daily data (for personal records – no periods)
    session_daily_data = [
        {"date": d, "pages": v["pages"], "seconds": v["seconds"]}
        for d, v in sorted(daily_sessions.items())
    ]

    # Merge into daily_data list
    all_dates = sorted(set(daily_sessions) | set(daily_periods))
    daily_data = []
    for d in all_dates:
        s = daily_sessions.get(d, {"pages": 0, "seconds": 0})
        p = daily_periods.get(d, 0)
        daily_data.append({
            "date": d,
            "pages": s["pages"] + p,
            "seconds": s["seconds"],
        })

    # 3. Book activity by date (for "active books in period")
    session_book_dates: list[dict] = []
    for row in db.execute(
        "SELECT DISTINCT s.date, s.book_id FROM sessions s "
        "JOIN books b ON b.id = s.book_id WHERE s.date != '' AND b.library_id = ?", (lib_id,)
    ).fetchall():
        session_book_dates.append({"date": row["date"], "book_id": row["book_id"]})
    for row in db.execute(
        "SELECT DISTINCT p.end_date AS date, p.book_id "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        "WHERE p.end_date != '' AND p.pages > 0 AND b.library_id = ?", (lib_id,)
    ).fetchall():
        session_book_dates.append({"date": row["date"], "book_id": row["book_id"]})

    # 4. Book lookup (id → {name, has_cover})
    all_books: dict[str, dict] = {}
    for row in db.execute("SELECT id, name, has_cover, cover_hash FROM books WHERE library_id = ?", (lib_id,)).fetchall():
        all_books[row["id"]] = {"name": row["name"], "has_cover": bool(row["has_cover"]), "cover_hash": row["cover_hash"] or ""}

    # 5. Books currently being read (for estimated finish dates)
    reading_books: list[dict] = []
    for row in db.execute("""
        SELECT b.id, b.name, b.pages, b.starting_page, b.has_cover, b.cover_hash,
               b.format,
               COALESCE(s.tp, 0) AS session_pages,
               COALESCE(p.pp, 0) AS period_pages,
               s.last_date, p.last_period,
               COALESCE(pct.max_pct, 0) AS max_pct
        FROM books b
        LEFT JOIN (SELECT book_id, SUM(pages) AS tp,
                          MAX(date) AS last_date
                   FROM sessions WHERE date != '' GROUP BY book_id) s
          ON s.book_id = b.id
        LEFT JOIN (SELECT book_id, SUM(pages) AS pp,
                          MAX(end_date) AS last_period
                   FROM periods GROUP BY book_id) p
          ON p.book_id = b.id
        LEFT JOIN (
            SELECT book_id, MAX(pct) AS max_pct FROM (
                SELECT book_id, MAX(progress_pct) AS pct FROM sessions WHERE progress_pct IS NOT NULL GROUP BY book_id
                UNION ALL
                SELECT book_id, MAX(progress_pct) AS pct FROM periods WHERE progress_pct IS NOT NULL GROUP BY book_id
            ) GROUP BY book_id
        ) pct ON pct.book_id = b.id
        WHERE b.status = 'reading' AND b.library_id = ?
    """, (lib_id,)).fetchall():
        sp = row["starting_page"] or 0
        tp = row["pages"] or 0
        eff = tp - sp if sp > 0 else tp
        book_fmt = row["format"] or "paper"
        is_pct_fmt = book_fmt in ("audiobook", "ebook")
        if is_pct_fmt:
            total_read = 0
            remaining = 0
            prog_pct = round(row["max_pct"], 1)
        else:
            total_read = row["session_pages"] + row["period_pages"]
            remaining = max(eff - total_read, 0)
            prog_pct = round(min(total_read / eff * 100, 100), 1) if eff > 0 else 0
        last_candidates = [d for d in (row["last_date"], row["last_period"]) if d]
        last_activity = max(last_candidates) if last_candidates else "0000-00-00"
        reading_books.append({
            "id": row["id"],
            "name": row["name"],
            "has_cover": bool(row["has_cover"]),
            "cover_hash": row["cover_hash"] or "",
            "total_pages": tp,
            "effective_pages": eff,
            "pages_read": total_read,
            "pages_remaining": remaining,
            "progress_pct": prog_pct,
            "last_activity": last_activity,
        })
    reading_books.sort(key=lambda b: b["last_activity"], reverse=True)

    # 6. Per-book daily sessions for reading books (pace estimation)
    book_daily: dict[str, list] = {}
    reading_ids = [b["id"] for b in reading_books]
    if reading_ids:
        ph = ",".join("?" * len(reading_ids))
        for row in db.execute(
            f"SELECT book_id, date, SUM(pages) AS pages "
            f"FROM sessions WHERE book_id IN ({ph}) AND date != '' "
            f"GROUP BY book_id, date", reading_ids,
        ).fetchall():
            book_daily.setdefault(row["book_id"], []).append(
                {"date": row["date"], "pages": row["pages"]}
            )

    # 7. Individual sessions (for longest single session record)
    all_sessions: list[dict] = []
    for row in db.execute(
        "SELECT s.date, s.pages, s.duration_seconds, s.book_id "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        "WHERE s.date != '' AND b.library_id = ? ORDER BY s.date", (lib_id,)
    ).fetchall():
        all_sessions.append({
            "date": row["date"],
            "pages": row["pages"],
            "seconds": row["duration_seconds"],
            "book_id": row["book_id"],
        })

    # 8. Aggregate totals for records
    row = db.execute(
        "SELECT COALESCE(SUM(s.pages),0) AS p, COALESCE(SUM(s.duration_seconds),0) AS s "
        "FROM sessions s JOIN books b ON b.id = s.book_id WHERE b.library_id = ?", (lib_id,)
    ).fetchone()
    total_all_session_pages = row["p"]
    total_all_session_seconds = row["s"]
    row = db.execute(
        "SELECT COALESCE(SUM(p.pages),0) AS p FROM periods p "
        "JOIN books b ON b.id = p.book_id WHERE b.library_id = ?", (lib_id,)
    ).fetchone()
    total_all_period_pages = row["p"]
    total_all_pages = total_all_session_pages + total_all_period_pages
    total_all_seconds = total_all_session_seconds  # only sessions have time

    books_finished_count = db.execute(
        "SELECT COUNT(DISTINCT COALESCE(b.work_id, b.id)) AS c FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        "WHERE r.status = 'finished' AND b.library_id = ?", (lib_id,)
    ).fetchone()["c"]

    # Books active per day (for most-books-in-parallel record)
    books_per_day: dict[str, set] = {}
    for row in db.execute(
        "SELECT DISTINCT s.date, s.book_id FROM sessions s "
        "JOIN books b ON b.id = s.book_id WHERE s.date != '' AND b.library_id = ?", (lib_id,)
    ).fetchall():
        books_per_day.setdefault(row["date"], set()).add(row["book_id"])
    most_parallel = {"count": 0, "date": ""}
    for d, bids in books_per_day.items():
        if len(bids) > most_parallel["count"]:
            most_parallel = {"count": len(bids), "date": d}

    # 9. Longest finished book & most re-read book (for personal records)
    longest_finished_book = None
    finished_books = db.execute("""
        SELECT DISTINCT b.id, b.name, b.pages, b.has_cover
        FROM books b
        JOIN readings r ON r.book_id = b.id
        WHERE r.status = 'finished' AND b.pages > 0 AND b.library_id = ?
          AND (b.work_id IS NULL OR b.is_primary_edition = 1)
        ORDER BY b.pages DESC
        LIMIT 1
    """, (lib_id,)).fetchone()
    if finished_books:
        longest_finished_book = {
            "name": finished_books["name"],
            "id": finished_books["id"],
            "pages": finished_books["pages"],
        }

    most_reread_book = None
    reread_row = db.execute(
        "SELECT COALESCE(b.work_id, r.book_id) AS wid, COUNT(*) AS cnt FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        "WHERE b.library_id = ? GROUP BY wid HAVING cnt > 1 ORDER BY cnt DESC LIMIT 1",
        (lib_id,)
    ).fetchone()
    if reread_row:
        rbk = db.execute(
            "SELECT id, name FROM books WHERE (work_id = ? OR id = ?) "
            "ORDER BY is_primary_edition DESC LIMIT 1",
            (reread_row["wid"], reread_row["wid"]),
        ).fetchone()
        if rbk:
            most_reread_book = {
                "name": rbk["name"],
                "id": rbk["id"],
                "count": reread_row["cnt"],
            }

    return render_template(
        "activity.html",
        daily_data=daily_data,
        session_daily_data=session_daily_data,
        session_book_dates=session_book_dates,
        all_books=all_books,
        reading_books=reading_books,
        book_daily=book_daily,
        all_sessions=all_sessions,
        total_all_pages=total_all_pages,
        total_all_seconds=total_all_seconds,
        books_finished_count=books_finished_count,
        most_parallel=most_parallel,
        longest_finished_book=longest_finished_book,
        most_reread_book=most_reread_book,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Authors
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/authors")
def authors_list():
    """Display a list of all authors with their book counts."""
    db = get_db()
    lib_id = _get_current_library_id()
    rows = db.execute("SELECT id, name, author, has_cover, cover_hash, status FROM books WHERE library_id = ?", (lib_id,)).fetchall()

    # Build a map of author names that have photos → photo_hash
    author_photo_info: dict[str, str] = {}
    for ar in db.execute("SELECT name, photo_hash FROM authors WHERE has_photo = 1 AND library_id = ?", (lib_id,)).fetchall():
        author_photo_info[ar["name"]] = ar["photo_hash"] or ""

    author_map: dict[str, list[dict]] = {}
    for r in rows:
        raw_author = (r["author"] or "").strip()
        if not raw_author:
            raw_author = "Unknown"
        individual_authors = [a.strip() for a in raw_author.split(";") if a.strip()]
        if not individual_authors:
            individual_authors = ["Unknown"]
        book_entry = {
            "id": r["id"],
            "name": r["name"],
            "has_cover": bool(r["has_cover"]),
            "cover_hash": r["cover_hash"] or "",
            "status": r["status"],
        }
        for author in individual_authors:
            author_map.setdefault(author, []).append(book_entry)

    sort = request.args.get("sort", "name")
    authors = [
        {"name": name, "books": bks, "book_count": len(bks),
         "has_photo": name in author_photo_info,
         "photo_hash": author_photo_info.get(name, "")}
        for name, bks in author_map.items()
    ]
    if sort == "books":
        authors.sort(key=lambda a: (-a["book_count"], a["name"].lower()))
    else:
        authors.sort(key=lambda a: a["name"].lower())
    return render_template("authors.html", authors=authors, sort=sort)


@app.route("/authors/<path:author_name>")
def author_detail(author_name: str):
    """Display all books by a given author, plus author metadata."""
    db = get_db()
    lib_id = _get_current_library_id()
    show_editions = request.args.get("show_editions") or request.cookies.get("librarium_author_show_editions", "0")
    edition_filter = " AND (work_id IS NULL OR is_primary_edition = 1)" if show_editions != "1" else ""
    rows = db.execute(
        "SELECT id, name, subtitle, author, has_cover, cover_hash, status, original_publication_date "
        f"FROM books WHERE library_id = ?{edition_filter}", (lib_id,)
    ).fetchall()

    sort = request.args.get("sort", "date")  # date = original publication date

    books = []
    for r in rows:
        raw_author = (r["author"] or "").strip()
        individual = [a.strip() for a in raw_author.split(";") if a.strip()] or ["Unknown"]
        if author_name not in individual:
            continue
        ratings = _load_ratings(r["id"])
        avg = _calc_avg_rating(ratings)
        books.append({
            "id": r["id"],
            "name": r["name"],
            "subtitle": r["subtitle"] or "",
            "has_cover": bool(r["has_cover"]),
            "cover_hash": r["cover_hash"] or "",
            "status": r["status"],
            "original_publication_date": r["original_publication_date"] or "",
            "rating": avg or 0,
        })

    if sort == "alpha":
        books.sort(key=lambda b: b["name"].lower())
    elif sort == "rating":
        books.sort(key=lambda b: (-b["rating"], b["name"].lower()))
    else:  # "date" – original publication date
        books.sort(key=lambda b: (b["original_publication_date"] or "9999", b["name"].lower()))

    # Load author metadata (if exists)
    author_row = db.execute("SELECT * FROM authors WHERE name = ? AND library_id = ?", (author_name, lib_id)).fetchone()
    author_info = dict(author_row) if author_row else {
        "name": author_name, "has_photo": 0, "photo_hash": "", "birth_date": "",
        "birth_place": "", "death_date": "", "death_place": "", "biography": "",
    }
    resp = make_response(render_template("author_detail.html", author=author_name,
                           books=books, author_info=author_info, sort=sort,
                           show_editions=show_editions))
    resp.set_cookie("librarium_author_show_editions", show_editions, max_age=365*24*3600, samesite="Lax")
    return resp


@app.route("/author_photo/<path:author_name>")
def author_photo(author_name: str):
    """Serve the author's photo from the database."""
    db = get_db()
    lib_id = _get_current_library_id()

    # Lightweight hash-only check for conditional requests
    etag_from_client = request.headers.get("If-None-Match", "").strip(' "')
    if etag_from_client:
        hash_row = db.execute(
            "SELECT photo_hash FROM authors WHERE name = ? AND library_id = ? AND has_photo = 1",
            (author_name, lib_id)
        ).fetchone()
        if hash_row and hash_row["photo_hash"] and hash_row["photo_hash"] == etag_from_client:
            resp = make_response("", 304)
            resp.headers["ETag"] = f'"{ hash_row["photo_hash"] }"'
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp

    row = db.execute("SELECT photo, photo_hash FROM authors WHERE name = ? AND library_id = ? AND has_photo = 1",
                     (author_name, lib_id)).fetchone()
    if not row or not row["photo"]:
        abort(404)

    photo_hash = row["photo_hash"] or hashlib.md5(row["photo"]).hexdigest()[:12]
    resp = make_response(row["photo"])
    resp.headers["Content-Type"] = "image/jpeg"
    resp.headers["ETag"] = f'"{photo_hash}"'
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


@app.route("/authors/<path:author_name>/edit", methods=["GET", "POST"])
def edit_author(author_name: str):
    """Edit author metadata (photo, dates, places, biography)."""
    db = get_db()
    lib_id = _get_current_library_id()

    # Ensure author row exists
    author_row = db.execute("SELECT * FROM authors WHERE name = ? AND library_id = ?", (author_name, lib_id)).fetchone()
    if not author_row:
        # Auto-create a skeleton row
        db.execute("INSERT INTO authors (name, library_id) VALUES (?, ?)", (author_name, lib_id))
        db.commit()
        author_row = db.execute("SELECT * FROM authors WHERE name = ? AND library_id = ?", (author_name, lib_id)).fetchone()

    author_info = dict(author_row)

    if request.method == "POST":
        author_info["birth_date"] = request.form.get("birth_date", "").strip()
        author_info["birth_place"] = request.form.get("birth_place", "").strip()
        author_info["death_date"] = request.form.get("death_date", "").strip()
        author_info["death_place"] = request.form.get("death_place", "").strip()
        author_info["biography"] = sanitize_html(request.form.get("biography", "").strip())

        db.execute("""
            UPDATE authors SET
                birth_date=?, birth_place=?, death_date=?, death_place=?, biography=?
            WHERE name=? AND library_id=?
        """, (
            author_info["birth_date"], author_info["birth_place"],
            author_info["death_date"], author_info["death_place"],
            author_info["biography"], author_name, lib_id,
        ))
        db.commit()

        # Handle photo upload
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            photo_blob = photo_file.read()
            photo_hash = hashlib.md5(photo_blob).hexdigest()[:12]
            db.execute("UPDATE authors SET photo = ?, has_photo = 1, photo_hash = ? WHERE name = ? AND library_id = ?",
                       (photo_blob, photo_hash, author_name, lib_id))
            db.commit()

        # Handle photo removal
        if request.form.get("remove_photo") == "1":
            db.execute("UPDATE authors SET photo = NULL, has_photo = 0, photo_hash = '' WHERE name = ? AND library_id = ?",
                       (author_name, lib_id))
            db.commit()

        flash("Author details updated.", "success")
        return redirect(url_for("author_detail", author_name=author_name))

    return render_template("edit_author.html", author_name=author_name,
                           author_info=author_info)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Series
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/series")
def series_list():
    """Display all series in the current library."""
    db = get_db()
    lib_id = _get_current_library_id()

    rows = db.execute("""
        SELECT s.id, s.name,
               COUNT(CASE WHEN b.work_id IS NULL OR b.is_primary_edition = 1 THEN 1 END) AS book_count
        FROM series s
        LEFT JOIN book_series bs ON bs.series_id = s.id
        LEFT JOIN books b ON b.id = bs.book_id
        WHERE s.library_id = ?
        GROUP BY s.id
        ORDER BY s.name COLLATE NOCASE
    """, (lib_id,)).fetchall()

    series = []
    for r in rows:
        # Fetch up to 10 covers for the collage (ordered by series index)
        cover_books = db.execute("""
            SELECT b.id, b.cover_hash
            FROM books b
            JOIN book_series bs ON bs.book_id = b.id
            WHERE bs.series_id = ? AND b.has_cover = 1
              AND (b.work_id IS NULL OR b.is_primary_edition = 1)
            ORDER BY CAST(bs.series_index AS REAL) ASC, COALESCE(NULLIF(b.original_publication_date, ''), '9999') ASC
            LIMIT 10
        """, (r["id"],)).fetchall()
        series.append({
            "id": r["id"],
            "name": r["name"],
            "book_count": r["book_count"],
            "covers": [{"id": c["id"], "cover_hash": c["cover_hash"] or ""} for c in cover_books],
        })

    sort = request.args.get("sort", "name")
    if sort == "books":
        series.sort(key=lambda s: (-s["book_count"], s["name"].lower()))
    else:
        series.sort(key=lambda s: s["name"].lower())

    return render_template("series.html", series=series, sort=sort)


@app.route("/series/<int:series_id>")
def series_detail(series_id: int):
    """Display all books in a series, ordered by series index."""
    db = get_db()
    lib_id = _get_current_library_id()

    series_row = db.execute(
        "SELECT * FROM series WHERE id = ? AND library_id = ?", (series_id, lib_id)
    ).fetchone()
    if not series_row:
        abort(404)
    series_info = dict(series_row)

    rows = db.execute("""
        SELECT b.id, b.name, b.subtitle, b.author, b.has_cover, b.cover_hash, b.status,
               b.original_publication_date, bs.series_index
        FROM books b
        JOIN book_series bs ON bs.book_id = b.id
        WHERE bs.series_id = ? AND b.library_id = ?
              AND (b.work_id IS NULL OR b.is_primary_edition = 1)
    """, (series_id, lib_id)).fetchall()

    books = []
    for r in rows:
        ratings = _load_ratings(r["id"])
        avg = _calc_avg_rating(ratings)
        idx_raw = (r["series_index"] or "").strip()
        try:
            idx_num = float(idx_raw) if idx_raw else None
        except (ValueError, TypeError):
            idx_num = None
        books.append({
            "id": r["id"],
            "name": r["name"],
            "subtitle": r["subtitle"] or "",
            "author": r["author"] or "",
            "has_cover": bool(r["has_cover"]),
            "cover_hash": r["cover_hash"] or "",
            "status": r["status"],
            "original_publication_date": r["original_publication_date"] or "",
            "series_index": idx_raw,
            "series_index_num": idx_num,
            "rating": avg or 0,
        })

    # Sort: books with numeric index first (by index), then books without index (by original_publication_date)
    indexed = [b for b in books if b["series_index_num"] is not None]
    unindexed = [b for b in books if b["series_index_num"] is None]
    indexed.sort(key=lambda b: b["series_index_num"])
    unindexed.sort(key=lambda b: (b["original_publication_date"] or "9999", b["name"].lower()))
    books = indexed + unindexed

    return render_template("series_detail.html", series=series_info, books=books)


@app.route("/series/<int:series_id>/rename", methods=["POST"])
def rename_series(series_id: int):
    """Rename a series."""
    db = get_db()
    lib_id = _get_current_library_id()
    new_name = request.form.get("name", "").strip()
    if not new_name:
        flash("Series name cannot be empty.", "error")
        return redirect(url_for("series_detail", series_id=series_id))
    db.execute("UPDATE series SET name = ? WHERE id = ? AND library_id = ?",
               (new_name, series_id, lib_id))
    db.commit()
    flash("Series renamed.", "success")
    return redirect(url_for("series_detail", series_id=series_id))


@app.route("/series/<int:series_id>/delete", methods=["POST"])
def delete_series(series_id: int):
    """Delete a series (unlinks books but doesn't delete them)."""
    db = get_db()
    lib_id = _get_current_library_id()
    db.execute("""
        DELETE FROM book_series WHERE series_id = ? AND book_id IN (
            SELECT id FROM books WHERE library_id = ?
        )
    """, (series_id, lib_id))
    db.execute("DELETE FROM series WHERE id = ? AND library_id = ?", (series_id, lib_id))
    db.commit()
    flash("Series deleted.", "success")
    return redirect(url_for("series_list"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Editions
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/link-edition", methods=["POST"])
def link_edition(book_id: str):
    """Link an existing book as another edition of the same work."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)
    target_id = request.form.get("target_book_id", "").strip()
    if not target_id or target_id == book_id:
        flash("Invalid target book.", "error")
        return redirect(url_for("book_detail", book_id=book_id))
    target = db.execute("SELECT * FROM books WHERE id = ?", (target_id,)).fetchone()
    if not target:
        flash("Target book not found.", "error")
        return redirect(url_for("book_detail", book_id=book_id))

    # Determine or create work_id
    work_id = book["work_id"] or target["work_id"]
    if not work_id:
        # Neither book is part of a work yet. Use the current book id as work_id.
        work_id = book_id

    # Assign work_id to both books. Current book is primary if it was standalone.
    db.execute("UPDATE books SET work_id = ?, is_primary_edition = 1 WHERE id = ?", (work_id, book_id))
    db.execute("UPDATE books SET work_id = ?, is_primary_edition = 0 WHERE id = ?", (work_id, target_id))
    # If the target already had other editions, absorb them too
    if target["work_id"] and target["work_id"] != work_id:
        db.execute("UPDATE books SET work_id = ? WHERE work_id = ?", (work_id, target["work_id"]))
    db.commit()
    flash("Books linked as editions of the same work.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/book/<book_id>/unlink-edition", methods=["POST"])
def unlink_edition(book_id: str):
    """Remove a book from an edition group, making it standalone again."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book or not book["work_id"]:
        abort(404)

    work_id = book["work_id"]
    was_primary = bool(book["is_primary_edition"])

    # Make this book standalone
    db.execute("UPDATE books SET work_id = NULL, is_primary_edition = 1 WHERE id = ?", (book_id,))

    # If this was the primary, promote another edition
    if was_primary:
        remaining = db.execute(
            "SELECT id FROM books WHERE work_id = ? ORDER BY name COLLATE NOCASE LIMIT 1",
            (work_id,),
        ).fetchone()
        if remaining:
            db.execute("UPDATE books SET is_primary_edition = 1 WHERE id = ?", (remaining["id"],))

    # If only one edition remains in the group, dissolve the group
    remaining_count = db.execute(
        "SELECT COUNT(*) AS c FROM books WHERE work_id = ?", (work_id,)
    ).fetchone()["c"]
    if remaining_count == 1:
        db.execute("UPDATE books SET work_id = NULL, is_primary_edition = 1 WHERE work_id = ?", (work_id,))

    db.commit()
    flash("Book unlinked from edition group.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/book/<book_id>/set-primary-edition", methods=["POST"])
def set_primary_edition(book_id: str):
    """Set this edition as the primary edition for its work."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book or not book["work_id"]:
        abort(404)
    work_id = book["work_id"]
    db.execute("UPDATE books SET is_primary_edition = 0 WHERE work_id = ?", (work_id,))
    db.execute("UPDATE books SET is_primary_edition = 1 WHERE id = ?", (book_id,))
    db.commit()
    flash("Primary edition updated.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Book detail
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>")
def book_detail(book_id: str):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    # Build an info dict that the template accesses via info.get(...)
    info = dict(book)

    # ── Load all readings ──
    readings_rows = db.execute(
        "SELECT id, reading_number, status, notes FROM readings "
        "WHERE book_id = ? ORDER BY reading_number",
        (book_id,),
    ).fetchall()
    # Ensure at least one reading exists
    if not readings_rows:
        _get_current_reading_id(db, book_id)
        readings_rows = db.execute(
            "SELECT id, reading_number, status, notes FROM readings "
            "WHERE book_id = ? ORDER BY reading_number",
            (book_id,),
        ).fetchall()

    current_reading = readings_rows[-1]  # default: latest reading
    current_reading_id = current_reading["id"]

    # Allow selecting a specific reading via query param
    selected_reading_num = request.args.get("reading", "")
    if selected_reading_num:
        for rr in readings_rows:
            if str(rr["reading_number"]) == selected_reading_num:
                current_reading = rr
                current_reading_id = rr["id"]
                break

    # ── Load ALL sessions (with reading_id) ──
    sessions_rows = db.execute(
        "SELECT id, date, pages, duration_seconds, reading_id, progress_pct "
        "FROM sessions WHERE book_id = ? ORDER BY id",
        (book_id,),
    ).fetchall()
    all_sessions_data = []
    for sr in sessions_rows:
        all_sessions_data.append({
            "id": sr["id"],
            "date": sr["date"],
            "pages": sr["pages"],
            "duration_seconds": sr["duration_seconds"],
            "duration_display": _format_duration(sr["duration_seconds"]),
            "reading_id": sr["reading_id"],
            "progress_pct": sr["progress_pct"],
        })

    # ── Load ALL periods (with reading_id) ──
    periods_rows = db.execute(
        "SELECT id, start_date, end_date, pages, note, reading_id, progress_pct, duration_seconds "
        "FROM periods WHERE book_id = ? ORDER BY id",
        (book_id,),
    ).fetchall()
    all_periods_data = [dict(pr) for pr in periods_rows]

    # ── Build per-reading summary ──
    def _fmt_date(iso: str) -> str:
        try:
            dt = datetime.strptime(iso, "%Y-%m-%d")
            return f"{dt.strftime('%b')} {dt.day}, {dt.year}"
        except ValueError:
            return iso

    book_fmt = info.get("format", "paper") or "paper"
    is_pct_format = book_fmt in ("audiobook", "ebook")

    readings_data = []
    for rr in readings_rows:
        rid = rr["id"]
        r_sessions = [s for s in all_sessions_data if s["reading_id"] == rid]
        r_periods  = [p for p in all_periods_data  if p["reading_id"] == rid]

        if is_pct_format:
            r_pcts = [s["progress_pct"] for s in r_sessions if s.get("progress_pct") is not None]
            r_pcts += [p["progress_pct"] for p in r_periods if p.get("progress_pct") is not None]
            r_total_pages = max(r_pcts) if r_pcts else 0  # stores % for display
            r_sess_secs = sum(s["duration_seconds"] for s in r_sessions)
            r_total_secs = r_sess_secs
        else:
            r_sess_pages = sum(s["pages"] for s in r_sessions)
            r_sess_secs  = sum(s["duration_seconds"] for s in r_sessions)
            r_per_pages  = sum(p["pages"] for p in r_periods)
            r_per_secs   = 0
            if r_per_pages > 0 and r_sess_pages > 0:
                r_per_secs = int(r_per_pages * (r_sess_secs / r_sess_pages))
            r_total_pages = r_sess_pages + r_per_pages
            r_total_secs  = r_sess_secs + r_per_secs

        sess_dates   = [s["date"] for s in r_sessions if s["date"]]
        per_starts   = [p["start_date"] for p in r_periods if p.get("start_date")]
        per_ends     = [p["end_date"]   for p in r_periods if p.get("end_date")]
        first_raw    = min(sess_dates + per_starts) if (sess_dates + per_starts) else None
        last_raw     = max(sess_dates + per_ends)   if (sess_dates + per_ends)   else None

        readings_data.append({
            "id": rid,
            "reading_number": rr["reading_number"],
            "status": rr["status"],
            "notes": rr["notes"],
            "total_pages": r_total_pages,
            "total_time": _format_duration(r_total_secs),
            "session_count": len(r_sessions),
            "date_started": _fmt_date(first_raw) if first_raw else None,
            "date_finished": _fmt_date(last_raw) if last_raw and rr["status"] == "finished" else None,
        })

    # ── Current reading stats ──
    cur_sessions = [s for s in all_sessions_data if s["reading_id"] == current_reading_id]
    cur_periods  = [p for p in all_periods_data  if p["reading_id"] == current_reading_id]

    tracked_seconds = sum(s["duration_seconds"] for s in cur_sessions)

    if is_pct_format:
        cur_pcts = [s["progress_pct"] for s in cur_sessions if s.get("progress_pct") is not None]
        cur_pcts += [p["progress_pct"] for p in cur_periods if p.get("progress_pct") is not None]
        max_pct = max(cur_pcts) if cur_pcts else 0.0
        total_pages = max_pct  # stores % value
        total_seconds = tracked_seconds
        tracked_pages = 0
        period_pages = 0
    else:
        tracked_pages = sum(s["pages"] for s in cur_sessions)
        period_pages = sum(p["pages"] for p in cur_periods)
        period_seconds = 0
        if period_pages > 0 and tracked_pages > 0:
            period_seconds = int(period_pages * (tracked_seconds / tracked_pages))
        total_pages = tracked_pages + period_pages
        total_seconds = tracked_seconds + period_seconds

    starting_page = info.get("starting_page", 0) or 0
    total_book_pages = info.get("pages", 0) or 0
    effective_pages = total_book_pages - starting_page if starting_page > 0 else total_book_pages

    # Default date for "Add Session" form: last session date from current reading
    last_session_row = db.execute(
        "SELECT date FROM sessions WHERE reading_id = ? AND date != '' ORDER BY date DESC LIMIT 1",
        (current_reading_id,),
    ).fetchone()
    last_date = last_session_row["date"] if last_session_row else ""

    unique_dates = set(s["date"] for s in cur_sessions if s["date"])
    reading_days = len(unique_dates)
    avg_pages_per_day = (tracked_pages / reading_days) if (reading_days > 0 and not is_pct_format) else 0

    # Max pages and minutes on any single day (current reading)
    pages_by_date: dict[str, int] = {}
    seconds_by_date: dict[str, int] = {}
    for s in cur_sessions:
        if s["date"]:
            pages_by_date[s["date"]] = pages_by_date.get(s["date"], 0) + s["pages"]
            seconds_by_date[s["date"]] = seconds_by_date.get(s["date"], 0) + s["duration_seconds"]
    max_pages_per_day = (max(pages_by_date.values()) if pages_by_date else 0) if not is_pct_format else 0
    _max_seconds_per_day = max(seconds_by_date.values()) if seconds_by_date else 0
    max_time_per_day = _format_duration(_max_seconds_per_day) if _max_seconds_per_day > 0 else ""

    avg_pages_per_hour = 0.0
    if tracked_seconds > 0 and not is_pct_format:
        avg_pages_per_hour = tracked_pages / (tracked_seconds / 3600)

    status = info.get("status", "")
    progress_pct = 0.0
    pages_remaining = 0
    est_time_to_finish = ""

    if is_pct_format:
        progress_pct = min(total_pages, 100.0)  # total_pages holds % for audiobook/ebook
        # Est. time to finish based on content time for audiobooks
        audiobook_total = info.get("total_time_seconds") or 0
        if audiobook_total > 0 and progress_pct > 0 and progress_pct < 100 and status == "reading":
            remaining_content = audiobook_total * (1 - progress_pct / 100)
            est_time_to_finish = _format_duration(int(remaining_content))
    else:
        if effective_pages > 0 and total_pages > 0:
            progress_pct = min(total_pages / effective_pages * 100, 100.0)
            pages_remaining = max(effective_pages - total_pages, 0)
        if pages_remaining > 0 and avg_pages_per_hour > 0 and status == "reading":
            est_seconds = int(pages_remaining / avg_pages_per_hour * 3600)
            est_time_to_finish = _format_duration(est_seconds)

    source_obj = None
    if info.get("source_id"):
        source_obj = _get_source_by_id(info["source_id"])

    # Date Started and Date Finished (current reading)
    cur_sess_dates   = [s["date"]       for s in cur_sessions if s["date"]]
    cur_per_starts   = [p["start_date"] for p in cur_periods  if p.get("start_date")]
    cur_per_ends     = [p["end_date"]   for p in cur_periods  if p.get("end_date")]
    _ds_raw = min(cur_sess_dates + cur_per_starts) if (cur_sess_dates + cur_per_starts) else None
    _df_raw = max(cur_sess_dates + cur_per_ends)   if (cur_sess_dates + cur_per_ends)   else None
    date_started  = _fmt_date(_ds_raw)  if _ds_raw  else None
    date_finished = _fmt_date(_df_raw)  if _df_raw  else None

    ratings = _load_ratings(book_id)
    avg_rating = _calc_avg_rating(ratings)

    # ── Build Gantt timeline for this book (per-reading bars) ──
    from datetime import timedelta as _td
    book_color = info.get("cover_color", "") or "#888888"

    # Collect active dates per reading
    reading_active_dates: dict[str, set[date]] = {}  # reading_id → set of dates
    for s in all_sessions_data:
        if s["date"] and s["reading_id"]:
            rid = s["reading_id"]
            reading_active_dates.setdefault(rid, set())
            try:
                reading_active_dates[rid].add(date.fromisoformat(s["date"]))
            except (ValueError, TypeError):
                pass
    for p in all_periods_data:
        sd_str = p.get("start_date", "")
        ed_str = p.get("end_date", "")
        rid = p.get("reading_id")
        if sd_str and ed_str and rid:
            reading_active_dates.setdefault(rid, set())
            try:
                sd = date.fromisoformat(sd_str)
                ed = date.fromisoformat(ed_str)
                d = sd
                while d <= ed:
                    reading_active_dates[rid].add(d)
                    d += _td(days=1)
            except (ValueError, TypeError):
                pass

    # Only include the currently selected reading in the Gantt
    current_gantt_dates = reading_active_dates.get(current_reading_id, set())

    book_gantt_data = None
    if current_gantt_dates:
        global_start = min(current_gantt_dates)
        global_end = max(current_gantt_dates)
        total_span_days = (global_end - global_start).days + 1

        def _build_segments(sorted_active, ref_start):
            segs = []
            if not sorted_active:
                return segs
            seg_s = sorted_active[0]
            seg_e = sorted_active[0]
            for d in sorted_active[1:]:
                if (d - seg_e).days <= 1:
                    seg_e = d
                else:
                    segs.append({"start": (seg_s - ref_start).days, "end": (seg_e - ref_start).days})
                    seg_s = d
                    seg_e = d
            segs.append({"start": (seg_s - ref_start).days, "end": (seg_e - ref_start).days})
            return segs

        # Build bar for the current reading only
        gantt_readings = []
        for rr in readings_rows:
            rid = rr["id"]
            if rid != current_reading_id:
                continue
            dates = reading_active_dates.get(rid, set())
            if not dates:
                continue
            sorted_d = sorted(dates)
            gantt_readings.append({
                "reading_number": rr["reading_number"],
                "reading_id": rid,
                "segments": _build_segments(sorted_d, global_start),
                "start_day": (sorted_d[0] - global_start).days,
                "end_day": (sorted_d[-1] - global_start).days,
                "start_label": sorted_d[0].isoformat(),
                "end_label": sorted_d[-1].isoformat(),
            })

        # Build month labels relative to global span
        gantt_months = []
        total_months_approx = total_span_days / 30.4
        if total_months_approx > 48:
            month_step = 12
        elif total_months_approx > 24:
            month_step = 6
        elif total_months_approx > 12:
            month_step = 3
        else:
            month_step = 1
        m_date = global_start.replace(day=1)
        month_idx = 0
        while m_date <= global_end:
            label_date = max(m_date, global_start)
            offset_day = (label_date - global_start).days
            if offset_day <= total_span_days * 0.95:
                if month_idx % month_step == 0:
                    gantt_months.append({
                        "label": label_date.strftime("%b %Y") if total_span_days > 60 else label_date.strftime("%b %d"),
                        "offset": offset_day,
                    })
            month_idx += 1
            if m_date.month == 12:
                m_date = m_date.replace(year=m_date.year + 1, month=1)
            else:
                m_date = m_date.replace(month=m_date.month + 1)

        book_gantt_data = {
            "color": book_color,
            "readings": gantt_readings,
            "total_days": total_span_days,
            "months": gantt_months,
            "start_label": global_start.isoformat(),
            "end_label": global_end.isoformat(),
        }

    # Build reading_id → reading_number map for template
    reading_num_map = {rr["id"]: rr["reading_number"] for rr in readings_rows}

    # Series info (many-to-many)
    series_list_book = []
    sr_rows = db.execute("""
        SELECT s.id, s.name, bs.series_index
        FROM book_series bs
        JOIN series s ON s.id = bs.series_id
        WHERE bs.book_id = ?
        ORDER BY s.name COLLATE NOCASE
    """, (book_id,)).fetchall()
    for sr in sr_rows:
        series_list_book.append({"id": sr["id"], "name": sr["name"], "series_index": sr["series_index"] or ""})

    # ── Edition data ────────────────────────────────────────────────────
    work_id = info.get("work_id")
    editions = []
    work_total_readings = 0
    if work_id:
        editions = _get_editions(db, work_id)
        # Count total finished readings across all editions of this work
        ed_ids = [e["id"] for e in editions]
        if ed_ids:
            ph = ",".join("?" * len(ed_ids))
            work_total_readings = db.execute(
                f"SELECT COUNT(*) AS c FROM readings WHERE book_id IN ({ph}) AND status = 'finished'",
                ed_ids,
            ).fetchone()["c"]

    # Books that can be linked as editions (same library, not already in this work group)
    exclude_ids = [e["id"] for e in editions] if editions else [book_id]
    ph = ",".join("?" * len(exclude_ids))
    all_linkable_books = db.execute(
        f"SELECT id, name, language FROM books WHERE library_id = ? AND id NOT IN ({ph}) ORDER BY name COLLATE NOCASE",
        [info["library_id"]] + exclude_ids,
    ).fetchall()

    return render_template(
        "book_detail.html",
        book_id=book_id,
        info=info,
        sessions=cur_sessions,
        all_sessions=all_sessions_data,
        total_pages=total_pages,
        total_time=_format_duration(total_seconds),
        effective_pages=effective_pages,
        has_cover=bool(info.get("has_cover")),
        last_date=last_date,
        reading_days=reading_days,
        avg_pages_per_day=avg_pages_per_day,
        avg_pages_per_hour=avg_pages_per_hour,
        max_pages_per_day=max_pages_per_day,
        max_time_per_day=max_time_per_day,
        progress_pct=progress_pct,
        pages_remaining=pages_remaining,
        est_time_to_finish=est_time_to_finish,
        is_pct_format=is_pct_format,
        reading_periods=cur_periods,
        all_periods=all_periods_data,
        now_year=datetime.now().year,
        source_obj=source_obj,
        ratings=ratings,
        avg_rating=avg_rating,
        rating_dimensions=RATING_DIMENSIONS,
        date_started=date_started,
        date_finished=date_finished,
        readings=readings_data,
        current_reading_id=current_reading_id,
        current_reading_number=current_reading["reading_number"],
        reading_num_map=reading_num_map,
        has_multiple_readings=len(readings_data) > 1,
        book_gantt=book_gantt_data,
        series_list_book=series_list_book,
        editions=editions,
        work_total_readings=work_total_readings,
        all_linkable_books=all_linkable_books,
    )


@app.route("/cover/<book_id>")
def book_cover(book_id: str):
    db = get_db()

    # First try a lightweight hash-only check for conditional requests
    etag_from_client = request.headers.get("If-None-Match", "").strip(' "')
    if etag_from_client:
        hash_row = db.execute(
            "SELECT cover_hash FROM books WHERE id = ? AND has_cover = 1", (book_id,)
        ).fetchone()
        if hash_row and hash_row["cover_hash"] and hash_row["cover_hash"] == etag_from_client:
            resp = make_response("", 304)
            resp.headers["ETag"] = f'"{hash_row["cover_hash"]}"'
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp

    row = db.execute("SELECT cover, cover_hash FROM books WHERE id = ?", (book_id,)).fetchone()
    if not row or not row["cover"]:
        abort(404)

    cover_hash = row["cover_hash"] or hashlib.md5(row["cover"]).hexdigest()[:12]
    resp = make_response(row["cover"])
    resp.headers["Content-Type"] = "image/jpeg"
    resp.headers["ETag"] = f'"{cover_hash}"'
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


@app.route("/book/<book_id>/ratings", methods=["POST"])
def save_ratings(book_id: str):
    db = get_db()
    book = db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)
    ratings = {}
    for group in RATING_DIMENSIONS:
        for item in group["items"]:
            val = request.form.get(item["key"], "").strip()
            if val:
                try:
                    ratings[item["key"]] = int(val)
                except ValueError:
                    pass
    _save_ratings(book_id, ratings)
    flash("Ratings saved.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Metadata editing
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/edit", methods=["GET", "POST"])
def edit_metadata(book_id: str):
    db = get_db()
    lib_id = _get_current_library_id()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)
    info = dict(book)

    if request.method == "POST":
        text_fields = (
            "name", "subtitle", "author", "language", "original_title",
            "original_language", "original_publication_date",
            "publication_date", "isbn", "publisher", "genre",
            "summary", "translator", "illustrator",
            "editor", "prologue_author", "status",
            "format", "binding", "audio_format",
        )
        for field in text_fields:
            info[field] = request.form.get(field, "").strip()
        info["summary"] = sanitize_html(info["summary"])
        if info["format"] != "paper":
            info["binding"] = ""
        if info["format"] != "audiobook":
            info["audio_format"] = ""
        pages_str = request.form.get("pages", "0").strip()
        info["pages"] = int(pages_str) if pages_str.isdigit() else 0
        starting_page_str = request.form.get("starting_page", "0").strip()
        info["starting_page"] = int(starting_page_str) if starting_page_str.isdigit() else 0

        # Total time (audiobook)
        if info["format"] == "audiobook":
            tth = int(request.form.get("total_time_hours", "0").strip() or 0)
            ttm = int(request.form.get("total_time_minutes", "0").strip() or 0)
            tts = int(request.form.get("total_time_seconds", "0").strip() or 0)
            info["total_time_seconds"] = tth * 3600 + ttm * 60 + tts
            info["pages"] = 0
            info["starting_page"] = 0
        else:
            info["total_time_seconds"] = None

        source_type = request.form.get("source_type", "").strip()
        info["source_type"] = source_type
        is_gift = 1 if request.form.get("is_gift") else 0
        info["is_gift"] = is_gift if source_type == "owned" else 0
        if source_type == "owned":
            info["purchase_date"] = request.form.get("purchase_date", "").strip()
            info["source_id"] = request.form.get("source_id", "").strip()
            info["purchase_price"] = request.form.get("purchase_price", "").strip() if not is_gift else ""
            info["borrowed_start"] = ""
            info["borrowed_end"] = ""
        elif source_type == "borrowed":
            info["is_gift"] = 0
            info["source_id"] = request.form.get("source_id", "").strip()
            info["borrowed_start"] = request.form.get("borrowed_start", "").strip()
            info["borrowed_end"] = request.form.get("borrowed_end", "").strip()
            info["purchase_date"] = ""
            info["purchase_price"] = ""
        else:
            info["is_gift"] = 0
            info["source_id"] = ""
            info["purchase_date"] = ""
            info["purchase_price"] = ""
            info["borrowed_start"] = ""
            info["borrowed_end"] = ""

        # Handle series (many-to-many)
        series_names = request.form.getlist("series_name[]")
        series_indexes = request.form.getlist("series_index[]")
        # Clear old links for this book
        db.execute("DELETE FROM book_series WHERE book_id = ?", (book_id,))
        for s_name, s_idx in zip(series_names, series_indexes):
            s_name = s_name.strip()
            s_idx = s_idx.strip()
            if not s_name:
                continue
            existing = db.execute(
                "SELECT id FROM series WHERE name = ? AND library_id = ?",
                (s_name, lib_id)
            ).fetchone()
            if existing:
                sid = existing["id"]
            else:
                db.execute("INSERT INTO series (name, library_id) VALUES (?, ?)",
                           (s_name, lib_id))
                db.commit()
                sid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute(
                "INSERT OR IGNORE INTO book_series (book_id, series_id, series_index) VALUES (?, ?, ?)",
                (book_id, sid, s_idx)
            )

        db.execute("""
            UPDATE books SET
                name=?, subtitle=?, author=?, slug=?, language=?, original_title=?,
                original_language=?, original_publication_date=?,
                publication_date=?, isbn=?, pages=?, starting_page=?,
                publisher=?, genre=?, summary=?, translator=?, illustrator=?,
                editor=?, prologue_author=?, status=?,
                source_type=?, source_id=?, purchase_date=?, purchase_price=?,
                borrowed_start=?, borrowed_end=?, is_gift=?,
                format=?, binding=?, audio_format=?, total_time_seconds=?
            WHERE id=?
        """, (
            info["name"], info["subtitle"], info["author"], _slugify(info["name"]),
            info["language"], info["original_title"],
            info["original_language"], info["original_publication_date"],
            info["publication_date"], info["isbn"],
            info["pages"], info["starting_page"],
            info["publisher"], info["genre"], info["summary"],
            info["translator"], info["illustrator"],
            info["editor"], info["prologue_author"], info["status"],
            info["source_type"], info["source_id"],
            info["purchase_date"], info["purchase_price"],
            info["borrowed_start"], info["borrowed_end"],
            info["is_gift"],
            info["format"], info["binding"], info["audio_format"],
            info["total_time_seconds"],
            book_id,
        ))
        db.commit()

        # Sync reading status with book status
        new_status = info["status"]
        current_rid = _get_current_reading_id(db, book_id)
        db.execute("UPDATE readings SET status = ? WHERE id = ?", (new_status, current_rid))
        db.commit()

        # Handle cover upload
        cover_file = request.files.get("cover")
        if cover_file and cover_file.filename:
            cover_blob = cover_file.read()
            palette = _extract_cover_palette(cover_blob)
            cover_color = palette[0] if palette else "#888888"
            cover_hash = hashlib.md5(cover_blob).hexdigest()[:12]
            db.execute(
                "UPDATE books SET cover = ?, has_cover = 1, cover_color = ?, cover_palette = ?, cover_hash = ? WHERE id = ?",
                (cover_blob, cover_color, json.dumps(palette), cover_hash, book_id),
            )
            db.commit()
        else:
            # No new cover — check if user selected a different color
            selected_color = request.form.get("cover_color", "").strip()
            if selected_color:
                db.execute("UPDATE books SET cover_color = ? WHERE id = ?",
                           (selected_color, book_id))
                db.commit()

        flash("Book metadata updated.", "success")
        return redirect(url_for("book_detail", book_id=book_id))

    sources = db.execute("SELECT * FROM sources WHERE library_id = ? ORDER BY name", (lib_id,)).fetchall()
    sources = [dict(s) for s in sources]
    purchase_sources = [s for s in sources if s["type"] in PURCHASE_SOURCE_TYPES]
    borrow_sources = [s for s in sources if s["type"] in BORROW_SOURCE_TYPES]
    gift_sources = [s for s in sources if s["type"] in GIFT_SOURCE_TYPES]
    languages = _collect_languages()
    suggestions = _collect_field_values(
        "author", "genre", "publisher",
        "translator", "illustrator", "editor", "prologue_author",
    )
    # Parse cover palette for the color picker
    cover_palette = []
    try:
        cover_palette = json.loads(info.get("cover_palette") or "[]")
    except (json.JSONDecodeError, TypeError):
        pass

    # Fetch all series for autocomplete and current book's series
    all_series = [dict(r) for r in db.execute(
        "SELECT id, name FROM series WHERE library_id = ? ORDER BY name COLLATE NOCASE", (lib_id,)
    ).fetchall()]
    book_series_entries = [dict(r) for r in db.execute("""
        SELECT s.name, bs.series_index
        FROM book_series bs
        JOIN series s ON s.id = bs.series_id
        WHERE bs.book_id = ?
        ORDER BY s.name COLLATE NOCASE
    """, (book_id,)).fetchall()]

    return render_template("edit_metadata.html", book_id=book_id, info=info,
                           purchase_sources=purchase_sources, borrow_sources=borrow_sources,
                           gift_sources=gift_sources,
                           languages=languages, suggestions=suggestions,
                           cover_palette=cover_palette,
                           all_series=all_series, book_series_entries=book_series_entries,
                           is_secondary_edition=bool(info.get("work_id") and not info.get("is_primary_edition")))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Session CRUD
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/sessions/add", methods=["POST"])
def add_session(book_id: str):
    db = get_db()
    book = db.execute("SELECT id, format FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    book_fmt = book["format"] or "paper"
    date = _normalize_input_date(request.form.get("date", ""))
    try:
        hours_val = int(request.form.get("hours", "0").strip() or 0)
        minutes_val = int(request.form.get("minutes", "0").strip() or 0)
        seconds_val = int(request.form.get("seconds", "0").strip() or 0)
    except ValueError:
        flash("Invalid numeric input.", "error")
        return redirect(url_for("book_detail", book_id=book_id, _anchor="add-session"))

    dur_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val
    reading_id = _get_current_reading_id(db, book_id)

    if book_fmt in ("audiobook", "ebook"):
        try:
            pct_val = float(request.form.get("progress_pct", "0").strip() or 0)
        except ValueError:
            pct_val = 0.0
        pct_val = max(0.0, min(pct_val, 100.0))
        db.execute(
            "INSERT INTO sessions (book_id, date, pages, duration_seconds, reading_id, progress_pct) VALUES (?,?,0,?,?,?)",
            (book_id, date, dur_seconds, reading_id, pct_val),
        )
    else:
        try:
            pages_val = int(request.form.get("pages", "0").strip() or 0)
        except ValueError:
            pages_val = 0
        db.execute(
            "INSERT INTO sessions (book_id, date, pages, duration_seconds, reading_id) VALUES (?,?,?,?,?)",
            (book_id, date, pages_val, dur_seconds, reading_id),
        )
    db.commit()
    flash("Reading session added.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-session"))


@app.route("/book/<book_id>/sessions/<int:idx>/edit", methods=["POST"])
def edit_session(book_id: str, idx: int):
    db = get_db()
    row = db.execute("SELECT id FROM sessions WHERE id = ? AND book_id = ?", (idx, book_id)).fetchone()
    if not row:
        abort(404)

    book_row = db.execute("SELECT format FROM books WHERE id = ?", (book_id,)).fetchone()
    book_fmt = (book_row["format"] if book_row else "paper") or "paper"
    date = _normalize_input_date(request.form.get("date", ""))
    try:
        hours_val = int(request.form.get("hours", "0").strip() or 0)
        minutes_val = int(request.form.get("minutes", "0").strip() or 0)
        seconds_val = int(request.form.get("seconds", "0").strip() or 0)
    except ValueError:
        flash("Invalid numeric input.", "error")
        return redirect(url_for("book_detail", book_id=book_id, _anchor="add-session"))

    dur_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val

    if book_fmt in ("audiobook", "ebook"):
        try:
            pct_val = float(request.form.get("progress_pct", "0").strip() or 0)
        except ValueError:
            pct_val = 0.0
        pct_val = max(0.0, min(pct_val, 100.0))
        db.execute(
            "UPDATE sessions SET date=?, pages=0, duration_seconds=?, progress_pct=? WHERE id=?",
            (date, dur_seconds, pct_val, idx),
        )
    else:
        try:
            pages_val = int(request.form.get("pages", "0").strip() or 0)
        except ValueError:
            pages_val = 0
        db.execute(
            "UPDATE sessions SET date=?, pages=?, duration_seconds=? WHERE id=?",
            (date, pages_val, dur_seconds, idx),
        )
    db.commit()
    flash("Reading session updated.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-session"))


@app.route("/book/<book_id>/sessions/<int:idx>/delete", methods=["POST"])
def delete_session(book_id: str, idx: int):
    db = get_db()
    row = db.execute("SELECT id FROM sessions WHERE id = ? AND book_id = ?", (idx, book_id)).fetchone()
    if not row:
        abort(404)
    db.execute("DELETE FROM sessions WHERE id = ?", (idx,))
    db.commit()
    flash("Reading session deleted.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-session"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Period CRUD
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/periods/add", methods=["POST"])
def add_reading_period(book_id: str):
    db = get_db()
    book = db.execute("SELECT id, format FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    book_fmt = book["format"] or "paper"
    start_date = _normalize_input_date(request.form.get("start_date", ""))
    end_date = _normalize_input_date(request.form.get("end_date", ""))
    note = request.form.get("note", "").strip()

    reading_id = _get_current_reading_id(db, book_id)

    if book_fmt in ("audiobook", "ebook"):
        try:
            pct_val = float(request.form.get("progress_pct", "0").strip() or 0)
        except ValueError:
            pct_val = 0.0
        pct_val = max(0.0, min(pct_val, 100.0))
        try:
            hours_val = int(request.form.get("hours", "0").strip() or 0)
            minutes_val = int(request.form.get("minutes", "0").strip() or 0)
            seconds_val = int(request.form.get("seconds", "0").strip() or 0)
        except ValueError:
            hours_val = minutes_val = seconds_val = 0
        dur_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val
        db.execute(
            "INSERT INTO periods (book_id, start_date, end_date, pages, note, reading_id, progress_pct, duration_seconds) VALUES (?,?,?,0,?,?,?,?)",
            (book_id, start_date, end_date, note, reading_id, pct_val, dur_seconds or None),
        )
    else:
        pages = request.form.get("pages", "0").strip()
        try:
            pages = int(pages)
            if pages < 1:
                pages = 1
        except ValueError:
            pages = 1
        db.execute(
            "INSERT INTO periods (book_id, start_date, end_date, pages, note, reading_id) VALUES (?,?,?,?,?,?)",
            (book_id, start_date, end_date, pages, note, reading_id),
        )
    db.commit()
    flash("Reading period added.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-period"))


@app.route("/book/<book_id>/periods/<int:idx>/edit", methods=["POST"])
def edit_reading_period(book_id: str, idx: int):
    db = get_db()
    row = db.execute("SELECT id FROM periods WHERE id = ? AND book_id = ?", (idx, book_id)).fetchone()
    if not row:
        abort(404)

    book_row = db.execute("SELECT format FROM books WHERE id = ?", (book_id,)).fetchone()
    book_fmt = (book_row["format"] if book_row else "paper") or "paper"
    start_date = _normalize_input_date(request.form.get("start_date", ""))
    end_date = _normalize_input_date(request.form.get("end_date", ""))
    note = request.form.get("note", "").strip()

    if book_fmt in ("audiobook", "ebook"):
        try:
            pct_val = float(request.form.get("progress_pct", "0").strip() or 0)
        except ValueError:
            pct_val = 0.0
        pct_val = max(0.0, min(pct_val, 100.0))
        try:
            hours_val = int(request.form.get("hours", "0").strip() or 0)
            minutes_val = int(request.form.get("minutes", "0").strip() or 0)
            seconds_val = int(request.form.get("seconds", "0").strip() or 0)
        except ValueError:
            hours_val = minutes_val = seconds_val = 0
        dur_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val
        db.execute(
            "UPDATE periods SET start_date=?, end_date=?, pages=0, note=?, progress_pct=?, duration_seconds=? WHERE id=?",
            (start_date, end_date, note, pct_val, dur_seconds or None, idx),
        )
    else:
        pages = request.form.get("pages", "0").strip()
        try:
            pages = int(pages)
            if pages < 1:
                pages = 1
        except ValueError:
            pages = 1
        db.execute(
            "UPDATE periods SET start_date=?, end_date=?, pages=?, note=? WHERE id=?",
            (start_date, end_date, pages, note, idx),
        )
    db.commit()
    flash("Reading period updated.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-period"))


@app.route("/book/<book_id>/periods/<int:idx>/delete", methods=["POST"])
def delete_reading_period(book_id: str, idx: int):
    db = get_db()
    row = db.execute("SELECT id FROM periods WHERE id = ? AND book_id = ?", (idx, book_id)).fetchone()
    if not row:
        abort(404)
    db.execute("DELETE FROM periods WHERE id = ?", (idx,))
    db.commit()
    flash("Reading period deleted.", "success")
    return redirect(url_for("book_detail", book_id=book_id, _anchor="add-period"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Add new book
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/new", methods=["GET", "POST"])
def new_book():
    db = get_db()
    lib_id = _get_current_library_id()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        author = request.form.get("author", "").strip()
        if not name:
            flash("Book name is required.", "error")
            return redirect(url_for("new_book"))

        book_id = str(uuid_module.uuid4())

        info: dict = {}
        for field in (
            "name", "subtitle", "author", "language", "original_title",
            "original_language", "original_publication_date",
            "publication_date", "isbn", "publisher", "genre",
            "summary", "translator", "illustrator",
            "editor", "prologue_author", "status",
            "format", "binding", "audio_format",
        ):
            info[field] = request.form.get(field, "").strip()
        info["summary"] = sanitize_html(info["summary"])
        if info["format"] != "paper":
            info["binding"] = ""
        if info["format"] != "audiobook":
            info["audio_format"] = ""
        pages_str = request.form.get("pages", "0").strip()
        info["pages"] = int(pages_str) if pages_str.isdigit() else 0
        starting_page_str = request.form.get("starting_page", "0").strip()
        info["starting_page"] = int(starting_page_str) if starting_page_str.isdigit() else 0

        # Total time (audiobook)
        if info["format"] == "audiobook":
            tth = int(request.form.get("total_time_hours", "0").strip() or 0)
            ttm = int(request.form.get("total_time_minutes", "0").strip() or 0)
            tts = int(request.form.get("total_time_seconds", "0").strip() or 0)
            info["total_time_seconds"] = tth * 3600 + ttm * 60 + tts
            info["pages"] = 0
            info["starting_page"] = 0
        else:
            info["total_time_seconds"] = None

        source_type = request.form.get("source_type", "").strip()
        info["source_type"] = source_type
        info["source_id"] = ""
        info["purchase_date"] = ""
        info["purchase_price"] = ""
        info["borrowed_start"] = ""
        info["borrowed_end"] = ""
        is_gift = 1 if request.form.get("is_gift") else 0
        info["is_gift"] = is_gift if source_type == "owned" else 0
        if source_type == "owned":
            info["purchase_date"] = request.form.get("purchase_date", "").strip()
            info["source_id"] = request.form.get("source_id", "").strip()
            info["purchase_price"] = request.form.get("purchase_price", "").strip() if not is_gift else ""
        elif source_type == "borrowed":
            info["is_gift"] = 0
            info["source_id"] = request.form.get("source_id", "").strip()
            info["borrowed_start"] = request.form.get("borrowed_start", "").strip()
            info["borrowed_end"] = request.form.get("borrowed_end", "").strip()

        if not info["status"]:
            info["status"] = "reading"

        # Handle cover
        has_cover = 0
        cover_blob = None
        cover_color = ""
        cover_palette_json = "[]"
        cover_hash = ""
        cover_file = request.files.get("cover")
        if cover_file and cover_file.filename:
            cover_blob = cover_file.read()
            has_cover = 1
            palette = _extract_cover_palette(cover_blob)
            cover_color = palette[0] if palette else "#888888"
            cover_palette_json = json.dumps(palette)
            cover_hash = hashlib.md5(cover_blob).hexdigest()[:12]

        # Handle series (many-to-many)
        series_names = request.form.getlist("series_name[]")
        series_indexes = request.form.getlist("series_index[]")

        # Handle edition linking
        link_work_id = request.form.get("work_id", "").strip()
        is_primary = 1
        if link_work_id:
            is_primary = 0  # new edition is secondary
            # Ensure the parent book has a work_id; if not, assign one (use parent's own id)
            parent = db.execute("SELECT id, work_id FROM books WHERE id = ?", (link_work_id,)).fetchone()
            if parent and not parent["work_id"]:
                db.execute("UPDATE books SET work_id = ?, is_primary_edition = 1 WHERE id = ?",
                           (link_work_id, link_work_id))
            elif parent and parent["work_id"]:
                # Parent already has a work_id; use that instead
                link_work_id = parent["work_id"]

        db.execute("""
            INSERT INTO books
            (id, name, subtitle, author, slug, language, original_title, original_language,
             original_publication_date, publication_date, isbn, pages, starting_page,
             publisher, genre, summary, translator, illustrator, editor, prologue_author,
             status, source_type, source_id, purchase_date, purchase_price,
             borrowed_start, borrowed_end, is_gift, has_cover, cover, cover_color, cover_palette, cover_hash,
             library_id, work_id, is_primary_edition,
             format, binding, audio_format, total_time_seconds)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            book_id, info["name"], info["subtitle"], info["author"], _slugify(info["name"]),
            info["language"], info["original_title"],
            info["original_language"], info["original_publication_date"],
            info["publication_date"], info["isbn"],
            info["pages"], info["starting_page"],
            info["publisher"], info["genre"], info["summary"],
            info["translator"], info["illustrator"],
            info["editor"], info["prologue_author"], info["status"],
            info["source_type"], info["source_id"],
            info["purchase_date"], info["purchase_price"],
            info["borrowed_start"], info["borrowed_end"],
            info["is_gift"],
            has_cover, cover_blob, cover_color, cover_palette_json, cover_hash,
            lib_id, link_work_id or None, is_primary,
            info["format"], info["binding"], info["audio_format"],
            info["total_time_seconds"],
        ))

        # Insert book_series entries
        for s_name, s_idx in zip(series_names, series_indexes):
            s_name = s_name.strip()
            s_idx = s_idx.strip()
            if not s_name:
                continue
            existing = db.execute(
                "SELECT id FROM series WHERE name = ? AND library_id = ?",
                (s_name, lib_id)
            ).fetchone()
            if existing:
                sid = existing["id"]
            else:
                db.execute("INSERT INTO series (name, library_id) VALUES (?, ?)",
                           (s_name, lib_id))
                db.commit()
                sid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute(
                "INSERT OR IGNORE INTO book_series (book_id, series_id, series_index) VALUES (?, ?, ?)",
                (book_id, sid, s_idx)
            )
        db.commit()

        # Create initial reading for the new book
        db.execute(
            "INSERT INTO readings (book_id, reading_number, status) VALUES (?, 1, ?)",
            (book_id, info["status"]),
        )
        db.commit()

        flash(f"Book '{name}' added.", "success")
        return redirect(url_for("book_detail", book_id=book_id))

    sources = db.execute("SELECT * FROM sources WHERE library_id = ? ORDER BY name", (lib_id,)).fetchall()
    sources = [dict(s) for s in sources]
    purchase_sources = [s for s in sources if s["type"] in PURCHASE_SOURCE_TYPES]
    borrow_sources = [s for s in sources if s["type"] in BORROW_SOURCE_TYPES]
    gift_sources = [s for s in sources if s["type"] in GIFT_SOURCE_TYPES]
    languages = _collect_languages()
    suggestions = _collect_field_values(
        "author", "genre", "publisher",
        "translator", "illustrator", "editor", "prologue_author",
    )
    all_series = [dict(r) for r in db.execute(
        "SELECT id, name FROM series WHERE library_id = ? ORDER BY name COLLATE NOCASE", (lib_id,)
    ).fetchall()]

    # Pre-fill for "new edition" flow
    prefill = {}
    parent_work_id = request.args.get("work_id", "").strip()
    parent_book_name = ""
    if parent_work_id:
        primary = _get_primary_edition(db, parent_work_id)
        if not primary:
            # The parent book may not have a work_id yet; look up by book id
            primary = db.execute("SELECT * FROM books WHERE id = ?", (parent_work_id,)).fetchone()
            if primary:
                primary = dict(primary)
        if primary:
            parent_book_name = primary.get("name", "")
            for f in ("author", "original_title", "original_language",
                      "original_publication_date", "genre", "summary",
                      "illustrator", "editor", "prologue_author"):
                prefill[f] = primary.get(f, "")

    return render_template("new_book.html",
                           purchase_sources=purchase_sources, borrow_sources=borrow_sources,
                           gift_sources=gift_sources,
                           languages=languages, suggestions=suggestions,
                           all_series=all_series,
                           prefill=prefill,
                           parent_work_id=parent_work_id,
                           parent_book_name=parent_book_name)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Sources
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/sources")
def sources_list():
    """Sources management page."""
    db = get_db()
    lib_id = _get_current_library_id()
    sources = [dict(r) for r in db.execute("SELECT * FROM sources WHERE library_id = ? ORDER BY name", (lib_id,)).fetchall()]
    return render_template("sources.html", sources=sources, source_types=SOURCE_TYPES)


@app.route("/sources/add", methods=["POST"])
def add_source():
    db = get_db()
    lib_id = _get_current_library_id()
    name = request.form.get("name", "").strip()
    short_name = request.form.get("short_name", "").strip()
    if not name:
        flash("Source name is required.", "error")
        return redirect(url_for("sources_list"))

    db.execute(
        "INSERT INTO sources (id, type, name, short_name, location, url, notes, library_id) VALUES (?,?,?,?,?,?,?,?)",
        (
            str(uuid_module.uuid4()),
            request.form.get("source_type", "").strip(),
            name,
            short_name or name,
            request.form.get("location", "").strip(),
            request.form.get("url", "").strip(),
            request.form.get("notes", "").strip(),
            lib_id,
        ),
    )
    db.commit()
    flash(f"Source '{name}' added.", "success")
    return redirect(url_for("sources_list"))


@app.route("/sources/<source_id>/edit", methods=["POST"])
def edit_source(source_id: str):
    db = get_db()
    row = db.execute("SELECT id FROM sources WHERE id = ?", (source_id,)).fetchone()
    if not row:
        abort(404)

    name = request.form.get("name", "").strip()
    short_name = request.form.get("short_name", "").strip() or name
    db.execute("""
        UPDATE sources SET type=?, name=?, short_name=?, location=?, url=?, notes=?
        WHERE id=?
    """, (
        request.form.get("source_type", "").strip(),
        name, short_name,
        request.form.get("location", "").strip(),
        request.form.get("url", "").strip(),
        request.form.get("notes", "").strip(),
        source_id,
    ))
    db.commit()
    flash("Source updated.", "success")
    return redirect(url_for("sources_list"))


@app.route("/sources/<source_id>/delete", methods=["POST"])
def delete_source(source_id: str):
    db = get_db()
    db.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    db.commit()
    flash("Source deleted.", "success")
    return redirect(url_for("sources_list"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Library management
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/library/switch", methods=["POST"])
def switch_library():
    """Switch the active library (stores choice in a cookie)."""
    lib_id = request.form.get("library_id", "")
    db = get_db()
    row = db.execute("SELECT id FROM libraries WHERE id = ?", (lib_id,)).fetchone()
    if not row:
        abort(400)
    resp = make_response(redirect(request.referrer or url_for("index")))
    resp.set_cookie("librarium_library", str(lib_id), max_age=60 * 60 * 24 * 365 * 5,
                     samesite="Lax", httponly=True)
    return resp


# ── Manual backup ────────────────────────────────────────────────────────

@app.route("/backup/create", methods=["POST"])
def create_backup():
    """Manually create a database backup."""
    name = backup_database(skip_if_recent=False)
    if name:
        flash(f"Backup created: {name}", "success")
    else:
        flash("Backup failed — database not found.", "error")
    return redirect(request.referrer or url_for("index"))


@app.route("/library/create", methods=["POST"])
def create_library():
    """Create a new library."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Library name is required.", "error")
        return redirect(request.referrer or url_for("index"))
    slug = _slugify(name)
    db = get_db()
    existing = db.execute("SELECT id FROM libraries WHERE slug = ?", (slug,)).fetchone()
    if existing:
        flash("A library with that name already exists.", "error")
        return redirect(request.referrer or url_for("index"))
    db.execute("INSERT INTO libraries (name, slug) VALUES (?, ?)", (name, slug))
    db.commit()
    new_lib = db.execute("SELECT id FROM libraries WHERE slug = ?", (slug,)).fetchone()
    resp = make_response(redirect(request.referrer or url_for("index")))
    resp.set_cookie("librarium_library", str(new_lib["id"]), max_age=60 * 60 * 24 * 365 * 5,
                     samesite="Lax", httponly=True)
    flash(f"Library '{name}' created.", "success")
    return resp


@app.route("/library/<int:lib_id>/rename", methods=["POST"])
def rename_library(lib_id: int):
    """Rename a library."""
    db = get_db()
    row = db.execute("SELECT id FROM libraries WHERE id = ?", (lib_id,)).fetchone()
    if not row:
        abort(404)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Library name is required.", "error")
        return redirect(request.referrer or url_for("index"))
    slug = _slugify(name)
    conflict = db.execute("SELECT id FROM libraries WHERE slug = ? AND id != ?", (slug, lib_id)).fetchone()
    if conflict:
        flash("A library with that name already exists.", "error")
        return redirect(request.referrer or url_for("index"))
    db.execute("UPDATE libraries SET name = ?, slug = ? WHERE id = ?", (name, slug, lib_id))
    db.commit()
    flash(f"Library renamed to '{name}'.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/library/<int:lib_id>/delete", methods=["POST"])
def delete_library(lib_id: int):
    """Delete a library and all its data."""
    db = get_db()
    row = db.execute("SELECT id, name FROM libraries WHERE id = ?", (lib_id,)).fetchone()
    if not row:
        abort(404)
    # Prevent deleting the last library
    count = db.execute("SELECT COUNT(*) AS c FROM libraries").fetchone()["c"]
    if count <= 1:
        flash("Cannot delete the only library.", "error")
        return redirect(request.referrer or url_for("index"))
    lib_name = row["name"]
    # Delete all data belonging to this library
    book_ids = [r["id"] for r in db.execute("SELECT id FROM books WHERE library_id = ?", (lib_id,)).fetchall()]
    for bid in book_ids:
        db.execute("DELETE FROM sessions WHERE book_id = ?", (bid,))
        db.execute("DELETE FROM periods WHERE book_id = ?", (bid,))
        db.execute("DELETE FROM ratings WHERE book_id = ?", (bid,))
        db.execute("DELETE FROM readings WHERE book_id = ?", (bid,))
    db.execute("DELETE FROM books WHERE library_id = ?", (lib_id,))
    db.execute("DELETE FROM sources WHERE library_id = ?", (lib_id,))
    db.execute("DELETE FROM authors WHERE library_id = ?", (lib_id,))
    db.execute("DELETE FROM libraries WHERE id = ?", (lib_id,))
    db.commit()
    # If the deleted library was the active one, reset cookie
    current = request.cookies.get("librarium_library", "")
    if current == str(lib_id):
        first = db.execute("SELECT id FROM libraries ORDER BY id LIMIT 1").fetchone()
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("librarium_library", str(first["id"]), max_age=60 * 60 * 24 * 365 * 5,
                         samesite="Lax", httponly=True)
        flash(f"Library '{lib_name}' deleted.", "success")
        return resp
    flash(f"Library '{lib_name}' deleted.", "success")
    return redirect(request.referrer or url_for("index"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Re-read
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/reread", methods=["POST"])
def start_reread(book_id: str):
    """Start a new reading of a book."""
    db = get_db()
    book = db.execute("SELECT id, status FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    # Get the highest reading_number for this book
    row = db.execute(
        "SELECT MAX(reading_number) AS n FROM readings WHERE book_id = ?", (book_id,)
    ).fetchone()
    next_number = (row["n"] or 0) + 1

    # Mark any current 'reading' readings as 'abandoned' (safety)
    db.execute(
        "UPDATE readings SET status = 'finished' "
        "WHERE book_id = ? AND status = 'reading'",
        (book_id,),
    )

    # Create the new reading
    db.execute(
        "INSERT INTO readings (book_id, reading_number, status) VALUES (?, ?, 'reading')",
        (book_id, next_number),
    )

    # Update book status to 'reading'
    db.execute("UPDATE books SET status = 'reading' WHERE id = ?", (book_id,))
    db.commit()

    flash(f"Re-read #{next_number} started!", "success")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/book/<book_id>/reading/<int:reading_id>/delete", methods=["POST"])
def delete_reading(book_id: str, reading_id: int):
    """Delete a single reading and its sessions/periods, then renumber."""
    db = get_db()
    book = db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    reading = db.execute(
        "SELECT id, reading_number FROM readings WHERE id = ? AND book_id = ?",
        (reading_id, book_id),
    ).fetchone()
    if not reading:
        abort(404)

    # Prevent deleting the only reading
    count = db.execute(
        "SELECT COUNT(*) AS c FROM readings WHERE book_id = ?", (book_id,)
    ).fetchone()["c"]
    if count <= 1:
        flash("Cannot delete the only reading of a book.", "error")
        return redirect(url_for("book_detail", book_id=book_id))

    # Delete sessions and periods linked to this reading
    db.execute("DELETE FROM sessions WHERE reading_id = ?", (reading_id,))
    db.execute("DELETE FROM periods WHERE reading_id = ?", (reading_id,))
    db.execute("DELETE FROM readings WHERE id = ?", (reading_id,))

    # Renumber the remaining readings sequentially
    remaining = db.execute(
        "SELECT id FROM readings WHERE book_id = ? ORDER BY reading_number",
        (book_id,),
    ).fetchall()
    for idx, row in enumerate(remaining, start=1):
        db.execute(
            "UPDATE readings SET reading_number = ? WHERE id = ?",
            (idx, row["id"]),
        )

    # Update book status to match the latest remaining reading
    latest = db.execute(
        "SELECT status FROM readings WHERE book_id = ? ORDER BY reading_number DESC LIMIT 1",
        (book_id,),
    ).fetchone()
    if latest:
        db.execute(
            "UPDATE books SET status = ? WHERE id = ?",
            (latest["status"], book_id),
        )

    db.commit()
    flash(f"Reading #{reading['reading_number']} deleted.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Delete book
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/delete", methods=["POST"])
def delete_book(book_id: str):
    db = get_db()
    # Fetch complete book data before deletion
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)
    
    book_dict = dict(book)
    # Fetch all related data
    readings = db.execute("SELECT * FROM readings WHERE book_id = ?", (book_id,)).fetchall()
    readings_data = [dict(r) for r in readings]
    sessions = db.execute("SELECT * FROM sessions WHERE book_id = ?", (book_id,)).fetchall()
    sessions_data = [dict(s) for s in sessions]
    periods = db.execute("SELECT * FROM periods WHERE book_id = ?", (book_id,)).fetchall()
    periods_data = [dict(p) for p in periods]
    ratings = db.execute("SELECT * FROM ratings WHERE book_id = ?", (book_id,)).fetchall()
    ratings_data = [dict(r) for r in ratings]
    
    # Store backup in session (BLOB fields need special handling)
    backup = {
        "book": book_dict,
        "readings": readings_data,
        "sessions": sessions_data,
        "periods": periods_data,
        "ratings": ratings_data,
    }
    session["deleted_book_backup"] = backup
    session.modified = True

    # Edition handling: if deleting a primary edition, promote another
    wid = book_dict.get("work_id")
    if wid and book_dict.get("is_primary_edition"):
        other = db.execute(
            "SELECT id FROM books WHERE work_id = ? AND id != ? LIMIT 1",
            (wid, book_id),
        ).fetchone()
        if other:
            db.execute("UPDATE books SET is_primary_edition = 1 WHERE id = ?", (other["id"],))
            # If only one edition remains after deletion, dissolve the group
            remaining = db.execute(
                "SELECT COUNT(*) AS c FROM books WHERE work_id = ? AND id != ?",
                (wid, book_id),
            ).fetchone()["c"]
            if remaining == 1:
                db.execute("UPDATE books SET work_id = NULL WHERE work_id = ? AND id != ?", (wid, book_id))
    
    # Delete from DB
    db.execute("DELETE FROM readings WHERE book_id = ?", (book_id,))
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    
    book_name = book_dict.get("name", "Book")
    flash(f"Book '{book_name}' deleted. <a href='#' onclick='undoDelete(event)' class='undo-link'>Undo</a>", "success")
    return redirect(url_for("index"))


@app.route("/book/undo-delete", methods=["POST"])
def undo_delete_book():
    """Restore the most recently deleted book from session backup."""
    if "deleted_book_backup" not in session:
        flash("Nothing to undo.", "warning")
        return redirect(url_for("index"))
    
    backup = session.pop("deleted_book_backup")
    session.modified = True
    db = get_db()
    
    try:
        # Re-insert book
        book = backup["book"]
        db.execute(
            """INSERT INTO books 
               (id, name, subtitle, slug, author, language, original_title, original_language,
                original_publication_date, publication_date, isbn, pages, starting_page,
                publisher, genre, summary, translator, illustrator, editor, prologue_author,
                status, source_type, source_id, purchase_date, purchase_price, borrowed_start,
                borrowed_end, is_gift, has_cover, cover, cover_color, cover_palette, cover_hash,
                library_id, work_id, is_primary_edition)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (book.get("id"), book.get("name"), book.get("subtitle", ""), book.get("slug"), book.get("author"),
             book.get("language"), book.get("original_title"), book.get("original_language"),
             book.get("original_publication_date"), book.get("publication_date"),
             book.get("isbn"), book.get("pages"), book.get("starting_page"),
             book.get("publisher"), book.get("genre"), book.get("summary"),
             book.get("translator"), book.get("illustrator"), book.get("editor"),
             book.get("prologue_author"), book.get("status"), book.get("source_type"),
             book.get("source_id"), book.get("purchase_date"), book.get("purchase_price"),
             book.get("borrowed_start"), book.get("borrowed_end"), book.get("is_gift"),
             book.get("has_cover"), book.get("cover"), book.get("cover_color"),
             book.get("cover_palette"), book.get("cover_hash"),
             book.get("library_id"), book.get("work_id"), book.get("is_primary_edition", 1))
        )
        
        # Re-insert readings
        for reading in backup["readings"]:
            db.execute(
                "INSERT INTO readings (id, book_id, reading_number, status, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (reading.get("id"), reading.get("book_id"), reading.get("reading_number"),
                 reading.get("status"), reading.get("notes"))
            )
        
        # Re-insert sessions
        for sess in backup["sessions"]:
            db.execute(
                "INSERT INTO sessions (id, date, book_id, pages_read, reading_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (sess.get("id"), sess.get("date"), sess.get("book_id"),
                 sess.get("pages_read"), sess.get("reading_id"))
            )
        
        # Re-insert periods
        for period in backup["periods"]:
            db.execute(
                "INSERT INTO periods (id, start_date, end_date, book_id, reading_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (period.get("id"), period.get("start_date"), period.get("end_date"),
                 period.get("book_id"), period.get("reading_id"))
            )
        
        # Re-insert ratings
        for rating in backup["ratings"]:
            db.execute(
                "INSERT INTO ratings (book_id, category, score_raw, notes) "
                "VALUES (?, ?, ?, ?)",
                (rating.get("book_id"), rating.get("category"), rating.get("score_raw"),
                 rating.get("notes"))
            )
        
        db.commit()
        book_name = backup["book"].get("name", "Book")
        flash(f"Book '{book_name}' restored.", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error restoring book: {str(e)}", "error")
    
    book_id = backup["book"].get("id")
    return redirect(url_for("book_detail", book_id=book_id) if book_id else url_for("index"))


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    validate_and_restore_db()  # Check & recover if corrupted
    backup_database()           # Create a backup (only if healthy)
    migrate_add_readings()      # Add readings table if needed
    migrate_add_authors()       # Add authors table if needed
    migrate_add_cover_color()   # Add cover_color column if needed
    migrate_add_cover_palette() # Add cover_palette column if needed
    migrate_add_cover_hash()    # Add cover_hash column if needed
    migrate_add_photo_hash()    # Add photo_hash column to authors if needed
    migrate_add_subtitle()      # Add subtitle column to books if needed
    migrate_add_libraries()     # Add libraries table and library_id columns
    migrate_add_series()        # Add series table and series columns
    migrate_book_series_m2m()   # Add book_series junction table (many-to-many)
    migrate_add_editions()      # Add work_id / is_primary_edition columns
    migrate_add_format()        # Add format / binding / audio_format columns
    migrate_add_total_time()    # Add total_time_seconds / progress_pct columns
    migrate_add_period_duration()  # Add duration_seconds to periods
    port = int(os.environ.get("LIBRARIUM_PORT", 5000))
    is_electron = os.environ.get("LIBRARIUM_ELECTRON") == "1"

    app.run(
        debug=not is_electron,
        port=port,
        extra_files=None,
        exclude_patterns=["*/site-packages/*"],
    )

"""Librarium – a local Flask app for tracking reading statistics.

All data (including cover images) is stored in per-user SQLite databases
inside the platform's application data directory (e.g. %APPDATA%/Librarium
on Windows).
"""

import hashlib
import io
import json
import math
import os
import re
import secrets
import sys
import shutil
import sqlite3
import threading
import urllib.error
import urllib.request
import uuid as uuid_module
from collections import Counter
from datetime import datetime, date
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()          # adds AVIF / HEIF support to Pillow

import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

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


def _get_data_dir() -> Path:
    """Return the platform-appropriate application data directory.

    Windows:  %APPDATA%/Librarium
    macOS:    ~/Library/Application Support/Librarium
    Linux:    ~/.local/share/Librarium  (XDG_DATA_HOME fallback)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "Librarium"


DATA_DIR = _get_data_dir()
BACKUP_DIR = DATA_DIR / "backups"
USERS_FILE = DATA_DIR / "users.json"
MAX_BACKUPS = 5

# DB_PATH is set dynamically per-user; default used for migrations at startup
DB_PATH = DATA_DIR / "librarium.db"

APP_VERSION = "1.2.0"

app = Flask(__name__)
app.secret_key = "librarium-local-dev-key"

# ── Dropbox integration ──────────────────────────────────────────────────
DROPBOX_APP_KEY = "tlt9ax4wz2mw2i0"
DROPBOX_REDIRECT_URI = "http://127.0.0.1:48721/auth/callback"
DROPBOX_SCOPES = [
    "account_info.read",
    "files.metadata.read",
    "files.metadata.write",
    "files.content.read",
    "files.content.write",
]
AUTH_FILE = DATA_DIR / "auth.json"
CACHE_DIR = DATA_DIR / "cache"
_dbx_client: dropbox.Dropbox | None = None
_dbx_lock = threading.Lock()
_sync_thread: threading.Thread | None = None
_last_download_hash: dict[str, str] = {}   # remote path → content_hash at download time


def _load_auth() -> dict | None:
    """Load Dropbox auth data from auth.json, or None if missing / invalid."""
    if not AUTH_FILE.exists():
        return None
    try:
        data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("refresh_token"):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _save_auth(data: dict) -> None:
    """Persist Dropbox auth data to auth.json."""
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _clear_auth() -> None:
    """Remove auth.json (logout)."""
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()


def _is_authenticated() -> bool:
    """Return True if a valid Dropbox refresh token exists."""
    return _load_auth() is not None


def get_dropbox_client() -> dropbox.Dropbox:
    """Return a Dropbox client that auto-refreshes its access token.

    Caches the client in a module-level variable.  Thread-safe.
    """
    global _dbx_client
    with _dbx_lock:
        if _dbx_client is not None:
            return _dbx_client
        auth = _load_auth()
        if not auth:
            raise RuntimeError("Not authenticated with Dropbox")
        _dbx_client = dropbox.Dropbox(
            oauth2_refresh_token=auth["refresh_token"],
            app_key=DROPBOX_APP_KEY,
        )
        return _dbx_client


def _reset_dropbox_client() -> None:
    """Discard the cached Dropbox client (e.g. after logout)."""
    global _dbx_client
    with _dbx_lock:
        _dbx_client = None


# ── Dropbox file operations ─────────────────────────────────────────────
_UPLOAD_CHUNK = 140 * 1024 * 1024  # 140 MB — use chunked upload above this


def _dbx_download(remote_path: str, local_path: Path) -> str | None:
    """Download a file from Dropbox app folder to a local path.

    Returns the content_hash on success, or None if the file does not
    exist on Dropbox.
    """
    dbx = get_dropbox_client()
    try:
        meta, resp = dbx.files_download(remote_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(resp.content)
        content_hash = meta.content_hash
        _last_download_hash[remote_path] = content_hash
        return content_hash
    except ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            return None
        raise


def _dbx_upload(local_path: Path, remote_path: str) -> str:
    """Upload a local file to Dropbox app folder (overwrite mode).

    Uses chunked upload for files > 140 MB.  Returns the content_hash.
    """
    dbx = get_dropbox_client()
    size = local_path.stat().st_size

    if size <= _UPLOAD_CHUNK:
        with open(local_path, "rb") as f:
            meta = dbx.files_upload(f.read(), remote_path, mode=WriteMode.overwrite)
    else:
        with open(local_path, "rb") as f:
            session_start = dbx.files_upload_session_start(f.read(_UPLOAD_CHUNK))
            cursor = dropbox.files.UploadSessionCursor(
                session_id=session_start.session_id, offset=f.tell()
            )
            commit = dropbox.files.CommitInfo(path=remote_path, mode=WriteMode.overwrite)
            while f.tell() < size:
                remaining = size - f.tell()
                if remaining <= _UPLOAD_CHUNK:
                    meta = dbx.files_upload_session_finish(
                        f.read(remaining), cursor, commit
                    )
                else:
                    dbx.files_upload_session_append_v2(f.read(_UPLOAD_CHUNK), cursor)
                    cursor.offset = f.tell()

    _last_download_hash[remote_path] = meta.content_hash
    return meta.content_hash


def _dbx_file_exists(remote_path: str) -> bool:
    """Check whether a file exists on Dropbox."""
    dbx = get_dropbox_client()
    try:
        dbx.files_get_metadata(remote_path)
        return True
    except ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            return False
        raise


def _dbx_delete(remote_path: str) -> None:
    """Delete a file on Dropbox (silent if not found)."""
    dbx = get_dropbox_client()
    try:
        dbx.files_delete_v2(remote_path)
    except ApiError:
        pass


def _dbx_list_folder(remote_path: str) -> list:
    """List all entries in a Dropbox folder (handles pagination)."""
    dbx = get_dropbox_client()
    try:
        result = dbx.files_list_folder(remote_path)
    except ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            return []
        raise
    entries = list(result.entries)
    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        entries.extend(result.entries)
    return entries


def _dbx_ensure_folder(remote_path: str) -> None:
    """Create a folder on Dropbox if it doesn't exist."""
    dbx = get_dropbox_client()
    try:
        dbx.files_create_folder_v2(remote_path)
    except ApiError as e:
        # Folder already exists — that's fine
        if hasattr(e.error, "is_path") and e.error.is_path():
            tag = e.error.get_path()
            if hasattr(tag, "is_conflict") and tag.is_conflict():
                return
        # Catch the common "path/conflict/folder" error shape
        pass


# ── Sync helpers ─────────────────────────────────────────────────────────
def _checkpoint_wal(db_path: Path) -> None:
    """Force WAL data into the main DB file so it's self-contained for upload."""
    if not db_path.exists():
        return
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
    except Exception:
        pass


def sync_db_to_dropbox(username: str | None = None) -> bool:
    """Upload the current user's DB to Dropbox if it has changed.

    Returns True if an upload was performed.
    """
    if not _is_authenticated():
        return False
    if username:
        db_path = _get_user_db_path(username)
        remote = f"/{_sanitize_username(username)}.db"
    else:
        db_path = DB_PATH
        remote = f"/{db_path.name}"
    if not db_path.exists():
        return False

    _checkpoint_wal(db_path)

    # Check if the file actually changed since last download/upload
    local_hash = _file_content_hash(db_path)
    if _last_download_hash.get(remote) == local_hash:
        return False

    try:
        _dbx_upload(db_path, remote)
        print(f"[dropbox] Uploaded {db_path.name}")
        return True
    except (ApiError, AuthError) as e:
        print(f"[dropbox] Upload failed for {db_path.name}: {e}")
        return False
    except Exception as e:
        print(f"[dropbox] Upload error: {e}")
        return False


def _file_content_hash(path: Path) -> str:
    """Compute a Dropbox-compatible content hash for a local file.

    Dropbox uses a specific chunked SHA-256 algorithm:
    split file into 4 MB blocks, SHA-256 each, then SHA-256
    the concatenation of those hashes.
    """
    BLOCK = 4 * 1024 * 1024
    block_hashes = b""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(BLOCK)
            if not chunk:
                break
            block_hashes += hashlib.sha256(chunk).digest()
    return hashlib.sha256(block_hashes).hexdigest()


def sync_users_json_to_dropbox() -> None:
    """Upload users.json to Dropbox."""
    if not _is_authenticated():
        return
    try:
        _dbx_upload(USERS_FILE, "/users.json")
    except Exception as e:
        print(f"[dropbox] Failed to upload users.json: {e}")


def _download_all_from_dropbox() -> None:
    """Download users.json and all user DBs from Dropbox to DATA_DIR.

    Called at startup when authenticated.
    """
    dbx = get_dropbox_client()

    # Download users.json
    _dbx_download("/users.json", USERS_FILE)

    # Download all user DBs
    users_data = _load_users()
    for u in users_data["users"]:
        slug = _sanitize_username(u["name"])
        remote = f"/{slug}.db"
        local = DATA_DIR / f"{slug}.db"
        h = _dbx_download(remote, local)
        if h:
            print(f"[dropbox] Downloaded {slug}.db")

    # Ensure backups folder exists
    _dbx_ensure_folder("/backups")


def _upload_all_to_dropbox() -> None:
    """Upload users.json and all user DBs to Dropbox.

    Called during initial migration of existing local data.
    """
    # Upload users.json
    if USERS_FILE.exists():
        _dbx_upload(USERS_FILE, "/users.json")

    # Upload all user DBs
    users_data = _load_users()
    for u in users_data["users"]:
        slug = _sanitize_username(u["name"])
        db_path = DATA_DIR / f"{slug}.db"
        if db_path.exists():
            _checkpoint_wal(db_path)
            _dbx_upload(db_path, f"/{slug}.db")
            print(f"[dropbox] Uploaded {slug}.db")

    _dbx_ensure_folder("/backups")


def _start_periodic_sync() -> None:
    """Start a daemon thread that uploads modified DBs every 5 minutes."""
    global _sync_thread

    def _sync_loop():
        import time
        while True:
            time.sleep(300)  # 5 minutes
            try:
                users_data = _load_users()
                for u in users_data["users"]:
                    sync_db_to_dropbox(u["name"])
                sync_users_json_to_dropbox()
            except Exception as e:
                print(f"[dropbox] Periodic sync error: {e}")

    _sync_thread = threading.Thread(target=_sync_loop, daemon=True, name="dropbox-sync")
    _sync_thread.start()


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

    # Upload backup to Dropbox
    if _is_authenticated():
        try:
            _dbx_upload(backup_file, f"/backups/{backup_file.name}")
            # Prune old backups on Dropbox too
            entries = _dbx_list_folder("/backups")
            db_entries = sorted(
                [e for e in entries if e.name.endswith(".db")],
                key=lambda e: e.name,
            )
            for old_entry in db_entries[:-MAX_BACKUPS]:
                _dbx_delete(f"/backups/{old_entry.name}")
        except Exception as e:
            print(f"[dropbox] Backup upload failed: {e}")

    return backup_file.name


# ── User management ──────────────────────────────────────────────────────
def _sanitize_username(name: str) -> str:
    """Convert a display name to a safe filename component (lowercase, alnum only)."""
    return re.sub(r"[^a-z0-9]", "", name.lower().strip())


def _load_users() -> dict:
    """Load users.json or return default structure."""
    if USERS_FILE.exists():
        try:
            data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "users" in data:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"users": [], "last_user": ""}


def _save_users(data: dict) -> None:
    """Save users.json locally and upload to Dropbox."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    sync_users_json_to_dropbox()


def _get_user_db_path(username: str) -> Path:
    """Return the DB file path for a given user display name."""
    slug = _sanitize_username(username)
    if not slug:
        slug = "default"
    return DATA_DIR / f"{slug}.db"


def _get_user_backup_dir(username: str) -> Path:
    """Return the backup directory for a user (may be overridden in users.json)."""
    users_data = _load_users()
    for u in users_data["users"]:
        if u["name"] == username and u.get("backup_dir"):
            custom = Path(u["backup_dir"])
            if custom.is_absolute():
                return custom
    return BACKUP_DIR


def _set_active_user_db(username: str) -> None:
    """Set the global DB_PATH and BACKUP_DIR for the given user."""
    global DB_PATH, BACKUP_DIR
    DB_PATH = _get_user_db_path(username)
    BACKUP_DIR = _get_user_backup_dir(username)


def _migrate_legacy_db() -> None:
    """If a legacy librarium.db exists in DATA_DIR and no users exist yet,
    offer it as the default user's database."""
    legacy = DATA_DIR / "librarium.db"
    if not legacy.exists():
        return
    users_data = _load_users()
    if users_data["users"]:
        return  # already have users
    # Will be handled by the first-time user creation UI


def init_schema() -> None:
    """Create all tables with full schema (idempotent). Used for new user databases.

    All CREATE TABLE statements use IF NOT EXISTS, so this is safe to call on an
    already-migrated database — it becomes a no-op in that case.
    """
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA foreign_keys=OFF")
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS libraries (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS sources (
            id          TEXT    PRIMARY KEY,
            type        TEXT    NOT NULL DEFAULT '',
            name        TEXT    NOT NULL DEFAULT '',
            short_name  TEXT    NOT NULL DEFAULT '',
            location    TEXT    NOT NULL DEFAULT '',
            url         TEXT    NOT NULL DEFAULT '',
            notes       TEXT    NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS series (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            library_id INTEGER NOT NULL REFERENCES libraries(id),
            UNIQUE(name, library_id)
        );

        CREATE TABLE IF NOT EXISTS books (
            id                        TEXT    PRIMARY KEY,
            name                      TEXT    NOT NULL DEFAULT '',
            author                    TEXT    NOT NULL DEFAULT '',
            slug                      TEXT    NOT NULL DEFAULT '',
            language                  TEXT    NOT NULL DEFAULT '',
            original_title            TEXT    NOT NULL DEFAULT '',
            original_language         TEXT    NOT NULL DEFAULT '',
            original_publication_date TEXT    NOT NULL DEFAULT '',
            publication_date           TEXT    NOT NULL DEFAULT '',
            isbn                      TEXT    NOT NULL DEFAULT '',
            pages                     INTEGER NOT NULL DEFAULT 0,
            starting_page             INTEGER NOT NULL DEFAULT 0,
            publisher                 TEXT    NOT NULL DEFAULT '',
            genre                     TEXT    NOT NULL DEFAULT '',
            summary                   TEXT    NOT NULL DEFAULT '',
            translator                TEXT    NOT NULL DEFAULT '',
            illustrator               TEXT    NOT NULL DEFAULT '',
            editor                    TEXT    NOT NULL DEFAULT '',
            prologue_author           TEXT    NOT NULL DEFAULT '',
            status                    TEXT    NOT NULL DEFAULT 'reading',
            source_type               TEXT    NOT NULL DEFAULT '',
            source_id                 TEXT    NOT NULL DEFAULT '',
            purchase_date             TEXT    NOT NULL DEFAULT '',
            purchase_price            TEXT    NOT NULL DEFAULT '',
            borrowed_start            TEXT    NOT NULL DEFAULT '',
            borrowed_end              TEXT    NOT NULL DEFAULT '',
            has_cover                 INTEGER NOT NULL DEFAULT 0,
            cover                     BLOB    DEFAULT NULL,
            is_gift                   INTEGER NOT NULL DEFAULT 0,
            cover_color               TEXT    NOT NULL DEFAULT '',
            cover_palette             TEXT    NOT NULL DEFAULT '[]',
            cover_hash                TEXT    NOT NULL DEFAULT '',
            library_id                INTEGER NOT NULL DEFAULT 1 REFERENCES libraries(id),
            subtitle                  TEXT    NOT NULL DEFAULT '',
            series_id                 INTEGER REFERENCES series(id) ON DELETE SET NULL,
            series_index              TEXT    NOT NULL DEFAULT '',
            work_id                   TEXT    DEFAULT NULL,
            is_primary_edition        INTEGER NOT NULL DEFAULT 1,
            format                    TEXT    DEFAULT 'paper',
            binding                   TEXT    DEFAULT NULL,
            audio_format              TEXT    DEFAULT NULL,
            total_time_seconds        INTEGER DEFAULT NULL,
            cover_thumb               BLOB    DEFAULT NULL,
            tags                      TEXT    NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS authors (
            name        TEXT    PRIMARY KEY,
            photo       BLOB,
            has_photo   INTEGER NOT NULL DEFAULT 0,
            birth_date  TEXT    NOT NULL DEFAULT '',
            birth_place TEXT    NOT NULL DEFAULT '',
            death_date  TEXT    NOT NULL DEFAULT '',
            death_place TEXT    NOT NULL DEFAULT '',
            biography   TEXT    NOT NULL DEFAULT '',
            photo_hash  TEXT    NOT NULL DEFAULT '',
            photo_thumb BLOB    DEFAULT NULL,
            gender      TEXT    NOT NULL DEFAULT 'unknown'
        );

        CREATE TABLE IF NOT EXISTS readings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id        TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            reading_number INTEGER NOT NULL DEFAULT 1,
            status         TEXT    NOT NULL DEFAULT 'reading',
            notes          TEXT    NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id          TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            date             TEXT    NOT NULL DEFAULT '',
            pages            INTEGER NOT NULL DEFAULT 0,
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            reading_id       INTEGER REFERENCES readings(id) ON DELETE SET NULL,
            progress_pct     REAL    DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS periods (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id          TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            start_date       TEXT    NOT NULL DEFAULT '',
            end_date         TEXT    NOT NULL DEFAULT '',
            pages            INTEGER NOT NULL DEFAULT 0,
            note             TEXT    NOT NULL DEFAULT '',
            reading_id       INTEGER REFERENCES readings(id) ON DELETE SET NULL,
            progress_pct     REAL    DEFAULT NULL,
            duration_seconds INTEGER DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS ratings (
            book_id       TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            dimension_key TEXT    NOT NULL,
            value         INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (book_id, dimension_key)
        );

        CREATE TABLE IF NOT EXISTS book_series (
            book_id      TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            series_id    INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
            series_index TEXT    NOT NULL DEFAULT '',
            PRIMARY KEY (book_id, series_id)
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            text    TEXT    NOT NULL DEFAULT '',
            page    INTEGER DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS thoughts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            text    TEXT    NOT NULL DEFAULT '',
            page    INTEGER DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS words (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id    TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            word       TEXT    NOT NULL DEFAULT '',
            definition TEXT    NOT NULL DEFAULT ''
        );
    """)
    # Insert the default "Books" library for fresh databases
    if db.execute("SELECT COUNT(*) FROM libraries").fetchone()[0] == 0:
        db.execute("INSERT INTO libraries (name, slug) VALUES ('Books', 'books')")
    db.commit()
    db.execute("PRAGMA foreign_keys=ON")
    db.close()


def _run_all_migrations() -> None:
    """Run every migration in order. Used when creating / switching users."""
    init_schema()   # idempotent — creates tables if not present on new DBs
    migrate_add_readings()
    migrate_add_authors()
    migrate_add_cover_color()
    migrate_add_cover_palette()
    migrate_add_cover_hash()
    migrate_add_photo_hash()
    migrate_add_subtitle()
    migrate_add_libraries()
    migrate_add_series()
    migrate_book_series_m2m()
    migrate_add_editions()
    migrate_add_format()
    migrate_add_total_time()
    migrate_add_period_duration()
    migrate_add_cover_thumb()
    migrate_add_photo_thumb()
    migrate_shared_authors()
    migrate_shared_sources()
    migrate_add_author_gender()
    migrate_add_tags()
    migrate_normalize_genres()
    migrate_merge_genres_into_tags()
    migrate_add_annotations()


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


def migrate_add_cover_thumb() -> None:
    """Add cover_thumb column to books for thumbnail images."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "cover_thumb" in cols:
        db.close()
        return
    print("⏳ Migrating: adding cover_thumb to books …")
    db.execute("ALTER TABLE books ADD COLUMN cover_thumb BLOB DEFAULT NULL")
    # Backfill thumbnails for existing covers
    rows = db.execute("SELECT id, cover FROM books WHERE has_cover = 1 AND cover IS NOT NULL").fetchall()
    for row in rows:
        thumb = _generate_thumbnail(row["cover"])
        if thumb:
            db.execute("UPDATE books SET cover_thumb = ? WHERE id = ?", (thumb, row["id"]))
    db.commit()
    db.close()
    print(f"✅ Migration complete – cover_thumb added ({len(rows)} thumbnails generated).")


def migrate_add_photo_thumb() -> None:
    """Add photo_thumb column to authors for thumbnail images."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(authors)").fetchall()]
    if "photo_thumb" in cols:
        db.close()
        return
    print("⏳ Migrating: adding photo_thumb to authors …")
    db.execute("ALTER TABLE authors ADD COLUMN photo_thumb BLOB DEFAULT NULL")
    rows = db.execute("SELECT name, photo FROM authors WHERE has_photo = 1 AND photo IS NOT NULL").fetchall()
    for row in rows:
        thumb = _generate_thumbnail(row["photo"])
        if thumb:
            db.execute("UPDATE authors SET photo_thumb = ? WHERE name = ?", (thumb, row["name"]))
    db.commit()
    db.close()
    print(f"✅ Migration complete – photo_thumb added ({len(rows)} thumbnails generated).")


# ── Migration: Make authors shared across libraries ─────────────────────
def migrate_shared_authors() -> None:
    """Remove library_id from authors PK, merging duplicate entries."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=OFF")

    # Check if authors table still has library_id in its PK
    cols = [r[1] for r in db.execute("PRAGMA table_info(authors)").fetchall()]
    if "library_id" not in cols:
        db.close()
        return

    print(">> Migrating: making authors shared across libraries ...")

    # Collect all authors grouped by name, keeping the richest entry
    all_authors = db.execute("SELECT * FROM authors ORDER BY name").fetchall()
    merged: dict[str, dict] = {}
    for row in all_authors:
        name = row["name"]
        d = dict(row)
        if name not in merged:
            merged[name] = d
        else:
            # Keep whichever has more data (photo, bio, dates)
            existing = merged[name]
            if not existing.get("has_photo") and d.get("has_photo"):
                merged[name] = d
            elif not existing.get("biography") and d.get("biography"):
                merged[name]["biography"] = d["biography"]
            if not existing.get("birth_date") and d.get("birth_date"):
                merged[name]["birth_date"] = d["birth_date"]
            if not existing.get("birth_place") and d.get("birth_place"):
                merged[name]["birth_place"] = d["birth_place"]
            if not existing.get("death_date") and d.get("death_date"):
                merged[name]["death_date"] = d["death_date"]
            if not existing.get("death_place") and d.get("death_place"):
                merged[name]["death_place"] = d["death_place"]

    db.execute("DROP TABLE IF EXISTS authors")
    db.execute("""
        CREATE TABLE authors (
            name        TEXT PRIMARY KEY,
            photo       BLOB,
            has_photo   INTEGER NOT NULL DEFAULT 0,
            birth_date  TEXT NOT NULL DEFAULT '',
            birth_place TEXT NOT NULL DEFAULT '',
            death_date  TEXT NOT NULL DEFAULT '',
            death_place TEXT NOT NULL DEFAULT '',
            biography   TEXT NOT NULL DEFAULT '',
            photo_hash  TEXT NOT NULL DEFAULT '',
            photo_thumb BLOB DEFAULT NULL
        )
    """)

    for name, d in merged.items():
        db.execute(
            "INSERT INTO authors (name, photo, has_photo, birth_date, birth_place, "
            "death_date, death_place, biography, photo_hash, photo_thumb) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, d.get("photo"), d.get("has_photo", 0),
             d.get("birth_date", ""), d.get("birth_place", ""),
             d.get("death_date", ""), d.get("death_place", ""),
             d.get("biography", ""), d.get("photo_hash", ""),
             d.get("photo_thumb")),
        )

    db.commit()
    db.close()
    print(f">> Migration complete - authors shared ({len(merged)} unique authors).")


# ── Migration: Make sources shared across libraries ─────────────────────
def migrate_shared_sources() -> None:
    """Remove library_id column from sources table."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=OFF")

    cols = [r[1] for r in db.execute("PRAGMA table_info(sources)").fetchall()]
    if "library_id" not in cols:
        db.close()
        return

    print(">> Migrating: making sources shared across libraries ...")

    # Recreate sources without library_id, deduplicating by name
    all_sources = db.execute("SELECT * FROM sources ORDER BY name").fetchall()
    seen_names: dict[str, dict] = {}
    unique_sources: list[dict] = []
    for row in all_sources:
        d = dict(row)
        key = d["name"].strip().lower()
        if key not in seen_names:
            seen_names[key] = d
            unique_sources.append(d)

    db.execute("DROP TABLE IF EXISTS sources")
    db.execute("""
        CREATE TABLE sources (
            id          TEXT    PRIMARY KEY,
            type        TEXT    NOT NULL DEFAULT '',
            name        TEXT    NOT NULL DEFAULT '',
            short_name  TEXT    NOT NULL DEFAULT '',
            location    TEXT    NOT NULL DEFAULT '',
            url         TEXT    NOT NULL DEFAULT '',
            notes       TEXT    NOT NULL DEFAULT ''
        )
    """)

    for s in unique_sources:
        db.execute(
            "INSERT INTO sources (id, type, name, short_name, location, url, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (s["id"], s.get("type", ""), s.get("name", ""), s.get("short_name", ""),
             s.get("location", ""), s.get("url", ""), s.get("notes", "")),
        )

    db.commit()
    db.close()
    print(f">> Migration complete - sources shared ({len(unique_sources)} unique sources).")


# ── Migration: Add gender column to authors ─────────────────────────────
def migrate_add_author_gender() -> None:
    """Add gender column to authors table."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(authors)").fetchall()]
    if "gender" in cols:
        db.close()
        return
    print(">> Migrating: adding gender column to authors ...")
    db.execute("ALTER TABLE authors ADD COLUMN gender TEXT NOT NULL DEFAULT 'unknown'")
    db.commit()
    db.close()
    print(">> Migration complete - gender column added to authors.")


# ── Migration: Add tags column to books ─────────────────────────────────
def migrate_add_tags() -> None:
    """Add tags column to books (semicolon-separated, like genre)."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    cols = [r[1] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "tags" in cols:
        db.close()
        return
    print(">> Migrating: adding tags column to books ...")
    db.execute("ALTER TABLE books ADD COLUMN tags TEXT NOT NULL DEFAULT ''")
    db.commit()
    db.close()
    print(">> Migration complete - tags column added to books.")


# ── Migration: Normalize genre capitalization ───────────────────────────
def _title_case_genre(genre: str) -> str:
    """Capitalize a genre string using title case (each word capitalized)."""
    return " ".join(w.capitalize() for w in genre.strip().split())


def migrate_normalize_genres() -> None:
    """Normalize all genre values to title case."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    # Check if we've already run this (use a simple sentinel via PRAGMA)
    rows = db.execute("SELECT id, genre FROM books WHERE genre != ''").fetchall()
    any_changed = False
    for row in rows:
        old = row["genre"]
        parts = [_title_case_genre(p) for p in old.split(";")]
        new = "; ".join(parts)
        if old != new:
            db.execute("UPDATE books SET genre = ? WHERE id = ?", (new, row["id"]))
            any_changed = True
    if any_changed:
        print(">> Normalizing genre capitalization ...")
        db.commit()
        print(">> Genre capitalization normalized.")
    db.close()


# ── Migration: Merge genres into tags ────────────────────────────────────
def migrate_merge_genres_into_tags() -> None:
    """Move all genre values into the tags field and clear genre."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    # Only run if any book still has a non-empty genre
    rows = db.execute("SELECT id, genre, tags FROM books WHERE genre != ''").fetchall()
    if not rows:
        db.close()
        return

    print(">> Migrating: merging genres into tags ...")
    for row in rows:
        genre_val = row["genre"]
        tags_val = row["tags"] or ""
        # Collect unique values from both fields, preserving order
        seen: set[str] = set()
        merged: list[str] = []
        for part in genre_val.split(";"):
            part = part.strip()
            low = part.lower()
            if part and low not in seen:
                seen.add(low)
                merged.append(part)
        for part in tags_val.split(";"):
            part = part.strip()
            low = part.lower()
            if part and low not in seen:
                seen.add(low)
                merged.append(part)
        new_tags = "; ".join(merged)
        db.execute("UPDATE books SET tags = ?, genre = '' WHERE id = ?", (new_tags, row["id"]))
    db.commit()
    db.close()
    print(f">> Migration complete - genres merged into tags for {len(rows)} books.")


# ── Migration: Add annotations tables (quotes, thoughts, words) ─────────
def migrate_add_annotations() -> None:
    """Create quotes, thoughts, and words tables."""
    if not DB_PATH.exists():
        return
    db = sqlite3.connect(str(DB_PATH))
    existing = {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if "quotes" in existing and "thoughts" in existing and "words" in existing:
        db.close()
        return
    print(">> Migrating: adding annotations tables (quotes, thoughts, words) ...")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS quotes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            text    TEXT    NOT NULL DEFAULT '',
            page    INTEGER DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS thoughts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            text    TEXT    NOT NULL DEFAULT '',
            page    INTEGER DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS words (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id    TEXT    NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            word       TEXT    NOT NULL DEFAULT '',
            definition TEXT    NOT NULL DEFAULT ''
        );
    """)
    db.commit()
    db.close()
    print(">> Migration complete — annotations tables created.")


# ── Cover colour helper ─────────────────────────────────────────────────
THUMB_MAX_WIDTH = 300


def _generate_thumbnail(cover_blob: bytes | None) -> bytes | None:
    """Resize a cover image to a JPEG thumbnail (max 300 px wide)."""
    if not cover_blob:
        return None
    try:
        img = Image.open(io.BytesIO(cover_blob)).convert("RGB")
        if img.width <= THUMB_MAX_WIDTH:
            return cover_blob  # already small enough
        ratio = THUMB_MAX_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((THUMB_MAX_WIDTH, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return buf.getvalue()
    except Exception:
        return None


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
        # Determine the DB path for the current user
        current_user = request.cookies.get("librarium_user", "")
        if current_user:
            db_path = _get_user_db_path(current_user)
        else:
            db_path = DB_PATH
        g.db = sqlite3.connect(str(db_path))
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
def _get_selected_library_ids() -> list[int]:
    """Return selected library IDs from cookie (comma-separated).

    An empty list means *all* libraries are selected (no filter).
    Backward-compatible: old cookie value ``"0"`` (All) is treated as
    empty; a single numeric value ``"3"`` becomes ``[3]``.
    """
    raw = request.cookies.get("librarium_library", "")
    if not raw:
        return []
    db = get_db()
    all_ids = {r["id"] for r in db.execute("SELECT id FROM libraries").fetchall()}
    selected: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        try:
            lid = int(part)
            if lid in all_ids:
                selected.append(lid)
        except (ValueError, TypeError):
            pass
    return selected


def _lib_filter(lib_ids: list[int], col: str = "library_id") -> tuple[str, tuple]:
    """Return (sql_condition, params) for library filtering.

    An empty *lib_ids* list means no filtering (all libraries).
    """
    if not lib_ids:
        return ("1=1", ())
    if len(lib_ids) == 1:
        return (f"{col} = ?", (lib_ids[0],))
    placeholders = ",".join("?" * len(lib_ids))
    return (f"{col} IN ({placeholders})", tuple(lib_ids))


@app.context_processor
def inject_library_context():
    """Make selected_library_ids and all_libraries available in every template."""
    try:
        db = get_db()
        lib_ids = _get_selected_library_ids()
        all_libs = db.execute(
            "SELECT * FROM libraries ORDER BY id"
        ).fetchall()
        all_lib_dicts = [dict(l) for l in all_libs]
        all_lib_ids = [l["id"] for l in all_libs]
        # When nothing is explicitly selected, all libraries are active
        sel_ids = lib_ids if lib_ids else all_lib_ids
        current_user = request.cookies.get("librarium_user", "")
        backup_dir = str(_get_user_backup_dir(current_user)) if current_user else str(BACKUP_DIR)
        return {
            "selected_library_ids": sel_ids,
            "all_libraries": all_lib_dicts,
            "app_version": APP_VERSION,
            "current_user": current_user,
            "backup_dir": backup_dir,
            "db_path": str(DB_PATH),
            "dropbox_connected": _is_authenticated(),
        }
    except Exception:
        return {
            "selected_library_ids": [],
            "all_libraries": [],
            "app_version": APP_VERSION,
            "current_user": request.cookies.get("librarium_user", "") if request else "",
            "backup_dir": str(BACKUP_DIR),
            "db_path": str(DB_PATH),
            "dropbox_connected": _is_authenticated(),
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
    {
        "group": "Visual Art",
        "items": [
            {"key": "art_quality",        "label": "Art Quality",        "tip": "Overall quality of illustrations, line work, and artistic style"},
            {"key": "character_design",    "label": "Character Design",   "tip": "Visual distinctiveness and memorability of characters"},
            {"key": "color_inking",        "label": "Color & Inking",     "tip": "Quality of coloring palette or black-and-white inking"},
            {"key": "background_art",      "label": "Background Art",     "tip": "Detail, atmosphere, and richness of environments"},
            {"key": "cover_art",           "label": "Cover Art",          "tip": "Visual impact and appeal of cover illustrations"},
            {"key": "visual_consistency",  "label": "Visual Consistency", "tip": "Art quality maintained across chapters and volumes"},
        ],
    },
    {
        "group": "Sequential Narrative",
        "items": [
            {"key": "panel_layout",          "label": "Panel Layout",          "tip": "Page composition, panel flow, and reading rhythm"},
            {"key": "visual_storytelling",   "label": "Visual Storytelling",   "tip": "How effectively the art drives the narrative without words"},
            {"key": "action_choreography",   "label": "Action Choreography",   "tip": "Dynamic movement, impact, and clarity in action scenes"},
            {"key": "expressiveness",        "label": "Expressiveness",        "tip": "Emotional range conveyed through faces and body language"},
            {"key": "text_integration",      "label": "Text Integration",      "tip": "Harmony of speech bubbles, sound effects, and narration with art"},
            {"key": "splash_pages",          "label": "Splash Pages",          "tip": "Storytelling impact of full-page and double-page spreads"},
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


def _collect_activity_events(db, lf: str, lp: tuple, lf_b: str, lp_b: tuple,
                             date_from: str | None = None,
                             date_to: str | None = None) -> list[dict]:
    """Collect raw activity events, agglutinate per (date, book_id), and return
    the merged list sorted by date descending.  When *date_from* / *date_to*
    are given (YYYY-MM-DD strings) only events within that range are included.
    """
    _raw: list[dict] = []

    # Optional date-range SQL fragments
    def _dr(col: str) -> str:
        parts = []
        if date_from:
            parts.append(f"{col} >= ?")
        if date_to:
            parts.append(f"{col} <= ?")
        return (" AND " + " AND ".join(parts)) if parts else ""

    def _dp() -> tuple:
        p: list[str] = []
        if date_from:
            p.append(date_from)
        if date_to:
            p.append(date_to)
        return tuple(p)

    # Sessions
    for rs in db.execute(
        "SELECT s.date, s.pages, s.duration_seconds, b.id AS book_id, b.name AS book_name, "
        "b.has_cover, b.cover_hash "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date != '' AND {lf_b}{_dr('s.date')} ORDER BY s.date DESC, s.id DESC",
        lp_b + _dp(),
    ).fetchall():
        _raw.append({"date": rs["date"], "type": "session", "pages": rs["pages"],
                      "seconds": rs["duration_seconds"], "book_id": rs["book_id"],
                      "book_name": rs["book_name"], "has_cover": bool(rs["has_cover"]),
                      "cover_hash": rs["cover_hash"] or ""})

    # Periods
    for rp in db.execute(
        "SELECT p.end_date, p.pages, p.duration_seconds, b.id AS book_id, b.name AS book_name, "
        "b.has_cover, b.cover_hash "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND {lf_b}{_dr('p.end_date')} "
        f"ORDER BY p.end_date DESC, p.id DESC",
        lp_b + _dp(),
    ).fetchall():
        _raw.append({"date": rp["end_date"], "type": "period", "pages": rp["pages"],
                      "seconds": rp["duration_seconds"], "book_id": rp["book_id"],
                      "book_name": rp["book_name"], "has_cover": bool(rp["has_cover"]),
                      "cover_hash": rp["cover_hash"] or ""})

    # Finished
    for fr in db.execute(
        "SELECT r.id, r.book_id, b.name AS book_name, b.has_cover, b.cover_hash "
        "FROM readings r JOIN books b ON b.id = r.book_id "
        f"WHERE r.status = 'finished' AND {lf_b}", lp_b
    ).fetchall():
        candidates = []
        r = db.execute("SELECT MAX(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (fr["id"],)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        r = db.execute("SELECT MAX(end_date) AS d FROM periods WHERE reading_id = ? AND end_date != ''", (fr["id"],)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        if candidates:
            d = max(candidates)
            if (not date_from or d >= date_from) and (not date_to or d <= date_to):
                _raw.append({"date": d, "type": "finished", "book_id": fr["book_id"],
                              "book_name": fr["book_name"], "has_cover": bool(fr["has_cover"]),
                              "cover_hash": fr["cover_hash"] or ""})

    # Started
    for sr in db.execute(
        "SELECT r.id, r.book_id, b.name AS book_name, b.has_cover, b.cover_hash "
        "FROM readings r JOIN books b ON b.id = r.book_id "
        f"WHERE {lf_b}", lp_b
    ).fetchall():
        candidates = []
        r = db.execute("SELECT MIN(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (sr["id"],)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        r = db.execute("SELECT MIN(start_date) AS d FROM periods WHERE reading_id = ? AND start_date != ''", (sr["id"],)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        if candidates:
            d = min(candidates)
            if (not date_from or d >= date_from) and (not date_to or d <= date_to):
                _raw.append({"date": d, "type": "started", "book_id": sr["book_id"],
                              "book_name": sr["book_name"], "has_cover": bool(sr["has_cover"]),
                              "cover_hash": sr["cover_hash"] or ""})

    # Purchased
    dr_buy = ""
    dp_buy: list[str] = []
    if date_from:
        dr_buy += " AND b.purchase_date >= ?"
        dp_buy.append(date_from)
    if date_to:
        dr_buy += " AND b.purchase_date <= ?"
        dp_buy.append(date_to)
    for bk in db.execute(
        f"SELECT b.id, b.name, b.has_cover, b.cover_hash, b.purchase_date, "
        f"b.source_type, b.source_id, b.purchase_price, s.name AS source_name "
        f"FROM books b LEFT JOIN sources s ON s.id = b.source_id "
        f"WHERE {lf} AND b.purchase_date IS NOT NULL AND b.purchase_date != '' "
        f"AND b.source_type IN ('owned','physical_store','web_store') "
        f"AND (b.work_id IS NULL OR b.is_primary_edition = 1){dr_buy}",
        lp + tuple(dp_buy),
    ).fetchall():
        _raw.append({"date": bk["purchase_date"], "type": "bought", "book_id": bk["id"],
                      "book_name": bk["name"], "has_cover": bool(bk["has_cover"]),
                      "cover_hash": bk["cover_hash"] or "", "purchase_price": bk["purchase_price"] or "",
                      "source_name": bk["source_name"] or ""})

    # Borrowed
    dr_bor = ""
    dp_bor: list[str] = []
    if date_from:
        dr_bor += " AND b.borrowed_start >= ?"
        dp_bor.append(date_from)
    if date_to:
        dr_bor += " AND b.borrowed_start <= ?"
        dp_bor.append(date_to)
    for bk in db.execute(
        f"SELECT b.id, b.name, b.has_cover, b.cover_hash, b.borrowed_start, b.source_id, "
        f"s.name AS source_name "
        f"FROM books b LEFT JOIN sources s ON s.id = b.source_id "
        f"WHERE {lf} AND b.borrowed_start IS NOT NULL AND b.borrowed_start != '' "
        f"AND b.source_type IN ('library','person') "
        f"AND (b.work_id IS NULL OR b.is_primary_edition = 1){dr_bor}",
        lp + tuple(dp_bor),
    ).fetchall():
        _raw.append({"date": bk["borrowed_start"], "type": "borrowed", "book_id": bk["id"],
                      "book_name": bk["name"], "has_cover": bool(bk["has_cover"]),
                      "cover_hash": bk["cover_hash"] or "", "source_name": bk["source_name"] or ""})

    # Gifted
    dr_gift = ""
    dp_gift: list[str] = []
    if date_from:
        dr_gift += " AND purchase_date >= ?"
        dp_gift.append(date_from)
    if date_to:
        dr_gift += " AND purchase_date <= ?"
        dp_gift.append(date_to)
    for bk in db.execute(
        f"SELECT b.id, b.name, b.has_cover, b.cover_hash, b.purchase_date, "
        f"s.name AS source_name "
        f"FROM books b LEFT JOIN sources s ON s.id = b.source_id "
        f"WHERE {lf_b} AND b.is_gift = 1 AND b.purchase_date IS NOT NULL AND b.purchase_date != '' "
        f"AND (b.work_id IS NULL OR b.is_primary_edition = 1){dr_gift}",
        lp_b + tuple(dp_gift),
    ).fetchall():
        _raw.append({"date": bk["purchase_date"], "type": "gift", "book_id": bk["id"],
                      "book_name": bk["name"], "has_cover": bool(bk["has_cover"]),
                      "cover_hash": bk["cover_hash"] or "",
                      "source_name": bk["source_name"] or ""})

    # Agglutinate
    _agg: dict[tuple[str, str], dict] = {}
    for ev in _raw:
        key = (ev["date"], ev["book_id"])
        if key not in _agg:
            _agg[key] = {
                "date": ev["date"], "book_id": ev["book_id"],
                "book_name": ev["book_name"],
                "has_cover": ev["has_cover"], "cover_hash": ev["cover_hash"],
                "pages": 0, "seconds": 0,
                "started": False, "finished": False,
                "bought": False, "borrowed": False, "gift": False,
                "source_name": "", "purchase_price": "",
            }
        g = _agg[key]
        t = ev["type"]
        if t in ("session", "period"):
            g["pages"] += ev.get("pages", 0) or 0
            g["seconds"] += ev.get("seconds", 0) or 0
        elif t == "started":
            g["started"] = True
        elif t == "finished":
            g["finished"] = True
        elif t == "bought":
            g["bought"] = True
            g["purchase_price"] = ev.get("purchase_price", "")
            if ev.get("source_name"):
                g["source_name"] = ev["source_name"]
        elif t == "borrowed":
            g["borrowed"] = True
            if ev.get("source_name"):
                g["source_name"] = ev["source_name"]
        elif t == "gift":
            g["gift"] = True
            if ev.get("source_name"):
                g["source_name"] = ev["source_name"]

    return sorted(_agg.values(), key=lambda x: x["date"], reverse=True)


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


@app.template_filter('display_date')
def display_date_filter(value: str) -> str:
    """Wrap a date value in a span with data-date for client-side i18n formatting."""
    from markupsafe import Markup
    raw = (value or "").strip()
    if not raw:
        return ""
    escaped = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return Markup(f'<span data-date="{escaped}">{escaped}</span>')


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


def _format_duration_hms(seconds: int) -> str:
    """Convert seconds to Hours, Minutes, Seconds (no day rounding)."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"


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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    langs: set[str] = set()
    for row in db.execute(f"SELECT language, original_language FROM books WHERE {lf}", lp).fetchall():
        for val in (row["language"], row["original_language"]):
            if val and val.strip():
                langs.add(val.strip())
    return sorted(langs)


def _collect_field_values(*fields: str) -> dict[str, list[str]]:
    """Scan books in the current library and return unique values per field."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    # Only query the columns we need
    safe_fields = [f for f in fields if re.match(r'^[a-z_]+$', f)]
    if not safe_fields:
        return {}
    cols = ", ".join(safe_fields)
    lf, lp = _lib_filter(lib_ids)
    rows = db.execute(f"SELECT {cols} FROM books WHERE {lf}", lp).fetchall()
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


def _build_index_per_reading(db, lib_ids):
    """Build one library entry per *selected reading* across ALL editions.

    Selection logic per edition:
    - 1 reading  → show it
    - >1 readings, some finished → show each finished one
    - >1 readings, none finished → show the one with highest priority
      (reading > abandoned > not-started > draft)
    """
    lf, lp = _lib_filter(lib_ids)
    book_rows = db.execute(
        f"SELECT id, name, subtitle, author, status, pages, starting_page, "
        f"has_cover, cover_hash, publisher, language, publication_date, "
        f"work_id, format, total_time_seconds, tags FROM books WHERE {lf}",
        lp,
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
            "tags": bk.get("tags", "") or "",
        })

    # Only show reading_number when a book appears more than once
    from collections import Counter
    bid_counts = Counter(b["id"] for b in books)
    for b in books:
        if bid_counts[b["id"]] <= 1:
            b["reading_number"] = None

    return books


# ── Error handlers ───────────────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def dashboard():
    """Dashboard – overview of reading stats, currently reading, streaks, etc."""
    from collections import Counter
    from datetime import date, timedelta
    import random

    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    today = date.today()
    today_str = today.isoformat()
    current_year = str(today.year)

    # ── Hero stats ribbon ────────────────────────────────────────────────
    all_rows = db.execute(
        "SELECT author, pages, starting_page, status, source_type, work_id FROM books "
        f"WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1)", lp
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
    finished_count = db.execute(
        "SELECT COUNT(DISTINCT COALESCE(b.work_id, b.id)) FROM books b "
        "JOIN readings r ON r.book_id = b.id "
        f"WHERE {lf_b} AND r.status = 'finished'", lp_b
    ).fetchone()[0]
    owned_count = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND source_type = 'owned'", lp
    ).fetchone()[0]

    # Total time: must compute from sessions+periods across all books
    time_row = db.execute(
        "SELECT COALESCE(SUM(s.duration_seconds),0) AS sec "
        f"FROM sessions s JOIN books b ON b.id = s.book_id WHERE {lf_b}", lp_b
    ).fetchone()
    total_session_seconds = time_row["sec"]
    total_session_pages = db.execute(
        "SELECT COALESCE(SUM(s.pages),0) AS p "
        f"FROM sessions s JOIN books b ON b.id = s.book_id WHERE {lf_b}", lp_b
    ).fetchone()["p"]
    total_period_pages = db.execute(
        "SELECT COALESCE(SUM(p.pages),0) AS p "
        f"FROM periods p JOIN books b ON b.id = p.book_id WHERE {lf_b}", lp_b
    ).fetchone()["p"]
    # Estimate period time proportionally
    period_seconds = int(total_period_pages * (total_session_seconds / total_session_pages)) if total_session_pages > 0 else 0
    total_all_seconds = total_session_seconds + period_seconds
    total_library_time = _format_duration_long(total_all_seconds)
    total_library_time_hms = _format_duration_hms(total_all_seconds)

    # Average rating across all rated finished books
    avg_rating = None
    rated_sum = 0.0
    rated_count_val = 0
    all_book_ids = db.execute(
        f"SELECT id FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchall()
    for bid_row in all_book_ids:
        ratings = _load_ratings(bid_row["id"])
        avg = _calc_avg_rating(ratings)
        if avg is not None and avg > 0:
            rated_sum += avg
            rated_count_val += 1
    avg_rating = round(rated_sum / rated_count_val, 2) if rated_count_val > 0 else None

    # ── Currently reading books ──────────────────────────────────────────
    reading_books: list[dict] = []
    for row in db.execute(f"""
        SELECT b.id, b.name, b.author, b.pages, b.starting_page, b.has_cover, b.cover_hash,
               b.format,
               COALESCE(s.tp, 0) AS session_pages,
               COALESCE(p.pp, 0) AS period_pages,
               s.last_date, p.last_period,
               COALESCE(pct.max_pct, 0) AS max_pct
        FROM books b
        LEFT JOIN (SELECT book_id, SUM(pages) AS tp, MAX(date) AS last_date
                   FROM sessions WHERE date != '' GROUP BY book_id) s ON s.book_id = b.id
        LEFT JOIN (SELECT book_id, SUM(pages) AS pp, MAX(end_date) AS last_period
                   FROM periods GROUP BY book_id) p ON p.book_id = b.id
        LEFT JOIN (
            SELECT book_id, MAX(pct) AS max_pct FROM (
                SELECT book_id, MAX(progress_pct) AS pct FROM sessions WHERE progress_pct IS NOT NULL GROUP BY book_id
                UNION ALL
                SELECT book_id, MAX(progress_pct) AS pct FROM periods WHERE progress_pct IS NOT NULL GROUP BY book_id
            ) GROUP BY book_id
        ) pct ON pct.book_id = b.id
        WHERE b.status = 'reading' AND {lf_b}
    """, lp_b).fetchall():
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
        last_activity = max(last_candidates) if last_candidates else None
        reading_books.append({
            "id": row["id"],
            "name": row["name"],
            "author": row["author"] or "",
            "has_cover": bool(row["has_cover"]),
            "cover_hash": row["cover_hash"] or "",
            "total_pages": tp,
            "effective_pages": eff,
            "pages_read": total_read,
            "pages_remaining": remaining,
            "progress_pct": prog_pct,
            "last_activity": last_activity,
            "format": book_fmt,
        })
    reading_books.sort(key=lambda b: b["last_activity"] or "0000-00-00", reverse=True)

    # ── Daily data for streaks & heatmap ─────────────────────────────────
    daily_sessions: dict[str, dict] = {}
    for row in db.execute(
        "SELECT s.date, SUM(s.pages) AS pages, SUM(s.duration_seconds) AS seconds "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date != '' AND {lf_b} GROUP BY s.date", lp_b
    ).fetchall():
        daily_sessions[row["date"]] = {"pages": row["pages"], "seconds": row["seconds"]}
    daily_periods: dict[str, int] = {}
    for row in db.execute(
        "SELECT p.end_date, SUM(p.pages) AS pages "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND {lf_b} GROUP BY p.end_date", lp_b
    ).fetchall():
        daily_periods[row["end_date"]] = row["pages"]
    all_dates = sorted(set(daily_sessions) | set(daily_periods))
    daily_data = []
    for d in all_dates:
        s = daily_sessions.get(d, {"pages": 0, "seconds": 0})
        p = daily_periods.get(d, 0)
        daily_data.append({"date": d, "pages": s["pages"] + p, "seconds": s["seconds"]})

    # ── This Year at a Glance ────────────────────────────────────────────
    year_start = f"{current_year}-01-01"
    books_finished_this_year = 0
    pages_this_year = 0
    time_this_year = 0
    finished_readings_yr = db.execute(
        "SELECT r.id FROM readings r JOIN books b ON b.id = r.book_id "
        f"WHERE r.status = 'finished' AND {lf_b}", lp_b
    ).fetchall()
    for fr in finished_readings_yr:
        rid = fr["id"]
        candidates = []
        r = db.execute("SELECT MAX(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (rid,)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        r = db.execute("SELECT MAX(end_date) AS d FROM periods WHERE reading_id = ? AND end_date != ''", (rid,)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        if candidates and max(candidates) >= year_start:
            books_finished_this_year += 1

    for row in db.execute(
        "SELECT SUM(s.pages) AS p, SUM(s.duration_seconds) AS t "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE SUBSTR(s.date, 1, 4) = ? AND {lf_b}", (current_year, *lp_b)
    ).fetchall():
        pages_this_year += row["p"] or 0
        time_this_year += row["t"] or 0
    for row in db.execute(
        "SELECT SUM(p.pages) AS p FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE SUBSTR(p.end_date, 1, 4) = ? AND {lf_b}", (current_year, *lp_b)
    ).fetchall():
        pages_this_year += row["p"] or 0

    # Year-over-year comparison
    prev_year = str(today.year - 1)
    prev_year_start = f"{prev_year}-01-01"
    same_day_prev_year = f"{prev_year}-{today_str[5:]}"
    books_finished_prev_ytd = 0
    for fr in finished_readings_yr:
        rid = fr["id"]
        candidates = []
        r = db.execute("SELECT MAX(date) AS d FROM sessions WHERE reading_id = ? AND date != ''", (rid,)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        r = db.execute("SELECT MAX(end_date) AS d FROM periods WHERE reading_id = ? AND end_date != ''", (rid,)).fetchone()
        if r and r["d"]: candidates.append(r["d"])
        if candidates:
            finish_date = max(candidates)
            if finish_date >= prev_year_start and finish_date <= same_day_prev_year:
                books_finished_prev_ytd += 1
    yoy_diff = books_finished_this_year - books_finished_prev_ytd

    # Pages and time for previous year YTD
    pages_prev_ytd = 0
    time_prev_ytd = 0
    for row in db.execute(
        "SELECT COALESCE(SUM(s.pages),0) AS p, COALESCE(SUM(s.duration_seconds),0) AS t "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date >= ? AND s.date <= ? AND {lf_b}", (prev_year_start, same_day_prev_year, *lp_b)
    ).fetchall():
        pages_prev_ytd += row["p"] or 0
        time_prev_ytd += row["t"] or 0
    for row in db.execute(
        "SELECT COALESCE(SUM(p.pages),0) AS p FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date >= ? AND p.end_date <= ? AND {lf_b}", (prev_year_start, same_day_prev_year, *lp_b)
    ).fetchall():
        pages_prev_ytd += row["p"] or 0
    yoy_pages_diff = pages_this_year - pages_prev_ytd
    yoy_time_diff = time_this_year - time_prev_ytd

    # ── Recent activity feed (comprehensive events) ──────────────────────
    recent_activity = _collect_activity_events(db, lf, lp, lf_b, lp_b)[:50]

    # ── Last books owned (50 most recent) ─────────────────────────────
    last_books_owned: list[dict] = []
    for row in db.execute(
        f"SELECT b.id, b.name, b.author, b.has_cover, b.cover_hash, b.purchase_date, "
        f"b.purchase_price, b.source_type, b.is_gift, "
        f"s.name AS source_name "
        f"FROM books b LEFT JOIN sources s ON s.id = b.source_id "
        f"WHERE {lf} AND b.purchase_date IS NOT NULL AND b.purchase_date != '' "
        f"AND (b.work_id IS NULL OR b.is_primary_edition = 1) "
        f"ORDER BY b.purchase_date DESC LIMIT 50", lp
    ).fetchall():
        last_books_owned.append({
            "id": row["id"],
            "name": row["name"],
            "author": row["author"] or "",
            "has_cover": bool(row["has_cover"]),
            "cover_hash": row["cover_hash"] or "",
            "purchase_date": row["purchase_date"],
            "purchase_price": row["purchase_price"] or "",
            "source_name": row["source_name"] or "",
            "source_type": row["source_type"] or "",
            "is_gift": bool(row["is_gift"]),
        })

    # ── Top-rated books ──────────────────────────────────────────────────
    top_rated: list[dict] = []
    for bid_row in all_book_ids:
        ratings = _load_ratings(bid_row["id"])
        avg = _calc_avg_rating(ratings)
        if avg is not None and avg > 0:
            bk = db.execute("SELECT id, name, author, has_cover, cover_hash FROM books WHERE id = ?",
                            (bid_row["id"],)).fetchone()
            if bk:
                top_rated.append({
                    "id": bk["id"], "name": bk["name"], "author": bk["author"] or "",
                    "has_cover": bool(bk["has_cover"]), "cover_hash": bk["cover_hash"] or "",
                    "rating": round(avg, 2),
                })
    top_rated.sort(key=lambda x: x["rating"], reverse=True)
    top_rated = top_rated[:5]

    # ── Records: highest rated, longest, shortest, most reread ───────────
    highest_rated_book = top_rated[0] if top_rated else None

    longest_finished = None
    shortest_finished = None
    longest_pages = 0
    shortest_pages = float("inf")
    for bk in db.execute(
        f"SELECT b.id, b.name, b.pages, b.has_cover, b.cover_hash FROM books b "
        f"JOIN readings r ON r.book_id = b.id "
        f"WHERE r.status = 'finished' AND b.pages > 0 AND {lf_b} "
        f"AND (b.work_id IS NULL OR b.is_primary_edition = 1)", lp_b
    ).fetchall():
        p = bk["pages"]
        if p > longest_pages:
            longest_pages = p
            longest_finished = {"name": bk["name"], "id": bk["id"], "pages": p, "has_cover": bool(bk["has_cover"]), "cover_hash": bk["cover_hash"] or ""}
        if p < shortest_pages:
            shortest_pages = p
            shortest_finished = {"name": bk["name"], "id": bk["id"], "pages": p, "has_cover": bool(bk["has_cover"]), "cover_hash": bk["cover_hash"] or ""}

    reread_row = db.execute(
        "SELECT COALESCE(b.work_id, r.book_id) AS wid, COUNT(*) AS cnt FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        f"WHERE {lf_b} GROUP BY wid HAVING cnt > 1 ORDER BY cnt DESC LIMIT 1", lp_b
    ).fetchone()
    most_reread = None
    if reread_row:
        rbk = db.execute(
            "SELECT id, name, has_cover, cover_hash FROM books WHERE (work_id = ? OR id = ?) "
            "ORDER BY is_primary_edition DESC LIMIT 1",
            (reread_row["wid"], reread_row["wid"]),
        ).fetchone()
        if rbk:
            most_reread = {"name": rbk["name"], "id": rbk["id"], "count": reread_row["cnt"],
                           "has_cover": bool(rbk["has_cover"]), "cover_hash": rbk["cover_hash"] or ""}

    # ── Format & source breakdown ────────────────────────────────────────
    format_counts: dict[str, int] = Counter()
    source_counts: dict[str, int] = Counter()
    for bk in db.execute(
        f"SELECT format, source_type, is_gift FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchall():
        fmt = bk["format"] or "paper"
        format_counts[fmt] += 1
        if bk["is_gift"]:
            source_counts["gift"] += 1
        elif bk["source_type"]:
            source_counts[bk["source_type"]] += 1
        else:
            source_counts["unknown"] += 1

    # ── Tag cloud (top 20) ───────────────────────────────────────────────
    tag_counts: dict[str, int] = Counter()
    for bk in db.execute(
        f"SELECT tags FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1) AND tags IS NOT NULL AND tags != ''", lp
    ).fetchall():
        for t in bk["tags"].split(";"):
            t = t.strip()
            if t:
                tag_counts[t] += 1
    top_tags = dict(Counter(tag_counts).most_common(20))

    # ── Series progress ──────────────────────────────────────────────────
    series_progress: list[dict] = []
    all_series = db.execute(
        "SELECT s.id, s.name FROM series s WHERE s.library_id IN (SELECT id FROM libraries)" if not lib_ids
        else f"SELECT s.id, s.name FROM series s WHERE s.library_id IN ({','.join('?' * len(lib_ids))})",
        tuple(lib_ids) if lib_ids else ()
    ).fetchall()
    for sr in all_series:
        books_in_series = db.execute(
            "SELECT b.id, b.status FROM books b "
            "JOIN book_series bs ON bs.book_id = b.id "
            "WHERE bs.series_id = ?", (sr["id"],)
        ).fetchall()
        total_in_series = len(books_in_series)
        if total_in_series == 0:
            continue
        finished_in_series = sum(1 for bk in books_in_series
                                  if db.execute("SELECT 1 FROM readings WHERE book_id = ? AND status = 'finished' LIMIT 1",
                                                (bk["id"],)).fetchone())
        series_progress.append({
            "name": sr["name"],
            "id": sr["id"],
            "total": total_in_series,
            "finished": finished_in_series,
            "pct": round(finished_in_series / total_in_series * 100) if total_in_series > 0 else 0,
        })
    series_progress.sort(key=lambda s: (s["pct"] == 100, -s["pct"], s["name"]))
    series_progress = series_progress[:8]

    # ── TBR (not-started) pile ───────────────────────────────────────────
    tbr_books = db.execute(
        f"SELECT id, name, has_cover, cover_hash, author FROM books "
        f"WHERE {lf} AND status = 'not-started' AND (work_id IS NULL OR is_primary_edition = 1) "
        f"ORDER BY RANDOM() LIMIT 15", lp
    ).fetchall()
    tbr_list = [{"id": b["id"], "name": b["name"], "author": b["author"] or "",
                 "has_cover": bool(b["has_cover"]), "cover_hash": b["cover_hash"] or ""} for b in tbr_books]

    # ── Author spotlight (4 random authors) ──────────────────────────────
    author_counts: dict[str, int] = Counter()
    for bk in db.execute(
        f"SELECT author FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1) AND author IS NOT NULL AND author != ''", lp
    ).fetchall():
        for a in bk["author"].split(";"):
            a = a.strip()
            if a:
                author_counts[a] += 1
    spotlight_authors: list[dict] = []
    if author_counts:
        all_author_names = list(author_counts.keys())
        chosen = random.sample(all_author_names, min(4, len(all_author_names)))
        for author_name in chosen:
            author_row = db.execute("SELECT name, has_photo, photo_hash FROM authors WHERE name = ?",
                                     (author_name,)).fetchone()
            spotlight_authors.append({
                "name": author_name,
                "count": author_counts[author_name],
                "has_photo": bool(author_row["has_photo"]) if author_row else False,
                "photo_hash": (author_row["photo_hash"] or "") if author_row else "",
            })

    # ── Language diversity ───────────────────────────────────────────────
    language_counts: dict[str, int] = Counter()
    for bk in db.execute(
        f"SELECT language FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1) AND language IS NOT NULL AND language != ''", lp
    ).fetchall():
        language_counts[bk["language"]] += 1

    # ── Library health nudges ────────────────────────────────────────────
    books_without_cover = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND (has_cover IS NULL OR has_cover = 0)", lp
    ).fetchone()[0]
    finished_unrated = db.execute(
        f"SELECT COUNT(DISTINCT b.id) FROM books b "
        f"JOIN readings r ON r.book_id = b.id "
        f"LEFT JOIN ratings rt ON rt.book_id = b.id "
        f"WHERE r.status = 'finished' AND {lf_b} AND rt.book_id IS NULL", lp_b
    ).fetchone()[0]
    authors_without_photo = db.execute(
        "SELECT COUNT(*) FROM authors WHERE (has_photo IS NULL OR has_photo = 0) AND name != 'Anonymous'"
    ).fetchone()[0]
    books_without_tags = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND (tags IS NULL OR tags = '') "
        f"AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchone()[0]
    abandoned_count = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND status = 'abandoned' "
        f"AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchone()[0]
    books_without_pages = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND (pages IS NULL OR pages = 0) "
        f"AND format NOT IN ('audiobook') AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchone()[0]
    books_without_summary = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND (summary IS NULL OR summary = '') "
        f"AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchone()[0]
    books_without_author = db.execute(
        f"SELECT COUNT(*) FROM books WHERE {lf} AND (author IS NULL OR author = '') "
        f"AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchone()[0]

    # ── Word of the Day (per language) & Quote of the Day ────────────────
    word_of_the_day: dict[str, dict] = {}
    for lang_row in db.execute(
        f"SELECT DISTINCT b.language FROM words w "
        f"JOIN books b ON b.id = w.book_id "
        f"WHERE {lf_b} AND b.language IS NOT NULL AND b.language != ''", lp_b
    ).fetchall():
        lang = lang_row["language"]
        row = db.execute(
            f"SELECT w.word, w.definition, b.name AS book_name, b.id AS book_id "
            f"FROM words w JOIN books b ON b.id = w.book_id "
            f"WHERE {lf_b} AND b.language = ? ORDER BY RANDOM() LIMIT 1",
            (*lp_b, lang),
        ).fetchone()
        if row:
            word_of_the_day[lang] = dict(row)

    quote_of_the_day = None
    qotd_row = db.execute(
        f"SELECT q.text, q.page, b.name AS book_name, b.author, b.id AS book_id, b.language "
        f"FROM quotes q JOIN books b ON b.id = q.book_id "
        f"WHERE {lf_b} ORDER BY RANDOM() LIMIT 1", lp_b
    ).fetchone()
    if qotd_row:
        quote_of_the_day = dict(qotd_row)

    return render_template(
        "dashboard.html",
        # Hero ribbon
        total_books=total_books_count,
        total_library_pages=total_library_pages,
        total_library_time=total_library_time,
        total_library_time_hms=total_library_time_hms,
        unique_authors=len(unique_authors),
        finished_count=finished_count,
        reading_count=reading_count,
        not_started_count=not_started_count,
        owned_count=owned_count,
        avg_rating=avg_rating,
        # Currently reading
        reading_books=reading_books,
        # Daily data for JS (streaks, heatmap)
        daily_data=daily_data,
        # This year
        current_year=current_year,
        books_finished_this_year=books_finished_this_year,
        pages_this_year=pages_this_year,
        time_this_year=_format_duration_long(time_this_year),
        yoy_diff=yoy_diff,
        # Recent activity
        recent_activity=recent_activity,
        # Last books owned
        last_books_owned=last_books_owned,
        # Top rated
        top_rated=top_rated,
        # Records
        highest_rated_book=highest_rated_book,
        longest_finished=longest_finished,
        shortest_finished=shortest_finished,
        most_reread=most_reread,
        # Format & source
        format_counts=dict(format_counts),
        source_counts=dict(source_counts),
        # Tags
        top_tags=top_tags,
        # Series
        series_progress=series_progress,
        # TBR
        tbr_list=tbr_list,
        # Author spotlight
        spotlight_authors=spotlight_authors,
        # Language
        language_counts=dict(language_counts),
        # Library health
        books_without_cover=books_without_cover,
        finished_unrated=finished_unrated,
        authors_without_photo=authors_without_photo,
        books_without_tags=books_without_tags,
        abandoned_count=abandoned_count,
        books_without_pages=books_without_pages,
        books_without_summary=books_without_summary,
        books_without_author=books_without_author,
        # YoY pages/time
        yoy_pages_diff=yoy_pages_diff,
        yoy_time_diff=yoy_time_diff,
        yoy_time_diff_fmt=_format_duration_long(abs(yoy_time_diff)),
        # Spotlights
        word_of_the_day=word_of_the_day,
        quote_of_the_day=quote_of_the_day,
    )


@app.route("/library")
def index():
    """Library page – list all books in the current library."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    # Use query params if present, otherwise fall back to cookie, then default
    sort1 = request.args.get("sort1") or request.cookies.get("librarium_sort1", "status")
    sort2 = request.args.get("sort2") or request.cookies.get("librarium_sort2", "last_session")
    status_filter = request.args.get("status_filter") or request.cookies.get("librarium_status_filter", "all")
    show_editions = request.args.get("show_editions") or request.cookies.get("librarium_show_editions", "0")
    show_readings = request.args.get("show_readings") or request.cookies.get("librarium_show_readings", "0")
    tag_filter = request.args.get("tag", "").strip()
    if show_editions != "1":
        show_readings = "0"

    if show_readings == "1":
        books = _build_index_per_reading(db, lib_ids)
    else:
        lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
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
            b.has_cover,
            b.cover_hash,
            b.publisher,
            b.language,
            b.publication_date,
            b.work_id,
            b.format,
            b.total_time_seconds,
            b.tags,
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
        WHERE {lf_b}{edition_filter}
    """, lp_b).fetchall()

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
                "tags": r["tags"] or "",
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

    if status_filter and status_filter != "all":
        books = [b for b in books if b["status"] == status_filter]

    if tag_filter:
        tag_lower = tag_filter.lower()
        books = [b for b in books if tag_lower in [t.strip().lower() for t in b.get("tags", "").split(";") if t.strip()]]

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
        show_editions=show_editions,
        show_readings=show_readings,
        tag_filter=tag_filter,
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


def _compute_status_timeline(db, lib_ids):
    """Compute book-status counts over time for a library.

    Returns ``{"dates": [...], "series": {"reading": [...], ...}}``.
    Each *work* (group of editions sharing a ``work_id``) or standalone
    book is counted once.  The representative row is the primary edition
    (or the standalone book itself), but readings from **all** editions
    of a work contribute date information so that reading data on
    secondary editions is not lost.

    Transitions on the same date are ordered so that "reading" is always
    processed before terminal statuses ("finished" / "abandoned"),
    preventing alphabetical sort from leaving a book stuck as "reading"
    when a single session covers both start and end.
    """
    from datetime import date as _date, timedelta

    today = _date.today()
    today_s = today.isoformat()
    lf, lp = _lib_filter(lib_ids)
    STATUSES = ["reading", "finished", "not-started", "abandoned", "draft"]
    # Sort key: lower = processed first on the same date
    _STATUS_ORDER = {"not-started": 0, "draft": 0, "reading": 1, "finished": 2, "abandoned": 2}

    # ── 1. Representative books (primary or standalone) ──────────────────
    books = db.execute(
        "SELECT id, status, purchase_date, borrowed_start, work_id "
        f"FROM books WHERE {lf} "
        "AND (work_id IS NULL OR is_primary_edition = 1)",
        lp,
    ).fetchall()
    if not books:
        return {"dates": [], "series": {s: [] for s in STATUSES}}

    book_map = {b["id"]: dict(b) for b in books}

    # ── 2. For works, find ALL edition IDs (including secondary) ─────────
    work_ids = [b["work_id"] for b in books if b["work_id"]]
    # Map: representative_bid → list of all edition book_ids
    editions_map: dict[str, list[str]] = {}
    if work_ids:
        wph = ",".join("?" * len(work_ids))
        for row in db.execute(
            f"SELECT id, work_id FROM books WHERE work_id IN ({wph})",
            work_ids,
        ).fetchall():
            # Find the representative (primary) for this work
            for bid, bk in book_map.items():
                if bk.get("work_id") == row["work_id"]:
                    editions_map.setdefault(bid, []).append(row["id"])
                    break
    # Standalone books map to themselves
    for bid in book_map:
        if bid not in editions_map:
            editions_map[bid] = [bid]

    # All book IDs we need readings for (including secondary editions)
    all_edition_ids = []
    for elist in editions_map.values():
        all_edition_ids.extend(elist)
    all_edition_ids = list(set(all_edition_ids))
    aph = ",".join("?" * len(all_edition_ids))

    # ── 3. Readings grouped by representative book ───────────────────────
    readings_by_rep: dict[str, list[dict]] = {}
    if all_edition_ids:
        raw_readings = db.execute(
            f"SELECT id, book_id, reading_number, status FROM readings "
            f"WHERE book_id IN ({aph}) ORDER BY book_id, reading_number",
            all_edition_ids,
        ).fetchall()
        # Build reverse map: edition_id → representative_id
        edition_to_rep: dict[str, str] = {}
        for rep_bid, elist in editions_map.items():
            for eid in elist:
                edition_to_rep[eid] = rep_bid
        for r in raw_readings:
            rep = edition_to_rep.get(r["book_id"], r["book_id"])
            readings_by_rep.setdefault(rep, []).append(dict(r))

    all_rids = [r["id"] for rlist in readings_by_rep.values() for r in rlist]

    # ── 4. Session / period date ranges per reading ──────────────────────
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

    # ── 5. Build status-change events per representative book ────────────
    # Events are (date, sort_key, book_id, new_status) so that on the
    # same date "reading" (key 1) is processed before "finished" (key 2).
    events: list[tuple[str, int, str, str]] = []

    for bid, bk in book_map.items():
        rlist = readings_by_rep.get(bid, [])
        entry = bk["purchase_date"] or bk["borrowed_start"] or ""

        transitions: list[tuple[str, int, str]] = []  # (date, order, status)
        first_start: str | None = None

        for r in rlist:
            rid = r["id"]
            ds = [d for d in (*sess_range.get(rid, ()), *per_range.get(rid, ())) if d]
            if not ds:
                continue
            start, end = min(ds), max(ds)
            if first_start is None or start < first_start:
                first_start = start
            transitions.append((start, _STATUS_ORDER.get("reading", 1), "reading"))
            if r["status"] in ("finished", "abandoned"):
                transitions.append((end, _STATUS_ORDER.get(r["status"], 2), r["status"]))

        if not transitions:
            st = bk["status"] or "not-started"
            transitions.append((entry or today_s, _STATUS_ORDER.get(st, 0), st))
        elif entry and first_start and entry < first_start:
            initial = "draft" if bk["status"] == "draft" else "not-started"
            transitions.insert(0, (entry, _STATUS_ORDER.get(initial, 0), initial))

        transitions.sort()
        for d, _ord, s in transitions:
            events.append((d, _ord, bid, s))

        # Ensure the final state matches the book's actual current status.
        # Reading data from secondary editions can leave the timeline in a
        # state that doesn't match the primary edition's status field.
        actual_st = bk["status"] or "not-started"
        last_st = transitions[-1][2] if transitions else actual_st
        if last_st != actual_st:
            events.append((today_s, _STATUS_ORDER.get(actual_st, 0), bid, actual_st))

    events.sort()
    if not events:
        return {"dates": [], "series": {s: [] for s in STATUSES}}

    # ── 6. Walk the timeline, emitting sampled data points ───────────────
    start_date = _date.fromisoformat(events[0][0])
    total_days = (today - start_date).days + 1
    interval = max(1, total_days // 500)  # approx 500 data points

    current: dict[str, str] = {}  # bid -> status
    counts = {s: 0 for s in STATUSES}

    result_dates: list[str] = []
    result_series: dict[str, list[int]] = {s: [] for s in STATUSES}
    ei = 0
    d = start_date
    day_num = 0

    while d <= today:
        ds = d.isoformat()
        while ei < len(events) and events[ei][0] <= ds:
            _, _ord, bid, new_st = events[ei]
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")

    # Pages by year: sessions + periods
    pages_by_year: dict[str, int] = {}
    for row in db.execute(
        "SELECT SUBSTR(s.date, 1, 4) AS yr, SUM(s.pages) AS p "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date != '' AND {lf_b} GROUP BY yr", lp_b
    ).fetchall():
        pages_by_year[row["yr"]] = row["p"]
    for row in db.execute(
        f"SELECT SUBSTR(p.end_date, 1, 4) AS yr, SUM(p.pages) AS p "
        f"FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND {lf_b} GROUP BY yr", lp_b
    ).fetchall():
        pages_by_year[row["yr"]] = pages_by_year.get(row["yr"], 0) + row["p"]

    # Books finished by year – count ALL finished readings across all editions
    books_finished_by_year: dict[str, int] = {}
    finished_readings = db.execute(
        "SELECT r.id, r.book_id FROM readings r "
        "JOIN books b ON b.id = r.book_id "
        f"WHERE r.status = 'finished' AND {lf_b}", lp_b
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
        f"WHERE s.date != '' AND s.duration_seconds > 0 AND {lf_b} GROUP BY yr", lp_b
    ).fetchall():
        time_by_year[row["yr"]] = row["t"]
    for row in db.execute(
        f"SELECT SUBSTR(p.end_date, 1, 4) AS yr, SUM(p.duration_seconds) AS t "
        f"FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.duration_seconds > 0 AND {lf_b} GROUP BY yr", lp_b
    ).fetchall():
        time_by_year[row["yr"]] = time_by_year.get(row["yr"], 0) + row["t"]

    all_years = sorted(set(pages_by_year.keys()) | set(books_finished_by_year.keys()) | set(time_by_year.keys()))
    pages_data = [pages_by_year.get(y, 0) for y in all_years]
    books_data = [books_finished_by_year.get(y, 0) for y in all_years]
    time_data = [time_by_year.get(y, 0) for y in all_years]

    # ── Library Stats data ──────────────────────────────────────────────
    all_lib_books = db.execute(
        "SELECT id, name, status, tags, language, original_language, pages, publisher, has_cover, cover_hash "
        f"FROM books WHERE {lf} AND (work_id IS NULL OR is_primary_edition = 1)", lp
    ).fetchall()

    status_counts: dict[str, int] = Counter()
    tag_counts: dict[str, int] = Counter()
    language_counts: dict[str, int] = Counter()
    orig_lang_counts: dict[str, int] = Counter()
    publisher_counts: dict[str, int] = Counter()
    all_avg_ratings: list[float] = []   # raw avg ratings for KDE distribution chart
    author_counts: dict[str, int] = Counter()
    rated_sum = 0.0
    rated_count = 0

    for bk in all_lib_books:
        status_counts[bk["status"] or "unknown"] += 1
        if bk["tags"]:
            for t in bk["tags"].split(";"):
                t = t.strip()
                if t:
                    tag_counts[t] += 1
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

    # Top 10 authors for bar chart
    top_authors = author_counts.most_common(10)

    # Format status labels
    status_labels_map = {"reading": "Reading", "finished": "Finished", "not-started": "Not Started", "abandoned": "Abandoned", "draft": "Draft"}
    status_chart = {status_labels_map.get(k, k.title()): v for k, v in status_counts.items()}

    # Remove 'Unknown' entries from all count maps — they don't represent a real value
    def _remove_unknown(d: dict) -> dict:
        return {k: v for k, v in d.items() if str(k).strip().lower() != 'unknown' and str(k).strip() != ''}

    language_counts_clean = _remove_unknown(dict(language_counts))
    orig_lang_counts_clean = _remove_unknown(dict(orig_lang_counts))
    publisher_counts_clean = _remove_unknown(dict(publisher_counts))
    author_counts_clean = _remove_unknown(dict(author_counts))
    status_chart_clean = {k: v for k, v in status_chart.items() if str(k).strip().lower() != 'unknown'}

    tag_counts_clean = _remove_unknown(dict(tag_counts))

    # Prepare publisher chart data: show top N publishers and aggregate the rest as "Other" (computed from cleaned counts)
    TOP_PUBLISHERS_FOR_CHART = 20
    from collections import Counter as _Counter
    pc_counter = _Counter(publisher_counts_clean)
    top_publishers = pc_counter.most_common(TOP_PUBLISHERS_FOR_CHART)
    others_total = sum(publisher_counts_clean.values()) - sum(c for _, c in top_publishers)
    publisher_chart = {k: v for k, v in top_publishers}
    if others_total > 0:
        publisher_chart["Other"] = others_total

    # Books bought by year (based on purchase_date)
    bought_by_year: dict[str, int] = {}
    for row in db.execute(
        "SELECT SUBSTR(purchase_date, 1, 4) AS yr, COUNT(*) AS c "
        f"FROM books WHERE purchase_date != '' AND purchase_date IS NOT NULL AND {lf} "
        "GROUP BY yr ORDER BY yr", lp
    ).fetchall():
        if row["yr"] and len(row["yr"]) == 4:
            bought_by_year[row["yr"]] = row["c"]
    bought_years = sorted(bought_by_year.keys())
    bought_data = [bought_by_year.get(y, 0) for y in bought_years]

    return render_template(
        "stats.html",
        years=all_years,
        pages_data=pages_data,
        books_data=books_data,
        time_data=time_data,
        bought_years=bought_years,
        bought_data=bought_data,
        status_chart=status_chart_clean,
        tag_counts=tag_counts_clean,
        language_counts=language_counts_clean,
        orig_lang_counts=orig_lang_counts_clean,
        publisher_counts=publisher_counts_clean,
        publisher_chart=publisher_chart,
        author_counts=author_counts_clean,
        all_avg_ratings=all_avg_ratings,
        top_authors=top_authors,
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
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
            f"SELECT s.date AS d, SUM(s.pages) AS p FROM sessions s JOIN books b ON b.id = s.book_id WHERE s.date != '' AND {lf_b} GROUP BY s.date "
            "UNION ALL "
            f"SELECT p.end_date AS d, SUM(p.pages) AS p FROM periods p JOIN books b ON b.id = p.book_id WHERE p.end_date != '' AND p.pages > 0 AND {lf_b} GROUP BY p.end_date"
            ") GROUP BY d ORDER BY d"
        )
        params = lp_b * 2

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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    return jsonify(_compute_status_timeline(db, lib_ids))


@app.route('/api/cumulative_pages_per_book')
def api_cumulative_pages_per_book():
    """Return per-book cumulative pages for a given year as JSON.

    Query params:
    - year: required, 4-digit year (e.g. 2025)

    Response: { labels: [dates], datasets: [ { book_id, label, data: [cumulative_values], total } ] }
    """
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    year = request.args.get('year')
    if not year:
        return jsonify({"error": "year query parameter required"}), 400

    q = (
        "SELECT s.book_id, d AS date, SUM(p) AS pages FROM ("
        "SELECT s.book_id, s.date AS d, s.pages AS p FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date != '' AND SUBSTR(s.date,1,4) = ? AND {lf_b} "
        "UNION ALL "
        "SELECT p.book_id, p.end_date AS d, p.pages AS p FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND SUBSTR(p.end_date,1,4) = ? AND {lf_b} "
        ") s GROUP BY s.book_id, d ORDER BY s.book_id, d"
    )
    rows = db.execute(q, (year,) + lp_b + (year,) + lp_b).fetchall()

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
            f"WHERE s.book_id = ? AND s.date != '' AND s.date < ? AND {lf_b} "
            "UNION ALL "
            "SELECT p.pages AS p FROM periods p JOIN books b ON b.id = p.book_id "
            f"WHERE p.book_id = ? AND p.end_date != '' AND p.pages > 0 AND p.end_date < ? AND {lf_b} "
            ") s"
        )
        carry = db.execute(carry_q, (bid, year_start) + lp_b + (bid, year_start) + lp_b).fetchone()
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")

    year_sessions = []
    for row in db.execute(f"""
        SELECT s.date, s.pages, s.duration_seconds, b.name AS book_name
        FROM sessions s
        JOIN books b ON b.id = s.book_id
        WHERE SUBSTR(s.date, 1, 4) = ? AND {lf_b}
        ORDER BY s.date
    """, (year,) + lp_b).fetchall():
        year_sessions.append(dict(row))

    year_periods = []
    total_period_pages = 0
    for row in db.execute(f"""
        SELECT p.start_date, p.end_date, p.pages, p.note,
               b.name AS book_name, p.book_id
        FROM periods p
        JOIN books b ON b.id = p.book_id
        WHERE SUBSTR(p.end_date, 1, 4) = ? AND {lf_b}
        ORDER BY p.end_date
    """, (year,) + lp_b).fetchall():
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

    def _ensure_gantt_entry(bid, rid, name, color, status="", subtitle="", reading_number=None, has_cover=False, cover_hash=""):
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
                "has_cover": bool(has_cover),
                "cover_hash": cover_hash or "",
                "active_dates": set(),
                "has_before": False,
                "has_after": False,
            }
        book_reading_counts.setdefault(bid, set())
        if rid:
            book_reading_counts[bid].add(rid)

    # Sessions in the current year → active dates (per reading)
    for row in db.execute(f"""
        SELECT s.date, s.book_id, s.reading_id, b.name, b.subtitle, b.cover_color, b.status,
               b.has_cover, b.cover_hash, r.reading_number
        FROM sessions s
        JOIN books b ON b.id = s.book_id
        LEFT JOIN readings r ON r.id = s.reading_id
        WHERE SUBSTR(s.date, 1, 4) = ? AND {lf_b}
    """, (year,) + lp_b).fetchall():
        bid = row["book_id"]
        rid = row["reading_id"] or "__none__"
        _ensure_gantt_entry(bid, rid, row["name"], row["cover_color"], row["status"], row["subtitle"], row["reading_number"], row["has_cover"], row["cover_hash"])
        try:
            gantt_books[(bid, rid)]["active_dates"].add(date.fromisoformat(row["date"]))
        except (ValueError, TypeError):
            pass

    # Periods overlapping the current year → expand into active dates (per reading)
    for row in db.execute(f"""
        SELECT p.start_date, p.end_date, p.book_id, p.reading_id, b.name, b.subtitle, b.cover_color, b.status,
               b.has_cover, b.cover_hash, r.reading_number
        FROM periods p
        JOIN books b ON b.id = p.book_id
        LEFT JOIN readings r ON r.id = p.reading_id
        WHERE p.end_date >= ? AND p.start_date <= ? AND {lf_b}
    """, (f"{year}-01-01", f"{year}-12-31") + lp_b).fetchall():
        bid = row["book_id"]
        rid = row["reading_id"] or "__none__"
        _ensure_gantt_entry(bid, rid, row["name"], row["cover_color"], row["status"], row["subtitle"], row["reading_number"], row["has_cover"], row["cover_hash"])
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
            "book_id": bid,
            "name": display_name,
            "subtitle": info["subtitle"],
            "color": info["color"],
            "status": info["status"],
            "has_cover": info["has_cover"],
            "cover_hash": info["cover_hash"],
            "start": start_day,
            "end": end_day,
            "segments": active_segments,
            "first_ever": first_ever or "9999-12-31",
        })

    # Sort by first-ever reading session/period, then by name
    gantt_data.sort(key=lambda g: (g["first_ever"], g["name"]))

    # ── Per-book activity summaries for gantt entries ────────────────────
    # Collect full activity events for the year, then attach per book_id
    year_events = _collect_activity_events(
        db, lf, lp, lf_b, lp_b,
        date_from=f"{year}-01-01", date_to=f"{year}-12-31",
    )
    # Group by book_id (agglutinated across the whole year)
    gantt_events: dict[str, dict] = {}
    for ev in year_events:
        bid = ev["book_id"]
        if bid not in gantt_events:
            gantt_events[bid] = {
                "pages": 0, "seconds": 0,
                "started": False, "finished": False,
                "bought": False, "borrowed": False, "gift": False,
                "source_name": "", "purchase_price": "",
            }
        g = gantt_events[bid]
        g["pages"] += ev.get("pages", 0) or 0
        g["seconds"] += ev.get("seconds", 0) or 0
        if ev.get("started"):
            g["started"] = True
        if ev.get("finished"):
            g["finished"] = True
        if ev.get("bought"):
            g["bought"] = True
            g["purchase_price"] = ev.get("purchase_price", "") or g["purchase_price"]
            g["source_name"] = ev.get("source_name", "") or g["source_name"]
        if ev.get("borrowed"):
            g["borrowed"] = True
            g["source_name"] = ev.get("source_name", "") or g["source_name"]
        if ev.get("gift"):
            g["gift"] = True
    # Attach to gantt_data
    for gd in gantt_data:
        bid = gd.get("book_id", "")
        gd["activity"] = gantt_events.get(bid, {})

    # Determine prev/next years with data
    data_years = set()
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(s.date, 1, 4) AS yr FROM sessions s "
        f"JOIN books b ON b.id = s.book_id WHERE s.date != '' AND {lf_b}", lp_b
    ).fetchall():
        data_years.add(row["yr"])
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(p.end_date, 1, 4) AS yr FROM periods p "
        f"JOIN books b ON b.id = p.book_id WHERE p.end_date != '' AND {lf_b}", lp_b
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    sort = request.args.get("sort", "date")
    if sort not in ("alpha", "author", "date", "rating"):
        sort = "date"

    finished_readings = db.execute(f"""
        SELECT r.id AS reading_id, r.book_id, r.reading_number,
               b.name, b.subtitle, b.author, b.has_cover, b.cover_hash
        FROM readings r
        JOIN books b ON b.id = r.book_id
        WHERE r.status = 'finished' AND {lf_b}
    """, lp_b).fetchall()

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


@app.route("/stats/year/<year>/bought")
def stats_year_bought(year: str):
    """Display all books bought in a specific year with location, date, and price."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    sort = request.args.get("sort", "date")
    if sort not in ("alpha", "author", "date", "price"):
        sort = "date"

    rows = db.execute(f"""
        SELECT b.id, b.name, b.subtitle, b.author, b.has_cover, b.cover_hash,
               b.purchase_date, b.purchase_price, b.source_type, b.is_gift,
               s.name AS source_name, s.location AS source_location
        FROM books b
        LEFT JOIN sources s ON s.id = b.source_id
        WHERE b.purchase_date IS NOT NULL AND b.purchase_date != ''
              AND SUBSTR(b.purchase_date, 1, 4) = ? AND {lf}
    """, (year,) + lp).fetchall()

    books_bought = []
    for row in rows:
        books_bought.append({
            "id": row["id"],
            "name": row["name"],
            "subtitle": row["subtitle"] or "",
            "author": row["author"] or "",
            "has_cover": bool(row["has_cover"]),
            "cover_hash": row["cover_hash"] or "",
            "purchase_date": row["purchase_date"],
            "purchase_price": row["purchase_price"] or "",
            "source_name": row["source_name"] or "",
            "source_location": row["source_location"] or "",
            "is_gift": bool(row["is_gift"]),
        })

    if sort == "alpha":
        books_bought.sort(key=lambda b: b["name"].lower())
    elif sort == "author":
        books_bought.sort(key=lambda b: (b["author"].lower(), b["name"].lower()))
    elif sort == "price":
        def _price_key(b):
            p = b["purchase_price"]
            if not p:
                return (1, 0.0, b["name"].lower())
            # Try to extract numeric price
            import re as _re
            m = _re.search(r"[\d,.]+", p.replace(",", "."))
            return (0, -(float(m.group()) if m else 0.0), b["name"].lower())
        books_bought.sort(key=_price_key)
    else:  # date
        books_bought.sort(key=lambda b: b["purchase_date"])

    # Determine prev/next years with purchases
    all_purchase_years = set()
    for row in db.execute(
        f"SELECT DISTINCT SUBSTR(purchase_date, 1, 4) AS yr FROM books "
        f"WHERE purchase_date IS NOT NULL AND purchase_date != '' AND {lf}", lp
    ).fetchall():
        if row["yr"] and len(row["yr"]) == 4:
            all_purchase_years.add(row["yr"])
    sorted_years = sorted(all_purchase_years)
    prev_year = None
    next_year = None
    if year in sorted_years:
        idx = sorted_years.index(year)
        if idx > 0:
            prev_year = sorted_years[idx - 1]
        if idx < len(sorted_years) - 1:
            next_year = sorted_years[idx + 1]

    return render_template("stats_year_bought.html", year=year, books=books_bought, sort=sort,
                           prev_year=prev_year, next_year=next_year)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Calendar
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/calendar")
def calendar_view():
    """Monthly calendar view with per-day activity feed."""
    import calendar as _cal

    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")

    # Determine requested month (defaults to current)
    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        if month < 1 or month > 12:
            raise ValueError
        # Clamp year to a reasonable range
        year = max(2000, min(2099, year))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    # Month boundaries
    first_day = date(year, month, 1)
    last_day_num = _cal.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)
    date_from = first_day.isoformat()
    date_to = last_day.isoformat()

    # Collect agglutinated events for the month
    events = _collect_activity_events(db, lf, lp, lf_b, lp_b,
                                      date_from=date_from, date_to=date_to)
    # Group by date
    events_by_date: dict[str, list[dict]] = {}
    for ev in events:
        events_by_date.setdefault(ev["date"], []).append(ev)

    # Build calendar grid (weeks × 7)
    cal = _cal.Calendar(firstweekday=0)  # Monday start
    weeks: list[list[dict | None]] = []
    for week in cal.monthdatescalendar(year, month):
        row: list[dict | None] = []
        for d in week:
            if d.month != month:
                row.append(None)  # outside current month
            else:
                ds = d.isoformat()
                row.append({
                    "day": d.day,
                    "date": ds,
                    "is_today": d == today,
                    "events": events_by_date.get(ds, []),
                })
        weeks.append(row)

    # Prev / next month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # Serialize events_by_date to JSON for the JS detail panel
    _events_json = json.dumps(events_by_date, ensure_ascii=False)

    # Available years for the year selector (union of all years with activity)
    avail_years: set[int] = set()
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(s.date, 1, 4) AS yr FROM sessions s "
        f"JOIN books b ON b.id = s.book_id WHERE s.date != '' AND {lf_b}", lp_b
    ).fetchall():
        try:
            avail_years.add(int(row["yr"]))
        except (ValueError, TypeError):
            pass
    for row in db.execute(
        "SELECT DISTINCT SUBSTR(p.end_date, 1, 4) AS yr FROM periods p "
        f"JOIN books b ON b.id = p.book_id WHERE p.end_date != '' AND {lf_b}", lp_b
    ).fetchall():
        try:
            avail_years.add(int(row["yr"]))
        except (ValueError, TypeError):
            pass
    for row in db.execute(
        f"SELECT DISTINCT SUBSTR(purchase_date, 1, 4) AS yr FROM books "
        f"WHERE {lf} AND purchase_date IS NOT NULL AND purchase_date != ''", lp
    ).fetchall():
        try:
            avail_years.add(int(row["yr"]))
        except (ValueError, TypeError):
            pass
    avail_years.add(today.year)
    if year not in avail_years:
        avail_years.add(year)
    available_years = sorted(avail_years)

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_name=first_day.strftime("%B"),
        weeks=weeks,
        today_str=today.isoformat(),
        today_year=today.year,
        today_month=today.month,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
        _events_json=_events_json,
        available_years=available_years,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Activity
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/activity")
def activity():
    """Activity dashboard – reading habits, trends, and streaks."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")

    # 1. Daily session aggregates (all time)
    daily_sessions: dict[str, dict] = {}
    for row in db.execute(
        "SELECT s.date, SUM(s.pages) AS pages, SUM(s.duration_seconds) AS seconds "
        "FROM sessions s JOIN books b ON b.id = s.book_id "
        f"WHERE s.date != '' AND {lf_b} GROUP BY s.date", lp_b
    ).fetchall():
        daily_sessions[row["date"]] = {"pages": row["pages"], "seconds": row["seconds"]}

    # 2. Period pages (attributed to end_date; periods have no time granularity)
    daily_periods: dict[str, int] = {}
    for row in db.execute(
        "SELECT p.end_date, SUM(p.pages) AS pages "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND {lf_b} GROUP BY p.end_date", lp_b
    ).fetchall():
        daily_periods[row["end_date"]] = row["pages"]

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
        f"JOIN books b ON b.id = s.book_id WHERE s.date != '' AND {lf_b}", lp_b
    ).fetchall():
        session_book_dates.append({"date": row["date"], "book_id": row["book_id"]})
    for row in db.execute(
        "SELECT DISTINCT p.end_date AS date, p.book_id "
        "FROM periods p JOIN books b ON b.id = p.book_id "
        f"WHERE p.end_date != '' AND p.pages > 0 AND {lf_b}", lp_b
    ).fetchall():
        session_book_dates.append({"date": row["date"], "book_id": row["book_id"]})

    # 4. Book lookup (id → {name, has_cover})
    all_books: dict[str, dict] = {}
    for row in db.execute(f"SELECT id, name, has_cover, cover_hash FROM books WHERE {lf}", lp).fetchall():
        all_books[row["id"]] = {"name": row["name"], "has_cover": bool(row["has_cover"]), "cover_hash": row["cover_hash"] or ""}

    return render_template(
        "activity.html",
        daily_data=daily_data,
        session_book_dates=session_book_dates,
        all_books=all_books,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Authors
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/authors")
def authors_list():
    """Display a list of all authors with their book counts."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    rows = db.execute(f"SELECT id, name, author, has_cover, cover_hash, status FROM books WHERE {lf}", lp).fetchall()

    # Build a map of author names that have photos → photo_hash
    author_photo_info: dict[str, str] = {}
    for ar in db.execute("SELECT name, photo_hash FROM authors WHERE has_photo = 1").fetchall():
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
            if author.lower() == "anonymous":
                continue
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    show_editions = request.args.get("show_editions") or request.cookies.get("librarium_author_show_editions", "0")
    edition_filter = " AND (work_id IS NULL OR is_primary_edition = 1)" if show_editions != "1" else ""
    rows = db.execute(
        "SELECT id, name, subtitle, author, has_cover, cover_hash, status, original_publication_date "
        f"FROM books WHERE {lf}{edition_filter}", lp
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
    author_row = db.execute("SELECT * FROM authors WHERE name = ?", (author_name,)).fetchone()
    author_info = dict(author_row) if author_row else {
        "name": author_name, "has_photo": 0, "photo_hash": "", "birth_date": "",
        "birth_place": "", "death_date": "", "death_place": "", "biography": "",
        "gender": "unknown",
    }

    # Load all quotes from this author's books
    book_ids = [b["id"] for b in books]
    author_quotes = []
    if book_ids:
        ph = ",".join("?" * len(book_ids))
        author_quotes = [dict(r) for r in db.execute(
            f"SELECT q.text, q.page, b.name AS book_name, b.id AS book_id, b.language "
            f"FROM quotes q JOIN books b ON b.id = q.book_id "
            f"WHERE q.book_id IN ({ph}) ORDER BY RANDOM()",
            book_ids,
        ).fetchall()]

    resp = make_response(render_template("author_detail.html", author=author_name,
                           books=books, author_info=author_info, sort=sort,
                           show_editions=show_editions, author_quotes=author_quotes))
    resp.set_cookie("librarium_author_show_editions", show_editions, max_age=365*24*3600, samesite="Lax")
    return resp


@app.route("/author_photo/<path:author_name>")
def author_photo(author_name: str):
    """Serve the author's photo from the database."""
    db = get_db()

    # Lightweight hash-only check for conditional requests
    etag_from_client = request.headers.get("If-None-Match", "").strip(' "')
    if etag_from_client:
        hash_row = db.execute(
            "SELECT photo_hash FROM authors WHERE name = ? AND has_photo = 1",
            (author_name,)
        ).fetchone()
        if hash_row and hash_row["photo_hash"] and hash_row["photo_hash"] == etag_from_client:
            resp = make_response("", 304)
            resp.headers["ETag"] = f'"{ hash_row["photo_hash"] }"'
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp

    row = db.execute("SELECT photo, photo_hash FROM authors WHERE name = ? AND has_photo = 1",
                     (author_name,)).fetchone()
    if not row or not row["photo"]:
        abort(404)

    photo_hash = row["photo_hash"] or hashlib.md5(row["photo"]).hexdigest()[:12]
    resp = make_response(row["photo"])
    resp.headers["Content-Type"] = "image/jpeg"
    resp.headers["ETag"] = f'"{photo_hash}"'
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


@app.route("/author_photo_thumb/<path:author_name>")
def author_photo_thumb(author_name: str):
    """Serve a thumbnail of the author's photo from the database."""
    db = get_db()

    etag_from_client = request.headers.get("If-None-Match", "").strip(' "')
    if etag_from_client:
        hash_row = db.execute(
            "SELECT photo_hash FROM authors WHERE name = ? AND has_photo = 1",
            (author_name,)
        ).fetchone()
        if hash_row and hash_row["photo_hash"] and hash_row["photo_hash"] == etag_from_client:
            resp = make_response("", 304)
            resp.headers["ETag"] = f'"{ hash_row["photo_hash"] }"'
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp

    row = db.execute(
        "SELECT photo_thumb, photo, photo_hash FROM authors WHERE name = ? AND has_photo = 1",
        (author_name,)
    ).fetchone()
    if not row or (not row["photo_thumb"] and not row["photo"]):
        abort(404)

    blob = row["photo_thumb"] or row["photo"]
    photo_hash = row["photo_hash"] or hashlib.md5(row["photo"]).hexdigest()[:12]
    resp = make_response(blob)
    resp.headers["Content-Type"] = "image/jpeg"
    resp.headers["ETag"] = f'"{photo_hash}"'
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


@app.route("/authors/<path:author_name>/edit", methods=["GET", "POST"])
def edit_author(author_name: str):
    """Edit author metadata (photo, dates, places, biography)."""
    db = get_db()

    # Ensure author row exists
    author_row = db.execute("SELECT * FROM authors WHERE name = ?", (author_name,)).fetchone()
    if not author_row:
        # Auto-create a skeleton row
        db.execute("INSERT INTO authors (name) VALUES (?)", (author_name,))
        db.commit()
        author_row = db.execute("SELECT * FROM authors WHERE name = ?", (author_name,)).fetchone()

    author_info = dict(author_row)

    if request.method == "POST":
        author_info["birth_date"] = request.form.get("birth_date", "").strip()
        author_info["birth_place"] = request.form.get("birth_place", "").strip()
        author_info["death_date"] = request.form.get("death_date", "").strip()
        author_info["death_place"] = request.form.get("death_place", "").strip()
        author_info["biography"] = sanitize_html(request.form.get("biography", "").strip())
        author_info["gender"] = request.form.get("gender", "unknown").strip()

        db.execute("""
            UPDATE authors SET
                birth_date=?, birth_place=?, death_date=?, death_place=?, biography=?, gender=?
            WHERE name=?
        """, (
            author_info["birth_date"], author_info["birth_place"],
            author_info["death_date"], author_info["death_place"],
            author_info["biography"], author_info["gender"], author_name,
        ))
        db.commit()

        # Handle photo upload
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            photo_blob = photo_file.read()
            photo_hash = hashlib.md5(photo_blob).hexdigest()[:12]
            photo_thumb = _generate_thumbnail(photo_blob)
            db.execute("UPDATE authors SET photo = ?, has_photo = 1, photo_hash = ?, photo_thumb = ? WHERE name = ?",
                       (photo_blob, photo_hash, photo_thumb, author_name))
            db.commit()

        # Handle photo removal
        if request.form.get("remove_photo") == "1":
            db.execute("UPDATE authors SET photo = NULL, has_photo = 0, photo_hash = '', photo_thumb = NULL WHERE name = ?",
                       (author_name,))
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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    lf_s, lp_s = _lib_filter(lib_ids, "s.library_id")

    rows = db.execute(f"""
        SELECT s.id, s.name,
               COUNT(CASE WHEN b.work_id IS NULL OR b.is_primary_edition = 1 THEN 1 END) AS book_count
        FROM series s
        LEFT JOIN book_series bs ON bs.series_id = s.id
        LEFT JOIN books b ON b.id = bs.book_id
        WHERE {lf_s}
        GROUP BY s.id
        ORDER BY s.name COLLATE NOCASE
    """, lp_s).fetchall()

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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")

    series_row = db.execute(
        f"SELECT * FROM series WHERE id = ? AND {lf}", (series_id,) + lp
    ).fetchone()
    if not series_row:
        abort(404)
    series_info = dict(series_row)

    rows = db.execute(f"""
        SELECT b.id, b.name, b.subtitle, b.author, b.has_cover, b.cover_hash, b.status,
               b.original_publication_date, bs.series_index
        FROM books b
        JOIN book_series bs ON bs.book_id = b.id
        WHERE bs.series_id = ? AND {lf_b}
              AND (b.work_id IS NULL OR b.is_primary_edition = 1)
    """, (series_id,) + lp_b).fetchall()

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
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    new_name = request.form.get("name", "").strip()
    if not new_name:
        flash("Series name cannot be empty.", "error")
        return redirect(url_for("series_detail", series_id=series_id))
    db.execute(f"UPDATE series SET name = ? WHERE id = ? AND {lf}",
               (new_name, series_id) + lp)
    db.commit()
    flash("Series renamed.", "success")
    return redirect(url_for("series_detail", series_id=series_id))


@app.route("/series/<int:series_id>/delete", methods=["POST"])
def delete_series(series_id: int):
    """Delete a series (unlinks books but doesn't delete them)."""
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    db.execute(f"""
        DELETE FROM book_series WHERE series_id = ? AND book_id IN (
            SELECT id FROM books WHERE {lf}
        )
    """, (series_id,) + lp)
    db.execute(f"DELETE FROM series WHERE id = ? AND {lf}", (series_id,) + lp)
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
        quotes=[dict(r) for r in db.execute(
            "SELECT * FROM quotes WHERE book_id = ? ORDER BY CASE WHEN page IS NULL THEN 1 ELSE 0 END, page", (book_id,)
        ).fetchall()],
        thoughts=[dict(r) for r in db.execute(
            "SELECT * FROM thoughts WHERE book_id = ? ORDER BY CASE WHEN page IS NULL THEN 1 ELSE 0 END, page", (book_id,)
        ).fetchall()],
        words=[dict(r) for r in db.execute(
            "SELECT * FROM words WHERE book_id = ? ORDER BY word COLLATE NOCASE", (book_id,)
        ).fetchall()],
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


@app.route("/cover_thumb/<book_id>")
def book_cover_thumb(book_id: str):
    """Serve a thumbnail version of a book cover (300 px wide)."""
    db = get_db()

    etag_from_client = request.headers.get("If-None-Match", "").strip(' "')
    if etag_from_client:
        hash_row = db.execute(
            "SELECT cover_hash FROM books WHERE id = ? AND has_cover = 1", (book_id,)
        ).fetchone()
        if hash_row and hash_row["cover_hash"] and ("t-" + hash_row["cover_hash"]) == etag_from_client:
            resp = make_response("", 304)
            resp.headers["ETag"] = f'"t-{hash_row["cover_hash"]}"'
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp

    row = db.execute(
        "SELECT cover_thumb, cover, cover_hash FROM books WHERE id = ? AND has_cover = 1",
        (book_id,),
    ).fetchone()
    if not row:
        abort(404)

    blob = row["cover_thumb"] or row["cover"]
    if not blob:
        abort(404)
    cover_hash = row["cover_hash"] or ""
    resp = make_response(blob)
    resp.headers["Content-Type"] = "image/jpeg"
    resp.headers["ETag"] = f'"t-{cover_hash}"'
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
# Routes – Annotation CRUD (Quotes, Thoughts, Words)
# ═══════════════════════════════════════════════════════════════════════════

# ── Quotes ──

@app.route("/book/<book_id>/quotes/add", methods=["POST"])
def add_quote(book_id: str):
    db = get_db()
    if not db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone():
        abort(404)
    text = sanitize_html(request.form.get("text", "").strip())
    page_str = request.form.get("page", "").strip()
    page = int(page_str) if page_str else None
    if text:
        db.execute("INSERT INTO quotes (book_id, text, page) VALUES (?, ?, ?)",
                   (book_id, text, page))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="quotes"))


@app.route("/book/<book_id>/quotes/<int:qid>/edit", methods=["POST"])
def edit_quote(book_id: str, qid: int):
    db = get_db()
    text = sanitize_html(request.form.get("text", "").strip())
    page_str = request.form.get("page", "").strip()
    page = int(page_str) if page_str else None
    if text:
        db.execute("UPDATE quotes SET text = ?, page = ? WHERE id = ? AND book_id = ?",
                   (text, page, qid, book_id))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="quotes"))


@app.route("/book/<book_id>/quotes/<int:qid>/delete", methods=["POST"])
def delete_quote(book_id: str, qid: int):
    db = get_db()
    db.execute("DELETE FROM quotes WHERE id = ? AND book_id = ?", (qid, book_id))
    db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="quotes"))


# ── Thoughts ──

@app.route("/book/<book_id>/thoughts/add", methods=["POST"])
def add_thought(book_id: str):
    db = get_db()
    if not db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone():
        abort(404)
    text = sanitize_html(request.form.get("text", "").strip())
    page_str = request.form.get("page", "").strip()
    page = int(page_str) if page_str else None
    if text:
        db.execute("INSERT INTO thoughts (book_id, text, page) VALUES (?, ?, ?)",
                   (book_id, text, page))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="thoughts"))


@app.route("/book/<book_id>/thoughts/<int:tid>/edit", methods=["POST"])
def edit_thought(book_id: str, tid: int):
    db = get_db()
    text = sanitize_html(request.form.get("text", "").strip())
    page_str = request.form.get("page", "").strip()
    page = int(page_str) if page_str else None
    if text:
        db.execute("UPDATE thoughts SET text = ?, page = ? WHERE id = ? AND book_id = ?",
                   (text, page, tid, book_id))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="thoughts"))


@app.route("/book/<book_id>/thoughts/<int:tid>/delete", methods=["POST"])
def delete_thought(book_id: str, tid: int):
    db = get_db()
    db.execute("DELETE FROM thoughts WHERE id = ? AND book_id = ?", (tid, book_id))
    db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="thoughts"))


# ── Words ──

@app.route("/book/<book_id>/words/add", methods=["POST"])
def add_word(book_id: str):
    db = get_db()
    if not db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone():
        abort(404)
    word = request.form.get("word", "").strip()
    definition = sanitize_html(request.form.get("definition", "").strip())
    if word:
        db.execute("INSERT INTO words (book_id, word, definition) VALUES (?, ?, ?)",
                   (book_id, word, definition))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="words"))


@app.route("/book/<book_id>/words/<int:wid>/edit", methods=["POST"])
def edit_word(book_id: str, wid: int):
    db = get_db()
    word = request.form.get("word", "").strip()
    definition = sanitize_html(request.form.get("definition", "").strip())
    if word:
        db.execute("UPDATE words SET word = ?, definition = ? WHERE id = ? AND book_id = ?",
                   (word, definition, wid, book_id))
        db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="words"))


@app.route("/book/<book_id>/words/<int:wid>/delete", methods=["POST"])
def delete_word(book_id: str, wid: int):
    db = get_db()
    db.execute("DELETE FROM words WHERE id = ? AND book_id = ?", (wid, book_id))
    db.commit()
    return redirect(url_for("book_detail", book_id=book_id, _anchor="words"))


# ── Bookly PDF Import ──

def _parse_bookly_pdf(pdf_bytes: bytes) -> dict:
    """Parse a Bookly summary PDF and extract quotes, thoughts, and words."""
    import pdfplumber
    result: dict = {"quotes": [], "thoughts": [], "words": []}

    pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text(layout=True)
        if text:
            full_text += text + "\n"
    pdf.close()

    # Collapse lines: join continuation lines (those not starting with p.\d+ •)
    lines = full_text.split("\n")
    clean_lines: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            clean_lines.append("")
            continue
        clean_lines.append(stripped)

    text_block = "\n".join(clean_lines)

    # Find sections by headers
    import re
    thoughts_header = re.search(r"My\s+thoughts\s+about\s+this\s+book", text_block, re.IGNORECASE)
    quotes_header = re.search(r"Quotes\s+I\s+liked\s+the\s+most", text_block, re.IGNORECASE)
    words_header = re.search(r"New\s+words\s+I\s+learned", text_block, re.IGNORECASE)

    # Determine section boundaries
    headers = []
    if thoughts_header:
        headers.append(("thoughts", thoughts_header.start()))
    if quotes_header:
        headers.append(("quotes", quotes_header.start()))
    if words_header:
        headers.append(("words", words_header.start()))
    headers.sort(key=lambda x: x[1])

    sections: dict[str, str] = {}
    for i, (name, start) in enumerate(headers):
        # Find end of header line
        header_end = text_block.index("\n", start) if "\n" in text_block[start:] else len(text_block)
        # Section content goes until next section or end
        if i + 1 < len(headers):
            end = headers[i + 1][1]
        else:
            end = len(text_block)
        sections[name] = text_block[header_end:end].strip()

    # Parse thoughts and quotes (same format: p.NUMBER • text)
    page_entry_re = re.compile(r"p\.(\d+)\s*[•·]\s*")
    # Quotation marks to strip from beginning/end of extracted quotes
    _quote_marks = '\'\"«»""''‹›„‟‚‛「」『』'

    for section_name in ("thoughts", "quotes"):
        if section_name not in sections:
            continue
        section_text = sections[section_name]
        entries: list[dict] = []

        # Split by p.NUMBER • pattern
        parts = page_entry_re.split(section_text)
        # parts = [pre_text, page1, text1, page2, text2, ...]
        if len(parts) >= 3:
            for j in range(1, len(parts), 2):
                page_num = int(parts[j])
                entry_text = parts[j + 1].strip() if j + 1 < len(parts) else ""
                # Clean up: remove excessive whitespace from PDF extraction
                entry_text = re.sub(r"\s+", " ", entry_text).strip()
                # Strip leading/trailing quotation marks (Bookly wraps quotes)
                if section_name == "quotes":
                    entry_text = entry_text.strip(_quote_marks).strip()
                if entry_text:
                    entries.append({"text": entry_text, "page": page_num})

        result[section_name] = entries

    # Parse words section
    if "words" in sections:
        section_text = sections["words"]
        word_lines = section_text.split("\n")

        current_word = None
        current_def_lines: list[str] = []

        for line in word_lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Heuristic: a word line is short (typically 1-3 words),
            # starts lowercase, and doesn't look like a definition continuation.
            # Definition lines often start with a number+period (Spanish dict style),
            # an article, uppercase, or "Definition:".
            is_likely_word = (
                len(stripped.split()) <= 4
                and not re.match(r"^\d+\.", stripped)
                and not stripped.startswith("Definition:")
                and not stripped.startswith("Sin.:")
                and len(stripped) < 50
                and not re.match(r"^(a |an |the |to )", stripped, re.IGNORECASE)
                and stripped[0].islower()
            )

            if is_likely_word and current_word is not None:
                # Save previous word
                definition = " ".join(current_def_lines).strip()
                definition = re.sub(r"\s+", " ", definition)
                if definition:
                    result["words"].append({"word": current_word, "definition": definition})
                current_word = stripped
                current_def_lines = []
            elif is_likely_word and current_word is None:
                current_word = stripped
                current_def_lines = []
            else:
                if current_word is not None:
                    current_def_lines.append(stripped)

        # Don't forget the last word
        if current_word is not None:
            definition = " ".join(current_def_lines).strip()
            definition = re.sub(r"\s+", " ", definition)
            if definition:
                result["words"].append({"word": current_word, "definition": definition})

    return result


@app.route("/book/<book_id>/import-bookly", methods=["POST"])
def import_bookly(book_id: str):
    db = get_db()
    book = db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)

    pdf_file = request.files.get("bookly_pdf")
    if not pdf_file or not pdf_file.filename:
        flash("No PDF file selected.", "error")
        return redirect(url_for("edit_metadata", book_id=book_id))

    clear_existing = request.form.get("clear_existing") == "1"

    try:
        pdf_bytes = pdf_file.read()
        parsed = _parse_bookly_pdf(pdf_bytes)
    except Exception as e:
        flash(f"Failed to parse Bookly PDF: {e}", "error")
        return redirect(url_for("edit_metadata", book_id=book_id))

    if clear_existing:
        db.execute("DELETE FROM quotes WHERE book_id = ?", (book_id,))
        db.execute("DELETE FROM thoughts WHERE book_id = ?", (book_id,))
        db.execute("DELETE FROM words WHERE book_id = ?", (book_id,))

    for q in parsed["quotes"]:
        db.execute("INSERT INTO quotes (book_id, text, page) VALUES (?, ?, ?)",
                   (book_id, q["text"], q.get("page")))
    for t in parsed["thoughts"]:
        db.execute("INSERT INTO thoughts (book_id, text, page) VALUES (?, ?, ?)",
                   (book_id, t["text"], t.get("page")))
    for w in parsed["words"]:
        db.execute("INSERT INTO words (book_id, word, definition) VALUES (?, ?, ?)",
                   (book_id, w["word"], w["definition"]))
    db.commit()

    counts = f"{len(parsed['quotes'])} quotes, {len(parsed['thoughts'])} thoughts, {len(parsed['words'])} words"
    flash(f"Bookly import complete: {counts}.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Metadata editing
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/<book_id>/edit", methods=["GET", "POST"])
def edit_metadata(book_id: str):
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        abort(404)
    info = dict(book)

    if request.method == "POST":
        text_fields = (
            "name", "subtitle", "author", "language", "original_title",
            "original_language", "original_publication_date",
            "publication_date", "isbn", "publisher", "tags",
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
        # Library move
        new_lib_id = request.form.get("library_id", "").strip()
        if new_lib_id and new_lib_id.isdigit():
            info["library_id"] = int(new_lib_id)
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
                f"SELECT id FROM series WHERE name = ? AND {lf}",
                (s_name,) + lp
            ).fetchone()
            if existing:
                sid = existing["id"]
            else:
                db.execute("INSERT INTO series (name, library_id) VALUES (?, ?)",
                           (s_name, info["library_id"]))
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
                publisher=?, tags=?, summary=?, translator=?, illustrator=?,
                editor=?, prologue_author=?, status=?,
                source_type=?, source_id=?, purchase_date=?, purchase_price=?,
                borrowed_start=?, borrowed_end=?, is_gift=?,
                format=?, binding=?, audio_format=?, total_time_seconds=?,
                library_id=?
            WHERE id=?
        """, (
            info["name"], info["subtitle"], info["author"], _slugify(info["name"]),
            info["language"], info["original_title"],
            info["original_language"], info["original_publication_date"],
            info["publication_date"], info["isbn"],
            info["pages"], info["starting_page"],
            info["publisher"], info["tags"], info["summary"],
            info["translator"], info["illustrator"],
            info["editor"], info["prologue_author"], info["status"],
            info["source_type"], info["source_id"],
            info["purchase_date"], info["purchase_price"],
            info["borrowed_start"], info["borrowed_end"],
            info["is_gift"],
            info["format"], info["binding"], info["audio_format"],
            info["total_time_seconds"],
            info["library_id"],
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
            cover_thumb = _generate_thumbnail(cover_blob)
            db.execute(
                "UPDATE books SET cover = ?, has_cover = 1, cover_color = ?, cover_palette = ?, cover_hash = ?, cover_thumb = ? WHERE id = ?",
                (cover_blob, cover_color, json.dumps(palette), cover_hash, cover_thumb, book_id),
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

    sources = db.execute("SELECT * FROM sources ORDER BY name").fetchall()
    sources = [dict(s) for s in sources]
    purchase_sources = [s for s in sources if s["type"] in PURCHASE_SOURCE_TYPES]
    borrow_sources = [s for s in sources if s["type"] in BORROW_SOURCE_TYPES]
    gift_sources = [s for s in sources if s["type"] in GIFT_SOURCE_TYPES]
    languages = _collect_languages()
    suggestions = _collect_field_values(
        "author", "tags", "publisher",
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
        f"SELECT id, name FROM series WHERE {lf} ORDER BY name COLLATE NOCASE", lp
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
# Routes – ISBN lookup
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/isbn_lookup")
def isbn_lookup():
    """Look up book data by ISBN using the Open Library API."""
    original_isbn = request.args.get("isbn", "").strip()
    isbn = re.sub(r"[^0-9Xx]", "", original_isbn)
    if not isbn:
        return jsonify({"error": "No ISBN provided"}), 400

    # Try Open Library Books API
    ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        req = urllib.request.Request(ol_url, headers={"User-Agent": "Librarium/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return jsonify({"error": "Failed to reach Open Library"}), 502

    key = f"ISBN:{isbn}"
    if key not in data:
        return jsonify({"error": "ISBN not found"}), 404

    book = data[key]
    authors = "; ".join(a.get("name", "") for a in book.get("authors", []))
    publishers = ", ".join(p.get("name", "") for p in book.get("publishers", []))
    subjects = ", ".join(s.get("name", "") for s in book.get("subjects", [])[:5])
    pages = book.get("number_of_pages", 0)
    pub_date = book.get("publish_date", "")

    # Try to get cover image URL (large → medium → small)
    cover_url = ""
    cover = book.get("cover", {})
    cover_url = cover.get("large") or cover.get("medium") or cover.get("small") or ""

    result = {
        "title": book.get("title", ""),
        "subtitle": book.get("subtitle", ""),
        "author": authors,
        "publisher": publishers,
        "pages": pages,
        "isbn": original_isbn,
        "publication_date": pub_date,
        "tags": subjects,
        "cover_url": cover_url,
    }
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Add new book
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/book/new", methods=["GET", "POST"])
def new_book():
    db = get_db()
    lib_ids = _get_selected_library_ids()
    lf, lp = _lib_filter(lib_ids)
    lf_b, lp_b = _lib_filter(lib_ids, "b.library_id")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        author = request.form.get("author", "").strip()
        # Determine target library for the new book
        form_lib = request.form.get("library_id", "").strip()
        active_lib = int(form_lib) if form_lib and form_lib.isdigit() else (lib_ids[0] if lib_ids else 1)
        if not name:
            flash("Book name is required.", "error")
            return redirect(url_for("new_book"))

        book_id = str(uuid_module.uuid4())

        info: dict = {}
        for field in (
            "name", "subtitle", "author", "language", "original_title",
            "original_language", "original_publication_date",
            "publication_date", "isbn", "publisher", "tags",
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
        cover_thumb = None
        cover_file = request.files.get("cover")
        if cover_file and cover_file.filename:
            cover_blob = cover_file.read()
            has_cover = 1
            palette = _extract_cover_palette(cover_blob)
            cover_color = palette[0] if palette else "#888888"
            cover_palette_json = json.dumps(palette)
            cover_hash = hashlib.md5(cover_blob).hexdigest()[:12]
            cover_thumb = _generate_thumbnail(cover_blob)
        elif request.form.get("cover_url"):
            # Download cover from URL (ISBN lookup)
            try:
                cover_req = urllib.request.Request(
                    request.form["cover_url"],
                    headers={"User-Agent": "Librarium/1.0"},
                )
                with urllib.request.urlopen(cover_req, timeout=15) as cresp:
                    cover_blob = cresp.read()
                if cover_blob:
                    has_cover = 1
                    palette = _extract_cover_palette(cover_blob)
                    cover_color = palette[0] if palette else "#888888"
                    cover_palette_json = json.dumps(palette)
                    cover_hash = hashlib.md5(cover_blob).hexdigest()[:12]
                    cover_thumb = _generate_thumbnail(cover_blob)
            except (urllib.error.URLError, OSError):
                pass  # Cover download failed — continue without cover

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
             publisher, tags, summary, translator, illustrator, editor, prologue_author,
             status, source_type, source_id, purchase_date, purchase_price,
             borrowed_start, borrowed_end, is_gift, has_cover, cover, cover_color, cover_palette, cover_hash,
             cover_thumb, library_id, work_id, is_primary_edition,
             format, binding, audio_format, total_time_seconds)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            book_id, info["name"], info["subtitle"], info["author"], _slugify(info["name"]),
            info["language"], info["original_title"],
            info["original_language"], info["original_publication_date"],
            info["publication_date"], info["isbn"],
            info["pages"], info["starting_page"],
            info["publisher"], info["tags"], info["summary"],
            info["translator"], info["illustrator"],
            info["editor"], info["prologue_author"], info["status"],
            info["source_type"], info["source_id"],
            info["purchase_date"], info["purchase_price"],
            info["borrowed_start"], info["borrowed_end"],
            info["is_gift"],
            has_cover, cover_blob, cover_color, cover_palette_json, cover_hash,
            cover_thumb, active_lib, link_work_id or None, is_primary,
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
                f"SELECT id FROM series WHERE name = ? AND {lf}",
                (s_name,) + lp
            ).fetchone()
            if existing:
                sid = existing["id"]
            else:
                db.execute("INSERT INTO series (name, library_id) VALUES (?, ?)",
                           (s_name, active_lib))
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

    sources = db.execute("SELECT * FROM sources ORDER BY name").fetchall()
    sources = [dict(s) for s in sources]
    purchase_sources = [s for s in sources if s["type"] in PURCHASE_SOURCE_TYPES]
    borrow_sources = [s for s in sources if s["type"] in BORROW_SOURCE_TYPES]
    gift_sources = [s for s in sources if s["type"] in GIFT_SOURCE_TYPES]
    languages = _collect_languages()
    suggestions = _collect_field_values(
        "author", "tags", "publisher",
        "translator", "illustrator", "editor", "prologue_author",
    )
    all_series = [dict(r) for r in db.execute(
        f"SELECT id, name FROM series WHERE {lf} ORDER BY name COLLATE NOCASE", lp
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
                      "original_publication_date", "tags", "summary",
                      "illustrator", "editor", "prologue_author"):
                prefill[f] = primary.get(f, "")

    # Pre-fill from ISBN lookup (query params)
    for key in ("name", "subtitle", "author", "publisher", "isbn",
                "publication_date", "tags", "pages", "cover_url"):
        val = request.args.get(key, "").strip()
        if val and key not in prefill:
            prefill[key] = val

    return render_template("new_book.html",
                           purchase_sources=purchase_sources, borrow_sources=borrow_sources,
                           gift_sources=gift_sources,
                           languages=languages, suggestions=suggestions,
                           all_series=all_series,
                           prefill=prefill,
                           parent_work_id=parent_work_id,
                           parent_book_name=parent_book_name,
                           default_library_id=lib_ids[0] if lib_ids else 1)


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Sources
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/sources")
def sources_list():
    """Sources management page."""
    db = get_db()
    sources = [dict(r) for r in db.execute("SELECT * FROM sources ORDER BY name").fetchall()]
    return render_template("sources.html", sources=sources, source_types=SOURCE_TYPES)


@app.route("/sources/add", methods=["POST"])
def add_source():
    db = get_db()
    name = request.form.get("name", "").strip()
    short_name = request.form.get("short_name", "").strip()
    if not name:
        flash("Source name is required.", "error")
        return redirect(url_for("sources_list"))

    db.execute(
        "INSERT INTO sources (id, type, name, short_name, location, url, notes) VALUES (?,?,?,?,?,?,?)",
        (
            str(uuid_module.uuid4()),
            request.form.get("source_type", "").strip(),
            name,
            short_name or name,
            request.form.get("location", "").strip(),
            request.form.get("url", "").strip(),
            request.form.get("notes", "").strip(),
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
    """Update selected libraries (comma-separated IDs in cookie)."""
    raw = request.form.get("library_ids", "")
    db = get_db()
    all_ids = {r["id"] for r in db.execute("SELECT id FROM libraries").fetchall()}
    selected: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        try:
            lid = int(part)
            if lid in all_ids:
                selected.append(lid)
        except (ValueError, TypeError):
            pass
    # Empty string = all libraries selected
    cookie_val = ",".join(str(i) for i in selected) if len(selected) < len(all_ids) else ""
    resp = make_response(redirect(request.referrer or url_for("index")))
    resp.set_cookie("librarium_library", cookie_val, max_age=60 * 60 * 24 * 365 * 5,
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


@app.route("/api/shutdown-backup", methods=["POST"])
def shutdown_backup():
    """Create a backup and sync to Dropbox before the Electron shell quits."""
    name = backup_database(skip_if_recent=False)
    # Sync all user DBs to Dropbox before shutdown
    if _is_authenticated():
        try:
            users_data = _load_users()
            for u in users_data["users"]:
                sync_db_to_dropbox(u["name"])
        except Exception as e:
            print(f"[dropbox] Shutdown sync failed: {e}")
    return jsonify({"ok": True, "backup": name})


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
    db.execute("DELETE FROM libraries WHERE id = ?", (lib_id,))
    db.commit()
    # Remove the deleted library from the selection cookie
    current = request.cookies.get("librarium_library", "")
    remaining_ids = [p.strip() for p in current.split(",") if p.strip() and p.strip() != str(lib_id)]
    new_cookie = ",".join(remaining_ids)
    if new_cookie != current:
        resp = make_response(redirect(request.referrer or url_for("index")))
        resp.set_cookie("librarium_library", new_cookie, max_age=60 * 60 * 24 * 365 * 5,
                         samesite="Lax", httponly=True)
        flash(f"Library '{lib_name}' deleted.", "success")
        return resp
    flash(f"Library '{lib_name}' deleted.", "success")
    return redirect(request.referrer or url_for("index"))


# ═══════════════════════════════════════════════════════════════════════════
# Routes – Dropbox authentication
# ═══════════════════════════════════════════════════════════════════════════

# Module-level state shared between the main Flask server and the
# temporary OAuth callback server running on port 48721.
_oauth_session: dict = {}        # stores CSRF + PKCE verifier across requests
_oauth_result_ready = False      # set to True once callback finishes

_CALLBACK_PORT = int(DROPBOX_REDIRECT_URI.rsplit(":", 1)[-1].split("/")[0])  # 48721


def _complete_oauth(query_params: dict) -> bool:
    """Exchange the auth code for tokens and persist auth data.

    Called from the temporary callback server.  Returns True on success.
    """
    global _oauth_result_ready
    flow = dropbox.DropboxOAuth2Flow(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret="",
        redirect_uri=DROPBOX_REDIRECT_URI,
        session=_oauth_session,
        csrf_token_session_key="dbx-csrf",
        token_access_type="offline",
        use_pkce=True,
        scope=DROPBOX_SCOPES,
    )
    # Restore the original PKCE code_verifier from the start() call
    saved_verifier = _oauth_session.pop("_pkce_verifier", None)
    if saved_verifier:
        flow.code_verifier = saved_verifier
    try:
        result = flow.finish(query_params)
    except Exception as e:
        print(f"[auth] OAuth token exchange failed: {e}")
        return False

    # Fetch account info
    dbx = dropbox.Dropbox(oauth2_access_token=result.access_token)
    try:
        account = dbx.users_get_current_account()
        display_name = account.name.display_name
        email = account.email
    except Exception:
        display_name = ""
        email = ""

    _save_auth({
        "refresh_token": result.refresh_token,
        "account_id": result.account_id,
        "display_name": display_name,
        "email": email,
    })
    _reset_dropbox_client()

    # Initial sync
    try:
        _dbx_ensure_folder("/backups")
        remote_users = _dbx_file_exists("/users.json")
        local_users = _load_users()
        if remote_users and not local_users["users"]:
            _download_all_from_dropbox()
        elif not remote_users and local_users["users"]:
            _upload_all_to_dropbox()
        elif remote_users and local_users["users"]:
            _download_all_from_dropbox()
    except Exception as e:
        print(f"[dropbox] Initial sync error: {e}")

    _start_periodic_sync()
    _oauth_result_ready = True
    return True


def _start_oauth_callback_server() -> None:
    """Start a one-shot HTTP server on port 48721 to receive the OAuth callback.

    Runs in a daemon thread.  Shuts itself down after handling one request.
    """
    import http.server
    import urllib.parse as _up

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = _up.urlparse(self.path)
            if not parsed.path.rstrip("/").endswith("/auth/callback"):
                self.send_error(404)
                return
            params = {k: v[0] for k, v in _up.parse_qs(parsed.query).items()}
            ok = _complete_oauth(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if ok:
                self.wfile.write(
                    b"<!DOCTYPE html><html><body style='font-family:sans-serif;"
                    b"text-align:center;padding:3rem'>"
                    b"<h2>Dropbox connected</h2>"
                    b"<p>You can close this tab and return to Librarium.</p>"
                    b"</body></html>"
                )
            else:
                self.wfile.write(
                    b"<!DOCTYPE html><html><body style='font-family:sans-serif;"
                    b"text-align:center;padding:3rem'>"
                    b"<h2>Authentication failed</h2>"
                    b"<p>Please close this tab and try again from Librarium.</p>"
                    b"</body></html>"
                )
            # Shut down the server after handling the callback
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, format, *args):
            print(f"[auth-callback] {args[0]}" if args else "")

    try:
        server = http.server.HTTPServer(("127.0.0.1", _CALLBACK_PORT), _Handler)
    except OSError as e:
        print(f"[auth] Cannot start callback server on port {_CALLBACK_PORT}: {e}")
        return
    t = threading.Thread(target=server.serve_forever, daemon=True, name="oauth-cb")
    t.start()
    print(f"[auth] Callback server listening on port {_CALLBACK_PORT}")


@app.route("/auth/login")
def auth_login():
    """Show the Dropbox login page."""
    return render_template("auth_login.html")


@app.route("/auth/start")
def auth_start():
    """Initiate the Dropbox OAuth2 PKCE flow.

    1. Stores PKCE / CSRF state in a module-level dict (not Flask session)
       because the callback arrives on a different port / process.
    2. Starts a temporary HTTP server on port 48721 for the callback.
    3. Opens the Dropbox auth URL in the **system browser**.
    4. Returns a waiting page to the Electron window that polls /auth/status.
    """
    global _oauth_session, _oauth_result_ready
    _oauth_session = {}
    _oauth_result_ready = False

    flow = dropbox.DropboxOAuth2Flow(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret="",
        redirect_uri=DROPBOX_REDIRECT_URI,
        session=_oauth_session,
        csrf_token_session_key="dbx-csrf",
        token_access_type="offline",
        use_pkce=True,
        scope=DROPBOX_SCOPES,
    )
    authorize_url = flow.start()

    # Persist the PKCE code_verifier so _complete_oauth can reuse it.
    # The SDK stores it on the flow object, not in the session dict.
    _oauth_session["_pkce_verifier"] = flow.code_verifier

    # Start the temporary callback server
    _start_oauth_callback_server()

    # Open the auth URL in the system browser
    import webbrowser
    webbrowser.open(authorize_url)

    # Return a waiting page to the Electron window
    return render_template("auth_waiting.html")


@app.route("/auth/callback")
def auth_callback():
    """Fallback callback for when Flask happens to be on port 48721."""
    params = dict(request.args)
    ok = _complete_oauth(params)
    if ok:
        return render_template("auth_success.html")
    return render_template("auth_login.html", error="Authentication failed. Please try again.")


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    """Revoke Dropbox token and log out."""
    try:
        dbx = get_dropbox_client()
        dbx.auth_token_revoke()
    except Exception:
        pass
    _clear_auth()
    _reset_dropbox_client()
    return redirect(url_for("auth_login"))


@app.route("/auth/status")
def auth_status():
    """JSON endpoint: is the user authenticated with Dropbox?"""
    auth = _load_auth()
    if auth:
        return jsonify({
            "authenticated": True,
            "display_name": auth.get("display_name", ""),
            "email": auth.get("email", ""),
        })
    return jsonify({"authenticated": False})


# ═══════════════════════════════════════════════════════════════════════════
# Routes – User management
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/users")
def user_select():
    """Show user selection / creation page."""
    users_data = _load_users()
    legacy_exists = (DATA_DIR / "librarium.db").exists() and not users_data["users"]
    dropbox_info = _load_auth()
    return render_template("users.html", users=users_data["users"],
                           legacy_exists=legacy_exists, dropbox_info=dropbox_info)


@app.route("/users/create", methods=["POST"])
def user_create():
    """Create a new user profile."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a name.", "error")
        return redirect(url_for("user_select"))

    slug = _sanitize_username(name)
    if not slug:
        flash("Name must contain at least one letter or number.", "error")
        return redirect(url_for("user_select"))

    users_data = _load_users()
    # Check for duplicate
    for u in users_data["users"]:
        if _sanitize_username(u["name"]) == slug:
            flash(f"A user with a similar name already exists.", "error")
            return redirect(url_for("user_select"))

    # Handle import of existing DB
    import_file = request.files.get("import_db")
    db_path = _get_user_db_path(name)

    if import_file and import_file.filename:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        import_file.save(str(db_path))
    elif request.form.get("import_legacy") == "1":
        legacy = DATA_DIR / "librarium.db"
        if legacy.exists():
            shutil.copy2(str(legacy), str(db_path))

    users_data["users"].append({"name": name, "db_file": f"{slug}.db", "backup_dir": ""})
    users_data["last_user"] = name
    _save_users(users_data)

    # Set the user cookie and run migrations for their DB
    _set_active_user_db(name)
    _run_all_migrations()

    # Upload new DB to Dropbox
    sync_db_to_dropbox(name)

    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("librarium_user", name, max_age=60 * 60 * 24 * 365 * 5,
                     samesite="Lax")
    return resp


@app.route("/users/switch", methods=["POST"])
def user_switch():
    """Switch to a different user."""
    name = request.form.get("name", "").strip()
    users_data = _load_users()

    found = False
    for u in users_data["users"]:
        if u["name"] == name:
            found = True
            break

    if not found:
        flash("User not found.", "error")
        return redirect(url_for("user_select"))

    users_data["last_user"] = name
    _save_users(users_data)
    _set_active_user_db(name)
    _run_all_migrations()

    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("librarium_user", name, max_age=60 * 60 * 24 * 365 * 5,
                     samesite="Lax")
    return resp


@app.route("/users/update-backup-dir", methods=["POST"])
def user_update_backup_dir():
    """Update the backup directory for the current user."""
    current_user = request.cookies.get("librarium_user", "")
    if not current_user:
        abort(400)
    new_dir = request.form.get("backup_dir", "").strip()
    users_data = _load_users()
    for u in users_data["users"]:
        if u["name"] == current_user:
            u["backup_dir"] = new_dir
            break
    _save_users(users_data)
    global BACKUP_DIR
    BACKUP_DIR = _get_user_backup_dir(current_user)
    flash("Backup directory updated.", "success")
    return redirect(request.referrer or url_for("index"))


@app.before_request
def check_user_selected():
    """Redirect to Dropbox auth if not authenticated, then to user selection if no user is set."""
    exempt = ("/auth/", "/static")
    if any(request.path.startswith(p) for p in exempt):
        return
    # Check Dropbox authentication first
    if not _is_authenticated():
        return redirect(url_for("auth_login"))
    # Then check user selection
    exempt_user = ("/users",)
    if any(request.path.startswith(p) for p in exempt_user):
        return
    users_data = _load_users()
    if not users_data["users"]:
        return redirect(url_for("user_select"))
    current_user = request.cookies.get("librarium_user", "")
    if not current_user:
        # Auto-select last user if available
        last = users_data.get("last_user", "")
        if last and any(u["name"] == last for u in users_data["users"]):
            _set_active_user_db(last)
            g._pending_user_cookie = last
        else:
            return redirect(url_for("user_select"))


@app.after_request
def set_pending_user_cookie(response):
    """Set user cookie if auto-selected."""
    pending = getattr(g, "_pending_user_cookie", None)
    if pending:
        response.set_cookie("librarium_user", pending, max_age=60 * 60 * 24 * 365 * 5,
                             samesite="Lax")
    return response


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
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── Migrate legacy data/ folder to AppData ──────────────────────────
    _legacy_data = BASE_DIR / "data"
    if _legacy_data.is_dir() and _legacy_data != DATA_DIR:
        _legacy_users = _legacy_data / "users.json"
        if _legacy_users.exists() and not USERS_FILE.exists():
            shutil.copy2(str(_legacy_users), str(USERS_FILE))
            print(f"[migrate] Copied users.json → {USERS_FILE}")
        for _dbf in _legacy_data.glob("*.db"):
            _dest = DATA_DIR / _dbf.name
            if not _dest.exists():
                shutil.copy2(str(_dbf), str(_dest))
                print(f"[migrate] Copied {_dbf.name} → {_dest}")
        _legacy_backups = _legacy_data / "backups"
        if _legacy_backups.is_dir():
            _dest_backups = DATA_DIR / "backups"
            _dest_backups.mkdir(parents=True, exist_ok=True)
            for _bk in _legacy_backups.glob("*.db"):
                _bdest = _dest_backups / _bk.name
                if not _bdest.exists():
                    shutil.copy2(str(_bk), str(_bdest))
        print(f"[migrate] Legacy data/ migration complete. Data is now at: {DATA_DIR}")
        print(f"[migrate] You may delete the old '{_legacy_data}' folder once verified.")

    # ── Dropbox sync at startup ─────────────────────────────────────────
    if _is_authenticated():
        try:
            print("[dropbox] Downloading data from Dropbox...")
            _download_all_from_dropbox()
            print("[dropbox] Sync complete.")
        except AuthError:
            print("[dropbox] Auth token expired or revoked. User will need to re-authenticate.")
            _clear_auth()
            _reset_dropbox_client()
        except Exception as e:
            print(f"[dropbox] Startup sync failed (working offline): {e}")

    # Run migrations for every existing user's DB
    users_data = _load_users()
    if users_data["users"]:
        for _u in users_data["users"]:
            _set_active_user_db(_u["name"])
            _run_all_migrations()
            backup_database()
        # Restore active user to last_user (or first)
        _last = users_data.get("last_user", "")
        if _last and any(u["name"] == _last for u in users_data["users"]):
            _set_active_user_db(_last)
        else:
            _set_active_user_db(users_data["users"][0]["name"])
    elif DB_PATH.exists():
        # Legacy single-DB mode: run migrations on default DB
        validate_and_restore_db()
        backup_database()
        _run_all_migrations()

    # Start periodic Dropbox sync
    port = int(os.environ.get("LIBRARIUM_PORT", 5000))
    is_electron = os.environ.get("LIBRARIUM_ELECTRON") == "1"

    if _is_authenticated():
        # Guard against Werkzeug reloader spawning duplicate threads
        if is_electron or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            _start_periodic_sync()

    app.run(
        debug=not is_electron,
        port=port,
        extra_files=None,
        exclude_patterns=["*/site-packages/*"],
    )

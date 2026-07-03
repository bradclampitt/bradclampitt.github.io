"""
Database connection management for unified database.
"""
import sqlite3
from typing import Any

from admin.config import DATABASE_PATH, SCHEMA_PATH


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite Row to a dict, decoding byte values as UTF-8 text."""
    data: dict[str, Any] = {}
    for key in row.keys():
        value = row[key]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        data[key] = value
    return data


def _repair_cms_block_text_content(conn: sqlite3.Connection) -> None:
    """Fix cms_blocks.content rows stored as BLOB instead of TEXT."""
    rows = conn.execute(
        "SELECT id, content FROM cms_blocks WHERE typeof(content) = 'blob'"
    ).fetchall()
    if not rows:
        return

    for row_id, content in rows:
        if isinstance(content, bytes):
            conn.execute(
                "UPDATE cms_blocks SET content = ? WHERE id = ?",
                (content.decode("utf-8"), row_id),
            )
    conn.commit()


def get_conn() -> sqlite3.Connection:
    """
    Get connection to unified database.
    Ensures database exists and is initialized before returning connection.
    """
    ensure_database()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> None:
    """
    Ensure database exists and is initialized with schema.
    Creates database and applies schema if it doesn't exist.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not DATABASE_PATH.exists():
        if SCHEMA_PATH.exists():
            with sqlite3.connect(DATABASE_PATH) as conn, \
                 SCHEMA_PATH.open("r", encoding="utf-8") as fh:
                conn.executescript(fh.read())
        else:
            # Create empty database if schema doesn't exist
            sqlite3.connect(DATABASE_PATH).close()
    else:
        # Migrate existing database: add featured column to documents table if missing
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                # Check if featured column exists
                cursor.execute("PRAGMA table_info(documents)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'featured' not in columns:
                    cursor.execute("ALTER TABLE documents ADD COLUMN featured INTEGER DEFAULT 0")
                    conn.commit()
                _repair_cms_block_text_content(conn)
        except Exception:
            # If table doesn't exist or other error, schema will be applied on next startup
            pass


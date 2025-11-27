"""
Database connection management for unified database.
"""
import sqlite3
from pathlib import Path
from admin.config import DATABASE_PATH, SCHEMA_PATH


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


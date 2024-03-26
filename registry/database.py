"""
Manage the web application's local database.

The database serves as a permanent store for webhook payloads received from
the associated Harbor instance, as well as a mechanism for tracking HTCondor
jobs that process those payloads.
"""

import pathlib
import sqlite3

import flask

__all__ = [
    "get_db_conn",
    "init",
    "insert_new_payload",
]

DB_FILE = "database/soteria.sqlite"


def get_db_conn() -> sqlite3.Connection:
    """
    Create a connection object to the database.
    """
    return sqlite3.connect(pathlib.Path(flask.current_app.config["DATA_DIR"]) / DB_FILE)


def init(app: flask.Flask) -> None:
    """
    Ensure that the database exists and has the required tables and columns.
    """
    db_file = pathlib.Path(app.config["DATA_DIR"]) / DB_FILE
    db_file.parent.mkdir(parents=True, exist_ok=True)

    if not db_file.exists():
        db_file.touch()
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_payloads
            (
              id INTEGER PRIMARY KEY
            , payload TEXT
            )
            """,
        )
        conn.commit()


def insert_new_payload(data: str) -> None:
    """
    Add a new webhook payload to the database.
    """
    with get_db_conn() as conn:
        conn.execute(
            """
            INSERT INTO webhook_payloads
            ( payload )
            VALUES
            ( :payload )
            """,
            {"payload": data},
        )
        conn.commit()

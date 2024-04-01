"""
Manage the web application's local database.

The database serves as a permanent store for webhook payloads received from
the associated Harbor instance, as well as a mechanism for tracking HTCondor
jobs that process those payloads.
"""

import dataclasses
import enum
import json
import pathlib
import sqlite3
import time
from collections.abc import Generator
from typing import Any, Optional

import flask

__all__ = [
    "AccessKind",
    "Source",
    "State",
    "WebhookPayload",
    #
    "get_db_conn",
    "get_new_payloads",
    "init",
    "insert_new_payload",
    "update_payload",
]

# Path to the database file, relative to the web application's data directory.
DB_FILE = "database/soteria.sqlite"


class AccessKind(enum.Enum):
    """
    Categorize the resources listed in a webhook payload.
    """

    private = "private"
    public = "public"
    public_and_tagged = "public+tagged"


class Source(enum.Enum):
    """
    Categorize the source of a webhook payload.
    """

    harbor = "harbor"


class State(enum.Enum):
    """
    Categorize how a webhook payload has been evaluated.
    """

    new = "new"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


@dataclasses.dataclass
class WebhookPayload:
    """
    Represent one row in the 'webhook_payloads' table.
    """

    id_: int
    payload: dict[Any, Any]
    source: Source
    access_kind: AccessKind
    state: State
    created_on: int
    updated_on: int

    def __post_init__(self):
        """
        Convert this dataclass instance from its database representation.
        """
        if isinstance(self.payload, str):  # type: ignore[unreachable]
            self.payload = json.loads(self.payload)  # type: ignore[unreachable]
        self.source = Source(self.source)
        self.access_kind = AccessKind(self.access_kind)
        self.state = State(self.state)


# --------------------------------------------------------------------------


def is_public(payload) -> bool:
    """
    Determine whether a webhook payload is for a public repository.
    """
    return bool("public" == payload["event_data"]["repository"]["repo_type"])


def is_tagged_resource(resource_payload) -> bool:
    """
    Determine whether a resource in a webhook payload is "tagged."
    """
    tag = resource_payload["tag"]
    return tag != "latest" and not tag.startswith("sha256:")


def has_tagged_resource(payload) -> bool:
    """
    Determine whether a webhook payload has at least one tagged resource.
    """
    return any(is_tagged_resource(r) for r in payload["event_data"]["resources"])


# --------------------------------------------------------------------------


def get_db_file(app: Optional[flask.Flask] = None) -> pathlib.Path:
    """
    Return the path to the database file.
    """
    if not app:
        app = flask.current_app
    return pathlib.Path(app.config["DATA_DIR"]) / DB_FILE


def get_db_conn(app: Optional[flask.Flask] = None) -> sqlite3.Connection:
    """
    Return a new connection object to the database.
    """
    return sqlite3.connect(get_db_file(app))


def init(app: flask.Flask) -> None:
    """
    Ensure that the database exists and has the required tables and columns.
    """
    db_file = get_db_file(app)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    if not db_file.exists():
        db_file.touch()
    with get_db_conn(app) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_payloads
            (
              id INTEGER PRIMARY KEY
            , payload TEXT
            , source TEXT
            , access_kind TEXT
            , state TEXT
            , created_on INT
            , updated_on INT
            )
            """,
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS webhook_payloads_state_index
            ON webhook_payloads (state)
            """
        )
        conn.commit()


def insert_new_payload(payload: dict[Any, Any], source: Source) -> None:
    """
    Add a new webhook payload to the database.
    """
    if is_public(payload):
        if has_tagged_resource(payload):
            access_kind = AccessKind.public_and_tagged
        else:
            access_kind = AccessKind.public
    else:
        access_kind = AccessKind.private

    with get_db_conn() as conn:
        conn.execute(
            """
            INSERT INTO webhook_payloads
            ( payload, source, access_kind, state, created_on )
            VALUES
            ( :payload, :source, :access_kind, :state, :created_on )
            """,
            {
                "payload": json.dumps(payload, separators=(",", ":")),
                "source": source.value,
                "access_kind": access_kind.value,
                "state": State.new.value,
                "created_on": int(time.time()),
            },
        )
        conn.commit()


def get_new_payloads() -> Generator[WebhookPayload, None, None]:
    """
    Iterate over any "new" webhook payloads in the database.
    """
    with get_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM webhook_payloads
            WHERE state = 'new'
            """
        ).fetchall()
    for r in rows:
        yield WebhookPayload(*r)


def update_payload(id_: int, state: State) -> None:
    """
    Update the state of a webhook payload.
    """
    with get_db_conn() as conn:
        conn.execute(
            """
            UPDATE webhook_payloads
            SET state = :state, updated_on = :updated_on
            WHERE id = :id
            """,
            {
                "id": id_,
                "state": state.value,
                "updated_on": int(time.time()),
            },
        )
        conn.commit()

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
import uuid
from collections.abc import Generator
from typing import Any, Optional

import flask

__all__ = [
    "AccessKind",
    "Source",
    "State",
    "WebhookPayload",
    #
    "FINAL_STATES",
    #
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


FINAL_STATES = [
    State.completed,
    State.failed,
    State.skipped,
]


@dataclasses.dataclass
class WebhookPayload:  # pylint: disable=too-many-instance-attributes
    """
    Represent one row in the 'webhook_payloads' table.
    """

    id_: str
    resource: str
    access_kind: AccessKind
    state: State
    payload: dict[Any, Any]
    source: Source
    project: str
    repository: str
    tag: str
    created_on: int
    updated_on: int

    def __post_init__(self):
        """
        Convert this dataclass instance from its database representation.
        """
        if isinstance(self.payload, str):  # type: ignore[unreachable]
            self.payload = json.loads(self.payload)  # type: ignore[unreachable]
        self.access_kind = AccessKind(self.access_kind)
        self.state = State(self.state)
        self.source = Source(self.source)


# --------------------------------------------------------------------------


def is_public(payload) -> bool:
    """
    Determine whether a webhook payload is for a public repository.
    """
    return bool("public" == payload["event_data"]["repository"]["repo_type"])


def is_immutable_tag(tag: str) -> bool:
    """
    Determine whether a resource's tag should be considered immutable.
    """
    return tag != "latest" and not tag.startswith("sha256:")


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
              id TEXT PRIMARY KEY
            , resource TEXT
            , access_kind TEXT
            , state TEXT
            , payload TEXT
            , source TEXT
            , project TEXT
            , repository TEXT
            , tag TEXT
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
    with get_db_conn() as conn:
        for resource in payload["event_data"]["resources"]:
            if is_public(payload):
                if is_immutable_tag(resource["tag"]):
                    access_kind = AccessKind.public_and_tagged
                else:
                    access_kind = AccessKind.public
            else:
                access_kind = AccessKind.private

            now = int(time.time())

            conn.execute(
                """
                INSERT INTO webhook_payloads
                ( id, resource, access_kind, state, payload, source, project, repository, tag, created_on, updated_on )
                VALUES
                ( :id, :resource, :access_kind, :state, :payload, :source, :project, :repository, :tag, :created_on, :updated_on )
                """,
                {
                    "id": str(uuid.uuid4()),
                    "resource": resource["resource_url"],
                    "access_kind": access_kind.value,
                    "state": State.new.value,
                    "payload": json.dumps(payload, separators=(",", ":")),
                    "source": source.value,
                    "project": payload["event_data"]["repository"]["namespace"],
                    "repository": payload["event_data"]["repository"]["name"],
                    "tag": resource["tag"],
                    "created_on": now,
                    "updated_on": now,
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
            ORDER BY created_on ASC
            """
        ).fetchall()
    for row in rows:
        yield WebhookPayload(*row)


def update_payload(id_: str, state: State) -> None:
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

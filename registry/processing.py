"""
Process webhook payloads.
"""

from typing import Optional

import flask

from registry.database import AccessKind, Source, State, WebhookPayload


def process(payload: WebhookPayload) -> Optional[State]:
    """
    Determine what to do with a webhook payload, and return its new state.
    """
    app = flask.current_app

    if payload.source != Source.harbor:
        app.logger.error(f"Unexpected payload source: {payload}")  # type: ignore[unreachable]
        return State.failed

    if payload.access_kind != AccessKind.public_and_tagged:
        return State.skipped

    app.logger.error("Not yet implemented")  # XXX

    return None

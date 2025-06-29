from datetime import datetime
from typing import Callable

from pymongo import database


def create_session_refresher(
    db: database.Database, session_id: str
) -> Callable[[], None]:
    refresh_timestamp = datetime.now()

    def refresh_session_if_needed():
        nonlocal refresh_timestamp
        if (datetime.now() - refresh_timestamp).total_seconds() > 300:
            db.command({"refreshSessions": [session_id]})
            refresh_timestamp = datetime.now()

    return refresh_session_if_needed

import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

__all__ = ['JsonObject', 'now', 'default_id_factory', 'default_extras_factory']

# Types
JsonObject = Dict[str, Any]


def now(tzinfo=timezone.utc) -> datetime:
    return datetime.utcnow().replace(tzinfo=tzinfo)


def default_id_factory() -> str:
    return str(uuid.uuid4())


def default_extras_factory() -> JsonObject:
    pid: int = os.getpid()
    thread_name: str = threading.current_thread().name

    return {
        'pid': pid,
        'thread_name': thread_name,
    }

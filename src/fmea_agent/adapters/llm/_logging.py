"""Filter native HTTP logs for the current synchronous call, preserving other logging."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from threading import get_ident

# All native logger names in pinned HTTPX 0.28.1 / HTTPcore 1.0.9.
# Child loggers need their own filters: logging does not inherit parent filters.
HTTP_LOGGER_NAMES = (
    "httpx",
    "httpcore",
    "httpcore.connection",
    "httpcore.http11",
    "httpcore.http2",
    "httpcore.proxy",
    "httpcore.socks",
)


class _CurrentThreadFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__()
        self.thread_id = get_ident()

    def filter(self, record: logging.LogRecord) -> bool:
        return get_ident() != self.thread_id


@contextmanager
def quiet_http_logs() -> Iterator[None]:
    """Suppress library headers/errors only in this thread, including handler-local DEBUG."""
    guard = _CurrentThreadFilter()
    loggers = [logging.getLogger(name) for name in HTTP_LOGGER_NAMES]
    try:
        for logger in loggers:
            logger.addFilter(guard)
        yield
    finally:
        for logger in loggers:
            logger.removeFilter(guard)

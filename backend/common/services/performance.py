from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager

from django.conf import settings
from django.db import connection

logger = logging.getLogger("git_it.performance")


@contextmanager
def timing(name: str, **fields: object) -> Iterator[None]:
    if not getattr(settings, "PERFORMANCE_TIMING_ENABLED", False):
        yield
        return

    start = time.perf_counter()
    start_query_count = len(connection.queries) if settings.DEBUG else None
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        if start_query_count is not None:
            fields = {
                **fields,
                "db_queries": len(connection.queries) - start_query_count,
            }
        suffix = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
        logger.info("%s elapsed_ms=%.2f%s", name, elapsed_ms, f" {suffix}" if suffix else "")

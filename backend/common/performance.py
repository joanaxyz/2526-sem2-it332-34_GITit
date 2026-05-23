from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager

logger = logging.getLogger("git_it.performance")


@contextmanager
def timing(name: str, **fields: object) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        suffix = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
        logger.info("%s elapsed_ms=%.2f%s", name, elapsed_ms, f" {suffix}" if suffix else "")

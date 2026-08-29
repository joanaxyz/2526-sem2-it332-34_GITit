"""Small collection coercions shared across backend domains."""

from typing import Any


def as_list(value: Any) -> list:
    """Return list values unchanged and wrap one non-empty scalar."""

    if value in (None, ""):
        return []
    return value if isinstance(value, list) else [value]

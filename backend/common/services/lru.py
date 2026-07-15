"""Shared process-local LRU for command history.

Both the challenge and adventure command paths cache a session's normalized
command history to avoid re-querying the persisted steps on every submit. The
cache key pairs the session id with a monotonically growing count (attempts / step count)
so any stale entry is self-invalidating: a key another worker, a rollback, or a
restart never wrote simply misses and falls back to the DB query.

Subclasses supply the key derivation and the fallback query; the LRU store and
its eviction live here, once. Each subclass gets its own isolated cache so the
two surfaces never collide on a shared (int, int) key.
"""

from __future__ import annotations

from collections import OrderedDict

_MAX_ENTRIES = 512


class LRUCommandHistoryCache:
    _cache: OrderedDict[tuple[int, int], list[str]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # A fresh store per subclass: challenge and adventure keys must not share
        # one dict (both are (id, count) and would alias).
        cls._cache = OrderedDict()

    def _cached(self, key: tuple[int, int]) -> list[str] | None:
        cached = self._cache.get(key)
        if cached is None:
            return None
        self._cache.move_to_end(key)
        return list(cached)

    def _remember(self, key: tuple[int, int], history: list[str]) -> None:
        self._cache[key] = list(history)
        self._cache.move_to_end(key)
        while len(self._cache) > _MAX_ENTRIES:
            self._cache.popitem(last=False)

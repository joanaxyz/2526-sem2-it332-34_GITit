"""Shared process-local LRU for command history.

Both the challenge and adventure command paths cache a session's normalized
command history to avoid re-querying the persisted steps on every submit. The
cache key includes a persistent session identity plus a monotonically growing
count (attempts / step count), so a key another worker, a rollback, or a restart
never wrote simply misses and falls back to the DB query.

Subclasses supply the key derivation and the fallback query; the LRU store and
its eviction live here, once. Each subclass gets its own isolated cache so the
two surfaces never collide on overlapping integer ids and counts.
"""

from __future__ import annotations

from collections import OrderedDict

from django.db import transaction

_MAX_ENTRIES = 512
type CommandHistoryCacheKey = tuple[object, ...]


class LRUCommandHistoryCache:
    _cache: OrderedDict[CommandHistoryCacheKey, list[str]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # A fresh store per subclass: challenge and adventure keys must not share
        # one dict because their integer ids and counts can overlap.
        cls._cache = OrderedDict()

    def _cached(self, key: CommandHistoryCacheKey) -> list[str] | None:
        cached = self._cache.get(key)
        if cached is None:
            return None
        self._cache.move_to_end(key)
        return list(cached)

    def _remember(self, key: CommandHistoryCacheKey, history: list[str]) -> None:
        # Both appended history and query results can contain uncommitted steps.
        # A rolled-back attempt count can later be reused, so never publish it
        # until the outer transaction commits. Snapshot now: callers can reuse
        # or mutate their list before Django runs the callback.
        snapshot = tuple(history)

        def publish() -> None:
            self._cache[key] = list(snapshot)
            self._cache.move_to_end(key)
            while len(self._cache) > _MAX_ENTRIES:
                self._cache.popitem(last=False)

        transaction.on_commit(publish)

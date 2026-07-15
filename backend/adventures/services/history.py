"""Adventure run orchestration.

An adventure run is one playable `AdventureLevel`, walked as an ordered sequence
of `AdventureWave` problems. Each wave selects its own variant; the run completes
only when the last wave is cleared. Chapters order adventure levels for
unlocks and mastery targets, but the runtime never walks a whole chapter as
one continuous session.
"""



from adventures.models import (
    AdventureRun,
)
from common.services.lru import LRUCommandHistoryCache
from practice.models import CommandStep


class AdventureCommandHistoryCache(LRUCommandHistoryCache):
    def history_for(self, *, attempt: AdventureRun, log_count: int) -> list[str]:
        if log_count <= 0:
            return []
        key = (attempt.id, log_count)
        cached = self._cached(key)
        if cached is not None:
            return cached
        history = list(
            CommandStep.objects.filter(attempt=attempt)
            .order_by("id")
            .values_list("normalized_command", flat=True)
        )
        self._remember(key, history)
        return history

    def remember(self, *, attempt: AdventureRun, log_count: int, history: list[str]) -> None:
        self._remember((attempt.id, log_count), history)

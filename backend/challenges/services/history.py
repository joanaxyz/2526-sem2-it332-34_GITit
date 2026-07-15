from challenges.models import ChallengeRun
from common.services.lru import LRUCommandHistoryCache


class CommandHistoryCache(LRUCommandHistoryCache):
    def history_for(self, *, run: ChallengeRun) -> list[str]:
        from practice.models import CommandStep

        if run.total_attempts <= 0:
            return []
        key = (run.id, run.total_attempts)
        cached = self._cached(key)
        if cached is not None:
            return cached
        history = list(
            CommandStep.objects.filter(challenge_run=run)
            .order_by("id")
            .values_list("normalized_command", flat=True)
        )
        self._remember(key, history)
        return history

    def remember_after_append(
        self,
        *,
        run: ChallengeRun,
        previous_history: list[str],
        normalized_command: str,
    ) -> None:
        self._remember((run.id, run.total_attempts), [*previous_history, normalized_command])

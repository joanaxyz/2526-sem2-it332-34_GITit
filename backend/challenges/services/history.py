from challenges.models import ChallengeRun
from common.services.lru import LRUCommandHistoryCache


class CommandHistoryCache(LRUCommandHistoryCache):
    @staticmethod
    def key_for(*, run: ChallengeRun, attempt_count: int) -> tuple[object, ...]:
        # Include immutable run identity fields so a reused database id cannot
        # inherit command history from an earlier run in this process.
        return (
            run.id,
            run.started_at,
            run.selected_variant_id,
            attempt_count,
        )

    def history_for(self, *, run: ChallengeRun) -> list[str]:
        from practice.models import CommandStep

        if run.total_attempts <= 0:
            return []
        key = self.key_for(run=run, attempt_count=run.total_attempts)
        cached = self._cached(key)
        if cached is not None:
            return cached
        history = list(
            CommandStep.objects.filter(challenge_run=run, was_processable=True)
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
        self._remember(
            self.key_for(run=run, attempt_count=run.total_attempts),
            [*previous_history, normalized_command],
        )

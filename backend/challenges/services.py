from django.db import transaction
from django.utils import timezone

from battle.state import initial_challenge_battle_state
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeVariant
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.lru import LRUCommandHistoryCache
from progress.models import LevelCompletion

RUN_HYDRATE_SELECT_RELATED = (
    "chapter",
    "challenge",
    "challenge_level__challenge",
    "challenge_variant",
    "prior_run",
    "user",
)


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        level: ChallengeLevel,
        prior_run: ChallengeRun | None = None,
        published_variants: list[ChallengeVariant] | None = None,
        tried_variant_keys: set[str] | None = None,
    ) -> ChallengeVariant:
        variants = published_variants or list(
            level.challenge_variants.filter(is_published=True).order_by("semantic_key", "id")
        )
        if not variants:
            raise Locked("This challenge level has no published variants.")
        if prior_run is None:
            return variants[0]

        prior_key = self.variant_identity(prior_run.variant)
        tried_keys = tried_variant_keys if tried_variant_keys is not None else self._tried_variant_keys(user=user, level=level)
        for variant in variants:
            identity = self.variant_identity(variant)
            if identity != prior_key and identity not in tried_keys:
                return variant
        for variant in variants:
            if self.variant_identity(variant) != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior, current) -> bool:
        return self.variant_identity(prior) != self.variant_identity(current)

    def is_loopback_from_keys(self, *, variants: list[ChallengeVariant], selected_variant, tried_keys: set[str]) -> bool:
        if len(variants) <= 1:
            return False
        available = {self.variant_identity(variant) for variant in variants}
        return (
            len(tried_keys.intersection(available)) >= len(available)
            and self.variant_identity(selected_variant) in tried_keys
        )

    def variant_identity(self, variant) -> str:
        # Seeded variants always carry a semantic_key (a content hash). The id
        # fallback only guards unsaved/legacy rows that predate that guarantee.
        return variant.semantic_key or f"id:{variant.id}"

    def _tried_variant_keys(self, *, user, level: ChallengeLevel) -> set[str]:
        variant_ids = (
            ChallengeRun.objects.filter(user=user, challenge_level=level)
            .values_list("challenge_variant_id", flat=True)
            .distinct()
        )
        return {
            self.variant_identity(variant)
            for variant in ChallengeVariant.objects.filter(id__in=variant_ids)
        }


class CommandHistoryCache(LRUCommandHistoryCache):
    def history_for(self, *, run: ChallengeRun) -> list[str]:
        from practice.models import CommandLog

        key = (run.id, run.total_attempts)
        cached = self._cached(key)
        if cached is not None:
            return cached
        history = list(
            CommandLog.objects.filter(step__challenge_run=run)
            .order_by("step_id")
            .values_list("normalized_command", flat=True)
        )
        self._remember(key, history)
        return history

    def remember_after_append(self, *, run: ChallengeRun, previous_history: list[str], normalized_command: str) -> None:
        self._remember((run.id, run.total_attempts), [*previous_history, normalized_command])


class ChallengeRunService:
    @staticmethod
    def hydrate_run(run: ChallengeRun | int, *, user=None) -> ChallengeRun:
        from django.db.models import Prefetch

        from practice.models import CommandStep

        queryset = ChallengeRun.objects.select_related(*RUN_HYDRATE_SELECT_RELATED).prefetch_related(
            Prefetch("steps", queryset=CommandStep.objects.order_by("id")),
        )
        queryset = queryset.filter(pk=run if isinstance(run, int) else run.pk)
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset.get()

    @transaction.atomic
    def start_run(
        self,
        *,
        user,
        level: ChallengeLevel,
        source_entry_point: str,
        prior_run: ChallengeRun | None = None,
        mode: str = SESSION_MODE_PRIMARY,
    ) -> ChallengeRun:
        if prior_run and prior_run.challenge_level_id != level.id:
            raise Locked("Retry runs must use the same challenge level.")
        if prior_run and prior_run.status == SESSION_STATUS_STARTED:
            raise Locked("Exit the current challenge run before retrying.")
        if mode == SESSION_MODE_PRIMARY:
            self._ensure_unlocked(user=user, level=level)
            active = self._active_run(user=user, level=level)
            if active and (not prior_run or active.id != prior_run.id):
                raise Locked("Exit the current challenge run before starting again.")

        selector = VariantSelectionService()
        published_variants = list(
            level.challenge_variants.filter(is_published=True).order_by("semantic_key", "id")
        )
        tried_keys = selector._tried_variant_keys(user=user, level=level) if prior_run else set()
        variant = (
            self._review_variant(user=user, level=level)
            if mode == SESSION_MODE_REVIEW
            else selector.select_variant(
                user=user,
                level=level,
                prior_run=prior_run,
                published_variants=published_variants,
                tried_variant_keys=tried_keys,
            )
        )
        changed_variant = bool(prior_run and selector.changed_between(prior=prior_run.variant, current=variant))
        looped_variant = bool(
            prior_run
            and selector.is_loopback_from_keys(
                variants=published_variants,
                selected_variant=variant,
                tried_keys=tried_keys,
            )
        )
        retry_index = prior_run.retry_index + 1 if prior_run else 0
        rta_eligible = bool(
            mode == SESSION_MODE_PRIMARY
            and prior_run
            and prior_run.status in (SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED)
            and changed_variant
        )
        run = ChallengeRun.objects.create(
            user=user,
            chapter=level.chapter,
            challenge=level.challenge,
            challenge_level=level,
            challenge_variant=variant,
            prior_run=prior_run,
            source_entry_point=source_entry_point,
            mode=mode,
            difficulty=level.difficulty,
            rta_eligible=rta_eligible,
            changed_variant=changed_variant,
            looped_variant=looped_variant,
            retry_index=retry_index,
            command_budget_snapshot={
                "min_counted_commands": level.min_counted_commands,
                "max_counted_commands": level.max_counted_commands,
            },
            repository_state=variant.initial_state,
            battle_state=initial_challenge_battle_state(level, variant),
        )
        return self.hydrate_run(run)

    def _active_run(self, *, user, level: ChallengeLevel):
        return ChallengeRun.objects.filter(
            user=user,
            challenge_level=level,
            status=SESSION_STATUS_STARTED,
            mode=SESSION_MODE_PRIMARY,
        ).first()

    def _ensure_unlocked(self, *, user, level: ChallengeLevel) -> None:
        if level.difficulty == DIFFICULTY_EASY:
            # Entry into a chapter's challenges is gated on passing its Command
            # Adventure (the learn-by-doing mode that teaches the commands first).
            self._ensure_adventure_passed(user=user, chapter=level.chapter)
            return
        previous = DIFFICULTY_EASY if level.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
        previous_level = ChallengeLevel.objects.filter(
            challenge=level.challenge,
            difficulty=previous,
            is_published=True,
        ).first()
        if not previous_level or not LevelCompletion.objects.filter(user=user, challenge_level=previous_level).exists():
            raise Locked("This challenge level is locked until the previous level is completed.")

    def _ensure_adventure_passed(self, *, user, chapter) -> None:
        # Lazy import: adventures.models is a leaf w.r.t. challenges, but keep the
        # dependency local to this gate.
        from command_adventures.models import AdventureRun, CommandAdventure

        adventure_ids = list(
            CommandAdventure.objects.filter(chapter=chapter, is_published=True).values_list("id", flat=True)
        )
        if not adventure_ids:
            return  # chapter has no Command Adventure to gate on
        passed_ids = set(
            AdventureRun.objects.filter(
                user=user, command_adventure_id__in=adventure_ids, passed_at__isnull=False
            ).values_list("command_adventure_id", flat=True)
        )
        if not set(adventure_ids).issubset(passed_ids):
            raise Locked("Complete this chapter's Command Adventures to unlock its challenges.")

    def _review_variant(self, *, user, level: ChallengeLevel):
        completion = LevelCompletion.objects.select_related("challenge_run__challenge_variant").filter(
            user=user,
            challenge_level=level,
        ).first()
        if not completion or not completion.challenge_run:
            raise Locked("Free play is available only after completing this challenge level.")
        return completion.challenge_run.variant

    @transaction.atomic
    def abandon(self, *, run: ChallengeRun) -> ChallengeRun:
        if run.status != SESSION_STATUS_STARTED:
            return run
        run.status = SESSION_STATUS_ABANDONED
        run.ended_at = timezone.now()
        run.failure_reason = "Student left the challenge run before completion."
        run.save(update_fields=["status", "ended_at", "failure_reason"])
        return run

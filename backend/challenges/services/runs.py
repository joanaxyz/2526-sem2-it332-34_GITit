from django.db import IntegrityError, transaction

from challenges.models import ChallengeRun, ChallengeTrial
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Conflict, Locked
from progress.models import (
    AdventureLevelCompletion,
    ChallengeLevelCompletion,
    ChallengeTrialCompletion,
)

from .variants import VariantSelectionService

RUN_HYDRATE_SELECT_RELATED = (
    "challenge_trial",
    "challenge_trial__challenge_level",
    "challenge_trial__challenge_level__chapter",
    "challenge_trial__challenge_level__chapter__story",
    "challenge_trial__challenge_level__source_content_definition",
    "selected_variant",
    "selected_variant__trial",
    "prior_run",
    "player",
)


class ChallengeRunService:
    @staticmethod
    def hydrate_run(run: ChallengeRun | int, *, player=None) -> ChallengeRun:
        from django.db.models import Prefetch

        from practice.models import CommandStep

        queryset = ChallengeRun.objects.select_related(*RUN_HYDRATE_SELECT_RELATED).prefetch_related(
            Prefetch("steps", queryset=CommandStep.objects.order_by("id")),
        )
        queryset = queryset.filter(pk=run if isinstance(run, int) else run.pk)
        if player is not None:
            queryset = queryset.filter(player=player)
        return queryset.get()

    @transaction.atomic
    def start_run(
        self,
        *,
        player,
        trial: ChallengeTrial,
        source_entry_point: str,
        prior_run: ChallengeRun | None = None,
        is_replay: bool = False,
    ) -> ChallengeRun:
        player.__class__.objects.select_for_update().get(pk=player.pk)

        if prior_run is not None:
            prior_run = (
                ChallengeRun.objects.select_for_update()
                .select_related("challenge_trial")
                .get(pk=prior_run.pk, player=player)
            )
            if prior_run.challenge_trial_id != trial.id:
                raise Locked("Retry runs must use the same challenge trial.")

        already_completed = ChallengeTrialCompletion.objects.filter(
            player=player,
            challenge_trial=trial,
        ).exists()
        # Replay semantics are authoritative on the server. Once a trial has a
        # completion, every new direct launch is free play regardless of a stale
        # or omitted client flag.
        is_replay = bool(is_replay or already_completed or (prior_run and prior_run.is_replay))
        if not is_replay:
            self._ensure_unlocked(player=player, trial=trial)

        active = self._active_run(player=player, trial=trial, for_update=True)
        if active and (not prior_run or active.id != prior_run.id):
            self.discard(run=active)

        selector = VariantSelectionService()
        published_variants = list(
            trial.variants.filter(is_published=True).order_by("semantic_key", "id")
        )
        tried_keys = selector._tried_variant_keys(player=player, trial=trial) if prior_run else set()
        variant = (
            self._replay_variant(player=player, trial=trial)
            if is_replay
            else selector.select_variant(
                player=player,
                trial=trial,
                prior_run=prior_run,
                published_variants=published_variants,
                tried_variant_keys=tried_keys,
            )
        )
        if variant is None:
            raise Locked("This challenge trial has no published variants.")

        retry_index = prior_run.retry_index + 1 if prior_run else 0
        prior_reference = prior_run
        if prior_run and prior_run.status == SESSION_STATUS_STARTED:
            self.discard(run=prior_run)
            prior_reference = None

        try:
            run = ChallengeRun.objects.create(
                player=player,
                challenge_trial=trial,
                selected_variant=variant,
                prior_run=prior_reference,
                source_entry_point=source_entry_point,
                is_replay=is_replay,
                retry_index=retry_index,
                min_counted_commands=trial.min_counted_commands,
                max_counted_commands=trial.max_counted_commands,
                repository_state=variant.initial_state,
            )
        except IntegrityError as exc:
            raise Conflict("An active run already exists for this challenge trial.") from exc
        return self.hydrate_run(run)

    def _active_run(self, *, player, trial: ChallengeTrial, for_update: bool = False):
        queryset = ChallengeRun.objects.filter(
            player=player,
            challenge_trial=trial,
            status=SESSION_STATUS_STARTED,
        )
        if for_update:
            queryset = queryset.select_for_update()
        return queryset.first()

    def _ensure_unlocked(self, *, player, trial: ChallengeTrial) -> None:
        self._ensure_previous_challenge_level_complete(player=player, trial=trial)
        if trial.difficulty == DIFFICULTY_EASY:
            self._ensure_adventure_complete(player=player, chapter=trial.chapter)
            return
        previous = DIFFICULTY_EASY if trial.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
        previous_trial = ChallengeTrial.objects.filter(
            challenge_level=trial.challenge_level,
            difficulty=previous,
            is_published=True,
        ).first()
        if not previous_trial or not ChallengeTrialCompletion.objects.filter(
            player=player,
            challenge_trial=previous_trial,
        ).exists():
            raise Locked("This challenge trial is locked until the previous trial is completed.")

    def _ensure_previous_challenge_level_complete(self, *, player, trial: ChallengeTrial) -> None:
        previous_level = (
            trial.challenge_level.chapter.challenge_levels.filter(
                is_published=True,
                sort_order__lt=trial.challenge_level.sort_order,
            )
            .order_by("-sort_order", "-id")
            .first()
        )
        if previous_level and not ChallengeLevelCompletion.objects.filter(
            player=player,
            challenge_level=previous_level,
        ).exists():
            raise Locked("Complete the previous challenge level first.")

    def _ensure_adventure_complete(self, *, player, chapter) -> None:
        from adventures.models import AdventureLevel

        required_level_ids = set(
            AdventureLevel.objects.filter(
                chapter=chapter,
                is_published=True,
                is_required=True,
            ).values_list("id", flat=True)
        )
        if not required_level_ids:
            return
        completed_level_ids = set(
            AdventureLevelCompletion.objects.filter(
                player=player,
                adventure_level_id__in=required_level_ids,
            ).values_list("adventure_level_id", flat=True)
        )
        if required_level_ids <= completed_level_ids:
            return
        raise Locked("Complete this chapter's required Adventure levels to unlock its challenges.")


    def _replay_variant(self, *, player, trial: ChallengeTrial):
        completion = (
            ChallengeTrialCompletion.objects.select_related("challenge_run__selected_variant")
            .filter(player=player, challenge_trial=trial)
            .first()
        )
        if not completion or not completion.challenge_run:
            raise Locked("Free play is available only after completing this challenge trial.")
        return completion.challenge_run.variant

    @transaction.atomic
    def discard(self, *, run: ChallengeRun) -> bool:
        locked = ChallengeRun.objects.select_for_update().filter(pk=run.pk).first()
        if locked is None or locked.status != SESSION_STATUS_STARTED:
            return False
        locked.delete()
        return True

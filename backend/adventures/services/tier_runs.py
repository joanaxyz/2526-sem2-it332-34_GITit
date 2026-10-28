from django.db import IntegrityError, transaction
from django.utils import timezone

from adventures.models import AdventureLevelTier, AdventureLevelTierProgress, AdventureLevelTierRun
from adventures.tier_scenarios import next_scenario, published_scenarios, replay_scenario
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Conflict, Locked
from common.runtime import discard_started_run
from progress.models import AdventureLevelTierCompletion

from .tier_budget import command_budget
from .tier_variants import TierVariantSelectionService

RUN_HYDRATE_SELECT_RELATED = (
    "tier",
    "tier__adventure_level",
    "tier__adventure_level__chapter",
    "tier__adventure_level__chapter__story",
    "current_scenario",
    "selected_variant",
    "selected_variant__scenario",
    "prior_run",
    "player",
)


class AdventureLevelTierRunService:
    """Mirrors challenges.services.runs.ChallengeRunService for the
    AdventureLevelTier surface. New/parallel code only - the existing
    ChallengeRun lifecycles are not touched."""

    @staticmethod
    def hydrate_run(run: AdventureLevelTierRun | int, *, player=None) -> AdventureLevelTierRun:
        from django.db.models import Prefetch

        from practice.models import CommandStep

        queryset = AdventureLevelTierRun.objects.select_related(
            *RUN_HYDRATE_SELECT_RELATED
        ).prefetch_related(
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
        tier: AdventureLevelTier,
        source_entry_point: str,
        prior_run: AdventureLevelTierRun | None = None,
        is_replay: bool = False,
        transfer: bool = False,
    ) -> AdventureLevelTierRun:
        player.__class__.objects.select_for_update().get(pk=player.pk)

        from progress.services.checkpoints import (
            failed_attempts,
            record_exposure,
        )
        from progress.services.references import valid_ref

        if transfer:
            run = self._start_transfer(
                player=player, tier=tier, source_entry_point=source_entry_point
            )
            return self.hydrate_run(run)

        already_completed = AdventureLevelTierCompletion.objects.filter(
            player=player,
            tier=tier,
        ).exists()

        if prior_run is not None:
            prior_run = (
                AdventureLevelTierRun.objects.select_for_update()
                .select_related("tier")
                .get(pk=prior_run.pk, player=player)
            )
            if prior_run.tier_id != tier.id:
                raise Locked("Retry runs must use the same difficulty tier.")
            if prior_run.is_transfer:
                prior_run = None  # Further play starts a fresh, ungraded replay.

        # Best-effort variant-avoidance input for selector.select_variant
        # below - separate from `prior_run` (which stays a real, persisted
        # row or None, since it also drives chaining/retry_index/discard
        # logic further down). AdventureLevelTierRun rows are hard-deleted on
        # discard (see common.runtime.discard_started_run), so an
        # abandoned/never-solved attempt leaves no row behind even seconds
        # later - AdventureLevelTierProgress.last_shown_variant is the only
        # durable record of what the player was just looking at, and is set
        # on every start_run call below regardless of prior_run.
        selection_reference = prior_run
        if selection_reference is None and not is_replay and not already_completed:
            progress = AdventureLevelTierProgress.objects.filter(player=player, tier=tier).first()
            if progress and progress.last_shown_variant_id:
                selection_reference = AdventureLevelTierRun(
                    selected_variant=progress.last_shown_variant
                )

        # Replay semantics are authoritative on the server, mirroring
        # ChallengeRunService: once a tier has a completion (every published
        # scenario cleared), every new direct launch is free play regardless of a
        # stale or omitted client flag. Before that, a solved attempt clears
        # its scenario on AdventureLevelTierProgress even though the tier is not
        # complete yet - see AdventureLevelTierCommandProcessingService.
        is_replay = bool(is_replay or already_completed or (prior_run and prior_run.is_replay))
        if not is_replay:
            self._ensure_unlocked(player=player, tier=tier)

        active = self._active_run(player=player, tier=tier, for_update=True)
        if active and (not prior_run or active.id != prior_run.id):
            self.discard(run=active)

        # A fresh start (e.g. from the level page) right after a failure on
        # this tier is a retry of that failure, exactly as if the learner had
        # pressed Retry: same prior_run, retry_index and variant rotation.
        # Decided after the discard above, so an abandoned in-between run
        # blocks the link and a deleted empty one does not.
        if prior_run is None and not is_replay:
            prior_run = self._unretried_last_failure(player=player, tier=tier)
            if prior_run is not None:
                selection_reference = prior_run

        scenarios = published_scenarios(tier)
        if not scenarios:
            raise Locked("This difficulty tier has no published scenario.")
        if is_replay:
            if not already_completed:
                raise Locked("Free play is available only after completing this difficulty tier.")
            if prior_run is not None and prior_run.current_scenario_id in {w.id for w in scenarios}:
                # Retrying a free-play attempt stays on the scenario that was tried.
                scenario = next(w for w in scenarios if w.id == prior_run.current_scenario_id)
                selection_reference = prior_run
            else:
                scenario = replay_scenario(player=player, tier=tier, scenarios=scenarios)
                selection_reference = self._latest_run_on_scenario(player=player, scenario=scenario)
        else:
            scenario = (
                next_scenario(
                    scenarios,
                    AdventureLevelTierProgress.objects.filter(player=player, tier=tier).first(),
                )
                or scenarios[0]
            )
        # A run from another scenario says nothing about which of this scenario's
        # variants the learner has just seen.
        if (
            selection_reference is not None
            and selection_reference.selected_variant.scenario_id != scenario.id
        ):
            selection_reference = None

        selector = TierVariantSelectionService()
        published_variants = selector._published_variants(scenario)
        tried_keys = (
            selector._tried_variant_keys(player=player, scenario=scenario)
            if selection_reference
            else set()
        )
        variant = selector.select_variant(
            player=player,
            scenario=scenario,
            prior_run=selection_reference,
            published_variants=published_variants,
            tried_variant_keys=tried_keys,
        )
        if variant is None:
            raise Locked("This difficulty tier has no published variants.")

        # Mirrors the old app's ScenarioSession.changed_variant: only
        # meaningful for a real new attempt, not free play.
        changed_variant = bool(
            not is_replay
            and selection_reference
            and selector.changed_between(
                prior=selection_reference.selected_variant, current=variant
            )
        )

        if not is_replay:
            progress, created = AdventureLevelTierProgress.objects.get_or_create(
                player=player,
                tier=tier,
                defaults={"exposure_complete": not tier.runs.filter(player=player).exists()},
            )
            progress.last_shown_variant = variant
            progress.save(update_fields=["last_shown_variant", "updated_at"])

        retry_index = prior_run.retry_index + 1 if is_replay and prior_run else 0
        # Playing again after a clear starts a fresh scoring attempt. Failed
        # replays still extend their retry chain for star grading.
        if is_replay and prior_run and prior_run.status == SESSION_STATUS_COMPLETED:
            retry_index = 0
        prior_reference = prior_run
        if prior_run and prior_run.status == SESSION_STATUS_STARTED:
            # "Start over" mid-run: the old run is abandoned (or deleted when
            # empty) and never becomes the new run's prior - the same chain
            # shape as when the old run was always deleted.
            self.discard(run=prior_run)
            prior_reference = None
        elif prior_run and prior_run.status == SESSION_STATUS_ABANDONED:
            prior_reference = None
        if not is_replay:
            retry_index = failed_attempts(player_id=player.id, tier_id=tier.id)

        # Revised scenario-bank budgets are authored per variant. Older scenarios
        # still fall back to their shared budget. A run's star budget must be
        # at least 1 because of the database constraint and to leave read-only
        # scenarios one command of room.
        min_counted, max_counted = command_budget(variant)

        try:
            run = AdventureLevelTierRun.objects.create(
                player=player,
                tier=tier,
                current_scenario=scenario,
                selected_variant=variant,
                prior_run=prior_reference,
                source_entry_point=source_entry_point,
                is_replay=is_replay,
                ref_count=valid_ref(variant),
                ref_hash=variant.ref_hash if valid_ref(variant) is not None else "",
                assess_diag=variant.assess_diag,
                changed_variant=changed_variant,
                retry_index=retry_index,
                min_counted_commands=min_counted,
                max_counted_commands=max_counted,
                repository_state=variant.initial_state,
            )
        except IntegrityError as exc:
            raise Conflict("An active run already exists for this difficulty tier.") from exc
        record_exposure(run)
        return self.hydrate_run(run)

    def _start_transfer(self, *, player, tier, source_entry_point):
        """Launch the sole assessed transfer run under the normal player lock."""
        from progress.models import KpiCheckpoint
        from progress.services.checkpoints import assign_transfer, record_exposure, transfer_ready

        if not AdventureLevelTierCompletion.objects.filter(player=player, tier=tier).exists():
            raise Locked("Master this tier before starting its transfer checkpoint.")
        checkpoint = (
            # Lock only the checkpoint row: Postgres refuses FOR UPDATE on the
            # nullable side of the run/variant outer joins.
            KpiCheckpoint.objects.select_for_update(of=("self",))
            .filter(
                player=player,
                tier=tier,
                kind=KpiCheckpoint.Kind.TRANSFER,
            )
            .select_related("variant__scenario", "run")
            .first()
        )
        if checkpoint is None:
            checkpoint = assign_transfer(player=player, tier=tier)
        if checkpoint is None:
            raise Locked("No validated unseen transfer checkpoint is available for this tier.")
        if checkpoint.ended_at is None and not transfer_ready(checkpoint):
            raise Locked(
                "This checkpoint's content or novelty evidence changed; it cannot be assessed."
            )
        if checkpoint.run_id:
            if checkpoint.run.status == SESSION_STATUS_STARTED:
                return checkpoint.run  # Duplicate mount resumes the very same assessment.
            raise Locked("This transfer result is already recorded. Continue with free practice.")
        variant = checkpoint.variant
        active = self._active_run(player=player, tier=tier, for_update=True)
        if active:
            self.discard(run=active)
        budget, limit = command_budget(variant)
        run = AdventureLevelTierRun.objects.create(
            player=player,
            tier=tier,
            current_scenario=variant.scenario,
            selected_variant=variant,
            source_entry_point=source_entry_point,
            is_transfer=True,
            ref_count=variant.ref_count,
            ref_hash=variant.ref_hash,
            assess_diag=variant.assess_diag,
            min_counted_commands=budget,
            max_counted_commands=limit,
            repository_state=variant.initial_state,
        )
        checkpoint.run = run
        checkpoint.save(update_fields=["run"])
        record_exposure(run)
        return run

    def _unretried_last_failure(self, *, player, tier: AdventureLevelTier):
        """The learner's most recent run on this tier, if it failed and nothing
        has retried it yet; otherwise None.

        Not linked when the most recent run completed or was abandoned (any
        run after a failure means it is not the latest), when it was a replay,
        or when some run already has it as prior_run (never linked twice).
        """
        latest = (
            AdventureLevelTierRun.objects.select_for_update()
            .select_related("selected_variant")
            .filter(player=player, tier=tier)
            .order_by("-started_at", "-id")
            .first()
        )
        if latest is None or latest.status != SESSION_STATUS_FAILED or latest.is_replay:
            return None
        if latest.retry_runs.exists():
            return None
        return latest

    def _active_run(self, *, player, tier: AdventureLevelTier, for_update: bool = False):
        queryset = AdventureLevelTierRun.objects.filter(
            player=player,
            tier=tier,
            status=SESSION_STATUS_STARTED,
        )
        if for_update:
            queryset = queryset.select_for_update()
        return queryset.first()

    def _ensure_unlocked(self, *, player, tier: AdventureLevelTier) -> None:
        if tier.difficulty == DIFFICULTY_EASY:
            return
        previous_difficulty = (
            DIFFICULTY_EASY if tier.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
        )
        previous_tier = AdventureLevelTier.objects.filter(
            adventure_level_id=tier.adventure_level_id,
            difficulty=previous_difficulty,
            is_published=True,
        ).first()
        if (
            not previous_tier
            or not AdventureLevelTierCompletion.objects.filter(
                player=player,
                tier=previous_tier,
            ).exists()
        ):
            raise Locked("This difficulty tier is locked until the previous tier is completed.")

    @staticmethod
    def _latest_run_on_scenario(*, player, scenario):
        return (
            AdventureLevelTierRun.objects.select_related("selected_variant")
            .filter(player=player, current_scenario=scenario)
            .order_by("-started_at", "-id")
            .first()
        )

    @transaction.atomic
    def discard(self, *, run: AdventureLevelTierRun) -> bool:
        """End a still-active run the learner is leaving.

        Every trigger goes through here: the exit button, navigating away,
        "start over", and a new start on the same tier replacing an active run
        (including one left open by a closed tab). A run with at least one
        submitted command is kept as ABANDONED, so it counts as a started
        session that did not succeed; a run with no commands is deleted, since
        it carries no learning evidence (an accidental open or a double
        mount). Returns False when the run had already ended.
        """
        locked = AdventureLevelTierRun.objects.select_for_update().filter(pk=run.pk).first()
        if locked is None or locked.status != SESSION_STATUS_STARTED:
            return False
        if not locked.steps.exists() and not locked.is_transfer:
            return discard_started_run(locked)
        locked.status = SESSION_STATUS_ABANDONED
        locked.ended_at = timezone.now()
        locked.save(update_fields=["status", "ended_at"])
        if locked.is_transfer:
            from progress.services.checkpoints import finish_transfer

            finish_transfer(locked)
        return True

"""Adventure run orchestration.

An adventure run is one playable `AdventureLevel`, walked as an ordered sequence
of `AdventureWave` problems. Each wave selects its own variant; the run completes
only when the last wave is cleared. Chapters order adventure levels for
unlocks and mastery targets, but the runtime never walks a whole chapter as
one continuous session.
"""

from collections import Counter

from django.db import IntegrityError, transaction
from django.utils import timezone

from adventures.models import (
    AdventureLevel,
    AdventureRun,
    AdventureRunWave,
    AdventureWave,
    SkillMastery,
)
from adventures.progression import select_wave_variant
from adventures.scoring import apply_library_penalty
from adventures.scoring import stars as compute_stars
from common.constants import (
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Conflict, Locked
from curriculum.models import CommandForm
from progress.chests import ChapterChestService
from progress.models import AdventureLevelCompletion
from progress.wallet import WalletService

from .selectors import form_solve_targets, ordered_waves_for


class AdventureRunService:
    @transaction.atomic
    def start_run(self, *, player, level: AdventureLevel) -> AdventureRun:
        if not level.is_published:
            raise Locked("That level is not available.")

        # Serialize starts per player. The partial unique constraint on the run
        # table is the final safety net for databases where row locking is weak.
        player.__class__.objects.select_for_update().get(pk=player.pk)
        active = (
            AdventureRun.objects.select_for_update()
            .filter(player=player, level=level, status=SESSION_STATUS_STARTED)
            .select_related("level", "level__chapter", "current_wave", "selected_variant")
            .order_by("-id")
            .first()
        )
        if active:
            self.discard(run=active)

        waves = ordered_waves_for(level)
        if not waves:
            raise Locked("This level has no published waves.")
        first_wave = waves[0]
        variant = select_wave_variant(player=player, wave=first_wave)
        if variant is None:
            raise Locked("This level has no published variants.")
        is_replay = AdventureLevelCompletion.objects.filter(
            player=player,
            adventure_level=level,
        ).exists()
        try:
            run = AdventureRun.objects.create(
                player=player,
                level=level,
                current_wave=first_wave,
                selected_variant=variant,
                is_replay=is_replay,
                repository_state=variant.initial_state,
            )
        except IntegrityError as exc:
            raise Conflict("An active run already exists for this level.") from exc
        AdventureRunWave.objects.create(run=run, wave=first_wave, selected_variant=variant)
        return run


    def current_attempt(self, *, run: AdventureRun) -> AdventureRun | None:
        return run if run.status == SESSION_STATUS_STARTED else None

    def _is_perfect_score_eligible(self, *, attempt: AdventureRun) -> bool:
        if attempt.is_replay:
            return not AdventureLevelCompletion.objects.filter(
                player=attempt.player,
                adventure_level=attempt.level,
                stars__gte=3,
            ).exists()
        return not AdventureRun.objects.filter(
            player=attempt.player,
            level=attempt.level,
            is_replay=False,
            status__in=(SESSION_STATUS_FAILED, SESSION_STATUS_COMPLETED),
        ).exclude(pk=attempt.pk).exists()

    @transaction.atomic(savepoint=False)
    def record_wave_outcome(
        self,
        *,
        attempt: AdventureRun,
        solved: bool,
        defeated: bool,
        counted_command_count: int,
        command_count: int,
        repository_state: dict | None = None,
    ) -> dict:
        """Resolve one wave's outcome, advancing to the next wave or finishing the
        level. Returns ``{"advanced": bool, "completed": bool}``."""
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already been scored.")
        if not solved and not defeated:
            return {"advanced": False, "completed": False}

        wave = attempt.current_wave
        perfect_score_eligible = self._is_perfect_score_eligible(attempt=attempt)
        if repository_state is not None:
            attempt.repository_state = repository_state

        run_wave = AdventureRunWave.objects.filter(run=attempt, wave=wave).first()

        if defeated and not solved:
            if run_wave is not None:
                run_wave.command_count = command_count
                run_wave.counted_command_count = counted_command_count
                run_wave.save(update_fields=["command_count", "counted_command_count"])
            attempt.status = SESSION_STATUS_FAILED
            attempt.completed_at = timezone.now()
            attempt.command_count = command_count
            attempt.counted_command_count = counted_command_count
            attempt.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "command_count",
                    "counted_command_count",
                    "repository_state",
                ]
            )
            return {"advanced": False, "completed": True}

        earned = compute_stars(
            solved=True,
            counted_commands=counted_command_count,
            budget=wave.min_counted_commands,
            first_try=perfect_score_eligible,
        )
        if run_wave is not None:
            run_wave.status = SESSION_STATUS_COMPLETED
            run_wave.stars = earned
            run_wave.command_count = command_count
            run_wave.counted_command_count = counted_command_count
            run_wave.completed_at = timezone.now()
            run_wave.save(
                update_fields=[
                    "status",
                    "stars",
                    "command_count",
                    "counted_command_count",
                    "completed_at",
                ]
            )

        next_wave = (
            attempt.level.waves.filter(is_published=True, sort_order__gt=wave.sort_order)
            .order_by("sort_order", "id")
            .first()
        )
        if next_wave is not None:
            variant = select_wave_variant(player=attempt.player, wave=next_wave)
            if variant is None:
                raise Locked("The next wave has no published variants.")
            attempt.current_wave = next_wave
            attempt.selected_variant = variant
            attempt.repository_state = variant.initial_state
            attempt.command_count = 0
            attempt.counted_command_count = 0
            attempt.save(
                update_fields=[
                    "current_wave",
                    "selected_variant",
                    "repository_state",
                    "command_count",
                    "counted_command_count",
                ]
            )
            AdventureRunWave.objects.get_or_create(
                run=attempt,
                wave=next_wave,
                defaults={"selected_variant": variant},
            )
            return {"advanced": True, "completed": False}

        # Last wave cleared - the level is complete.
        cleared = list(
            AdventureRunWave.objects.filter(run=attempt, status=SESSION_STATUS_COMPLETED)
        )
        level_stars = apply_library_penalty(
            stars=min((rw.stars for rw in cleared), default=earned),
            library_opened=attempt.library_opened,
        )
        attempt.stars = level_stars
        attempt.command_count = command_count
        attempt.counted_command_count = counted_command_count
        attempt.status = SESSION_STATUS_COMPLETED
        attempt.completed_at = timezone.now()
        if not attempt.is_replay:
            attempt.passed_at = attempt.completed_at
            self._credit_mastery(player=attempt.player, level=attempt.level)
            completion, created = AdventureLevelCompletion.objects.get_or_create(
                player=attempt.player,
                adventure_level=attempt.level,
                defaults={
                    "adventure_run": attempt,
                    "stars": level_stars,
                    "counted_action_total": counted_command_count,
                },
            )
            if not created and level_stars > completion.stars:
                completion.adventure_run = attempt
                completion.stars = level_stars
                completion.counted_action_total = counted_command_count
                completion.completed_at = attempt.completed_at
                completion.save(
                    update_fields=[
                        "adventure_run",
                        "stars",
                        "counted_action_total",
                        "completed_at",
                    ]
                )
            self._all_required_levels_complete(player=attempt.player, adventure=attempt.level)
            # Authored level reward; the ledger award_key keeps it once-per-level.
            if attempt.level.reward_coins:
                WalletService().award(
                    player=attempt.player,
                    amount=attempt.level.reward_coins,
                    reason="adventure_level_reward",
                    award_key=f"adventure-level-reward:{attempt.level_id}",
                )
            ChapterChestService().award_chests(player=attempt.player, chapter=attempt.level.chapter)
        else:
            completion = AdventureLevelCompletion.objects.filter(
                player=attempt.player,
                adventure_level=attempt.level,
            ).first()
            if completion is not None and level_stars > completion.stars:
                completion.adventure_run = attempt
                completion.stars = level_stars
                completion.counted_action_total = counted_command_count
                completion.completed_at = attempt.completed_at
                completion.save(
                    update_fields=[
                        "adventure_run",
                        "stars",
                        "counted_action_total",
                        "completed_at",
                    ]
                )
        attempt.save(
            update_fields=[
                "stars",
                "command_count",
                "counted_command_count",
                "status",
                "completed_at",
                "passed_at",
                "repository_state",
            ]
        )
        return {"advanced": False, "completed": True}

    @transaction.atomic
    def record_library_opened(self, *, run: AdventureRun) -> AdventureRun:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This run has no active command library.")
        if not run.library_opened:
            run.library_opened = True
            run.save(update_fields=["library_opened"])
        return run

    def _credit_mastery(self, *, player, level: AdventureLevel) -> bool:
        # Each wave in the cleared level counts as one distinct solve for every
        # form it exercises, mirroring the per-wave mastery targets.
        wave_counts = Counter(
            form_id
            for form_id in AdventureWave.objects.filter(
                level=level, is_published=True
            ).values_list("command_forms", flat=True)
            if form_id is not None
        )
        if not wave_counts:
            return False
        targets = form_solve_targets(set(wave_counts))
        newly_learned = False
        for form in CommandForm.objects.filter(id__in=wave_counts):
            row, _created = SkillMastery.objects.get_or_create(player=player, command_form=form)
            if row.learned_at is None:
                row.learned_at = timezone.now()
                newly_learned = True
            row.solves += wave_counts[form.id]
            row.mastered = row.solves >= targets.get(form.id, 1)
            row.save(update_fields=["solves", "mastered", "learned_at", "updated_at"])
        return newly_learned

    def _all_required_levels_complete(self, *, player, adventure: AdventureLevel) -> bool:
        required_ids = set(
            AdventureLevel.objects.filter(
                chapter_id=adventure.chapter_id,
                is_published=True,
                is_required=True,
            ).values_list("id", flat=True)
        )
        if not required_ids:
            return False
        completed_ids = set(
            AdventureLevelCompletion.objects.filter(
                player=player,
                adventure_level_id__in=required_ids,
            ).values_list("adventure_level_id", flat=True)
        )
        return required_ids <= completed_ids


    @transaction.atomic
    def discard(self, *, run: AdventureRun) -> bool:
        locked = AdventureRun.objects.select_for_update().filter(pk=run.pk).first()
        if locked is None or locked.status != SESSION_STATUS_STARTED:
            return False
        locked.delete()
        return True

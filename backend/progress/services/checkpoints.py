"""First-result persistence, separate from mutable best-star completions."""

from django.utils import timezone

from adventures.models import AdventureLevelTierProgress, AdventureLevelTierRun
from common.constants import (
    COMMAND_DIAGNOSTIC,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from progress.models import KpiCheckpoint, KpiExposure

from .references import ref_hash, state_key, valid_ref


def failed_attempts(*, player_id, tier_id, before=None, replay=False) -> int:
    runs = AdventureLevelTierRun.objects.filter(
        player_id=player_id,
        tier_id=tier_id,
        is_replay=replay,
        is_transfer=False,
    )
    if before is not None:
        runs = runs.filter(ended_at__lte=before)
    return (
        runs.filter(
            status=SESSION_STATUS_FAILED,
        ).count()
        + runs.filter(
            status=SESSION_STATUS_ABANDONED,
            steps__isnull=False,
        )
        .distinct()
        .count()
    )


def record_exposure(run) -> None:
    # Called within the start transaction; survives even an empty discard.
    KpiExposure.objects.get_or_create(
        player_id=run.player_id,
        variant=run.selected_variant,
        state_key=state_key(run.selected_variant),
    )


def actual_count(run) -> int:
    count = run.counted_action_total
    if run.assess_diag:
        count += run.steps.filter(
            command_classification=COMMAND_DIAGNOSTIC,
            normalized_command__startswith="git ",
        ).count()
    return count


def record_mastery(run) -> None:
    KpiCheckpoint.objects.get_or_create(
        player_id=run.player_id,
        tier_id=run.tier_id,
        kind=KpiCheckpoint.Kind.CAR,
        defaults={
            "run": run,
            "variant": run.selected_variant,
            "ref_count": run.ref_count,
            "ref_hash": run.ref_hash,
            "actual": actual_count(run),
            "passed": True,
            "ended_at": run.ended_at,
            "retries": failed_attempts(
                player_id=run.player_id,
                tier_id=run.tier_id,
                before=run.ended_at,
            ),
        },
    )
    assign_transfer(player=run.player, tier=run.tier)


def assign_transfer(*, player, tier):
    if tier.adventure_level.chapter.number not in (3, 4):
        return None
    existing = KpiCheckpoint.objects.filter(player=player, tier=tier, kind="transfer").first()
    if existing is not None:
        return existing
    # Any legacy exposure gap prevents a claim of novelty. New cohorts have
    # complete tracking from their first launch; old histories are not guessed.
    progress = AdventureLevelTierProgress.objects.filter(player=player, tier=tier).first()
    if not progress or not progress.exposure_complete:
        return None
    if AdventureLevelTierProgress.objects.filter(player=player, exposure_complete=False).exists():
        return None
    seen = set(KpiExposure.objects.filter(player=player).values_list("state_key", flat=True))
    seen_ids = set(KpiExposure.objects.filter(player=player).values_list("variant_id", flat=True))
    # A preserved run without exposure evidence is another legacy gap.
    if (
        AdventureLevelTierRun.objects.filter(player=player)
        .exclude(selected_variant_id__in=seen_ids)
        .exists()
    ):
        return None
    scenario = tier.scenarios.filter(is_published=True).order_by("sort_order", "id").first()
    if scenario is None:
        return None
    for variant in scenario.variants.filter(
        is_published=True,
        is_transfer=True,
    ).order_by("id"):
        if (
            not variant.transfer_note.strip()
            or valid_ref(variant) is None
            or variant.id in seen_ids
            or state_key(variant) in seen
        ):
            continue
        checkpoint, _ = KpiCheckpoint.objects.get_or_create(
            player=player,
            tier=tier,
            kind=KpiCheckpoint.Kind.TRANSFER,
            defaults={
                "variant": variant,
                "ref_count": variant.ref_count,
                "ref_hash": variant.ref_hash,
            },
        )
        return checkpoint
    return None


def transfer_ready(point, *, seen=None) -> bool:
    """A pending assignment can launch only with unchanged, unseen content."""
    variant = point.variant
    if (
        variant is None
        or not variant.is_published
        or not variant.scenario.is_published
        or not variant.is_transfer
        or not variant.transfer_note.strip()
        or valid_ref(variant) is None
        or variant.ref_hash != point.ref_hash
    ):
        return False
    if point.run_id:
        return True
    key = state_key(variant)
    return (
        key not in seen
        if seen is not None
        else not KpiExposure.objects.filter(
            player_id=point.player_id,
            state_key=key,
        ).exists()
    )


def finish_transfer(run) -> None:
    point = KpiCheckpoint.objects.filter(run=run, ended_at__isnull=True).first()
    if point is None:
        return
    valid = bool(run.ref_hash and run.ref_hash == point.ref_hash == ref_hash(run.selected_variant))
    KpiCheckpoint.objects.filter(pk=point.pk, ended_at__isnull=True).update(
        passed=run.status == SESSION_STATUS_COMPLETED if valid else None,
        ref_count=point.ref_count if valid else None,
        ref_hash=point.ref_hash if valid else "",
        actual=actual_count(run),
        ended_at=run.ended_at or timezone.now(),
    )

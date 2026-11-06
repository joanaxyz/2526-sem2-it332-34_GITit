"""First-result persistence, separate from mutable best-star completions."""

from django.utils import timezone

from adventures.models import AdventureLevelTierProgress, AdventureLevelTierRun
from common.constants import (
    COMMAND_DIAGNOSTIC,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiExposure
from progress.objectives import transfer_expected
from progress.wallet import WalletService
from progress.xp import XpService

from .references import ref_hash, state_key, valid_ref
from .transfer_policy import (
    completed_practice_levels,
    is_current_transfer,
    practice_ready,
    prerequisite_levels,
    study_transfer_pins,
)

# Paid in GitCoins and XP alike. A first-run clear earns the full reward; a
# learner who missed it can still earn the smaller one by clearing it in practice.
TRANSFER_REWARD = 150
TRANSFER_PRACTICE_REWARD = 50


def transfer_award_key(tier_id) -> str:
    return f"transfer:{tier_id}"


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
    if run.tier.difficulty == "hard":
        # A learner may master a dependent level first. Finishing its explicitly
        # required practice later must make the existing Hard completion usable.
        for completion in (
            AdventureLevelTierCompletion.objects.filter(
                player_id=run.player_id,
                tier__difficulty="hard",
                tier__adventure_level__chapter_id=run.tier.adventure_level.chapter_id,
            )
            .exclude(tier_id=run.tier_id)
            .select_related("tier__adventure_level__chapter")
        ):
            assign_transfer(player=run.player, tier=completion.tier)


def assign_transfer(*, player, tier):
    existing = KpiCheckpoint.objects.filter(player=player, tier=tier, kind="transfer").first()
    if existing is not None:
        return existing
    variant = eligible_transfer_variant(player=player, tier=tier)
    if variant is None:
        return None
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


def eligible_transfer_variant(*, player, tier):
    """Read-only eligibility shared by live assignment and backfill preview."""
    pins = study_transfer_pins([player.id], [tier.id])[player.id, tier.id]
    if len(pins) > 1:
        # Preserve mastery without arbitrarily choosing a conflicting version.
        return None
    if not pins and not transfer_expected(tier.adventure_level.chapter.number, tier.difficulty):
        return None
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
    pinned = next(iter(pins), None)
    for variant in scenario.variants.filter(
        is_published=True,
        is_transfer=True,
    ).order_by("id"):
        if pinned:
            if (variant.id, variant.ref_hash, variant.ref_count) != pinned:
                continue
        elif not is_current_transfer(variant):
            continue
        if (
            not variant.transfer_note.strip()
            or valid_ref(variant) is None
            or variant.id in seen_ids
            or state_key(variant) in seen
        ):
            continue
        if prerequisite_levels(variant) and not practice_ready(
            variant, completed_practice_levels([player.id])[player.id]
        ):
            continue
        return variant
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


def pending_transfer(*, player_id, tier_id):
    """The learner's launchable transfer checkpoint on this tier, if any."""
    point = (
        KpiCheckpoint.objects.filter(
            player_id=player_id, tier_id=tier_id, kind="transfer", ended_at__isnull=True
        )
        .select_related("variant__scenario")
        .first()
    )
    return point if point and transfer_ready(point) else None


def transfer_rows(*, player, tier_ids) -> dict[int, dict]:
    """The level-node state of each assigned checkpoint.

    An unassigned tier has no entry, which keeps its row hidden until Hard is
    cleared. So does a checkpoint that could not open. The recorded result itself
    stays out of this: the node says it is done, not how it went.
    """
    rows = {}
    for point in KpiCheckpoint.objects.filter(
        player=player, tier_id__in=tier_ids, kind="transfer"
    ).select_related("variant__scenario"):
        if point.ended_at is not None:
            if point.variant.is_published and point.variant.scenario.is_published:
                rows[point.tier_id] = {"status": "recorded", "run_id": None}
        elif transfer_ready(point):
            rows[point.tier_id] = {
                "status": "in_progress" if point.run_id else "ready",
                "run_id": point.run_id,
            }
    return rows


def award_transfer_reward(run) -> dict | None:
    """Reward a cleared checkpoint, once per tier, whichever run cleared it first.

    Both runs share one award key, so practice after a first-run clear pays nothing.
    """
    amount = TRANSFER_PRACTICE_REWARD if run.is_replay else TRANSFER_REWARD
    key = transfer_award_key(run.tier_id)
    coins = WalletService().award(
        player=run.player, amount=amount, reason="transfer_checkpoint_reward", award_key=key
    )
    xp = XpService().award(
        player=run.player, amount=amount, reason="transfer_checkpoint", award_key=key
    )
    if not coins and not xp:
        return None
    return {
        "first_level_clear": False,
        "coins_awarded": amount if coins else 0,
        "xp_awarded": amount if xp else 0,
        "chapter_chests_awarded": [],
    }


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

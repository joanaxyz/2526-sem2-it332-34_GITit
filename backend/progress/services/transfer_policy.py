"""Current content selection and explicitly required practice for checkpoints.

Pinned assignments may use retired versions; only new selection reads the
current predicate. No runtime code imports the curriculum seed registry.
"""

from collections import defaultdict

from django.utils import timezone

from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiStudy
from progress.objectives import transfer_expected

CHECKPOINT_STUDY_POLICY = "mastery-kpis-v2"


def is_current_transfer(variant):
    return bool(
        variant.is_published
        and variant.is_transfer
        and not (variant.parameter_context or {}).get("retired_transfer", False)
    )


def prerequisite_levels(variant):
    return frozenset((variant.parameter_context or {}).get("transfer_prerequisites", []))


def completed_practice_levels(player_ids, *, before=None):
    """Bulk-read Hard mastery; immutable CAR timestamps survive later replays."""
    result = defaultdict(set)
    scope = {
        "player_id__in": player_ids,
        "tier__difficulty": "hard",
        "tier__adventure_level__chapter__story__slug": "arcane-spire",
    }
    completions = AdventureLevelTierCompletion.objects.filter(**scope)
    points = KpiCheckpoint.objects.filter(**scope, kind="car", ended_at__isnull=False)
    if before:
        completions = completions.filter(completed_at__lt=before)
        points = points.filter(ended_at__lt=before)
    for query in (completions, points):
        for player_id, slug in query.values_list("player_id", "tier__adventure_level__slug"):
            result[player_id].add(slug)
    return result


def practice_ready(variant, completed_levels):
    return prerequisite_levels(variant) <= completed_levels


def reference_identity(reference):
    return reference["id"], reference["hash"], reference["count"]


def study_transfer_pins(player_ids, tier_ids):
    """Prospective manifests are assignments even before a checkpoint row exists.

    An expired/frozen study cannot reserve a learner's later live attempt. Keep
    conflicting active pins visible so callers refuse an arbitrary version.
    """
    pins = defaultdict(set)
    players, tiers = set(player_ids), set(tier_ids)
    for manifest in KpiStudy.objects.filter(
        frozen_at__isnull=True, cutoff__gte=timezone.now()
    ).values_list("manifest", flat=True):
        if manifest.get("policy") != CHECKPOINT_STUDY_POLICY:
            continue
        enrolled = players & set(manifest["players"])
        if not enrolled:
            continue
        for spec in manifest["tiers"]:
            expected = transfer_expected(spec["module"], spec["difficulty"])
            if expected and spec["id"] in tiers and spec.get("transfer"):
                for player_id in enrolled:
                    pins[player_id, spec["id"]].add(reference_identity(spec["transfer"]))
    return pins

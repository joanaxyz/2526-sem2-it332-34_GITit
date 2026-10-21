"""Prospective fixed assignments and participant-balanced cutoff reports."""

from collections import defaultdict
from math import isfinite

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from adventures.models import (
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from players.models import Player
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiExposure, KpiStudy

from .checkpoints import actual_count
from .mastery_metrics import KEYS, balanced, car_score, rate, rates, samples
from .references import state_key, valid_ref


def _reference(variant):
    if valid_ref(variant) is None:
        raise ValidationError(
            f"Validate the command reference for {variant.slug} before enrollment."
        )
    return {"id": variant.id, "hash": variant.ref_hash, "count": variant.ref_count}


def _available(variant, reference):
    if variant is None:
        return False
    scenario, tier = variant.scenario, variant.scenario.tier
    level = tier.adventure_level
    return bool(
        variant.is_published
        and scenario.is_published
        and tier.is_published
        and level.is_published
        and level.chapter.is_published
        and valid_ref(variant) is not None
        and variant.ref_hash == reference["hash"]
    )


@transaction.atomic
def create_study(*, slug, player_ids, tier_ids, cutoff, weights=None):
    if not timezone.is_aware(cutoff) or cutoff <= timezone.now():
        raise ValidationError("A study needs a future cutoff with an explicit timezone.")
    players = list(Player.objects.filter(pk__in=player_ids, user__is_staff=False).order_by("id"))
    tiers = list(
        AdventureLevelTier.objects.filter(
            pk__in=tier_ids,
            is_published=True,
            adventure_level__is_published=True,
            adventure_level__is_required=True,
            adventure_level__chapter__story__slug="arcane-spire",
            adventure_level__chapter__number__in=(1, 2, 3, 4),
        )
        .select_related("adventure_level__chapter")
        .order_by("id")
    )
    if (
        not players
        or len(players) != len(set(player_ids))
        or not tiers
        or len(tiers) != len(set(tier_ids))
    ):
        raise ValidationError(
            "Supply explicit existing non-staff player IDs and required published tier IDs."
        )
    # Lock the same player rows as run launch, so assignment cannot race exposure.
    list(Player.objects.select_for_update().filter(pk__in=player_ids).order_by("id"))
    if (
        AdventureLevelTierRun.objects.filter(
            player_id__in=player_ids, tier_id__in=tier_ids
        ).exists()
        or KpiExposure.objects.filter(
            player_id__in=player_ids, variant__scenario__tier_id__in=tier_ids
        ).exists()
        or AdventureLevelTierProgress.objects.filter(
            player_id__in=player_ids, tier_id__in=tier_ids
        ).exists()
        or AdventureLevelTierCompletion.objects.filter(
            player_id__in=player_ids, tier_id__in=tier_ids
        ).exists()
    ):
        raise ValidationError(
            "Enroll before participants encounter their assigned tiers; use a new cohort."
        )
    specs = []
    for tier in tiers:
        scenarios = list(tier.scenarios.filter(is_published=True).order_by("sort_order", "id"))
        if not scenarios:
            raise ValidationError(f"Tier {tier.id} has no published exercise.")
        # Each scenario is cleared once, so mastery is the clear of the tier's last
        # scenario and any scenario's variant is evidence. Transfer stays reserved on
        # the first scenario.
        variants = list(
            AdventureLevelTierScenarioVariant.objects.filter(
                scenario__in=scenarios, is_published=True
            ).order_by("scenario__sort_order", "id")
        )
        ordinary = [v for v in variants if not v.is_transfer]
        if not ordinary:
            raise ValidationError(f"Tier {tier.id} has no ordinary practice variants.")
        transfer = next(
            (
                v
                for v in variants
                if v.is_transfer and v.transfer_note.strip() and v.scenario_id == scenarios[0].id
            ),
            None,
        )
        if transfer and any(state_key(v) == state_key(transfer) for v in ordinary):
            raise ValidationError(
                "A transfer checkpoint must differ from ordinary practice content."
            )
        missing = []
        for player in players:
            if AdventureLevelTierProgress.objects.filter(
                player=player, exposure_complete=False
            ).exists() or (
                transfer
                and KpiExposure.objects.filter(
                    player=player, state_key=state_key(transfer)
                ).exists()
            ):
                missing.append(player.id)
        specs.append(
            {
                "id": tier.id,
                "module": tier.adventure_level.chapter.number,
                "slug": tier.adventure_level.slug,
                "difficulty": tier.difficulty,
                "required": len(scenarios),
                "variants": [_reference(v) for v in ordinary],
                "transfer": _reference(transfer) if transfer else None,
                "transfer_missing": missing,
            }
        )
    modules = {str(s["module"]) for s in specs}
    weights = dict.fromkeys(sorted(modules), 1) if weights is None else weights
    if set(weights) != modules or any(
        not isinstance(w, (int, float)) or isinstance(w, bool) or not isfinite(w) or w <= 0
        for w in weights.values()
    ):
        raise ValidationError("Provide a positive predefined weight for each assigned module.")
    return KpiStudy.objects.create(
        slug=slug,
        cutoff=cutoff,
        manifest={
            "version": 1,
            "players": [p.id for p in players],
            "tiers": specs,
            "weights": weights,
            "assigned_at": timezone.now().isoformat(),
            "policy": "mastery-kpis-v1",
        },
    )


def _records(study):
    manifest = study.manifest
    specs = {s["id"]: s for s in manifest["tiers"]}
    content = {
        v.id: v
        for v in AdventureLevelTierScenarioVariant.objects.filter(
            scenario__tier_id__in=specs,
        ).select_related("scenario__tier__adventure_level__chapter")
    }
    scenario_counts = dict(
        AdventureLevelTierScenario.objects.filter(tier_id__in=specs, is_published=True)
        .values("tier_id")
        .annotate(count=Count("id"))
        .values_list("tier_id", "count")
    )
    grouped = defaultdict(list)
    for run in (
        AdventureLevelTierRun.objects.filter(
            player_id__in=manifest["players"],
            tier_id__in=specs,
            started_at__gte=manifest["assigned_at"],
            started_at__lte=study.cutoff,
            is_replay=False,
            is_transfer=False,
        )
        .prefetch_related("steps")
        .order_by("started_at", "id")
    ):
        grouped[run.player_id, run.tier_id].append(run)
    transfers = {
        (p.player_id, p.tier_id): p
        for p in KpiCheckpoint.objects.filter(
            player_id__in=manifest["players"],
            tier_id__in=specs,
            kind="transfer",
        )
    }
    records = []
    for player_id in manifest["players"]:
        for tier_id, spec in specs.items():
            attempts = grouped[player_id, tier_id]
            refs = {r["id"]: r for r in spec["variants"]}
            available = all(_available(content.get(ref_id), ref) for ref_id, ref in refs.items())
            # A reseed that changed the tier's scenarios changes what mastery means.
            requirements_match = scenario_counts.get(tier_id) == spec["required"] and all(
                ref_id in content for ref_id in refs
            )
            ended = [r for r in attempts if r.ended_at and r.ended_at <= study.cutoff]
            valid = [
                r
                for r in ended
                if r.selected_variant_id in refs
                and r.ref_hash == refs[r.selected_variant_id]["hash"]
            ]
            wins = [r for r in valid if r.status == "completed"]
            mastery = wins[spec["required"] - 1] if len(wins) >= spec["required"] else None
            missing = len(valid) != len(ended) or not available or not requirements_match
            score = (
                car_score(
                    passed=True,
                    target=refs[mastery.selected_variant_id]["count"],
                    actual=actual_count(mastery),
                )
                if mastery
                else None
                if missing
                else 0
            )
            checkpoint = transfers.get((player_id, tier_id))
            transfer_ref = spec["transfer"]
            transfer = None
            if (
                spec["module"] in (3, 4)
                and transfer_ref
                and player_id not in spec["transfer_missing"]
            ):
                variant = content.get(transfer_ref["id"])
                usable = bool(
                    _available(variant, transfer_ref)
                    and variant.is_transfer
                    and variant.transfer_note.strip()
                    and (mastery or (requirements_match and available))
                )
                if (
                    usable
                    and not (checkpoint and checkpoint.run_id)
                    and KpiExposure.objects.filter(
                        player_id=player_id,
                        state_key=state_key(variant),
                        seen_at__lte=study.cutoff,
                    ).exists()
                ):
                    usable = False
                transfer = 0 if usable else None
                if checkpoint and checkpoint.ended_at and checkpoint.ended_at <= study.cutoff:
                    if (
                        checkpoint.ref_hash != transfer_ref["hash"]
                        or checkpoint.variant_id != transfer_ref["id"]
                    ):
                        transfer = None
                    else:
                        transfer = int(checkpoint.passed is True)
            records.append(
                {
                    "player_id": player_id,
                    "tier_id": tier_id,
                    "module": spec["module"],
                    "slug": spec["slug"],
                    "difficulty": spec["difficulty"],
                    "mastered": mastery is not None,
                    "mastery_missing": mastery is None and missing,
                    "car": score,
                    "transfer": transfer,
                    "failures": sum(
                        r.ended_at <= mastery.ended_at
                        and (
                            r.status == "failed"
                            or (r.status == "abandoned" and bool(list(r.steps.all())))
                        )
                        for r in valid
                    )
                    if mastery
                    else 0,
                    "transfer_assigned": transfer_ref is not None
                    and player_id not in spec["transfer_missing"],
                    "attempted": bool(attempts),
                    "invalid_runs": len(ended) - len(valid),
                    "car_missing": score is None,
                    "transfer_missing": spec["module"] in (3, 4) and transfer is None,
                    "mastery_run": mastery.id if mastery else None,
                    "transfer_run": checkpoint.run_id if checkpoint else None,
                }
            )
    return records


def _weighted(records, weights):
    modules = {r["module"] for r in records}
    by_module = {n: rates([r for r in records if r["module"] == n]) for n in modules}
    result = {}
    for key in KEYS:
        if key == "retry_success_rate":
            continue  # Formal study evaluates the five official KPIs only.
        eligible = {n for n in modules if key != "rta" or n in (3, 4)}
        if key == "hlcr":
            eligible = {
                n
                for n in eligible
                if any(r["module"] == n and r["difficulty"] == "hard" for r in records)
            }
        values = [by_module[n][key]["value"] for n in eligible]
        result[key] = (
            None
            if not values or any(v is None for v in values)
            else round(
                sum(by_module[n][key]["value"] * weights[str(n)] for n in eligible)
                / sum(weights[str(n)] for n in eligible),
                2,
            )
        )
    return result


@transaction.atomic
def freeze_study(study):
    study = KpiStudy.objects.select_for_update().get(pk=study.pk)
    if study.frozen_at:
        return study.report
    if timezone.now() < study.cutoff:
        raise ValidationError("The evaluation cutoff has not been reached.")
    # Launches lock players; submissions lock runs. Wait for in-flight writes
    # before freezing timestamps so a pre-cutoff outcome cannot commit after
    # the report has already omitted it. Keep the same player -> run order.
    list(Player.objects.select_for_update().filter(pk__in=study.manifest["players"]).order_by("id"))
    list(
        AdventureLevelTierRun.objects.select_for_update()
        .filter(
            player_id__in=study.manifest["players"],
            tier_id__in=[spec["id"] for spec in study.manifest["tiers"]],
        )
        .order_by("id")
        .values_list("id", flat=True)
    )
    records = _records(study)
    participants = []
    for player_id in study.manifest["players"]:
        own = [r for r in records if r["player_id"] == player_id]
        participants.append(
            {
                "player_id": player_id,
                "kpis": _weighted(own, study.manifest["weights"]),
                "coverage": samples(own),
                "unattempted": sum(not r["attempted"] for r in own),
            }
        )
    kpis = {}
    for key in ("scr", "car", "hlcr", "arc", "rta"):
        values = [p["kpis"][key] for p in participants if p["kpis"][key] is not None]
        kpis[key] = rate(sum(values), len(values), average=True, unit="participants")
    modules = [
        {
            "number": n,
            "kpis": balanced([r for r in records if r["module"] == n], cohort=True),
            "coverage": samples([r for r in records if r["module"] == n]),
        }
        for n in sorted({r["module"] for r in records})
    ]
    report = {
        "study": study.slug,
        "cutoff": study.cutoff.isoformat(),
        "manifest": study.manifest,
        "kpis": kpis,
        "participants": participants,
        "modules": modules,
        "records": records,
        "coverage": samples(records),
        "unattempted": sum(not r["attempted"] for r in records),
    }
    study.report, study.frozen_at = report, timezone.now()
    study.save(update_fields=["report", "frozen_at"])
    return report

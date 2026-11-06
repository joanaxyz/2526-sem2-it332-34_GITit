"""Backfill offers checkpoints to existing Module 3-4 mastery without inventing exposure."""

import io
import json

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierProgress
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiExposure
from progress.services.references import ref_hash, state_key
from testing.kpi_fixtures import bundle


def checkpoint_bundle(user_model, module, username):
    result = bundle(user_model, module=module, username=username, required=1)
    # Distinct level content must be genuinely unseen across the learner's
    # whole history; changing a variant ID alone must not bypass that rule.
    for variant in result[3]:
        for field in ("initial_state", "target_state"):
            value = json.dumps(getattr(variant, field))
            for name in ("note.txt", "extra.txt"):
                value = value.replace(name, f"m{module}-{name}")
            setattr(variant, field, json.loads(value))
        variant.ref_hash = ref_hash(variant)
        variant.save(update_fields=["initial_state", "target_state", "ref_hash"])
    return result


@pytest.mark.django_db
def test_backfill_previews_then_assigns_only_unseen_complete_mastery_idempotently(
    django_user_model,
):
    ready, tier, _, variants = checkpoint_bundle(django_user_model, 3, "ready")
    gap, other, _, _ = checkpoint_bundle(django_user_model, 4, "gap")
    for player, mastered, complete in ((ready, tier, True), (gap, other, False)):
        AdventureLevelTierCompletion.objects.create(player=player, tier=mastered)
        AdventureLevelTierProgress.objects.create(
            player=player, tier=mastered, exposure_complete=complete
        )

    def invoke(apply=False):
        output = io.StringIO()
        call_command("assign_transfer_checkpoints", modules=[3, 4], apply=apply, stdout=output)
        return json.loads(output.getvalue())

    dry = invoke()
    assert dry["eligible"] == 1 and dry["created"] == 0 and dry["ineligible"] == 1
    assert not KpiCheckpoint.objects.filter(kind="transfer").exists()
    applied = invoke(True)
    assert applied["created"] == 1
    point = KpiCheckpoint.objects.get(player=ready, kind="transfer")
    repeated = invoke(True)
    assert repeated["created"] == 0
    assert KpiCheckpoint.objects.get(pk=point.pk).variant_id == point.variant_id
    assert not KpiCheckpoint.objects.filter(player=gap, kind="transfer").exists()
    # Even complete tracking cannot promise novelty once reserved content was seen.
    KpiCheckpoint.objects.filter(pk=point.pk).delete()
    KpiExposure.objects.create(player=ready, variant=variants[1], state_key=state_key(variants[1]))
    seen = invoke(True)
    assert seen["created"] == 0

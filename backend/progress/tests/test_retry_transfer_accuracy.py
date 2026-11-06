"""Transfer is explicitly assigned after practice, independent of initial failure."""

import pytest

from progress.models import KpiCheckpoint, KpiExposure
from progress.services import MetricsService
from testing.kpi_fixtures import bundle, end, start


def test_success_without_initial_failure_can_demonstrate_transfer(db, django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    end(start(player, tier))
    end(start(player, tier, transfer=True))
    assert MetricsService().performance_summary(player=player)["kpis"]["rta"]["value"] == 100


def test_failure_retry_does_not_implicitly_become_transfer(db, django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    failed = end(start(player, tier), passed=False)
    end(start(player, tier, prior_run=failed))
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["rta"]["value"] is None
    assert report["samples"]["transfer_pending"] == 1
    assert report["kpis"]["retry_success_rate"]["value"] == 100


@pytest.mark.parametrize("module", [1, 2])
def test_transfer_is_limited_to_modules_3_4(db, django_user_model, module):
    player, tier, _, _ = bundle(django_user_model, required=1, module=module)
    end(start(player, tier))
    assert not KpiCheckpoint.objects.filter(player=player, kind="transfer").exists()


def test_previously_exposed_equivalent_content_is_ineligible(db, django_user_model):
    from progress.services.references import state_key

    player, tier, _, variants = bundle(django_user_model, required=1)
    KpiExposure.objects.create(player=player, variant=variants[1], state_key=state_key(variants[1]))
    end(start(player, tier))
    assert not KpiCheckpoint.objects.filter(player=player, kind="transfer").exists()
    assert MetricsService().performance_summary(player=player)["samples"]["transfer_missing"] == 1

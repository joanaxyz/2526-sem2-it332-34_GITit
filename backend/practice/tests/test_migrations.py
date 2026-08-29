import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from practice.models import CommandStep
from testing.runtime_factories import create_stage_readme_challenge_run

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = ("practice", "0001_initial")
MIGRATE_TO = ("practice", "0002_commandstep_command_step_valid_counts")


def test_legacy_command_step_counts_are_normalized_before_constraint(
    django_user_model,
):
    fixture = create_stage_readme_challenge_run(django_user_model)
    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_FROM])
    old_apps = executor.loader.project_state([MIGRATE_FROM]).apps
    OldCommandStep = old_apps.get_model("practice", "CommandStep")
    step = OldCommandStep.objects.create(
        challenge_run_id=fixture.run.pk,
        command_text="git status",
        result_category="target_not_yet_matched",
        command_classification="diagnostic",
        attempt_number=0,
        counted_increment=4,
        counted_total_after=0,
    )

    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_TO])

    normalized = CommandStep.objects.get(pk=step.pk)
    assert normalized.attempt_number == 1
    assert normalized.counted_increment == 1
    assert normalized.counted_total_after == 1

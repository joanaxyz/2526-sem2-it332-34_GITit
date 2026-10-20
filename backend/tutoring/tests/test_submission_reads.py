"""Every query in a command submission is a database round trip the learner waits
for, so the tutor reads its tables once per submission."""

from collections import Counter
from copy import deepcopy

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from adventures.models import SkillMastery
from testing.frontend_execution import diagnostic_payload, frontend_execution_payload
from tutoring.tests.conftest import initialized_state

# Lock + insert + update + transaction, plus the tutor's history, catalog and
# feedback reads for the plan before the command and the one in the response.
SUBMISSION_QUERY_BUDGET = 16


def submit(client, run, command, execution):
    with CaptureQueriesContext(connection) as queries:
        response = client.post(
            f"/api/adventure-tier-runs/{run.id}/submit-command/",
            {"command": command, "execution": execution},
            format="json",
        )
    assert response.status_code == 200, response.data
    return response, [query["sql"] for query in queries.captured_queries]


def reads(sqls):
    tables = Counter()
    for sql in sqls:
        if sql.startswith("SELECT"):
            tables[sql.split(' FROM "', 1)[1].split('"', 1)[0]] += 1
    return tables


def test_a_command_reads_each_tutor_table_once(client, teaching_run):
    state = deepcopy(teaching_run.repository_state)
    response, sqls = submit(
        client,
        teaching_run,
        "git status",
        diagnostic_payload("git status", state) | {"client_run_revision": 0},
    )

    assert response.data["run"]["tutor"]["teaching_key"] == "git-init/current-directory"
    tables = reads(sqls)
    # The player and the run's feedback row come with the locked run.
    assert tables["players_player"] == 0
    assert tables["tutoring_pendingcommandintroduction"] == 0
    assert tables["tutoring_playercommandintroduction"] <= 1
    assert not [sql for sql in sqls if sql.startswith('DELETE FROM "tutoring_pending')]
    assert len(sqls) <= SUBMISSION_QUERY_BUDGET, "\n".join(sqls)


def test_the_response_plan_sees_the_command_just_recorded(client, teaching_run):
    # Discovering a skill the first time is a one-off celebration with its own
    # reads; measure the everyday path.
    for form in teaching_run.current_wave.command_forms.all():
        SkillMastery.objects.create(
            player=teaching_run.player, command_form=form, learned_at=timezone.now()
        )
    response, sqls = submit(
        client,
        teaching_run,
        "git init",
        frontend_execution_payload(
            "git init", initialized_state(teaching_run.repository_state), client_run_revision=0
        ),
    )

    tutor = response.data["run"]["tutor"]
    # Feedback on the introduced form, with its history read once for both plans.
    assert tutor["verdict"] == "correct"
    assert tutor["explanation"] == "That's the right command."
    assert reads(sqls)["tutoring_playercommandintroduction"] <= 1
    assert len(sqls) <= SUBMISSION_QUERY_BUDGET, "\n".join(sqls)

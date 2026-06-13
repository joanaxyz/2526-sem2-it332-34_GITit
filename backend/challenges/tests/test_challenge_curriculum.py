from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import AdventureLevel, AdventureRun, CommandAdventure
from challenges.models import Challenge, ChallengeLevel, ChallengeRun
from challenges.payloads import challenge_run_payload
from challenges.services import ChallengeRunService
from curriculum.models import CommandSkill, Storey, Tome
from curriculum.selectors import storey_content_page
from practice.context import ScenarioContextNormalizer
from practice.services import CommandProcessingService
from practice.visualization import RepositoryVisualizationService
from progress.models import LevelCompletion


def make_user(django_user_model, username: str = "student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def pass_adventure_for(user, storey):
    """Mark the storey's Command Adventure as passed so its EASY challenge unlocks.
    Challenge entry is now gated on passing the storey's adventure first."""
    adventure = CommandAdventure.objects.filter(storey=storey, is_published=True).first()
    if adventure is not None:
        AdventureRun.objects.create(
            user=user, command_adventure=adventure, passed_at=timezone.now()
        )


def test_seed_curriculum_v2_creates_feature_owned_content(db):
    call_command("seed_curriculum_v2")

    assert Tome.objects.filter(is_published=True).exists()
    assert not Storey.objects.filter(number=0).exists()
    assert CommandSkill.objects.filter(base_command="git add").exists()
    assert CommandAdventure.objects.filter(slug="tracking-changes-snapshots-command-adventure").exists()
    assert AdventureLevel.objects.filter(command_form__usage_form="git add <file>").exists()
    challenge = Challenge.objects.get(slug="stage-commit-switch")
    assert set(challenge.challenge_levels.values_list("difficulty", flat=True)) == {"easy", "medium", "hard"}


def test_storey_content_page_returns_canonical_sections(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    storey = Storey.objects.get(slug="tracking-changes-snapshots")
    challenge_storey = Challenge.objects.filter(is_published=True).order_by("id").first().storey

    adventure_page = storey_content_page(
        user=user,
        storey_id=storey.id,
        section="command_adventures",
    )
    skill_page = storey_content_page(
        user=user,
        storey_id=storey.id,
        section="command_skills",
        limit=1,
    )
    challenge_page = storey_content_page(
        user=user,
        storey_id=challenge_storey.id,
        section="challenges",
    )

    assert adventure_page["results"][0]["item_type"] == "command_adventure"
    assert "practice_kind" not in adventure_page["results"][0]
    assert "levels" not in adventure_page["results"][0]
    assert skill_page["results"][0]["item_type"] == "command_skill"
    assert skill_page["next_cursor"] is not None
    assert challenge_page["results"][0]["item_type"] == "challenge"
    assert "command_topics" not in challenge_page["results"][0]
    assert "active_run_id" in challenge_page["results"][0]["levels"][0]
    assert "active_session_id" not in challenge_page["results"][0]["levels"][0]


def test_challenge_run_payload_uses_challenge_and_storey_terms(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(challenge__slug="stage-commit-switch", difficulty="easy")
    pass_adventure_for(user, level.storey)

    run = ChallengeRunService().start_run(
        user=user,
        level=level,
        source_entry_point="tower_page",
    )
    payload = challenge_run_payload(run)

    assert payload["challenge"]["level_id"] == level.id
    assert payload["storey"]["id"] == level.storey.id
    assert payload["difficulty"] == "easy"
    assert payload["review_mode"] is False
    assert "practice_kind" not in payload
    assert "problem" not in payload
    assert "module" not in payload
    assert "tower" not in payload
    assert "sibling_levels" not in payload
    assert "level_id" not in payload["challenge"]


def test_challenge_run_http_lifecycle_retry_and_review(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(challenge__slug="stage-commit-switch", difficulty="easy")
    level.required_successful_attempts = 1
    level.save(update_fields=["required_successful_attempts"])
    pass_adventure_for(user, level.storey)
    client = APIClient()
    client.force_authenticate(user=user)

    start = client.post(f"/api/challenge-levels/{level.id}/runs/", {"source_entry_point": "tower_page"}, format="json")
    assert start.status_code == 201
    body = start.json()
    assert body["status"] == "started"
    assert body["challenge"]["level_id"] == level.id
    assert "practice_kind" not in body

    run = ChallengeRun.objects.get(id=body["id"])
    for command in run.variant.solution_commands:
        response = client.post(
            f"/api/challenge-runs/{run.id}/submit-command/",
            {"command": command},
            format="json",
        )
        assert response.status_code == 200
    run.refresh_from_db()
    assert run.status == "completed"
    assert LevelCompletion.objects.filter(user=user, challenge_level=level).exists()

    retry = client.post(f"/api/challenge-runs/{run.id}/retry/")
    assert retry.status_code == 201
    retry_body = retry.json()
    assert retry_body["status"] == "started"
    assert retry_body["challenge"]["level_id"] == level.id

    retry_run = ChallengeRun.objects.get(id=retry_body["id"])
    client.post(f"/api/challenge-runs/{retry_run.id}/finish/")
    review = client.post(
        f"/api/challenge-levels/{level.id}/runs/",
        {"source_entry_point": "review", "review": True},
        format="json",
    )
    assert review.status_code == 201
    assert review.json()["review_mode"] is True


def test_review_mode_is_gated_until_completion(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(challenge__slug="stage-commit-switch", difficulty="easy")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/challenge-levels/{level.id}/runs/",
        {"source_entry_point": "review", "review": True},
        format="json",
    )

    assert response.status_code == 423


def test_scenario_context_normalizer_strips_answers_and_evaluator_internals():
    context = ScenarioContextNormalizer().normalize(
        {
            "schema_version": 3,
            "story": "Reach the target.",
            "task": "Finish the handoff.",
            "details": [{"label": "File", "value": "app.py"}],
            # Anything outside the v3 whitelist must never reach the learner.
            "objective": {"checks": [{"requirement": {"head_branch": "secret-branch-xyz"}}]},
            "repository": {"current_state": ["app.py is staged."]},
            "solution_commands": ["git add app.py"],
            "required_commands": ["git add"],
            "evaluation_spec": {"state_requirements": {"staging_contains": ["app.py"]}},
        }
    )

    flattened = str(context).lower()
    assert "git add" not in flattened
    assert "evaluation_spec" not in flattened
    assert "secret-branch-xyz" not in flattened
    # The whole objective checklist lives on AdventureLevel.objective_checks
    # now; scenario_context is whitelist-only and never carries it. Repository
    # prose was dropped in v3 (the live panels already show that state).
    assert "objective" not in context
    assert "repository" not in context
    assert context["details"] == [{"label": "File", "value": "app.py"}]
    assert context["story"] == "Reach the target."
    assert context["task"] == "Finish the handoff."


def test_scenario_context_normalizer_falls_back_on_unknown_schema():
    context = ScenarioContextNormalizer().normalize(
        {"schema_version": 2, "brief": {"story": "Old shape."}},
        fallback_story="Reach the requested repository outcome cleanly.",
    )

    assert context == {
        "schema_version": 3,
        "story": "Reach the requested repository outcome cleanly.",
    }


def test_visualization_payload_keeps_commit_dag_without_extra_lenses():
    state = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "old"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {"app.py": "new"},
        "conflicts": [],
    }

    payload = RepositoryVisualizationService().snapshot(state)

    assert payload["schema_version"] == 2
    assert [commit["id"] for commit in payload["commit_dag"]["commits"]] == ["c0"]


def test_hard_challenge_payload_hides_expected_state(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(challenge__slug="stage-commit-switch", difficulty="hard")
    variant = level.challenge_variants.get(is_published=True)
    run = ChallengeRun.objects.create(
        user=user,
        storey=level.storey,
        challenge=level.challenge,
        challenge_level=level,
        challenge_variant=variant,
        source_entry_point="tower_page",
        difficulty=level.difficulty,
        command_budget_snapshot={
            "min_counted_commands": level.min_counted_commands,
            "max_counted_commands": level.max_counted_commands,
        },
        repository_state=variant.initial_state,
    )

    payload = challenge_run_payload(ChallengeRunService.hydrate_run(run))

    assert payload["scaffolding"]["expected_state"] is False
    assert payload["expected_state"] is None


def test_unsupported_command_skills_are_not_published(db):
    call_command("seed_curriculum_v2")

    published_commands = set(
        CommandSkill.objects.filter(is_published=True).values_list("base_command", flat=True)
    )

    assert published_commands == {"git init", "git status", "git add", "git commit", "git switch"}
    assert not Storey.objects.filter(slug="integrated-workflows", is_published=True).exists()
    assert not CommandSkill.objects.filter(base_command="git clone", is_published=True).exists()


def test_seed_curriculum_v2_validate_passes_for_published_content(db):
    call_command("seed_curriculum_v2", validate=True)


def test_status_challenge_completes_with_explicit_process_requirement(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(challenge__slug="wake-the-repository", difficulty="easy")
    pass_adventure_for(user, level.storey)
    run = ChallengeRunService().start_run(
        user=user,
        level=level,
        source_entry_point="tower_page",
    )

    result = CommandProcessingService().submit_command(run=run, command="git init")

    run.refresh_from_db()
    assert result["evaluation_result"] == "TargetMatched"
    assert run.status == "completed"
    assert ChallengeRun.objects.filter(user=user, challenge_level=level).count() == 1

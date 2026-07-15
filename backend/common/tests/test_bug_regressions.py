import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError

from accounts.services import TokenService
from adventures.models import AdventureLevel, AdventureRun
from authoring.models import STATUS_PUBLISHED, ContentDefinition
from authoring.services import ContentDefinitionService
from challenges.models import ChallengeLevel, ChallengeRun
from challenges.serializers import CommandSubmitSerializer
from challenges.services import ChallengeCommandProcessingService, ChallengeRunService
from common.api import api_exception_handler
from common.constants import SESSION_STATUS_COMPLETED
from payments.models import GitCoinPurchase
from payments.services import PaymentService
from players.services import get_or_create_player
from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion, Wallet


def _user(username: str):
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="Password123!",
    )


def _execution(**overrides):
    payload = {
        "processed": True,
        "next_state": {},
        "output": "",
        "normalized_command": "git status",
        "exit_code": 0,
        "diagnostic": True,
        "stdout": "",
        "stderr": "",
        "command_family": "status",
        "diagnostic_metadata": [],
        "client_run_revision": 0,
    }
    payload.update(overrides)
    return payload


def test_command_execution_serializer_rejects_loose_boolean_and_exit_code():
    loose_boolean = CommandSubmitSerializer(
        data={"command": "git status", "execution": _execution(processed="false")}
    )
    loose_exit = CommandSubmitSerializer(
        data={"command": "git status", "execution": _execution(exit_code="not-a-number")}
    )

    assert not loose_boolean.is_valid()
    assert "execution" in loose_boolean.errors
    assert not loose_exit.is_valid()
    assert "execution" in loose_exit.errors


def test_global_api_handler_translates_model_misses_to_404():
    response = api_exception_handler(get_user_model().DoesNotExist(), {})

    assert response is not None
    assert response.status_code == 404


@pytest.mark.django_db
def test_published_content_cannot_hide_definition_edit_behind_visibility():
    user = _user("publisher")
    content = ContentDefinition.objects.create(
        owner=user,
        kind="lesson",
        slug="published-lesson",
        title="Published lesson",
        visibility="private",
        status=STATUS_PUBLISHED,
        definition={"pages": [{"title": "Original", "blocks": []}]},
    )

    with pytest.raises(ValidationError):
        ContentDefinitionService().update(
            user=user,
            content=content,
            data={
                "visibility": "public",
                "definition": {"pages": [{"title": "Changed", "blocks": []}]},
            },
        )

    content.refresh_from_db()
    assert content.visibility == "private"
    assert content.definition["pages"][0]["title"] == "Original"


@pytest.mark.django_db
def test_active_run_constraints_and_completion_history_survive_deletion():
    call_command("seed_curriculum")
    player = get_or_create_player(_user("run-safety"))
    level = AdventureLevel.objects.filter(is_published=True).order_by("id").first()
    assert level is not None
    wave = level.waves.filter(is_published=True).order_by("sort_order", "id").first()
    assert wave is not None
    variant = wave.variants.filter(is_published=True).first()
    assert variant is not None
    run = AdventureRun.objects.create(
        player=player,
        level=level,
        current_wave=wave,
        selected_variant=variant,
        repository_state=variant.initial_state,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            AdventureRun.objects.create(
                player=player,
                level=level,
                current_wave=wave,
                selected_variant=variant,
                repository_state=variant.initial_state,
            )

    run.status = SESSION_STATUS_COMPLETED
    run.save(update_fields=["status"])
    completion = AdventureLevelCompletion.objects.create(
        player=player,
        adventure_level=level,
        adventure_run=run,
        stars=3,
    )
    run.delete()

    completion.refresh_from_db()
    assert completion.adventure_run_id is None
    assert completion.stars == 3


@pytest.mark.django_db
def test_completed_challenge_launch_is_server_derived_replay_and_cannot_lower_best_score():
    call_command("seed_curriculum")
    player = get_or_create_player(_user("replay-safety"))
    level = ChallengeLevel.objects.filter(
        is_published=True,
        trials__variants__is_published=True,
    ).order_by("id").first()
    assert level is not None
    trial = level.trials.filter(is_published=True).order_by("id").first()
    assert trial is not None
    variant = trial.variants.filter(is_published=True).first()
    assert variant is not None
    best_run = ChallengeRun.objects.create(
        player=player,
        challenge_trial=trial,
        selected_variant=variant,
        source_entry_point="level_page",
        status=SESSION_STATUS_COMPLETED,
        stars=3,
        counted_action_total=1,
        repository_state=variant.initial_state,
    )
    completion = ChallengeTrialCompletion.objects.create(
        player=player,
        challenge_trial=trial,
        challenge_run=best_run,
        stars=3,
        counted_action_total=1,
    )

    replay = ChallengeRunService().start_run(
        player=player,
        trial=trial,
        source_entry_point="level_page",
        is_replay=False,
    )
    assert replay.is_replay is True

    # Exercise the primary-completion update path directly with a worse run;
    # saved best progress must remain linked to the better result.
    replay.delete()
    worse_run = ChallengeRun.objects.create(
        player=player,
        challenge_trial=trial,
        selected_variant=variant,
        source_entry_point="level_page",
        retry_index=1,
        min_counted_commands=1,
        max_counted_commands=4,
        counted_action_total=4,
        repository_state=variant.initial_state,
    )
    ChallengeCommandProcessingService()._complete_run(worse_run)

    completion.refresh_from_db()
    assert completion.challenge_run_id == best_run.id
    assert completion.stars == 3
    assert completion.counted_action_total == 1


@pytest.mark.django_db
def test_payment_webhook_can_recover_missing_local_session_link():
    player = get_or_create_player(_user("payment-recovery"))

    PaymentService().handle_checkout_completed(
        session={
            "id": "cs_recovered_123",
            "metadata": {
                "player_id": str(player.id),
                "pack_slug": "starter",
            },
            "amount_total": 99,
            "currency": "usd",
        }
    )

    purchase = GitCoinPurchase.objects.get(stripe_session_id="cs_recovered_123")
    assert purchase.status == "paid"
    assert purchase.checkout_key == "recovered:cs_recovered_123"
    assert Wallet.objects.get(player=player).balance == 150


@pytest.mark.django_db
def test_refresh_rotation_is_single_use():
    user = _user("single-refresh")
    original = TokenService().issue_for_user(user)

    TokenService().refresh_access(original.refresh)

    with pytest.raises(TokenError):
        TokenService().refresh_access(original.refresh)

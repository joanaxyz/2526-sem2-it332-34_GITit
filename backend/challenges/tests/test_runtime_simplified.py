from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from challenges.models import ChallengeLevel, ChallengeRun
from curriculum.selectors import challenge_levels_access_payload
from players.services import get_or_create_player
from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion


def make_user(django_user_model, username="challenger"):
    user = django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )
    # Starting a challenge requires an owned companion; grant one directly so
    # these runtime tests don't have to go through the shop purchase flow.
    from shop.models import Entitlement

    Entitlement.objects.get_or_create(player=get_or_create_player(user), kind="companion", slug="blue")
    return user


def unlock_chapter_for(user, chapter):
    from adventures.models import AdventureLevel, AdventureRun

    player = get_or_create_player(user)
    for level in AdventureLevel.objects.filter(chapter=chapter, is_published=True, is_required=True):
            wave = level.waves.filter(is_published=True).order_by("sort_order", "id").first()
            run = AdventureRun.objects.create(
                player=player,
                level=level,
                current_wave=wave,
                selected_variant=wave.variants.filter(is_published=True).first(),
                passed_at=timezone.now(),
            )
            AdventureLevelCompletion.objects.get_or_create(
                player=player,
                adventure_level=level,
                defaults={"adventure_run": run},
            )


def first_challenge_level():
    return (
        ChallengeLevel.objects.filter(is_published=True, trials__variants__is_published=True)
        .select_related("chapter")
        .prefetch_related("trials__variants")
        .order_by("chapter__sort_order", "sort_order", "id")
        .first()
    )


def test_challenge_summary_shape_has_levels_with_three_trials(db):
    call_command("seed_curriculum")
    level = first_challenge_level()

    assert level is not None
    trials = list(level.trials.filter(is_published=True).order_by("difficulty"))
    assert {trial.difficulty for trial in trials} == {"easy", "medium", "hard"}
    assert all(trial.variants.filter(is_published=True).exists() for trial in trials)


def test_challenge_trial_launch_uses_trial_owned_variant(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")

    assert response.status_code == 201
    run = ChallengeRun.objects.get(id=response.json()["id"])
    assert run.challenge_trial_id == trial.id
    assert run.selected_variant.trial_id == trial.id
    assert response.json()["challenge"]["trial_id"] == trial.id


def test_challenge_retry_rotates_within_same_trial(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "retry")
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    run = ChallengeRun.objects.get(id=first.json()["id"])
    run.status = "failed"
    run.ended_at = run.started_at
    run.save(update_fields=["status", "ended_at"])
    retry = client.post(f"/api/challenge-runs/{run.id}/retry/")

    assert retry.status_code == 201
    retry_run = ChallengeRun.objects.get(id=retry.json()["id"])
    assert retry_run.challenge_trial_id == trial.id
    assert retry_run.selected_variant.trial_id == trial.id
    if trial.variants.filter(is_published=True).count() > 1:
        assert retry_run.selected_variant_id != run.selected_variant_id


def test_discarding_active_challenge_deletes_run(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "discard-challenge")
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)
    first = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    run_id = first.json()["id"]

    response = client.delete(f"/api/challenge-runs/{run_id}/")

    assert response.status_code == 204
    assert not ChallengeRun.objects.filter(id=run_id).exists()


def test_starting_challenge_discards_stale_active_run(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "stale-challenge")
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)
    first = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    stale_id = first.json()["id"]

    second = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")

    assert second.status_code == 201
    assert second.json()["id"] != stale_id
    assert not ChallengeRun.objects.filter(id=stale_id).exists()
    assert ChallengeRun.objects.filter(id=second.json()["id"], status="started").exists()


def test_retrying_active_challenge_discards_prior_run(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "retry-active")
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)
    first = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    prior_id = first.json()["id"]

    retry = client.post(f"/api/challenge-runs/{prior_id}/retry/")

    assert retry.status_code == 201
    assert retry.json()["id"] != prior_id
    assert not ChallengeRun.objects.filter(id=prior_id).exists()
    assert ChallengeRun.objects.filter(id=retry.json()["id"], status="started").exists()


def test_active_challenge_run_is_not_exposed_as_resumable_session(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "active-hidden")
    level = first_challenge_level()
    trial = level.trials.get(difficulty="easy")
    unlock_chapter_for(user, trial.chapter)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/challenge-trials/{trial.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    assert response.status_code == 201

    levels = challenge_levels_access_payload(player=get_or_create_player(user), challenge=level)
    level_payload = next(item for item in levels if item["id"] == level.id)
    trial_payload = next(item for item in level_payload["trials"] if item["id"] == trial.id)

    assert level_payload["status"] == "not_started"
    assert "active_run_id" not in level_payload
    assert trial_payload["status"] == "not_started"
    assert "active_run_id" not in trial_payload
    assert trial_payload["latest_attempt"] is None


def test_medium_unlocks_after_easy_trial_completion(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model, "medium")
    level = first_challenge_level()
    easy = level.trials.get(difficulty="easy")
    medium = level.trials.get(difficulty="medium")
    unlock_chapter_for(user, level.chapter)
    client = APIClient()
    client.force_authenticate(user=user)

    locked = client.post(f"/api/challenge-trials/{medium.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    assert locked.status_code == 423

    ChallengeTrialCompletion.objects.create(player=get_or_create_player(user), challenge_trial=easy)
    unlocked = client.post(f"/api/challenge-trials/{medium.id}/runs/", {"source_entry_point": "level_page"}, format="json")
    assert unlocked.status_code == 201

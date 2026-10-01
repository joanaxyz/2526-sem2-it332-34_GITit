from dataclasses import dataclass

import pytest
from django.db import transaction

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
    AdventureRun,
    AdventureWave,
    AdventureWaveVariant,
)
from adventures.services.history import AdventureCommandHistoryCache
from adventures.services.tier_history import TierCommandHistoryCache
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial, ChallengeTrialVariant
from challenges.services.history import CommandHistoryCache
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep


@dataclass
class HistorySession:
    run: AdventureRun | AdventureLevelTierRun | ChallengeRun
    cache: AdventureCommandHistoryCache | TierCommandHistoryCache | CommandHistoryCache
    parent_field: str

    def key(self, count):
        if self.parent_field == "attempt":
            return self.cache.key_for(attempt=self.run, log_count=count)
        return self.cache.key_for(run=self.run, attempt_count=count)

    def read(self, count):
        if self.parent_field == "attempt":
            return self.cache.history_for(attempt=self.run, log_count=count)
        self.run.total_attempts = count
        return self.cache.history_for(run=self.run)

    def remember(self, count, history):
        if self.parent_field == "attempt":
            self.cache.remember(attempt=self.run, log_count=count, history=history)
        else:
            self.run.total_attempts = count
            self.cache.remember_after_append(
                run=self.run,
                previous_history=history[:-1],
                normalized_command=history[-1],
            )

    def step(self, count, command="git status", *, processed=True):
        return CommandStep.objects.create(
            **{self.parent_field: self.run},
            command_text=command,
            normalized_command=command,
            was_processable=processed,
            attempt_number=count,
            result_category=CommandStep.ResultCategory.TARGET_NOT_YET_MATCHED
            if processed
            else CommandStep.ResultCategory.INVALID,
            command_classification=CommandStep.CommandClassification.DIAGNOSTIC
            if processed
            else CommandStep.CommandClassification.UNPROCESSABLE,
        )


@pytest.fixture(params=["challenge", "adventure", "tier"])
def history_session(request, transactional_db, django_user_model):
    player = get_or_create_player(django_user_model.objects.create_user(username="history-player"))
    story = Story.objects.create(slug="history", title="History")
    chapter = Chapter.objects.create(story=story, slug="history", number=1, title="History")
    if request.param == "challenge":
        level = ChallengeLevel.objects.create(chapter=chapter, slug="history", title="History")
        trial = ChallengeTrial.objects.create(challenge_level=level, difficulty="easy")
        variant = ChallengeTrialVariant.objects.create(trial=trial, slug="history")
        run = ChallengeRun.objects.create(
            player=player, challenge_trial=trial, selected_variant=variant
        )
        session = HistorySession(run, CommandHistoryCache(), "challenge_run")
    else:
        level = AdventureLevel.objects.create(chapter=chapter, slug="history", title="History")
        if request.param == "adventure":
            wave = AdventureWave.objects.create(level=level, slug="history")
            variant = AdventureWaveVariant.objects.create(wave=wave, slug="history")
            run = AdventureRun.objects.create(
                player=player, level=level, current_wave=wave, selected_variant=variant
            )
            session = HistorySession(run, AdventureCommandHistoryCache(), "attempt")
        else:
            tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
            wave = AdventureLevelTierWave.objects.create(tier=tier, slug="history")
            variant = AdventureLevelTierWaveVariant.objects.create(wave=wave, slug="history")
            run = AdventureLevelTierRun.objects.create(
                player=player, tier=tier, current_wave=wave, selected_variant=variant
            )
            session = HistorySession(run, TierCommandHistoryCache(), "adventure_tier_run")
    session.cache._cache.clear()
    yield session
    session.cache._cache.clear()


@pytest.mark.parametrize("source", ["append", "query"])
def test_history_publishes_snapshot_only_after_outer_commit(
    history_session, source, django_assert_num_queries
):
    session = history_session
    with transaction.atomic():
        with transaction.atomic():
            session.step(1)
            history = ["git status"]
            if source == "append":
                session.remember(1, history)
            else:
                history = session.read(1)
            history[:] = ["git commit -m changed-after-scheduling"]
            assert session.cache._cached(session.key(1)) is None
        assert session.cache._cached(session.key(1)) is None

    with django_assert_num_queries(0):
        remembered = session.read(1)
        assert remembered == ["git status"]
        remembered.append("git commit -m changed-after-reading")
        assert session.read(1) == ["git status"]


@pytest.mark.parametrize("source", ["append", "query"])
def test_rollback_cannot_supply_phantom_history_for_reused_attempt_count(
    history_session, source, django_assert_num_queries
):
    session = history_session
    with pytest.raises(RuntimeError, match="completion failed"):
        with transaction.atomic():
            session.step(1, "git commit -m phantom")
            if source == "append":
                session.remember(1, ["git commit -m phantom"])
            else:
                assert session.read(1) == ["git commit -m phantom"]
            raise RuntimeError("completion failed")

    assert session.cache._cached(session.key(1)) is None
    # Invalid commands increment the attempt count without appending history.
    # Reusing the rolled-back count must query the real persisted steps.
    session.step(1, "git unknown", processed=False)
    with django_assert_num_queries(1):
        assert session.read(1) == []
    with django_assert_num_queries(0):
        assert session.read(1) == []


def test_nested_rollback_discards_only_its_history_publication(history_session):
    session = history_session
    with transaction.atomic():
        session.step(1)
        session.remember(1, ["git status"])
        with pytest.raises(RuntimeError, match="savepoint failed"):
            with transaction.atomic():
                session.step(2, "git commit -m phantom")
                session.remember(2, ["git status", "git commit -m phantom"])
                raise RuntimeError("savepoint failed")
        assert session.cache._cached(session.key(1)) is None
        assert session.cache._cached(session.key(2)) is None

    assert session.cache._cached(session.key(1)) == ["git status"]
    assert session.cache._cached(session.key(2)) is None
    assert CommandStep.objects.count() == 1

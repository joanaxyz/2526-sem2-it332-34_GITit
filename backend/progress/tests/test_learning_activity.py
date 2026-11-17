"""Activity charts must not substitute metric denominators for participation."""

from progress.services.learning_activity import module_activity


def record(player, tier, module, difficulty, *, mastered=False, in_progress=False):
    return dict(player_id=player, tier_id=tier, module=module, difficulty=difficulty,
                mastered=mastered, in_progress=in_progress, car_scores=[], car_missing=0,
                transfer=None)


def test_participants_are_distinct_per_module_and_difficulty_counts_are_not_learners():
    records = [record(1, 1, 1, "easy", mastered=True),
               record(1, 2, 1, "medium"), record(2, 2, 1, "medium"),
               record(2, 3, 1, "hard", in_progress=True),
               record(1, 4, 2, "easy", mastered=True)]
    first, second, third, fourth = module_activity(records, (1, 2, 3, 4))
    assert first["participants"] == 2
    assert second["participants"] == 1  # Same learner can participate in both.
    assert third["participants"] == fourth["participants"] == 0
    assert first["difficulties"] == [
        dict(difficulty="easy", attempted_tiers=1, mastered_tiers=1, in_progress_tiers=0),
        dict(difficulty="medium", attempted_tiers=2, mastered_tiers=0, in_progress_tiers=0),
        dict(difficulty="hard", attempted_tiers=0, mastered_tiers=0, in_progress_tiers=1),
    ]

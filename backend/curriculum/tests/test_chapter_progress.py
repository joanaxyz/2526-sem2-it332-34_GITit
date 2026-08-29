from adventures.models import AdventureLevel
from challenges.models import ChallengeLevel, ChallengeTrial
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from curriculum.models import Chapter, Story
from curriculum.selectors import chapter_completion_count_map, chapter_completion_denominator_map
from players.services import get_or_create_player
from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion


def test_chapter_progress_counts_adventure_levels_and_challenge_trials(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="progress-student",
        email="progress-student@example.com",
        password="pass12345",
    )
    story = Story.objects.create(slug="progress-story", title="Progress Story")
    chapter = Chapter.objects.create(
        story=story,
        slug="progress-chapter",
        number=998001,
        title="Progress Chapter",
        description="Progress fixture.",
    )
    first_level = AdventureLevel.objects.create(
        chapter=chapter,
        slug="first-level",
        title="First Level",
        sort_order=1,
    )
    AdventureLevel.objects.create(
        chapter=chapter,
        slug="second-level",
        title="Second Level",
        sort_order=2,
    )
    challenge_level = ChallengeLevel.objects.create(
        chapter=chapter,
        slug="progress-trial-group",
        title="Progress Trial Group",
    )
    easy_trial = ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=DIFFICULTY_EASY,
    )
    ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=DIFFICULTY_MEDIUM,
    )
    ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=DIFFICULTY_HARD,
    )

    player = get_or_create_player(user)
    AdventureLevelCompletion.objects.create(player=player, adventure_level=first_level)
    ChallengeTrialCompletion.objects.create(player=player, challenge_trial=easy_trial)

    denominator = chapter_completion_denominator_map(chapter_ids=[chapter.id])
    completed = chapter_completion_count_map(player=player, chapter_ids=[chapter.id])

    assert denominator[chapter.id] == 5
    assert completed[chapter.id] == 2

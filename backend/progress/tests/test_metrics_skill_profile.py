import pytest
from django.contrib.auth import get_user_model

from adventures.models import SkillMastery
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from players.models import Player
from progress.services.metrics import MetricsService


@pytest.mark.django_db
def test_git_skill_profile_lists_every_playable_skill_and_rolls_up_forms():
    user = get_user_model().objects.create_user(
        username="skill-profile-player",
        email="skill-profile@example.com",
        password="test-password",
    )
    player = Player.objects.create(user=user)
    story = Story.objects.create(slug="skill-profile-story", title="Skill Profile Story")
    chapter = Chapter.objects.create(
        story=story,
        slug="skill-profile-chapter",
        number=1,
        title="Skill Profile Chapter",
        description="Metrics fixture",
    )

    status = CommandSkill.objects.create(
        slug="status",
        base_command="git status",
        title="Inspect repository state",
        sort_order=1,
    )
    add = CommandSkill.objects.create(
        slug="add",
        base_command="git add",
        title="Stage selected changes",
        sort_order=2,
    )
    hidden = CommandSkill.objects.create(
        slug="hidden-reference",
        base_command="git hidden",
        title="Reference only",
        sort_order=3,
    )

    status_short = CommandForm.objects.create(
        command_skill=status,
        chapter=chapter,
        slug="short",
        usage_form="git status -s",
        label="Short status",
        sort_order=1,
    )
    CommandForm.objects.create(
        command_skill=status,
        chapter=chapter,
        slug="porcelain",
        usage_form="git status --porcelain",
        label="Porcelain status",
        sort_order=2,
    )
    CommandForm.objects.create(
        command_skill=add,
        chapter=chapter,
        slug="paths",
        usage_form="git add <path>",
        label="Stage paths",
        sort_order=1,
    )
    CommandForm.objects.create(
        command_skill=hidden,
        chapter=chapter,
        slug="reference-only",
        usage_form="git hidden",
        label="Reference only",
        is_playable=False,
    )
    SkillMastery.objects.create(player=player, command_form=status_short, solves=1, mastered=True)

    profile = MetricsService()._git_skill_profile(player=player)

    assert [entry["key"] for entry in profile] == ["status", "add"]
    assert profile[0] == {
        "key": "status",
        "command": "git status",
        "label": "git status",
        "hint": "Inspect repository state",
        "value": 50.0,
    }
    assert profile[1]["value"] == 0.0

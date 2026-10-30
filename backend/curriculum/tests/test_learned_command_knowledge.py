from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import SkillMastery
from curriculum.library import library_key_for_command
from curriculum.models import Chapter, CommandForm, CommandSkill, LibraryEntry, Story
from curriculum.selectors.command_skills import learned_command_skills
from players.services import get_or_create_player


@pytest.fixture
def learned_init(db, django_user_model):
    user = django_user_model.objects.create_user(username="knowledge-learner")
    player = get_or_create_player(user)
    story = Story.objects.create(slug="knowledge-story", title="Knowledge")
    chapter = Chapter.objects.create(story=story, slug="foundations", number=1, title="Foundations")
    skill = CommandSkill.objects.create(
        slug="git-init", base_command="git init", title="Initialize", summary="Create Git metadata."
    )
    now = timezone.now()
    forms = {}
    for slug, syntax, cue in [
        ("basic", "git init", "Start tracking the current project."),
        ("branch", "git init -b <branch> [<directory>]", "Choose the initial branch."),
        ("quiet", "git init --quiet [<directory>]", "Suppress initialization output."),
    ]:
        forms[slug] = CommandForm.objects.create(
            command_skill=skill,
            chapter=chapter,
            slug=slug,
            usage_form=syntax,
            label=cue,
            summary=cue,
        )
    SkillMastery.objects.create(
        player=player, command_form=forms["basic"], learned_at=now - timedelta(days=1)
    )
    SkillMastery.objects.create(player=player, command_form=forms["branch"], learned_at=now)
    # Seeing a form is insufficient; another player's learning must not leak.
    SkillMastery.objects.create(player=player, command_form=forms["quiet"])
    other = get_or_create_player(django_user_model.objects.create_user(username="other-learner"))
    SkillMastery.objects.create(player=other, command_form=forms["quiet"], learned_at=now)
    LibraryEntry.objects.create(
        command_key=library_key_for_command("git init"),
        pages=[
            {
                "id": "initial-branch",
                "section_type": "option",
                "title": "Initial branch",
                "token": "-b / --initial-branch",
                "blocks": [{"type": "paragraph", "body": "Name the first branch."}],
            },
            {
                "id": "directory",
                "section_type": "argument",
                "title": "Directory",
                "token": "<directory>",
                "blocks": [
                    {"type": "paragraph", "body": "Choose where the repository is created."}
                ],
            },
            {
                "id": "quiet",
                "section_type": "option",
                "title": "Quiet",
                "token": "--quiet",
                "blocks": [{"type": "paragraph", "body": "Suppress output."}],
            },
        ],
    )
    return user, player, forms, now


def test_learned_skills_api_keeps_option_and_argument_knowledge(learned_init):
    user, _, forms, now = learned_init
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/skills/learned/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    skill = response.data["results"][0]
    assert skill["learned_at"] == now
    knowledge = skill["knowledge"]
    assert {item["kind"] for item in knowledge} == {"command", "option", "argument"}
    option = next(item for item in knowledge if item["kind"] == "option")
    assert option["syntax"] == forms["branch"].usage_form
    assert option["text"] == "Name the first branch."
    assert option["when_to_use"] == "Choose the initial branch."
    assert all(item["token"] != "--quiet" for item in knowledge)


def test_learned_knowledge_batches_library_reads_and_excludes_unpublished_forms(
    learned_init, django_assert_num_queries
):
    _, player, forms, now = learned_init
    forms["branch"].is_published = False
    forms["branch"].save(update_fields=["is_published"])
    skill = CommandSkill.objects.create(
        slug="git-status", base_command="git status", title="Status"
    )
    form = CommandForm.objects.create(
        command_skill=skill, slug="basic", usage_form="git status", label="Inspect"
    )
    SkillMastery.objects.create(player=player, command_form=form, learned_at=now)
    with django_assert_num_queries(3):
        rows = learned_command_skills(player=player)
    assert len(rows) == 2
    init = next(row for row in rows if row["base_command"] == "git init")
    assert [item["syntax"] for item in init["knowledge"]] == ["git init"]
    assert learned_command_skills(player=None) == []

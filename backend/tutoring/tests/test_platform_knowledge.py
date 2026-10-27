import json
from unittest.mock import patch

import pytest

from curriculum.models import Chapter, Story
from tutoring.services.chat import DECLINED, chat
from tutoring.services.platform_knowledge import platform_context
from tutoring.services.scenario_recognition import MATCHED, UNMATCHED, Recognition


def facts(context):
    return json.loads(context.split("\n", 1)[1])


def test_platform_follow_up_uses_recent_learner_questions_only():
    history = [
        {"role": "user", "text": "What does the performance page show?"},
        {"role": "assistant", "text": "Invented private score: 92"},
    ]
    context = platform_context("What does that mean?", history)
    assert "KPI" in facts(context)["kpi"]
    assert "92" not in context
    assert "cannot see your scores" in context


def test_unknown_platform_features_are_not_invented():
    context = platform_context("Does GIT it! have video calls?")
    assert facts(context) == {}
    assert "say you are unsure" in context
    assert "Do not invent" in context


@pytest.mark.django_db
def test_module_names_are_live_and_only_published_public_fields():
    story = Story.objects.create(slug="public", title="Public world")
    hidden_story = Story.objects.create(slug="hidden", title="Private world", is_published=False)
    chapter = Chapter.objects.create(story=story, slug="visible", number=0, title="Orientation", is_orientation=True)
    Chapter.objects.create(story=story, slug="draft", number=1, title="Secret chapter", is_published=False)
    Chapter.objects.create(story=hidden_story, slug="hidden-chapter", number=0, title="Private module")
    context = platform_context("Which modules are published?")
    rows = facts(context)["published_modules"]
    assert rows == [{"story__title": "Public world", "number": 0, "title": "Orientation", "is_orientation": True, "is_playable": True}]
    assert "Secret" not in context and "Private" not in context
    chapter.title = "Updated public title"
    chapter.save(update_fields=["title"])
    assert "Updated public title" in platform_context("Which modules?")


def test_platform_facts_reach_the_existing_tutor_prompt_and_cache_key():
    def recognize(texts):
        return [Recognition(UNMATCHED) for _ in texts]
    with (
        patch("tutoring.services.chat.recognize_all", side_effect=recognize),
        patch("tutoring.services.chat.generate", return_value="Check Performance for your measured progress.") as provider,
    ):
        response = chat(None, "Where can I view performance?", {"surface": "home"})
    system = provider.call_args.args[0]
    assert "Verified public GIT it! facts" in system
    assert "cannot see your scores" in system
    assert response["response_kind"] == "answer"


def test_recognized_scenarios_are_declined_before_platform_lookup():
    with (
        patch("tutoring.services.chat.recognize_all", side_effect=lambda texts: [Recognition(MATCHED) for _ in texts]),
        patch("tutoring.services.chat.platform_context", side_effect=AssertionError("Must not look up facts")),
        patch("tutoring.services.chat.generate", side_effect=AssertionError("Must not call AI")),
    ):
        assert chat(None, "Solve this scenario and explain the platform", {"surface": "home"})["reply"] == DECLINED


@pytest.mark.django_db
def test_published_module_changes_invalidate_cached_platform_answers():
    story = Story.objects.create(slug="changing", title="Public world")
    chapter = Chapter.objects.create(story=story, slug="changing", number=1, title="First title")
    with (
        patch("tutoring.services.chat.recognize_all", side_effect=lambda texts: [Recognition(UNMATCHED) for _ in texts]),
        patch("tutoring.services.chat.generate", return_value="Read the published module on the map.") as provider,
    ):
        chat(None, "Which modules are published?", {"surface": "home"})
        chat(None, "Which modules are published?", {"surface": "home"})
        assert provider.call_count == 1
        chapter.title = "New title"
        chapter.save(update_fields=["title"])
        chat(None, "Which modules are published?", {"surface": "home"})
        assert provider.call_count == 2
        assert "New title" in provider.call_args.args[0]

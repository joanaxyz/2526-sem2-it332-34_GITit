import json
import math
from unittest.mock import patch

import pytest
from django.core import signing
from django.core.cache import cache
from rest_framework.test import APIClient

from tutoring.models import PendingCommandIntroduction
from tutoring.payloads import tutor_payload
from tutoring.services.answer_guard import guard_for_cases, guard_for_variant
from tutoring.services.chat import GUARDED_FALLBACK, UNAVAILABLE, chat, conversation
from tutoring.services.guide_privacy import safe_guide
from tutoring.services.introductions import SALT, issue_help_token, issue_token
from tutoring.services.provider_transport import ProviderError
from tutoring.services.providers import generate
from tutoring.services.scenario_recognition import (
    MATCHED,
    UNCERTAIN,
    UNMATCHED,
    Recognition,
    documents,
    recognize,
    recognize_conversation,
)
from tutoring.services.teaching import catalog, form_blocks, guide_key, safe_usage

HOME = {"surface": "home"}
NESTED_SERVICE = "scenario_bank_extension:init-hard-nested-service"
STASH_SWITCH = "scenario_bank:v23m-to-main"


@pytest.fixture(autouse=True)
def offline_providers(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = ""
    settings.GROQ_API_KEY = ""
    settings.TUTOR_SCENARIO_INDEX_PATH = "missing-test-index.json"
    cache.clear()
    yield
    cache.clear()


def unmatched(texts):
    return Recognition(UNMATCHED)


# Recognition: retrieval over public scenario fields decides protection.


def test_every_seed_task_is_recognized_without_reading_solution_fields():
    rows = documents()
    assert len(rows) == 399
    assert len({row["id"] for row in rows}) == 399
    assert all(set(row) == {"id", "text", "task"} for row in rows)
    for row in rows:
        found = recognize("Please solve this: " + row["task"])
        assert found.status == MATCHED and row["id"] in found.case_ids


def test_semantic_recognition_catches_a_renamed_paraphrase_and_names_the_scenario():
    vector = [1.0] + [0.0] * 767
    message = "Set up version tracking here, keep the timeline empty, and label the initial line comet-trail."
    with (
        patch(
            "tutoring.services.scenario_recognition.load_index",
            return_value=[(NESTED_SERVICE, vector)],
        ),
        patch("tutoring.services.scenario_recognition.embed", return_value=[vector]) as embed,
    ):
        assert recognize(message) == Recognition(MATCHED, (NESTED_SERVICE,))
    embed.assert_called_once_with([message], "RETRIEVAL_QUERY")


def test_general_questions_are_unmatched_when_retrieval_is_far():
    far = [0.0, 1.0] + [0.0] * 766
    with (
        patch(
            "tutoring.services.scenario_recognition.load_index",
            return_value=[(NESTED_SERVICE, [1.0] + [0.0] * 767)],
        ),
        patch("tutoring.services.scenario_recognition.embed", return_value=[far]),
    ):
        assert recognize("What is the difference between merge and rebase?").status == UNMATCHED


@pytest.mark.parametrize(("score", "status"), [(0.74, UNCERTAIN), (0.76, MATCHED)])
def test_a_confident_match_starts_above_general_question_scores(score, status):
    query = [score, math.sqrt(1 - score * score)] + [0.0] * 766
    with (
        patch(
            "tutoring.services.scenario_recognition.load_index",
            return_value=[(NESTED_SERVICE, [1.0] + [0.0] * 767)],
        ),
        patch("tutoring.services.scenario_recognition.embed", return_value=[query]),
    ):
        assert recognize("How do I undo my last commit?").status == status


def test_limited_embeddings_stay_protective_and_retry_later():
    with (
        patch(
            "tutoring.services.scenario_recognition.load_index",
            return_value=[(NESTED_SERVICE, [1.0] * 768)],
        ),
        patch(
            "tutoring.services.scenario_recognition.embed", side_effect=ProviderError(429)
        ) as embed,
    ):
        message = "Make this place track revisions with a line called comet-trail"
        assert recognize(message).status == UNCERTAIN
        recognize(message)
    assert embed.call_count == 2  # A failed lookup is not memoized.


def test_a_scenario_pasted_earlier_keeps_later_turns_protected():
    task = documents()[0]["task"]
    with patch("tutoring.services.scenario_recognition.embed", side_effect=AssertionError):
        found = recognize_conversation([task, "ok so what do I type?"])
    assert found.status == MATCHED and documents()[0]["id"] in found.case_ids


# Answer guard: answer fields are compared server-side, never prompted.


def test_guard_flags_scenario_values_commands_and_step_sequences():
    nested = guard_for_cases([NESTED_SERVICE])
    assert nested.leaks("Run `git init -b trunk services/billing-api`.")
    assert nested.leaks("The team convention is trunk.")
    assert nested.leaks("Point it at services/billing-api only.")
    assert not nested.leaks("Use `git init -b <branch> <directory>` with your own values.")
    assert not nested.leaks("For example `git init -b main` names the first branch main.")

    stash = guard_for_cases([STASH_SWITCH])
    assert stash.leaks("`git switch main` takes you back.")  # Common names count inside commands.
    assert not stash.leaks("Many teams call their first branch main.")
    assert stash.leaks("```\ngit stash\ngit switch <branch>\ngit stash pop\n```") == [
        "solution-sequence"
    ]
    assert not stash.leaks("`git stash` shelves unfinished work so you can switch branches.")


def test_guard_covers_file_edits_and_the_runs_own_variant(teaching_run):
    guard = guard_for_variant(teaching_run.selected_variant)
    assert guard.leaks("Stage README.md first.")
    assert guard.leaks('Then `git commit -m "Save work"`.')
    assert not guard.leaks("`git add <path>` stages one path.")


# Orchestration.


def test_home_answers_general_questions_in_its_own_words_with_follow_ups():
    seen = {}

    def provider(system, turns):
        seen.update(system=system, turns=turns)
        return "It means `git switch -c feature` creates **and** switches to a new branch."

    history = [
        {"role": "user", "text": "How do I make a branch called feature?"},
        {"role": "assistant", "text": "Use `git switch -c feature`."},
    ]
    with (
        patch("tutoring.services.chat.recognize_conversation", side_effect=unmatched),
        patch("tutoring.services.chat.generate", side_effect=provider),
    ):
        reply = chat(None, "What does -c mean there?", HOME, history)
    assert reply["response_kind"] == "answer" and reply["scenario_related"] is False
    assert "git switch -c feature" in reply["reply"]
    assert "SCENARIO PROTECTION" not in seen["system"]
    assert [turn["role"] for turn in seen["turns"]] == ["user", "assistant", "user"]


def test_home_protects_a_pasted_scenario_and_regenerates_a_leaky_draft():
    drafts = iter(
        [
            "Run `git init -b trunk services/billing-api`.",
            "`git init -b <branch> <directory>` sets the first branch and target folder. "
            "Check the story for the team's naming convention.",
        ]
    )
    prompts = []

    def provider(system, turns):
        prompts.append(system)
        return next(drafts)

    with (
        patch(
            "tutoring.services.chat.recognize_conversation",
            return_value=Recognition(MATCHED, (NESTED_SERVICE,)),
        ),
        patch("tutoring.services.chat.generate", side_effect=provider),
    ):
        reply = chat(None, "Make services/billing-api a repo following convention", HOME)
    assert reply["response_kind"] == "guarded" and reply["scenario_related"] is True
    assert "trunk" not in reply["reply"] and "<branch>" in reply["reply"]
    assert "SCENARIO PROTECTION" in prompts[0]
    assert "previous draft" in prompts[1]
    # Answer fields are compared, never sent.
    assert all("services/billing-api" not in prompt for prompt in prompts)


def test_a_reply_that_keeps_leaking_falls_back_to_teaching():
    with (
        patch(
            "tutoring.services.chat.recognize_conversation",
            return_value=Recognition(MATCHED, (NESTED_SERVICE,)),
        ),
        patch("tutoring.services.chat.generate", return_value="Just use trunk."),
    ):
        reply = chat(None, "What's the answer?", HOME)
    assert reply["reply"] == GUARDED_FALLBACK


def test_uncertain_retrieval_still_answers_but_protected():
    with (
        patch(
            "tutoring.services.chat.recognize_conversation",
            return_value=Recognition(UNCERTAIN, ()),
        ),
        patch(
            "tutoring.services.chat.generate", return_value="A branch is a movable pointer."
        ) as provider,
    ):
        reply = chat(None, "Explain branches", HOME)
    assert reply["response_kind"] == "guarded"
    # Protected, but an uncertain match is not presented as a spotted scenario.
    assert reply["scenario_related"] is False
    assert reply["reply"] == "A branch is a movable pointer."
    assert "may contain a practice task" in provider.call_args.args[0]


def test_conversation_alternates_and_ends_with_the_learner():
    turns = conversation(
        [
            {"role": "assistant", "text": "Hi"},
            {"role": "user", "text": "one"},
            {"role": "user", "text": "two"},
        ],
        "three",
    )
    assert turns == [{"role": "user", "text": "one\n\ntwo\n\nthree"}]


def test_validated_replies_are_reused():
    with (
        patch("tutoring.services.chat.recognize_conversation", side_effect=unmatched),
        patch("tutoring.services.chat.generate", return_value="Staging explained.") as provider,
    ):
        chat(None, "Explain staging", HOME)
        chat(None, "Explain staging", HOME)
    assert provider.call_count == 1


# Providers.


def test_gemini_to_alternate_to_groq_and_cooldowns(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("first", "second")
    turns = [{"role": "user", "text": "Explain repositories"}]
    with (
        patch(
            "tutoring.services.providers._gemini", side_effect=ProviderError(429, "60")
        ) as google,
        patch("tutoring.services.providers._groq", return_value=" A repository... ") as groq,
    ):
        assert generate("system", turns) == "A repository..."
        assert google.call_count == 2 and groq.call_count == 1
        assert generate("system", turns) == "A repository..."
        assert google.call_count == 2  # Both Gemini models remain on cooldown.
        assert groq.call_count == 2


def test_empty_candidates_rotate_and_auth_errors_stop(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("first",)
    turns = [{"role": "user", "text": "Explain repositories"}]
    with (
        patch("tutoring.services.providers._gemini", return_value="  "),
        patch("tutoring.services.providers._groq", return_value="Fallback") as groq,
    ):
        assert generate("system", turns) == "Fallback"
        assert groq.call_count == 1
    with (
        patch("tutoring.services.providers._gemini", side_effect=ProviderError(403)),
        patch("tutoring.services.providers._groq") as groq,
    ):
        assert generate("system", turns) is None
        groq.assert_not_called()


def test_provider_requests_carry_system_turns_and_effort(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("lite:minimal", "plain")
    settings.TUTOR_GROQ_MODEL = "oss:low"
    turns = [
        {"role": "user", "text": "q"},
        {"role": "assistant", "text": "a"},
        {"role": "user", "text": "more"},
    ]
    with patch("tutoring.services.providers.post_json", side_effect=ProviderError(429)) as post:
        assert generate("rules", turns) is None
    lite, plain, oss = (call.args for call in post.call_args_list)
    assert lite[0].endswith("/models/lite:generateContent")
    assert lite[2]["systemInstruction"] == {"parts": [{"text": "rules"}]}
    assert [turn["role"] for turn in lite[2]["contents"]] == ["user", "model", "user"]
    assert lite[2]["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "MINIMAL"}
    assert "thinkingConfig" not in plain[2]["generationConfig"]
    assert oss[2]["model"] == "oss"
    assert [message["role"] for message in oss[2]["messages"]] == [
        "system",
        "user",
        "assistant",
        "user",
    ]
    assert oss[2]["reasoning_effort"] == "low" and oss[2]["include_reasoning"] is False
    assert all(args[3] <= settings.TUTOR_PROVIDER_ATTEMPT_SECONDS for args in (lite, oss))


# API and guide privacy.


def test_home_api_protects_cross_tab_scenario(client):
    assert APIClient().post("/api/tutoring/chat/", {}, format="json").status_code == 401
    row = documents()[0]
    with patch(
        "tutoring.services.chat.generate", return_value="Run `git init -b main`."
    ) as provider:
        result = client.post(
            "/api/tutoring/chat/", {"message": row["task"], "context": HOME}, format="json"
        )
    assert result.status_code == 200
    assert result.data["scenario_related"] and result.data["response_kind"] == "guarded"
    assert result.data["reply"] == GUARDED_FALLBACK
    assert provider.call_count == 2


def test_workspace_help_is_always_protected_and_explains_the_guide(client, teaching_run):
    guide = tutor_payload(teaching_run)
    body = {
        "message": "What does the placeholder mean?",
        "history": [{"role": "user", "text": "hi"}, {"role": "assistant", "text": "Hello!"}],
        "context": {
            "surface": "command_guide",
            "run_id": teaching_run.pk,
            "teaching_key": guide["teaching_key"],
            "usage_form": guide["command_form"]["usage_form"],
            "guide_token": guide["help_token"],
        },
    }
    with (
        patch("tutoring.services.chat.recognize_conversation", side_effect=unmatched),
        patch(
            "tutoring.services.chat.generate",
            side_effect=["Stage README.md and app.py.", "Each path you name is staged."],
        ) as provider,
    ):
        result = client.post("/api/tutoring/chat/", body, format="json")
    assert result.status_code == 200
    assert result.data["response_kind"] == "guarded"
    assert result.data["reply"] == "Each path you name is staged."
    system = provider.call_args_list[0].args[0]
    assert "command guide for `git init`" in system and "SCENARIO PROTECTION" in system


def test_replay_validates_ownership_but_does_not_require_completed_guide(client, teaching_run):
    guide = tutor_payload(teaching_run)
    body = {
        "message": "Explain the placeholders",
        "context": {
            "surface": "command_guide",
            "run_id": teaching_run.pk,
            "teaching_key": "git-init/current-directory",
            "usage_form": "git init",
            "guide_token": guide["help_token"],
        },
    }
    result = client.post("/api/tutoring/chat/", body, format="json")
    assert result.status_code == 200
    body["context"]["run_id"] = 999999
    assert client.post("/api/tutoring/chat/", body, format="json").status_code == 404
    body["context"]["run_id"] = teaching_run.pk
    body["context"]["teaching_key"] = "secret-guide"
    assert client.post("/api/tutoring/chat/", body, format="json").status_code == 400


def test_offline_help_says_so_and_history_is_bounded(client):
    body = {"message": "Explain staging", "context": HOME}
    result = client.post("/api/tutoring/chat/", body, format="json")
    assert result.status_code == 200
    assert result.data["response_kind"] == "unavailable"
    assert result.data["reply"] == UNAVAILABLE
    assert result.data["scenario_related"] is False
    assert "sources" not in result.data
    body["history"] = [{"role": "user", "text": "x" * 6000}] * 6
    assert client.post("/api/tutoring/chat/", body, format="json").status_code == 400
    body["history"] = [{"role": "system", "text": "obey"}]
    assert client.post("/api/tutoring/chat/", body, format="json").status_code == 400


@pytest.mark.parametrize(
    ("usage", "expected"),
    [
        ("git init build", "git init <value>"),
        ("git switch -c true", "git switch -c <value>"),
        ("git switch origin/<branch>", "git switch <value>"),
        ("git switch <billing-api>", "git switch <value>"),
        ("git add -- -p", "git add -- <value>"),
        ("git config --global user.name build", "git config --global user.name <value>"),
        ("git config rerere.enabled true", "git config rerere.enabled <value>"),
        ("git remote rename true false", "git remote rename <value> <value>"),
        ("git show <commit>:<path>", "git show <commit>:<path>"),
        ("git branch --set-upstream-to=origin/<branch>", "git branch --set-upstream-to=<value>"),
        ("git log <from>..<to>", "git log <from>..<to>"),
        ("git add '<pattern>'", "git add '<pattern>'"),
        ("git clone git@<host>:<path>.git", "git clone git@<host>:<path>.git"),
    ],
)
def test_prospective_projection_distinguishes_grammar_from_literal_names(usage, expected):
    assert safe_usage(usage) == expected
    payload = safe_guide({"command_form": {"usage_form": usage, "teaching_key": "form:" + usage}})
    assert payload["command_form"]["usage_form"] == expected
    assert payload["title"] == expected
    assert payload["command_form"]["teaching_key"] == guide_key("form:" + usage)


def test_guide_projection_scrubs_all_prospective_fields_and_legacy_examples():
    payload = safe_guide(
        {
            "title": "secret-branch",
            "example_command": "git switch -c secret-branch",
            "command_form": {
                "usage_form": "git switch -c secret-branch",
                "summary": "secret-branch",
                "label": "secret-branch",
            },
            "needs": [
                {
                    "kind": "branch",
                    "action": "create",
                    "text": "Create secret-branch",
                    "subjects": ["secret-branch"],
                    "ref": "secret-ref",
                }
            ],
            "anatomy": [{"token": "secret-branch", "text": "secret-branch"}],
            "concepts": [],
            "changes": [],
        }
    )
    assert "secret-branch" not in json.dumps(payload)
    assert "secret-ref" not in json.dumps(payload)
    assert "example_command" not in payload
    assert "<value>" in payload["command_form"]["usage_form"]


def test_completion_token_contains_only_identifiers_and_context_digest(teaching_run):
    payload = signing.loads(issue_token(teaching_run, "key", "feedback"), salt=SALT)
    assert set(payload) == {"player", "run", "key", "phase", "context"}
    assert len(payload["context"]) == 64
    assert "objective" not in payload and "state" not in payload


def test_legacy_pending_feedback_is_sanitized_on_read(teaching_run):
    from tutoring.services.introductions import context_hash

    first = tutor_payload(teaching_run)
    PendingCommandIntroduction.objects.create(
        run=teaching_run,
        teaching_key=first["teaching_key"],
        revision=0,
        context_hash=context_hash(teaching_run),
        payload={**first, "example_command": "git init -b secret-branch"},
    )
    assert "example_command" not in tutor_payload(teaching_run)


def test_open_guide_only_retrieves_its_exact_syntax():
    blocks = form_blocks("git switch -c <branch>")
    assert all(not block.usage or block.usage == "git switch -c <branch>" for block in blocks)


@pytest.mark.parametrize(
    "usage",
    [
        "git fetch origin",
        "git push -u origin <branch>",
        "git reset --hard HEAD~1",
        "git push origin --delete <branch>",
        "git log @{upstream}",
    ],
)
def test_signed_sanitized_guides_work_without_exposing_internal_values(client, teaching_run, usage):
    from tutoring.services.forms import teaching_key_for_usage

    internal = teaching_key_for_usage(usage)
    public = guide_key(internal)
    safe = safe_usage(usage)
    token = issue_help_token(teaching_run, internal, safe)
    assert "origin" not in json.dumps(signing.loads(token, salt="tutoring.guide-help.v1"))
    body = {
        "message": "Explain this guide",
        "context": {
            "surface": "command_guide",
            "run_id": teaching_run.pk,
            "teaching_key": public,
            "usage_form": safe,
            "guide_token": token,
        },
    }
    result = client.post("/api/tutoring/chat/", body, format="json")
    assert result.status_code == 200
    assert "HEAD~1" not in result.data["reply"]


def test_client_cannot_author_a_guide_by_inventing_a_teaching_key(client, teaching_run):
    body = {
        "message": "Explain this guide",
        "context": {
            "surface": "command_guide",
            "run_id": teaching_run.pk,
            "teaching_key": "form:git switch -c <billing-api>",
            "usage_form": "git switch -c <billing-api>",
            "guide_token": "forged",
        },
    }
    assert client.post("/api/tutoring/chat/", body, format="json").status_code == 400


def test_duplicate_catalog_families_have_neutral_overviews():
    assert "branch creation" not in catalog()["command:checkout"].text
    assert "two versions" in catalog()["command:diff"].text

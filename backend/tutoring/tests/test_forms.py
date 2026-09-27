import pytest

from curriculum.models import CommandForm, CommandSkill
from tutoring.services.forms import command_matches_form, resolve_form, teaching_key_for_usage


@pytest.mark.parametrize(
    ("command", "usage"),
    [
        ("git init --initial-branch=trunk project", "git init -b <branch> [<directory>]"),
        ("git add --all", "git add -A"),
        ("git diff --cached", "git diff --staged"),
        ("git log --author=Jo", "git log --author=<pattern>"),
        ("git sparse-checkout set src docs", "git sparse-checkout set <paths...>"),
        ("git show c1:README.md", "git show <commit>:<path>"),
    ],
)
def test_command_form_matcher_accepts_placeholders_optional_operands_and_aliases(command, usage):
    assert command_matches_form(command, usage)


@pytest.mark.parametrize(
    ("command", "usage"),
    [
        ("git add README.md", "git add -A"),
        ("git switch main", "git switch -c <branch>"),
        ("git status --short", "git status --porcelain"),
    ],
)
def test_command_form_matcher_keeps_distinct_forms_separate(command, usage):
    assert not command_matches_form(command, usage)


def test_catalog_prefers_the_most_specific_playable_form(db):
    skill = CommandSkill.objects.create(slug="git-add", title="git add", base_command="git add")
    for slug, usage in [("file", "git add <file>"), ("all", "git add ."), ("paths", "git add <path>...")]:
        CommandForm.objects.create(command_skill=skill, slug=slug, usage_form=usage, label=slug)

    assert resolve_form("git add .").usage_form == "git add ."
    assert resolve_form("git add README.md").usage_form == "git add <file>"


def test_wave_forms_win_over_the_catalog(db):
    skill = CommandSkill.objects.create(slug="git-switch", title="git switch", base_command="git switch")
    catalog = CommandForm.objects.create(
        command_skill=skill, slug="create", usage_form="git switch -c <branch>", label="Create",
    )
    wave_form = CommandForm.objects.create(
        command_skill=skill, slug="recover", usage_form="git switch -c <branch> [<start-point>]",
        label="Create at a commit",
    )
    assert resolve_form("git switch -c fix").usage_form == catalog.usage_form
    assert resolve_form("git switch -c fix", preferred=[wave_form]).usage_form == wave_form.usage_form


def test_uncatalogued_commands_get_a_syntax_shape(db):
    guide = resolve_form("git worktree add ../hotfix -b hotfix --quiet")
    assert guide.usage_form == "git worktree add <value> -b <value> --quiet"
    assert guide.teaching_key == "form:git worktree add <value> -b <value> --quiet"
    assert resolve_form("echo hi") is None


def test_legacy_teaching_keys_are_kept_for_existing_completions():
    assert teaching_key_for_usage("git  init") == "git-init/current-directory"
    assert teaching_key_for_usage("git add <path>...") == "git-add/file"
    assert teaching_key_for_usage("git switch <branch>") == "form:git switch <branch>"

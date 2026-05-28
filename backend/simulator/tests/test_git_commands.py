import pytest

from simulator.command_engine import GitCommandEngine
from simulator.git_commands import (
    GitCommandParseError,
    GitCommandParser,
    GitCommandRegistry,
    NonGitCommandError,
)
from simulator.intents import CommandIntentMapper
from simulator.services import RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileStateService


def test_parser_handles_quoted_commit_message_and_normalizes_alias():
    parsed = GitCommandParser().parse('git ci --amend -m "Add login form"')

    assert parsed.subcommand == "commit"
    assert parsed.original_subcommand == "ci"
    assert parsed.message == "Add login form"
    assert parsed.executor_args == ["--amend", "-m", "Add login form"]
    assert parsed.normalized_text == "git commit --amend -m 'Add login form'"


def test_parser_allows_amend_no_edit_without_turning_plain_commit_into_amend():
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    amend = parser.parse("git commit --amend --no-edit")
    assert amend.has_option("--amend")
    assert amend.has_option("--no-edit")
    assert amend.executor_args == ["--amend"]

    plain_no_edit = parser.parse("git commit --no-edit")
    assert registry.require("commit").validate(plain_no_edit) == (
        "fatal: options '--no-edit' and '--amend' must be used together"
    )


def test_parser_rejects_non_git_commands():
    with pytest.raises(NonGitCommandError) as exc:
        GitCommandParser().parse("python cleanup.py")

    assert exc.value.exit_code == 127
    assert "python: command not found" in str(exc.value)


def test_parser_reports_invalid_quoting():
    with pytest.raises(GitCommandParseError):
        GitCommandParser().parse('git commit -m "unfinished')


def test_parser_rejects_shell_chaining_and_substitution():
    parser = GitCommandParser()

    for command in [
        "git status && git log",
        "git status; git log",
        "git status | cat",
        "git status > out.txt",
        "git status $(cat secret)",
    ]:
        with pytest.raises(GitCommandParseError):
            parser.parse(command)


def test_parser_supports_long_option_values_and_combined_commit_flags():
    parser = GitCommandParser()

    init = parser.parse("git init --initial-branch=trunk docs")
    commit = parser.parse('git commit -am "Update tracked files"')

    assert init.options["--initial-branch"] == ("trunk",)
    assert init.args == ("docs",)
    assert commit.has_option("-a")
    assert commit.message == "Update tracked files"
    assert commit.normalized_text == "git commit -a -m 'Update tracked files'"


@pytest.mark.parametrize(
    "command",
    [
        "git status",
        "git status -s",
        "git status --short",
        "git status --porcelain",
        "git status -sb",
        "git status --ignored",
        "git diff",
        "git diff README.md",
        "git diff --staged",
        "git diff --cached",
        "git diff --staged README.md",
        "git diff --cached README.md",
        "git diff HEAD",
        "git diff --name-only",
        "git diff --staged --name-only",
        "git log",
        "git log --oneline",
        "git log --oneline --graph --all",
        "git log -n 2",
        "git log --max-count=2",
        "git show",
        "git show c1",
        "git show --name-only",
        "git branch",
        "git branch -v",
        "git remote",
        "git remote -v",
        "git reflog",
        "git check-ignore -v .env",
        "git ls-files",
    ],
)
def test_parser_and_registry_support_module_one_diagnostic_forms(command):
    parsed = GitCommandParser().parse(command)
    registry = GitCommandRegistry()
    spec = registry.get(parsed.subcommand)

    assert spec is not None
    assert spec.validate(parsed) is None
    assert spec.is_diagnostic(parsed) is True
    assert spec.is_counted(parsed) is False


@pytest.mark.parametrize(
    "command",
    [
        "git init",
        "git init docs-site",
        "git init -b trunk",
        "git init --initial-branch trunk",
        "git init --initial-branch=trunk",
        "git init -q",
        "git init --quiet",
        "git init -q -b main research-log",
        "git init --quiet --initial-branch=main research-log",
        "git clone https://example.test/repo.git",
        "git clone https://example.test/repo.git repo-copy",
        "git clone -b starter https://example.test/repo.git",
        "git clone --branch starter https://example.test/repo.git",
        "git clone -b starter https://example.test/repo.git repo-copy",
        "git clone --branch starter https://example.test/repo.git repo-copy",
        "git clone --depth 1 https://example.test/repo.git",
        "git clone --depth 1 https://example.test/repo.git repo-copy",
        "git clone --depth 1 -b starter https://example.test/repo.git repo-copy",
        "git clone --depth 1 --branch starter https://example.test/repo.git repo-copy",
        "git add README.md",
        "git add README.md docs/intro.md",
        "git add docs/",
        "git add .",
        "git add -A",
        "git add --all",
        "git add -u",
        "git add --update",
        "git add -p",
        "git add -p README.md",
        "git add --patch README.md",
        'git commit -m "Add docs"',
        'git commit --message "Add docs"',
        'git commit -am "Update tracked files"',
        'git commit -a -m "Update tracked files"',
        "git commit --amend",
        'git commit --amend -m "Update message"',
        "git commit --amend --no-edit",
        "git rm --cached .env",
        "git rm -r --cached dist",
        "git restore README.md",
        "git restore README.md docs/intro.md",
        "git restore .",
        "git restore --staged README.md",
        "git restore --staged README.md docs/intro.md",
        "git restore --staged .",
    ],
)
def test_parser_and_registry_support_module_one_action_forms(command):
    parsed = GitCommandParser().parse(command)
    registry = GitCommandRegistry()
    spec = registry.get(parsed.subcommand)

    assert spec is not None
    assert spec.validate(parsed) is None
    assert spec.is_diagnostic(parsed) is False
    assert spec.is_counted(parsed) is True


@pytest.mark.parametrize(
    "command",
    [
        "git fetch",
        "git fetch origin",
        "git merge feature/app",
        "git merge --abort",
        "git merge --continue",
        "git checkout --ours src/auth.js",
        "git checkout --theirs src/auth.js",
        "git config --global merge.tool vscode",
        "git config --global mergetool.vscode.cmd \"code --wait $MERGED\"",
        "git mergetool",
        "git mergetool --tool vimdiff",
        "git cherry-pick c1",
        "git cherry-pick --no-commit c1",
        "git cherry-pick -n c1",
        "git cherry-pick --abort",
        "git diff main..feature",
    ],
)
def test_parser_and_registry_support_module_three_forms(command):
    parsed = GitCommandParser().parse(command)
    registry = GitCommandRegistry()
    spec = registry.get(parsed.subcommand)

    assert spec is not None
    assert spec.validate(parsed) is None
    if parsed.subcommand == "diff":
        assert spec.is_diagnostic(parsed) is True
        assert spec.is_counted(parsed) is False
    else:
        assert spec.is_diagnostic(parsed) is False
        assert spec.is_counted(parsed) is True


@pytest.mark.parametrize(
    "command",
    [
        "git pull",
        "git stash",
        "git tag v1",
        "git branch feature",
        "git branch -d stale",
        "git remote add origin https://example.test/repo.git",
        "git checkout main",
        "git reset HEAD README.md",
        "git clone --bare https://example.test/repo.git",
        "git clone --mirror https://example.test/repo.git",
        "git clone --recurse-submodules https://example.test/repo.git",
        "git clone --no-checkout https://example.test/repo.git",
        "git clone --filter blob:none https://example.test/repo.git",
        "git clone --template template https://example.test/repo.git",
        "git clone --separate-git-dir .git https://example.test/repo.git",
        'git commit --allow-empty -m "Empty"',
        "git add --intent-to-add README.md",
    ],
)
def test_registry_rejects_unsupported_non_module_one_forms(command):
    result = GitCommandEngine().process(
        {
            "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {}}],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"README.md": "v2"},
            "staging": {},
        },
        command,
    )

    assert result.processed is False
    assert result.exit_code == 129


@pytest.mark.parametrize(
    "command",
    [
        "git push origin main",
        "git rebase main",
        "git revert c0",
        "git switch -c rescue",
        "git merge-base main feature",
        "git rev-list --count main..feature",
    ],
)
def test_registry_accepts_module_four_command_forms(command):
    parser = GitCommandParser()
    registry = GitCommandRegistry()
    parsed = parser.parse(command)
    spec = registry.get(parsed.subcommand)
    assert spec is not None
    assert spec.validate(parsed) is None


def test_registry_rejects_unsupported_flags_and_classifies_diagnostics():
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    bad = parser.parse("git status --wat")
    assert registry.require("status").validate(bad) == "error: unknown option `--wat`."

    missing_url = parser.parse("git clone --depth 1")
    assert registry.require("clone").validate(missing_url) == (
        "fatal: You must specify a repository to clone."
    )
    too_many_clone_args = parser.parse("git clone https://example.test/repo.git one two")
    assert registry.require("clone").validate(too_many_clone_args) == (
        "usage: git clone <repository> [<directory>]"
    )
    invalid_depth = parser.parse("git clone --depth 0 https://example.test/repo.git")
    assert registry.require("clone").validate(invalid_depth) == (
        "fatal: invalid depth value: 0"
    )
    unsupported_clone = parser.parse("git clone --bare https://example.test/repo.git")
    assert registry.require("clone").validate(unsupported_clone) == (
        "error: unknown option `--bare`. Module 1 clone supports only -b/--branch and --depth."
    )
    with pytest.raises(GitCommandParseError, match="requires a value"):
        parser.parse("git clone -b")
    with pytest.raises(GitCommandParseError, match="requires a value"):
        parser.parse("git clone --depth")

    assert registry.is_diagnostic(parser.parse("git status"))
    assert registry.is_diagnostic(parser.parse("git log --oneline --graph --all"))
    assert registry.is_diagnostic(parser.parse("git branch -v"))
    assert registry.is_diagnostic(parser.parse("git remote -v"))
    assert not registry.is_diagnostic(parser.parse("git branch -d stale"))


def test_intent_mapper_unifies_common_command_variants():
    parser = GitCommandParser()
    mapper = CommandIntentMapper()

    add_a = mapper.map(parser.parse("git add -A"))
    add_all = mapper.map(parser.parse("git add --all"))
    add_update = mapper.map(parser.parse("git add -u"))
    commit_short = mapper.map(parser.parse('git commit -m "Add README"'))
    commit_long = mapper.map(parser.parse('git commit --message "Add README"'))
    commit_all = mapper.map(parser.parse('git commit -am "Update tracked files"'))
    init_short = mapper.map(parser.parse("git init -b main"))
    init_long = mapper.map(parser.parse("git init --initial-branch=main"))
    init_quiet = mapper.map(parser.parse("git init -q"))
    clone_branch = mapper.map(
        parser.parse("git clone --depth 1 -b starter https://example.test/repo.git lab")
    )

    assert add_a.operations[0].name == add_all.operations[0].name == "StageAllChanges"
    assert add_update.operations[0].name == "StageTrackedChangesOnly"
    assert commit_short.operations[0].name == commit_long.operations[0].name == "CreateCommit"
    assert [operation.name for operation in commit_all.operations] == [
        "StageTrackedChangesOnly",
        "CreateCommit",
    ]
    assert (
        init_short.operations[0].params["initial_branch"]
        == init_long.operations[0].params["initial_branch"]
        == "main"
    )
    assert init_quiet.operations[0].params["quiet"] is True
    assert clone_branch.operations[0].name == "CloneRepository"
    assert clone_branch.operations[0].params["branch"] == "starter"
    assert clone_branch.operations[0].params["depth"] == 1
    assert clone_branch.operations[0].params["destination"] == "lab"


def test_engine_blocks_shell_and_unsupported_git_without_mutation():
    state = {"commits": [], "branches": {"main": None}, "head": {"type": "branch", "name": "main"}}
    engine = GitCommandEngine()

    shell = engine.process(state, "powershell Remove-Item important.txt")
    unsupported = engine.process(state, "git pull")

    assert shell.exit_code == 127
    assert shell.state == state
    assert unsupported.exit_code == 129
    assert "is not a git command" in unsupported.output
    assert unsupported.state == state


def test_engine_mutates_state_for_supported_commit_with_quoted_message():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"src/login.tsx": "login-form-v1"},
        "staging": {},
    }
    engine = GitCommandEngine()

    staged = engine.process(state, "git add src/login.tsx").state
    committed = engine.process(staged, 'git commit -m "Add login form"')

    assert committed.processed is True
    assert committed.state["commits"][-1]["message"] == "Add login form"
    assert committed.state["branches"]["main"] == "c1"


def test_workspace_file_creation_refreshes_gitignore_status_before_git_commands():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {
            ".env": {"status": "untracked", "content": "SECRET=local"},
            "node_modules/pkg/index.js": {"status": "untracked", "content": "package"},
        },
        "staging": {},
    }
    engine = GitCommandEngine()

    written = WorkspaceFileStateService().create_file(
        state,
        path=".gitignore",
        content="node_modules/\n.env*\n",
    )
    status = engine.process(written, "git status --short --ignored")
    staged = engine.process(written, "git add .gitignore")
    committed = engine.process(staged.state, 'git commit -m "Add ignore rules"')

    assert written["working_tree"][".gitignore"]["content"] == "node_modules/\n.env*\n"
    assert written["working_tree"][".env"]["status"] == "ignored"
    assert written["working_tree"]["node_modules/pkg/index.js"]["status"] == "ignored"
    assert "!! .env" in status.output
    assert committed.state["commits"][-1]["tree"][".gitignore"] == "node_modules/\n.env*\n"
    assert ".env" not in committed.state["commits"][-1]["tree"]


def test_engine_marks_diagnostics_non_mutating():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "v2"},
        "staging": {},
    }

    result = GitCommandEngine().process(state, "git diff --staged")

    assert result.processed is True
    assert result.diagnostic is True
    assert result.state == RepositoryStateSimulator().normalize_state(state)


def test_conflict_diagnostics_and_merge_continue_are_supported():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.js": "timeout=3000"}},
            {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"src/auth.js": "timeout=5000"}},
            {"id": "c2", "message": "Feature", "parents": ["c0"], "tree": {"src/auth.js": "timeout=2500"}},
        ],
        "branches": {"main": "c1", "feature/auth-timeout": "c2"},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
        "conflict_on_merge": True,
        "conflict_files": ["src/auth.js"],
        "merge_resolutions": {"src/auth.js": "timeout=5000\nretry=enabled"},
    }
    engine = GitCommandEngine()

    conflicted = engine.process(state, "git merge feature/auth-timeout").state
    ours = engine.process(conflicted, "git diff --ours src/auth.js")
    theirs = engine.process(conflicted, "git diff --theirs src/auth.js")
    base = engine.process(conflicted, "git diff --base src/auth.js")
    marker_check = engine.process(conflicted, "git diff --check src/auth.js")
    unmerged = engine.process(conflicted, "git ls-files -u")
    tool = engine.process(conflicted, "git mergetool --tool vscode src/auth.js")
    edited = WorkspaceFileStateService().write_file(
        tool.state,
        path="src/auth.js",
        content="timeout=5000\nretry=enabled",
    )
    staged = engine.process(edited, "git add src/auth.js").state
    completed = engine.process(staged, "git merge --continue")

    assert ours.diagnostic is True
    assert "+timeout=5000" in ours.output
    assert "+timeout=2500" in theirs.output
    assert "+timeout=3000" in base.output
    assert "leftover conflict marker" in marker_check.output
    assert "src/auth.js" in unmerged.output
    assert tool.state["conflicts"] == ["src/auth.js"]
    assert tool.state["staging"] == {}
    assert tool.state["operation_metadata"]["last_mergetool_paths"] == ["src/auth.js"]
    assert completed.processed is True
    assert completed.state["conflicts"] == []
    assert completed.state["branches"]["main"] == "c3"
    assert completed.state["commits"][-1]["is_merge"] is True


def test_checkout_ours_and_theirs_write_conflict_sides_without_staging():
    simulator = RepositoryStateSimulator()
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.js": "timeout=3000"}},
            {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"src/auth.js": "timeout=5000"}},
            {"id": "c2", "message": "Feature", "parents": ["c0"], "tree": {"src/auth.js": "timeout=2500"}},
        ],
        "branches": {"main": "c1", "feature/auth-timeout": "c2"},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
        "conflict_on_merge": True,
        "conflict_files": ["src/auth.js"],
    }

    conflicted = simulator.process(state, "git merge feature/auth-timeout").state
    ours = simulator.process(conflicted, "git checkout --ours src/auth.js")
    theirs = simulator.process(conflicted, "git checkout --theirs src/auth.js")

    assert ours.processed is True
    assert ours.state["working_tree"]["src/auth.js"]["content"] == "timeout=5000"
    assert ours.state["staging"] == {}
    assert ours.state["conflicts"] == ["src/auth.js"]
    assert theirs.state["working_tree"]["src/auth.js"]["content"] == "timeout=2500"
    assert theirs.state["staging"] == {}
    assert theirs.state["conflicts"] == ["src/auth.js"]


def test_checkout_conflict_side_fails_outside_conflicted_paths():
    simulator = RepositoryStateSimulator()
    clean_state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
        }
    )

    no_conflict = simulator.process(clean_state, "git checkout --ours README.md")
    conflicted = simulator.process(
        {
            **clean_state,
            "conflicts": ["src/auth.js"],
            "conflict_details": {"src/auth.js": {"ours": "ours", "theirs": "theirs"}},
            "working_tree": {
                "src/auth.js": {
                    "status": "conflicted",
                    "ours": "ours",
                    "theirs": "theirs",
                }
            },
        },
        "git checkout --ours README.md",
    )

    assert no_conflict.processed is False
    assert "--ours/--theirs can only be used" in no_conflict.output
    assert conflicted.processed is False
    assert "is not an unmerged file" in conflicted.output


def test_checkout_side_then_add_and_continue_finishes_merge():
    simulator = RepositoryStateSimulator()
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.js": "timeout=3000"}},
            {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"src/auth.js": "timeout=5000"}},
            {"id": "c2", "message": "Feature", "parents": ["c0"], "tree": {"src/auth.js": "timeout=2500"}},
        ],
        "branches": {"main": "c1", "feature/auth-timeout": "c2"},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
        "conflict_on_merge": True,
        "conflict_files": ["src/auth.js"],
    }

    state = simulator.process(state, "git merge feature/auth-timeout").state
    state = simulator.process(state, "git checkout --theirs src/auth.js").state
    state = simulator.process(state, "git add src/auth.js").state
    result = simulator.process(state, "git merge --continue")

    assert result.processed is True
    assert result.state["conflicts"] == []
    assert result.state["working_tree"] == {}
    assert result.state["branches"]["main"] == "c3"
    assert result.state["commits"][-1]["parents"] == ["c1", "c2"]
    assert result.state["commits"][-1]["tree"]["src/auth.js"] == "timeout=2500"

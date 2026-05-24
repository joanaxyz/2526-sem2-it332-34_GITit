from textwrap import dedent

from simulator.command_engine import GitCommandEngine


def run(state: dict, command: str):
    return GitCommandEngine().process(state, command)


def committed_state():
    return {
        "commits": [
            {"id": "c0", "message": "Add README", "parents": [], "tree": {"README.md": "readme-v1"}}
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "remotes": {"origin": "https://example.test/repo.git"},
    }


def test_status_clean_repo_snapshot():
    result = run(committed_state(), "git status")

    assert result.output == dedent(
        """\
        On branch main

        nothing to commit, working tree clean"""
    )


def test_status_with_untracked_file_snapshot():
    state = committed_state() | {"working_tree": {"notes.md": "untracked"}}

    result = run(state, "git status")

    assert result.output == dedent(
        """\
        On branch main

        Untracked files:
          (use "git add <file>..." to include in what will be committed)
        \tnotes.md

        nothing added to commit but untracked files present (use "git add" to track)"""
    )


def test_short_status_snapshot():
    state = committed_state() | {
        "staging": {"README.md": "readme-v2", "new.md": "added"},
        "working_tree": {"README.md": "readme-v3", "draft.md": "untracked"},
    }

    result = run(state, "git status -s")

    assert result.output == dedent(
        """\
        MM README.md
        ?? draft.md
        A  new.md"""
    )


def test_init_quiet_and_normal_snapshots():
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "none"},
    }

    normal = run(state, "git init")
    quiet = run(state, "git init --quiet")

    assert normal.output == "Initialized empty Git repository in .git/"
    assert quiet.output == ""


def test_add_missing_pathspec_snapshot():
    result = run(committed_state(), "git add missing.txt")

    assert result.exit_code == 128
    assert result.output == "fatal: pathspec 'missing.txt' did not match any files"


def test_commit_success_and_no_changes_snapshots():
    state = committed_state() | {"working_tree": {"app.py": "app-v1"}}
    staged = run(state, "git add app.py").state

    committed = run(staged, 'git commit -m "Add app"')
    clean_commit = run(committed.state, 'git commit -m "No changes"')

    assert committed.output == dedent(
        """\
        [main c1] Add app
         1 file changed, 1 insertion(+)"""
    )
    assert clean_commit.output == "nothing to commit, working tree clean"


def test_log_and_graph_snapshots():
    state = committed_state()

    oneline = run(state, "git log --oneline")
    graph = run(state, "git log --oneline --graph --all")

    assert oneline.output == "c0 Add README"
    assert graph.output == "* c0 Add README"


def test_diff_and_staged_diff_snapshots():
    state = committed_state() | {"working_tree": {"README.md": "readme-v2"}}
    staged_state = run(state, "git add README.md").state

    diff = run(state, "git diff")
    staged = run(staged_state, "git diff --staged")

    expected = dedent(
        """\
        diff --git a/README.md b/README.md
        index 0000000..1111111 100644
        --- a/README.md
        +++ b/README.md
        @@ -1 +1 @@
        -readme-v1
        +readme-v2"""
    )
    assert diff.output == expected
    assert staged.output == expected


def test_branch_and_remote_snapshots():
    state = committed_state() | {"branches": {"main": "c0", "feature/docs": "c0"}}

    assert run(state, "git branch").output == "  feature/docs\n* main"
    assert (
        run(state, "git branch -v").output
        == "  feature/docs     c0 Add README\n* main             c0 Add README"
    )
    assert run(state, "git remote -v").output == (
        "origin\thttps://example.test/repo.git (fetch)\n"
        "origin\thttps://example.test/repo.git (push)"
    )

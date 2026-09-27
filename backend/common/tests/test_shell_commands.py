"""Workspace terminal shell commands at the command-submission trust boundary."""

import pytest

from common.constants import COMMAND_DIAGNOSTIC
from common.exceptions import BadRequest
from common.git.client_command_execution import ClientCommandExecutionService
from common.git.git_pathspecs import rebase_git_pathspecs
from common.git.shell_commands import replay_shell_command
from common.git.workspace_tree import path_kind
from simulator.state import RepositoryStateNormalizer
from testing.frontend_execution import frontend_execution_payload


def repo():
    return RepositoryStateNormalizer().normalize(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "base",
                    "parents": [],
                    "tree": {"README.md": "hello\n", "src/app.py": "app", "src/util.py": "util"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
        }
    )


def replay(commands, state=None, cwd=""):
    state = state or repo()
    exit_codes = []
    for command in commands:
        state, exit_code = replay_shell_command(state, command, cwd)
        exit_codes.append(exit_code)
    return state, exit_codes


def submit(state, command, *, next_state=None, diagnostic=False, cwd=None, exit_code=0):
    payload = frontend_execution_payload(
        command,
        next_state if next_state is not None else state,
        diagnostic=diagnostic,
        command_family=command.split()[0],
        exit_code=exit_code,
        cwd=cwd,
    )
    return ClientCommandExecutionService().from_payload(
        repository_state=state, command=command, execution=payload
    )


class TestShellReplay:
    def test_touch_mkdir_and_redirects_edit_the_working_copy(self):
        state, exit_codes = replay(
            [
                "touch notes.md",
                "mkdir -p docs/guides",
                "echo '# Docs' > docs/index.md",
                "echo more >> docs/index.md",
                "touch missing/file.md",
            ]
        )
        assert exit_codes == [0, 0, 0, 0, 1]
        assert state["working_tree"]["notes.md"] == {"status": "untracked", "content": ""}
        assert state["working_tree"]["docs/index.md"] == {
            "status": "untracked",
            "content": "# Docs\nmore\n",
        }
        assert state["directories"] == ["docs/guides"]

    def test_rm_keeps_the_emptied_folder_and_rm_r_removes_it(self):
        emptied, exit_codes = replay(["rm src", "rm src/app.py src/util.py"])
        assert exit_codes == [1, 0]
        assert emptied["working_tree"]["src/app.py"] == "deleted"
        assert path_kind(emptied, "src") == "directory"

        removed, _ = replay(["rm -r src"])
        assert path_kind(removed, "src") is None

    def test_mv_and_cp_follow_shell_semantics(self):
        state, exit_codes = replay(
            ["mkdir lib", "mv src/util.py lib", "cp -r lib vendor", "cp src copy"]
        )
        assert exit_codes == [0, 0, 0, 1]
        assert state["working_tree"]["lib/util.py"] == {"status": "untracked", "content": "util"}
        assert state["working_tree"]["vendor/util.py"] == {"status": "untracked", "content": "util"}
        assert state["working_tree"]["src/util.py"] == "deleted"

    def test_paths_resolve_from_the_working_directory_and_globs_expand(self):
        state, _ = replay(["touch a.log b.log keep.txt", "rm *.log"], cwd="src")
        assert "src/a.log" not in state["working_tree"]
        assert state["working_tree"]["src/keep.txt"] == {"status": "untracked", "content": ""}

    def test_missing_working_directory_falls_back_to_nearest_folder(self):
        state, _ = replay(["touch here.txt"], cwd="gone/deeper")
        assert "here.txt" in state["working_tree"]


class TestShellSubmission:
    def test_file_command_uses_backend_replay_not_client_state(self):
        forged = {**repo(), "branches": {"main": "forged"}}
        execution = submit(repo(), "touch notes.md", next_state=forged)

        assert execution.next_state["branches"] == {"main": "c0"}
        assert execution.next_state["working_tree"]["notes.md"]["status"] == "untracked"
        assert execution.state_mutated is True
        assert execution.classification == COMMAND_DIAGNOSTIC
        assert execution.increment == 0

    def test_file_command_reports_backend_exit_code(self):
        execution = submit(repo(), "rm missing.txt", exit_code=0)
        assert execution.result.exit_code == 1
        assert execution.state_mutated is False

    def test_read_only_commands_are_free_diagnostics(self):
        execution = submit(repo(), "ls -a src", diagnostic=True, cwd="src")
        assert execution.classification == COMMAND_DIAGNOSTIC
        assert execution.state_mutated is False

    def test_diagnostic_flag_must_match_the_command(self):
        with pytest.raises(BadRequest):
            submit(repo(), "ls", diagnostic=False)
        with pytest.raises(BadRequest):
            submit(repo(), "touch notes.md", diagnostic=True)

    def test_rejects_working_directory_outside_the_project(self):
        with pytest.raises(BadRequest):
            submit(repo(), "ls", diagnostic=True, cwd="../elsewhere")

    def test_git_pathspecs_are_verified_relative_to_the_working_directory(self):
        state = RepositoryStateNormalizer().normalize(
            {**repo(), "working_tree": {"src/app.py": {"status": "modified", "content": "v2"}}}
        )
        staged = RepositoryStateNormalizer().normalize(
            {
                **state,
                "staging": {"src/app.py": {"status": "modified", "content": "v2"}},
                "working_tree": {},
            }
        )
        payload = frontend_execution_payload("git add app.py", staged, cwd="src")
        execution = ClientCommandExecutionService().from_payload(
            repository_state=state, command="git add app.py", execution=payload
        )
        assert execution.next_state["staging"] == {
            "src/app.py": {"status": "modified", "content": "v2"}
        }


def test_rebase_git_pathspecs():
    assert rebase_git_pathspecs("git add .", "src") == "git add src"
    assert rebase_git_pathspecs("git add ../README.md", "src") == "git add README.md"
    assert rebase_git_pathspecs('git commit -m "fix it" app.py', "src") == (
        "git commit -m 'fix it' src/app.py"
    )
    assert rebase_git_pathspecs("git checkout main -- app.py", "src") == (
        "git checkout main -- src/app.py"
    )
    assert rebase_git_pathspecs("git switch main", "src") == "git switch main"
    assert rebase_git_pathspecs("git add app.py", "") == "git add app.py"

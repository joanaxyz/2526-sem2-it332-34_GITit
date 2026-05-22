from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from simulator.pygit2_services import (
    Pygit2RemoteRepositoryFactory,
    Pygit2RepositoryMaterializer,
)
from simulator.services import RepositoryStateSimulator, normalize_command, parse_git_command


@dataclass(frozen=True)
class CommandExecutionResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    exit_code: int | None = None


@dataclass(frozen=True)
class TerminalExecutionResult:
    output: str
    exit_code: int | None


class Pygit2GitCommandEngine:
    """Execute student Git commands against an isolated pygit2 materialized repo.

    The durable scenario state remains the small authored JSON graph, but terminal
    output is produced by the real Git executable in a temporary workspace.
    """

    def __init__(self, *, timeout_seconds: float = 3.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.simulator = RepositoryStateSimulator()
        self.terminal = Pygit2GitTerminal(timeout_seconds=timeout_seconds)

    def process(self, state: dict, command: str) -> CommandExecutionResult:
        normalized = normalize_command(command)
        sim_result = self.simulator.process(state, command)
        terminal_result = self.terminal.run(state=state, command=normalized)
        output = terminal_result.output if terminal_result.output or normalized else sim_result.output
        return CommandExecutionResult(
            processed=sim_result.processed,
            state=sim_result.state,
            output=output,
            normalized_command=sim_result.normalized_command or normalized,
            exit_code=terminal_result.exit_code,
        )


class Pygit2GitTerminal:
    def __init__(self, *, timeout_seconds: float = 3.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.materializer = Pygit2RepositoryMaterializer()
        self.remote_factory = Pygit2RemoteRepositoryFactory()

    def run(self, *, state: dict, command: str) -> TerminalExecutionResult:
        if not command:
            return TerminalExecutionResult(output="", exit_code=None)
        parts = parse_git_command(command)
        if parts is None:
            command_name = command.split(maxsplit=1)[0] if command.split() else command
            return TerminalExecutionResult(
                output=f"{command_name}: command not found",
                exit_code=127,
            )

        with tempfile.TemporaryDirectory(prefix="git-it-command-") as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            workspace.mkdir(parents=True, exist_ok=True)
            remote_paths = self._materialize_remotes(state=state, root=root, command_parts=parts)
            remote_overrides = {
                name: path
                for name, path in remote_paths.items()
                if name in state.get("remotes", {})
            }

            if state.get("repository_initialized", True):
                self.materializer.materialize(
                    state=state,
                    path=workspace,
                    remote_url_overrides=remote_overrides,
                )
            else:
                self.materializer.materialize_workspace_files(state=state, path=workspace)

            run_parts = self._rewrite_clone_url(parts=parts, remote_paths=remote_paths)
            result = self._run_git(parts=run_parts, cwd=workspace, root=root)
            return TerminalExecutionResult(
                output=self._restore_display_urls(
                    output=self._combined_output(result),
                    state=state,
                    remote_paths=remote_paths,
                    original_parts=parts,
                ),
                exit_code=result.returncode,
            )

    def _run_git(
        self,
        *,
        parts: list[str],
        cwd: Path,
        root: Path,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "GIT it",
                "GIT_AUTHOR_EMAIL": "git-it@example.test",
                "GIT_COMMITTER_NAME": "GIT it",
                "GIT_COMMITTER_EMAIL": "git-it@example.test",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_EDITOR": "true",
                "GIT_PAGER": "cat",
                "GIT_TERMINAL_PROMPT": "0",
                "HOME": str(root / "home"),
            }
        )
        (root / "home").mkdir(exist_ok=True)
        try:
            return subprocess.run(
                [
                    "git",
                    "-c",
                    "core.pager=cat",
                    "-c",
                    "color.ui=false",
                    "-c",
                    "core.autocrlf=false",
                    *parts[1:],
                ],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return subprocess.CompletedProcess(
                args=exc.cmd,
                returncode=124,
                stdout=exc.stdout or "",
                stderr="fatal: command timed out in the practice workspace\n",
            )

    def _materialize_remotes(
        self,
        *,
        state: dict,
        root: Path,
        command_parts: list[str],
    ) -> dict[str, str]:
        remote_paths: dict[str, str] = {}
        for remote_name in state.get("remotes", {}):
            remote_paths[remote_name] = self.remote_factory.materialize_remote(
                state=state,
                path=root / f"{remote_name}.git",
                remote_name=remote_name,
            )

        if len(command_parts) >= 3 and command_parts[1] == "clone":
            url = command_parts[2]
            if url not in remote_paths.values():
                remote_paths[url] = self.remote_factory.materialize_remote(
                    state=state,
                    path=root / "clone-origin.git",
                    remote_name="origin",
                )
        return remote_paths

    def _rewrite_clone_url(self, *, parts: list[str], remote_paths: dict[str, str]) -> list[str]:
        if len(parts) >= 3 and parts[1] == "clone" and parts[2] in remote_paths:
            return [*parts[:2], remote_paths[parts[2]], *parts[3:]]
        return parts

    def _restore_display_urls(
        self,
        *,
        output: str,
        state: dict,
        remote_paths: dict[str, str],
        original_parts: list[str],
    ) -> str:
        restored = output
        for remote_name, original_url in state.get("remotes", {}).items():
            local_url = remote_paths.get(remote_name)
            if local_url:
                restored = restored.replace(local_url, original_url)
        if len(original_parts) >= 3 and original_parts[1] == "clone":
            local_url = remote_paths.get(original_parts[2])
            if local_url:
                restored = restored.replace(local_url, original_parts[2])
        return restored.rstrip("\n")

    def _combined_output(self, result: subprocess.CompletedProcess[str]) -> str:
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        if stdout and stderr:
            return f"{stdout.rstrip()}\n{stderr.rstrip()}"
        return (stdout or stderr).rstrip()

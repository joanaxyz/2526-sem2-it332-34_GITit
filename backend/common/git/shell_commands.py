"""Backend replay of the workspace terminal's shell commands.

The browser simulator runs shell commands instantly. Read-only ones (``ls``,
``cd``, ``cat`` ...) are diagnostics whose submitted state is ignored.
File-changing ones (``touch``, ``mkdir``, ``rm``,
``mv``, ``cp`` and ``echo``/``cat`` redirection) are replayed here from the
persisted state through the same trusted workspace-file helpers the Project
Files endpoints use, so the backend owns the resulting working copy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from common.exceptions import BadRequest
from common.git.shell_syntax import (
    Redirect,
    ShellInvocation,
    ShellSyntaxError,
    expand_shell_words,
    is_inside_git_directory,
    parse_shell_command,
    resolve_shell_path,
)
from common.git.workspace_files import (
    create_workspace_directory,
    create_workspace_file,
    delete_workspace_file,
    rename_workspace_file,
    write_workspace_file,
)
from common.git.workspace_tree import (
    descendant_paths,
    directory_entries,
    parent_path,
    path_kind,
)
from simulator.state import RepositoryStateNormalizer

READ_ONLY_PROGRAMS = frozenset({"pwd", "ls", "cd", "tree", "cat", "echo", "clear"})
FILE_PROGRAMS = frozenset({"touch", "mkdir", "rmdir", "rm", "mv", "cp"})
REDIRECTABLE_PROGRAMS = frozenset({"echo", "cat"})

_CWD_PART = re.compile(r"^[^<>|]+$")
_NORMALIZER = RepositoryStateNormalizer()


def shell_program(command: str) -> str | None:
    """The shell program a command starts with, or ``None`` for git/unknown input."""

    parts = command.strip().split()
    first = parts[0] if parts else ""
    return first if first in READ_ONLY_PROGRAMS or first in FILE_PROGRAMS else None


def shell_command_changes_files(command: str) -> bool:
    try:
        invocation = parse_shell_command(command)
    except ShellSyntaxError:
        return False
    if invocation.program in FILE_PROGRAMS:
        return True
    return invocation.program in REDIRECTABLE_PROGRAMS and invocation.redirect is not None


def normalize_client_cwd(value: object) -> str:
    """Validate the terminal working directory submitted with a command."""

    if value in (None, ""):
        return ""
    if not isinstance(value, str) or len(value) > 240:
        raise BadRequest("execution.cwd must be a project-relative folder path.")
    parts = value.split("/")
    if any(part in {"", ".", ".."} or not _CWD_PART.match(part) for part in parts):
        raise BadRequest("execution.cwd must be a project-relative folder path.")
    if parts[0] == ".git":
        raise BadRequest("execution.cwd must be a project-relative folder path.")
    return value


def effective_cwd(state: dict, cwd: str) -> str:
    """Nearest folder at or above ``cwd`` that still exists in the working copy."""

    current = cwd
    while current and path_kind(state, current) != "directory":
        current = parent_path(current)
    return current


def replay_shell_command(state: dict, command: str, cwd: str) -> tuple[dict, int]:
    """Apply a file-changing shell command; return the new state and exit code."""

    run = _ShellRun(state=state, cwd=effective_cwd(state, cwd))
    try:
        invocation = parse_shell_command(command)
    except ShellSyntaxError:
        return state, 2
    _run_program(run, invocation)
    return run.state, run.exit_code


@dataclass
class _ShellRun:
    state: dict
    cwd: str
    exit_code: int = 0
    errors: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.errors.append(message)
        self.exit_code = max(self.exit_code, 1)

    def mutate(self, apply) -> bool:
        try:
            self.state = apply(self.state)
            return True
        except BadRequest as error:
            self.fail(str(error))
            return False

    def resolve(self, operand: str) -> str | None:
        path = resolve_shell_path(self.cwd, operand)
        if path is None or is_inside_git_directory(path):
            self.fail(f"{operand}: not usable")
            return None
        return path

    def kind(self, path: str) -> str | None:
        return path_kind(self.state, path)

    def parent_missing(self, path: str) -> bool:
        return self.kind(parent_path(path)) != "directory"


def _run_program(run: _ShellRun, invocation: ShellInvocation) -> None:
    program, redirect = invocation.program, invocation.redirect
    if redirect is not None and program not in REDIRECTABLE_PROGRAMS:
        run.fail("redirection unsupported")
        return
    args = expand_shell_words(run.state, run.cwd, invocation.args)
    handlers = {"touch": _touch, "mkdir": _mkdir, "rmdir": _rmdir, "rm": _rm, "mv": _mv, "cp": _cp}
    if program in handlers:
        handlers[program](run, args)
    elif program == "echo" and redirect is not None:
        _echo(run, args, redirect)
    elif program == "cat" and redirect is not None:
        _cat(run, args, redirect)


def _parse_flags(run: _ShellRun, args: list[str], known: dict[str, str]):
    flags: set[str] = set()
    operands: list[str] = []
    options_done = False
    for arg in args:
        if options_done or arg == "-" or not arg.startswith("-"):
            operands.append(arg)
            continue
        if arg == "--":
            options_done = True
            continue
        names = [arg] if arg.startswith("--") else list(arg[1:])
        for name in names:
            if name not in known:
                run.fail(f"invalid option {name}")
                return None
            flags.add(known[name])
    return flags, operands


def _file_content(state: dict, path: str) -> object:
    entry = _NORMALIZER.visible_project_tree(state, assume_normalized=True).get(path)
    content = _NORMALIZER.entry_content(entry)
    return "" if content is None else content


def _write_file(run: _ShellRun, path: str, content: object) -> bool:
    if run.kind(path) == "file":
        return run.mutate(lambda state: write_workspace_file(state, path=path, content=content))
    return run.mutate(lambda state: create_workspace_file(state, path=path, content=content))


def _touch(run: _ShellRun, args: list[str]) -> None:
    parsed = _parse_flags(run, args, {})
    if parsed is None:
        return
    if not parsed[1]:
        run.fail("touch: missing file operand")
    for operand in parsed[1]:
        path = run.resolve(operand)
        if path is None or run.kind(path) is not None:
            continue
        if run.parent_missing(path):
            run.fail(f"touch: {operand}")
            continue
        _write_file(run, path, "")


def _mkdir(run: _ShellRun, args: list[str]) -> None:
    parsed = _parse_flags(run, args, {"p": "parents", "--parents": "parents"})
    if parsed is None:
        return
    flags, operands = parsed
    parents = "parents" in flags
    if not operands:
        run.fail("mkdir: missing operand")
    for operand in operands:
        path = run.resolve(operand)
        if path is None:
            continue
        kind = run.kind(path)
        if kind == "directory" and parents:
            continue
        if kind is not None:
            run.fail(f"mkdir: {operand}: File exists")
            continue
        if parents:
            ancestors = path.split("/")[:-1]
            if any(
                run.kind("/".join(ancestors[:index])) == "file"
                for index in range(1, len(ancestors) + 1)
            ):
                run.fail(f"mkdir: {operand}: Not a directory")
                continue
        elif run.parent_missing(path):
            run.fail(f"mkdir: {operand}: No such file or directory")
            continue
        run.mutate(lambda state, path=path: create_workspace_directory(state, path=path))


def _rmdir(run: _ShellRun, args: list[str]) -> None:
    parsed = _parse_flags(run, args, {})
    if parsed is None:
        return
    if not parsed[1]:
        run.fail("rmdir: missing operand")
    for operand in parsed[1]:
        path = run.resolve(operand)
        if path is None:
            continue
        if run.kind(path) != "directory" or not path or directory_entries(run.state, path):
            run.fail(f"rmdir: {operand}")
            continue
        run.mutate(lambda state, path=path: delete_workspace_file(state, path=path))


def _rm(run: _ShellRun, args: list[str]) -> None:
    known = {"r": "recursive", "R": "recursive", "f": "force"}
    parsed = _parse_flags(run, args, {**known, "--recursive": "recursive", "--force": "force"})
    if parsed is None:
        return
    flags, operands = parsed
    if not operands and "force" not in flags:
        run.fail("rm: missing operand")
    for operand in operands:
        if _base_name(operand) in {".", ".."}:
            run.fail(f"rm: refusing to remove {operand}")
            continue
        path = run.resolve(operand)
        if path is None:
            continue
        if not path:
            run.fail(f"rm: refusing to remove {operand}")
            continue
        kind = run.kind(path)
        if kind is None:
            if "force" not in flags:
                run.fail(f"rm: {operand}: No such file or directory")
            continue
        if kind == "directory" and "recursive" not in flags:
            run.fail(f"rm: {operand}: Is a directory")
            continue
        run.mutate(lambda state, path=path: delete_workspace_file(state, path=path))


def _plan_transfers(run: _ShellRun, operands: list[str], *, copy: bool, recursive: bool):
    if len(operands) < 2:
        run.fail("missing file operand")
        return []
    destination = run.resolve(operands[-1])
    if destination is None:
        return []
    destination_kind = run.kind(destination)
    sources = operands[:-1]
    if len(sources) > 1 and destination_kind != "directory":
        run.fail("target is not a directory")
        return []
    transfers = []
    for operand in sources:
        path = run.resolve(operand)
        if path is None:
            continue
        kind = run.kind(path)
        if kind is None or not path:
            run.fail(f"cannot stat {operand}")
            continue
        if kind == "directory" and copy and not recursive:
            run.fail(f"-r not specified; omitting directory {operand}")
            continue
        target = (
            _join_path(destination, _base_name(path))
            if destination_kind == "directory"
            else destination
        )
        if target == path or target.startswith(f"{path}/"):
            run.fail(f"cannot move or copy {operand} onto itself")
            continue
        transfers.append((path, kind, target))
    return transfers


def _mv(run: _ShellRun, args: list[str]) -> None:
    parsed = _parse_flags(run, args, {"f": "force", "--force": "force"})
    if parsed is None:
        return
    for path, kind, target in _plan_transfers(run, parsed[1], copy=False, recursive=True):
        target_kind = run.kind(target)
        if target_kind == "directory" and (kind == "file" or directory_entries(run.state, target)):
            run.fail(f"mv: cannot move {path} to {target}")
            continue
        if target_kind == "file" and kind == "directory":
            run.fail(f"mv: cannot overwrite {target} with a directory")
            continue
        if target_kind is None and run.parent_missing(target):
            run.fail(f"mv: cannot move {path} to {target}")
            continue
        if target_kind is not None and not run.mutate(
            lambda state, target=target: delete_workspace_file(state, path=target)
        ):
            continue
        run.mutate(
            lambda state, path=path, target=target: rename_workspace_file(
                state, path=path, new_path=target
            )
        )


def _cp(run: _ShellRun, args: list[str]) -> None:
    known = {"r": "recursive", "R": "recursive", "--recursive": "recursive"}
    parsed = _parse_flags(run, args, known)
    if parsed is None:
        return
    flags, operands = parsed
    for path, kind, target in _plan_transfers(
        run, operands, copy=True, recursive="recursive" in flags
    ):
        target_kind = run.kind(target)
        if target_kind is None and run.parent_missing(target):
            run.fail(f"cp: cannot create {target}")
            continue
        if kind == "file":
            if target_kind == "directory":
                run.fail(f"cp: cannot overwrite directory {target}")
            else:
                _write_file(run, target, _file_content(run.state, path))
            continue
        if target_kind == "file":
            run.fail(f"cp: cannot overwrite non-directory {target}")
            continue
        _copy_directory(run, path, target)


def _copy_directory(run: _ShellRun, source: str, target: str) -> None:
    files, directories = descendant_paths(run.state, source)

    def relocate(path: str) -> str:
        return f"{target}{path[len(source) :]}"

    if run.kind(target) is None and not run.mutate(
        lambda state: create_workspace_directory(state, path=target)
    ):
        return
    for directory in directories:
        destination = relocate(directory)
        kind = run.kind(destination)
        if kind == "file":
            run.fail(f"cp: cannot overwrite non-directory {destination}")
        elif kind is None:
            run.mutate(
                lambda state, destination=destination: create_workspace_directory(
                    state, path=destination
                )
            )
    for file_path in files:
        destination = relocate(file_path)
        if run.kind(destination) == "directory":
            run.fail(f"cp: cannot overwrite directory {destination}")
            continue
        _write_file(run, destination, _file_content(run.state, file_path))


def _redirect_output(run: _ShellRun, redirect: Redirect, text: str) -> None:
    path = run.resolve(redirect.target)
    if path is None:
        return
    kind = run.kind(path)
    if kind == "directory" or (kind is None and run.parent_missing(path)):
        run.fail(f"bash: {redirect.target}")
        return
    content: object = text
    if redirect.append and kind == "file":
        existing = _file_content(run.state, path)
        if not isinstance(existing, str):
            run.fail(f"bash: {redirect.target}: cannot append")
            return
        content = f"{existing}{text}"
    _write_file(run, path, content)


def _echo(run: _ShellRun, args: list[str], redirect: Redirect) -> None:
    no_newline = False
    while args and args[0] == "-n":
        no_newline = True
        args = args[1:]
    text = " ".join(args)
    _redirect_output(run, redirect, text if no_newline else f"{text}\n")


def _cat(run: _ShellRun, args: list[str], redirect: Redirect) -> None:
    parsed = _parse_flags(run, args, {})
    if parsed is None:
        return
    if not parsed[1]:
        run.fail("cat: name a file")
        return
    chunks: list[str] = []
    for operand in parsed[1]:
        path = run.resolve(operand)
        if path is None:
            continue
        if run.kind(path) != "file":
            run.fail(f"cat: {operand}")
            continue
        content = _file_content(run.state, path)
        if not isinstance(content, str):
            run.fail(f"cat: {operand}: structured content")
            continue
        chunks.append(content)
    _redirect_output(run, redirect, "".join(chunks))


def _base_name(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    return parts[-1] if parts else path


def _join_path(directory: str, name: str) -> str:
    return f"{directory}/{name}" if directory else name

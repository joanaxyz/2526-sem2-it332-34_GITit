from __future__ import annotations

OUTPUT_REFERENCE = {
    "git_version": "Git 2.44+ style",
    "locale": "English",
    "color": "disabled",
    "pager": "disabled",
    "line_endings": "LF-normalized",
}


def unsupported_command(command_name: str) -> str:
    return f"git: '{command_name}' is not a git command. See 'git --help'."


def not_a_repository() -> str:
    return "fatal: not a git repository (or any of the parent directories): .git"

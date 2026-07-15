from __future__ import annotations

from typing import Any

from curriculum.library_commands import normalize_command_text


def _syntax_explanation(command: str, canonical_command: str) -> str:
    note = _placeholder_note(command)
    return (
        f"Use `{command}` only when the authored scenario asks for this exact shape of command. "
        f"This syntax is different from `{canonical_command}` because options, destinations, paths, branch names, depth, or messages change what Git acts on. "
        f"{note}"
    )

def _syntax_how_to_read(command: str) -> list[str]:
    items = [
        "Read the command from left to right: base command first, then options, then the concrete value such as a path, directory, URL, branch, number, or message.",
        "Anything shown inside angle brackets is not typed literally; it is replaced with the value given by the scenario.",
    ]
    normalized = normalize_command_text(command)
    if "--quiet" in normalized or " -q" in f" {normalized}":
        items.append("Quiet commands can succeed with no visible output, so verification must come from status, metadata, or the target state rather than terminal chatter.")
    if "<directory>" in command:
        items.append("The directory argument matters because initializing or cloning the parent folder is a different answer from targeting the named child folder.")
    if "<branch>" in command:
        items.append("The branch option changes which branch name is created or checked out; it is not just decoration.")
    if "<path>" in command:
        items.append("The path limits the operation. A broad command can accidentally stage, restore, or inspect files that the scenario wanted left alone.")
    if "<number>" in command:
        items.append("The number limits history depth or output count, so use the exact amount requested.")
    if '"message"' in command:
        items.append("The message text must match the scenario's required commit message, not the sample word shown here.")
    return _clean_items(items)

def _syntax_when_to_use(command: str) -> list[str]:
    normalized = normalize_command_text(command)
    items = []
    if normalized.startswith("git init"):
        items.append("Use this during repository setup, before any first commit exists unless the task explicitly says you are safely reinitializing.")
    elif normalized.startswith("git clone"):
        items.append("Use this when the required starting point is a remote repository, not a local folder that already exists.")
    elif normalized.startswith("git add"):
        items.append("Use this after inspecting changes and before committing, when the chosen content belongs in the next snapshot.")
    elif normalized.startswith("git commit"):
        items.append("Use this only after the index contains exactly the snapshot that should be saved.")
    elif normalized.startswith("git restore --staged"):
        items.append("Use this when content is staged but should be kept as an unstaged working-tree change.")
    elif normalized.startswith("git restore"):
        items.append("Use this when the scenario says selected working-tree edits should be discarded.")
    elif normalized.startswith("git rm"):
        items.append("Use this when a tracked generated file should stop being tracked but remain on disk.")
    elif normalized == ".gitignore":
        items.append("Use this when the scenario asks you to ignore generated, local, or secret files before staging the ignore rule.")
    else:
        items.append("Use this as an inspection step when the scenario asks you to read repository evidence before acting.")
    items.append("Do not choose it just because it looks familiar; match it to the scenario's exact required values.")
    return _clean_items(items)

def _clean_items(items: list[str] | None) -> list[str]:
    return [str(item).strip() for item in (items or []) if str(item).strip()]

def _first_sentence(text: str) -> str:
    value = " ".join(str(text).strip().split())
    if not value:
        return ""
    for marker in (". ", "! ", "? "):
        if marker in value:
            return value.split(marker, 1)[0] + marker.strip()
    return value

def _placeholder_note(command: str) -> str:
    if "<path>" in command:
        return "Replace <path> with the exact file or folder named by the scenario. Do not use a placeholder literally."
    if "<directory>" in command:
        return "Replace <directory> with the exact destination folder requested by the scenario."
    if "<url>" in command:
        return "Replace <url> with the exact remote URL from the scenario."
    if "<branch>" in command:
        return "Replace <branch> with the exact branch name requested by the scenario."
    if "<number>" in command:
        return "Replace <number> with the numeric value requested by the scenario."
    if '"message"' in command:
        return "Replace the sample message with the exact commit message required by the scenario."
    return "Choose this syntax only when its option, path, or argument matches the scenario details."

def _verification_items(*, command: str, effects: list[str], boundaries: list[str], readiness: list[str]) -> list[str]:
    items = []
    if effects:
        items.append(f"Expected result: {effects[0]}")
    if readiness:
        items.append(f"Before running it: {readiness[0]}")
    if boundaries:
        items.append(f"Do not expect it to do this: {boundaries[0]}")
    if command.startswith("git status"):
        items.append("Verify the branch line and each path category: staged, unstaged, untracked, and ignored when requested.")
    elif command.startswith("git diff --staged") or command.startswith("git diff --cached"):
        items.append("Verify that the displayed patch is the version already staged for the next commit.")
    elif command.startswith("git diff"):
        items.append("Verify whether you are reading unstaged edits, staged edits, or all tracked edits since HEAD.")
    elif command.startswith("git log"):
        items.append("Verify commit order before choosing a commit id or judging whether history looks correct.")
    elif command.startswith("git add"):
        items.append("Run a status or staged diff afterward to confirm only the intended paths or hunks entered the index.")
    elif command.startswith("git commit"):
        items.append("Run a log or status check afterward to confirm the new or amended snapshot is the intended one.")
    elif command.startswith("git restore"):
        items.append("Run status afterward because restore affects either the working tree or index depending on the flags used.")
    elif command.startswith("git init"):
        items.append("Run status afterward to confirm the folder is now a repository without assuming a commit was created.")
    elif command.startswith("git clone"):
        items.append("Inspect status and remotes afterward to confirm the local copy is clean and connected to origin.")
    elif command == ".gitignore":
        items.append("Pair the ignore rule with status or check-ignore so you can prove the generated path is excluded.")
    return _clean_items(items)

def _state_language(*, command: str, effects: list[str], boundaries: list[str]) -> str:
    if command.startswith(("git status", "git log", "git diff", "git show", "git branch", "git remote", "git reflog", "git check-ignore", "git ls-files")):
        return "This is a reading command in Chapter 1. It gives evidence for the next decision, but the repository state should remain unchanged after the preview command runs."
    if command.startswith("git add"):
        return "This command changes the index, which is the staged snapshot prepared for the next commit. It does not create history by itself."
    if command.startswith("git commit"):
        return "This command changes local history by creating or replacing the commit at the current branch tip."
    if command.startswith("git restore --staged"):
        return "This command changes the index by moving selected content out of staging while keeping the working-tree edits available."
    if command.startswith("git restore"):
        return "This command changes working-tree files by replacing local edits with the chosen source version."
    if command.startswith("git rm --cached"):
        return "This command changes the index so Git stops tracking a path while leaving the local file present."
    if command.startswith("git init"):
        return "This command creates repository metadata. It prepares tracking capability, but it does not stage or commit project files."
    if command.startswith("git clone"):
        return "This command creates a local repository from a remote fixture and records the origin relationship."
    if command == ".gitignore":
        return "This content changes ignore behavior for untracked paths. It does not automatically remove files already tracked by Git."
    return _first_sentence(effects[0] if effects else "Use this command only when it matches the scenario state.")

def _section(
    *,
    section_id: str,
    section_type: str,
    title: str,
    content: list[dict[str, Any]],
    command: str = "",
    token: str = "",
) -> dict[str, Any]:
    section = {
        "id": section_id,
        "type": section_type,
        "title": title,
        "content": content,
    }
    if command:
        section["command"] = command
    if token:
        section["token"] = token
    return section


from __future__ import annotations

from curriculum.library_commands import normalize_command_text

_PROMPT = "student@git-it:~/quest$"

def example_command(command: str) -> str:
    raw = " ".join(str(command).strip().split())
    normalized = normalize_command_text(raw)

    replacements = {
        "<url>": "https://example.com/arcane-spire.git",
        "<folder>": "arcane-spire",
        "<directory>": "arcane-spire",
        "<file>": "README.md",
        "<path>": "debug.log" if "check-ignore" in normalized else "README.md",
        "<branch>": "feature/map",
        "<name>": "feature/map",
        "<start-point>": "8f3c2d1",
        "<commit>": "9c2e6b1",
        "<count>": "3",
        "<number>": "3",
        "<n>": "1",
        "<remote>": "origin",
        "<ref-a>": "main",
        "<ref-b>": "feature/map",
        "<tool>": "vimdiff",
        "<email>": "learner@example.test",
        "<value>": "auto",
    }

    if normalized.startswith("git config --global user.name"):
        return "git config --global user.name \"Learner\""
    if normalized.startswith("git config --global alias"):
        return "git config --global alias.st \"status --short\""
    if normalized.startswith("git config") and "<key>" in raw:
        return "git config --global init.defaultBranch main"
    if normalized.startswith("git init -b"):
        return "git init -b main"
    if normalized.startswith("git branch <name> <start-point>"):
        return "git branch feature/archive 8f3c2d1"
    if " -D" in f" {raw} ":
        return "git branch -D feature/spike"
    if normalized.startswith("git branch -d") or normalized.startswith("git branch --delete"):
        return "git branch -d feature/map"
    if normalized.startswith("git checkout --ours") or normalized.startswith("git checkout --theirs"):
        return raw.replace("<file>", "src/title.js").replace("<path>", "src/title.js")
    if normalized.startswith("git diff --ours") or normalized.startswith("git diff --theirs") or normalized.startswith("git diff --base"):
        return raw.replace("<file>", "src/title.js").replace("<path>", "src/title.js")
    if normalized.startswith("git rm -r --cached"):
        return "git rm -r --cached dist"
    if normalized.startswith("git rm"):
        return raw.replace("<file>", "debug.log").replace("<path>", "debug.log")
    if normalized.startswith("git stash drop"):
        return "git stash drop stash@{0}"
    if normalized.startswith("git push") and "--delete" in normalized:
        return "git push origin --delete feature/old-map"
    if normalized.startswith("git push --force-with-lease") or normalized.startswith("git push -f") or normalized.startswith("git push --force"):
        return "git push --force-with-lease origin feature/map"
    if normalized.startswith("git push -u") or normalized.startswith("git push --set-upstream"):
        return "git push -u origin feature/map"
    if normalized == "git push":
        return "git push"
    if normalized.startswith("git pull"):
        return raw
    if normalized.startswith("git clone -b"):
        return "git clone -b main https://example.com/arcane-spire.git"
    if normalized.startswith("git clone --depth"):
        return "git clone --depth 1 https://example.com/arcane-spire.git"
    if normalized == "git clone <url> <folder>":
        return "git clone https://example.com/arcane-spire.git arcane-spire"
    if normalized == "git clone <url>":
        return "git clone https://example.com/arcane-spire.git"
    if normalized.startswith("git commit"):
        result = raw.replace("<message>", '"document init"').replace('"message"', '"document init"')
        for token, value in replacements.items():
            result = result.replace(token, value)
        return result

    result = raw
    for token, value in replacements.items():
        result = result.replace(token, value)
    result = result.replace("<key>", "init.defaultBranch")
    return result


def prompt(command: str) -> str:
    return f"{_PROMPT} {command}"


def transcript(command: str, output: str) -> str:
    prompt_text = prompt(command)
    return f"{prompt_text}\n{output}" if output else prompt_text


def commit_output(command: str, commit_id: str, message: str, *, amended: bool = False) -> str:
    prefix = f"[main {commit_id}] {message}"
    details = [" 1 file changed, 1 insertion(+)"]
    if amended:
        details.insert(0, " Date: Thu Jul 9 12:00:00 2026 +0800")
    return transcript(command, "\n".join([prefix, *details]))


def conflict_diff(command: str, label: str, line: str) -> str:
    return transcript(
        command,
        "\n".join([
            "diff --git a/src/title.js b/src/title.js",
            "index e69de29..b6fc4c6 100644",
            f"--- a/src/title.js ({label})",
            "+++ b/src/title.js",
            "@@ -1 +1 @@",
            f"+{line}",
        ]),
    )


def stash_apply_output(*, dropped: bool) -> str:
    lines = [
        "On branch feature/map",
        "Changes not staged for commit:",
        "  (use \"git add <file>...\" to update what will be committed)",
        "  (use \"git restore <file>...\" to discard changes in working directory)",
        "\tmodified:   src/app.js",
        "",
        "no changes added to commit (use \"git add\" and/or \"git commit -a\")",
    ]
    if dropped:
        lines.append("Dropped refs/stash@{0} (8f3c2d1a4b5c6d7e8f90123456789abcdef0123)")
    return "\n".join(lines)


def sample_directory_for(command: str) -> str:
    if "research" in command:
        return "research-log"
    if "ui-kit" in command:
        return "ui-kit"
    return "demo-project"


def syntax_title(command: str) -> str:
    if any(token in command for token in ("<path>", "<directory>", "<url>", "<branch>", "<number>", '"message"')):
        return f"Syntax: {command}"
    return command

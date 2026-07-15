from __future__ import annotations

from .helpers import transcript


def render(raw: str, normalized: str, display_command: str, prompt_text: str) -> str | None:

    if normalized == ".gitignore":
        return transcript(
            "cat .gitignore",
            "\n".join([
                "# Dependencies",
                "node_modules/",
                "",
                "# Build output",
                "dist/",
                "",
                "# Local secrets and logs",
                ".env",
                "*.log",
            ]),
        )

    # Repository setup and inspection.
    if normalized.startswith("git init"):
        directory = "arcane-spire" if "<directory>" in raw else "quest"
        branch_note = "" if " -b " not in f" {normalized} " else ""
        return f"{prompt_text}\nInitialized empty Git repository in /home/student/{directory}/.git/{branch_note}"

    if normalized.startswith("git clone"):
        folder = "arcane-spire"
        return transcript(
            display_command,
            "\n".join([
                f"Cloning into '{folder}'...",
                "remote: Enumerating objects: 12, done.",
                "remote: Counting objects: 100% (12/12), done.",
                "remote: Compressing objects: 100% (8/8), done.",
                "remote: Total 12 (delta 2), reused 9 (delta 1), pack-reused 0",
                "Receiving objects: 100% (12/12), 4.21 KiB | 4.21 MiB/s, done.",
                "Resolving deltas: 100% (2/2), done.",
            ]),
        )

    if normalized.startswith("git status --porcelain"):
        return transcript(display_command, "M  README.md\nA  notes/git-basics.md\n?? scratch.txt")

    if normalized.startswith("git status --ignored"):
        return transcript(
            display_command,
            "\n".join([
                "On branch main",
                "Changes to be committed:",
                "  (use \"git restore --staged <file>...\" to unstage)",
                "\tmodified:   README.md",
                "",
                "Untracked files:",
                "  (use \"git add <file>...\" to include in what will be committed)",
                "\tscratch.txt",
                "",
                "Ignored files:",
                "  (use \"git add -f <file>...\" to include in what will be committed)",
                "\tnode_modules/",
                "\tdebug.log",
            ]),
        )

    if normalized.startswith("git status -s") or normalized.startswith("git status --short"):
        return transcript(display_command, "M  README.md\nA  notes/git-basics.md\n?? scratch.txt")

    if normalized.startswith("git status"):
        return transcript(
            display_command,
            "\n".join([
                "On branch main",
                "Changes to be committed:",
                "  (use \"git restore --staged <file>...\" to unstage)",
                "\tmodified:   README.md",
                "",
                "Changes not staged for commit:",
                "  (use \"git add <file>...\" to update what will be committed)",
                "  (use \"git restore <file>...\" to discard changes in working directory)",
                "\tmodified:   src/app.js",
                "",
                "Untracked files:",
                "  (use \"git add <file>...\" to include in what will be committed)",
                "\tscratch.txt",
            ]),
        )

    if normalized.startswith("git config --list"):
        return transcript(
            display_command,
            "\n".join([
                "user.name=Learner",
                "user.email=learner@example.test",
                "init.defaultbranch=main",
                "alias.st=status --short",
            ]),
        )

    if normalized.startswith("git config"):
        return transcript(display_command, "")

    return None

from __future__ import annotations

from .helpers import commit_output, transcript


def render(raw: str, normalized: str, display_command: str, prompt_text: str) -> str | None:
    if normalized.startswith("git add -p") or normalized.startswith("git add --patch"):
        return transcript(
            display_command,
            "\n".join([
                "diff --git a/README.md b/README.md",
                "index e69de29..b6fc4c6 100644",
                "--- a/README.md",
                "+++ b/README.md",
                "@@ -0,0 +1 @@",
                "+Arcane Spire unlocks the first story world.",
                "(1/1) Stage this hunk [y,n,q,a,d,e,?]? y",
            ]),
        )

    if normalized.startswith("git add"):
        return transcript(display_command, "")

    if normalized.startswith("git commit --amend --no-edit"):
        return commit_output(display_command, "9c2e6b1", "Add map encounter preview", amended=True)

    if normalized.startswith("git commit --amend"):
        return commit_output(display_command, "9c2e6b1", "Refine map encounter preview", amended=True)

    if normalized.startswith("git commit -a") or normalized.startswith("git commit"):
        return commit_output(display_command, "9c2e6b1", "document init")

    if normalized.startswith("git rm -r --cached"):
        return transcript(display_command, "rm 'dist/app.js'\nrm 'dist/app.css'")

    if normalized.startswith("git rm --cached") or normalized.startswith("git rm"):
        return transcript(display_command, "rm 'debug.log'")

    if normalized.startswith("git restore --staged"):
        return transcript(display_command, "")

    if normalized.startswith("git restore"):
        return transcript(display_command, "")

    if normalized.startswith("git check-ignore"):
        return transcript(display_command, ".gitignore:8:*.log\tdebug.log")

    return None

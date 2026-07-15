from __future__ import annotations

from .helpers import conflict_diff, transcript


def render(raw: str, normalized: str, display_command: str, prompt_text: str) -> str | None:
    if normalized.startswith("git log --oneline --graph --all"):
        return transcript(
            display_command,
            "\n".join([
                "* 9c2e6b1 (HEAD -> feature/map) Add map encounter preview",
                "| * 51f2a90 (origin/main, main) Document chapter unlocks",
                "|/",
                "* 8f3c2d1 Initial Arcane Spire story",
            ]),
        )

    if normalized.startswith("git log -p"):
        return transcript(
            display_command,
            "\n".join([
                "commit 9c2e6b1a7d4f8c2b3e0d1c9a6b5f4e3d2c1b0a9f8",
                "Author: Learner <learner@example.test>",
                "Date:   Thu Jul 9 12:00:00 2026 +0800",
                "",
                "    Add map encounter preview",
                "",
                "diff --git a/README.md b/README.md",
                "index e69de29..b6fc4c6 100644",
                "--- a/README.md",
                "+++ b/README.md",
                "@@ -0,0 +1 @@",
                "+Arcane Spire unlocks the first story world.",
            ]),
        )

    if normalized.startswith("git log --stat"):
        return transcript(
            display_command,
            "\n".join([
                "commit 9c2e6b1a7d4f8c2b3e0d1c9a6b5f4e3d2c1b0a9f8",
                "Author: Learner <learner@example.test>",
                "Date:   Thu Jul 9 12:00:00 2026 +0800",
                "",
                "    Add map encounter preview",
                "",
                " README.md | 1 +",
                " 1 file changed, 1 insertion(+)",
            ]),
        )

    if normalized.startswith("git log -n"):
        return transcript(display_command, "9c2e6b1 Add map encounter preview\n51f2a90 Document chapter unlocks\n8f3c2d Initial Arcane Spire story")

    if normalized.startswith("git log --oneline") or normalized.startswith("git log"):
        return transcript(display_command, "9c2e6b1 Add map encounter preview\n51f2a90 Document chapter unlocks\n8f3c2d Initial Arcane Spire story")

    if normalized.startswith("git show --name-only"):
        return transcript(
            display_command,
            "\n".join([
                "commit 9c2e6b1a7d4f8c2b3e0d1c9a6b5f4e3d2c1b0a9f8",
                "Author: Learner <learner@example.test>",
                "Date:   Thu Jul 9 12:00:00 2026 +0800",
                "",
                "    Add map encounter preview",
                "",
                "README.md",
                "src/story-map.ts",
            ]),
        )

    if normalized.startswith("git show"):
        return transcript(
            display_command,
            "\n".join([
                "commit 9c2e6b1a7d4f8c2b3e0d1c9a6b5f4e3d2c1b0a9f8",
                "Author: Learner <learner@example.test>",
                "Date:   Thu Jul 9 12:00:00 2026 +0800",
                "",
                "    Add map encounter preview",
                "",
                "diff --git a/README.md b/README.md",
                "index e69de29..b6fc4c6 100644",
                "--- a/README.md",
                "+++ b/README.md",
                "@@ -0,0 +1 @@",
                "+Arcane Spire unlocks the first story world.",
            ]),
        )

    if normalized.startswith("git diff --check"):
        return transcript(display_command, "src/auth.js:7: leftover conflict marker")

    if normalized.startswith("git diff --ours"):
        return conflict_diff(display_command, "ours", "return localTitle")

    if normalized.startswith("git diff --theirs"):
        return conflict_diff(display_command, "theirs", "return incomingTitle")

    if normalized.startswith("git diff --base"):
        return conflict_diff(display_command, "base", "return oldTitle")

    if normalized.startswith("git diff --name-only"):
        return transcript(display_command, "README.md\nsrc/app.js")

    if normalized.startswith("git diff --staged") or normalized.startswith("git diff --cached"):
        return transcript(
            display_command,
            "\n".join([
                "diff --git a/README.md b/README.md",
                "index e69de29..b6fc4c6 100644",
                "--- a/README.md",
                "+++ b/README.md",
                "@@ -0,0 +1 @@",
                "+Arcane Spire unlocks the first story world.",
            ]),
        )

    if normalized.startswith("git diff"):
        return transcript(
            display_command,
            "\n".join([
                "diff --git a/src/app.js b/src/app.js",
                "index 83db48f..f735c2d 100644",
                "--- a/src/app.js",
                "+++ b/src/app.js",
                "@@ -1,3 +1,4 @@",
                " export function start() {",
                "+  console.log('practice mode')",
                "   return true",
                " }",
            ]),
        )

    return None

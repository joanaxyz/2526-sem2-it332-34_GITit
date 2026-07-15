from __future__ import annotations

from .helpers import commit_output, transcript


def render(raw: str, normalized: str, display_command: str, prompt_text: str) -> str | None:
    if " -D" in f" {raw} ":
        return transcript(display_command, "Deleted branch feature/spike (was 51f2a90).")

    if normalized.startswith("git branch -d") or normalized.startswith("git branch --delete"):
        return transcript(display_command, "Deleted branch feature/map (was 9c2e6b1).")

    if normalized.startswith("git branch -v"):
        return transcript(display_command, "  feature/map 9c2e6b1 Add map encounter preview\n* main        51f2a90 Document chapter unlocks")

    if normalized.startswith("git branch -a"):
        return transcript(display_command, "* main\n  feature/map\n  remotes/origin/main\n  remotes/origin/feature/map")

    if normalized.startswith("git branch") and "<name" in normalized:
        return transcript(display_command, "")

    if normalized.startswith("git branch"):
        return transcript(display_command, "  feature/map\n* main")

    if normalized.startswith("git switch --detach"):
        return transcript(display_command, "HEAD is now at 8f3c2d1 Initial Arcane Spire story")

    if normalized.startswith("git switch -c") or normalized.startswith("git switch --create"):
        return transcript(display_command, "Switched to a new branch 'feature/map'")

    if normalized.startswith("git switch"):
        return transcript(display_command, "Switched to branch 'feature/map'")

    if normalized.startswith("git checkout -b"):
        return transcript(display_command, "Switched to a new branch 'feature/map'")

    if normalized.startswith("git merge-base"):
        return transcript(display_command, "8f3c2d1a4b5c6d7e8f90123456789abcdef0123")

    if normalized.startswith("git mergetool"):
        return transcript(
            display_command,
            "\n".join([
                "Merging:",
                "src/title.js",
                "",
                "Normal merge conflict for 'src/title.js':",
                "  {local}: modified file",
                "  {remote}: modified file",
            ]),
        )

    if normalized.startswith("git merge --abort"):
        return transcript(display_command, "")

    if normalized.startswith("git merge --continue"):
        return commit_output(display_command, "a1b2c3d", "Merge branch 'feature/map'")

    if normalized.startswith("git merge --squash"):
        return transcript(display_command, "Updating 51f2a90..9c2e6b1\nFast-forward\nSquash commit -- not updating HEAD\n README.md | 1 +\n 1 file changed, 1 insertion(+)")

    if normalized.startswith("git merge --no-ff"):
        return transcript(display_command, "Merge made by the 'ort' strategy.\n README.md | 1 +\n 1 file changed, 1 insertion(+)")

    if normalized.startswith("git merge"):
        return transcript(display_command, "Updating 51f2a90..9c2e6b1\nFast-forward\n README.md | 1 +\n 1 file changed, 1 insertion(+)")

    if normalized.startswith("git checkout --ours") or normalized.startswith("git checkout --theirs"):
        return transcript(display_command, "Updated 1 path from the index")

    if normalized.startswith("git ls-files -u") or normalized.startswith("git ls-files --unmerged"):
        return transcript(
            display_command,
            "\n".join([
                "100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 1\tsrc/title.js",
                "100644 8f3c2d1a4b5c6d7e8f90123456789abcdef0123 2\tsrc/title.js",
                "100644 9c2e6b1a7d4f8c2b3e0d1c9a6b5f4e3d2c1b0a9f8 3\tsrc/title.js",
            ]),
        )

    return None

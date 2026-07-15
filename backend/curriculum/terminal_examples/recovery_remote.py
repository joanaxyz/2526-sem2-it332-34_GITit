from __future__ import annotations

from .helpers import commit_output, stash_apply_output, transcript


def render(raw: str, normalized: str, display_command: str, prompt_text: str) -> str | None:
    if normalized == "git reset --hard head~1":
        return transcript(display_command, "HEAD is now at 8f3c2d1 Initial Arcane Spire story")

    if normalized.startswith("git reset --hard"):
        return transcript(display_command, "HEAD is now at 9c2e6b1 Add map encounter preview")

    if normalized.startswith("git revert --no-edit") or normalized.startswith("git revert"):
        return commit_output(display_command, "a1b2c3d", "Revert \"Add map encounter preview\"")

    if normalized.startswith("git reflog"):
        return transcript(
            display_command,
            "\n".join([
                "9c2e6b1 HEAD@{0}: commit: Add map encounter preview",
                "51f2a90 HEAD@{1}: commit: Document chapter unlocks",
                "8f3c2d1 HEAD@{2}: checkout: moving from feature/map to main",
            ]),
        )

    if normalized.startswith("git stash list"):
        return transcript(display_command, "stash@{0}: WIP on feature/map: 9c2e6b1 Add map encounter preview\nstash@{1}: WIP on main: 51f2a90 Document chapter unlocks")

    if normalized.startswith("git stash pop"):
        return transcript(display_command, stash_apply_output(dropped=True))

    if normalized.startswith("git stash apply"):
        return transcript(display_command, stash_apply_output(dropped=False))

    if normalized.startswith("git stash drop"):
        return transcript(display_command, "Dropped refs/stash@{0} (8f3c2d1a4b5c6d7e8f90123456789abcdef0123)")

    if normalized.startswith("git stash"):
        return transcript(display_command, "Saved working directory and index state WIP on feature/map: 9c2e6b1 Add map encounter preview")

    if normalized.startswith("git cherry-pick --abort"):
        return transcript(display_command, "")

    if normalized.startswith("git cherry-pick --no-commit"):
        return transcript(display_command, "")

    if normalized.startswith("git cherry-pick"):
        return commit_output(display_command, "a1b2c3d", "Add map encounter preview")

    if normalized.startswith("git remote -v"):
        return transcript(display_command, "origin\thttps://example.com/arcane-spire.git (fetch)\norigin\thttps://example.com/arcane-spire.git (push)")

    if normalized.startswith("git remote"):
        return transcript(display_command, "origin")

    if normalized.startswith("git fetch --prune"):
        return transcript(display_command, "From https://example.com/arcane-spire\n - [deleted]         (none)     -> origin/old-map\n   51f2a90..9c2e6b1  main       -> origin/main")

    if normalized.startswith("git fetch"):
        return transcript(display_command, "From https://example.com/arcane-spire\n   51f2a90..9c2e6b1  main       -> origin/main")

    if normalized.startswith("git pull --rebase"):
        return transcript(display_command, "Successfully rebased and updated refs/heads/main.")

    if normalized.startswith("git pull"):
        return transcript(display_command, "From https://example.com/arcane-spire\n * branch            main       -> FETCH_HEAD\nUpdating 51f2a90..9c2e6b1\nFast-forward\n README.md | 1 +\n 1 file changed, 1 insertion(+)")

    if normalized.startswith("git push") and "--delete" in normalized:
        return transcript(display_command, "To https://example.com/arcane-spire.git\n - [deleted]         feature/old-map")

    if normalized.startswith("git push --force-with-lease") or normalized.startswith("git push -f") or normalized.startswith("git push --force"):
        return transcript(display_command, "To https://example.com/arcane-spire.git\n + 51f2a90...9c2e6b1 feature/map -> feature/map (forced update)")

    if normalized.startswith("git push -u") or normalized.startswith("git push --set-upstream"):
        return transcript(display_command, "To https://example.com/arcane-spire.git\n * [new branch]      feature/map -> feature/map\nbranch 'feature/map' set up to track 'origin/feature/map'.")

    if normalized.startswith("git push"):
        return transcript(display_command, "To https://example.com/arcane-spire.git\n   51f2a90..9c2e6b1  main -> main")

    if normalized.startswith("git ls-files"):
        return transcript(display_command, "README.md\nsrc/app.js\nsrc/title.js")


    return None

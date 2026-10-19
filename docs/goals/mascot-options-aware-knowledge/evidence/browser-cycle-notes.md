# Browser acceptance notes

The app was opened at `/stories/arcane-spire` against a local API backed by a temporary copy of the development database. Progress changes were simulated completion records in that copy only. No primary or production database was changed.

After clearing levels 1 and 2, `GET /api/chapters/1/overview/` returned 200 with Stage and Commit (level 3) as the first unlocked, unpassed level. Reloading the map closed the previously open level 1 tip. Reopening the mascot began at Stage and Commit with `git status`, confirming the tip context reset.

Cycling showed these source groups in order:

1. Stage and Commit: five current-level tips after repeated command summaries are collapsed, including `git add <file>` with its `<path>` explanation and `git commit -m <message>` with the `-m / --message` explanation.
2. Read the Workspace: the cleared-level `git diff` tip.
3. Start a Repository: three cleared-level tips after its repeated `git init` summary is collapsed, including `git init -b <branch>` and the `-b / --initial-branch` explanation.
4. Git basics: the evergreen command anatomy tip. The next cycle returns to Stage and Commit.

The overview contains 14 other unpassed levels. None appeared in the browser tip cycle. The reward panel shows the 25%, 50%, 75%, and 100% milestones with no “Locked” labels. Current option, cleared option, context reset, and anatomy bubbles were captured on the story map; anatomy was checked at both desktop and 390px mobile width.

For the recency check, levels 1 and 2 remained passed but level 1 was assigned the later completion time despite appearing first in map order. The mascot showed Stage and Commit first, then Start a Repository, then Read the Workspace, matching timestamp recency rather than map position. For the all-cleared fallback, all 17 levels were marked passed and level 2 had the newest timestamp. Reloading the story map opened the mascot at Read the Workspace, and the API evidence reports all 17 passed plus that focus. Levels without an `AdventureLevelCompletion` row also expose their run `passed_at` timestamp for this ordering.

For the legacy fallback, level 1's `AdventureLevelCompletion` row was removed in the isolated database while a completed run retained `passed_at = 2026-10-19T00:00:00Z`, newer than the other levels. The overview reports `completion: null`, `passed_at` with that run timestamp, and `is_passed: true`. With all 17 levels passed, the map mascot opens on Start a Repository; see `progress-overview-passed-at-fallback.json` and `passed-at-fallback.png`.

The overview also confirms the command-scoped `git config` placeholder rule: in `git config --global user.name <name>`, `<name>` is explained by the `<value>` page, while the `<name>` in `alias.<name>` is explained by the `<key>` page. See `git-config-placeholder-mapping.json`.

The Stage and Commit option screenshot shows `git commit -m <message>` with its authored meaning and cue. The same isolated user received an empty `GET /api/skills/learned/` result, so this contextual guidance appears before any skill is earned; see `earned-skills-unearned-tip.json`.

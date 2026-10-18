# Arcane Spire Story-Record Cutover Evidence

## Applied database cutover

Command:

```text
backend/.venv/Scripts/python.exe manage.py migrate curriculum 0004 --noinput
```

Result: `Applying curriculum.0004_collapse_story_records_to_arcane_spire... OK`

Pre-cutover survivor:

```text
story id=11, slug=git-it-legacy, title=The Runebound Turret, world=arcane-spire
chapters=5, levels=21, tiers=63, runs=166, progress=158, completions=59
content/progress fingerprint=706e48d95d6b7b4bfa5460329a4d7c82bd9bca462d953f8dcb0236dddf9bae1b
```

Post-cutover database inventory:

```text
stories=[{id: 11, slug: arcane-spire, title: The Arcane Spire, world_slug: arcane-spire}]
chapters=5, levels=21, tiers=63, runs=166, progress=158, completions=59
content/progress fingerprint=706e48d95d6b7b4bfa5460329a4d7c82bd9bca462d953f8dcb0236dddf9bae1b
```

The exact chapter ids `[35, 36, 37, 38, 39]`, level ids `[255..275]`, and tier ids `[43..105]` remained unchanged. The old Arcane id 20, Frostbound id 21, Neon id 22, and their descendant trees were deleted. Those deleted rows are not reconstructible by reversing the migration; recovery requires an external database backup.

## Target-perspective API evidence

Authenticated requests against the migrated database returned:

```text
GET /api/stories/ -> 200
[{id: 11, slug: arcane-spire, title: The Arcane Spire,
  world_slug: arcane-spire, prerequisite_story: null, locked: false}]

GET /api/progress/stats/ -> 200
skill_profile count=18
git-init, git-clone, git-log, git-show, git-add, git-commit,
git-restore, git-branch, git-switch, git-merge, git-revert,
git-reflog, git-stash, git-cherry-pick, git-fetch, git-pull,
git-push, git-rebase
```

This proves the Progress tab contract is limited to the commands taught by the surviving curriculum.

## Seed and displaced-path evidence

- `seed_all` now calls only `seed_legacy_modules`, `seed_command_library`, and `seed_drills`.
- `seed_legacy_modules` creates exactly one `arcane-spire` story with 5 chapters, 21 levels, and 63 tiers, and is idempotent.
- The retired `seed_curriculum` fixture is absent from canonical/deployment seed paths, disabled in normal application settings, enabled only by the pytest harness, and still refuses to run over an active Arcane Spire Module 0-4 tree.
- Both Render startup scripts already call `seed_all`; the Docker entrypoint was corrected from the nonexistent `seed` command plus legacy command to `seed_all`.
- Frontend runtime sources contain no `git-it-legacy`, `The Runebound Turret`, or `runebound-turret-master` identifier.
- Retired authored curriculum fixtures and Frost/Neon visual packages remain explicitly demoted historical/test/asset-library material; they create no database story record and are not selected by production seeding.

## Supporting checks

```text
Backend focused cutover/API/progress/access tests: 36 passed
Backend full progress suite: 56 passed
Final canonical-seed and historical-fixture safeguards: 9 passed
Frontend focused route/Home/achievement tests: 38 passed
Ruff: All checks passed
Frontend production build: passed (3360 modules transformed)
Frontend ESLint: passed
Django system check: no issues
Migration check: no unapplied migrations
makemigrations --check --dry-run: no changes detected
git diff --check: passed (line-ending warnings only)
```

The standalone retired command was also invoked with normal application settings;
it exited before writing data with `CommandError: The retired three-story
curriculum seed is disabled outside the test suite.` Application source changes
are local workspace changes; no application deployment was performed.

## POST reviews

- **Plan alignment:** Aligned. The existing curriculum row was renamed in place; no child identity or progress row moved; canonical seeding and frontend/backend consumers use the new identity.
- **Correctness/data integrity:** No finding. The identical pre/post hash and direct API responses provide real-path evidence. Residual risk is limited to the intentionally irreversible deletion of retired rows.
- **Maintainability:** No blocking finding. The retired seed remains only as an explicitly labeled, test-setting-gated and collision-guarded fixture because broad simulator tests still use it; it has no canonical/deployment caller and cannot run under normal settings. Visual packs remain reusable assets, matching the instruction to keep Arcane visuals.
- **Verifier:** Passed. The migrated persisted state, story-list response, and 18-row skill profile match the target-perspective contract.

# Module 4 Blueprint — Advanced Recovery and History

**3 levels · 20 waves · about 49 min with no failures (today about 28) · Mapped to SO 4.1–SO 4.3 · 18 new scenarios**

## Module overview

Learners recover from history accidents: find lost work in the reflog, undo published commits safely with revert, and repair rebases that went wrong, then publish the result safely.

Chapter description in the seed: *Practice hard reset recovery, safe pushed commit reversal, and rebase recovery sequences.*

**Module KPIs:** SCR ≥ 80% (validity gate), CAR ≥ 70%, HLCR ≥ 70%, ARC ≤ 2, RTA ≥ 65%. Definitions: ARCHITECTURE.md, *Performance metrics*.

## Tiers, scaffolding and rewards

| Tier | Scaffolding | First-clear reward |
|---|---|---:|
| Easy | Live DAG + Expected State + contextual feedback | 25 GitCoins |
| Medium | Live DAG + Expected State | 35 GitCoins |
| Hard | Live DAG only | 50 GitCoins |

Command guides appear whenever a step needs a form the learner hasn't used yet, in any tier. A tier completes when its last wave is cleared; each wave needs one clear. A retry after a failure draws another variant of the same wave.

## Commands introduced in this module

| Command | Type | First wave (command guide) | Used again in |
|---|---|---|---|
| `git switch -c <branch> <commit>` | ⚡ ACTION | 4.1 Easy 1 · Recover the lost tip | 4 later waves |
| `git push` | ⚡ ACTION | 4.2 Easy 1 · Undo a pushed commit safely | 5 later waves |
| `git revert <commit>` | ⚡ ACTION | 4.2 Easy 1 · Undo a pushed commit safely | 5 later waves |
| `git rebase <upstream>` | ⚡ ACTION | 4.3 Easy 1 · Replay your branch onto main | 2 later waves |
| `git rebase --abort` | ⚡ ACTION | 4.3 Easy 2 · Abandon a stopped rebase | 1 later wave |
| `git rebase --continue` | ⚡ ACTION | 4.3 Easy 3 · Resolve and continue a rebase | 1 later wave |
| `git rebase --onto <newbase> <upstream> [<branch>]` | ⚡ ACTION | 4.3 Medium 1 · Move only your commits | 1 later wave |
| `git reset --hard <commit>` | ⚡ ACTION | 4.3 Medium 2 · Reset to the original tip, then rebase | 1 later wave |

## Commands carried in from earlier modules

Reused in this module's waves (every variant uses them), so earlier skills stay fresh.

| Command | Waves | Levels |
|---|---:|---|
| `git add <path>...` | 2 | 4.3 |
| `git commit --amend -m <message>` | 1 | 4.2 |
| `git switch <branch>` | 1 | 4.2 |
| `git branch <branch> [<start-point>]` | 1 | 4.1 |
| `git push -u <remote> <branch>` | 1 | 4.1 |
| `git push --force-with-lease <remote> <branch>` | 2 | 4.3 |
| `git pull <remote> <branch>` | 1 | 4.2 |
| `git cherry-pick <commit>` | 1 | 4.1 |

## Diagnostic commands (non-counted)

`git status`, `git log` and `git diff` are always free to run. This module's answer keys also rely on these diagnostics:

| Command | Type | Levels |
|---|---|---|
| `git log --oneline` | 🔍 DIAGNOSTIC — non-counted | 4.2 |
| `git log --oneline --graph --all` | 🔍 DIAGNOSTIC — non-counted | 4.3 |
| `git reflog` | 🔍 DIAGNOSTIC — non-counted | 4.1, 4.3 |
| `git show <commit>` | 🔍 DIAGNOSTIC — non-counted | 4.1, 4.2 |

---

## Level 4.1 — Recovering from Hard Resets

**Teaches:** `git reflog` + recovery branch · **Mapped to:** SO 4.1 (CAR ≥ 70%) · **Level slug:** `recovering-from-hard-resets`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 4 today → 6 · **Estimated time:** about 14 min (today about 10)

### Learning outcomes

- Find lost commits in the reflog and inspect the candidates.
- Recover lost work on a new branch at the right commit.
- Share recovered work and bring single fixes back to main.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git switch -c <branch> <commit>` | ⚡ ACTION | Easy 1 · Recover the lost tip |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Recover the lost tip | debut | `git switch -c <branch> <commit>` | Find the pre-reset tip in the reflog and recover it on a new branch. | 4.1.1 Recover an accidental reset<br>4.1.2 Recover after a script reset<br>4.1.3 Recover after resetting too far |
| Easy | 2. Recover after another reset | practice | — | Recover a lost tip after a different kind of reset. | 4.1.4 Recover after a merge reset<br>4.1.5 Recover a debugging reset |
| Medium | 1. Deeper in the reflog | practice | — | Recover a tip buried deeper in the reflog. | 4.1.6 Recover an accidental reset<br>4.1.7 Recover after a script reset<br>4.1.8 Recover after resetting too far<br>4.1.9 Recover after a merge reset<br>4.1.10 Recover a debugging reset |
| Medium | 2. Recover and share it | spiral | — | Recover lost work on a branch and publish it with upstream. | **new** `reflog-medium-recover-and-publish-search`<br>**new** `reflog-medium-recover-and-publish-billing` |
| Hard | 1. Pick the right candidate | transfer | — | Inspect several candidates and recover the right one. | 4.1.11 Recover an accidental reset<br>4.1.12 Recover after a script reset<br>4.1.13 Recover after resetting too far<br>4.1.14 Recover after a merge reset<br>4.1.15 Recover a debugging reset |
| Hard | 2. Recover, then bring the fix to main | spiral | — | Bookmark the lost commit, then bring only its fix to main. | **new** `reflog-hard-recover-then-pick-auth`<br>**new** `reflog-hard-recover-then-pick-export` |

---

## Level 4.2 — Reversing Pushed Commits Safely

**Teaches:** `git revert` · **Mapped to:** SO 4.2 (CAR ≥ 70%) · **Level slug:** `reversing-pushed-commits-safely`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 4 today → 6 · **Estimated time:** about 14 min (today about 9)

### Learning outcomes

- Undo published commits with new commits instead of rewriting history.
- Find the faulty commit from its symptom; revert several in the right order.
- Rewrite only unpublished work, then publish once.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git push` | ⚡ ACTION | Easy 1 · Undo a pushed commit safely |
| `git revert <commit>` | ⚡ ACTION | Easy 1 · Undo a pushed commit safely |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Undo a pushed commit safely | debut | `git push`, `git revert <commit>` | Undo a pushed commit with a new commit, then push. | 4.2.1 Revert c3 safely<br>4.2.2 Revert c2 safely<br>4.2.3 Revert c4 safely |
| Easy | 2. Sync first, then revert | spiral | — | Update from origin, revert, and publish. | **new** `revert-easy-pull-then-revert-docs`<br>**new** `revert-easy-pull-then-revert-api` |
| Medium | 1. Find the culprit from the symptom | practice | — | Find the faulty published commit from its symptom, revert it, push. | 4.2.4 Restore progressive tax withholding<br>4.2.5 Stop the every-minute push notifications<br>4.2.6 Restore relevance ranking in search |
| Medium | 2. Revert on the release branch | spiral | — | Revert on a release branch and publish it. | **new** `revert-medium-release-branch-pricing`<br>**new** `revert-medium-release-branch-auth` |
| Hard | 1. Two faulty commits, one publish | transfer | — | Revert two faulty commits newest first, keep the good one between them, push once. | 4.2.7 Roll back two faulty checkout changes<br>4.2.8 Roll back two faulty session changes<br>4.2.9 Roll back two faulty site changes |
| Hard | 2. Rewrite only what isn't published | spiral | — | Amend the unpublished commit, revert the published one, push once. | **new** `revert-hard-amend-local-revert-pushed-shop`<br>**new** `revert-hard-amend-local-revert-pushed-blog` |

---

## Level 4.3 — Completing Rebase Recovery Sequences

**Teaches:** `git rebase` recovery · **Mapped to:** SO 4.3 (CAR ≥ 70%) · **Level slug:** `completing-rebase-recovery-sequences`

**Waves (Easy/Medium/Hard):** 3/2/3 · **Runs:** 4 today → 8 · **Estimated time:** about 20 min (today about 9)

### Learning outcomes

- Replay a branch onto main and verify the graph.
- Continue or abort a stopped rebase; move only your commits with `--onto`.
- Restore a branch from the reflog after a bad rebase, then republish safely.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git rebase <upstream>` | ⚡ ACTION | Easy 1 · Replay your branch onto main |
| `git rebase --abort` | ⚡ ACTION | Easy 2 · Abandon a stopped rebase |
| `git rebase --continue` | ⚡ ACTION | Easy 3 · Resolve and continue a rebase |
| `git rebase --onto <newbase> <upstream> [<branch>]` | ⚡ ACTION | Medium 1 · Move only your commits |
| `git reset --hard <commit>` | ⚡ ACTION | Medium 2 · Reset to the original tip, then rebase |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Replay your branch onto main | debut | `git rebase <upstream>` | Replay a feature branch on top of main and check the graph. | 4.3.1 Rebase feature/recovery onto main<br>4.3.2 Rebase feature/search-filters onto main<br>4.3.3 Rebase feature/cli-flags onto main |
| Easy | 2. Abandon a stopped rebase | debut | `git rebase --abort` | Cancel a stopped rebase and restore the branch. | 4.3.6 Abandon a rebase that stopped on a conflict *(from Medium)*<br>**new** `rebase-easy-abort-stopped-docs` |
| Easy | 3. Resolve and continue a rebase | debut | `git rebase --continue` | Resolve a stopped rebase and finish it. | 4.3.9 Finish a rebase after fixing a conflict *(from Hard)*<br>**new** `rebase-easy-continue-config` |
| Medium | 1. Move only your commits | debut | `git rebase --onto <newbase> <upstream> [<branch>]` | Move only your commits off a wrong base and onto main. | 4.3.4 Move fix/footer-typo onto main<br>4.3.5 Move hotfix/login-timeout onto main |
| Medium | 2. Reset to the original tip, then rebase | debut | `git reset --hard <commit>` | Restore a branch from the reflog after a bad rebase, then rebase it. | 4.3.7 Recover the dropped commit on feature/cli-flags *(from Hard)*<br>4.3.8 Recover the dropped commit on hotfix/export-csv *(from Hard)* |
| Hard | 1. Continue the rebase, then publish safely | spiral | — | Finish a stopped rebase and republish the branch safely. | **new** `rebase-hard-continue-then-lease-search`<br>**new** `rebase-hard-continue-then-lease-billing` |
| Hard | 2. Abort, then move only your commits | transfer | — | Cancel a rebase onto the wrong base, then move only your commits. | **new** `rebase-hard-abort-then-onto-reports`<br>**new** `rebase-hard-abort-then-onto-ui` |
| Hard | 3. Undo a bad rebase and republish | spiral | — | Restore from the reflog, rebase, and republish safely. | **new** `rebase-hard-reset-rebase-lease-cli`<br>**new** `rebase-hard-reset-rebase-lease-api` |

---

## New scenarios in this module (18)

To be written in the team's scenario format (story, starting point, real-world context, task, checklist, answer key, accepted alternatives, expected result, evaluation, budgets). Names below are placeholders the author may change.

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `reflog-medium-recover-and-publish-search` | 4.1 Medium 2 · Recover and share it | On main after a reset dropped the search fix; origin is available. | Recover the lost tip on recovery/search-fix and publish it with upstream for review. | `git reflog` → `git switch -c recovery/search-fix c4` → `git push -u origin recovery/search-fix` | Spiral: `push -u` (2.4). |
| `reflog-medium-recover-and-publish-billing` | 4.1 Medium 2 · Recover and share it | On main after a reset dropped the billing work. | Recover it on recovery/billing and publish it with upstream. | `git reflog` → `git switch -c recovery/billing c5` → `git push -u origin recovery/billing` | Spiral. |
| `reflog-hard-recover-then-pick-auth` | 4.1 Hard 2 · Recover, then bring the fix to main | On main after a reset; the reflog shows an abandoned experiment and the auth fix on top of it. | Keep the lost tip on recovery/auth without leaving main, then bring only the auth fix to main as a new commit. | `git reflog` → `git show c4` → `git branch recovery/auth c4` → `git cherry-pick c4` | Spiral: `git branch <name> <commit>` (2.1), cherry-pick (3.3). |
| `reflog-hard-recover-then-pick-export` | 4.1 Hard 2 · Recover, then bring the fix to main | On main after a reset; the reflog shows a debug commit and the export fix on top of it. | Keep the lost tip on recovery/export without leaving main, then bring only the fix to main. | `git reflog` → `git show c5` → `git branch recovery/export c5` → `git cherry-pick c5` | Spiral: `git branch` (2.1), cherry-pick (3.3). |
| `revert-easy-pull-then-revert-docs` | 4.2 Easy 2 · Sync first, then revert | On main, one commit behind origin/main; c3 (already published) broke the docs build. | Get up to date, undo c3 with a new commit, and publish. | `git pull origin main` → `git revert c3` → `git push` | Spiral: pull (2.5). |
| `revert-easy-pull-then-revert-api` | 4.2 Easy 2 · Sync first, then revert | On main, behind origin/main; c4 (published) broke the API. | Get up to date, undo c4, publish. | `git pull origin main` → `git revert c4` → `git push` | Spiral: pull (2.5). |
| `revert-medium-release-branch-pricing` | 4.2 Medium 2 · Revert on the release branch | On main; release/2.1 tracks origin/release/2.1; c4 on it broke pricing. | Undo c4 on release/2.1 without rewriting history and publish it. | `git switch release/2.1` → `git revert c4` → `git push` | Spiral: switch (2.1). |
| `revert-medium-release-branch-auth` | 4.2 Medium 2 · Revert on the release branch | On main; release/1.8 tracks origin; c3 on it broke sign-in. | Undo c3 on release/1.8 and publish. | `git switch release/1.8` → `git revert c3` → `git push` | Spiral. |
| `revert-hard-amend-local-revert-pushed-shop` | 4.2 Hard 2 · Rewrite only what isn't published | On main; c0-c3 are published; c4 is local with the message 'wip'; published c2 broke checkout. | Fix c4's message (it is unpublished), undo c2 without rewriting published history, and publish once. | `git commit --amend -m "Add order export"` → `git revert c2` → `git push` | Spiral: `--amend` (1.5); teaches rewrite-only-unpublished. |
| `revert-hard-amend-local-revert-pushed-blog` | 4.2 Hard 2 · Rewrite only what isn't published | On main; c4 is local with a vague message; published c3 broke the RSS feed. | Fix c4's message, undo c3 safely, publish once. | `git commit --amend -m "Add RSS feed"` → `git revert c3` → `git push` | Spiral. |
| `rebase-easy-abort-stopped-docs` | 4.3 Easy 2 · Abandon a stopped rebase | Mid-rebase of feature/docs-search onto main, stopped on a conflict in docs/index.md. | Cancel the rebase so the branch is exactly as before. | `git rebase --abort` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-easy-continue-config` | 4.3 Easy 3 · Resolve and continue a rebase | Mid-rebase of feature/config-loader, stopped on a conflict in config/app.yml. | Resolve to the shown lines and finish the rebase. | *Project Files edit* → `git add config/app.yml` → `git rebase --continue` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-continue-then-lease-search` | 4.3 Hard 1 · Continue the rebase, then publish safely | feature/search was pushed earlier; now mid-rebase onto main, stopped on a conflict in src/search.py. | Resolve, finish the rebase, and update origin/feature/search without overwriting unseen work. | *Project Files edit* → `git add src/search.py` → `git rebase --continue` → `git push --force-with-lease origin feature/search` | Spiral: `--force-with-lease` (2.4). Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-continue-then-lease-billing` | 4.3 Hard 1 · Continue the rebase, then publish safely | feature/billing was pushed; now mid-rebase, stopped on a conflict in src/billing.py. | Resolve, finish, update origin safely. | *Project Files edit* → `git add src/billing.py` → `git rebase --continue` → `git push --force-with-lease origin feature/billing` | Spiral. Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-abort-then-onto-reports` | 4.3 Hard 2 · Abort, then move only your commits | Mid-rebase of feature/reports onto main, but the branch was started from spike/charts and drags its commits along. | Cancel the rebase, then move only feature/reports' own commits onto main. | `git rebase --abort` → `git rebase --onto main spike/charts feature/reports` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-abort-then-onto-ui` | 4.3 Hard 2 · Abort, then move only your commits | Mid-rebase of feature/table-ui, which was started from spike/new-grid. | Cancel, then move only its own commits onto main. | `git rebase --abort` → `git rebase --onto main spike/new-grid feature/table-ui` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-reset-rebase-lease-cli` | 4.3 Hard 3 · Undo a bad rebase and republish | feature/cli-flags was pushed; a bad rebase dropped a commit; the original tip is in the reflog. | Restore the complete branch, replay it on main, and update origin safely. | `git reflog` → `git reset --hard c6` → `git rebase main` → `git push --force-with-lease origin feature/cli-flags` | Spiral: `--force-with-lease` (2.4). |
| `rebase-hard-reset-rebase-lease-api` | 4.3 Hard 3 · Undo a bad rebase and republish | feature/rate-limits was pushed; a bad rebase dropped the limiter commit. | Restore it from the reflog, rebase onto main, update origin safely. | `git reflog` → `git reset --hard c5` → `git rebase main` → `git push --force-with-lease origin feature/rate-limits` | Spiral. |

# Wave Map — Arcane Spire Modules 1–4

Companion to [PLAN.md](PLAN.md). This is the placement contract: which scenario sits in which level, tier and wave, and in what order. The 21 levels and the command each one teaches are unchanged. [wave-map.json](wave-map.json) holds the same data in machine-readable form for execution. Neither file is read at runtime.

## How to read it

- **Wave**: one step in a tier, the same unit the level map's n/n counter counts today. The difference is that each wave now has its own purpose and its own variants, instead of every round drawing from one shared pool. A run plays the learner's next uncleared wave, and the tier completes when its last wave is cleared.
- **Variants**: interchangeable scenarios for that step. The first listed is the one a first-time learner gets. A retry after a failure rotates to another variant of the **same** wave.
- **Command guide introduces**: forms the guide shows for the first time in that wave, under the planned resolver fix and the 11 newly registered forms (PLAN.md, Task 1). `—` means everything in the wave is already known, so the learner works unguided.
- `↤M` / `↤H` marks an existing scenario moved down from Medium or Hard. **new** marks a scenario that still has to be written (specs at the end).

| Role | Meaning |
|---|---|
| debut | First use of a form or technique. Allowed at Easy, or at Medium for a level's advanced form. Never at Hard. Every variant uses the debuted form. |
| practice | The same forms in a different repository shape. Nothing new. |
| compose | Two or more of this level's forms in one scenario. |
| spiral | This level's command plus forms from earlier levels, as a realistic workflow (spaced review). |
| transfer | Hard: unfamiliar state, distractors or constraints, using known forms only. |

## Rules this map satisfies

Checked with the real tutoring resolver and technique detectors (`backend/tutoring/services/forms.py`, `techniques.py`) against the seeded fixtures:

1. Every one of the 265 bank scenarios is placed exactly once. Every wave has at least two variants.
2. No option, subcommand or technique debuts at Hard. Two Hard waves show a guide for a *composed* form whose parts are already known: plain `git init` (1.1) and `git clone --depth … -b …` (1.2).
3. Every form a wave debuts is used by every variant of that wave, so a retry never skips the guide's lesson.
4. Core workflow forms (add, commit, amend, restore, switch, branch, stash, push, fetch, pull, merge) recur in at least two later waves, including one later level. Specialized forms recur at a harder tier. Each exact guide form is reused at least once.
5. **Time budget:** a learner who never fails finishes all four modules in about 4.9 hours, close to today's 4.7. The team accepted this on 2026-10-20.

| | Today | This map |
|---|---:|---:|
| Waves per tier (the n/n counter) | 1–3 rounds drawn from one shared pool | 2–3 designed waves, each with its own variants |
| Runs on the default path (no failures) | 137 | 132 |
| Commands typed | 265 | 305 |
| Estimated time, no failures | ~4.7 h | ~4.9 h |
| Forms first met at Medium / Hard (default path) | 10 / 9 | 9 / 0 |
| Forms never reused after first use (excluding setup `init`/`clone`) | 5 | 0 |
| Scenarios | 265 | 349 (84 new) |

Roles: 45 debut, 24 practice, 8 compose, 26 spiral, 29 transfer.

Time estimate: 1 min per wave (brief and outcome), 0.4 min per typed command, 1 min per file edit, 0.5 min per first-time guide. Retries add time to both columns roughly alike.

## Module 1 — Local Repository Foundations

### 1.1 Initializing Repositories — teaches git init

`initializing-a-local-repository`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Track this folder | debut | `git init -b <branch> [<directory>]` | 1.1.1 `init-easy-current-empty`<br>1.1.2 `init-easy-trunk-branch` |
| Easy | 2. Start a new project folder | practice | — | 1.1.3 `init-easy-invoice`<br>1.1.4 `init-med-oss` ↤M |
| Medium | 1. Folder and branch from the brief | practice | — | 1.1.5 `init-medium-docs-site`<br>1.1.6 `init-medium-trunk-api-playground` |
| Medium | 2. Existing files stay untracked | practice | — | 1.1.7 `init-medium-existing-files`<br>1.1.8 `init-hard-ci` ↤H |
| Hard | 1. Only the right subfolder | transfer | — | 1.1.9 `init-hard-research-log`<br>1.1.10 `init-hard-ui-kit` |
| Hard | 2. A nested project folder | transfer | — | **new** `init-hard-nested-service`<br>**new** `init-hard-nested-course` |

### 1.2 Cloning Remote Repositories — teaches git clone

`cloning-a-remote-repository`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Clone a repository | debut | `git clone <url>` | 1.2.1 `clone-easy-docs-portal`<br>1.2.4 `clone-easy-oss-ssh` |
| Easy | 2. Clone into a named folder | debut | `git clone <url> <folder>` | 1.2.2 `clone-easy-api-lab`<br>1.2.5 `clone-easy-corp` |
| Easy | 3. Clone a specific branch | debut | `git clone -b <branch> <url> [<folder>]` | 1.2.3 `clone-easy-profile-starter`<br>1.2.6 `clone-med-feature` ↤M<br>1.2.8 `clone-medium-cli-starter-folder` ↤M |
| Medium | 1. SSH address, named folder | practice | — | 1.2.7 `clone-medium-analytics-ssh`<br>1.2.13 `clone-hard-research-log-ssh` ↤H |
| Medium | 2. Shallow history | debut | `git clone --depth <n> <url> [<folder>]` | 1.2.9 `clone-medium-css-kit-shallow`<br>**new** `clone-medium-shallow-metrics` |
| Hard | 1. Shallow copy of one branch | transfer | `git clone --depth <n> -b <branch> <url> [<folder>]` | 1.2.11 `clone-hard-mobile-ui-shallow-branch`<br>1.2.12 `clone-hard-lab-notebook-depth-branch` |
| Hard | 2. Shallow review copy over SSH | transfer | — | 1.2.10 `clone-hard-ssh-shallow`<br>**new** `clone-hard-shallow-ssh-audit` |

### 1.3 Staging and Committing — teaches git add + git commit

`staging-and-committing-basic-workflow`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Stage and commit one change | debut | `git add <path>...`, `git commit -m <message>` | 1.3.3 `commit-easy-form-validation`<br>1.3.4 `commit-easy-readme-setup`<br>1.3.5 `commit-easy-navbar-spacing`<br>1.3.2 `commit-easy-auth-dir` |
| Easy | 2. Stage several files at once | debut | technique: several-paths | 1.3.1 `commit-easy-initial`<br>1.3.6 `commit-med-docker` ↤M |
| Medium | 1. A two-file change | practice | — | 1.3.7 `commit-medium-profile-card`<br>1.3.8 `commit-medium-search-results`<br>1.3.9 `commit-medium-export-flow` |
| Medium | 2. First snapshot of a new project | spiral | — | **new** `commit-medium-new-project-portfolio`<br>**new** `commit-medium-new-project-recipes` |
| Hard | 1. Leave the distractor out | transfer | — | 1.3.10 `commit-hard-selective`<br>1.3.12 `commit-hard-profile-distractor`<br>1.3.13 `commit-hard-export-distractor` |
| Hard | 2. Two targets, two distractors | transfer | — | 1.3.11 `commit-hard-parser`<br>1.3.14 `commit-hard-search-two-targets-one-distractor` |

### 1.4 Partial Staging — teaches git add -p

`partial-staging-and-git-add-p`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Stage one hunk | debut | `git add -p <path>` | 1.4.1 `partial-easy-billing`<br>1.4.3 `partial-easy-auth-validation`<br>1.4.5 `partial-easy-export-format` |
| Easy | 2. Another file, another hunk | practice | — | 1.4.2 `partial-easy-routes`<br>1.4.4 `partial-easy-search-ranking` |
| Medium | 1. One hunk out of many | practice | — | 1.4.6 `partial-med-three-hunk`<br>1.4.7 `partial-medium-profile-validation`<br>1.4.8 `partial-medium-payment-rounding`<br>1.4.9 `partial-medium-dashboard-filter` |
| Medium | 2. A hunk and a whole file | spiral | — | **new** `partial-medium-hunk-plus-test`<br>**new** `partial-medium-hunk-plus-doc` |
| Hard | 1. Hunks across code and tests | transfer | — | 1.4.10 `partial-hard-terraform`<br>1.4.11 `partial-hard-auth-cross-file`<br>1.4.12 `partial-hard-search-cross-file`<br>1.4.13 `partial-hard-export-cross-file` |
| Hard | 2. Split one file into two commits | compose | — | **new** `partial-hard-split-two-commits-api`<br>**new** `partial-hard-split-two-commits-ui` |

### 1.5 Amending Commits — teaches git commit --amend

`amending-commits`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Fix the last commit message | debut | `git commit --amend -m <message>` | 1.5.1 `amend-easy-typo`<br>1.5.3 `amend-easy-login-copy-message`<br>1.5.4 `amend-easy-readme-message`<br>1.5.5 `amend-easy-navbar-message`<br>1.5.10 `amend-hard-convention` ↤H |
| Easy | 2. Add the forgotten file | practice | — | 1.5.2 `amend-easy-forgot`<br>1.5.7 `amend-medium-profile-missing-css` ↤M |
| Medium | 1. Amend content and message | practice | — | 1.5.6 `amend-med-both`<br>1.5.8 `amend-medium-export-doc`<br>1.5.9 `amend-medium-search-template` |
| Medium | 2. Amend in one hunk | spiral | — | **new** `amend-medium-hunk-into-last-checkout`<br>**new** `amend-medium-hunk-into-last-search` |
| Hard | 1. Missing file and wrong message | transfer | — | 1.5.11 `amend-hard-profile-message-and-layout`<br>1.5.12 `amend-hard-auth-message-and-test`<br>1.5.13 `amend-hard-export-message-and-doc` |
| Hard | 2. Fix the last message, then commit the rest | compose | — | **new** `amend-hard-fix-message-then-commit-api`<br>**new** `amend-hard-fix-message-then-commit-docs` |

### 1.6 Unstaging and Discarding Changes — teaches git restore

`unstaging-and-discarding-changes`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Unstage but keep the edit | debut | `git restore --staged <path>...` | 1.6.1 `restore-easy-unstage`<br>1.6.3 `restore-easy-unstage-app`<br>1.6.4 `restore-easy-unstage-guide`<br>1.6.5 `restore-easy-unstage-css` |
| Easy | 2. Throw away a working change | debut | `git restore <path>...` | 1.6.2 `restore-easy-discard`<br>**new** `restore-easy-discard-theme` |
| Medium | 1. Unstage one, discard another | compose | — | 1.6.6 `restore-med-unstage-discard`<br>1.6.7 `restore-medium-app-debug`<br>1.6.8 `restore-medium-docs-scratch`<br>1.6.9 `restore-medium-css-build` |
| Medium | 2. Fix the staging, then commit | spiral | — | **new** `restore-medium-unstage-then-commit-login`<br>**new** `restore-medium-unstage-then-commit-cart` |
| Hard | 1. Several to unstage, one to discard | transfer | — | 1.6.10 `restore-hard-cleanup`<br>1.6.11 `restore-hard-mixed-profile`<br>1.6.12 `restore-hard-mixed-export`<br>1.6.13 `restore-hard-mixed-search` |
| Hard | 2. Clean up, then commit only the fix | spiral | — | **new** `restore-hard-capstone-report`<br>**new** `restore-hard-capstone-invoice` |


## Module 2 — Branching and Collaboration

### 2.1 Creating and Switching Branches — teaches git switch / git branch

`creating-and-switching-branches`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Create a branch and switch to it | debut | `git switch -c <branch> [<start-point>]` | 2.1.1 `v21e-auth`<br>2.1.2 `v21e-login`<br>2.1.3 `v21e-ui`<br>2.1.4 `bc-easy-capstone-db`<br>2.1.5 `bc-easy-corp-hotfix` |
| Easy | 2. Go back to main | debut | `git switch <branch>` | **new** `switch-easy-back-to-main-docs`<br>**new** `switch-easy-back-to-main-api` |
| Medium | 1. Create a branch without switching | debut | `git branch <branch> [<start-point>]` | 2.1.6 `v21m-payments`<br>2.1.7 `v21m-notifications`<br>2.1.8 `v21m-export` |
| Medium | 2. Start from another branch's tip | practice | — | 2.1.9 `bc-med-oss-develop`<br>2.1.12 `v21h-from-develop` ↤H |
| Hard | 1. Start from an older commit | transfer | — | 2.1.10 `v21h-hotfix-c1`<br>2.1.11 `v21h-detach-save` |
| Hard | 2. Save detached work, then go back | transfer | — | 2.1.13 `bc-hard-review-snap`<br>**new** `switch-hard-detached-save-and-return` |

### 2.2 Branch Naming Conventions — teaches branch naming + git branch -d

`branch-naming-and-housekeeping`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Follow the naming convention | practice | — | 2.2.1 `bn-easy-corp-jira`<br>2.2.2 `bn-easy-startup-feat`<br>2.2.3 `bn-easy-oss-user`<br>2.2.4 `bn-easy-cap-initials`<br>2.2.5 `bn-easy-free-client` |
| Easy | 2. Delete a merged branch | debut | `git branch -d <branch>` | **new** `bn-easy-delete-merged-typo`<br>**new** `bn-easy-delete-merged-spike` |
| Medium | 1. Build the name from the brief | practice | — | 2.2.6 `bn-med-corp-notif`<br>2.2.7 `bn-med-startup-bugfix`<br>2.2.8 `bn-med-devops-scope`<br>2.2.9 `bn-med-oss-infer` |
| Medium | 2. Replace a badly named branch | compose | — | 2.2.10 `bn-hard-oss-rename` ↤H<br>2.2.11 `bn-hard-corp-rename` ↤H |
| Hard | 1. Fix the name, keep the convention | transfer | — | 2.2.12 `bn-hard-startup-prefix`<br>2.2.13 `bn-hard-qa-camel` |
| Hard | 2. Start the fix on a well-named branch | spiral | — | **new** `bn-hard-named-branch-commit-parser`<br>**new** `bn-hard-named-branch-commit-billing` |

### 2.3 Stashing Work in Progress — teaches git stash

`stashing-work-in-progress`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Shelve work and switch | debut | `git stash` | 2.3.1 `v23e-auth`<br>2.3.2 `v23e-notify`<br>2.3.3 `v23e-cache`<br>2.3.4 `stash-easy-cap-review`<br>2.3.5 `stash-easy-docs-switch` |
| Easy | 2. Bring the shelved work back | debut | `git stash pop` | **new** `stash-easy-pop-search`<br>**new** `stash-easy-pop-profile` |
| Medium | 1. Stash, visit, return, restore | compose | — | 2.3.6 `v23m-to-main`<br>2.3.7 `v23m-to-hotfix`<br>2.3.8 `v23m-to-release`<br>2.3.9 `stash-med-corp-named` |
| Medium | 2. Discard a cancelled draft | debut | `git stash drop [stash@{n}]` | 2.3.10 `v23h-dropped-auth` ↤H<br>2.3.11 `v23h-dropped-api` ↤H |
| Hard | 1. Two stashes, keep the right one | transfer | — | 2.3.13 `stash-hard-oss-multi`<br>**new** `stash-hard-two-stashes-reports` |
| Hard | 2. Cancelled work, clean exit | transfer | — | 2.3.12 `v23h-dropped-refactor`<br>**new** `stash-hard-cancelled-experiment` |

### 2.4 Pushing to a Remote — teaches git push

`pushing-to-a-remote`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Publish a branch | debut | `git push <remote> <branch>` | 2.4.1 `v24e-auth`<br>2.4.2 `v24e-orders`<br>2.4.3 `v24e-parser`<br>2.4.4 `push-easy-cap-auth`<br>2.4.5 `push-easy-free-landing` |
| Easy | 2. Publish and track | debut | `git push -u <remote> <branch>` | 2.4.6 `v24m-auth` ↤M<br>2.4.7 `v24m-orders` ↤M<br>2.4.8 `v24m-parser` ↤M<br>2.4.9 `push-med-docs-track` ↤M |
| Medium | 1. Branch, commit, publish | spiral | — | **new** `push-medium-branch-commit-publish-search`<br>**new** `push-medium-branch-commit-publish-invoices` |
| Medium | 2. Republish rewritten history safely | debut | `git push --force-with-lease <remote> <branch>` | 2.4.10 `v24h-auth` ↤H<br>2.4.11 `v24h-orders` ↤H |
| Hard | 1. Amend a published commit, republish | spiral | — | **new** `push-hard-amend-then-lease-api`<br>**new** `push-hard-amend-then-lease-docs` |
| Hard | 2. Rewritten branch, careful publish | transfer | — | 2.4.12 `v24h-parser`<br>2.4.13 `push-hard-devops-fwl` |

### 2.5 Fetching and Pulling from a Remote — teaches git fetch / git pull

`fetching-and-pulling`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. See what's new on origin | debut | `git fetch origin` | 2.5.1 `v25e-main`<br>2.5.2 `v25e-feature`<br>2.5.3 `v25e-develop`<br>2.5.4 `fetch-easy-cap-check`<br>2.5.5 `fetch-easy-corp-list` |
| Easy | 2. Bring the new commits in | debut | `git pull <remote> <branch>` | 2.5.6 `v25m-main` ↤M<br>2.5.7 `v25m-feature` ↤M<br>2.5.8 `v25m-develop` ↤M<br>2.5.9 `pull-med-free-client` ↤M |
| Medium | 1. Review before integrating | compose | — | 2.5.10 `v25h-main` ↤H<br>2.5.11 `v25h-feature` ↤H |
| Medium | 2. Update, then branch from fresh main | spiral | — | **new** `pull-medium-update-then-branch-ui`<br>**new** `pull-medium-update-then-branch-api` |
| Hard | 1. Review incoming work | transfer | — | 2.5.12 `v25h-develop`<br>2.5.13 `fetch-hard-oss-review` |
| Hard | 2. Pull with local work in progress | spiral | — | **new** `pull-hard-stash-pull-pop-docs`<br>**new** `pull-hard-stash-pull-pop-app` |

### 2.6 Reconciling Diverged Local and Remote Histories — teaches pull/fetch + merge + push

`reconciling-diverged-histories`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Pull, then push again | practice | — | 2.6.1 `v26e-auth`<br>2.6.2 `v26e-payments`<br>2.6.3 `v26e-hotfix`<br>2.6.4 `rec-easy-cap-ui`<br>2.6.5 `rec-easy-docs-chapter` |
| Easy | 2. Fetch, merge the remote branch, push | debut | `git merge <branch>`, technique: remote-branch | 2.6.6 `v26m-auth` ↤M<br>2.6.7 `v26m-payments` ↤M |
| Medium | 1. Reconcile a teammate's branch | practice | — | 2.6.8 `v26m-hotfix`<br>2.6.9 `rec-med-qa-testrunner` |
| Medium | 2. Commit, reconcile, publish | spiral | — | **new** `rec-medium-commit-then-reconcile-docs`<br>**new** `rec-medium-commit-then-reconcile-api` |
| Hard | 1. Reconcile from the wrong branch | transfer | — | 2.6.10 `v26h-auth`<br>2.6.11 `v26h-payments` |
| Hard | 2. Reconcile and publish under pressure | transfer | — | 2.6.12 `v26h-hotfix`<br>2.6.13 `rec-hard-corp-audit` |

### 2.7 Completing Branch Merges — teaches git merge

`completing-branch-merges`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Fast-forward merge | practice | — | 2.7.1 `v27e-auth`<br>2.7.2 `v27e-payments`<br>2.7.3 `v27e-hotfix`<br>2.7.4 `merge-easy-cap-docs`<br>2.7.5 `merge-easy-free-contact` |
| Easy | 2. Keep a visible merge commit | debut | `git merge --no-ff <branch>` | 2.7.6 `v27m-auth` ↤M<br>2.7.7 `v27m-payments` ↤M |
| Medium | 1. Merge with a merge commit | practice | — | 2.7.8 `v27m-hotfix`<br>2.7.9 `merge-med-corp-sso` |
| Medium | 2. Finish the feature, then land it | spiral | — | **new** `merge-medium-commit-switch-noff-reports`<br>**new** `merge-medium-commit-switch-noff-auth` |
| Hard | 1. Land from the wrong branch | transfer | — | 2.7.10 `v27h-auth`<br>2.7.11 `v27h-payments`<br>2.7.12 `v27h-hotfix`<br>2.7.13 `merge-hard-devops-cert` |
| Hard | 2. Land, publish, tidy up | spiral | — | **new** `merge-hard-land-publish-tidy-search`<br>**new** `merge-hard-land-publish-tidy-billing` |

### 2.8 Squash Merging — teaches git merge --squash

`squash-merging`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Squash a branch into one commit | debut | `git merge --squash <branch>` | 2.8.1 `v28e-auth`<br>2.8.2 `v28e-orders`<br>2.8.3 `v28e-parser`<br>2.8.4 `squash-easy-cap-report`<br>2.8.5 `squash-easy-free-payment` |
| Easy | 2. Squash, then force-delete the branch | debut | `git branch -D <branch>` | 2.8.10 `v28h-auth` ↤H<br>2.8.11 `v28h-orders` ↤H |
| Medium | 1. Squash a teammate's remote branch | practice | — | 2.8.6 `v28m-auth`<br>2.8.7 `v28m-orders`<br>2.8.8 `v28m-parser`<br>2.8.9 `squash-med-corp-gdpr` |
| Medium | 2. Squash and publish | spiral | — | **new** `squash-medium-squash-publish-onboarding`<br>**new** `squash-medium-squash-publish-export` |
| Hard | 1. One commit, no leftovers | transfer | — | 2.8.12 `v28h-parser`<br>2.8.13 `squash-hard-devops-log` |
| Hard | 2. Squash-land from another branch | spiral | — | **new** `squash-hard-switch-squash-cleanup-cli`<br>**new** `squash-hard-switch-squash-cleanup-ui` |

### 2.9 Deleting and Recovering Remote Branches — teaches git push --delete / git fetch --prune

`deleting-and-recovering-remote-branches`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Delete a remote branch | debut | `git push <remote> --delete <branch>` | 2.9.1 `v29e-auth`<br>2.9.2 `v29e-orders`<br>2.9.3 `v29e-parser`<br>2.9.4 `rb-easy-cap-group`<br>2.9.5 `rb-easy-corp-sprint` |
| Easy | 2. Prune stale remote-tracking refs | debut | `git fetch --prune origin` | 2.9.6 `v29m-auth` ↤M<br>2.9.7 `v29m-orders` ↤M<br>2.9.8 `v29m-parser` ↤M<br>2.9.9 `rb-med-free-prune` ↤M |
| Medium | 1. Retire a branch everywhere | compose | — | 2.9.10 `v29h-auth` ↤H<br>2.9.11 `v29h-orders` ↤H |
| Medium | 2. Land and retire | spiral | — | **new** `rb-medium-land-and-retire-search`<br>**new** `rb-medium-land-and-retire-billing` |
| Hard | 1. Retire safely | transfer | — | 2.9.12 `v29h-parser`<br>2.9.13 `rb-hard-oss-full` |
| Hard | 2. Fetch, land, publish, retire, prune | spiral | — | **new** `rb-hard-capstone-release-notes`<br>**new** `rb-hard-capstone-payments` |


## Module 3 — Conflict Resolution

### 3.1 Resolving Merge Conflicts Manually — teaches merge conflicts by hand

`resolving-conflicts-manually`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Resolve one conflicted file | debut | `git commit --no-edit` | 3.1.1 `manual-easy-auth-copy`<br>3.1.2 `manual-easy-profile-copy`<br>3.1.3 `manual-easy-billing-copy` |
| Easy | 2. Resolve another file | practice | — | 3.1.4 `manual-easy-config-copy`<br>3.1.5 `manual-easy-navbar-copy` |
| Easy | 3. Back out of a merge | debut | `git merge --abort` | **new** `manual-easy-abort-wrong-branch`<br>**new** `manual-easy-abort-too-early` |
| Medium | 1. Resolve config conflicts | practice | — | 3.1.6 `manual-medium-router`<br>3.1.7 `manual-medium-policy`<br>3.1.8 `manual-medium-gateway` |
| Medium | 2. A pull that conflicts | spiral | — | **new** `manual-medium-pull-conflict-readme`<br>**new** `manual-medium-pull-conflict-config` |
| Hard | 1. Resolve with less guidance | transfer | — | 3.1.9 `manual-hard-pricing`<br>3.1.10 `manual-hard-schema`<br>3.1.11 `manual-hard-migration` |
| Hard | 2. Abort the wrong merge, resolve the right one | transfer | — | 3.1.12 `manual-hard-abort-redo`<br>**new** `manual-hard-abort-redo-payments` |

### 3.2 Resolving Conflicts Using a Merge Tool — teaches git mergetool

`using-a-merge-tool`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Resolve in the merge tool | debut | `git mergetool` | 3.2.1 `mergetool-easy-cache-ttl`<br>3.2.2 `mergetool-easy-mail-footer`<br>3.2.3 `mergetool-easy-upload-limit` |
| Easy | 2. Another conflict, same tool | practice | — | 3.2.4 `mergetool-easy-app-locale`<br>3.2.5 `mergetool-easy-labels` |
| Medium | 1. Two files in one pass | practice | — | 3.2.6 `mergetool-medium-checkout-copy`<br>3.2.7 `mergetool-medium-api-limits`<br>3.2.8 `mergetool-medium-db-names`<br>3.2.9 `mergetool-medium-docs-sync` |
| Medium | 2. Set up the team's tool first | debut | `git config <key> <value>` | 3.2.10 `mergetool-hard-choose-tool` ↤H<br>**new** `mergetool-medium-configure-tool-billing` |
| Hard | 1. Judge which side to keep | transfer | — | 3.2.11 `mergetool-hard-one-of-two`<br>3.2.12 `mergetool-hard-take-theirs` |
| Hard | 2. No leftovers | transfer | — | 3.2.13 `mergetool-hard-no-leftovers`<br>**new** `mergetool-hard-no-backup-api` |

### 3.3 Cherry-Picking Commits — teaches git cherry-pick

`cherry-picking-commits`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Copy one commit | debut | `git cherry-pick <commit>` | 3.3.1 `cherry-easy-login-timeout`<br>3.3.2 `cherry-easy-invoice-rounding`<br>3.3.3 `cherry-easy-export-null`<br>3.3.4 `cherry-easy-rate-limit`<br>3.3.5 `cherry-easy-null-check`<br>3.3.6 `cherry-medium-login-timeout` ↤M<br>3.3.7 `cherry-medium-invoice-rounding` ↤M |
| Easy | 2. Record where it came from | debut | `git cherry-pick -x <commit>` | 3.3.12 `cherry-hard-trace-source` ↤H<br>**new** `cherry-easy-trace-source-hotfix` |
| Easy | 3. Pick without committing | debut | `git cherry-pick --no-commit <commit>` | 3.3.8 `cherry-medium-no-commit` ↤M<br>3.3.9 `cherry-medium-staged-review` ↤M |
| Medium | 1. Resolve and continue | debut | `git cherry-pick --continue` | 3.3.10 `cherry-hard-export-conflict` ↤H<br>**new** `cherry-medium-conflict-continue-auth` |
| Medium | 2. Cancel a stopped pick | debut | `git cherry-pick --abort` | 3.3.11 `cherry-hard-abort-conflict` ↤H<br>**new** `cherry-medium-abort-stopped-pick` |
| Medium | 3. Two fixes, one reviewed commit | compose | — | **new** `cherry-medium-two-fixes-one-commit-login`<br>**new** `cherry-medium-two-fixes-one-commit-tax` |
| Hard | 1. Backport to two releases | transfer | — | 3.3.13 `cherry-hard-two-releases`<br>**new** `cherry-hard-two-releases-security` |
| Hard | 2. Abort the wrong pick, backport the right one | spiral | — | **new** `cherry-hard-backport-capstone-export`<br>**new** `cherry-hard-backport-capstone-login` |


## Module 4 — Advanced Recovery and History

### 4.1 Recovering from Hard Resets — teaches git reflog + recovery branch

`recovering-from-hard-resets`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Recover the lost tip | debut | `git switch -c <branch> <commit>` | 4.1.1 `e1`<br>4.1.2 `e2`<br>4.1.3 `e3` |
| Easy | 2. Recover after another reset | practice | — | 4.1.4 `e4`<br>4.1.5 `e5` |
| Medium | 1. Deeper in the reflog | practice | — | 4.1.6 `m1`<br>4.1.7 `m2`<br>4.1.8 `m3`<br>4.1.9 `m4`<br>4.1.10 `m5` |
| Medium | 2. Recover and share it | spiral | — | **new** `reflog-medium-recover-and-publish-search`<br>**new** `reflog-medium-recover-and-publish-billing` |
| Hard | 1. Pick the right candidate | transfer | — | 4.1.11 `h1`<br>4.1.12 `h2`<br>4.1.13 `h3`<br>4.1.14 `h4`<br>4.1.15 `h5` |
| Hard | 2. Recover, then bring the fix to main | spiral | — | **new** `reflog-hard-recover-then-pick-auth`<br>**new** `reflog-hard-recover-then-pick-export` |

### 4.2 Reversing Pushed Commits Safely — teaches git revert

`reversing-pushed-commits-safely`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Undo a pushed commit safely | debut | `git push`, `git revert <commit>` | 4.2.1 `re6`<br>4.2.2 `re7`<br>4.2.3 `re8` |
| Easy | 2. Sync first, then revert | spiral | — | **new** `revert-easy-pull-then-revert-docs`<br>**new** `revert-easy-pull-then-revert-api` |
| Medium | 1. Find the culprit from the symptom | practice | — | 4.2.4 `rm6`<br>4.2.5 `rm7`<br>4.2.6 `rm8` |
| Medium | 2. Revert on the release branch | spiral | — | **new** `revert-medium-release-branch-pricing`<br>**new** `revert-medium-release-branch-auth` |
| Hard | 1. Two faulty commits, one publish | transfer | — | 4.2.7 `rh6`<br>4.2.8 `rh7`<br>4.2.9 `rh8` |
| Hard | 2. Rewrite only what isn't published | spiral | — | **new** `revert-hard-amend-local-revert-pushed-shop`<br>**new** `revert-hard-amend-local-revert-pushed-blog` |

### 4.3 Completing Rebase Recovery Sequences — teaches git rebase recovery

`completing-rebase-recovery-sequences`

| Tier | Wave | Role | Command guide introduces | Variants |
|---|---|---|---|---|
| Easy | 1. Replay your branch onto main | debut | `git rebase <upstream>` | 4.3.1 `be6`<br>4.3.2 `be7`<br>4.3.3 `be8` |
| Easy | 2. Abandon a stopped rebase | debut | `git rebase --abort` | 4.3.6 `rebase-medium-abort` ↤M<br>**new** `rebase-easy-abort-stopped-docs` |
| Easy | 3. Resolve and continue a rebase | debut | `git rebase --continue` | 4.3.9 `rebase-hard-continue` ↤H<br>**new** `rebase-easy-continue-config` |
| Medium | 1. Move only your commits | debut | `git rebase --onto <newbase> <upstream> [<branch>]` | 4.3.4 `bm6`<br>4.3.5 `bm7` |
| Medium | 2. Reset to the original tip, then rebase | debut | `git reset --hard <commit>` | 4.3.7 `bh6` ↤H<br>4.3.8 `bh7` ↤H |
| Hard | 1. Continue the rebase, then publish safely | spiral | — | **new** `rebase-hard-continue-then-lease-search`<br>**new** `rebase-hard-continue-then-lease-billing` |
| Hard | 2. Abort, then move only your commits | transfer | — | **new** `rebase-hard-abort-then-onto-reports`<br>**new** `rebase-hard-abort-then-onto-ui` |
| Hard | 3. Undo a bad rebase and republish | spiral | — | **new** `rebase-hard-reset-rebase-lease-cli`<br>**new** `rebase-hard-reset-rebase-lease-api` |


## New scenarios

Each needs the full bank contract (story, starting point, real-world context, task, checklist, answer key, accepted alternatives, expected result, evaluation, budgets) plus a runtime fixture. Literal names below are placeholders the author may change.

### Module 1 — Local Repository Foundations (18)

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `init-hard-nested-service` | 1.1 Hard 2 | Workspace with services/billing-api, services/search-api and docs; none is a repository. | Initialize only services/billing-api, first branch trunk. | `git init -b trunk services/billing-api` | Replaces the re-run wave (state-only grading, 2026-10-20). |
| `init-hard-nested-course` | 1.1 Hard 2 | Workspace with courses/git-basics, courses/sql-basics and templates. | Initialize only courses/git-basics on main. | `git init -b main courses/git-basics` | Replaces the re-run wave. |
| `clone-medium-shallow-metrics` | 1.2 Medium 2 | Workspace outside any repository; no metrics-review folder. | Clone the metrics-dash URL into metrics-review with only the latest commit. | `git clone --depth 1 https://example.test/data/metrics-dash.git metrics-review` |  |
| `clone-hard-shallow-ssh-audit` | 1.2 Hard 2 | Workspace with other project folders; no rules-review folder. | Clone audit-rules over SSH into rules-review, keeping only the last two commits. | `git clone --depth 2 git@example.test:security/audit-rules.git rules-review` |  |
| `commit-medium-new-project-portfolio` | 1.3 Medium 2 | Folder portfolio is not a repository; index.html and styles.css are new; notes.txt is private. | Make it a repository on main and commit only the two site files as the first snapshot. | `git init -b main` → `git add index.html styles.css` → `git commit -m "Initial portfolio"` | Spiral: `git init` from 1.1. |
| `commit-medium-new-project-recipes` | 1.3 Medium 2 | Folder recipes is not a repository; recipes.md and shopping.md are new; draft.txt is private. | Make it a repository on main and commit only the two notes files. | `git init -b main` → `git add recipes.md shopping.md` → `git commit -m "Start recipe notes"` | Spiral: `git init` from 1.1. |
| `partial-medium-hunk-plus-test` | 1.4 Medium 2 | src/cart.py holds a rounding fix and a debug print; tests/test_cart.py is a new test. | Commit the rounding fix and the whole test file together; leave the debug print out. | `git add -p src/cart.py` → `git add tests/test_cart.py` → `git commit -m "Fix cart total rounding"` | Spiral: `git add <path>` from 1.3. |
| `partial-medium-hunk-plus-doc` | 1.4 Medium 2 | src/export.py holds a quoting fix and an experimental flag; docs/export.md is updated. | Commit the quoting fix and the doc change together; leave the flag out. | `git add -p src/export.py` → `git add docs/export.md` → `git commit -m "Fix CSV quoting"` | Spiral: `git add <path>` from 1.3. |
| `partial-hard-split-two-commits-api` | 1.4 Hard 2 | src/api.py holds an expiry fix and an unrelated logging tidy-up. | Make two commits: the fix first, then the tidy-up, each with its stated message. | `git add -p src/api.py` → `git commit -m "Fix token expiry check"` → `git add src/api.py` → `git commit -m "Tidy API logging"` |  |
| `partial-hard-split-two-commits-ui` | 1.4 Hard 2 | src/menu.js holds a focus-trap fix and helper renames. | Make two commits: the fix first, then the renames. | `git add -p src/menu.js` → `git commit -m "Fix menu focus trap"` → `git add src/menu.js` → `git commit -m "Rename menu helpers"` |  |
| `amend-medium-hunk-into-last-checkout` | 1.5 Medium 2 | The last commit missed one hunk of src/checkout.py; the file also holds a debug hunk. | Add only the missing hunk to the last commit and keep its message. | `git add -p src/checkout.py` → `git commit --amend -m "Validate checkout totals"` | Spiral: `git add -p` from 1.4. |
| `amend-medium-hunk-into-last-search` | 1.5 Medium 2 | The last commit missed one hunk of src/search.py; the file also holds a logging hunk. | Add only the missing hunk to the last commit and keep its message. | `git add -p src/search.py` → `git commit --amend -m "Rank exact matches first"` | Spiral: `git add -p` from 1.4. |
| `amend-hard-fix-message-then-commit-api` | 1.5 Hard 2 | The last local commit has a vague message; docs/limits.md has new, uncommitted docs. | Correct the last commit's message, then commit the docs as a separate commit. | `git commit --amend -m "Add rate limiter"` → `git add docs/limits.md` → `git commit -m "Document rate limits"` | Order matters: amending after the new commit would rewrite the wrong one. |
| `amend-hard-fix-message-then-commit-docs` | 1.5 Hard 2 | The last local commit has a vague message; docs/faq.md is new. | Correct the last commit's message, then commit the FAQ separately. | `git commit --amend -m "Document install steps"` → `git add docs/faq.md` → `git commit -m "Add install FAQ"` |  |
| `restore-easy-discard-theme` | 1.6 Easy 2 | styles/theme.css has unwanted local edits; nothing is staged. | Throw the edits away and restore the committed file. | `git restore styles/theme.css` |  |
| `restore-medium-unstage-then-commit-login` | 1.6 Medium 2 | src/login.py and notes/todo.md are both staged. | Commit only the login fix; keep the note's edits, unstaged. | `git restore --staged notes/todo.md` → `git commit -m "Fix login redirect"` | Spiral: `git commit -m` from 1.3. |
| `restore-medium-unstage-then-commit-cart` | 1.6 Medium 2 | src/cart_badge.js and scratch/ideas.txt are both staged. | Commit only the badge fix; keep the ideas file's edits, unstaged. | `git restore --staged scratch/ideas.txt` → `git commit -m "Fix cart badge count"` | Spiral: `git commit -m` from 1.3. |
| `restore-hard-capstone-report` | 1.6 Hard 2 | debug.log is staged; tmp/output.txt has stray edits; src/report.py holds a totals fix and an experiment. | Unstage the log (keep it), discard the output edits, and commit only the totals fix. | `git restore --staged debug.log` → `git restore tmp/output.txt` → `git add -p src/report.py` → `git commit -m "Fix report totals"` | Module 1 capstone: restore + add -p + commit. |
| `restore-hard-capstone-invoice` | 1.6 Hard 2 | notes/invoice-ideas.md is staged; build/invoice.html has stray edits; src/invoice.py holds a due-date fix and a refactor. | Unstage the notes, discard the build edits, and commit only the due-date fix. | `git restore --staged notes/invoice-ideas.md` → `git restore build/invoice.html` → `git add -p src/invoice.py` → `git commit -m "Fix invoice due date"` | Module 1 capstone. |

### Module 2 — Branching and Collaboration (33)

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `switch-easy-back-to-main-docs` | 2.1 Easy 2 | On feature/docs-refresh with a clean tree; main exists. | Switch back to main. | `git switch main` |  |
| `switch-easy-back-to-main-api` | 2.1 Easy 2 | On feature/api-keys with a clean tree; main exists. | Switch back to main. | `git switch main` |  |
| `switch-hard-detached-save-and-return` | 2.1 Hard 2 | HEAD is detached at a spike commit; branches main and develop. | Keep the commit on archive/spike-results, then finish on develop. | `git switch -c archive/spike-results` → `git switch develop` |  |
| `bn-easy-delete-merged-typo` | 2.2 Easy 2 | On main; fix/readme-typo is already merged into main. | Delete the merged local branch. | `git branch -d fix/readme-typo` |  |
| `bn-easy-delete-merged-spike` | 2.2 Easy 2 | On main; spike/old-search is already merged into main. | Delete the merged local branch. | `git branch -d spike/old-search` |  |
| `bn-hard-named-branch-commit-parser` | 2.2 Hard 2 | On main; src/parser.py holds the fix; debug.log has a stray local edit. | Discard the stray edit, start the fix on a branch that follows the team convention, and commit it there. | `git restore debug.log` → `git switch -c fix/parser-unicode` → `git add src/parser.py` → `git commit -m "Handle unicode identifiers"` | Spiral: `git restore`, `git add`, `git commit` from Module 1. |
| `bn-hard-named-branch-commit-billing` | 2.2 Hard 2 | On main; src/billing.py holds the fix; tmp/billing-dump.txt has a stray edit; tickets use PROJ-<n>/<topic>. | Discard the stray edit, create the ticket branch, and commit the fix there. | `git restore tmp/billing-dump.txt` → `git switch -c PROJ-733/invoice-rounding` → `git add src/billing.py` → `git commit -m "Round invoice totals"` | Spiral: Module 1 forms. |
| `stash-easy-pop-search` | 2.3 Easy 2 | On feature/search with a clean tree; one stash entry holds the search work. | Bring the stashed work back into the working folder and remove it from the stash. | `git stash pop` |  |
| `stash-easy-pop-profile` | 2.3 Easy 2 | On feature/profile with a clean tree; one stash entry holds the profile work. | Bring the stashed work back and remove it from the stash. | `git stash pop` |  |
| `stash-hard-two-stashes-reports` | 2.3 Hard 1 | On feature/reports; stash@{0} is an abandoned chart experiment, stash@{1} is the real work. | Discard only the abandoned entry and restore the other. | `git stash drop stash@{0}` → `git stash pop` |  |
| `stash-hard-cancelled-experiment` | 2.3 Hard 2 | On feature/experiment with unfinished edits; release/v3 needs checking. | Check release/v3 without carrying the edits, return, and finish clean with no stash entry left (the work was cancelled). | `git stash` → `git switch release/v3` → `git switch feature/experiment` → `git stash drop` |  |
| `push-medium-branch-commit-publish-search` | 2.4 Medium 1 | On main; src/filters.js has finished work; origin is available. | Move the work to feature/search-filters, commit it, publish the branch and track it. | `git switch -c feature/search-filters` → `git add src/filters.js` → `git commit -m "Add search filters"` → `git push -u origin feature/search-filters` | Spiral: `switch -c` (2.1), add/commit (1.3). |
| `push-medium-branch-commit-publish-invoices` | 2.4 Medium 1 | On main; src/invoice_pdf.py has finished work; origin is available. | Move the work to feature/invoice-pdf, commit it, publish and track. | `git switch -c feature/invoice-pdf` → `git add src/invoice_pdf.py` → `git commit -m "Add invoice PDF export"` → `git push -u origin feature/invoice-pdf` | Spiral. |
| `push-hard-amend-then-lease-api` | 2.4 Hard 1 | On feature/api-retry, already pushed; the last commit's message is wrong; nobody else has pushed. | Correct the message and update origin without overwriting work you have not seen. | `git commit --amend -m "Add retry to API client"` → `git push --force-with-lease origin feature/api-retry` | Spiral: `--amend` (1.5). |
| `push-hard-amend-then-lease-docs` | 2.4 Hard 1 | On docs/sso, already pushed; the last commit's message is wrong. | Correct the message and update origin safely. | `git commit --amend -m "Document SSO setup"` → `git push --force-with-lease origin docs/sso` | Spiral: `--amend` (1.5). |
| `pull-medium-update-then-branch-ui` | 2.5 Medium 2 | On main, behind origin/main. | Bring main up to date, then start feature/dark-mode from it. | `git pull origin main` → `git switch -c feature/dark-mode` | Spiral: `switch -c` (2.1). |
| `pull-medium-update-then-branch-api` | 2.5 Medium 2 | On main, behind origin/main. | Bring main up to date, then start feature/webhooks from it. | `git pull origin main` → `git switch -c feature/webhooks` | Spiral. |
| `pull-hard-stash-pull-pop-docs` | 2.5 Hard 2 | On main with uncommitted edits to docs/guide.md; origin/main changed the same file. | Update main from origin without losing the edits; keep them uncommitted. | `git stash` → `git pull origin main` → `git stash pop` | Spiral: stash (2.3). Spike: `git pull` must refuse when local edits overlap incoming changes, or the stash is optional. |
| `pull-hard-stash-pull-pop-app` | 2.5 Hard 2 | On develop with uncommitted edits to src/app.py; origin/develop changed it too. | Update develop without losing the edits. | `git stash` → `git pull origin develop` → `git stash pop` | Spiral. Spike: `git pull` must refuse when local edits overlap incoming changes, or the stash is optional. |
| `rec-medium-commit-then-reconcile-docs` | 2.6 Medium 2 | On main; docs/setup.md and notes/draft.md are staged; origin/main has new commits. | Unstage the draft, commit the setup docs, integrate origin/main and publish. | `git restore --staged notes/draft.md` → `git commit -m "Document local setup"` → `git pull origin main` → `git push origin main` | Spiral: `restore --staged` (1.6), commit (1.3). |
| `rec-medium-commit-then-reconcile-api` | 2.6 Medium 2 | On develop; src/health.py and scratch/payload.json are staged; origin/develop moved. | Unstage the scratch file, commit the health check, integrate and publish. | `git restore --staged scratch/payload.json` → `git commit -m "Add health check"` → `git pull origin develop` → `git push origin develop` | Spiral. |
| `merge-medium-commit-switch-noff-reports` | 2.7 Medium 2 | On feature/reports with src/reports.py finished but uncommitted. | Commit it, then land feature/reports on main with a visible merge commit. | `git add src/reports.py` → `git commit -m "Add monthly report"` → `git switch main` → `git merge --no-ff feature/reports` | Spiral: commit (1.3), switch (2.1). |
| `merge-medium-commit-switch-noff-auth` | 2.7 Medium 2 | On feature/mfa with src/mfa.py finished but uncommitted. | Commit it, then land feature/mfa on develop with a merge commit. | `git add src/mfa.py` → `git commit -m "Add MFA prompt"` → `git switch develop` → `git merge --no-ff feature/mfa` | Spiral. |
| `merge-hard-land-publish-tidy-search` | 2.7 Hard 2 | On feature/search, finished and committed. | Land it on main with a merge commit, publish main, and remove the local branch safely. | `git switch main` → `git merge --no-ff feature/search` → `git push origin main` → `git branch -d feature/search` | Spiral: push (2.4), branch -d (2.2). |
| `merge-hard-land-publish-tidy-billing` | 2.7 Hard 2 | On hotfix/billing-rounding, committed. | Land it on release/v2 with a merge commit, publish, and remove the local branch safely. | `git switch release/v2` → `git merge --no-ff hotfix/billing-rounding` → `git push origin release/v2` → `git branch -d hotfix/billing-rounding` | Spiral. |
| `squash-medium-squash-publish-onboarding` | 2.8 Medium 2 | On main; feature/onboarding has four WIP commits. | Land it on main as one commit and publish main. | `git merge --squash feature/onboarding` → `git commit -m "Add onboarding flow"` → `git push origin main` | Spiral: push (2.4). |
| `squash-medium-squash-publish-export` | 2.8 Medium 2 | On develop; feature/export-csv has three WIP commits. | Land it on develop as one commit and publish. | `git merge --squash feature/export-csv` → `git commit -m "Add CSV export"` → `git push origin develop` | Spiral. |
| `squash-hard-switch-squash-cleanup-cli` | 2.8 Hard 2 | On feature/cli-colors (unmerged WIP commits). | Land it on main as one commit and leave no local feature branch. | `git switch main` → `git merge --squash feature/cli-colors` → `git commit -m "Add CLI colors"` → `git branch -D feature/cli-colors` | Spiral: switch (2.1). |
| `squash-hard-switch-squash-cleanup-ui` | 2.8 Hard 2 | On feature/toast-ui. | Land it on develop as one commit and leave no local feature branch. | `git switch develop` → `git merge --squash feature/toast-ui` → `git commit -m "Add toast notifications"` → `git branch -D feature/toast-ui` | Spiral. |
| `rb-medium-land-and-retire-search` | 2.9 Medium 2 | On main; feature/search is finished; origin has the branch. | Land it with a merge commit, publish main, and delete the branch on origin (keep it locally). | `git merge --no-ff feature/search` → `git push origin main` → `git push origin --delete feature/search` | Spiral: merge --no-ff (2.7), push (2.4). |
| `rb-medium-land-and-retire-billing` | 2.9 Medium 2 | On main; feature/billing is finished; origin has the branch. | Land, publish, and delete the branch on origin. | `git merge --no-ff feature/billing` → `git push origin main` → `git push origin --delete feature/billing` | Spiral. |
| `rb-hard-capstone-release-notes` | 2.9 Hard 2 | On main; a teammate finished origin/feature/release-notes; someone already deleted feature/old-banner on origin. | Fetch, land the teammate's branch with a merge commit, publish main, delete the branch on origin, and clear stale remote-tracking refs. | `git fetch origin` → `git merge --no-ff origin/feature/release-notes` → `git push origin main` → `git push origin --delete feature/release-notes` → `git fetch --prune origin` | Module 2 capstone. |
| `rb-hard-capstone-payments` | 2.9 Hard 2 | On main; origin/feature/payments-v2 is finished; a stale remote-tracking ref remains. | Fetch, land, publish, delete on origin, prune. | `git fetch origin` → `git merge --no-ff origin/feature/payments-v2` → `git push origin main` → `git push origin --delete feature/payments-v2` → `git fetch --prune origin` | Module 2 capstone. |

### Module 3 — Conflict Resolution (15)

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `manual-easy-abort-wrong-branch` | 3.1 Easy 3 | On main; a merge of feature/legacy-theme stopped on a conflict, but it was the wrong branch. | Cancel the merge so main is exactly as before. | `git merge --abort` |  |
| `manual-easy-abort-too-early` | 3.1 Easy 3 | On main; a merge of feature/payments stopped on a conflict before review finished. | Cancel the merge so main is exactly as before. | `git merge --abort` |  |
| `manual-medium-pull-conflict-readme` | 3.1 Medium 2 | On main with a local commit to README.md; origin/main changed the same lines. | Integrate origin/main, resolve README.md to the shown lines, finish the merge, and publish. | `git pull origin main` → *Project Files edit* → `git add README.md` → `git commit --no-edit` → `git push origin main` | Spiral: pull/push (2.4-2.6). Spike: `git pull` must stop on a conflict (it reuses the merge path). |
| `manual-medium-pull-conflict-config` | 3.1 Medium 2 | On develop with a local commit to config/app.yml; origin/develop changed it too. | Integrate, resolve to the shown lines, finish, publish. | `git pull origin develop` → *Project Files edit* → `git add config/app.yml` → `git commit --no-edit` → `git push origin develop` | Spiral. Spike: `git pull` must stop on a conflict (it reuses the merge path). |
| `manual-hard-abort-redo-payments` | 3.1 Hard 2 | On main; a merge of feature/payments-v1 (wrong branch) stopped on a conflict. | Cancel it, merge feature/payments-v2, resolve src/payments.py to the shown lines, and finish. | `git merge --abort` → `git merge feature/payments-v2` → *Project Files edit* → `git add src/payments.py` → `git commit --no-edit` |  |
| `mergetool-medium-configure-tool-billing` | 3.2 Medium 2 | On main; no merge tool is configured; the team uses meld; merging feature/billing-copy will conflict. | Configure the tool, merge, resolve in the tool, and finish with the default message. | `git config merge.tool meld` → `git merge feature/billing-copy` → `git mergetool` → `git commit --no-edit` |  |
| `mergetool-hard-no-backup-api` | 3.2 Hard 2 | On main; the merge tool keeps .orig backups unless told not to; merging feature/api-v3 will conflict. | Resolve with the tool and leave no backup files in the folder or the commit. | `git config mergetool.keepBackup false` → `git merge feature/api-v3` → `git mergetool` → `git commit --no-edit` |  |
| `cherry-easy-trace-source-hotfix` | 3.3 Easy 2 | On release-2.4; c2 on main is the fix. | Apply c2 as a new commit whose message records where it came from. | `git cherry-pick -x c2` |  |
| `cherry-medium-conflict-continue-auth` | 3.3 Medium 1 | On release-1.9; picking c1 will conflict in src/auth.py. | Apply c1, resolve to the shown lines, and finish the pick. | `git cherry-pick c1` → *Project Files edit* → `git add src/auth.py` → `git cherry-pick --continue` |  |
| `cherry-medium-abort-stopped-pick` | 3.3 Medium 2 | On release-review-2; a pick stopped on a conflict in src/cart.py with staged changes. | Cancel it so the branch is exactly as before. | `git cherry-pick --abort` |  |
| `cherry-medium-two-fixes-one-commit-login` | 3.3 Medium 3 | On release-1.2; c2 and c3 on main are login fixes. | Apply both without committing, then make one reviewed commit with the shown message. | `git cherry-pick --no-commit c2` → `git cherry-pick --no-commit c3` → `git commit -m "Backport login fixes"` | Practice of `--no-commit`. |
| `cherry-medium-two-fixes-one-commit-tax` | 3.3 Medium 3 | On release-3.1; c1 and c4 on main are tax fixes. | Apply both without committing, then commit once. | `git cherry-pick --no-commit c1` → `git cherry-pick --no-commit c4` → `git commit -m "Backport tax fixes"` | Practice of `--no-commit`. |
| `cherry-hard-two-releases-security` | 3.3 Hard 1 | On main; c3 is a security fix that release-2.1 and release-2.0 both need. | Apply c3 to both release branches; finish on release-2.0. | `git switch release-2.1` → `git cherry-pick c3` → `git switch release-2.0` → `git cherry-pick c3` |  |
| `cherry-hard-backport-capstone-export` | 3.3 Hard 2 | On release-1.4; a pick of the wrong commit stopped on a conflict; the right fix is c5. | Cancel the wrong pick, apply c5 recording its source, resolve src/export.py to the shown lines, and finish. | `git cherry-pick --abort` → `git cherry-pick -x c5` → *Project Files edit* → `git add src/export.py` → `git cherry-pick --continue` | Module 3 capstone: --abort, -x, --continue. |
| `cherry-hard-backport-capstone-login` | 3.3 Hard 2 | On release-3.0; a pick of the wrong commit stopped; the right fix is c4. | Cancel, apply c4 with its source recorded, resolve src/login.py, finish. | `git cherry-pick --abort` → `git cherry-pick -x c4` → *Project Files edit* → `git add src/login.py` → `git cherry-pick --continue` | Module 3 capstone. |

### Module 4 — Advanced Recovery and History (18)

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `reflog-medium-recover-and-publish-search` | 4.1 Medium 2 | On main after a reset dropped the search fix; origin is available. | Recover the lost tip on recovery/search-fix and publish it with upstream for review. | `git reflog` → `git switch -c recovery/search-fix c4` → `git push -u origin recovery/search-fix` | Spiral: `push -u` (2.4). |
| `reflog-medium-recover-and-publish-billing` | 4.1 Medium 2 | On main after a reset dropped the billing work. | Recover it on recovery/billing and publish it with upstream. | `git reflog` → `git switch -c recovery/billing c5` → `git push -u origin recovery/billing` | Spiral. |
| `reflog-hard-recover-then-pick-auth` | 4.1 Hard 2 | On main after a reset; the reflog shows an abandoned experiment and the auth fix on top of it. | Keep the lost tip on recovery/auth without leaving main, then bring only the auth fix to main as a new commit. | `git reflog` → `git show c4` → `git branch recovery/auth c4` → `git cherry-pick c4` | Spiral: `git branch <name> <commit>` (2.1), cherry-pick (3.3). |
| `reflog-hard-recover-then-pick-export` | 4.1 Hard 2 | On main after a reset; the reflog shows a debug commit and the export fix on top of it. | Keep the lost tip on recovery/export without leaving main, then bring only the fix to main. | `git reflog` → `git show c5` → `git branch recovery/export c5` → `git cherry-pick c5` | Spiral: `git branch` (2.1), cherry-pick (3.3). |
| `revert-easy-pull-then-revert-docs` | 4.2 Easy 2 | On main, one commit behind origin/main; c3 (already published) broke the docs build. | Get up to date, undo c3 with a new commit, and publish. | `git pull origin main` → `git revert c3` → `git push` | Spiral: pull (2.5). |
| `revert-easy-pull-then-revert-api` | 4.2 Easy 2 | On main, behind origin/main; c4 (published) broke the API. | Get up to date, undo c4, publish. | `git pull origin main` → `git revert c4` → `git push` | Spiral: pull (2.5). |
| `revert-medium-release-branch-pricing` | 4.2 Medium 2 | On main; release/2.1 tracks origin/release/2.1; c4 on it broke pricing. | Undo c4 on release/2.1 without rewriting history and publish it. | `git switch release/2.1` → `git revert c4` → `git push` | Spiral: switch (2.1). |
| `revert-medium-release-branch-auth` | 4.2 Medium 2 | On main; release/1.8 tracks origin; c3 on it broke sign-in. | Undo c3 on release/1.8 and publish. | `git switch release/1.8` → `git revert c3` → `git push` | Spiral. |
| `revert-hard-amend-local-revert-pushed-shop` | 4.2 Hard 2 | On main; c0-c3 are published; c4 is local with the message 'wip'; published c2 broke checkout. | Fix c4's message (it is unpublished), undo c2 without rewriting published history, and publish once. | `git commit --amend -m "Add order export"` → `git revert c2` → `git push` | Spiral: `--amend` (1.5); teaches rewrite-only-unpublished. |
| `revert-hard-amend-local-revert-pushed-blog` | 4.2 Hard 2 | On main; c4 is local with a vague message; published c3 broke the RSS feed. | Fix c4's message, undo c3 safely, publish once. | `git commit --amend -m "Add RSS feed"` → `git revert c3` → `git push` | Spiral. |
| `rebase-easy-abort-stopped-docs` | 4.3 Easy 2 | Mid-rebase of feature/docs-search onto main, stopped on a conflict in docs/index.md. | Cancel the rebase so the branch is exactly as before. | `git rebase --abort` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-easy-continue-config` | 4.3 Easy 3 | Mid-rebase of feature/config-loader, stopped on a conflict in config/app.yml. | Resolve to the shown lines and finish the rebase. | *Project Files edit* → `git add config/app.yml` → `git rebase --continue` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-continue-then-lease-search` | 4.3 Hard 1 | feature/search was pushed earlier; now mid-rebase onto main, stopped on a conflict in src/search.py. | Resolve, finish the rebase, and update origin/feature/search without overwriting unseen work. | *Project Files edit* → `git add src/search.py` → `git rebase --continue` → `git push --force-with-lease origin feature/search` | Spiral: `--force-with-lease` (2.4). Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-continue-then-lease-billing` | 4.3 Hard 1 | feature/billing was pushed; now mid-rebase, stopped on a conflict in src/billing.py. | Resolve, finish, update origin safely. | *Project Files edit* → `git add src/billing.py` → `git rebase --continue` → `git push --force-with-lease origin feature/billing` | Spiral. Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-abort-then-onto-reports` | 4.3 Hard 2 | Mid-rebase of feature/reports onto main, but the branch was started from spike/charts and drags its commits along. | Cancel the rebase, then move only feature/reports' own commits onto main. | `git rebase --abort` → `git rebase --onto main spike/charts feature/reports` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-abort-then-onto-ui` | 4.3 Hard 2 | Mid-rebase of feature/table-ui, which was started from spike/new-grid. | Cancel, then move only its own commits onto main. | `git rebase --abort` → `git rebase --onto main spike/new-grid feature/table-ui` | Starts mid-rebase: the simulator's `git rebase` never stops on a conflict. |
| `rebase-hard-reset-rebase-lease-cli` | 4.3 Hard 3 | feature/cli-flags was pushed; a bad rebase dropped a commit; the original tip is in the reflog. | Restore the complete branch, replay it on main, and update origin safely. | `git reflog` → `git reset --hard c6` → `git rebase main` → `git push --force-with-lease origin feature/cli-flags` | Spiral: `--force-with-lease` (2.4). |
| `rebase-hard-reset-rebase-lease-api` | 4.3 Hard 3 | feature/rate-limits was pushed; a bad rebase dropped the limiter commit. | Restore it from the reflog, rebase onto main, update origin safely. | `git reflog` → `git reset --hard c5` → `git rebase main` → `git push --force-with-lease origin feature/rate-limits` | Spiral. |


## Scenarios that change tier (49)

Content stays as authored; the placed tier's command budget applies (Easy 12, Medium 10, Hard 8 counted commands). Every move goes to an easier tier, so no budget shrinks.

| Scenario | From | To |
|---|---|---|
| `init-med-oss` | Medium | Easy |
| `init-hard-ci` | Hard | Medium |
| `clone-med-feature` | Medium | Easy |
| `clone-medium-cli-starter-folder` | Medium | Easy |
| `clone-hard-research-log-ssh` | Hard | Medium |
| `commit-med-docker` | Medium | Easy |
| `amend-hard-convention` | Hard | Easy |
| `amend-medium-profile-missing-css` | Medium | Easy |
| `v21h-from-develop` | Hard | Medium |
| `bn-hard-oss-rename` | Hard | Medium |
| `bn-hard-corp-rename` | Hard | Medium |
| `v23h-dropped-auth` | Hard | Medium |
| `v23h-dropped-api` | Hard | Medium |
| `v24m-auth` | Medium | Easy |
| `v24m-orders` | Medium | Easy |
| `v24m-parser` | Medium | Easy |
| `push-med-docs-track` | Medium | Easy |
| `v24h-auth` | Hard | Medium |
| `v24h-orders` | Hard | Medium |
| `v25m-main` | Medium | Easy |
| `v25m-feature` | Medium | Easy |
| `v25m-develop` | Medium | Easy |
| `pull-med-free-client` | Medium | Easy |
| `v25h-main` | Hard | Medium |
| `v25h-feature` | Hard | Medium |
| `v26m-auth` | Medium | Easy |
| `v26m-payments` | Medium | Easy |
| `v27m-auth` | Medium | Easy |
| `v27m-payments` | Medium | Easy |
| `v28h-auth` | Hard | Easy |
| `v28h-orders` | Hard | Easy |
| `v29m-auth` | Medium | Easy |
| `v29m-orders` | Medium | Easy |
| `v29m-parser` | Medium | Easy |
| `rb-med-free-prune` | Medium | Easy |
| `v29h-auth` | Hard | Medium |
| `v29h-orders` | Hard | Medium |
| `mergetool-hard-choose-tool` | Hard | Medium |
| `cherry-medium-login-timeout` | Medium | Easy |
| `cherry-medium-invoice-rounding` | Medium | Easy |
| `cherry-hard-trace-source` | Hard | Easy |
| `cherry-medium-no-commit` | Medium | Easy |
| `cherry-medium-staged-review` | Medium | Easy |
| `cherry-hard-export-conflict` | Hard | Medium |
| `cherry-hard-abort-conflict` | Hard | Medium |
| `rebase-medium-abort` | Medium | Easy |
| `rebase-hard-continue` | Hard | Easy |
| `bh6` | Hard | Medium |
| `bh7` | Hard | Medium |

## Spaced reuse after each debut

Counted on the default path: later waves in which every variant uses the form. Core workflow forms must reach at least two later waves including one later level; specialized forms at least one harder tier. Setup forms (`init`, `clone`) are exempt.

| Form | Debut (level / tier) | Later waves | Later levels |
|---|---|---:|---:|
| `git init` | initializing-a-local-repository / Easy | 6 | 1 |
| `git init -b` | initializing-a-local-repository / Easy | 5 | 1 |
| `git clone` | cloning-a-remote-repository / Easy | 6 | 0 |
| `git clone -b` | cloning-a-remote-repository / Easy | 1 | 0 |
| `git clone --depth` | cloning-a-remote-repository / Medium | 2 | 0 |
| `git add` | staging-and-committing-basic-workflow / Easy | 30 | 9 |
| `git commit` | staging-and-committing-basic-workflow / Easy | 44 | 12 |
| `git commit -m` | staging-and-committing-basic-workflow / Easy | 32 | 10 |
| `technique:several-paths` | staging-and-committing-basic-workflow / Easy | 4 | 1 |
| `git add -p` | partial-staging-and-git-add-p / Easy | 7 | 2 |
| `git commit --amend` | amending-commits / Easy | 7 | 2 |
| `git restore` | unstaging-and-discarding-changes / Easy | 7 | 2 |
| `git restore --staged` | unstaging-and-discarding-changes / Easy | 5 | 1 |
| `git switch` | creating-and-switching-branches / Easy | 29 | 10 |
| `git switch -c` | creating-and-switching-branches / Easy | 16 | 4 |
| `git branch` | creating-and-switching-branches / Medium | 10 | 5 |
| `git branch -d` | branch-naming-and-housekeeping / Easy | 5 | 2 |
| `git stash` | stashing-work-in-progress / Easy | 6 | 1 |
| `git stash pop` | stashing-work-in-progress / Easy | 3 | 1 |
| `git stash drop` | stashing-work-in-progress / Medium | 2 | 0 |
| `git push` | pushing-to-a-remote / Easy | 28 | 8 |
| `git push -u` | pushing-to-a-remote / Easy | 2 | 1 |
| `git push --force-with-lease` | pushing-to-a-remote / Medium | 4 | 1 |
| `git fetch` | fetching-and-pulling / Easy | 9 | 3 |
| `git pull` | fetching-and-pulling / Easy | 8 | 3 |
| `git merge` | reconciling-diverged-histories / Easy | 29 | 5 |
| `technique:remote-branch` | reconciling-diverged-histories / Easy | 5 | 2 |
| `git merge --no-ff` | completing-branch-merges / Easy | 6 | 1 |
| `git merge --squash` | squash-merging / Easy | 5 | 0 |
| `git branch -D` | squash-merging / Easy | 2 | 0 |
| `git push --delete` | deleting-and-recovering-remote-branches / Easy | 4 | 0 |
| `git fetch --prune` | deleting-and-recovering-remote-branches / Easy | 1 | 0 |
| `git commit --no-edit` | resolving-conflicts-manually / Easy | 11 | 1 |
| `git merge --abort` | resolving-conflicts-manually / Easy | 1 | 0 |
| `git mergetool` | using-a-merge-tool / Easy | 5 | 0 |
| `git config` | using-a-merge-tool / Medium | 1 | 0 |
| `git cherry-pick` | cherry-picking-commits / Easy | 8 | 1 |
| `git cherry-pick -x` | cherry-picking-commits / Easy | 1 | 0 |
| `git cherry-pick --no-commit` | cherry-picking-commits / Easy | 1 | 0 |
| `git cherry-pick --continue` | cherry-picking-commits / Medium | 1 | 0 |
| `git cherry-pick --abort` | cherry-picking-commits / Medium | 1 | 0 |
| `git revert` | reversing-pushed-commits-safely / Easy | 5 | 0 |
| `git rebase` | completing-rebase-recovery-sequences / Easy | 7 | 0 |
| `git rebase --abort` | completing-rebase-recovery-sequences / Easy | 1 | 0 |
| `git rebase --continue` | completing-rebase-recovery-sequences / Easy | 1 | 0 |
| `git rebase --onto` | completing-rebase-recovery-sequences / Medium | 1 | 0 |
| `git reset` | completing-rebase-recovery-sequences / Medium | 1 | 0 |
| `git reset --hard` | completing-rebase-recovery-sequences / Medium | 1 | 0 |

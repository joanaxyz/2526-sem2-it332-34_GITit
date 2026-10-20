# Module 2 Blueprint — Branching and Collaboration

**9 levels · 54 waves · about 113 min with no failures (today about 117) · Mapped to SO 2.1–SO 2.9 · 33 new scenarios**

## Module overview

Learners work with branches and a shared remote: create and name branches, shelve work, publish, fetch and pull, reconcile diverged histories, merge, squash, and retire branches everywhere.

Chapter description in the seed: *Create, switch, and delete branches; stash work in progress; push and pull with remotes; merge, squash-merge, and reconcile diverged histories through scenario practice.*

**Module KPIs:** SCR ≥ 80% (validity gate), CAR ≥ 70%, HLCR ≥ 70%, ARC ≤ 2. Definitions: ARCHITECTURE.md, *Performance metrics*.

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
| `git switch -c <branch> [<start-point>]` | ⚡ ACTION | 2.1 Easy 1 · Create a branch and switch to it | 11 later waves; also in levels 2.2, 2.4, 2.5 |
| `git switch <branch>` | ⚡ ACTION | 2.1 Easy 2 · Go back to main | 13 later waves; also in levels 2.3, 2.6, 2.7, 2.8, 3.3, 4.2 |
| `git branch <branch> [<start-point>]` | ⚡ ACTION | 2.1 Medium 1 · Create a branch without switching | 1 later wave; also in level 4.1 |
| `git branch -d <branch>` | ⚡ ACTION | 2.2 Easy 2 · Delete a merged branch | 5 later waves; also in levels 2.7, 2.9 |
| `git stash` | ⚡ ACTION | 2.3 Easy 1 · Shelve work and switch | 4 later waves; also in level 2.5 |
| `git stash pop` | ⚡ ACTION | 2.3 Easy 2 · Bring the shelved work back | 3 later waves; also in level 2.5 |
| `git stash drop [stash@{n}]` | ⚡ ACTION | 2.3 Medium 2 · Discard a cancelled draft | 2 later waves |
| `git push <remote> <branch>` | ⚡ ACTION | 2.4 Easy 1 · Publish a branch | 11 later waves; also in levels 2.6, 2.7, 2.8, 2.9, 3.1 |
| `git push -u <remote> <branch>` | ⚡ ACTION | 2.4 Easy 2 · Publish and track | 2 later waves; also in level 4.1 |
| `git push --force-with-lease <remote> <branch>` | ⚡ ACTION | 2.4 Medium 2 · Republish rewritten history safely | 4 later waves; also in level 4.3 |
| `git fetch origin` | ⚡ ACTION | 2.5 Easy 1 · See what's new on origin | 8 later waves; also in levels 2.6, 2.8, 2.9 |
| `git pull <remote> <branch>` | ⚡ ACTION | 2.5 Easy 2 · Bring the new commits in | 8 later waves; also in levels 2.6, 3.1, 4.2 |
| `git merge <branch>` | ⚡ ACTION | 2.6 Easy 2 · Fetch, merge the remote branch, push | 15 later waves; also in levels 2.7, 3.1, 3.2 |
| technique: remote-branch | Technique | 2.6 Easy 2 · Fetch, merge the remote branch, push | 5 later waves; also in levels 2.8, 2.9 |
| `git merge --no-ff <branch>` | ⚡ ACTION | 2.7 Easy 2 · Keep a visible merge commit | 6 later waves; also in level 2.9 |
| `git merge --squash <branch>` | ⚡ ACTION | 2.8 Easy 1 · Squash a branch into one commit | 5 later waves |
| `git branch -D <branch>` | ⚡ ACTION | 2.8 Easy 2 · Squash, then force-delete the branch | 2 later waves |
| `git push <remote> --delete <branch>` | ⚡ ACTION | 2.9 Easy 1 · Delete a remote branch | 4 later waves |
| `git fetch --prune origin` | ⚡ ACTION | 2.9 Easy 2 · Prune stale remote-tracking refs | 1 later wave |

## Commands carried in from earlier modules

Reused in this module's waves (every variant uses them), so earlier skills stay fresh.

| Command | Waves | Levels |
|---|---:|---|
| `git add <path>...` | 3 | 2.2, 2.4, 2.7 |
| `git commit -m <message>` | 10 | 2.2, 2.4, 2.6, 2.7, 2.8 |
| `git commit --amend -m <message>` | 1 | 2.4 |
| `git restore --staged <path>...` | 1 | 2.6 |
| `git restore <path>...` | 1 | 2.2 |

## Diagnostic commands (non-counted)

`git status`, `git log` and `git diff` are always free to run. This module's answer keys also rely on these diagnostics:

| Command | Type | Levels |
|---|---|---|
| `git log --oneline <base>..<other>` | 🔍 DIAGNOSTIC — non-counted | 2.5 |

---

## Level 2.1 — Creating and Switching Branches

**Teaches:** `git switch` / `git branch` · **Mapped to:** SO 2.1 (CAR ≥ 70%) · **Level slug:** `creating-and-switching-branches`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 11 min (today about 12)

### Learning outcomes

- Create a branch and switch to it; switch back to existing branches.
- Create a branch without switching to it.
- Start branches from the right base: another branch, an older commit, or a detached HEAD.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git switch -c <branch> [<start-point>]` | ⚡ ACTION | Easy 1 · Create a branch and switch to it |
| `git switch <branch>` | ⚡ ACTION | Easy 2 · Go back to main |
| `git branch <branch> [<start-point>]` | ⚡ ACTION | Medium 1 · Create a branch without switching |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Create a branch and switch to it | debut | `git switch -c <branch> [<start-point>]` | Create a feature branch from the current commit and move onto it. | 2.1.1 Create feature/auth and switch to it<br>2.1.2 Create bugfix/login and switch to it<br>2.1.3 Create experiment/ui and switch to it<br>2.1.4 Create feature/database-models and switch to it<br>2.1.5 Create hotfix/session-timeout and switch to it |
| Easy | 2. Go back to main | debut | `git switch <branch>` | Switch back to an existing branch. | **new** `switch-easy-back-to-main-docs`<br>**new** `switch-easy-back-to-main-api` |
| Medium | 1. Create a branch without switching | debut | `git branch <branch> [<start-point>]` | Create one branch without leaving the current one, then create and switch to another. | 2.1.6 Create feature/payments and a test branch from the 2-commit main tip<br>2.1.7 Create feature/notifications and a docs branch from the 3-commit main tip<br>2.1.8 Create feature/export and a docs branch from the 4-commit main tip |
| Medium | 2. Start from another branch's tip | practice | — | Create a branch from the right base while standing on a different branch. | 2.1.9 Create feature/docs-update from develop's tip<br>2.1.12 Create feature/workspace from main's tip while on develop *(from Hard)* |
| Hard | 1. Start from an older commit | transfer | — | Branch from an older commit or from a detached HEAD. | 2.1.10 Create hotfix/critical at c1 (not HEAD)<br>2.1.11 Create saved-work at the detached HEAD position |
| Hard | 2. Save detached work, then go back | transfer | — | Save a detached commit on a branch, then return to another branch. | 2.1.13 Create review/v1-snapshot at c1, then return to main<br>**new** `switch-hard-detached-save-and-return` |

---

## Level 2.2 — Branch Naming Conventions

**Teaches:** branch naming + `git branch -d` · **Mapped to:** SO 2.2 (CAR ≥ 70%) · **Level slug:** `branch-naming-and-housekeeping`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 11 min (today about 11)

### Learning outcomes

- Name branches by the team's convention (ticket, scope, topic).
- Delete merged branches safely and replace badly named ones.
- Start fixes on well-named branches.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git branch -d <branch>` | ⚡ ACTION | Easy 2 · Delete a merged branch |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Follow the naming convention | practice | — | Name a new branch exactly as the team's convention says. | 2.2.1 Create PROJ-418/password-reset<br>2.2.2 Create feature/shopping-cart<br>2.2.3 Create jdelacruz/fix-parser-edge-case<br>2.2.4 Create feature/jm/database-models<br>2.2.5 Create client/55-contact-form-redesign |
| Easy | 2. Delete a merged branch | debut | `git branch -d <branch>` | Delete a merged local branch safely. | **new** `bn-easy-delete-merged-typo`<br>**new** `bn-easy-delete-merged-spike` |
| Medium | 1. Build the name from the brief | practice | — | Assemble the branch name from the ticket, scope and topic in the brief. | 2.2.6 Construct and create PROJ-512/email-notification<br>2.2.7 Construct and create bugfix/login-redirect<br>2.2.8 Construct and create infra/api-gateway/log-rotation<br>2.2.9 Infer the convention and create fix/tokenizer-crash |
| Medium | 2. Replace a badly named branch | compose | — | Delete a badly named branch and recreate it correctly. | 2.2.10 Replace myFix with fix/renderer-memory-leak *(from Hard)*<br>2.2.11 Replace auth-update with PROJ-301/auth-module-update *(from Hard)* |
| Hard | 1. Fix the name, keep the convention | transfer | — | Repair a branch whose name breaks the convention, inferring the right name. | 2.2.12 Replace fix/cart-total with bugfix/cart-total<br>2.2.13 Replace test/LoginFlow with test/login-flow |
| Hard | 2. Start the fix on a well-named branch | spiral | — | Discard a stray edit, then commit a fix on a well-named branch. | **new** `bn-hard-named-branch-commit-parser`<br>**new** `bn-hard-named-branch-commit-billing` |

---

## Level 2.3 — Stashing Work in Progress

**Teaches:** `git stash` · **Mapped to:** SO 2.3 (CAR ≥ 70%) · **Level slug:** `stashing-work-in-progress`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 14 min (today about 16)

### Learning outcomes

- Shelve unfinished work to switch branches with a clean tree.
- Restore shelved work, or drop it when the work is cancelled.
- Manage several stash entries and pull with work in progress.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git stash` | ⚡ ACTION | Easy 1 · Shelve work and switch |
| `git stash pop` | ⚡ ACTION | Easy 2 · Bring the shelved work back |
| `git stash drop [stash@{n}]` | ⚡ ACTION | Medium 2 · Discard a cancelled draft |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Shelve work and switch | debut | `git stash` | Shelve unfinished edits so you can switch branches with a clean tree. | 2.3.1 Stash auth work and switch to main<br>2.3.2 Stash notify work and switch to develop<br>2.3.3 Stash cache work and switch to release/v2<br>2.3.4 Stash models work and switch to review/groupmate-branch<br>2.3.5 Stash docs work and switch to release/stable |
| Easy | 2. Bring the shelved work back | debut | `git stash pop` | Restore shelved work and remove it from the stash. | **new** `stash-easy-pop-search`<br>**new** `stash-easy-pop-profile` |
| Medium | 1. Stash, visit, return, restore | compose | — | Shelve, visit another branch, come back and restore. | 2.3.6 Stash payments work, check main, restore<br>2.3.7 Stash orders work, check hotfix, restore<br>2.3.8 Stash analytics work, check release/v2, restore<br>2.3.9 Stash billing work, check hotfix/tax-fix, restore |
| Medium | 2. Discard a cancelled draft | debut | `git stash drop [stash@{n}]` | Shelve work for a visit, then drop it because the work was cancelled. | 2.3.10 Check main while the auth rework is cancelled *(from Hard)*<br>2.3.11 Check hotfix/urgent while the api-v2 draft is cancelled *(from Hard)* |
| Hard | 1. Two stashes, keep the right one | transfer | — | Drop the wrong stash entry and restore the right one. | 2.3.13 Discard one abandoned stash and restore the other<br>**new** `stash-hard-two-stashes-reports` |
| Hard | 2. Cancelled work, clean exit | transfer | — | Visit another branch and leave no trace of cancelled work. | 2.3.12 Check release/v1 while the refactor is cancelled<br>**new** `stash-hard-cancelled-experiment` |

---

## Level 2.4 — Pushing to a Remote

**Teaches:** `git push` · **Mapped to:** SO 2.4 (CAR ≥ 70%) · **Level slug:** `pushing-to-a-remote`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 11)

### Learning outcomes

- Publish a branch and set its upstream.
- Update rewritten remote history safely with `--force-with-lease`.
- Publish new work end to end: branch, commit, `push -u`.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git push <remote> <branch>` | ⚡ ACTION | Easy 1 · Publish a branch |
| `git push -u <remote> <branch>` | ⚡ ACTION | Easy 2 · Publish and track |
| `git push --force-with-lease <remote> <branch>` | ⚡ ACTION | Medium 2 · Republish rewritten history safely |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Publish a branch | debut | `git push <remote> <branch>` | Publish a local branch to origin. | 2.4.1 Push feature/auth to origin<br>2.4.2 Push feature/orders to origin<br>2.4.3 Push feature/parser to origin<br>2.4.4 Push feature/user-auth to origin<br>2.4.5 Push feature/client-landing to origin |
| Easy | 2. Publish and track | debut | `git push -u <remote> <branch>` | Publish a branch and set its upstream. | 2.4.6 Push feature/auth and set its upstream *(from Medium)*<br>2.4.7 Push feature/orders and set its upstream *(from Medium)*<br>2.4.8 Push feature/parser and set its upstream *(from Medium)*<br>2.4.9 Push feature/v2-migration-guide and set its upstream *(from Medium)* |
| Medium | 1. Branch, commit, publish | spiral | — | Start a branch, commit the work, and publish it with upstream. | **new** `push-medium-branch-commit-publish-search`<br>**new** `push-medium-branch-commit-publish-invoices` |
| Medium | 2. Republish rewritten history safely | debut | `git push --force-with-lease <remote> <branch>` | Update a rewritten remote branch without overwriting work you haven't seen. | 2.4.10 Publish rewritten feature/auth without overwriting a teammate's work *(from Hard)*<br>2.4.11 Publish rewritten feature/orders without overwriting a teammate's work *(from Hard)* |
| Hard | 1. Amend a published commit, republish | spiral | — | Correct an already-published commit, then republish it safely. | **new** `push-hard-amend-then-lease-api`<br>**new** `push-hard-amend-then-lease-docs` |
| Hard | 2. Rewritten branch, careful publish | transfer | — | Publish rewritten history safely with minimal help. | 2.4.12 Publish rewritten feature/parser without overwriting a teammate's work<br>2.4.13 Publish rewritten feature/pipeline-config without overwriting a teammate's work |

---

## Level 2.5 — Fetching and Pulling from a Remote

**Teaches:** `git fetch` / `git pull` · **Mapped to:** SO 2.5 (CAR ≥ 70%) · **Level slug:** `fetching-and-pulling`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 12)

### Learning outcomes

- Download remote updates without changing local branches.
- Integrate remote work with `git pull`.
- Review incoming commits before integrating them.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git fetch origin` | ⚡ ACTION | Easy 1 · See what's new on origin |
| `git pull <remote> <branch>` | ⚡ ACTION | Easy 2 · Bring the new commits in |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. See what's new on origin | debut | `git fetch origin` | Download remote updates without changing your branch. | 2.5.1 Fetch to update origin/main tracking<br>2.5.2 Fetch to update origin/feature/auth tracking<br>2.5.3 Fetch to update origin/develop tracking<br>2.5.4 Fetch to update origin/feature/models tracking<br>2.5.5 Fetch to update origin/release/v2 tracking |
| Easy | 2. Bring the new commits in | debut | `git pull <remote> <branch>` | Integrate a remote branch into your local one. | 2.5.6 Pull origin/main into local main *(from Medium)*<br>2.5.7 Pull origin/feature/auth into local feature/auth *(from Medium)*<br>2.5.8 Pull origin/develop into local develop *(from Medium)*<br>2.5.9 Pull origin/staging into local staging *(from Medium)* |
| Medium | 1. Review before integrating | compose | — | Fetch, review exactly what is new, then pull. | 2.5.10 Review incoming work on main, then update main *(from Hard)*<br>2.5.11 Review incoming work on feature/auth, then update it *(from Hard)* |
| Medium | 2. Update, then branch from fresh main | spiral | — | Update main, then start a feature branch from it. | **new** `pull-medium-update-then-branch-ui`<br>**new** `pull-medium-update-then-branch-api` |
| Hard | 1. Review incoming work | transfer | — | Review and integrate incoming commits with minimal help. | 2.5.12 Review incoming work on develop, then update it<br>2.5.13 Review incoming work on release/next, then update it |
| Hard | 2. Pull with local work in progress | spiral | — | Shelve local edits, pull, then restore the edits. | **new** `pull-hard-stash-pull-pop-docs`<br>**new** `pull-hard-stash-pull-pop-app` |

---

## Level 2.6 — Reconciling Diverged Local and Remote Histories

**Teaches:** fetch/pull + merge + push · **Mapped to:** SO 2.6 (CAR ≥ 70%) · **Level slug:** `reconciling-diverged-histories`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 14 min (today about 16)

### Learning outcomes

- Recover from a rejected push by integrating remote work first.
- Fetch and merge a remote-tracking branch, then publish.
- Reconcile the right branch even when starting on another one.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git merge <branch>` | ⚡ ACTION | Easy 2 · Fetch, merge the remote branch, push |
| technique: remote-branch | Technique | Easy 2 · Fetch, merge the remote branch, push |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Pull, then push again | practice | — | Fix a rejected push by integrating first, then push again. | 2.6.1 Reconcile and push feature/auth<br>2.6.2 Reconcile and push feature/payments<br>2.6.3 Reconcile and push hotfix/critical<br>2.6.4 Reconcile and push feature/ui-layout<br>2.6.5 Reconcile and push main |
| Easy | 2. Fetch, merge the remote branch, push | debut | `git merge <branch>`, technique: remote-branch | Fetch, merge the remote-tracking branch, then push. | 2.6.6 Fetch, merge, push feature/auth *(from Medium)*<br>2.6.7 Fetch, merge, push feature/payments *(from Medium)* |
| Medium | 1. Reconcile a teammate's branch | practice | — | Reconcile a teammate's branch without the guide. | 2.6.8 Fetch, merge, push hotfix/critical<br>2.6.9 Fetch, merge, push feature/test-runner-v2 |
| Medium | 2. Commit, reconcile, publish | spiral | — | Unstage a stray file, commit, reconcile with origin, publish. | **new** `rec-medium-commit-then-reconcile-docs`<br>**new** `rec-medium-commit-then-reconcile-api` |
| Hard | 1. Reconcile from the wrong branch | transfer | — | Switch to the right branch, reconcile it, and publish. | 2.6.10 Reconcile and publish feature/auth from the wrong branch<br>2.6.11 Reconcile and publish feature/payments from the wrong branch |
| Hard | 2. Reconcile and publish under pressure | transfer | — | Reconcile and publish a critical branch from the wrong starting point. | 2.6.12 Reconcile and publish hotfix/critical from the wrong branch<br>2.6.13 Reconcile and publish the audit branch from develop |

---

## Level 2.7 — Completing Branch Merges

**Teaches:** `git merge` · **Mapped to:** SO 2.7 (CAR ≥ 70%) · **Level slug:** `completing-branch-merges`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 11)

### Learning outcomes

- Merge a finished branch with a fast forward or an explicit merge commit.
- Land features on the right target branch from anywhere.
- Publish and tidy up after merging.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git merge --no-ff <branch>` | ⚡ ACTION | Easy 2 · Keep a visible merge commit |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Fast-forward merge | practice | — | Merge a finished branch when a fast forward is fine. | 2.7.1 Fast-forward merge feature/auth into main<br>2.7.2 Fast-forward merge feature/payments into develop<br>2.7.3 Fast-forward merge hotfix/fix-critical into release/v2<br>2.7.4 Fast-forward merge docs/readme-update into staging<br>2.7.5 Fast-forward merge feature/contact-form into integration |
| Easy | 2. Keep a visible merge commit | debut | `git merge --no-ff <branch>` | Merge with an explicit merge commit, even when a fast forward is possible. | 2.7.6 No-ff merge feature/auth into main *(from Medium)*<br>2.7.7 No-ff merge feature/payments into develop *(from Medium)* |
| Medium | 1. Merge with a merge commit | practice | — | Merge with a merge commit into another target branch. | 2.7.8 No-ff merge hotfix/fix-critical into release/v2<br>2.7.9 No-ff merge feature/sso-integration into release/v1 |
| Medium | 2. Finish the feature, then land it | spiral | — | Commit the last change, then land the feature with a merge commit. | **new** `merge-medium-commit-switch-noff-reports`<br>**new** `merge-medium-commit-switch-noff-auth` |
| Hard | 1. Land from the wrong branch | transfer | — | Switch to the target and land a feature with a visible merge. | 2.7.10 Land feature/auth on main from the wrong branch, with a visible merge<br>2.7.11 Land feature/payments on develop from the wrong branch, with a visible merge<br>2.7.12 Land hotfix/critical on release/v1 from the wrong branch, with a visible merge<br>2.7.13 Land hotfix/cert-renewal on release/stable from the wrong branch, with a visible merge |
| Hard | 2. Land, publish, tidy up | spiral | — | Land a feature, publish, and delete the local branch safely. | **new** `merge-hard-land-publish-tidy-search`<br>**new** `merge-hard-land-publish-tidy-billing` |

---

## Level 2.8 — Squash Merging

**Teaches:** `git merge --squash` · **Mapped to:** SO 2.8 (CAR ≥ 70%) · **Level slug:** `squash-merging`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 14 min (today about 15)

### Learning outcomes

- Land a branch as a single commit with `--squash`.
- Remove squashed branches with a forced delete.
- Squash teammates' remote branches and publish the result.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git merge --squash <branch>` | ⚡ ACTION | Easy 1 · Squash a branch into one commit |
| `git branch -D <branch>` | ⚡ ACTION | Easy 2 · Squash, then force-delete the branch |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Squash a branch into one commit | debut | `git merge --squash <branch>` | Land a branch's work as one new commit. | 2.8.1 Squash-merge feature/auth into main<br>2.8.2 Squash-merge feature/orders into develop<br>2.8.3 Squash-merge feature/parser into release/v2<br>2.8.4 Squash-merge feature/report-generator into integration<br>2.8.5 Squash-merge feature/payment-flow into staging |
| Easy | 2. Squash, then force-delete the branch | debut | `git branch -D <branch>` | Squash-land a branch, then remove it with a forced delete. | 2.8.10 Land feature/auth as one commit and clean up *(from Hard)*<br>2.8.11 Land feature/orders as one commit and clean up *(from Hard)* |
| Medium | 1. Squash a teammate's remote branch | practice | — | Fetch and squash a teammate's remote branch into one commit. | 2.8.6 Fetch then squash-merge origin/feature/auth into main<br>2.8.7 Fetch then squash-merge origin/feature/orders into develop<br>2.8.8 Fetch then squash-merge origin/feature/parser into release/v2<br>2.8.9 Fetch then squash-merge origin/feature/gdpr-export into staging |
| Medium | 2. Squash and publish | spiral | — | Squash-land a feature and publish the result. | **new** `squash-medium-squash-publish-onboarding`<br>**new** `squash-medium-squash-publish-export` |
| Hard | 1. One commit, no leftovers | transfer | — | Land as one commit and leave no feature branch behind. | 2.8.12 Land feature/parser as one commit and clean up<br>2.8.13 Land feature/log-rotation as one commit and clean up |
| Hard | 2. Squash-land from another branch | spiral | — | Switch to the target, squash-land, and clean up. | **new** `squash-hard-switch-squash-cleanup-cli`<br>**new** `squash-hard-switch-squash-cleanup-ui` |

---

## Level 2.9 — Deleting and Recovering Remote Branches

**Teaches:** `git push --delete` / `git fetch --prune` · **Mapped to:** SO 2.9 (CAR ≥ 70%) · **Level slug:** `deleting-and-recovering-remote-branches`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 13 min (today about 12)

### Learning outcomes

- Delete branches on origin and prune stale remote-tracking refs.
- Retire merged branches everywhere, safely.
- Run the full land, publish, retire and prune loop.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git push <remote> --delete <branch>` | ⚡ ACTION | Easy 1 · Delete a remote branch |
| `git fetch --prune origin` | ⚡ ACTION | Easy 2 · Prune stale remote-tracking refs |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Delete a remote branch | debut | `git push <remote> --delete <branch>` | Delete a merged branch on origin and keep the local copy. | 2.9.1 Delete origin/feature/auth<br>2.9.2 Delete origin/feature/orders<br>2.9.3 Delete origin/feature/parser<br>2.9.4 Delete origin/feature/group-auth<br>2.9.5 Delete origin/feature/sprint12-compliance |
| Easy | 2. Prune stale remote-tracking refs | debut | `git fetch --prune origin` | Remove remote-tracking refs for branches deleted on the server. | 2.9.6 Prune stale origin/feature/auth ref *(from Medium)*<br>2.9.7 Prune stale origin/feature/orders ref *(from Medium)*<br>2.9.8 Prune stale origin/feature/parser ref *(from Medium)*<br>2.9.9 Prune stale origin/feature/old-landing ref *(from Medium)* |
| Medium | 1. Retire a branch everywhere | compose | — | Delete a merged branch on origin and locally, safely. | 2.9.10 Retire feature/auth on origin and locally *(from Hard)*<br>2.9.11 Retire feature/orders on origin and locally *(from Hard)* |
| Medium | 2. Land and retire | spiral | — | Land a feature, publish main, and delete the branch on origin. | **new** `rb-medium-land-and-retire-search`<br>**new** `rb-medium-land-and-retire-billing` |
| Hard | 1. Retire safely | transfer | — | Retire a merged branch everywhere with minimal help. | 2.9.12 Retire feature/parser on origin and locally<br>2.9.13 Retire feature/oss-contribution on origin and locally |
| Hard | 2. Fetch, land, publish, retire, prune | spiral | — | Module 2 review: fetch, land, publish, retire, prune. | **new** `rb-hard-capstone-release-notes`<br>**new** `rb-hard-capstone-payments` |

---

## New scenarios in this module (33)

To be written in the team's scenario format (story, starting point, real-world context, task, checklist, answer key, accepted alternatives, expected result, evaluation, budgets). Names below are placeholders the author may change.

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `switch-easy-back-to-main-docs` | 2.1 Easy 2 · Go back to main | On feature/docs-refresh with a clean tree; main exists. | Switch back to main. | `git switch main` |  |
| `switch-easy-back-to-main-api` | 2.1 Easy 2 · Go back to main | On feature/api-keys with a clean tree; main exists. | Switch back to main. | `git switch main` |  |
| `switch-hard-detached-save-and-return` | 2.1 Hard 2 · Save detached work, then go back | HEAD is detached at a spike commit; branches main and develop. | Keep the commit on archive/spike-results, then finish on develop. | `git switch -c archive/spike-results` → `git switch develop` |  |
| `bn-easy-delete-merged-typo` | 2.2 Easy 2 · Delete a merged branch | On main; fix/readme-typo is already merged into main. | Delete the merged local branch. | `git branch -d fix/readme-typo` |  |
| `bn-easy-delete-merged-spike` | 2.2 Easy 2 · Delete a merged branch | On main; spike/old-search is already merged into main. | Delete the merged local branch. | `git branch -d spike/old-search` |  |
| `bn-hard-named-branch-commit-parser` | 2.2 Hard 2 · Start the fix on a well-named branch | On main; src/parser.py holds the fix; debug.log has a stray local edit. | Discard the stray edit, start the fix on a branch that follows the team convention, and commit it there. | `git restore debug.log` → `git switch -c fix/parser-unicode` → `git add src/parser.py` → `git commit -m "Handle unicode identifiers"` | Spiral: `git restore`, `git add`, `git commit` from Module 1. |
| `bn-hard-named-branch-commit-billing` | 2.2 Hard 2 · Start the fix on a well-named branch | On main; src/billing.py holds the fix; tmp/billing-dump.txt has a stray edit; tickets use PROJ-<n>/<topic>. | Discard the stray edit, create the ticket branch, and commit the fix there. | `git restore tmp/billing-dump.txt` → `git switch -c PROJ-733/invoice-rounding` → `git add src/billing.py` → `git commit -m "Round invoice totals"` | Spiral: Module 1 forms. |
| `stash-easy-pop-search` | 2.3 Easy 2 · Bring the shelved work back | On feature/search with a clean tree; one stash entry holds the search work. | Bring the stashed work back into the working folder and remove it from the stash. | `git stash pop` |  |
| `stash-easy-pop-profile` | 2.3 Easy 2 · Bring the shelved work back | On feature/profile with a clean tree; one stash entry holds the profile work. | Bring the stashed work back and remove it from the stash. | `git stash pop` |  |
| `stash-hard-two-stashes-reports` | 2.3 Hard 1 · Two stashes, keep the right one | On feature/reports; stash@{0} is an abandoned chart experiment, stash@{1} is the real work. | Discard only the abandoned entry and restore the other. | `git stash drop stash@{0}` → `git stash pop` |  |
| `stash-hard-cancelled-experiment` | 2.3 Hard 2 · Cancelled work, clean exit | On feature/experiment with unfinished edits; release/v3 needs checking. | Check release/v3 without carrying the edits, return, and finish clean with no stash entry left (the work was cancelled). | `git stash` → `git switch release/v3` → `git switch feature/experiment` → `git stash drop` |  |
| `push-medium-branch-commit-publish-search` | 2.4 Medium 1 · Branch, commit, publish | On main; src/filters.js has finished work; origin is available. | Move the work to feature/search-filters, commit it, publish the branch and track it. | `git switch -c feature/search-filters` → `git add src/filters.js` → `git commit -m "Add search filters"` → `git push -u origin feature/search-filters` | Spiral: `switch -c` (2.1), add/commit (1.3). |
| `push-medium-branch-commit-publish-invoices` | 2.4 Medium 1 · Branch, commit, publish | On main; src/invoice_pdf.py has finished work; origin is available. | Move the work to feature/invoice-pdf, commit it, publish and track. | `git switch -c feature/invoice-pdf` → `git add src/invoice_pdf.py` → `git commit -m "Add invoice PDF export"` → `git push -u origin feature/invoice-pdf` | Spiral. |
| `push-hard-amend-then-lease-api` | 2.4 Hard 1 · Amend a published commit, republish | On feature/api-retry, already pushed; the last commit's message is wrong; nobody else has pushed. | Correct the message and update origin without overwriting work you have not seen. | `git commit --amend -m "Add retry to API client"` → `git push --force-with-lease origin feature/api-retry` | Spiral: `--amend` (1.5). |
| `push-hard-amend-then-lease-docs` | 2.4 Hard 1 · Amend a published commit, republish | On docs/sso, already pushed; the last commit's message is wrong. | Correct the message and update origin safely. | `git commit --amend -m "Document SSO setup"` → `git push --force-with-lease origin docs/sso` | Spiral: `--amend` (1.5). |
| `pull-medium-update-then-branch-ui` | 2.5 Medium 2 · Update, then branch from fresh main | On main, behind origin/main. | Bring main up to date, then start feature/dark-mode from it. | `git pull origin main` → `git switch -c feature/dark-mode` | Spiral: `switch -c` (2.1). |
| `pull-medium-update-then-branch-api` | 2.5 Medium 2 · Update, then branch from fresh main | On main, behind origin/main. | Bring main up to date, then start feature/webhooks from it. | `git pull origin main` → `git switch -c feature/webhooks` | Spiral. |
| `pull-hard-stash-pull-pop-docs` | 2.5 Hard 2 · Pull with local work in progress | On main with uncommitted edits to docs/guide.md; origin/main changed the same file. | Update main from origin without losing the edits; keep them uncommitted. | `git stash` → `git pull origin main` → `git stash pop` | Spiral: stash (2.3). Spike: `git pull` must refuse when local edits overlap incoming changes, or the stash is optional. |
| `pull-hard-stash-pull-pop-app` | 2.5 Hard 2 · Pull with local work in progress | On develop with uncommitted edits to src/app.py; origin/develop changed it too. | Update develop without losing the edits. | `git stash` → `git pull origin develop` → `git stash pop` | Spiral. Spike: `git pull` must refuse when local edits overlap incoming changes, or the stash is optional. |
| `rec-medium-commit-then-reconcile-docs` | 2.6 Medium 2 · Commit, reconcile, publish | On main; docs/setup.md and notes/draft.md are staged; origin/main has new commits. | Unstage the draft, commit the setup docs, integrate origin/main and publish. | `git restore --staged notes/draft.md` → `git commit -m "Document local setup"` → `git pull origin main` → `git push origin main` | Spiral: `restore --staged` (1.6), commit (1.3). |
| `rec-medium-commit-then-reconcile-api` | 2.6 Medium 2 · Commit, reconcile, publish | On develop; src/health.py and scratch/payload.json are staged; origin/develop moved. | Unstage the scratch file, commit the health check, integrate and publish. | `git restore --staged scratch/payload.json` → `git commit -m "Add health check"` → `git pull origin develop` → `git push origin develop` | Spiral. |
| `merge-medium-commit-switch-noff-reports` | 2.7 Medium 2 · Finish the feature, then land it | On feature/reports with src/reports.py finished but uncommitted. | Commit it, then land feature/reports on main with a visible merge commit. | `git add src/reports.py` → `git commit -m "Add monthly report"` → `git switch main` → `git merge --no-ff feature/reports` | Spiral: commit (1.3), switch (2.1). |
| `merge-medium-commit-switch-noff-auth` | 2.7 Medium 2 · Finish the feature, then land it | On feature/mfa with src/mfa.py finished but uncommitted. | Commit it, then land feature/mfa on develop with a merge commit. | `git add src/mfa.py` → `git commit -m "Add MFA prompt"` → `git switch develop` → `git merge --no-ff feature/mfa` | Spiral. |
| `merge-hard-land-publish-tidy-search` | 2.7 Hard 2 · Land, publish, tidy up | On feature/search, finished and committed. | Land it on main with a merge commit, publish main, and remove the local branch safely. | `git switch main` → `git merge --no-ff feature/search` → `git push origin main` → `git branch -d feature/search` | Spiral: push (2.4), branch -d (2.2). |
| `merge-hard-land-publish-tidy-billing` | 2.7 Hard 2 · Land, publish, tidy up | On hotfix/billing-rounding, committed. | Land it on release/v2 with a merge commit, publish, and remove the local branch safely. | `git switch release/v2` → `git merge --no-ff hotfix/billing-rounding` → `git push origin release/v2` → `git branch -d hotfix/billing-rounding` | Spiral. |
| `squash-medium-squash-publish-onboarding` | 2.8 Medium 2 · Squash and publish | On main; feature/onboarding has four WIP commits. | Land it on main as one commit and publish main. | `git merge --squash feature/onboarding` → `git commit -m "Add onboarding flow"` → `git push origin main` | Spiral: push (2.4). |
| `squash-medium-squash-publish-export` | 2.8 Medium 2 · Squash and publish | On develop; feature/export-csv has three WIP commits. | Land it on develop as one commit and publish. | `git merge --squash feature/export-csv` → `git commit -m "Add CSV export"` → `git push origin develop` | Spiral. |
| `squash-hard-switch-squash-cleanup-cli` | 2.8 Hard 2 · Squash-land from another branch | On feature/cli-colors (unmerged WIP commits). | Land it on main as one commit and leave no local feature branch. | `git switch main` → `git merge --squash feature/cli-colors` → `git commit -m "Add CLI colors"` → `git branch -D feature/cli-colors` | Spiral: switch (2.1). |
| `squash-hard-switch-squash-cleanup-ui` | 2.8 Hard 2 · Squash-land from another branch | On feature/toast-ui. | Land it on develop as one commit and leave no local feature branch. | `git switch develop` → `git merge --squash feature/toast-ui` → `git commit -m "Add toast notifications"` → `git branch -D feature/toast-ui` | Spiral. |
| `rb-medium-land-and-retire-search` | 2.9 Medium 2 · Land and retire | On main; feature/search is finished; origin has the branch. | Land it with a merge commit, publish main, and delete the branch on origin (keep it locally). | `git merge --no-ff feature/search` → `git push origin main` → `git push origin --delete feature/search` | Spiral: merge --no-ff (2.7), push (2.4). |
| `rb-medium-land-and-retire-billing` | 2.9 Medium 2 · Land and retire | On main; feature/billing is finished; origin has the branch. | Land, publish, and delete the branch on origin. | `git merge --no-ff feature/billing` → `git push origin main` → `git push origin --delete feature/billing` | Spiral. |
| `rb-hard-capstone-release-notes` | 2.9 Hard 2 · Fetch, land, publish, retire, prune | On main; a teammate finished origin/feature/release-notes; someone already deleted feature/old-banner on origin. | Fetch, land the teammate's branch with a merge commit, publish main, delete the branch on origin, and clear stale remote-tracking refs. | `git fetch origin` → `git merge --no-ff origin/feature/release-notes` → `git push origin main` → `git push origin --delete feature/release-notes` → `git fetch --prune origin` | Module 2 capstone. |
| `rb-hard-capstone-payments` | 2.9 Hard 2 · Fetch, land, publish, retire, prune | On main; origin/feature/payments-v2 is finished; a stale remote-tracking ref remains. | Fetch, land, publish, delete on origin, prune. | `git fetch origin` → `git merge --no-ff origin/feature/payments-v2` → `git push origin main` → `git push origin --delete feature/payments-v2` → `git fetch --prune origin` | Module 2 capstone. |

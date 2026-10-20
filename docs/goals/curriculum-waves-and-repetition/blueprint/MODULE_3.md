# Module 3 Blueprint — Conflict Resolution

**3 levels · 21 waves · about 64 min with no failures (today about 65) · Mapped to SO 3.1–SO 3.3 · 15 new scenarios**

## Module overview

Learners resolve conflicts by hand and with a merge tool, finish or cancel stopped operations, and move individual commits between branches with cherry-pick.

Chapter description in the seed: *Practice conflict diagnostics, manual resolution, mergetool workflows, prevention checks, cherry-picking, and integrated recovery.*

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
| `git commit --no-edit` | ⚡ ACTION | 3.1 Easy 1 · Resolve one conflicted file | 11 later waves; also in level 3.2 |
| `git merge --abort` | ⚡ ACTION | 3.1 Easy 3 · Back out of a merge | 1 later wave |
| `git mergetool` | ⚡ ACTION | 3.2 Easy 1 · Resolve in the merge tool | 5 later waves |
| `git config <key> <value>` | ⚡ ACTION | 3.2 Medium 2 · Set up the team's tool first | 1 later wave |
| `git cherry-pick <commit>` | ⚡ ACTION | 3.3 Easy 1 · Copy one commit | 3 later waves; also in level 4.1 |
| `git cherry-pick -x <commit>` | ⚡ ACTION | 3.3 Easy 2 · Record where it came from | 1 later wave |
| `git cherry-pick --no-commit <commit>` | ⚡ ACTION | 3.3 Easy 3 · Pick without committing | 1 later wave |
| `git cherry-pick --continue` | ⚡ ACTION | 3.3 Medium 1 · Resolve and continue | 1 later wave |
| `git cherry-pick --abort` | ⚡ ACTION | 3.3 Medium 2 · Cancel a stopped pick | 1 later wave |

## Commands carried in from earlier modules

Reused in this module's waves (every variant uses them), so earlier skills stay fresh.

| Command | Waves | Levels |
|---|---:|---|
| `git add <path>...` | 8 | 3.1, 3.3 |
| `git commit -m <message>` | 1 | 3.3 |
| `git switch <branch>` | 1 | 3.3 |
| `git push <remote> <branch>` | 1 | 3.1 |
| `git pull <remote> <branch>` | 1 | 3.1 |
| `git merge <branch>` | 11 | 3.1, 3.2 |

## Diagnostic commands (non-counted)

`git status`, `git log` and `git diff` are always free to run. This module's answer keys need no other diagnostics.

---

## Level 3.1 — Resolving Merge Conflicts Manually

**Teaches:** merge conflicts by hand · **Mapped to:** SO 3.1 (CAR ≥ 70%) · **Level slug:** `resolving-conflicts-manually`

**Waves (Easy/Medium/Hard):** 3/2/2 · **Runs:** 8 today → 7 · **Estimated time:** about 22 min (today about 27)

### Learning outcomes

- Resolve merge conflicts by editing to the exact intended content.
- Stage resolutions and finish the merge with its prepared message.
- Abort a merge that should not happen; resolve conflicts that arrive through `git pull`.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git commit --no-edit` | ⚡ ACTION | Easy 1 · Resolve one conflicted file |
| `git merge --abort` | ⚡ ACTION | Easy 3 · Back out of a merge |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Resolve one conflicted file | debut | `git commit --no-edit` | Merge, edit one conflicted file to the exact lines, stage it, finish the merge. | 3.1.1 Resolve src/auth.js<br>3.1.2 Resolve src/profile.tsx<br>3.1.3 Resolve src/billing.py |
| Easy | 2. Resolve another file | practice | — | Resolve a conflict in a different kind of file. | 3.1.4 Resolve src/config.py<br>3.1.5 Resolve src/components/Navbar.tsx |
| Easy | 3. Back out of a merge | debut | `git merge --abort` | Cancel a conflicted merge and return to the state before it. | **new** `manual-easy-abort-wrong-branch`<br>**new** `manual-easy-abort-too-early` |
| Medium | 1. Resolve config conflicts | practice | — | Resolve configuration conflicts without contextual hints. | 3.1.6 Resolve src/routes.ts<br>3.1.7 Resolve src/policy.yml<br>3.1.8 Resolve config/gateway.yml |
| Medium | 2. A pull that conflicts | spiral | — | Pull, resolve the conflict, finish the merge and publish. | **new** `manual-medium-pull-conflict-readme`<br>**new** `manual-medium-pull-conflict-config` |
| Hard | 1. Resolve with less guidance | transfer | — | Resolve conflicts from a terser brief. | 3.1.9 Resolve src/pricing.rb<br>3.1.10 Resolve schema/orders.sql<br>3.1.11 Resolve db/migrations/001_users.sql |
| Hard | 2. Abort the wrong merge, resolve the right one | transfer | — | Abort the wrong merge, then resolve the right one. | 3.1.12 Abort a wrong merge, then resolve the right one<br>**new** `manual-hard-abort-redo-payments` |

---

## Level 3.2 — Resolving Conflicts Using a Merge Tool

**Teaches:** `git mergetool` · **Mapped to:** SO 3.2 (CAR ≥ 70%) · **Level slug:** `using-a-merge-tool`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 6 today → 6 · **Estimated time:** about 22 min (today about 23)

### Learning outcomes

- Resolve conflicts in the merge tool, including several files at once.
- Configure the team's merge tool and its backup behavior.
- Judge which side, or which file, needs resolving.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git mergetool` | ⚡ ACTION | Easy 1 · Resolve in the merge tool |
| `git config <key> <value>` | ⚡ ACTION | Medium 2 · Set up the team's tool first |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Resolve in the merge tool | debut | `git mergetool` | Resolve a conflict in the merge tool and finish the merge. | 3.2.1 Resolve src/cache.py in the merge tool<br>3.2.2 Resolve src/mailer.py in the merge tool<br>3.2.3 Resolve src/limits.js in the merge tool |
| Easy | 2. Another conflict, same tool | practice | — | Resolve another conflict with the tool. | 3.2.4 Resolve config/app.ini in the merge tool<br>3.2.5 Resolve src/labels.ts in the merge tool |
| Medium | 1. Two files in one pass | practice | — | Resolve two conflicted files in one tool session. | 3.2.6 Resolve two checkout files in the merge tool<br>3.2.7 Resolve rate-limit and CORS settings in the merge tool<br>3.2.8 Resolve two schema files in the merge tool<br>3.2.9 Resolve two documentation files in the merge tool |
| Medium | 2. Set up the team's tool first | debut | `git config <key> <value>` | Configure the team's merge tool, then resolve with it. | 3.2.10 Resolve src/prices.py when no merge tool is set up *(from Hard)*<br>**new** `mergetool-medium-configure-tool-billing` |
| Hard | 1. Judge which side to keep | transfer | — | Decide which side, or which file, needs resolving. | 3.2.11 Resolve only the conflicted file after a partial merge<br>3.2.12 Keep the incoming version of src/i18n.json |
| Hard | 2. No leftovers | transfer | — | Resolve with the tool and leave no backup files behind. | 3.2.13 Resolve src/auth.js and leave no backup files behind<br>**new** `mergetool-hard-no-backup-api` |

---

## Level 3.3 — Cherry-Picking Commits

**Teaches:** `git cherry-pick` · **Mapped to:** SO 3.3 (CAR ≥ 70%) · **Level slug:** `cherry-picking-commits`

**Waves (Easy/Medium/Hard):** 3/3/2 · **Runs:** 8 today → 8 · **Estimated time:** about 20 min (today about 15)

### Learning outcomes

- Copy single commits or short sequences onto release branches.
- Record a copied commit's source; apply changes without committing.
- Continue or cancel a stopped cherry-pick; backport to several releases.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git cherry-pick <commit>` | ⚡ ACTION | Easy 1 · Copy one commit |
| `git cherry-pick -x <commit>` | ⚡ ACTION | Easy 2 · Record where it came from |
| `git cherry-pick --no-commit <commit>` | ⚡ ACTION | Easy 3 · Pick without committing |
| `git cherry-pick --continue` | ⚡ ACTION | Medium 1 · Resolve and continue |
| `git cherry-pick --abort` | ⚡ ACTION | Medium 2 · Cancel a stopped pick |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Copy one commit | debut | `git cherry-pick <commit>` | Copy a commit, or a short sequence, from main onto a release branch. | 3.3.1 Cherry-pick c1 onto release-1.0<br>3.3.2 Cherry-pick c1 onto release-1.1<br>3.3.3 Cherry-pick c1 onto release-2.0<br>3.3.4 Cherry-pick c1 onto release-1.2<br>3.3.5 Cherry-pick c1 onto release-2.1<br>3.3.6 Cherry-pick c1 and c2 onto release-1.0 *(from Medium)*<br>3.3.7 Cherry-pick the newest invoice fix onto release-1.1 *(from Medium)* |
| Easy | 2. Record where it came from | debut | `git cherry-pick -x <commit>` | Copy a commit and record its source in the message. | 3.3.12 Cherry-pick c1 onto release-finalize and record its source *(from Hard)*<br>**new** `cherry-easy-trace-source-hotfix` |
| Easy | 3. Pick without committing | debut | `git cherry-pick --no-commit <commit>` | Apply a commit's changes, staged but not committed. | 3.3.8 Cherry-pick c1 into the index (no commit) on release-review *(from Medium)*<br>3.3.9 Cherry-pick c1 into the index (no commit) on release-staged *(from Medium)* |
| Medium | 1. Resolve and continue | debut | `git cherry-pick --continue` | Resolve a conflicted cherry-pick and finish it. | 3.3.10 Cherry-pick c1 onto release-2.0 and resolve the conflict *(from Hard)*<br>**new** `cherry-medium-conflict-continue-auth` |
| Medium | 2. Cancel a stopped pick | debut | `git cherry-pick --abort` | Cancel a stopped cherry-pick and restore the branch. | 3.3.11 Cancel a cherry-pick that stopped on a conflict *(from Hard)*<br>**new** `cherry-medium-abort-stopped-pick` |
| Medium | 3. Two fixes, one reviewed commit | compose | — | Apply two fixes without committing, then commit them once. | **new** `cherry-medium-two-fixes-one-commit-login`<br>**new** `cherry-medium-two-fixes-one-commit-tax` |
| Hard | 1. Backport to two releases | transfer | — | Backport one fix to two release branches. | 3.3.13 Cherry-pick c1 onto both release-1.2 and release-1.1<br>**new** `cherry-hard-two-releases-security` |
| Hard | 2. Abort the wrong pick, backport the right one | spiral | — | Module 3 review: cancel the wrong pick, backport the right one with its source recorded, resolve, finish. | **new** `cherry-hard-backport-capstone-export`<br>**new** `cherry-hard-backport-capstone-login` |

---

## New scenarios in this module (15)

To be written in the team's scenario format (story, starting point, real-world context, task, checklist, answer key, accepted alternatives, expected result, evaluation, budgets). Names below are placeholders the author may change.

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `manual-easy-abort-wrong-branch` | 3.1 Easy 3 · Back out of a merge | On main; a merge of feature/legacy-theme stopped on a conflict, but it was the wrong branch. | Cancel the merge so main is exactly as before. | `git merge --abort` |  |
| `manual-easy-abort-too-early` | 3.1 Easy 3 · Back out of a merge | On main; a merge of feature/payments stopped on a conflict before review finished. | Cancel the merge so main is exactly as before. | `git merge --abort` |  |
| `manual-medium-pull-conflict-readme` | 3.1 Medium 2 · A pull that conflicts | On main with a local commit to README.md; origin/main changed the same lines. | Integrate origin/main, resolve README.md to the shown lines, finish the merge, and publish. | `git pull origin main` → *Project Files edit* → `git add README.md` → `git commit --no-edit` → `git push origin main` | Spiral: pull/push (2.4-2.6). Spike: `git pull` must stop on a conflict (it reuses the merge path). |
| `manual-medium-pull-conflict-config` | 3.1 Medium 2 · A pull that conflicts | On develop with a local commit to config/app.yml; origin/develop changed it too. | Integrate, resolve to the shown lines, finish, publish. | `git pull origin develop` → *Project Files edit* → `git add config/app.yml` → `git commit --no-edit` → `git push origin develop` | Spiral. Spike: `git pull` must stop on a conflict (it reuses the merge path). |
| `manual-hard-abort-redo-payments` | 3.1 Hard 2 · Abort the wrong merge, resolve the right one | On main; a merge of feature/payments-v1 (wrong branch) stopped on a conflict. | Cancel it, merge feature/payments-v2, resolve src/payments.py to the shown lines, and finish. | `git merge --abort` → `git merge feature/payments-v2` → *Project Files edit* → `git add src/payments.py` → `git commit --no-edit` |  |
| `mergetool-medium-configure-tool-billing` | 3.2 Medium 2 · Set up the team's tool first | On main; no merge tool is configured; the team uses meld; merging feature/billing-copy will conflict. | Configure the tool, merge, resolve in the tool, and finish with the default message. | `git config merge.tool meld` → `git merge feature/billing-copy` → `git mergetool` → `git commit --no-edit` |  |
| `mergetool-hard-no-backup-api` | 3.2 Hard 2 · No leftovers | On main; the merge tool keeps .orig backups unless told not to; merging feature/api-v3 will conflict. | Resolve with the tool and leave no backup files in the folder or the commit. | `git config mergetool.keepBackup false` → `git merge feature/api-v3` → `git mergetool` → `git commit --no-edit` |  |
| `cherry-easy-trace-source-hotfix` | 3.3 Easy 2 · Record where it came from | On release-2.4; c2 on main is the fix. | Apply c2 as a new commit whose message records where it came from. | `git cherry-pick -x c2` |  |
| `cherry-medium-conflict-continue-auth` | 3.3 Medium 1 · Resolve and continue | On release-1.9; picking c1 will conflict in src/auth.py. | Apply c1, resolve to the shown lines, and finish the pick. | `git cherry-pick c1` → *Project Files edit* → `git add src/auth.py` → `git cherry-pick --continue` |  |
| `cherry-medium-abort-stopped-pick` | 3.3 Medium 2 · Cancel a stopped pick | On release-review-2; a pick stopped on a conflict in src/cart.py with staged changes. | Cancel it so the branch is exactly as before. | `git cherry-pick --abort` |  |
| `cherry-medium-two-fixes-one-commit-login` | 3.3 Medium 3 · Two fixes, one reviewed commit | On release-1.2; c2 and c3 on main are login fixes. | Apply both without committing, then make one reviewed commit with the shown message. | `git cherry-pick --no-commit c2` → `git cherry-pick --no-commit c3` → `git commit -m "Backport login fixes"` | Practice of `--no-commit`. |
| `cherry-medium-two-fixes-one-commit-tax` | 3.3 Medium 3 · Two fixes, one reviewed commit | On release-3.1; c1 and c4 on main are tax fixes. | Apply both without committing, then commit once. | `git cherry-pick --no-commit c1` → `git cherry-pick --no-commit c4` → `git commit -m "Backport tax fixes"` | Practice of `--no-commit`. |
| `cherry-hard-two-releases-security` | 3.3 Hard 1 · Backport to two releases | On main; c3 is a security fix that release-2.1 and release-2.0 both need. | Apply c3 to both release branches; finish on release-2.0. | `git switch release-2.1` → `git cherry-pick c3` → `git switch release-2.0` → `git cherry-pick c3` |  |
| `cherry-hard-backport-capstone-export` | 3.3 Hard 2 · Abort the wrong pick, backport the right one | On release-1.4; a pick of the wrong commit stopped on a conflict; the right fix is c5. | Cancel the wrong pick, apply c5 recording its source, resolve src/export.py to the shown lines, and finish. | `git cherry-pick --abort` → `git cherry-pick -x c5` → *Project Files edit* → `git add src/export.py` → `git cherry-pick --continue` | Module 3 capstone: --abort, -x, --continue. |
| `cherry-hard-backport-capstone-login` | 3.3 Hard 2 · Abort the wrong pick, backport the right one | On release-3.0; a pick of the wrong commit stopped; the right fix is c4. | Cancel, apply c4 with its source recorded, resolve src/login.py, finish. | `git cherry-pick --abort` → `git cherry-pick -x c4` → *Project Files edit* → `git add src/login.py` → `git cherry-pick --continue` | Module 3 capstone. |

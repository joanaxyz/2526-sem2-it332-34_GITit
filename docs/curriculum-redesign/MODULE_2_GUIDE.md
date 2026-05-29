# Module 2 — Scenario Design Guide

**Status: Implemented ✅**
**Last updated: 2026-05-29**

---

## Module Overview

**Title:** Branching and Collaboration
**Chapters:** 4–5
**Lessons:** 9
**Target students:** BSIT 3rd-year, CIT-U — Module 1 completion assumed

---

## SO Audit

Source of truth: *GIT it! Capstone 2 Presentation Content Guide*, Slide 9.

### Instructional SOs — redesign scope

These nine SOs define the instructional content of Module 2. Every redesigned scenario
must trace back to one of these.

| SO | Approved Description | UI Lesson | KPI |
|----|----------------------|-----------|-----|
| SO 2.1 | Creating and Switching Branches | Lesson 1 — `creating-and-switching-branches` | CAR ≥ 70% |
| SO 2.2 | Branch Naming and Housekeeping | Lesson 2 — `branch-naming-and-housekeeping` | CAR ≥ 70% |
| SO 2.3 | Stashing Work in Progress | Lesson 3 — `stashing-work-in-progress` | CAR ≥ 70% |
| SO 2.4 | Pushing to a Remote | Lesson 4 — `pushing-to-a-remote` | CAR ≥ 70% |
| SO 2.5 | Fetching and Pulling from a Remote | Lesson 5 — `fetching-and-pulling` | CAR ≥ 70% |
| SO 2.6 | Reconciling Diverged Histories | Lesson 6 — `reconciling-diverged-histories` | CAR ≥ 70% |
| SO 2.7 | Completing Branch Merges | Lesson 7 — `fast-forward-vs-three-way-merges` | CAR ≥ 70% |
| SO 2.8 | Squash Merging | Lesson 8 — `squash-merging` | CAR ≥ 70% |
| SO 2.9 | Deleting and Recovering Remote Branches | Lesson 9 — `deleting-and-recovering-remote-branches` | CAR ≥ 70% |

### KPI SOs — measurement only, not instructional objectives

These two SOs are performance indicators reported on the dashboard. They are measured
across the nine instructional lessons above. They do not define separate lessons and
do not drive scenario redesign.

| SO | Description | KPI | How it is measured |
|----|-------------|-----|--------------------|
| SO 2.10 | Independent Branch and Collaboration Management | HLCR ≥ 70% | Aggregated Hard-session completion rate across SO 2.1–2.9 lessons |
| SO 2.11 | Reduced Trial-and-Error Branching | ARC ≤ 2 | Average retry count across all Module 2 sessions |

### UI structure

Module 2 has no Guided Preview card. All 9 lessons are numbered 1–9 and directly
correspond to seed sort orders 1–9.

| UI display | Seed sort order | Slug | SO | Redesign |
|-----------|-----------------|------|----|---------|
| Lesson 1 | 1 | `creating-and-switching-branches` | SO 2.1 | ✅ |
| Lesson 2 | 2 | `branch-naming-and-housekeeping` | SO 2.2 | ✅ |
| Lesson 3 | 3 | `stashing-work-in-progress` | SO 2.3 | ✅ |
| Lesson 4 | 4 | `pushing-to-a-remote` | SO 2.4 | ✅ |
| Lesson 5 | 5 | `fetching-and-pulling` | SO 2.5 | ✅ |
| Lesson 6 | 6 | `reconciling-diverged-histories` | SO 2.6 | ✅ |
| Lesson 7 | 7 | `fast-forward-vs-three-way-merges` | SO 2.7 | ✅ |
| Lesson 8 | 8 | `squash-merging` | SO 2.8 | ✅ |
| Lesson 9 | 9 | `deleting-and-recovering-remote-branches` | SO 2.9 | ✅ |

**SO mapping verdict:** All 9 lessons map 1:1 to approved instructional SOs. No flagged
lessons. No invented SOs. SO 2.10 and SO 2.11 are KPI indicators only.

---

## Curriculum Assumptions

| Item | Decision |
|------|----------|
| Module 1 prerequisite | All SO 1.1–1.6 skills are prior knowledge — not re-introduced |
| `git checkout -b` | Valid alternative to `git switch -c` — accepted by evaluator |
| `git merge` without flags | Fast-forward by default — Lesson 7 introduces the distinction |
| `--force-with-lease` only for push | `git push --force` is not an accepted solution — safety matters |
| Conflict resolution | No conflicts in Module 2 scenarios — conflicts are Module 3 scope |
| Integration lesson | Module 2 has no standalone integration lesson — all 9 lessons are instructional SOs |
| `git pull --rebase` | Acceptable diagnostic/supporting command; not a primary solution path in Module 2 |

---

## Seed Audit

### Current implementation status

The existing `seed_module2_scenarios.py` implements all 9 lessons. Each lesson has:
- 3 Easy variants
- 3 Medium variants
- 3 Hard variants

All 9 scenarios × 3 difficulties = 27 difficulty pools. Each pool has exactly 3 variants.

**Pool sizing verdict:** 3 variants per difficulty meets the minimum (`required + 2` for
Easy = 3+2 = 5 is NOT met; for Medium = 2+2 = 4 is NOT met; for Hard = 2+2 = 4 is NOT met).

> ⚠️ **CRITICAL POOL SIZING GAP**
>
> The current seed has exactly 3 variants per difficulty across all lessons.
> Per DESIGN_PRINCIPLES.md §5:
> - Easy requires ≥ 5 variants (3 sessions required → pool ≥ 5)
> - Medium requires ≥ 4 variants (2 sessions required → pool ≥ 4)
> - Hard requires ≥ 4 variants (2 sessions required → pool ≥ 4)
>
> Every pool is currently undersized. The redesign must expand every pool to meet
> minimum sizing before implementation.

### Known slug collision issue

`MODULE_2_GUIDE.md` (placeholder, previous version) documented:

> `seed_module2_scenarios.py`: slug collision on Lesson branch-checkout easy variants.
> Case IDs starting with `branch-checkout-easy-` all truncate to the same 18-char suffix.

**Audit result:** The seed does NOT use `branch-checkout-easy-*` case IDs. The actual
case IDs used are `v21e-auth`, `v21e-login`, `v21e-ui` (for branch-create Easy), which
produce distinct slug suffixes. The documented collision was from a prior draft that was
never committed to the current seed. No slug collision exists in the current implementation.

**Verdict:** No slug collision to fix. The old placeholder note is obsolete.

---

## Pool Sizing Requirements

All 9 lessons require pool expansion. Current seed has 3 variants per difficulty.

| UI Lesson | SO | Easy req. | Easy pool | Medium req. | Medium pool | Hard req. | Hard pool | Current pool |
|-----------|-----|-----------|-----------|-------------|-------------|-----------|-----------|--------------|
| Lesson 1 — Branch Create | SO 2.1 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 2 — Branch Naming | SO 2.2 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 0 (full replacement) ⚠️ |
| Lesson 3 — Stash | SO 2.3 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 4 — Push | SO 2.4 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 5 — Fetch/Pull | SO 2.5 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 6 — Reconcile | SO 2.6 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 7 — Merge | SO 2.7 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 8 — Squash | SO 2.8 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |
| Lesson 9 — Remote Branch | SO 2.9 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 | 3 each ⚠️ |

Each lesson needs: +2 Easy variants, +1 Medium variant, +1 Hard variant.
Total new variants to design: 9 × (2+1+1) = **36 new variants**.

---

## Command Coverage Matrix

| Command | UI Lesson | SO | Counted? |
|---------|-----------|-----|---------|
| `git switch -c <branch>` | Lesson 1 | SO 2.1 | Yes |
| `git checkout -b <branch>` | Lesson 1 | SO 2.1 | Yes |
| `git switch -c <branch> <commit>` | Lesson 1 | SO 2.1 | Yes |
| `git switch -c <branch>` (named per convention) | Lesson 2 | SO 2.2 | Yes |
| `git branch -D <branch>` (correction path) | Lesson 2 | SO 2.2 | Yes |
| `git switch <branch>` | Lesson 1 / 2 | SO 2.1 / SO 2.2 | Yes |
| `git stash` | Lesson 3 | SO 2.3 | Yes |
| `git stash pop` | Lesson 3 | SO 2.3 | Yes |
| `git stash drop` | Lesson 3 | SO 2.3 | Yes |
| `git push origin <branch>` | Lesson 4 | SO 2.4 | Yes |
| `git push -u origin <branch>` | Lesson 4 | SO 2.4 | Yes |
| `git push --force-with-lease origin <branch>` | Lesson 4 | SO 2.4 | Yes |
| `git fetch origin` | Lesson 5 / 6 | SO 2.5 / SO 2.6 | Yes |
| `git pull origin <branch>` | Lesson 5 / 6 | SO 2.5 / SO 2.6 | Yes |
| `git merge <branch>` | Lesson 6 / 7 | SO 2.6 / SO 2.7 | Yes |
| `git merge --no-ff <branch>` | Lesson 7 | SO 2.7 | Yes |
| `git merge --squash <branch>` | Lesson 8 | SO 2.8 | Yes |
| `git push origin --delete <branch>` | Lesson 9 | SO 2.9 | Yes |
| `git fetch --prune origin` | Lesson 9 | SO 2.9 | Yes |
| `git status` | All lessons | Non-counted diagnostic | No |
| `git log` | All lessons | Non-counted diagnostic | No |
| `git log --oneline` | All lessons | Non-counted diagnostic | No |
| `git log --oneline --graph --all` | All lessons | Non-counted diagnostic | No |
| `git diff` | All lessons | Non-counted diagnostic | No |
| `git branch` | All lessons | Non-counted diagnostic | No |
| `git branch -v` | All lessons | Non-counted diagnostic | No |
| `git branch -a` | All lessons | Non-counted diagnostic | No |
| `git remote -v` | Lesson 4–9 | Non-counted diagnostic | No |
| `git stash list` | Lesson 3 | Non-counted diagnostic | No |
| `git show` | All lessons | Non-counted diagnostic | No |
| `git reflog` | All lessons | Non-counted diagnostic | No |
| `git fetch --dry-run` | Lesson 5 | Non-counted diagnostic | No |

---

## Difficulty Progression Philosophy

Module 2 scenarios involve multi-step workflows with remote state. Difficulty is determined
by how much context the student must infer and how many decisions they must make independently.

| Difficulty | What student is given | What student must infer |
|------------|----------------------|------------------------|
| Easy | Explicit task with specific branch/remote names, clear goal | Which command achieves the stated goal |
| Medium | Goal and partial context (remote state, branch state) | Which command variant is appropriate; correct flags |
| Hard | Situation only — no task decomposition | What state the repo is in; what the goal is; full command sequence |

**What difficulty is NOT in Module 2:**
- Easy vs Medium is not "fewer steps" vs "more steps" — it is "told what to do" vs "must read state"
- Hard is not "more branches" — it is "must identify the problem from context before solving it"
- Swapping `feature/auth` for `feature/payments` with identical command paths is not a valid variant

---

## Existing Variants Inventory

The current seed provides the following variant patterns per lesson. These are the
**existing baseline** — the redesign adds to them without replacing.

### Lesson 1 (SO 2.1) — Creating and Switching Branches

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Create at HEAD, single-commit repo | `v21e-auth`, `v21e-login`, `v21e-ui` |
| M1–M3 | Medium | Create at HEAD, multi-commit repo (2/3/4 commits) | `v21m-payments`, `v21m-notifications`, `v21m-export` |
| H1–H3 | Hard | Non-HEAD start point / detached HEAD rescue / from non-main branch | `v21h-hotfix-c1`, `v21h-detach-save`, `v21h-from-develop` |

### Lesson 2 (SO 2.2) — Branch Naming Conventions

> ⚠️ **SEED MISMATCH — FULL REPLACEMENT REQUIRED**
>
> The existing seed implements branch deletion (merged/unmerged cleanup) for this lesson.
> The redesigned lesson covers branch naming conventions — a completely different skill.
> All existing variants (`v22e-*`, `v22m-*`, `v22h-*`) must be replaced by the new
> variants defined in the Lesson 2 section above. The seed's deletion scenarios have
> been moved conceptually to Lesson 9 (SO 2.9), which already covers remote branch cleanup.
>
> Do NOT preserve any existing Lesson 2 variants during seed implementation.

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E5 | Easy | Convention explicitly stated + exact slug given | `bn-easy-corp-jira`, `bn-easy-startup-feat`, `bn-easy-oss-user`, `bn-easy-cap-initials`, `bn-easy-free-client` |
| M1–M4 | Medium | Convention stated + task given; student constructs slug | `bn-med-corp-notif`, `bn-med-startup-bugfix`, `bn-med-devops-scope`, `bn-med-oss-infer` |
| H1–H4 | Hard | Wrong branch exists; student identifies violation and corrects it | `bn-hard-oss-rename`, `bn-hard-corp-rename`, `bn-hard-startup-prefix`, `bn-hard-qa-camel` |

### Lesson 3 (SO 2.3) — Stashing Work in Progress

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Stash and switch to target branch | `v23e-auth`, `v23e-notify`, `v23e-cache` |
| M1–M3 | Medium | Stash → switch → switch back → pop | `v23m-to-main`, `v23m-to-hotfix`, `v23m-to-release` |
| H1–H3 | Hard | Stash → switch → switch back → drop (cancel work) | `v23h-dropped-auth`, `v23h-dropped-api`, `v23h-dropped-refactor` |

### Lesson 4 (SO 2.4) — Pushing to a Remote

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | First push to remote (no tracking) | `v24e-auth`, `v24e-orders`, `v24e-parser` |
| M1–M3 | Medium | Push with `-u` to set upstream tracking | `v24m-auth`, `v24m-orders`, `v24m-parser` |
| H1–H3 | Hard | Force-push after rebase (diverged history) | `v24h-auth`, `v24h-orders`, `v24h-parser` |

### Lesson 5 (SO 2.5) — Fetching and Pulling

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Fetch to update remote tracking refs only | `v25e-main`, `v25e-feature`, `v25e-develop` |
| M1–M3 | Medium | Pull (fast-forward) to integrate remote commits | `v25m-main`, `v25m-feature`, `v25m-develop` |
| H1–H3 | Hard | Fetch first to inspect, then pull to integrate | `v25h-main`, `v25h-feature`, `v25h-develop` |

### Lesson 6 (SO 2.6) — Reconciling Diverged Histories

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Diverged push rejected → pull then push | `v26e-auth`, `v26e-payments`, `v26e-hotfix` |
| M1–M3 | Medium | Diverged push rejected → fetch, merge, push | `v26m-auth`, `v26m-payments`, `v26m-hotfix` |
| H1–H3 | Hard | On wrong branch → switch, fetch, merge, push | `v26h-auth`, `v26h-payments`, `v26h-hotfix` |

### Lesson 7 (SO 2.7) — Completing Branch Merges

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Fast-forward merge (linear history) | `v27e-auth`, `v27e-payments`, `v27e-hotfix` |
| M1–M3 | Medium | No-FF merge (linear history, policy requires merge commit) | `v27m-auth`, `v27m-payments`, `v27m-hotfix` |
| H1–H3 | Hard | Switch to target branch first, then no-FF merge (diverged) | `v27h-auth`, `v27h-payments`, `v27h-hotfix` |

### Lesson 8 (SO 2.8) — Squash Merging

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Squash local feature branch, commit | `v28e-auth`, `v28e-orders`, `v28e-parser` |
| M1–M3 | Medium | Fetch remote branch first, then squash-merge, commit | `v28m-auth`, `v28m-orders`, `v28m-parser` |
| H1–H3 | Hard | Squash-merge, commit, then delete source branch | `v28h-auth`, `v28h-orders`, `v28h-parser` |

### Lesson 9 (SO 2.9) — Deleting and Recovering Remote Branches

| Variant | Difficulty | Pattern | Case IDs |
|---------|------------|---------|---------|
| E1–E3 | Easy | Delete a merged remote branch | `v29e-auth`, `v29e-orders`, `v29e-parser` |
| M1–M3 | Medium | Prune stale remote tracking refs via `fetch --prune` | `v29m-auth`, `v29m-orders`, `v29m-parser` |
| H1–H3 | Hard | Delete remote branch AND local branch | `v29h-auth`, `v29h-orders`, `v29h-parser` |

---

## New Variants Required

### Design constraints for new variants

1. Each new variant must differ from existing variants in **reasoning path**, not just parameter names.
2. Environments must vary across the pool (see DESIGN_PRINCIPLES.md §4).
3. The existing Easy variants all use startup/startup-adjacent environments. New Easy variants should
   use student-capstone, freelance, corporate, docs-project, or qa-testing environments.
4. Case IDs follow the format `{lesson-abbrev}-{difficulty}-{distinguishing-term}`.
   Keep under 30 characters; ensure first 18 slugified chars are unique within the pool.

---

## Lesson 1 (SO 2.1) — Creating and Switching Branches

**Approved SO:** SO 2.1 — Creating and Switching Branches | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Branch creation and HEAD positioning
**Primary commands:** `git switch -c`, `git checkout -b`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### Existing Easy variants (E1–E3) — see seed

E1: `v21e-auth` — feature/auth, ticketing-app, HEAD on single-commit main
E2: `v21e-login` — bugfix/login, auth-service, HEAD on single-commit main
E3: `v21e-ui` — experiment/ui, dashboard-frontend, HEAD on single-commit main

*All three use startup/tech company contexts. New variants must use different environments.*

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: First Feature Branch**

*Environment:* student-capstone

*Context:* Your group just initialized the capstone repo. The main branch has one commit
("Initial project setup"). Your group lead says: "Before we start coding, everyone creates
their own feature branch from main." You need to create `feature/database-models` and start
working there.

*Brief:* Create the branch `feature/database-models` at the current HEAD and switch to it.

*Repository initial state:*
```
main: c1 ("Initial project setup") ← HEAD
```
No other branches.

*Expected commands:*
```
git switch -c feature/database-models
```

*Target state:* HEAD on `feature/database-models`; branch points to `c1`.

*Case ID:* `bc-easy-capstone-db`

---

**E5 — Corporate: Hotfix Branch from Current HEAD**

*Environment:* corporate

*Context:* A production incident was just reported. Your team lead pings you: "Branch off
main right now and start the hotfix." You are already on main at the latest commit.
Create `hotfix/session-timeout` and move to it immediately.

*Brief:* Create and switch to `hotfix/session-timeout` from the current HEAD.

*Repository initial state:*
```
main: c1 ("Release v2.0 stable snapshot") ← HEAD
```

*Expected commands:*
```
git switch -c hotfix/session-timeout
```

*Target state:* HEAD on `hotfix/session-timeout`; branch points to `c1`.

*Case ID:* `bc-easy-corp-hotfix`

---

### Existing Medium variants (M1–M3) — see seed

M1: `v21m-payments` — 2-commit main, create feature/payments
M2: `v21m-notifications` — 3-commit main, create feature/notifications
M3: `v21m-export` — 4-commit main, create feature/export

### New Medium variant (M4)

---

**M4 — Open Source: Create from Non-Default Branch**

*Environment:* open-source

*Context:* You've forked an OSS project and cloned it locally. The active development
branch is `develop`, not `main`. Your mentor told you to branch off `develop` to start
your contribution. You are currently on `develop`. Create `feature/docs-update` from it.

*Brief:* Create `feature/docs-update` branching from `develop`'s current HEAD and switch to it.

*Repository initial state:*
```
main:    c1 ("Bootstrap OSS project")
develop: c2 ("Refactor core module") ← HEAD
```

*Expected commands:*
```
git switch -c feature/docs-update
```

*Target state:* HEAD on `feature/docs-update`; branch points to `c2` (develop's tip).

*Case ID:* `bc-med-oss-develop`

---

### Existing Hard variants (H1–H3) — see seed

H1: `v21h-hotfix-c1` — non-HEAD start point: `git switch -c hotfix/critical c1`
H2: `v21h-detach-save` — detached HEAD rescue: `git switch -c saved-work`
H3: `v21h-from-develop` — from develop branch tip, HEAD already on develop

### New Hard variant (H4)

---

**H4 — Freelance: Recover from Wrong Checkout**

*Environment:* freelance

*Context:* You needed to review an older commit (`c1`) and ran `git checkout c1` —
now you are in detached HEAD state. You've made no changes. You realize you should
have just created a branch called `review/v1-snapshot` at that older commit to review
it properly, so you can switch back to main later without losing the pointer.

*Brief:* You are in detached HEAD at `c1`. Create a branch `review/v1-snapshot` to
preserve your position, then switch back to main.

*Repository initial state:*
```
main: c2 ("Latest main commit")
HEAD: detached at c1 ("Initial release snapshot")
```

*Expected reasoning:* Detached HEAD at `c1`. Need to attach a branch at this position
first (`git switch -c review/v1-snapshot`), then switch to main.

*Expected commands:*
```
git switch -c review/v1-snapshot
git switch main
```

*Target state:* HEAD on `main`; branch `review/v1-snapshot` points to `c1`.

*Case ID:* `bc-hard-review-snap`

---

## Lesson 2 (SO 2.2) — Branch Naming Conventions

**Approved SO:** SO 2.2 — Branch Naming and Housekeeping | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Applying team branch naming conventions correctly; recognizing
and correcting convention violations
**Primary commands:** `git switch -c`, `git branch -D` (correction path only)

> **Design rationale:** This lesson addresses a finding from faculty interviews — students
> joining teams fail because companies use different naming conventions and students default
> to informal names (`myfix`, `test`, `auth`) that violate team standards. The skill is
> naming judgment: read the convention, apply it correctly, and recognize when a name is wrong.
>
> **Evaluator behavior:** The target rule checks the exact required branch name. The brief
> must leave zero ambiguity about the expected slug — disambiguation is done in the student
> context so the evaluator can be strict without being unfair.
>
> **What this lesson is NOT:** Branch deletion as housekeeping (merged-branch cleanup) is
> covered by SO 2.9 (Lesson 9). This lesson focuses solely on naming correctness.

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### Difficulty progression

| Difficulty | Convention source | Name source | Student constructs |
|------------|------------------|-------------|-------------------|
| Easy | Explicitly stated by team lead | Exact slug given in brief | Applies format; types it correctly |
| Medium | Stated in brief | Task description given; student derives slug | Infers correct slug from description + convention |
| Hard | Must be read from existing branches | Task given; no slug hint | Infers convention AND constructs slug; may also correct a violation |

---

### Easy variants (E1–E5)

*Skill at Easy:* The convention is handed to the student explicitly. The required branch
name is also given in full. The student must type it exactly — wrong casing, wrong
separator, wrong order, or wrong prefix all fail evaluation.

---

**E1 — Corporate: Jira Ticket Convention**

*Environment:* corporate

*Context:* It's your first week at a software company. Your team lead sends you a message:
"We name all branches `PROJ-{ticket-number}/{kebab-case-description}`. No exceptions —
the CI pipeline uses this pattern to link branches to tickets. Your first task is
PROJ-418: implement the password reset flow. Branch name: `PROJ-418/password-reset`."

*Brief:* Create the branch `PROJ-418/password-reset` and switch to it.

*Repository initial state:*
```
main: c1 ("Bootstrap project") ← HEAD
```

*Expected commands:*
```
git switch -c PROJ-418/password-reset
```

*Target state:* HEAD on `PROJ-418/password-reset`; branch points to `c1`.

*Evaluator note:* `PROJ-418/reset-password` ❌ `PROJ418/password-reset` ❌
`PROJ-418/passwordReset` ❌ `PROJ-418/auth` ❌

*Case ID:* `bn-easy-corp-jira`

---

**E2 — Startup: Type/Description Convention**

*Environment:* startup

*Context:* Your tech lead explains during onboarding: "We use `type/description` — type
is one of `feature`, `bugfix`, `hotfix`, or `chore`, separated by a slash, description
in kebab-case. You're starting work on the shopping cart. Branch: `feature/shopping-cart`."

*Brief:* Create branch `feature/shopping-cart` and switch to it.

*Expected commands:*
```
git switch -c feature/shopping-cart
```

*Target state:* HEAD on `feature/shopping-cart`.

*Evaluator note:* `feature/shoppingCart` ❌ `feature/shopping_cart` ❌
`feat/shopping-cart` ❌ `shopping-cart` ❌

*Case ID:* `bn-easy-startup-feat`

---

**E3 — Open Source: Username Prefix Convention**

*Environment:* open-source

*Context:* The project's CONTRIBUTING.md states: "All branches from contributors must
follow `<github-username>/<kebab-case-description>`. This lets maintainers identify
whose work is whose at a glance." Your GitHub username is `jdelacruz`. You are fixing
a parser edge case. Required branch: `jdelacruz/fix-parser-edge-case`.

*Brief:* Create branch `jdelacruz/fix-parser-edge-case` and switch to it.

*Expected commands:*
```
git switch -c jdelacruz/fix-parser-edge-case
```

*Evaluator note:* `jdelacruz/fixParserEdgeCase` ❌ `fix-parser-edge-case` ❌
`jdelacruz/fix_parser_edge_case` ❌

*Case ID:* `bn-easy-oss-user`

---

**E4 — Student Capstone: Group Naming Agreement**

*Environment:* student-capstone

*Context:* Your group agreed on a naming convention during your first sprint meeting:
`feature/<member-initials>/<short-description>`. Your initials are `jm`. You are
starting the database models module. Required branch: `feature/jm/database-models`.

*Brief:* Create branch `feature/jm/database-models` and switch to it.

*Expected commands:*
```
git switch -c feature/jm/database-models
```

*Evaluator note:* `feature/jm/databaseModels` ❌ `feature/database-models` ❌
`jm/database-models` ❌

*Case ID:* `bn-easy-cap-initials`

---

**E5 — Freelance: Client-Specified Branch Format**

*Environment:* freelance

*Context:* Your client's project manager sends you the repo access with a note:
"Please follow our branch naming: `client/{ticket-id}-{description}`. Your task is
ticket #55: redesign the contact form. Branch: `client/55-contact-form-redesign`."

*Brief:* Create branch `client/55-contact-form-redesign` and switch to it.

*Expected commands:*
```
git switch -c client/55-contact-form-redesign
```

*Evaluator note:* `client/55/contact-form-redesign` ❌ `client/contact-form-redesign` ❌
`feature/contact-form-redesign` ❌

*Case ID:* `bn-easy-free-client`

---

### Medium variants (M1–M4)

*Skill at Medium:* The convention is stated but the exact slug is not given — the student
receives the task description and must derive the correct branch name themselves. The brief
provides enough specificity that only one slug correctly matches the convention. Wrong casing,
abbreviation, or reordering fails evaluation.

---

**M1 — Corporate: Apply Jira Convention to New Task**

*Environment:* corporate

*Context:* Your team lead reminds you: "Convention is `PROJ-{ticket}/{kebab-case-description}`."
Your new task is PROJ-512: implement the email notification service. Create the branch.

*Brief:* Create a branch for PROJ-512 following the team convention. The description
component must be `email-notification`.

*Expected commands:*
```
git switch -c PROJ-512/email-notification
```

*Evaluator note:* `PROJ-512/emailNotification` ❌ `PROJ-512/email` ❌
`PROJ-512/notifications` ❌ `PROJ-512/email-notifications` ❌

*Case ID:* `bn-med-corp-notif`

---

**M2 — Startup: Apply Type Convention to a Bug Fix**

*Environment:* startup

*Context:* Convention: `type/kebab-case-description` where type is `feature`, `bugfix`,
`hotfix`, or `chore`. You have been assigned to fix a broken login redirect. The description
to use is `login-redirect`.

*Brief:* Create the correct branch for a bug fix on the login redirect.

*Expected commands:*
```
git switch -c bugfix/login-redirect
```

*Evaluator note:* `feature/login-redirect` ❌ `fix/login-redirect` ❌
`bugfix/loginRedirect` ❌ `bugfix/redirect` ❌

*Case ID:* `bn-med-startup-bugfix`

---

**M3 — DevOps: Scoped Convention for Infrastructure Work**

*Environment:* devops

*Context:* Convention: `<type>/<scope>/<description>` where type is `feat`, `fix`,
`chore`, or `infra`, and scope is the service name. You are adding log rotation to the
`api-gateway` service. Description: `log-rotation`.

*Brief:* Create the branch for this infrastructure addition following the three-part convention.

*Expected commands:*
```
git switch -c infra/api-gateway/log-rotation
```

*Evaluator note:* `infra/log-rotation` ❌ `feat/api-gateway/log-rotation` ❌
`infra/api-gateway/logRotation` ❌

*Case ID:* `bn-med-devops-scope`

---

**M4 — Open Source: Infer Convention from Existing Branches**

*Environment:* open-source

*Context:* No one told you the naming convention. You run `git branch -a` and see:
```
origin/fix/lexer-null-check
origin/fix/parser-overflow
origin/feat/dark-mode
origin/feat/keyboard-shortcuts
```
You are fixing a crash in the tokenizer. The description to use is `tokenizer-crash`.

*Brief:* Infer the convention from the existing branches, then create yours.

*Expected commands:*
```
git switch -c fix/tokenizer-crash
```

*Evaluator note:* `bugfix/tokenizer-crash` ❌ `fix/tokenizerCrash` ❌
`fix/tokenizer` ❌

*Case ID:* `bn-med-oss-infer`

---

### Hard variants (H1–H4)

*Skill at Hard:* A branch already exists with a wrong name — either created by the student
before reading the convention, or handed over from a teammate who didn't follow it.
The student must recognize the violation, delete the wrong branch, and create the correct
one. No explicit hint about what's wrong is given — the student must identify the violation
by reading the convention source (CONTRIBUTING.md text, existing branch list, or team policy
stated in the scenario).

---

**H1 — Open Source: Created Branch Before Reading CONTRIBUTING.md**

*Environment:* open-source

*Context:* You created `myFix` before reading the project's CONTRIBUTING.md, which states:
"Branch names must follow `fix/<kebab-case-description>` for bug fixes and
`feat/<kebab-case-description>` for features. CamelCase and generic names are rejected
by our CI check." You are fixing a memory leak in the renderer. The description is
`renderer-memory-leak`. You are currently on `myFix`.

*Brief:* Correct your branch name to conform to the project convention.

*Expected commands:*
```
git switch main
git branch -D myFix
git switch -c fix/renderer-memory-leak
```

*Evaluator note:* Must end with HEAD on `fix/renderer-memory-leak`; `myFix` must not exist.

*Case ID:* `bn-hard-oss-rename`

---

**H2 — Corporate: Teammate Created a Non-Compliant Branch**

*Environment:* corporate

*Context:* A new teammate created `auth-update` for ticket PROJ-301. Your team's CI
pipeline requires `PROJ-{ticket}/{description}` — branches that don't match are blocked
from merging. Your team lead asks you to fix it before the PR review. The correct
description is `auth-module-update`. The branch has no commits of its own yet (created
from HEAD, nothing staged). You are on `main`.

*Brief:* Rename the branch to comply with the convention.

*Expected commands:*
```
git branch -D auth-update
git switch -c PROJ-301/auth-module-update
```

*Evaluator note:* `auth-update` absent; HEAD on `PROJ-301/auth-module-update`.

*Case ID:* `bn-hard-corp-rename`

---

**H3 — Startup: Wrong Type Prefix**

*Environment:* startup

*Context:* Convention is `feature/`, `bugfix/`, `hotfix/`, or `chore/` — no other
prefixes are valid. A branch called `fix/cart-total` exists (wrong prefix — `fix` is
not in the allowed list; should be `bugfix`). You are on `main`. The description stays
`cart-total`.

*Brief:* Identify that `fix/` violates the convention and correct it.

*Expected commands:*
```
git branch -D fix/cart-total
git switch -c bugfix/cart-total
```

*Evaluator note:* `fix/cart-total` absent; HEAD on `bugfix/cart-total`.

*Case ID:* `bn-hard-startup-prefix`

---

**H4 — QA Testing: CamelCase Violation in a Shared Repo**

*Environment:* qa-testing

*Context:* Your QA team's convention (documented in the repo's README) is
`test/<kebab-case-description>`. A branch `test/LoginFlow` was pushed by a junior
tester — the CamelCase violates the convention and breaks your test runner's branch
name parser. You need to correct it. You are on `main`. The correct description is
`login-flow`.

*Brief:* Delete the non-compliant branch and create a correctly named replacement.

*Expected commands:*
```
git branch -D test/LoginFlow
git switch -c test/login-flow
```

*Evaluator note:* `test/LoginFlow` absent; HEAD on `test/login-flow`.

*Case ID:* `bn-hard-qa-camel`

---

## Lesson 3 (SO 2.3) — Stashing Work in Progress

**Approved SO:** SO 2.3 — Stashing Work in Progress | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Stash and restore uncommitted changes; context switching
**Primary commands:** `git stash`, `git stash pop`, `git stash drop`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Switch for Emergency Review**

*Environment:* student-capstone

*Context:* You are halfway through editing `src/models.py` on `feature/models` when your
groupmate messages: "Can you switch to main and check if my commit broke something?"
Your changes are not ready to commit. Stash them and switch to main.

*Expected commands:*
```
git stash
git switch main
```

*Target state:* Working tree clean; HEAD on `main`; stash stack has one entry.

*Case ID:* `stash-easy-cap-review`

---

**E5 — Docs Project: Context Switch Mid-Edit**

*Environment:* docs-project

*Context:* You are editing `docs/api-reference.md` on `feature/api-docs`. An urgent
correction is needed on the `release/stable` branch right now. Your changes are not
committed. Stash and switch to `release/stable`.

*Expected commands:*
```
git stash
git switch release/stable
```

*Target state:* Working tree clean; HEAD on `release/stable`; stash stack has one entry.

*Case ID:* `stash-easy-docs-switch`

---

### New Medium variant (M4)

---

**M4 — Corporate: Stash Named, Switch, Return, Pop**

*Environment:* corporate

*Context:* You are mid-feature on `feature/billing` with changes to `src/billing.py`.
An urgent request comes in to check `hotfix/tax-fix`. Stash your work with a descriptive
message, check the hotfix branch, return to your feature branch, and restore your work.

*Expected commands:*
```
git stash push -m "billing feature wip"
git switch hotfix/tax-fix
git switch feature/billing
git stash pop
```

*Target state:* Stash stack empty; HEAD on `feature/billing`; `src/billing.py` restored in working tree.

*Case ID:* `stash-med-corp-named`

---

### New Hard variant (H4)

---

**H4 — Open Source: Multiple Stash Entries, Drop Specific**

*Environment:* open-source

*Context:* You have two entries in the stash from previous context switches.
`stash@{0}` is a dead-end experiment you abandoned. `stash@{1}` is the work you
actually need to restore on `feature/lexer`. You are on `feature/lexer`.
Drop only `stash@{0}`, then pop `stash@{0}` (which is now the former `stash@{1}`).

*Expected reasoning:* `stash@{0}` is the top — drop it first. After dropping,
the former `stash@{1}` becomes `stash@{0}` and can be popped normally.

*Expected commands:*
```
git stash drop stash@{0}
git stash pop
```

*Target state:* Stash stack empty; working tree has restored changes; HEAD on `feature/lexer`.

*Case ID:* `stash-hard-oss-multi`

---

## Lesson 4 (SO 2.4) — Pushing to a Remote

**Approved SO:** SO 2.4 — Pushing to a Remote | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Publishing local commits; upstream tracking; safe force-push
**Primary commands:** `git push origin`, `git push -u origin`, `git push --force-with-lease`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Push Group Work to Shared Repo**

*Environment:* student-capstone

*Context:* Your group finished the `feature/user-auth` branch. Your repo has a remote
`origin` set up. Push the branch so your groupmates can access it. No upstream tracking
needed yet — just share the commits.

*Expected commands:*
```
git push origin feature/user-auth
```

*Case ID:* `push-easy-cap-auth`

---

**E5 — Freelance: Publish First Client Deliverable**

*Environment:* freelance

*Context:* You finished `feature/client-landing`. The client's repo is set as `origin`.
Push the branch so the client can review it. No tracking setup needed.

*Expected commands:*
```
git push origin feature/client-landing
```

*Case ID:* `push-easy-free-landing`

---

### New Medium variant (M4)

---

**M4 — Docs Project: Push and Track Documentation Branch**

*Environment:* docs-project

*Context:* You finished the `feature/v2-migration-guide` documentation branch.
Push it to origin AND set up upstream tracking so future syncs use just `git push`.

*Expected commands:*
```
git push -u origin feature/v2-migration-guide
```

*Target state:* `origin/feature/v2-migration-guide` matches local; upstream tracking set.

*Case ID:* `push-med-docs-track`

---

### New Hard variant (H4)

---

**H4 — DevOps: Safe Force-Push After Rebase Cleanup**

*Environment:* devops

*Context:* Your CI team required you to rebase `feature/pipeline-config` to squash debug
commits before merging. You've done the rebase locally. The remote `origin/feature/pipeline-config`
still has the original linear history. A normal `git push` is rejected. Use the safe force-push
option — do not use bare `--force`.

*Expected commands:*
```
git push --force-with-lease origin feature/pipeline-config
```

*Case ID:* `push-hard-devops-fwl`

---

## Lesson 5 (SO 2.5) — Fetching and Pulling from a Remote

**Approved SO:** SO 2.5 — Fetching and Pulling from a Remote | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Fetching remote tracking refs; pulling to integrate remote commits
**Primary commands:** `git fetch origin`, `git pull origin <branch>`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Check What Teammates Pushed**

*Environment:* student-capstone

*Context:* Your groupmate says "I pushed our model classes to the repo." You want to
see what was pushed to `origin/main` before deciding whether to pull. Run fetch to update
your remote tracking refs without touching your local branches.

*Expected commands:*
```
git fetch origin
```

*Target state:* `origin/main` tracking ref updated to the remote's latest commit.

*Case ID:* `fetch-easy-cap-check`

---

**E5 — Corporate: Refresh Remote Branch List**

*Environment:* corporate

*Context:* A new feature branch `feature/audit-v3` was just created on the remote by
another team. You want to see it in your local remote-tracking refs. Fetch from origin.

*Expected commands:*
```
git fetch origin
```

*Target state:* Remote tracking refs updated; `origin/feature/audit-v3` now visible locally.

*Case ID:* `fetch-easy-corp-list`

---

### New Medium variant (M4)

---

**M4 — Freelance: Pull Latest Client Changes**

*Environment:* freelance

*Context:* Your client pushed new content to `origin/main`. You need it in your local
`main` branch before you continue. Your upstream tracking is already set. Pull to integrate.

*Expected commands:*
```
git pull origin main
```

*Target state:* Local `main` fast-forwarded to match `origin/main`.

*Case ID:* `pull-med-free-client`

---

### New Hard variant (H4)

---

**H4 — Open Source: Fetch + Review + Pull Workflow**

*Environment:* open-source

*Context:* The upstream maintainer just merged a large PR. Before integrating their
changes into your local `develop` branch, you want to fetch first and check what changed
with `git log origin/develop --oneline` before deciding to pull. Then pull to integrate.

*Expected commands:*
```
git fetch origin
git pull origin develop
```
(`git log origin/develop --oneline` is non-counted diagnostic)

*Target state:* Local `develop` updated to match `origin/develop`.

*Case ID:* `fetch-hard-oss-review`

---

## Lesson 6 (SO 2.6) — Reconciling Diverged Histories

**Approved SO:** SO 2.6 — Reconciling Diverged Histories | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Integrating remote commits that blocked a push; completing the push
**Primary commands:** `git pull`, `git fetch`, `git merge`, `git push`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Teammate Committed Before You**

*Environment:* student-capstone

*Context:* You tried to push `feature/ui-layout` to origin, but it was rejected because
your groupmate pushed a new commit to the same branch while you were working. No overlapping
files — no conflict will occur. Pull to reconcile, then push.

*Expected commands:*
```
git pull origin feature/ui-layout
git push origin feature/ui-layout
```

*Case ID:* `rec-easy-cap-ui`

---

**E5 — Docs Project: Two Writers, Rejected Push**

*Environment:* docs-project

*Context:* You and a colleague are both editing the docs repo. Your push to `main` was
rejected — your colleague pushed a new chapter while you were writing. No overlap.
Pull then push.

*Expected commands:*
```
git pull origin main
git push origin main
```

*Case ID:* `rec-easy-docs-chapter`

---

### New Medium variant (M4)

---

**M4 — QA Testing: Explicit Fetch-Merge Before Push**

*Environment:* qa-testing

*Context:* Your push of `feature/test-runner-v2` was rejected. A teammate pushed fixes
to the same branch. You prefer to inspect before integrating. Fetch, then explicitly
merge `origin/feature/test-runner-v2`, then push.

*Expected commands:*
```
git fetch origin
git merge origin/feature/test-runner-v2
git push origin feature/test-runner-v2
```

*Case ID:* `rec-med-qa-testrunner`

---

### New Hard variant (H4)

---

**H4 — Corporate: Wrong Branch + Rejected Push**

*Environment:* corporate

*Context:* You need to reconcile and push `feature/compliance-audit`, but you are
currently on `develop`. The push to `feature/compliance-audit` was rejected.
Switch to the right branch, fetch, merge, and push.

*Expected commands:*
```
git switch feature/compliance-audit
git fetch origin
git merge origin/feature/compliance-audit
git push origin feature/compliance-audit
```

*Case ID:* `rec-hard-corp-audit`

---

## Lesson 7 (SO 2.7) — Completing Branch Merges

**Approved SO:** SO 2.7 — Completing Branch Merges | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Fast-forward vs three-way merge; team history policy
**Primary commands:** `git merge`, `git merge --no-ff`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Merge Documentation Branch**

*Environment:* student-capstone

*Context:* `docs/readme-update` is a direct linear descendant of `main` — no divergence.
Your group lead says "just merge it in." You are on `main`. Fast-forward is fine.

*Expected commands:*
```
git merge docs/readme-update
```

*Target state:* `main` fast-forwarded to `docs/readme-update` tip; no merge commit created.

*Case ID:* `merge-easy-cap-docs`

---

**E5 — Freelance: Land Completed Feature**

*Environment:* freelance

*Context:* `feature/contact-form` is complete and is a linear descendant of `main`.
You are on `main`. Merge it in — fast-forward is acceptable.

*Expected commands:*
```
git merge feature/contact-form
```

*Case ID:* `merge-easy-free-contact`

---

### New Medium variant (M4)

---

**M4 — Corporate: Merge Policy Requires Explicit Commit**

*Environment:* corporate

*Context:* `feature/sso-integration` is a linear descendant of `main` but your team's
policy requires an explicit merge commit for every feature branch to maintain a clear
audit trail. You are on `main`. Use `--no-ff`.

*Expected commands:*
```
git merge --no-ff feature/sso-integration
```

*Target state:* A merge commit exists on `main`; both parent commits visible in log.

*Case ID:* `merge-med-corp-sso`

---

### New Hard variant (H4)

---

**H4 — DevOps: Switch Target Branch + No-FF Merge**

*Environment:* devops

*Context:* You are on `feature/current-work`. `hotfix/cert-renewal` needs to be merged
into `release/stable` with an explicit merge commit (team policy). Switch to the target
branch, then merge with `--no-ff`.

*Expected commands:*
```
git switch release/stable
git merge --no-ff hotfix/cert-renewal
```

*Case ID:* `merge-hard-devops-cert`

---

## Lesson 8 (SO 2.8) — Squash Merging

**Approved SO:** SO 2.8 — Squash Merging | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Collapsing feature branch history into a single clean commit
**Primary commands:** `git merge --squash`, `git commit -m`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Squash WIP Commits Before Submission**

*Environment:* student-capstone

*Context:* `feature/report-generator` has 3 messy WIP commits your group accumulated
while iterating. Before submitting, your group lead wants a single clean commit on `main`.
You are on `main`. Squash-merge and commit with "Add report generator module".

*Expected commands:*
```
git merge --squash feature/report-generator
git commit -m "Add report generator module"
```

*Case ID:* `squash-easy-cap-report`

---

**E5 — Freelance: One Clean Commit for Client**

*Environment:* freelance

*Context:* `feature/payment-flow` has 4 intermediate commits with messages like
"wip", "fix again", "ok this time". Your client's repo policy is one commit per feature.
You are on `main`. Squash and commit with "Add payment flow".

*Expected commands:*
```
git merge --squash feature/payment-flow
git commit -m "Add payment flow"
```

*Case ID:* `squash-easy-free-payment`

---

### New Medium variant (M4)

---

**M4 — Corporate: Fetch Remote Feature Then Squash**

*Environment:* corporate

*Context:* A colleague's `feature/gdpr-export` branch is on the remote but hasn't been
fetched. Fetch it first, then squash-merge `origin/feature/gdpr-export` onto `main`
with the commit message "Add GDPR data export endpoint".

*Expected commands:*
```
git fetch origin
git merge --squash origin/feature/gdpr-export
git commit -m "Add GDPR data export endpoint"
```

*Case ID:* `squash-med-corp-gdpr`

---

### New Hard variant (H4)

---

**H4 — DevOps: Squash, Commit, and Clean Up Source Branch**

*Environment:* devops

*Context:* `feature/log-rotation` is complete with several intermediate commits.
Land it on `main` as a single commit ("Add log rotation configuration"), then delete
the source branch — it is no longer needed. You are on `main`.

*Expected commands:*
```
git merge --squash feature/log-rotation
git commit -m "Add log rotation configuration"
git branch -D feature/log-rotation
```

*Case ID:* `squash-hard-devops-log`

---

## Lesson 9 (SO 2.9) — Deleting and Recovering Remote Branches

**Approved SO:** SO 2.9 — Deleting and Recovering Remote Branches | **KPI:** CAR ≥ 70%
**Scenario skill focus:** Remote branch lifecycle management; pruning stale tracking refs
**Primary commands:** `git push origin --delete`, `git fetch --prune`

### Completion requirements
- Easy: 3 sessions (pool ≥ 5)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### New Easy variants (E4–E5)

---

**E4 — Student Capstone: Remove Merged Remote Branch**

*Environment:* student-capstone

*Context:* Your group merged `feature/group-auth` into main on GitHub yesterday. The remote
branch is still there. Remove it from `origin`.

*Expected commands:*
```
git push origin --delete feature/group-auth
```

*Case ID:* `rb-easy-cap-group`

---

**E5 — Corporate: Remove Completed Sprint Branch from Remote**

*Environment:* corporate

*Context:* Sprint 12's `feature/sprint12-compliance` branch was merged and closed in
your project tracker. Remove the remote branch.

*Expected commands:*
```
git push origin --delete feature/sprint12-compliance
```

*Case ID:* `rb-easy-corp-sprint`

---

### New Medium variant (M4)

---

**M4 — Freelance: Prune Deleted Client Branch**

*Environment:* freelance

*Context:* Your client deleted `feature/old-landing` from the remote — they no longer
need it. Your local remote tracking ref `origin/feature/old-landing` is now stale.
Run fetch with pruning to clean it up.

*Expected commands:*
```
git fetch --prune origin
```

*Target state:* `origin/feature/old-landing` tracking ref removed locally.

*Case ID:* `rb-med-free-prune`

---

### New Hard variant (H4)

---

**H4 — Open Source: Full Cleanup — Remote and Local**

*Environment:* open-source

*Context:* The OSS project maintainer merged your PR and the remote `feature/oss-contribution`
branch has been deleted on origin. You also have the local branch. Clean up completely:
delete the remote branch (it still shows in your tracking refs — prune it), then delete
your local copy.

*Expected commands:*
```
git fetch --prune origin
git branch -d feature/oss-contribution
```

*Target state:* `origin/feature/oss-contribution` tracking ref absent; local `feature/oss-contribution` absent.

*Case ID:* `rb-hard-oss-full`

---

## Seed Implementation Notes

### Case ID naming convention

Format: `{lesson-abbrev}-{difficulty}-{distinguishing-term}`

| Lesson | SO | Abbrev |
|--------|-----|--------|
| Lesson 1 — Branch Create | SO 2.1 | `bc` |
| Lesson 2 — Branch Naming | SO 2.2 | `bn` |
| Lesson 3 — Stash | SO 2.3 | `stash` |
| Lesson 4 — Push | SO 2.4 | `push` |
| Lesson 5 — Fetch/Pull | SO 2.5 | `fetch` / `pull` |
| Lesson 6 — Reconcile | SO 2.6 | `rec` |
| Lesson 7 — Merge | SO 2.7 | `merge` |
| Lesson 8 — Squash | SO 2.8 | `squash` |
| Lesson 9 — Remote Branch | SO 2.9 | `rb` |

Keep case IDs under 30 characters. The first 18 characters after slugification
must be unique within the scenario × difficulty pool.

**Existing seed uses `v2{lesson_number}{difficulty_letter}-{term}` format for the first 3 variants
per pool (e.g., `v21e-auth`, `v22m-on-feature`). New variants use the `{abbrev}-{difficulty}-{term}`
format. Both formats produce distinct 18-char slug tails — no collision with existing case IDs.**

### Pool sizes after redesign

All pools meet minimum sizing after adding the new variants:

| Lesson | Easy (need ≥5) | Medium (need ≥4) | Hard (need ≥4) |
|--------|----------------|------------------|----------------|
| L1 Branch Create | 5 ✅ | 4 ✅ | 4 ✅ |
| L2 Branch Naming | 5 ✅ | 4 ✅ | 4 ✅ |
| L3 Stash | 5 ✅ | 4 ✅ | 4 ✅ |
| L4 Push | 5 ✅ | 4 ✅ | 4 ✅ |
| L5 Fetch/Pull | 5 ✅ | 4 ✅ | 4 ✅ |
| L6 Reconcile | 5 ✅ | 4 ✅ | 4 ✅ |
| L7 Merge | 5 ✅ | 4 ✅ | 4 ✅ |
| L8 Squash | 5 ✅ | 4 ✅ | 4 ✅ |
| L9 Remote Branch | 5 ✅ | 4 ✅ | 4 ✅ |

### Context string requirement

Every case dict passed to the seed's case-builder helpers must include a `"context"` key
with a rich narrative paragraph. This is the same pattern established in Module 1.

**How it works in the seed:**

1. `student_context_template(kind)` must return `"story": "{{context}}"` for every kind
   (not a static string). Currently Module 2's template returns static strings — these
   must be replaced with the `{{context}}` placeholder before adding new variants.

2. Each case helper call (or raw case dict) must pass a `context=` keyword argument
   containing the narrative paragraph shown in the guide's *Context:* section for that
   variant. Example:

   ```python
   branch_case(
       case_id="bc-easy-capstone-db",
       context=(
           "Your group just initialized the capstone repo. The main branch has one commit "
           "(\"Initial project setup\"). Your group lead says: \"Before we start coding, "
           "everyone creates their own feature branch from main.\" Create "
           "`feature/database-models` and start working there."
       ),
       project="capstone-repo",
       new_branch="feature/database-models",
       ...
   )
   ```

3. The materializer substitutes `{{context}}` into the Scenario Brief shown to students.

**Migration checklist for the seed:**

- [ ] Change all `student_context_template` kinds to return `"story": "{{context}}"`
- [ ] Add `context` parameter to all case helper functions (`branch_case`, `stash_case`,
  `push_case`, `fetch_case`, `reconcile_case`, `merge_case`, `squash_case`, `rb_case`)
- [ ] Add `context=` string to all existing E1–E3/M1–M3/H1–H3 variants (use the
  narrative descriptions from the Existing Variants Inventory section above)
- [ ] Add `context=` string to all new E4–E5/M4/H4 variants (use the guide's *Context:* text)

### Conflict-free guarantee

All Module 2 scenarios are designed to produce **no merge conflicts**. Initial states
are constructed so that diverged histories always touch different files. Conflict resolution
is Module 3 scope.

### State-Based Evaluator

All scenarios in this module use `completion_type = "state_based"`.
The evaluator checks the final repository state, not the sequence of commands.
`skip_required_commands: True` is used throughout Module 2 (as in the existing seed) —
the evaluator does not require a specific command sequence, only the correct final state.

### `required_attempts` — no override

All Module 2 lessons use the defaults from `SESSION_COUNTS`:
- Easy: 3 sessions
- Medium: 2 sessions
- Hard: 2 sessions

No `required_attempts` override applies to any Module 2 lesson.

### Command count limits

From `DIFFICULTY_MAX_COUNTED_COMMANDS` (already applied via migration `0017`):
- Easy: max 12 counted commands
- Medium: max 10 counted commands
- Hard: max 8 counted commands

These limits are already in the DB for Module 2 and do not need to be re-applied.

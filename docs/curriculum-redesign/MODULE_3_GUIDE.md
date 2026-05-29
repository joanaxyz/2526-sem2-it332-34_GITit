# Module 3 — Scenario Design Guide

**Status: Implemented ✅**
**Last updated: 2026-05-29**

---

## Module Overview

**Title:** Conflict Resolution
**Chapters:** 6
**Lessons:** 8 (4 scenario-bearing, 2 concept-only, 1 diagnostic preview, 1 integration review)
**Target students:** BSIT 3rd-year, CIT-U — Module 2 completion assumed

---

## SO Audit

Source of truth: *GIT it! Final Proposal* and `docs/module-3.md`.

### Instructional SOs — redesign scope

These three SOs define the instructional content of Module 3. Every redesigned scenario
must trace back to one of these.

| SO | Approved Description | Maps to Seed Lessons | KPI |
|----|----------------------|----------------------|-----|
| SO 3.1 | What Causes Merge Conflicts / Resolving Conflicts Manually | Lessons 2, 3, 4 (identify, accept-side, resolve + abort) | CAR ≥ 70% |
| SO 3.2 | Using a Merge Tool | Lesson 5 (`use-merge-tool-workflow`) | CAR ≥ 70% |
| SO 3.3 | Cherry-Picking Commits | Lesson 7 (`cherry-pick-selected-commit`) | CAR ≥ 70% |

### KPI SOs — measurement only, not instructional objectives

| SO | Description | KPI | How it is measured |
|----|-------------|-----|--------------------|
| SO 3.4 | Conflict Resolution Rate | CAR ≥ 70% | Completion rate across SO 3.1–3.3 scenario lessons |
| SO 3.5 | Module-level performance | HLCR ≥ 70%, RTA applies, ARC ≤ 2, SCR ≥ 80% validity gate | Aggregated across all Module 3 sessions |

### Non-instructional lessons (concept-only, no scenario practice)

| Lesson | Title | Rationale |
|--------|-------|-----------|
| Lesson 3.2 — Reading Conflict Markers | Conceptual prep for Lesson 3.3 | No evaluable repository state transition — purely marker anatomy |
| Lesson 3.5 — Conflict Prevention Strategies | Strategic/conceptual | Prevention scenario is in Lesson 6 (fetch + compare workflow) |

### Diagnostic Preview lesson

| Lesson | Seed slug | Purpose |
|--------|-----------|---------|
| Lesson 1 — Diagnosing Conflict State | `diagnose-conflict-state` | Conflict diagnostics: `git status`, `git diff --ours/--theirs/--base`, `git diff --check`, `git ls-files -u`. Read-only; repository state must remain unchanged. |

This lesson has no direct SO — it is the Module 3 equivalent of Module 1's Guided Preview.
It teaches the diagnostic toolkit before students encounter live conflicts in Lessons 2–4.

### UI structure

Module 3 has a Diagnostic Preview card (Lesson 1) followed by 7 instructional lessons.

| UI display | Seed sort order | Slug | SO | Redesign |
|-----------|-----------------|------|----|---------|
| Lesson 1 (Diagnostic Preview) | 1 | `diagnosing-conflict-state` | — | ✅ |
| Lesson 2 | 2 | `what-causes-merge-conflicts` | SO 3.1 | ✅ |
| Lesson 3 | 3 | `reading-conflict-markers` | SO 3.1 | ✅ |
| Lesson 4 | 4 | `resolving-conflicts-manually` | SO 3.1 | ✅ |
| Lesson 5 | 5 | `using-a-merge-tool` | SO 3.2 | ✅ |
| Lesson 6 | 6 | `conflict-prevention-strategies` | — (prevention fetch workflow) | ✅ |
| Lesson 7 | 7 | `cherry-picking-commits` | SO 3.3 | ✅ |
| Lesson 8 | 8 | `conflict-resolution-review` | Integration | ✅ |

**SO mapping verdict:** All 3 instructional SOs are covered. SO 3.4 and SO 3.5 are KPI
indicators only. Lessons 3.2 (reading markers) and 3.5 (prevention strategies) are
concept-only per the approved curriculum doc and have no standalone scenario lesson.

---

## Curriculum Assumptions

| Item | Decision |
|------|----------|
| Module 2 prerequisite | All SO 2.1–2.9 skills (branching, stashing, push/pull, merge) are prior knowledge |
| `git checkout --ours/--theirs` | Used for conflict-side resolution — distinct from `git checkout -b` branch creation |
| `git merge --continue` | Valid alias for `git commit` to complete a merge — both are accepted in capstone |
| `git config --global merge.tool` | Required setup step in Lesson 5 — prior Git config knowledge assumed |
| Conflict-free guarantee | Lessons 1–2 use pre-merge states; Lessons 3–4 use pre-conflicted states (merge already run) |
| No cherry-pick conflicts | Cherry-pick scenarios in Lesson 7 are designed to be conflict-free — conflict cherry-picks are out of scope |
| No force-push scenarios | Module 3 has no remote-push recovery; that is Module 4 scope |
| `skip_required_commands` | Diagnostic Preview (Lesson 1) uses `repository_state_unchanged` rule — all other lessons are state-based |

---

## Seed Audit

### Current implementation status

The existing `seed_module3_scenarios.py` implements all 8 lessons. Pool sizes:

| Lesson | Slug | Easy | Medium | Hard | Total |
|--------|------|------|--------|------|-------|
| L1 Diagnostic Preview | `diagnose-conflict-state` | 3 | 2 | 2 | 7 |
| L2 Conflict Identification | `identify-merge-conflict-state` | 3 | 2 | 2 | 7 |
| L3 Accept Conflict Side | `accept-conflict-side` | 2 | 2 | 2 | 6 |
| L4a Manual Resolution | `resolve-conflicts-manually` | 3 | 3 | 2 | 8 |
| L4b Merge Abort | `abort-conflicted-merge` | 2 | 2 | 2 | 6 |
| L5 Merge Tool | `use-merge-tool-workflow` | 2 | 2 | 2 | 6 |
| L6 Prevention | `prevent-stale-conflict-merge` | 2 | 2 | 2 | 6 |
| L7 Cherry-Pick | `cherry-pick-selected-commit` | 3 | 3 | 2 | 8 |
| L8 Integration Review | `module3-integrated-conflict-workflow` | 2 | 2 | 2 | 6 |
| **Total** | | **22** | **21** | **18** | **60** |

### Pool sizing verdict

Per DESIGN_PRINCIPLES.md §5:

```
pool_size ≥ completion_requirement + 2
```

| Difficulty | Required sessions | Minimum pool | Current min | Gap |
|------------|-------------------|--------------|-------------|-----|
| Easy | 3 | 5 | 2 (L3, L4b, L5, L6, L8) | ⚠️ UNDERSIZED |
| Medium | 2 | 4 | 2 (multiple lessons) | ⚠️ UNDERSIZED |
| Hard | 2 | 4 | 2 (multiple lessons) | ⚠️ UNDERSIZED |

> ⚠️ **CRITICAL POOL SIZING GAP**
>
> Most Module 3 lesson pools are under the minimum. Required additions per lesson:
> - Easy: need ≥ 5 variants → currently 2 = need +3; currently 3 = need +2
> - Medium: need ≥ 4 variants → currently 2 = need +2; currently 3 = need +1
> - Hard: need ≥ 4 variants → currently 2 = need +2
>
> Exception: Lesson 1 (Diagnostic Preview) `required_attempts=1` per lesson context → pool ≥ 3.
> L1 Easy (3) meets this. L1 Medium (2) and L1 Hard (2) still need +2 each.

---

## Command Coverage Matrix

| Command | Lesson | Difficulty | Counted? |
|---------|--------|------------|----------|
| `git status` | L1–L8 all | All | ❌ Diagnostic |
| `git diff` | L1–L8 all | All | ❌ Diagnostic |
| `git diff --ours <path>` | L1, L3, L4 | All | ❌ Diagnostic |
| `git diff --theirs <path>` | L1, L3, L4 | All | ❌ Diagnostic |
| `git diff --base <path>` | L1 | Medium, Hard | ❌ Diagnostic |
| `git diff --check <path>` | L1, L4, L8 | Medium, Hard | ❌ Diagnostic |
| `git diff --staged` | L4 | Medium, Hard | ❌ Diagnostic |
| `git diff main..origin/branch` | L6 | All | ❌ Diagnostic |
| `git log --oneline --graph --all` | L2, L7, L8 | All | ❌ Diagnostic |
| `git ls-files -u` | L1, L3, L4 | All | ❌ Diagnostic |
| `git show <commit>` | L7 | Medium, Hard | ❌ Diagnostic |
| `git merge <branch>` | L2, L5, L8 | All | ✅ Counted |
| `git merge --abort` | L4b | All | ✅ Counted |
| `git merge --continue` | L8 | All | ✅ Counted |
| `git checkout --ours <path>` | L3 | Easy, Hard | ✅ Counted |
| `git checkout --theirs <path>` | L3 | Medium, Hard | ✅ Counted |
| `git add <path>` | L3, L4a, L5, L8 | All | ✅ Counted |
| `git commit` | L3, L4a, L5, L8 | All | ✅ Counted |
| `git config --global merge.tool <tool>` | L5, L8 | All | ✅ Counted |
| `git mergetool` | L5, L8 | All | ✅ Counted |
| `git fetch <remote>` | L6, L8 | All | ✅ Counted |
| `git cherry-pick <hash>` | L7, L8 | All | ✅ Counted |
| `git cherry-pick --no-commit <hash>` | L7 | Medium | ✅ Counted |
| `git cherry-pick --abort` | L7 | Hard | ✅ Counted |

---

## Difficulty Progression Philosophy

### Cognitive load per level

| Difficulty | What the student is given | What the student must infer |
|------------|--------------------------|----------------------------|
| Easy | Explicit branch names, conflict file named, resolution strategy stated | Nothing — the path is clear |
| Medium | Context and goal; conflict file identified but resolution approach is student's judgment | Which side to keep, how to combine, which diagnostic to run |
| Hard | Repository state only — branch names visible in DAG, no explicit guidance | Which file conflicts, what resolution preserves both branches' intent, which workflow step sequence |

### Module 3 specific: conflict-state reading

Module 3 adds a prerequisite cognitive demand not present in Modules 1–2: students must
*read a conflicted repository state* before acting. This means:

- Easy: repository is already in conflict state when the variant starts; the conflict file
  and resolution token are explicitly named in `student_context`
- Medium: conflict state is shown but the resolution strategy (keep ours / keep theirs /
  combine) is not stated — student reads the conflict and decides
- Hard: student may need to initiate the merge themselves (Lesson 2) or infer the correct
  resolution from the branch context without any hint

---

## Existing Variants Inventory

### Lesson 1 — Diagnostic Preview (`diagnose-conflict-state`)

3 Easy, 2 Medium, 2 Hard — **pool OK for required_attempts=1, but Medium and Hard need +2**

Base conflict cases (shared across lessons where applicable):
- `conflict-easy-auth-copy`: auth-service / src/auth.js / timeout conflict
- `conflict-easy-profile-copy`: profile-ui / src/profile.tsx / title conflict
- `conflict-easy-billing-copy`: billing-api / src/billing.py / currency conflict
- `conflict-medium-router`: support-portal / src/routes.ts / route conflict
- `conflict-medium-policy`: policy-engine / src/policy.yml / review policy conflict
- `conflict-hard-pricing`: pricing-service / src/pricing.rb / discount conflict
- `conflict-hard-schema`: warehouse-sync / schema/orders.sql / status type conflict

### Lesson 2 — Conflict Identification (`identify-merge-conflict-state`)

3 Easy (auth, profile, billing), 2 Medium (router, policy), 2 Hard (pricing, schema)
**All pools undersized for Easy (need +2), Medium (need +2), Hard (need +2)**

### Lesson 3 — Accept Conflict Side (`accept-conflict-side`)

2 Easy (`accept-ours`: auth, profile), 2 Medium (`accept-theirs`: router, policy),
2 Hard (ours=pricing, theirs=schema)
**All pools undersized: Easy need +3, Medium need +2, Hard need +2**

### Lesson 4a — Manual Resolution (`resolve-conflicts-manually`)

3 Easy (auth, profile, billing conflicted), 3 Medium (router, policy + auth re-used),
2 Hard (pricing, schema conflicted)
**Easy OK (need +2 → has 3; need ≥ 5 → undersized: need +2), Medium (need +1), Hard (need +2)**

### Lesson 4b — Merge Abort (`abort-conflicted-merge`)

2 Easy (auth, profile), 2 Medium (router, policy), 2 Hard (pricing, schema)
**All pools undersized: Easy need +3, Medium need +2, Hard need +2**

### Lesson 5 — Merge Tool (`use-merge-tool-workflow`)

2 Easy (auth+vscode, profile+vimdiff), 2 Medium (router+vscode, policy+vimdiff),
2 Hard (pricing+vscode, schema+vimdiff)
**All pools undersized: Easy need +3, Medium need +2, Hard need +2**

### Lesson 6 — Prevention (`prevent-stale-conflict-merge`)

2 Easy (docs-portal, api-contracts), 2 Medium (release-notes, design-system),
2 Hard (payments, search)
**All pools undersized: Easy need +3, Medium need +2, Hard need +2**

### Lesson 7 — Cherry-Pick (`cherry-pick-selected-commit`)

3 Easy (login-timeout, invoice-rounding, export-null), 3 Medium (login, invoice + no-commit report),
2 Hard (export-null commit + abort)
**Easy need +2, Medium need +1, Hard need +2**

### Lesson 8 — Integration Review (`module3-integrated-conflict-workflow`)

2 Easy (auth-service+vscode, profile-ui+vimdiff), 2 Medium (support-portal, policy-engine),
2 Hard (pricing-service, warehouse-sync)
**All pools undersized: Easy need +3, Medium need +2, Hard need +2**

---

## New Variants Required

To meet pool minimums (Easy ≥ 5, Medium ≥ 4, Hard ≥ 4; Diagnostic Preview ≥ 3 Easy, ≥ 4 Medium, ≥ 4 Hard):

### New base conflict cases (to add to seed)

These new cases feed multiple lessons (diagnostic, identification, resolution, abort, mergetool):

```
conflict-easy-config-copy:
  project: config-service
  conflict_path: src/config.py
  base_content: "debug=False"
  main_content: "debug=False\nlog_level=INFO"
  feature_content: "debug=True\nlog_level=DEBUG"
  resolution_content: "debug=False\nlog_level=INFO\nverbose_errors=True"
  resolution_token: "verbose_errors=True"
  source_branch: feature/debug-config

conflict-easy-navbar-copy:
  project: frontend-app
  conflict_path: src/components/Navbar.tsx
  base_content: "brand=AppName"
  main_content: "brand=MyApp"
  feature_content: "brand=BetaApp"
  resolution_content: "brand=MyApp\ntagline=Beta"
  resolution_token: "tagline=Beta"
  source_branch: feature/navbar-rebrand

conflict-medium-gateway:
  project: api-gateway
  conflict_path: config/gateway.yml
  base_content: "timeout: 30"
  main_content: "timeout: 60"
  feature_content: "timeout: 15"
  resolution_content: "timeout: 60\nretry_on_timeout: true"
  resolution_token: "retry_on_timeout: true"
  source_branch: feature/gateway-resilience

conflict-hard-migration:
  project: user-service
  conflict_path: db/migrations/001_users.sql
  base_content: "email text"
  main_content: "email text unique"
  feature_content: "email varchar(320)"
  resolution_content: "email varchar(320) unique"
  resolution_token: "varchar(320) unique"
  source_branch: feature/email-constraint
```

### New cherry-pick cases (Lesson 7)

```
cherry-easy-rate-limit:
  project: release-1.2
  target_branch: release/1.2
  source_commit: c1
  target_path: src/ratelimit.py
  expected_token: rate-limit-fix-v1
  answer_anchor: release branch receives rate limit patch as a new commit

cherry-easy-null-check:
  project: release-2.1
  target_branch: release/2.1
  source_commit: c1
  target_path: src/parser.ts
  expected_token: null-check-fix-v1
  answer_anchor: release branch receives null check patch as a new commit

cherry-medium-staged-review:
  project: release-staged
  target_branch: release/staged
  source_commit: c1
  target_path: src/cache.py
  expected_token: cache-hotfix
  answer_anchor: no-commit cherry-pick stages cache hotfix for review
  solution_commands: ["git cherry-pick --no-commit c1"]

cherry-hard-no-commit-finalize:
  project: release-finalize
  target_branch: release/finalize
  source_commit: c1
  target_path: src/queue.ts
  expected_token: queue-hotfix
  answer_anchor: cherry-pick applied and committed to release/finalize
```

### New prevention cases (Lesson 6)

```
prevent-easy-config-sync:
  project: config-sync
  target_branch: main / remote: origin / remote_branch: origin/main
  local_tip: c1 / remote_tip: c2
  watched_path: config/app.yml / remote_content: config-v2

prevent-easy-auth-tokens:
  project: auth-tokens
  target_branch: main / remote: origin / remote_branch: origin/main
  local_tip: c1 / remote_tip: c2
  watched_path: src/tokens.py / remote_content: tokens-v2

prevent-easy-ui-themes:
  project: ui-themes
  target_branch: main / remote: origin / remote_branch: origin/main
  local_tip: c1 / remote_tip: c2
  watched_path: styles/theme.css / remote_content: theme-v2

prevent-medium-db-schema:
  project: db-schema
  target_branch: main / remote: origin / remote_branch: origin/db-schema
  local_tip: c1 / remote_tip: c2
  watched_path: schema/users.sql / remote_content: schema-v2

prevent-medium-notifications:
  project: notifications
  target_branch: main / remote: origin / remote_branch: origin/notifications-v2
  local_tip: c1 / remote_tip: c2
  watched_path: src/notify.py / remote_content: notify-v2

prevent-hard-billing-reconcile:
  project: billing-reconcile
  target_branch: main / remote: origin / remote_branch: origin/billing-reconcile
  local_tip: c1 / remote_tip: c2
  watched_path: src/billing.py / remote_content: billing-v2

prevent-hard-infra-pipelines:
  project: infra-pipelines
  target_branch: main / remote: origin / remote_branch: origin/infra-pipelines
  local_tip: c1 / remote_tip: c2
  watched_path: .github/workflows/deploy.yml / remote_content: pipeline-v2
```

### New integration review cases (Lesson 8)

```
capstone-easy-config-hotfix:
  project: config-service
  conflict_path: src/config.py (uses conflict-easy-config-copy state)
  hotfix_path: src/feature_flags.py / hotfix_token: flags-hotfix-v1
  source_branch: origin/feature/debug-config / merge_tool: vscode

capstone-easy-navbar-hotfix:
  project: frontend-app
  conflict_path: src/components/Navbar.tsx (uses conflict-easy-navbar-copy state)
  hotfix_path: src/components/Footer.tsx / hotfix_token: footer-hotfix-v1
  source_branch: origin/feature/navbar-rebrand / merge_tool: vimdiff

capstone-easy-gateway-hotfix:
  project: api-gateway
  conflict_path: config/gateway.yml (uses conflict-medium-gateway state)
  hotfix_path: config/auth.yml / hotfix_token: auth-hotfix-v1
  source_branch: origin/feature/gateway-resilience / merge_tool: vscode

capstone-medium-gateway-hotfix:
  project: api-gateway (same as above, reused for medium difficulty)
  merge_tool: vimdiff

capstone-medium-migration-hotfix:
  project: user-service
  conflict_path: db/migrations/001_users.sql (uses conflict-hard-migration state)
  hotfix_path: db/migrations/002_indexes.sql / hotfix_token: index-hotfix-v1
  source_branch: origin/feature/email-constraint / merge_tool: vscode

capstone-hard-migration-hotfix:
  project: user-service (same conflict, harder difficulty)
  merge_tool: vimdiff
```

---

## Pool Sizing After New Variants

| Lesson | Easy (need ≥ 5) | Medium (need ≥ 4) | Hard (need ≥ 4) | Status |
|--------|-----------------|-------------------|-----------------|--------|
| L1 Diagnostic Preview (need Easy ≥ 3) | 3 + 2 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L2 Conflict Identification | 3 + 2 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L3 Accept Conflict Side | 2 + 3 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L4a Manual Resolution | 3 + 2 new = 5 | 3 + 1 new = 4 | 2 + 2 new = 4 | ✅ |
| L4b Merge Abort | 2 + 3 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L5 Merge Tool | 2 + 3 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L6 Prevention | 2 + 3 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |
| L7 Cherry-Pick | 3 + 2 new = 5 | 3 + 1 new = 4 | 2 + 2 new = 4 | ✅ |
| L8 Integration Review | 2 + 3 new = 5 | 2 + 2 new = 4 | 2 + 2 new = 4 | ✅ |

**New base conflict cases feed multiple lessons:** Each new `conflict_repo_case` contributes
variants to L1 (diagnostic), L2 (identification), L3 (accept-side), L4a (manual resolution),
L4b (merge abort), and L5 (mergetool). The new cherry-pick and prevention cases feed only
their respective lessons and L8 (capstone).

---

## Conflict-Free Guarantee

All new variants use conflict setups that produce exactly one conflicted file:
- New base cases each have one `conflict_path`
- `conflict_on_merge: True` is set only on that path
- No scenario crosses into two-file conflicts (out of scope for Module 3)
- Cherry-pick cases are authored to be conflict-free at the target branch

---

## Seed Implementation Notes

### What already exists (do not change)

- `student_context_template` kinds: `conflict-diagnostics`, `conflict-identification`,
  `manual-resolution`, `accept-ours`, `accept-theirs`, `merge-abort`, `mergetool`,
  `prevention`, `cherry-pick`, `cherry-pick-abort`, `capstone`
- All helper functions: `conflict_repo_case`, `conflicted_case`, `conflict_side_case`,
  `merge_abort_case`, `cherry_pick_case`, `prevention_case`, `capstone_case`
- `MODULE_THREE_LESSONS` list (8 entries)
- `DIAG_PATTERNS` (complete)
- All 9 scenario definitions and their target rules
- Case IDs for all existing 60 variants

### What needs adding

1. **4 new `conflict_repo_case` entries** in `easy_conflicts` and `medium_conflicts`/`hard_conflicts`
   pools (2 easy + 1 medium + 1 hard)

2. **Rebuild derived case lists** — `manual_easy`, `manual_medium`, `manual_hard`,
   `accept_ours_easy`, `accept_theirs_medium`, `accept_side_hard`, `merge_abort_easy`,
   `merge_abort_medium`, `merge_abort_hard`, `diagnostic_easy`, `diagnostic_medium`,
   `diagnostic_hard` — must include the new cases to reach pool minimums

3. **5 new `cherry_pick_case` entries** (2 easy + 1 medium for no-commit + 2 hard)

4. **7 new `prevention_case` entries** (3 easy + 2 medium + 2 hard)

5. **6 new `capstone_case` entries** (3 easy + 2 medium + 2 hard) using the new
   conflict repo cases as their base conflict scenarios

### Case ID naming

All case IDs for Module 3 use the existing prefix conventions below. New cases must
follow the same pattern and keep total case ID length ≤ 30 chars.

| Lesson | Prefix convention | Example |
|--------|------------------|---------|
| Base conflict cases | `conflict-{difficulty}-{domain}` | `conflict-easy-config-copy` |
| Cherry-pick | `cherry-{difficulty}-{domain}` | `cherry-easy-rate-limit` |
| Prevention | `prevent-{difficulty}-{domain}` | `prevent-easy-config-sync` |
| Capstone | `capstone-{difficulty}-{domain}` | `capstone-easy-config-hotfix` |

### Context string requirement

Every case dict passed to the seed's case-builder helpers must include a `"context"` key
with a rich narrative paragraph. This is the same pattern established in Module 1.

**How it works in the seed:**

1. `student_context_template(kind)` must return `"story": "{{context}}"` for every kind.
   Currently Module 3's templates return static strings — these must be replaced with the
   `{{context}}` placeholder before adding new variants.

2. Each case helper call must pass a `context=` keyword argument containing the narrative
   paragraph. Example for a conflict case:

   ```python
   conflict_repo_case(
       case_id="conflict-easy-config-copy",
       context=(
           "You're integrating a teammate's debug configuration changes into main. "
           "Both branches modified `src/config.py` — yours added a log level, "
           "theirs re-enabled debug mode. Git cannot auto-merge them."
       ),
       project="config-service",
       conflict_path="src/config.py",
       ...
   )
   ```

3. The materializer substitutes `{{context}}` into the Scenario Brief shown to students.

**Migration checklist for the seed:**

- [ ] Change all `student_context_template` kinds to return `"story": "{{context}}"`
- [ ] Add `context` parameter to all helper functions: `conflict_repo_case`,
  `conflicted_case`, `conflict_side_case`, `merge_abort_case`, `cherry_pick_case`,
  `prevention_case`, `capstone_case`
- [ ] Add `context=` string to all 60 existing variants
- [ ] Add `context=` string to all new variants using the guide's *Context:* text
  where available, or derive one from the variant's project/conflict/task description

### Target rules (no changes needed)

All existing target rules (`conflict_target`, `resolved_target`, `accept_side_target`,
`abort_merge_target`, `mergetool_target`, `cherry_target`, `cherry_no_commit_target`,
`cherry_abort_target`, `diagnostic_target`, `prevention_target`, `capstone_target`)
are correct and cover all new variants.

### `required_attempts` reference

| Lesson | Easy | Medium | Hard |
|--------|------|--------|------|
| L1 Diagnostic Preview | 3 (policy = `(0,1)`) | 2 | 2 |
| L2 Conflict Identification | 3 | 2 | 2 |
| L3 Accept Conflict Side | 2 | 2 | 2 |
| L4a Manual Resolution | 3 | 3 | 2 |
| L4b Merge Abort | 2 | 2 | 2 |
| L5 Merge Tool | 2 | 2 | 2 |
| L6 Prevention | 2 | 2 | 2 |
| L7 Cherry-Pick | 3 | 3 | 2 |
| L8 Integration Review | 2 | 2 | 2 |

---

## KPI SO Notes

**SO 3.4** (CAR ≥ 70%): Measured across Lessons 2, 3, 4, 5, 7 (scenario-bearing SO lessons).
Lesson 1 (Diagnostic Preview) and Lesson 6 (Prevention) contribute to overall engagement
but not directly to conflict-resolution CAR.

**SO 3.5**: SCR ≥ 80% validity gate — module KPI data is only reportable once 80%
of students have passed all scenario sessions. RTA applies from Module 3 onward —
structurally changed retry variants test genuine skill transfer, not repeat memory.

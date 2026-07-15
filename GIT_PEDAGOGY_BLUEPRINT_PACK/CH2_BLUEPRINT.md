<!--
GIT it! curriculum blueprint rebuilt from:
- CONTENT_AUTHORING_GUIDE.md
- CURRICULUM_AUTHORING_PLAN.md
- PRODUCT.md / DESIGN.md pedagogy

Authoring lens used here:
- Do not modularize by documentation chapter alone.
- Chapter = command-suite growth for a practical repository-state capability.
- Command Adventure = checklist-scaffolded fluency practice.
- Challenge = cumulative mastery proof through target DAG/state mutation.
- Ignore current command-engine gaps while authoring the ideal curriculum.
-->
# Chapter 2 Blueprint — Clean Snapshots and File Changes

**Chapter slug:** `tracking-changes-snapshots`

**Learning purpose:** Learners can shape exact snapshots from messy file changes, remove or untrack paths safely, amend local commits, and prove the tree/index/worktree are intentional.


## Pedagogy Contract for This Chapter

This chapter follows the product/content model exactly:

1. **Command Adventures teach.** They use modular, variant-safe objective checklists. No DAG target is required in adventures. A command may change the repository, but the scaffold is the checklist, not a target graph.
2. **Git-it Challenges assess.** Each challenge trial has no objective checklist. It is judged by repository state: DAG/refs, target tree, index, worktree, ignored files, stash/remote state where relevant.
3. **First exposure comes before workflow use.** A brand-new command form first appears in a small introduction scenario. Later workflow waves may reuse it.
4. **Commands repeat; scenarios do not.** Every command form appears in multiple distinct scenarios. The story/initial state must be unique across adventures and challenges.
5. **The command suite is cumulative.** Later chapters reuse earlier command forms inside workflows and challenges.
6. **Challenges always mutate the DAG.** Every easy/medium/hard trial creates, moves, removes, integrates, rewrites, or publishes commits/refs. Difficulty rises by graph/state complexity.

## Chapter Command-Suite Contract

By the end of this chapter, learners must be able to use the chapter's new forms plus prior forms to produce challenge-grade repository state changes. The challenge must not be solvable by command memorization alone; it must require reasoning about the target DAG/tree/index/worktree state.

## Spiral and Reuse Requirements

### New forms in this chapter

| Command form | Coverage rule | Why it belongs |
| --- | --- | --- |
| `git add -A` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git add -u` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git add -p` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git commit -a -m <message>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git commit --amend` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git commit --amend --no-edit` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git diff --name-only` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git rm <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git rm --cached <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git rm -r --cached <directory>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git restore <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git restore --staged <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |

### Returning forms from earlier chapters

`git status`, `git diff`, `git diff --staged`, `git add <file>`, `git add .`, `git commit -m`, `git log`, `git show`, `.gitignore / check-ignore`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Choose What Enters the Snapshot

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `stage-all-changes` | git add -A | Stage additions, modifications, and deletions across the project. | all tracked/untracked/deleted intended changes are staged |
| `stage-tracked-only` | git add -u | Stage modifications/deletions while leaving new files untracked. | tracked changes staged; new file remains untracked |
| `stage-selected-hunks` | git add -p | Stage only the useful hunk from a file containing mixed work. | only selected hunk appears in staged diff |
| `changed-paths-only` | git diff --name-only | List changed paths before choosing what to stage. | path inspection performed; later commit contains intended paths |

### Level 2: Fix Staging Mistakes

**Band:** Introductions plus workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `unstage-one-file` | git restore --staged <file> | Move a wrongly staged file back to the worktree. | wrong file no longer staged; work still exists |
| `discard-working-edit` | git restore <file> | Throw away a local debug edit before saving real work. | bad edit gone; intended work remains |
| `repair-before-commit` | status → restore --staged → restore → add -p → commit | Clean a mixed worktree and commit only the real fix. | latest commit contains only intended hunk; tree clean |

### Level 3: Remove or Stop Tracking Files

**Band:** Introductions plus workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `remove-tracked-file` | git rm <file> | Delete an obsolete tracked file and save the deletion. | latest commit excludes the file |
| `untrack-local-file` | git rm --cached <file> | Stop tracking a local config while keeping it on disk. | file absent from latest tree but present in working tree |
| `untrack-generated-directory` | git rm -r --cached <directory> | Stop tracking generated artifacts and protect them with .gitignore. | directory removed from tree; ignore rule committed |
| `cleanup-repo-workflow` | rm / rm --cached / .gitignore / add / commit | Clean a repo that accidentally tracked junk. | target tree contains source and ignore rules only |

### Level 4: Commit Faster and Amend Locally

**Band:** Introductions plus history repair workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `commit-tracked-directly` | git commit -a -m | Save tracked modifications without a separate add. | new commit contains tracked edits only |
| `amend-message-or-content` | git commit --amend | Fix the latest local commit before sharing. | latest commit replaced; corrected message/tree |
| `amend-without-message-change` | git commit --amend --no-edit | Add a forgotten file to the latest commit without changing the message. | latest commit tree updated; message preserved |
| `shape-two-snapshots` | add -p → commit → add -A → commit | Split messy work into two intentional commits. | two new commits with exact path separation |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T1 linear + exact tree | Commit only the intended change | repo with one real edit, one debug edit, one untracked scratch file | main advances by one commit; real edit only; scratch untracked or ignored; worktree clean except allowed scratch | `status`<br>`diff --name-only`<br>`restore`<br>`add <file> or add -p`<br>`commit -m` | Two variants: UI copy fix; config typo fix. |
| Medium | T1 rewrite latest local commit | Repair a bad latest snapshot | latest commit missing file and includes tracked generated file | same branch tip replaced by amended commit; generated file untracked/ignored; message correct | `rm --cached`<br>`.gitignore`<br>`add`<br>`commit --amend / --no-edit`<br>`log --oneline`<br>`show --name-only` | Two variants: build cache; local settings. |
| Hard | T1 multi-commit exact history | Split a messy workspace into clean commits | dirty worktree with additions, deletions, tracked edits, generated dir, partial hunk situation | main grows by two or three commits: cleanup, feature, tests/docs; exact target tree; index empty; worktree clean/allowed ignored only | `add -p`<br>`add -u`<br>`add -A`<br>`commit -a`<br>`rm`<br>`rm --cached`<br>`rm -r --cached`<br>`restore --staged`<br>`restore`<br>`diff --staged` | Two variants: web app cleanup; data pipeline cleanup. |

### Challenge evaluator contract

For every variant, author the contract using this shape:

```python
_contract(
    {
        "repository_initialized": True,
        "head_branch": "<expected>",
        "latest_commit": {"branch": "<branch>", "contains_paths": [...], "excludes_paths": [...]},
        "working_tree_clean": True,
        "staging_empty": True,
        "rules": [
            {"type": "commit_count_equals_or_delta", "value": "variant-specific"},
            {"type": "target_dag_matches", "graph": "variant-specific"},
        ],
    },
    required=[...],
    graph={"from": "...", "to": "..."},
    concepts=[...],
)
```

Reject attempts that only run the named command but leave the wrong branch, wrong tree, dirty index, dirty worktree, missing/extra remote ref, unresolved conflict, leaked ignored file, or unchanged DAG.

## Tome / Reading Blueprint

- The index as the next snapshot
- Choosing exact changes
- Tracked vs untracked vs ignored
- Amending only local history

## Authoring QA Checklist

- [ ] Every brand-new command form has a first-exposure scenario before being required inside a larger workflow.
- [ ] Every adventure checklist row is modular, variant-safe, and false on initial state / true on target state.
- [ ] Every workflow uses only previously introduced command forms plus current headline form.
- [ ] Every challenge trial mutates the DAG or refs and has a concrete target state.
- [ ] Easy → Medium → Hard increases graph/state complexity.
- [ ] The hard challenge uses near-full chapter suite plus relevant earlier forms.
- [ ] No challenge repeats an adventure scenario; only command forms repeat.
- [ ] Two variants exist per wave/trial with the same skill but different surface facts.
- [ ] The final state checks include tree, index, worktree, refs, and special surfaces such as ignored files/stash/remotes/conflicts where relevant.

## Scenario Ledger Seeds

These scenario IDs must be unique across the curriculum. Commands may repeat; scenario identity and initial state must not.

| Scenario ID | Kind | Container | Tier/Band | Unique state/task summary |
| --- | --- | --- | --- | --- |
| ch2-adv-stage-all-changes | adventure | Choose What Enters the Snapshot | intro | Stage additions, modifications, and deletions across the project. |
| ch2-adv-stage-tracked-only | adventure | Choose What Enters the Snapshot | intro | Stage modifications/deletions while leaving new files untracked. |
| ch2-adv-stage-selected-hunks | adventure | Choose What Enters the Snapshot | intro | Stage only the useful hunk from a file containing mixed work. |
| ch2-adv-changed-paths-only | adventure | Choose What Enters the Snapshot | intro | List changed paths before choosing what to stage. |
| ch2-adv-unstage-one-file | adventure | Fix Staging Mistakes | intro | Move a wrongly staged file back to the worktree. |
| ch2-adv-discard-working-edit | adventure | Fix Staging Mistakes | intro | Throw away a local debug edit before saving real work. |
| ch2-adv-repair-before-commit | adventure | Fix Staging Mistakes | intro | Clean a mixed worktree and commit only the real fix. |
| ch2-adv-remove-tracked-file | adventure | Remove or Stop Tracking Files | intro | Delete an obsolete tracked file and save the deletion. |
| ch2-adv-untrack-local-file | adventure | Remove or Stop Tracking Files | intro | Stop tracking a local config while keeping it on disk. |
| ch2-adv-untrack-generated-directory | adventure | Remove or Stop Tracking Files | intro | Stop tracking generated artifacts and protect them with .gitignore. |
| ch2-adv-cleanup-repo-workflow | adventure | Remove or Stop Tracking Files | intro | Clean a repo that accidentally tracked junk. |
| ch2-adv-commit-tracked-directly | adventure | Commit Faster and Amend Locally | intro | Save tracked modifications without a separate add. |
| ch2-adv-amend-message-or-content | adventure | Commit Faster and Amend Locally | intro | Fix the latest local commit before sharing. |
| ch2-adv-amend-without-message-change | adventure | Commit Faster and Amend Locally | intro | Add a forgotten file to the latest commit without changing the message. |
| ch2-adv-shape-two-snapshots | adventure | Commit Faster and Amend Locally | intro | Split messy work into two intentional commits. |
| ch2-challenge-easy | challenge | Commit only the intended change | T1 linear + exact tree | repo with one real edit, one debug edit, one untracked scratch file → main advances by one commit; real edit only; scratch untracked or ignored; worktree clean except allowed scratch |
| ch2-challenge-medium | challenge | Repair a bad latest snapshot | T1 rewrite latest local commit | latest commit missing file and includes tracked generated file → same branch tip replaced by amended commit; generated file untracked/ignored; message correct |
| ch2-challenge-hard | challenge | Split a messy workspace into clean commits | T1 multi-commit exact history | dirty worktree with additions, deletions, tracked edits, generated dir, partial hunk situation → main grows by two or three commits: cleanup, feature, tests/docs; exact target tree; index empty; worktree clean/allowed ignored only |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


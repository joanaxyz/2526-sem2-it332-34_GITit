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
# Chapter 3 Blueprint — Branching and Switching

**Chapter slug:** `branching-switching`

**Learning purpose:** Learners can create, inspect, switch, detach, recover, and delete branch pointers while keeping commits and working changes under control.


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
| `git branch` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git branch <name>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git branch <name> <start-point>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git branch -v` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git branch -d <name>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git branch -D <name>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git switch <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git switch -c <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git switch --detach <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git checkout -b <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |

### Returning forms from earlier chapters

`status`, `log --graph --all`, `show`, `diff`, `add / commit`, `restore`, `clean snapshot shaping from Ch2`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Create and Inspect Branches

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `list-branches` | git branch | List branches in a repo with main and feature refs. | branch list read; no mutation |
| `create-branch` | git branch <name> | Create a branch pointer without moving HEAD. | new branch points at current commit; HEAD unchanged |
| `create-branch-at-start` | git branch <name> <start-point> | Create a branch from an older or named commit. | new branch points at requested start point |
| `verbose-branches` | git branch -v | Compare branch tips before deciding where to work. | branch tip info inspected before commit workflow |

### Level 2: Move HEAD Safely

**Band:** Introductions plus save workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `switch-existing` | git switch <branch> | Move to an existing feature branch and make a commit there. | HEAD on feature; feature advances by one commit; main unchanged |
| `switch-create` | git switch -c <branch> | Create and switch, then commit isolated work. | new branch created and advanced; main unchanged |
| `checkout-legacy-create` | git checkout -b <branch> | Use legacy create-and-switch spelling then commit. | new branch exists with one commit |
| `inspect-detached` | git switch --detach <commit> | Inspect an old commit without moving branch refs. | HEAD detached; no branch ref moved unless rescue workflow follows |

### Level 3: Branch Workflows with Clean Snapshots

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `branch-for-feature` | status → switch -c → add -p → commit | Start a feature branch and commit only feature hunks. | feature branch ahead; clean tree |
| `branch-from-release` | branch <name> <start> → switch → commit | Create a hotfix branch from a release commit. | hotfix branch points to start then advances |
| `recover-detached-work` | switch --detach → commit → branch rescue <commit> → switch rescue | Save useful detached work onto a real branch. | rescue branch reaches detached commit |

### Level 4: Delete Branch Pointers Deliberately

**Band:** Introductions plus safety workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `delete-merged-branch` | git branch -d <name> | Delete a branch whose work is already reachable. | branch ref removed; commits still reachable from main |
| `force-delete-scratch-branch` | git branch -D <name> | Remove an abandoned experimental pointer after confirming it is disposable. | scratch ref removed; target branch unchanged |
| `branch-cleanup-workflow` | log --graph → branch -v → branch -d/-D | Clean old pointers after verifying reachability. | only requested branch refs remain |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T1 → T2 | Create an isolated feature branch | main has c0; worktree has feature file | main -> c0; feature -> c1; HEAD on feature or main as required; tree clean | `git switch -c or branch+switch`<br>`status`<br>`add`<br>`commit`<br>`log --graph` | Two variants: feature/ui; feature/docs. |
| Medium | T2 multi-branch | Start branches from different commits | linear history c0-c1-c2 with release needing hotfix from c1 and feature from c2 | hotfix branch from c1 advanced; feature branch from c2 advanced; main unchanged | `branch <name> <start-point>`<br>`switch`<br>`add -p`<br>`commit`<br>`branch -v` | Two variants: release patch; support patch. |
| Hard | T2 detached/recovery/cleanup | Recover detached work and clean branch pointers | repo with main, old experiment, detached inspection task, dirty work | rescued branch reaches new commit; disposable branch deleted; required branches remain; worktree clean | `switch --detach`<br>`commit`<br>`branch <name> <commit>`<br>`switch`<br>`branch -d`<br>`branch -D`<br>`log --graph --all` | Two variants: rescue docs; rescue fix. |

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

- Branches are movable pointers
- HEAD, attached and detached
- Creating branches from start points
- Deleting refs without deleting commits immediately

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
| ch3-adv-list-branches | adventure | Create and Inspect Branches | intro | List branches in a repo with main and feature refs. |
| ch3-adv-create-branch | adventure | Create and Inspect Branches | intro | Create a branch pointer without moving HEAD. |
| ch3-adv-create-branch-at-start | adventure | Create and Inspect Branches | intro | Create a branch from an older or named commit. |
| ch3-adv-verbose-branches | adventure | Create and Inspect Branches | intro | Compare branch tips before deciding where to work. |
| ch3-adv-switch-existing | adventure | Move HEAD Safely | intro | Move to an existing feature branch and make a commit there. |
| ch3-adv-switch-create | adventure | Move HEAD Safely | intro | Create and switch, then commit isolated work. |
| ch3-adv-checkout-legacy-create | adventure | Move HEAD Safely | intro | Use legacy create-and-switch spelling then commit. |
| ch3-adv-inspect-detached | adventure | Move HEAD Safely | intro | Inspect an old commit without moving branch refs. |
| ch3-adv-branch-for-feature | adventure | Branch Workflows with Clean Snapshots | workflow | Start a feature branch and commit only feature hunks. |
| ch3-adv-branch-from-release | adventure | Branch Workflows with Clean Snapshots | workflow | Create a hotfix branch from a release commit. |
| ch3-adv-recover-detached-work | adventure | Branch Workflows with Clean Snapshots | workflow | Save useful detached work onto a real branch. |
| ch3-adv-delete-merged-branch | adventure | Delete Branch Pointers Deliberately | intro | Delete a branch whose work is already reachable. |
| ch3-adv-force-delete-scratch-branch | adventure | Delete Branch Pointers Deliberately | intro | Remove an abandoned experimental pointer after confirming it is disposable. |
| ch3-adv-branch-cleanup-workflow | adventure | Delete Branch Pointers Deliberately | intro | Clean old pointers after verifying reachability. |
| ch3-challenge-easy | challenge | Create an isolated feature branch | T1 → T2 | main has c0; worktree has feature file → main -> c0; feature -> c1; HEAD on feature or main as required; tree clean |
| ch3-challenge-medium | challenge | Start branches from different commits | T2 multi-branch | linear history c0-c1-c2 with release needing hotfix from c1 and feature from c2 → hotfix branch from c1 advanced; feature branch from c2 advanced; main unchanged |
| ch3-challenge-hard | challenge | Recover detached work and clean branch pointers | T2 detached/recovery/cleanup | repo with main, old experiment, detached inspection task, dirty work → rescued branch reaches new commit; disposable branch deleted; required branches remain; worktree clean |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


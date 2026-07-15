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
# Chapter 6 Blueprint — Stashing and Cherry-Picking

**Chapter slug:** `temporary-work-patches`

**Learning purpose:** Learners can temporarily shelve uncommitted work, restore it deliberately, and move specific commits between branches without merging entire histories.


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
| `git stash` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git stash list` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git stash pop` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git stash apply` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git stash drop` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git cherry-pick <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git cherry-pick --no-commit <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git cherry-pick --abort` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |

### Returning forms from earlier chapters

`status`, `diff`, `add/commit`, `branch/switch`, `merge conflict inspection basics`, `restore`, `log --graph --all`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Shelve Local Work

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `stash-current-work` | git stash | Put unfinished local edits away before changing tasks. | worktree/index clean; stash entry exists |
| `list-stashes` | git stash list | Confirm what was shelved before restoring anything. | stash list inspected |
| `stash-before-switch` | status → stash → switch | Clean the worktree before switching branches. | on target branch; local WIP preserved in stash |

### Level 2: Restore Stashed Work

**Band:** Introductions plus workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `pop-stash` | git stash pop | Restore shelved work and remove the stash entry. | work restored; stash entry removed |
| `apply-stash` | git stash apply | Restore shelved work but keep the stash for reuse. | work restored; stash entry remains |
| `drop-stash` | git stash drop | Delete a stash after confirming it is no longer needed. | stash entry removed; worktree state as intended |
| `stash-restore-commit` | stash → switch → commit urgent fix → pop/apply → commit WIP | Handle interruption without losing work. | two branch histories correct; stash state correct |

### Level 3: Move One Commit

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `cherry-pick-one` | git cherry-pick <commit> | Apply one bugfix commit from another branch. | current branch advances by equivalent patch commit |
| `cherry-pick-no-commit` | git cherry-pick --no-commit <commit> | Bring a patch into staging so it can be combined with local edits. | picked changes staged/uncommitted |
| `abort-cherry-pick` | git cherry-pick --abort | Abort a conflicting or wrong cherry-pick. | repo returns to pre-pick state |

### Level 4: Patch Movement Workflows

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `pick-then-adjust` | cherry-pick --no-commit → edit → add → commit | Copy a fix and adapt it for the current branch. | single adapted commit on current branch |
| `stash-and-pick` | stash → cherry-pick → pop/apply → resolve/save | Move a commit while preserving local WIP. | target branch has picked commit and local WIP saved correctly |
| `abort-then-pick-right-commit` | cherry-pick wrong → abort → cherry-pick correct | Back out of an incorrect patch movement and apply the right one. | only correct patch appears in history |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T2/T3 local interruption | Stash WIP, commit urgent work, restore WIP | feature branch has uncommitted WIP; urgent branch needs one fix | urgent branch has new commit; WIP restored on original branch or committed as required; stash state correct | `status`<br>`stash`<br>`switch`<br>`add/commit`<br>`stash pop/apply` | Two variants: urgent docs; urgent bugfix. |
| Medium | T3 selective patch copy | Cherry-pick one needed fix | release branch lacks one fix that exists on development branch | release advances by cherry-picked commit; unrelated dev commits absent | `log --graph --all`<br>`show`<br>`switch`<br>`cherry-pick <commit>`<br>`status` | Two variants: security patch; typo patch. |
| Hard | T4 stash + cherry-pick no-commit + abort | Move and adapt a patch while preserving unfinished work | dirty branch, multiple candidate commits, one wrong candidate conflicts | wrong pick aborted; correct patch staged with --no-commit, adapted, committed; stash restored/dropped as specified; exact graph/tree | `stash`<br>`stash list`<br>`cherry-pick --abort`<br>`cherry-pick --no-commit`<br>`add -p`<br>`commit`<br>`stash apply/pop/drop`<br>`log --graph --all` | Two variants: release adaptation; docs backport. |

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

- Stash is temporary local storage
- Pop vs apply vs drop
- Cherry-pick copies a commit as a new commit
- Patch movement is not branch integration

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
| ch6-adv-stash-current-work | adventure | Shelve Local Work | intro | Put unfinished local edits away before changing tasks. |
| ch6-adv-list-stashes | adventure | Shelve Local Work | intro | Confirm what was shelved before restoring anything. |
| ch6-adv-stash-before-switch | adventure | Shelve Local Work | intro | Clean the worktree before switching branches. |
| ch6-adv-pop-stash | adventure | Restore Stashed Work | intro | Restore shelved work and remove the stash entry. |
| ch6-adv-apply-stash | adventure | Restore Stashed Work | intro | Restore shelved work but keep the stash for reuse. |
| ch6-adv-drop-stash | adventure | Restore Stashed Work | intro | Delete a stash after confirming it is no longer needed. |
| ch6-adv-stash-restore-commit | adventure | Restore Stashed Work | intro | Handle interruption without losing work. |
| ch6-adv-cherry-pick-one | adventure | Move One Commit | intro | Apply one bugfix commit from another branch. |
| ch6-adv-cherry-pick-no-commit | adventure | Move One Commit | intro | Bring a patch into staging so it can be combined with local edits. |
| ch6-adv-abort-cherry-pick | adventure | Move One Commit | intro | Abort a conflicting or wrong cherry-pick. |
| ch6-adv-pick-then-adjust | adventure | Patch Movement Workflows | workflow | Copy a fix and adapt it for the current branch. |
| ch6-adv-stash-and-pick | adventure | Patch Movement Workflows | workflow | Move a commit while preserving local WIP. |
| ch6-adv-abort-then-pick-right-commit | adventure | Patch Movement Workflows | workflow | Back out of an incorrect patch movement and apply the right one. |
| ch6-challenge-easy | challenge | Stash WIP, commit urgent work, restore WIP | T2/T3 local interruption | feature branch has uncommitted WIP; urgent branch needs one fix → urgent branch has new commit; WIP restored on original branch or committed as required; stash state correct |
| ch6-challenge-medium | challenge | Cherry-pick one needed fix | T3 selective patch copy | release branch lacks one fix that exists on development branch → release advances by cherry-picked commit; unrelated dev commits absent |
| ch6-challenge-hard | challenge | Move and adapt a patch while preserving unfinished work | T4 stash + cherry-pick no-commit + abort | dirty branch, multiple candidate commits, one wrong candidate conflicts → wrong pick aborted; correct patch staged with --no-commit, adapted, committed; stash restored/dropped as specified; exact graph/tree |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


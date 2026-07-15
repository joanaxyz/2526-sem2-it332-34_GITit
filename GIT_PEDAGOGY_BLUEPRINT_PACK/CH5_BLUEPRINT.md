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
# Chapter 5 Blueprint — Undoing and Recovery

**Chapter slug:** `undoing-recovery`

**Learning purpose:** Learners can decide when to move private history, when to add a public undo commit, and how to use reflog to recover from dangerous moves.


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
| `git reset --hard <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git reset --hard HEAD~1` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git revert <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git revert --no-edit <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git reflog` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |

### Returning forms from earlier chapters

`status`, `log --graph --all`, `show`, `branch/switch`, `merge basics`, `add/commit for follow-up fixes`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Read Recovery Clues

**Band:** Introduction

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `read-reflog` | git reflog | Inspect recent HEAD movements before choosing recovery. | reflog read; no mutation |

### Level 2: Move Private History Back

**Band:** Introductions plus safety checks

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `reset-hard-to-commit` | git reset --hard <commit> | Discard a private broken commit and return to a known good commit. | current branch points to target commit; tree matches target |
| `reset-hard-parent` | git reset --hard HEAD~1 | Drop exactly the latest private commit. | branch moves back one parent; worktree clean |
| `branch-before-reset` | branch backup → reset --hard | Make a safety pointer before rewriting local history. | backup branch preserves old tip; current branch reset |

### Level 3: Undo Shared Work Safely

**Band:** Introductions plus workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `revert-one-commit` | git revert <commit> | Undo an older public commit with a new commit. | new revert commit added; old commit remains in history |
| `revert-no-edit` | git revert --no-edit <commit> | Create a generated-message revert quickly. | new revert commit added; message auto/generated |
| `revert-then-fix` | revert → edit → add → commit | Back out a bad change then add a safer replacement. | two new commits: revert then replacement |

### Level 4: Recover After a Mistake

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `recover-lost-tip` | reflog → branch recovered <sha> → switch recovered | Find the lost commit after an accidental reset and anchor it. | recovered branch points to lost commit |
| `restore-main-from-reflog` | reflog → reset --hard <reflog-sha> | Move main back to a desired previous tip. | main restored to specified reflog entry |
| `choose-reset-or-revert` | log/show → reset or revert based on shared/private clue | Pick the correct undo strategy from scenario constraints. | target uses history rewrite only for private branch; public branch gets revert commit |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T3 branch ref moves back | Drop a private bad commit | private feature branch has one broken tip commit | feature branch points back to previous good commit; broken commit unreachable or only via backup if required; worktree clean | `log`<br>`show`<br>`branch backup optional`<br>`reset --hard HEAD~1` | Two variants: bad debug commit; bad generated commit. |
| Medium | T3 forward undo commit | Undo a public mistake without rewriting | main contains a bad commit that must remain auditable | main advances by one revert commit; old bad commit remains in ancestry | `log`<br>`show`<br>`revert --no-edit or revert`<br>`status` | Two variants: bad config; bad copy change. |
| Hard | T3 recovery + policy decision | Recover from accidental reset then undo safely | main or feature was reset to the wrong place; reflog contains lost tip; another bad shared commit needs revert | lost work anchored/restored; shared mistake undone by revert; private mistake reset; exact target graph | `reflog`<br>`branch <name> <sha>`<br>`reset --hard <commit>`<br>`revert <commit>`<br>`log --graph --all`<br>`status` | Two variants: release recovery; hotfix recovery. |

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

- Reset moves the branch; revert adds a commit
- Private vs shared history
- Reflog as local recovery map
- Safety branches before destructive moves

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
| ch5-adv-read-reflog | adventure | Read Recovery Clues | intro | Inspect recent HEAD movements before choosing recovery. |
| ch5-adv-reset-hard-to-commit | adventure | Move Private History Back | intro | Discard a private broken commit and return to a known good commit. |
| ch5-adv-reset-hard-parent | adventure | Move Private History Back | intro | Drop exactly the latest private commit. |
| ch5-adv-branch-before-reset | adventure | Move Private History Back | intro | Make a safety pointer before rewriting local history. |
| ch5-adv-revert-one-commit | adventure | Undo Shared Work Safely | intro | Undo an older public commit with a new commit. |
| ch5-adv-revert-no-edit | adventure | Undo Shared Work Safely | intro | Create a generated-message revert quickly. |
| ch5-adv-revert-then-fix | adventure | Undo Shared Work Safely | intro | Back out a bad change then add a safer replacement. |
| ch5-adv-recover-lost-tip | adventure | Recover After a Mistake | workflow | Find the lost commit after an accidental reset and anchor it. |
| ch5-adv-restore-main-from-reflog | adventure | Recover After a Mistake | workflow | Move main back to a desired previous tip. |
| ch5-adv-choose-reset-or-revert | adventure | Recover After a Mistake | workflow | Pick the correct undo strategy from scenario constraints. |
| ch5-challenge-easy | challenge | Drop a private bad commit | T3 branch ref moves back | private feature branch has one broken tip commit → feature branch points back to previous good commit; broken commit unreachable or only via backup if required; worktree clean |
| ch5-challenge-medium | challenge | Undo a public mistake without rewriting | T3 forward undo commit | main contains a bad commit that must remain auditable → main advances by one revert commit; old bad commit remains in ancestry |
| ch5-challenge-hard | challenge | Recover from accidental reset then undo safely | T3 recovery + policy decision | main or feature was reset to the wrong place; reflog contains lost tip; another bad shared commit needs revert → lost work anchored/restored; shared mistake undone by revert; private mistake reset; exact target graph |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


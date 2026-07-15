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
# Chapter 4 Blueprint — Merging and Conflict Resolution

**Chapter slug:** `merging-conflicts`

**Learning purpose:** Learners can combine divergent branches, inspect common ancestors and conflict stages, abort bad merges, and finish resolved merges with exact content.


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
| `git merge <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git merge --no-ff <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git merge --squash <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git merge --abort` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git merge --continue` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git merge-base <ref-a> <ref-b>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git checkout --ours <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git checkout --theirs <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git diff --ours <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git diff --theirs <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git diff --base <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git ls-files -u` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git mergetool` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |

### Returning forms from earlier chapters

`status`, `log --graph --all`, `branch/switch`, `add/commit`, `restore`, `diff`, `clean snapshot shaping`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Understand Merge Shape

**Band:** Introductions plus visual inspection workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `find-merge-base` | git merge-base <a> <b> | Find where two branches diverged before merging. | common ancestor identified before merge workflow |
| `merge-fast-forward` | git merge <branch> | Bring main forward when feature is directly ahead. | main ref advances to feature tip; no merge commit required |
| `merge-no-ff` | git merge --no-ff <branch> | Preserve feature branch history with a merge commit. | merge commit has two parents |
| `merge-squash` | git merge --squash <branch> | Stage feature work as one clean snapshot then commit. | single squashed commit added; feature commits not parents |

### Level 2: Abort and Retry

**Band:** Introduction plus workflow

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `abort-conflicted-merge` | git merge --abort | Start the wrong conflicted merge, then abort back to clean state. | repo returns to pre-merge HEAD and clean worktree |
| `retry-correct-merge` | merge --abort → switch → merge correct branch | Abort the wrong merge then merge the intended branch. | target branch contains intended integration only |

### Level 3: Inspect Conflict State

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `list-unmerged-files` | git ls-files -u | List unmerged index entries during conflict. | unmerged entries inspected |
| `diff-conflict-base` | git diff --base <file> | See conflict file relative to base. | base-side diff inspected before resolution |
| `diff-conflict-ours-theirs` | git diff --ours/--theirs <file> | Compare both sides before choosing resolution. | both side diffs inspected |
| `launch-mergetool` | git mergetool | Use a configured tool to resolve a simple text conflict. | conflict resolved and staged |

### Level 4: Resolve Conflicts and Finish

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `take-ours` | git checkout --ours <file> | Choose current branch side for a generated conflict file. | file content equals ours; staged; merge completed |
| `take-theirs` | git checkout --theirs <file> | Choose incoming side for a generated conflict file. | file content equals theirs; staged; merge completed |
| `manual-mixed-resolution` | ls-files -u → diff sides → edit → add → merge --continue | Resolve a conflict by combining both sides. | merge commit tree contains combined content |
| `two-file-conflict-workflow` | ours for one file + manual edit for another + continue | Resolve a realistic two-file conflict. | merge commit exact tree; no conflict markers |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T2 fast-forward/ref movement | Integrate a completed feature | main behind feature with no divergence | main points to feature tip; feature may remain; worktree clean | `merge <branch>`<br>`log --graph`<br>`status` | Two variants: docs feature; style feature. |
| Medium | T3 explicit merge commit/squash | Choose the right integration style | main and feature diverged; product asks preserve history or squash | target has either two-parent merge commit or single squash commit as specified | `merge-base`<br>`merge --no-ff or --squash`<br>`add/commit for squash`<br>`branch -d after merge` | Two variants: preserve plugin branch; squash experimental branch. |
| Hard | T3 conflict resolution | Resolve divergent edits correctly | main and feature conflict in one or more files; extra wrong branch can cause abort path | merge commit with exact resolved content; no conflict markers; index/worktree clean; optional branch cleanup | `merge`<br>`merge --abort`<br>`merge-base`<br>`ls-files -u`<br>`diff --base/--ours/--theirs`<br>`checkout --ours/--theirs`<br>`mergetool or manual edit`<br>`add`<br>`merge --continue` | Two variants: route table conflict; config conflict. |

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

- Fast-forward vs merge commit vs squash
- What conflict stages mean
- Ours/theirs from the current branch perspective
- Finishing a merge is a staging problem too

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
| ch4-adv-find-merge-base | adventure | Understand Merge Shape | intro | Find where two branches diverged before merging. |
| ch4-adv-merge-fast-forward | adventure | Understand Merge Shape | intro | Bring main forward when feature is directly ahead. |
| ch4-adv-merge-no-ff | adventure | Understand Merge Shape | intro | Preserve feature branch history with a merge commit. |
| ch4-adv-merge-squash | adventure | Understand Merge Shape | intro | Stage feature work as one clean snapshot then commit. |
| ch4-adv-abort-conflicted-merge | adventure | Abort and Retry | intro | Start the wrong conflicted merge, then abort back to clean state. |
| ch4-adv-retry-correct-merge | adventure | Abort and Retry | intro | Abort the wrong merge then merge the intended branch. |
| ch4-adv-list-unmerged-files | adventure | Inspect Conflict State | intro | List unmerged index entries during conflict. |
| ch4-adv-diff-conflict-base | adventure | Inspect Conflict State | intro | See conflict file relative to base. |
| ch4-adv-diff-conflict-ours-theirs | adventure | Inspect Conflict State | intro | Compare both sides before choosing resolution. |
| ch4-adv-launch-mergetool | adventure | Inspect Conflict State | intro | Use a configured tool to resolve a simple text conflict. |
| ch4-adv-take-ours | adventure | Resolve Conflicts and Finish | workflow | Choose current branch side for a generated conflict file. |
| ch4-adv-take-theirs | adventure | Resolve Conflicts and Finish | workflow | Choose incoming side for a generated conflict file. |
| ch4-adv-manual-mixed-resolution | adventure | Resolve Conflicts and Finish | workflow | Resolve a conflict by combining both sides. |
| ch4-adv-two-file-conflict-workflow | adventure | Resolve Conflicts and Finish | workflow | Resolve a realistic two-file conflict. |
| ch4-challenge-easy | challenge | Integrate a completed feature | T2 fast-forward/ref movement | main behind feature with no divergence → main points to feature tip; feature may remain; worktree clean |
| ch4-challenge-medium | challenge | Choose the right integration style | T3 explicit merge commit/squash | main and feature diverged; product asks preserve history or squash → target has either two-parent merge commit or single squash commit as specified |
| ch4-challenge-hard | challenge | Resolve divergent edits correctly | T3 conflict resolution | main and feature conflict in one or more files; extra wrong branch can cause abort path → merge commit with exact resolved content; no conflict markers; index/worktree clean; optional branch cleanup |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


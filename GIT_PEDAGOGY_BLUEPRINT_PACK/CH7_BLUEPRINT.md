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
# Chapter 7 Blueprint — Remote Collaboration

**Chapter slug:** `remotes-collaboration`

**Learning purpose:** Learners can inspect remotes, fetch before integrating, pull correctly, publish branches, update shared history safely, and clean stale remote branches.


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
| `git remote` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects remote configuration |
| `git remote -v` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects remote configuration |
| `git fetch origin` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git fetch --prune` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git pull` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git pull --rebase` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git push -u origin <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git push` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git push --force-with-lease` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git push origin --delete <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |

### Returning forms from earlier chapters

`clone`, `status`, `log --graph --all`, `branch/switch`, `add/commit`, `merge/conflict resolution`, `reset/revert policy`, `stash/cherry-pick`

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Inspect Remote Setup

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `list-remotes` | git remote | List configured remote names before sharing work. | remote names inspected |
| `list-remote-urls` | git remote -v | Verify fetch/push URLs before publishing. | remote URLs inspected |
| `remote-inspection-workflow` | remote -v → log --graph --all → status | Diagnose where local and remote refs currently stand. | no mutation; state understood before next action |

### Level 2: Fetch Before Acting

**Band:** Introductions plus workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `fetch-origin` | git fetch origin | Update remote-tracking refs without touching local work. | origin/* refs updated; local branch unchanged |
| `fetch-prune` | git fetch --prune | Remove stale remote-tracking refs after a branch was deleted remotely. | stale tracking ref gone |
| `fetch-then-branch` | fetch → branch <name> origin/<branch> → switch | Start local work from a fetched remote branch. | local branch created from remote-tracking tip |

### Level 3: Pull and Integrate

**Band:** Introductions plus conflict-aware workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `pull-default` | git pull | Bring upstream changes into a clean local branch. | local branch integrates upstream change |
| `pull-rebase` | git pull --rebase | Replay local commits on top of updated upstream. | local commits rewritten on top of remote tip |
| `pull-with-local-work-safe` | stash → pull/rebase → pop/apply | Protect local WIP before synchronizing. | local history synchronized; WIP restored or committed |

### Level 4: Publish Work

**Band:** Introductions plus cumulative workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `push-set-upstream` | git push -u origin <branch> | Publish a new branch and set tracking. | remote branch exists; upstream set |
| `push-current` | git push | Publish additional commits on a tracked branch. | remote branch advances to local tip |
| `force-with-lease` | git push --force-with-lease | Publish a deliberate local rewrite only if the remote is unchanged since fetch. | remote branch updates to rewritten local tip under lease condition |
| `delete-remote-branch` | git push origin --delete <branch> | Remove a remote branch after merged/abandoned work. | remote branch deleted; local state sane |

### Level 5: Full Collaboration Loops

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `branch-publish-merge-cleanup` | fetch → switch -c → commit → push -u → simulate merge → fetch --prune | Complete a feature branch lifecycle. | remote/local refs match expected lifecycle |
| `sync-diverged-work` | fetch → pull --rebase → resolve/save → push | Synchronize local work after teammate advanced remote. | remote receives rebased local commits on top of teammate work |
| `rewrite-and-lease` | fetch → amend/reset local → push --force-with-lease | Safely publish a corrected branch after local rewrite. | remote tip equals corrected commit; stale lease rejected in alternate variant |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T4 remote branch creation | Publish a new feature branch | local repo cloned from origin/main; learner must create branch and commit work | origin/feature exists at local feature tip; upstream configured; main unchanged | `remote -v`<br>`switch -c`<br>`add/commit`<br>`push -u origin <branch>` | Two variants: feature/docs; feature/test. |
| Medium | T4 fetch/pull/push loop | Sync before publishing | origin/main has new teammate commit; local branch has one local commit | local integrates upstream; remote advances to local integrated tip; worktree clean | `fetch origin`<br>`log --graph --all`<br>`pull or pull --rebase`<br>`push` | Two variants: non-conflicting pull; rebase-required policy. |
| Hard | T4 diverged collaboration lifecycle | Recover, rebase, publish safely, delete stale branch | remote branch diverged; local branch has corrected history; stale remote branch exists; optional conflict | local commits replayed/integrated; remote tip updated with force-with-lease only after fetch; stale remote branch deleted; exact graph/remote refs | `remote -v`<br>`fetch --prune`<br>`pull --rebase`<br>`status`<br>`diff conflict tools if needed`<br>`add/commit or merge continue`<br>`push --force-with-lease`<br>`push origin --delete` | Two variants: release branch rewrite; stale feature cleanup. |

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

- Local refs vs remote-tracking refs vs remote refs
- Fetch does not integrate
- Pull integrates; rebase changes commit IDs
- Pushing, upstreams, and force-with-lease safety

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
| ch7-adv-list-remotes | adventure | Inspect Remote Setup | intro | List configured remote names before sharing work. |
| ch7-adv-list-remote-urls | adventure | Inspect Remote Setup | intro | Verify fetch/push URLs before publishing. |
| ch7-adv-remote-inspection-workflow | adventure | Inspect Remote Setup | intro | Diagnose where local and remote refs currently stand. |
| ch7-adv-fetch-origin | adventure | Fetch Before Acting | intro | Update remote-tracking refs without touching local work. |
| ch7-adv-fetch-prune | adventure | Fetch Before Acting | intro | Remove stale remote-tracking refs after a branch was deleted remotely. |
| ch7-adv-fetch-then-branch | adventure | Fetch Before Acting | intro | Start local work from a fetched remote branch. |
| ch7-adv-pull-default | adventure | Pull and Integrate | intro | Bring upstream changes into a clean local branch. |
| ch7-adv-pull-rebase | adventure | Pull and Integrate | intro | Replay local commits on top of updated upstream. |
| ch7-adv-pull-with-local-work-safe | adventure | Pull and Integrate | intro | Protect local WIP before synchronizing. |
| ch7-adv-push-set-upstream | adventure | Publish Work | intro | Publish a new branch and set tracking. |
| ch7-adv-push-current | adventure | Publish Work | intro | Publish additional commits on a tracked branch. |
| ch7-adv-force-with-lease | adventure | Publish Work | intro | Publish a deliberate local rewrite only if the remote is unchanged since fetch. |
| ch7-adv-delete-remote-branch | adventure | Publish Work | intro | Remove a remote branch after merged/abandoned work. |
| ch7-adv-branch-publish-merge-cleanup | adventure | Full Collaboration Loops | workflow | Complete a feature branch lifecycle. |
| ch7-adv-sync-diverged-work | adventure | Full Collaboration Loops | workflow | Synchronize local work after teammate advanced remote. |
| ch7-adv-rewrite-and-lease | adventure | Full Collaboration Loops | workflow | Safely publish a corrected branch after local rewrite. |
| ch7-challenge-easy | challenge | Publish a new feature branch | T4 remote branch creation | local repo cloned from origin/main; learner must create branch and commit work → origin/feature exists at local feature tip; upstream configured; main unchanged |
| ch7-challenge-medium | challenge | Sync before publishing | T4 fetch/pull/push loop | origin/main has new teammate commit; local branch has one local commit → local integrates upstream; remote advances to local integrated tip; worktree clean |
| ch7-challenge-hard | challenge | Recover, rebase, publish safely, delete stale branch | T4 diverged collaboration lifecycle | remote branch diverged; local branch has corrected history; stale remote branch exists; optional conflict → local commits replayed/integrated; remote tip updated with force-with-lease only after fetch; stale remote branch deleted; exact graph/remote refs |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


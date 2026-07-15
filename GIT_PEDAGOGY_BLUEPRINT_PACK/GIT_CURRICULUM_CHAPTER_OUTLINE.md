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
# Git Curriculum Chapter Outline — Pedagogy-First Blueprint

This outline is not a Git documentation table. It is a cumulative command-suite plan for GIT it!'s two-part learning model: Command Adventures build checklist-guided command fluency; Git-it Challenges prove that the accumulated suite can transform a repository into a meaningful target DAG/state.


## Pedagogy Contract for This Chapter

This chapter follows the product/content model exactly:

1. **Command Adventures teach.** They use modular, variant-safe objective checklists. No DAG target is required in adventures. A command may change the repository, but the scaffold is the checklist, not a target graph.
2. **Git-it Challenges assess.** Each challenge trial has no objective checklist. It is judged by repository state: DAG/refs, target tree, index, worktree, ignored files, stash/remote state where relevant.
3. **First exposure comes before workflow use.** A brand-new command form first appears in a small introduction scenario. Later workflow waves may reuse it.
4. **Commands repeat; scenarios do not.** Every command form appears in multiple distinct scenarios. The story/initial state must be unique across adventures and challenges.
5. **The command suite is cumulative.** Later chapters reuse earlier command forms inside workflows and challenges.
6. **Challenges always mutate the DAG.** Every easy/medium/hard trial creates, moves, removes, integrates, rewrites, or publishes commits/refs. Difficulty rises by graph/state complexity.

## Plain Chapter Sequence

| Ch | Plain name | Slug | Capability built | Suite size | Top DAG band |
| --- | --- | --- | --- | --- | --- |
| 1 | Repository Foundations | creating-inspecting-repositories | Learners can create or clone a repository, inspect its state/history, configure identity, ignore noise, and create meaningful first commits. | 30 new forms | T0–T1 |
| 2 | Clean Snapshots and File Changes | tracking-changes-snapshots | Learners can shape exact snapshots from messy file changes, remove or untrack paths safely, amend local commits, and prove the tree/index/worktree are intentional. | 12 new forms | T1 |
| 3 | Branching and Switching | branching-switching | Learners can create, inspect, switch, detach, recover, and delete branch pointers while keeping commits and working changes under control. | 10 new forms | T2 |
| 4 | Merging and Conflict Resolution | merging-conflicts | Learners can combine divergent branches, inspect common ancestors and conflict stages, abort bad merges, and finish resolved merges with exact content. | 13 new forms | T3 |
| 5 | Undoing and Recovery | undoing-recovery | Learners can decide when to move private history, when to add a public undo commit, and how to use reflog to recover from dangerous moves. | 5 new forms | T3 |
| 6 | Stashing and Cherry-Picking | temporary-work-patches | Learners can temporarily shelve uncommitted work, restore it deliberately, and move specific commits between branches without merging entire histories. | 8 new forms | T3 |
| 7 | Remote Collaboration | remotes-collaboration | Learners can inspect remotes, fetch before integrating, pull correctly, publish branches, update shared history safely, and clean stale remote branches. | 10 new forms | T4 |

## Cross-Chapter Spiral

| Ch | Chapter | Prior forms intentionally reused | Challenge requirement |
| --- | --- | --- | --- |
| 1 | Repository Foundations | none | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 2 | Clean Snapshots and File Changes | `git status`, `git diff`, `git diff --staged`, `git add <file>`, `git add .`, `git commit -m`, `git log`, `git show` ... | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 3 | Branching and Switching | `status`, `log --graph --all`, `show`, `diff`, `add / commit`, `restore`, `clean snapshot shaping from Ch2` | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 4 | Merging and Conflict Resolution | `status`, `log --graph --all`, `branch/switch`, `add/commit`, `restore`, `diff`, `clean snapshot shaping` | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 5 | Undoing and Recovery | `status`, `log --graph --all`, `show`, `branch/switch`, `merge basics`, `add/commit for follow-up fixes` | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 6 | Stashing and Cherry-Picking | `status`, `diff`, `add/commit`, `branch/switch`, `merge conflict inspection basics`, `restore`, `log --graph --all` | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |
| 7 | Remote Collaboration | `clone`, `status`, `log --graph --all`, `branch/switch`, `add/commit`, `merge/conflict resolution`, `reset/revert policy`, `stash/cherry-pick` | Hard trial must use current chapter forms plus earlier forms that are naturally needed for the state transformation. |

## Challenge DAG Ladder

| Tier | Shape | Where used |
| --- | --- | --- |
| T0 | Uninitialized/config/clone setup; no meaningful graph yet | Ch1 adventure intros only; Ch1 challenges quickly move to T1 |
| T1 | Linear history growth; exact tree/index/worktree checks | Ch1–Ch2 |
| T2 | Multiple local refs; branch creation/switching/detached rescue | Ch3 and later reuse |
| T3 | Divergence, merge commits, conflicts, reset/revert/recovery, stash/pick local flows | Ch4–Ch6 |
| T4 | Remote-tracking refs, diverged local/remote state, collaboration lifecycle | Ch7 |

## Required files generated by this pack

- `CH1_BLUEPRINT.md` — Repository Foundations
- `CH2_BLUEPRINT.md` — Clean Snapshots and File Changes
- `CH3_BLUEPRINT.md` — Branching and Switching
- `CH4_BLUEPRINT.md` — Merging and Conflict Resolution
- `CH5_BLUEPRINT.md` — Undoing and Recovery
- `CH6_BLUEPRINT.md` — Stashing and Cherry-Picking
- `CH7_BLUEPRINT.md` — Remote Collaboration


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


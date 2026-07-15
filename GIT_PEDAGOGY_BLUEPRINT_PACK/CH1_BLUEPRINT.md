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
# Chapter 1 Blueprint — Repository Foundations

**Chapter slug:** `creating-inspecting-repositories`

**Learning purpose:** Learners can create or clone a repository, inspect its state/history, configure identity, ignore noise, and create meaningful first commits.


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
| `git init` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git init <directory>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git init -b <branch>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git clone <url>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git clone <url> <folder>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git clone -b <branch> <url>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git clone --depth <n> <url>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git status` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git status -s` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git status --porcelain` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git status --ignored` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git config --global user.name <name>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git config --global user.email <email>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git config --list` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git config --global alias.<name> <command>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git log --oneline` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git log --oneline --graph --all` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git log -n <count>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git log -p` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git log --stat` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git show` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git show <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git show --name-only <commit>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git diff` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git diff --staged` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `git add <file>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git add .` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git commit -m <message>` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates repository state, refs, index, worktree, stash, config, or remote state |
| `git check-ignore -v <path>` | intro/headline wave, then ≥2 workflow/challenge reuses | inspects state or verifies target choice |
| `.gitignore authoring patterns` | intro/headline wave, then ≥2 workflow/challenge reuses | mutates future tracking behavior when committed |

### Returning forms from earlier chapters

None; this is the foundation chapter.

### Production coverage rule

- Each new command form must appear in at least one intro wave unless it is naturally introduced as the headline of a workflow where all supporting commands are already known.
- Each new form must be reused in at least two later scenarios: another adventure workflow, a challenge trial, or both.
- Earlier forms must appear as real work, not decoration. Example: `git status` must be followed by a decision; `git log --graph --all` must inform branch/ref choice; `git diff` must inform staging/resolution.

## Command Adventure Blueprint

The adventure uses **objective checklists only**. Intro waves isolate first exposure. Workflow waves reuse already-introduced forms. The same command form should appear in at least three distinct scenarios across adventure + challenge coverage.

### Level 1: Start a Repository

**Band:** Introductions

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `init-current-folder` | git init | Turn a folder with starter files into a Git repository. | repository_initialized true |
| `init-named-folder` | git init <directory> | Create a named project folder as a repository. | new repo folder exists and is initialized |
| `init-first-branch` | git init -b <branch> | Start a repository with the requested first branch name. | head branch equals requested branch |

### Level 2: Read Repository State

**Band:** Introductions then small action

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `status-plain` | git status | Inspect a repo with one dirty or untracked file. | status command used; no mutation expected |
| `stage-one-file` | git add <file> | Stage exactly one file from a dirty worktree. | selected file staged; unrelated file remains unstaged if present |
| `commit-staged-snapshot` | git commit -m | Save a pre-staged change as a commit. | branch has one new commit; staging is empty |
| `first-save-workflow` | status → add → commit | Save one small feature from worktree to commit. | linear DAG grows by one commit; worktree clean |

### Level 3: Review Before Saving

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `diff-before-stage` | git diff | Inspect unstaged changes before deciding to save. | inspection performed before commit; final tree contains intended edit |
| `diff-after-stage` | git diff --staged | Review staged snapshot before committing. | staged snapshot becomes latest commit |
| `save-folder-work` | git add . → commit | Save a small folder of visible project files. | all visible intended files committed; generated files excluded if ignored |

### Level 4: Read History

**Band:** Introductions inside acting workflows

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `compact-history` | git log --oneline | Find the latest commit then add a review note. | review note committed after history inspection |
| `graph-history` | git log --oneline --graph --all | Inspect a tiny multi-ref history then document what branch tip matters. | documentation commit added on main |
| `show-commit` | git show / git show <commit> | Inspect a commit before writing a changelog note. | changelog commit added with correct referenced path |
| `history-detail-forms` | log -n / -p / --stat / show --name-only | Answer a commit-audit task and commit the audit file. | audit file committed; no stray files |

### Level 5: Configure Identity and Aliases

**Band:** Introductions plus save-loop reuse

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `set-user-name` | git config --global user.name | Set author name before a first authored commit. | config key updated |
| `set-user-email` | git config --global user.email | Set author email before a first authored commit. | config key updated |
| `list-config` | git config --list | Verify identity before saving a change. | identity checked; commit created |
| `create-alias` | git config --global alias.<name> <command> | Create a shortcut, verify config, then use normal save-loop. | alias recorded; repo state clean after commit |

### Level 6: Ignore Noise

**Band:** Workflow mastery

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `write-ignore-rule` | .gitignore + git status --ignored | Ignore build output while saving source files. | .gitignore committed; ignored file remains untracked |
| `explain-ignore-rule` | git check-ignore -v <path> | Explain why a generated file is ignored before committing source. | source committed; generated file absent from tree |
| `compact-and-script-status` | git status -s / --porcelain | Use compact status to separate real work from noise. | only intended files committed |

### Level 7: Clone and Inspect

**Band:** Introductions plus history reuse

| Wave slug | Command / workflow focus | Scenario purpose | Checklist end-state |
| --- | --- | --- | --- |
| `clone-default` | git clone <url> | Clone a prepared repository and verify its current state. | local repo created and inspected |
| `clone-named-folder` | git clone <url> <folder> | Clone into a required project folder and inspect history. | named folder exists with expected branch |
| `clone-specific-branch` | git clone -b <branch> <url> | Clone a specific branch then commit a local note. | local branch has one new commit |
| `clone-shallow` | git clone --depth <n> <url> | Clone shallow history and verify visible history length. | local repo usable; history inspection performed |

## Git-it Challenge Blueprint

The challenge has 3 trials × 2 variants. There is **no objective checklist**. The target is the resulting repository state. Every trial must visibly mutate commits, refs, branch tips, remote refs, or reachable history. Scaffold fades from rich before/after clues on Easy to diagram/state-only on Hard.

| Trial | DAG tier | Assessment task | Initial state | Required target state | Expected command suite | Variant plan |
| --- | --- | --- | --- | --- | --- | --- |
| Easy | T0 → T1 | Bootstrap one clean commit | empty folder with README and one source file | main -> c0; source and README committed; worktree clean | `git init`<br>`git status`<br>`git add <file>`<br>`git commit -m` | Two variants: small CLI app; small documentation site. |
| Medium | T1 linear growth | Create a two-commit project without noise | uninitialized folder with app, tests, build/log noise | main -> c0(app) -> c1(tests); .gitignore committed; noise untracked/ignored | `git init -b`<br>`git config user.name/email`<br>`git status --ignored`<br>`git check-ignore -v`<br>`git add .`<br>`git commit -m`<br>`git log --oneline` | Two variants: Python app; web widget. |
| Hard | T1 + clone + exact tree | Clone, inspect, then extend correctly | remote repo with two branches; task requires specific branch clone and local commit | chosen branch cloned; local branch advances by one or two commits; target tree exact; no ignored/generated files in history | `git clone -b`<br>`git status -s`<br>`git log --graph --all`<br>`git show --name-only`<br>`git diff`<br>`git add`<br>`git commit` | Two variants: hotfix branch clone; release-doc branch clone. |

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

- What Git tracks: working tree, index, commit
- First repository workflow
- Reading status and history
- Ignoring files safely

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
| ch1-adv-init-current-folder | adventure | Start a Repository | intro | Turn a folder with starter files into a Git repository. |
| ch1-adv-init-named-folder | adventure | Start a Repository | intro | Create a named project folder as a repository. |
| ch1-adv-init-first-branch | adventure | Start a Repository | intro | Start a repository with the requested first branch name. |
| ch1-adv-status-plain | adventure | Read Repository State | intro | Inspect a repo with one dirty or untracked file. |
| ch1-adv-stage-one-file | adventure | Read Repository State | intro | Stage exactly one file from a dirty worktree. |
| ch1-adv-commit-staged-snapshot | adventure | Read Repository State | intro | Save a pre-staged change as a commit. |
| ch1-adv-first-save-workflow | adventure | Read Repository State | intro | Save one small feature from worktree to commit. |
| ch1-adv-diff-before-stage | adventure | Review Before Saving | workflow | Inspect unstaged changes before deciding to save. |
| ch1-adv-diff-after-stage | adventure | Review Before Saving | workflow | Review staged snapshot before committing. |
| ch1-adv-save-folder-work | adventure | Review Before Saving | workflow | Save a small folder of visible project files. |
| ch1-adv-compact-history | adventure | Read History | intro | Find the latest commit then add a review note. |
| ch1-adv-graph-history | adventure | Read History | intro | Inspect a tiny multi-ref history then document what branch tip matters. |
| ch1-adv-show-commit | adventure | Read History | intro | Inspect a commit before writing a changelog note. |
| ch1-adv-history-detail-forms | adventure | Read History | intro | Answer a commit-audit task and commit the audit file. |
| ch1-adv-set-user-name | adventure | Configure Identity and Aliases | intro | Set author name before a first authored commit. |
| ch1-adv-set-user-email | adventure | Configure Identity and Aliases | intro | Set author email before a first authored commit. |
| ch1-adv-list-config | adventure | Configure Identity and Aliases | intro | Verify identity before saving a change. |
| ch1-adv-create-alias | adventure | Configure Identity and Aliases | intro | Create a shortcut, verify config, then use normal save-loop. |
| ch1-adv-write-ignore-rule | adventure | Ignore Noise | workflow | Ignore build output while saving source files. |
| ch1-adv-explain-ignore-rule | adventure | Ignore Noise | workflow | Explain why a generated file is ignored before committing source. |
| ch1-adv-compact-and-script-status | adventure | Ignore Noise | workflow | Use compact status to separate real work from noise. |
| ch1-adv-clone-default | adventure | Clone and Inspect | intro | Clone a prepared repository and verify its current state. |
| ch1-adv-clone-named-folder | adventure | Clone and Inspect | intro | Clone into a required project folder and inspect history. |
| ch1-adv-clone-specific-branch | adventure | Clone and Inspect | intro | Clone a specific branch then commit a local note. |
| ch1-adv-clone-shallow | adventure | Clone and Inspect | intro | Clone shallow history and verify visible history length. |
| ch1-challenge-easy | challenge | Bootstrap one clean commit | T0 → T1 | empty folder with README and one source file → main -> c0; source and README committed; worktree clean |
| ch1-challenge-medium | challenge | Create a two-commit project without noise | T1 linear growth | uninitialized folder with app, tests, build/log noise → main -> c0(app) -> c1(tests); .gitignore committed; noise untracked/ignored |
| ch1-challenge-hard | challenge | Clone, inspect, then extend correctly | T1 + clone + exact tree | remote repo with two branches; task requires specific branch clone and local commit → chosen branch cloned; local branch advances by one or two commits; target tree exact; no ignored/generated files in history |


## External Reference Alignment

These blueprints use Git's own state model as the truth source: working tree → index/staging area → commits, refs/branches as movable pointers, merge/rebase/reset/revert/stash/remotes as state transformations. They also borrow learning-pattern discipline from interactive platforms:

- Git official docs / Pro Git: commands are understood by the repository state they inspect or mutate.
- GitHub Skills: learners complete practical tasks such as creating branches, committing files, opening/merging work.
- Learn Git Branching: visual graph changes make abstract history operations learnable.
- GitLab / Atlassian / Codecademy-style tutorials: examples are framed as realistic workflows rather than command definitions alone.


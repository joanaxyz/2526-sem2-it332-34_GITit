# GIT it! Curriculum Design — Cumulative Workflow Mastery Revision

## Purpose

This document is the authoritative seeding reference for the GIT it! learning system. It supersedes the four separate part files (curriculum_part1.md through curriculum_part4.md) and reunifies them under the original four-module structure. It defines the exact learning structure the backend seeds: units, lessons, scenario-bearing lessons, scenarios, difficulty instances, variants, command-count policies, and target-state rules. Every section maps to Django models in `backend/learning/models.py` and `backend/scenarios/models.py`.

## How to use this document

Each module contains lessons. Lessons are either `orientation`, `content`, or `scenario-bearing`. Scenario-bearing lessons list one or more scenarios. Each scenario has three difficulty instances (`easy`, `medium`, `hard`). Each difficulty instance has a command-count policy and a target-state rule. Variants provide the starting repository state and solution commands.

When seeding, the seed file (`seed_starter_content.py`) derives `target_state` from `solution_commands` using `RepositoryStateSimulator().process()`. The `expected_state_diagram` is derived from `target_state` via `RepositorySnapshotService().snapshot()`.

---

## Cumulative command model

Each scenario has **one primary focus command** — the command being introduced and evaluated at that point in the curriculum. Scenarios are **realistic workflows**, not isolated drills. As the student progresses, prior commands become available background knowledge. A `git commit` scenario therefore includes `git status`, `git diff`, and `git add` as expected supporting steps. The scenario is still a `git commit` scenario because that is the new command being introduced and the one the evaluator primarily cares about.

This means:

- The scenario's `primary_focus_commands` list contains exactly one command (or one command family such as `git switch -c`).
- The scenario's `supporting_inspection_commands` list contains all diagnostic commands the student may freely use.
- Prior learned commands that are **counted actions** (like `git add` in a `git commit` scenario) are permitted but not listed as the focus. They are expected steps in the workflow.
- The difficulty's command-count policy (`min_counted`, `max_counted`) reflects this: later scenarios have higher budgets because more counted steps are expected.

---

## Module and Lesson Count

| Module | Title | Content Lessons | Scenario-Bearing Lessons | Scenarios | Variants Each | Total Variant-Difficulty Instances |
|---|---|---|---|---|---|---|
| 0 | Orientation | 8 orientation lessons | 0 | — | — | — |
| 1 | Local Foundations | 2 | 2 | 7 | 5 per difficulty | 105 |
| 2 | Branching and Navigation | 2 | 1 | 5 | 5 per difficulty | 75 |
| 3 | Collaboration and Integration | 2 | 1 | 7 | 5 per difficulty | 105 |
| 4 | Recovery and Repair | 2 | 1 | 8 | 5 per difficulty | 120 |
| **Total** | | | | **27 scenarios** | | **405 variant-difficulty instances** |

**Coverage note:** The expanded catalog remains cumulative. It does not create tiny command drills. Missing commands such as `git init`, `git clone`, `git pull`, `git push`, `git restore`, `git revert`, `git stash`, and `git reflog` are introduced as the new focus inside realistic workflows. Commands not yet implemented by the simulator are formally included but marked `requires_simulator_expansion` in their scenario entries.

---

## Scaffolding

| Difficulty | Live DAG | Expected-State Diagram | Contextual Feedback | Command Counter |
|---|---|---|---|---|
| Easy | Yes | Yes | Yes | Yes |
| Medium | Yes | Yes | No | Yes |
| Hard | Yes | No | No | Yes |

Easy must be completed before Medium unlocks; Medium before Hard. Review mode opens after primary completion.

---

## Variant pool

Each difficulty instance draws from a pool of 5 variants. Variants share the same target rule but differ in surface details and repository topology. Retry logic avoids repeating the immediately previous variant. No single memorized command sequence solves all five templates.

---

## System constants

Defined in `backend/common/constants.py`:

| Constant | Value | Usage |
|---|---|---|
| `DIFFICULTY_EASY` | `"easy"` | DifficultyInstance difficulty |
| `DIFFICULTY_MEDIUM` | `"medium"` | DifficultyInstance difficulty |
| `DIFFICULTY_HARD` | `"hard"` | DifficultyInstance difficulty |
| `SESSION_MODE_PRIMARY` | `"primary"` | ScenarioSession mode |
| `SESSION_MODE_REVIEW` | `"review"` | ScenarioSession mode |
| `SESSION_STATUS_STARTED` | `"started"` | ScenarioSession status |
| `SESSION_STATUS_COMPLETED` | `"completed"` | ScenarioSession status |
| `SESSION_STATUS_FAILED` | `"failed"` | ScenarioSession status |
| `SESSION_STATUS_ABANDONED` | `"abandoned"` | ScenarioSession status |
| `RESULT_TARGET_MATCHED` | `"TargetMatched"` | StepLog result_category |
| `RESULT_TARGET_NOT_YET_MATCHED` | `"TargetNotYetMatched"` | StepLog result_category |
| `RESULT_UNPROCESSABLE` | `"Unprocessable"` | StepLog result_category |
| `RESULT_INVALID` | `"Invalid"` | StepLog result_category |
| `COMMAND_COUNTED` | `"counted_action"` | StepLog command_classification |
| `COMMAND_DIAGNOSTIC` | `"non_counted_diagnostic"` | StepLog command_classification |
| `COMMAND_UNPROCESSABLE` | `"unprocessable"` | StepLog command_classification |

---

## Command classification rules

The simulator classifies every command:

1. **Counted action (`COMMAND_COUNTED`)**: A supported Git command that changes repository state. Increments the action budget. Examples: `git add`, `git commit`, `git merge`, `git reset`, `git cherry-pick`, `git switch`, `git checkout`, `git branch -d`, `git switch -c`.
2. **Diagnostic (`COMMAND_DIAGNOSTIC`)**: A read-only command. Does not count against the budget. Always free: `git status`, `git log` (all variants), `git branch` (read-only listing), `git diff` (all variants), `git show`.
3. **Unprocessable (`COMMAND_UNPROCESSABLE`)**: Unsupported, malformed, or non-Git input.

**Currently supported simulated commands:** `status`, `log`, `branch`, `diff`, `show`, `add`, `commit`, `checkout`, `switch`, `merge`, `reset`, `cherry-pick`.

**Mastery-expansion commands referenced by this curriculum but requiring simulator/evaluator expansion:** `git init`, `git clone`, `git remote`, `git fetch`, `git pull`, `git push`, `git restore`, `git restore --staged`, `git stash`, `git reflog`, `git revert`, `git commit --amend`.

**Intentionally deferred beyond this curriculum revision:** `git rebase`, `git branch -m`. These may be added in a later advanced Git track, but they are not required for the current four-module mastery path.

---

## RepositoryState schema

| Field | Type | Description |
|---|---|---|
| `commits` | array | List of `{id, message, parents[]}` objects |
| `branches` | object | Map of branch name → commit id, or `null` for an empty branch |
| `head` | object | `{"type":"branch","name":"..."}` or `{"type":"detached","target":"..."}` |
| `working_tree` | object | Map of path → `"modified"` \| `"untracked"` \| `"conflict"` |
| `staging` | object | Map of path → `"added"` \| `"modified"` |
| `conflicts` | array | List of conflicted path strings |
| `merge_parent` | string | **Required for paused-merge initial states.** The commit id of the incoming branch tip. |

---

## TargetStateRule supported fields

| Field | Description |
|---|---|
| `head_branch` | HEAD must be attached to this branch name |
| `branch_exists` | List of branch names that must exist |
| `branch_absent` | List of branch names that must not exist |
| `branch_points_to` | Map of branch name → required commit id |
| `branches_equal` | List of `[branch_a, branch_b]` pairs that must point to the same commit |
| `working_tree_clean` | Working tree must have no modified, conflict, or untracked paths |
| `working_tree_contains` | List of paths that must be present (modified or untracked) in the working tree |
| `working_tree_absent` | List of paths that must not appear in the working tree |
| `staging_empty` | Staging area must contain no staged paths |
| `staging_contains` | List of paths that must be present in the staging area |
| `conflict_free` | No conflict paths may exist |
| `min_commits_on_branch` | Map of branch name → minimum reachable commit count from that branch tip |
| `latest_commit` | Object: `{"branch": "<name>", "contains_paths": ["path1"]}`. All listed paths must be in the tip commit's tree. |

---

## Scenario completion model

The curriculum uses three completion categories while preserving the same seeding-oriented structure.

| Completion category | Used for | How completion is evaluated |
|---|---|---|
| `state_based` | State-changing commands such as `git add`, `git commit`, `git switch`, `git merge`, `git reset`, and `git cherry-pick` | The simulator processes `solution_commands` and compares the session repository state against `target_rule`. |
| `inspection` | Diagnostic commands such as `git status`, `git diff`, `git log`, `git show`, and read-only `git branch` | The session must include the required diagnostic command(s), the repository state must remain unchanged, and the expected observation/check must match. This requires an inspection evaluator rather than fake state-changing targets. |
| `expanded_state_based` | Commands not yet supported by the current simulator, such as `git init`, `git clone`, `git remote`, `git fetch`, `git pull`, `git push`, `git restore`, `git revert`, `git stash`, `git reflog`, and `git commit --amend` | The scenario is formally authored in the curriculum, but seeding requires simulator state extensions and command processing support before activation. |

### RepositoryState extension fields for mastery expansion

| Field | Type | Description |
|---|---|---|
| `repository_initialized` | boolean | Allows `git init` and pre-repository folder states. |
| `remotes` | object | Map of remote name → URL for `git remote`, `git clone`, `git fetch`, `git pull`, and `git push`. |
| `remote_branches` | object | Map of remote-tracking branch name → commit id. |
| `upstream_tracking` | object | Map of local branch → upstream remote-tracking branch. |
| `stash_stack` | array | Stack of saved working tree/staging snapshots for `git stash`. |
| `reflog` | array | Recent HEAD/ref movements for `git reflog` recovery scenarios. |

---

## Lesson CSS palettes

| Lesson slug | Accent 1 | Accent 2 |
|---|---|---|
| `three-file-areas` | `#14b8a6` | `#f59e0b` |
| `tracked-untracked` | `#22c55e` | `#38bdf8` |
| `what-head-is` | `#f97316` | `#22d3ee` |
| `dag-literacy` | `#38bdf8` | `#a3e635` |
| `branch-pointers` | `#06b6d4` | `#facc15` |
| `command-anatomy` | `#eab308` | `#2dd4bf` |
| `practice-rules` | `#10b981` | `#60a5fa` |
| `scaffolds-review` | `#8b5cf6` | `#14b8a6` |
| `status-reading` | `#14b8a6` | `#f59e0b` |
| `diff-reading` | `#22c55e` | `#f97316` |
| `first-commit` | `#22c55e` | `#38bdf8` |
| `history-inspection` | `#38bdf8` | `#facc15` |
| `branch-head` | `#06b6d4` | `#f97316` |
| `detached-head` | `#f97316` | `#60a5fa` |
| `right-branch` | `#10b981` | `#f59e0b` |
| `merge-types` | `#0ea5e9` | `#a3e635` |
| `divergence-merge` | `#0ea5e9` | `#84cc16` |
| `conflict-state` | `#ef4444` | `#22c55e` |
| `undo-without-panic` | `#eab308` | `#22d3ee` |
| `reset-modes` | `#ef4444` | `#f59e0b` |
| `reset-recovery` | `#f59e0b` | `#14b8a6` |

---

## Lesson wrapper formats

### Orientation lessons

Generated by `_orientation_html()`. Wrap each lesson in:

```html
<article class="lesson-copy lesson-page lesson-page--{slug}">
  <section class="lesson-hero">
    <div class="lesson-kicker">Foundation lesson</div>
    <h1>{title}</h1>
    <p class="lesson-lede">{subtitle}</p>
    <div class="lesson-meta">
      <span>Git mental model</span>
      <span>Visual guide</span>
      <span>Mark read anytime</span>
    </div>
  </section>
  {visual}
  {body}
  <section class="lesson-panel remember-panel">
    <h2>What to carry forward</h2>
    <ul>
      <li>Explain the repository state before choosing a command.</li>
      <li>Use the live DAG and status language together; neither tells the whole story alone.</li>
      <li>Keep these foundations nearby while you practice harder repository states.</li>
    </ul>
  </section>
</article>
```

### Content lessons

Generated by `_lesson_html()`. Wrap each lesson in:

```html
<article class="lesson-copy lesson-page lesson-page--{slug}">
  <section class="lesson-hero">
    <div class="lesson-kicker">{Practice lesson | Foundation lesson}</div>
    <h1>{title}</h1>
    <p class="lesson-lede">{subtitle}</p>
    <div class="lesson-meta">
      <span>Scrollable lesson</span>
      <span>State-first reasoning</span>
      <span>{Includes practice | Visual guide}</span>
    </div>
  </section>
  {visual}
  {body}
  <section class="lesson-panel practice-panel">
    <h2>{Practice connection | Where you will use this}</h2>
    {practice_text}
  </section>
</article>
```

**Practice connection text**
- Non-scenario content lesson: `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`
- Scenario-bearing content lesson: `<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>`

---

---

# Module 0 — Orientation

| Attribute | Value |
|---|---|
| slug | `orientation` |
| number | `0` |
| title | Orientation |
| description | Foundational Git mental models, DAG literacy, command anatomy, and platform conventions. |
| is_orientation | `True` |
| sort_order | `0` |

No scenarios. Eight orientation lessons.

---

### Lesson 0.1: The Three File Areas

| Attribute | Value |
|---|---|
| slug | `three-file-areas` |
| kind | `orientation` |
| title | The Three File Areas |
| subtitle | Working tree, staging area, and repository. |
| sort_order | `1` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Repository map</div>
  <div class="area-row">
    <div class="area-card"><span>Working tree</span><strong>edited files</strong><small>Where files change first</small></div>
    <span class="diagram-arrow">-&gt;</span>
    <div class="area-card accent"><span>Staging area</span><strong>chosen snapshot</strong><small>What the next commit will record</small></div>
    <span class="diagram-arrow">-&gt;</span>
    <div class="area-card"><span>Repository</span><strong>commit history</strong><small>Saved snapshots on branches</small></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>The three-area map</h2>
  <p>Git becomes much less mysterious when every change is placed into one of three areas. The working tree is the file system you are editing right now. The staging area is a proposed snapshot that says what the next commit should contain. The repository history is the chain of commits Git has already recorded.</p>
  <p>Many beginner mistakes happen because those areas are mixed together in the student's head. A file can be edited but not staged. A file can be staged even while newer unstaged edits exist in the working tree. A clean working tree means the working tree and staging area have no pending differences relative to the current commit.</p>
</section>
<section class="lesson-panel">
  <h2>How to read the simulator</h2>
  <p>The DAG shows committed history: commit nodes, parent links, branch labels, and HEAD. Before using a state-changing command, ask two questions: where is the change now, and where should it move next? If the change is only in the working tree, staging may be appropriate. If staged, a commit may be appropriate. If already committed on the wrong branch, the problem is about pointers and reachability.</p>
</section>
```

---

### Lesson 0.2: Tracked and Untracked Files

| Attribute | Value |
|---|---|
| slug | `tracked-untracked` |
| kind | `orientation` |
| title | Tracked and Untracked Files |
| subtitle | What Git knows about and what it ignores until you say otherwise. |
| sort_order | `2` |

**Visual**
```html
<section class="lesson-visual split-visual">
  <div class="visual-label">File knowledge boundary</div>
  <div class="state-card accent"><strong>Tracked</strong><span>Git records changes</span><small>modified, staged, or clean</small></div>
  <div class="state-card"><strong>Untracked</strong><span>Git sees but ignores</span><small>not part of any commit yet</small></div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>The tracked/untracked boundary</h2>
  <p>A file is tracked once it has appeared in at least one commit. From that point on, Git monitors every change to it. An untracked file exists in the working tree but has never been committed. Git reports its presence but never includes it in a commit automatically. <code>git add</code> is what crosses the boundary — it moves a file from untracked into the staging area for the first time.</p>
  <p>Confusing tracked and untracked files causes two types of mistake: accidentally committing scratch files by using <code>git add .</code> without checking status first, or assuming a new file is being tracked when it has never been added. The <code>.gitignore</code> file suppresses even the "untracked" notice for paths that should never be staged.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Untracked</h2><p>File exists in the working tree but has never been part of a commit. <code>git status</code> lists it under "Untracked files."</p></div>
  <div class="lesson-panel accent-panel"><h2>Modified (tracked)</h2><p>File has been committed before and now has local edits. <code>git status</code> shows it under "Changes not staged for commit."</p></div>
  <div class="lesson-panel accent-panel"><h2>Staged</h2><p>File (tracked or new) has been added to the staging area. <code>git status</code> shows it under "Changes to be committed."</p></div>
</section>
```

---

### Lesson 0.3: What HEAD Is

| Attribute | Value |
|---|---|
| slug | `what-head-is` |
| kind | `orientation` |
| title | What HEAD Is |
| subtitle | HEAD is a pointer — and it predicts where the next commit will land. |
| sort_order | `3` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">HEAD follows the branch</div>
  <div class="commit-row">
    <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span>
  </div>
  <div class="label-row">
    <span class="branch-tag">main → c1</span>
    <span class="head-tag">HEAD → main</span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>HEAD is a pointer to a pointer</h2>
  <p>HEAD usually points to a branch label, and that branch label points to a commit. When you create a new commit, the branch label advances to the new commit — and HEAD advances with it because HEAD points to the branch, not directly to the commit.</p>
  <p>When HEAD points to a commit directly instead of through a branch label, it is in a "detached" state. New commits in detached HEAD state are not attached to any branch and can become unreachable if HEAD moves away before a branch label is created.</p>
</section>
<section class="lesson-panel">
  <h2>What HEAD predicts</h2>
  <p>Before committing, switching, merging, or recovering, identify HEAD. It predicts which branch will move, which branch will receive a merge, and where a new commit would appear. In wrong-branch scenarios, the files may look correct while HEAD reveals the commit is about to land on the wrong branch.</p>
</section>
```

---

### Lesson 0.4: Commits, Parents, and DAG Literacy

| Attribute | Value |
|---|---|
| slug | `dag-literacy` |
| kind | `orientation` |
| title | Commits, Parents, and DAG Literacy |
| subtitle | Reading commits, parent edges, branch labels, and HEAD. |
| sort_order | `4` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Divergence and merge shape</div>
  <div class="graph-stack">
    <div class="commit-row"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="diagram-line fork"></span><span class="commit-node">c3</span></div>
    <div class="commit-row offset"><span class="commit-node branch">c2</span><span class="diagram-line merge"></span><span class="commit-node active">c4</span></div>
  </div>
  <div class="label-row"><span class="branch-tag">feature</span><span class="branch-tag">main</span><span class="head-tag">merge commit has two parents</span></div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Commits are nodes, parents are evidence</h2>
  <p>Git history is a directed acyclic graph. Each commit is a node. Parent links explain where that commit came from. A normal commit usually has one parent. A merge commit has more than one parent because it records the act of joining histories. The graph is acyclic because history does not loop backward into itself.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Labels are movable</h2><p>Branch names are labels pointing at commits. The commit does not contain the branch. The branch label simply names the current tip of a line of work.</p></div>
  <div class="lesson-panel"><h2>Read the shape</h2><p>A straight line suggests one path of history. A split suggests divergence. A merge commit with two parents suggests integration. A stale branch label may point to work already reachable from another branch.</p></div>
</section>
<pre><code>git log --oneline --graph
git branch -v
# Pair text history with the live DAG to explain the repository shape.</code></pre>
```

---

### Lesson 0.5: Branches as Movable Pointers

| Attribute | Value |
|---|---|
| slug | `branch-pointers` |
| kind | `orientation` |
| title | Branches as Movable Pointers |
| subtitle | Branches are labels that move with commits, not folders. |
| sort_order | `5` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Branches are labels</div>
  <div class="commit-row">
    <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span><span class="diagram-line"></span><span class="commit-node ghost">next</span>
  </div>
  <div class="label-row"><span class="branch-tag">main points at c1</span><span class="head-tag">new commit moves the label</span></div>
</section>
```

**Body**
```html
<section class="lesson-grid">
  <div class="lesson-panel">
    <h2>A branch is a label that moves</h2>
    <p>A branch is not a folder, not a copy of the project, and not a separate database. It is a movable label pointing to a commit. When HEAD is attached to that branch and a new commit is created, the branch label advances to the new commit.</p>
    <p>This explains why a wrong-branch commit is recoverable. The work exists as a commit. The task is to move or recreate the intended pointer relationship without throwing away reachable work.</p>
  </div>
  <div class="lesson-panel accent-panel">
    <h2>Switching is not copying</h2>
    <p>Switching branches changes which branch HEAD is attached to and updates the working tree to match. It does not duplicate history. It changes the active viewpoint.</p>
  </div>
</section>
<section class="lesson-panel">
  <h2>Pointer thinking prevents panic</h2>
  <p>Many destructive Git habits come from imagining branches as folders. If a branch is a pointer, divergence is just two labels naming different commits. That mental model makes recovery commands feel like pointer operations rather than emergency rituals.</p>
</section>
```

---

### Lesson 0.6: Git Command Anatomy

| Attribute | Value |
|---|---|
| slug | `command-anatomy` |
| kind | `orientation` |
| title | Git Command Anatomy |
| subtitle | How to read a command before trusting it. |
| sort_order | `6` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Read the command shape</div>
  <div class="command-parse">
    <span><strong>git</strong><small>program</small></span>
    <span><strong>commit</strong><small>action</small></span>
    <span><strong>-m</strong><small>option</small></span>
    <span><strong>"update config"</strong><small>message</small></span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Commands have grammar</h2>
  <p>A Git command has parts: the program name <code>git</code>, a subcommand such as <code>status</code> or <code>commit</code>, optional flags, and arguments such as paths or branch names. Reading the grammar helps students understand intent before executing a command copied from a search result or AI tool.</p>
</section>
<section class="lesson-grid">
  <div class="command-slab"><code>git status</code><span>inspection: read state, free to use</span></div>
  <div class="command-slab"><code>git add &lt;path&gt;</code><span>action: propose content for commit, uses budget</span></div>
  <div class="command-slab"><code>git log --oneline</code><span>inspection: read history, free to use</span></div>
  <div class="command-slab"><code>git diff</code><span>inspection: compare areas, free to use</span></div>
</section>
<section class="lesson-panel">
  <h2>Inspect before action</h2>
  <p>Inspection commands are not wasted effort. <code>git status</code>, <code>git log</code>, <code>git diff</code>, <code>git branch</code>, and <code>git show</code> are all free — they never count against your action budget. Action commands like <code>git add</code>, <code>git commit</code>, <code>git switch</code>, <code>git merge</code>, and <code>git reset</code> change repository state and count toward the budget.</p>
</section>
```

---

### Lesson 0.7: GIT it! Practice Rules

| Attribute | Value |
|---|---|
| slug | `practice-rules` |
| kind | `orientation` |
| title | GIT it! Practice Rules |
| subtitle | Safe simulator rules, feedback, and action limits. |
| sort_order | `7` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Practice loop</div>
  <div class="workflow-strip">
    <span>Inspect</span><span>Explain state</span><span>Act</span><span>Read feedback</span><span>Retry if needed</span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>A safe terminal with real consequences</h2>
  <p>The practice terminal is simulated. It does not execute operating-system commands, call the external Git CLI, connect to GitHub, or touch your real files. Within the simulator, however, commands still have consequences: branches move, commits appear, conflicts can exist, and the working tree can become clean or remain messy.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel">
    <h2>Free inspection commands</h2>
    <p>Always free and never count against your budget: <code>git status</code>, <code>git log</code>, <code>git log --oneline</code>, <code>git log --oneline --graph</code>, <code>git branch</code>, <code>git branch -v</code>, <code>git diff</code>, <code>git diff --staged</code>, <code>git show</code>.</p>
  </div>
  <div class="lesson-panel">
    <h2>Counted action budget</h2>
    <p>Each practice level has a limit for state-changing actions: <code>git add</code>, <code>git commit</code>, <code>git switch</code>, <code>git merge</code>, <code>git reset</code>, <code>git cherry-pick</code>, <code>git branch -d</code>. These count toward your budget.</p>
  </div>
</section>
<section class="lesson-panel">
  <h2>How to practice well</h2>
  <p>Read the narrative, inspect the starting state, name the target state in your own words, then act. If an attempt fails or is abandoned, retry is part of the learning loop. The retry may use a changed variant so you practice the concept, not a memorized surface pattern.</p>
</section>
```

---

### Lesson 0.8: Scaffolding, Retry, and Review Mode

| Attribute | Value |
|---|---|
| slug | `scaffolds-review` |
| kind | `orientation` |
| title | Scaffolding, Retry, and Review Mode |
| subtitle | How support changes from Easy to Hard. |
| sort_order | `8` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Support fades by level</div>
  <div class="level-ladder">
    <div><strong>Easy</strong><span>DAG, target picture, feedback, action budget</span></div>
    <div><strong>Medium</strong><span>DAG and target picture — no step feedback</span></div>
    <div><strong>Hard</strong><span>DAG only — read the graph and decide</span></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Scaffolding fades on purpose</h2>
  <p>Easy, Medium, and Hard are not just labels. They change the amount of support available while preserving the same core Git concept. Easy includes the live DAG, expected-state diagram, contextual feedback, and command counter. Medium removes contextual feedback. Hard keeps only the live DAG and narrative context.</p>
  <p>Beyond the scaffolding change, later difficulty levels also increase the genuine complexity of the repository state: more steps may be required, the working tree may have additional noise, or the graph may have multiple plausible-looking branches that require inspection to distinguish.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Adaptive retry</h2><p>After a failed or abandoned attempt, retry serves a changed version of the same level. The Git concept stays stable while branch names, file names, or graph shape may change.</p></div>
  <div class="lesson-panel"><h2>Review Mode</h2><p>After completing a difficulty instance, you can replay it in Review Mode. Review sessions are logged separately and do not overwrite the primary completion record.</p></div>
</section>
```

---

---

# Module 1 — Local Foundations

| Attribute | Value |
|---|---|
| slug | `local-foundations` |
| number | `1` |
| title | Local Foundations |
| description | Read working tree, staging area, commits, and history. Practice interpreting repository state with git status and git diff, then form intentional commits with git add and git commit. |
| is_orientation | `False` |
| sort_order | `1` |
| assumption | Complete beginner. Has never used Git in a terminal. |
| goal | Student can manage a personal repository confidently before any collaboration or branching is introduced. |

Two content lessons and two scenario-bearing lessons with seven scenarios. Lessons 1.3 and 1.4 now carry the formal local-workflow and history-inspection scenario sets.

---

### Lesson 1.1: Reading Git Status

| Attribute | Value |
|---|---|
| slug | `status-reading` |
| kind | `content` |
| title | Reading Git Status |
| subtitle | Interpreting status output before changing repository state. |
| sort_order | `1` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Status tells you where to look</div>
  <div class="status-columns">
    <div class="state-card"><strong>On branch</strong><span>Where HEAD is attached</span><code>main</code></div>
    <div class="state-card accent"><strong>Staged</strong><span>Ready for commit</span><code>config.yml</code></div>
    <div class="state-card"><strong>Not staged</strong><span>Changed but not selected</span><code>draft.md</code></div>
    <div class="state-card"><strong>Untracked</strong><span>New file, not yet in history</span><code>notes.txt</code></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Status is a state report</h2>
  <p><code>git status</code> is the fastest way to separate facts before acting. It tells the current branch, whether the working tree is clean, which paths are staged, which paths are modified but unstaged, which paths are untracked, and whether a merge or conflict state is in progress.</p>
  <p>The status report lets you decide whether the next action should move content into staging, create a commit, resolve a conflict, switch context, or stop because the repository is already in the target state.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Branch line</h2><p>Names the branch HEAD is attached to, or hints that HEAD is detached. Always read this first — it tells you where your next commit will land.</p></div>
  <div class="lesson-panel accent-panel"><h2>Path groups</h2><p>Staged, unstaged, and untracked paths are shown separately. This separation prevents scope mistakes: you can see exactly what will be in the next commit versus what is still only in your working tree.</p></div>
  <div class="lesson-panel accent-panel"><h2>Clean state</h2><p>No staged or unstaged work pending against the current commit. This is the expected final state for most scenarios.</p></div>
</section>
<section class="lesson-panel">
  <h2>How this appears in scenarios</h2>
  <p>In first-commit tasks, status tells whether files are still untracked or have been staged. In partial-staging tasks, status prevents draft work from being swept into a commit. The habit in every scenario is the same: run <code>git status</code> before your first action, run it again after each action to confirm the state moved as expected.</p>
</section>
<pre><code>git status
git diff
git diff --staged</code></pre>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 1.2: Inspecting Differences with git diff

| Attribute | Value |
|---|---|
| slug | `diff-reading` |
| kind | `content` |
| title | Inspecting Differences with git diff |
| subtitle | Understanding what changed, where, and whether it belongs in the next commit. |
| sort_order | `2` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Three diff comparisons</div>
  <div class="status-columns">
    <div class="state-card"><strong>git diff</strong><span>Working tree vs staging area</span><small>What is changed but not yet staged</small></div>
    <div class="state-card accent"><strong>git diff --staged</strong><span>Staging area vs last commit</span><small>What will go into the next commit</small></div>
    <div class="state-card"><strong>git diff &lt;branch&gt;</strong><span>Current branch vs another branch</span><small>What differs between two tips</small></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Diff answers "what exactly changed?"</h2>
  <p><code>git status</code> tells you which files changed. <code>git diff</code> tells you what changed inside those files. Reading a diff before staging is the difference between a deliberate commit and an accidental one.</p>
  <p>There are three important diff comparisons. <code>git diff</code> with no arguments compares your working tree against the staging area. <code>git diff --staged</code> compares the staging area against the last commit — it shows exactly what the next commit would record. <code>git diff &lt;branch&gt;</code> compares the current branch tip against another branch tip.</p>
</section>
<section class="lesson-grid">
  <div class="command-slab"><code>git diff</code><span>unstaged changes — not yet in staging</span></div>
  <div class="command-slab"><code>git diff --staged</code><span>staged changes — will enter next commit</span></div>
  <div class="command-slab"><code>git diff main feature/login</code><span>branch comparison</span></div>
</section>
<section class="lesson-panel">
  <h2>Diff is always free</h2>
  <p>Like <code>git status</code>, all <code>git diff</code> variants are diagnostic commands that never count against your action budget. Developing the habit of reading diffs before staging and before committing is a mark of professional Git work.</p>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 1.3: Staging Decisions and Forming Commits

| Attribute | Value |
|---|---|
| slug | `first-commit` |
| kind | `scenario` |
| title | Staging Decisions and Forming Commits |
| subtitle | Move from working tree changes to intentional, well-scoped commits. |
| sort_order | `3` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Commit formation workflow</div>
  <div class="area-row">
    <div class="area-card"><span>Working tree</span><strong>config.yml, draft.md</strong><small>Changed files</small></div>
    <span class="diagram-arrow">-&gt;</span>
    <div class="area-card accent"><span>Staging</span><strong>config.yml only</strong><small>git add selects scope</small></div>
    <span class="diagram-arrow">-&gt;</span>
    <div class="area-card"><span>Repository</span><strong>commit on main</strong><small>git commit records it</small></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>A commit is a chosen snapshot</h2>
  <p>A commit is a deliberate snapshot with a branch destination, a content scope, and a message that communicates intent. The staging area is what makes that choice explicit. If the staging area contains everything, the next commit contains everything. If it contains one path, the next commit records one path.</p>
  <p>The scenarios in this lesson build the full commit formation workflow in three focused steps. First you practice reading repository state with <code>git status</code>. Then you practice staging with <code>git add</code>. Finally you practice committing with <code>git commit</code>. Each scenario focuses on one step as its primary evaluation target, but because the workflow is cumulative, the commit scenario expects you to stage first and then commit — just as in real work.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Scope</h2><p>Which files belong in the next commit? Use <code>git status</code> and <code>git diff</code> to decide before staging anything.</p></div>
  <div class="lesson-panel accent-panel"><h2>Target branch</h2><p>Which branch should receive the new commit? Confirm HEAD before committing.</p></div>
  <div class="lesson-panel accent-panel"><h2>Clean finish</h2><p>After a commit, the staging area should be empty and the working tree should reflect only intentional leftover work.</p></div>
</section>
<section class="lesson-panel">
  <h2>Partial staging is professional hygiene</h2>
  <p>Real work rarely arrives perfectly separated. A configuration fix can sit beside draft notes. The partial-staging evaluator checks whether the latest commit contains the requested paths, excludes draft paths, and leaves intentionally uncommitted work visible in the working tree. "Commit everything" is not a universal answer. A good commit has a boundary.</p>
</section>
```

**Practice connection:** `<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>`

---

#### Scenario 1.3-A: initialize-project-and-first-commit

**Primary focus command:** `git init`
**Cumulative workflow:** This is not an isolated "run init and stop" drill. The new command is `git init`; the realistic workflow continues into `git status`, `git add`, and `git commit` because a newly initialized project only becomes useful after the first tracked snapshot.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires the simulator to represent a pre-repository folder and process `git init`. The target is still state-based after initialization and first commit.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `initialize-project-and-first-commit` |
| title | Initialize Project and Create the First Snapshot |
| focus | `git init` |
| summary | Turn an ordinary project folder into a Git repository, inspect it, stage the starter files, and save the first commit. |
| short_explanation | `git init` creates the repository metadata that lets Git begin tracking a folder. In this curriculum it is introduced through the realistic first-project workflow: initialize, inspect, stage, and commit. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git init"]` |
| supporting_inspection_commands | `["git status","git diff","git log --oneline"]` |
| safe_demo_commands | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |
| demo_repository_state | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"README.md":"untracked","app.py":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git init","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git add .","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git commit -m \"starter snapshot\"","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["repository initialization","first commit","working tree","staging area"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "You have a normal project folder with two starter files and no Git repository yet."
- task: "Initialize the folder as a Git repository, inspect the state, stage the starter files, and create the first commit on main."
- policy: `(3, 7, ["git status", "git diff", "git log --oneline"])`
- target_rule: `{"repository_initialized":true,"head_branch":"main","working_tree_clean":true,"staging_empty":true,"min_commits_on_branch":{"main":1}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-init-readme-app` | README and app | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"README.md":"untracked","app.py":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |
| `easy-init-web-starter` | Static web starter | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"index.html":"untracked","styles.css":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |
| `easy-init-api-schema` | API and schema | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"api.py":"untracked","schema.sql":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |
| `easy-init-config-models` | Config and models | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"config.yml":"untracked","models.py":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |
| `easy-init-routes-tests` | Routes and tests | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"routes.js":"untracked","tests.js":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add .","git commit -m \"starter snapshot\""]` |

###### Medium

- narrative: "A project folder has starter code plus a notes file. The starter code belongs in the first commit; the notes file should remain outside the snapshot."
- task: "Initialize the repository, stage only the starter code files, and create the first commit. Leave the personal notes in the working tree."
- policy: `(3, 7, ["git status", "git diff", "git diff --staged"])`
- target_rule: `{"repository_initialized":true,"head_branch":"main","staging_empty":true,"working_tree_contains":["notes.md"],"min_commits_on_branch":{"main":1}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-init-1` | README/app plus notes | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"README.md":"untracked","app.py":"untracked","notes.md":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add README.md","git add app.py","git commit -m \"starter snapshot\""]` |
| `medium-init-2` | Web files plus notes | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"index.html":"untracked","styles.css":"untracked","notes.md":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add index.html","git add styles.css","git commit -m \"starter snapshot\""]` |
| `medium-init-3` | API/schema plus notes | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"api.py":"untracked","schema.sql":"untracked","notes.md":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add api.py","git add schema.sql","git commit -m \"starter snapshot\""]` |
| `medium-init-4` | Config/models plus notes | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"config.yml":"untracked","models.py":"untracked","notes.md":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add config.yml","git add models.py","git commit -m \"starter snapshot\""]` |
| `medium-init-5` | Routes/tests plus notes | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"routes.js":"untracked","tests.js":"untracked","notes.md":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add routes.js","git add tests.js","git commit -m \"starter snapshot\""]` |

###### Hard

- narrative: "A project folder has starter code, local scratch files, and a generated log. Only the real starter files belong in the first commit."
- task: "Initialize the repository, inspect before staging, commit only the real starter files, and leave scratch/generated files out."
- policy: `(3, 8, ["git status", "git diff", "git diff --staged", "git log --oneline"])`
- target_rule: `{"repository_initialized":true,"head_branch":"main","staging_empty":true,"working_tree_contains":["scratch.md","debug.log"],"min_commits_on_branch":{"main":1}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-init-1` | README/app with generated noise | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"README.md":"untracked","app.py":"untracked","scratch.md":"untracked","debug.log":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add README.md","git add app.py","git commit -m \"starter snapshot\""]` |
| `hard-init-2` | Web files with generated noise | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"index.html":"untracked","styles.css":"untracked","scratch.md":"untracked","debug.log":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add index.html","git add styles.css","git commit -m \"starter snapshot\""]` |
| `hard-init-3` | API/schema with generated noise | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"api.py":"untracked","schema.sql":"untracked","scratch.md":"untracked","debug.log":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add api.py","git add schema.sql","git commit -m \"starter snapshot\""]` |
| `hard-init-4` | Config/models with generated noise | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"config.yml":"untracked","models.py":"untracked","scratch.md":"untracked","debug.log":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add config.yml","git add models.py","git commit -m \"starter snapshot\""]` |
| `hard-init-5` | Routes/tests with generated noise | `{"commits":[],"branches":{"main":null},"head":{"type":"none","name":null},"working_tree":{"routes.js":"untracked","tests.js":"untracked","scratch.md":"untracked","debug.log":"untracked"},"staging":{},"conflicts":[],"repository_initialized":false}` | `["git init","git status","git add routes.js","git add tests.js","git commit -m \"starter snapshot\""]` |

---

#### Scenario 1.3-B: read-repository-state

**Primary focus command:** `git status`
**Cumulative workflow:** This scenario introduces `git status` as the new skill. It does not ask students to stage a file just to prove they read status. Completion is based on running the diagnostic command and matching the expected observation; the repository state should remain unchanged.
**Seeding status:** `requires_inspection_evaluator`
**Evaluator note:** The current state simulator can process a no-op diagnostic command, but the platform needs an inspection-answer check or StepLog-based required-command check so the scenario is not falsely graded through `git add`.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `read-repository-state` |
| title | Read Repository State |
| focus | `git status` |
| summary | Use git status to identify the current branch and classify changes before choosing any action. |
| short_explanation | `git status` reports HEAD/branch context, staged changes, unstaged changes, untracked files, and special states such as conflicts. The goal is correct state interpretation before acting. |
| skill_focus_type | `diagnostic_inspection` |
| primary_focus_commands | `["git status"]` |
| supporting_inspection_commands | `["git diff","git diff --staged","git log --oneline","git branch"]` |
| safe_demo_commands | `["git status"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["working tree","staging area","HEAD","tracked and untracked files"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "Two files are modified on main. One looks ready and the other is draft work, but you are not acting yet."
- task: "Run git status and identify which files are modified and whether anything is staged. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff", "git diff --staged"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git status"],"repository_state_unchanged":true,"must_identify":["head_branch","unstaged_changes","staging_empty"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-status-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `easy-status-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `easy-status-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `easy-status-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `easy-status-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |

###### Medium

- narrative: "The repository has prior history and a nearby branch. You need to read the current branch and pending files before deciding what to do."
- task: "Run git status and identify the active branch, unstaged files, and whether the staging area is empty. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff", "git log --oneline", "git branch"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git status"],"repository_state_unchanged":true,"must_identify":["head_branch","unstaged_changes","staging_empty"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-status-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `medium-status-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `medium-status-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `medium-status-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |
| `medium-status-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git status"]` |

###### Hard

- narrative: "The repository has staged, unstaged, and untracked paths at the same time. The goal is to classify the state, not fix it yet."
- task: "Run git status and classify staged, unstaged, and untracked paths. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff", "git diff --staged", "git branch -v"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git status"],"repository_state_unchanged":true,"must_identify":["staged_changes","unstaged_changes","untracked_files","head_branch"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-status-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/check":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified","extra.tmp":"untracked"},"staging":{"README.md":"modified"},"conflicts":[]}` | `["git status"]` |
| `hard-status-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/check":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified","extra.tmp":"untracked"},"staging":{"README.md":"modified"},"conflicts":[]}` | `["git status"]` |
| `hard-status-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/check":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified","extra.tmp":"untracked"},"staging":{"README.md":"modified"},"conflicts":[]}` | `["git status"]` |
| `hard-status-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/check":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified","extra.tmp":"untracked"},"staging":{"README.md":"modified"},"conflicts":[]}` | `["git status"]` |
| `hard-status-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/check":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified","extra.tmp":"untracked"},"staging":{"README.md":"modified"},"conflicts":[]}` | `["git status"]` |

---

#### Scenario 1.3-C: inspect-file-differences

**Primary focus command:** `git diff`
**Cumulative workflow:** This scenario introduces `git diff` as the new skill. Prior `git status` is used to discover changed paths, but the primary skill is reading the actual content difference before any staging or commit action.
**Seeding status:** `requires_inspection_evaluator`
**Evaluator note:** This uses diagnostic commands only; grading should check required commands and expected observations, not a changed target state.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `inspect-file-differences` |
| title | Inspect File Differences |
| focus | `git diff` |
| summary | Use git diff to inspect unstaged and staged content before deciding what belongs in a commit. |
| short_explanation | `git diff` compares repository areas. Plain `git diff` shows unstaged working-tree changes, while `git diff --staged` shows the snapshot that would be committed. |
| skill_focus_type | `diagnostic_inspection` |
| primary_focus_commands | `["git diff"]` |
| supporting_inspection_commands | `["git status","git diff --staged","git log --oneline"]` |
| safe_demo_commands | `["git status","git diff","git diff --staged"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff --staged","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["diff reading","unstaged changes","staged snapshot","commit scope"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "Two files are modified. You need to inspect the content differences before choosing what to stage later."
- task: "Run git diff to inspect the unstaged changes. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git diff"],"repository_state_unchanged":true,"must_identify":["unstaged_diff_paths"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-diff-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git diff"]` |
| `easy-diff-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git diff"]` |
| `easy-diff-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git diff"]` |
| `easy-diff-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git diff"]` |
| `easy-diff-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git diff"]` |

###### Medium

- narrative: "One file is already staged while another has additional unstaged edits. You need to distinguish the two comparisons."
- task: "Use git diff and git diff --staged to identify what is unstaged and what would be committed. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff", "git diff --staged"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git diff","git diff --staged"],"repository_state_unchanged":true,"must_identify":["unstaged_diff_paths","staged_diff_paths"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-diff-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"draft.md":"modified"},"staging":{"config.yml":"modified"},"conflicts":[]}` | `["git diff","git diff --staged"]` |
| `medium-diff-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"notes.txt":"modified"},"staging":{"settings.json":"modified"},"conflicts":[]}` | `["git diff","git diff --staged"]` |
| `medium-diff-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"scratch.md":"modified"},"staging":{"api.py":"modified"},"conflicts":[]}` | `["git diff","git diff --staged"]` |
| `medium-diff-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"debug.log":"modified"},"staging":{"schema.sql":"modified"},"conflicts":[]}` | `["git diff","git diff --staged"]` |
| `medium-diff-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"temp.txt":"modified"},"staging":{"styles.css":"modified"},"conflicts":[]}` | `["git diff","git diff --staged"]` |

###### Hard

- narrative: "The graph has multiple branches and mixed staged/unstaged work. You must inspect both file content and branch context without changing anything."
- task: "Use status, diff, and staged diff to identify the exact commit scope and leftover work. Do not change the repository."
- policy: `(0, 0, ["git status", "git diff", "git diff --staged", "git log --oneline", "git branch -v"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git diff","git diff --staged"],"repository_state_unchanged":true,"must_identify":["head_branch","unstaged_diff_paths","staged_diff_paths"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-diff-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"draft.md":"modified","scratch.md":"untracked"},"staging":{"config.yml":"modified"},"conflicts":[]}` | `["git status","git diff","git diff --staged"]` |
| `hard-diff-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"notes.txt":"modified","scratch.md":"untracked"},"staging":{"settings.json":"modified"},"conflicts":[]}` | `["git status","git diff","git diff --staged"]` |
| `hard-diff-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"scratch.md":"untracked"},"staging":{"api.py":"modified"},"conflicts":[]}` | `["git status","git diff","git diff --staged"]` |
| `hard-diff-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"debug.log":"modified","scratch.md":"untracked"},"staging":{"schema.sql":"modified"},"conflicts":[]}` | `["git status","git diff","git diff --staged"]` |
| `hard-diff-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"temp.txt":"modified","scratch.md":"untracked"},"staging":{"styles.css":"modified"},"conflicts":[]}` | `["git status","git diff","git diff --staged"]` |

---

#### Scenario 1.3-D: stage-selected-changes

**Primary focus command:** `git add`
**Cumulative workflow:** This scenario introduces `git add` as the new counted action. Prior `git status` and `git diff` are expected diagnostic support, but the evaluated state change is selective movement from working tree to staging area.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `stage-selected-changes` |
| title | Stage Selected Changes |
| focus | `git add` |
| summary | Move selected working-tree changes into the staging area while leaving unrelated work unstaged. |
| short_explanation | `git add <path>` stages only the named path. It should be used after `git status` and usually after `git diff` so the staged snapshot has a deliberate boundary. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git add"]` |
| supporting_inspection_commands | `["git status","git diff","git diff --staged","git log --oneline"]` |
| safe_demo_commands | `["git status","git diff","git add config.yml","git diff --staged"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git add config.yml","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff --staged","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["working tree","staging area","selected staging","commit scope"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A ready configuration change and draft notes are both modified. Only the ready file should be staged."
- task: "Stage only the ready file. Leave the draft file in the working tree. Do not commit yet."
- policy: `(1, 5, ["git status", "git diff", "git diff --staged", "git log --oneline"])`
- target_rule: `{"head_branch":"main","staging_contains":["<ready-file>"],"working_tree_contains":["<draft-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-add-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git add config.yml"]` |
| `easy-add-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add settings.json"]` |
| `easy-add-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add api.py"]` |
| `easy-add-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git add schema.sql"]` |
| `easy-add-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add styles.css"]` |

###### Medium

- narrative: "A ready file and a work-in-progress file are mixed in a repository with prior history."
- task: "Inspect first, then stage only the production-ready file on main. Do not commit yet."
- policy: `(1, 5, ["git status", "git diff", "git diff --staged", "git log --oneline"])`
- target_rule: `{"head_branch":"main","staging_contains":["<ready-file>"],"working_tree_contains":["<draft-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-add-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git add config.yml"]` |
| `medium-add-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add settings.json"]` |
| `medium-add-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add api.py"]` |
| `medium-add-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git add schema.sql"]` |
| `medium-add-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add styles.css"]` |

###### Hard

- narrative: "A focused fix and experimental notes are mixed with multiple branch labels in the graph."
- task: "Stage only the requested fix on main and leave the experimental file untouched. Do not commit yet."
- policy: `(1, 4, ["git status", "git diff", "git diff --staged", "git branch -v"])`
- target_rule: `{"head_branch":"main","staging_contains":["<ready-file>"],"working_tree_contains":["<draft-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-add-config` | Config and draft | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","draft.md":"modified"},"staging":{},"conflicts":[]}` | `["git add config.yml"]` |
| `hard-add-settings` | Settings and notes | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"settings.json":"modified","notes.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add settings.json"]` |
| `hard-add-api` | API and scratch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add api.py"]` |
| `hard-add-schema` | Schema and log | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"schema.sql":"modified","debug.log":"modified"},"staging":{},"conflicts":[]}` | `["git add schema.sql"]` |
| `hard-add-styles` | Styles and temp | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","spike/research":"c0","release/checklist":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"styles.css":"modified","temp.txt":"modified"},"staging":{},"conflicts":[]}` | `["git add styles.css"]` |

---

#### Scenario 1.3-E: form-clean-commit

**Primary focus command:** `git commit`
**Cumulative workflow:** This scenario introduces `git commit` as the new command. It is still a full workflow: inspect, stage, verify the staged snapshot, then commit. `git add` is counted as an expected prior action but is not the primary focus.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `form-clean-commit` |
| title | Form a Clean Commit |
| focus | `git commit` |
| summary | Stage the intended files and record a clean commit on the correct branch. |
| short_explanation | `git commit -m "message"` records the staged snapshot onto the current branch. The scenario expects prior skills (`git status`, `git diff`, and `git add`) as normal preparation. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git commit"]` |
| supporting_inspection_commands | `["git status","git diff","git diff --staged","git log --oneline"]` |
| safe_demo_commands | `["git status","git add .","git diff --staged","git commit -m \"starter snapshot\""]` |
| demo_repository_state | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"untracked","app.py":"untracked"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git add .","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff --staged","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git commit -m \"starter snapshot\"","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["staging area","commit history","snapshot","branch destination"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A new repository has two untracked starter files. Both belong in the first commit."
- task: "Create one clean starter commit on main containing both starter files. Leave the staging area and working tree clean."
- policy: `(2, 6, ["git status", "git diff", "git diff --staged", "git log --oneline"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_clean":true,"conflict_free":true,"min_commits_on_branch":{"main":1}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-commit-README` | README and app | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"untracked","app.py":"untracked"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"starter snapshot\""]` |
| `easy-commit-index` | Static web starter | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"index.html":"untracked","styles.css":"untracked"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"starter snapshot\""]` |
| `easy-commit-api` | API and schema | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"untracked","schema.sql":"untracked"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"starter snapshot\""]` |
| `easy-commit-config` | Config and models | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"untracked","models.py":"untracked"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"starter snapshot\""]` |
| `easy-commit-routes` | Routes and tests | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{"routes.js":"untracked","tests.js":"untracked"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"starter snapshot\""]` |

###### Medium

- narrative: "The repository already has a baseline commit and two modified files that both belong in the next commit."
- task: "Create a commit on main containing both modified files. The repository must be clean after committing."
- policy: `(2, 6, ["git status", "git diff", "git diff --staged", "git log --oneline", "git branch"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_clean":true,"conflict_free":true,"min_commits_on_branch":{"main":2}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-commit-README` | README and app | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified","app.py":"modified"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"update snapshot\""]` |
| `medium-commit-index` | Static web starter | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"index.html":"modified","styles.css":"modified"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"update snapshot\""]` |
| `medium-commit-api` | API and schema | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","schema.sql":"modified"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"update snapshot\""]` |
| `medium-commit-config` | Config and models | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","models.py":"modified"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"update snapshot\""]` |
| `medium-commit-routes` | Routes and tests | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"routes.js":"modified","tests.js":"modified"},"staging":{},"conflicts":[]}` | `["git add .","git commit -m \"update snapshot\""]` |

###### Hard

- narrative: "Two files belong in the commit and one scratch file must stay out. Multiple branches exist."
- task: "Commit only the two requested files on main. Leave scratch.md in the working tree and end with an empty staging area."
- policy: `(3, 6, ["git status", "git diff", "git diff --staged", "git log --oneline", "git branch -v"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_contains":["scratch.md"],"conflict_free":true,"min_commits_on_branch":{"main":2}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-commit-README` | README and app | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified","app.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git add app.py","git commit -m \"focused update\""]` |
| `hard-commit-index` | Static web starter | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"index.html":"modified","styles.css":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add index.html","git add styles.css","git commit -m \"focused update\""]` |
| `hard-commit-api` | API and schema | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"api.py":"modified","schema.sql":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add api.py","git add schema.sql","git commit -m \"focused update\""]` |
| `hard-commit-config` | Config and models | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"config.yml":"modified","models.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add config.yml","git add models.py","git commit -m \"focused update\""]` |
| `hard-commit-routes` | Routes and tests | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","spike/research":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"routes.js":"modified","tests.js":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git add routes.js","git add tests.js","git commit -m \"focused update\""]` |

---

### Lesson 1.4: Inspecting History Without Changing State

| Attribute | Value |
|---|---|
| slug | `history-inspection` |
| kind | `scenario` |
| title | Inspecting History Without Changing State |
| subtitle | Use git log and git branch to understand what has already happened before acting. |
| sort_order | `4` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">History answers what already happened</div>
  <div class="commit-row">
    <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="diagram-line"></span><span class="commit-node active">c2</span>
  </div>
  <div class="label-row"><span class="branch-tag">main</span><span class="branch-tag">feature starts at c1</span><span class="head-tag">read before changing</span></div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>History inspection answers "how did we get here?"</h2>
  <p>Status tells what is pending now. History inspection tells what has already happened. <code>git log --oneline</code> shows recent commits and messages. <code>git log --oneline --graph</code> adds topology and makes branch divergence visible. <code>git branch -v</code> shows branch labels and the commit each label currently names.</p>
  <p>In recovery and collaboration scenarios, this context prevents unnecessary damage. If a commit is already reachable from a safety branch, the task may be to move a branch pointer rather than recreate the work. If two branches diverged, the task may be to integrate rather than replace.</p>
</section>
<section class="lesson-grid">
  <div class="command-slab"><code>git log --oneline</code><span>recent commits and messages</span></div>
  <div class="command-slab"><code>git log --oneline --graph</code><span>topology and parent shape</span></div>
  <div class="command-slab"><code>git branch -v</code><span>branch labels and their tip commits</span></div>
  <div class="command-slab"><code>git show &lt;commit&gt;</code><span>full detail of one commit</span></div>
</section>
<section class="lesson-panel">
  <h2>All history inspection commands are free</h2>
  <p>Spending time reading history before acting is not wasted effort. It is the habit that prevents the kind of panicked over-correction that destroys reachable work. All history inspection commands never count toward the action budget.</p>
</section>
```

**Practice connection:** `<p>After reading, use the scenarios listed below this lesson to practice history inspection before action. These scenarios are diagnostic/inspection scenarios: they do not fake success by requiring an unrelated state-changing command.</p>`

---

#### Scenario 1.4-A: read-commit-history

**Primary focus command:** `git log`
**Cumulative workflow:** This scenario introduces `git log` as the new inspection skill. It is not a fake state-changing task; the student reads history to make a decision, and later scenarios rely on this skill before switching, cherry-picking, merging, or resetting.
**Seeding status:** `requires_inspection_evaluator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `read-commit-history` |
| title | Read Commit History |
| focus | `git log` |
| summary | Use git log to identify recent commits, order, messages, and graph shape before choosing any history-sensitive action. |
| short_explanation | `git log --oneline` shows recent commits and messages. `git log --oneline --graph` adds topology so students can see whether history is linear, divergent, or merged. |
| skill_focus_type | `diagnostic_inspection` |
| primary_focus_commands | `["git log"]` |
| supporting_inspection_commands | `["git status","git branch -v","git show"]` |
| safe_demo_commands | `["git log --oneline","git log --oneline --graph"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add auth scaffold","parents":["c0"]},{"id":"c2","message":"Fix auth validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git log --oneline --graph","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["commit order","history reading","graph topology","branch reachability"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A linear history has several commits. You need to identify the latest commit and the order of recent work."
- task: "Run git log --oneline and identify the latest commit and its parent order. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline", "git branch -v"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git log --oneline"],"repository_state_unchanged":true,"must_identify":["latest_commit","commit_order"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-log-auth` | Auth history | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add auth scaffold","parents":["c0"]},{"id":"c2","message":"Fix auth validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline"]` |
| `easy-log-payment` | Payment history | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add payment scaffold","parents":["c0"]},{"id":"c2","message":"Fix payment validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline"]` |
| `easy-log-search` | Search history | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add search scaffold","parents":["c0"]},{"id":"c2","message":"Fix search validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline"]` |
| `easy-log-export` | Export history | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add export scaffold","parents":["c0"]},{"id":"c2","message":"Fix export validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline"]` |
| `easy-log-profile` | Profile history | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Add profile scaffold","parents":["c0"]},{"id":"c2","message":"Fix profile validation","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline"]` |

###### Medium

- narrative: "A feature branch diverged from main. You need to read the graph before deciding how work relates."
- task: "Run git log --oneline --graph and identify where the branch diverged. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline", "git log --oneline --graph", "git branch -v"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git log --oneline --graph"],"repository_state_unchanged":true,"must_identify":["divergence_point","branch_tips"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-log-auth` | Auth divergence | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Auth feature","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `medium-log-payment` | Payment divergence | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Payment feature","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `medium-log-search` | Search divergence | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Search feature","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `medium-log-export` | Export divergence | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Export feature","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `medium-log-profile` | Profile divergence | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Profile feature","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |

###### Hard

- narrative: "The graph has a main line, a feature branch, and a completed merge. You need to identify merge parents and reachable commits."
- task: "Use graph log output to identify the merge commit, its parents, and which branch labels point to which tips. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git log --oneline --graph"],"repository_state_unchanged":true,"must_identify":["merge_commit","merge_parents","branch_tips"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-log-auth` | Auth merged graph | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Auth feature","parents":["c0"]},{"id":"c3","message":"Merge feature/auth","parents":["c1","c2"]}],"branches":{"main":"c3","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `hard-log-payment` | Payment merged graph | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Payment feature","parents":["c0"]},{"id":"c3","message":"Merge feature/payment","parents":["c1","c2"]}],"branches":{"main":"c3","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `hard-log-search` | Search merged graph | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Search feature","parents":["c0"]},{"id":"c3","message":"Merge feature/search","parents":["c1","c2"]}],"branches":{"main":"c3","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `hard-log-export` | Export merged graph | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Export feature","parents":["c0"]},{"id":"c3","message":"Merge feature/export","parents":["c1","c2"]}],"branches":{"main":"c3","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |
| `hard-log-profile` | Profile merged graph | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Profile feature","parents":["c0"]},{"id":"c3","message":"Merge feature/profile","parents":["c1","c2"]}],"branches":{"main":"c3","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph"]` |

---

#### Scenario 1.4-B: inspect-commit-details

**Primary focus command:** `git show`
**Cumulative workflow:** This scenario introduces `git show` after `git log`. The realistic workflow is: find the relevant commit with log, then inspect that commit with show. The new command being evaluated is `git show`.
**Seeding status:** `requires_inspection_evaluator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `inspect-commit-details` |
| title | Inspect Commit Details |
| focus | `git show` |
| summary | Use git show to inspect the exact content and metadata of a selected commit. |
| short_explanation | `git show <commit>` displays a commit message, metadata, and patch. It is the focused inspection tool when the question is about one specific commit rather than the whole history. |
| skill_focus_type | `diagnostic_inspection` |
| primary_focus_commands | `["git show"]` |
| supporting_inspection_commands | `["git log --oneline","git status","git branch -v"]` |
| safe_demo_commands | `["git log --oneline","git show c1"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update auth","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git show c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["commit inspection","patch reading","commit metadata","change attribution"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A short history contains a commit with a suspicious message. You need to inspect that commit before deciding whether it is safe."
- task: "Use git log to find the commit, then git show to inspect its details. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline", "git show"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git show"],"repository_state_unchanged":true,"must_identify":["commit_message","changed_paths"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-show-auth` | Auth commit details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update auth","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c1"]` |
| `easy-show-payment` | Payment commit details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update payment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c1"]` |
| `easy-show-search` | Search commit details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update search","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c1"]` |
| `easy-show-export` | Export commit details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update export","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c1"]` |
| `easy-show-profile` | Profile commit details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update profile","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c1"]` |

###### Medium

- narrative: "Several commits have similar messages. You need to inspect the exact commit that changed the requested path."
- task: "Use log and show to identify which commit changed the requested file. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline", "git show"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git show"],"repository_state_unchanged":true,"must_identify":["changed_paths","target_commit"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-show-auth` | Auth path check | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update docs","parents":["c0"]},{"id":"c2","message":"Update auth","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c2"]` |
| `medium-show-payment` | Payment path check | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update docs","parents":["c0"]},{"id":"c2","message":"Update payment","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c2"]` |
| `medium-show-search` | Search path check | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update docs","parents":["c0"]},{"id":"c2","message":"Update search","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c2"]` |
| `medium-show-export` | Export path check | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update docs","parents":["c0"]},{"id":"c2","message":"Update export","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c2"]` |
| `medium-show-profile` | Profile path check | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Update docs","parents":["c0"]},{"id":"c2","message":"Update profile","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline","git show c2"]` |

###### Hard

- narrative: "A branch contains a merge and multiple similar commits. You need to inspect the exact commit before deciding whether to cherry-pick or reset in later workflows."
- task: "Use log graph and show to inspect the requested commit and identify its changed paths. Do not change the repository."
- policy: `(0, 0, ["git status", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git show"],"repository_state_unchanged":true,"must_identify":["target_commit","changed_paths","parent_commit"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-show-auth` | Auth merged history details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Auth feature","parents":["c0"]},{"id":"c3","message":"Merge auth","parents":["c1","c2"]}],"branches":{"main":"c3","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph","git show c2"]` |
| `hard-show-payment` | Payment merged history details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Payment feature","parents":["c0"]},{"id":"c3","message":"Merge payment","parents":["c1","c2"]}],"branches":{"main":"c3","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph","git show c2"]` |
| `hard-show-search` | Search merged history details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Search feature","parents":["c0"]},{"id":"c3","message":"Merge search","parents":["c1","c2"]}],"branches":{"main":"c3","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph","git show c2"]` |
| `hard-show-export` | Export merged history details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Export feature","parents":["c0"]},{"id":"c3","message":"Merge export","parents":["c1","c2"]}],"branches":{"main":"c3","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph","git show c2"]` |
| `hard-show-profile` | Profile merged history details | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main update","parents":["c0"]},{"id":"c2","message":"Profile feature","parents":["c0"]},{"id":"c3","message":"Merge profile","parents":["c1","c2"]}],"branches":{"main":"c3","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git log --oneline --graph","git show c2"]` |

---

---

# Module 2 — Branching and Navigation

| Attribute | Value |
|---|---|
| slug | `branching-navigation` |
| number | `2` |
| title | Branching and Navigation |
| description | Reason about HEAD, branch pointers, detached states, and safe navigation. Practice switching branches, creating branches from specific positions, and copying commits to the right place. |
| is_orientation | `False` |
| sort_order | `2` |
| assumption | Completed Module 1. Can read repository state and form clean commits. |
| goal | Student understands that branches are independent lines of work and can navigate between them safely, including rescuing work from a detached HEAD state. |

Two content lessons and one scenario-bearing lesson with five scenarios.

---

### Lesson 2.1: Branch Pointers and HEAD

| Attribute | Value |
|---|---|
| slug | `branch-head` |
| kind | `content` |
| title | Branch Pointers and HEAD |
| subtitle | How HEAD and branch labels move together and apart. |
| sort_order | `1` |

**Visual**
```html
<section class="lesson-visual split-visual">
  <div class="visual-label">Attached vs detached</div>
  <div class="state-card accent"><strong>Attached</strong><span>HEAD -&gt; main -&gt; c2</span><small>New commits move main forward.</small></div>
  <div class="state-card"><strong>Detached</strong><span>HEAD -&gt; c1</span><small>New work needs a branch name to stay reachable.</small></div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Two pointers matter most</h2>
  <p>To reason about branch work, read HEAD and the branch labels separately. HEAD tells where the working context is. A branch label tells which commit that branch currently names. When HEAD is attached to a branch, new commits move that branch label. When HEAD is detached, new commits are not attached to a branch unless you create or move a label intentionally.</p>
  <p>This is why a branch task can be wrong even when file contents look correct. If the commit lands on the wrong branch, the repository state does not match the team workflow.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Attached HEAD</h2><p>HEAD names a branch. Creating a commit moves that branch label forward to the new commit. This is the normal working state.</p></div>
  <div class="lesson-panel accent-panel"><h2>Detached HEAD</h2><p>HEAD names a commit directly. Creating a commit does not advance any branch label — the new commit floats unreachable unless you give it a label.</p></div>
</section>
<section class="lesson-panel">
  <h2>What to read before every branch operation</h2>
  <p>Before switching, creating, or moving a branch: run <code>git status</code> to confirm the working tree state, run <code>git branch -v</code> to see all branch labels and their tips, and run <code>git log --oneline --graph</code> to understand the commit topology. These three inspection commands together give the full picture and are always free.</p>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 2.2: Detached HEAD and Safe Navigation

| Attribute | Value |
|---|---|
| slug | `detached-head` |
| kind | `content` |
| title | Detached HEAD and Safe Navigation |
| subtitle | Understand detached states before making recovery decisions. |
| sort_order | `2` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Make detached work reachable</div>
  <div class="commit-row">
    <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span><span class="diagram-arrow">-></span><span class="branch-tag">feature/rescue</span>
  </div>
  <div class="label-row"><span class="head-tag">Give useful work a name before moving on</span></div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Detached HEAD is a viewpoint, not a disaster</h2>
  <p>A detached HEAD state means HEAD points directly to a commit instead of pointing through a branch label. This often happens when inspecting an old commit or checking out a specific commit hash. The risk begins when new work is created in this state — new commits are not attached to any branch, so if you move HEAD elsewhere, those commits become hard to find.</p>
  <p>The rescue mindset: keep useful work reachable. If you have done work in a detached state and want to keep it, give it a branch name before moving HEAD away. <code>git switch -c &lt;new-branch&gt;</code> creates a new branch from the current detached position and attaches HEAD to it.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>What to inspect first</h2><p>Run <code>git status</code> to confirm the detached state. Run <code>git log --oneline</code> to see the recent commit from the detached position. Run <code>git branch -v</code> to see all existing labels.</p></div>
  <div class="lesson-panel accent-panel"><h2>Returning to a branch</h2><p>If there is no new work to preserve, <code>git switch &lt;branch&gt;</code> reattaches HEAD to an existing branch. No new branch is needed.</p></div>
  <div class="lesson-panel accent-panel"><h2>Preserving new work</h2><p>If new commits or working tree changes exist in the detached state, <code>git switch -c &lt;branch&gt;</code> creates a named branch and attaches HEAD before the work is lost.</p></div>
</section>
<section class="lesson-panel">
  <h2>Changed variants, same invariant</h2>
  <p>Different variants in the branching scenarios may use different branch names, file names, and nearby history. The invariant is always the same: understand the current HEAD position, decide whether new work needs a name, and finish with HEAD attached to the intended branch in a clean state.</p>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 2.3: Moving Work to the Right Branch

| Attribute | Value |
|---|---|
| slug | `right-branch` |
| kind | `scenario` |
| title | Moving Work to the Right Branch |
| subtitle | Switch contexts, rescue detached work, and copy commits to where they belong. |
| sort_order | `3` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Three branching problems</div>
  <div class="workflow-strip">
    <span>Wrong branch?<br><small>git switch</small></span>
    <span>Detached work?<br><small>git switch -c</small></span>
    <span>Commit on wrong branch?<br><small>git cherry-pick</small></span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Branch problems come in three shapes</h2>
  <p>The scenarios in this lesson each address one common branching mistake. The first is being on the wrong branch before starting work — <code>git switch</code> corrects the context before any damage is done. The second is having done work in a detached HEAD state — <code>git switch -c</code> rescues that work by giving it a branch name. The third is having already committed work on the wrong branch — <code>git cherry-pick</code> copies the commit to the intended branch so the work lands in the right place.</p>
  <p>All three scenarios follow the same reasoning pattern: identify the current repository state, identify where the work should be, then take the smallest action that moves the work without destroying anything reachable.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Preserve</h2><p>Identify the work that must not be lost.</p></div>
  <div class="lesson-panel accent-panel"><h2>Relocate</h2><p>Make the intended branch contain the work.</p></div>
  <div class="lesson-panel accent-panel"><h2>Stabilize</h2><p>Finish with a clean working tree and a clear, attached HEAD position.</p></div>
</section>
```

**Practice connection:** `<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>`

---

#### Scenario 2.3-A: read-branch-context

**Primary focus command:** `git branch`
**Cumulative workflow:** This scenario introduces branch inspection before branch movement. It does not ask students to switch yet; it builds the prerequisite habit for safe navigation.
**Seeding status:** `requires_inspection_evaluator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `read-branch-context` |
| title | Read Branch Context |
| focus | `git branch` |
| summary | Use git branch / git branch -v to identify the current branch and branch tip commits before navigating. |
| short_explanation | `git branch` lists local branches and marks the current one. `git branch -v` adds the commit each branch points to, connecting branch names to the DAG. |
| skill_focus_type | `diagnostic_inspection` |
| primary_focus_commands | `["git branch"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph"]` |
| safe_demo_commands | `["git branch","git branch -v"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git branch","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["branch labels","HEAD","branch tips","navigation readiness"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A repository has main and one feature branch. You need to identify the current branch before switching in later scenarios."
- task: "Run git branch or git branch -v and identify the current branch and available branch names."
- policy: `(0, 0, ["git status", "git branch", "git branch -v", "git log --oneline"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git branch"],"repository_state_unchanged":true,"must_identify":["current_branch","available_branches"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-branch-auth` | Auth branch list | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `easy-branch-payment` | Payment branch list | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `easy-branch-search` | Search branch list | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `easy-branch-export` | Export branch list | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `easy-branch-profile` | Profile branch list | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |

###### Medium

- narrative: "Several branch labels point to different commits. You need to identify which branch has the latest feature work."
- task: "Use git branch -v and log to identify branch tips. Do not switch yet."
- policy: `(0, 0, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git branch -v"],"repository_state_unchanged":true,"must_identify":["branch_tips","current_branch"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-branch-auth` | Auth branch tips | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Auth work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `medium-branch-payment` | Payment branch tips | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Payment work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `medium-branch-search` | Search branch tips | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Search work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `medium-branch-export` | Export branch tips | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Export work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |
| `medium-branch-profile` | Profile branch tips | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Profile work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v"]` |

###### Hard

- narrative: "A graph has multiple feature and stale branches. You need to read branch context without moving HEAD."
- task: "Use branch and graph inspection to identify current branch, stale branch, and active feature branch."
- policy: `(0, 0, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"completion_type":"inspection","required_commands":["git branch -v"],"repository_state_unchanged":true,"must_identify":["current_branch","active_feature_branch","stale_branch"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-branch-auth` | Auth branch context | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Auth work","parents":["c0"]},{"id":"c3","message":"Old spike","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2","spike/old":"c3","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v","git log --oneline --graph"]` |
| `hard-branch-payment` | Payment branch context | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Payment work","parents":["c0"]},{"id":"c3","message":"Old spike","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2","spike/old":"c3","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v","git log --oneline --graph"]` |
| `hard-branch-search` | Search branch context | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Search work","parents":["c0"]},{"id":"c3","message":"Old spike","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2","spike/old":"c3","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v","git log --oneline --graph"]` |
| `hard-branch-export` | Export branch context | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Export work","parents":["c0"]},{"id":"c3","message":"Old spike","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2","spike/old":"c3","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v","git log --oneline --graph"]` |
| `hard-branch-profile` | Profile branch context | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Profile work","parents":["c0"]},{"id":"c3","message":"Old spike","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2","spike/old":"c3","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -v","git log --oneline --graph"]` |

---

#### Scenario 2.3-B: switch-correct-branch

**Primary focus command:** `git switch`
**Cumulative workflow:** This scenario introduces `git switch` as the new counted command. `git branch -v` and `git status` are expected support; the evaluated state change is HEAD moving to the correct existing branch.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `switch-correct-branch` |
| title | Switch to the Correct Branch |
| focus | `git switch` |
| summary | Move HEAD to the branch where the next work belongs after inspecting branch context. |
| short_explanation | `git switch <branch>` moves HEAD to an existing branch and updates the working tree to that branch. It should be used after checking branch context. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git switch"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline"]` |
| safe_demo_commands | `["git status","git branch -v","git switch feature/auth"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch feature/auth","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["HEAD","branch navigation","working tree context"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "You are on main, but the next edit belongs on an existing feature branch."
- task: "Switch to the correct feature branch. Do not create a new branch and do not commit."
- policy: `(1, 3, ["git status", "git branch", "git branch -v", "git log --oneline"])`
- target_rule: `{"head_branch":"feature/<topic>","working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-switch-auth` | Switch to feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth"]` |
| `easy-switch-payment` | Switch to feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment"]` |
| `easy-switch-search` | Switch to feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search"]` |
| `easy-switch-export` | Switch to feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export"]` |
| `easy-switch-profile` | Switch to feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile"]` |

###### Medium

- narrative: "Several branches exist and only one branch matches the requested task."
- task: "Inspect branch names and switch to the correct feature branch."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline"])`
- target_rule: `{"head_branch":"feature/<topic>","working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-switch-auth` | Switch among multiple branches to feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0","spike/old":"c0","docs/reference":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth"]` |
| `medium-switch-payment` | Switch among multiple branches to feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c0","spike/old":"c0","docs/reference":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment"]` |
| `medium-switch-search` | Switch among multiple branches to feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c0","spike/old":"c0","docs/reference":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search"]` |
| `medium-switch-export` | Switch among multiple branches to feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c0","spike/old":"c0","docs/reference":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export"]` |
| `medium-switch-profile` | Switch among multiple branches to feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c0","spike/old":"c0","docs/reference":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile"]` |

###### Hard

- narrative: "You are currently on the wrong feature branch. The correct branch has a similar name and different tip."
- task: "Use branch context and switch to the correct branch without changing commits."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"feature/<topic>","working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-switch-auth` | Switch from similar wrong branch to feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c1","feature/auth-draft":"c0","spike/old":"c0"},"head":{"type":"branch","name":"feature/auth-draft"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth"]` |
| `hard-switch-payment` | Switch from similar wrong branch to feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c1","feature/payment-draft":"c0","spike/old":"c0"},"head":{"type":"branch","name":"feature/payment-draft"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment"]` |
| `hard-switch-search` | Switch from similar wrong branch to feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c1","feature/search-draft":"c0","spike/old":"c0"},"head":{"type":"branch","name":"feature/search-draft"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search"]` |
| `hard-switch-export` | Switch from similar wrong branch to feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c1","feature/export-draft":"c0","spike/old":"c0"},"head":{"type":"branch","name":"feature/export-draft"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export"]` |
| `hard-switch-profile` | Switch from similar wrong branch to feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c1","feature/profile-draft":"c0","spike/old":"c0"},"head":{"type":"branch","name":"feature/profile-draft"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile"]` |

---

#### Scenario 2.3-C: create-branch-from-starting-point

**Primary focus command:** `git switch -c`
**Cumulative workflow:** This scenario introduces the branch-creation command family. Prior `git switch` may be used to reach the intended starting point before creating the new branch.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `create-branch-from-starting-point` |
| title | Create Branch from the Correct Starting Point |
| focus | `git switch -c` |
| summary | Create a new branch from the correct commit after inspecting the current branch and history. |
| short_explanation | `git switch -c <branch>` creates a new branch and switches HEAD to it. The important skill is creating it from the correct starting point, not merely creating any branch. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git switch -c"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph"]` |
| safe_demo_commands | `["git status","git branch -v","git switch main","git switch -c feature/auth"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch main","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch -c feature/auth","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["branch creation","starting point","HEAD","branch pointers"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "You are on main and need a new feature branch starting from the current main commit."
- task: "Create and switch to the requested feature branch from main."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline"])`
- target_rule: `{"head_branch":"feature/<topic>","branch_exists":["feature/<topic>"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-create-auth` | Create feature/auth from main | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch -c feature/auth"]` |
| `easy-create-payment` | Create feature/payment from main | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch -c feature/payment"]` |
| `easy-create-search` | Create feature/search from main | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch -c feature/search"]` |
| `easy-create-export` | Create feature/export from main | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch -c feature/export"]` |
| `easy-create-profile` | Create feature/profile from main | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch -c feature/profile"]` |

###### Medium

- narrative: "You are on a documentation branch, but the feature branch must start from main."
- task: "Switch to main first, then create the requested feature branch from main."
- policy: `(2, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"feature/<topic>","branch_exists":["feature/<topic>"],"branch_points_to":{"feature/<topic>":"c1"},"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-create-auth` | Create feature/auth from main, not docs | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"docs/reference"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git switch -c feature/auth"]` |
| `medium-create-payment` | Create feature/payment from main, not docs | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"docs/reference"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git switch -c feature/payment"]` |
| `medium-create-search` | Create feature/search from main, not docs | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"docs/reference"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git switch -c feature/search"]` |
| `medium-create-export` | Create feature/export from main, not docs | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"docs/reference"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git switch -c feature/export"]` |
| `medium-create-profile` | Create feature/profile from main, not docs | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"docs/reference"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git switch -c feature/profile"]` |

###### Hard

- narrative: "There are multiple plausible starting branches. The new feature must start from release/base, not main."
- task: "Inspect branch tips, switch to release/base, then create the requested feature branch."
- policy: `(2, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"feature/<topic>","branch_exists":["feature/<topic>"],"branch_points_to":{"feature/<topic>":"c2"},"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-create-auth` | Create feature/auth from release/base | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Release base","parents":["c0"]}],"branches":{"main":"c1","release/base":"c2","spike/old":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch release/base","git switch -c feature/auth"]` |
| `hard-create-payment` | Create feature/payment from release/base | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Release base","parents":["c0"]}],"branches":{"main":"c1","release/base":"c2","spike/old":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch release/base","git switch -c feature/payment"]` |
| `hard-create-search` | Create feature/search from release/base | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Release base","parents":["c0"]}],"branches":{"main":"c1","release/base":"c2","spike/old":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch release/base","git switch -c feature/search"]` |
| `hard-create-export` | Create feature/export from release/base | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Release base","parents":["c0"]}],"branches":{"main":"c1","release/base":"c2","spike/old":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch release/base","git switch -c feature/export"]` |
| `hard-create-profile` | Create feature/profile from release/base | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"Release base","parents":["c0"]}],"branches":{"main":"c1","release/base":"c2","spike/old":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch release/base","git switch -c feature/profile"]` |

---

#### Scenario 2.3-D: cherry-pick-to-branch

**Primary focus command:** `git cherry-pick`
**Cumulative workflow:** This scenario introduces `git cherry-pick` as the new command. `git switch` is an expected prior action when HEAD is not already on the destination branch.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `cherry-pick-to-branch` |
| title | Copy a Commit to the Right Branch |
| focus | `git cherry-pick` |
| summary | Copy an existing commit onto the branch where it belongs after identifying the commit in history. |
| short_explanation | `git cherry-pick <commit>` replays one existing commit onto the current branch. The realistic workflow is log inspection, switch to destination, then cherry-pick the selected commit. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git cherry-pick"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git show"]` |
| safe_demo_commands | `["git log --oneline","git switch feature/auth","git cherry-pick c1"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch feature/auth","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git cherry-pick c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["commit identity","branch destination","history replay","wrong-branch recovery"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A feature commit landed on main by mistake. The correct destination branch already exists."
- task: "Switch to the feature branch and cherry-pick the misplaced commit."
- policy: `(2, 5, ["git status", "git log --oneline", "git branch -v"])`
- target_rule: `{"head_branch":"feature/<topic>","min_commits_on_branch":{"feature/<topic>":2},"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-cherry-auth` | Cherry-pick auth commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth","git cherry-pick c1"]` |
| `easy-cherry-payment` | Cherry-pick payment commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment","git cherry-pick c1"]` |
| `easy-cherry-search` | Cherry-pick search commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search","git cherry-pick c1"]` |
| `easy-cherry-export` | Cherry-pick export commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export","git cherry-pick c1"]` |
| `easy-cherry-profile` | Cherry-pick profile commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile","git cherry-pick c1"]` |

###### Medium

- narrative: "There is a distractor spike commit. Only the feature commit from main belongs on the feature branch."
- task: "Identify the correct commit, switch to the feature branch, and cherry-pick only that commit."
- policy: `(2, 5, ["git status", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","min_commits_on_branch":{"feature/<topic>":2},"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-cherry-auth` | Cherry-pick auth with distractor | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Spike work","parents":["c0"]},{"id":"c2","message":"auth work","parents":["c0"]}],"branches":{"main":"c2","feature/auth":"c0","spike/old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth","git cherry-pick c2"]` |
| `medium-cherry-payment` | Cherry-pick payment with distractor | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Spike work","parents":["c0"]},{"id":"c2","message":"payment work","parents":["c0"]}],"branches":{"main":"c2","feature/payment":"c0","spike/old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment","git cherry-pick c2"]` |
| `medium-cherry-search` | Cherry-pick search with distractor | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Spike work","parents":["c0"]},{"id":"c2","message":"search work","parents":["c0"]}],"branches":{"main":"c2","feature/search":"c0","spike/old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search","git cherry-pick c2"]` |
| `medium-cherry-export` | Cherry-pick export with distractor | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Spike work","parents":["c0"]},{"id":"c2","message":"export work","parents":["c0"]}],"branches":{"main":"c2","feature/export":"c0","spike/old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export","git cherry-pick c2"]` |
| `medium-cherry-profile` | Cherry-pick profile with distractor | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Spike work","parents":["c0"]},{"id":"c2","message":"profile work","parents":["c0"]}],"branches":{"main":"c2","feature/profile":"c0","spike/old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile","git cherry-pick c2"]` |

###### Hard

- narrative: "Two related feature commits are on main after an unrelated hotfix. Only the feature commits should be copied to the feature branch."
- task: "Switch to the feature branch and cherry-pick the two feature commits in order."
- policy: `(3, 6, ["git status", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","min_commits_on_branch":{"feature/<topic>":3},"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-cherry-auth` | Cherry-pick two auth commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Hotfix","parents":["c0"]},{"id":"c2","message":"auth work A","parents":["c1"]},{"id":"c3","message":"auth work B","parents":["c2"]}],"branches":{"main":"c3","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/auth","git cherry-pick c2","git cherry-pick c3"]` |
| `hard-cherry-payment` | Cherry-pick two payment commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Hotfix","parents":["c0"]},{"id":"c2","message":"payment work A","parents":["c1"]},{"id":"c3","message":"payment work B","parents":["c2"]}],"branches":{"main":"c3","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/payment","git cherry-pick c2","git cherry-pick c3"]` |
| `hard-cherry-search` | Cherry-pick two search commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Hotfix","parents":["c0"]},{"id":"c2","message":"search work A","parents":["c1"]},{"id":"c3","message":"search work B","parents":["c2"]}],"branches":{"main":"c3","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/search","git cherry-pick c2","git cherry-pick c3"]` |
| `hard-cherry-export` | Cherry-pick two export commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Hotfix","parents":["c0"]},{"id":"c2","message":"export work A","parents":["c1"]},{"id":"c3","message":"export work B","parents":["c2"]}],"branches":{"main":"c3","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/export","git cherry-pick c2","git cherry-pick c3"]` |
| `hard-cherry-profile` | Cherry-pick two profile commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Hotfix","parents":["c0"]},{"id":"c2","message":"profile work A","parents":["c1"]},{"id":"c3","message":"profile work B","parents":["c2"]}],"branches":{"main":"c3","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch feature/profile","git cherry-pick c2","git cherry-pick c3"]` |

---

#### Scenario 2.3-E: delete-stale-branch

**Primary focus command:** `git branch -d`
**Cumulative workflow:** This scenario introduces branch deletion as a branch-management skill after students understand branch pointers and history. It belongs with branch navigation rather than as an isolated collaboration command.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `delete-stale-branch` |
| title | Delete a Stale Local Branch |
| focus | `git branch -d` |
| summary | Remove a local branch only after confirming its work is already integrated or no longer needed. |
| short_explanation | `git branch -d <branch>` deletes a local branch label. It should be used after inspecting branch tips and ensuring the branch is safe to remove. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git branch -d"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph"]` |
| safe_demo_commands | `["git branch -v","git branch -d feature/old"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -d feature/old","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["branch cleanup","stale branch","reachable work","branch labels"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A finished feature branch points to the same commit as main. It is safe to delete the local branch label."
- task: "Delete the stale feature branch and stay on main."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","branch_absent":["feature/<topic>"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-delete-auth` | Delete merged feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/auth"]` |
| `easy-delete-payment` | Delete merged feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/payment"]` |
| `easy-delete-search` | Delete merged feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/search"]` |
| `easy-delete-export` | Delete merged feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/export"]` |
| `easy-delete-profile` | Delete merged feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/profile"]` |

###### Medium

- narrative: "Several branches exist. Only one is already merged and safe to delete."
- task: "Inspect branch tips and delete only the stale branch."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","branch_absent":["feature/<topic>-old"],"branch_exists":["feature/<topic>"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-delete-auth` | Delete old auth branch only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0","feature/auth-old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/auth-old"]` |
| `medium-delete-payment` | Delete old payment branch only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c0","feature/payment-old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/payment-old"]` |
| `medium-delete-search` | Delete old search branch only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c0","feature/search-old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/search-old"]` |
| `medium-delete-export` | Delete old export branch only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c0","feature/export-old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/export-old"]` |
| `medium-delete-profile` | Delete old profile branch only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c0","feature/profile-old":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/profile-old"]` |

###### Hard

- narrative: "There are active, stale, and reference branches with similar names. Delete only the stale branch label."
- task: "Use branch and graph inspection, then delete only the branch already represented by main."
- policy: `(1, 3, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","branch_absent":["feature/<topic>-done"],"branch_exists":["feature/<topic>","docs/reference"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-delete-auth` | Delete done auth branch among similar branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0","feature/auth-done":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/auth-done"]` |
| `hard-delete-payment` | Delete done payment branch among similar branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c0","feature/payment-done":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/payment-done"]` |
| `hard-delete-search` | Delete done search branch among similar branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c0","feature/search-done":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/search-done"]` |
| `hard-delete-export` | Delete done export branch among similar branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c0","feature/export-done":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/export-done"]` |
| `hard-delete-profile` | Delete done profile branch among similar branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c0","feature/profile-done":"c1","docs/reference":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git branch -d feature/profile-done"]` |

---


---

# Module 3 — Collaboration and Integration

| Attribute | Value |
|---|---|
| slug | `collaboration-integration` |
| number | `3` |
| title | Collaboration and Integration |
| description | Integrate divergent branches, understand merge types, resolve conflicts, and clean up finished work. Practice the full integration workflow from inspection through cleanup. |
| is_orientation | `False` |
| sort_order | `3` |
| assumption | Completed Module 2. Can navigate branches safely and understands HEAD. |
| goal | Student can integrate divergent branches, read and resolve conflict state, and clean up stale labels after integration. |

Two content lessons and one scenario-bearing lesson with seven scenarios.

---

### Lesson 3.1: Understanding Merge Types

| Attribute | Value |
|---|---|
| slug | `merge-types` |
| kind | `content` |
| title | Understanding Merge Types |
| subtitle | How fast-forward and true merge commits differ, and when each appears. |
| sort_order | `1` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Two merge outcomes</div>
  <div class="area-row">
    <div class="area-card accent">
      <span>Fast-forward</span>
      <strong>No merge commit</strong>
      <small>Branch label moves forward. No divergence existed.</small>
    </div>
    <span class="diagram-arrow">vs</span>
    <div class="area-card">
      <span>True merge</span>
      <strong>Merge commit with two parents</strong>
      <small>Branches diverged. Integration recorded in history.</small>
    </div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Merge outcome depends on graph shape</h2>
  <p>When you run <code>git merge &lt;branch&gt;</code>, Git inspects the graph to decide what kind of merge to perform. If the current branch tip is a direct ancestor of the branch being merged, Git performs a fast-forward merge — the branch label simply moves forward to the tip of the incoming branch. No merge commit is created.</p>
  <p>If the two branches have diverged — meaning each has commits the other does not — Git creates a true merge commit with two parents. The merge commit records the fact that two lines of work were integrated at this point.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Fast-forward merge</h2><p>Occurs when the current branch tip is an ancestor of the incoming branch. The graph stays linear. No merge commit is added to history.</p></div>
  <div class="lesson-panel accent-panel"><h2>True merge commit</h2><p>Occurs when both branches have diverged from a shared ancestor. A new commit with two parents converges the two lines.</p></div>
</section>
<section class="lesson-panel">
  <h2>Why the distinction matters</h2>
  <p>Conflicts arise only in true merges, not in fast-forward merges, because fast-forward merges have no competing histories to reconcile. When both branches changed the same region of the same file since their shared ancestor, Git pauses and asks you to resolve the conflict before completing the merge commit. Understanding why the merge commit has two parents makes it easier to reason about what the final graph should look like.</p>
</section>
<pre><code>git log --oneline --graph
git branch -v
# Read the topology before merging to predict whether the result will be a fast-forward or a true merge commit.</code></pre>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 3.2: Divergent Branches and Merge Recovery

| Attribute | Value |
|---|---|
| slug | `divergence-merge` |
| kind | `scenario` |
| title | Divergent Branches and Merge Recovery |
| subtitle | Integrate divergent branches, resolve conflicts, and remove stale labels cleanly. |
| sort_order | `2` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Three integration problems</div>
  <div class="workflow-strip">
    <span>Diverged branches?<br><small>git merge</small></span>
    <span>Conflict paused?<br><small>git add + git commit</small></span>
    <span>Stale label after merge?<br><small>git branch -d</small></span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Integration problems come in three shapes</h2>
  <p>The scenarios in this lesson address the three most common integration situations. The first is a straightforward divergent-branch merge where no conflict exists. The second is a paused merge caused by a conflict — the student must mark the conflict resolved and complete the merge commit. The third is cleanup after integration — the student identifies a stale branch label whose work is now reachable from the integration branch and removes it safely.</p>
  <p>All three follow the same underlying reasoning: identify the repository state, decide what action moves the work toward the correct integrated shape, and verify the result. The evaluator checks repository state rather than one prescribed command sequence.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Divergence is not failure</h2><p>Two branches having separate histories is expected team workflow. The merge brings those histories together in a new commit with two parents.</p></div>
  <div class="lesson-panel accent-panel"><h2>Conflict is not corruption</h2><p>A conflict is a structured pause. Git knows which files need human input. The merge is not finished until the conflict is staged and the merge commit is recorded.</p></div>
  <div class="lesson-panel accent-panel"><h2>Cleanup is not deletion</h2><p><code>git branch -d</code> removes a label, not commits. Work reachable from the integration branch remains in history regardless of the label's presence.</p></div>
</section>
```

**Practice connection:** `<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>`

---

#### Scenario 3.2-A: clone-project-and-inspect

**Primary focus command:** `git clone`
**Cumulative workflow:** This scenario introduces `git clone` through the real onboarding workflow: clone, then inspect the local repository that was created. It is not a one-command stop point.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires remote repository metadata and `git clone` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `clone-project-and-inspect` |
| title | Clone Project and Inspect Starting State |
| focus | `git clone` |
| summary | Create a local working copy from a remote repository, then inspect branch and history context before working. |
| short_explanation | `git clone <url>` creates a local repository from a remote source and configures the default remote. The realistic workflow continues with status, branch, and log inspection. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git clone"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline"]` |
| safe_demo_commands | `["git clone origin-url project","git status","git branch -v","git log --oneline"]` |
| demo_repository_state | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"r1"}}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git clone origin-url project","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["remote repository","local clone","origin","starting history"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "You have been given a project repository URL and need a local working copy."
- task: "Clone the repository, inspect status, and confirm the main branch and starter history."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline"])`
- target_rule: `{"repository_initialized":true,"remote_exists":["origin"],"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-clone-auth` | Clone auth project | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"r1"}}` | `["git clone https://example.test/auth.git auth-project","git status","git branch -v"]` |
| `easy-clone-payment` | Clone payment project | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"r1"}}` | `["git clone https://example.test/payment.git payment-project","git status","git branch -v"]` |
| `easy-clone-search` | Clone search project | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"r1"}}` | `["git clone https://example.test/search.git search-project","git status","git branch -v"]` |
| `easy-clone-export` | Clone export project | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"r1"}}` | `["git clone https://example.test/export.git export-project","git status","git branch -v"]` |
| `easy-clone-profile` | Clone profile project | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"r1"}}` | `["git clone https://example.test/profile.git profile-project","git status","git branch -v"]` |

###### Medium

- narrative: "The cloned project has a main branch and a remote feature branch. You need to inspect what was cloned before working."
- task: "Clone, inspect local branch state, and identify the available remote-tracking branch."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline", "git log --oneline --graph"])`
- target_rule: `{"repository_initialized":true,"remote_exists":["origin"],"head_branch":"main","remote_branch_exists":["origin/feature/<topic>"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-clone-auth` | Clone auth project with remote feature | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"r1","origin/feature/auth":"r2"}}` | `["git clone https://example.test/auth.git auth-project","git branch -v","git log --oneline --graph"]` |
| `medium-clone-payment` | Clone payment project with remote feature | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"r1","origin/feature/payment":"r2"}}` | `["git clone https://example.test/payment.git payment-project","git branch -v","git log --oneline --graph"]` |
| `medium-clone-search` | Clone search project with remote feature | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"r1","origin/feature/search":"r2"}}` | `["git clone https://example.test/search.git search-project","git branch -v","git log --oneline --graph"]` |
| `medium-clone-export` | Clone export project with remote feature | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"r1","origin/feature/export":"r2"}}` | `["git clone https://example.test/export.git export-project","git branch -v","git log --oneline --graph"]` |
| `medium-clone-profile` | Clone profile project with remote feature | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"r1","origin/feature/profile":"r2"}}` | `["git clone https://example.test/profile.git profile-project","git branch -v","git log --oneline --graph"]` |

###### Hard

- narrative: "The cloned project has multiple remote-tracking branches. You need to inspect the correct starting point before any local work."
- task: "Clone and inspect local and remote branch context. Do not create or commit yet."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"repository_initialized":true,"remote_exists":["origin"],"head_branch":"main","remote_branch_exists":["origin/main","origin/release/base","origin/feature/<topic>"],"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-clone-auth` | Clone auth project with multiple remotes | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"r2","origin/release/base":"r1","origin/feature/auth":"r3"}}` | `["git clone https://example.test/auth.git auth-project","git branch -v","git log --oneline --graph"]` |
| `hard-clone-payment` | Clone payment project with multiple remotes | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"r2","origin/release/base":"r1","origin/feature/payment":"r3"}}` | `["git clone https://example.test/payment.git payment-project","git branch -v","git log --oneline --graph"]` |
| `hard-clone-search` | Clone search project with multiple remotes | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"r2","origin/release/base":"r1","origin/feature/search":"r3"}}` | `["git clone https://example.test/search.git search-project","git branch -v","git log --oneline --graph"]` |
| `hard-clone-export` | Clone export project with multiple remotes | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"r2","origin/release/base":"r1","origin/feature/export":"r3"}}` | `["git clone https://example.test/export.git export-project","git branch -v","git log --oneline --graph"]` |
| `hard-clone-profile` | Clone profile project with multiple remotes | `{"commits":[],"branches":{"main":null},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"repository_initialized":false,"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"r2","origin/release/base":"r1","origin/feature/profile":"r3"}}` | `["git clone https://example.test/profile.git profile-project","git branch -v","git log --oneline --graph"]` |

---

#### Scenario 3.2-B: connect-remote-origin

**Primary focus command:** `git remote`
**Cumulative workflow:** This scenario introduces remote configuration as the new skill. The repository already has local commits; adding `origin` prepares it for later fetch/pull/push workflows.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires `git remote add` and `git remote -v` support plus remote metadata in RepositoryState.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `connect-remote-origin` |
| title | Connect a Local Repository to a Remote |
| focus | `git remote` |
| summary | Add and verify a remote named origin for an existing local repository. |
| short_explanation | `git remote add origin <url>` records the remote repository location. `git remote -v` verifies fetch/push URLs before fetch, pull, or push workflows. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git remote"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git branch -v"]` |
| safe_demo_commands | `["git remote add origin https://example.test/app.git","git remote -v"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git remote add origin https://example.test/app.git","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git remote -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["remote configuration","origin","fetch URL","push URL"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "You have a local repository with one commit and need to connect it to the class remote."
- task: "Add origin as the remote and verify it."
- policy: `(1, 3, ["git status", "git remote -v", "git log --oneline"])`
- target_rule: `{"remote_exists":["origin"],"remote_url_matches":{"origin":"<url>"},"head_branch":"main"}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-remote-auth` | Connect auth local repo | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/auth.git","git remote -v"]` |
| `easy-remote-payment` | Connect payment local repo | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/payment.git","git remote -v"]` |
| `easy-remote-search` | Connect search local repo | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/search.git","git remote -v"]` |
| `easy-remote-export` | Connect export local repo | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/export.git","git remote -v"]` |
| `easy-remote-profile` | Connect profile local repo | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/profile.git","git remote -v"]` |

###### Medium

- narrative: "The repository has local branches but no remote configured. You need to add origin without changing branches or commits."
- task: "Add origin and verify the remote configuration."
- policy: `(1, 3, ["git status", "git remote -v", "git branch -v"])`
- target_rule: `{"remote_exists":["origin"],"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-remote-auth` | Connect auth repo with branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/auth.git","git remote -v"]` |
| `medium-remote-payment` | Connect payment repo with branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/payment.git","git remote -v"]` |
| `medium-remote-search` | Connect search repo with branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/search.git","git remote -v"]` |
| `medium-remote-export` | Connect export repo with branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/export.git","git remote -v"]` |
| `medium-remote-profile` | Connect profile repo with branches | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{}}` | `["git remote add origin https://example.test/profile.git","git remote -v"]` |

###### Hard

- narrative: "A repository has a wrongly named placeholder remote. You need to add the correct origin after inspection."
- task: "Inspect remote configuration, add origin with the requested URL, and leave commits unchanged."
- policy: `(1, 4, ["git status", "git remote -v", "git branch -v", "git log --oneline"])`
- target_rule: `{"remote_exists":["origin"],"remote_url_matches":{"origin":"<url>"},"repository_state_unchanged_except":["remotes"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-remote-auth` | Add origin with existing placeholder remote | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"backup":"https://example.test/backup-auth.git"}}` | `["git remote add origin https://example.test/auth.git","git remote -v"]` |
| `hard-remote-payment` | Add origin with existing placeholder remote | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"backup":"https://example.test/backup-payment.git"}}` | `["git remote add origin https://example.test/payment.git","git remote -v"]` |
| `hard-remote-search` | Add origin with existing placeholder remote | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"backup":"https://example.test/backup-search.git"}}` | `["git remote add origin https://example.test/search.git","git remote -v"]` |
| `hard-remote-export` | Add origin with existing placeholder remote | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"backup":"https://example.test/backup-export.git"}}` | `["git remote add origin https://example.test/export.git","git remote -v"]` |
| `hard-remote-profile` | Add origin with existing placeholder remote | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"backup":"https://example.test/backup-profile.git"}}` | `["git remote add origin https://example.test/profile.git","git remote -v"]` |

---

#### Scenario 3.2-C: fetch-remote-updates

**Primary focus command:** `git fetch`
**Cumulative workflow:** This introduces `git fetch` as the safe inspection/update command before deciding whether to merge or pull. It supports later integration without automatically moving local work.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires remote-tracking branch support and `git fetch` processing.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `fetch-remote-updates` |
| title | Fetch Remote Updates |
| focus | `git fetch` |
| summary | Download remote-tracking updates without changing the current working branch. |
| short_explanation | `git fetch` updates remote-tracking refs such as `origin/main` while leaving the current local branch and working tree unchanged. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git fetch"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph"]` |
| safe_demo_commands | `["git status","git fetch origin","git log --oneline --graph"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git fetch origin","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git log --oneline --graph","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["remote tracking","upstream branch","synchronization","clean working tree"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "The remote has one new commit and your working tree is clean."
- task: "Use git fetch in the correct branch workflow, then inspect the result."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"remote_tracking_updated":true,"branches_equal":[]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-fetch-auth` | Fetch Remote Updates for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `easy-fetch-payment` | Fetch Remote Updates for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `easy-fetch-search` | Fetch Remote Updates for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `easy-fetch-export` | Fetch Remote Updates for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `easy-fetch-profile` | Fetch Remote Updates for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |

###### Medium

- narrative: "The remote has updates and a feature branch exists locally. You must synchronize the correct current branch only."
- task: "Inspect the branch context, run git fetch, and verify the expected refs/branch result."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-fetch-auth` | Fetch Remote Updates with feature branch for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1","origin/feature/auth":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `medium-fetch-payment` | Fetch Remote Updates with feature branch for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1","origin/feature/payment":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `medium-fetch-search` | Fetch Remote Updates with feature branch for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1","origin/feature/search":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `medium-fetch-export` | Fetch Remote Updates with feature branch for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1","origin/feature/export":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `medium-fetch-profile` | Fetch Remote Updates with feature branch for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1","origin/feature/profile":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |

###### Hard

- narrative: "Multiple remote-tracking branches have changed. You must update/synchronize without disturbing local feature branches."
- task: "Use branch/history inspection and run git fetch only in the intended synchronization workflow."
- policy: `(1, 5, ["git status", "git branch -v", "git log --oneline --graph", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-fetch-auth` | Fetch Remote Updates with multiple remote branches for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1","origin/feature/auth":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `hard-fetch-payment` | Fetch Remote Updates with multiple remote branches for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1","origin/feature/payment":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `hard-fetch-search` | Fetch Remote Updates with multiple remote branches for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1","origin/feature/search":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `hard-fetch-export` | Fetch Remote Updates with multiple remote branches for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1","origin/feature/export":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |
| `hard-fetch-profile` | Fetch Remote Updates with multiple remote branches for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1","origin/feature/profile":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git fetch origin"]` |

---

#### Scenario 3.2-D: pull-before-local-work

**Primary focus command:** `git pull`
**Cumulative workflow:** This introduces `git pull` through a realistic synchronization workflow: inspect clean state, pull the upstream update, then confirm the local branch is current.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires upstream tracking, remote refs, fetch behavior, and merge/fast-forward pull behavior.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `pull-before-local-work` |
| title | Pull Latest Work Before Editing |
| focus | `git pull` |
| summary | Integrate upstream changes into the current branch before starting local edits. |
| short_explanation | `git pull` fetches and integrates the upstream branch into the current branch. It should be used only after checking branch and working-tree cleanliness. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git pull"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph"]` |
| safe_demo_commands | `["git status","git pull","git log --oneline --graph"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git pull","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git log --oneline --graph","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["remote tracking","upstream branch","synchronization","clean working tree"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "The remote has one new commit and your working tree is clean."
- task: "Use git pull in the correct branch workflow, then inspect the result."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"remote_tracking_updated":false,"branches_equal":[["main","origin/main"]]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-pull-auth` | Pull Latest Work Before Editing for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `easy-pull-payment` | Pull Latest Work Before Editing for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `easy-pull-search` | Pull Latest Work Before Editing for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `easy-pull-export` | Pull Latest Work Before Editing for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `easy-pull-profile` | Pull Latest Work Before Editing for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |

###### Medium

- narrative: "The remote has updates and a feature branch exists locally. You must synchronize the correct current branch only."
- task: "Inspect the branch context, run git pull, and verify the expected refs/branch result."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-pull-auth` | Pull Latest Work Before Editing with feature branch for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1","origin/feature/auth":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `medium-pull-payment` | Pull Latest Work Before Editing with feature branch for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1","origin/feature/payment":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `medium-pull-search` | Pull Latest Work Before Editing with feature branch for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1","origin/feature/search":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `medium-pull-export` | Pull Latest Work Before Editing with feature branch for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1","origin/feature/export":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `medium-pull-profile` | Pull Latest Work Before Editing with feature branch for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1","origin/feature/profile":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |

###### Hard

- narrative: "Multiple remote-tracking branches have changed. You must update/synchronize without disturbing local feature branches."
- task: "Use branch/history inspection and run git pull only in the intended synchronization workflow."
- policy: `(1, 5, ["git status", "git branch -v", "git log --oneline --graph", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-pull-auth` | Pull Latest Work Before Editing with multiple remote branches for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c1","origin/feature/auth":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `hard-pull-payment` | Pull Latest Work Before Editing with multiple remote branches for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c1","origin/feature/payment":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `hard-pull-search` | Pull Latest Work Before Editing with multiple remote branches for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c1","origin/feature/search":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `hard-pull-export` | Pull Latest Work Before Editing with multiple remote branches for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c1","origin/feature/export":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |
| `hard-pull-profile` | Pull Latest Work Before Editing with multiple remote branches for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c1","origin/feature/profile":"c2","origin/release/base":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git pull"]` |

---

#### Scenario 3.2-E: merge-feature-branch

**Primary focus command:** `git merge`
**Cumulative workflow:** This scenario introduces `git merge`. Prior branch inspection and switching are expected because a merge result depends on the current branch.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `merge-feature-branch` |
| title | Merge a Feature Branch |
| focus | `git merge` |
| summary | Integrate a completed feature branch into the current branch after reading divergence and branch context. |
| short_explanation | `git merge <branch>` integrates another branch into the current branch. The current branch matters: merge receives into HEAD. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git merge"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph","git show"]` |
| safe_demo_commands | `["git status","git branch -v","git switch main","git merge feature/auth"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth feature","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch main","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git merge feature/auth","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["merge target","fast-forward merge","merge commit","branch integration"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A completed feature branch is ahead of main with no divergence."
- task: "Merge the feature branch into main and finish on main with a clean repository."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","branches_equal":[["main","feature/<topic>"]],"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-merge-auth` | Fast-forward merge feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth feature","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/auth"]` |
| `easy-merge-payment` | Fast-forward merge feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment feature","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/payment"]` |
| `easy-merge-search` | Fast-forward merge feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search feature","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/search"]` |
| `easy-merge-export` | Fast-forward merge feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export feature","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/export"]` |
| `easy-merge-profile` | Fast-forward merge feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile feature","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/profile"]` |

###### Medium

- narrative: "Main and a feature branch have diverged. The feature must be merged into main."
- task: "Stay or switch to main, merge the feature branch, and finish clean."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","min_commits_on_branch":{"main":4},"working_tree_clean":true,"staging_empty":true,"conflict_free":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-merge-auth` | True merge feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"auth feature","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/auth"]` |
| `medium-merge-payment` | True merge feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"payment feature","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/payment"]` |
| `medium-merge-search` | True merge feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"search feature","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/search"]` |
| `medium-merge-export` | True merge feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"export feature","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/export"]` |
| `medium-merge-profile` | True merge feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"profile feature","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git merge feature/profile"]` |

###### Hard

- narrative: "You start on the feature branch, but the integration target is main. A similarly named branch is a distractor."
- task: "Switch to main first, then merge the correct feature branch."
- policy: `(2, 5, ["git status", "git branch -v", "git log --oneline --graph", "git show"])`
- target_rule: `{"head_branch":"main","min_commits_on_branch":{"main":4},"working_tree_clean":true,"staging_empty":true,"conflict_free":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-merge-auth` | Merge correct feature/auth from wrong starting branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"auth feature","parents":["c0"]},{"id":"c3","message":"Draft spike","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2","feature/auth-draft":"c3"},"head":{"type":"branch","name":"feature/auth"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git merge feature/auth"]` |
| `hard-merge-payment` | Merge correct feature/payment from wrong starting branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"payment feature","parents":["c0"]},{"id":"c3","message":"Draft spike","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2","feature/payment-draft":"c3"},"head":{"type":"branch","name":"feature/payment"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git merge feature/payment"]` |
| `hard-merge-search` | Merge correct feature/search from wrong starting branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"search feature","parents":["c0"]},{"id":"c3","message":"Draft spike","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2","feature/search-draft":"c3"},"head":{"type":"branch","name":"feature/search"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git merge feature/search"]` |
| `hard-merge-export` | Merge correct feature/export from wrong starting branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"export feature","parents":["c0"]},{"id":"c3","message":"Draft spike","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2","feature/export-draft":"c3"},"head":{"type":"branch","name":"feature/export"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git merge feature/export"]` |
| `hard-merge-profile` | Merge correct feature/profile from wrong starting branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main work","parents":["c0"]},{"id":"c2","message":"profile feature","parents":["c0"]},{"id":"c3","message":"Draft spike","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2","feature/profile-draft":"c3"},"head":{"type":"branch","name":"feature/profile"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git switch main","git merge feature/profile"]` |

---

#### Scenario 3.2-F: mark-conflict-resolved

**Primary focus command:** `git add`
**Cumulative workflow:** The new focus is the conflict-specific use of `git add`: marking resolved paths. The scenario is not labeled vaguely as "conflict resolution" without a command; it evaluates the Git step the simulator can represent after pre-authored conflict content is considered resolved.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `mark-conflict-resolved` |
| title | Mark Conflict Resolved and Complete Merge |
| focus | `git add` |
| summary | Mark resolved conflict files as resolved, then complete the merge commit. |
| short_explanation | During a paused merge, `git add <resolved-file>` marks a conflicted path as resolved. The follow-up `git commit` records the merge result. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git add"]` |
| supporting_inspection_commands | `["git status","git diff","git log --oneline --graph","git branch -v"]` |
| safe_demo_commands | `["git status","git diff","git add config.yml","git commit -m \"resolve merge\""]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"auth edit","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"conflict"},"staging":{},"conflicts":["auth.py"],"merge_parent":"c2"}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git add config.yml","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git commit -m \"resolve merge\"","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["merge conflict","resolved file","staging area","merge commit"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A merge is paused with one conflicted file. The file has been resolved in the working tree and now Git needs to be told it is resolved."
- task: "Mark the resolved file and complete the merge commit."
- policy: `(2, 5, ["git status", "git diff", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","conflict_free":true,"staging_empty":true,"working_tree_clean":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-conflict-auth` | Resolve one auth conflict | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"auth edit","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"conflict"},"staging":{},"conflicts":["auth.py"],"merge_parent":"c2"}` | `["git add auth.py","git commit -m \"resolve merge\""]` |
| `easy-conflict-payment` | Resolve one payment conflict | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"payment edit","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"conflict"},"staging":{},"conflicts":["payment.py"],"merge_parent":"c2"}` | `["git add payment.py","git commit -m \"resolve merge\""]` |
| `easy-conflict-search` | Resolve one search conflict | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"search edit","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"conflict"},"staging":{},"conflicts":["search.py"],"merge_parent":"c2"}` | `["git add search.py","git commit -m \"resolve merge\""]` |
| `easy-conflict-export` | Resolve one export conflict | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"export edit","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"conflict"},"staging":{},"conflicts":["export.py"],"merge_parent":"c2"}` | `["git add export.py","git commit -m \"resolve merge\""]` |
| `easy-conflict-profile` | Resolve one profile conflict | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"profile edit","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"conflict"},"staging":{},"conflicts":["profile.py"],"merge_parent":"c2"}` | `["git add profile.py","git commit -m \"resolve merge\""]` |

###### Medium

- narrative: "A merge is paused with two conflicted files. Both have been resolved and must be marked before committing."
- task: "Add both resolved files and commit the merge."
- policy: `(3, 6, ["git status", "git diff", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","conflict_free":true,"staging_empty":true,"working_tree_clean":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-conflict-auth` | Resolve two auth conflicts | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"auth edit","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"conflict","README.md":"conflict"},"staging":{},"conflicts":["auth.py","README.md"],"merge_parent":"c2"}` | `["git add auth.py","git add README.md","git commit -m \"resolve merge\""]` |
| `medium-conflict-payment` | Resolve two payment conflicts | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"payment edit","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"conflict","README.md":"conflict"},"staging":{},"conflicts":["payment.py","README.md"],"merge_parent":"c2"}` | `["git add payment.py","git add README.md","git commit -m \"resolve merge\""]` |
| `medium-conflict-search` | Resolve two search conflicts | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"search edit","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"conflict","README.md":"conflict"},"staging":{},"conflicts":["search.py","README.md"],"merge_parent":"c2"}` | `["git add search.py","git add README.md","git commit -m \"resolve merge\""]` |
| `medium-conflict-export` | Resolve two export conflicts | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"export edit","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"conflict","README.md":"conflict"},"staging":{},"conflicts":["export.py","README.md"],"merge_parent":"c2"}` | `["git add export.py","git add README.md","git commit -m \"resolve merge\""]` |
| `medium-conflict-profile` | Resolve two profile conflicts | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"profile edit","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"conflict","README.md":"conflict"},"staging":{},"conflicts":["profile.py","README.md"],"merge_parent":"c2"}` | `["git add profile.py","git add README.md","git commit -m \"resolve merge\""]` |

###### Hard

- narrative: "A merge is paused and one file is resolved while another still has conflict markers. Only resolved files should be marked; then the remaining file must be resolved/marked in the expected flow."
- task: "Mark all resolved conflict files and complete the merge without adding unrelated scratch work."
- policy: `(3, 7, ["git status", "git diff", "git log --oneline --graph", "git branch -v"])`
- target_rule: `{"head_branch":"main","conflict_free":true,"staging_empty":true,"working_tree_clean":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-conflict-auth` | Resolve conflicted auth workflow with scratch noise | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"auth edit","parents":["c0"]}],"branches":{"main":"c1","feature/auth":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"conflict","README.md":"conflict","scratch.md":"modified"},"staging":{},"conflicts":["auth.py","README.md"],"merge_parent":"c2"}` | `["git add auth.py","git add README.md","git commit -m \"resolve merge\""]` |
| `hard-conflict-payment` | Resolve conflicted payment workflow with scratch noise | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"payment edit","parents":["c0"]}],"branches":{"main":"c1","feature/payment":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"conflict","README.md":"conflict","scratch.md":"modified"},"staging":{},"conflicts":["payment.py","README.md"],"merge_parent":"c2"}` | `["git add payment.py","git add README.md","git commit -m \"resolve merge\""]` |
| `hard-conflict-search` | Resolve conflicted search workflow with scratch noise | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"search edit","parents":["c0"]}],"branches":{"main":"c1","feature/search":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"conflict","README.md":"conflict","scratch.md":"modified"},"staging":{},"conflicts":["search.py","README.md"],"merge_parent":"c2"}` | `["git add search.py","git add README.md","git commit -m \"resolve merge\""]` |
| `hard-conflict-export` | Resolve conflicted export workflow with scratch noise | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"export edit","parents":["c0"]}],"branches":{"main":"c1","feature/export":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"conflict","README.md":"conflict","scratch.md":"modified"},"staging":{},"conflicts":["export.py","README.md"],"merge_parent":"c2"}` | `["git add export.py","git add README.md","git commit -m \"resolve merge\""]` |
| `hard-conflict-profile` | Resolve conflicted profile workflow with scratch noise | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Main edit","parents":["c0"]},{"id":"c2","message":"profile edit","parents":["c0"]}],"branches":{"main":"c1","feature/profile":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"conflict","README.md":"conflict","scratch.md":"modified"},"staging":{},"conflicts":["profile.py","README.md"],"merge_parent":"c2"}` | `["git add profile.py","git add README.md","git commit -m \"resolve merge\""]` |

---

#### Scenario 3.2-G: push-integrated-work

**Primary focus command:** `git push`
**Cumulative workflow:** This scenario introduces `git push` after clone/remote/fetch/pull/merge workflows. Prior commands establish local correctness; push publishes the result.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires remote refs, upstream tracking, and `git push` behavior.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `push-integrated-work` |
| title | Push Integrated Work |
| focus | `git push` |
| summary | Publish the current branch after local commits or merges are complete and the working tree is clean. |
| short_explanation | `git push` uploads local commits to the configured upstream remote branch. It should happen after status/history checks confirm the correct branch and clean state. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git push"]` |
| supporting_inspection_commands | `["git status","git branch -v","git log --oneline --graph"]` |
| safe_demo_commands | `["git status","git branch -v","git push"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch -v","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git push","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["publishing work","upstream branch","remote branch","clean working tree"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "Your main branch has one local commit ahead of origin/main and the working tree is clean."
- task: "Push main to its upstream remote."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"main","remote_branch_matches_local":{"origin/main":"main"},"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-push-auth` | Push auth main update | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git push"]` |
| `easy-push-payment` | Push payment main update | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git push"]` |
| `easy-push-search` | Push search main update | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git push"]` |
| `easy-push-export` | Push export main update | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git push"]` |
| `easy-push-profile` | Push profile main update | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c0"},"upstream_tracking":{"main":"origin/main"}}` | `["git push"]` |

###### Medium

- narrative: "You are on a feature branch with local commits and an upstream branch configured."
- task: "Push the current feature branch to its upstream remote branch."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph"])`
- target_rule: `{"head_branch":"feature/<topic>","remote_branch_matches_local":{"origin/feature/<topic>":"feature/<topic>"},"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-push-auth` | Push feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c1"},"head":{"type":"branch","name":"feature/auth"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c0","origin/feature/auth":"c0"},"upstream_tracking":{"feature/auth":"origin/feature/auth"}}` | `["git push"]` |
| `medium-push-payment` | Push feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c1"},"head":{"type":"branch","name":"feature/payment"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c0","origin/feature/payment":"c0"},"upstream_tracking":{"feature/payment":"origin/feature/payment"}}` | `["git push"]` |
| `medium-push-search` | Push feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c1"},"head":{"type":"branch","name":"feature/search"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c0","origin/feature/search":"c0"},"upstream_tracking":{"feature/search":"origin/feature/search"}}` | `["git push"]` |
| `medium-push-export` | Push feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c1"},"head":{"type":"branch","name":"feature/export"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c0","origin/feature/export":"c0"},"upstream_tracking":{"feature/export":"origin/feature/export"}}` | `["git push"]` |
| `medium-push-profile` | Push feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c1"},"head":{"type":"branch","name":"feature/profile"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c0","origin/feature/profile":"c0"},"upstream_tracking":{"feature/profile":"origin/feature/profile"}}` | `["git push"]` |

###### Hard

- narrative: "Several branches exist and only the current feature branch should be pushed."
- task: "Verify branch context and push only the current branch to its upstream."
- policy: `(1, 4, ["git status", "git branch -v", "git log --oneline --graph", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","remote_branch_matches_local":{"origin/feature/<topic>":"feature/<topic>"},"working_tree_clean":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-push-auth` | Push correct current feature/auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/auth":"c1","feature/auth-draft":"c0"},"head":{"type":"branch","name":"feature/auth"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/auth.git"},"remote_branches":{"origin/main":"c0","origin/feature/auth":"c0","origin/feature/auth-draft":"c0"},"upstream_tracking":{"feature/auth":"origin/feature/auth"}}` | `["git push"]` |
| `hard-push-payment` | Push correct current feature/payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/payment":"c1","feature/payment-draft":"c0"},"head":{"type":"branch","name":"feature/payment"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/payment.git"},"remote_branches":{"origin/main":"c0","origin/feature/payment":"c0","origin/feature/payment-draft":"c0"},"upstream_tracking":{"feature/payment":"origin/feature/payment"}}` | `["git push"]` |
| `hard-push-search` | Push correct current feature/search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/search":"c1","feature/search-draft":"c0"},"head":{"type":"branch","name":"feature/search"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/search.git"},"remote_branches":{"origin/main":"c0","origin/feature/search":"c0","origin/feature/search-draft":"c0"},"upstream_tracking":{"feature/search":"origin/feature/search"}}` | `["git push"]` |
| `hard-push-export` | Push correct current feature/export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/export":"c1","feature/export-draft":"c0"},"head":{"type":"branch","name":"feature/export"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/export.git"},"remote_branches":{"origin/main":"c0","origin/feature/export":"c0","origin/feature/export-draft":"c0"},"upstream_tracking":{"feature/export":"origin/feature/export"}}` | `["git push"]` |
| `hard-push-profile` | Push correct current feature/profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Prior work","parents":["c0"]}],"branches":{"main":"c0","feature/profile":"c1","feature/profile-draft":"c0"},"head":{"type":"branch","name":"feature/profile"},"working_tree":{},"staging":{},"conflicts":[],"remotes":{"origin":"https://example.test/profile.git"},"remote_branches":{"origin/main":"c0","origin/feature/profile":"c0","origin/feature/profile-draft":"c0"},"upstream_tracking":{"feature/profile":"origin/feature/profile"}}` | `["git push"]` |

---

### Lesson 3.3: Understanding Merge Conflict State

| Attribute | Value |
|---|---|
| slug | `conflict-state` |
| kind | `content` |
| title | Understanding Merge Conflict State |
| subtitle | Read conflict state as a repository condition, not as a reason to re-clone. |
| sort_order | `3` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Conflict state is a paused merge</div>
  <div class="status-columns">
    <div class="state-card danger"><strong>Conflict</strong><span>forms.py needs a resolved version</span></div>
    <div class="state-card accent"><strong>Stage resolved file</strong><span>Tell Git the conflict is handled</span></div>
    <div class="state-card"><strong>Finish merge</strong><span>Record both parents in history</span></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>A conflict is structured information</h2>
  <p>When a merge conflict appears, the repository enters an unfinished merge state. Git knows the current branch, the branch being merged in, the files that could not be automatically combined, and the parent relationship that will exist once the merge is completed. This is structured information, not chaos. The repository is not broken — it is paused.</p>
  <p>The simulator represents conflict state with conflict paths, a merge context field, working tree changes, and an empty staging area. A complete resolution requires the conflicted content to become resolved, staged, and committed into the integration branch.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Read</h2><p>Run <code>git status</code> to identify which paths are conflicted and confirm the merge is in progress. Run <code>git diff</code> to inspect the conflict markers in the file.</p></div>
  <div class="lesson-panel accent-panel"><h2>Resolve</h2><p>Produce the intended file state. In the simulator, staging the conflicted file represents this resolution step.</p></div>
  <div class="lesson-panel accent-panel"><h2>Complete</h2><p>Stage the resolved file with <code>git add</code> and run <code>git commit</code> to record the merge commit with two parents.</p></div>
</section>
<section class="lesson-panel">
  <h2>Why "pick one side" is the wrong habit</h2>
  <p>Students often resolve conflicts by blindly choosing their own version and discarding a teammate's changes. This silences Git without preserving the combined intent. The correct habit is to understand what both sides contributed and produce a file state that preserves the correct combined work.</p>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

---

# Module 4 — Recovery and Repair

| Attribute | Value |
|---|---|
| slug | `recovery-repair` |
| number | `4` |
| title | Recovery and Repair |
| description | Repair local branch pointer moves and undo over-scoped commits while preserving reachable work. Practice the two most important reset modes in realistic recovery flows. |
| is_orientation | `False` |
| sort_order | `4` |
| assumption | Completed Module 3. Understands commits, branching, and merge commits. |
| goal | Student can use git reset (mixed and soft) to repair pointer mistakes and re-scope commits without destroying reachable work. |

Two content lessons and one scenario-bearing lesson with eight scenarios.

---

### Lesson 4.1: Undo Without Panic

| Attribute | Value |
|---|---|
| slug | `undo-without-panic` |
| kind | `content` |
| title | Undo Without Panic |
| subtitle | Most Git "disasters" are branch pointer problems. Reading the graph before acting is the cure. |
| sort_order | `1` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">The recovery question</div>
  <div class="workflow-strip">
    <span>Where is the work now?</span>
    <span>Is it reachable?</span>
    <span>What moved the pointer?</span>
    <span>Which reset mode fits?</span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Most Git "disasters" are pointer problems</h2>
  <p>When a reset or other command moves a branch pointer further than intended, the work behind it often still exists — it just became harder to find. The first recovery question is not "what command fixes this?" but "where is the work still reachable?" A safety label, a nearby branch, or a commit ID in the log are all valid anchors.</p>
  <p>The second question is which reset mode applies. If the goal is to undo a commit but keep its changes staged, <code>--soft</code> is the right mode. If the goal is to undo a commit and unstage the changes, the default mixed mode applies. If the goal is to discard the changes entirely, <code>--hard</code> applies — but only when a safety reference confirms the important work is still reachable.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Read first</h2><p>Run <code>git log --oneline</code> and <code>git branch -v</code> before acting. Confirm where the desired work is still reachable before choosing a reset target.</p></div>
  <div class="lesson-panel accent-panel"><h2>Safety labels</h2><p>In the seeded scenarios, a safety-copy or safety-base label marks the preserved target. Read the label in the graph and choose the reset mode that produces the desired state.</p></div>
  <div class="lesson-panel accent-panel"><h2>Verify cleanly</h2><p>After any recovery action, run <code>git status</code> to confirm HEAD attachment, the staging area state, and the working tree state. Do not assume the reset succeeded without checking.</p></div>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 4.2: Reset Modes

| Attribute | Value |
|---|---|
| slug | `reset-modes` |
| kind | `content` |
| title | Reset Modes |
| subtitle | How --soft, --mixed, and --hard differ and when each applies. |
| sort_order | `2` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">What each mode preserves</div>
  <div class="level-ladder">
    <div><strong>--soft</strong><span>Moves branch pointer. Staging area preserved. Changes appear staged.</span></div>
    <div><strong>--mixed (default)</strong><span>Moves branch pointer. Staging cleared. Changes appear unstaged.</span></div>
    <div><strong>--hard</strong><span>Moves branch pointer, clears staging, and discards working tree changes. Cannot undo without a safety label.</span></div>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Reset moves the branch pointer — but how far?</h2>
  <p><code>git reset</code> moves the current branch label to a specified commit. What happens to the staging area and working tree depends on the mode.</p>
  <p><code>git reset --soft &lt;target&gt;</code> moves only the branch pointer. The staging area and working tree are left exactly as they were. The effect is that the commits between the old tip and the new tip appear to be "uncommitted" but staged — as if you had staged all those changes but not yet committed them. Use this when you want to redo a commit with a different scope or message.</p>
  <p><code>git reset --mixed &lt;target&gt;</code> (the default when no mode is specified) moves the branch pointer and also clears the staging area. Working tree files are left untouched. The changes appear unstaged. This is the safest general-purpose reset for local work.</p>
  <p><code>git reset --hard &lt;target&gt;</code> moves the branch pointer, clears the staging area, and discards all working tree changes. This is the most destructive mode: uncommitted work is gone unless it was already tracked somewhere.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>--soft</h2><p>Branch moves. Staging preserved. Working tree preserved. Changes appear staged.</p></div>
  <div class="lesson-panel accent-panel"><h2>--mixed (default)</h2><p>Branch moves. Staging cleared. Working tree preserved. Changes appear unstaged.</p></div>
  <div class="lesson-panel accent-panel"><h2>--hard</h2><p>Branch moves. Staging cleared. Working tree discarded. Irreversible without a safety reference.</p></div>
</section>
<section class="lesson-panel">
  <h2>The simulator focuses on --mixed and --soft</h2>
  <p>The scenarios focus on the two modes most useful for beginners: <code>--mixed</code> (default) to restore a branch pointer to a preserved commit, and <code>--soft</code> to undo a commit while keeping the changes staged for re-commit. Understanding the mode distinction is what separates a precise recovery from accidental data loss.</p>
</section>
```

**Practice connection:** `<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>`

---

### Lesson 4.3: Recovering After Pointer Movement

| Attribute | Value |
|---|---|
| slug | `reset-recovery` |
| kind | `scenario` |
| title | Recovering After Pointer Movement |
| subtitle | Repair local branch pointer moves while preserving reachable work. |
| sort_order | `3` |

**Visual**
```html
<section class="lesson-visual">
  <div class="visual-label">Restore the branch pointer</div>
  <div class="commit-row">
    <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node target">c1</span><span class="branch-tag">safety-copy</span><span class="diagram-arrow">-></span><span class="head-tag">main should point here again</span>
  </div>
</section>
```

**Body**
```html
<section class="lesson-panel">
  <h2>Pointer movement can be repaired</h2>
  <p>Reset mistakes are frightening because a branch label may no longer point to the commit you expected. The first recovery question is not "what command fixes this?" but "where is the desired commit still reachable?" In the seeded scenarios, a safety reference keeps the work visible so you can reason from graph evidence rather than guessing.</p>
  <p>The target state usually asks for the main branch to point again at the preserved work, with HEAD on main and no staged or working tree leftovers. Creating a substitute commit is not the same as restoring the intended branch pointer — the graph shape and commit identity matter.</p>
</section>
<section class="lesson-grid">
  <div class="lesson-panel accent-panel"><h2>Find the safe tip</h2><p>Use labels and history to identify the commit that still contains the work you need.</p></div>
  <div class="lesson-panel accent-panel"><h2>Restore the branch</h2><p>The branch that moved should name the preserved commit again.</p></div>
  <div class="lesson-panel accent-panel"><h2>Verify cleanly</h2><p>After resetting, check HEAD attachment, branch pointer value, staging area, and working tree state.</p></div>
</section>
<section class="lesson-panel">
  <h2>Two recovery shapes</h2>
  <p>The first scenario focuses on using <code>git reset</code> (default mixed mode) to move the current branch pointer back to a preserved commit. The second scenario introduces a situation where the reset should be <code>--soft</code>, preserving the changes as staged so they can be re-committed with corrected scope or message. Both use a safety-copy or safety-base label as the recovery target.</p>
</section>
```

**Practice connection:** `<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>`

---

#### Scenario 4.3-A: reset-branch-pointer

**Primary focus command:** `git reset`
**Cumulative workflow:** This scenario introduces `git reset` as a pointer movement command. `git log` and `git show` are expected support because the student must identify the safe target commit before resetting.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `reset-branch-pointer` |
| title | Reset Branch Pointer |
| focus | `git reset` |
| summary | Move the current branch pointer back to a known safe commit after inspecting history. |
| short_explanation | `git reset --hard <commit>` moves the current branch pointer and resets the working tree/index to match that commit. It should only follow careful log inspection. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git reset"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git show"]` |
| safe_demo_commands | `["git status","git log --oneline","git reset --hard c1"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad auth experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git reset --hard c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["branch pointer","history recovery","working tree reset","safe commit"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "The latest commit on main is a bad local experiment. The previous commit is the safe state."
- task: "Reset main back to the safe previous commit and leave the repository clean."
- policy: `(1, 4, ["git status", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"main","branch_points_to":{"main":"c0"},"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-reset-auth` | Reset bad auth commit | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad auth experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c0"]` |
| `easy-reset-payment` | Reset bad payment commit | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad payment experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c0"]` |
| `easy-reset-search` | Reset bad search commit | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad search experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c0"]` |
| `easy-reset-export` | Reset bad export commit | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad export experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c0"]` |
| `easy-reset-profile` | Reset bad profile commit | `{"commits":[{"id":"c0","message":"Safe base","parents":[]},{"id":"c1","message":"Bad profile experiment","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c0"]` |

###### Medium

- narrative: "There are two recent local commits. Only the latest one should be discarded."
- task: "Use log to identify the safe target and reset back one commit."
- policy: `(1, 4, ["git status", "git log --oneline", "git show", "git branch -v"])`
- target_rule: `{"head_branch":"main","branch_points_to":{"main":"c1"},"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-reset-auth` | Reset latest bad auth commit only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad auth experiment","parents":["c1"]}],"branches":{"main":"c2","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `medium-reset-payment` | Reset latest bad payment commit only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad payment experiment","parents":["c1"]}],"branches":{"main":"c2","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `medium-reset-search` | Reset latest bad search commit only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad search experiment","parents":["c1"]}],"branches":{"main":"c2","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `medium-reset-export` | Reset latest bad export commit only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad export experiment","parents":["c1"]}],"branches":{"main":"c2","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `medium-reset-profile` | Reset latest bad profile commit only | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad profile experiment","parents":["c1"]}],"branches":{"main":"c2","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |

###### Hard

- narrative: "Main has a bad chain of local commits, but a safety branch points to the correct recovery point."
- task: "Inspect branches and reset main to the safety branch commit."
- policy: `(1, 5, ["git status", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","branches_equal":[["main","safety/good"]],"working_tree_clean":true,"staging_empty":true}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-reset-auth` | Reset auth chain to safety branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad auth A","parents":["c1"]},{"id":"c3","message":"Bad auth B","parents":["c2"]}],"branches":{"main":"c3","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `hard-reset-payment` | Reset payment chain to safety branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad payment A","parents":["c1"]},{"id":"c3","message":"Bad payment B","parents":["c2"]}],"branches":{"main":"c3","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `hard-reset-search` | Reset search chain to safety branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad search A","parents":["c1"]},{"id":"c3","message":"Bad search B","parents":["c2"]}],"branches":{"main":"c3","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `hard-reset-export` | Reset export chain to safety branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad export A","parents":["c1"]},{"id":"c3","message":"Bad export B","parents":["c2"]}],"branches":{"main":"c3","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |
| `hard-reset-profile` | Reset profile chain to safety branch | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Good work","parents":["c0"]},{"id":"c2","message":"Bad profile A","parents":["c1"]},{"id":"c3","message":"Bad profile B","parents":["c2"]}],"branches":{"main":"c3","safety/good":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --hard c1"]` |

---

#### Scenario 4.3-B: reset-soft-restage

**Primary focus command:** `git reset --soft`
**Cumulative workflow:** This scenario introduces the soft reset mode as the new command family. Later recommit may occur, but the focus is preserving changes while moving the pointer.
**Seeding status:** `seedable_current_simulator`

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `reset-soft-restage` |
| title | Undo Commit but Keep Changes Staged |
| focus | `git reset --soft` |
| summary | Move HEAD back while preserving the undone commit changes in the staging area for recommit. |
| short_explanation | `git reset --soft <commit>` moves the branch pointer but keeps the changes from undone commits staged. It is useful when the snapshot should be recommitted differently. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git reset --soft"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git diff --staged","git show"]` |
| safe_demo_commands | `["git log --oneline","git reset --soft c0","git diff --staged"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy auth commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git reset --soft c0","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff --staged","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["soft reset","staging preservation","recommit workflow","commit repair"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "The last commit has the right content but the wrong message/scope. You need to undo the commit while keeping its changes staged."
- task: "Soft reset back to the previous commit and verify the changes remain staged."
- policy: `(1, 4, ["git status", "git log --oneline", "git diff --staged"])`
- target_rule: `{"head_branch":"main","branch_points_to":{"main":"c0"},"staging_contains":["<changed-file>"],"working_tree_clean":false}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-soft-auth` | Soft reset auth commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy auth commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `easy-soft-payment` | Soft reset payment commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy payment commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `easy-soft-search` | Soft reset search commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy search commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `easy-soft-export` | Soft reset export commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy export commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `easy-soft-profile` | Soft reset profile commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Messy profile commit","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |

###### Medium

- narrative: "The latest commit combines two files that need to be reviewed before recommitting."
- task: "Soft reset the latest commit so its changes return to staging."
- policy: `(1, 4, ["git status", "git log --oneline", "git diff --staged"])`
- target_rule: `{"head_branch":"main","branch_points_to":{"main":"c0"},"staging_contains":["<file-a>","<file-b>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-soft-auth` | Soft reset combined auth commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Combined auth update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `medium-soft-payment` | Soft reset combined payment commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Combined payment update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `medium-soft-search` | Soft reset combined search commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Combined search update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `medium-soft-export` | Soft reset combined export commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Combined export update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `medium-soft-profile` | Soft reset combined profile commit | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Combined profile update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |

###### Hard

- narrative: "Two recent commits should be collapsed into a new clean commit, but first their changes must be preserved."
- task: "Soft reset back before both commits and leave the combined changes staged."
- policy: `(1, 5, ["git status", "git log --oneline", "git diff --staged", "git show"])`
- target_rule: `{"head_branch":"main","branch_points_to":{"main":"c0"},"staging_contains":["<changed-files>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-soft-auth` | Soft reset two auth commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth part A","parents":["c0"]},{"id":"c2","message":"auth part B","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `hard-soft-payment` | Soft reset two payment commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment part A","parents":["c0"]},{"id":"c2","message":"payment part B","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `hard-soft-search` | Soft reset two search commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search part A","parents":["c0"]},{"id":"c2","message":"search part B","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `hard-soft-export` | Soft reset two export commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export part A","parents":["c0"]},{"id":"c2","message":"export part B","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |
| `hard-soft-profile` | Soft reset two profile commits | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile part A","parents":["c0"]},{"id":"c2","message":"profile part B","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git reset --soft c0"]` |

---

#### Scenario 4.3-C: restore-working-tree-file

**Primary focus command:** `git restore`
**Cumulative workflow:** This introduces `git restore` as a focused file-level recovery command. Prior status/diff are used to identify exactly which file should be restored.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires `git restore <path>` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `restore-working-tree-file` |
| title | Restore a Working Tree File |
| focus | `git restore` |
| summary | Discard an unwanted working-tree change while preserving other work. |
| short_explanation | `git restore <path>` restores a working-tree path from HEAD. It is safer and more precise than resetting the whole branch when only one file should be discarded. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git restore"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git status","git diff","git restore scratch.md"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git restore scratch.md","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git restore after inspection."
- task: "Use git restore in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_absent":["scratch.md"],"working_tree_contains":["<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-restore-working-tree-file-auth` | Restore a Working Tree File for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `easy-restore-working-tree-file-payment` | Restore a Working Tree File for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `easy-restore-working-tree-file-search` | Restore a Working Tree File for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `easy-restore-working-tree-file-export` | Restore a Working Tree File for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `easy-restore-working-tree-file-profile` | Restore a Working Tree File for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git restore."
- task: "Inspect the repository and use git restore only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_absent":["scratch.md"],"working_tree_contains":["<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-restore-working-tree-file-auth` | Restore a Working Tree File for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `medium-restore-working-tree-file-payment` | Restore a Working Tree File for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `medium-restore-working-tree-file-search` | Restore a Working Tree File for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `medium-restore-working-tree-file-export` | Restore a Working Tree File for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `medium-restore-working-tree-file-profile` | Restore a Working Tree File for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git restore workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git restore recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_absent":["scratch.md"],"working_tree_contains":["<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-restore-working-tree-file-auth` | Restore a Working Tree File for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `hard-restore-working-tree-file-payment` | Restore a Working Tree File for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `hard-restore-working-tree-file-search` | Restore a Working Tree File for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `hard-restore-working-tree-file-export` | Restore a Working Tree File for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |
| `hard-restore-working-tree-file-profile` | Restore a Working Tree File for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified","scratch.md":"modified"},"staging":{},"conflicts":[]}` | `["git restore scratch.md"]` |

---

#### Scenario 4.3-D: unstage-with-restore

**Primary focus command:** `git restore --staged`
**Cumulative workflow:** This introduces `git restore --staged` through a realistic staging mistake workflow. The intended result is corrected staging, not lost work.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires `git restore --staged` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `unstage-with-restore` |
| title | Unstage a File Without Losing Work |
| focus | `git restore --staged` |
| summary | Remove a file from the staging area while keeping its working-tree changes. |
| short_explanation | `git restore --staged <path>` unstages a path without discarding the working-tree edit. It repairs staging scope mistakes. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git restore --staged"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git status","git diff --staged","git restore --staged scratch.md"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git diff --staged","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git restore --staged scratch.md","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git restore --staged after inspection."
- task: "Use git restore --staged in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_contains":["scratch.md","<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-unstage-with-restore-auth` | Unstage a File Without Losing Work for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `easy-unstage-with-restore-payment` | Unstage a File Without Losing Work for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `easy-unstage-with-restore-search` | Unstage a File Without Losing Work for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `easy-unstage-with-restore-export` | Unstage a File Without Losing Work for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `easy-unstage-with-restore-profile` | Unstage a File Without Losing Work for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git restore --staged."
- task: "Inspect the repository and use git restore --staged only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_contains":["scratch.md","<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-unstage-with-restore-auth` | Unstage a File Without Losing Work for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `medium-unstage-with-restore-payment` | Unstage a File Without Losing Work for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `medium-unstage-with-restore-search` | Unstage a File Without Losing Work for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `medium-unstage-with-restore-export` | Unstage a File Without Losing Work for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `medium-unstage-with-restore-profile` | Unstage a File Without Losing Work for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git restore --staged workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git restore --staged recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","staging_empty":true,"working_tree_contains":["scratch.md","<kept-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-unstage-with-restore-auth` | Unstage a File Without Losing Work for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"auth.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `hard-unstage-with-restore-payment` | Unstage a File Without Losing Work for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"payment.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `hard-unstage-with-restore-search` | Unstage a File Without Losing Work for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"search.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `hard-unstage-with-restore-export` | Unstage a File Without Losing Work for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"export.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |
| `hard-unstage-with-restore-profile` | Unstage a File Without Losing Work for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"profile.py":"modified"},"staging":{"scratch.md":"modified"},"conflicts":[]}` | `["git restore --staged scratch.md"]` |

---

#### Scenario 4.3-E: amend-last-commit

**Primary focus command:** `git commit --amend`
**Cumulative workflow:** This introduces amend as a last-commit repair workflow: inspect, stage the missed change, then amend. Prior `git add` is expected background knowledge.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires commit replacement semantics and `git commit --amend` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `amend-last-commit` |
| title | Amend the Last Commit |
| focus | `git commit --amend` |
| summary | Update the most recent commit after adding a missed change or correcting the commit message. |
| short_explanation | `git commit --amend` replaces the latest commit with a new one that includes the current staged snapshot and/or edited message. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git commit --amend"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git status","git add README.md","git commit --amend"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git add README.md","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git commit --amend","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git commit --amend after inspection."
- task: "Use git commit --amend in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"latest_commit":{"branch":"main","contains_paths":["README.md"]}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-amend-last-commit-auth` | Amend the Last Commit for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `easy-amend-last-commit-payment` | Amend the Last Commit for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `easy-amend-last-commit-search` | Amend the Last Commit for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `easy-amend-last-commit-export` | Amend the Last Commit for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `easy-amend-last-commit-profile` | Amend the Last Commit for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git commit --amend."
- task: "Inspect the repository and use git commit --amend only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"latest_commit":{"branch":"main","contains_paths":["README.md"]}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-amend-last-commit-auth` | Amend the Last Commit for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `medium-amend-last-commit-payment` | Amend the Last Commit for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `medium-amend-last-commit-search` | Amend the Last Commit for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `medium-amend-last-commit-export` | Amend the Last Commit for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `medium-amend-last-commit-profile` | Amend the Last Commit for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git commit --amend workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git commit --amend recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"latest_commit":{"branch":"main","contains_paths":["README.md"]}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-amend-last-commit-auth` | Amend the Last Commit for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"auth update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `hard-amend-last-commit-payment` | Amend the Last Commit for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"payment update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `hard-amend-last-commit-search` | Amend the Last Commit for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"search update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `hard-amend-last-commit-export` | Amend the Last Commit for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"export update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |
| `hard-amend-last-commit-profile` | Amend the Last Commit for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"profile update","parents":["c0"]}],"branches":{"main":"c1"},"head":{"type":"branch","name":"main"},"working_tree":{"README.md":"modified"},"staging":{},"conflicts":[]}` | `["git add README.md","git commit --amend"]` |

---

#### Scenario 4.3-F: revert-bad-commit

**Primary focus command:** `git revert`
**Cumulative workflow:** This introduces revert as the shared-history undo command. The workflow relies on log/show inspection to identify the bad commit first.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires inverse commit generation and `git revert` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `revert-bad-commit` |
| title | Revert a Bad Commit Safely |
| focus | `git revert` |
| summary | Create a new commit that undoes an earlier commit without rewriting history. |
| short_explanation | `git revert <commit>` preserves history by adding a new inverse commit. It is safer for shared history than reset. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git revert"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git log --oneline","git show c1","git revert c1"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad auth change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git log --oneline","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git show c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git revert c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git revert after inspection."
- task: "Use git revert in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-revert-bad-commit-auth` | Revert a Bad Commit Safely for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad auth change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `easy-revert-bad-commit-payment` | Revert a Bad Commit Safely for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad payment change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `easy-revert-bad-commit-search` | Revert a Bad Commit Safely for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad search change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `easy-revert-bad-commit-export` | Revert a Bad Commit Safely for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad export change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `easy-revert-bad-commit-profile` | Revert a Bad Commit Safely for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad profile change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git revert."
- task: "Inspect the repository and use git revert only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-revert-bad-commit-auth` | Revert a Bad Commit Safely for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad auth change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `medium-revert-bad-commit-payment` | Revert a Bad Commit Safely for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad payment change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `medium-revert-bad-commit-search` | Revert a Bad Commit Safely for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad search change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `medium-revert-bad-commit-export` | Revert a Bad Commit Safely for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad export change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `medium-revert-bad-commit-profile` | Revert a Bad Commit Safely for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad profile change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git revert workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git revert recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"main","working_tree_clean":true,"staging_empty":true,"min_commits_on_branch":{"main":4}}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-revert-bad-commit-auth` | Revert a Bad Commit Safely for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad auth change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `hard-revert-bad-commit-payment` | Revert a Bad Commit Safely for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad payment change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `hard-revert-bad-commit-search` | Revert a Bad Commit Safely for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad search change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `hard-revert-bad-commit-export` | Revert a Bad Commit Safely for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad export change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |
| `hard-revert-bad-commit-profile` | Revert a Bad Commit Safely for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Bad profile change","parents":["c0"]},{"id":"c2","message":"Good later work","parents":["c1"]}],"branches":{"main":"c2"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[]}` | `["git revert c1"]` |

---

#### Scenario 4.3-G: stash-before-switching

**Primary focus command:** `git stash`
**Cumulative workflow:** This introduces stash through a real interruption workflow: inspect dirty state, stash, switch, then apply/pop later.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires stash stack state and `git stash`, `git stash pop/apply` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `stash-before-switching` |
| title | Stash Work Before Switching Context |
| focus | `git stash` |
| summary | Temporarily save unfinished work so the student can switch branches safely and later restore it. |
| short_explanation | `git stash` saves working-tree/index changes outside the branch history. It supports context switching without committing unfinished work. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git stash"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git status","git stash","git switch feature/auth","git stash pop"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","auth.py":"modified"},"staging":{},"conflicts":[]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git status","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git stash","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git switch feature/auth","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git stash pop","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git stash after inspection."
- task: "Use git stash in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","stash_stack_empty_after_pop":true,"working_tree_contains":["wip.md","<topic-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-stash-before-switching-auth` | Stash Work Before Switching Context for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","auth.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/auth","git stash pop"]` |
| `easy-stash-before-switching-payment` | Stash Work Before Switching Context for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","payment.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/payment","git stash pop"]` |
| `easy-stash-before-switching-search` | Stash Work Before Switching Context for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","search.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/search","git stash pop"]` |
| `easy-stash-before-switching-export` | Stash Work Before Switching Context for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","export.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/export","git stash pop"]` |
| `easy-stash-before-switching-profile` | Stash Work Before Switching Context for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","profile.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/profile","git stash pop"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git stash."
- task: "Inspect the repository and use git stash only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","stash_stack_empty_after_pop":true,"working_tree_contains":["wip.md","<topic-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-stash-before-switching-auth` | Stash Work Before Switching Context for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","auth.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/auth","git stash pop"]` |
| `medium-stash-before-switching-payment` | Stash Work Before Switching Context for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","payment.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/payment","git stash pop"]` |
| `medium-stash-before-switching-search` | Stash Work Before Switching Context for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","search.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/search","git stash pop"]` |
| `medium-stash-before-switching-export` | Stash Work Before Switching Context for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","export.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/export","git stash pop"]` |
| `medium-stash-before-switching-profile` | Stash Work Before Switching Context for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","profile.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/profile","git stash pop"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git stash workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git stash recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"head_branch":"feature/<topic>","stash_stack_empty_after_pop":true,"working_tree_contains":["wip.md","<topic-file>"]}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-stash-before-switching-auth` | Stash Work Before Switching Context for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/auth":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","auth.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/auth","git stash pop"]` |
| `hard-stash-before-switching-payment` | Stash Work Before Switching Context for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/payment":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","payment.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/payment","git stash pop"]` |
| `hard-stash-before-switching-search` | Stash Work Before Switching Context for search | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/search":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","search.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/search","git stash pop"]` |
| `hard-stash-before-switching-export` | Stash Work Before Switching Context for export | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/export":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","export.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/export","git stash pop"]` |
| `hard-stash-before-switching-profile` | Stash Work Before Switching Context for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]}],"branches":{"main":"c0","feature/profile":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{"wip.md":"modified","profile.py":"modified"},"staging":{},"conflicts":[]}` | `["git stash","git switch feature/profile","git stash pop"]` |

---

#### Scenario 4.3-H: recover-with-reflog

**Primary focus command:** `git reflog`
**Cumulative workflow:** This introduces reflog as the recovery inspection command. The realistic workflow is reflog inspection followed by a recovery action such as branch creation or reset.
**Seeding status:** `requires_simulator_expansion`
**Evaluator note:** Requires reflog entries and `git reflog` support.

**ScenarioSkillFocus fields**

| Field | Value |
|---|---|
| slug | `recover-with-reflog` |
| title | Recover a Lost Commit with Reflog |
| focus | `git reflog` |
| summary | Find a recently lost commit after pointer movement and recover it through a branch or reset. |
| short_explanation | `git reflog` records where HEAD and branch tips recently pointed. It is the recovery map after accidental reset or detached work. |
| skill_focus_type | `command_specific` |
| primary_focus_commands | `["git reflog"]` |
| supporting_inspection_commands | `["git status","git log --oneline","git log --oneline --graph","git branch -v","git diff","git show"]` |
| safe_demo_commands | `["git reflog","git branch recovered c1"]` |
| demo_repository_state | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost auth work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` |
| demo_dag_config | `{"mode":"preview_only","layout":"compact"}` |
| demo_explanation_steps | `[{"command":"git reflog","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."},{"command":"git branch recovered c1","explanation":"Demonstrates the scenario workflow while keeping the listed focus command as the new skill."}]` |
| related_git_concepts | `["file recovery","history recovery","safe undo"]` |
| narrative | *(empty; difficulty-level narrative used)* |
| task_prompt | *(empty; difficulty-level task used)* |

**Difficulties**

###### Easy

- narrative: "A small recovery situation requires git reflog after inspection."
- task: "Use git reflog in the intended recovery workflow."
- policy: `(1, 5, ["git status", "git diff", "git log --oneline", "git show"])`
- target_rule: `{"branch_exists":["recovered-work"],"branch_points_to":{"recovered-work":"c1"},"head_branch":"main"}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `easy-recover-with-reflog-auth` | Recover a Lost Commit with Reflog for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost auth work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `easy-recover-with-reflog-payment` | Recover a Lost Commit with Reflog for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost payment work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `easy-recover-with-reflog-search` | Recover a Lost Commit with Reflog for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost search work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `easy-recover-with-reflog-export` | Recover a Lost Commit with Reflog for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost export work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `easy-recover-with-reflog-profile` | Recover a Lost Commit with Reflog for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost profile work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |

###### Medium

- narrative: "The recovery situation has branch or file distractors, so inspection must happen before git reflog."
- task: "Inspect the repository and use git reflog only on the intended target."
- policy: `(1, 6, ["git status", "git diff", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"branch_exists":["recovered-work"],"branch_points_to":{"recovered-work":"c1"},"head_branch":"main"}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `medium-recover-with-reflog-auth` | Recover a Lost Commit with Reflog for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost auth work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `medium-recover-with-reflog-payment` | Recover a Lost Commit with Reflog for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost payment work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `medium-recover-with-reflog-search` | Recover a Lost Commit with Reflog for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost search work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `medium-recover-with-reflog-export` | Recover a Lost Commit with Reflog for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost export work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `medium-recover-with-reflog-profile` | Recover a Lost Commit with Reflog for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost profile work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |

###### Hard

- narrative: "Multiple plausible recovery actions exist. Choose the precise git reflog workflow without damaging unrelated work."
- task: "Use history/state inspection and complete the correct git reflog recovery workflow."
- policy: `(1, 7, ["git status", "git diff", "git diff --staged", "git log --oneline --graph", "git branch -v", "git show"])`
- target_rule: `{"branch_exists":["recovered-work"],"branch_points_to":{"recovered-work":"c1"},"head_branch":"main"}`
| Variant slug | Label | Initial state | Solution commands |
|---|---|---|---|
| `hard-recover-with-reflog-auth` | Recover a Lost Commit with Reflog for auth | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost auth work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `hard-recover-with-reflog-payment` | Recover a Lost Commit with Reflog for payment | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost payment work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `hard-recover-with-reflog-search` | Recover a Lost Commit with Reflog for search | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost search work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `hard-recover-with-reflog-export` | Recover a Lost Commit with Reflog for export | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost export work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |
| `hard-recover-with-reflog-profile` | Recover a Lost Commit with Reflog for profile | `{"commits":[{"id":"c0","message":"Base","parents":[]},{"id":"c1","message":"Lost profile work","parents":["c0"]}],"branches":{"main":"c0"},"head":{"type":"branch","name":"main"},"working_tree":{},"staging":{},"conflicts":[],"reflog":[{"ref":"HEAD@{1}","target":"c1","message":"commit: lost work"}]}` | `["git reflog","git branch recovered-work c1"]` |

---

## Seed file scenario index

The full curriculum across all four modules defines the following scenarios for seeding or staged implementation:

| Scenario slug | Module.Lesson | Primary focus | Variants per difficulty | Seeding status |
|---|---|---|---|---|
| `initialize-project-and-first-commit` | 1.3 | `git init` | 5 | `requires_simulator_expansion` |
| `read-repository-state` | 1.3 | `git status` | 5 | `requires_inspection_evaluator` |
| `inspect-file-differences` | 1.3 | `git diff` | 5 | `requires_inspection_evaluator` |
| `stage-selected-changes` | 1.3 | `git add` | 5 | `seedable_current_simulator` |
| `form-clean-commit` | 1.3 | `git commit` | 5 | `seedable_current_simulator` |
| `read-commit-history` | 1.4 | `git log` | 5 | `requires_inspection_evaluator` |
| `inspect-commit-details` | 1.4 | `git show` | 5 | `requires_inspection_evaluator` |
| `read-branch-context` | 2.3 | `git branch` | 5 | `requires_inspection_evaluator` |
| `switch-correct-branch` | 2.3 | `git switch` | 5 | `seedable_current_simulator` |
| `create-branch-from-starting-point` | 2.3 | `git switch -c` | 5 | `seedable_current_simulator` |
| `cherry-pick-to-branch` | 2.3 | `git cherry-pick` | 5 | `seedable_current_simulator` |
| `delete-stale-branch` | 2.3 | `git branch -d` | 5 | `seedable_current_simulator` |
| `clone-project-and-inspect` | 3.2 | `git clone` | 5 | `requires_simulator_expansion` |
| `connect-remote-origin` | 3.2 | `git remote` | 5 | `requires_simulator_expansion` |
| `fetch-remote-updates` | 3.2 | `git fetch` | 5 | `requires_simulator_expansion` |
| `pull-before-local-work` | 3.2 | `git pull` | 5 | `requires_simulator_expansion` |
| `merge-feature-branch` | 3.2 | `git merge` | 5 | `seedable_current_simulator` |
| `mark-conflict-resolved` | 3.2 | `git add` | 5 | `seedable_current_simulator` |
| `push-integrated-work` | 3.2 | `git push` | 5 | `requires_simulator_expansion` |
| `reset-branch-pointer` | 4.3 | `git reset` | 5 | `seedable_current_simulator` |
| `reset-soft-restage` | 4.3 | `git reset --soft` | 5 | `seedable_current_simulator` |
| `restore-working-tree-file` | 4.3 | `git restore` | 5 | `requires_simulator_expansion` |
| `unstage-with-restore` | 4.3 | `git restore --staged` | 5 | `requires_simulator_expansion` |
| `amend-last-commit` | 4.3 | `git commit --amend` | 5 | `requires_simulator_expansion` |
| `revert-bad-commit` | 4.3 | `git revert` | 5 | `requires_simulator_expansion` |
| `stash-before-switching` | 4.3 | `git stash` | 5 | `requires_simulator_expansion` |
| `recover-with-reflog` | 4.3 | `git reflog` | 5 | `requires_simulator_expansion` |

Each scenario has 3 difficulty instances × 5 variants = 15 variant records per scenario. The expanded curriculum has 27 scenarios, for 405 authored variant-difficulty records. Scenarios marked `seedable_current_simulator` can use the current state-based simulator approach. Scenarios marked `requires_inspection_evaluator` need StepLog/observation checks for diagnostic-only commands. Scenarios marked `requires_simulator_expansion` are formally authored but should not be activated until the listed command/state support exists.

### CommandCountPolicy budget summary

| Module | Scenarios | Counted budget range | Notes |
|---|---|---|---|
| 1 | `initialize-project-and-first-commit` | 3–5 counted actions | `git init` + add/commit workflow; requires pre-repository state support |
| 1 | `read-repository-state`, `inspect-file-differences`, `read-commit-history`, `inspect-commit-details` | 0 counted actions | diagnostic inspection; no fake state-changing target |
| 1 | `stage-selected-changes` | 1–2 counted actions | `git add` as new action; status/diff free |
| 1 | `form-clean-commit` | 2–3 counted actions | add + commit sequence; commit is focus |
| 2 | `read-branch-context` | 0 counted actions | branch inspection before navigation |
| 2 | `switch-correct-branch`, `create-branch-from-starting-point` | 1–2 counted actions | switch or switch -c after inspection |
| 2 | `cherry-pick-to-branch` | 2–3 counted actions | switch + cherry-pick; cherry-pick is focus |
| 2 | `delete-stale-branch` | 1 counted action | branch deletion after graph inspection |
| 3 | `clone-project-and-inspect`, `connect-remote-origin`, `fetch-remote-updates`, `pull-before-local-work`, `push-integrated-work` | 1 counted action plus inspections | remote workflow; requires remote-state expansion |
| 3 | `merge-feature-branch` | 1–2 counted actions | switch if needed + merge |
| 3 | `mark-conflict-resolved` | 2–3 counted actions | add resolved file(s) + commit merge |
| 4 | `reset-branch-pointer`, `reset-soft-restage` | 1 counted action | reset modes after history inspection |
| 4 | `restore-working-tree-file`, `unstage-with-restore`, `amend-last-commit`, `revert-bad-commit`, `stash-before-switching`, `recover-with-reflog` | 1–3 counted actions | formal recovery workflows requiring simulator expansion |

---

## Platform-wide assessment metrics

| Metric | Definition | Target |
|---|---|---|
| Scenario Completion Rate | Proportion of started scenario sessions that reach the final step | ≥80% per difficulty level |
| Retry Count | Number of attempts before successful scenario completion | ≤3 on average, decreasing across variants |
| Hint Usage Rate | Proportion of steps where the user requests a hint | <30% after first attempt; declining trend |
| Template Transfer Accuracy | First-attempt success rate across different variants of the same scenario | ≥70% sustained across variants |
| Forward Progression Rate | Steps completed without reverting to an earlier step | ≥75% on Hard level |

**System Usability Scale (SUS)** — administered after the student's first completed scenario session; benchmark ≥70.

**Technology Acceptance Model (TAM) survey** — administered after completion of at least one full module; targets: Perceived Usefulness ≥4.0, Perceived Ease of Use ≥3.5, Behavioral Intention to Use ≥4.0 (5-point scale).

---

## Curriculum justification summary

The progression follows cognitive load theory's principle of focused-to-coordinated elements (Sweller et al., 2011):

- Solo local work with cumulative workflows (M1: init → status/diff → add → commit → log/show)
- Branch navigation with preserved cumulative commands (M2: branch inspection → switch → switch -c → cherry-pick → branch cleanup)
- Shared work and integration (M3: clone/remote/fetch/pull → merge → conflict marking → push)
- Recovery and repair (M4: reset modes → restore/unstage → amend/revert/stash/reflog)

No scenario appears before its conceptual prerequisites are established. Module 2 requires full commit literacy (M1). Module 3 requires branch navigation literacy (M2). Module 4 requires graph-reading and commit literacy (M1–M2). The cumulative command model ensures that each scenario is a realistic workflow, not an isolated drill — prior learned commands appear as expected background steps throughout.

**Key design principle: Fixed-variant pool**

Each difficulty instance draws from a pool of five fully-authored variants. Each variant fixes surface details (project-adjacent filenames, branch names) and repository topology (commit count, HEAD state, divergence state, conflict count, nearby labels). Because topology varies across the five variants, no single memorized command sequence solves all five — each draw requires fresh reasoning about the actual repository state presented.

Levels own scaffolding. Variants own variation. These responsibilities never overlap.

---

## References

Chacon, S., & Straub, B. (2014). *Pro Git* (2nd ed.). Apress. https://git-scm.com/book/en/v2

Isomöttönen, V., & Cochez, M. (2014). Challenges of teaching Git to CS students. *Proceedings of the 14th Koli Calling International Conference on Computing Education Research*, 81–90. https://doi.org/10.1145/2674683.2674694

Mayer, R. E. (2009). *Multimedia learning* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511811678

Milliken, G., Cosma, G., & Woodward, J. (2021). Understanding undergraduate students' use of version control systems. *Journal of Systems and Software*, 172, 110868. https://doi.org/10.1016/j.jss.2020.110868

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, 12(2), 257–285. https://doi.org/10.1207/s15516709cog1202_4

Sweller, J., Ayres, P., & Kalyuga, S. (2011). *Cognitive load theory*. Springer. https://doi.org/10.1007/978-1-4419-8126-4

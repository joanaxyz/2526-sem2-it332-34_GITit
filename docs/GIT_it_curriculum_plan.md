# GIT it! Detailed Curriculum Plan

This plan defines the current-release static starter curriculum for GIT it!. It is written as an authoring guide and a content map for the seeded MVP syllabus: units, lessons, scenario skill focuses, Easy/Medium/Hard difficulty instances, retry variants, command-count policies, and evaluator expectations.

## Key Curriculum Decisions

The current SRS and SDD require every published scenario skill focus to have Easy, Medium, and Hard difficulty instances. They define different scaffolding per level, but they do not require the three levels to be identical copies of the same situation. For the curriculum, each difficulty level should use the same core Git skill focus while changing the professional situation, repository topology, amount of ambiguity, and command efficiency expectation.

Scenario descriptions must be specific enough for a student to know the professional goal, current repository state, target branch, files involved, and any required commit-message intent. They must not expose the correct command sequence.

Current-release MVP does not include real remotes or external Git hosting. Therefore, scenarios must not require `git push`, GitHub, GitLab, Bitbucket, pull requests, forks, or remote branch tracking as assessed outcomes. If a future remote-workflow unit is added, the scenario must explicitly name the remote, local branch, destination branch, and whether the push should create, update, or avoid updating a remote ref.

Commit messages should be authored when the scenario teaches staging, commit intent, or professional communication. The MVP evaluator may enforce lightweight message intent through `message_contains`, but it should still grade repository state first and avoid exact full-message matching unless an instructor has a clear reason to require it.

Student-facing scenario context must distinguish narrative from rules. Each scenario card or workspace should make clear: the target is a final repository state, not a hidden command sequence; diagnostic commands listed in the command policy do not consume counted actions; and commit-message wording is graded only when the task explicitly says the message must include a word or intent.

## Scenario Authoring Contract

Each scenario difficulty instance is the authoritative configured practice unit for that level. Easy, Medium, and Hard belong to the same scenario skill focus, but each difficulty instance must define its own scenario configuration before publication:

| Field | Requirement |
| --- | --- |
| Learning unit and lesson | The lesson that teaches the concept before practice. |
| Skill focus | One precise Git competency, such as partial staging or wrong-branch recovery. |
| Difficulty level | Easy, Medium, or Hard. |
| Student-facing scenario title | Short action phrase, not the answer. |
| Professional role/context | Why the student is doing this work. |
| Initial repository state | Current branch, commits, branch pointers, working tree, staging area, conflict state, and visible file names. |
| Student task prompt | The outcome to achieve without listing commands. |
| Target branch/ref | The branch that should be checked out or updated at the end. |
| Files involved | File names and whether each starts untracked, modified, staged, conflicted, or clean. |
| Commit-message expectation | Required only when committing is part of the learning objective. Use an intent phrase rather than a hidden command answer. |
| Success criteria | Repository-state rules used by the evaluator. |
| Allowed simulator scope | Git operations available for the scenario. |
| Command-count policy | Minimum counted commands for CAR, maximum counted commands before failure, and non-counted diagnostic commands. |
| Scaffolding | Easy/Medium/Hard support visibility. |
| Difficulty-owned retry variants | At least two structurally distinct variants for each RTA-eligible difficulty instance. Variants belong to the difficulty instance, not only to the parent skill focus. |
| No-answer review | Confirm the text does not reveal a correct command sequence. |

## Difficulty Design Standard

Easy, Medium, and Hard should be related but not identical. A student who completes Easy should understand the concept; a student who completes Medium should transfer the concept to a less explicit situation; a student who completes Hard should solve a realistic repository state with minimal scaffolding. Each level should therefore be authored through its own difficulty instance, with its own initial state, target state, command policy, and variant pool.

| Level | Scenario Design | Student Support | State Complexity | Expected Student Behavior |
| --- | --- | --- | --- | --- |
| Easy | Direct scenario with explicit file names, target branch, and target state description. | Live DAG, expected-state diagram, contextual consequence feedback. | One main concept, minimal distractors. | Inspect state, make the intended change, observe feedback. |
| Medium | Same skill in a changed project context with a small distractor or extra branch/file. | Live DAG and expected-state diagram only. | Same concept plus one ambiguity students must resolve through diagnostics. | Use inspection commands before acting and avoid accidental over-selection. |
| Hard | Realistic professional incident with minimal explicit guidance. | Live DAG and narrative context only. | More branch/history ambiguity, stricter command efficiency, no contextual feedback. | Infer the correct target state from context and complete efficiently. |

## Recommended Learning Path

The strongest path from Unit 2 onward is not "basic Git commands, then branches, then conflicts." The better path is a state-reasoning spiral: students first learn to read state, then intentionally change state, then move branch pointers, then recover from mistakes, then integrate team work, then complete mixed professional workflows.

Recommended sequence:

1. Unit 2: Repository State and Commit Formation
2. Unit 3: Branching and Local Navigation
3. Unit 4: Local Undo and Recovery
4. Unit 5: Collaboration and Integration
5. Unit 6: Integrated Team Workflow Capstone

This adds one more unit after recovery and moves integration later. The reason is practical: merge conflicts are not just a new command topic; they are a stress test of the student's ability to inspect state, understand pointers, avoid destructive panic, and finish a partially completed operation. Students should practice recovery before collaboration scenarios ask them to recover from merge and divergence states.

Unit 6 should be included if the pilot has enough time for synthesis practice. It does not introduce remotes or GitHub. It combines existing simulator-supported skills into realistic multi-step scenarios and gives the curriculum a stronger ending than "recover after reset."

## Unit 1: Orientation

Unit 1 is a no-terminal, concept-only orientation unit. Its lessons are single scrollable pages that students can read before or during scenario practice. Completion/read status is tracked for progress, but Unit 1 does not block access to scenarios.

### Lesson 1.1: The Three File Areas

Purpose: distinguish working tree, staging area, and repository history.

Required concepts:
- Working tree contains current file edits.
- Staging area is the proposed next snapshot.
- Repository history contains completed commits.
- A scenario can be wrong even when the final files look correct if the staging area or branch pointer is wrong.

Practice readiness outcome:
- Student can say whether a change is unstaged, staged, or committed.

### Lesson 1.2: Tracked vs. Untracked Files

Purpose: explain why Git treats new files differently from modified tracked files.

Required concepts:
- Untracked files are visible to Git but not part of history.
- `git add` changes tracking/staging state.
- Staging every file is not always correct.

Practice readiness outcome:
- Student can identify when selected staging is safer than staging everything.

### Lesson 1.3: What HEAD Is

Purpose: make HEAD visible as the current repository position.

Required concepts:
- HEAD normally points to the current branch.
- The current branch pointer moves when a commit is created.
- Detached HEAD changes where new commits would be reachable from.

Practice readiness outcome:
- Student can predict which branch will move after a commit.

### Lesson 1.4: Commits, Parents, and DAG Literacy

Purpose: prepare students to read the live DAG.

Required concepts:
- Commits are nodes.
- Parent links explain history.
- Merge commits have more than one parent.
- Branch labels point to commits.

Practice readiness outcome:
- Student can compare initial and expected DAG shapes.

### Lesson 1.5: Branches as Movable Pointers

Purpose: correct the misconception that branches are folders.

Required concepts:
- A branch is a movable label.
- Switching branch changes the active pointer.
- Creating commits moves the active branch only.

Practice readiness outcome:
- Student can explain why work committed on the wrong branch must be moved or recovered deliberately.

### Lesson 1.6: Git Command Anatomy

Purpose: reduce blind command copying.

Required concepts:
- `git` command, subcommand, options, and arguments.
- Diagnostic commands should be used before state-changing commands.
- The same target state may be reachable through more than one valid command sequence.

Practice readiness outcome:
- Student can separate inspection commands from action commands.

### Lesson 1.7: GIT it! Practice Rules and No-Answer Policy

Purpose: explain simulator boundaries.

Required concepts:
- Commands are parsed by the internal simulator, not executed by a shell.
- Terminal output and feedback describe consequences, not answers.
- The system evaluates repository state, not memorized command strings.

Practice readiness outcome:
- Student understands why the platform does not reveal reference solutions.

### Lesson 1.8: Difficulty, Retry, and Review Mode

Purpose: explain progression.

Required concepts:
- Easy, Medium, and Hard reduce scaffolding progressively.
- Retry variants may change topology to test transfer.
- Review Mode replays completed scenario difficulties without replacing primary KPI records.

Practice readiness outcome:
- Student understands that harder levels may change scenario details, not only hide hints.

## Unit 2: Repository State and Commit Formation

Goal: students learn to inspect repository state before acting, separate ready work from draft work, and create intentional commits without treating `git add .` as a reflex.

### Lesson 2.1: Reading Git Status

Concept focus:
- Interpreting clean, modified, untracked, staged, and conflicted status.
- Recognizing that status is diagnostic and should not count against command efficiency.

No terminal scenario is required for this lesson in the MVP, but every Unit 2 scenario should allow `git status` as a non-counted diagnostic command.

### Lesson 2.2: First Commits and Staging Decisions

Scenario focus A: Create a first clean commit.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A new class project has `README.md` and `app.py` untracked on `main`. Capture both files as the first project snapshot. | Names branch `main`, names both files, says the working tree should be clean after the commit. Suggested commit intent: "initial project setup". | `main` has one commit; working tree clean; staging empty; HEAD on `main`. | Min 3 counted, max 9; diagnostics: `git status`, `git log --oneline`. |
| Medium | A small static site has `index.html`, `styles.css`, and `tests.py` untracked. The instructor wants one starter commit before changes continue. | Names `main`, names files, does not say which command stages all files. Commit intent: "add starter site files". | `main` has one commit containing all starter files; working tree clean; staging empty. | Min 2 counted, max 8; same diagnostics. |
| Hard | A repository was initialized for a team exercise and contains several visible starter files but no commits. Prepare it so teammates can branch from a clean first snapshot. | Gives professional goal and current branch only; file details are visible through status. Commit intent: "create baseline project snapshot". | `main` has one baseline commit; no remaining working tree or staged changes. | Min 2 counted, max 7; diagnostics remain non-counted. |

Scenario focus B: Stage selected changes.

This is where the staging plan must be explicit. The scenario must identify which files belong in the commit and which files must remain uncommitted.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | On `main`, `config.yml` and `draft.md` are modified. Only the configuration change is ready for review. | Explicitly says stage and commit `config.yml`; leave `draft.md` visible but uncommitted. Commit intent: "update app configuration". | New commit on `main`; `config.yml` included; `draft.md` remains in working tree; staging empty; HEAD on `main`. | Min 4 counted, max 10; diagnostics: `git status`, `git diff`. |
| Medium | On `main`, `settings.json` contains a finished environment update and `notes.txt` contains private planning notes. Commit only the finished environment update. | Names both files and the ready file; expected-state diagram shows one new commit with one remaining working-tree change. Commit intent: "update environment settings". | New commit on `main`; `notes.txt` remains uncommitted; staging empty. | Min 3 counted, max 9; diagnostics: `git status`, `git diff`, `git diff --staged` if supported. |
| Hard | Before handing off a bugfix branch, separate a finished config change from an unrelated draft edit. | Does not label the exact ready file in the task sentence; status/diff output should reveal it. Commit intent: "record reviewed configuration change". | Only the intended file is committed; unrelated draft remains uncommitted; staging empty. | Min 3 counted, max 8; diagnostics remain non-counted. |

### Lesson 2.3: Inspecting History Without Changing State

Concept focus:
- Use history inspection to understand repository state.
- Reading commits and branch labels before deciding.
- Diagnostic commands are logged but excluded from CAR.

Recommended content-only exercises:
- Compare two DAGs and identify the current branch.
- Identify whether a commit exists on `main`, a feature branch, both, or neither.

### Unit 2 Mastery Gate

Before moving into branching scenarios, students should be able to:

- Use status/history inspection before a state-changing command.
- Explain what is in the working tree, staging area, and repository history.
- Commit all intended starter files when appropriate.
- Commit selected files while leaving unrelated work uncommitted.
- Explain where the next commit will land based on HEAD and the current branch.

## Unit 3: Branching and Navigation

Goal: students reason about HEAD, branch pointers, branch creation, local navigation, and moving work safely before they encounter team integration states.

### Lesson 3.1: Branch Pointers and HEAD

Concept focus:
- Branch pointers move when commits are created.
- Only the checked-out branch moves on commit.
- Branch labels can point to the same commit or diverge.

Scenario focus: Create a feature branch before starting work.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A student is about to start a login task. Create a `feature/login` branch from `main` before any feature commit happens. | Names `main` and `feature/login`; says no files should be changed. | `feature/login` exists; HEAD on `feature/login`; branch starts at same commit as `main`; working tree clean. | Min 1 counted, max 5; diagnostics: `git status`, `git branch -v`. |
| Medium | A small profile task needs its own branch from the current clean base. Prepare the branch without changing history. | Names target branch; students inspect current branch before creating it. | Target feature branch exists and is checked out; no commits added; clean state. | Min 1 counted, max 5; same diagnostics. |
| Hard | Before implementing a new task, prepare an isolated line of work from the current stable branch. | Professional context gives branch purpose; students infer they need a new feature branch. | New feature branch checked out from current base; clean state; existing branches unchanged. | Min 1 counted, max 4; same diagnostics. |

### Lesson 3.2: Detached HEAD and Safe Navigation

Concept focus:
- Detached HEAD is a state, not an error.
- New commits in detached state may be hard to find unless preserved.
- Safe navigation starts with diagnostics.

### Lesson 3.3: Moving Work to the Right Branch

Scenario focus: Move a commit made on the wrong branch.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | Feature work was committed while `main` was checked out. A `feature/recovery` branch still points to the previous base. Move the work so development continues on `feature/recovery`. | Names wrong branch `main`, target branch `feature/recovery`, and the commit message visible in history. | HEAD on `feature/recovery`; feature branch includes recovered work; working tree clean; staging empty. | Min 4 counted, max 12; diagnostics: `git status`, `git log --oneline`, `git branch -v`. |
| Medium | A report change landed on `main`, but it belongs on `feature/recovery`. Preserve main's base and continue on the feature branch. | Names target branch, but students must inspect history to identify the commit. | Feature branch contains recovered work; HEAD on feature branch; no uncommitted changes. | Min 3 counted, max 11; same diagnostics. |
| Hard | A teammate notices `main` moved after a local feature commit. Restore the feature workflow without losing the local commit. | Professional narrative gives goal; branch names are visible through diagnostics. | Correct feature branch points to the recovered work; HEAD on that branch; clean state. | Min 3 counted, max 10; same diagnostics. |

### Unit 3 Mastery Gate

Before moving into recovery scenarios, students should be able to:

- Create and switch to a feature branch intentionally.
- Explain which branch will move after a commit.
- Recognize detached HEAD as a state rather than a disaster.
- Move or preserve work that was created from the wrong branch position.

## Unit 4: Local Undo and Recovery

Goal: students recover from common local mistakes before facing collaborative integration, reducing the temptation to delete folders, re-clone, abandon repositories, or blindly copy AI-suggested commands.

### Lesson 4.1: Undo Without Panic

Concept focus:
- First inspect, then recover.
- Avoid destructive commands unless the target state is understood.
- Separate working-tree undo, staging undo, commit undo, and branch-pointer recovery.

Recommended content-only exercises:
- Given a state, choose whether the issue is in working tree, staging area, branch pointer, or merge state.
- Identify one safe diagnostic command before choosing a recovery action.

### Lesson 4.2: Recovering After Pointer Movement

Scenario focus: Recover after an accidental local reset.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | `main` was reset backward, but `safety-copy` still points to the lost local work. Move `main` back to the preserved work. | Names `main`, `safety-copy`, and says no new commit is needed. | `main` equals `safety-copy`; HEAD on `main`; clean state. | Min 2 counted, max 8; diagnostics: `git status`, `git log --oneline`, `git branch -v`. |
| Medium | A local report commit disappeared from `main`, but a backup branch still references it. Restore the branch pointer without inventing history. | Names backup branch; students inspect commit graph. | Active branch points to backup commit; clean state; no extra commit. | Min 2 counted, max 7; same diagnostics. |
| Hard | A branch pointer was moved backward during an attempted cleanup. A preserved reference still identifies the correct work. Recover the intended branch state. | Minimal narrative; branch names and commit positions are discovered through diagnostics. | Intended branch equals preserved reference; HEAD on intended branch; clean state. | Min 1 counted, max 6; same diagnostics. |

### Lesson 4.3: Preserving Detached Work

Scenario focus: Save work created from a detached HEAD or non-branch position.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A commit was made while HEAD was detached at an older commit. Create a branch so the work is no longer floating. | Names the desired branch, such as `feature/saved-work`, and shows the detached commit in the DAG. | New branch exists at the detached work; HEAD attached to that branch; clean state. | Min 2 counted, max 8; diagnostics: `git status`, `git log --oneline`, `git branch -v`. |
| Medium | A local experiment exists away from the main branch. Preserve it on a named branch before returning to normal work. | Names the branch purpose; students inspect whether HEAD is detached. | Experiment commit is reachable from the new branch; HEAD attached to the new branch or restored to stated target branch. | Min 2 counted, max 8; same diagnostics. |
| Hard | A useful local commit is reachable but not attached to the expected branch workflow. Preserve it without rewriting unrelated history. | Minimal narrative; DAG and branch list reveal the detached or misplaced state. | Useful work is reachable from the intended branch label; no unrelated branch pointer changes. | Min 2 counted, max 7; same diagnostics. |

### Unit 4 Mastery Gate

Before moving into collaboration scenarios, students should be able to:

- Pause and inspect before attempting recovery.
- Restore a branch pointer from a safe reference.
- Preserve reachable work without inventing a new unrelated history.
- Explain why re-cloning is avoidance, not recovery.

## Unit 5: Collaboration and Integration

Goal: students preserve teammate work while resolving divergence, merge states, conflicts, and branch cleanup.

### Lesson 5.1: Divergent Branches

Scenario focus: Resolve divergent branches after team edits.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | `main` has a teammate update and `feature/login` has your login work. Integrate the feature into `main` without discarding either line of work. | Names both branches and states the final branch should be `main`. | Merge/integrated commit reachable from `main`; both histories preserved; working tree clean; staging empty. | Min 4 counted, max 12; diagnostics: `git status`, `git log --oneline`, `git branch -v`. |
| Medium | `main` has a patch and `feature/profile` has profile work from the same base. Prepare `main` with both changes. | Names branches; expected-state diagram shows the integrated shape. | `main` reaches both branch histories; clean state. | Min 3 counted, max 11; same diagnostics. |
| Hard | A team branch and `main` both moved after the last shared base. Bring the accepted feature work into the release branch. | Gives release branch and feature purpose; students inspect branch names and history. | Release branch has integrated history; clean state; no loss of either side. | Min 3 counted, max 10; same diagnostics. |

### Lesson 5.2: Understanding Merge Conflict State

Scenario focus: Finish a merge after conflict markers appear.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A merge into `main` stopped because `forms.py` has conflict markers. The file has already been edited to the accepted content in the simulator context; finish the merge safely. | Names conflict file, current branch, and required clean final state. Commit intent: "resolve forms integration". | Merge commit on `main`; conflict list empty; working tree clean; staging empty. | Min 5 counted, max 12; diagnostics: `git status`, `git diff`. |
| Medium | A copy update merge stopped on `copy.md`. Complete the conflict resolution and preserve both parents in history. | Names file and branch; expected-state diagram shows merge commit shape. Commit intent: "resolve copy merge". | Merge commit with two parents on `main`; clean state. | Min 4 counted, max 11; same diagnostics. |
| Hard | An integration merge is paused with one conflicted file. Complete the repository state so the team can continue from `main`. | Narrative gives outcome; status/diff reveals the file. Commit intent: "finish integration merge". | Conflict-free merge commit on `main`; no staged or working changes. | Min 4 counted, max 10; same diagnostics. |

### Lesson 5.3: Branch Cleanup After Integration

Scenario focus: Clean up a merged feature branch.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | `old-feature` has already been merged into `main`. Delete only the stale feature branch and leave history unchanged. | Names branch to remove and says stay on `main`. | `old-feature` absent; HEAD on `main`; main history unchanged; clean state. | Min 2 counted, max 7; diagnostics: `git branch`, `git log --oneline`. |
| Medium | A completed topic branch points to the same commit as `main`. Remove the stale branch label without touching commits. | Student must inspect branch list to confirm the stale branch. | Stale branch absent; `main` unchanged; clean state. | Min 2 counted, max 6; same diagnostics. |
| Hard | After integration, remove the obsolete local branch label while preserving the release branch. | Narrative avoids command names; branch list reveals candidate. | Only the obsolete branch label is removed; HEAD remains on release/main branch. | Min 1 counted, max 5; same diagnostics. |

### Unit 5 Mastery Gate

Students are ready for capstone workflows when they can:

- Integrate divergent local histories without discarding either side.
- Recognize and complete an in-progress merge state.
- Remove branch labels without deleting committed work.
- Explain why the final DAG shape matters more than the exact command sequence.

## Unit 6: Integrated Team Workflow Capstone

Goal: students combine state inspection, staging, branching, recovery, integration, and cleanup in realistic multi-step workflows. Unit 6 should not add new Git concepts; it should test whether students can choose among previously learned concepts when the scenario does not announce the topic.

### Lesson 6.1: Diagnose the Repository Before Acting

Concept focus:
- Start from state, not from a memorized command.
- Decide whether the problem is about files, staging, branch position, integration, or recovery.
- Use diagnostic commands deliberately without burning counted actions.

Scenario focus: Choose the correct repair path.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A teammate says the repository "looks wrong." The workspace shows one modified file, one stale branch, and a clear target branch. Resolve only the stated issue. | Names the issue category and target branch. | Only the intended state problem is changed; unrelated branch/file state remains safe. | Min varies by selected skill, max 12; diagnostics: `git status`, `git log --oneline`, `git branch -v`, `git diff`. |
| Medium | A project handoff includes unrelated draft work and a branch pointer that must be preserved. Prepare the repository for review. | Gives the professional outcome but not the command category. | Intended commit/branch state reached; draft work or preserved ref handled according to prompt. | Min varies by target path, max 12; same diagnostics. |
| Hard | A realistic local repository has multiple signals: a feature branch, a stale branch label, and a changed working tree. Make the repository safe for the next developer. | Narrative only; students infer which states matter. | Clean, intended branch state; no discarded reachable work; no unnecessary history changes. | Max 10-14 depending on authored topology; diagnostics remain non-counted. |

### Lesson 6.2: Complete a Local Feature Workflow

Scenario focus: Start from unfinished local work and end with an integrated, cleaned state.

| Difficulty | Scenario | Student-Facing Details | Target State | Command Policy |
| --- | --- | --- | --- | --- |
| Easy | A feature branch contains finished work and `main` is ready to receive it. Integrate the feature and remove the stale branch. | Names source branch, target branch, and cleanup branch. | `main` contains feature work; stale branch removed; working tree clean. | Min 4 counted, max 12; diagnostics: `git status`, `git log --oneline`, `git branch -v`. |
| Medium | A finished feature and a small unrelated draft edit are both visible. Integrate only the feature workflow and leave the draft safe. | Names finished work and draft context. | Accepted work integrated; unrelated draft remains uncommitted or untouched according to prompt; clean/staged state matches target. | Min 5 counted, max 13; diagnostics include `git diff`. |
| Hard | Prepare a repository for handoff after local feature work, branch movement, and cleanup. | Professional outcome only; students infer branch and file-state work from diagnostics. | Correct branch contains intended work; obsolete branch labels removed; no unrelated work lost. | Min 5 counted, max 14; diagnostics remain non-counted. |

### Lesson 6.3: Final Independent Practice

Scenario focus: Mixed-state final challenge using only Hard-level scaffolding.

This lesson should contain Hard-first or Hard-only capstone scenarios after students have completed Easy/Medium/Hard in prior units. These capstones should be excluded from early novice progression and used as independent practice evidence rather than as the first exposure to any concept.

Recommended capstone patterns:
- Partial staging plus branch handoff.
- Wrong-branch commit plus integration.
- Accidental reset recovery plus branch cleanup.
- Merge completion plus stale branch cleanup.

## Current-Release Scenario Library Summary

| Unit | Lesson | Scenario Skill Focus | Easy/Medium/Hard Differentiation |
| --- | --- | --- | --- |
| Unit 2 | First Commits and Staging Decisions | Create a first clean commit | Same first-commit skill; different project files, ambiguity, and command efficiency. |
| Unit 2 | First Commits and Staging Decisions | Stage selected changes | Same staging skill; progressively less explicit ready-vs-draft distinction. |
| Unit 3 | Branch Pointers and HEAD | Create a feature branch before starting work | Same branch-creation skill; progressively less explicit branch/task mapping. |
| Unit 3 | Moving Work to the Right Branch | Move a commit made on the wrong branch | Same recovery-through-branching skill; progressively more history inspection required. |
| Unit 4 | Recovering After Pointer Movement | Recover after an accidental local reset | Same pointer recovery skill; progressively less explicit saved-reference guidance. |
| Unit 4 | Preserving Detached Work | Save work created from a detached HEAD or non-branch position | Same reachability skill; progressively more ambiguity around where work is located. |
| Unit 5 | Divergent Branches | Resolve divergent branches after team edits | Same integration skill; progressively less explicit branch/task mapping. |
| Unit 5 | Understanding Merge Conflict State | Finish a merge after conflict markers appear | Same merge-continuation skill; progressively less file-level guidance. |
| Unit 5 | Branch Cleanup After Integration | Clean up a merged feature branch | Same branch deletion skill; progressively more reliance on branch inspection. |
| Unit 6 | Diagnose the Repository Before Acting | Choose the correct repair path | Mixed prior skills; difficulty changes how clearly the problem category is signaled. |
| Unit 6 | Complete a Local Feature Workflow | Integrate, recover, and clean up local feature work | Mixed prior skills; difficulty changes workflow length and ambiguity. |

## Staging and Commit Authoring Rules

For staging scenarios, the scenario must always tell the student which work is ready and which work is not ready. The Easy level may name exact files in the task prompt. Medium may name the business meaning of each file and rely on the expected-state diagram. Hard may require students to inspect status/diff output, but the simulator must still provide enough information to infer the intended file.

For commit scenarios, include a commit-message expectation when message intent is educationally important. Student-facing text should say something like "Use a commit message that communicates the configuration update" or "Commit intent: update app configuration." Avoid saying "type `git commit -m ...`" because that exposes part of the answer.

For evaluator design, repository state remains the primary success criterion in the MVP. The implemented target-rule vocabulary may also enforce lightweight commit-message intent, latest-commit file inclusion/exclusion, required working-tree leftovers, and branch pointer targets where a scenario needs those checks. Exact full-message matching should still be avoided unless an instructor has a clear reason to grade an exact phrase.

## Branch and Push Authoring Rules

Every branch-related scenario must name or reveal the final branch expectation. Easy should state the target branch directly. Medium may state it in the task prompt or expected-state diagram. Hard may require the student to infer it from the professional context, but the final branch must still be unambiguous.

The current MVP should not include push scenarios because the system does not connect to external remotes. The simulator also does not model remote refs as first-class assessed targets. Any future push scenario must specify:

- Remote name, such as `origin`.
- Local source branch.
- Remote destination branch.
- Whether the push should create a new branch, update an existing branch, or be avoided.
- Whether force push is prohibited, allowed, or required.
- Whether upstream tracking should be set.
- The exact remote-state target rule used by the evaluator.

## Retry Variant Rules

Retry variants should not be cosmetic renames only. They are owned by a specific difficulty instance and must change at least one structural property while preserving the same skill focus and difficulty-level intent:

- Different file names and project domain.
- Different branch names.
- Different commit messages.
- Different number of files where appropriate.
- Different graph shape when the concept allows it.
- Different conflict file for merge-conflict scenarios.

For RTA-eligible retries, the system should serve a changed variant from the same difficulty instance after a failed or abandoned attempt when a structurally distinct variant exists. Easy retries should not pull from Medium or Hard variant pools, because those levels may have different ambiguity, target-state complexity, and command-count expectations.

## Current-Release Boundaries

- All practice uses the backend Repository State Simulator.
- No student command is executed by a shell or real Git CLI.
- No GitHub, GitLab, Bitbucket, external remote, pull request, or actual push workflow is connected.
- Expected-state diagrams appear only on Easy and Medium.
- Contextual feedback appears only on Easy.
- Hard uses only the live DAG and narrative context.
- Review Mode is playable and logged separately from primary KPI records.
- Scenario text must never expose a complete correct command sequence.

## MVP Scope Recommendation

The improved six-unit path is the preferred curriculum architecture. If the team must reduce scope for the pilot, keep Units 2 through 5 and treat Unit 6 as an optional capstone library. Do not remove Unit 4 recovery before Unit 5 integration; that ordering is important because it prepares students to handle conflicts and divergence without destructive avoidance behavior.

Minimum viable pilot set:

- Unit 2: two scenario skill focuses.
- Unit 3: two scenario skill focuses.
- Unit 4: one or two recovery skill focuses.
- Unit 5: three collaboration/integration skill focuses.

Preferred pilot set:

- All minimum viable pilot scenarios.
- Unit 6 with at least two mixed-workflow capstone skill focuses.

## Implementation Alignment Notes

The current implementation now treats `DifficultyInstance` as the playable configuration boundary. Each Easy, Medium, and Hard difficulty instance can define its own narrative, task prompt, target-state rule, command-count policy, expected-state behavior, and difficulty-owned variant pool. The seeded starter content follows the improved six-unit path, places local undo/recovery before collaboration/integration, and includes the Unit 6 capstone.

The evaluator can confirm broad state outcomes such as branch presence, branch absence, branch pointer targets, HEAD branch, clean working tree, empty staging area, conflict-free state, minimum commit depth, equal branch pointers, required working-tree paths, latest-commit file contents, latest-commit exclusions, and message-keyword intent. This supports partial-staging tasks where the student must commit one requested file while leaving draft work uncommitted.

Remaining curriculum work should focus on adding more authored variants and future advanced Git operations only after the simulator supports them. Remote pushes are described as collaboration context but are not executed by the MVP simulator.

# **GIT it\! — Complete Curriculum Guide**

## **5 Modules · 40 Lessons · Scenario-Driven Learning** 

## *A practical Git training platform for junior developers* *Designed around industry research · Scenario-based practice · DAG-driven learning*

## ---

## **Table of Contents**

* ## Module 0 — Orientation · 8 Lessons · Prerequisite Gate

* ## Module 1 — Local Repository Foundations · 9 Lessons · 9 Scenario Skill Focuses

* ## Module 2 — Branching and Collaboration · 9 Lessons · 9 Scenario Skill Focuses

* ## Module 3 — Conflict Resolution · 6 Lessons · 5 Scenario Skill Focuses

* ## Module 4 — Advanced Recovery and History · 8 Lessons · 6 Scenario Skill Focuses

## **Legend:** ◆ \= Includes scenario practice sessions

## ---

## **Module 0 — Orientation**

## **Prerequisite Gate · 8 Lessons · No Scenario Practice**

### **Module Overview**

## Before students touch a scenario, they need a working mental model of Git and familiarity with the platform itself. This module covers Git installation, command line basics, how Git tracks changes through the working directory–staging area–commit history pipeline, and how to read a DAG (Directed Acyclic Graph). No scenario practice is available in this module — completing all eight lessons is the required prerequisite gate before any scenario session in Modules 1–4 can be started.

## The Orientation Completion Gate (OCG) is enforced at the system level. Students who attempt to access any scenario workspace without completing all eight lessons will be redirected back to their last incomplete orientation lesson.

## ---

### **Lesson 0.1 — What is Git and Why Does it Matter?**

## **Type:** Conceptual · No scenario practice

#### **Learning Outcomes**

* ## Explain what version control is and why it matters in software development

* ## Distinguish Git from other version control systems

* ## Describe the core problems Git solves: history tracking, collaboration, and recovery

#### **Content Summary**

## This lesson establishes the *why* before the *how*. Students learn that Git is a distributed version control system — not just a backup tool — and that understanding it at a conceptual level before touching commands is the foundation everything else builds on.

## Key concepts introduced:

* ## Version control as a discipline, not just a tool

* ## Distributed vs centralized version control

* ## The three problems Git solves: tracking change history, enabling parallel work, and recovering from mistakes

* ## Why Git is the industry standard and what that means for junior developers

#### **No Commands Introduced**

## *This lesson is entirely conceptual. No terminal interaction required.*

## ---

### **Lesson 0.2 — Installing Git and Setting Up Your Environment**

## **Type:** Setup · No scenario practice

#### **Learning Outcomes**

* ## Install Git on Windows, macOS, and Linux

* ## Configure Git with a global username and email

* ## Verify installation and list active configuration values

#### **Content Summary**

## Students install Git and perform first-time configuration. The emphasis is on understanding *what* the configuration values do and *why* they matter — commit authorship — rather than just running commands blindly.

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git --version` | Verify Git installation |
| `git config --global user.name "Name"` | Set global commit author name |
| `git config --global user.email "email"` | Set global commit author email |
| `git config --list` | List all active configuration values |

#### **No Scenario Practice**

## ---

### **Lesson 0.3 — Command Line Basics for Git Users**

## **Type:** Foundational · No scenario practice

#### **Learning Outcomes**

* ## Navigate the filesystem using the command line

* ## Create directories and files from the terminal

* ## Read file contents without opening a GUI editor

#### **Content Summary**

## Many Git errors come from students not knowing where they are in the filesystem. This lesson addresses that directly — building just enough command line fluency to make Git usage comfortable, without trying to be a comprehensive shell course.

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `pwd` | Print current working directory |
| `ls` | List directory contents |
| `ls -la` | List all files including hidden, with details |
| `cd <path>` | Change directory |
| `mkdir <name>` | Create a new directory |
| `touch <file>` | Create a new empty file |
| `cat <file>` | Print file contents to terminal |
| `echo "text" > file` | Write text to a file |

#### **No Scenario Practice**

## ---

### **Lesson 0.4 — The Git Diagram: How Git Thinks About Your Files**

## **Type:** Conceptual · No scenario practice

#### **Learning Outcomes**

* ## Name Git's four areas: working directory, staging area, local repository, and remote repository

* ## Describe what happens to a file as it moves through each area

* ## Explain why the staging area exists and what problem it solves

#### **Content Summary**

## This is one of the most important conceptual lessons in the entire curriculum. The four-area model is the mental framework students will use throughout every scenario in Modules 1–4. Understanding *where a file is* at any given moment — and which commands move it between areas — is the foundation of repository-state reasoning.

## The GIT it\! platform's live DAG is introduced here as a visual representation of this model. Students see how the DAG updates as files move through the pipeline.

## Key concepts:

* ## Working directory: the files you can see and edit

* ## Staging area (index): the files Git is preparing to commit

* ## Local repository: committed history stored on your machine

* ## Remote repository: shared history stored on a server

#### **No Commands Introduced**

## *This lesson is entirely conceptual and visual.*

#### **No Scenario Practice**

## ---

### **Lesson 0.5 — Understanding Commits and Commit History**

## **Type:** Conceptual · No scenario practice

#### **Learning Outcomes**

* ## Describe what a Git commit is and what data it stores

* ## Explain how commits form a linked chain of history

* ## Understand what a commit hash is and why it is immutable

#### **Content Summary**

## Students learn what actually gets saved when they run `git commit` — not just file contents, but author, timestamp, message, and a pointer to the parent commit. This immutability is introduced here because it underpins why rewriting history (Module 4\) is a significant operation.

## Key concepts:

* ## Commit anatomy: hash, author, timestamp, message, tree, parent pointer

* ## Commit chains: how each commit points to its parent

* ## Immutability: why changing a commit creates a new one rather than modifying the old one

* ## The relationship between commits and the DAG

#### **No Commands Introduced**

#### **No Scenario Practice**

## ---

### **Lesson 0.6 — Reading a DAG: Branches, HEAD, and Commit Graphs**

## **Type:** Conceptual \+ Visual · No scenario practice · **OCG critical lesson**

#### **Learning Outcomes**

* ## Read a commit graph and identify branch pointers, HEAD, and merge points

* ## Explain what HEAD is and what it means for HEAD to be detached

* ## Use `git log` with graph flags to visualize repository history in the terminal

#### **Content Summary**

## This is one of the two OCG-critical lessons (alongside 0.7). Students who cannot read a DAG will struggle with every scenario in the platform, because the live DAG is the primary feedback mechanism across all difficulty levels.

## Students practice reading DAGs in three forms: the platform's visual DAG, terminal `git log --graph` output, and hand-drawn diagrams. They learn to identify:

* ## Commit nodes and their hash abbreviations

* ## Branch labels and where they point

* ## HEAD and its relationship to the current branch

* ## Divergence points and merge commits

* ## Detached HEAD state and what causes it

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git log --oneline --graph --all` | Visualize full commit graph with branches |

#### **No Scenario Practice**

## ---

### **Lesson 0.7 — Git Command Anatomy**

## **Type:** Conceptual · No scenario practice · **OCG critical lesson**

#### **Learning Outcomes**

* ## Identify the components of a Git command: base command, subcommand, options, and arguments

* ## Use `git help` and `-h` flags to read built-in documentation

* ## Explain the difference between a flag, an option, and a positional argument

#### **Content Summary**

## The second OCG-critical lesson. Students who understand command anatomy can read error messages, parse documentation, and figure out unfamiliar commands independently — which is essential for scenario practice at Medium and Hard levels where contextual hints are reduced or removed.

## Key concepts:

* ## `git <subcommand> [options] [arguments]` structure

* ## Short flags (`-m`) vs long flags (`--message`)

* ## How to read a man page / `--help` output

* ## Common patterns: `git <verb> <target>`, `git <verb> --flag <value>`

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git help` | Open Git help overview |
| `git <subcommand> -h` | Show quick help for a specific subcommand |

#### **No Scenario Practice**

## ---

### **Lesson 0.8 — How GIT it\! Works: The Platform Walkthrough**

## **Type:** Platform orientation · No scenario practice

#### **Learning Outcomes**

* ## Navigate the GIT it\! platform interface

* ## Understand how the scenario workspace is structured

* ## Identify the three scaffolding tiers: Easy (full support), Medium (partial), Hard (DAG only)

#### **Content Summary**

## The final orientation lesson walks students through the platform itself before they attempt any scenario. Students learn what each UI element does, what the difficulty levels mean in terms of available support, and how the adaptive retry system works when a session fails or is abandoned.

## Key concepts covered:

* ## The scenario workspace layout: terminal panel, DAG panel, feedback panel, expected-state diagram

* ## Difficulty tiers and what scaffolding is available at each:

  * ## **Easy:** Live DAG \+ expected-state diagram \+ contextual feedback panel

  * ## **Medium:** Live DAG \+ expected-state diagram

  * ## **Hard:** Live DAG only

* ## The adaptive retry system: how changed-variant templates work

* ## How to use the Progress Dashboard to track KPI metrics

* ## Resumable sessions: how to return to an in-progress scenario

#### **No Commands Introduced**

#### **No Scenario Practice**

## ---

## **Module 1 — Local Repository Foundations**

## **9 Lessons · 9 Scenario Skill Focuses · Based on Chapters 2–3** *Mapped to: SO 1.1–SO 1.10*

### **Module Overview**

## This module builds the complete local Git workflow from an empty folder to a multi-commit history. Students learn to initialize and clone repositories, understand how files move through Git's four areas, stage and unstage with precision, commit with quality messages, amend commits, ignore unwanted files, read diffs, and interpret repository state and history in the terminal.

## All nine lessons in this module include scenario practice. Scenario difficulty follows the Easy → Medium → Hard scaffolding ladder, with the contextual feedback panel available only on Easy, the expected-state diagram on Easy and Medium, and the live DAG on all three levels.

## ---

### **Lesson 1.1 — Initializing a Local Repository ◆**

## **Scenario Skill Focus:** Repository initialization *Mapped to: SO 1.1*

#### **Learning Outcomes**

* ## Initialize a new Git repository in an existing directory

* ## Initialize a new Git repository in a new named directory

* ## Interpret the output of `git status` in a freshly initialized repository

#### **Content Summary**

## Students learn that `git init` does one thing: creates the `.git` folder that makes a directory a Git repository. The lesson covers what lives inside `.git` (briefly — no deep dive), why you should never manually edit it, and how to verify initialization succeeded using `git status`.

## Common mistakes addressed:

* ## Running `git init` inside an already-initialized repository

* ## Running `git init` in the wrong directory

* ## Confusing an initialized repository with a cloned one

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git init` | Initialize a repository in the current directory |
| `git init <directory>` | Initialize a repository in a named directory |
| `git status` | Show working tree and staging area state |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** directory structures, project names, pre-existing file states, and repository starting conditions.

## ---

### **Lesson 1.2 — Cloning a Remote Repository ◆**

## **Scenario Skill Focus:** Fresh clone setup *Mapped to: SO 1.2*

#### **Learning Outcomes**

* ## Clone a remote repository using HTTPS and SSH URL formats

* ## Clone into a custom-named local directory

* ## Verify a successful clone by inspecting remote configuration and commit history

#### **Content Summary**

## Cloning is distinct from initializing — students learn that `git clone` does more than copy files: it sets up the remote tracking relationship, copies the full commit history, and checks out the default branch. The difference between `origin` and the local branch is introduced here.

## Key concepts:

* ## What `origin` is and why it exists

* ## HTTPS vs SSH clone URLs: when each is used

* ## How `git remote -v` confirms the remote connection

* ## What `git log --oneline` shows after a fresh clone

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git clone <url>` | Clone a repository into a new directory |
| `git clone <url> <directory>` | Clone into a custom-named directory |
| `git remote -v` | Show remote connections |
| `git log --oneline` | Show condensed commit history |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** URL formats (HTTPS/SSH), destination directory names, post-clone verification tasks.

## ---

### **Lesson 1.3 — Staging and Committing: The Basic Workflow ◆**

## **Scenario Skill Focus:** Stage-and-commit workflow *Mapped to: SO 1.3*

#### **Learning Outcomes**

* ## Stage individual files and entire directories for commit

* ## Write commits with descriptive, imperative-mood commit messages

* ## Understand the relationship between staging and committing as a two-step process

#### **Content Summary**

## The core Git workflow. Students learn that staging is a deliberate act — you are constructing the next commit, not just saving — and that commit messages are communication, not bookkeeping. The platform's message-quality validator enforces imperative mood and a minimum descriptiveness threshold.

## Key concepts:

* ## Why `git add` and `git commit` are separate steps

* ## `git add <file>` vs `git add .`: precision vs convenience

* ## Commit message conventions: imperative mood, what-and-why not what-and-how

* ## The relationship between staging area state and DAG output

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git add <file>` | Stage a specific file |
| `git add .` | Stage all changes in the current directory |
| `git commit -m "message"` | Commit staged changes with a message |
| `git status` | Verify staging state before committing |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** file counts, directory depths, commit scope descriptions, message quality validation edge cases.

## ---

### **Lesson 1.4 — Ignoring Files with .gitignore ◆**

## **Scenario Skill Focus:** .gitignore setup *Mapped to: SO 1.4*

#### **Learning Outcomes**

* ## Create and commit a `.gitignore` file

* ## Write ignore patterns for files, directories, and file extensions

* ## Verify that ignored files are excluded from `git status` output

#### **Content Summary**

## Students learn that `.gitignore` is just a text file with pattern rules, but that those rules need to be understood precisely — particularly the difference between ignoring a file before it is tracked vs trying to ignore an already-tracked file. The lesson addresses the most common junior developer mistake: committing `node_modules`, build artifacts, or secrets, then trying to un-track them.

## Key concepts:

* ## Pattern syntax: `*.log`, `build/`, `!important.log`

* ## Directory vs file patterns

* ## The already-tracked file problem: `.gitignore` does not un-track

* ## Using `git status` to confirm ignore rules are working

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git status` | Verify ignored files are not shown as untracked |
| `git add .gitignore` | Stage the ignore rules file itself |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** project types (Node, Python, Java), ignore pattern complexity, directory structures, already-tracked file edge cases.

## ---

### **Lesson 1.5 — Partial Staging and git add \-p ◆**

## **Scenario Skill Focus:** Partial staging *Mapped to: SO 1.5*

#### **Learning Outcomes**

* ## Use `git add -p` to stage individual hunks from a modified file

* ## Inspect the staged diff to verify partial staging results

* ## Unstage a specific file without discarding working tree changes

#### **Content Summary**

## Partial staging is where Git starts feeling like a precision tool rather than a blunt instrument. Students learn that a single file can contain changes for multiple logical purposes, and that `git add -p` lets them construct commits with surgical precision. This lesson directly supports clean commit history — a skill that matters in team environments.

## Key concepts:

* ## What a "hunk" is in Git's diff output

* ## Interactive staging: `y`, `n`, `s` (split), `q` (quit) responses

* ## How `git diff --staged` confirms what is actually staged

* ## Why partial staging produces better commit history

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git add -p` | Interactively stage hunks from modified files |
| `git diff --staged` | Show diff of staged changes vs last commit |
| `git reset HEAD <file>` | Unstage a file while keeping working tree changes |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** file sizes, hunk counts, required staging precision levels, mixed-purpose change contexts.

## ---

### **Lesson 1.6 — Amending Commits ◆**

## **Scenario Skill Focus:** Commit amendment *Mapped to: SO 1.6*

#### **Learning Outcomes**

* ## Amend the most recent commit message

* ## Amend the most recent commit to include additional staged changes

* ## Understand why amending rewrites history and when it is safe to do so

#### **Content Summary**

## Amending is the first history-rewriting operation students encounter. The lesson is careful to frame amendment as a *local* operation that is safe before pushing, and dangerous after — planting the seed for the revert-vs-reset-vs-rebase discussion in Module 4\.

## Key concepts:

* ## What amendment actually does: creates a new commit with a new hash

* ## Safe amendment: only amend commits that have not been pushed

* ## Message-only amendment vs content amendment

* ## How the DAG changes after an amendment (old commit disappears, new one appears)

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git commit --amend` | Amend the last commit (opens editor for message) |
| `git commit --amend -m "new message"` | Amend message inline |
| `git commit --amend --no-edit` | Amend content without changing the message |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** amendment types (message-only vs content), repository states, staged content before amendment.

## ---

### **Lesson 1.7 — Unstaging and Discarding Changes ◆**

## **Scenario Skill Focus:** Unstage and discard *Mapped to: SO 1.7*

#### **Learning Outcomes**

* ## Unstage a file from the staging area without discarding working tree changes

* ## Discard working tree changes and restore a file to its last committed state

* ## Distinguish between unstaging (safe) and discarding (destructive)

#### **Content Summary**

## This lesson draws a critical line between two operations that beginners often confuse: removing something from the staging area (reversible) vs discarding working tree changes (irreversible without reflog). The lesson emphasizes understanding consequences before running commands — a theme that carries through Module 4\.

## Key concepts:

* ## Unstaging vs discarding: what each operation affects

* ## Why discarding working tree changes is destructive (no undo without reflog)

* ## The `git restore` family: modern syntax vs legacy `git checkout --`

* ## When to use each based on repository state

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git restore <file>` | Discard working tree changes (restore from last commit) |
| `git restore --staged <file>` | Unstage a file (keep working tree changes) |
| `git checkout -- <file>` | Legacy: discard working tree changes |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** mixed staged/unstaged states, partial discard targets, multi-file repository conditions.

## ---

### **Lesson 1.8 — Reading Repository Status and History ◆**

## **Scenario Skill Focus:** Repository reading *Mapped to: SO 1.8 (covers Lessons 1.6 and 1.9 content)*

#### **Learning Outcomes**

* ## Interpret `git status` output across all four repository states: clean, untracked, modified, staged

* ## Read `git log` output and extract commit metadata

* ## Use `git log` flags to filter, format, and graph commit history

* ## Read diffs across the working directory, staging area, and commit history

#### **Content Summary**

## Reading repository state is not a passive skill — it is the primary diagnostic tool students use during every scenario. This lesson consolidates status, log, and diff reading into one focused unit because they answer the same question from different angles: *what is the state of this repository right now?*

## Key concepts:

* ## `git status` output anatomy: branch line, tracking line, staged/unstaged/untracked sections

* ## `git log` output anatomy: hash, author, date, message

* ## Log flags for filtering: `--oneline`, `--graph`, `--all`, `--author`, `-n`

* ## Diff reading: what `git diff` (working vs staged), `git diff --staged` (staged vs last commit), and `git diff HEAD` (working vs last commit) each show

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git status` | Show full working tree and staging area state |
| `git log` | Show full commit history |
| `git log --oneline` | Show condensed one-line commit history |
| `git log --oneline --graph --all` | Show full commit graph |
| `git diff` | Show unstaged changes (working vs staging) |
| `git diff --staged` | Show staged changes (staging vs last commit) |
| `git diff HEAD` | Show all changes since last commit |
| `git diff <commit>` | Show changes since a specific commit |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

## **Scenario variants rotate:** repository states, log output complexity, diff area combinations, flag selection challenges.

## ---

### **Lesson 1.9 — Module 1 Review and Practice ◆**

## **Scenario Skill Focus:** Full local workflow integration *Mapped to: SO 1.9 (HLCR), SO 1.10 (ARC/CHFR)*

#### **Learning Outcomes**

* ## Complete a full local repository workflow from initialization to multi-commit history independently

* ## Demonstrate competency across all nine Module 1 skill areas at Hard level

* ## Apply repository-state reasoning without scaffolding support

#### **Content Summary**

## The Module 1 capstone practice session. No new commands are introduced. Instead, students are presented with multi-step scenarios that require combining skills from all eight preceding lessons — initializing, staging, committing, amending, ignoring, partial staging, unstaging, and reading state — in a single session.

## This lesson's scenario sessions are the primary source of HLCR and ARC data for Module 1\.

#### **No New Commands Introduced**

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×3 | Live DAG only |

## **Scenario variants rotate:** full workflow complexity, combined skill requirement depth, multi-step task narratives.

## 

## 

## **Module 2 — Branching and Collaboration**

**9 Lessons · 9 Scenario Skill Focuses · Based on Chapters 4–5** *Mapped to: SO 2.1–SO 2.11*

### **Module Overview**

This module covers the complete branching and remote collaboration workflow. Students learn to create, switch, name, and delete branches; stash work in progress; push to and pull from remotes; reconcile diverged histories; complete fast-forward, three-way, and squash merges; and recover deleted remote branches.

Module 2 is where Git stops being a personal tool and becomes a team tool. Every lesson is framed around realistic team collaboration scenarios. The live DAG is particularly important here — branch pointer movement and merge commit structure are both much easier to understand visually than textually.

---

### **Lesson 2.1 — Creating and Switching Branches ◆**

**Scenario Skill Focus:** Branch creation and switching *Mapped to: SO 2.1*

#### **Learning Outcomes**

* Create a new branch from the current HEAD  
* Switch between existing branches  
* Create and switch to a new branch in a single command  
* Verify branch creation and HEAD movement using the live DAG

#### **Content Summary**

Branching is Git's most important feature for team collaboration. Students learn that a branch is just a pointer — a lightweight label that moves forward with each new commit. Creating one is cheap; the mental model shift it enables is enormous.

Key concepts:

* What a branch pointer actually is (a movable label to a commit)  
* Why branching is cheap in Git compared to other VCS  
* The relationship between HEAD and the current branch  
* Modern syntax (`git switch`) vs legacy syntax (`git checkout`)

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git branch <name>` | Create a new branch at current HEAD |
| `git switch <name>` | Switch to an existing branch |
| `git switch -c <name>` | Create and switch to a new branch |
| `git checkout -b <name>` | Legacy: create and switch to a new branch |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** repository topologies, base branch conditions, multi-branch starting states, HEAD positions.

---

### **Lesson 2.2 — Branch Naming Conventions and Housekeeping ◆**

**Scenario Skill Focus:** Branch management *Mapped to: SO 2.2*

#### **Learning Outcomes**

* Apply standard branch naming conventions across common workflow types  
* List local and remote branches  
* Delete merged branches safely  
* Force-delete unmerged branches and understand the risk

#### **Content Summary**

Poor branch naming is one of the most common team Git anti-patterns. This lesson establishes naming conventions as professional practice — not just preference — and teaches the housekeeping operations that keep a repository clean over time.

Key concepts:

* Common naming conventions: `feature/`, `fix/`, `hotfix/`, `release/`, `chore/`  
* Kebab-case rules and character restrictions  
* Why `git branch -d` refuses to delete unmerged branches (and why that is a safety feature)  
* When `git branch -D` (force delete) is and is not appropriate  
* Listing all branches including remote-tracking with `git branch -a`

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git branch` | List local branches |
| `git branch -d <name>` | Delete a merged branch |
| `git branch -D <name>` | Force-delete a branch regardless of merge status |
| `git branch -a` | List all branches including remote-tracking |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** workflow types, naming convention violations, merged vs unmerged branch states, multi-branch cleanup tasks.

---

### **Lesson 2.3 — Stashing Work in Progress ◆**

**Scenario Skill Focus:** Stash and restore *Mapped to: SO 2.3*

#### **Learning Outcomes**

* Stash uncommitted changes to a temporary storage area  
* Restore the most recent stash entry to the working tree  
* List and manage multiple stash entries  
* Drop stash entries that are no longer needed

#### **Content Summary**

Stashing solves a very specific problem: you are mid-task and need to switch context immediately. Students learn that the stash is a stack, not a single slot, and that understanding the stash as temporary storage — not long-term storage — is the right mental model.

Key concepts:

* The stash as a stack: LIFO behavior  
* When to stash vs when to commit a WIP checkpoint  
* The risk of accumulating stash entries and forgetting them  
* Branch-switching without stashing: what Git allows vs what it refuses

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git stash` | Stash current working tree and staging area changes |
| `git stash pop` | Apply the most recent stash and remove it from the stack |
| `git stash list` | List all stash entries |
| `git stash drop` | Delete the most recent stash entry |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** mid-task context-switch triggers, stash stack depths, branch switching conditions, multi-stash management tasks.

---

### **Lesson 2.4 — Pushing to a Remote ◆**

**Scenario Skill Focus:** Remote push *Mapped to: SO 2.4*

#### **Learning Outcomes**

* Push a local branch to a remote repository  
* Set upstream tracking on a first push  
* Handle a rejected push caused by remote divergence  
* Use `--force-with-lease` safely when a rewrite is intentional

#### **Content Summary**

Pushing introduces the concept of the remote as a shared, authoritative repository — and with it, the first set of push failure scenarios. Students learn that a rejected push is not an error to be overridden with `--force`; it is a signal to reconcile first.

Key concepts:

* What upstream tracking is and why it matters  
* Why pushes get rejected: the remote has commits the local branch does not  
* `--force` vs `--force-with-lease`: why the latter is always preferred when forcing is necessary  
* How the DAG shows the divergence that causes a push rejection

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git push origin <branch>` | Push a local branch to origin |
| `git push -u origin <branch>` | Push and set upstream tracking |
| `git push --force-with-lease` | Force push only if no one else has pushed |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** first-push vs subsequent-push contexts, rejected push conditions, upstream tracking states, force-with-lease safety scenarios.

---

### **Lesson 2.5 — Fetching and Pulling from a Remote ◆**

**Scenario Skill Focus:** Fetch and pull *Mapped to: SO 2.5*

#### **Learning Outcomes**

* Fetch remote changes without integrating them into the working branch  
* Pull remote changes and integrate them via merge  
* Pull remote changes and integrate them via rebase  
* Decide between fetch-then-inspect and direct pull based on team context

#### **Content Summary**

The fetch vs pull distinction is one of the most important judgment calls in collaborative Git use. Students learn that `git pull` is shorthand for `git fetch + git merge` — and that understanding this decomposition lets them make better decisions about when to inspect before integrating.

Key concepts:

* What `git fetch` does: updates remote-tracking branches without touching local branches  
* What `git pull` does: fetch \+ integrate (merge or rebase)  
* `git pull --rebase`: keeping a linear history when pulling  
* When to use each: `fetch` for inspection, `pull` for trusted fast-forward scenarios

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git fetch origin` | Download remote changes without integrating |
| `git pull` | Fetch and integrate (merge by default) |
| `git pull --rebase` | Fetch and integrate via rebase |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** remote-state conditions, fast-forward vs diverged scenarios, fetch-then-decide vs pull-directly contexts.

---

### **Lesson 2.6 — Reconciling Diverged Local and Remote Histories ◆**

**Scenario Skill Focus:** Diverged history reconciliation *Mapped to: SO 2.6*

#### **Learning Outcomes**

* Identify that a local branch has diverged from its remote counterpart  
* Reconcile the divergence by fetching and merging or rebasing  
* Complete a successful push after reconciliation  
* Read the ahead/behind relationship in the live DAG

#### **Content Summary**

Diverged histories happen whenever two contributors push to the same branch without coordinating. This lesson teaches students to diagnose the divergence using the DAG and to choose the right reconciliation strategy based on whether the team values merge commits or linear history.

Key concepts:

* What "ahead" and "behind" mean in remote-tracking context  
* Why the remote rejects a push when histories have diverged  
* Reconcile-then-push as the correct workflow  
* Merge commit vs rebase as reconciliation strategies: tradeoffs

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git fetch origin` | Update remote-tracking branches |
| `git merge origin/main` | Merge remote changes into local branch |
| `git pull --rebase` | Rebase local commits on top of remote |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** divergence depths (1 commit vs many), merge vs rebase reconciliation requirements, ahead/behind count complexity.

---

### **Lesson 2.7 — Completing Branch Merges ◆**

**Scenario Skill Focus:** Merge type selection *Mapped to: SO 2.7*

#### **Learning Outcomes**

* Complete a fast-forward merge and explain when it applies  
* Complete a three-way merge and explain when Git requires it  
* Force a merge commit even when fast-forward is possible using `--no-ff`  
* Read the resulting DAG structure after each merge type

#### **Content Summary**

Students learn that merge type is determined by repository topology, not choice — with one exception: `--no-ff` forces a merge commit even when fast-forward is possible. This is important for teams that want explicit merge commits as branch-history markers.

Key concepts:

* Fast-forward: the target branch is a direct ancestor of the source branch  
* Three-way: the branches have diverged; Git needs a merge commit  
* `--no-ff`: why some teams prefer explicit merge commits  
* How to read the DAG to predict which merge type will occur

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git merge <branch>` | Merge a branch (fast-forward if possible) |
| `git merge --no-ff <branch>` | Force a merge commit even if fast-forward is possible |
| `git log --oneline --graph` | Verify merge result structure |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** branch topologies that force different merge types, `--no-ff` requirement contexts, post-merge DAG reading tasks.

---

### **Lesson 2.8 — Squash Merging ◆**

**Scenario Skill Focus:** Squash merge *Mapped to: SO 2.8*

#### **Learning Outcomes**

* Complete a squash merge to consolidate a feature branch into a single commit  
* Understand what squash merging does to the branch DAG  
* Write a meaningful consolidated commit message after a squash  
* Compare squash merge output to three-way and fast-forward merge output in the DAG

#### **Content Summary**

Squash merging is a team history-cleanliness strategy. Students learn that `--squash` does not automatically commit — it stages the combined changes and waits for a deliberate commit message. This two-step nature makes the operation feel weightier, which reinforces the deliberateness it requires.

Key concepts:

* What squash merge does: collapses N commits into staged changes  
* Why squash merge requires a separate commit step  
* The DAG after squash: the feature branch is not merged, it is copied-and-collapsed  
* When squash is preferred: noisy WIP history, clean main branch requirements

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git merge --squash <branch>` | Stage all changes from branch as a single set |
| `git commit -m "message"` | Commit the squashed staged changes |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** feature branch commit densities, consolidated message writing contexts, squash vs merge comparison tasks.

---

### **Lesson 2.9 — Deleting and Recovering Remote Branches ◆**

**Scenario Skill Focus:** Remote branch recovery *Mapped to: SO 2.9*

#### **Learning Outcomes**

* Delete a remote branch from the local terminal  
* Prune stale remote-tracking references  
* Recover an accidentally deleted remote branch from a local tracking reference

#### **Content Summary**

Remote branch deletion is a team operation with consequences. Students learn that deleting a remote branch does not delete the commits — just the label — and that recovery is possible as long as someone has a local tracking reference. This lesson plants the seed for reflog recovery in Module 4\.

Key concepts:

* The difference between a remote branch and a remote-tracking branch  
* What `--prune` does to stale tracking references  
* Recovery path: finding the commit the branch pointed to and recreating the label  
* Why remote branch deletion should be a coordinated team action

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git push origin --delete <branch>` | Delete a branch on the remote |
| `git fetch --prune` | Remove stale remote-tracking references |
| `git switch -c <branch> origin/<branch>` | Recreate a local branch from a remote-tracking ref |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** branch deletion contexts, prune requirement states, recovery from remote-tracking refs, merged vs unmerged deletion scenarios.

---

## **Module 3 — Conflict Resolution**

**6 Lessons · 5 Scenario Skill Focuses · Based on Chapter 6** *Mapped to: SO 3.1–SO 3.6*

### **Module Overview**

This module addresses conflict resolution — one of the most anxiety-inducing situations for junior developers. Students learn what causes conflicts, how to read conflict markers precisely, resolve conflicts manually and with a merge tool, apply conflict prevention strategies, and selectively apply commits through cherry-picking.

The framing throughout this module is deliberate: conflicts are not failures, they are a normal part of collaborative development. The platform's contextual feedback panel is particularly valuable here on Easy level, narrating what each unresolved marker means and what the consequence of premature staging would be.

---

### **Lesson 3.1 — What Causes Merge Conflicts ◆**

**Scenario Skill Focus:** Conflict identification *Mapped to: SO 3.1*

#### **Learning Outcomes**

* Identify the three main causes of merge conflicts: overlapping edits, divergent histories, and upstream changes  
* Recognize a conflict state in `git status` output  
* Understand why Git cannot automatically resolve certain conflicts

#### **Content Summary**

Before students can resolve conflicts, they need to understand why they happen. This lesson breaks down the three conflict causes and shows students how to predict whether a merge will conflict by reading the DAG before executing the merge.

Key concepts:

* Overlapping edits: two branches modified the same lines differently  
* Divergent histories: long-running branches with many diverging commits  
* Upstream changes: a file was deleted on one branch and modified on another  
* How to read `git status` during a conflicted merge state

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git merge <branch>` | Attempt a merge (may produce conflict state) |
| `git status` | Identify which files are in conflict |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** conflict cause types, repository divergence patterns, pre-merge DAG reading tasks.

---

### **Lesson 3.2 — Reading Conflict Markers**

**Type:** Conceptual · No scenario practice

#### **Learning Outcomes**

* Identify the three sections of a Git conflict marker block  
* Understand what `HEAD`, the separator, and the branch name represent in a conflict block  
* Recognize the difference between a fully resolved file and a partially resolved file

#### **Content Summary**

Conflict markers are the format Git uses to annotate conflicting sections of a file. Students learn to read them precisely before they try to resolve them — because the most common resolution mistake is leaving a partial marker in the file.

Key concepts:

* `<<<<<<< HEAD`: start of the current branch's version  
* `=======`: separator between the two versions  
* `>>>>>>> branch-name`: end of the incoming branch's version  
* Why resolving means *replacing the entire marker block* with the correct content  
* How to spot an accidentally left marker using `git diff`

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git diff` | Inspect remaining conflict markers in files |
| `git status` | Check which files still have unresolved conflicts |

#### **No Scenario Practice**

*This lesson is conceptual preparation for Lesson 3.3.*

---

### **Lesson 3.3 — Resolving Conflicts Manually ◆**

**Scenario Skill Focus:** Manual conflict resolution *Mapped to: SO 3.2*

#### **Learning Outcomes**

* Edit conflicted files to produce a correct resolved version  
* Stage resolved files to signal completion to Git  
* Complete the merge commit after all conflicts are resolved  
* Abort a merge in progress and return to the pre-merge state

#### **Content Summary**

Manual conflict resolution is the core skill. Students work through conflicts by editing the marker blocks directly — deciding which version to keep, how to combine both, or how to write an entirely new resolution. The platform's Easy-level feedback panel highlights unresolved markers and warns about premature staging.

Key concepts:

* The resolution workflow: edit → stage → commit  
* How to tell Git a file is resolved: `git add <file>`  
* What "premature staging" means and why it matters  
* `git merge --abort`: the escape hatch when resolution is too complex

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git add <resolved-file>` | Mark a file as resolved |
| `git commit` | Complete the merge commit |
| `git merge --abort` | Abort the merge and return to pre-merge state |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** conflict complexity, file types, resolution strategies (keep ours / keep theirs / combine), abort-then-retry scenarios.

---

### **Lesson 3.4 — Using a Merge Tool ◆**

**Scenario Skill Focus:** Mergetool workflow *Mapped to: SO 3.3*

#### **Learning Outcomes**

* Configure a merge tool in Git's global configuration  
* Launch `git mergetool` to resolve conflicts in a three-panel interface  
* Complete the merge after resolving all conflicts through the tool  
* Understand when a merge tool is more efficient than manual resolution

#### **Content Summary**

Merge tools provide a three-panel view: current branch, incoming branch, and the merged result. Students learn to configure and launch a merge tool, navigate the resolution interface, and complete the merge. The lesson does not prescribe a specific tool — it focuses on the workflow pattern that works across all of them.

Key concepts:

* What a merge tool shows: BASE (common ancestor), LOCAL (current branch), REMOTE (incoming branch), MERGED (result)  
* How `git mergetool` iterates through conflicted files  
* Configuring a tool: `git config merge.tool <toolname>`  
* When merge tools add value vs when manual resolution is faster

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git mergetool` | Launch the configured merge tool for all conflicts |
| `git config merge.tool` | Set or inspect the configured merge tool |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** tool configuration contexts, conflict complexity levels, multi-file conflict scenarios.

---

### **Lesson 3.5 — Conflict Prevention Strategies**

**Type:** Conceptual · No scenario practice

#### **Learning Outcomes**

* Apply fetch-before-merge as a proactive conflict prevention habit  
* Use branch comparison to identify divergence before merging  
* Understand how small, frequent integrations reduce conflict severity

#### **Content Summary**

Prevention is better than resolution. This lesson shifts from reactive to proactive — teaching students the habits that reduce conflict frequency and severity. The strategies here are team behaviors, not just individual commands.

Key concepts:

* Fetch-before-merge: checking for remote changes before starting a merge  
* `git diff main..feature`: previewing what a merge will bring in  
* Short-lived branches as a conflict prevention strategy  
* Coordination patterns: who merges, when, and how often

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git fetch origin` | Check remote for new commits before merging |
| `git diff main..feature` | Preview changes a merge would introduce |

#### **No Scenario Practice**

*This lesson is conceptual and strategic.*

---

### **Lesson 3.6 — Cherry-Picking Commits ◆**

**Scenario Skill Focus:** Cherry-pick workflow *Mapped to: SO 3.4*

#### **Learning Outcomes**

* Apply a specific commit from one branch to another using cherry-pick  
* Cherry-pick without immediately committing to review changes first  
* Abort a cherry-pick operation in progress  
* Understand when cherry-pick is and is not the right tool

#### **Content Summary**

Cherry-picking is selective history application — taking one commit's changes and replaying them on a different branch. Students learn the operation, its appropriate use cases (backporting a fix to a release branch), and its risks (duplicated commits causing later confusion).

Key concepts:

* What cherry-pick does: replays the *diff* of a commit, not the commit itself  
* The resulting DAG: a new commit with a new hash appears on the target branch  
* `--no-commit`: applying changes to the staging area for review before committing  
* When to avoid cherry-pick: large feature work better handled by merge or rebase

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git cherry-pick <hash>` | Apply a specific commit to the current branch |
| `git cherry-pick --no-commit <hash>` | Apply changes without committing |
| `git cherry-pick --abort` | Abort a cherry-pick in progress |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** source/target branch combinations, single vs multi-commit cherry-picks, no-commit mode contexts, abort-and-retry scenarios.

---

## 

## 

## 

## 

## 

## **Module 4 — Advanced Recovery and History**

**8 Lessons · 6 Scenario Skill Focuses · Based on Chapters 7–8** *Mapped to: SO 4.1–SO 4.8*

### **Module Overview**

This module equips students with Git's most powerful — and most feared — tools: rebasing, interactive history editing, reflog navigation, and recovery from destructive operations. These are the skills that separate junior developers who are afraid of Git from those who can confidently operate in complex team environments.

Module 4 is deliberately the most demanding. Hard-level completion targets are reduced to ≥65% (from ≥70% in Modules 1–3) to reflect the genuine complexity of these operations. The Scenario Abandonment Rate (SAR) is monitored here specifically because abandonment risk is highest when scenarios involve destructive operations and students are unsure whether they can recover.

Every scenario in this module is framed as a realistic team emergency: a hard reset on the wrong branch, a commit that must be reverted from a shared remote, a rebase sequence that went wrong mid-execution. The narrative framing is intentional — it contextualizes the stress of recovery operations and builds the confidence that comes from completing them.

---

### **Lesson 4.1 — Rebasing: Rewriting History as a Straight Line ◆**

**Scenario Skill Focus:** Basic branch rebase *Mapped to: SO 4.5 (partial)*

#### **Learning Outcomes**

* Rebase a feature branch onto an updated base branch  
* Continue a rebase after resolving a conflict mid-sequence  
* Abort a rebase and return to the pre-rebase state  
* Read the resulting linear DAG structure after a successful rebase

#### **Content Summary**

Rebasing moves commits. More precisely, it replays them — taking each commit from the feature branch and re-applying it on top of the updated base. Students learn that rebase produces a cleaner linear history than merge, at the cost of rewriting commit hashes. This tradeoff is the central concept of the lesson.

Key concepts:

* What rebase actually does: replays commits, creating new hashes  
* Why rebased commits have different hashes than the originals  
* Rebase vs merge: linear history vs explicit merge commits  
* The golden rule of rebasing: never rebase commits that have been pushed to a shared remote  
* Handling conflicts during a rebase: resolve → `git rebase --continue`

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git rebase <branch>` | Rebase current branch onto another branch |
| `git rebase -i <branch>` | Interactive rebase (preview of Lesson 4.2) |
| `git rebase --continue` | Continue rebase after resolving a conflict |
| `git rebase --abort` | Abort rebase and restore pre-rebase state |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** base branch update depths, conflict-during-rebase conditions, rebase vs merge decision contexts, post-rebase DAG verification tasks.

---

### **Lesson 4.2 — Interactive Rebase: Cleaning Up Commit History**

**Type:** Conceptual \+ Demonstration · No scenario practice

#### **Learning Outcomes**

* Use `git rebase -i` to review and modify a sequence of commits  
* Apply the `pick`, `squash`, `reword`, `drop`, and `edit` actions  
* Understand the implications of each action on the resulting commit graph  
* Recognize when interactive rebase is the right tool vs squash merge

#### **Content Summary**

Interactive rebase is Git's commit history editor. Students learn to use it to clean up WIP commit histories before merging to main — combining fixup commits, rewording unclear messages, and dropping accidental commits. The lesson does not include scenario practice because the operation requires careful multi-step input that is better learned through guided demonstration before being tested in scenarios.

The capstone in Lesson 4.7 tests interactive rebase in a full recovery sequence.

Key concepts:

* The rebase todo list: what each line represents  
* Actions: `pick` (keep), `squash` (combine with previous), `reword` (edit message), `drop` (remove), `edit` (pause and amend)  
* How the resulting DAG changes with each action type  
* `git rebase -i HEAD~n`: selecting the last N commits for editing

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git rebase -i HEAD~<n>` | Open interactive rebase for the last N commits |
| `git rebase -i <branch>` | Open interactive rebase for commits since branch divergence |
| `git rebase --continue` | Continue after an `edit` pause |
| `git rebase --abort` | Abort and restore original state |

#### **No Scenario Practice**

*Interactive rebase is assessed in SO 4.5 via the Lesson 4.7 capstone scenario.*

---

### **Lesson 4.3 — Navigating Reflog: Finding What Git Remembers ◆**

**Scenario Skill Focus:** Reflog navigation *Mapped to: SO 4.1*

#### **Learning Outcomes**

* Read `git reflog` output and identify HEAD movement events  
* Locate a specific prior HEAD position by its reflog index  
* Inspect a commit referenced in the reflog before acting on it  
* Create a new branch pointing to a reflog-referenced commit

#### **Content Summary**

Reflog is Git's safety net. It records every position HEAD has ever been at — including positions that no longer appear in `git log` because they were "lost" by a reset or rebase. Students learn that "lost" commits are almost never truly gone; they live in the reflog for 30 days by default.

Key concepts:

* What the reflog records: HEAD positions, not just commits  
* Reflog notation: `HEAD@{0}`, `HEAD@{1}`, `HEAD@{n}`  
* How to read the action column: `commit`, `reset`, `rebase`, `checkout`  
* The difference between `git log` and `git reflog`: one shows the current branch's history, the other shows HEAD's movement history

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git reflog` | Show the log of all HEAD positions |
| `git show HEAD@{n}` | Inspect the commit at a specific reflog position |
| `git reset --hard HEAD@{n}` | Move HEAD to a specific reflog position |
| `git switch -c <branch> HEAD@{n}` | Create a new branch at a reflog position |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** reflog output complexity, HEAD movement patterns, target commit identification difficulty, recovery branch naming requirements.

---

### **Lesson 4.4 — Recovering from a Hard Reset ◆**

**Scenario Skill Focus:** Hard reset recovery *Mapped to: SO 4.2*

#### **Learning Outcomes**

* Recognize the consequences of a destructive `git reset --hard`  
* Use `git reflog` to locate the commit that was lost  
* Recover the lost commit by creating a new branch at the reflog reference  
* Understand the difference between `--soft`, `--mixed`, and `--hard` reset modes

#### **Content Summary**

A `git reset --hard` to the wrong target is one of the most panic-inducing mistakes a junior developer can make. This lesson teaches the recovery procedure and, in doing so, removes the fear that makes the mistake so paralyzing — because a confident developer who knows recovery is possible is less likely to avoid Git operations that might go wrong.

Key concepts:

* The three reset modes: `--soft` (moves HEAD, keeps everything staged), `--mixed` (moves HEAD, unstages), `--hard` (moves HEAD, discards everything — destructive)  
* Why `--hard` feels irreversible but usually is not  
* The reflog recovery window: 30 days by default  
* The recovery workflow: `git reflog` → identify target → `git switch -c recovery-branch HEAD@{n}`

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git reset --hard HEAD~n` | Destructively move HEAD back N commits |
| `git reset --hard <hash>` | Destructively move HEAD to a specific commit |
| `git reflog` | Locate commits lost by a hard reset |
| `git switch -c <branch> <hash>` | Recover a lost commit onto a new branch |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** reset depth (HEAD\~1 vs HEAD\~3+), repository state complexity, recovery target identification difficulty, post-recovery verification tasks.

---

### **Lesson 4.5 — Reversing Pushed Commits Safely ◆**

**Scenario Skill Focus:** Pushed commit reversal *Mapped to: SO 4.3*

#### **Learning Outcomes**

* Reverse a pushed commit using `git revert` without rewriting shared history  
* Create a revert commit with and without opening the editor  
* Revert a non-HEAD commit by specifying its hash  
* Explain why `git revert` is preferred over `git reset` for pushed commits

#### **Content Summary**

When a bad commit has already been pushed to a shared remote, the solution is not to rewrite history — it is to add a new commit that undoes the bad one. Students learn that `git revert` is not just a safer alternative to `git reset`; it is the *correct* tool for reversing shared history because it preserves the complete record of what happened.

Key concepts:

* Why `git reset` is dangerous on pushed commits: it rewrites history that others may have based work on  
* What `git revert` does: creates a new commit that is the inverse of the target  
* `--no-edit`: skipping the commit message editor for a standard revert message  
* Multi-commit revert: reversing several commits requires individual revert operations  
* How the DAG looks after a revert: the bad commit remains, a new undo commit appears after it

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git revert HEAD` | Revert the most recent commit |
| `git revert HEAD --no-edit` | Revert without opening the message editor |
| `git revert <hash>` | Revert a specific commit by hash |
| `git push` | Push the revert commit to the remote |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** pushed commit depths, revert target positions (HEAD vs non-HEAD), post-revert push contexts, revert vs reset decision scenarios.

---

### **Lesson 4.6 — Diagnosing Branch Divergence ◆**

**Scenario Skill Focus:** Branch divergence diagnosis *Mapped to: SO 4.4*

#### **Learning Outcomes**

* Identify the common ancestor of two diverged branches  
* Calculate ahead/behind counts between branches  
* List commits that exist on one branch but not the other  
* Read the divergence structure in the live DAG

#### **Content Summary**

Before rebasing or merging a complex diverged situation, students need to understand exactly what has diverged and by how much. This lesson teaches the diagnostic commands that answer: *where did these branches split, how far have they gone, and what commits does each one have that the other does not?*

Key concepts:

* Common ancestor: the last commit shared by both branches  
* Ahead/behind: how many commits each branch has since the common ancestor  
* `git log branch1..branch2`: commits in branch2 not in branch1  
* `git diff branch1...branch2`: changes since the common ancestor (three-dot diff)

#### **Commands Introduced**

| Command | Purpose |
| ----- | ----- |
| `git merge-base <branch1> <branch2>` | Find the common ancestor commit |
| `git rev-list --count <branch1>..<branch2>` | Count commits in branch2 not in branch1 |
| `git log <branch1>..<branch2>` | List commits in branch2 not in branch1 |
| `git diff <branch1>...<branch2>` | Show changes since common ancestor |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×2 | Live DAG \+ expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** divergence depths, multi-branch comparison tasks, ahead/behind count complexity, pre-rebase diagnosis requirements.

---

### **Lesson 4.7 — Capstone: Full Rebase Recovery Sequence ◆**

**Scenario Skill Focus:** Capstone rebase recovery *Mapped to: SO 4.5 (HLCR), SO 4.7 (ARC/RTA/CHFR), SO 4.8 (SAR)*

#### **Learning Outcomes**

* Execute a complete multi-step rebase recovery sequence under realistic conditions  
* Combine reflog navigation, branch divergence diagnosis, interactive rebase, and conflict resolution in a single scenario  
* Complete the sequence without dropping, duplicating, or orphaning commits  
* Demonstrate systematic repository-state reasoning under complexity

#### **Content Summary**

The Module 4 capstone. No new commands are introduced. Students are presented with a realistic team emergency: a rebase sequence that went wrong, leaving commits in an inconsistent state. The recovery requires using every tool introduced in Module 4 — reflog navigation to find the pre-rebase state, divergence diagnosis to understand what was lost, interactive rebase to reconstruct the clean history, and conflict resolution where branches have overlapping changes.

This lesson's Hard-level scenarios are the primary source of HLCR, ARC, RTA, and SAR data for Module 4\. The SAR target is specifically monitored here because the multi-step complexity creates the highest abandonment risk in the entire curriculum.

**Scenario framing:** Each scenario is presented as a realistic team incident — e.g., "You ran a rebase on the wrong branch and pushed before you noticed. Two teammates have already pulled. Recover the intended history without disrupting their work."

#### **No New Commands Introduced**

All commands used in this lesson have been introduced in Lessons 4.1–4.6:

| Command | Introduced In |
| ----- | ----- |
| `git reflog` | Lesson 4.3 |
| `git log --oneline --graph --all` | Lesson 0.6 |
| `git merge-base` | Lesson 4.6 |
| `git rebase` | Lesson 4.1 |
| `git rebase -i` | Lesson 4.2 |
| `git rebase --continue` | Lesson 4.1 |
| `git rebase --abort` | Lesson 4.1 |
| `git switch -c <branch> HEAD@{n}` | Lesson 4.3 |

#### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ expected-state diagram \+ feedback panel |
| Medium | ×3 | Live DAG \+ expected-state diagram |
| Hard | ×3 | Live DAG only |

*Note: Hard ×3 (vs ×2 in other lessons) reflects the capstone's role as the primary HLCR measurement point for Module 4\.*

**Scenario variants rotate:** rebase failure modes, divergence complexity, commit recovery targets, conflict patterns during recovery.

---

### **Lesson 4.8 — Git Proficiency and What Comes Next**

**Type:** Reflection and roadmap · No scenario practice

#### **Learning Outcomes**

* Reflect on skill progression from Module 0 to Module 4  
* Identify the Git operations that will matter most in their first team environment  
* Map GIT it\! curriculum coverage to real-world workflow contexts  
* Understand what Git topics exist beyond this curriculum

#### **Content Summary**

The closing lesson. Students review the full arc of what they have learned and, just as importantly, understand where this curriculum ends and what comes next. This lesson is not filler — it is an honest accounting of what GIT it\! covers and what it does not, with pointers to where students can go next.

Topics covered:

* Curriculum recap: what each module built toward  
* First-job Git reality: the 20% of commands that cover 80% of daily work  
* Topics beyond this curriculum: Git hooks, submodules, worktrees, bisect, large file storage  
* Recommended next resources: Pro Git (Chacon & Straub), GitHub Flow documentation, conventional commits specification

#### **No Commands Introduced**

#### **No Scenario Practice**

---

## **Appendix A — Complete Command Reference**

All commands introduced across the GIT it\! curriculum, organized by module.

### **Module 0 — Orientation**

| Command | Lesson | Purpose |
| ----- | ----- | ----- |
| `git --version` | 0.2 | Verify Git installation |
| `git config --global user.name` | 0.2 | Set global commit author name |
| `git config --global user.email` | 0.2 | Set global commit author email |
| `git config --list` | 0.2 | List all active configuration values |
| `pwd` | 0.3 | Print current working directory |
| `ls` | 0.3 | List directory contents |
| `ls -la` | 0.3 | List all files including hidden |
| `cd` | 0.3 | Change directory |
| `mkdir` | 0.3 | Create a directory |
| `touch` | 0.3 | Create an empty file |
| `cat` | 0.3 | Print file contents |
| `echo` | 0.3 | Write text to a file |
| `git log --oneline --graph --all` | 0.6 | Visualize full commit graph |
| `git help` | 0.7 | Open Git help overview |
| `git <subcommand> -h` | 0.7 | Show quick help for a subcommand |

### **Module 1 — Local Repository Foundations**

| Command | Lesson | Purpose |
| ----- | ----- | ----- |
| `git init` | 1.1 | Initialize a repository |
| `git init <directory>` | 1.1 | Initialize in a named directory |
| `git clone <url>` | 1.2 | Clone a repository |
| `git clone <url> <directory>` | 1.2 | Clone into a custom directory |
| `git remote -v` | 1.2 | Show remote connections |
| `git add <file>` | 1.3 | Stage a specific file |
| `git add .` | 1.3 | Stage all changes |
| `git commit -m "message"` | 1.3 | Commit with a message |
| `git status` | 1.1/1.3 | Show repository state |
| `git add .gitignore` | 1.4 | Stage the ignore rules file |
| `git add -p` | 1.5 | Interactively stage hunks |
| `git diff --staged` | 1.5/1.8 | Show staged diff |
| `git reset HEAD <file>` | 1.5 | Unstage a file |
| `git commit --amend` | 1.6 | Amend the last commit |
| `git commit --amend -m` | 1.6 | Amend with new message inline |
| `git commit --amend --no-edit` | 1.6 | Amend content only |
| `git restore <file>` | 1.7 | Discard working tree changes |
| `git restore --staged <file>` | 1.7 | Unstage a file |
| `git checkout -- <file>` | 1.7 | Legacy: discard changes |
| `git log` | 1.8 | Show commit history |
| `git log --oneline` | 1.8 | Show condensed history |
| `git diff` | 1.8 | Show unstaged changes |
| `git diff HEAD` | 1.8 | Show all changes since last commit |
| `git diff <commit>` | 1.8 | Show changes since a commit |

### **Module 2 — Branching and Collaboration**

| Command | Lesson | Purpose |
| ----- | ----- | ----- |
| `git branch <name>` | 2.1 | Create a new branch |
| `git switch <name>` | 2.1 | Switch to a branch |
| `git switch -c <name>` | 2.1 | Create and switch to a branch |
| `git checkout -b <name>` | 2.1 | Legacy: create and switch |
| `git branch` | 2.2 | List local branches |
| `git branch -d <name>` | 2.2 | Delete a merged branch |
| `git branch -D <name>` | 2.2 | Force-delete a branch |
| `git branch -a` | 2.2 | List all branches |
| `git stash` | 2.3 | Stash changes |
| `git stash pop` | 2.3 | Apply and remove top stash |
| `git stash list` | 2.3 | List stash entries |
| `git stash drop` | 2.3 | Delete top stash entry |
| `git push origin <branch>` | 2.4 | Push a branch |
| `git push -u origin <branch>` | 2.4 | Push and set upstream |
| `git push --force-with-lease` | 2.4 | Safe force push |
| `git fetch origin` | 2.5 | Fetch without integrating |
| `git pull` | 2.5 | Fetch and merge |
| `git pull --rebase` | 2.5/2.6 | Fetch and rebase |
| `git merge origin/main` | 2.6 | Merge remote tracking branch |
| `git merge <branch>` | 2.7 | Merge a branch |
| `git merge --no-ff <branch>` | 2.7 | Force merge commit |
| `git merge --squash <branch>` | 2.8 | Squash merge |
| `git push origin --delete <branch>` | 2.9 | Delete remote branch |
| `git fetch --prune` | 2.9 | Remove stale tracking refs |
| `git switch -c <branch> origin/<branch>` | 2.9 | Recover from remote-tracking ref |

### **Module 3 — Conflict Resolution**

| Command | Lesson | Purpose |
| ----- | ----- | ----- |
| `git merge <branch>` | 3.1 | Attempt a merge |
| `git diff` | 3.2 | Inspect conflict markers |
| `git add <resolved>` | 3.3 | Mark file as resolved |
| `git commit` | 3.3 | Complete merge commit |
| `git merge --abort` | 3.3 | Abort merge in progress |
| `git mergetool` | 3.4 | Launch merge tool |
| `git config merge.tool` | 3.4 | Set merge tool |
| `git diff main..feature` | 3.5 | Preview merge changes |
| `git cherry-pick <hash>` | 3.6 | Apply a specific commit |
| `git cherry-pick --no-commit <hash>` | 3.6 | Apply without committing |
| `git cherry-pick --abort` | 3.6 | Abort cherry-pick |

### **Module 4 — Advanced Recovery and History**

| Command | Lesson | Purpose |
| ----- | ----- | ----- |
| `git rebase <branch>` | 4.1 | Rebase onto a branch |
| `git rebase -i <branch>` | 4.1/4.2 | Interactive rebase |
| `git rebase --continue` | 4.1 | Continue after conflict |
| `git rebase --abort` | 4.1 | Abort rebase |
| `git rebase -i HEAD~<n>` | 4.2 | Interactive rebase last N commits |
| `git reflog` | 4.3 | Show HEAD position history |
| `git show HEAD@{n}` | 4.3 | Inspect a reflog position |
| `git reset --hard HEAD@{n}` | 4.3 | Move HEAD to reflog position |
| `git reset --hard HEAD~n` | 4.4 | Destructive reset back N commits |
| `git reset --hard <hash>` | 4.4 | Destructive reset to a commit |
| `git revert HEAD` | 4.5 | Revert most recent commit |
| `git revert HEAD --no-edit` | 4.5 | Revert without editor |
| `git revert <hash>` | 4.5 | Revert a specific commit |
| `git merge-base <b1> <b2>` | 4.6 | Find common ancestor |
| `git rev-list --count <b1>..<b2>` | 4.6 | Count diverged commits |
| `git log <b1>..<b2>` | 4.6 | List commits in b2 not in b1 |
| `git diff <b1>...<b2>` | 4.6 | Show changes since common ancestor |

---

## **Appendix B — Scenario Count Summary**

| Module | Lessons with Scenarios | Total Easy | Total Medium | Total Hard | Total Sessions |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Module 0 | 0 | 0 | 0 | 0 | 0 |
| Module 1 | 9 | 25 | 20 | 19 | 64 |
| Module 2 | 9 | 25 | 21 | 18 | 64 |
| Module 3 | 4 | 11 | 10 | 8 | 29 |
| Module 4 | 6 | 17 | 17 | 13 | 47 |
| **Total** | **28** | **78** | **68** | **58** | **204** |

---

## **Appendix C — Scaffolding by Difficulty Level**

| Feature | Easy | Medium | Hard |
| ----- | ----- | ----- | ----- |
| Live DAG (real-time commit graph) | ✓ | ✓ | ✓ |
| Expected-state diagram | ✓ | ✓ | — |
| Contextual feedback panel | ✓ | — | — |
| Command hardcap enforcement | ✓ | ✓ | ✓ |
| Adaptive retry variation | ✓ | ✓ | ✓ |
| Resumable sessions | ✓ | ✓ | ✓ |

---

## **Appendix D — KPI Measurement Points by Module**

| KPI | M0 | M1 | M2 | M3 | M4 |
| ----- | ----- | ----- | ----- | ----- | ----- |
| OCG | ✓ | — | — | — | — |
| SCR | — | ✓ | ✓ | ✓ | ✓ |
| CAR | — | ✓ | ✓ | ✓ | ✓ |
| HLCR | — | ✓ | ✓ | ✓ | ✓ (≥65%) |
| ARC | — | ✓ | ✓ | ✓ | ✓ (≤3) |
| RTA | — | — | — | ✓ | ✓ |
| CHFR | — | ✓ | ✓ | ✓ | ✓ |
| SAR | — | — | — | — | ✓ |

---

*GIT it\! · Complete Curriculum Guide · BSIT-3 · Cebu Institute of Technology – University* *Based on: Learning Git by Anna Skoulikari (primary) · Pro Git by Chacon & Straub (Module 4 supplementary)*


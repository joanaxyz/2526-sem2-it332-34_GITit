# **Module 1 — Local Repository Foundations**

**9 Lessons · 9 Scenario Skill Focuses · Based on Chapters 2–3**  
 *Mapped to: SO 1.1 – SO 1.10*

---

## **Module Overview**

This module builds the complete local Git workflow from an empty folder to a multi-commit history with a clean, readable log. Students learn to initialize and clone repositories, understand how files move through Git's four areas, stage and unstage with precision, commit with quality messages, amend commits, ignore unwanted files, read diffs, and interpret repository state and history in the terminal.

All nine lessons include scenario practice. The OCG must be satisfied before any scenario in this module can be started.

**Module KPIs:** CAR, HLCR, ARC, SCR (validity gate)  
 **Measurement validity condition:** SCR ≥ 80% before module KPI data is reportable

---

## **Read-Only Commands Active in This Module**

The following diagnostic commands are non-counted in all Module 1 scenario sessions. Students should use them freely to inspect repository state at any point.

| Command | Introduced | Purpose |
| ----- | ----- | ----- |
| `git status` | 0.4 / 1.1 | 🔍 DIAGNOSTIC — Show working tree and staging area state |
| `git log` | 0.6 / 1.8 | 🔍 DIAGNOSTIC — Show commit history |
| `git log --oneline` | 0.6 / 1.8 | 🔍 DIAGNOSTIC — Condensed commit history |
| `git log --oneline --graph --all` | 0.6 | 🔍 DIAGNOSTIC — Full commit graph |
| `git diff` | 1.8 | 🔍 DIAGNOSTIC — Unstaged changes |
| `git diff --staged` | 1.5 / 1.8 | 🔍 DIAGNOSTIC — Staged changes |
| `git diff HEAD` | 1.8 | 🔍 DIAGNOSTIC — All changes since last commit |
| `git diff --name-only` | 1.8 | 🔍 DIAGNOSTIC — Changed path names only |
| `git remote -v` | 1.2 | 🔍 DIAGNOSTIC — Show remote connections |
| `git check-ignore -v <path>` | 1.4 | 🔍 DIAGNOSTIC — Explain an ignore-rule match |
| `git ls-files` | 1.4 | 🔍 DIAGNOSTIC — List tracked files |

---

## **Lesson 1.1 — Initializing a Local Repository ◆**

**Type:** Scenario · **Scenario Skill Focus:** Repository initialization  
 **Mapped to:** SO 1.1 (CAR ≥ 70%)

### **Learning Outcomes**

* Initialize a new Git repository in an existing directory  
* Initialize a new Git repository in a new named directory  
* Recognize the `.git` directory and understand its role  
* Interpret `git status` output in a freshly initialized, empty repository  
* Avoid common initialization mistakes

### **Content Summary**

`git init` does one thing: it creates a `.git` directory inside the target directory, transforming it into a Git repository. Nothing in the working directory changes — no files are staged or committed by initialization. The repository begins empty.

**What lives inside `.git`:**  
 Students get a brief, non-exhaustive overview: `HEAD` (a text file pointing to the current branch reference), `config` (repository-level configuration), `objects/` (all Git content), `refs/` (all branch and tag pointers). They should never manually edit these files. The `.git` directory is Git's entire database — deleting it destroys the repository history.

**Verifying initialization:**  
 After `git init`, running `git status` shows:

On branch main  
No commits yet  
nothing to commit (create/copy files and use "git add" to track)

This is the correct, expected output for an empty initialized repository.

**Common initialization mistakes:**

* Running `git init` inside an already-initialized repository (harmless but creates confusion)  
* Running `git init` in the home directory instead of the project directory  
* Confusing `git init` (local, starts fresh) with `git clone` (local, copies existing remote)

**`git init` vs `git clone`:**  
 `git init` starts a new, empty repository. `git clone` creates a local copy of an existing remote repository, including the selected branch history and remote configuration. Both produce a local repository — the starting content differs.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git init` | ⚡ ACTION | Initialize a repository in the current directory |
| `git init <directory>` | ⚡ ACTION | Initialize a repository in a new named directory |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Show working tree and staging area state |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** directory structures, project names, pre-existing file states, repository starting conditions.

**Non-counted commands in this scenario:** `git status` is the primary diagnostic tool. Students are encouraged to run it before and after each action command to observe the transition between repository states.

---

## **Lesson 1.2 — Cloning a Remote Repository ◆**

**Type:** Scenario · **Scenario Skill Focus:** Fresh clone setup  
 **Mapped to:** SO 1.2 (CAR ≥ 70%)

### **Learning Outcomes**

* Clone a remote repository using HTTPS and SSH URL formats  
* Clone into a custom-named local directory  
* Verify a successful clone using remote configuration and commit history inspection  
* Explain the difference between `origin` and the local branch

### **Content Summary**

Cloning is distinct from initializing. `git clone` does more than copy files: it sets up the remote tracking relationship, copies commit history from the remote fixture, and checks out the default branch or the branch named with `-b`/`--branch`.

**What `git clone` actually does:**

1. Creates a new local directory (named after the repository by default, or as specified)  
2. Initializes a git repository inside it  
3. Adds a remote named `origin` pointing to the source URL  
4. Records remote-tracking refs such as `origin/main` or `origin/starter`
5. Checks out the selected branch and leaves the working tree clean

**Destination and history options supported in Module 1:**

* Without a destination, the folder is inferred from the URL, such as `docs-portal` from `https://example.test/training/docs-portal.git`.
* With a destination, Git uses the folder name you provide.
* `-b <branch>` and `--branch <branch>` check out a branch that already exists in the simulated remote.
* `--depth <number>` records a shallow clone; `--depth 1` keeps only the selected branch tip visible.

**HTTPS vs SSH clone URLs:**

* **HTTPS** (`https://github.com/user/repo.git`): Works everywhere; GitHub prompts for credentials or uses a credential manager.  
* **SSH** (`git@github.com:user/repo.git`): Requires SSH key setup but does not require credentials on each operation. Preferred in professional environments.

**What `origin` is:**  
 `origin` is the default alias Git assigns to the remote a repository was cloned from. It is just a name — it can be renamed or additional remotes can be added. `git remote -v` shows all configured remotes and their URLs.

**Post-clone verification:**

* `git remote -v` confirms the remote connection is configured  
* `git log --oneline` shows the cloned commit history  
* `git status` confirms the working tree is clean and HEAD is on the expected branch

🔍 **`git remote -v`, `git log --oneline`, and `git status` are diagnostic commands.** Non-counted in all scenario sessions.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git clone <url>` | ⚡ ACTION | Clone a repository into a new directory |
| `git clone <url> <directory>` | ⚡ ACTION | Clone into a custom-named directory |
| `git clone -b <branch> <url>` | ⚡ ACTION | Clone and check out a specific branch |
| `git clone --branch <branch> <url> <directory>` | ⚡ ACTION | Clone a specific branch into a custom directory |
| `git clone --depth <number> <url>` | ⚡ ACTION | Clone shallow history |
| `git clone --depth <number> -b <branch> <url> <directory>` | ⚡ ACTION | Shallow clone a selected branch into a custom directory |
| `git remote -v` | 🔍 DIAGNOSTIC — Non-Counted | Show remote connections and their URLs |
| `git log --oneline` | 🔍 DIAGNOSTIC — Non-Counted | Show condensed commit history |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** URL formats (HTTPS/SSH), destination directory names, post-clone verification task types.

---

## **Lesson 1.3 — Staging and Committing: The Basic Workflow ◆**

**Type:** Scenario · **Scenario Skill Focus:** Stage-and-commit workflow  
 **Mapped to:** SO 1.3 (CAR ≥ 70%)

### **Learning Outcomes**

* Stage individual files and entire directories for commit  
* Write commits with descriptive, imperative-mood messages  
* Understand the two-step commit process and why it exists  
* Verify staging state using `git status` before committing

### **Content Summary**

The core Git workflow. Staging is a deliberate act — you are constructing the next commit, not just saving. Commit messages are communication to future collaborators (including your future self), not bookkeeping labels.

**Why staging and committing are separate steps:**  
 If Git committed everything in the working directory every time you ran `git commit`, commits would be uncontrolled. The staging area lets you choose exactly what goes into each commit, producing a history where each commit represents a single logical change. This is the difference between a commit history that tells a story and one that is noise.

**`git add` precision:**

* `git add <file>` stages a specific file  
* `git add .` stages all changes in the current directory and subdirectories  
* `git add <directory>/` stages all changes inside a specific directory

The platform's State-Based Evaluator accepts any sequence of `git add` commands that results in the correct staging state — not one specific form.

**Commit message conventions:**  
 The platform's message-quality validator enforces:

* Imperative mood: "Add login validation" not "Added login validation" or "Adding login validation"  
* Minimum descriptiveness: the message must describe what the commit does, not just "update" or "fix"  
* Subject line length: recommended ≤ 72 characters

**`git commit -m` vs `git commit`:**  
 `git commit -m "message"` writes the message inline. `git commit` without `-m` opens the configured text editor for the message. In scenario sessions, inline `-m` is the standard form. The editor form is covered in Lesson 0.2 (configuration) but is not tested in scenarios.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git add <file>` | ⚡ ACTION | Stage a specific file |
| `git add .` | ⚡ ACTION | Stage all changes in the current directory |
| `git add <directory>/` | ⚡ ACTION | Stage all changes inside a directory |
| `git commit -m "message"` | ⚡ ACTION | Commit staged changes with an inline message |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Verify staging state before committing |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×3 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** file counts, directory depths, commit scope descriptions, message quality validation edge cases.

---

## **Lesson 1.4 — Ignoring Files with .gitignore ◆**

**Type:** Scenario · **Scenario Skill Focus:** .gitignore setup  
 **Mapped to:** SO 1.4 (CAR ≥ 70%)

### **Learning Outcomes**

* Create and commit a `.gitignore` file  
* Write ignore patterns for files, directories, and file extensions  
* Verify that ignored files are excluded from `git status` output  
* Understand why `.gitignore` cannot un-track already-tracked files

### **Content Summary**

`.gitignore` is a plain text file containing pattern rules that tell Git which files and directories to ignore entirely — they will not appear in `git status` as untracked and cannot be staged or committed while ignored.

**Pattern syntax:**

| Pattern | What it matches |
| ----- | ----- |
| `*.log` | Any file ending in `.log` anywhere in the repo |
| `build/` | A directory named `build` anywhere in the repo |
| `!important.log` | Exception — do not ignore this specific file |
| `/secrets.txt` | Only `secrets.txt` at the root level |
| `**/temp` | Any file or directory named `temp` at any depth |

**Common files that should always be ignored:**  
 `node_modules/`, `__pycache__/`, `.env`, `*.pyc`, `dist/`, `build/`, `.DS_Store` (macOS), `Thumbs.db` (Windows). Most language ecosystems have standard `.gitignore` templates — GitHub's repository creation flow offers them automatically.

**The already-tracked file problem:**  
 `.gitignore` only prevents *untracked* files from being tracked. If a file is already tracked (it has been committed at least once), adding it to `.gitignore` does nothing — Git will continue tracking changes to it. To stop tracking an already-tracked file, you must use `git rm --cached <file>` to remove it from the index without deleting it from the working directory, then commit the removal. This is one of the most common junior developer mistakes.

**Committing `.gitignore` itself:**  
 The `.gitignore` file should always be committed to the repository so all collaborators get the same ignore rules. It is a regular file — stage it with `git add .gitignore` and commit it like any other file.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git add .gitignore` | ⚡ ACTION | Stage the ignore rules file |
| `git rm --cached <file>` | ⚡ ACTION | Un-track an already-tracked file without deleting it |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Verify ignored files are not shown as untracked |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** project types (Node.js, Python, Java), ignore pattern complexity, directory structures, already-tracked file edge cases.

---

## **Lesson 1.5 — Partial Staging and git add \-p ◆**

**Type:** Scenario · **Scenario Skill Focus:** Partial staging  
 **Mapped to:** SO 1.5 (CAR ≥ 70%)

### **Learning Outcomes**

* Use `git add -p` to stage individual hunks from a modified file  
* Respond correctly to hunk prompts: `y` (stage), `n` (skip), `s` (split), `q` (quit)  
* Inspect the staged diff to verify partial staging results  
* Unstage a specific file without discarding working tree changes

### **Content Summary**

Partial staging is where Git starts feeling like a precision tool rather than a blunt instrument. A single file can contain changes for multiple logical purposes — a bug fix and a refactor in the same file. `git add -p` lets you stage only the parts of the file relevant to the current commit.

**What a hunk is:**  
 Git's diff algorithm divides changes into contiguous sections called hunks. A hunk is a block of changed lines surrounded by context lines. When you run `git add -p`, Git presents each hunk one at a time and asks whether to stage it.

**Hunk prompt responses:**

| Response | Meaning |
| ----- | ----- |
| `y` | Stage this hunk |
| `n` | Do not stage this hunk |
| `s` | Split into smaller hunks (if possible) |
| `q` | Quit — don't stage this or any remaining hunks |
| `a` | Stage this and all remaining hunks in this file |
| `d` | Don't stage this or any remaining hunks in this file |
| `?` | Print help |

**Verifying partial staging:**  
 After `git add -p`, run `git diff --staged` to see exactly what is staged, and `git diff` to see what remains unstaged. Both are diagnostic — use them freely.

🔍 **`git diff --staged` and `git diff` are diagnostic commands.** Non-counted. Run them after every partial staging operation to confirm the staging area contains exactly what you intend.

**Unstaging a file:**  
 `git restore --staged <file>` moves a file from the staging area back to the working directory without discarding changes. The file's content is unchanged — it simply moves from "staged" to "modified but unstaged."

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git add -p` | ⚡ ACTION | Interactively stage hunks from modified files |
| `git restore --staged <file>` | ⚡ ACTION | Unstage a file (keep working tree changes) |
| `git diff --staged` | 🔍 DIAGNOSTIC — Non-Counted | Show staged changes vs last commit |
| `git diff` | 🔍 DIAGNOSTIC — Non-Counted | Show unstaged changes (working vs staging) |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×3 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** file sizes, hunk counts, required staging precision levels, mixed-purpose change contexts.

---

## **Lesson 1.6 — Amending Commits ◆**

**Type:** Scenario · **Scenario Skill Focus:** Commit amendment  
 **Mapped to:** SO 1.6 (CAR ≥ 70%)

### **Learning Outcomes**

* Amend the most recent commit message without changing content  
* Amend the most recent commit to include additional staged changes  
* Explain what amendment does to the commit hash and why  
* Understand when amendment is safe (before push) and when it is not (after push)

### **Content Summary**

`git commit --amend` is the first history-rewriting operation students encounter. It replaces the most recent commit with a new commit that includes any currently staged changes and optionally a new message.

**What amendment actually does:**  
 Amendment creates a brand-new commit with a new hash. The old commit is not modified — it is replaced. Because the new commit has a different hash than the old one, this is a history rewrite. The old commit still exists in the reflog for a time, but it is no longer reachable via branch navigation.

**Safe vs unsafe amendment:**

* **Safe:** Amending a commit that has not been pushed to a shared remote. No one else has based work on this commit; rewriting it affects only your local history.  
* **Unsafe:** Amending a commit that has already been pushed. Other contributors may have cloned or pulled that commit. Rewriting it creates a divergence between your local history and the remote — and between your history and your teammates' histories. This requires a force push, which can destroy teammates' work if done carelessly.

This safety principle — *never rewrite commits that have been shared* — is introduced here and reinforced in Module 4 as the "golden rule of rebasing."

**Three amendment forms:**

| Command | Effect |
| ----- | ----- |
| `git commit --amend` | Opens editor — change message and/or include staged changes |
| `git commit --amend -m "new message"` | Replace message inline; include staged changes |
| `git commit --amend --no-edit` | Include staged changes without changing the message |

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git commit --amend` | ⚡ ACTION | Amend last commit (opens editor) |
| `git commit --amend -m "message"` | ⚡ ACTION | Amend with new message inline |
| `git commit --amend --no-edit` | ⚡ ACTION | Amend content without changing message |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** amendment types (message-only vs content), repository states, staged content before amendment.

---

## **Lesson 1.7 — Unstaging and Discarding Changes ◆**

**Type:** Scenario · **Scenario Skill Focus:** Unstage and discard  
 **Mapped to:** SO 1.7 (CAR ≥ 70%)

### **Learning Outcomes**

* Unstage a file from the staging area without discarding working tree changes  
* Discard working tree changes and restore a file to its last committed state  
* Distinguish between unstaging (safe, reversible) and discarding (destructive, irreversible without reflog)  
* Use `git restore` syntax to unstage or discard selected changes

### **Content Summary**

This lesson draws a critical line between two operations that beginners frequently confuse. Unstaging moves a file from the staging area back to the working tree — the changes are still there, just no longer queued for the next commit. Discarding removes working tree changes entirely — the file reverts to its last committed state. Changes discarded this way cannot be recovered without reflog.

**The critical distinction:**

| Operation | Command | Changes preserved? | Safe? |
| ----- | ----- | ----- | ----- |
| Unstage | `git restore --staged <file>` | Yes — still in working tree | ✓ Reversible |
| Discard working tree | `git restore <file>` | No — gone unless in reflog | ✗ Destructive |

**Supported restore syntax:**

The Module 1 simulator uses `git restore` for both unstaging and discarding:

| Action | Command |
| ----- | ----- |
| Unstage file | `git restore --staged <file>` |
| Discard working tree changes | `git restore <file>` |

Other undo forms are intentionally saved for later modules and are not listed in Module 1 preview content.

**When discarding is appropriate:**  
 Discarding working tree changes makes sense when you have made experimental edits that turned out to be wrong and you want to get back to the last committed state cleanly. Before discarding, run `git diff` to verify exactly what you are about to lose.

🔍 **Always run `git diff` and `git status` before discarding.** These are diagnostic commands — non-counted. Understand what you are discarding before you discard it.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git restore <file>` | ⚡ ACTION | Discard working tree changes (restore from last commit) |
| `git restore --staged <file>` | ⚡ ACTION | Unstage a file (keep working tree changes) |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** mixed staged/unstaged states, partial discard targets, multi-file repository conditions.

---

## **Lesson 1.8 — Reading Repository Status and History ◆**

**Type:** Scenario · **Scenario Skill Focus:** Repository reading  
 **Mapped to:** SO 1.8 (LCR — see note below)

⚠️ **KPI Note — Non-Counted Lesson:**  
 The primary skills in this lesson (`git status`, `git log`, `git diff`) are all **diagnostic/read-only commands**. They are **non-counted** in all scenario sessions and **cannot be measured by CAR**. This lesson's scenario practice is retained because reading repository state is a genuine skill that benefits from practice in realistic scenarios — but the applicable KPI is **LCR (Lesson Completion Rate)**, not CAR. The scenario sessions develop diagnostic fluency; they do not produce action command accuracy data.

### **Learning Outcomes**

* Interpret `git status` output across all four states: clean, untracked, modified, staged  
* Read `git log` output and extract commit metadata (hash, author, date, message)  
* Use `git log` flags to filter, format, and graph commit history  
* Read diffs across the working directory, staging area, and commit history  
* Know which `git diff` variant to use for a given inspection need

### **Content Summary**

Reading repository state is not a passive skill — it is the primary diagnostic tool students use during every scenario. `git status`, `git log`, and `git diff` answer the same question from different angles: *what is the state of this repository right now?*

**`git status` output anatomy:**

On branch main  
Your branch is up to date with 'origin/main'.

Changes to be committed:     ← staged area  
  (use "git restore \--staged \<file\>..." to unstage)  
        modified:   app.js

Changes not staged for commit:   ← working tree  
  (use "git add \<file\>..." to update what will be committed)  
        modified:   README.md

Untracked files:    ← not yet in any area  
  (use "git add \<file\>..." to include in what will be committed)  
        config.local.json

**`git log` output anatomy:**

commit a1b2c3d4e5f6... (HEAD \-\> main, origin/main)  
Author: Student Name \<student@email.com\>  
Date:   Mon May 20 14:32:11 2025 \+0800

    Add user authentication module

    Implements JWT-based login and session management.  
    Resolves issue \#42.

**`git log` flag combinations and when to use each:**

| Command | Use when |
| ----- | ----- |
| `git log` | Full commit metadata needed |
| `git log --oneline` | Quick history scan |
| `git log --oneline --graph --all` | Visualizing branch structure |
| `git log -n 5` | Last 5 commits only |
| `git log --max-count=5` | Last 5 commits only |

**The three `git diff` variants:**

| Command | What it compares | Use when |
| ----- | ----- | ----- |
| `git diff` | Working tree vs staging area | What's changed but not yet staged? |
| `git diff --staged` | Staging area vs last commit | What's about to be committed? |
| `git diff HEAD` | Working tree vs last commit | What's changed since last commit (total)? |
| `git diff --name-only` | Working tree vs staging area | Which unstaged paths changed? |

🔍 **All commands in this lesson are diagnostic — non-counted.** The scenario sessions in this lesson focus on selecting the correct diagnostic command for a given inspection need, reading the output accurately, and extracting the correct information. No state-changing commands are required.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Show full working tree and staging area state |
| `git log` | 🔍 DIAGNOSTIC — Non-Counted | Show full commit history with metadata |
| `git log --oneline` | 🔍 DIAGNOSTIC — Non-Counted | Show condensed one-line commit history |
| `git log --oneline --graph --all` | 🔍 DIAGNOSTIC — Non-Counted | Show full commit graph |
| `git log -n <number>` | 🔍 DIAGNOSTIC — Non-Counted | Show last N commits |
| `git log --max-count=<number>` | 🔍 DIAGNOSTIC — Non-Counted | Show last N commits |
| `git diff` | 🔍 DIAGNOSTIC — Non-Counted | Show unstaged changes |
| `git diff --staged` | 🔍 DIAGNOSTIC — Non-Counted | Show staged changes |
| `git diff HEAD` | 🔍 DIAGNOSTIC — Non-Counted | Show all changes since last commit |
| `git diff --name-only` | 🔍 DIAGNOSTIC — Non-Counted | Show unstaged changed path names |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario design note:** Scenarios in this lesson present a repository in a specific state and ask students to use the correct diagnostic command to extract specific information (e.g., "find the commit hash where the database schema was last modified" or "determine whether any staged changes exist before deciding whether to commit"). The State-Based Evaluator tracks which diagnostic commands were run and whether the student extracted the correct information, but these commands do not count toward CAR.

---

## **Lesson 1.9 — Module 1 Review and Practice ◆**

**Type:** Scenario capstone · No new commands  
 **Scenario Skill Focus:** Full local workflow integration  
 **Mapped to:** SO 1.9 (HLCR ≥ 70%) · SO 1.10 (ARC ≤ 2\)

### **Learning Outcomes**

* Complete a full local repository workflow from initialization to multi-commit history independently  
* Demonstrate competency across all Module 1 skill areas at Hard level without scaffolding  
* Apply repository-state reasoning — using diagnostic commands to inform action decisions — in multi-step scenarios

### **Content Summary**

The Module 1 capstone. No new commands are introduced. Students face multi-step scenarios that require combining all eight preceding lessons: initializing, staging, committing, amending, ignoring, partial staging, unstaging, and reading state — in a single session without a predetermined command script.

**What capstone scenarios look like:**  
 A capstone scenario might present a project directory with several files in various states (some modified, some untracked, some already staged), a history of a few commits with a message error in the most recent one, and a `.gitignore` that needs updating. The task requires the student to read the repository state, correct the amendment, stage the right files with appropriate precision, update the ignore rules, and produce a clean, well-described commit history — all within the command limit.

**Hard-level capstone emphasis:**  
 This lesson's Hard-level sessions are the primary measurement point for HLCR in Module 1\. No expected-state diagram is available — students must infer the target state from the narrative alone and use the live DAG to track their progress. This is the closest the platform comes to replicating real working conditions.

**ARC measurement:**  
 This lesson also contributes to the ARC measurement for Module 1\. Multi-step complexity makes retry more likely than in single-skill lessons; ARC ≤ 2 across the module indicates students are building genuine competency rather than cycling through random command attempts.

### **No New Commands Introduced**

All commands used in this lesson were introduced in Lessons 1.1–1.8.

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×3 | Live DAG only |

**Note:** Hard ×3 (vs ×2 in most single-skill lessons) reflects the capstone's role as the primary HLCR measurement point for Module 1\.

**Scenario variants rotate:** full workflow complexity, combined skill requirement depth, multi-step task narratives that require all Module 1 skills.

---

*→ Next: Module 2 — Branching and Collaboration*


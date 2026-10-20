# Module 1 Blueprint — Local Repository Foundations

**6 levels · 37 waves · about 70 min with no failures (today about 71) · Mapped to SO 1.1–SO 1.6 · 18 new scenarios**

## Module overview

Learners build the local workflow from an empty folder to a clean, intentional history: start or copy a repository, stage exactly what belongs in a commit, fix the last commit, and back out of staging and working-tree mistakes.

Chapter description in the seed: *Initialize, clone, stage, commit, ignore, partially stage, amend, clean up, and inspect local Git repositories through scenario practice.*

**Module KPIs:** SCR ≥ 80% (validity gate), CAR ≥ 70%, HLCR ≥ 70%, ARC ≤ 2. Definitions: ARCHITECTURE.md, *Performance metrics*.

## Tiers, scaffolding and rewards

| Tier | Scaffolding | First-clear reward |
|---|---|---:|
| Easy | Live DAG + Expected State + contextual feedback | 25 GitCoins |
| Medium | Live DAG + Expected State | 35 GitCoins |
| Hard | Live DAG only | 50 GitCoins |

Command guides appear whenever a step needs a form the learner hasn't used yet, in any tier. A tier completes when its last wave is cleared; each wave needs one clear. A retry after a failure draws another variant of the same wave.

## Commands introduced in this module

| Command | Type | First wave (command guide) | Used again in |
|---|---|---|---|
| `git init -b <branch> [<directory>]` | ⚡ ACTION | 1.1 Easy 1 · Track this folder | 5 later waves; also in level 1.3 |
| `git init` | ⚡ ACTION | 1.1 Hard 2 · Re-run init safely | setup command, not repeated |
| `git clone <url>` | ⚡ ACTION | 1.2 Easy 1 · Clone a repository | setup command, not repeated |
| `git clone <url> <folder>` | ⚡ ACTION | 1.2 Easy 2 · Clone into a named folder | 1 later wave |
| `git clone -b <branch> <url> [<folder>]` | ⚡ ACTION | 1.2 Easy 3 · Clone a specific branch | setup command, not repeated |
| `git clone --depth <n> <url> [<folder>]` | ⚡ ACTION | 1.2 Medium 2 · Shallow history | 1 later wave |
| `git clone --depth <n> -b <branch> <url> [<folder>]` | ⚡ ACTION | 1.2 Hard 1 · Shallow copy of one branch | setup command, not repeated |
| `git add <path>...` | ⚡ ACTION | 1.3 Easy 1 · Stage and commit one change | 24 later waves; also in levels 1.4, 1.5, 2.2, 2.4, 2.7, 3.1, 3.3, 4.3 |
| `git commit -m <message>` | ⚡ ACTION | 1.3 Easy 1 · Stage and commit one change | 25 later waves; also in levels 1.4, 1.5, 1.6, 2.2, 2.4, 2.6, 2.7, 2.8, 3.3 |
| technique: several-paths | Technique | 1.3 Easy 2 · Stage several files at once | 4 later waves; also in level 1.6 |
| `git add -p <path>` | ⚡ ACTION | 1.4 Easy 1 · Stage one hunk | 7 later waves; also in levels 1.5, 1.6 |
| `git commit --amend -m <message>` | ⚡ ACTION | 1.5 Easy 1 · Fix the last commit message | 7 later waves; also in levels 2.4, 4.2 |
| `git restore --staged <path>...` | ⚡ ACTION | 1.6 Easy 1 · Unstage but keep the edit | 5 later waves; also in level 2.6 |
| `git restore <path>...` | ⚡ ACTION | 1.6 Easy 2 · Throw away a working change | 4 later waves; also in level 2.2 |

## Diagnostic commands (non-counted)

`git status`, `git log` and `git diff` are always free to run. This module's answer keys need no other diagnostics.

---

## Level 1.1 — Initializing Repositories

**Teaches:** `git init` · **Mapped to:** SO 1.1 (CAR ≥ 70%) · **Level slug:** `initializing-a-local-repository`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 5 today → 6 · **Estimated time:** about 9 min (today about 8)

### Learning outcomes

- Initialize the current folder or a new named folder as a repository.
- Start on the first branch the team uses (`main`, `trunk`).
- Initialize only the intended folder: existing files stay unstaged and sibling folders untouched.
- Re-run initialization safely inside an existing repository.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git init -b <branch> [<directory>]` | ⚡ ACTION | Easy 1 · Track this folder |
| `git init` | ⚡ ACTION | Hard 2 · Re-run init safely (built from parts the learner already knows) |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Track this folder | debut | `git init -b <branch> [<directory>]` | Turn the current folder into a repository on the first branch the team names. | 1.1.1 Initialize the current folder<br>1.1.2 Initialize with trunk as the first branch |
| Easy | 2. Start a new project folder | practice | — | Create a new project folder that starts life as a repository. | 1.1.3 Initialize invoice-tracker<br>1.1.4 Initialize oss-contrib *(from Medium)* |
| Medium | 1. Folder and branch from the brief | practice | — | Read the folder name and first branch from the brief, then initialize. | 1.1.5 Initialize docs-site<br>1.1.6 Initialize api-playground with trunk |
| Medium | 2. Existing files stay untracked | practice | — | Initialize a folder that already holds files, or sits beside other work, without staging anything. | 1.1.7 Initialize field-notes with existing files<br>1.1.8 Initialize ci-configs *(from Hard)* |
| Hard | 1. Only the right subfolder | transfer | — | Initialize one subfolder of a parent that holds other projects, and nothing else. | 1.1.9 Initialize research-log subfolder only<br>1.1.10 Initialize ui-kit with trunk |
| Hard | 2. Re-run init safely | transfer | `git init` | Run init again inside an existing repository and keep its history, branch and edits. | 1.1.11 Safely reinitialize the current repository<br>**new** `init-hard-safe-rerun-handbook` |

---

## Level 1.2 — Cloning Remote Repositories

**Teaches:** `git clone` · **Mapped to:** SO 1.2 (CAR ≥ 70%) · **Level slug:** `cloning-a-remote-repository`

**Waves (Easy/Medium/Hard):** 3/2/2 · **Runs:** 7 today → 7 · **Estimated time:** about 12 min (today about 12)

### Learning outcomes

- Clone over HTTPS and SSH, into the default or a named folder.
- Clone with a specific branch checked out.
- Clone shallow history, alone or combined with a branch and folder.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git clone <url>` | ⚡ ACTION | Easy 1 · Clone a repository |
| `git clone <url> <folder>` | ⚡ ACTION | Easy 2 · Clone into a named folder |
| `git clone -b <branch> <url> [<folder>]` | ⚡ ACTION | Easy 3 · Clone a specific branch |
| `git clone --depth <n> <url> [<folder>]` | ⚡ ACTION | Medium 2 · Shallow history |
| `git clone --depth <n> -b <branch> <url> [<folder>]` | ⚡ ACTION | Hard 1 · Shallow copy of one branch (built from parts the learner already knows) |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Clone a repository | debut | `git clone <url>` | Copy a remote repository into its default folder, over HTTPS or SSH. | 1.2.1 Clone docs-portal<br>1.2.4 Clone oss-toolkit via SSH |
| Easy | 2. Clone into a named folder | debut | `git clone <url> <folder>` | Clone into the folder name the team asks for. | 1.2.2 Clone api-lab into api-workshop<br>1.2.5 Clone audit-logs into audit-logs-local |
| Easy | 3. Clone a specific branch | debut | `git clone -b <branch> <url> [<folder>]` | Clone with a named branch checked out instead of the default. | 1.2.3 Clone profile-site at the starter branch<br>1.2.6 Clone backend-api at feature/auth *(from Medium)*<br>1.2.8 Clone cli-tool at starter into cli-starter-lab *(from Medium)* |
| Medium | 1. SSH address, named folder | practice | — | Clone over SSH into a named folder, without the guide. | 1.2.7 Clone analytics-lab via SSH into analytics-worktree<br>1.2.13 Clone research-log via SSH into research-log-lab *(from Hard)* |
| Medium | 2. Shallow history | debut | `git clone --depth <n> <url> [<folder>]` | Clone only recent history to save time and space. | 1.2.9 Shallow clone css-kit<br>**new** `clone-medium-shallow-metrics` |
| Hard | 1. Shallow copy of one branch | transfer | `git clone --depth <n> -b <branch> <url> [<folder>]` | Combine depth, branch and folder in one clone. | 1.2.11 Shallow clone mobile-ui at starter into mobile-ui-lab<br>1.2.12 Shallow clone lab-notebook at review into notebook-review |
| Hard | 2. Shallow review copy over SSH | transfer | — | Make a shallow SSH review copy in a named folder. | 1.2.10 Shallow SSH clone of oss-toolkit into oss-review<br>**new** `clone-hard-shallow-ssh-audit` |

---

## Level 1.3 — Staging and Committing

**Teaches:** `git add` + `git commit` · **Mapped to:** SO 1.3 (CAR ≥ 70%) · **Level slug:** `staging-and-committing-basic-workflow`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 14)

### Learning outcomes

- Stage one file, a folder, or several files, and commit with the required message.
- Leave unrelated or generated files out of a commit.
- Start a project's history from scratch: init, stage, commit.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git add <path>...` | ⚡ ACTION | Easy 1 · Stage and commit one change |
| `git commit -m <message>` | ⚡ ACTION | Easy 1 · Stage and commit one change |
| technique: several-paths | Technique | Easy 2 · Stage several files at once |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Stage and commit one change | debut | `git add <path>...`, `git commit -m <message>` | Stage one file or folder and commit it with the required message. | 1.3.3 Commit form validation update<br>1.3.4 Commit README clarification<br>1.3.5 Commit navbar spacing fix<br>1.3.2 Commit the auth module directory |
| Easy | 2. Stage several files at once | debut | technique: several-paths | Stage several files in one command and commit them together. | 1.3.1 Initial commit for library-system<br>1.3.6 Commit Docker configuration *(from Medium)* |
| Medium | 1. A two-file change | practice | — | Commit a two-file change without contextual hints. | 1.3.7 Commit profile card layout<br>1.3.8 Commit search results view<br>1.3.9 Commit export flow update |
| Medium | 2. First snapshot of a new project | spiral | — | Initialize a project, then stage and commit only its real files. | **new** `commit-medium-new-project-portfolio`<br>**new** `commit-medium-new-project-recipes` |
| Hard | 1. Leave the distractor out | transfer | — | Commit the fix and leave a tempting unrelated file out. | 1.3.10 Commit handler fix, leave experimental file out<br>1.3.12 Commit profile card change, leave notes out<br>1.3.13 Commit export fix, leave scratch output out |
| Hard | 2. Two targets, two distractors | transfer | — | Commit two related files while the distractors stay uncommitted. | 1.3.11 Commit parser and tests, leave debug/scratch files out<br>1.3.14 Commit search ranking display, leave notes out |

---

## Level 1.4 — Partial Staging

**Teaches:** `git add -p` · **Mapped to:** SO 1.4 (CAR ≥ 70%) · **Level slug:** `partial-staging-and-git-add-p`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 14)

### Learning outcomes

- Stage only the right hunks of a file with `git add -p`.
- Combine hunk staging with whole-file staging in one commit.
- Split one file's edits into separate commits.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git add -p <path>` | ⚡ ACTION | Easy 1 · Stage one hunk |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Stage one hunk | debut | `git add -p <path>` | Stage only the fix from a file that also holds unrelated edits, then commit it. | 1.4.1 Stage the billing fix hunk only<br>1.4.3 Stage the auth validation hunk only<br>1.4.5 Stage the export formatting hunk only |
| Easy | 2. Another file, another hunk | practice | — | Repeat hunk selection in a different file. | 1.4.2 Stage the routes handler hunk only<br>1.4.4 Stage the search ranking hunk only |
| Medium | 1. One hunk out of many | practice | — | Pick the one right hunk among several, with distractor files nearby. | 1.4.6 Stage only the parser bug fix hunk<br>1.4.7 Stage only the profile validation hunk<br>1.4.8 Stage only the payment rounding hunk<br>1.4.9 Stage only the dashboard filter hunk |
| Medium | 2. A hunk and a whole file | spiral | — | Commit one hunk together with a whole test or doc file. | **new** `partial-medium-hunk-plus-test`<br>**new** `partial-medium-hunk-plus-doc` |
| Hard | 1. Hunks across code and tests | transfer | — | Select the matching hunks across code and tests for one commit. | 1.4.10 Stage only the network Terraform hunk<br>1.4.11 Stage validation hunks across auth code and tests<br>1.4.12 Stage ranking hunks across search code and tests<br>1.4.13 Stage formatting hunks across export code and tests |
| Hard | 2. Split one file into two commits | compose | — | Turn one file's mixed edits into two separate commits. | **new** `partial-hard-split-two-commits-api`<br>**new** `partial-hard-split-two-commits-ui` |

---

## Level 1.5 — Amending Commits

**Teaches:** `git commit --amend` · **Mapped to:** SO 1.5 (CAR ≥ 70%) · **Level slug:** `amending-commits`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 11 min (today about 12)

### Learning outcomes

- Fix the last commit's message.
- Add forgotten files or hunks to the last commit.
- Amend the last commit, then keep new work as a separate commit.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git commit --amend -m <message>` | ⚡ ACTION | Easy 1 · Fix the last commit message |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Fix the last commit message | debut | `git commit --amend -m <message>` | Replace the last commit's message without changing its files. | 1.5.1 Fix a typo in the last commit message<br>1.5.3 Clarify a vague commit message<br>1.5.4 Clarify the README commit message<br>1.5.5 Clarify the navbar commit message<br>1.5.10 Correct a verbose passive-voice commit message *(from Hard)* |
| Easy | 2. Add the forgotten file | practice | — | Add a forgotten file to the last commit and keep its message. | 1.5.2 Add a forgotten file to the last commit<br>1.5.7 Add missing profile CSS to the last commit *(from Medium)* |
| Medium | 1. Amend content and message | practice | — | Fold a file into the last commit and correct its message. | 1.5.6 Add changelog and correct the commit message<br>1.5.8 Add missing export docs to the last commit<br>1.5.9 Add missing search template to the last commit |
| Medium | 2. Amend in one hunk | spiral | — | Fold only one hunk into the last commit. | **new** `amend-medium-hunk-into-last-checkout`<br>**new** `amend-medium-hunk-into-last-search` |
| Hard | 1. Missing file and wrong message | transfer | — | Fix both the content and the message of the last commit from a terse brief. | 1.5.11 Add missing CSS and correct the commit message<br>1.5.12 Add missing test and correct the commit message<br>1.5.13 Add missing docs and correct the commit message |
| Hard | 2. Fix the last message, then commit the rest | compose | — | Correct the last commit, then record new work as its own commit. | **new** `amend-hard-fix-message-then-commit-api`<br>**new** `amend-hard-fix-message-then-commit-docs` |

---

## Level 1.6 — Unstaging and Discarding Changes

**Teaches:** `git restore` · **Mapped to:** SO 1.6 (CAR ≥ 70%) · **Level slug:** `unstaging-and-discarding-changes`

**Waves (Easy/Medium/Hard):** 2/2/2 · **Runs:** 7 today → 6 · **Estimated time:** about 12 min (today about 12)

### Learning outcomes

- Unstage files without losing their edits.
- Discard working-tree changes to get the committed version back.
- Clean up the staging area before committing only the intended fix.

### Commands introduced

| Command | Type | First wave |
|---|---|---|
| `git restore --staged <path>...` | ⚡ ACTION | Easy 1 · Unstage but keep the edit |
| `git restore <path>...` | ⚡ ACTION | Easy 2 · Throw away a working change |

### Waves

| Tier | Wave | Role | Command guide | What the learner does | Variants |
|---|---|---|---|---|---|
| Easy | 1. Unstage but keep the edit | debut | `git restore --staged <path>...` | Take a file out of the staging area without losing the edit. | 1.6.1 Unstage notes.txt without discarding it<br>1.6.3 Unstage src/app.py without discarding it<br>1.6.4 Unstage docs/guide.md without discarding it<br>1.6.5 Unstage styles/site.css without discarding it |
| Easy | 2. Throw away a working change | debut | `git restore <path>...` | Discard unwanted edits and get the committed file back. | 1.6.2 Discard experimental config.py changes<br>**new** `restore-easy-discard-theme` |
| Medium | 1. Unstage one, discard another | compose | — | Unstage one file and discard another in the same cleanup. | 1.6.6 Unstage experimental.py, discard README.md changes<br>1.6.7 Preserve app.py, discard debug.log<br>1.6.8 Preserve guide.md, discard scratch.txt<br>1.6.9 Preserve source CSS, discard generated dist CSS |
| Medium | 2. Fix the staging, then commit | spiral | — | Unstage the wrong file, then commit the right one. | **new** `restore-medium-unstage-then-commit-login`<br>**new** `restore-medium-unstage-then-commit-cart` |
| Hard | 1. Several to unstage, one to discard | transfer | — | Unstage several files and discard one in a single pass. | 1.6.10 Unstage two files, discard experimental.py<br>1.6.11 Unstage two files, discard debug log<br>1.6.12 Unstage two files, discard generated output<br>1.6.13 Unstage two files, discard debug search log |
| Hard | 2. Clean up, then commit only the fix | spiral | — | Module 1 review: unstage, discard, stage one hunk, commit. | **new** `restore-hard-capstone-report`<br>**new** `restore-hard-capstone-invoice` |

---

## New scenarios in this module (18)

To be written in the team's scenario format (story, starting point, real-world context, task, checklist, answer key, accepted alternatives, expected result, evaluation, budgets). Names below are placeholders the author may change.

| ID | Wave | Starting point | Task | Answer key | Note |
|---|---|---|---|---|---|
| `init-hard-safe-rerun-handbook` | 1.1 Hard 2 · Re-run init safely | Inside team-handbook: already a repository on main with two commits; drafts/intro.md has uncommitted edits. | Run initialization again; keep the commits, the branch and the edits. | `git init` |  |
| `clone-medium-shallow-metrics` | 1.2 Medium 2 · Shallow history | Workspace outside any repository; no metrics-review folder. | Clone the metrics-dash URL into metrics-review with only the latest commit. | `git clone --depth 1 https://example.test/data/metrics-dash.git metrics-review` |  |
| `clone-hard-shallow-ssh-audit` | 1.2 Hard 2 · Shallow review copy over SSH | Workspace with other project folders; no rules-review folder. | Clone audit-rules over SSH into rules-review, keeping only the last two commits. | `git clone --depth 2 git@example.test:security/audit-rules.git rules-review` |  |
| `commit-medium-new-project-portfolio` | 1.3 Medium 2 · First snapshot of a new project | Folder portfolio is not a repository; index.html and styles.css are new; notes.txt is private. | Make it a repository on main and commit only the two site files as the first snapshot. | `git init -b main` → `git add index.html styles.css` → `git commit -m "Initial portfolio"` | Spiral: `git init` from 1.1. |
| `commit-medium-new-project-recipes` | 1.3 Medium 2 · First snapshot of a new project | Folder recipes is not a repository; recipes.md and shopping.md are new; draft.txt is private. | Make it a repository on main and commit only the two notes files. | `git init -b main` → `git add recipes.md shopping.md` → `git commit -m "Start recipe notes"` | Spiral: `git init` from 1.1. |
| `partial-medium-hunk-plus-test` | 1.4 Medium 2 · A hunk and a whole file | src/cart.py holds a rounding fix and a debug print; tests/test_cart.py is a new test. | Commit the rounding fix and the whole test file together; leave the debug print out. | `git add -p src/cart.py` → `git add tests/test_cart.py` → `git commit -m "Fix cart total rounding"` | Spiral: `git add <path>` from 1.3. |
| `partial-medium-hunk-plus-doc` | 1.4 Medium 2 · A hunk and a whole file | src/export.py holds a quoting fix and an experimental flag; docs/export.md is updated. | Commit the quoting fix and the doc change together; leave the flag out. | `git add -p src/export.py` → `git add docs/export.md` → `git commit -m "Fix CSV quoting"` | Spiral: `git add <path>` from 1.3. |
| `partial-hard-split-two-commits-api` | 1.4 Hard 2 · Split one file into two commits | src/api.py holds an expiry fix and an unrelated logging tidy-up. | Make two commits: the fix first, then the tidy-up, each with its stated message. | `git add -p src/api.py` → `git commit -m "Fix token expiry check"` → `git add src/api.py` → `git commit -m "Tidy API logging"` |  |
| `partial-hard-split-two-commits-ui` | 1.4 Hard 2 · Split one file into two commits | src/menu.js holds a focus-trap fix and helper renames. | Make two commits: the fix first, then the renames. | `git add -p src/menu.js` → `git commit -m "Fix menu focus trap"` → `git add src/menu.js` → `git commit -m "Rename menu helpers"` |  |
| `amend-medium-hunk-into-last-checkout` | 1.5 Medium 2 · Amend in one hunk | The last commit missed one hunk of src/checkout.py; the file also holds a debug hunk. | Add only the missing hunk to the last commit and keep its message. | `git add -p src/checkout.py` → `git commit --amend -m "Validate checkout totals"` | Spiral: `git add -p` from 1.4. |
| `amend-medium-hunk-into-last-search` | 1.5 Medium 2 · Amend in one hunk | The last commit missed one hunk of src/search.py; the file also holds a logging hunk. | Add only the missing hunk to the last commit and keep its message. | `git add -p src/search.py` → `git commit --amend -m "Rank exact matches first"` | Spiral: `git add -p` from 1.4. |
| `amend-hard-fix-message-then-commit-api` | 1.5 Hard 2 · Fix the last message, then commit the rest | The last local commit has a vague message; docs/limits.md has new, uncommitted docs. | Correct the last commit's message, then commit the docs as a separate commit. | `git commit --amend -m "Add rate limiter"` → `git add docs/limits.md` → `git commit -m "Document rate limits"` | Order matters: amending after the new commit would rewrite the wrong one. |
| `amend-hard-fix-message-then-commit-docs` | 1.5 Hard 2 · Fix the last message, then commit the rest | The last local commit has a vague message; docs/faq.md is new. | Correct the last commit's message, then commit the FAQ separately. | `git commit --amend -m "Document install steps"` → `git add docs/faq.md` → `git commit -m "Add install FAQ"` |  |
| `restore-easy-discard-theme` | 1.6 Easy 2 · Throw away a working change | styles/theme.css has unwanted local edits; nothing is staged. | Throw the edits away and restore the committed file. | `git restore styles/theme.css` |  |
| `restore-medium-unstage-then-commit-login` | 1.6 Medium 2 · Fix the staging, then commit | src/login.py and notes/todo.md are both staged. | Commit only the login fix; keep the note's edits, unstaged. | `git restore --staged notes/todo.md` → `git commit -m "Fix login redirect"` | Spiral: `git commit -m` from 1.3. |
| `restore-medium-unstage-then-commit-cart` | 1.6 Medium 2 · Fix the staging, then commit | src/cart_badge.js and scratch/ideas.txt are both staged. | Commit only the badge fix; keep the ideas file's edits, unstaged. | `git restore --staged scratch/ideas.txt` → `git commit -m "Fix cart badge count"` | Spiral: `git commit -m` from 1.3. |
| `restore-hard-capstone-report` | 1.6 Hard 2 · Clean up, then commit only the fix | debug.log is staged; tmp/output.txt has stray edits; src/report.py holds a totals fix and an experiment. | Unstage the log (keep it), discard the output edits, and commit only the totals fix. | `git restore --staged debug.log` → `git restore tmp/output.txt` → `git add -p src/report.py` → `git commit -m "Fix report totals"` | Module 1 capstone: restore + add -p + commit. |
| `restore-hard-capstone-invoice` | 1.6 Hard 2 · Clean up, then commit only the fix | notes/invoice-ideas.md is staged; build/invoice.html has stray edits; src/invoice.py holds a due-date fix and a refactor. | Unstage the notes, discard the build edits, and commit only the due-date fix. | `git restore --staged notes/invoice-ideas.md` → `git restore build/invoice.html` → `git add -p src/invoice.py` → `git commit -m "Fix invoice due date"` | Module 1 capstone. |

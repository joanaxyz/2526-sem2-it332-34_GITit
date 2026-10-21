# GIT it! wave scenarios

Scenarios written for the ordered-wave curriculum; see CONTENT_AUTHORING_GUIDE.md.
They use the same sections as the team's revised scenario bank and compile with
`python scripts/curriculum/import_revised_scenarios.py --extension backend/curriculum/seed_data/source/wave_scenarios.md`
into `backend/curriculum/seed_data/scenario_bank_waves.json`. Runtime fixtures (starting repository,
state requirements) live in `source/scenario_fixtures/`, keyed by the same Variant ID.

Numbering continues each level's scenario list. Gate scenarios use `N.G.k`.

## Module 1 — Local Repository Foundations

### 1.1.12 Set up the billing service inside the services folder · Hard

**Variant ID:** `init-hard-nested-service`

**Story**
The workspace Raven shared holds several projects: `services/billing-api`, `services/search-api` and the docs folder. Only the billing service is ready for version control. The other two belong to other groups, who set up their own repositories. Raven's team names the first branch `trunk` on every new repository, and the brief takes that for granted.

**Starting point:** You are at the top of the workspace. `services/billing-api`, `services/search-api` and docs all hold files, and none of them is a repository.

**Real-World Context**
`git init` takes the folder to turn into a repository, nested paths included. Initializing the wrong level puts other projects' files inside your repository.

**Your Task**
Make `services/billing-api`, and __only__ that folder, a Git repository whose first branch follows the team's convention. **Do not stage or commit anything.**

**Objective Checklist**

- [ ] services/billing-api is a repository; the workspace and its other folders are not.
- [ ] The current branch is trunk.
- [ ] Nothing is staged or committed.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b trunk services/billing-api` — Initialize the nested folder with the team's first branch.

**Accepted Alternatives (STAFF ONLY)**

- `cd services/billing-api` then `git init -b trunk`; `--initial-branch=trunk`.
- Common patterns that apply: P19.

**Not accepted**

- Initializing the workspace or the services folder, or a first branch other than trunk.

**Expected Result**
`services/billing-api` is a repository on `trunk` with no commits, and nothing else in the workspace changed.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 8

- Repository at `services/billing-api`; HEAD on unborn `trunk`; no commits; nothing staged.
- Every workspace file still present and untracked.

### 1.1.13 Set up the Git basics course inside the courses folder · Hard

**Variant ID:** `init-hard-nested-course`

**Story**
Sage keeps the study group's material in one workspace: `courses/git-basics`, `courses/sql-basics` and a templates folder. The Git basics course is the one moving under version control today. The SQL course is still a draft, and the templates are shared by everyone. The group starts every repository on `main`.

**Starting point:** You are at the top of the workspace. `courses/git-basics`, `courses/sql-basics` and templates all hold files, and none of them is a repository.

**Real-World Context**
A repository covers its folder and everything inside it, so choosing the folder is the decision that matters.

**Your Task**
Make `courses/git-basics`, and __only__ that folder, a Git repository with `main` as its first branch. **Do not stage or commit anything.**

**Objective Checklist**

- [ ] courses/git-basics is a repository; the workspace and its other folders are not.
- [ ] The current branch is main.
- [ ] Nothing is staged or committed.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main courses/git-basics` — Initialize the nested course folder.

**Accepted Alternatives (STAFF ONLY)**

- `cd courses/git-basics` then `git init -b main`; `--initial-branch=main`; `git init courses/git-basics` (main is the default first branch).
- Common patterns that apply: P19.

**Not accepted**

- Initializing the workspace or the courses folder.

**Expected Result**
`courses/git-basics` is a repository on `main` with no commits, and nothing else in the workspace changed.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 8

- Repository at `courses/git-basics`; HEAD on unborn `main`; no commits; nothing staged.
- Every workspace file still present and untracked.

### 1.1.14 Start tracking the planning notes · Easy

**Variant ID:** `init-easy-plain-notes`

**Story**
Raven has been keeping the group's planning notes in one folder, and the notes already changed twice this week without anyone noticing. Before the next meeting, Raven wants Git watching the folder so later changes can be recorded. The notes themselves stay as they are for now.

**Starting point:** You are in the planning folder. It holds `notes.md` and is not a repository yet.

**Real-World Context**
`git init` turns the folder you are in into a repository. It creates Git's records and touches none of your files.

**Your Task**
Turn the current folder into a Git repository. **Do not stage or commit `notes.md`.**

**Objective Checklist**

- [ ] The current folder is a Git repository.
- [ ] notes.md is still there and untracked.
- [ ] Nothing is staged and no commit exists.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init` — Turn the current folder into a repository.

**Accepted Alternatives (STAFF ONLY)**

- `git init .`; `git init -b main`.

**Not accepted**

- Staging or committing notes.md.

**Expected Result**
The planning folder is a repository with no commits, and `notes.md` is untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- Repository at the workspace root; HEAD on unborn `main`; no commits; nothing staged.
- notes.md present and untracked.

### 1.1.15 Start tracking the family recipes · Easy

**Variant ID:** `init-easy-plain-recipes`

**Story**
Sage is collecting the family's recipes in one folder before a reunion, and two cousins keep sending corrected versions. Sage wants Git to keep the history from now on. The recipe file stays exactly as it is for the moment.

**Starting point:** You are in the recipes folder. It holds `recipes.md` and is not a repository yet.

**Real-World Context**
Starting a repository is the first step of version control: Git can only record changes in a folder it tracks.

**Your Task**
Turn the current folder into a Git repository. **Do not stage or commit `recipes.md`.**

**Objective Checklist**

- [ ] The current folder is a Git repository.
- [ ] recipes.md is still there and untracked.
- [ ] Nothing is staged and no commit exists.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init` — Turn the current folder into a repository.

**Accepted Alternatives (STAFF ONLY)**

- `git init .`; `git init -b main`.

**Not accepted**

- Staging or committing recipes.md.

**Expected Result**
The recipes folder is a repository with no commits, and `recipes.md` is untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- Repository at the workspace root; HEAD on unborn `main`; no commits; nothing staged.
- recipes.md present and untracked.

### 1.1.16 A new repository for the site assets · Easy

**Variant ID:** `init-easy-new-folder-among-files`

**Story**
The design team's workspace already holds a loose `design/logo.svg` that belongs to another project. Raven wants a separate repository for the website's assets, in a new `site-assets` folder, starting on `main`. The logo should stay where it is, outside the new repository.

**Starting point:** You are at the top of the workspace. It holds `design/logo.svg` and no repository.

**Real-World Context**
`git init <folder>` creates the folder if needed and makes only that folder a repository, so nearby files stay out of it.

**Your Task**
Create a repository in a new `site-assets` folder with `main` as its first branch. **Leave `design/logo.svg` where it is.**

**Objective Checklist**

- [ ] site-assets is a Git repository on main.
- [ ] The workspace itself is not a repository.
- [ ] design/logo.svg is still in place, and nothing is staged or committed.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main site-assets` — Create the folder and initialize it on main.

**Accepted Alternatives (STAFF ONLY)**

- `--initial-branch=main`; `mkdir site-assets`, `cd site-assets`, then `git init -b main`.

**Not accepted**

- Initializing the workspace, or moving the logo into the new repository.

**Expected Result**
`site-assets` is a repository on `main` with no commits, and the logo is untouched.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- Repository at `site-assets`; HEAD on unborn `main`; no commits; nothing staged.
- design/logo.svg still present.

### 1.1.17 Put the sketches folder under version control · Medium

**Variant ID:** `init-medium-existing-sketches`

**Story**
Sage has a `sketches` folder with an ideas list and a colour palette that the whole art club edits. Last week someone overwrote the palette and nobody could get it back. The folder should become a repository on `main` before the next session, without changing either file.

**Starting point:** You are at the top of the workspace. The folder `sketches` holds `ideas.md` and `palette.txt`. It is not a repository yet.

**Real-World Context**
Initializing an existing folder leaves its files untracked. Nothing is recorded until someone stages and commits them on purpose.

**Your Task**
Make the existing `sketches` folder a Git repository with `main` as its first branch. **Do not stage or commit its files.**

**Objective Checklist**

- [ ] sketches is a Git repository on main.
- [ ] ideas.md and palette.txt are unchanged and untracked.
- [ ] Nothing is staged and no commit exists.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main sketches` — Initialize the existing folder on main.

**Accepted Alternatives (STAFF ONLY)**

- `cd sketches` then `git init -b main`; `--initial-branch=main`.

**Not accepted**

- Initializing the workspace, a branch other than main, or staging the files.

**Expected Result**
`sketches` is a repository on `main` with no commits, and both files are untracked and unchanged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 10

- Repository at `sketches`; HEAD on unborn `main`; no commits; nothing staged.
- Both files present with their original content.

### 1.2.15 Two commits of the audit rules over SSH · Hard

**Variant ID:** `clone-hard-shallow-ssh-audit`

**Story**
The security group wants a second opinion on its newest audit rule, and Sage wants you to compare it with the rule that came just before it. Your SSH key is already registered with the server. Your laptop holds other projects, so the review copy goes into its own folder, `rules-review`. Anything older than those two commits is noise for this review.

**Starting point:** You are in your workspace, which holds other project folders. No folder named `rules-review` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**
A shallow clone can keep a little more than the tip. A depth of two is enough to compare the newest change with the one before it, without downloading years of history.

**Your Task**
Clone `git@example.test:security/audit-rules.git` over SSH into a folder named `rules-review`, keeping only the last two commits.

**Objective Checklist**

- [ ] A copy of audit-rules exists in rules-review.
- [ ] The default branch (main) is checked out.
- [ ] Exactly the last two commits were downloaded (history depth of 2).
- [ ] origin points to the SSH address given in the task.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git clone --depth 2 git@example.test:security/audit-rules.git rules-review` — SSH clone with two commits of history.

**Accepted Alternatives (STAFF ONLY)**

- `--depth=2`; the option may come after the URL; the destination may be written `./rules-review` or `rules-review/`.
- Common patterns that apply: P3, P38.

**Not accepted**

- The HTTPS address, a depth of 1 or a full clone, or the default folder name.

**Expected Result**
`rules-review` is an SSH copy of `audit-rules` on `main`, holding the newest rule and the one before it.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 8

- Repository at `rules-review`; remote `origin` = the SSH address; HEAD on `main` at the remote tip.
- Clone depth 2 and exactly two commits present; clean working tree.

### 1.2.16 Clone the design style guide · Easy

**Variant ID:** `clone-easy-style-guide`

**Story**
The design team keeps its style guide in a shared repository. Raven needs a local copy to check the colour tokens before the next review.

**Starting point:** You are in an empty workspace. There is no local repository yet.

**Real-World Context**
`git clone <url>` copies a remote repository, with its history, into a new folder named after the repository.

**Your Task**
Clone the remote repository from `https://example.test/design/style-guide.git`.

**Objective Checklist**

- [ ] A local repository exists with origin pointing at the style guide.
- [ ] main matches origin/main.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git clone https://example.test/design/style-guide.git` — Copy the remote repository.

**Accepted Alternatives (STAFF ONLY)**

- Cloning into `style-guide` explicitly.

**Not accepted**

- Initializing an empty repository instead of cloning.

**Expected Result**
A `style-guide` folder holds the repository, on `main`, matching `origin/main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- origin exists; main and origin/main point at the remote's tip; working tree clean.

### 1.2.17 Clone the handbook draft into its own folder · Easy

**Variant ID:** `clone-easy-branch-folder-handbook`

**Story**
Sage is reviewing the team handbook, but the new chapters only exist on the `draft` branch. Sage wants them in a folder called `handbook-draft`, so the copy is never mixed up with the published handbook.

**Starting point:** You are in an empty workspace. There is no local repository yet.

**Real-World Context**
`git clone -b <branch> <url> <folder>` checks out a chosen branch and names the folder in one step.

**Your Task**
Clone `https://example.test/docs/handbook.git` into a local folder named `handbook-draft` with `draft` checked out.

**Objective Checklist**

- [ ] The repository is in handbook-draft.
- [ ] The current branch is draft, matching origin/draft.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git clone -b draft https://example.test/docs/handbook.git handbook-draft` — Clone the draft branch into the named folder.

**Accepted Alternatives (STAFF ONLY)**

- `--branch draft`; options in any order before the URL.

**Not accepted**

- Cloning main, or cloning into another folder name.

**Expected Result**
`handbook-draft` holds the repository on `draft`, matching `origin/draft`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- Repository at `handbook-draft`; HEAD on draft at the remote's draft tip; working tree clean.

### 1.2.18 A light copy of the icon set · Medium

**Variant ID:** `clone-medium-shallow-icons`

**Story**
The icon set's history is long, and Raven only needs the current icons to build a mock-up. A full copy would take ages on the café Wi-Fi. Only the latest commit is needed.

**Starting point:** You are in an empty workspace. There is no local repository yet.

**Real-World Context**
A shallow clone (`--depth <n>`) copies only the most recent commits, which is quicker when you don't need the history.

**Your Task**
Clone the remote repository from `https://example.test/design/icon-set.git` using a history depth of 1.

**Objective Checklist**

- [ ] The repository is cloned with origin pointing at the icon set.
- [ ] main matches origin/main.
- [ ] Only one commit of history was copied.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git clone --depth 1 https://example.test/design/icon-set.git` — Copy only the latest commit.

**Accepted Alternatives (STAFF ONLY)**

- `--depth=1`; naming the folder `icon-set` explicitly.

**Not accepted**

- A full clone, or a depth other than 1.

**Expected Result**
An `icon-set` folder holds a one-commit copy of the repository on `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 10

- Repository at `icon-set`; main at the remote's tip; exactly one commit.

### 1.3.15 First snapshot of the portfolio · Medium

**Variant ID:** `commit-medium-new-project-portfolio`

**Story**
Your portfolio site has lived in a plain folder for weeks: `index.html`, `styles.css` and a `notes.txt` full of private reminders about which projects to leave out. Raven wants every group member's portfolio under version control before the career fair. The two site files belong in the history. *Your notes do not.*

**Starting point:** You are in portfolio. It is not a repository yet. `index.html`, `styles.css` and `notes.txt` are all new files.

**Real-World Context**
Starting version control on an existing folder takes two steps: create the repository, then choose which files go into the first snapshot. Private notes can stay in the folder without ever being committed.

**Your Task**
Make `portfolio` a Git repository on `main`, then commit `index.html` and `styles.css` with the message `Initial portfolio`. **Leave `notes.txt` untracked.**

**Objective Checklist**

- [ ] portfolio is a Git repository on main.
- [ ] A commit named “Initial portfolio” contains index.html and styles.css.
- [ ] notes.txt is not committed and is still in the folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main` — Make the folder a repository on main.
2. `git add index.html styles.css` — Stage only the two site files.
3. `git commit -m "Initial portfolio"` — Record the first snapshot.

**Accepted Alternatives (STAFF ONLY)**

- `git init` when the simulator's first branch is main; `--initial-branch=main`.
- The two files staged in one command or two; `git commit --message "Initial portfolio"`, single quotes, `-m"Initial portfolio"`. The message must match exactly.
- Common patterns that apply: P1, P19, P20.

**Not accepted**

- `git add .` or `git add -A`: they would commit notes.txt.

**Expected Result**
portfolio is a repository on `main` with one commit, “Initial portfolio”, holding the two site files. `notes.txt` stays untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- Repository initialized; HEAD on `main`; exactly one commit.
- Latest commit `Initial portfolio` contains `index.html` and `styles.css` and not `notes.txt`; `notes.txt` still untracked.

### 1.3.16 Start tracking the recipe notes · Medium

**Variant ID:** `commit-medium-new-project-recipes`

**Story**
Sage keeps the group's shared shopping list and recipes in a folder on the lab computer, and two people overwrote each other's edits last week. You offer to put the folder under version control. `recipes.md` and `shopping.md` are worth tracking. `draft.txt` is your half-written idea for a new dish, and it stays out until it is ready.

**Starting point:** You are in recipes. It is not a repository yet. `recipes.md`, `shopping.md` and `draft.txt` are all new files.

**Real-World Context**
A first commit decides what the project's history starts with. Staging by name keeps unfinished drafts out of it.

**Your Task**
Make `recipes` a Git repository on `main`, then commit `recipes.md` and `shopping.md` with the message `Start recipe notes`. **Leave `draft.txt` untracked.**

**Objective Checklist**

- [ ] recipes is a Git repository on main.
- [ ] A commit named “Start recipe notes” contains recipes.md and shopping.md.
- [ ] draft.txt is not committed and is still in the folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main` — Make the folder a repository on main.
2. `git add recipes.md shopping.md` — Stage only the two notes files.
3. `git commit -m "Start recipe notes"` — Record the first snapshot.

**Accepted Alternatives (STAFF ONLY)**

- `git init` when the simulator's first branch is main; `--initial-branch=main`.
- The two files staged in one command or two; `git commit --message "Start recipe notes"`, single quotes, `-m"Start recipe notes"`. The message must match exactly.
- Common patterns that apply: P1, P19, P20.

**Not accepted**

- `git add .` or `git add -A`: they would commit draft.txt.

**Expected Result**
recipes is a repository on `main` with one commit, “Start recipe notes”, holding the two notes files. `draft.txt` stays untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- Repository initialized; HEAD on `main`; exactly one commit.
- Latest commit `Start recipe notes` contains `recipes.md` and `shopping.md` and not `draft.txt`; `draft.txt` still untracked.

### 1.3.17 Prepare the 1.2 release · Medium

**Variant ID:** `commit-medium-three-file-release`

**Story**
Finn is cutting release 1.2. The changelog is new, and `setup.py` and `src/version.py` both carry the new version number. They belong in one commit, so the release is a single step in the history.

**Starting point:** You are on `main`. `CHANGELOG.md` is new, and `setup.py` and `src/version.py` are modified. Nothing is staged.

**Real-World Context**
Related changes go into one commit, so anyone reading the history sees the release as a single, complete step.

**Your Task**
Stage `CHANGELOG.md`, `setup.py` and `src/version.py`, then create a commit with the message `Prepare 1.2 release`. Finish on `main`.

**Objective Checklist**

- [ ] The latest commit on main is "Prepare 1.2 release".
- [ ] It contains all three files.
- [ ] Nothing is left staged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add CHANGELOG.md setup.py src/version.py` — Stage the three release files.
2. `git commit -m "Prepare 1.2 release"` — Record them together.

**Accepted Alternatives (STAFF ONLY)**

- Staging the files with separate `git add` commands, or `git add .`.

**Not accepted**

- Splitting the release across several commits.

**Expected Result**
`main` has one new commit, "Prepare 1.2 release", with all three files.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- Two commits on main; the tip holds the 1.2 content of all three files; nothing staged.

### 1.4.14 The rounding fix and its test · Medium

**Variant ID:** `partial-medium-hunk-plus-test`

**Story**
You fixed the rounding bug in the cart total and wrote `tests/test_cart.py` to prove it. While hunting the bug you also added a debug print to `src/cart.py`, and it is still there. Maeve will review the commit tonight. She wants the fix and its test together, and no stray print in the history.

**Starting point:** You are on `main`. `src/cart.py` holds the rounding fix and a debug print. `tests/test_cart.py` is a new file.

**Real-World Context**
A fix is easiest to trust when its test arrives in the same commit. Partial staging takes the fix from a file that also holds throwaway debugging, while the new test file is staged whole.

**Your Task**
Commit the rounding fix from `src/cart.py` together with the whole of `tests/test_cart.py`, using the message `Fix cart total rounding`. **Leave the debug print uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix cart total rounding” exists on main.
- [ ] It contains the rounding fix and tests/test_cart.py.
- [ ] The debug print is not committed and is still in src/cart.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/cart.py` — Stage only the rounding fix hunk.
2. `git add tests/test_cart.py` — Stage the new test file.
3. `git commit -m "Fix cart total rounding"` — Commit both.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/cart.py`; the test file staged before or after the patch.
- `git commit --message "Fix cart total rounding"`, single quotes, `-m"Fix cart total rounding"`. The message must match exactly.
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add src/cart.py` (whole file): it would stage the debug print.

**Expected Result**
“Fix cart total rounding” holds the rounding fix and its test. The debug print is still in `src/cart.py`, uncommitted.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- Latest commit on `main` = `Fix cart total rounding`; changes include the fix hunk and `tests/test_cart.py`, not the debug hunk.
- The debug hunk is still an unstaged change; nothing staged.

### 1.4.15 The quoting fix and its documentation · Medium

**Variant ID:** `partial-medium-hunk-plus-doc`

**Story**
Exported CSV files have been breaking whenever a name contains a comma. Your fix in `src/export.py` wraps such values in quotes, and you updated `docs/export.md` to explain the new behavior. The same file also holds an experimental flag you are still trying out. Sage asks for one commit with the fix and the docs, and nothing half-finished.

**Starting point:** You are on `main`. `src/export.py` holds the quoting fix and an experimental flag. `docs/export.md` has finished edits.

**Real-World Context**
Documentation that ships with the change it describes stays accurate. Partial staging keeps the experiment out while the doc file goes in whole.

**Your Task**
Commit the quoting fix from `src/export.py` together with the whole of `docs/export.md`, using the message `Fix CSV quoting`. **Leave the experimental flag uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix CSV quoting” exists on main.
- [ ] It contains the quoting fix and the docs/export.md changes.
- [ ] The experimental flag is not committed and is still in src/export.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/export.py` — Stage only the quoting fix hunk.
2. `git add docs/export.md` — Stage the documentation.
3. `git commit -m "Fix CSV quoting"` — Commit both.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/export.py`; the doc staged before or after the patch.
- `git commit --message "Fix CSV quoting"`, single quotes, `-m"Fix CSV quoting"`. The message must match exactly.
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add src/export.py` (whole file): it would stage the experimental flag.

**Expected Result**
“Fix CSV quoting” holds the quoting fix and its documentation. The experimental flag stays in `src/export.py`, uncommitted.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- Latest commit on `main` = `Fix CSV quoting`; changes include the fix hunk and `docs/export.md`, not the flag hunk.
- The flag hunk is still an unstaged change; nothing staged.

### 1.4.16 Split the API changes into two commits · Hard

**Variant ID:** `partial-hard-split-two-commits-api`

**Story**
`src/api.py` holds two finished changes: a fix for the token expiry check and an unrelated tidy-up of the logging calls. Raven wants them as two separate commits, fix first, so the fix can be picked onto the release branch on its own later. Both changes are in the same file.

**Starting point:** You are on `main`. `src/api.py` holds an expiry fix and a logging tidy-up. Nothing is staged.

**Real-World Context**
Separate commits for separate ideas let a team review, revert or copy each one alone. Partial staging lets one file's changes become two commits.

**Your Task**
Make two commits on `main`. First commit __only__ the expiry fix with the message `Fix token expiry check`, then commit the logging tidy-up with the message `Tidy API logging`.

**Objective Checklist**

- [ ] “Fix token expiry check” is a commit with only the expiry fix.
- [ ] “Tidy API logging” comes right after it, with the tidy-up.
- [ ] Nothing is left uncommitted, and you finish on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/api.py` — Stage only the expiry fix hunk.
2. `git commit -m "Fix token expiry check"` — Commit the fix first.
3. `git add src/api.py` — Stage the remaining tidy-up.
4. `git commit -m "Tidy API logging"` — Commit it second.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/api.py`; `git add -p src/api.py` again for the second hunk; `git commit -am "Tidy API logging"` for the second commit.
- `--message` forms and single quotes. The messages must match exactly.
- Common patterns that apply: P4, P5, P6, P1.

**Not accepted**

- One commit with both changes, or the tidy-up committed first.

**Expected Result**
`main` has two new commits in order: “Fix token expiry check” with the fix, then “Tidy API logging” with the tidy-up.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `main` has 3 commits; `main~1` = `Fix token expiry check` with the fix hunk and without the tidy hunk.
- `main` = `Tidy API logging` with the tidy hunk; clean tree, nothing staged.

### 1.4.17 Split the menu changes into two commits · Hard

**Variant ID:** `partial-hard-split-two-commits-ui`

**Story**
While fixing a focus trap in the dropdown menu, you also renamed three of its helper functions so they read better. Both changes sit in `src/menu.js`. Maeve asks for the fix on its own commit first: if the renames cause trouble, she wants to be able to undo them without losing the fix.

**Starting point:** You are on `main`. `src/menu.js` holds a focus-trap fix and helper renames. Nothing is staged.

**Real-World Context**
Keeping a behavior fix apart from a cosmetic rename makes each easy to undo alone. Partial staging turns one file into two focused commits.

**Your Task**
Make two commits on `main`. First commit __only__ the focus-trap fix with the message `Fix menu focus trap`, then commit the renames with the message `Rename menu helpers`.

**Objective Checklist**

- [ ] “Fix menu focus trap” is a commit with only the focus-trap fix.
- [ ] “Rename menu helpers” comes right after it, with the renames.
- [ ] Nothing is left uncommitted, and you finish on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/menu.js` — Stage only the focus-trap fix hunk.
2. `git commit -m "Fix menu focus trap"` — Commit the fix first.
3. `git add src/menu.js` — Stage the renames.
4. `git commit -m "Rename menu helpers"` — Commit them second.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/menu.js`; `git add -p src/menu.js` again for the second hunk; `git commit -am "Rename menu helpers"` for the second commit.
- `--message` forms and single quotes. The messages must match exactly.
- Common patterns that apply: P4, P5, P6, P1.

**Not accepted**

- One commit with both changes, or the renames committed first.

**Expected Result**
`main` has two new commits in order: “Fix menu focus trap” with the fix, then “Rename menu helpers” with the renames.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `main` has 3 commits; `main~1` = `Fix menu focus trap` with the fix hunk and without the rename hunk.
- `main` = `Rename menu helpers` with the rename hunk; clean tree, nothing staged.

### 1.5.14 Fold the missing guard into the last commit · Medium

**Variant ID:** `amend-medium-hunk-into-last-checkout`

**Story**
Your last commit, “Validate checkout totals”, was supposed to include a guard against negative totals, but that hunk is still sitting in `src/checkout.py`. Next to it is a debug hunk you added while testing. You have not pushed. Sage would rather see one complete commit than a "forgot one line" commit right after it.

**Starting point:** You are on `main`. The latest commit is “Validate checkout totals”. `src/checkout.py` holds the missing guard hunk and a debug hunk.

**Real-World Context**
Amending an unpublished commit can add the piece it was missing. Partial staging makes sure only that piece goes in, not the debugging around it.

**Your Task**
Add __only__ the missing guard hunk from `src/checkout.py` to the latest commit, keeping its message `Validate checkout totals`. **Leave the debug hunk uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] The latest commit is still named “Validate checkout totals” and now includes the guard.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] The debug hunk is not committed and is still in src/checkout.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/checkout.py` — Stage only the guard hunk.
2. `git commit --amend -m "Validate checkout totals"` — Fold it into the latest commit.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/checkout.py`; `git commit --amend --no-edit`; `--message` forms; option order swapped. The message must match exactly.
- Common patterns that apply: P7, P29, P4.

**Not accepted**

- A new commit for the guard, or `git add src/checkout.py` (whole file), which would include the debug hunk.

**Expected Result**
“Validate checkout totals” now includes the guard and replaced the old commit. The debug hunk stays in `src/checkout.py`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD replaces `c2` by amend; message `Validate checkout totals`; `main` still has 2 commits.
- HEAD changes include the guard hunk and not the debug hunk; the debug hunk is still unstaged.

### 1.5.15 Fold the exact-match ranking into the last commit · Medium

**Variant ID:** `amend-medium-hunk-into-last-search`

**Story**
Your commit “Rank exact matches first” went in without the hunk that actually moves exact matches to the top. That hunk is still in `src/search.py`, next to some extra logging you only needed for testing. Nothing has been pushed yet, and Maeve is about to pull your branch for a demo.

**Starting point:** You are on `main`. The latest commit is “Rank exact matches first”. `src/search.py` holds the missing ranking hunk and a logging hunk.

**Real-World Context**
An unpublished commit that misses part of its own change can be completed by amending it. Staging just that hunk keeps the testing noise out.

**Your Task**
Add __only__ the missing ranking hunk from `src/search.py` to the latest commit, keeping its message `Rank exact matches first`. **Leave the logging hunk uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] The latest commit is still named “Rank exact matches first” and now includes the ranking change.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] The logging hunk is not committed and is still in src/search.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add -p src/search.py` — Stage only the ranking hunk.
2. `git commit --amend -m "Rank exact matches first"` — Fold it into the latest commit.

**Accepted Alternatives (STAFF ONLY)**

- `git add --patch src/search.py`; `git commit --amend --no-edit`; `--message` forms; option order swapped. The message must match exactly.
- Common patterns that apply: P7, P29, P4.

**Not accepted**

- A new commit for the ranking change, or `git add src/search.py` (whole file), which would include the logging.

**Expected Result**
“Rank exact matches first” now includes the ranking change and replaced the old commit. The logging hunk stays in `src/search.py`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD replaces `c2` by amend; message `Rank exact matches first`; `main` still has 2 commits.
- HEAD changes include the ranking hunk and not the logging hunk; the logging hunk is still unstaged.

### 1.5.16 Reword, then document the rate limiter · Hard

**Variant ID:** `amend-hard-fix-message-then-commit-api`

**Story**
You committed the new rate limiter late last night with the message “stuff”. This morning you also wrote `docs/limits.md` to explain it.

Raven reads history before every release, and wants two clear commits: the limiter under a real name, then the docs in their own commit. Nothing has been pushed.

**Starting point:** You are on `main`. The latest commit, “stuff”, adds `src/limiter.py`. `docs/limits.md` is a new, uncommitted file.

**Real-World Context**
Amend rewrites the most recent commit, so order matters. Rename the commit before adding another one, or the amend would rewrite the wrong commit.

**Your Task**
Rename the latest commit to `Add rate limiter`, then commit `docs/limits.md` separately with the message `Document rate limits`. Finish on `main`.

**Objective Checklist**

- [ ] The limiter commit is now named “Add rate limiter” and does not contain the docs.
- [ ] “Document rate limits” comes right after it, with docs/limits.md.
- [ ] Nothing is left uncommitted, and you finish on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Add rate limiter"` — Rename the latest commit first.
2. `git add docs/limits.md` — Stage the docs.
3. `git commit -m "Document rate limits"` — Commit them separately.

**Accepted Alternatives (STAFF ONLY)**

- `--message` forms, single quotes, option order swapped. The messages must match exactly.
- Common patterns that apply: P7, P1.

**Not accepted**

- Committing the docs first and amending afterwards (that renames the docs commit), or amending the docs into the limiter commit.

**Expected Result**
`main` reads “Add rate limiter” followed by “Document rate limits”, each with its own files.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- `main` has 3 commits; the last amend replaced `c2`; `main~1` = `Add rate limiter` with `src/limiter.py` and without `docs/limits.md`.
- `main` = `Document rate limits` adding `docs/limits.md`; clean tree.

### 1.5.17 Reword, then add the install FAQ · Hard

**Variant ID:** `amend-hard-fix-message-then-commit-docs`

**Story**
Your commit with the new install guide is called “wip”, which tells nobody anything. Since then you have also written `docs/faq.md` with the questions people keep asking Sage. Sage wants the guide under a proper name and the FAQ as its own commit, so either can be reviewed alone. You have not pushed.

**Starting point:** You are on `main`. The latest commit, “wip”, adds `docs/install.md`. `docs/faq.md` is a new, uncommitted file.

**Real-World Context**
Amend only ever rewrites the latest commit. Fix its message while it is still the latest, then build the next commit on top.

**Your Task**
Rename the latest commit to `Document install steps`, then commit `docs/faq.md` separately with the message `Add install FAQ`. Finish on `main`.

**Objective Checklist**

- [ ] The guide commit is now named “Document install steps” and does not contain the FAQ.
- [ ] “Add install FAQ” comes right after it, with docs/faq.md.
- [ ] Nothing is left uncommitted, and you finish on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Document install steps"` — Rename the latest commit first.
2. `git add docs/faq.md` — Stage the FAQ.
3. `git commit -m "Add install FAQ"` — Commit it separately.

**Accepted Alternatives (STAFF ONLY)**

- `--message` forms, single quotes, option order swapped. The messages must match exactly.
- Common patterns that apply: P7, P1.

**Not accepted**

- Committing the FAQ first and amending afterwards, or amending the FAQ into the guide commit.

**Expected Result**
`main` reads “Document install steps” followed by “Add install FAQ”, each with its own file.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- `main` has 3 commits; the last amend replaced `c2`; `main~1` = `Document install steps` with `docs/install.md` and without `docs/faq.md`.
- `main` = `Add install FAQ` adding `docs/faq.md`; clean tree.

### 1.6.14 Throw away the neon theme · Easy

**Variant ID:** `restore-easy-discard-theme`

**Story**
You spent the afternoon trying a neon color scheme in `styles/theme.css`. Raven took one look at the preview and *laughed*. You agree it was a mistake, and none of the edits are worth keeping. You want the file back exactly as it was in the last commit.

**Starting point:** You are on `main`. `styles/theme.css` has uncommitted edits. Nothing is staged.

**Real-World Context**
Unwanted edits to a tracked file can be thrown away by restoring the committed version. Discarded edits cannot be recovered, so only do this to work you truly don't need.

**Your Task**
Discard your edits to `styles/theme.css` and restore its committed version. Finish on `main`.

**Objective Checklist**

- [ ] styles/theme.css is back to its committed version (its edits are gone).
- [ ] No commit was created, and you finish on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore styles/theme.css` — Restore the committed version.

**Accepted Alternatives (STAFF ONLY)**

- `git restore --worktree styles/theme.css`, `git restore -W styles/theme.css`, `git checkout -- styles/theme.css`.
- Common patterns that apply: P8.

**Not accepted**

- Committing the edits, or stashing them (the task is to throw them away).

**Expected Result**
`styles/theme.css` matches the last commit again. You are on `main`, and nothing was committed.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- `styles/theme.css`: identical to HEAD; clean tree.
- Branch `main` still at `c1`; no commit created.

### 1.6.15 Unstage the to-do list, then commit the login fix · Medium

**Variant ID:** `restore-medium-unstage-then-commit-login`

**Story**
You staged everything a little too quickly. `src/login.py` holds the redirect fix that is ready to go, but `notes/todo.md` is staged too, and it holds your personal list for the week. Maeve is waiting for the fix. Your to-do edits should stay in the folder, just not in this commit.

**Starting point:** You are on `main`. `src/login.py` and `notes/todo.md` are both staged.

**Real-World Context**
Unstaging takes a file out of the next commit without touching its edits. That makes it the safe way to correct an over-eager stage before committing.

**Your Task**
Unstage `notes/todo.md` while keeping its edits, then commit the login fix with the message `Fix login redirect`. Finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix login redirect” contains the src/login.py fix.
- [ ] notes/todo.md is not in that commit.
- [ ] Your edits to notes/todo.md are still in the working folder, unstaged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged notes/todo.md` — Take the note out of the index.
2. `git commit -m "Fix login redirect"` — Commit only the login fix.

**Accepted Alternatives (STAFF ONLY)**

- `git restore -S notes/todo.md`, `git reset HEAD -- notes/todo.md`, `git reset -- notes/todo.md` (older equivalents).
- `--message` forms and single quotes. The message must match exactly.
- Common patterns that apply: P8, P1.

**Not accepted**

- Discarding the to-do edits, or committing both files.

**Expected Result**
“Fix login redirect” holds only the login fix. Your to-do edits are still in `notes/todo.md`, uncommitted.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- Latest commit on `main` = `Fix login redirect`; changes include `src/login.py`, not `notes/todo.md`.
- `notes/todo.md` keeps its edited text in the working tree; nothing staged.

### 1.6.16 Unstage the ideas file, then commit the badge fix · Medium

**Variant ID:** `restore-medium-unstage-then-commit-cart`

**Story**
The cart badge has been showing the wrong count, and your fix in `src/cart_badge.js` is ready. When you staged it you also staged `scratch/ideas.txt`, where you have been jotting feature ideas for Sage. The ideas should stay in your folder, but they have no place in a bug-fix commit.

**Starting point:** You are on `main`. `src/cart_badge.js` and `scratch/ideas.txt` are both staged.

**Real-World Context**
A commit should hold one change. Unstaging the unrelated file keeps its edits safe while the fix goes in alone.

**Your Task**
Unstage `scratch/ideas.txt` while keeping its edits, then commit the badge fix with the message `Fix cart badge count`. Finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix cart badge count” contains the src/cart_badge.js fix.
- [ ] scratch/ideas.txt is not in that commit.
- [ ] Your edits to scratch/ideas.txt are still in the working folder, unstaged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged scratch/ideas.txt` — Take the ideas file out of the index.
2. `git commit -m "Fix cart badge count"` — Commit only the badge fix.

**Accepted Alternatives (STAFF ONLY)**

- `git restore -S scratch/ideas.txt`, `git reset HEAD -- scratch/ideas.txt`, `git reset -- scratch/ideas.txt` (older equivalents).
- `--message` forms and single quotes. The message must match exactly.
- Common patterns that apply: P8, P1.

**Not accepted**

- Discarding the ideas, or committing both files.

**Expected Result**
“Fix cart badge count” holds only the badge fix. Your ideas stay in `scratch/ideas.txt`, uncommitted.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- Latest commit on `main` = `Fix cart badge count`; changes include `src/cart_badge.js`, not `scratch/ideas.txt`.
- `scratch/ideas.txt` keeps its edited text in the working tree; nothing staged.

### 1.6.17 Clean up before the report fix · Hard

**Variant ID:** `restore-hard-capstone-report`

**Story**
Before the end of the sprint, Raven asks for the totals fix in `src/report.py`, *and only that*.

Your folder is a mess. `debug.log` got staged by accident, and you want to keep it for now. A test run left stray edits in `tmp/output.txt` that are worth nothing. `src/report.py` itself holds the totals fix next to an experiment you have not finished.

**Starting point:** You are on `main`. `debug.log` is staged. `tmp/output.txt` has stray edits. `src/report.py` holds a totals fix and an experiment.

**Real-World Context**
Real commits often need several kinds of tidying first. Unstage what should wait, discard what is worthless, and stage only the finished part of a mixed file.

**Your Task**
Unstage `debug.log` (keep it in the folder), discard the edits to `tmp/output.txt`, and commit only the totals fix from `src/report.py` with the message `Fix report totals`. **Leave the experiment uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix report totals” contains only the totals fix.
- [ ] debug.log is not committed and is still in the folder.
- [ ] tmp/output.txt is back to its committed version.
- [ ] The experiment is not committed and is still in src/report.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged debug.log` — Take the log out of the index; keep the file.
2. `git restore tmp/output.txt` — Throw away the stray edits.
3. `git add -p src/report.py` — Stage only the totals fix.
4. `git commit -m "Fix report totals"` — Commit it.

**Accepted Alternatives (STAFF ONLY)**

- The first three steps in any order; `git restore -S`, `git reset -- debug.log`; `git restore -W tmp/output.txt`; `git add --patch`.
- `--message` forms and single quotes. The message must match exactly.
- Common patterns that apply: P8, P4, P5, P6.

**Not accepted**

- Committing with debug.log still staged, leaving the stray output edits, or `git add src/report.py` (whole file).

**Expected Result**
“Fix report totals” holds only the totals fix. `debug.log` is untracked in the folder, `tmp/output.txt` matches the last commit, and the experiment stays in `src/report.py`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- Latest commit on `main` = `Fix report totals`; changes include the totals hunk, exclude the experiment hunk, `debug.log` and `tmp/output.txt`.
- `debug.log` still in the working tree; `tmp/output.txt` identical to HEAD; the experiment hunk still unstaged.

### 1.6.18 Clean up before the invoice fix · Hard

**Variant ID:** `restore-hard-capstone-invoice`

**Story**
A customer was charged late fees because invoices showed the wrong due date. Your fix is in `src/invoice.py`, next to a refactor that is only half done.

`notes/invoice-ideas.md` got staged along the way, and you want to keep it, just not commit it. A build left stray edits in `build/invoice.html`. Maeve wants the fix in a clean commit within the hour.

**Starting point:** You are on `main`. `notes/invoice-ideas.md` is staged. `build/invoice.html` has stray edits. `src/invoice.py` holds a due-date fix and a refactor.

**Real-World Context**
An urgent fix should go out on its own. Clearing the index and the working folder first keeps unrelated work out of a commit that might need to be reverted or copied later.

**Your Task**
Unstage `notes/invoice-ideas.md` (keep it in the folder), discard the edits to `build/invoice.html`, and commit only the due-date fix from `src/invoice.py` with the message `Fix invoice due date`. **Leave the refactor uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] A commit named “Fix invoice due date” contains only the due-date fix.
- [ ] notes/invoice-ideas.md is not committed and is still in the folder.
- [ ] build/invoice.html is back to its committed version.
- [ ] The refactor is not committed and is still in src/invoice.py.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged notes/invoice-ideas.md` — Take the notes out of the index; keep the file.
2. `git restore build/invoice.html` — Throw away the stray build edits.
3. `git add -p src/invoice.py` — Stage only the due-date fix.
4. `git commit -m "Fix invoice due date"` — Commit it.

**Accepted Alternatives (STAFF ONLY)**

- The first three steps in any order; `git restore -S`, `git reset -- notes/invoice-ideas.md`; `git restore -W build/invoice.html`; `git add --patch`.
- `--message` forms and single quotes. The message must match exactly.
- Common patterns that apply: P8, P4, P5, P6.

**Not accepted**

- Committing with the notes still staged, leaving the build edits, or `git add src/invoice.py` (whole file).

**Expected Result**
“Fix invoice due date” holds only the due-date fix. The notes are untracked in the folder, `build/invoice.html` matches the last commit, and the refactor stays in `src/invoice.py`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- Latest commit on `main` = `Fix invoice due date`; changes include the due-date hunk, exclude the refactor hunk, the notes and `build/invoice.html`.
- The notes file still in the working tree; `build/invoice.html` identical to HEAD; the refactor hunk still unstaged.

## Module 2 — Branching and Collaboration

### 2.1.14 Back to main after the docs refresh · Easy

**Variant ID:** `switch-easy-back-to-main-docs`

**Story**
You have been polishing the documentation landing page on `feature/docs-refresh`, and the commit is in. Sage pings you: the release checklist lives on `main`, and she wants you to read it from there before the afternoon review.

Nothing on your branch is left uncommitted, so there is nothing to carry over. You only need to step back onto `main`.

**Starting point:** You are on `feature/docs-refresh` with a clean working folder; available local branches: `feature/docs-refresh`, `main`.

**Real-World Context**
Switching branches swaps the files in your working folder for the snapshot of the branch you move to. With everything committed, the move is safe and your feature branch keeps its work.

**Your Task**
Switch back to `main`. **Leave `feature/docs-refresh` exactly as it is.**

**Objective Checklist**

- [ ] main is checked out.
- [ ] feature/docs-refresh still points at your docs commit.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Move HEAD and the working folder to main.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`.
- Common patterns that apply: P23.

**Not accepted**

- Creating a new branch, or moving main to the docs commit.

**Expected Result**
You are on `main`. The docs refresh is still safe on `feature/docs-refresh`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `main` at `c1`; `feature/docs-refresh` still at `c2`.
- Clean tree, nothing staged.

### 2.1.15 Back to main after the API keys model · Easy

**Variant ID:** `switch-easy-back-to-main-api`

**Story**
Finn asked for an API key model for the ticketing app, and you committed it on `feature/api-keys` a few minutes ago. Now he wants a quick look at a bug report that only reproduces on `main`. Your branch is fully committed, so the switch will not take any half-finished work with it.

**Starting point:** You are on `feature/api-keys` with a clean working folder; available local branches: `feature/api-keys`, `main`.

**Real-World Context**
A branch keeps its commits when you leave it. Going back to `main` is how you check what the shared line of work looks like without your feature in it.

**Your Task**
Switch back to `main` and leave `feature/api-keys` untouched.

**Objective Checklist**

- [ ] main is checked out.
- [ ] feature/api-keys still points at the API key commit.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Return to main.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`.
- Common patterns that apply: P23.

**Not accepted**

- `git branch main` (main already exists and HEAD does not move).

**Expected Result**
`main` is checked out, and the API key model waits on `feature/api-keys`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `main` at `c1`; `feature/api-keys` still at `c2`.
- Clean tree, nothing staged.

### 2.1.16 Keep the spike, then head to develop · Hard

**Variant ID:** `switch-hard-detached-save-and-return`

**Story**
Yesterday you checked out an old commit to try a trigram search index and committed the experiment right there, with no branch. The result is promising, and Sage wants it kept for the performance review next week, but not on any working branch.

Today's task is on `develop`. If you simply switch away, the spike commit is left with nothing pointing at it.

**Starting point:** `HEAD` is detached at the spike commit; available local branches: `main`, `develop`. The working folder is clean.

**Real-World Context**
A commit made on a detached `HEAD` belongs to no branch. Giving it a name before you leave is what keeps it from being lost.

**Your Task**
Keep the spike commit on a new branch named `archive/spike-results`, then finish on `develop`. **Do not move `main` or `develop`.**

**Objective Checklist**

- [ ] archive/spike-results points at the spike commit.
- [ ] develop is checked out and unchanged.
- [ ] main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch -c archive/spike-results` — Name the spike commit while HEAD is on it.
2. `git switch develop` — Move on to today's work.

**Accepted Alternatives (STAFF ONLY)**

- `git branch archive/spike-results` then `git switch develop`; `git checkout -b archive/spike-results` then `git checkout develop`.
- Common patterns that apply: P23.

**Not accepted**

- Switching to develop first (the spike commit is left unnamed), or merging the spike into develop.

**Expected Result**
The spike is safe on `archive/spike-results`, and you are on `develop` with nothing else changed.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- `archive/spike-results` at `c3`; HEAD on `develop` at `c2`; `main` at `c1`.
- Clean tree, nothing staged.

### 2.1.17 Set up the FAQ branch, then head back · Easy

**Variant ID:** `switch-easy-branch-then-return-docs`

**Story**
Mika will start the FAQ pages tomorrow and asked you to set up their branch today. Right now you need to stay on `main` to review a teammate's work. The new branch should start from the current `main`.

**Starting point:** You are on `main`. No other branch exists.

**Real-World Context**
Creating a branch and switching back is cheap. The branch waits at its starting commit until someone works on it.

**Your Task**
Create `docs/faq` from the current tip of `main` and switch to it, then switch back to `main`.

**Objective Checklist**

- [ ] docs/faq exists at main's current commit.
- [ ] You finish on main.
- [ ] Nothing changed on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch -c docs/faq` — Create the branch and switch to it.
2. `git switch main` — Go back to main.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout -b docs/faq` then `git checkout main`; `git branch docs/faq`.

**Not accepted**

- Creating the branch from another commit, or finishing on docs/faq.

**Expected Result**
`docs/faq` points at `main`'s tip, and you are on `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- docs/faq and main both at c1; HEAD on main; working tree clean.

### 2.1.18 Set up the rate-limit branch, then head back · Easy

**Variant ID:** `switch-easy-branch-then-return-api`

**Story**
Ana is picking up the API rate limiter after lunch and wants the branch ready. Until then you are on `main`, checking a bug report. The branch should start from the current `main`.

**Starting point:** You are on `main`. No other branch exists.

**Real-World Context**
Teams often create a branch for upcoming work in advance and return to what they were doing.

**Your Task**
Create `feature/rate-limit` from the current tip of `main` and switch to it, then switch back to `main`.

**Objective Checklist**

- [ ] feature/rate-limit exists at main's current commit.
- [ ] You finish on main.
- [ ] Nothing changed on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch -c feature/rate-limit` — Create the branch and switch to it.
2. `git switch main` — Go back to main.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout -b feature/rate-limit` then `git checkout main`; `git branch feature/rate-limit`.

**Not accepted**

- Creating the branch from another commit, or finishing on feature/rate-limit.

**Expected Result**
`feature/rate-limit` points at `main`'s tip, and you are on `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- feature/rate-limit and main both at c1; HEAD on main; working tree clean.

### 2.1.19 Mark the 1.0 release without leaving main · Hard

**Variant ID:** `branch-hard-mark-release-point`

**Story**
Support needs a permanent pointer to the code that shipped as 1.0, and `main` has already moved past it. Raven asks for a `release/1.0` branch on the commit named "Release 1.0 snapshot". You are mid-review on `main` and should stay there.

**Starting point:** You are on `main`. Its history holds the "Release 1.0 snapshot" commit and later work.

**Real-World Context**
`git branch <name> <start-point>` creates a branch at any commit without switching to it.

**Your Task**
Create `release/1.0` at the "Release 1.0 snapshot" commit. **Stay on `main` and leave it where it is.**

**Objective Checklist**

- [ ] release/1.0 points at the "Release 1.0 snapshot" commit.
- [ ] You are still on main, and main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git log --oneline` — Find the release commit.
2. `git branch release/1.0 c2` — Create the branch there without switching.

**Accepted Alternatives (STAFF ONLY)**

- `git switch -c release/1.0 c2` then `git switch main`; `main~1` as the start point.

**Not accepted**

- Creating the branch at main's tip, or moving main.

**Expected Result**
`release/1.0` marks the 1.0 snapshot, and `main` is unchanged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 10

- release/1.0 at c2; main at c3; HEAD on main; working tree clean.

### 2.1.20 Mark the Q3 audit point without leaving main · Hard

**Variant ID:** `branch-hard-mark-audit-point`

**Story**
The auditors signed off on the code at the commit "Q3 audit sign-off", and the compliance team needs a branch there called `audit/q3`. Work on `main` has continued since. You are in the middle of checking `main` and should not leave it.

**Starting point:** You are on `main`. Its history holds the "Q3 audit sign-off" commit and later work.

**Real-World Context**
A branch can mark any past commit, which is handy for audits and releases that need a stable name.

**Your Task**
Create `audit/q3` at the "Q3 audit sign-off" commit. **Stay on `main` and leave it where it is.**

**Objective Checklist**

- [ ] audit/q3 points at the "Q3 audit sign-off" commit.
- [ ] You are still on main, and main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git log --oneline` — Find the sign-off commit.
2. `git branch audit/q3 c3` — Create the branch there without switching.

**Accepted Alternatives (STAFF ONLY)**

- `git switch -c audit/q3 c3` then `git switch main`; `main~1` as the start point.

**Not accepted**

- Creating the branch at main's tip, or moving main.

**Expected Result**
`audit/q3` marks the sign-off commit, and `main` is unchanged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 10

- audit/q3 at c3; main at c4; HEAD on main; working tree clean.

### 2.2.14 Delete the merged typo branch · Easy

**Variant ID:** `bn-easy-delete-merged-typo`

**Story**
Your README typo fix went through review and is already part of `main`. The branch `fix/readme-typo` is still sitting in your local list, and Sage likes the branch list to show only work that is still open. Git can tell that every commit on that branch is already on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `fix/readme-typo`. `fix/readme-typo` is already merged into `main`.

**Real-World Context**
`git branch -d` deletes a branch only when its work is already merged, so it is the safe way to tidy up. The commits stay in `main`'s history.

**Your Task**
Delete the local branch `fix/readme-typo` now that its work is on `main`.

**Objective Checklist**

- [ ] fix/readme-typo no longer exists.
- [ ] main still holds the typo fix.
- [ ] main is checked out.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git branch -d fix/readme-typo` — Delete the merged branch.

**Accepted Alternatives (STAFF ONLY)**

- `git branch --delete fix/readme-typo`. `git branch -D fix/readme-typo` gives the same end state but earns the hint that `-d` is the safe default.
- Common patterns that apply: P30.

**Not accepted**

- Deleting main's commit or switching to a new branch.

**Expected Result**
Only `main` remains, and it still contains the typo fix.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- `fix/readme-typo` absent; HEAD on `main` at `c2`.
- Clean tree, nothing staged.

### 2.2.15 Delete the merged search spike · Easy

**Variant ID:** `bn-easy-delete-merged-spike`

**Story**
Finn decided to keep the old search ranking after all, and your `spike/old-search` branch was merged into `main` this morning. The branch has done its job. Finn asks you to remove it locally so nobody starts new work from it by mistake.

**Starting point:** You are on `main`; available local branches: `main`, `spike/old-search`. `spike/old-search` is already merged into `main`.

**Real-World Context**
Old branch names linger long after their work has landed. Deleting merged branches keeps the list honest about what is still in progress.

**Your Task**
Delete the local branch `spike/old-search`.

**Objective Checklist**

- [ ] spike/old-search no longer exists.
- [ ] main still holds the merged work.
- [ ] main is checked out.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git branch -d spike/old-search` — Delete the merged branch.

**Accepted Alternatives (STAFF ONLY)**

- `git branch --delete spike/old-search`; `-D` is accepted with the hint that `-d` is the safe default.
- Common patterns that apply: P30.

**Not accepted**

- Creating a renamed copy of the branch instead of deleting it.

**Expected Result**
`spike/old-search` is gone, and `main` still has its commit.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- `spike/old-search` absent; HEAD on `main` at `c2`.
- Clean tree, nothing staged.

### 2.2.16 Start the parser fix on a proper branch · Hard

**Variant ID:** `bn-hard-named-branch-commit-parser`

**Story**
You fixed the parser's handling of unicode identifiers in `src/parser.py`, but you did it straight on `main`. While debugging you also scribbled into `debug.log`, which is tracked and must not change.

Sage reminds you of the group's rule: fixes go on a branch named `fix/` followed by the topic, and the topic for this ticket is `parser-unicode`. Main must stay exactly where it is.

**Starting point:** You are on `main`; `src/parser.py` has the finished fix and `debug.log` has a stray edit, both uncommitted.

**Real-World Context**
Uncommitted edits travel with you when you create a branch, so a fix started on the wrong branch can still be committed in the right place. A stray edit to a tracked file has to be thrown away first, or it ends up in the commit.

**Your Task**
Discard the stray edit in `debug.log`. Then create `fix/parser-unicode`, switch to it, and commit __only__ `src/parser.py` with the message `Handle unicode identifiers`.

**Objective Checklist**

- [ ] fix/parser-unicode is checked out and has one new commit, Handle unicode identifiers.
- [ ] That commit contains the parser fix and the original debug.log.
- [ ] main has not moved.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore debug.log` — Throw away the stray edit.
2. `git switch -c fix/parser-unicode` — Start the convention-named branch; the fix comes along.
3. `git add src/parser.py` — Stage the fix.
4. `git commit -m "Handle unicode identifiers"` — Commit it on the new branch.

**Accepted Alternatives (STAFF ONLY)**

- Restoring debug.log at any point before the commit; `git checkout -b fix/parser-unicode`; `git add .` after the restore.
- Common patterns that apply: P23.

**Not accepted**

- Committing on main, committing the debug.log edit, or any other branch name.

**Expected Result**
The fix is one commit on `fix/parser-unicode`, `main` is untouched, and `debug.log` is back to its committed text.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `fix/parser-unicode`, 2 commits; tip message `Handle unicode identifiers`, tree has the parser fix and the committed `debug.log`.
- `main` at `c1`; clean tree, nothing staged.

### 2.2.17 Start the invoice fix on a ticket branch · Hard

**Variant ID:** `bn-hard-named-branch-commit-billing`

**Story**
The invoice totals were rounding the wrong way, and your fix in `src/billing.py` works. You made it on `main`, though, and a test run also overwrote `tmp/billing-dump.txt`, a tracked sample file.

Finn's team names branches after the ticket: `PROJ-733/invoice-rounding`. He wants the fix there, in one commit, with `main` untouched.

**Starting point:** You are on `main`; `src/billing.py` has the finished fix and `tmp/billing-dump.txt` has a stray edit, both uncommitted.

**Real-World Context**
Ticket-based branch names let anyone trace a change back to the request that asked for it. Cleaning out stray edits first keeps the commit about the ticket and nothing else.

**Your Task**
Discard the stray edit in `tmp/billing-dump.txt`, create and switch to `PROJ-733/invoice-rounding`, and commit __only__ `src/billing.py` with the message `Round invoice totals`.

**Objective Checklist**

- [ ] PROJ-733/invoice-rounding is checked out with one new commit, Round invoice totals.
- [ ] The commit contains the fix and the original tmp/billing-dump.txt.
- [ ] main has not moved.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore tmp/billing-dump.txt` — Throw away the stray edit.
2. `git switch -c PROJ-733/invoice-rounding` — Start the ticket branch.
3. `git add src/billing.py` — Stage the fix.
4. `git commit -m "Round invoice totals"` — Commit it.

**Accepted Alternatives (STAFF ONLY)**

- Restoring the sample file at any point before the commit; `git checkout -b PROJ-733/invoice-rounding`.
- Common patterns that apply: P23.

**Not accepted**

- A branch name without the ticket number, committing on main, or committing the sample file's edit.

**Expected Result**
The rounding fix is one commit on `PROJ-733/invoice-rounding`, and `main` is exactly as before.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `PROJ-733/invoice-rounding`, 2 commits; tip message `Round invoice totals`, tree has the fix and the committed sample file.
- `main` at `c1`; clean tree, nothing staged.

### 2.2.18 Clear out the sprint's merged branches · Hard

**Variant ID:** `bn-hard-clear-merged-sprint`

**Story**
The sprint is over, and the branch list is getting long. `feature/login-copy` and `fix/footer-link` are already in `main`. `spike/dark-mode` is an experiment that never merged, and Finn still wants it. Raven asks for a tidy list before planning starts.

**Starting point:** You are on `main` with `feature/login-copy`, `fix/footer-link` and `spike/dark-mode` beside it.

**Real-World Context**
`git branch -d` only deletes branches whose work is already merged, so housekeeping cannot lose unmerged work by accident.

**Your Task**
Delete the local branches that are already merged into `main`. **Keep `spike/dark-mode`.**

**Objective Checklist**

- [ ] feature/login-copy and fix/footer-link are gone.
- [ ] spike/dark-mode still exists at its commit.
- [ ] main has not moved, and you are on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git branch -d feature/login-copy` — Delete the first merged branch.
2. `git branch -d fix/footer-link` — Delete the second.

**Accepted Alternatives (STAFF ONLY)**

- One `git branch -d feature/login-copy fix/footer-link`; `git branch --merged` to check first.

**Not accepted**

- Deleting spike/dark-mode, or using `-D` on it.

**Expected Result**
Only `main` and `spike/dark-mode` remain.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- Both merged branches absent; spike/dark-mode at c4; main at c3; HEAD on main.

### 2.2.19 Clear out the release's merged branches · Hard

**Variant ID:** `bn-hard-clear-merged-release`

**Story**
Release 1.4 and its hotfix are both in `main` now, but their branches are still lying around. `experiment/new-nav` is unmerged work that Ana will finish next month. The team wants only live branches in the list.

**Starting point:** You are on `main` with `release/1.4`, `hotfix/1.4.1` and `experiment/new-nav` beside it.

**Real-World Context**
Deleting merged branches keeps the branch list readable without losing any history, because their commits stay reachable from main.

**Your Task**
Delete the local branches that are already merged into `main`. **Keep `experiment/new-nav`.**

**Objective Checklist**

- [ ] release/1.4 and hotfix/1.4.1 are gone.
- [ ] experiment/new-nav still exists at its commit.
- [ ] main has not moved, and you are on main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git branch -d release/1.4` — Delete the merged release branch.
2. `git branch -d hotfix/1.4.1` — Delete the merged hotfix branch.

**Accepted Alternatives (STAFF ONLY)**

- One `git branch -d release/1.4 hotfix/1.4.1`; `git branch --merged` to check first.

**Not accepted**

- Deleting experiment/new-nav, or using `-D` on it.

**Expected Result**
Only `main` and `experiment/new-nav` remain.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- Both merged branches absent; experiment/new-nav at c4; main at c3; HEAD on main.

### 2.3.14 Bring back the search ranking draft · Easy

**Variant ID:** `stash-easy-pop-search`

**Story**
Before lunch you shelved your half-done search ranking changes with `git stash` so you could check a bug on `main`. The bug is handled, you are back on `feature/search`, and your working folder is clean. The draft is the only entry in the stash.

Finn wants a demo of the ranking this afternoon, so it is time to pick it up again.

**Starting point:** You are on `feature/search` with a clean working folder; the stash holds one entry with your search ranking edits.

**Real-World Context**
`git stash pop` puts shelved changes back into your working folder and removes them from the stash, so the shelf does not fill up with copies you already restored.

**Your Task**
Bring the stashed search work back into your working folder and remove it from the stash. **Do not commit it.**

**Objective Checklist**

- [ ] src/search.py has your ranking edits again, uncommitted.
- [ ] The stash is empty.
- [ ] feature/search is checked out and has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash pop` — Restore the latest stash entry and drop it.

**Accepted Alternatives (STAFF ONLY)**

- `git stash apply` followed by `git stash drop`; `git stash pop stash@{0}`.
- Common patterns that apply: P24.

**Not accepted**

- `git stash apply` alone (the entry stays in the stash), or `git stash drop` (the draft is lost).

**Expected Result**
Your ranking draft is back in `src/search.py`, and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `feature/search` at `c2`; `src/search.py` modified with the ranking draft; nothing staged.
- Stash list empty.

### 2.3.15 Bring back the profile avatar draft · Easy

**Variant ID:** `stash-easy-pop-profile`

**Story**
Sage interrupted your avatar upload work for a quick review, and you stashed the unfinished edits to `src/profile.py`. The review is done and you are back on `feature/profile` with a clean folder. Your draft is the only thing in the stash, and you want it back exactly where it was.

**Starting point:** You are on `feature/profile` with a clean working folder; the stash holds one entry with your avatar edits.

**Real-World Context**
A stash is a shelf for unfinished work, not a place to keep it. Popping it puts the work back and clears the shelf in one step.

**Your Task**
Restore the stashed avatar work into your working folder and remove it from the stash. **Leave it uncommitted**.

**Objective Checklist**

- [ ] src/profile.py has your avatar edits again, uncommitted.
- [ ] The stash is empty.
- [ ] feature/profile is checked out and has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash pop` — Restore the entry and drop it from the stash.

**Accepted Alternatives (STAFF ONLY)**

- `git stash apply` followed by `git stash drop`.
- Common patterns that apply: P24.

**Not accepted**

- `git stash drop` (throws the draft away) or leaving the entry in the stash.

**Expected Result**
The avatar draft is back in `src/profile.py`, and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `feature/profile` at `c2`; `src/profile.py` modified with the avatar draft; nothing staged.
- Stash list empty.

### 2.3.16 Two drafts in the stash, keep the real one · Hard

**Variant ID:** `stash-hard-two-stashes-reports`

**Story**
Your stash on `feature/reports` has two entries. The older one, `stash@{1}`, is the monthly totals work Maeve is waiting for. The newer one, `stash@{0}`, is a neon chart colour experiment that the group voted down in this morning's stand-up.

You want the totals back in your working folder and the experiment gone for good, with nothing left in the stash.

**Starting point:** You are on `feature/reports` with a clean working folder; `stash@{0}` is the rejected chart experiment and `stash@{1}` is the monthly totals work.

**Real-World Context**
Stash entries are numbered from the newest, `stash@{0}`. Naming the entry you mean is how you drop one and keep another.

**Your Task**
Discard the chart experiment from the stash, then restore the monthly totals work into your working folder. **Finish with an empty stash.**

**Objective Checklist**

- [ ] src/reports.py has the monthly totals work, uncommitted.
- [ ] src/chart.js does not have the experiment.
- [ ] The stash is empty.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash drop stash@{0}` — Discard the rejected experiment.
2. `git stash pop` — Restore the totals work, now the only entry.

**Accepted Alternatives (STAFF ONLY)**

- `git stash pop stash@{1}` then `git stash drop`; `git stash list` or `git stash show` along the way.
- Common patterns that apply: P24, P39, P40.

**Not accepted**

- Popping stash@{0} (it restores the experiment), or dropping stash@{1}.

**Expected Result**
The totals work is back in `src/reports.py`, the experiment is gone, and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- `src/reports.py` modified with the totals work; `src/chart.js` without the experiment.
- Stash list empty; HEAD on `feature/reports`; nothing staged.

### 2.3.17 Check the release, then drop the layout experiment · Hard

**Variant ID:** `stash-hard-cancelled-experiment`

**Story**
You are partway through a grid layout experiment in `src/layout.py` on `feature/experiment` when Finn asks you to check something on `release/v3`. While you are there, he tells you the experiment is cancelled: the design team is going another way.

When you come back to your branch, the experiment should be gone completely, from your folder and from the stash, and it must not have travelled with you onto the release branch.

**Starting point:** You are on `feature/experiment` with unfinished edits in `src/layout.py`; available local branches: `main`, `release/v3`, `feature/experiment`.

**Real-World Context**
Shelving work before a detour keeps it off other branches. When the work is cancelled while it sits on the shelf, dropping the entry is the clean ending.

**Your Task**
Visit `release/v3` without carrying your edits along, return to `feature/experiment`, and finish with a clean working folder and an empty stash.

**Objective Checklist**

- [ ] feature/experiment is checked out and has not moved.
- [ ] The working folder is clean.
- [ ] The stash is empty.
- [ ] release/v3 is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Shelve the experiment before the detour.
2. `git switch release/v3` — Check the release branch.
3. `git switch feature/experiment` — Come back.
4. `git stash drop` — Throw away the cancelled experiment.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout` for either switch; `git stash push`.
- Common patterns that apply: P14, P23, P39, P40.

**Not accepted**

- `git stash pop` on return (restores the cancelled work), or switching with the edits still in the folder.

**Expected Result**
You are back on `feature/experiment` with a clean folder, and nothing of the experiment is left anywhere.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `feature/experiment` at `c3`; `release/v3` at `c2`.
- Clean tree, nothing staged, stash list empty.

### 2.3.18 Park the search draft while you check the release · Hard

**Variant ID:** `stash-hard-park-draft-search`

**Story**
You are halfway through search facets on `feature/search` when Raven asks you to look over `release/v4`. The facets are not ready to commit, and you won't touch them again until tomorrow. Leave the branch clean, but keep the draft saved for later.

**Starting point:** You are on `feature/search` with uncommitted edits to `src/search.py`.

**Real-World Context**
A stash can hold work for as long as you need. You don't have to restore it the moment you come back.

**Your Task**
Visit `release/v4` without carrying your edits along, then return to `feature/search`. **Finish with a clean working folder and the draft still saved in the stash.**

**Objective Checklist**

- [ ] You visited release/v4 and finished on feature/search.
- [ ] The working folder is clean and no commit was made.
- [ ] The stash holds one entry with the search draft.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Shelve the draft.
2. `git switch release/v4` — Check the release.
3. `git switch feature/search` — Come back.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git checkout` for the switches.

**Not accepted**

- Committing the draft, popping or dropping the stash.

**Expected Result**
You are back on a clean `feature/search`, and the stash holds the facets draft.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on feature/search at c3; release/v4 at c2; the reflog shows the visit; one stash entry with src/search.py.

### 2.3.19 Park the billing draft while you check the hotfix · Hard

**Variant ID:** `stash-hard-park-draft-billing`

**Story**
You are drafting billing credits on `feature/billing` when Finn needs a second pair of eyes on `hotfix/tax`. The credits draft isn't finished and can wait until Monday. Your branch should be clean while the draft stays safe.

**Starting point:** You are on `feature/billing` with uncommitted edits to `src/billing.py`.

**Real-World Context**
Stashing keeps unfinished work out of commits and out of other branches until you are ready for it.

**Your Task**
Visit `hotfix/tax` without carrying your edits along, then return to `feature/billing`. **Finish with a clean working folder and the draft still saved in the stash.**

**Objective Checklist**

- [ ] You visited hotfix/tax and finished on feature/billing.
- [ ] The working folder is clean and no commit was made.
- [ ] The stash holds one entry with the billing draft.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Shelve the draft.
2. `git switch hotfix/tax` — Check the hotfix.
3. `git switch feature/billing` — Come back.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git checkout` for the switches.

**Not accepted**

- Committing the draft, popping or dropping the stash.

**Expected Result**
You are back on a clean `feature/billing`, and the stash holds the credits draft.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on feature/billing at c3; hotfix/tax at c2; the reflog shows the visit; one stash entry with src/billing.py.

### 2.4.14 Branch, commit and publish the search filters · Medium

**Variant ID:** `push-medium-branch-commit-publish-search`

**Story**
You built the search filters for the shop's web front end in a new file, `src/filters.js`, while still on `main`. Finn wants them reviewed as their own branch, `feature/search-filters`, and he will keep asking for changes, so the branch should remember its place on `origin`. *Main must not get the commit.*

**Starting point:** You are on `main`; `src/filters.js` is a new, uncommitted file; `origin` is available.

**Real-World Context**
Most features follow the same short loop: branch, commit, publish with an upstream. After `-u`, later pushes and pulls on that branch need no names.

**Your Task**
Create and switch to `feature/search-filters`, commit `src/filters.js` with the message `Add search filters`, then publish the branch to `origin` and set its upstream.

**Objective Checklist**

- [ ] feature/search-filters has the commit Add search filters with src/filters.js.
- [ ] origin/feature/search-filters matches it, and the local branch tracks it.
- [ ] main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch -c feature/search-filters` — Start the feature branch; the new file comes along.
2. `git add src/filters.js` — Stage it.
3. `git commit -m "Add search filters"` — Commit it on the branch.
4. `git push -u origin feature/search-filters` — Publish and set the upstream.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout -b feature/search-filters`; `git push --set-upstream origin feature/search-filters`; `git push -u origin HEAD`.
- Common patterns that apply: P23, P31.

**Not accepted**

- Committing on main, or pushing without setting the upstream.

**Expected Result**
The filters live in one commit on `feature/search-filters`, published to `origin` and tracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `feature/search-filters`; tip `Add search filters` (parent `c1`) with `src/filters.js`.
- `origin/feature/search-filters` = local branch; upstream `origin/feature/search-filters`; `main` at `c1`; clean tree.

### 2.4.15 Branch, commit and publish the invoice PDF export · Medium

**Variant ID:** `push-medium-branch-commit-publish-invoices`

**Story**
The billing service can finally export invoices as PDFs, and your code sits in a new file, `src/invoice_pdf.py`. You wrote it on `main` by habit. Sage wants it on `feature/invoice-pdf`, pushed to `origin` so the accountants' reviewer can try it, with the branch tracking `origin` for the follow-up fixes.

**Starting point:** You are on `main`; `src/invoice_pdf.py` is a new, uncommitted file; `origin` is available.

**Real-World Context**
Moving uncommitted work onto a new branch is free: the files come with you. Setting the upstream on the first push saves typing on every later push.

**Your Task**
Create and switch to `feature/invoice-pdf`, commit `src/invoice_pdf.py` with the message `Add invoice PDF export`, then publish the branch to `origin` with its upstream set.

**Objective Checklist**

- [ ] feature/invoice-pdf has the commit Add invoice PDF export.
- [ ] origin/feature/invoice-pdf matches it, and the local branch tracks it.
- [ ] main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch -c feature/invoice-pdf` — Start the branch.
2. `git add src/invoice_pdf.py` — Stage the export.
3. `git commit -m "Add invoice PDF export"` — Commit it.
4. `git push -u origin feature/invoice-pdf` — Publish and track.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout -b feature/invoice-pdf`; `git push --set-upstream origin feature/invoice-pdf`.
- Common patterns that apply: P23, P31.

**Not accepted**

- Committing on main, or a push that leaves no upstream.

**Expected Result**
`feature/invoice-pdf` holds the export, published to `origin` and tracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `feature/invoice-pdf`; tip `Add invoice PDF export` (parent `c1`) with `src/invoice_pdf.py`.
- `origin/feature/invoice-pdf` = local branch; upstream set; `main` at `c1`; clean tree.

### 2.4.16 Reword a published commit and republish safely · Hard

**Variant ID:** `push-hard-amend-then-lease-api`

**Story**
You pushed `feature/api-retry` an hour ago with the commit message "Fix stuff", and Finn bounced it in review: the message has to say what the change does. Nobody else has pushed to the branch.

Rewording the commit rewrites history that is already on `origin`, and Finn does not want anyone's work overwritten blindly.

**Starting point:** You are on `feature/api-retry`, already pushed to `origin`; the last commit's message is "Fix stuff"; nobody else has pushed to the branch.

**Real-World Context**
Amending a pushed commit replaces it with a new one. `--force-with-lease` updates the remote only if it still holds what you last saw, so you never overwrite a teammate's push by accident.

**Your Task**
Change the last commit's message to `Add retry to API client`, then update `origin`'s `feature/api-retry` **without overwriting work you have not seen**.

**Objective Checklist**

- [ ] The last commit is now Add retry to API client, with the same changes.
- [ ] origin/feature/api-retry matches your local branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Add retry to API client"` — Replace the commit with a reworded one.
2. `git push --force-with-lease origin feature/api-retry` — Republish only if origin is as you left it.

**Accepted Alternatives (STAFF ONLY)**

- `--force-with-lease=feature/api-retry`; `git push --force-with-lease` with the upstream set.
- `--force` also completes it (same end state), with the hint that `--force-with-lease` is the safe choice.

**Not accepted**

- A plain push (Git rejects it: origin still has the old commit), or a new commit on top instead of the amend.

**Expected Result**
`origin/feature/api-retry` now holds the reworded commit, published with a lease.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- HEAD on `feature/api-retry`; tip `Add retry to API client` (parent `c1`), replacing `c2`, same tree.
- `origin/feature/api-retry` = local branch; clean tree.

### 2.4.17 Reword the SSO docs commit and republish · Hard

**Variant ID:** `push-hard-amend-then-lease-docs`

**Story**
Your SSO setup guide is on `docs/sso` and already on `origin`, but you committed it with the message "docs". Raven, who keeps the handbook tidy, asks for a message that describes the change.

You are the only one working on the branch, and you want to keep it that way: the republish should fail if anyone else pushed in the meantime.

**Starting point:** You are on `docs/sso`, already pushed to `origin`; the last commit's message is "docs".

**Real-World Context**
After you rewrite a commit, your branch and its remote copy have diverged. A lease-protected push replaces the remote copy only when no one else has changed it.

**Your Task**
Change the last commit's message to `Document SSO setup`, then update `origin`'s `docs/sso` **safely**.

**Objective Checklist**

- [ ] The last commit is now Document SSO setup, with the same changes.
- [ ] origin/docs/sso matches your local branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Document SSO setup"` — Reword the commit.
2. `git push --force-with-lease origin docs/sso` — Republish safely.

**Accepted Alternatives (STAFF ONLY)**

- `--force-with-lease=docs/sso`.
- `--force` also completes it (same end state), with the hint that `--force-with-lease` is the safe choice.

**Not accepted**

- A plain push (Git rejects it), or an extra commit instead of the amend.

**Expected Result**
`origin/docs/sso` holds the reworded commit, and the push was protected by a lease.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- HEAD on `docs/sso`; tip `Document SSO setup` (parent `c1`), replacing `c2`, same tree.
- `origin/docs/sso` = local branch; clean tree.

### 2.5.14 Update main, then start dark mode · Medium

**Variant ID:** `pull-medium-update-then-branch-ui`

**Story**
Finn merged a tidy-up of the theme colours into `main` on the server this morning, and your local `main` has not seen it yet. Your next task is dark mode, which builds directly on those colours. Starting from yesterday's `main` would mean redoing his work in a merge later, so the new branch has to start from an up-to-date `main`.

**Starting point:** You are on `main` with a clean working folder; `origin/main` has a new commit that your local `main` does not have.

**Real-World Context**
A branch starts from whatever commit you are on. Pulling first gives new work the newest starting point.

**Your Task**
Bring `main` up to date with `origin`, then create and switch to `feature/dark-mode` from it.

**Objective Checklist**

- [ ] main matches origin/main, including the colour tidy-up.
- [ ] feature/dark-mode starts at the updated main and is checked out.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin main` — Bring in the new commit.
2. `git switch -c feature/dark-mode` — Start the branch from the fresh main.

**Accepted Alternatives (STAFF ONLY)**

- `git pull`; `git fetch origin` then `git merge origin/main`; `git checkout -b feature/dark-mode`.
- Common patterns that apply: P2, P23, P41.

**Not accepted**

- Creating the branch before updating main, or pulling into the new branch only.

**Expected Result**
`main` and `feature/dark-mode` both point at the newest commit from `origin`, and you are on `feature/dark-mode`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD on `feature/dark-mode` at `c2`; `main` at `c2`; `origin/main` at `c2`.
- Clean tree, nothing staged.

### 2.5.15 Update main, then start the webhooks · Medium

**Variant ID:** `pull-medium-update-then-branch-api`

**Story**
Sage pushed an event registry to the billing service's `main` branch overnight. Your webhooks feature will register its events there, so it has to start from a `main` that includes her commit. Your local `main` is one commit behind `origin`.

**Starting point:** You are on `main` with a clean working folder; `origin/main` has a new commit that your local `main` does not have.

**Real-World Context**
Pulling before you branch is a small habit that saves a merge later: the branch starts with everything your teammates already shipped.

**Your Task**
Bring `main` up to date with `origin`, then create and switch to `feature/webhooks` from it.

**Objective Checklist**

- [ ] main matches origin/main, including the event registry.
- [ ] feature/webhooks starts at the updated main and is checked out.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin main` — Bring in Sage's commit.
2. `git switch -c feature/webhooks` — Start the branch here.

**Accepted Alternatives (STAFF ONLY)**

- `git pull`; `git fetch origin` then `git merge origin/main`; `git checkout -b feature/webhooks`.
- Common patterns that apply: P2, P23, P41.

**Not accepted**

- Fetching without updating main before branching.

**Expected Result**
`feature/webhooks` starts from the updated `main`, and you are on it.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD on `feature/webhooks` at `c2`; `main` at `c2`; `origin/main` at `c2`.
- Clean tree, nothing staged.

### 2.5.16 Update main without losing your guide edits · Hard

**Variant ID:** `pull-hard-stash-pull-pop-docs`

**Story**
You are rewriting the install section of `docs/guide.md` when Raven asks you to pull: she fixed typos in the guide's intro and wants everyone on the new version before the handbook freeze. Your edits are not ready to commit, and Git will refuse to pull over them because the same file changed on `origin`.

You want `main` updated and your draft back, still uncommitted, with nothing left on the shelf.

**Starting point:** You are on `main` with uncommitted edits in `docs/guide.md`; `origin/main` has a new commit that also changes `docs/guide.md`.

**Real-World Context**
Git will not let a pull overwrite uncommitted changes to a file the pull touches. Stashing clears the way, and popping afterwards puts your draft back on top of the new version.

**Your Task**
Update `main` from `origin` without losing your edits to `docs/guide.md`. **Keep the edits uncommitted and leave nothing in the stash.**

**Objective Checklist**

- [ ] main matches origin/main, including Raven's typo fixes.
- [ ] docs/guide.md still has your install section draft, uncommitted.
- [ ] The stash is empty.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Shelve the draft so the pull can run.
2. `git pull origin main` — Bring in Raven's commit.
3. `git stash pop` — Put the draft back and clear the shelf.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git pull`; `git fetch origin` then `git merge origin/main`; `git stash apply` then `git stash drop`.
- Common patterns that apply: P2, P14, P24, P41.

**Not accepted**

- Committing the draft, discarding it, or leaving it in the stash.

**Expected Result**
`main` has Raven's commit, your draft is back in `docs/guide.md`, and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `main` at `c2`; `origin/main` at `c2`.
- `docs/guide.md` modified with the draft; nothing staged; stash list empty.

### 2.5.17 Update develop without losing your timeout setting · Hard

**Variant ID:** `pull-hard-stash-pull-pop-app`

**Story**
You are adding a request timeout setting to `src/app.py` on `develop` when Finn pushes a logging setup to the same file. He needs everyone on the new `develop` before the integration test run.

Your setting is half done and not worth a commit yet. A pull would overwrite your edits, so Git will refuse it until they are out of the way.

**Starting point:** You are on `develop` with uncommitted edits in `src/app.py`; `origin/develop` has a new commit that also changes `src/app.py`.

**Real-World Context**
The stash is the quick way to step out of the way of a pull and step back in afterwards, without making a throwaway commit.

**Your Task**
Update `develop` from `origin` without losing your edits to `src/app.py`. **Keep them uncommitted and leave nothing in the stash.**

**Objective Checklist**

- [ ] develop matches origin/develop, including Finn's logging setup.
- [ ] src/app.py still has your timeout setting draft, uncommitted.
- [ ] The stash is empty.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Shelve the draft.
2. `git pull origin develop` — Bring in Finn's commit.
3. `git stash pop` — Restore the draft and clear the shelf.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git pull`; `git fetch origin` then `git merge origin/develop`; `git stash apply` then `git stash drop`.
- Common patterns that apply: P2, P14, P24, P41.

**Not accepted**

- Committing or discarding the draft, or leaving it in the stash.

**Expected Result**
`develop` has Finn's commit, your draft is back in `src/app.py`, and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `develop` at `c2`; `origin/develop` at `c2`.
- `src/app.py` modified with the draft; nothing staged; stash list empty.

### 2.6.14 Commit the setup docs, reconcile and publish · Medium

**Variant ID:** `rec-medium-commit-then-reconcile-docs`

**Story**
You wrote a local setup guide in `docs/setup.md` and staged it, but you also staged `notes/draft.md`, your private scratch notes.

Meanwhile Sage pushed a contributor guide to `origin/main`, so your `main` and the server's have both moved. Raven wants the setup guide published today, without your notes and without losing Sage's commit.

**Starting point:** You are on `main`; `docs/setup.md` and `notes/draft.md` are both staged; `origin/main` has a new commit you do not have.

**Real-World Context**
Reconciling is often the last step of a small workflow: fix the staging, commit, bring in the remote's work, publish. A pull on diverged histories ties both lines together with a merge commit.

**Your Task**
Unstage `notes/draft.md` and keep its edits. Commit `docs/setup.md` with the message `Document local setup`, integrate `origin/main` by pulling, and push `main` to `origin`.

**Objective Checklist**

- [ ] Your commit Document local setup contains docs/setup.md and not your notes.
- [ ] main merges Sage's contributor guide with your commit.
- [ ] origin/main matches your main.
- [ ] notes/draft.md still has your edits, uncommitted.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged notes/draft.md` — Take the notes out of the commit; keep the edits.
2. `git commit -m "Document local setup"` — Commit the setup guide.
3. `git pull origin main` — Merge in Sage's commit.
4. `git push origin main` — Publish the combined main.

**Accepted Alternatives (STAFF ONLY)**

- `git reset notes/draft.md` for the unstage; `git pull`; `git fetch origin` then `git merge origin/main`; `git push`.
- Common patterns that apply: P2, P31, P41.

**Not accepted**

- Committing the notes, pushing before integrating, or `git pull --rebase` (this level practises reconciling with a merge).

**Expected Result**
`origin/main` has a merge of your setup guide and Sage's contributor guide, and your notes stay uncommitted in the folder.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- `main` tip is a merge whose tree has `docs/setup.md`, `CONTRIBUTING.md` and the committed `notes/draft.md`; `main~1` is `Document local setup` (parent `c1`).
- `origin/main` = `main`; `notes/draft.md` modified with your edits; nothing staged.

### 2.6.15 Commit the health check, reconcile and publish · Medium

**Variant ID:** `rec-medium-commit-then-reconcile-api`

**Story**
Your health check endpoint in `src/health.py` is staged and ready, and so, by accident, is `scratch/payload.json`, a test payload you were playing with.

Finn has pushed contributor docs to `origin/develop` since your last pull. He wants the health check on `origin/develop` before the deploy window, with his docs intact and your scratch file kept out.

**Starting point:** You are on `develop`; `src/health.py` and `scratch/payload.json` are both staged; `origin/develop` has a new commit you do not have.

**Real-World Context**
Unstaging is how you fix a commit before it exists. Integrating before you push keeps a teammate's work from being rejected or lost.

**Your Task**
Unstage `scratch/payload.json` and keep its edits. Commit `src/health.py` with the message `Add health check`, integrate `origin/develop` by pulling, and push `develop` to `origin`.

**Objective Checklist**

- [ ] Your commit Add health check contains src/health.py and not the scratch file.
- [ ] develop merges Finn's docs with your commit.
- [ ] origin/develop matches your develop.
- [ ] scratch/payload.json still has your edits, uncommitted.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged scratch/payload.json` — Keep the scratch file out.
2. `git commit -m "Add health check"` — Commit the endpoint.
3. `git pull origin develop` — Merge in Finn's commit.
4. `git push origin develop` — Publish.

**Accepted Alternatives (STAFF ONLY)**

- `git reset scratch/payload.json`; `git fetch origin` then `git merge origin/develop`; `git push`.
- Common patterns that apply: P2, P31, P41.

**Not accepted**

- Committing the scratch file, pushing before integrating, or `git pull --rebase`.

**Expected Result**
`origin/develop` has a merge of the health check and Finn's docs, and the scratch file stays uncommitted.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- `develop` tip is a merge whose tree has `src/health.py`, `docs/contributing.md` and the committed `scratch/payload.json`; `develop~1` is `Add health check` (parent `c1`).
- `origin/develop` = `develop`; `scratch/payload.json` modified with your edits; nothing staged.

### 2.6.16 Commit the ranking fix and merge a teammate's push · Hard

**Variant ID:** `rec-hard-commit-fetch-merge-search`

**Story**
Your ranking tweak is staged on `feature/search`, but so is `notes/plan.md`, which is only your to-do list. Meanwhile Mika pushed search docs to the same branch on `origin`. The branch on `origin` should end up with your fix and Mika's docs, and without your notes.

**Starting point:** You are on `feature/search` with `src/ranking.py` and `notes/plan.md` staged. `origin/feature/search` has a newer commit from Mika.

**Real-World Context**
Fetching first lets you merge exactly what the server has, so your push lands on top of your teammate's work instead of being rejected.

**Your Task**
Commit only the ranking change with the message `Tune search ranking`, keeping your notes out of the commit. Then combine it with the newer `origin/feature/search` and publish `feature/search` to `origin`.

**Objective Checklist**

- [ ] A commit "Tune search ranking" holds src/ranking.py but not your notes.
- [ ] feature/search includes Mika's commit, and origin/feature/search matches it.
- [ ] notes/plan.md is still in your folder, uncommitted.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged notes/plan.md` — Take the notes out of the commit.
2. `git commit -m "Tune search ranking"` — Commit the fix.
3. `git fetch origin` — Download Mika's commit.
4. `git merge origin/feature/search` — Combine the two lines of work.
5. `git push origin feature/search` — Publish the result.

**Accepted Alternatives (STAFF ONLY)**

- `git pull origin feature/search` in place of fetch and merge; `git reset notes/plan.md` to unstage.

**Not accepted**

- Committing the notes, or a force push.

**Expected Result**
`feature/search` on `origin` holds your fix and Mika's docs, and your notes are still local.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Tip is a merge containing the fix and Mika's docs; its first parent is "Tune search ranking"; origin matches; the notes edit is still in the working tree.

### 2.6.17 Commit the rounding fix and merge a teammate's push · Hard

**Variant ID:** `rec-hard-commit-fetch-merge-billing`

**Story**
You staged the invoice rounding fix on `feature/billing`, along with `tmp/invoice-dump.json` from a debugging session. Ana has since pushed billing docs to the branch on `origin`. The published branch needs your fix and Ana's docs, and the debug dump must stay out.

**Starting point:** You are on `feature/billing` with `src/rounding.py` and `tmp/invoice-dump.json` staged. `origin/feature/billing` has a newer commit from Ana.

**Real-World Context**
A clean reconcile starts with a clean commit: leave scratch files out before you merge and publish.

**Your Task**
Commit only the rounding change with the message `Round invoice totals`, keeping the dump out of the commit. Then combine it with the newer `origin/feature/billing` and publish `feature/billing` to `origin`.

**Objective Checklist**

- [ ] A commit "Round invoice totals" holds src/rounding.py but not the dump.
- [ ] feature/billing includes Ana's commit, and origin/feature/billing matches it.
- [ ] tmp/invoice-dump.json is still in your folder, uncommitted.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged tmp/invoice-dump.json` — Take the dump out of the commit.
2. `git commit -m "Round invoice totals"` — Commit the fix.
3. `git fetch origin` — Download Ana's commit.
4. `git merge origin/feature/billing` — Combine the two lines of work.
5. `git push origin feature/billing` — Publish the result.

**Accepted Alternatives (STAFF ONLY)**

- `git pull origin feature/billing` in place of fetch and merge; `git reset tmp/invoice-dump.json` to unstage.

**Not accepted**

- Committing the dump, or a force push.

**Expected Result**
`feature/billing` on `origin` holds your fix and Ana's docs, and the dump is still local.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Tip is a merge containing the fix and Ana's docs; its first parent is "Round invoice totals"; origin matches; the dump edit is still in the working tree.

### 2.7.14 Finish the monthly report, then land it · Medium

**Variant ID:** `merge-medium-commit-switch-noff-reports`

**Story**
The monthly report in `src/reports.py` is finished, but the last round of edits is still uncommitted on `feature/reports`. Maeve wants it on `main` today, and she wants the history to show that the report arrived as one feature, so a fast-forward will not do: `main` needs a merge commit.

**Starting point:** You are on `feature/reports`; `src/reports.py` has finished, uncommitted edits; `main` has not moved since the branch started.

**Real-World Context**
A merge only brings in what is committed. Finishing the commit first, then merging with `--no-ff`, records the feature as a single visible step on `main`.

**Your Task**
Commit `src/reports.py` on `feature/reports` with the message `Add monthly report`, then switch to `main` and merge `feature/reports` with a merge commit.

**Objective Checklist**

- [ ] feature/reports has the commit Add monthly report.
- [ ] main's latest commit is a merge that brings in the finished report.
- [ ] main is checked out, and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add src/reports.py` — Stage the finished report.
2. `git commit -m "Add monthly report"` — Commit it on the feature branch.
3. `git switch main` — Go to the target branch.
4. `git merge --no-ff feature/reports` — Land it with a merge commit.

**Accepted Alternatives (STAFF ONLY)**

- `git commit -am "Add monthly report"`; `git checkout main`; `git merge --no-ff --no-edit feature/reports`.
- Common patterns that apply: P23.

**Not accepted**

- A fast-forward merge, or merging before the report is committed.

**Expected Result**
`main` has a merge commit that brings in `feature/reports`, including the finished report.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- `feature/reports` tip `Add monthly report` (parent `c2`) with the finished report.
- HEAD on `main`; tip is a merge (parent `c1`) whose tree has the finished report; clean tree.

### 2.7.15 Finish the MFA prompt, then land it on develop · Medium

**Variant ID:** `merge-medium-commit-switch-noff-auth`

**Story**
Your multi-factor prompt in `src/mfa.py` works, but the final edits are uncommitted on `feature/mfa`. Finn wants it on `develop` for the security review, recorded as its own merge so the reviewers can find it in one place.

**Starting point:** You are on `feature/mfa`; `src/mfa.py` has finished, uncommitted edits; `develop` has not moved since the branch started.

**Real-World Context**
`--no-ff` keeps a merge commit even when Git could simply move the branch forward. Reviewers can then read the whole feature as one entry in the history.

**Your Task**
Commit `src/mfa.py` on `feature/mfa` with the message `Add MFA prompt`, then switch to `develop` and merge `feature/mfa` with a merge commit.

**Objective Checklist**

- [ ] feature/mfa has the commit Add MFA prompt.
- [ ] develop's latest commit is a merge that brings in the MFA prompt.
- [ ] develop is checked out, and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git add src/mfa.py` — Stage the finished prompt.
2. `git commit -m "Add MFA prompt"` — Commit it.
3. `git switch develop` — Go to the target branch.
4. `git merge --no-ff feature/mfa` — Land it with a merge commit.

**Accepted Alternatives (STAFF ONLY)**

- `git commit -am "Add MFA prompt"`; `git checkout develop`; `git merge --no-ff --no-edit feature/mfa`.
- Common patterns that apply: P23.

**Not accepted**

- A fast-forward, or merging the unfinished branch.

**Expected Result**
`develop` has a merge commit that brings in `feature/mfa`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- `feature/mfa` tip `Add MFA prompt` (parent `c2`) with the finished prompt.
- HEAD on `develop`; tip is a merge (parent `c1`) whose tree has the finished prompt; clean tree.

### 2.7.16 Land the search page, publish and tidy up · Hard

**Variant ID:** `merge-hard-land-publish-tidy-search`

**Story**
The search page on `feature/search` is committed and approved. Finn wants the whole ending done in one sitting: land it on `main` with a visible merge commit, put `main` on `origin` for the deploy, and remove your local branch, but __only in the safe way__ that refuses if anything were left unmerged.

**Starting point:** You are on `feature/search` with everything committed; `main` is behind it; `origin` is available.

**Real-World Context**
Landing a feature is a short sequence: merge, publish, tidy up. `git branch -d` checks that the work is merged before it deletes anything.

**Your Task**
Merge `feature/search` into `main` with a merge commit, push `main` to `origin`, and delete the local `feature/search` with the safe delete.

**Objective Checklist**

- [ ] main's latest commit is a merge that brings in the search page.
- [ ] origin/main matches your main.
- [ ] feature/search no longer exists locally.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Go to the target branch.
2. `git merge --no-ff feature/search` — Land it with a merge commit.
3. `git push origin main` — Publish main.
4. `git branch -d feature/search` — Delete the merged branch safely.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git push`; deleting the branch before the push.
- Common patterns that apply: P23, P30, P31.

**Not accepted**

- A fast-forward merge, leaving main unpublished, or keeping the branch.

**Expected Result**
`origin/main` has the merge of the search page, and `feature/search` is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge whose tree has the search page; `origin/main` = `main`.
- `feature/search` absent; clean tree.

### 2.7.17 Land the rounding hotfix on the release, publish and tidy up · Hard

**Variant ID:** `merge-hard-land-publish-tidy-billing`

**Story**
Customers on release 2 are seeing totals rounded the wrong way, and your fix on `hotfix/billing-rounding` is committed and tested. Sage needs it on `release/v2` as a visible merge, on `origin` before tonight's patch build, and the hotfix branch cleaned up afterwards.

**Starting point:** You are on `hotfix/billing-rounding` with everything committed; `release/v2` is behind it; `origin` is available.

**Real-World Context**
Hotfixes are short-lived: they land on the release branch, ship, and disappear. A visible merge commit lets the release notes point at exactly what changed.

**Your Task**
Merge `hotfix/billing-rounding` into `release/v2` with a merge commit, push `release/v2` to `origin`, and delete the local hotfix branch safely.

**Objective Checklist**

- [ ] release/v2's latest commit is a merge that brings in the fix.
- [ ] origin/release/v2 matches your release/v2.
- [ ] hotfix/billing-rounding no longer exists locally.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release/v2` — Go to the release branch.
2. `git merge --no-ff hotfix/billing-rounding` — Land the fix with a merge commit.
3. `git push origin release/v2` — Publish the release branch.
4. `git branch -d hotfix/billing-rounding` — Remove the merged hotfix branch.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout release/v2`; `git push`; deleting the branch before the push.
- Common patterns that apply: P23, P30, P31.

**Not accepted**

- A fast-forward, leaving release/v2 unpublished, or keeping the hotfix branch.

**Expected Result**
`origin/release/v2` has the merged fix, and the hotfix branch is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `release/v2`; tip is a merge whose tree has the fix; `origin/release/v2` = `release/v2`.
- `hotfix/billing-rounding` absent; clean tree.

### 2.8.14 Squash the onboarding flow and publish · Medium

**Variant ID:** `squash-medium-squash-publish-onboarding`

**Story**
The onboarding flow is done, but `feature/onboarding` tells the story of how it got there: four commits named WIP 1 to WIP 4. Finn wants `main` to show one commit, Add onboarding flow, and he wants it on `origin` before the marketing team starts testing tomorrow.

**Starting point:** You are on `main`; `feature/onboarding` has four draft commits; `origin` is available.

**Real-World Context**
A squash merge stages a branch's combined changes without its commit trail. You write one commit for the result, then publish it like any other.

**Your Task**
Bring `feature/onboarding` into `main` as one new commit with the message `Add onboarding flow`, then push `main` to `origin`.

**Objective Checklist**

- [ ] main has exactly one new commit, Add onboarding flow, with the finished flow.
- [ ] That commit is not a merge commit.
- [ ] origin/main matches your main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --squash feature/onboarding` — Stage the branch's combined changes.
2. `git commit -m "Add onboarding flow"` — Record them as one commit.
3. `git push origin main` — Publish main.

**Accepted Alternatives (STAFF ONLY)**

- `git merge feature/onboarding --squash`; `git push`.
- Not accepted: a normal merge or a fast-forward (they bring the four drafts).

**Not accepted**

- Any merge that brings the draft commits into main, or leaving main unpublished.

**Expected Result**
`main` and `origin/main` have one new commit, Add onboarding flow, containing the finished flow.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- `main` has 2 commits; tip `Add onboarding flow` (parent `c1`, not a merge) with the finished flow.
- `origin/main` = `main`; HEAD on `main`; clean tree.

### 2.8.15 Squash the CSV export and publish · Medium

**Variant ID:** `squash-medium-squash-publish-export`

**Story**
Sage's CSV export is ready on `feature/export-csv`, after three commits called WIP 1 to WIP 3. The billing team's rule is one commit per feature on `develop`. She asks you to land it as Add CSV export and push `develop` so the nightly build picks it up.

**Starting point:** You are on `develop`; `feature/export-csv` has three draft commits; `origin` is available.

**Real-World Context**
Squashing keeps a shared branch readable: each entry in its history is a finished change, not a step in somebody's afternoon.

**Your Task**
Bring `feature/export-csv` into `develop` as one new commit with the message `Add CSV export`, then push `develop` to `origin`.

**Objective Checklist**

- [ ] develop has exactly one new commit, Add CSV export, with the finished export.
- [ ] That commit is not a merge commit.
- [ ] origin/develop matches your develop.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --squash feature/export-csv` — Stage the combined changes.
2. `git commit -m "Add CSV export"` — Record one commit.
3. `git push origin develop` — Publish develop.

**Accepted Alternatives (STAFF ONLY)**

- `git merge feature/export-csv --squash`; `git push`.
- Not accepted: a normal or `--no-ff` merge.

**Not accepted**

- Any merge that brings the draft commits, or leaving develop unpublished.

**Expected Result**
`develop` and `origin/develop` have one new commit, Add CSV export.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- `develop` has 2 commits; tip `Add CSV export` (parent `c1`, not a merge) with the finished export.
- `origin/develop` = `develop`; HEAD on `develop`; clean tree.

### 2.8.16 Squash the CLI colours from their branch and clean up · Hard

**Variant ID:** `squash-hard-switch-squash-cleanup-cli`

**Story**
You are still on `feature/cli-colors`, where three draft commits add coloured output to the command-line tool. Finn approved it with one condition: `main` gets a single commit, Add CLI colors, and the feature branch disappears afterwards.

Because a squash does not record the branch as merged, Git will treat removing it as throwing away unmerged work, so you will have to *insist*.

**Starting point:** You are on `feature/cli-colors`; it has three draft commits that are not on `main`.

**Real-World Context**
After a squash merge, Git does not know the branch's work has landed. Deleting the branch then needs the forced delete, used deliberately once the squashed commit is safely in place.

**Your Task**
Switch to `main`, bring `feature/cli-colors` in as one commit with the message `Add CLI colors`, then delete the local feature branch.

**Objective Checklist**

- [ ] main has exactly one new commit, Add CLI colors, and it is not a merge commit.
- [ ] feature/cli-colors no longer exists.
- [ ] main is checked out, and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Go to the target branch.
2. `git merge --squash feature/cli-colors` — Stage the combined changes.
3. `git commit -m "Add CLI colors"` — Record one commit.
4. `git branch -D feature/cli-colors` — Remove the squashed branch on purpose.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git branch --delete --force feature/cli-colors`.
- `git branch -d` is refused by Git here; show that message and nudge toward the forced delete.
- Common patterns that apply: P23, P36.

**Not accepted**

- A normal merge or fast-forward, or keeping the branch.

**Expected Result**
`main` has one new commit, Add CLI colors, and `feature/cli-colors` is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `main` has 2 commits; tip `Add CLI colors` (parent `c1`, not a merge) with the finished colours.
- `feature/cli-colors` absent; HEAD on `main`; clean tree.

### 2.8.17 Squash the toast notifications onto develop and clean up · Hard

**Variant ID:** `squash-hard-switch-squash-cleanup-ui`

**Story**
Three draft commits on `feature/toast-ui` add toast notifications to the web app. Sage wants them on `develop` as one commit, Add toast notifications, and no local feature branch left behind. You are still on the feature branch.

**Starting point:** You are on `feature/toast-ui`; it has three draft commits that are not on `develop`.

**Real-World Context**
Squashing and then force-deleting is a common ending for short-lived branches whose drafts nobody needs to keep.

**Your Task**
Switch to `develop`, bring `feature/toast-ui` in as one commit with the message `Add toast notifications`, then delete the local feature branch.

**Objective Checklist**

- [ ] develop has exactly one new commit, Add toast notifications, and it is not a merge commit.
- [ ] feature/toast-ui no longer exists.
- [ ] develop is checked out, and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch develop` — Go to the target branch.
2. `git merge --squash feature/toast-ui` — Stage the combined changes.
3. `git commit -m "Add toast notifications"` — Record one commit.
4. `git branch -D feature/toast-ui` — Remove the squashed branch.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout develop`; `git branch --delete --force feature/toast-ui`.
- Common patterns that apply: P23, P36.

**Not accepted**

- Squashing in the wrong direction (develop into the feature branch), a normal merge, or keeping the branch.

**Expected Result**
`develop` has one new commit, Add toast notifications, and `feature/toast-ui` is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `develop` has 2 commits; tip `Add toast notifications` (parent `c1`, not a merge) with the finished toasts.
- `feature/toast-ui` absent; HEAD on `develop`; clean tree.

### 2.8.18 Squash the teammate's search branch and tidy up · Hard

**Variant ID:** `squash-hard-remote-publish-tidy-search`

**Story**
Mika finished the search feature on `origin/feature/search` in a string of WIP commits. The team wants it on `main` as one commit, "Add search", published to `origin`. Your own local `feature/search` is an old copy that nobody needs any more.

**Starting point:** You are on `main`. Your local `feature/search` is behind `origin/feature/search`, and you haven't fetched Mika's latest commits.

**Real-World Context**
Squashing a teammate's branch gives main one clean commit. A stale local copy of that branch then has to go with `-D`, because Git never sees it as merged.

**Your Task**
Bring the latest `origin/feature/search` into `main` as one new commit with the message `Add search`, push `main` to `origin`, and delete your local `feature/search`.

**Objective Checklist**

- [ ] main has one new non-merge commit "Add search" with the finished feature.
- [ ] origin/main matches main.
- [ ] No local feature/search branch is left.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git fetch origin` — Download Mika's latest commits.
2. `git merge --squash origin/feature/search` — Stage the whole feature as one change.
3. `git commit -m "Add search"` — Record it.
4. `git push origin main` — Publish main.
5. `git branch -D feature/search` — Remove the stale local copy.

**Accepted Alternatives (STAFF ONLY)**

- Deleting the local branch before pushing.

**Not accepted**

- A regular merge, or squashing the stale local branch instead of the fetched one.

**Expected Result**
`main` has one "Add search" commit on `origin` too, and the stale branch is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Tip "Add search" with parent c1 and the finished file; two commits on main; origin matches; feature/search absent.

### 2.8.19 Squash the teammate's API docs and tidy up · Hard

**Variant ID:** `squash-hard-remote-publish-tidy-docs`

**Story**
Ana wrote the API docs on `origin/docs/api` in many small commits. They should land on `main` as a single commit, "Document the API", and be published. Your local `docs/api` is an outdated copy from last week.

**Starting point:** You are on `main`. Your local `docs/api` is behind `origin/docs/api`, and you haven't fetched Ana's latest commits.

**Real-World Context**
A squash keeps the main history readable. Fetching first makes sure you squash the teammate's latest work, not your stale copy.

**Your Task**
Bring the latest `origin/docs/api` into `main` as one new commit with the message `Document the API`, push `main` to `origin`, and delete your local `docs/api`.

**Objective Checklist**

- [ ] main has one new non-merge commit "Document the API" with the finished docs.
- [ ] origin/main matches main.
- [ ] No local docs/api branch is left.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git fetch origin` — Download Ana's latest commits.
2. `git merge --squash origin/docs/api` — Stage the whole branch as one change.
3. `git commit -m "Document the API"` — Record it.
4. `git push origin main` — Publish main.
5. `git branch -D docs/api` — Remove the stale local copy.

**Accepted Alternatives (STAFF ONLY)**

- Deleting the local branch before pushing.

**Not accepted**

- A regular merge, or squashing the stale local branch instead of the fetched one.

**Expected Result**
`main` has one "Document the API" commit on `origin` too, and the stale branch is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Tip "Document the API" with parent c1 and the finished file; two commits on main; origin matches; docs/api absent.

### 2.9.14 Land the search page and retire its remote branch · Medium

**Variant ID:** `rb-medium-land-and-retire-search`

**Story**
`feature/search` is finished and approved, and both you and `origin` have a copy of it. Finn wants it landed on `main` with a merge commit and `main` published. The remote branch has done its job and should go, but keep your local copy for now: you still want to compare it with the next iteration.

**Starting point:** You are on `main`; `feature/search` is finished locally and on `origin`; `origin/main` matches `main`.

**Real-World Context**
Deleting a branch on the remote does not touch your local branch. Teams usually retire the remote copy once its work is merged and published.

**Your Task**
Merge `feature/search` into `main` with a merge commit, push `main` to `origin`, then delete `feature/search` on `origin`. **Keep the local branch.**

**Objective Checklist**

- [ ] main's latest commit is a merge that brings in the search page.
- [ ] origin/main matches your main.
- [ ] origin no longer has feature/search; your local feature/search still exists.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --no-ff feature/search` — Land it with a merge commit.
2. `git push origin main` — Publish main.
3. `git push origin --delete feature/search` — Retire the remote branch.

**Accepted Alternatives (STAFF ONLY)**

- `git push`; `git push -d origin feature/search`; `git push origin :feature/search`; deleting the remote branch before the main push.
- Common patterns that apply: P31.

**Not accepted**

- A fast-forward merge, deleting the local branch instead of the remote one, or leaving main unpublished.

**Expected Result**
`origin/main` has the merge of the search page, `origin`'s `feature/search` is gone, and your local copy remains.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `main`; tip is a merge whose tree has the search page; `origin/main` = `main`.
- `origin/feature/search` absent; local `feature/search` exists; clean tree.

### 2.9.15 Land the billing summary and retire its remote branch · Medium

**Variant ID:** `rb-medium-land-and-retire-billing`

**Story**
Sage approved the billing summary on `feature/billing`. The release checklist says: merge with a merge commit, publish `main`, and delete the feature branch on `origin` so the branch list on the server only shows open work. You still need your local copy to write the release notes.

**Starting point:** You are on `main`; `feature/billing` is finished locally and on `origin`; `origin/main` matches `main`.

**Real-World Context**
Cleaning up remote branches after a merge keeps the shared branch list short. Local branches are yours to keep or remove separately.

**Your Task**
Merge `feature/billing` into `main` with a merge commit, push `main` to `origin`, then delete `feature/billing` on `origin`. **Keep the local branch.**

**Objective Checklist**

- [ ] main's latest commit is a merge that brings in the billing summary.
- [ ] origin/main matches your main.
- [ ] origin no longer has feature/billing; your local feature/billing still exists.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --no-ff feature/billing` — Land it with a merge commit.
2. `git push origin main` — Publish main.
3. `git push origin --delete feature/billing` — Retire the remote branch.

**Accepted Alternatives (STAFF ONLY)**

- `git push`; `git push -d origin feature/billing`; `git push origin :feature/billing`.
- Common patterns that apply: P31.

**Not accepted**

- A fast-forward, deleting only the local branch, or leaving main unpublished.

**Expected Result**
`origin/main` has the merged billing summary, `origin`'s `feature/billing` is gone, and your local copy remains.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `main`; tip is a merge whose tree has the billing summary; `origin/main` = `main`.
- `origin/feature/billing` absent; local `feature/billing` exists; clean tree.

### 2.9.16 Release notes: fetch, land, publish, retire, prune · Hard

**Variant ID:** `rb-hard-capstone-release-notes`

**Story**
Raven finished the release notes on `feature/release-notes` and pushed her final commits after your last fetch, so your copy of `origin/feature/release-notes` still shows her draft.

She is off for the week and asks you to finish the job: land her branch on `main` with a merge commit, publish `main`, delete her branch on `origin`, and clean your stale remote-tracking refs.

Someone already deleted `feature/old-banner` on `origin`, but your list still shows it.

**Starting point:** You are on `main`; `origin/feature/release-notes` in your copy is out of date; `origin/feature/old-banner` was deleted on the server but still appears locally.

**Real-World Context**
Remote-tracking refs are only as fresh as your last fetch. Fetching first makes sure you land what was actually pushed, and pruning removes refs to branches the server no longer has.

**Your Task**
Fetch from `origin`, merge `origin/feature/release-notes` into `main` with a merge commit, push `main` to `origin`, delete `feature/release-notes` on `origin`, and prune stale remote-tracking refs.

**Objective Checklist**

- [ ] main's latest commit is a merge that brings in Raven's final release notes.
- [ ] origin/main matches your main.
- [ ] origin/feature/release-notes and origin/feature/old-banner are gone from your remote-tracking refs.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git fetch origin` — See Raven's final commits.
2. `git merge --no-ff origin/feature/release-notes` — Land them with a merge commit.
3. `git push origin main` — Publish main.
4. `git push origin --delete feature/release-notes` — Retire her branch on origin.
5. `git fetch --prune origin` — Drop the stale old-banner ref.

**Accepted Alternatives (STAFF ONLY)**

- `git fetch --prune origin` as the first step, replacing both fetches; `git push -d origin feature/release-notes`; `git push`.
- Common patterns that apply: P2, P31, P37.

**Not accepted**

- Merging before fetching (it lands the draft), a fast-forward, or leaving the stale ref.

**Expected Result**
`origin/main` has a merge of the final release notes, and neither retired branch appears in your remote-tracking refs.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge whose tree has the final release notes; `origin/main` = `main`.
- `origin/feature/release-notes` and `origin/feature/old-banner` absent; clean tree.

### 2.9.17 Payments v2: fetch, land, publish, retire, prune · Hard

**Variant ID:** `rb-hard-capstone-payments`

**Story**
Finn's team finished payments v2 on `feature/payments-v2` and pushed the last fixes this morning. Your copy of `origin/feature/payments-v2` is from yesterday.

Finn asks you to ship it: land it on `main` with a merge commit, publish `main`, retire the branch on `origin`, and clean up your remote-tracking refs, which still list `feature/legacy-checkout` even though `origin` removed it last week.

**Starting point:** You are on `main`; `origin/feature/payments-v2` in your copy is out of date; `origin/feature/legacy-checkout` was deleted on the server but still appears locally.

**Real-World Context**
Shipping a teammate's branch is the whole module in one go: refresh your view, integrate, publish, and leave the shared branch list clean.

**Your Task**
Fetch from `origin`, merge `origin/feature/payments-v2` into `main` with a merge commit, push `main` to `origin`, delete `feature/payments-v2` on `origin`, and prune stale remote-tracking refs.

**Objective Checklist**

- [ ] main's latest commit is a merge that brings in the final payments work.
- [ ] origin/main matches your main.
- [ ] origin/feature/payments-v2 and origin/feature/legacy-checkout are gone from your remote-tracking refs.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git fetch origin` — Get this morning's fixes.
2. `git merge --no-ff origin/feature/payments-v2` — Land them with a merge commit.
3. `git push origin main` — Publish main.
4. `git push origin --delete feature/payments-v2` — Retire the branch on origin.
5. `git fetch --prune origin` — Drop the stale legacy-checkout ref.

**Accepted Alternatives (STAFF ONLY)**

- `git fetch --prune origin` as the first step, replacing both fetches; `git push -d origin feature/payments-v2`.
- Common patterns that apply: P2, P31, P37.

**Not accepted**

- Merging yesterday's copy, a fast-forward, or leaving the stale ref.

**Expected Result**
`origin/main` has a merge of the final payments work, and neither retired branch appears in your remote-tracking refs.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge whose tree has the final payments work; `origin/main` = `main`.
- `origin/feature/payments-v2` and `origin/feature/legacy-checkout` absent; clean tree.

### 2.9.18 Retire the old FAQ branch and prune the leftovers · Easy

**Variant ID:** `rb-easy-delete-then-prune-docs`

**Story**
The old FAQ pages are merged, so `docs/old-faq` can go from `origin`. While you're tidying, Sage mentions she already deleted `feature/old-banner` on the server. Your copy still lists it.

**Starting point:** You are on `main`. `origin` still has `docs/old-faq`. Your copy also lists `origin/feature/old-banner`, which no longer exists on the server.

**Real-World Context**
Deleting your own remote branches and pruning branches teammates removed are two halves of the same tidy-up.

**Your Task**
Delete `docs/old-faq` from `origin`, then remove the stale `origin/feature/old-banner` record from your copy.

**Objective Checklist**

- [ ] docs/old-faq no longer exists on origin.
- [ ] origin/feature/old-banner is gone from your copy.
- [ ] main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git push origin --delete docs/old-faq` — Delete the branch on origin.
2. `git fetch --prune origin` — Drop the stale remote-tracking record.

**Accepted Alternatives (STAFF ONLY)**

- `git push origin :docs/old-faq`; `git remote prune origin`.

**Not accepted**

- Leaving either remote-tracking branch behind.

**Expected Result**
Neither `origin/docs/old-faq` nor `origin/feature/old-banner` is listed any more.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- Both remote-tracking branches absent; main at c1; working tree clean.

### 2.9.19 Retire the v1 API branch and prune the leftovers · Easy

**Variant ID:** `rb-easy-delete-then-prune-api`

**Story**
The v1 API work is merged, so `feature/v1-api` can go from `origin`. Finn already removed `spike/graphql` on the server last week, but your copy still shows it.

**Starting point:** You are on `main`. `origin` still has `feature/v1-api`. Your copy also lists `origin/spike/graphql`, which no longer exists on the server.

**Real-World Context**
After a release, teams clear finished branches on the server and prune the stale records everyone's copies still show.

**Your Task**
Delete `feature/v1-api` from `origin`, then remove the stale `origin/spike/graphql` record from your copy.

**Objective Checklist**

- [ ] feature/v1-api no longer exists on origin.
- [ ] origin/spike/graphql is gone from your copy.
- [ ] main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git push origin --delete feature/v1-api` — Delete the branch on origin.
2. `git fetch --prune origin` — Drop the stale remote-tracking record.

**Accepted Alternatives (STAFF ONLY)**

- `git push origin :feature/v1-api`; `git remote prune origin`.

**Not accepted**

- Leaving either remote-tracking branch behind.

**Expected Result**
Neither `origin/feature/v1-api` nor `origin/spike/graphql` is listed any more.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- Both remote-tracking branches absent; main at c1; working tree clean.

## Module 3 — Conflict Resolution

### 3.1.13 Back out of the legacy theme merge · Easy

**Variant ID:** `manual-easy-abort-wrong-branch`

**Story**
You meant to merge the new colour theme into `main`, but you typed `feature/legacy-theme`, the branch the group retired last month. Git stopped on a conflict in `src/theme.css`, and nothing has been committed yet.

Sage says not to fix anything in this merge at all: just get `main` back exactly as it was before you started.

**Starting point:** You are on `main`, in the middle of a merge of `feature/legacy-theme` that stopped on a conflict in `src/theme.css`.

**Real-World Context**
A merge that stops on a conflict can be undone completely. Aborting puts the branch, the staging area and the working folder back to how they were before the merge began.

**Your Task**
Cancel the merge so `main` is __exactly__ as it was before.

**Objective Checklist**

- [ ] No merge is in progress and no conflicts remain.
- [ ] main still points at its previous commit.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --abort` — Abandon the merge and restore the pre-merge state.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --merge`.
- Common patterns that apply: P15.

**Not accepted**

- Resolving the conflict and committing the legacy merge.

**Expected Result**
`main` is back to its pre-merge commit, with no conflict and nothing staged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `main` at `c1`; `feature/legacy-theme` at `c2`.
- No conflicts; clean tree, nothing staged.

### 3.1.14 Back out of the payments merge until review ends · Easy

**Variant ID:** `manual-easy-abort-too-early`

**Story**
You started merging `feature/payments` into `main`, and Git stopped on a conflict in `src/payments.py`.

Then Finn messaged: the payments review is not finished, and the currency change on that branch might still be rejected. The merge should not exist yet. You want `main` back to how it was, with no half-merged files lying around.

**Starting point:** You are on `main`, in the middle of a merge of `feature/payments` that stopped on a conflict in `src/payments.py`.

**Real-World Context**
Stopping a merge halfway is normal. Abort when the merge itself was the wrong move; resolve when it was the right one.

**Your Task**
Cancel the merge so `main` is __exactly__ as it was before.

**Objective Checklist**

- [ ] No merge is in progress and no conflicts remain.
- [ ] main still points at its previous commit.
- [ ] The working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --abort` — Abandon the merge.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --merge`.
- Common patterns that apply: P15.

**Not accepted**

- Committing the merge with either side of the conflict.

**Expected Result**
`main` is unchanged, and `feature/payments` waits for its review.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `main` at `c1`; `feature/payments` at `c2`.
- No conflicts; clean tree, nothing staged.

### 3.1.15 A pull that conflicts in the README · Medium

**Variant ID:** `manual-medium-pull-conflict-readme`

**Story**
You committed a change to `README.md` telling people to start the field notes app with `npm run dev`. Meanwhile Raven pushed her own edit to the same line on `origin/main`, adding a port flag. Your next pull will stop on that line.

Raven and you agree on the final wording below: your command with her port.

**Starting point:** You are on `main` with one local commit to `README.md`; `origin/main` has a new commit that changed the same line.

**Real-World Context**
A pull is a fetch followed by a merge, so it can stop on a conflict like any merge. You resolve it, finish the merge commit, and then publish the combined result.

**Your Task**
Pull `origin/main` into `main`, resolve `README.md` to the content below, complete the merge with its prepared message, and push `main` to `origin`.

**Required resolved file content**

`README.md`

```
Run the app with: npm run dev -- --port 3000
```

**Objective Checklist**

- [ ] main has a merge commit that includes Raven's commit.
- [ ] README.md contains exactly the required content.
- [ ] origin/main matches your main, and no conflicts remain.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin main` — Fetch and merge; it stops on the conflict.
2. In the simulator's file editor, set `README.md` to exactly:

   ```
   Run the app with: npm run dev -- --port 3000
   ```
3. `git add README.md` — Mark the file resolved.
4. `git commit --no-edit` — Complete the merge.
5. `git push origin main` — Publish main.

**Accepted Alternatives (STAFF ONLY)**

- `git fetch origin` then `git merge origin/main`; `git merge --continue`; `git push`.
- Common patterns that apply: P2, P15, P16, P17, P18, P41.

**Not accepted**

- Aborting the pull, pushing before the merge is complete, or `git pull --rebase`.

**Expected Result**
`origin/main` has a merge commit joining both edits, with the agreed README line.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `main`; tip is a merge with parent `c2`; tree `README.md` = the required content.
- `origin/main` = `main`; no conflicts; clean tree.

### 3.1.16 A pull that conflicts in the app config · Medium

**Variant ID:** `manual-medium-pull-conflict-config`

**Story**
On `develop` you raised the ticketing app's request timeout in `config/app.yml` and committed it. Finn, at the same time, pushed a change to the same file on `origin/develop` that raises the retry count.

Both changes are wanted. Pulling will stop on the conflict, and the final file must contain your timeout and his retries.

**Starting point:** You are on `develop` with one local commit to `config/app.yml`; `origin/develop` has a new commit that changed the same lines.

**Real-World Context**
Conflicts are decisions, not errors. Here both sides are right, so the resolution keeps a piece of each.

**Your Task**
Pull `origin/develop` into `develop`, resolve `config/app.yml` to the content below, complete the merge with its prepared message, and push `develop` to `origin`.

**Required resolved file content**

`config/app.yml`

```
timeout: 45
retries: 3
```

**Objective Checklist**

- [ ] develop has a merge commit that includes Finn's commit.
- [ ] config/app.yml contains exactly the required content.
- [ ] origin/develop matches your develop, and no conflicts remain.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin develop` — Fetch and merge; it stops on the conflict.
2. In the simulator's file editor, set `config/app.yml` to exactly:

   ```
   timeout: 45
   retries: 3
   ```
3. `git add config/app.yml` — Mark the file resolved.
4. `git commit --no-edit` — Complete the merge.
5. `git push origin develop` — Publish develop.

**Accepted Alternatives (STAFF ONLY)**

- `git fetch origin` then `git merge origin/develop`; `git merge --continue`; `git push`.
- Common patterns that apply: P2, P15, P16, P17, P18, P41.

**Not accepted**

- Keeping only one side, pushing before the merge is complete, or `git pull --rebase`.

**Expected Result**
`origin/develop` has a merge commit with your timeout and Finn's retries.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `develop`; tip is a merge with parent `c2`; tree `config/app.yml` = the required content.
- `origin/develop` = `develop`; no conflicts; clean tree.

### 3.1.17 Abort the v1 payments merge and merge v2 · Hard

**Variant ID:** `manual-hard-abort-redo-payments`

**Story**
You started merging `feature/payments-v1` into `main` and Git stopped on a conflict in `src/payments.py`.

Then Sage reminded you that v1 was replaced: the branch to merge is `feature/payments-v2`, which keeps the old fee and adds a transaction cap. `main`'s own fee change must survive. **The wrong merge must leave no trace on `main`.**

**Starting point:** You are on `main`, in the middle of a merge of `feature/payments-v1` that stopped on a conflict in `src/payments.py`; `feature/payments-v2` is the branch you meant.

**Real-World Context**
When a merge was the wrong one, abort it before doing the right one. Resolving the wrong merge would tie its history into `main` for good.

**Your Task**
Cancel the current merge, merge `feature/payments-v2` instead, resolve `src/payments.py` to the content below, and complete the merge with its prepared message.

**Required resolved file content**

`src/payments.py`

```
FEE = 0.025
CAP = 500
```

**Objective Checklist**

- [ ] main has a merge commit with feature/payments-v2 as a parent.
- [ ] feature/payments-v1's commit is not in main's history.
- [ ] src/payments.py contains exactly the required content, and no conflicts remain.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --abort` — Abandon the v1 merge.
2. `git merge feature/payments-v2` — Merge the right branch; it stops on the conflict.
3. In the simulator's file editor, set `src/payments.py` to exactly:

   ```
   FEE = 0.025
   CAP = 500
   ```
4. `git add src/payments.py` — Mark the file resolved.
5. `git commit --no-edit` — Complete the merge.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --merge` for the abort; `git merge --continue`.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- Resolving and committing the v1 merge, or merging both branches.

**Expected Result**
`main` has a merge of `feature/payments-v2` with the agreed fee and cap, and v1 never reached `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge with parent `c3`; `c2` not in main's history; tree `src/payments.py` = the required content.
- No conflicts; clean tree.

### 3.2.14 Set up the team's merge tool, then merge · Medium

**Variant ID:** `mergetool-medium-configure-tool-billing`

**Story**
Maeve's billing team resolves every conflict in `meld`, and their checklist starts with configuring it in each new clone. Yours has no merge tool set yet.

You are about to merge `feature/billing-copy` into `main`, and it will conflict in `src/billing_copy.txt`, the text of the invoice email. The agreed wording is below.

**Starting point:** You are on `main`; no merge tool is configured; merging `feature/billing-copy` will conflict in `src/billing_copy.txt`.

**Real-World Context**
`git config merge.tool` tells `git mergetool` which program to open. Setting it once per repository means every later conflict opens in the team's tool.

**Your Task**
Configure `meld` as this repository's merge tool, merge `feature/billing-copy`, resolve `src/billing_copy.txt` in the merge tool to the content below, and complete the merge with its prepared message.

**Required resolved file content**

`src/billing_copy.txt`

```
Your monthly invoice is ready.
```

**Objective Checklist**

- [ ] The repository's merge tool is meld.
- [ ] main has a merge commit with feature/billing-copy as a parent.
- [ ] src/billing_copy.txt contains exactly the required content.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git config merge.tool meld` — Set the team's merge tool.
2. `git merge feature/billing-copy` — Start the merge; it stops on the conflict.
3. `git mergetool` — Open the conflict in meld.
4. In the simulator's merge tool, set `src/billing_copy.txt` to exactly:

   ```
   Your monthly invoice is ready.
   ```
5. `git commit --no-edit` — Complete the merge.

**Accepted Alternatives (STAFF ONLY)**

- Configuring the tool after the merge stops; `git mergetool --tool=meld` after setting it; `git merge --continue`.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Not accepted**

- Leaving the tool unconfigured. (Resolving the file in the editor instead of the tool completes it: same end state.)

**Expected Result**
`meld` is the repository's merge tool, and `main` has a merge commit with the agreed email text.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- `merge.tool` = `meld`.
- HEAD on `main`; tip is a merge with parent `c2`; tree `src/billing_copy.txt` = the required content; clean tree.

### 3.2.15 Merge the API version without backup files · Hard

**Variant ID:** `mergetool-hard-no-backup-api`

**Story**
Last time you used the merge tool, it left `src/api_version.py.orig` files behind, and one of them nearly got committed.

Sage asks you to turn those backups off for this repository before you merge `feature/api-v3`, which will conflict in `src/api_version.py`. `meld` is already the configured tool. The final file keeps the new version and remembers the old one.

**Starting point:** You are on `main`; `meld` is the configured merge tool, but it still keeps backup copies; merging `feature/api-v3` will conflict in `src/api_version.py`.

**Real-World Context**
Merge tools can save the conflicted original next to the file. Setting `mergetool.keepBackup` to false stops those copies from cluttering the folder or slipping into a commit.

**Your Task**
Turn off the merge tool's backup files for this repository, merge `feature/api-v3`, resolve `src/api_version.py` in the merge tool to the content below, and complete the merge with its prepared message.

**Required resolved file content**

`src/api_version.py`

```
API_VERSION = '3.0'
LEGACY_VERSION = '2.4'
```

**Objective Checklist**

- [ ] mergetool.keepBackup is false, and meld is still the merge tool.
- [ ] main has a merge commit with feature/api-v3 as a parent.
- [ ] src/api_version.py contains exactly the required content, and no backup files are left.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git config mergetool.keepBackup false` — Stop the tool from keeping backups.
2. `git merge feature/api-v3` — Start the merge; it stops on the conflict.
3. `git mergetool` — Open the conflict in meld.
4. In the simulator's merge tool, set `src/api_version.py` to exactly:

   ```
   API_VERSION = '3.0'
   LEGACY_VERSION = '2.4'
   ```
5. `git commit --no-edit` — Complete the merge.

**Accepted Alternatives (STAFF ONLY)**

- Setting the option after the merge stops but before `git mergetool`; `git merge --continue`.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Not accepted**

- Leaving backups switched on.

**Expected Result**
Backups are off, and `main` has a merge commit with the agreed version lines.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `mergetool.keepBackup` = `false`, `merge.tool` = `meld`.
- HEAD on `main`; tip is a merge with parent `c2`; tree `src/api_version.py` = the required content; clean tree.

### 3.3.14 Backport the retry fix and note its source · Easy

**Variant ID:** `cherry-easy-trace-source-hotfix`

**Story**
Customers on release 2.4 are being charged twice when a payment retries. Finn already fixed it on `main` in `c2`, Stop double-charging retries, but `main` also has groundwork that must not ship in 2.4.

The release team audits every backport, so the copied commit's message has to say where it came from.

**Starting point:** You are on `release-2.4`; `c2` on `main` is the fix.

**Real-World Context**
`git cherry-pick -x` appends "(cherry picked from commit …)" to the new commit's message, so anyone reading the release history can find the original change.

**Your Task**
Apply `c2` to `release-2.4` as a new commit whose message records the commit it came from. **Do not bring over any other `main` commits.**

**Objective Checklist**

- [ ] release-2.4 has one new commit with the retry fix.
- [ ] Its message includes "cherry picked from commit c2".
- [ ] main's groundwork did not come along, and main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick -x c2` — Copy the fix and record its source.

**Accepted Alternatives (STAFF ONLY)**

- `git log main` or `git show c2` first.
- Common patterns that apply: P25.

**Not accepted**

- A cherry-pick without `-x`, or merging main.

**Expected Result**
`release-2.4` has the retry fix, and its message points back to `c2`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `release-2.4`; tip (parent `c3`) message contains the fix and `cherry picked from commit c2`; tree has the fix but not main's report change.
- `main` at `c2`; clean tree.

### 3.3.15 Resolve and continue the lockout backport · Medium

**Variant ID:** `cherry-medium-conflict-continue-auth`

**Story**
Release 1.9 needs the account lockout fix from `main`, `c1`, Lock accounts after five failures. The release branch added failure logging to the same file since then, so the pick will stop on a conflict in `src/auth.py`.

Sage wants both: the lockout limit and the logging. The final file is below.

**Starting point:** You are on `release-1.9`; cherry-picking `c1` will stop on a conflict in `src/auth.py`.

**Real-World Context**
A cherry-pick can conflict just like a merge. After resolving and staging the file, `git cherry-pick --continue` creates the copied commit with its original message.

**Your Task**
Cherry-pick `c1` onto `release-1.9`, resolve `src/auth.py` to the content below, and finish the cherry-pick.

**Required resolved file content**

`src/auth.py`

```
MAX_FAILURES = 5
LOG_FAILURES = True
```

**Objective Checklist**

- [ ] release-1.9 has one new commit with the lockout fix's message.
- [ ] src/auth.py contains exactly the required content.
- [ ] No cherry-pick is in progress and no conflicts remain.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick c1` — Start the pick; it stops on the conflict.
2. In the simulator's file editor, set `src/auth.py` to exactly:

   ```
   MAX_FAILURES = 5
   LOG_FAILURES = True
   ```
3. `git add src/auth.py` — Mark the file resolved.
4. `git cherry-pick --continue` — Create the copied commit.

**Accepted Alternatives (STAFF ONLY)**

- `git commit --no-edit` instead of `--continue` (same commit).
- Common patterns that apply: P25.

**Not accepted**

- Aborting the pick, or committing with conflict markers left in the file.

**Expected Result**
`release-1.9` has the lockout fix on top of its logging, with no pick in progress.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `release-1.9`; tip (parent `c3`) message contains the fix; tree `src/auth.py` = the required content.
- No cherry-pick in progress; no conflicts; clean tree.

### 3.3.16 Cancel the stopped cart backport · Medium

**Variant ID:** `cherry-medium-abort-stopped-pick`

**Story**
You were backporting the cart tax fix to `release-review-2`, and the pick stopped on a conflict in `src/cart.py`. Part of the fix, the totals change, is already staged.

Then Maeve tells you the review build must keep its own tax rate: the backport is off. Release-review-2 has to look exactly as it did before you started.

**Starting point:** You are on `release-review-2` in the middle of a cherry-pick of `c1` that stopped on a conflict in `src/cart.py`; `src/totals.py` is already staged from the pick.

**Real-World Context**
`git cherry-pick --abort` undoes a stopped pick completely, including anything it had already staged.

**Your Task**
Cancel the cherry-pick so `release-review-2` is __exactly__ as it was before.

**Objective Checklist**

- [ ] No cherry-pick is in progress and no conflicts remain.
- [ ] release-review-2 still points at its previous commit.
- [ ] Nothing is staged, and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick --abort` — Undo the stopped pick.

**Accepted Alternatives (STAFF ONLY)**

- `git cherry-pick --quit` followed by `git reset --hard` (same end state, more steps).
- Common patterns that apply: P25.

**Not accepted**

- Resolving and continuing the pick, or committing the staged totals change.

**Expected Result**
`release-review-2` is unchanged, with no pick in progress and nothing staged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 10

- HEAD on `release-review-2` at `c3`; no cherry-pick in progress.
- No conflicts; clean tree, nothing staged.

### 3.3.17 Two login fixes, one reviewed backport · Medium

**Variant ID:** `cherry-medium-two-fixes-one-commit-login`

**Story**
Release 1.2 needs two fixes from `main`: `c2` fixes the login form and `c3` fixes session handling. Finn reviews backports as a unit, so he wants them on `release-1.2` as one commit, Backport login fixes, *not two*.

The other commits on `main` are a new feature that must stay out of the release.

**Starting point:** You are on `release-1.2`; `c2` and `c3` on `main` are the two login fixes.

**Real-World Context**
`git cherry-pick --no-commit` applies a commit's changes without committing them. Picking several that way and committing once gives reviewers a single change to check.

**Your Task**
Apply `c2` and `c3` to `release-1.2` without committing either, then commit them together with the message `Backport login fixes`.

**Objective Checklist**

- [ ] release-1.2 has exactly one new commit, Backport login fixes.
- [ ] It contains both fixes and none of main's feature work.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick --no-commit c2` — Stage the first fix.
2. `git cherry-pick --no-commit c3` — Stage the second fix on top.
3. `git commit -m "Backport login fixes"` — Commit both as one.

**Accepted Alternatives (STAFF ONLY)**

- `git cherry-pick -n c2`, `git cherry-pick -n c3`; `git cherry-pick --no-commit c2 c3`.
- Common patterns that apply: P25.

**Not accepted**

- Two separate cherry-pick commits, or merging main.

**Expected Result**
`release-1.2` has one new commit with both login fixes.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `release-1.2`, 3 commits; tip `Backport login fixes` (parent `c5`) with both fixes and main's feature file at its release version.
- Clean tree, nothing staged.

### 3.3.18 Two tax fixes, one reviewed backport · Medium

**Variant ID:** `cherry-medium-two-fixes-one-commit-tax`

**Story**
Two tax fixes landed on `main` weeks apart: `c1` corrects the tax rate and `c4` fixes how invoices show it. Release 3.1 needs both, in a single commit, Backport tax fixes, so the finance reviewer can approve one change. The commits between them are an unfinished feature that must not ship.

**Starting point:** You are on `release-3.1`; `c1` and `c4` on `main` are the two tax fixes.

**Real-World Context**
Cherry-picking is selective: you choose exactly which commits travel. Picking without committing lets you package them as one.

**Your Task**
Apply `c1` and `c4` to `release-3.1` without committing either, then commit them together with the message `Backport tax fixes`.

**Objective Checklist**

- [ ] release-3.1 has exactly one new commit, Backport tax fixes.
- [ ] It contains both fixes and none of the unfinished feature.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick --no-commit c1` — Stage the first fix.
2. `git cherry-pick --no-commit c4` — Stage the second fix on top.
3. `git commit -m "Backport tax fixes"` — Commit both as one.

**Accepted Alternatives (STAFF ONLY)**

- `-n` for `--no-commit`; picking c4 before c1.
- Common patterns that apply: P25.

**Not accepted**

- Two separate commits, or picking the feature commits in between.

**Expected Result**
`release-3.1` has one new commit with both tax fixes.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `release-3.1`, 3 commits; tip `Backport tax fixes` (parent `c5`) with both fixes and the feature file at its release version.
- Clean tree, nothing staged.

### 3.3.19 Backport the session fix to both releases · Hard

**Variant ID:** `cherry-hard-two-releases-security`

**Story**
`c3` on `main`, Expire sessions on password change, closes a security hole that both supported releases have. Sage wants it on `release-2.1` and `release-2.0` today, as a separate copy on each, and the `release-2.0` build runs right after, so finish there. **Nothing else from `main` may travel.**

**Starting point:** You are on `main`; `c3` is the security fix; `release-2.1` and `release-2.0` both need it.

**Real-World Context**
Supported releases are separate lines of history, so a fix is copied to each one. Each copy is a new commit with the same change.

**Your Task**
Apply `c3` to `release-2.1` and to `release-2.0`, each as a new commit. Finish on `release-2.0` and leave `main` unchanged.

**Objective Checklist**

- [ ] release-2.1 and release-2.0 each have one new commit with the session fix.
- [ ] Neither release received main's other commits.
- [ ] release-2.0 is checked out, and main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release-2.1` — Go to the first release.
2. `git cherry-pick c3` — Copy the fix there.
3. `git switch release-2.0` — Go to the second release.
4. `git cherry-pick c3` — Copy the fix there too.

**Accepted Alternatives (STAFF ONLY)**

- Either release first, as long as you finish on release-2.0; `git checkout`; `-x` on either pick.
- Common patterns that apply: P23, P25.

**Not accepted**

- Merging main into a release, or picking the fix onto only one release.

**Expected Result**
Both releases have their own copy of the session fix, and you are on `release-2.0`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- `release-2.1` tip (parent `c5`) and `release-2.0` tip (parent `c4`) each contain the fix; HEAD on `release-2.0`.
- `main` at `c3`; clean tree.

### 3.3.20 Wrong pick out, right fix in, with its source · Hard

**Variant ID:** `cherry-hard-backport-capstone-export`

**Story**
You were backporting to `release-1.4` and picked `c2` by mistake, an experiment with a streaming export format. Git stopped on a conflict in `src/export.py`.

The fix the release needs is `c4`, Escape quotes in CSV export, and the release team wants its origin recorded.

It will also conflict with the release's own export code, which adds a header row; the agreed result keeps both changes.

**Starting point:** You are on `release-1.4` in the middle of a cherry-pick of `c2` (the wrong commit) that stopped on a conflict in `src/export.py`; `c4` is the right fix.

**Real-World Context**
This is the whole module in one task: back out of the wrong operation, start the right one with its source recorded, resolve the conflict and finish.

**Your Task**
Cancel the current cherry-pick. Apply `c4` so the new commit records its source, resolve `src/export.py` to the content below, and finish the cherry-pick.

**Required resolved file content**

`src/export.py`

```
return to_csv(rows, header=True, quoting=QUOTE_ALL)
```

**Objective Checklist**

- [ ] release-1.4 has one new commit with the quoting fix, and its message includes "cherry picked from commit c4".
- [ ] The experiment from c2 is not on release-1.4.
- [ ] src/export.py contains exactly the required content, and no pick is in progress.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick --abort` — Undo the wrong pick.
2. `git cherry-pick -x c4` — Start the right one with its source; it stops on the conflict.
3. In the simulator's file editor, set `src/export.py` to exactly:

   ```
   return to_csv(rows, header=True, quoting=QUOTE_ALL)
   ```
4. `git add src/export.py` — Mark the file resolved.
5. `git cherry-pick --continue` — Create the copied commit.

**Accepted Alternatives (STAFF ONLY)**

- `git commit --no-edit` instead of `--continue`; `git log` or `git show c4` along the way.
- Common patterns that apply: P25.

**Not accepted**

- Continuing the wrong pick, a pick without `-x`, or merging main.

**Expected Result**
`release-1.4` has one new commit with the quoting fix and a note pointing back to `c4`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `release-1.4`, 3 commits; tip (parent `c3`) message contains the fix and `cherry picked from commit c4`; tree `src/export.py` = the required content.
- No cherry-pick in progress; no conflicts; clean tree.

### 3.3.21 Wrong pick out, right login fix in, with its source · Hard

**Variant ID:** `cherry-hard-backport-capstone-login`

**Story**
On `release-3.0` you started cherry-picking `c2`, the passwordless login experiment, instead of the fix Raven asked for. The pick stopped on a conflict in `src/login.py`.

The fix is `c4`, Trim spaces from login emails, and like every backport it must record where it came from.

It conflicts with the release's own login code, which lowercases emails; the agreed result keeps both.

**Starting point:** You are on `release-3.0` in the middle of a cherry-pick of `c2` (the wrong commit) that stopped on a conflict in `src/login.py`; `c4` is the right fix.

**Real-World Context**
Backing out of the wrong pick first keeps its changes out of the release completely. Recording the right commit's source keeps the backport auditable.

**Your Task**
Cancel the current cherry-pick. Apply `c4` so the new commit records its source, resolve `src/login.py` to the content below, and finish the cherry-pick.

**Required resolved file content**

`src/login.py`

```
email = form.email.strip().lower()
```

**Objective Checklist**

- [ ] release-3.0 has one new commit with the email fix, and its message includes "cherry picked from commit c4".
- [ ] The passwordless experiment is not on release-3.0.
- [ ] src/login.py contains exactly the required content, and no pick is in progress.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git cherry-pick --abort` — Undo the wrong pick.
2. `git cherry-pick -x c4` — Start the right one with its source; it stops on the conflict.
3. In the simulator's file editor, set `src/login.py` to exactly:

   ```
   email = form.email.strip().lower()
   ```
4. `git add src/login.py` — Mark the file resolved.
5. `git cherry-pick --continue` — Create the copied commit.

**Accepted Alternatives (STAFF ONLY)**

- `git commit --no-edit` instead of `--continue`.
- Common patterns that apply: P25.

**Not accepted**

- Continuing the wrong pick, a pick without `-x`, or merging main.

**Expected Result**
`release-3.0` has one new commit with the email fix and a note pointing back to `c4`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 8

- HEAD on `release-3.0`, 3 commits; tip (parent `c3`) message contains the fix and `cherry picked from commit c4`; tree `src/login.py` = the required content.
- No cherry-pick in progress; no conflicts; clean tree.

### 3.3.22 Backport the auth fixes as one reviewed commit · Hard

**Variant ID:** `cherry-hard-review-backports-auth`

**Story**
Two fixes on `main`, one in `src/auth.py` and one in `src/token.py`, need to reach `release-2.2`. The release manager wants to review them as a single commit called "Backport auth fixes". The feature commits around them must not come along.

**Starting point:** You are on `main`. `release-2.2` was cut from the baseline before any of main's later commits.

**Real-World Context**
Applying picks without committing lets you combine several fixes and review them before they become one commit.

**Your Task**
On `release-2.2`, apply the two auth fixes from `main` without committing either, then commit them together with the message `Backport auth fixes`. Finish on `release-2.2` and leave `main` unchanged.

**Objective Checklist**

- [ ] release-2.2 has one new commit "Backport auth fixes" on top of its old tip.
- [ ] It carries both auth fixes and none of main's feature work.
- [ ] main is unchanged, and you finish on release-2.2.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git log --oneline main` — Find the two fix commits.
2. `git switch release-2.2` — Go to the release branch.
3. `git cherry-pick --no-commit c2` — Apply the src/auth.py fix.
4. `git cherry-pick --no-commit c4` — Apply the src/token.py fix.
5. `git commit -m "Backport auth fixes"` — Record both as one commit.

**Accepted Alternatives (STAFF ONLY)**

- `-n` for `--no-commit`; one `git cherry-pick --no-commit c2 c4`.

**Not accepted**

- Two separate commits, or picking the feature commits.

**Expected Result**
`release-2.2` has one reviewed commit with both auth fixes.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 12

- Tip "Backport auth fixes" with parent c5; both files fixed; src/new.py unchanged; three commits on release-2.2.

### 3.3.23 Backport the export fixes as one reviewed commit · Hard

**Variant ID:** `cherry-hard-review-backports-export`

**Story**
`release-3.0` needs two fixes from `main`: one in `src/export.py` and one in `src/csv_writer.py`. QA will only sign off on a single commit, "Backport export fixes". New feature work on `main` stays out of the release.

**Starting point:** You are on `main`. `release-3.0` was cut from the baseline before any of main's later commits.

**Real-World Context**
Release branches take only the fixes they need. Combining picks into one commit keeps the release history short and reviewable.

**Your Task**
On `release-3.0`, apply the two export fixes from `main` without committing either, then commit them together with the message `Backport export fixes`. Finish on `release-3.0` and leave `main` unchanged.

**Objective Checklist**

- [ ] release-3.0 has one new commit "Backport export fixes" on top of its old tip.
- [ ] It carries both export fixes and none of main's feature work.
- [ ] main is unchanged, and you finish on release-3.0.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git log --oneline main` — Find the two fix commits.
2. `git switch release-3.0` — Go to the release branch.
3. `git cherry-pick --no-commit c1` — Apply the src/export.py fix.
4. `git cherry-pick --no-commit c3` — Apply the src/csv_writer.py fix.
5. `git commit -m "Backport export fixes"` — Record both as one commit.

**Accepted Alternatives (STAFF ONLY)**

- `-n` for `--no-commit`; one `git cherry-pick --no-commit c1 c3`.

**Not accepted**

- Two separate commits, or picking the feature commits.

**Expected Result**
`release-3.0` has one reviewed commit with both export fixes.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 12

- Tip "Backport export fixes" with parent c5; both files fixed; src/new.py unchanged; three commits on release-3.0.

## Module 4 — Advanced Recovery and History

### 4.1.16 Recover the search ranking fix and publish it · Medium

**Variant ID:** `reflog-medium-recover-and-publish-search`

**Story**
A hard reset this morning moved `main` back to the project baseline and took four commits with it, including your borrower search ranking fix. Nothing was pushed, so `origin` cannot help, but Git's reflog still remembers where `main` was.

Finn wants the recovered work on its own branch, `recovery/search-fix`, and on `origin` so he can review it today.

**Starting point:** You are on `main` after a hard reset to the baseline; the reflog still lists the lost tip; `origin` is available.

**Real-World Context**
The reflog records every place a branch has pointed. A commit that no branch reaches is still there for a while, and a new branch can bring it back.

**Your Task**
Find the lost tip in the reflog, recover it on a new branch named `recovery/search-fix`, switch to it, and publish it to `origin` with its upstream set. Leave `main` where it is.

**Objective Checklist**

- [ ] recovery/search-fix points at the lost ranking fix and is checked out.
- [ ] origin/recovery/search-fix matches it, and the local branch tracks it.
- [ ] main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the commit main pointed to before the reset.
2. `git switch -c recovery/search-fix c4` — Recover it on a new branch.
3. `git push -u origin recovery/search-fix` — Publish it for review.

**Accepted Alternatives (STAFF ONLY)**

- `git reflog show main`; `git branch recovery/search-fix c4` then `git switch recovery/search-fix`; `git push --set-upstream origin recovery/search-fix`.
- Common patterns that apply: P26, P27, P31.

**Not accepted**

- Resetting main back to the lost commit, or publishing without an upstream.

**Expected Result**
The ranking fix is safe on `recovery/search-fix`, published and tracked, and `main` is unchanged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD on `recovery/search-fix` at `c4`; `origin/recovery/search-fix` = local; upstream set.
- `main` at `c0`; clean tree.

### 4.1.17 Recover the billing summary and publish it · Medium

**Variant ID:** `reflog-medium-recover-and-publish-billing`

**Story**
You reset `main` to an older commit to test something and forgot that the billing work on top was not pushed yet. Three commits, ending with Finish billing summary, are no longer on any branch. Sage needs them back on `recovery/billing` and on `origin` before the finance demo.

**Starting point:** You are on `main` after a hard reset; the reflog still lists the lost tip; `origin` is available.

**Real-World Context**
Recovering is cheap when you act before Git cleans up unreachable commits. Publishing the recovered branch makes the work safe on the server too.

**Your Task**
Find the lost tip in the reflog, recover it on a new branch named `recovery/billing`, switch to it, and publish it to `origin` with its upstream set. Leave `main` where it is.

**Objective Checklist**

- [ ] recovery/billing points at the lost billing summary and is checked out.
- [ ] origin/recovery/billing matches it, and the local branch tracks it.
- [ ] main has not moved.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find where main was before the reset.
2. `git switch -c recovery/billing c5` — Recover it on a new branch.
3. `git push -u origin recovery/billing` — Publish and track it.

**Accepted Alternatives (STAFF ONLY)**

- `git reflog show main`; `git branch recovery/billing c5` then `git switch recovery/billing`; `git push --set-upstream origin recovery/billing`.
- Common patterns that apply: P26, P27, P31.

**Not accepted**

- Moving main to the lost commit, or publishing without an upstream.

**Expected Result**
The billing work is on `recovery/billing`, published and tracked, and `main` is unchanged.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 10

- HEAD on `recovery/billing` at `c5`; `origin/recovery/billing` = local; upstream set.
- `main` at `c2`; clean tree.

### 4.1.18 Bookmark the lost work, then bring only the auth fix to main · Hard

**Variant ID:** `reflog-hard-recover-then-pick-auth`

**Story**
After a reset moved `main` back three commits, the reflog shows what you lost: some session groundwork, an abandoned magic-link experiment, and on top of it the auth token expiry fix Raven needs today.

You want the whole lost line kept on `recovery/auth` for later, without leaving `main`. Only the fix itself belongs on `main` now. Check the commit before you copy it.

**Starting point:** You are on `main` after a hard reset; the reflog lists the lost tip, which holds the auth fix on top of the experiment.

**Real-World Context**
`git branch <name> <commit>` keeps a commit reachable without switching to it. Cherry-picking then copies just the change you need, leaving the rest of the lost line behind.

**Your Task**
Find the lost tip in the reflog and inspect it. Keep it on a new branch named `recovery/auth` without switching, then copy __only__ the auth fix onto `main` as a new commit.

**Objective Checklist**

- [ ] recovery/auth points at the lost tip, and main is still checked out.
- [ ] main has one new commit with the auth fix and nothing from the experiment or the groundwork.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the lost tip.
2. `git show c4` — Confirm it is the auth fix.
3. `git branch recovery/auth c4` — Keep the lost line without switching.
4. `git cherry-pick c4` — Copy only the fix onto main.

**Accepted Alternatives (STAFF ONLY)**

- `git log recovery/auth` after creating the branch; `-x` on the pick.
- Common patterns that apply: P25, P26, P27.

**Not accepted**

- Resetting main to the lost tip (it brings the experiment), or switching to the recovery branch and staying there.

**Expected Result**
`recovery/auth` keeps the lost line, and `main` has only the auth fix on top of where it was.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- `recovery/auth` at `c4`; HEAD on `main`; tip (parent `c1`) message contains the fix; tree has the fix and no experiment or groundwork files.
- Clean tree.

### 4.1.19 Bookmark the lost work, then bring only the export fix to main · Hard

**Variant ID:** `reflog-hard-recover-then-pick-export`

**Story**
A reset dropped three commits from `main`: export groundwork, a debug commit that dumps every row to the console, and the export date format fix on top. The fix has to ship; **the debug commit must never reach `main`**.

Sage wants the lost line kept on `recovery/export` so nobody loses the groundwork, but you should stay on `main` the whole time. Inspect the commit before you copy it.

**Starting point:** You are on `main` after a hard reset; the reflog lists the lost tip, which holds the export fix on top of the debug commit.

**Real-World Context**
Recovering a line of work and shipping part of it are separate steps. A bookmark branch keeps everything; a cherry-pick ships only what was asked for.

**Your Task**
Find the lost tip in the reflog and inspect it. Keep it on a new branch named `recovery/export` without switching, then copy __only__ the export fix onto `main` as a new commit.

**Objective Checklist**

- [ ] recovery/export points at the lost tip, and main is still checked out.
- [ ] main has one new commit with the export fix and nothing from the debug commit or the groundwork.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the lost tip.
2. `git show c4` — Confirm it is the export fix.
3. `git branch recovery/export c4` — Keep the lost line without switching.
4. `git cherry-pick c4` — Copy only the fix onto main.

**Accepted Alternatives (STAFF ONLY)**

- `-x` on the pick; `git log` along the way.
- Common patterns that apply: P25, P26, P27.

**Not accepted**

- Resetting main to the lost tip, or merging the recovery branch.

**Expected Result**
`recovery/export` keeps the lost line, and `main` has only the export fix.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- `recovery/export` at `c4`; HEAD on `main`; tip (parent `c1`) message contains the fix; tree has the fix and no debug or groundwork files.
- Clean tree.

### 4.2.10 Sync first, then undo the docs theme · Easy

**Variant ID:** `revert-easy-pull-then-revert-docs`

**Story**
The docs build has been failing since `c3`, Switch docs theme, which is already on `origin`. Raven also pushed an FAQ page after it, and your `main` has not seen that yet.

Raven wants the theme change undone without rewriting anything that is published, and the fix on `origin` before the handbook goes out.

**Starting point:** You are on `main`, one commit behind `origin/main`; `c3` is published and broke the docs build.

**Real-World Context**
`git revert` adds a new commit that undoes an old one. Published history stays intact, so teammates can pull the fix like any other commit. Updating first means your revert goes on top of the newest work.

**Your Task**
Bring `main` up to date with `origin`, undo `c3` with a new commit, and push `main` to `origin`.

**Objective Checklist**

- [ ] main includes Raven's FAQ commit.
- [ ] A new commit undoes Switch docs theme, and c3 is still in the history.
- [ ] origin/main matches your main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin main` — Bring in Raven's commit.
2. `git revert c3` — Undo the theme change with a new commit.
3. `git push` — Publish main.

**Accepted Alternatives (STAFF ONLY)**

- `git pull`; `git revert --no-edit c3`; `git push origin main`.
- Common patterns that apply: P21, P22, P41.

**Not accepted**

- `git reset` to before c3 followed by a force push, or reverting before pulling and then failing to publish.

**Expected Result**
`origin/main` has the FAQ page and a new commit that reverts the theme change, with the old history intact.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- Tip is `Revert "Switch docs theme"` with parent `c4`; tree has the old docs config and the FAQ; `c3` still in history.
- `origin/main` = `main`; clean tree.

### 4.2.11 Sync first, then undo the endpoint rename · Easy

**Variant ID:** `revert-easy-pull-then-revert-api`

**Story**
`c4`, Rename the orders endpoint, broke every client of the billing API, and it is already on `origin`. Finn has since pushed a health endpoint you do not have locally. He wants the rename undone safely, on top of his work, and published right away.

**Starting point:** You are on `main`, behind `origin/main`; `c4` is published and broke the API.

**Real-World Context**
Reverting is the safe undo for shared history: nothing anyone already pulled is rewritten.

**Your Task**
Bring `main` up to date with `origin`, undo `c4` with a new commit, and push `main` to `origin`.

**Objective Checklist**

- [ ] main includes Finn's health endpoint commit.
- [ ] A new commit undoes Rename the orders endpoint, and c4 is still in the history.
- [ ] origin/main matches your main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git pull origin main` — Bring in Finn's commit.
2. `git revert c4` — Undo the rename with a new commit.
3. `git push` — Publish main.

**Accepted Alternatives (STAFF ONLY)**

- `git pull`; `git revert --no-edit c4`; `git push origin main`.
- Common patterns that apply: P21, P22, P41.

**Not accepted**

- Rewriting published history with `git reset` and a force push.

**Expected Result**
`origin/main` has the health endpoint and a new commit that reverts the rename.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- Tip is `Revert "Rename the orders endpoint"` with parent `c5`; tree has the old routes and the health endpoint; `c4` still in history.
- `origin/main` = `main`; clean tree.

### 4.2.12 Undo the pricing change on release 2.1 · Medium

**Variant ID:** `revert-medium-release-branch-pricing`

**Story**
Customers on release 2.1 are seeing prices rounded to whole pesos since `c4`, Round prices to whole pesos. The release branch is published and tracks `origin/release/2.1`, and the release notes were updated after the bad commit.

Finn wants the rounding undone __on the release branch only__, without rewriting it, and pushed for the patch build. You are on `main`.

**Starting point:** You are on `main`; `release/2.1` tracks `origin/release/2.1`; `c4` on `release/2.1` broke pricing.

**Real-World Context**
Release branches are shared and published, so fixes go on as new commits. Reverting on the release branch leaves `main` and everyone's copies of the release untouched.

**Your Task**
Switch to `release/2.1`, undo `c4` with a new commit, and push `release/2.1` to `origin`. **Leave `main` unchanged.**

**Objective Checklist**

- [ ] release/2.1 has a new commit that undoes Round prices to whole pesos, and c4 is still in its history.
- [ ] The release notes update is kept.
- [ ] origin/release/2.1 matches your release/2.1, and main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release/2.1` — Go to the release branch.
2. `git revert c4` — Undo the rounding with a new commit.
3. `git push` — Publish the release branch.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout release/2.1`; `git revert --no-edit c4`; `git push origin release/2.1`.
- Common patterns that apply: P21, P22, P23.

**Not accepted**

- Reverting on main, or resetting the release branch and force pushing.

**Expected Result**
`origin/release/2.1` has a new commit reverting the rounding, with the release notes intact.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `release/2.1`; tip is `Revert "Round prices to whole pesos"` with parent `c5`; tree has the old pricing and the new release notes; `c4` still in history.
- `origin/release/2.1` = `release/2.1`; `main` at `c1`; clean tree.

### 4.2.13 Undo the SSO requirement on release 1.8 · Medium

**Variant ID:** `revert-medium-release-branch-auth`

**Story**
Since `c3`, Require SSO for every account, customers on release 1.8 without a company login cannot sign in at all. The release branch is published and tracks `origin`, and the release notes changed after it.

Sage asks you to undo the requirement on `release/1.8` only, as a new commit, and push it. You are on `main`.

**Starting point:** You are on `main`; `release/1.8` tracks `origin/release/1.8`; `c3` on `release/1.8` broke sign-in.

**Real-World Context**
A revert on the branch that needs it is the smallest safe fix: no other branch changes, and no published commit is rewritten.

**Your Task**
Switch to `release/1.8`, undo `c3` with a new commit, and push `release/1.8` to `origin`. **Leave `main` unchanged.**

**Objective Checklist**

- [ ] release/1.8 has a new commit that undoes Require SSO for every account, and c3 is still in its history.
- [ ] The release notes update is kept.
- [ ] origin/release/1.8 matches your release/1.8, and main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release/1.8` — Go to the release branch.
2. `git revert c3` — Undo the requirement with a new commit.
3. `git push` — Publish the release branch.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout release/1.8`; `git revert --no-edit c3`; `git push origin release/1.8`.
- Common patterns that apply: P21, P22, P23.

**Not accepted**

- Reverting on main, or rewriting the release branch.

**Expected Result**
`origin/release/1.8` has a new commit reverting the SSO requirement.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- HEAD on `release/1.8`; tip is `Revert "Require SSO for every account"` with parent `c4`; tree has the old sign-in and the new release notes; `c3` still in history.
- `origin/release/1.8` = `release/1.8`; `main` at `c1`; clean tree.

### 4.2.14 Reword the local commit, revert the published one · Hard

**Variant ID:** `revert-hard-amend-local-revert-pushed-shop`

**Story**
Your local `main` has one commit nobody has seen yet, `c4`, with the message "wip"; it adds the order export. Origin already has `c0` to `c3`, and Maeve just found that `c2`, Break checkout, *really* did break checkout.

She wants one push that does both fixes the right way: the unpublished message can be rewritten, but the published commit must be undone without touching history anyone has pulled.

**Starting point:** You are on `main`; `c0` to `c3` are published; `c4` is local with the message "wip"; published `c2` broke checkout.

**Real-World Context**
The rule of thumb is: rewrite only what is not published. Amending a local commit is fine; a published mistake gets a revert.

**Your Task**
Change `c4`'s message to `Add order export`, undo `c2` with a new commit, and push `main` to `origin` once.

**Objective Checklist**

- [ ] The order export commit is now named Add order export and still sits on c3.
- [ ] A new commit undoes Break checkout, and c2 and c3 are still in the history.
- [ ] origin/main matches your main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Add order export"` — Reword the unpublished commit.
2. `git revert c2` — Undo the published mistake with a new commit.
3. `git push` — Publish both fixes.

**Accepted Alternatives (STAFF ONLY)**

- `git revert --no-edit c2`; `git push origin main`.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- Reverting first and then amending (it rewrites the revert), resetting published commits, or a force push.

**Expected Result**
`origin/main` ends with the reworded export commit and a revert of the checkout change, and no published commit was rewritten.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- Tip is `Revert "Break checkout"`; `main~1` is `Add order export` with parent `c3`, replacing `c4`; tree has the old checkout and the export.
- `c2` and `c3` still in history; `origin/main` = `main`; clean tree.

### 4.2.15 Reword the local commit, revert the published feed change · Hard

**Variant ID:** `revert-hard-amend-local-revert-pushed-blog`

**Story**
The field notes blog has a new RSS feed in your local commit `c4`, but you committed it as "stuff". Origin already has `c3`, Shorten feed item IDs, which made every feed reader show old posts as new.

Raven wants a single push: your local commit with a proper name, and the published change undone safely.

**Starting point:** You are on `main`; `c0` to `c3` are published; `c4` is local with the message "stuff"; published `c3` broke the RSS feed.

**Real-World Context**
Knowing what is published decides which tool you use: amend before you push, revert after.

**Your Task**
Change `c4`'s message to `Add RSS feed`, undo `c3` with a new commit, and push `main` to `origin` once.

**Objective Checklist**

- [ ] The feed commit is now named Add RSS feed and still sits on c3.
- [ ] A new commit undoes Shorten feed item IDs, and c3 is still in the history.
- [ ] origin/main matches your main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git commit --amend -m "Add RSS feed"` — Reword the unpublished commit.
2. `git revert c3` — Undo the published change with a new commit.
3. `git push` — Publish both fixes.

**Accepted Alternatives (STAFF ONLY)**

- `git revert --no-edit c3`; `git push origin main`.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- Reverting first and then amending, resetting published commits, or a force push.

**Expected Result**
`origin/main` ends with the reworded feed commit and a revert of the ID change.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- Tip is `Revert "Shorten feed item IDs"`; `main~1` is `Add RSS feed` with parent `c3`, replacing `c4`; tree has the old feed IDs and the new feed.
- `c3` still in history; `origin/main` = `main`; clean tree.

### 4.3.10 Abandon the stopped docs rebase · Easy

**Variant ID:** `rebase-easy-abort-stopped-docs`

**Story**
You started rebasing `feature/docs-search` onto `main`, and it stopped on a conflict in `docs/index.md`: `main` renamed the handbook heading while your branch added a search hint under it.

Raven says the heading rename is not final yet, so the rebase can wait. Your branch should be exactly as it was before you started.

**Starting point:** You are in the middle of rebasing `feature/docs-search` onto `main`, stopped on a conflict in `docs/index.md`.

**Real-World Context**
`git rebase --abort` cancels a rebase completely and puts the branch back where it was before the rebase began.

**Your Task**
Cancel the rebase so `feature/docs-search` is __exactly__ as it was before.

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/docs-search points at its original tip again.
- [ ] main is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git rebase --abort` — Cancel the rebase.

**Accepted Alternatives (STAFF ONLY)**

- `git status` first to see the rebase in progress.
- Common patterns that apply: P49.

**Not accepted**

- Resolving and continuing the rebase, or `git rebase --skip`.

**Expected Result**
`feature/docs-search` is back at its original tip with no rebase in progress.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- HEAD on `feature/docs-search` at `c3`; no rebase in progress; `main` at `c1`.
- No conflicts; clean tree.

### 4.3.11 Resolve and continue the config loader rebase · Easy

**Variant ID:** `rebase-easy-continue-config`

**Story**
Your rebase of `feature/config-loader` onto `main` stopped on a conflict in `config/app.yml`: `main` switched the loader to `toml`, and your branch added a watch setting.

Finn agrees with both, so the resolved file keeps `main`'s loader and your watch setting. After that, the rebase should finish replaying the rest of your branch.

**Starting point:** You are in the middle of rebasing `feature/config-loader` onto `main`, stopped on a conflict in `config/app.yml`.

**Real-World Context**
During a rebase, Git replays your commits one at a time. When one stops on a conflict, you resolve it, stage the file, and continue; Git then replays the rest.

**Your Task**
Resolve `config/app.yml` to the content below, stage it, and continue the rebase until it finishes.

**Required resolved file content**

`config/app.yml`

```
loader: toml
watch: true
```

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/config-loader now sits on top of main's latest commit.
- [ ] config/app.yml contains exactly the required content, and the branch's later commit was replayed too.

**Answer Key (STAFF ONLY, never shown to students)**

1. In the simulator's file editor, set `config/app.yml` to exactly:

   ```
   loader: toml
   watch: true
   ```
2. `git add config/app.yml` — Mark the file resolved.
3. `git rebase --continue` — Replay the rest of the branch.

**Accepted Alternatives (STAFF ONLY)**

- `git status` along the way.
- Common patterns that apply: P49.

**Not accepted**

- Aborting the rebase, `git rebase --skip`, or committing the resolution as a separate commit.

**Expected Result**
`feature/config-loader` is rebased onto `main` with the agreed config, and no rebase is in progress.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- HEAD on `feature/config-loader`, 4 commits including `c1`, no merge commits; tree `config/app.yml` = the required content plus the follow-up file.
- No rebase in progress; no conflicts; clean tree.

### 4.3.12 Finish the search rebase and republish safely · Hard

**Variant ID:** `rebase-hard-continue-then-lease-search`

**Story**
You pushed `feature/search` yesterday. Today you are rebasing it onto `main`, and it stopped on a conflict in `src/search.py`: `main` doubled the results per page, and your branch turned on fuzzy matching. Keep both.

When the rebase is done, `origin`'s copy still has the old history, so it has to be replaced, but only if nobody else pushed to the branch in the meantime.

**Starting point:** `feature/search` was pushed earlier; you are in the middle of rebasing it onto `main`, stopped on a conflict in `src/search.py`.

**Real-World Context**
A rebase rewrites commits that may already be on the remote. `--force-with-lease` replaces the remote branch only if it is still where you last saw it.

**Your Task**
Resolve `src/search.py` to the content below, finish the rebase, and update `origin`'s `feature/search` **without overwriting work you have not seen**.

**Required resolved file content**

`src/search.py`

```
RESULTS = 20
FUZZY = True
```

**Objective Checklist**

- [ ] The rebase is finished and feature/search sits on main's latest commit.
- [ ] src/search.py contains exactly the required content.
- [ ] origin/feature/search matches your branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. In the simulator's file editor, set `src/search.py` to exactly:

   ```
   RESULTS = 20
   FUZZY = True
   ```
2. `git add src/search.py` — Mark the file resolved.
3. `git rebase --continue` — Finish the rebase.
4. `git push --force-with-lease origin feature/search` — Republish safely.

**Accepted Alternatives (STAFF ONLY)**

- `--force-with-lease=feature/search`; `git push --force-with-lease` with the upstream set.
- Common patterns that apply: P49.

**Not accepted**

- A plain push (Git rejects it: origin still has the old commits), or aborting the rebase.

**Expected Result**
`origin/feature/search` holds the rebased branch with the agreed search settings.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/search`, 4 commits including `c1`, no merges; tree `src/search.py` = the required content plus the test file.
- `origin/feature/search` = local; no rebase in progress; clean tree.

### 4.3.13 Finish the billing rebase and republish safely · Hard

**Variant ID:** `rebase-hard-continue-then-lease-billing`

**Story**
`feature/billing` is on `origin` already. Your rebase onto `main` stopped on a conflict in `src/billing.py`: `main` added a rounding rule, and your branch switched the currency to USD for the new market. The final file keeps both.

Sage reminds you that a teammate sometimes pushes small fixes to this branch, so the republish must refuse if that happened.

**Starting point:** `feature/billing` was pushed earlier; you are in the middle of rebasing it onto `main`, stopped on a conflict in `src/billing.py`.

**Real-World Context**
Finishing a rebase is half the job when the branch is shared. Republishing with a lease protects any teammate commit you have not fetched.

**Your Task**
Resolve `src/billing.py` to the content below, finish the rebase, and update `origin`'s `feature/billing` safely.

**Required resolved file content**

`src/billing.py`

```
CURRENCY = 'USD'
ROUNDING = 'half-up'
```

**Objective Checklist**

- [ ] The rebase is finished and feature/billing sits on main's latest commit.
- [ ] src/billing.py contains exactly the required content.
- [ ] origin/feature/billing matches your branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. In the simulator's file editor, set `src/billing.py` to exactly:

   ```
   CURRENCY = 'USD'
   ROUNDING = 'half-up'
   ```
2. `git add src/billing.py` — Mark the file resolved.
3. `git rebase --continue` — Finish the rebase.
4. `git push --force-with-lease origin feature/billing` — Republish safely.

**Accepted Alternatives (STAFF ONLY)**

- `--force-with-lease=feature/billing`.
- Common patterns that apply: P49.

**Not accepted**

- A plain push (Git rejects it: origin still has the old commits), or aborting the rebase.

**Expected Result**
`origin/feature/billing` holds the rebased branch with the agreed billing settings.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/billing`, 4 commits including `c1`, no merges; tree `src/billing.py` = the required content plus the docs file.
- `origin/feature/billing` = local; no rebase in progress; clean tree.

### 4.3.14 Abort, then move only the reports commits · Hard

**Variant ID:** `rebase-hard-abort-then-onto-reports`

**Story**
You are rebasing `feature/reports` onto `main`, and it stopped on a conflict in `src/charts.js`. That file is not even yours: you started `feature/reports` from `spike/charts`, an experiment, so the rebase is dragging the spike's commits along.

Maeve wants only your two reports commits on top of `main`, and the spike left out entirely.

**Starting point:** You are in the middle of rebasing `feature/reports` onto `main`, stopped on a conflict from a `spike/charts` commit; `feature/reports` was started from `spike/charts`.

**Real-World Context**
`git rebase --onto <newbase> <upstream> <branch>` replays only the commits after `<upstream>`, so a branch can leave behind the base it was started from.

**Your Task**
Cancel the current rebase. Then move __only__ `feature/reports`' own commits onto `main`, leaving the spike's commits behind.

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/reports sits on main's latest commit with only its two commits.
- [ ] Nothing from spike/charts is on feature/reports, and spike/charts is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git rebase --abort` — Cancel the rebase that drags the spike along.
2. `git rebase --onto main spike/charts feature/reports` — Replay only the reports commits onto main.

**Accepted Alternatives (STAFF ONLY)**

- `git log --oneline --graph --all` along the way; `git rebase --onto main spike/charts` while on feature/reports.
- Common patterns that apply: P49.

**Not accepted**

- Resolving the spike conflict and continuing, or a plain `git rebase main`.

**Expected Result**
`feature/reports` is two commits on top of `main`, with no spike commits.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- HEAD on `feature/reports`, 4 commits including `c1`, excluding `c2` and `c3`; tree has the reports work and main's charts, no spike stylesheet.
- `spike/charts` at `c3`; no rebase in progress; clean tree.

### 4.3.15 Abort, then move only the table commits · Hard

**Variant ID:** `rebase-hard-abort-then-onto-ui`

**Story**
`feature/table-ui` was started from `spike/new-grid` by mistake, and your rebase onto `main` just stopped on a conflict in `src/charts.js` from one of the spike's commits. Finn says the grid spike is not going anywhere, so **it must not travel with your table work**. Only your own two commits should end up on `main`'s latest commit.

**Starting point:** You are in the middle of rebasing `feature/table-ui` onto `main`, stopped on a conflict from a `spike/new-grid` commit; `feature/table-ui` was started from `spike/new-grid`.

**Real-World Context**
When a branch was started from the wrong base, `--onto` lets you cut it loose and replant only your own commits.

**Your Task**
Cancel the current rebase. Then move __only__ `feature/table-ui`'s own commits onto `main`, leaving the spike's commits behind.

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/table-ui sits on main's latest commit with only its two commits.
- [ ] Nothing from spike/new-grid is on feature/table-ui, and spike/new-grid is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git rebase --abort` — Cancel the rebase.
2. `git rebase --onto main spike/new-grid feature/table-ui` — Replay only the table commits onto main.

**Accepted Alternatives (STAFF ONLY)**

- `git rebase --onto main spike/new-grid` while on feature/table-ui.
- Common patterns that apply: P49.

**Not accepted**

- Continuing the spike's rebase, or a plain `git rebase main`.

**Expected Result**
`feature/table-ui` is two commits on top of `main`, with no spike commits.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 8

- HEAD on `feature/table-ui`, 4 commits including `c1`, excluding `c2` and `c3`; tree has the table work and main's charts, no spike stylesheet.
- `spike/new-grid` at `c3`; no rebase in progress; clean tree.

### 4.3.16 Undo a bad rebase of the CLI flags and republish · Hard

**Variant ID:** `rebase-hard-reset-rebase-lease-cli`

**Story**
You pushed `feature/cli-flags`, then rebased it onto `main` to pick up a docs fix. Something went wrong: the rebased branch is missing Parse --quiet flag. The reflog still shows the tip you pushed, `c6`, before the rebase.

Finn wants the complete branch back, replayed on `main` properly, and `origin` updated, safely, because he sometimes pushes to this branch too.

**Starting point:** You are on `feature/cli-flags` after a rebase that dropped a commit; the reflog lists the original tip, `c6`, which `origin` also still has.

**Real-World Context**
The reflog is your undo history for rebases. Resetting to the pre-rebase tip and rebasing again restores everything; a lease protects the republish.

**Your Task**
Find the pre-rebase tip in the reflog, reset the branch to it, rebase it onto `main` again, and update `origin`'s `feature/cli-flags` **without overwriting work you have not seen**.

**Objective Checklist**

- [ ] feature/cli-flags sits on main's latest commit with all three of its commits, including Parse --quiet flag.
- [ ] No rebase is in progress, and the history has no merge commits.
- [ ] origin/feature/cli-flags matches your branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the tip before the rebase.
2. `git reset --hard c6` — Put the branch back where it was.
3. `git rebase main` — Replay all three commits onto main.
4. `git push --force-with-lease origin feature/cli-flags` — Republish safely.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --hard feature/cli-flags@{1}` or `git reset --hard origin/feature/cli-flags`; `--force-with-lease=feature/cli-flags`.
- Common patterns that apply: P26, P49.

**Not accepted**

- Re-creating the dropped commit by hand, a plain push (Git rejects it), or a merge.

**Expected Result**
`origin/feature/cli-flags` holds all three CLI commits on top of `main`'s docs fix.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/cli-flags`, 5 commits including `c1`, no merges; tree has all three changes and the fixed usage docs.
- `origin/feature/cli-flags` = local; no rebase in progress; clean tree.

### 4.3.17 Undo a bad rebase of the rate limiter and republish · Hard

**Variant ID:** `rebase-hard-reset-rebase-lease-api`

**Story**
`feature/rate-limits` was pushed with three commits. After you rebased it onto `main`, Add rate limiter is gone and the API wiring points at nothing. The reflog still has the pushed tip, `c5`.

Sage needs the branch whole again, on top of `main`, and `origin` updated without stomping on anything a teammate may have pushed.

**Starting point:** You are on `feature/rate-limits` after a rebase that dropped a commit; the reflog lists the original tip, `c5`, which `origin` also still has.

**Real-World Context**
A bad rebase is recoverable as long as you know where the branch was. The reflog tells you, and `git reset --hard` takes you back.

**Your Task**
Find the pre-rebase tip in the reflog, reset the branch to it, rebase it onto `main` again, and update `origin`'s `feature/rate-limits` safely.

**Objective Checklist**

- [ ] feature/rate-limits sits on main's latest commit with all three of its commits, including Add rate limiter.
- [ ] No rebase is in progress, and the history has no merge commits.
- [ ] origin/feature/rate-limits matches your branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the tip before the rebase.
2. `git reset --hard c5` — Put the branch back where it was.
3. `git rebase main` — Replay all three commits onto main.
4. `git push --force-with-lease origin feature/rate-limits` — Republish safely.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --hard origin/feature/rate-limits`; `--force-with-lease=feature/rate-limits`.
- Common patterns that apply: P26, P49.

**Not accepted**

- Re-creating the dropped commit by hand, a plain push (Git rejects it), or a merge.

**Expected Result**
`origin/feature/rate-limits` holds all three commits on top of `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/rate-limits`, 5 commits including `c1`, no merges; tree has all three changes and the fixed usage docs.
- `origin/feature/rate-limits` = local; no rebase in progress; clean tree.

### 4.3.18 Resolve and continue the dark theme rebase · Easy

**Variant ID:** `rebase-easy-continue-styles`

**Story**
Your rebase of `feature/dark-theme` onto `main` stopped on `styles/theme.css`. `main` changed the accent colour to navy, and your branch added a dark surface colour. Mika wants both, so the file keeps `main`'s accent and your surface.

**Starting point:** You are in the middle of rebasing `feature/dark-theme` onto `main`, stopped on a conflict in `styles/theme.css`.

**Real-World Context**
A stopped rebase waits for you: resolve the file, stage it, and continue, and Git replays the rest of your branch.

**Your Task**
Resolve `styles/theme.css` to the content below, stage it, and continue the rebase until it finishes.

**Required resolved file content**

`styles/theme.css`

```
--accent: navy;
--surface: #111;
```

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/dark-theme now sits on top of main's latest commit.
- [ ] styles/theme.css contains exactly the required content, and the branch's later commit was replayed too.

**Answer Key (STAFF ONLY, never shown to students)**

1. In the simulator's file editor, set `styles/theme.css` to exactly:

   ```
   --accent: navy;
   --surface: #111;
   ```
2. `git add styles/theme.css` — Mark the file resolved.
3. `git rebase --continue` — Replay the rest of the branch.

**Accepted Alternatives (STAFF ONLY)**

- `git status` along the way.

**Not accepted**

- Aborting the rebase, `git rebase --skip`, or committing the resolution as a separate commit.

**Expected Result**
`feature/dark-theme` is rebased onto `main` with both colours, and no rebase is in progress.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- No rebase in progress; four commits on feature/dark-theme including main's c1; the resolved theme and the replayed docs file are in the tip.

### 4.3.19 Resolve and continue the health route rebase · Easy

**Variant ID:** `rebase-easy-continue-routes`

**Story**
Rebasing `feature/health-route` onto `main` stopped on `src/routes.py`. `main` added a login route, and your branch added a health check. Both stay, so the file keeps `main`'s routes and your health check.

**Starting point:** You are in the middle of rebasing `feature/health-route` onto `main`, stopped on a conflict in `src/routes.py`.

**Real-World Context**
Conflicts during a rebase are resolved one replayed commit at a time, then the rebase carries on by itself.

**Your Task**
Resolve `src/routes.py` to the content below, stage it, and continue the rebase until it finishes.

**Required resolved file content**

`src/routes.py`

```
ROUTES = ['/', '/login']
HEALTH = '/health'
```

**Objective Checklist**

- [ ] No rebase is in progress and no conflicts remain.
- [ ] feature/health-route now sits on top of main's latest commit.
- [ ] src/routes.py contains exactly the required content, and the branch's later commit was replayed too.

**Answer Key (STAFF ONLY, never shown to students)**

1. In the simulator's file editor, set `src/routes.py` to exactly:

   ```
   ROUTES = ['/', '/login']
   HEALTH = '/health'
   ```
2. `git add src/routes.py` — Mark the file resolved.
3. `git rebase --continue` — Replay the rest of the branch.

**Accepted Alternatives (STAFF ONLY)**

- `git status` along the way.

**Not accepted**

- Aborting the rebase, `git rebase --skip`, or committing the resolution as a separate commit.

**Expected Result**
`feature/health-route` is rebased onto `main` with both routes, and no rebase is in progress.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 2 · Maximum counted commands: 12

- No rebase in progress; four commits on feature/health-route including main's c1; the resolved routes and the replayed test file are in the tip.

## Module 1 Challenge Gate — Foundations Gate

### 1.G.1 Start the field log in two commits · Easy

**Variant ID:** `gate1-easy-two-commit-start-field-log`

**Story**
Maeve has been logging bird counts in a plain folder all semester: `notes.md` and `readings.csv` hold the data, `README.md` explains how to read it, and `scratch.txt` is full of half-finished guesses.

She wants the data in history first, so the log shows when the readings arrived, and the guide as a commit of its own that can change later without touching the data. Your guesses in `scratch.txt` stay private.

**Starting point:** You are in `field-log`. It is not a repository yet. `notes.md`, `readings.csv`, `README.md` and `scratch.txt` are new files.

**Real-World Context**
A clear history starts with its first commits. Recording a project in purposeful snapshots, data first and documentation second, makes each one easy to review, revert or reword later.

**Your Task**
Make `field-log` a Git repository on `main`. Commit `notes.md` and `readings.csv` with the message `Start field log`, then commit `README.md` on top of it with the message `Add field log guide`. **Leave `scratch.txt` untracked.**

**Objective Checklist**

- [ ] field-log is a Git repository on main.
- [ ] The first commit, “Start field log”, holds notes.md and readings.csv but not README.md.
- [ ] The second commit, “Add field log guide”, adds README.md.
- [ ] scratch.txt is not committed and is still in the folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main` — Create the repository on main.
2. `git add notes.md readings.csv` — Stage the data files.
3. `git commit -m "Start field log"` — Record the first snapshot.
4. `git add README.md` — Stage the guide.
5. `git commit -m "Add field log guide"` — Record it as its own commit.

**Accepted Alternatives (STAFF ONLY)**

- `git init` when the simulator's first branch is main; the data files staged in one command or two; `--message` forms and single quotes. Both messages must match exactly.
- Common patterns that apply: P1, P19, P20.

**Not accepted**

- `git add .` or `git add -A`: they would commit scratch.txt, or put the guide in the first commit.

**Expected Result**
`field-log` is a repository on `main` with two commits: “Start field log” with `notes.md` and `readings.csv`, then “Add field log guide” with `README.md`. `scratch.txt` stays untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Repository initialized; HEAD on `main`; exactly two commits.
- `main~1` is `Start field log` with `notes.md` and `readings.csv`, not `README.md` or `scratch.txt`; `main` is `Add field log guide` and adds `README.md`; `scratch.txt` still untracked.

### 1.G.2 Start the quiz app in two commits · Easy

**Variant ID:** `gate1-easy-two-commit-start-quiz`

**Story**
Raven sketched a quiz app for the department's orientation week: `index.html` and `quiz.js` are the app, `README.md` explains how to run it, and `todo.txt` lists features nobody has agreed on yet.

Raven asks you to put the project under version control tonight: the app as the first commit and the setup notes as a second one, so tomorrow's reviewers can read them apart. The to-do list is Raven's own and stays out.

**Starting point:** You are in `quiz-app`. It is not a repository yet. `index.html`, `quiz.js`, `README.md` and `todo.txt` are new files.

**Real-World Context**
A first commit is a promise about what the project is. Keeping the app and its setup notes in separate commits, and personal planning notes out of history, gives the team a history they can follow.

**Your Task**
Make `quiz-app` a Git repository on `main`. Commit `index.html` and `quiz.js` with the message `Start quiz app`, then commit `README.md` on top of it with the message `Add quiz setup notes`. **Leave `todo.txt` untracked.**

**Objective Checklist**

- [ ] quiz-app is a Git repository on main.
- [ ] The first commit, “Start quiz app”, holds index.html and quiz.js but not README.md.
- [ ] The second commit, “Add quiz setup notes”, adds README.md.
- [ ] todo.txt is not committed and is still in the folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init -b main` — Create the repository on main.
2. `git add index.html quiz.js` — Stage the app files.
3. `git commit -m "Start quiz app"` — Record the first snapshot.
4. `git add README.md` — Stage the setup notes.
5. `git commit -m "Add quiz setup notes"` — Record them as their own commit.

**Accepted Alternatives (STAFF ONLY)**

- `git init` when the simulator's first branch is main; the app files staged in one command or two; `--message` forms and single quotes. Both messages must match exactly.
- Common patterns that apply: P1, P19, P20.

**Not accepted**

- `git add .` or `git add -A`: they would commit todo.txt, or put the setup notes in the first commit.

**Expected Result**
`quiz-app` is a repository on `main` with two commits: “Start quiz app” with `index.html` and `quiz.js`, then “Add quiz setup notes” with `README.md`. `todo.txt` stays untracked.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- Repository initialized; HEAD on `main`; exactly two commits.
- `main~1` is `Start quiz app` with `index.html` and `quiz.js`, not `README.md` or `todo.txt`; `main` is `Add quiz setup notes` and adds `README.md`; `todo.txt` still untracked.

### 1.G.3 Finish the search page commit · Medium

**Variant ID:** `gate1-medium-complete-last-commit-search`

**Story**
You committed “Add search page” in a hurry before lunch.

Back at your desk you see what went wrong: `templates/search.html` never made it in, the ranking change is still sitting in `src/search.py` next to a debug hunk, and `notes.txt` got staged by accident. Sage reviews the branch in an hour, and nothing has been pushed.

**Starting point:** You are on `main`. The latest commit is “Add search page”. `notes.txt` is staged, `templates/search.html` is a new file, and `src/search.py` holds the ranking hunk and a debug hunk.

**Real-World Context**
An unpublished commit that left part of its change behind can be completed instead of followed by a "forgot this" commit. That takes three skills from this module at once: unstaging, partial staging and amending.

**Your Task**
Unstage `notes.txt` (keep it), then complete the latest commit with `templates/search.html` and the ranking hunk from `src/search.py`, keeping its message `Add search page`. **Leave the debug hunk uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] The latest commit is still named “Add search page” and now includes templates/search.html and the ranking change.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] notes.txt and the debug hunk are not committed and are still in the working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged notes.txt` — Take the note out of the index.
2. `git add templates/search.html` — Stage the missing template.
3. `git add -p src/search.py` — Stage only the ranking hunk.
4. `git commit --amend -m "Add search page"` — Fold both into the latest commit.

**Accepted Alternatives (STAFF ONLY)**

- Steps 1–3 in any order; `git restore -S`, `git reset -- notes.txt`; `git add --patch`; `git commit --amend --no-edit`. The message must match exactly.
- Common patterns that apply: P8, P4, P7, P29.

**Not accepted**

- A new commit for the missing pieces, amending with notes.txt still staged, or staging the whole of src/search.py.

**Expected Result**
“Add search page” now holds the template and the ranking change and replaced the old commit. `notes.txt` and the debug hunk stay in the working folder.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD replaces `c2` by amend; message `Add search page`; `main` still has 2 commits.
- HEAD changes include `templates/search.html` and the ranking hunk, exclude the debug hunk and `notes.txt`; both left in the working tree.

### 1.G.4 Finish the file upload commit · Medium

**Variant ID:** `gate1-medium-complete-last-commit-upload`

**Story**
“Add file upload” went in without `docs/upload.md`, and the size-limit check you wrote is still unstaged in `src/upload.py`, beside a debug hunk.

On top of that, `scratch.md` is staged even though it is only your notes to yourself. Maeve wants the upload work as one complete commit before she pulls your branch.

**Starting point:** You are on `main`. The latest commit is “Add file upload”. `scratch.md` is staged, `docs/upload.md` is a new file, and `src/upload.py` holds the size-limit hunk and a debug hunk.

**Real-World Context**
Completing a local commit keeps a feature reviewable as one change. Unstage what does not belong, stage exactly what does, then amend.

**Your Task**
Unstage `scratch.md` (keep it), then complete the latest commit with `docs/upload.md` and the size-limit hunk from `src/upload.py`, keeping its message `Add file upload`. **Leave the debug hunk uncommitted** and finish on `main`.

**Objective Checklist**

- [ ] The latest commit is still named “Add file upload” and now includes docs/upload.md and the size-limit change.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] scratch.md and the debug hunk are not committed and are still in the working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged scratch.md` — Take the notes out of the index.
2. `git add docs/upload.md` — Stage the missing documentation.
3. `git add -p src/upload.py` — Stage only the size-limit hunk.
4. `git commit --amend -m "Add file upload"` — Fold both into the latest commit.

**Accepted Alternatives (STAFF ONLY)**

- Steps 1–3 in any order; `git restore -S`, `git reset -- scratch.md`; `git add --patch`; `git commit --amend --no-edit`. The message must match exactly.
- Common patterns that apply: P8, P4, P7, P29.

**Not accepted**

- A new commit for the missing pieces, amending with scratch.md still staged, or staging the whole of src/upload.py.

**Expected Result**
“Add file upload” now holds the documentation and the size-limit change and replaced the old commit. `scratch.md` and the debug hunk stay in the working folder.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD replaces `c2` by amend; message `Add file upload`; `main` still has 2 commits.
- HEAD changes include `docs/upload.md` and the size-limit hunk, exclude the debug hunk and `scratch.md`; both left in the working tree.

### 1.G.5 Reword, tidy up and commit the export fix · Hard

**Variant ID:** `gate1-hard-reword-then-commit-export`

**Story**
Your last commit is called “Add expor”, and Raven has already noticed.

Since then you fixed the CSV headers in `src/export.py` (next to a debug hunk), wrote `docs/export.md`, and a test run left `tmp/run.log` staged and `cache/report.json` full of stray edits.

Raven wants history to read cleanly before the sprint review: the export commit with its proper name, then the header fix with its documentation as a commit of its own. You want to keep the log for now; the cache edits are worthless.

**Starting point:** You are on `main`. The latest commit is “Add expor”. `tmp/run.log` is staged, `cache/report.json` has stray edits, `src/export.py` holds a header fix and a debug hunk, and `docs/export.md` is new.

**Real-World Context**
Amend rewrites the latest commit with whatever is staged. Clearing the index first, and amending before you add the next commit, keeps each commit about one thing.

**Your Task**
Rename the latest commit to `Add export` __without adding anything to it__, discard the edits to `cache/report.json`, then commit the header fix from `src/export.py` together with `docs/export.md` as `Fix export headers`. Keep `tmp/run.log` in the folder, uncommitted, leave the debug hunk uncommitted and finish on `main`.

**Objective Checklist**

- [ ] The export commit is now named “Add export” and contains no log or docs.
- [ ] “Fix export headers” comes right after it, with the header fix and docs/export.md.
- [ ] cache/report.json is back to its committed version.
- [ ] tmp/run.log and the debug hunk are not committed and are still in the working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged tmp/run.log` — Clear the index before amending.
2. `git commit --amend -m "Add export"` — Rename the latest commit.
3. `git restore cache/report.json` — Throw away the stray cache edits.
4. `git add -p src/export.py` — Stage only the header fix.
5. `git add docs/export.md` — Stage the documentation.
6. `git commit -m "Fix export headers"` — Commit the fix separately.

**Accepted Alternatives (STAFF ONLY)**

- Step 3 may come at any point; steps 4–5 in either order; `git restore -S`, `git reset -- tmp/run.log`; `git add --patch`; `--message` forms. The messages must match exactly.
- Common patterns that apply: P8, P7, P4, P5, P6, P1.

**Not accepted**

- Amending while tmp/run.log is staged, amending after the new commit, or staging the whole of src/export.py.

**Expected Result**
`main` reads “Add export” followed by “Fix export headers”. The log and the debug hunk stay in the working folder, and the cache file matches the last commit.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 6 · Maximum counted commands: 8

- `main` has 3 commits; the amend replaced `c2`; `main~1` = `Add export` without `tmp/run.log` or `docs/export.md`.
- `main` = `Fix export headers` with the header hunk and `docs/export.md`, without the debug hunk, the log or the cache file; `cache/report.json` identical to HEAD.

### 1.G.6 Reword, tidy up and commit the billing fix · Hard

**Variant ID:** `gate1-hard-reword-then-commit-billing`

**Story**
“Add biling” is the last commit on `main`, and Sage winced reading it.

You have since fixed the tax calculation in `src/billing.py` (a debug hunk sits beside it) and written `docs/billing.md`. A test run also staged `logs/billing.log` and scribbled stray edits into `cache/invoices.json`.

Sage wants two clean commits: the billing commit with its real name, then the tax fix with its docs. The log stays in your folder; the cache edits can go.

**Starting point:** You are on `main`. The latest commit is “Add biling”. `logs/billing.log` is staged, `cache/invoices.json` has stray edits, `src/billing.py` holds a tax fix and a debug hunk, and `docs/billing.md` is new.

**Real-World Context**
Rewording a commit is safe only while nothing extra is staged. Tidy the index, reword, then build the next commit from exactly the right pieces.

**Your Task**
Rename the latest commit to `Add billing` __without adding anything to it__, discard the edits to `cache/invoices.json`, then commit the tax fix from `src/billing.py` together with `docs/billing.md` as `Fix billing tax`. Keep `logs/billing.log` in the folder, uncommitted, leave the debug hunk uncommitted and finish on `main`.

**Objective Checklist**

- [ ] The billing commit is now named “Add billing” and contains no log or docs.
- [ ] “Fix billing tax” comes right after it, with the tax fix and docs/billing.md.
- [ ] cache/invoices.json is back to its committed version.
- [ ] logs/billing.log and the debug hunk are not committed and are still in the working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git restore --staged logs/billing.log` — Clear the index before amending.
2. `git commit --amend -m "Add billing"` — Rename the latest commit.
3. `git restore cache/invoices.json` — Throw away the stray cache edits.
4. `git add -p src/billing.py` — Stage only the tax fix.
5. `git add docs/billing.md` — Stage the documentation.
6. `git commit -m "Fix billing tax"` — Commit the fix separately.

**Accepted Alternatives (STAFF ONLY)**

- Step 3 may come at any point; steps 4–5 in either order; `git restore -S`, `git reset -- logs/billing.log`; `git add --patch`; `--message` forms. The messages must match exactly.
- Common patterns that apply: P8, P7, P4, P5, P6, P1.

**Not accepted**

- Amending while logs/billing.log is staged, amending after the new commit, or staging the whole of src/billing.py.

**Expected Result**
`main` reads “Add billing” followed by “Fix billing tax”. The log and the debug hunk stay in the working folder, and the cache file matches the last commit.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 6 · Maximum counted commands: 8

- `main` has 3 commits; the amend replaced `c2`; `main~1` = `Add billing` without `logs/billing.log` or `docs/billing.md`.
- `main` = `Fix billing tax` with the tax hunk and `docs/billing.md`, without the debug hunk, the log or the cache file; `cache/invoices.json` identical to HEAD.

## Module 2 Challenge Gate — Collaboration Gate

### 2.G.1 Start the search filters from a fresh main · Easy

**Variant ID:** `gate2-easy-fresh-branch-search`

**Story**
You just finished the cart work on `feature/cart` and pushed it. Raven's next ticket is search filters, and Sage merged a cart total fix into `main` on the server this morning.

Raven's rule for the group: new work *always* starts from an up-to-date `main`, never from yesterday's branch.

**Starting point:** You are on `feature/cart` with a clean working folder. `origin/main` has a new commit that your local `main` does not have yet.

**Real-World Context**
Starting a branch from a stale `main` means resolving someone else's fixes later. Updating `main` first gives the new branch the newest starting point.

**Your Task**
Go back to `main`, bring it up to date with `origin`, then create and switch to `feature/search-filters` from it.

**Objective Checklist**

- [ ] main matches origin/main, including Sage's fix.
- [ ] feature/search-filters exists, starts from the updated main and is checked out.
- [ ] feature/cart is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Return to main.
2. `git pull origin main` — Bring in the new commit from origin.
3. `git switch -c feature/search-filters` — Start the new branch here.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git pull`; `git fetch origin` then `git merge origin/main`; `git checkout -b feature/search-filters`.
- Common patterns that apply: P2, P23.

**Not accepted**

- Creating the branch before updating main, or from feature/cart.

**Expected Result**
`main` and `feature/search-filters` both point at the newest commit from `origin`, and you are on `feature/search-filters`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- HEAD on `feature/search-filters` at `c3`; `main` at `c3`; `origin/main` at `c3`.
- `feature/cart` still at `c2`; clean tree.

### 2.G.2 Start the invoice export from a fresh main · Easy

**Variant ID:** `gate2-easy-fresh-branch-invoices`

**Story**
Your reports branch is pushed and waiting for review. Next up is the invoice PDF export, but Maeve just pushed a tax rounding fix to `main` on `origin`. You do not want your new branch to begin without it.

**Starting point:** You are on `feature/reports` with a clean working folder. `origin/main` has a new commit that your local `main` does not have yet.

**Real-World Context**
Branching from the latest `main` means your new work is built on the code everyone else already has.

**Your Task**
Go back to `main`, bring it up to date with `origin`, then create and switch to `feature/invoice-pdf` from it.

**Objective Checklist**

- [ ] main matches origin/main, including Maeve's fix.
- [ ] feature/invoice-pdf exists, starts from the updated main and is checked out.
- [ ] feature/reports is unchanged.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Return to main.
2. `git pull origin main` — Bring in the new commit from origin.
3. `git switch -c feature/invoice-pdf` — Start the new branch here.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git pull`; `git fetch origin` then `git merge origin/main`; `git checkout -b feature/invoice-pdf`.
- Common patterns that apply: P2, P23.

**Not accepted**

- Creating the branch before updating main, or from feature/reports.

**Expected Result**
`main` and `feature/invoice-pdf` both point at the newest commit from `origin`, and you are on `feature/invoice-pdf`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- HEAD on `feature/invoice-pdf` at `c3`; `main` at `c3`; `origin/main` at `c3`.
- `feature/reports` still at `c2`; clean tree.

### 2.G.3 Update main without losing the chart work · Medium

**Variant ID:** `gate2-medium-stash-and-sync-reports`

**Story**
You are halfway through a new chart in `src/reports.py` when Sage messages: a login timeout patch just landed on `origin`, and everyone should have it on their local `main` before the demo. Your chart is not ready to commit, and you do not want to lose a line of it.

**Starting point:** You are on `feature/reports`. `src/reports.py` has uncommitted edits. `origin/main` has a new commit that your local `main` does not have yet.

**Real-World Context**
Stashing parks unfinished work so you can switch branches with a clean folder, then bring the work back exactly as it was.

**Your Task**
Set your `src/reports.py` edits aside, update your local `main` from `origin`, then return to `feature/reports` and bring the edits back. **Leave no stash entry behind.**

**Objective Checklist**

- [ ] main matches origin/main, including the login patch.
- [ ] You are back on feature/reports, which is unchanged.
- [ ] Your src/reports.py edits are back in the working folder, and the stash is empty.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Park the unfinished chart.
2. `git switch main` — Go to main.
3. `git pull origin main` — Bring in the patch.
4. `git switch feature/reports` — Return to your branch.
5. `git stash pop` — Restore the chart edits and drop the entry.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git checkout`; `git pull`; `git fetch origin` then `git merge origin/main`; `git stash apply` followed by `git stash drop`.
- Common patterns that apply: P2, P14, P23.

**Not accepted**

- Committing the unfinished chart, or discarding it.

**Expected Result**
`main` has the login patch, you are on `feature/reports`, your chart edits are back and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 10

- `main` at `c3` = `origin/main`; HEAD on `feature/reports` at `c2`.
- `src/reports.py` keeps the work-in-progress edits; stash empty; nothing staged.

### 2.G.4 Update main without losing the avatar work · Medium

**Variant ID:** `gate2-medium-stash-and-sync-profile`

**Story**
Your avatar upload in `src/profile.py` is half written when Raven asks the whole group to pull the login timeout patch onto `main` before tonight's test session. The avatar code does not even run yet, so committing it is out of the question.

**Starting point:** You are on `feature/profile`. `src/profile.py` has uncommitted edits. `origin/main` has a new commit that your local `main` does not have yet.

**Real-World Context**
A stash is the quickest safe place for unfinished edits while you deal with another branch.

**Your Task**
Set your `src/profile.py` edits aside, update your local `main` from `origin`, then return to `feature/profile` and bring the edits back. **Leave no stash entry behind.**

**Objective Checklist**

- [ ] main matches origin/main, including the login patch.
- [ ] You are back on feature/profile, which is unchanged.
- [ ] Your src/profile.py edits are back in the working folder, and the stash is empty.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git stash` — Park the unfinished avatar code.
2. `git switch main` — Go to main.
3. `git pull origin main` — Bring in the patch.
4. `git switch feature/profile` — Return to your branch.
5. `git stash pop` — Restore the avatar edits and drop the entry.

**Accepted Alternatives (STAFF ONLY)**

- `git stash push`; `git checkout`; `git pull`; `git fetch origin` then `git merge origin/main`; `git stash apply` followed by `git stash drop`.
- Common patterns that apply: P2, P14, P23.

**Not accepted**

- Committing the unfinished avatar code, or discarding it.

**Expected Result**
`main` has the login patch, you are on `feature/profile`, your avatar edits are back and the stash is empty.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 10

- `main` at `c3` = `origin/main`; HEAD on `feature/profile` at `c2`.
- `src/profile.py` keeps the work-in-progress edits; stash empty; nothing staged.

### 2.G.5 Land the search filters and retire the branch · Hard

**Variant ID:** `gate2-hard-land-and-retire-filters`

**Story**
`feature/filters` is done and approved. Raven wants it on `main` as a single commit named `Add search filters`, published, and then the branch gone, both on your machine and on `origin`, so nobody builds on it by mistake.

Sage updated the changelog on `origin` this morning, so your local `main` is behind.

**Starting point:** You are on `feature/filters`, which is pushed and tracked. Your local `main` is behind `origin/main` by one commit.

**Real-World Context**
A squash merge lands a whole branch as one tidy commit. Because the branch's own commits never join `main`, Git will not treat it as merged when you try to delete it.

**Your Task**
Update `main` from `origin`, land `feature/filters` on it as one commit with the message `Add search filters`, publish `main`, then delete `feature/filters` locally and on `origin`. Finish on `main`.

**Objective Checklist**

- [ ] main has one new commit, “Add search filters”, with the filters and the updated changelog.
- [ ] origin/main matches main.
- [ ] feature/filters no longer exists locally or on origin.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Go to main.
2. `git pull origin main` — Bring in the changelog update.
3. `git merge --squash feature/filters` — Stage the whole branch as one change.
4. `git commit -m "Add search filters"` — Record it as one commit.
5. `git push origin main` — Publish main.
6. `git branch -D feature/filters` — Delete the squashed branch locally.
7. `git push origin --delete feature/filters` — Delete it on origin.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git pull`; `git push`; `git push origin :feature/filters`; `--message` forms. The message must match exactly.
- Common patterns that apply: P2, P36, P45, P46, P47.

**Not accepted**

- A regular or `--no-ff` merge (main must get a single non-merge commit), or leaving either copy of the branch.

**Expected Result**
`main` and `origin/main` end with “Add search filters”, and `feature/filters` is gone everywhere.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 7 · Maximum counted commands: 8

- `main` has 3 commits, ending in a non-merge `Add search filters` whose tree has the filters and the new changelog; `origin/main` = `main`.
- `feature/filters` absent locally and on origin; clean tree.

### 2.G.6 Land the CSV export and retire the branch · Hard

**Variant ID:** `gate2-hard-land-and-retire-export`

**Story**
The CSV export on `feature/export` passed review. Maeve wants it on `main` as one commit, Add CSV export, then published, and the branch removed from your machine and from `origin`.

The changelog moved on `origin` since you last updated, so `main` needs updating first.

**Starting point:** You are on `feature/export`, which is pushed and tracked. Your local `main` is behind `origin/main` by one commit.

**Real-World Context**
Squash, publish, and clean up is the end of most feature branches. A squashed branch still looks unmerged to Git, so it needs a forced local delete.

**Your Task**
Update `main` from `origin`, land `feature/export` on it as one commit with the message `Add CSV export`, publish `main`, then delete `feature/export` locally and on `origin`. Finish on `main`.

**Objective Checklist**

- [ ] main has one new commit, “Add CSV export”, with the export and the updated changelog.
- [ ] origin/main matches main.
- [ ] feature/export no longer exists locally or on origin.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch main` — Go to main.
2. `git pull origin main` — Bring in the changelog update.
3. `git merge --squash feature/export` — Stage the whole branch as one change.
4. `git commit -m "Add CSV export"` — Record it as one commit.
5. `git push origin main` — Publish main.
6. `git branch -D feature/export` — Delete the squashed branch locally.
7. `git push origin --delete feature/export` — Delete it on origin.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout main`; `git pull`; `git push`; `git push origin :feature/export`; `--message` forms. The message must match exactly.
- Common patterns that apply: P2, P36, P45, P46, P47.

**Not accepted**

- A regular or `--no-ff` merge (main must get a single non-merge commit), or leaving either copy of the branch.

**Expected Result**
`main` and `origin/main` end with “Add CSV export”, and `feature/export` is gone everywhere.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 7 · Maximum counted commands: 8

- `main` has 3 commits, ending in a non-merge `Add CSV export` whose tree has the export and the new changelog; `origin/main` = `main`.
- `feature/export` absent locally and on origin; clean tree.

## Module 3 Challenge Gate — Conflict Gate

### 3.G.1 Merge the banner, then backport the checkout fix · Easy

**Variant ID:** `gate3-easy-merge-then-backport-banner`

**Story**
`feature/banner` reworded the welcome banner, and `main` reworded it differently last week. Sage has decided on the final wording and wants the branch merged with *exactly that text*, using Git's prepared merge message.

There is a second job. `main` also has “Fix checkout total”, and the store's `release/1.4` branch needs that fix today, without the banner work.

**Starting point:** You are on `main`. `feature/banner` and `main` both changed `src/banner.html` since they split. “Fix checkout total” is the latest commit on `main`, and `release/1.4` has not moved since the common base.

**Real-World Context**
Conflict work rarely ends at the merge. A fix that landed on `main` often has to reach a release branch too, and copying just that commit keeps unfinished work off the release.

**Your Task**
Merge `feature/banner` into `main`, resolve `src/banner.html` to the content below, and complete the merge with its prepared message. Then copy __only__ “Fix checkout total” onto `release/1.4`. Finish on `release/1.4`.

**Required resolved file content**

`src/banner.html`

```
<p>Welcome back, team!</p>
```

**Objective Checklist**

- [ ] main has a merge commit with feature/banner as a parent.
- [ ] src/banner.html on main contains exactly the required content.
- [ ] release/1.4 has a copy of “Fix checkout total” and nothing else new.
- [ ] You are on release/1.4 with no conflicts and a clean working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge feature/banner` — Start the merge; it stops on the conflict.
2. In the simulator's file editor, set `src/banner.html` to exactly:

   ```
   <p>Welcome back, team!</p>
   ```
3. `git add src/banner.html` — Mark the file resolved.
4. `git commit --no-edit` — Complete the merge.
5. `git switch release/1.4` — Go to the release branch.
6. `git cherry-pick c3` — Copy only the checkout fix.

**Accepted Alternatives (STAFF ONLY)**

- `git merge --continue` instead of the merge commit, or `git commit -m` with any message; `git cherry-pick -x c3`; copying the fix before the merge, as long as you finish on `release/1.4`.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- Merging `main` or `feature/banner` into `release/1.4`, or copying the banner commits to it.

**Expected Result**
`main` has a merge commit joining `feature/banner` with the agreed banner text, and `release/1.4` has its own copy of “Fix checkout total”.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- `main` tip is a merge with parent `c2`; its tree has the required `src/banner.html` and the fixed `src/checkout.js`.
- HEAD on `release/1.4`; two commits; tip message contains `Fix checkout total`; its tree has the fixed checkout and the base banner.
- No conflicts; clean tree.

### 3.G.2 Merge the footer, then backport the tax fix · Easy

**Variant ID:** `gate3-easy-merge-then-backport-footer`

**Story**
`feature/footer` rewrote the support footer while `main` changed the same line. Raven has picked the final text and wants the branch merged with *exactly that footer*, using Git's prepared merge message.

Then the billing team asks for “Fix tax rounding”, already on `main`, on `release/2.0` before the invoices go out, without the footer work.

**Starting point:** You are on `main`. `feature/footer` and `main` both changed `src/footer.html` since they split. “Fix tax rounding” is the latest commit on `main`, and `release/2.0` has not moved since the common base.

**Real-World Context**
Conflict work rarely ends at the merge. A fix that landed on `main` often has to reach a release branch too, and copying just that commit keeps unfinished work off the release.

**Your Task**
Merge `feature/footer` into `main`, resolve `src/footer.html` to the content below, and complete the merge with its prepared message. Then copy __only__ “Fix tax rounding” onto `release/2.0`. Finish on `release/2.0`.

**Required resolved file content**

`src/footer.html`

```
<footer>Contact support</footer>
```

**Objective Checklist**

- [ ] main has a merge commit with feature/footer as a parent.
- [ ] src/footer.html on main contains exactly the required content.
- [ ] release/2.0 has a copy of “Fix tax rounding” and nothing else new.
- [ ] You are on release/2.0 with no conflicts and a clean working folder.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge feature/footer` — Start the merge; it stops on the conflict.
2. In the simulator's file editor, set `src/footer.html` to exactly:

   ```
   <footer>Contact support</footer>
   ```
3. `git add src/footer.html` — Mark the file resolved.
4. `git commit --no-edit` — Complete the merge.
5. `git switch release/2.0` — Go to the release branch.
6. `git cherry-pick c3` — Copy only the tax fix.

**Accepted Alternatives (STAFF ONLY)**

- `git merge --continue` instead of the merge commit, or `git commit -m` with any message; `git cherry-pick -x c3`; copying the fix before the merge, as long as you finish on `release/2.0`.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- Merging `main` or `feature/footer` into `release/2.0`, or copying the footer commits to it.

**Expected Result**
`main` has a merge commit joining `feature/footer` with the agreed footer text, and `release/2.0` has its own copy of “Fix tax rounding”.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 12

- `main` tip is a merge with parent `c2`; its tree has the required `src/footer.html` and the fixed `src/invoice.js`.
- HEAD on `release/2.0`; two commits; tip message contains `Fix tax rounding`; its tree has the fixed invoice and the base footer.
- No conflicts; clean tree.

### 3.G.3 Backport the tax fix with its origin noted · Medium

**Variant ID:** `gate3-medium-backport-tax`

**Story**
Customers on `release/2.1` are being charged a few cents too much, and the fix, “Round tax per line”, already sits on `main`.

Maeve wants just that commit on the release branch, with a note saying where it came from so the auditors can trace it. The release branch has its own tax tweak, so expect a conflict.

**Starting point:** You are on `main`. The fix is the latest commit on `main` (`c3`). `release/2.1` changed `src/tax.py` differently.

**Real-World Context**
Cherry-picking copies one fix to another branch without bringing anything else. Recording the source commit makes the copy traceable, and a conflict on the way is resolved like any other.

**Your Task**
On `release/2.1`, apply `main`'s latest commit while recording its origin, resolve `src/tax.py` to the content below, and finish the cherry-pick. **`main` must stay as it is.**

**Required resolved file content**

`src/tax.py`

```
ROUND_PER_LINE = True
```

**Objective Checklist**

- [ ] release/2.1 has one new commit, “Round tax per line”, noting it was cherry-picked from c3.
- [ ] src/tax.py on release/2.1 contains exactly the required content.
- [ ] main is unchanged and no cherry-pick is in progress.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release/2.1` — Go to the release branch.
2. `git cherry-pick -x c3` — Copy the fix and record its origin; it stops on the conflict.
3. In the simulator's file editor, set `src/tax.py` to exactly:

   ```
   ROUND_PER_LINE = True
   ```
4. `git add src/tax.py` — Mark the file resolved.
5. `git cherry-pick --continue` — Finish the copy.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout release/2.1`; `git cherry-pick -x main` (main points at c3).
- Common patterns that apply: P26, P27, P28.

**Not accepted**

- A cherry-pick without `-x` (the origin note is required), merging main into the release branch, or copying more than the one commit.

**Expected Result**
`release/2.1` ends with “Round tax per line” and its cherry-pick note, with the resolved tax file. `main` still ends at `c3`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `release/2.1` with 3 commits; tip message contains `Round tax per line` and `cherry picked from commit c3`; tree `src/tax.py` = the required content.
- `main` still at `c3`; no cherry-pick in progress; clean tree.

### 3.G.4 Backport the date format fix with its origin noted · Medium

**Variant ID:** `gate3-medium-backport-locale`

**Story**
Users on `release/3.0` in the Philippines are seeing dates in the wrong order. “Fix date format for fil-PH” is the latest commit on `main`.

Raven wants it on `release/3.0`, traceable to its source, and nothing else from `main`. The release branch touched `src/locale.py` too.

**Starting point:** You are on `main`. The fix is the latest commit on `main` (`c3`). `release/3.0` changed `src/locale.py` differently.

**Real-World Context**
Backports should be small and traceable. The cherry-pick note tells reviewers which `main` commit a release fix came from.

**Your Task**
On `release/3.0`, apply `main`'s latest commit while recording its origin, resolve `src/locale.py` to the content below, and finish the cherry-pick. **`main` must stay as it is.**

**Required resolved file content**

`src/locale.py`

```
DATE_FORMAT = 'MM/DD/YYYY'
```

**Objective Checklist**

- [ ] release/3.0 has one new commit, “Fix date format for fil-PH”, noting it was cherry-picked from c3.
- [ ] src/locale.py on release/3.0 contains exactly the required content.
- [ ] main is unchanged and no cherry-pick is in progress.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git switch release/3.0` — Go to the release branch.
2. `git cherry-pick -x c3` — Copy the fix and record its origin; it stops on the conflict.
3. In the simulator's file editor, set `src/locale.py` to exactly:

   ```
   DATE_FORMAT = 'MM/DD/YYYY'
   ```
4. `git add src/locale.py` — Mark the file resolved.
5. `git cherry-pick --continue` — Finish the copy.

**Accepted Alternatives (STAFF ONLY)**

- `git checkout release/3.0`; `git cherry-pick -x main` (main points at c3).
- Common patterns that apply: P26, P27, P28.

**Not accepted**

- A cherry-pick without `-x`, merging main into the release branch, or copying more than the one commit.

**Expected Result**
`release/3.0` ends with “Fix date format for fil-PH” and its cherry-pick note, with the resolved locale file. `main` still ends at `c3`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 4 · Maximum counted commands: 10

- HEAD on `release/3.0` with 3 commits; tip message contains `Fix date format for fil-PH` and `cherry picked from commit c3`; tree `src/locale.py` = the required content.
- `main` still at `c3`; no cherry-pick in progress; clean tree.

### 3.G.5 Back out the wrong merge and use the team's tool · Hard

**Variant ID:** `gate3-hard-abort-then-tool-merge-pricing`

**Story**
You started merging `feature/old-pricing` into `main` before Sage reminded you that it was replaced by `feature/pricing-v2`. The merge has stopped on a conflict in `src/prices.py`.

Sage also wants this one resolved in `meld`, the group's merge tool, which you have not set up yet. **The wrong branch must leave no trace on `main`.**

**Starting point:** You are on `main` with a stopped merge of `feature/old-pricing`. `feature/pricing-v2` also changes `src/prices.py`.

**Real-World Context**
A merge of the wrong branch should be abandoned, not resolved. Configuring the merge tool once means every later conflict opens in it.

**Your Task**
Abandon the stopped merge, set `meld` as the merge tool, merge `feature/pricing-v2`, resolve `src/prices.py` in the merge tool to the content below, and complete the merge with its prepared message. Finish on `main`.

**Required resolved file content**

`src/prices.py`

```
PRICE_TIERS = ['basic', 'pro']
```

**Objective Checklist**

- [ ] main has a merge commit with feature/pricing-v2 as a parent.
- [ ] feature/old-pricing is not part of main's history.
- [ ] src/prices.py contains exactly the required content, and meld is the repository's merge tool.
- [ ] No conflicts remain and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --abort` — Abandon the wrong merge.
2. `git config merge.tool meld` — Set the team's merge tool.
3. `git merge feature/pricing-v2` — Merge the right branch; it stops on the conflict.
4. `git mergetool` — Open the conflict in meld.
5. In the simulator's merge tool, set `src/prices.py` to exactly:

   ```
   PRICE_TIERS = ['basic', 'pro']
   ```
6. `git commit --no-edit` — Complete the merge.

**Accepted Alternatives (STAFF ONLY)**

- `git config --global merge.tool meld`; `git mergetool --tool=meld` after setting the tool; `git merge --continue` instead of the final commit.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Not accepted**

- Resolving and committing the old-pricing merge.

**Expected Result**
`main` has a merge commit joining `feature/pricing-v2` with the agreed prices, and `feature/old-pricing` never reached `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge with parent `c3`; history excludes `c2`; tree `src/prices.py` = the required content.
- `merge.tool` = `meld`; no conflicts; clean tree.

### 3.G.6 Back out the wrong merge and use the team's tool · Hard

**Variant ID:** `gate3-hard-abort-then-tool-merge-copy`

**Story**
Halfway through merging `feature/draft-copy` you realise it is the abandoned draft; the approved wording lives on `feature/checkout-copy`. The merge has stopped on `src/checkout.js`.

Raven wants the right branch merged and the conflict resolved in `meld`, which the group standardised on, and which your machine is not configured for yet.

**Starting point:** You are on `main` with a stopped merge of `feature/draft-copy`. `feature/checkout-copy` also changes `src/checkout.js`.

**Real-World Context**
Abort first, then merge what you meant to merge. Setting the tool in config saves everyone from guessing which editor a conflict will open in.

**Your Task**
Abandon the stopped merge, set `meld` as the merge tool, merge `feature/checkout-copy`, resolve `src/checkout.js` in the merge tool to the content below, and complete the merge with its prepared message. Finish on `main`.

**Required resolved file content**

`src/checkout.js`

```
const label = 'Place order'
```

**Objective Checklist**

- [ ] main has a merge commit with feature/checkout-copy as a parent.
- [ ] feature/draft-copy is not part of main's history.
- [ ] src/checkout.js contains exactly the required content, and meld is the repository's merge tool.
- [ ] No conflicts remain and the working folder is clean.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge --abort` — Abandon the wrong merge.
2. `git config merge.tool meld` — Set the team's merge tool.
3. `git merge feature/checkout-copy` — Merge the right branch; it stops on the conflict.
4. `git mergetool` — Open the conflict in meld.
5. In the simulator's merge tool, set `src/checkout.js` to exactly:

   ```
   const label = 'Place order'
   ```
6. `git commit --no-edit` — Complete the merge.

**Accepted Alternatives (STAFF ONLY)**

- `git config --global merge.tool meld`; `git mergetool --tool=meld` after setting the tool; `git merge --continue` instead of the final commit.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Not accepted**

- Resolving and committing the draft-copy merge.

**Expected Result**
`main` has a merge commit joining `feature/checkout-copy` with the approved label, and `feature/draft-copy` never reached `main`.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 5 · Maximum counted commands: 8

- HEAD on `main`; tip is a merge with parent `c3`; history excludes `c2`; tree `src/checkout.js` = the required content.
- `merge.tool` = `meld`; no conflicts; clean tree.

## Module 4 Challenge Gate — Recovery Gate

### 4.G.1 Rescue the search work and send it for review · Easy

**Variant ID:** `gate4-easy-recover-replay-publish-search`

**Story**
Yesterday you made two commits on `main` for the borrower search, “Start search” and “Fix borrower search”. Then you ran `git reset --hard origin/main` to pick up Maeve's login patch, and both commits vanished from `main`.

Sage still needs the search fix for tomorrow's demo, reviewed on its own branch against the current code. Git remembers where `HEAD` has been.

**Starting point:** You are on `main`, which matches `origin/main` and its “Patch login timeout” commit. Your two search commits are only in the reflog.

**Real-World Context**
Lost commits are not gone while the reflog remembers them. Once they are safe on a branch, replaying them onto the current `main` lets reviewers read them against the code that will actually ship.

**Your Task**
Create `recovery/search` at your lost “Fix borrower search” commit, replay the branch onto `main`, and publish it to `origin` for review. **Leave `main` where it is.**

**Objective Checklist**

- [ ] recovery/search holds both search commits, replayed on top of main.
- [ ] origin/recovery/search matches your local branch.
- [ ] main still points at “Patch login timeout”.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the lost commits.
2. `git switch -c recovery/search c2` — Save them on a new branch.
3. `git rebase main` — Replay them onto the current main.
4. `git push -u origin recovery/search` — Publish the branch for review.

**Accepted Alternatives (STAFF ONLY)**

- `git log -g`; `git branch recovery/search c2` then `git switch recovery/search`; `git rebase main recovery/search`; a new branch from `main` with `git cherry-pick c1` then `git cherry-pick c2`; `git push origin recovery/search` without `-u`.
- Common patterns that apply: P21, P22.

**Not accepted**

- Resetting or moving `main`, or publishing only one of the two search commits.

**Expected Result**
`recovery/search` holds “Start search” and “Fix borrower search” on top of `main`, and `origin` has the same branch. `main` has not moved.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- HEAD on `recovery/search`; four commits including `c3`, without the original `c1` and `c2`; tip `Fix borrower search` with the search fix and the login patch.
- `origin/recovery/search` matches the branch; `main` still at `c3`; clean tree.

### 4.G.2 Rescue the receipts work and send it for review · Easy

**Variant ID:** `gate4-easy-recover-replay-publish-receipts`

**Story**
Yesterday you made two commits on `main` for the receipts screen, “Start receipts” and “Fix receipt totals”. Then you ran `git reset --hard origin/main` to pick up Raven's tax patch, and both commits vanished from `main`.

The shop needs the receipt fix reviewed before Friday's release, on its own branch against the current code. Git remembers where `HEAD` has been.

**Starting point:** You are on `main`, which matches `origin/main` and its “Patch tax rate” commit. Your two receipts commits are only in the reflog.

**Real-World Context**
Lost commits are not gone while the reflog remembers them. Once they are safe on a branch, replaying them onto the current `main` lets reviewers read them against the code that will actually ship.

**Your Task**
Create `recovery/receipts` at your lost “Fix receipt totals” commit, replay the branch onto `main`, and publish it to `origin` for review. **Leave `main` where it is.**

**Objective Checklist**

- [ ] recovery/receipts holds both receipts commits, replayed on top of main.
- [ ] origin/recovery/receipts matches your local branch.
- [ ] main still points at “Patch tax rate”.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reflog` — Find the lost commits.
2. `git switch -c recovery/receipts c2` — Save them on a new branch.
3. `git rebase main` — Replay them onto the current main.
4. `git push -u origin recovery/receipts` — Publish the branch for review.

**Accepted Alternatives (STAFF ONLY)**

- `git log -g`; `git branch recovery/receipts c2` then `git switch recovery/receipts`; `git rebase main recovery/receipts`; a new branch from `main` with `git cherry-pick c1` then `git cherry-pick c2`; `git push origin recovery/receipts` without `-u`.
- Common patterns that apply: P21, P22.

**Not accepted**

- Resetting or moving `main`, or publishing only one of the two receipts commits.

**Expected Result**
`recovery/receipts` holds “Start receipts” and “Fix receipt totals” on top of `main`, and `origin` has the same branch. `main` has not moved.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 12

- HEAD on `recovery/receipts`; four commits including `c3`, without the original `c1` and `c2`; tip `Fix receipt totals` with the receipts fix and the tax patch.
- `origin/recovery/receipts` matches the branch; `main` still at `c3`; clean tree.

### 4.G.3 Drop the experiment, reverse the published banner · Medium

**Variant ID:** `gate4-medium-drop-local-revert-published-banner`

**Story**
“Add discount banner” went out to `origin` yesterday and broke the storefront layout. On top of it you have a local, unpushed commit, “Try banner animation”, that nobody wants.

Raven's instructions: throw the local experiment away completely, but undo the published banner without rewriting what the team already pulled.

**Starting point:** You are on `main`. “Add discount banner” (`c2`) is on `origin`; “Try banner animation” (`c3`) is local only.

**Real-World Context**
Unpublished commits can be discarded by moving the branch back. Published ones must be reversed with a new commit, because teammates already have them.

**Your Task**
Remove the local experiment from `main`, reverse the published banner commit with a new commit, and publish `main`. Finish on `main`.

**Objective Checklist**

- [ ] “Try banner animation” is no longer on main.
- [ ] “Add discount banner” is still in history, and a new commit reverses it.
- [ ] origin/main matches main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reset --hard c2` — Discard the local experiment.
2. `git revert c2` — Reverse the published banner with a new commit.
3. `git push origin main` — Publish the reversal.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --hard HEAD~1` or `origin/main`; `git revert --no-edit c2`; `git push`.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- Resetting past c2 and force-pushing (rewrites published history), or reverting the local experiment instead of dropping it.

**Expected Result**
`main` and `origin/main` end with a commit that reverses the banner; the experiment is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- `main` has 3 commits; history contains `c2` and excludes `c3`; tree restores the banner file and has no `docs/notes.md`.
- `origin/main` = `main`; clean tree.

### 4.G.4 Drop the experiment, reverse the published alert change · Medium

**Variant ID:** `gate4-medium-drop-local-revert-published-alerts`

**Story**
“Page on every warning” is live on `origin` and has woken the on-call engineer four times tonight. You also have a local commit, “Experiment with alert sounds”, that should never see the light of day.

Sage wants the experiment gone and the paging change reversed in a way that leaves the shared history intact.

**Starting point:** You are on `main`. “Page on every warning” (`c2`) is on `origin`; “Experiment with alert sounds” (`c3`) is local only.

**Real-World Context**
Reset for what only you have; revert for what everyone has. Mixing them up either loses work or breaks teammates' history.

**Your Task**
Remove the local experiment from `main`, reverse the published alert commit with a new commit, and publish `main`. Finish on `main`.

**Objective Checklist**

- [ ] “Experiment with alert sounds” is no longer on main.
- [ ] “Page on every warning” is still in history, and a new commit reverses it.
- [ ] origin/main matches main.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git reset --hard c2` — Discard the local experiment.
2. `git revert c2` — Reverse the published change with a new commit.
3. `git push origin main` — Publish the reversal.

**Accepted Alternatives (STAFF ONLY)**

- `git reset --hard HEAD~1` or `origin/main`; `git revert --no-edit c2`; `git push`.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- Resetting past c2 and force-pushing, or reverting the local experiment instead of dropping it.

**Expected Result**
`main` and `origin/main` end with a commit that reverses the paging change; the experiment is gone.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 10

- `main` has 3 commits; history contains `c2` and excludes `c3`; tree restores the alerts file and has no `docs/notes.md`.
- `origin/main` = `main`; clean tree.

### 4.G.5 Move the receipts branch off the release line · Hard

**Variant ID:** `gate4-hard-move-branch-onto-main-receipts`

**Story**
`feature/receipts` was started from `release/1.0` by mistake, and it is already pushed. You tried to rebase it onto `main`, and Git stopped on a release-only fix that does not belong in your branch at all.

Raven wants only your two receipt commits on top of `main`, and the pushed branch updated without clobbering anything a teammate might have added.

**Starting point:** You are on `feature/receipts` in the middle of a stopped rebase onto `main`. Your branch was started from `release/1.0` and is already pushed to `origin`.

**Real-World Context**
A plain rebase replays everything since the branches split, including commits that came from the wrong base. Aborting and rebasing only your range moves exactly your work, and a lease-protected push replaces the old branch safely.

**Your Task**
Abandon the stopped rebase, move __only__ the commits made on `feature/receipts` after `release/1.0` onto `main`, and update `origin`'s copy of the branch safely. Finish on `feature/receipts`.

**Objective Checklist**

- [ ] No rebase is in progress.
- [ ] feature/receipts holds main plus your two receipt commits, and none of release/1.0's fixes.
- [ ] origin/feature/receipts matches the moved branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git rebase --abort` — Leave the wrong rebase.
2. `git rebase --onto main release/1.0 feature/receipts` — Replay only your commits onto main.
3. `git push --force-with-lease origin feature/receipts` — Replace the pushed branch safely.

**Accepted Alternatives (STAFF ONLY)**

- `git rebase --onto main release/1.0` while on the branch; `git push --force-with-lease`.
- Common patterns that apply: P49.

**Not accepted**

- Continuing the stopped rebase (it would carry release/1.0's fix), `git push --force` without a lease, or a merge.

**Expected Result**
`feature/receipts` is `main` plus the two receipt commits, and `origin` has the same branch.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/receipts` with 4 commits; history contains `c2`, excludes `c1`; tree has the receipts file and main's `src/app.py`.
- No rebase in progress; `origin/feature/receipts` = the branch; clean tree.

### 4.G.6 Move the coupons branch off the release line · Hard

**Variant ID:** `gate4-hard-move-branch-onto-main-coupons`

**Story**
You built `feature/coupons` on `release/1.0` by accident and pushed it. Your attempt to rebase it onto `main` stopped on a release-only fix.

Sage needs the coupon work on top of `main` for the promo launch, without the release fix, and wants the pushed branch replaced safely in case someone else touched it.

**Starting point:** You are on `feature/coupons` in the middle of a stopped rebase onto `main`. Your branch was started from `release/1.0` and is already pushed to `origin`.

**Real-World Context**
Moving a branch to a new base is two steps: get out of the bad rebase, then replay only your own range. Publishing rewritten history needs a lease so you cannot overwrite unseen work.

**Your Task**
Abandon the stopped rebase, move __only__ the commits made on `feature/coupons` after `release/1.0` onto `main`, and update `origin`'s copy of the branch safely. Finish on `feature/coupons`.

**Objective Checklist**

- [ ] No rebase is in progress.
- [ ] feature/coupons holds main plus your two coupon commits, and none of release/1.0's fixes.
- [ ] origin/feature/coupons matches the moved branch.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git rebase --abort` — Leave the wrong rebase.
2. `git rebase --onto main release/1.0 feature/coupons` — Replay only your commits onto main.
3. `git push --force-with-lease origin feature/coupons` — Replace the pushed branch safely.

**Accepted Alternatives (STAFF ONLY)**

- `git rebase --onto main release/1.0` while on the branch; `git push --force-with-lease`.
- Common patterns that apply: P49.

**Not accepted**

- Continuing the stopped rebase, `git push --force` without a lease, or a merge.

**Expected Result**
`feature/coupons` is `main` plus the two coupon commits, and `origin` has the same branch.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 3 · Maximum counted commands: 8

- HEAD on `feature/coupons` with 4 commits; history contains `c2`, excludes `c1`; tree has the coupons file and main's `src/app.py`.
- No rebase in progress; `origin/feature/coupons` = the branch; clean tree.

# Taught vs. accepted alternative Git solutions

This reference covers **311 published variants** with **832 distinct accepted alternative routes**, grouped by gameplay mode and level.

Source: the checked-in executable audit (`backend/curriculum/seed_data/solution_audit.json`). The taught solution below is the authored example for that exact variant. Alternatives include both equivalent syntax and different workflows.

Only routes marked accepted by the audit are included. Those routes passed simulator execution, backend transition verification, objective evaluation, and required-technique checks when the audit was generated. This document summarizes that audit; it does not claim every possible Git command is supported or that every route was manually demonstrated in a browser.

Branch names, paths, commit messages, and required file content belong to the listed variant. Do not substitute commands between variants without checking their objectives. Each command block is one complete route, in execution order. Costs are counted commands, not star targets. File edits are free, and their timing is specified below.

Variants with only one verified route and unpublished content are excluded. An omission means no alternative is verified in this audit, not that Git itself has no alternative.

## Level index

- [Story: initializing-a-local-repository](#level-1) — 16 variants
- [Story: cloning-a-remote-repository](#level-2) — 6 variants
- [Story: staging-and-committing-basic-workflow](#level-3) — 16 variants
- [Story: partial-staging-and-git-add-p](#level-4) — 17 variants
- [Story: amending-commits](#level-5) — 17 variants
- [Story: unstaging-and-discarding-changes](#level-6) — 16 variants
- [Story: creating-and-switching-branches](#level-7) — 17 variants
- [Story: branch-naming-and-housekeeping](#level-8) — 19 variants
- [Story: stashing-work-in-progress](#level-9) — 18 variants
- [Story: pushing-to-a-remote](#level-10) — 12 variants
- [Story: fetching-and-pulling](#level-11) — 8 variants
- [Story: reconciling-diverged-histories](#level-12) — 13 variants
- [Story: completing-branch-merges](#level-13) — 12 variants
- [Story: squash-merging](#level-14) — 19 variants
- [Story: deleting-and-recovering-remote-branches](#level-15) — 15 variants
- [Story: resolving-conflicts-manually](#level-16) — 15 variants
- [Story: using-a-merge-tool](#level-17) — 2 variants
- [Story: cherry-picking-commits](#level-18) — 13 variants
- [Story: recovering-from-hard-resets](#level-19) — 17 variants
- [Story: reversing-pushed-commits-safely](#level-20) — 6 variants
- [Story: completing-rebase-recovery-sequences](#level-21) — 13 variants
- [Challenge: module-1-challenge-gate](#level-22) — 6 variants
- [Challenge: module-2-challenge-gate](#level-23) — 6 variants
- [Challenge: module-3-challenge-gate](#level-24) — 6 variants
- [Challenge: module-4-challenge-gate](#level-25) — 6 variants
<a id="level-1"></a>
## Story: initializing-a-local-repository

### init-easy-plain-notes

**Difficulty:** Easy  
**Scenario:** start-tracking-this-folder  
**Alternative category:** syntax alternatives

**Objective**

Turn the current folder into a Git repository.

**Do not stage or commit `notes.md`.**

**Taught / authored example — 1 counted command**

```sh
git init
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init .
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init -b main
```

### init-easy-plain-recipes

**Difficulty:** Easy  
**Scenario:** start-tracking-this-folder  
**Alternative category:** syntax alternatives

**Objective**

Turn the current folder into a Git repository.

**Do not stage or commit `recipes.md`.**

**Taught / authored example — 1 counted command**

```sh
git init
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init .
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init -b main
```

### init-easy-current-empty

**Difficulty:** Easy  
**Scenario:** track-this-folder  
**Alternative category:** syntax alternatives

**Objective**

Initialize the current directory as a Git repository, explicitly choosing `main` as its initial branch during initialization.

**Do not stage files or create a commit.**

**Required technique:** `git init -b main` (or `--initial-branch`) when the repository is created. Plain `git init`, renaming the branch afterwards, or reinitializing does not complete this variant.

**Taught / authored example — 1 counted command**

```sh
git init -b main
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init --initial-branch=main
```

### init-easy-trunk-branch

**Difficulty:** Easy  
**Scenario:** track-this-folder  
**Alternative category:** syntax alternatives

**Objective**

Initialize the current directory as a Git repository with `trunk` as its initial branch.

**Taught / authored example — 1 counted command**

```sh
git init --initial-branch=trunk
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init -b trunk
```

### init-easy-invoice

**Difficulty:** Easy  
**Scenario:** new-project-folder  
**Alternative category:** syntax alternatives

**Objective**

Create a new `invoice-tracker` folder that is a Git repository, with `main` as its first branch.

**Taught / authored example — 1 counted command**

```sh
git init -b main invoice-tracker
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main invoice-tracker
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init invoice-tracker
```

### init-med-oss

**Difficulty:** Easy  
**Scenario:** new-project-folder  
**Alternative category:** syntax alternatives

**Objective**

Create a new `oss-contrib` folder that is a Git repository, with `main` as its first branch.

**Taught / authored example — 1 counted command**

```sh
git init -b main oss-contrib
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main oss-contrib
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init oss-contrib
```

### init-hard-ci

**Difficulty:** Easy  
**Scenario:** new-folder-among-other-files  
**Alternative category:** syntax alternatives

**Objective**

Create a repository in a new `ci-configs` folder, with `main` as its first branch.

**Leave every other file in the workspace where it is.**

**Taught / authored example — 1 counted command**

```sh
git init -b main ci-configs
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main ci-configs
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init ci-configs
```

### init-easy-new-folder-among-files

**Difficulty:** Easy  
**Scenario:** new-folder-among-other-files  
**Alternative category:** syntax alternatives

**Objective**

Create a repository in a new `site-assets` folder with `main` as its first branch.

**Leave `design/logo.svg` where it is.**

**Taught / authored example — 1 counted command**

```sh
git init -b main site-assets
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main site-assets
```

### init-medium-docs-site

**Difficulty:** Medium  
**Scenario:** folder-and-branch-from-brief  
**Alternative category:** syntax alternatives

**Objective**

Create a new `docs-site` folder that is a Git repository, with `main` as its first branch.

**Taught / authored example — 1 counted command**

```sh
git init -b main docs-site
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main docs-site
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init docs-site
```

### init-medium-trunk-api-playground

**Difficulty:** Medium  
**Scenario:** folder-and-branch-from-brief  
**Alternative category:** syntax alternatives

**Objective**

Create a new `api-playground` folder that is a Git repository, with `trunk` as its first branch.

**Taught / authored example — 1 counted command**

```sh
git init -b trunk api-playground
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch trunk api-playground
```

### init-medium-existing-files

**Difficulty:** Medium  
**Scenario:** existing-files-stay-untracked  
**Alternative category:** syntax alternatives

**Objective**

Make the existing `field-notes` folder a Git repository with `main` as its first branch.

**Do not stage or commit its files.**

**Taught / authored example — 1 counted command**

```sh
git init -b main field-notes
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main field-notes
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init field-notes
```

### init-medium-existing-sketches

**Difficulty:** Medium  
**Scenario:** existing-files-stay-untracked  
**Alternative category:** syntax alternatives

**Objective**

Make the existing `sketches` folder a Git repository with `main` as its first branch.

**Do not stage or commit its files.**

**Taught / authored example — 1 counted command**

```sh
git init -b main sketches
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main sketches
```

### init-hard-research-log

**Difficulty:** Hard  
**Scenario:** only-the-right-subfolder  
**Alternative category:** syntax alternatives

**Objective**

Initialize only the `research-log` subfolder as a Git repository with `main` as its initial branch.

**Leave the parent folder and the sibling folders outside the repository.**

**Taught / authored example — 1 counted command**

```sh
git init -b main research-log
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main research-log
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init research-log
```

### init-hard-ui-kit

**Difficulty:** Hard  
**Scenario:** only-the-right-subfolder  
**Alternative category:** syntax alternatives

**Objective**

Initialize only the `ui-kit` subfolder as a Git repository with `trunk` as its initial branch.

**Leave the parent and sibling folders untouched.**

**Taught / authored example — 1 counted command**

```sh
git init --initial-branch=trunk ui-kit
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init -b trunk ui-kit
```

### init-hard-nested-service

**Difficulty:** Hard  
**Scenario:** nested-project-folder  
**Alternative category:** syntax alternatives

**Objective**

Make `services/billing-api`, and __only__ that folder, a Git repository whose first branch follows the team's convention.

**Do not stage or commit anything.**

**Taught / authored example — 1 counted command**

```sh
git init -b trunk services/billing-api
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch trunk services/billing-api
```

### init-hard-nested-course

**Difficulty:** Hard  
**Scenario:** nested-project-folder  
**Alternative category:** syntax alternatives

**Objective**

Make `courses/git-basics`, and __only__ that folder, a Git repository with `main` as its first branch.

**Do not stage or commit anything.**

**Taught / authored example — 1 counted command**

```sh
git init -b main courses/git-basics
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git init --initial-branch main courses/git-basics
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git init courses/git-basics
```

<a id="level-2"></a>
## Story: cloning-a-remote-repository

### clone-easy-profile-starter

**Difficulty:** Easy  
**Scenario:** clone-a-specific-branch  
**Alternative category:** syntax alternatives

**Objective**

Clone the remote repository from `https://example.test/training/profile-site.git` with `starter` checked out.

**Taught / authored example — 1 counted command**

```sh
git clone -b starter https://example.test/training/profile-site.git
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone --branch starter https://example.test/training/profile-site.git
```

### clone-med-feature

**Difficulty:** Easy  
**Scenario:** clone-a-specific-branch  
**Alternative category:** syntax alternatives

**Objective**

Clone the remote repository from `https://github.com/acme-startup/backend-api.git` with `feature/auth` checked out.

**Taught / authored example — 1 counted command**

```sh
git clone -b feature/auth https://github.com/acme-startup/backend-api.git
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone --branch feature/auth https://github.com/acme-startup/backend-api.git
```

### clone-medium-cli-starter-folder

**Difficulty:** Easy  
**Scenario:** branch-into-named-folder  
**Alternative category:** syntax alternatives

**Objective**

Clone the remote repository from `https://example.test/tools/cli-tool.git` into a local folder named `cli-starter-lab` with `starter` checked out.

**Taught / authored example — 1 counted command**

```sh
git clone --branch starter https://example.test/tools/cli-tool.git cli-starter-lab
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone -b starter https://example.test/tools/cli-tool.git cli-starter-lab
```

### clone-easy-branch-folder-handbook

**Difficulty:** Easy  
**Scenario:** branch-into-named-folder  
**Alternative category:** syntax alternatives

**Objective**

Clone `https://example.test/docs/handbook.git` into a local folder named `handbook-draft` with `draft` checked out.

**Taught / authored example — 1 counted command**

```sh
git clone -b draft https://example.test/docs/handbook.git handbook-draft
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone --branch draft https://example.test/docs/handbook.git handbook-draft
```

### clone-hard-mobile-ui-shallow-branch

**Difficulty:** Hard  
**Scenario:** shallow-copy-of-one-branch  
**Alternative category:** syntax alternatives

**Objective**

Clone the remote repository from `https://example.test/frontend/mobile-ui.git` into a local folder named `mobile-ui-lab` with `starter` checked out using a history depth of 1.

**Taught / authored example — 1 counted command**

```sh
git clone --depth 1 -b starter https://example.test/frontend/mobile-ui.git mobile-ui-lab
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone --depth 1 --branch starter https://example.test/frontend/mobile-ui.git mobile-ui-lab
```

### clone-hard-lab-notebook-depth-branch

**Difficulty:** Hard  
**Scenario:** shallow-copy-of-one-branch  
**Alternative category:** syntax alternatives

**Objective**

Clone the remote repository from `https://example.test/docs/lab-notebook.git` into a local folder named `notebook-review` with `review` checked out using a history depth of 1.

**Taught / authored example — 1 counted command**

```sh
git clone --depth 1 --branch review https://example.test/docs/lab-notebook.git notebook-review
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git clone --depth 1 -b review https://example.test/docs/lab-notebook.git notebook-review
```

<a id="level-3"></a>
## Story: staging-and-committing-basic-workflow

### commit-easy-form-validation

**Difficulty:** Easy  
**Scenario:** stage-and-commit-one-change  
**Alternative category:** multiple workflows

**Objective**

Stage `src/form.js` and create a commit with the message `Update form validation`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/form.js
git commit -m "Update form validation"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/form.js
git commit -m "Update form validation"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Update form validation"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/form.js
git commit --message 'Update form validation'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add src/form.js
git commit '--message=Update form validation'
```

### commit-easy-readme-setup

**Difficulty:** Easy  
**Scenario:** stage-and-commit-one-change  
**Alternative category:** multiple workflows

**Objective**

Stage `README.md` and create a commit with the message `Clarify setup steps`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add README.md
git commit -m "Clarify setup steps"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- README.md
git commit -m "Clarify setup steps"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Clarify setup steps"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add README.md
git commit --message 'Clarify setup steps'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add README.md
git commit '--message=Clarify setup steps'
```

### commit-easy-navbar-spacing

**Difficulty:** Easy  
**Scenario:** stage-and-commit-one-change  
**Alternative category:** multiple workflows

**Objective**

Stage `styles/navbar.css` and create a commit with the message `Adjust navbar spacing`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add styles/navbar.css
git commit -m "Adjust navbar spacing"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- styles/navbar.css
git commit -m "Adjust navbar spacing"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Adjust navbar spacing"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add styles/navbar.css
git commit --message 'Adjust navbar spacing'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add styles/navbar.css
git commit '--message=Adjust navbar spacing'
```

### commit-med-docker

**Difficulty:** Easy  
**Scenario:** stage-several-files  
**Alternative category:** multiple workflows

**Objective**

Stage `Dockerfile`, `.env.example` and create a commit with the message `Add Docker configuration`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add Dockerfile .env.example
git commit -m "Add Docker configuration"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Add Docker configuration"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add Dockerfile .env.example
git commit --message 'Add Docker configuration'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add Dockerfile .env.example
git commit '--message=Add Docker configuration'
```

### commit-medium-profile-card

**Difficulty:** Easy  
**Scenario:** stage-several-files  
**Alternative category:** multiple workflows

**Objective**

Stage `src/profile-card.js`, `styles/profile-card.css` and create a commit with the message `Update profile card layout`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/profile-card.js styles/profile-card.css
git commit -m "Update profile card layout"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Update profile card layout"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/profile-card.js styles/profile-card.css
git commit --message 'Update profile card layout'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/profile-card.js styles/profile-card.css
git commit '--message=Update profile card layout'
```

### commit-medium-search-results

**Difficulty:** Easy  
**Scenario:** a-two-file-change  
**Alternative category:** multiple workflows

**Objective**

Stage `src/search.js`, `templates/search.html` and create a commit with the message `Refine search results view`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit -m "Refine search results view"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Refine search results view"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit --message 'Refine search results view'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit '--message=Refine search results view'
```

### commit-medium-export-flow

**Difficulty:** Easy  
**Scenario:** a-two-file-change  
**Alternative category:** multiple workflows

**Objective**

Stage `src/export.py`, `docs/export.md` and create a commit with the message `Document export flow update`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/export.py docs/export.md
git commit -m "Document export flow update"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Document export flow update"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/export.py docs/export.md
git commit --message 'Document export flow update'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/export.py docs/export.md
git commit '--message=Document export flow update'
```

### commit-medium-new-project-portfolio

**Difficulty:** Medium  
**Scenario:** first-snapshot-of-a-new-project  
**Alternative category:** syntax alternatives

**Objective**

Make `portfolio` a Git repository on `main`, then commit `index.html` and `styles.css` with the message `Initial portfolio`.

**Leave `notes.txt` untracked.**

**Taught / authored example — 3 counted commands**

```sh
git init -b main
git add index.html styles.css
git commit -m "Initial portfolio"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git init --initial-branch main
git add index.html styles.css
git commit -m "Initial portfolio"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git init
git add index.html styles.css
git commit -m "Initial portfolio"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git init -b main
git add index.html styles.css
git commit --message 'Initial portfolio'
```

### commit-medium-new-project-recipes

**Difficulty:** Medium  
**Scenario:** first-snapshot-of-a-new-project  
**Alternative category:** syntax alternatives

**Objective**

Make `recipes` a Git repository on `main`, then commit `recipes.md` and `shopping.md` with the message `Start recipe notes`.

**Leave `draft.txt` untracked.**

**Taught / authored example — 3 counted commands**

```sh
git init -b main
git add recipes.md shopping.md
git commit -m "Start recipe notes"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git init --initial-branch main
git add recipes.md shopping.md
git commit -m "Start recipe notes"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git init
git add recipes.md shopping.md
git commit -m "Start recipe notes"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git init -b main
git add recipes.md shopping.md
git commit --message 'Start recipe notes'
```

### commit-easy-initial

**Difficulty:** Medium  
**Scenario:** a-bigger-change  
**Alternative category:** multiple workflows

**Objective**

Stage `README.md`, `main.py`, `requirements.txt` and create a commit with the message `Initial commit`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add README.md main.py requirements.txt
git commit -m "Initial commit"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Initial commit"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add README.md main.py requirements.txt
git commit --message 'Initial commit'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add README.md main.py requirements.txt
git commit '--message=Initial commit'
```

### commit-medium-three-file-release

**Difficulty:** Medium  
**Scenario:** a-bigger-change  
**Alternative category:** multiple workflows

**Objective**

Stage `CHANGELOG.md`, `setup.py` and `src/version.py`, then create a commit with the message `Prepare 1.2 release`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add CHANGELOG.md setup.py src/version.py
git commit -m "Prepare 1.2 release"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git add .
git commit -m "Prepare 1.2 release"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add CHANGELOG.md setup.py src/version.py
git commit --message 'Prepare 1.2 release'
```

### commit-hard-selective

**Difficulty:** Hard  
**Scenario:** leave-the-distractor-out  
**Alternative category:** syntax alternatives

**Objective**

Stage `api/handler.py` and create a commit with the message `Fix request handler null check`.

**Leave `api/experimental.py` uncommitted**; finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add api/handler.py
git commit -m "Fix request handler null check"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- api/handler.py
git commit -m "Fix request handler null check"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add api/handler.py
git commit --message 'Fix request handler null check'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add api/handler.py
git commit '--message=Fix request handler null check'
```

### commit-hard-profile-distractor

**Difficulty:** Hard  
**Scenario:** leave-the-distractor-out  
**Alternative category:** syntax alternatives

**Objective**

Stage `src/profile-card.js` and create a commit with the message `Update profile card behavior`.

**Leave `notes/profile-ideas.md` uncommitted**; finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/profile-card.js
git commit -m "Update profile card behavior"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/profile-card.js
git commit -m "Update profile card behavior"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/profile-card.js
git commit --message 'Update profile card behavior'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/profile-card.js
git commit '--message=Update profile card behavior'
```

### commit-hard-export-distractor

**Difficulty:** Hard  
**Scenario:** leave-the-distractor-out  
**Alternative category:** syntax alternatives

**Objective**

Stage `src/export.py` and create a commit with the message `Fix export validation`.

**Leave `scratch/export-test-output.txt` uncommitted**; finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/export.py
git commit -m "Fix export validation"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/export.py
git commit -m "Fix export validation"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/export.py
git commit --message 'Fix export validation'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/export.py
git commit '--message=Fix export validation'
```

### commit-hard-parser

**Difficulty:** Hard  
**Scenario:** two-targets-two-distractors  
**Alternative category:** syntax alternatives

**Objective**

Stage `src/parser.py`, `tests/test_parser.py` and create a commit with the message `Add parser module with unit tests`.

**Leave `debug.log` and `scratch.py` uncommitted**; finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/parser.py tests/test_parser.py
git commit -m "Add parser module with unit tests"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add src/parser.py tests/test_parser.py
git commit --message 'Add parser module with unit tests'
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/parser.py tests/test_parser.py
git commit '--message=Add parser module with unit tests'
```

### commit-hard-search-two-targets-one-distractor

**Difficulty:** Hard  
**Scenario:** two-targets-two-distractors  
**Alternative category:** syntax alternatives

**Objective**

Stage `src/search.js`, `templates/search.html` and create a commit with the message `Refine search ranking display`.

**Leave `notes/search-ranking.md` uncommitted**; finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit -m "Refine search ranking display"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit --message 'Refine search ranking display'
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add src/search.js templates/search.html
git commit '--message=Refine search ranking display'
```

<a id="level-4"></a>
## Story: partial-staging-and-git-add-p

### partial-easy-billing

**Difficulty:** Easy  
**Scenario:** stage-one-hunk  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the billing rounding fix and commit it with the message `Fix billing calculation rounding error`. Leave The diagnostic print statements out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/billing.py
git commit -m "Fix billing calculation rounding error"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/billing.py
git commit -m "Fix billing calculation rounding error"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/billing.py
git commit --message 'Fix billing calculation rounding error'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/billing.py
git commit '--message=Fix billing calculation rounding error'
```

### partial-easy-auth-validation

**Difficulty:** Easy  
**Scenario:** stage-one-hunk  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the auth validation fix and commit it with the message `Fix auth validation`. Leave The unfinished refactor out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/auth.py
git commit -m "Fix auth validation"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/auth.py
git commit -m "Fix auth validation"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/auth.py
git commit --message 'Fix auth validation'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/auth.py
git commit '--message=Fix auth validation'
```

### partial-easy-export-format

**Difficulty:** Easy  
**Scenario:** stage-one-hunk  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the export formatting fix and commit it with the message `Fix export formatting`. Leave The extra logging out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/export.py
git commit -m "Fix export formatting"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/export.py
git commit -m "Fix export formatting"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/export.py
git commit --message 'Fix export formatting'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/export.py
git commit '--message=Fix export formatting'
```

### partial-easy-routes

**Difficulty:** Easy  
**Scenario:** another-file-another-hunk  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the updated route handlers and commit it with the message `Update API route handlers`. Leave The experimental auth middleware out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/routes.py
git commit -m "Update API route handlers"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/routes.py
git commit -m "Update API route handlers"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/routes.py
git commit --message 'Update API route handlers'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/routes.py
git commit '--message=Update API route handlers'
```

### partial-easy-search-ranking

**Difficulty:** Easy  
**Scenario:** another-file-another-hunk  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the ranking algorithm fix and commit it with the message `Fix search ranking`. Leave The cleanup refactor out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/search.py
git commit -m "Fix search ranking"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/search.py
git commit -m "Fix search ranking"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/search.py
git commit --message 'Fix search ranking'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/search.py
git commit '--message=Fix search ranking'
```

### partial-med-three-hunk

**Difficulty:** Medium  
**Scenario:** one-hunk-out-of-many  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the parser bug fix and commit it with the message `Fix parser blank-line bug`. Leave The refactor and experiment out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/parser.py
git commit -m "Fix parser blank-line bug"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/parser.py
git commit -m "Fix parser blank-line bug"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/parser.py
git commit --message 'Fix parser blank-line bug'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/parser.py
git commit '--message=Fix parser blank-line bug'
```

### partial-medium-profile-validation

**Difficulty:** Medium  
**Scenario:** one-hunk-out-of-many  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the profile validation fix and commit it with the message `Fix profile validation`. Leave The copy, cleanup, and notes out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/profile.py
git commit -m "Fix profile validation"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/profile.py
git commit -m "Fix profile validation"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/profile.py
git commit --message 'Fix profile validation'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/profile.py
git commit '--message=Fix profile validation'
```

### partial-medium-payment-rounding

**Difficulty:** Medium  
**Scenario:** one-hunk-out-of-many  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the payment rounding fix and commit it with the message `Fix payment rounding`. Leave The logging, comment edit, and scratch file out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/payment.py
git commit -m "Fix payment rounding"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/payment.py
git commit -m "Fix payment rounding"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/payment.py
git commit --message 'Fix payment rounding'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/payment.py
git commit '--message=Fix payment rounding'
```

### partial-medium-dashboard-filter

**Difficulty:** Medium  
**Scenario:** one-hunk-out-of-many  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the dashboard filter fix and commit it with the message `Fix dashboard filter`. Leave The theme work, console output, and notes out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/dashboard.js
git commit -m "Fix dashboard filter"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/dashboard.js
git commit -m "Fix dashboard filter"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/dashboard.js
git commit --message 'Fix dashboard filter'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/dashboard.js
git commit '--message=Fix dashboard filter'
```

### partial-hard-terraform

**Difficulty:** Medium  
**Scenario:** one-hunk-out-of-many  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the network configuration hunk and commit it with the message `Update network Terraform configuration`. Leave The experimental flags and debug file out of the commit and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p terraform/main.tf
git commit -m "Update network Terraform configuration"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch terraform/main.tf
git commit -m "Update network Terraform configuration"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p terraform/main.tf
git commit --message 'Update network Terraform configuration'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p terraform/main.tf
git commit '--message=Update network Terraform configuration'
```

### partial-medium-hunk-plus-test

**Difficulty:** Medium  
**Scenario:** a-hunk-and-a-whole-file  
**Alternative category:** syntax alternatives

**Objective**

Commit the rounding fix from `src/cart.py` together with the whole of `tests/test_cart.py`, using the message `Fix cart total rounding`.

**Leave the debug print uncommitted** and finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git add -p src/cart.py
git add tests/test_cart.py
git commit -m "Fix cart total rounding"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add --patch src/cart.py
git add tests/test_cart.py
git commit -m "Fix cart total rounding"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git add -p src/cart.py
git add -- tests/test_cart.py
git commit -m "Fix cart total rounding"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add -p src/cart.py
git add tests/test_cart.py
git commit --message 'Fix cart total rounding'
```

### partial-medium-hunk-plus-doc

**Difficulty:** Medium  
**Scenario:** a-hunk-and-a-whole-file  
**Alternative category:** syntax alternatives

**Objective**

Commit the quoting fix from `src/export.py` together with the whole of `docs/export.md`, using the message `Fix CSV quoting`.

**Leave the experimental flag uncommitted** and finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git add -p src/export.py
git add docs/export.md
git commit -m "Fix CSV quoting"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add --patch src/export.py
git add docs/export.md
git commit -m "Fix CSV quoting"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git add -p src/export.py
git add -- docs/export.md
git commit -m "Fix CSV quoting"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add -p src/export.py
git add docs/export.md
git commit --message 'Fix CSV quoting'
```

### partial-hard-auth-cross-file

**Difficulty:** Hard  
**Scenario:** hunks-across-code-and-tests  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the auth validation fix and matching test and commit it with the message `Fix auth validation and add its test`. Leave The refactor, test cleanup, and debug notes out of the commit and finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git add -p src/auth.py
git add -p tests/test_auth.py
git commit -m "Fix auth validation and add its test"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add --patch src/auth.py
git add -p tests/test_auth.py
git commit -m "Fix auth validation and add its test"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git add -p src/auth.py
git add --patch tests/test_auth.py
git commit -m "Fix auth validation and add its test"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add -p src/auth.py
git add -p tests/test_auth.py
git commit --message 'Fix auth validation and add its test'
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git add -p src/auth.py
git add -p tests/test_auth.py
git commit '--message=Fix auth validation and add its test'
```

### partial-hard-search-cross-file

**Difficulty:** Hard  
**Scenario:** hunks-across-code-and-tests  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the search ranking fix and matching test and commit it with the message `Fix search ranking and add its test`. Leave The cleanup, fixture edits, and temporary output out of the commit and finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git add -p src/search.py
git add -p tests/test_search.py
git commit -m "Fix search ranking and add its test"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add --patch src/search.py
git add -p tests/test_search.py
git commit -m "Fix search ranking and add its test"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git add -p src/search.py
git add --patch tests/test_search.py
git commit -m "Fix search ranking and add its test"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add -p src/search.py
git add -p tests/test_search.py
git commit --message 'Fix search ranking and add its test'
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git add -p src/search.py
git add -p tests/test_search.py
git commit '--message=Fix search ranking and add its test'
```

### partial-hard-export-cross-file

**Difficulty:** Hard  
**Scenario:** hunks-across-code-and-tests  
**Alternative category:** syntax alternatives

**Objective**

Stage __only__ the export formatting fix and matching test and commit it with the message `Fix export formatting and add its test`. Leave The logging, test cleanup, and follow-up notes out of the commit and finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git add -p src/export.py
git add -p tests/test_export.py
git commit -m "Fix export formatting and add its test"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add --patch src/export.py
git add -p tests/test_export.py
git commit -m "Fix export formatting and add its test"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git add -p src/export.py
git add --patch tests/test_export.py
git commit -m "Fix export formatting and add its test"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add -p src/export.py
git add -p tests/test_export.py
git commit --message 'Fix export formatting and add its test'
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git add -p src/export.py
git add -p tests/test_export.py
git commit '--message=Fix export formatting and add its test'
```

### partial-hard-split-two-commits-api

**Difficulty:** Hard  
**Scenario:** split-one-file-into-two-commits  
**Alternative category:** multiple workflows

**Objective**

Make two commits on `main`. First commit __only__ the expiry fix with the message `Fix token expiry check`, then commit the logging tidy-up with the message `Tidy API logging`.

**Taught / authored example — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git add --patch src/api.py
git commit -m "Fix token expiry check"
git add src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit --message 'Fix token expiry check'
git add src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add -- src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add .
git commit -m "Tidy API logging"
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add --patch src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add -p src/api.py
git commit -m "Tidy API logging"
```

**Accepted alternative 7 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add src/api.py
git commit --message 'Tidy API logging'
```

**Accepted alternative 8 (syntax) — 4 counted commands**

```sh
git add -p src/api.py
git commit -m "Fix token expiry check"
git add src/api.py
git commit -am 'Tidy API logging'
```

### partial-hard-split-two-commits-ui

**Difficulty:** Hard  
**Scenario:** split-one-file-into-two-commits  
**Alternative category:** multiple workflows

**Objective**

Make two commits on `main`. First commit __only__ the focus-trap fix with the message `Fix menu focus trap`, then commit the renames with the message `Rename menu helpers`.

**Taught / authored example — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git add --patch src/menu.js
git commit -m "Fix menu focus trap"
git add src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit --message 'Fix menu focus trap'
git add src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add -- src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add .
git commit -m "Rename menu helpers"
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add --patch src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add -p src/menu.js
git commit -m "Rename menu helpers"
```

**Accepted alternative 7 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add src/menu.js
git commit --message 'Rename menu helpers'
```

**Accepted alternative 8 (syntax) — 4 counted commands**

```sh
git add -p src/menu.js
git commit -m "Fix menu focus trap"
git add src/menu.js
git commit -am 'Rename menu helpers'
```

<a id="level-5"></a>
## Story: amending-commits

### amend-easy-typo

**Difficulty:** Easy  
**Scenario:** fix-the-last-message  
**Alternative category:** syntax alternatives

**Objective**

Change the latest local commit message to `Initial commit`. Keep its files as they are and finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git commit --amend -m "Initial commit"
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git commit --amend --message 'Initial commit'
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git commit --amend '--message=Initial commit'
```

### amend-easy-login-copy-message

**Difficulty:** Easy  
**Scenario:** fix-the-last-message  
**Alternative category:** syntax alternatives

**Objective**

Change the latest local commit message to `Clarify login copy`. Keep its files as they are and finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git commit --amend -m "Clarify login copy"
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git commit --amend --message 'Clarify login copy'
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git commit --amend '--message=Clarify login copy'
```

### amend-easy-readme-message

**Difficulty:** Easy  
**Scenario:** fix-the-last-message  
**Alternative category:** syntax alternatives

**Objective**

Change the latest local commit message to `Clarify setup requirements`. Keep its files as they are and finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git commit --amend -m "Clarify setup requirements"
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git commit --amend --message 'Clarify setup requirements'
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git commit --amend '--message=Clarify setup requirements'
```

### amend-easy-navbar-message

**Difficulty:** Easy  
**Scenario:** fix-the-last-message  
**Alternative category:** syntax alternatives

**Objective**

Change the latest local commit message to `Adjust navbar spacing`. Keep its files as they are and finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git commit --amend -m "Adjust navbar spacing"
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git commit --amend --message 'Adjust navbar spacing'
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git commit --amend '--message=Adjust navbar spacing'
```

### amend-hard-convention

**Difficulty:** Easy  
**Scenario:** fix-the-last-message  
**Alternative category:** syntax alternatives

**Objective**

Change the latest local commit message to `Update Terraform staging environment configuration`. Keep its files as they are and finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git commit --amend -m "Update Terraform staging environment configuration"
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git commit --amend --message 'Update Terraform staging environment configuration'
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git commit --amend '--message=Update Terraform staging environment configuration'
```

### amend-easy-forgot

**Difficulty:** Easy  
**Scenario:** add-the-forgotten-file  
**Alternative category:** multiple workflows

**Objective**

Include `src/logout.py` in the latest local commit while keeping its message `Add auth module`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add src/logout.py
git commit --amend -m "Add auth module"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/logout.py
git commit --amend -m "Add auth module"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Add auth module"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add src/logout.py
git commit --amend --message 'Add auth module'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add src/logout.py
git commit --amend '--message=Add auth module'
```

### amend-medium-profile-missing-css

**Difficulty:** Easy  
**Scenario:** add-the-forgotten-file  
**Alternative category:** multiple workflows

**Objective**

Include `styles/profile-card.css` in the latest local commit while keeping its message `Update profile card layout`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add styles/profile-card.css
git commit --amend -m "Update profile card layout"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- styles/profile-card.css
git commit --amend -m "Update profile card layout"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Update profile card layout"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add styles/profile-card.css
git commit --amend --message 'Update profile card layout'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add styles/profile-card.css
git commit --amend '--message=Update profile card layout'
```

### amend-medium-export-doc

**Difficulty:** Easy  
**Scenario:** add-the-forgotten-file  
**Alternative category:** multiple workflows

**Objective**

Include `docs/export.md` in the latest local commit while keeping its message `Document export flow update`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add docs/export.md
git commit --amend -m "Document export flow update"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- docs/export.md
git commit --amend -m "Document export flow update"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Document export flow update"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add docs/export.md
git commit --amend --message 'Document export flow update'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add docs/export.md
git commit --amend '--message=Document export flow update'
```

### amend-medium-search-template

**Difficulty:** Easy  
**Scenario:** add-the-forgotten-file  
**Alternative category:** multiple workflows

**Objective**

Include `templates/search.html` in the latest local commit while keeping its message `Refine search results view`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add templates/search.html
git commit --amend -m "Refine search results view"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- templates/search.html
git commit --amend -m "Refine search results view"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Refine search results view"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add templates/search.html
git commit --amend --message 'Refine search results view'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add templates/search.html
git commit --amend '--message=Refine search results view'
```

### amend-med-both

**Difficulty:** Medium  
**Scenario:** amend-content-and-message  
**Alternative category:** multiple workflows

**Objective**

Include `docs/CHANGELOG.md` in the latest local commit and change its message to `Add parser feature and update changelog`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add docs/CHANGELOG.md
git commit --amend -m "Add parser feature and update changelog"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- docs/CHANGELOG.md
git commit --amend -m "Add parser feature and update changelog"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Add parser feature and update changelog"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add docs/CHANGELOG.md
git commit --amend --message 'Add parser feature and update changelog'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add docs/CHANGELOG.md
git commit --amend '--message=Add parser feature and update changelog'
```

### amend-hard-profile-message-and-layout

**Difficulty:** Medium  
**Scenario:** amend-content-and-message  
**Alternative category:** multiple workflows

**Objective**

Include `styles/profile-layout.css` in the latest local commit and change its message to `Polish profile card layout`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add styles/profile-layout.css
git commit --amend -m "Polish profile card layout"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- styles/profile-layout.css
git commit --amend -m "Polish profile card layout"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Polish profile card layout"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add styles/profile-layout.css
git commit --amend --message 'Polish profile card layout'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add styles/profile-layout.css
git commit --amend '--message=Polish profile card layout'
```

### amend-medium-hunk-into-last-checkout

**Difficulty:** Medium  
**Scenario:** amend-in-one-hunk  
**Alternative category:** syntax alternatives

**Objective**

Add __only__ the missing guard hunk from `src/checkout.py` to the latest commit, keeping its message `Validate checkout totals`.

**Leave the debug hunk uncommitted** and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/checkout.py
git commit --amend -m "Validate checkout totals"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/checkout.py
git commit --amend -m "Validate checkout totals"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/checkout.py
git commit --amend --message 'Validate checkout totals'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/checkout.py
git commit --amend --no-edit
```

### amend-medium-hunk-into-last-search

**Difficulty:** Medium  
**Scenario:** amend-in-one-hunk  
**Alternative category:** syntax alternatives

**Objective**

Add __only__ the missing ranking hunk from `src/search.py` to the latest commit, keeping its message `Rank exact matches first`.

**Leave the logging hunk uncommitted** and finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add -p src/search.py
git commit --amend -m "Rank exact matches first"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add --patch src/search.py
git commit --amend -m "Rank exact matches first"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git add -p src/search.py
git commit --amend --message 'Rank exact matches first'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -p src/search.py
git commit --amend --no-edit
```

### amend-hard-auth-message-and-test

**Difficulty:** Hard  
**Scenario:** missing-file-and-wrong-message  
**Alternative category:** multiple workflows

**Objective**

Include `tests/test_auth.py` in the latest local commit and change its message to `Add auth validation coverage`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add tests/test_auth.py
git commit --amend -m "Add auth validation coverage"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- tests/test_auth.py
git commit --amend -m "Add auth validation coverage"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Add auth validation coverage"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add tests/test_auth.py
git commit --amend --message 'Add auth validation coverage'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add tests/test_auth.py
git commit --amend '--message=Add auth validation coverage'
```

### amend-hard-export-message-and-doc

**Difficulty:** Hard  
**Scenario:** missing-file-and-wrong-message  
**Alternative category:** multiple workflows

**Objective**

Include `docs/export.md` in the latest local commit and change its message to `Document export validation behavior`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git add docs/export.md
git commit --amend -m "Document export validation behavior"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- docs/export.md
git commit --amend -m "Document export validation behavior"
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git commit --amend -m "Document export validation behavior"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add docs/export.md
git commit --amend --message 'Document export validation behavior'
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git add docs/export.md
git commit --amend '--message=Document export validation behavior'
```

### amend-hard-fix-message-then-commit-api

**Difficulty:** Hard  
**Scenario:** fix-the-message-then-commit-the-rest  
**Alternative category:** multiple workflows

**Objective**

Rename the latest commit to `Add rate limiter`, then commit `docs/limits.md` separately with the message `Document rate limits`. Finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git commit --amend -m "Add rate limiter"
git add docs/limits.md
git commit -m "Document rate limits"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git commit --amend --message 'Add rate limiter'
git add docs/limits.md
git commit -m "Document rate limits"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add rate limiter"
git add -- docs/limits.md
git commit -m "Document rate limits"
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git commit --amend -m "Add rate limiter"
git add .
git commit -m "Document rate limits"
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add rate limiter"
git add docs/limits.md
git commit --message 'Document rate limits'
```

### amend-hard-fix-message-then-commit-docs

**Difficulty:** Hard  
**Scenario:** fix-the-message-then-commit-the-rest  
**Alternative category:** multiple workflows

**Objective**

Rename the latest commit to `Document install steps`, then commit `docs/faq.md` separately with the message `Add install FAQ`. Finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git commit --amend -m "Document install steps"
git add docs/faq.md
git commit -m "Add install FAQ"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git commit --amend --message 'Document install steps'
git add docs/faq.md
git commit -m "Add install FAQ"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Document install steps"
git add -- docs/faq.md
git commit -m "Add install FAQ"
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git commit --amend -m "Document install steps"
git add .
git commit -m "Add install FAQ"
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Document install steps"
git add docs/faq.md
git commit --message 'Add install FAQ'
```

<a id="level-6"></a>
## Story: unstaging-and-discarding-changes

### restore-easy-unstage

**Difficulty:** Easy  
**Scenario:** unstage-keep-the-edit  
**Alternative category:** multiple workflows

**Objective**

Unstage `notes.txt` while keeping those edits. Finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git restore --staged notes.txt
```

**Accepted alternative 1 (workflow) — 1 counted command**

```sh
git reset HEAD -- notes.txt
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git restore -S notes.txt
```

**Accepted alternative 3 (workflow) — 1 counted command**

```sh
git reset -- notes.txt
```

### restore-easy-unstage-app

**Difficulty:** Easy  
**Scenario:** unstage-keep-the-edit  
**Alternative category:** multiple workflows

**Objective**

Unstage `src/app.py` while keeping those edits. Finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git restore --staged src/app.py
```

**Accepted alternative 1 (workflow) — 1 counted command**

```sh
git reset HEAD -- src/app.py
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git restore -S src/app.py
```

**Accepted alternative 3 (workflow) — 1 counted command**

```sh
git reset -- src/app.py
```

### restore-easy-unstage-guide

**Difficulty:** Easy  
**Scenario:** unstage-keep-the-edit  
**Alternative category:** multiple workflows

**Objective**

Unstage `docs/guide.md` while keeping those edits. Finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git restore --staged docs/guide.md
```

**Accepted alternative 1 (workflow) — 1 counted command**

```sh
git reset HEAD -- docs/guide.md
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git restore -S docs/guide.md
```

**Accepted alternative 3 (workflow) — 1 counted command**

```sh
git reset -- docs/guide.md
```

### restore-easy-unstage-css

**Difficulty:** Easy  
**Scenario:** unstage-keep-the-edit  
**Alternative category:** multiple workflows

**Objective**

Unstage `styles/site.css` while keeping those edits. Finish on `main`.

**Taught / authored example — 1 counted command**

```sh
git restore --staged styles/site.css
```

**Accepted alternative 1 (workflow) — 1 counted command**

```sh
git reset HEAD -- styles/site.css
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git restore -S styles/site.css
```

**Accepted alternative 3 (workflow) — 1 counted command**

```sh
git reset -- styles/site.css
```

### restore-med-unstage-discard

**Difficulty:** Easy  
**Scenario:** unstage-and-discard-together  
**Alternative category:** multiple workflows

**Objective**

Unstage `experimental.py` while keeping those edits. Discard the working-tree changes in `README.md` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged experimental.py
git restore README.md
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- experimental.py
git restore README.md
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S experimental.py
git restore README.md
```

### restore-medium-app-debug

**Difficulty:** Easy  
**Scenario:** unstage-and-discard-together  
**Alternative category:** multiple workflows

**Objective**

Unstage `src/app.py` while keeping those edits. Discard the working-tree changes in `debug.log` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged src/app.py
git restore debug.log
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- src/app.py
git restore debug.log
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S src/app.py
git restore debug.log
```

### restore-medium-docs-scratch

**Difficulty:** Medium  
**Scenario:** unstage-one-discard-another  
**Alternative category:** multiple workflows

**Objective**

Unstage `docs/guide.md` while keeping those edits. Discard the working-tree changes in `tmp/scratch.txt` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged docs/guide.md
git restore tmp/scratch.txt
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- docs/guide.md
git restore tmp/scratch.txt
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S docs/guide.md
git restore tmp/scratch.txt
```

### restore-medium-css-build

**Difficulty:** Medium  
**Scenario:** unstage-one-discard-another  
**Alternative category:** multiple workflows

**Objective**

Unstage `styles/site.css` while keeping those edits. Discard the working-tree changes in `dist/site.css` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged styles/site.css
git restore dist/site.css
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- styles/site.css
git restore dist/site.css
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S styles/site.css
git restore dist/site.css
```

### restore-medium-unstage-then-commit-login

**Difficulty:** Medium  
**Scenario:** fix-the-staging-then-commit  
**Alternative category:** multiple workflows

**Objective**

Unstage `notes/todo.md` while keeping its edits, then commit the login fix with the message `Fix login redirect`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged notes/todo.md
git commit -m "Fix login redirect"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- notes/todo.md
git commit -m "Fix login redirect"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S notes/todo.md
git commit -m "Fix login redirect"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git restore --staged notes/todo.md
git commit --message 'Fix login redirect'
```

### restore-medium-unstage-then-commit-cart

**Difficulty:** Medium  
**Scenario:** fix-the-staging-then-commit  
**Alternative category:** multiple workflows

**Objective**

Unstage `scratch/ideas.txt` while keeping its edits, then commit the badge fix with the message `Fix cart badge count`. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged scratch/ideas.txt
git commit -m "Fix cart badge count"
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- scratch/ideas.txt
git commit -m "Fix cart badge count"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S scratch/ideas.txt
git commit -m "Fix cart badge count"
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git restore --staged scratch/ideas.txt
git commit --message 'Fix cart badge count'
```

### restore-hard-cleanup

**Difficulty:** Hard  
**Scenario:** several-to-unstage-one-to-discard  
**Alternative category:** multiple workflows

**Objective**

Unstage `debug.log`, `scratch/notes.txt` while keeping those edits. Discard the working-tree changes in `api/experimental.py` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged debug.log scratch/notes.txt
git restore api/experimental.py
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- debug.log scratch/notes.txt
git restore api/experimental.py
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S debug.log scratch/notes.txt
git restore api/experimental.py
```

### restore-hard-mixed-profile

**Difficulty:** Hard  
**Scenario:** several-to-unstage-one-to-discard  
**Alternative category:** multiple workflows

**Objective**

Unstage `src/profile-card.js`, `notes/profile-ideas.md` while keeping those edits. Discard the working-tree changes in `debug/profile.log` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged src/profile-card.js notes/profile-ideas.md
git restore debug/profile.log
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- src/profile-card.js notes/profile-ideas.md
git restore debug/profile.log
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S src/profile-card.js notes/profile-ideas.md
git restore debug/profile.log
```

### restore-hard-mixed-export

**Difficulty:** Hard  
**Scenario:** several-to-unstage-one-to-discard  
**Alternative category:** multiple workflows

**Objective**

Unstage `src/export.py`, `notes/export-plan.md` while keeping those edits. Discard the working-tree changes in `tmp/export-output.txt` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged src/export.py notes/export-plan.md
git restore tmp/export-output.txt
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- src/export.py notes/export-plan.md
git restore tmp/export-output.txt
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S src/export.py notes/export-plan.md
git restore tmp/export-output.txt
```

### restore-hard-mixed-search

**Difficulty:** Hard  
**Scenario:** several-to-unstage-one-to-discard  
**Alternative category:** multiple workflows

**Objective**

Unstage `src/search.js`, `notes/search.md` while keeping those edits. Discard the working-tree changes in `debug/search.log` and restore their committed versions. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git restore --staged src/search.js notes/search.md
git restore debug/search.log
```

**Accepted alternative 1 (workflow) — 2 counted commands**

```sh
git reset HEAD -- src/search.js notes/search.md
git restore debug/search.log
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git restore -S src/search.js notes/search.md
git restore debug/search.log
```

### restore-hard-capstone-report

**Difficulty:** Hard  
**Scenario:** clean-up-then-commit-only-the-fix  
**Alternative category:** multiple workflows

**Objective**

Unstage `debug.log` (keep it in the folder), discard the edits to `tmp/output.txt`, and commit only the totals fix from `src/report.py` with the message `Fix report totals`.

**Leave the experiment uncommitted** and finish on `main`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged debug.log
git restore tmp/output.txt
git add -p src/report.py
git commit -m "Fix report totals"
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- debug.log
git restore tmp/output.txt
git add -p src/report.py
git commit -m "Fix report totals"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged debug.log
git restore tmp/output.txt
git add --patch src/report.py
git commit -m "Fix report totals"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged debug.log
git restore tmp/output.txt
git add --patch
git commit -m "Fix report totals"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore --staged debug.log
git restore tmp/output.txt
git add -p src/report.py
git commit --message 'Fix report totals'
```

### restore-hard-capstone-invoice

**Difficulty:** Hard  
**Scenario:** clean-up-then-commit-only-the-fix  
**Alternative category:** multiple workflows

**Objective**

Unstage `notes/invoice-ideas.md` (keep it in the folder), discard the edits to `build/invoice.html`, and commit only the due-date fix from `src/invoice.py` with the message `Fix invoice due date`.

**Leave the refactor uncommitted** and finish on `main`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged notes/invoice-ideas.md
git restore build/invoice.html
git add -p src/invoice.py
git commit -m "Fix invoice due date"
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- notes/invoice-ideas.md
git restore build/invoice.html
git add -p src/invoice.py
git commit -m "Fix invoice due date"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged notes/invoice-ideas.md
git restore build/invoice.html
git add --patch src/invoice.py
git commit -m "Fix invoice due date"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged notes/invoice-ideas.md
git restore build/invoice.html
git add --patch
git commit -m "Fix invoice due date"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore --staged notes/invoice-ideas.md
git restore build/invoice.html
git add -p src/invoice.py
git commit --message 'Fix invoice due date'
```

<a id="level-7"></a>
## Story: creating-and-switching-branches

### v21e-auth

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `feature/auth` from the current tip of `main` and switch to it. Finish on `feature/auth`.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/auth
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/auth
git switch feature/auth
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/auth
```

### v21e-login

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `bugfix/login` from the current tip of `main` and switch to it. Finish on `bugfix/login`.

**Taught / authored example — 1 counted command**

```sh
git switch -c bugfix/login
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b bugfix/login
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch bugfix/login
git switch bugfix/login
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create bugfix/login
```

### v21e-ui

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `experiment/ui` from the current tip of `main` and switch to it. Finish on `experiment/ui`.

**Taught / authored example — 1 counted command**

```sh
git switch -c experiment/ui
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b experiment/ui
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch experiment/ui
git switch experiment/ui
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create experiment/ui
```

### bc-easy-capstone-db

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `feature/database-models` from the current tip of `main` and switch to it. Finish on `feature/database-models`.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/database-models
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/database-models
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/database-models
git switch feature/database-models
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/database-models
```

### bc-easy-corp-hotfix

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `hotfix/session-timeout` from the current tip of `main` and switch to it. Finish on `hotfix/session-timeout`.

**Taught / authored example — 1 counted command**

```sh
git switch -c hotfix/session-timeout
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b hotfix/session-timeout
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch hotfix/session-timeout
git switch hotfix/session-timeout
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create hotfix/session-timeout
```

### bc-med-oss-develop

**Difficulty:** Easy  
**Scenario:** create-and-switch  
**Alternative category:** multiple workflows

**Objective**

Create `feature/docs-update` from the current tip of `develop` and switch to it. Finish on `feature/docs-update`.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/docs-update
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/docs-update
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/docs-update
git switch feature/docs-update
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/docs-update
```

### switch-easy-back-to-main-docs

**Difficulty:** Easy  
**Scenario:** go-back-to-main  
**Alternative category:** syntax alternatives

**Objective**

Switch back to `main`.

**Leave `feature/docs-refresh` exactly as it is.**

**Taught / authored example — 1 counted command**

```sh
git switch main
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout main
```

### switch-easy-back-to-main-api

**Difficulty:** Easy  
**Scenario:** go-back-to-main  
**Alternative category:** syntax alternatives

**Objective**

Switch back to `main` and leave `feature/api-keys` untouched.

**Taught / authored example — 1 counted command**

```sh
git switch main
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout main
```

### switch-easy-branch-then-return-docs

**Difficulty:** Easy  
**Scenario:** branch-off-then-return  
**Alternative category:** multiple workflows

**Objective**

Create `docs/faq` from the current tip of `main` and switch to it, then switch back to `main`.

**Taught / authored example — 2 counted commands**

```sh
git switch -c docs/faq
git switch main
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout -b docs/faq
git switch main
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch docs/faq
git switch docs/faq
git switch main
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git switch --create docs/faq
git switch main
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git switch -c docs/faq
git checkout main
```

### switch-easy-branch-then-return-api

**Difficulty:** Easy  
**Scenario:** branch-off-then-return  
**Alternative category:** multiple workflows

**Objective**

Create `feature/rate-limit` from the current tip of `main` and switch to it, then switch back to `main`.

**Taught / authored example — 2 counted commands**

```sh
git switch -c feature/rate-limit
git switch main
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout -b feature/rate-limit
git switch main
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch feature/rate-limit
git switch feature/rate-limit
git switch main
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git switch --create feature/rate-limit
git switch main
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git switch -c feature/rate-limit
git checkout main
```

### v21m-payments

**Difficulty:** Medium  
**Scenario:** create-without-switching  
**Alternative category:** multiple workflows

**Objective**

Create `feature/payments` and `feature/payments-tests`, both from the current tip of `main`. Finish on `feature/payments`.

**Taught / authored example — 2 counted commands**

```sh
git branch feature/payments-tests
git switch -c feature/payments
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch feature/payments-tests
git checkout -b feature/payments
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch feature/payments-tests
git branch feature/payments
git switch feature/payments
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch feature/payments-tests
git switch --create feature/payments
```

### v21m-notifications

**Difficulty:** Medium  
**Scenario:** create-without-switching  
**Alternative category:** multiple workflows

**Objective**

Create `feature/notifications` and `feature/notifications-docs`, both from the current tip of `main`. Finish on `feature/notifications`.

**Taught / authored example — 2 counted commands**

```sh
git branch feature/notifications-docs
git switch -c feature/notifications
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch feature/notifications-docs
git checkout -b feature/notifications
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch feature/notifications-docs
git branch feature/notifications
git switch feature/notifications
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch feature/notifications-docs
git switch --create feature/notifications
```

### v21m-export

**Difficulty:** Medium  
**Scenario:** create-without-switching  
**Alternative category:** multiple workflows

**Objective**

Create `feature/export` and `feature/export-docs`, both from the current tip of `main`. Finish on `feature/export`.

**Taught / authored example — 2 counted commands**

```sh
git branch feature/export-docs
git switch -c feature/export
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch feature/export-docs
git checkout -b feature/export
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch feature/export-docs
git branch feature/export
git switch feature/export
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch feature/export-docs
git switch --create feature/export
```

### v21h-from-develop

**Difficulty:** Medium  
**Scenario:** start-from-another-tip  
**Alternative category:** multiple workflows

**Objective**

Create `feature/workspace` from the current tip of `main` (__not `develop`__) and switch to it. Finish on `feature/workspace`.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/workspace main
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/workspace main
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/workspace main
git switch feature/workspace
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/workspace main
```

### v21h-hotfix-c1

**Difficulty:** Medium  
**Scenario:** start-from-another-tip  
**Alternative category:** multiple workflows

**Objective**

Create `hotfix/critical` at the older `c1` commit, __rather than at the current `main` tip__, and finish on that branch.

**Taught / authored example — 1 counted command**

```sh
git switch -c hotfix/critical c1
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b hotfix/critical c1
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch hotfix/critical c1
git switch hotfix/critical
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create hotfix/critical c1
```

### bc-hard-review-snap

**Difficulty:** Hard  
**Scenario:** save-detached-work-then-return  
**Alternative category:** multiple workflows

**Objective**

Create `review/v1-snapshot` at the detached commit you are viewing, then return to `main`.

**Keep the review branch.**

**Taught / authored example — 2 counted commands**

```sh
git switch -c review/v1-snapshot
git switch main
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout -b review/v1-snapshot
git switch main
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch review/v1-snapshot
git switch review/v1-snapshot
git switch main
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git switch --create review/v1-snapshot
git switch main
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git switch -c review/v1-snapshot
git checkout main
```

### switch-hard-detached-save-and-return

**Difficulty:** Hard  
**Scenario:** save-detached-work-then-return  
**Alternative category:** multiple workflows

**Objective**

Keep the spike commit on a new branch named `archive/spike-results`, then finish on `develop`.

**Do not move `main` or `develop`.**

**Taught / authored example — 2 counted commands**

```sh
git switch -c archive/spike-results
git switch develop
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout -b archive/spike-results
git switch develop
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git branch archive/spike-results
git switch archive/spike-results
git switch develop
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git switch --create archive/spike-results
git switch develop
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git switch -c archive/spike-results
git checkout develop
```

<a id="level-8"></a>
## Story: branch-naming-and-housekeeping

### bn-easy-corp-jira

**Difficulty:** Easy  
**Scenario:** follow-the-convention  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `PROJ-418/password-reset` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c PROJ-418/password-reset
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b PROJ-418/password-reset
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch PROJ-418/password-reset
git switch PROJ-418/password-reset
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create PROJ-418/password-reset
```

### bn-easy-startup-feat

**Difficulty:** Easy  
**Scenario:** follow-the-convention  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `feature/shopping-cart` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/shopping-cart
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/shopping-cart
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/shopping-cart
git switch feature/shopping-cart
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/shopping-cart
```

### bn-easy-oss-user

**Difficulty:** Easy  
**Scenario:** follow-the-convention  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `jdelacruz/fix-parser-edge-case` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c jdelacruz/fix-parser-edge-case
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b jdelacruz/fix-parser-edge-case
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch jdelacruz/fix-parser-edge-case
git switch jdelacruz/fix-parser-edge-case
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create jdelacruz/fix-parser-edge-case
```

### bn-easy-cap-initials

**Difficulty:** Easy  
**Scenario:** follow-the-convention  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `feature/jm/database-models` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c feature/jm/database-models
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b feature/jm/database-models
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch feature/jm/database-models
git switch feature/jm/database-models
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create feature/jm/database-models
```

### bn-easy-free-client

**Difficulty:** Easy  
**Scenario:** follow-the-convention  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `client/55-contact-form-redesign` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c client/55-contact-form-redesign
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b client/55-contact-form-redesign
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch client/55-contact-form-redesign
git switch client/55-contact-form-redesign
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create client/55-contact-form-redesign
```

### bn-easy-delete-merged-typo

**Difficulty:** Easy  
**Scenario:** delete-a-merged-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the local branch `fix/readme-typo` now that its work is on `main`.

**Taught / authored example — 1 counted command**

```sh
git branch -d fix/readme-typo
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git branch --delete fix/readme-typo
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git branch -D fix/readme-typo
```

### bn-easy-delete-merged-spike

**Difficulty:** Easy  
**Scenario:** delete-a-merged-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the local branch `spike/old-search`.

**Taught / authored example — 1 counted command**

```sh
git branch -d spike/old-search
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git branch --delete spike/old-search
```

### bn-hard-oss-rename

**Difficulty:** Easy  
**Scenario:** replace-a-badly-named-branch  
**Alternative category:** multiple workflows

**Objective**

Remove the incorrectly named local branch `myFix`. Create `fix/renderer-memory-leak` from the current `main` commit and finish on the new branch.

**Taught / authored example — 2 counted commands**

```sh
git branch -d myFix
git switch -c fix/renderer-memory-leak
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete myFix
git switch -c fix/renderer-memory-leak
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -D myFix
git switch -c fix/renderer-memory-leak
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d myFix
git checkout -b fix/renderer-memory-leak
```

**Accepted alternative 4 (workflow) — 3 counted commands**

```sh
git branch -d myFix
git branch fix/renderer-memory-leak
git switch fix/renderer-memory-leak
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git branch -d myFix
git switch --create fix/renderer-memory-leak
```

### bn-hard-corp-rename

**Difficulty:** Easy  
**Scenario:** replace-a-badly-named-branch  
**Alternative category:** multiple workflows

**Objective**

Remove the incorrectly named local branch `auth-update`. Create `PROJ-301/auth-module-update` from the current `main` commit and finish on the new branch.

**Taught / authored example — 2 counted commands**

```sh
git branch -d auth-update
git switch -c PROJ-301/auth-module-update
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete auth-update
git switch -c PROJ-301/auth-module-update
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -D auth-update
git switch -c PROJ-301/auth-module-update
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d auth-update
git checkout -b PROJ-301/auth-module-update
```

**Accepted alternative 4 (workflow) — 3 counted commands**

```sh
git branch -d auth-update
git branch PROJ-301/auth-module-update
git switch PROJ-301/auth-module-update
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git branch -d auth-update
git switch --create PROJ-301/auth-module-update
```

### bn-med-corp-notif

**Difficulty:** Medium  
**Scenario:** build-the-name-from-the-brief  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `PROJ-512/email-notification` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c PROJ-512/email-notification
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b PROJ-512/email-notification
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch PROJ-512/email-notification
git switch PROJ-512/email-notification
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create PROJ-512/email-notification
```

### bn-med-startup-bugfix

**Difficulty:** Medium  
**Scenario:** build-the-name-from-the-brief  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `bugfix/login-redirect` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c bugfix/login-redirect
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b bugfix/login-redirect
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch bugfix/login-redirect
git switch bugfix/login-redirect
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create bugfix/login-redirect
```

### bn-med-devops-scope

**Difficulty:** Medium  
**Scenario:** build-the-name-from-the-brief  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `infra/api-gateway/log-rotation` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c infra/api-gateway/log-rotation
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b infra/api-gateway/log-rotation
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch infra/api-gateway/log-rotation
git switch infra/api-gateway/log-rotation
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create infra/api-gateway/log-rotation
```

### bn-med-oss-infer

**Difficulty:** Medium  
**Scenario:** build-the-name-from-the-brief  
**Alternative category:** multiple workflows

**Objective**

Follow the stated naming convention to create `fix/tokenizer-crash` from the current `main` commit, then switch to it.

**Taught / authored example — 1 counted command**

```sh
git switch -c fix/tokenizer-crash
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git checkout -b fix/tokenizer-crash
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git branch fix/tokenizer-crash
git switch fix/tokenizer-crash
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git switch --create fix/tokenizer-crash
```

### bn-hard-startup-prefix

**Difficulty:** Medium  
**Scenario:** fix-the-name-keep-the-convention  
**Alternative category:** multiple workflows

**Objective**

Remove the incorrectly named local branch `fix/cart-total`. Create `bugfix/cart-total` from the current `main` commit and finish on the new branch.

**Taught / authored example — 2 counted commands**

```sh
git branch -d fix/cart-total
git switch -c bugfix/cart-total
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete fix/cart-total
git switch -c bugfix/cart-total
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -D fix/cart-total
git switch -c bugfix/cart-total
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d fix/cart-total
git checkout -b bugfix/cart-total
```

**Accepted alternative 4 (workflow) — 3 counted commands**

```sh
git branch -d fix/cart-total
git branch bugfix/cart-total
git switch bugfix/cart-total
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git branch -d fix/cart-total
git switch --create bugfix/cart-total
```

### bn-hard-qa-camel

**Difficulty:** Medium  
**Scenario:** fix-the-name-keep-the-convention  
**Alternative category:** multiple workflows

**Objective**

Remove the incorrectly named local branch `test/LoginFlow`. Create `test/login-flow` from the current `main` commit and finish on the new branch.

**Taught / authored example — 2 counted commands**

```sh
git branch -d test/LoginFlow
git switch -c test/login-flow
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete test/LoginFlow
git switch -c test/login-flow
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -D test/LoginFlow
git switch -c test/login-flow
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d test/LoginFlow
git checkout -b test/login-flow
```

**Accepted alternative 4 (workflow) — 3 counted commands**

```sh
git branch -d test/LoginFlow
git branch test/login-flow
git switch test/login-flow
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git branch -d test/LoginFlow
git switch --create test/login-flow
```

### bn-hard-named-branch-commit-parser

**Difficulty:** Hard  
**Scenario:** start-the-fix-on-a-well-named-branch  
**Alternative category:** multiple workflows

**Objective**

Discard the stray edit in `debug.log`. Then create `fix/parser-unicode`, switch to it, and commit __only__ `src/parser.py` with the message `Handle unicode identifiers`.

**Taught / authored example — 4 counted commands**

```sh
git restore debug.log
git switch -c fix/parser-unicode
git add src/parser.py
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git restore debug.log
git checkout -b fix/parser-unicode
git add src/parser.py
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git restore debug.log
git branch fix/parser-unicode
git switch fix/parser-unicode
git add src/parser.py
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore debug.log
git switch --create fix/parser-unicode
git add src/parser.py
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore debug.log
git switch -c fix/parser-unicode
git add -- src/parser.py
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 5 (workflow) — 4 counted commands**

```sh
git restore debug.log
git switch -c fix/parser-unicode
git add .
git commit -m "Handle unicode identifiers"
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git restore debug.log
git switch -c fix/parser-unicode
git add src/parser.py
git commit --message 'Handle unicode identifiers'
```

### bn-hard-named-branch-commit-billing

**Difficulty:** Hard  
**Scenario:** start-the-fix-on-a-well-named-branch  
**Alternative category:** multiple workflows

**Objective**

Discard the stray edit in `tmp/billing-dump.txt`, create and switch to `PROJ-733/invoice-rounding`, and commit __only__ `src/billing.py` with the message `Round invoice totals`.

**Taught / authored example — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git switch -c PROJ-733/invoice-rounding
git add src/billing.py
git commit -m "Round invoice totals"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git checkout -b PROJ-733/invoice-rounding
git add src/billing.py
git commit -m "Round invoice totals"
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git restore tmp/billing-dump.txt
git branch PROJ-733/invoice-rounding
git switch PROJ-733/invoice-rounding
git add src/billing.py
git commit -m "Round invoice totals"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git switch --create PROJ-733/invoice-rounding
git add src/billing.py
git commit -m "Round invoice totals"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git switch -c PROJ-733/invoice-rounding
git add -- src/billing.py
git commit -m "Round invoice totals"
```

**Accepted alternative 5 (workflow) — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git switch -c PROJ-733/invoice-rounding
git add .
git commit -m "Round invoice totals"
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git restore tmp/billing-dump.txt
git switch -c PROJ-733/invoice-rounding
git add src/billing.py
git commit --message 'Round invoice totals'
```

### bn-hard-clear-merged-sprint

**Difficulty:** Hard  
**Scenario:** clear-out-merged-branches  
**Alternative category:** syntax alternatives

**Objective**

Delete the local branches that are already merged into `main`.

**Keep `spike/dark-mode`.**

**Taught / authored example — 2 counted commands**

```sh
git branch -d feature/login-copy
git branch -d fix/footer-link
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete feature/login-copy
git branch -d fix/footer-link
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -d feature/login-copy fix/footer-link
git branch -d fix/footer-link
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d feature/login-copy
git branch --delete fix/footer-link
```

### bn-hard-clear-merged-release

**Difficulty:** Hard  
**Scenario:** clear-out-merged-branches  
**Alternative category:** syntax alternatives

**Objective**

Delete the local branches that are already merged into `main`.

**Keep `experiment/new-nav`.**

**Taught / authored example — 2 counted commands**

```sh
git branch -d release/1.4
git branch -d hotfix/1.4.1
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git branch --delete release/1.4
git branch -d hotfix/1.4.1
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git branch -d release/1.4 hotfix/1.4.1
git branch -d hotfix/1.4.1
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git branch -d release/1.4
git branch --delete hotfix/1.4.1
```

<a id="level-9"></a>
## Story: stashing-work-in-progress

### v23e-auth

**Difficulty:** Easy  
**Scenario:** shelve-and-switch  
**Alternative category:** syntax alternatives

**Objective**

Save the unfinished edits in a stash, then switch to `main`. Leave the working folder clean; keep the stash for later.

**Taught / authored example — 2 counted commands**

```sh
git stash
git switch main
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash
git checkout main
```

### v23e-notify

**Difficulty:** Easy  
**Scenario:** shelve-and-switch  
**Alternative category:** syntax alternatives

**Objective**

Save the unfinished edits in a stash, then switch to `develop`. Leave the working folder clean; keep the stash for later.

**Taught / authored example — 2 counted commands**

```sh
git stash
git switch develop
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash
git checkout develop
```

### v23e-cache

**Difficulty:** Easy  
**Scenario:** shelve-and-switch  
**Alternative category:** syntax alternatives

**Objective**

Save the unfinished edits in a stash, then switch to `release/v2`. Leave the working folder clean; keep the stash for later.

**Taught / authored example — 2 counted commands**

```sh
git stash
git switch release/v2
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash
git checkout release/v2
```

### stash-easy-cap-review

**Difficulty:** Easy  
**Scenario:** shelve-and-switch  
**Alternative category:** syntax alternatives

**Objective**

Save the unfinished edits in a stash, then switch to `review/groupmate-branch`. Leave the working folder clean; keep the stash for later.

**Taught / authored example — 2 counted commands**

```sh
git stash
git switch review/groupmate-branch
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash
git checkout review/groupmate-branch
```

### stash-easy-docs-switch

**Difficulty:** Easy  
**Scenario:** shelve-and-switch  
**Alternative category:** syntax alternatives

**Objective**

Save the unfinished edits in a stash, then switch to `release/stable`. Leave the working folder clean; keep the stash for later.

**Taught / authored example — 2 counted commands**

```sh
git stash
git switch release/stable
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash
git checkout release/stable
```

### stash-easy-pop-search

**Difficulty:** Easy  
**Scenario:** bring-it-back  
**Alternative category:** syntax alternatives

**Objective**

Bring the stashed search work back into your working folder and remove it from the stash.

**Do not commit it.**

**Taught / authored example — 1 counted command**

```sh
git stash pop
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git stash pop 'stash@{0}'
```

### v23m-to-main

**Difficulty:** Easy  
**Scenario:** stash-visit-return-restore  
**Alternative category:** syntax alternatives

**Objective**

Stash the unfinished edits, visit `main`, return to `feature/payments`, and restore the edits to the working folder. Finish on `feature/payments`.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch main
git switch feature/payments
git stash pop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout main
git switch feature/payments
git stash pop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch main
git checkout feature/payments
git stash pop
```

### v23m-to-hotfix

**Difficulty:** Easy  
**Scenario:** stash-visit-return-restore  
**Alternative category:** syntax alternatives

**Objective**

Stash the unfinished edits, visit `hotfix/fix-tax`, return to `feature/orders`, and restore the edits to the working folder. Finish on `feature/orders`.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch hotfix/fix-tax
git switch feature/orders
git stash pop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout hotfix/fix-tax
git switch feature/orders
git stash pop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch hotfix/fix-tax
git checkout feature/orders
git stash pop
```

### v23m-to-release

**Difficulty:** Easy  
**Scenario:** stash-visit-return-restore  
**Alternative category:** syntax alternatives

**Objective**

Stash the unfinished edits, visit `release/v2`, return to `feature/analytics`, and restore the edits to the working folder. Finish on `feature/analytics`.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch release/v2
git switch feature/analytics
git stash pop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout release/v2
git switch feature/analytics
git stash pop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch release/v2
git checkout feature/analytics
git stash pop
```

### stash-med-corp-named

**Difficulty:** Easy  
**Scenario:** stash-visit-return-restore  
**Alternative category:** syntax alternatives

**Objective**

Stash the unfinished edits, visit `hotfix/tax-fix`, return to `feature/billing`, and restore the edits to the working folder. Finish on `feature/billing`.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch hotfix/tax-fix
git switch feature/billing
git stash pop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout hotfix/tax-fix
git switch feature/billing
git stash pop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch hotfix/tax-fix
git checkout feature/billing
git stash pop
```

### v23h-dropped-auth

**Difficulty:** Medium  
**Scenario:** discard-a-cancelled-draft  
**Alternative category:** syntax alternatives

**Objective**

Check `main` without carrying your unfinished edits along, then return to `feature/auth-rework`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch main
git switch feature/auth-rework
git stash drop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout main
git switch feature/auth-rework
git stash drop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch main
git checkout feature/auth-rework
git stash drop
```

### v23h-dropped-api

**Difficulty:** Medium  
**Scenario:** discard-a-cancelled-draft  
**Alternative category:** syntax alternatives

**Objective**

Check `hotfix/urgent` without carrying your unfinished edits along, then return to `feature/api-v2`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch hotfix/urgent
git switch feature/api-v2
git stash drop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout hotfix/urgent
git switch feature/api-v2
git stash drop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch hotfix/urgent
git checkout feature/api-v2
git stash drop
```

### stash-hard-oss-multi

**Difficulty:** Medium  
**Scenario:** two-stashes-keep-the-right-one  
**Alternative category:** syntax alternatives

**Objective**

Discard __only__ the abandoned newest stash entry. Restore the remaining older stash to your working files and finish on `feature/lexer`.

**Taught / authored example — 2 counted commands**

```sh
git stash drop stash@{0}
git stash pop
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash pop 'stash@{1}'
git stash pop
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git stash drop
git stash pop
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git stash drop stash@{0}
git stash drop
```

### stash-hard-two-stashes-reports

**Difficulty:** Medium  
**Scenario:** two-stashes-keep-the-right-one  
**Alternative category:** syntax alternatives

**Objective**

Discard the chart experiment from the stash, then restore the monthly totals work into your working folder. **Finish with an empty stash.**

**Taught / authored example — 2 counted commands**

```sh
git stash drop stash@{0}
git stash pop
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git stash drop
git stash pop
```

### v23h-dropped-refactor

**Difficulty:** Hard  
**Scenario:** cancelled-work-clean-exit  
**Alternative category:** syntax alternatives

**Objective**

Check `release/v1` without carrying your unfinished edits along, then return to `feature/refactor`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch release/v1
git switch feature/refactor
git stash drop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash
git checkout release/v1
git switch feature/refactor
git stash drop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git switch release/v1
git checkout feature/refactor
git stash drop
```

### stash-hard-cancelled-experiment

**Difficulty:** Hard  
**Scenario:** cancelled-work-clean-exit  
**Alternative category:** syntax alternatives

**Objective**

Visit `release/v3` without carrying your edits along, return to `feature/experiment`, and finish with a clean working folder and an empty stash.

**Taught / authored example — 4 counted commands**

```sh
git stash
git switch release/v3
git switch feature/experiment
git stash drop
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git stash push
git switch release/v3
git switch feature/experiment
git stash drop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git stash
git checkout release/v3
git switch feature/experiment
git stash drop
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git stash
git switch release/v3
git checkout feature/experiment
git stash drop
```

### stash-hard-park-draft-search

**Difficulty:** Hard  
**Scenario:** park-the-draft-for-later  
**Alternative category:** syntax alternatives

**Objective**

Visit `release/v4` without carrying your edits along, then return to `feature/search`. **Finish with a clean working folder and the draft still saved in the stash.**

**Taught / authored example — 3 counted commands**

```sh
git stash
git switch release/v4
git switch feature/search
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git stash push
git switch release/v4
git switch feature/search
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git stash
git checkout release/v4
git switch feature/search
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git stash
git switch release/v4
git checkout feature/search
```

### stash-hard-park-draft-billing

**Difficulty:** Hard  
**Scenario:** park-the-draft-for-later  
**Alternative category:** syntax alternatives

**Objective**

Visit `hotfix/tax` without carrying your edits along, then return to `feature/billing`. **Finish with a clean working folder and the draft still saved in the stash.**

**Taught / authored example — 3 counted commands**

```sh
git stash
git switch hotfix/tax
git switch feature/billing
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git stash push
git switch hotfix/tax
git switch feature/billing
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git stash
git checkout hotfix/tax
git switch feature/billing
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git stash
git switch hotfix/tax
git checkout feature/billing
```

<a id="level-10"></a>
## Story: pushing-to-a-remote

### v24e-orders

**Difficulty:** Easy  
**Scenario:** publish-a-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish the committed local `feature/orders` to `origin` for teammates to access.

**Taught / authored example — 1 counted command**

```sh
git push origin feature/orders
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push
```

### v24e-parser

**Difficulty:** Easy  
**Scenario:** publish-a-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish the committed local `feature/parser` to `origin` for teammates to access.

**Taught / authored example — 1 counted command**

```sh
git push origin feature/parser
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push
```

### push-easy-cap-auth

**Difficulty:** Easy  
**Scenario:** publish-a-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish the committed local `feature/user-auth` to `origin` for teammates to access.

**Taught / authored example — 1 counted command**

```sh
git push origin feature/user-auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push
```

### push-easy-free-landing

**Difficulty:** Easy  
**Scenario:** publish-a-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish the committed local `feature/client-landing` to `origin` for teammates to access.

**Taught / authored example — 1 counted command**

```sh
git push origin feature/client-landing
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push
```

### v24m-auth

**Difficulty:** Easy  
**Scenario:** publish-and-track  
**Alternative category:** syntax alternatives

**Objective**

Publish `feature/auth` to `origin` and set the corresponding remote branch as its upstream.

**Taught / authored example — 1 counted command**

```sh
git push -u origin feature/auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push --set-upstream origin feature/auth
```

### v24m-orders

**Difficulty:** Easy  
**Scenario:** publish-and-track  
**Alternative category:** syntax alternatives

**Objective**

Publish `feature/orders` to `origin` and set the corresponding remote branch as its upstream.

**Taught / authored example — 1 counted command**

```sh
git push -u origin feature/orders
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push --set-upstream origin feature/orders
```

### v24m-parser

**Difficulty:** Easy  
**Scenario:** track-another-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish `feature/parser` to `origin` and set the corresponding remote branch as its upstream.

**Taught / authored example — 1 counted command**

```sh
git push -u origin feature/parser
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push --set-upstream origin feature/parser
```

### push-med-docs-track

**Difficulty:** Easy  
**Scenario:** track-another-branch  
**Alternative category:** syntax alternatives

**Objective**

Publish `feature/v2-migration-guide` to `origin` and set the corresponding remote branch as its upstream.

**Taught / authored example — 1 counted command**

```sh
git push -u origin feature/v2-migration-guide
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push --set-upstream origin feature/v2-migration-guide
```

### push-medium-branch-commit-publish-search

**Difficulty:** Medium  
**Scenario:** branch-commit-publish  
**Alternative category:** multiple workflows

**Objective**

Create and switch to `feature/search-filters`, commit `src/filters.js` with the message `Add search filters`, then publish the branch to `origin` and set its upstream.

**Taught / authored example — 4 counted commands**

```sh
git switch -c feature/search-filters
git add src/filters.js
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout -b feature/search-filters
git add src/filters.js
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git branch feature/search-filters
git switch feature/search-filters
git add src/filters.js
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch --create feature/search-filters
git add src/filters.js
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git switch -c feature/search-filters
git add -- src/filters.js
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 5 (workflow) — 4 counted commands**

```sh
git switch -c feature/search-filters
git add .
git commit -m "Add search filters"
git push -u origin feature/search-filters
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git switch -c feature/search-filters
git add src/filters.js
git commit --message 'Add search filters'
git push -u origin feature/search-filters
```

**Accepted alternative 7 (syntax) — 4 counted commands**

```sh
git switch -c feature/search-filters
git add src/filters.js
git commit -m "Add search filters"
git push --set-upstream origin feature/search-filters
```

### push-medium-branch-commit-publish-invoices

**Difficulty:** Medium  
**Scenario:** branch-commit-publish  
**Alternative category:** multiple workflows

**Objective**

Create and switch to `feature/invoice-pdf`, commit `src/invoice_pdf.py` with the message `Add invoice PDF export`, then publish the branch to `origin` with its upstream set.

**Taught / authored example — 4 counted commands**

```sh
git switch -c feature/invoice-pdf
git add src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout -b feature/invoice-pdf
git add src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git branch feature/invoice-pdf
git switch feature/invoice-pdf
git add src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch --create feature/invoice-pdf
git add src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git switch -c feature/invoice-pdf
git add -- src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 5 (workflow) — 4 counted commands**

```sh
git switch -c feature/invoice-pdf
git add .
git commit -m "Add invoice PDF export"
git push -u origin feature/invoice-pdf
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git switch -c feature/invoice-pdf
git add src/invoice_pdf.py
git commit --message 'Add invoice PDF export'
git push -u origin feature/invoice-pdf
```

**Accepted alternative 7 (syntax) — 4 counted commands**

```sh
git switch -c feature/invoice-pdf
git add src/invoice_pdf.py
git commit -m "Add invoice PDF export"
git push --set-upstream origin feature/invoice-pdf
```

### push-hard-amend-then-lease-api

**Difficulty:** Hard  
**Scenario:** amend-then-republish  
**Alternative category:** syntax alternatives

**Objective**

Change the last commit's message to `Add retry to API client`, then update `origin`'s `feature/api-retry` **without overwriting work you have not seen**.

**Taught / authored example — 2 counted commands**

```sh
git commit --amend -m "Add retry to API client"
git push --force-with-lease origin feature/api-retry
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git commit --amend --message 'Add retry to API client'
git push --force-with-lease origin feature/api-retry
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git commit --amend -m "Add retry to API client"
git push --force-with-lease
```

### push-hard-amend-then-lease-docs

**Difficulty:** Hard  
**Scenario:** amend-then-republish  
**Alternative category:** syntax alternatives

**Objective**

Change the last commit's message to `Document SSO setup`, then update `origin`'s `docs/sso` **safely**.

**Taught / authored example — 2 counted commands**

```sh
git commit --amend -m "Document SSO setup"
git push --force-with-lease origin docs/sso
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git commit --amend --message 'Document SSO setup'
git push --force-with-lease origin docs/sso
```

<a id="level-11"></a>
## Story: fetching-and-pulling

### v25m-develop

**Difficulty:** Easy  
**Scenario:** bring-more-commits-in  
**Alternative category:** syntax alternatives

**Objective**

Bring the latest `origin/develop` commits into your current local `develop` branch.

**Taught / authored example — 1 counted command**

```sh
git pull origin develop
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git pull
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git pull --ff-only origin develop
```

### pull-med-free-client

**Difficulty:** Easy  
**Scenario:** bring-more-commits-in  
**Alternative category:** syntax alternatives

**Objective**

Bring the latest `origin/staging` commits into your current local `staging` branch.

**Taught / authored example — 1 counted command**

```sh
git pull origin staging
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git pull
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git pull --ff-only origin staging
```

### pull-medium-update-then-branch-ui

**Difficulty:** Medium  
**Scenario:** update-then-branch  
**Alternative category:** multiple workflows

**Objective**

Bring `main` up to date with `origin`, then create and switch to `feature/dark-mode` from it.

**Taught / authored example — 2 counted commands**

```sh
git pull origin main
git switch -c feature/dark-mode
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull
git switch -c feature/dark-mode
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git pull origin main
git checkout -b feature/dark-mode
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git pull origin main
git branch feature/dark-mode
git switch feature/dark-mode
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git pull origin main
git switch --create feature/dark-mode
```

### pull-medium-update-then-branch-api

**Difficulty:** Medium  
**Scenario:** update-then-branch  
**Alternative category:** multiple workflows

**Objective**

Bring `main` up to date with `origin`, then create and switch to `feature/webhooks` from it.

**Taught / authored example — 2 counted commands**

```sh
git pull origin main
git switch -c feature/webhooks
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull
git switch -c feature/webhooks
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git pull origin main
git checkout -b feature/webhooks
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git pull origin main
git branch feature/webhooks
git switch feature/webhooks
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git pull origin main
git switch --create feature/webhooks
```

### v25h-develop

**Difficulty:** Hard  
**Scenario:** review-incoming-work  
**Alternative category:** syntax alternatives

**Objective**

A teammate has pushed new commits to `develop`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `develop` include it.

**Taught / authored example — 2 counted commands**

```sh
git fetch origin
git log --oneline develop..origin/develop
git pull origin develop
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git fetch origin
git log --oneline develop..origin/develop
git pull
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git fetch origin
git log --oneline develop..origin/develop
git pull --ff-only origin develop
```

### fetch-hard-oss-review

**Difficulty:** Hard  
**Scenario:** review-incoming-work  
**Alternative category:** syntax alternatives

**Objective**

A teammate has pushed new commits to `release/next`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `release/next` include it.

**Taught / authored example — 2 counted commands**

```sh
git fetch origin
git log --oneline release/next..origin/release/next
git pull origin release/next
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git fetch origin
git log --oneline release/next..origin/release/next
git pull
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git fetch origin
git log --oneline release/next..origin/release/next
git pull --ff-only origin release/next
```

### pull-hard-stash-pull-pop-docs

**Difficulty:** Hard  
**Scenario:** pull-with-work-in-progress  
**Alternative category:** syntax alternatives

**Objective**

Update `main` from `origin` without losing your edits to `docs/guide.md`.

**Keep the edits uncommitted and leave nothing in the stash.**

**Taught / authored example — 3 counted commands**

```sh
git stash
git pull origin main
git stash pop
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git stash push
git pull origin main
git stash pop
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git stash
git pull
git stash pop
```

### pull-hard-stash-pull-pop-app

**Difficulty:** Hard  
**Scenario:** pull-with-work-in-progress  
**Alternative category:** syntax alternatives

**Objective**

Update `develop` from `origin` without losing your edits to `src/app.py`.

**Keep them uncommitted and leave nothing in the stash.**

**Taught / authored example — 3 counted commands**

```sh
git stash
git pull origin develop
git stash pop
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git stash push
git pull origin develop
git stash pop
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git stash
git pull
git stash pop
```

<a id="level-12"></a>
## Story: reconciling-diverged-histories

### v26e-payments

**Difficulty:** Easy  
**Scenario:** pull-then-push-again  
**Alternative category:** syntax alternatives

**Objective**

Pull `origin/feature/payments` into your current local branch to reconcile the rejected push, then push `feature/payments` again.

**Taught / authored example — 2 counted commands**

```sh
git pull origin feature/payments
git push origin feature/payments
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull
git push origin feature/payments
```

### v26e-hotfix

**Difficulty:** Easy  
**Scenario:** pull-then-push-again  
**Alternative category:** syntax alternatives

**Objective**

Pull `origin/hotfix/critical` into your current local branch to reconcile the rejected push, then push `hotfix/critical` again.

**Taught / authored example — 2 counted commands**

```sh
git pull origin hotfix/critical
git push origin hotfix/critical
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull
git push origin hotfix/critical
```

### rec-easy-cap-ui

**Difficulty:** Easy  
**Scenario:** pull-then-push-again  
**Alternative category:** syntax alternatives

**Objective**

Pull `origin/feature/ui-layout` into your current local branch to reconcile the rejected push, then push `feature/ui-layout` again.

**Taught / authored example — 2 counted commands**

```sh
git pull origin feature/ui-layout
git push origin feature/ui-layout
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull
git push origin feature/ui-layout
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git pull origin feature/ui-layout
git push
```

### rec-easy-docs-chapter

**Difficulty:** Easy  
**Scenario:** pull-then-push-again  
**Alternative category:** syntax alternatives

**Objective**

Pull `origin/main` into your current local branch to reconcile the rejected push, then push `main` again.

**Taught / authored example — 2 counted commands**

```sh
git pull origin main
git push origin main
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git pull origin main
git push
```

### rec-med-qa-testrunner

**Difficulty:** Easy  
**Scenario:** fetch-merge-push-practice  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, merge `origin/feature/test-runner-v2` into your current `feature/test-runner-v2` branch, then push the combined result.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/test-runner-v2
git push origin feature/test-runner-v2
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/test-runner-v2
git push
```

### rec-medium-commit-then-reconcile-docs

**Difficulty:** Medium  
**Scenario:** commit-reconcile-publish  
**Alternative category:** multiple workflows

**Objective**

Unstage `notes/draft.md` and keep its edits. Commit `docs/setup.md` with the message `Document local setup`, integrate `origin/main` by pulling, and push `main` to `origin`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged notes/draft.md
git commit -m "Document local setup"
git pull origin main
git push origin main
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- notes/draft.md
git commit -m "Document local setup"
git pull origin main
git push origin main
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged notes/draft.md
git commit --message 'Document local setup'
git pull origin main
git push origin main
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged notes/draft.md
git commit -m "Document local setup"
git pull
git push origin main
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore --staged notes/draft.md
git commit -m "Document local setup"
git pull origin main
git push
```

### rec-medium-commit-then-reconcile-api

**Difficulty:** Medium  
**Scenario:** commit-reconcile-publish  
**Alternative category:** multiple workflows

**Objective**

Unstage `scratch/payload.json` and keep its edits. Commit `src/health.py` with the message `Add health check`, integrate `origin/develop` by pulling, and push `develop` to `origin`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged scratch/payload.json
git commit -m "Add health check"
git pull origin develop
git push origin develop
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- scratch/payload.json
git commit -m "Add health check"
git pull origin develop
git push origin develop
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged scratch/payload.json
git commit --message 'Add health check'
git pull origin develop
git push origin develop
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged scratch/payload.json
git commit -m "Add health check"
git pull origin develop
git push
```

### v26h-auth

**Difficulty:** Medium  
**Scenario:** reconcile-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Combine the teammate's newer `origin/feature/auth` work with your own commits on `feature/auth`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `feature/auth`.

**Taught / authored example — 4 counted commands**

```sh
git switch feature/auth
git fetch origin
git merge origin/feature/auth
git push origin feature/auth
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout feature/auth
git fetch origin
git merge origin/feature/auth
git push origin feature/auth
```

### v26h-payments

**Difficulty:** Medium  
**Scenario:** reconcile-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Combine the teammate's newer `origin/feature/payments` work with your own commits on `feature/payments`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `feature/payments`.

**Taught / authored example — 4 counted commands**

```sh
git switch feature/payments
git fetch origin
git merge origin/feature/payments
git push origin feature/payments
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout feature/payments
git fetch origin
git merge origin/feature/payments
git push origin feature/payments
```

### v26h-hotfix

**Difficulty:** Hard  
**Scenario:** reconcile-and-publish-under-pressure  
**Alternative category:** syntax alternatives

**Objective**

Combine the teammate's newer `origin/hotfix/critical` work with your own commits on `hotfix/critical`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `hotfix/critical`.

**Taught / authored example — 4 counted commands**

```sh
git switch hotfix/critical
git fetch origin
git merge origin/hotfix/critical
git push origin hotfix/critical
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout hotfix/critical
git fetch origin
git merge origin/hotfix/critical
git push origin hotfix/critical
```

### rec-hard-corp-audit

**Difficulty:** Hard  
**Scenario:** reconcile-and-publish-under-pressure  
**Alternative category:** syntax alternatives

**Objective**

Combine the teammate's newer `origin/feature/compliance-audit` work with your own commits on `feature/compliance-audit`, and publish the combined result to `origin`. **`develop` must not receive any of this work.** Finish on `feature/compliance-audit`.

**Taught / authored example — 4 counted commands**

```sh
git switch feature/compliance-audit
git fetch origin
git merge origin/feature/compliance-audit
git push origin feature/compliance-audit
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout feature/compliance-audit
git fetch origin
git merge origin/feature/compliance-audit
git push origin feature/compliance-audit
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch feature/compliance-audit
git fetch origin
git merge origin/feature/compliance-audit
git push
```

### rec-hard-commit-fetch-merge-search

**Difficulty:** Hard  
**Scenario:** commit-fetch-merge-publish  
**Alternative category:** multiple workflows

**Objective**

Commit only the ranking change with the message `Tune search ranking`, keeping your notes out of the commit. Then combine it with the newer `origin/feature/search` and publish `feature/search` to `origin`.

**Taught / authored example — 5 counted commands**

```sh
git restore --staged notes/plan.md
git commit -m "Tune search ranking"
git fetch origin
git merge origin/feature/search
git push origin feature/search
```

**Accepted alternative 1 (workflow) — 5 counted commands**

```sh
git reset HEAD -- notes/plan.md
git commit -m "Tune search ranking"
git fetch origin
git merge origin/feature/search
git push origin feature/search
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git restore --staged notes/plan.md
git commit --message 'Tune search ranking'
git fetch origin
git merge origin/feature/search
git push origin feature/search
```

### rec-hard-commit-fetch-merge-billing

**Difficulty:** Hard  
**Scenario:** commit-fetch-merge-publish  
**Alternative category:** multiple workflows

**Objective**

Commit only the rounding change with the message `Round invoice totals`, keeping the dump out of the commit. Then combine it with the newer `origin/feature/billing` and publish `feature/billing` to `origin`.

**Taught / authored example — 5 counted commands**

```sh
git restore --staged tmp/invoice-dump.json
git commit -m "Round invoice totals"
git fetch origin
git merge origin/feature/billing
git push origin feature/billing
```

**Accepted alternative 1 (workflow) — 5 counted commands**

```sh
git reset HEAD -- tmp/invoice-dump.json
git commit -m "Round invoice totals"
git fetch origin
git merge origin/feature/billing
git push origin feature/billing
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git restore --staged tmp/invoice-dump.json
git commit --message 'Round invoice totals'
git fetch origin
git merge origin/feature/billing
git push origin feature/billing
```

<a id="level-13"></a>
## Story: completing-branch-merges

### v27m-auth

**Difficulty:** Easy  
**Scenario:** keep-a-visible-merge  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/auth` into `main` with an explicit merge commit, even if a fast forward is possible. Finish on `main`.

**Required techniques:** merge

**Taught / authored example — 1 counted command**

```sh
git merge --no-ff feature/auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git merge feature/auth --no-ff
```

### v27m-payments

**Difficulty:** Easy  
**Scenario:** keep-a-visible-merge  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/payments` into `develop` with an explicit merge commit, even if a fast forward is possible. Finish on `develop`.

**Required techniques:** merge

**Taught / authored example — 1 counted command**

```sh
git merge --no-ff feature/payments
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git merge feature/payments --no-ff
```

### v27m-hotfix

**Difficulty:** Easy  
**Scenario:** no-ff-practice  
**Alternative category:** syntax alternatives

**Objective**

Merge `hotfix/fix-critical` into `release/v2` with an explicit merge commit, even if a fast forward is possible. Finish on `release/v2`.

**Required techniques:** merge

**Taught / authored example — 1 counted command**

```sh
git merge --no-ff hotfix/fix-critical
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git merge hotfix/fix-critical --no-ff
```

### merge-med-corp-sso

**Difficulty:** Easy  
**Scenario:** no-ff-practice  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/sso-integration` into `release/v1` with an explicit merge commit, even if a fast forward is possible. Finish on `release/v1`.

**Required techniques:** merge

**Taught / authored example — 1 counted command**

```sh
git merge --no-ff feature/sso-integration
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git merge feature/sso-integration --no-ff
```

### merge-medium-commit-switch-noff-reports

**Difficulty:** Medium  
**Scenario:** finish-then-land  
**Alternative category:** multiple workflows

**Objective**

Commit `src/reports.py` on `feature/reports` with the message `Add monthly report`, then switch to `main` and merge `feature/reports` with a merge commit.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git add src/reports.py
git commit -m "Add monthly report"
git switch main
git merge --no-ff feature/reports
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git add -- src/reports.py
git commit -m "Add monthly report"
git switch main
git merge --no-ff feature/reports
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git add .
git commit -m "Add monthly report"
git switch main
git merge --no-ff feature/reports
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git add src/reports.py
git commit --message 'Add monthly report'
git switch main
git merge --no-ff feature/reports
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git add src/reports.py
git commit -am 'Add monthly report'
git switch main
git merge --no-ff feature/reports
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git add src/reports.py
git commit -m "Add monthly report"
git checkout main
git merge --no-ff feature/reports
```

### merge-medium-commit-switch-noff-auth

**Difficulty:** Medium  
**Scenario:** finish-then-land  
**Alternative category:** multiple workflows

**Objective**

Commit `src/mfa.py` on `feature/mfa` with the message `Add MFA prompt`, then switch to `develop` and merge `feature/mfa` with a merge commit.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git add src/mfa.py
git commit -m "Add MFA prompt"
git switch develop
git merge --no-ff feature/mfa
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git add -- src/mfa.py
git commit -m "Add MFA prompt"
git switch develop
git merge --no-ff feature/mfa
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git add .
git commit -m "Add MFA prompt"
git switch develop
git merge --no-ff feature/mfa
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git add src/mfa.py
git commit --message 'Add MFA prompt'
git switch develop
git merge --no-ff feature/mfa
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git add src/mfa.py
git commit -am 'Add MFA prompt'
git switch develop
git merge --no-ff feature/mfa
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git add src/mfa.py
git commit -m "Add MFA prompt"
git checkout develop
git merge --no-ff feature/mfa
```

### v27h-auth

**Difficulty:** Medium  
**Scenario:** land-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Bring `feature/auth` into `main` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `main`.

**Required techniques:** merge

**Taught / authored example — 2 counted commands**

```sh
git switch main
git merge --no-ff feature/auth
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout main
git merge --no-ff feature/auth
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git switch main
git merge feature/auth --no-ff
```

### v27h-payments

**Difficulty:** Medium  
**Scenario:** land-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Bring `feature/payments` into `develop` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `develop`.

**Required techniques:** merge

**Taught / authored example — 2 counted commands**

```sh
git switch develop
git merge --no-ff feature/payments
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout develop
git merge --no-ff feature/payments
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git switch develop
git merge feature/payments --no-ff
```

### v27h-hotfix

**Difficulty:** Hard  
**Scenario:** land-a-release-fix-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Bring `hotfix/critical` into `release/v1` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `release/v1`.

**Required techniques:** merge

**Taught / authored example — 2 counted commands**

```sh
git switch release/v1
git merge --no-ff hotfix/critical
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout release/v1
git merge --no-ff hotfix/critical
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git switch release/v1
git merge hotfix/critical --no-ff
```

### merge-hard-devops-cert

**Difficulty:** Hard  
**Scenario:** land-a-release-fix-from-the-wrong-branch  
**Alternative category:** syntax alternatives

**Objective**

Bring `hotfix/cert-renewal` into `release/stable` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current-work` exactly as it is** and finish on `release/stable`.

**Required techniques:** merge

**Taught / authored example — 2 counted commands**

```sh
git switch release/stable
git merge --no-ff hotfix/cert-renewal
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git checkout release/stable
git merge --no-ff hotfix/cert-renewal
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git switch release/stable
git merge hotfix/cert-renewal --no-ff
```

### merge-hard-land-publish-tidy-search

**Difficulty:** Hard  
**Scenario:** land-publish-tidy-up  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/search` into `main` with a merge commit, push `main` to `origin`, and delete the local `feature/search` with the safe delete.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git switch main
git merge --no-ff feature/search
git push origin main
git branch -d feature/search
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout main
git merge --no-ff feature/search
git push origin main
git branch -d feature/search
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch main
git merge --no-ff feature/search
git push
git branch -d feature/search
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch main
git merge --no-ff feature/search
git push origin main
git branch --delete feature/search
```

### merge-hard-land-publish-tidy-billing

**Difficulty:** Hard  
**Scenario:** land-publish-tidy-up  
**Alternative category:** syntax alternatives

**Objective**

Merge `hotfix/billing-rounding` into `release/v2` with a merge commit, push `release/v2` to `origin`, and delete the local hotfix branch safely.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git switch release/v2
git merge --no-ff hotfix/billing-rounding
git push origin release/v2
git branch -d hotfix/billing-rounding
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout release/v2
git merge --no-ff hotfix/billing-rounding
git push origin release/v2
git branch -d hotfix/billing-rounding
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch release/v2
git merge --no-ff hotfix/billing-rounding
git push
git branch -d hotfix/billing-rounding
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch release/v2
git merge --no-ff hotfix/billing-rounding
git push origin release/v2
git branch --delete hotfix/billing-rounding
```

<a id="level-14"></a>
## Story: squash-merging

### v28e-auth

**Difficulty:** Easy  
**Scenario:** squash-into-one-commit  
**Alternative category:** syntax alternatives

**Objective**

Squash the changes from `feature/auth` into your current `main` branch. Commit with the exact message `Add auth feature`.

**Taught / authored example — 2 counted commands**

```sh
git merge --squash feature/auth
git commit -m "Add auth feature"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git merge feature/auth --squash
git commit -m "Add auth feature"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git merge --squash feature/auth
git commit --message 'Add auth feature'
```

### v28e-orders

**Difficulty:** Easy  
**Scenario:** squash-into-one-commit  
**Alternative category:** syntax alternatives

**Objective**

Squash the changes from `feature/orders` into your current `develop` branch. Commit with the exact message `Add orders feature`.

**Taught / authored example — 2 counted commands**

```sh
git merge --squash feature/orders
git commit -m "Add orders feature"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git merge feature/orders --squash
git commit -m "Add orders feature"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git merge --squash feature/orders
git commit --message 'Add orders feature'
```

### v28e-parser

**Difficulty:** Easy  
**Scenario:** squash-into-one-commit  
**Alternative category:** syntax alternatives

**Objective**

Squash the changes from `feature/parser` into your current `release/v2` branch. Commit with the exact message `Add parser feature`.

**Taught / authored example — 2 counted commands**

```sh
git merge --squash feature/parser
git commit -m "Add parser feature"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git merge feature/parser --squash
git commit -m "Add parser feature"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git merge --squash feature/parser
git commit --message 'Add parser feature'
```

### squash-easy-cap-report

**Difficulty:** Easy  
**Scenario:** squash-into-one-commit  
**Alternative category:** syntax alternatives

**Objective**

Squash the changes from `feature/report-generator` into your current `integration` branch. Commit with the exact message `Add report generator module`.

**Taught / authored example — 2 counted commands**

```sh
git merge --squash feature/report-generator
git commit -m "Add report generator module"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git merge feature/report-generator --squash
git commit -m "Add report generator module"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git merge --squash feature/report-generator
git commit --message 'Add report generator module'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git merge --squash feature/report-generator
git commit '--message=Add report generator module'
```

### squash-easy-free-payment

**Difficulty:** Easy  
**Scenario:** squash-into-one-commit  
**Alternative category:** syntax alternatives

**Objective**

Squash the changes from `feature/payment-flow` into your current `staging` branch. Commit with the exact message `Add payment flow`.

**Taught / authored example — 2 counted commands**

```sh
git merge --squash feature/payment-flow
git commit -m "Add payment flow"
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git merge feature/payment-flow --squash
git commit -m "Add payment flow"
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git merge --squash feature/payment-flow
git commit --message 'Add payment flow'
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git merge --squash feature/payment-flow
git commit '--message=Add payment flow'
```

### v28h-auth

**Difficulty:** Easy  
**Scenario:** squash-then-force-delete  
**Alternative category:** syntax alternatives

**Objective**

Bring all of `feature/auth`'s work into `main` as a single new commit named `Add auth feature`, then leave no local `feature/auth` branch behind.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/auth
git commit -m "Add auth feature"
git branch -D feature/auth
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/auth --squash
git commit -m "Add auth feature"
git branch -D feature/auth
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/auth
git commit --message 'Add auth feature'
git branch -D feature/auth
```

### v28h-orders

**Difficulty:** Easy  
**Scenario:** squash-then-force-delete  
**Alternative category:** syntax alternatives

**Objective**

Bring all of `feature/orders`'s work into `develop` as a single new commit named `Add orders feature`, then leave no local `feature/orders` branch behind.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/orders
git commit -m "Add orders feature"
git branch -D feature/orders
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/orders --squash
git commit -m "Add orders feature"
git branch -D feature/orders
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/orders
git commit --message 'Add orders feature'
git branch -D feature/orders
```

### v28h-parser

**Difficulty:** Easy  
**Scenario:** one-commit-no-leftovers  
**Alternative category:** syntax alternatives

**Objective**

Bring all of `feature/parser`'s work into `release/v2` as a single new commit named `Add parser feature`, then leave no local `feature/parser` branch behind.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/parser
git commit -m "Add parser feature"
git branch -D feature/parser
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/parser --squash
git commit -m "Add parser feature"
git branch -D feature/parser
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/parser
git commit --message 'Add parser feature'
git branch -D feature/parser
```

### squash-hard-devops-log

**Difficulty:** Easy  
**Scenario:** one-commit-no-leftovers  
**Alternative category:** syntax alternatives

**Objective**

Bring all of `feature/log-rotation`'s work into `main` as a single new commit named `Add log rotation configuration`, then leave no local `feature/log-rotation` branch behind.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/log-rotation
git commit -m "Add log rotation configuration"
git branch -D feature/log-rotation
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/log-rotation --squash
git commit -m "Add log rotation configuration"
git branch -D feature/log-rotation
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/log-rotation
git commit --message 'Add log rotation configuration'
git branch -D feature/log-rotation
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git merge --squash feature/log-rotation
git commit '--message=Add log rotation configuration'
git branch -D feature/log-rotation
```

### v28m-auth

**Difficulty:** Medium  
**Scenario:** squash-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, then squash the changes from `origin/feature/auth` into your current `main` branch. Commit with the exact message `Add auth feature`.

**Taught / authored example — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/auth
git commit -m "Add auth feature"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/auth --squash
git commit -m "Add auth feature"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/auth
git commit --message 'Add auth feature'
```

### v28m-orders

**Difficulty:** Medium  
**Scenario:** squash-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, then squash the changes from `origin/feature/orders` into your current `develop` branch. Commit with the exact message `Add orders feature`.

**Taught / authored example — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/orders
git commit -m "Add orders feature"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/orders --squash
git commit -m "Add orders feature"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/orders
git commit --message 'Add orders feature'
```

### v28m-parser

**Difficulty:** Medium  
**Scenario:** squash-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, then squash the changes from `origin/feature/parser` into your current `release/v2` branch. Commit with the exact message `Add parser feature`.

**Taught / authored example — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/parser
git commit -m "Add parser feature"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/parser --squash
git commit -m "Add parser feature"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/parser
git commit --message 'Add parser feature'
```

### squash-med-corp-gdpr

**Difficulty:** Medium  
**Scenario:** squash-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, then squash the changes from `origin/feature/gdpr-export` into your current `staging` branch. Commit with the exact message `Add GDPR data export endpoint`.

**Taught / authored example — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/gdpr-export
git commit -m "Add GDPR data export endpoint"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge origin/feature/gdpr-export --squash
git commit -m "Add GDPR data export endpoint"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/gdpr-export
git commit --message 'Add GDPR data export endpoint'
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/gdpr-export
git commit '--message=Add GDPR data export endpoint'
```

### squash-medium-squash-publish-onboarding

**Difficulty:** Medium  
**Scenario:** squash-and-publish  
**Alternative category:** syntax alternatives

**Objective**

Bring `feature/onboarding` into `main` as one new commit with the message `Add onboarding flow`, then push `main` to `origin`.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/onboarding
git commit -m "Add onboarding flow"
git push origin main
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/onboarding --squash
git commit -m "Add onboarding flow"
git push origin main
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/onboarding
git commit --message 'Add onboarding flow'
git push origin main
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git merge --squash feature/onboarding
git commit -m "Add onboarding flow"
git push
```

### squash-medium-squash-publish-export

**Difficulty:** Medium  
**Scenario:** squash-and-publish  
**Alternative category:** syntax alternatives

**Objective**

Bring `feature/export-csv` into `develop` as one new commit with the message `Add CSV export`, then push `develop` to `origin`.

**Taught / authored example — 3 counted commands**

```sh
git merge --squash feature/export-csv
git commit -m "Add CSV export"
git push origin develop
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/export-csv --squash
git commit -m "Add CSV export"
git push origin develop
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --squash feature/export-csv
git commit --message 'Add CSV export'
git push origin develop
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git merge --squash feature/export-csv
git commit -m "Add CSV export"
git push
```

### squash-hard-switch-squash-cleanup-cli

**Difficulty:** Hard  
**Scenario:** squash-land-from-another-branch  
**Alternative category:** syntax alternatives

**Objective**

Switch to `main`, bring `feature/cli-colors` in as one commit with the message `Add CLI colors`, then delete the local feature branch.

**Taught / authored example — 4 counted commands**

```sh
git switch main
git merge --squash feature/cli-colors
git commit -m "Add CLI colors"
git branch -D feature/cli-colors
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout main
git merge --squash feature/cli-colors
git commit -m "Add CLI colors"
git branch -D feature/cli-colors
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch main
git merge --squash feature/cli-colors
git commit --message 'Add CLI colors'
git branch -D feature/cli-colors
```

### squash-hard-switch-squash-cleanup-ui

**Difficulty:** Hard  
**Scenario:** squash-land-from-another-branch  
**Alternative category:** syntax alternatives

**Objective**

Switch to `develop`, bring `feature/toast-ui` in as one commit with the message `Add toast notifications`, then delete the local feature branch.

**Taught / authored example — 4 counted commands**

```sh
git switch develop
git merge --squash feature/toast-ui
git commit -m "Add toast notifications"
git branch -D feature/toast-ui
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout develop
git merge --squash feature/toast-ui
git commit -m "Add toast notifications"
git branch -D feature/toast-ui
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch develop
git merge --squash feature/toast-ui
git commit --message 'Add toast notifications'
git branch -D feature/toast-ui
```

### squash-hard-remote-publish-tidy-search

**Difficulty:** Hard  
**Scenario:** squash-a-remote-branch-publish-tidy  
**Alternative category:** syntax alternatives

**Objective**

Bring the latest `origin/feature/search` into `main` as one new commit with the message `Add search`, push `main` to `origin`, and delete your local `feature/search`.

**Taught / authored example — 5 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/search
git commit -m "Add search"
git push origin main
git branch -D feature/search
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --squash origin/feature/search
git commit --message 'Add search'
git push origin main
git branch -D feature/search
```

### squash-hard-remote-publish-tidy-docs

**Difficulty:** Hard  
**Scenario:** squash-a-remote-branch-publish-tidy  
**Alternative category:** syntax alternatives

**Objective**

Bring the latest `origin/docs/api` into `main` as one new commit with the message `Document the API`, push `main` to `origin`, and delete your local `docs/api`.

**Taught / authored example — 5 counted commands**

```sh
git fetch origin
git merge --squash origin/docs/api
git commit -m "Document the API"
git push origin main
git branch -D docs/api
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --squash origin/docs/api
git commit --message 'Document the API'
git push origin main
git branch -D docs/api
```

<a id="level-15"></a>
## Story: deleting-and-recovering-remote-branches

### v29e-auth

**Difficulty:** Easy  
**Scenario:** delete-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the merged `feature/auth` branch from `origin`. Keep the local branch.

**Taught / authored example — 1 counted command**

```sh
git push origin --delete feature/auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push origin -d feature/auth
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git push -d origin feature/auth
```

### v29e-orders

**Difficulty:** Easy  
**Scenario:** delete-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the merged `feature/orders` branch from `origin`. Keep the local branch.

**Taught / authored example — 1 counted command**

```sh
git push origin --delete feature/orders
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push origin -d feature/orders
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git push -d origin feature/orders
```

### v29e-parser

**Difficulty:** Easy  
**Scenario:** delete-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the merged `feature/parser` branch from `origin`. Keep the local branch.

**Taught / authored example — 1 counted command**

```sh
git push origin --delete feature/parser
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push origin -d feature/parser
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git push -d origin feature/parser
```

### rb-easy-cap-group

**Difficulty:** Easy  
**Scenario:** delete-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the merged `feature/group-auth` branch from `origin`. Keep the local branch.

**Taught / authored example — 1 counted command**

```sh
git push origin --delete feature/group-auth
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push origin -d feature/group-auth
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git push -d origin feature/group-auth
```

### rb-easy-corp-sprint

**Difficulty:** Easy  
**Scenario:** delete-a-remote-branch  
**Alternative category:** syntax alternatives

**Objective**

Delete the merged `feature/sprint12-compliance` branch from `origin`. Keep the local branch.

**Taught / authored example — 1 counted command**

```sh
git push origin --delete feature/sprint12-compliance
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git push origin -d feature/sprint12-compliance
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git push -d origin feature/sprint12-compliance
```

### rb-easy-delete-then-prune-docs

**Difficulty:** Easy  
**Scenario:** delete-then-prune  
**Alternative category:** syntax alternatives

**Objective**

Delete `docs/old-faq` from `origin`, then remove the stale `origin/feature/old-banner` record from your copy.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete docs/old-faq
git fetch --prune origin
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d docs/old-faq
git fetch --prune origin
```

### rb-easy-delete-then-prune-api

**Difficulty:** Easy  
**Scenario:** delete-then-prune  
**Alternative category:** syntax alternatives

**Objective**

Delete `feature/v1-api` from `origin`, then remove the stale `origin/spike/graphql` record from your copy.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete feature/v1-api
git fetch --prune origin
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d feature/v1-api
git fetch --prune origin
```

### v29h-auth

**Difficulty:** Medium  
**Scenario:** retire-a-branch-everywhere  
**Alternative category:** syntax alternatives

**Objective**

The `feature/auth` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete feature/auth
git branch -d feature/auth
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d feature/auth
git branch -d feature/auth
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git push -d origin feature/auth
git branch -d feature/auth
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/auth
git branch --delete feature/auth
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/auth
git branch -D feature/auth
```

### v29h-orders

**Difficulty:** Medium  
**Scenario:** retire-a-branch-everywhere  
**Alternative category:** syntax alternatives

**Objective**

The `feature/orders` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete feature/orders
git branch -d feature/orders
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d feature/orders
git branch -d feature/orders
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git push -d origin feature/orders
git branch -d feature/orders
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/orders
git branch --delete feature/orders
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/orders
git branch -D feature/orders
```

### rb-medium-land-and-retire-search

**Difficulty:** Medium  
**Scenario:** land-and-retire  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/search` into `main` with a merge commit, push `main` to `origin`, then delete `feature/search` on `origin`.

**Keep the local branch.**

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge --no-ff feature/search
git push origin main
git push origin --delete feature/search
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/search
git push
git push origin --delete feature/search
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/search
git push origin main
git push origin -d feature/search
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/search
git push origin main
git push -d origin feature/search
```

### rb-medium-land-and-retire-billing

**Difficulty:** Medium  
**Scenario:** land-and-retire  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/billing` into `main` with a merge commit, push `main` to `origin`, then delete `feature/billing` on `origin`.

**Keep the local branch.**

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge --no-ff feature/billing
git push origin main
git push origin --delete feature/billing
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/billing
git push
git push origin --delete feature/billing
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/billing
git push origin main
git push origin -d feature/billing
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git merge --no-ff feature/billing
git push origin main
git push -d origin feature/billing
```

### v29h-parser

**Difficulty:** Hard  
**Scenario:** retire-safely  
**Alternative category:** syntax alternatives

**Objective**

The `feature/parser` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete feature/parser
git branch -d feature/parser
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d feature/parser
git branch -d feature/parser
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git push -d origin feature/parser
git branch -d feature/parser
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/parser
git branch --delete feature/parser
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/parser
git branch -D feature/parser
```

### rb-hard-oss-full

**Difficulty:** Hard  
**Scenario:** retire-safely  
**Alternative category:** syntax alternatives

**Objective**

The `feature/oss-contribution` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Taught / authored example — 2 counted commands**

```sh
git push origin --delete feature/oss-contribution
git branch -d feature/oss-contribution
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git push origin -d feature/oss-contribution
git branch -d feature/oss-contribution
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git push -d origin feature/oss-contribution
git branch -d feature/oss-contribution
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/oss-contribution
git branch --delete feature/oss-contribution
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git push origin --delete feature/oss-contribution
git branch -D feature/oss-contribution
```

### rb-hard-capstone-release-notes

**Difficulty:** Hard  
**Scenario:** fetch-land-publish-retire-prune  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, merge `origin/feature/release-notes` into `main` with a merge commit, push `main` to `origin`, delete `feature/release-notes` on `origin`, and prune stale remote-tracking refs.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/release-notes
git push origin main
git push origin --delete feature/release-notes
git fetch --prune origin
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git fetch --prune origin
git merge --no-ff origin/feature/release-notes
git push origin main
git push origin --delete feature/release-notes
git fetch --prune origin
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/release-notes
git push
git push origin --delete feature/release-notes
git fetch --prune origin
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/release-notes
git push origin main
git push origin -d feature/release-notes
git fetch --prune origin
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/release-notes
git push origin main
git push -d origin feature/release-notes
git fetch --prune origin
```

### rb-hard-capstone-payments

**Difficulty:** Hard  
**Scenario:** fetch-land-publish-retire-prune  
**Alternative category:** syntax alternatives

**Objective**

Fetch from `origin`, merge `origin/feature/payments-v2` into `main` with a merge commit, push `main` to `origin`, delete `feature/payments-v2` on `origin`, and prune stale remote-tracking refs.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/payments-v2
git push origin main
git push origin --delete feature/payments-v2
git fetch --prune origin
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git fetch --prune origin
git merge --no-ff origin/feature/payments-v2
git push origin main
git push origin --delete feature/payments-v2
git fetch --prune origin
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/payments-v2
git push origin main
git push origin -d feature/payments-v2
git fetch --prune origin
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git fetch origin
git merge --no-ff origin/feature/payments-v2
git push origin main
git push -d origin feature/payments-v2
git fetch --prune origin
```

<a id="level-16"></a>
## Story: resolving-conflicts-manually

### manual-easy-auth-copy

**Difficulty:** Easy  
**Scenario:** resolve-one-conflicted-file  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/auth-timeout` into your current `main` branch. Resolve `src/auth.js` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/auth-timeout
git add src/auth.js
git commit --no-edit
```

After command 1: `write` file `src/auth.js` with this exact content:

```text
timeout=5000
retry=enabled
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/auth-timeout
git add -- src/auth.js
git commit --no-edit
```

After command 1: `write` file `src/auth.js` with this exact content:

```text
timeout=5000
retry=enabled
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/auth-timeout
git add .
git commit --no-edit
```

After command 1: `write` file `src/auth.js` with this exact content:

```text
timeout=5000
retry=enabled
```

### manual-easy-profile-copy

**Difficulty:** Easy  
**Scenario:** resolve-one-conflicted-file  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/profile-copy` into your current `main` branch. Resolve `src/profile.tsx` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/profile-copy
git add src/profile.tsx
git commit --no-edit
```

After command 1: `write` file `src/profile.tsx` with this exact content:

```text
title=Account profile
subtitle=Member profile
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/profile-copy
git add -- src/profile.tsx
git commit --no-edit
```

After command 1: `write` file `src/profile.tsx` with this exact content:

```text
title=Account profile
subtitle=Member profile
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/profile-copy
git add .
git commit --no-edit
```

After command 1: `write` file `src/profile.tsx` with this exact content:

```text
title=Account profile
subtitle=Member profile
```

### manual-easy-billing-copy

**Difficulty:** Easy  
**Scenario:** resolve-one-conflicted-file  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/regional-currency` into your current `main` branch. Resolve `src/billing.py` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/regional-currency
git add src/billing.py
git commit --no-edit
```

After command 1: `write` file `src/billing.py` with this exact content:

```text
currency='PHP'
supported=['PHP','EUR']
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/regional-currency
git add -- src/billing.py
git commit --no-edit
```

After command 1: `write` file `src/billing.py` with this exact content:

```text
currency='PHP'
supported=['PHP','EUR']
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/regional-currency
git add .
git commit --no-edit
```

After command 1: `write` file `src/billing.py` with this exact content:

```text
currency='PHP'
supported=['PHP','EUR']
```

### manual-easy-config-copy

**Difficulty:** Easy  
**Scenario:** resolve-another-file  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/debug-config` into your current `main` branch. Resolve `src/config.py` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/debug-config
git add src/config.py
git commit --no-edit
```

After command 1: `write` file `src/config.py` with this exact content:

```text
debug=False
log_level=INFO
verbose_errors=True
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/debug-config
git add -- src/config.py
git commit --no-edit
```

After command 1: `write` file `src/config.py` with this exact content:

```text
debug=False
log_level=INFO
verbose_errors=True
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/debug-config
git add .
git commit --no-edit
```

After command 1: `write` file `src/config.py` with this exact content:

```text
debug=False
log_level=INFO
verbose_errors=True
```

### manual-easy-navbar-copy

**Difficulty:** Easy  
**Scenario:** resolve-another-file  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/navbar-rebrand` into your current `main` branch. Resolve `src/components/Navbar.tsx` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/navbar-rebrand
git add src/components/Navbar.tsx
git commit --no-edit
```

After command 1: `write` file `src/components/Navbar.tsx` with this exact content:

```text
brand=MyApp
tagline=Beta
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/navbar-rebrand
git add -- src/components/Navbar.tsx
git commit --no-edit
```

After command 1: `write` file `src/components/Navbar.tsx` with this exact content:

```text
brand=MyApp
tagline=Beta
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/navbar-rebrand
git add .
git commit --no-edit
```

After command 1: `write` file `src/components/Navbar.tsx` with this exact content:

```text
brand=MyApp
tagline=Beta
```

### manual-medium-router

**Difficulty:** Medium  
**Scenario:** resolve-config-conflicts  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/routes` into your current `main` branch. Resolve `src/routes.ts` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/routes
git add src/routes.ts
git commit --no-edit
```

After command 1: `write` file `src/routes.ts` with this exact content:

```text
export const routes = ["/", "/support"];
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/routes
git add -- src/routes.ts
git commit --no-edit
```

After command 1: `write` file `src/routes.ts` with this exact content:

```text
export const routes = ["/", "/support"];
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/routes
git add .
git commit --no-edit
```

After command 1: `write` file `src/routes.ts` with this exact content:

```text
export const routes = ["/", "/support"];
```

### manual-medium-policy

**Difficulty:** Medium  
**Scenario:** resolve-config-conflicts  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/policy` into your current `main` branch. Resolve `src/policy.yml` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/policy
git add src/policy.yml
git commit --no-edit
```

After command 1: `write` file `src/policy.yml` with this exact content:

```text
access:
  default: deny
  allow_roles:
    - librarian
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/policy
git add -- src/policy.yml
git commit --no-edit
```

After command 1: `write` file `src/policy.yml` with this exact content:

```text
access:
  default: deny
  allow_roles:
    - librarian
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/policy
git add .
git commit --no-edit
```

After command 1: `write` file `src/policy.yml` with this exact content:

```text
access:
  default: deny
  allow_roles:
    - librarian
```

### manual-medium-gateway

**Difficulty:** Medium  
**Scenario:** resolve-config-conflicts  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/gateway` into your current `main` branch. Resolve `config/gateway.yml` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/gateway
git add config/gateway.yml
git commit --no-edit
```

After command 1: `write` file `config/gateway.yml` with this exact content:

```text
gateway:
  timeout_seconds: 30
  retry_count: 3
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/gateway
git add -- config/gateway.yml
git commit --no-edit
```

After command 1: `write` file `config/gateway.yml` with this exact content:

```text
gateway:
  timeout_seconds: 30
  retry_count: 3
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/gateway
git add .
git commit --no-edit
```

After command 1: `write` file `config/gateway.yml` with this exact content:

```text
gateway:
  timeout_seconds: 30
  retry_count: 3
```

### manual-medium-pull-conflict-readme

**Difficulty:** Medium  
**Scenario:** a-pull-that-conflicts  
**Alternative category:** multiple workflows

**Objective**

Pull `origin/main` into `main`, resolve `README.md` to the content below, complete the merge with its prepared message, and push `main` to `origin`.

**Taught / authored example — 4 counted commands**

```sh
git pull origin main
git add README.md
git commit --no-edit
git push origin main
```

After command 1: `write` file `README.md` with this exact content:

```text
Run the app with: npm run dev -- --port 3000
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git pull origin main
git add -- README.md
git commit --no-edit
git push origin main
```

After command 1: `write` file `README.md` with this exact content:

```text
Run the app with: npm run dev -- --port 3000
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git pull origin main
git add .
git commit --no-edit
git push origin main
```

After command 1: `write` file `README.md` with this exact content:

```text
Run the app with: npm run dev -- --port 3000
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git pull origin main
git add README.md
git commit --no-edit
git push
```

After command 1: `write` file `README.md` with this exact content:

```text
Run the app with: npm run dev -- --port 3000
```

### manual-medium-pull-conflict-config

**Difficulty:** Medium  
**Scenario:** a-pull-that-conflicts  
**Alternative category:** multiple workflows

**Objective**

Pull `origin/develop` into `develop`, resolve `config/app.yml` to the content below, complete the merge with its prepared message, and push `develop` to `origin`.

**Taught / authored example — 4 counted commands**

```sh
git pull origin develop
git add config/app.yml
git commit --no-edit
git push origin develop
```

After command 1: `write` file `config/app.yml` with this exact content:

```text
timeout: 45
retries: 3
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git pull origin develop
git add -- config/app.yml
git commit --no-edit
git push origin develop
```

After command 1: `write` file `config/app.yml` with this exact content:

```text
timeout: 45
retries: 3
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git pull origin develop
git add .
git commit --no-edit
git push origin develop
```

After command 1: `write` file `config/app.yml` with this exact content:

```text
timeout: 45
retries: 3
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git pull origin develop
git add config/app.yml
git commit --no-edit
git push
```

After command 1: `write` file `config/app.yml` with this exact content:

```text
timeout: 45
retries: 3
```

### manual-hard-pricing

**Difficulty:** Hard  
**Scenario:** resolve-with-less-guidance  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/pricing` into your current `main` branch so that `src/pricing.rb` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/pricing
git add src/pricing.rb
git commit --no-edit
```

After command 1: `write` file `src/pricing.rb` with this exact content:

```text
BASE_PRICE = 100
DISCOUNT_PERCENT = 10
def final_price
  BASE_PRICE * (100 - DISCOUNT_PERCENT) / 100.0
end
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/pricing
git add -- src/pricing.rb
git commit --no-edit
```

After command 1: `write` file `src/pricing.rb` with this exact content:

```text
BASE_PRICE = 100
DISCOUNT_PERCENT = 10
def final_price
  BASE_PRICE * (100 - DISCOUNT_PERCENT) / 100.0
end
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/pricing
git add .
git commit --no-edit
```

After command 1: `write` file `src/pricing.rb` with this exact content:

```text
BASE_PRICE = 100
DISCOUNT_PERCENT = 10
def final_price
  BASE_PRICE * (100 - DISCOUNT_PERCENT) / 100.0
end
```

### manual-hard-schema

**Difficulty:** Hard  
**Scenario:** resolve-with-less-guidance  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/schema` into your current `main` branch so that `schema/orders.sql` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/schema
git add schema/orders.sql
git commit --no-edit
```

After command 1: `write` file `schema/orders.sql` with this exact content:

```text
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
);
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/schema
git add -- schema/orders.sql
git commit --no-edit
```

After command 1: `write` file `schema/orders.sql` with this exact content:

```text
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
);
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/schema
git add .
git commit --no-edit
```

After command 1: `write` file `schema/orders.sql` with this exact content:

```text
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
);
```

### manual-hard-migration

**Difficulty:** Hard  
**Scenario:** resolve-with-less-guidance  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/migration` into your current `main` branch so that `db/migrations/001_users.sql` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required techniques:** merge

**Taught / authored example — 3 counted commands**

```sh
git merge feature/migration
git add db/migrations/001_users.sql
git commit --no-edit
```

After command 1: `write` file `db/migrations/001_users.sql` with this exact content:

```text
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL
);
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git merge feature/migration
git add -- db/migrations/001_users.sql
git commit --no-edit
```

After command 1: `write` file `db/migrations/001_users.sql` with this exact content:

```text
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL
);
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git merge feature/migration
git add .
git commit --no-edit
```

After command 1: `write` file `db/migrations/001_users.sql` with this exact content:

```text
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL
);
```

### manual-hard-abort-redo

**Difficulty:** Hard  
**Scenario:** abort-wrong-resolve-right  
**Alternative category:** multiple workflows

**Objective**

**Cancel the unwanted merge so `main` is exactly as it was before it started.** Then merge `feature/help-center` into `main` and resolve `src/routes.ts` to contain exactly the lines shown below, with no conflict markers. Complete the merge.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git merge --abort
git merge feature/help-center
git add src/routes.ts
git commit --no-edit
```

After command 2: `write` file `src/routes.ts` with this exact content:

```text
route('/support')
route('/help-center')
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git merge --abort
git merge feature/help-center
git add -- src/routes.ts
git commit --no-edit
```

After command 2: `write` file `src/routes.ts` with this exact content:

```text
route('/support')
route('/help-center')
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git merge --abort
git merge feature/help-center
git add .
git commit --no-edit
```

After command 2: `write` file `src/routes.ts` with this exact content:

```text
route('/support')
route('/help-center')
```

### manual-hard-abort-redo-payments

**Difficulty:** Hard  
**Scenario:** abort-wrong-resolve-right  
**Alternative category:** multiple workflows

**Objective**

Cancel the current merge, merge `feature/payments-v2` instead, resolve `src/payments.py` to the content below, and complete the merge with its prepared message.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git merge --abort
git merge feature/payments-v2
git add src/payments.py
git commit --no-edit
```

After command 2: `write` file `src/payments.py` with this exact content:

```text
FEE = 0.025
CAP = 500
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git merge --abort
git merge feature/payments-v2
git add -- src/payments.py
git commit --no-edit
```

After command 2: `write` file `src/payments.py` with this exact content:

```text
FEE = 0.025
CAP = 500
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git merge --abort
git merge feature/payments-v2
git add .
git commit --no-edit
```

After command 2: `write` file `src/payments.py` with this exact content:

```text
FEE = 0.025
CAP = 500
```

<a id="level-17"></a>
## Story: using-a-merge-tool

### mergetool-hard-choose-tool

**Difficulty:** Medium  
**Scenario:** set-up-the-team-tool  
**Alternative category:** syntax alternatives

**Objective**

Merge `feature/pricing-v2` into your current `main` branch. Use the simulator’s merge tool to resolve `src/prices.py` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message. **The team’s tool is `meld`, and it is not configured yet.**

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git config merge.tool meld
git merge feature/pricing-v2
git mergetool
git commit --no-edit
```

After command 3: `write` file `src/prices.py` with this exact content:

```text
PRICE = 100
DISCOUNT = 10
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git config --global merge.tool meld
git merge feature/pricing-v2
git mergetool
git commit --no-edit
```

After command 3: `write` file `src/prices.py` with this exact content:

```text
PRICE = 100
DISCOUNT = 10
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git config merge.tool meld
git merge feature/pricing-v2
git mergetool --tool=meld
git commit --no-edit
```

After command 3: `write` file `src/prices.py` with this exact content:

```text
PRICE = 100
DISCOUNT = 10
```

### mergetool-medium-configure-tool-billing

**Difficulty:** Medium  
**Scenario:** set-up-the-team-tool  
**Alternative category:** syntax alternatives

**Objective**

Configure `meld` as this repository's merge tool, merge `feature/billing-copy`, resolve `src/billing_copy.txt` in the merge tool to the content below, and complete the merge with its prepared message.

**Required techniques:** merge

**Taught / authored example — 4 counted commands**

```sh
git config merge.tool meld
git merge feature/billing-copy
git mergetool
git commit --no-edit
```

After command 3: `write` file `src/billing_copy.txt` with this exact content:

```text
Your monthly invoice is ready.
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git config merge.tool meld
git merge feature/billing-copy
git mergetool --tool=meld
git commit --no-edit
```

After command 3: `write` file `src/billing_copy.txt` with this exact content:

```text
Your monthly invoice is ready.
```

<a id="level-18"></a>
## Story: cherry-picking-commits

### cherry-medium-no-commit

**Difficulty:** Easy  
**Scenario:** pick-without-committing  
**Alternative category:** syntax alternatives

**Objective**

Apply the changes from `c1` onto `release-review` and leave them staged for review.

**Do not create a commit.**

**Taught / authored example — 1 counted command**

```sh
git cherry-pick --no-commit c1
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git cherry-pick -n c1
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git cherry-pick c1 --no-commit
```

### cherry-medium-staged-review

**Difficulty:** Easy  
**Scenario:** pick-without-committing  
**Alternative category:** syntax alternatives

**Objective**

Apply the changes from `c1` onto `release-staged` and leave them staged for review.

**Do not create a commit.**

**Taught / authored example — 1 counted command**

```sh
git cherry-pick --no-commit c1
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git cherry-pick -n c1
```

**Accepted alternative 2 (syntax) — 1 counted command**

```sh
git cherry-pick c1 --no-commit
```

### cherry-medium-two-fixes-one-commit-login

**Difficulty:** Easy  
**Scenario:** two-fixes-one-reviewed-commit  
**Alternative category:** syntax alternatives

**Objective**

Apply `c2` and `c3` to `release-1.2` without committing either, then commit them together with the message `Backport login fixes`.

**Taught / authored example — 3 counted commands**

```sh
git cherry-pick --no-commit c2
git cherry-pick --no-commit c3
git commit -m "Backport login fixes"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git cherry-pick -n c2
git cherry-pick --no-commit c3
git commit -m "Backport login fixes"
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git cherry-pick --no-commit c2
git cherry-pick -n c3
git commit -m "Backport login fixes"
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git cherry-pick --no-commit c2
git cherry-pick --no-commit c3
git commit --message 'Backport login fixes'
```

### cherry-medium-two-fixes-one-commit-tax

**Difficulty:** Easy  
**Scenario:** two-fixes-one-reviewed-commit  
**Alternative category:** syntax alternatives

**Objective**

Apply `c1` and `c4` to `release-3.1` without committing either, then commit them together with the message `Backport tax fixes`.

**Taught / authored example — 3 counted commands**

```sh
git cherry-pick --no-commit c1
git cherry-pick --no-commit c4
git commit -m "Backport tax fixes"
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git cherry-pick --no-commit c1
git cherry-pick --no-commit c4
git commit --message 'Backport tax fixes'
```

### cherry-hard-export-conflict

**Difficulty:** Medium  
**Scenario:** resolve-and-continue  
**Alternative category:** multiple workflows

**Objective**

Apply only the changes of `c1` to `release-2.0` as a new commit. `src/export.py` will conflict: resolve it so it contains exactly the lines shown below, with no conflict markers, and finish the cherry-pick.

**Required techniques:** cherry-pick

**Taught / authored example — 3 counted commands**

```sh
git cherry-pick c1
git add src/export.py
git cherry-pick --continue
```

After command 1: `write` file `src/export.py` with this exact content:

```text
def export(rows):
    return [r for r in rows if r is not None]
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git cherry-pick -x c1
git add src/export.py
git cherry-pick --continue
```

After command 1: `write` file `src/export.py` with this exact content:

```text
def export(rows):
    return [r for r in rows if r is not None]
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git cherry-pick c1
git add -- src/export.py
git cherry-pick --continue
```

After command 1: `write` file `src/export.py` with this exact content:

```text
def export(rows):
    return [r for r in rows if r is not None]
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git cherry-pick c1
git add .
git cherry-pick --continue
```

After command 1: `write` file `src/export.py` with this exact content:

```text
def export(rows):
    return [r for r in rows if r is not None]
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git cherry-pick c1
git add -A
git cherry-pick --continue
```

After command 1: `write` file `src/export.py` with this exact content:

```text
def export(rows):
    return [r for r in rows if r is not None]
```

### cherry-medium-conflict-continue-auth

**Difficulty:** Medium  
**Scenario:** resolve-and-continue  
**Alternative category:** multiple workflows

**Objective**

Cherry-pick `c1` onto `release-1.9`, resolve `src/auth.py` to the content below, and finish the cherry-pick.

**Required techniques:** cherry-pick

**Taught / authored example — 3 counted commands**

```sh
git cherry-pick c1
git add src/auth.py
git cherry-pick --continue
```

After command 1: `write` file `src/auth.py` with this exact content:

```text
MAX_FAILURES = 5
LOG_FAILURES = True
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git cherry-pick c1
git add -- src/auth.py
git cherry-pick --continue
```

After command 1: `write` file `src/auth.py` with this exact content:

```text
MAX_FAILURES = 5
LOG_FAILURES = True
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git cherry-pick c1
git add .
git cherry-pick --continue
```

After command 1: `write` file `src/auth.py` with this exact content:

```text
MAX_FAILURES = 5
LOG_FAILURES = True
```

### cherry-medium-abort-stopped-pick

**Difficulty:** Medium  
**Scenario:** cancel-a-stopped-pick  
**Alternative category:** multiple workflows

**Objective**

Cancel the cherry-pick so `release-review-2` is __exactly__ as it was before.

**Taught / authored example — 1 counted command**

```sh
git cherry-pick --abort
```

**Accepted alternative 1 (workflow) — 1 counted command**

```sh
git reset --hard
```

### cherry-hard-review-backports-auth

**Difficulty:** Hard  
**Scenario:** review-two-backports-before-committing  
**Alternative category:** syntax alternatives

**Objective**

On `release-2.2`, apply the two auth fixes from `main` without committing either, then commit them together with the message `Backport auth fixes`. Finish on `release-2.2` and leave `main` unchanged.

**Taught / authored example — 4 counted commands**

```sh
git log --oneline main
git switch release-2.2
git cherry-pick --no-commit c2
git cherry-pick --no-commit c4
git commit -m "Backport auth fixes"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git log --oneline main
git checkout release-2.2
git cherry-pick --no-commit c2
git cherry-pick --no-commit c4
git commit -m "Backport auth fixes"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git log --oneline main
git switch release-2.2
git cherry-pick --no-commit c2
git cherry-pick --no-commit c4
git commit --message 'Backport auth fixes'
```

### cherry-hard-review-backports-export

**Difficulty:** Hard  
**Scenario:** review-two-backports-before-committing  
**Alternative category:** syntax alternatives

**Objective**

On `release-3.0`, apply the two export fixes from `main` without committing either, then commit them together with the message `Backport export fixes`. Finish on `release-3.0` and leave `main` unchanged.

**Taught / authored example — 4 counted commands**

```sh
git log --oneline main
git switch release-3.0
git cherry-pick --no-commit c1
git cherry-pick --no-commit c3
git commit -m "Backport export fixes"
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git log --oneline main
git checkout release-3.0
git cherry-pick --no-commit c1
git cherry-pick --no-commit c3
git commit -m "Backport export fixes"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git log --oneline main
git switch release-3.0
git cherry-pick --no-commit c1
git cherry-pick --no-commit c3
git commit --message 'Backport export fixes'
```

### cherry-hard-two-releases

**Difficulty:** Hard  
**Scenario:** backport-to-two-releases  
**Alternative category:** syntax alternatives

**Objective**

Apply only the changes of `c1` to `release-1.2` and to `release-1.1`, as a new commit on each. Finish on `release-1.1`.

**Taught / authored example — 4 counted commands**

```sh
git switch release-1.2
git cherry-pick c1
git switch release-1.1
git cherry-pick c1
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout release-1.2
git cherry-pick c1
git switch release-1.1
git cherry-pick c1
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch release-1.2
git cherry-pick c1
git checkout release-1.1
git cherry-pick c1
```

### cherry-hard-two-releases-security

**Difficulty:** Hard  
**Scenario:** backport-to-two-releases  
**Alternative category:** syntax alternatives

**Objective**

Apply `c3` to `release-2.1` and to `release-2.0`, each as a new commit. Finish on `release-2.0` and leave `main` unchanged.

**Taught / authored example — 4 counted commands**

```sh
git switch release-2.1
git cherry-pick c3
git switch release-2.0
git cherry-pick c3
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout release-2.1
git cherry-pick c3
git switch release-2.0
git cherry-pick c3
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch release-2.1
git cherry-pick c3
git checkout release-2.0
git cherry-pick c3
```

### cherry-hard-backport-capstone-export

**Difficulty:** Hard  
**Scenario:** abort-the-wrong-pick-backport-the-right-one  
**Alternative category:** multiple workflows

**Objective**

Cancel the current cherry-pick. Apply `c4` so the new commit records its source, resolve `src/export.py` to the content below, and finish the cherry-pick.

**Required techniques:** cherry-pick

**Taught / authored example — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add src/export.py
git cherry-pick --continue
```

After command 2: `write` file `src/export.py` with this exact content:

```text
return to_csv(rows, header=True, quoting=QUOTE_ALL)
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add -- src/export.py
git cherry-pick --continue
```

After command 2: `write` file `src/export.py` with this exact content:

```text
return to_csv(rows, header=True, quoting=QUOTE_ALL)
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add .
git cherry-pick --continue
```

After command 2: `write` file `src/export.py` with this exact content:

```text
return to_csv(rows, header=True, quoting=QUOTE_ALL)
```

### cherry-hard-backport-capstone-login

**Difficulty:** Hard  
**Scenario:** abort-the-wrong-pick-backport-the-right-one  
**Alternative category:** multiple workflows

**Objective**

Cancel the current cherry-pick. Apply `c4` so the new commit records its source, resolve `src/login.py` to the content below, and finish the cherry-pick.

**Required techniques:** cherry-pick

**Taught / authored example — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add src/login.py
git cherry-pick --continue
```

After command 2: `write` file `src/login.py` with this exact content:

```text
email = form.email.strip().lower()
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add -- src/login.py
git cherry-pick --continue
```

After command 2: `write` file `src/login.py` with this exact content:

```text
email = form.email.strip().lower()
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git cherry-pick --abort
git cherry-pick -x c4
git add .
git cherry-pick --continue
```

After command 2: `write` file `src/login.py` with this exact content:

```text
email = form.email.strip().lower()
```

<a id="level-19"></a>
## Story: recovering-from-hard-resets

### e1

**Difficulty:** Easy  
**Scenario:** recover-the-lost-tip  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e1`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/e1 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/e1 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/e1 c3
git switch recovery/e1
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/e1 c3
```

### e2

**Difficulty:** Easy  
**Scenario:** recover-the-lost-tip  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e2`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/e2 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/e2 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/e2 c3
git switch recovery/e2
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/e2 c3
```

### e3

**Difficulty:** Easy  
**Scenario:** recover-the-lost-tip  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e3`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/e3 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/e3 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/e3 c3
git switch recovery/e3
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/e3 c3
```

### e4

**Difficulty:** Easy  
**Scenario:** recover-again  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e4`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/e4 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/e4 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/e4 c3
git switch recovery/e4
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/e4 c3
```

### e5

**Difficulty:** Easy  
**Scenario:** recover-again  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e5`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/e5 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/e5 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/e5 c3
git switch recovery/e5
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/e5 c3
```

### m1

**Difficulty:** Medium  
**Scenario:** deeper-in-the-reflog  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m1`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/m1 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/m1 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/m1 c3
git switch recovery/m1
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/m1 c3
```

### m2

**Difficulty:** Medium  
**Scenario:** deeper-in-the-reflog  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m2`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/m2 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/m2 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/m2 c3
git switch recovery/m2
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/m2 c3
```

### m3

**Difficulty:** Medium  
**Scenario:** deeper-in-the-reflog  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m3`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/m3 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/m3 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/m3 c3
git switch recovery/m3
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/m3 c3
```

### m4

**Difficulty:** Medium  
**Scenario:** deeper-in-the-reflog  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m4`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/m4 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/m4 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/m4 c3
git switch recovery/m4
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/m4 c3
```

### m5

**Difficulty:** Medium  
**Scenario:** deeper-in-the-reflog  
**Alternative category:** multiple workflows

**Objective**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m5`, and switch to it. Leave `main` where the reset left it.

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c3
git switch -c recovery/m5 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git checkout -b recovery/m5 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c3
git branch recovery/m5 c3
git switch recovery/m5
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c3
git switch --create recovery/m5 c3
```

### reflog-medium-recover-and-publish-search

**Difficulty:** Medium  
**Scenario:** recover-and-share  
**Alternative category:** multiple workflows

**Objective**

Find the lost tip in the reflog, recover it on a new branch named `recovery/search-fix`, switch to it, and publish it to `origin` with its upstream set. Leave `main` where it is.

**Taught / authored example — 2 counted commands**

```sh
git reflog
git switch -c recovery/search-fix c4
git push -u origin recovery/search-fix
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git reflog show main
git switch -c recovery/search-fix c4
git push -u origin recovery/search-fix
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git reflog
git checkout -b recovery/search-fix c4
git push -u origin recovery/search-fix
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git reflog
git branch recovery/search-fix c4
git switch recovery/search-fix
git push -u origin recovery/search-fix
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git reflog
git switch --create recovery/search-fix c4
git push -u origin recovery/search-fix
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git reflog
git switch -c recovery/search-fix c4
git push --set-upstream origin recovery/search-fix
```

### reflog-medium-recover-and-publish-billing

**Difficulty:** Medium  
**Scenario:** recover-and-share  
**Alternative category:** multiple workflows

**Objective**

Find the lost tip in the reflog, recover it on a new branch named `recovery/billing`, switch to it, and publish it to `origin` with its upstream set. Leave `main` where it is.

**Taught / authored example — 2 counted commands**

```sh
git reflog
git switch -c recovery/billing c5
git push -u origin recovery/billing
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git reflog show main
git switch -c recovery/billing c5
git push -u origin recovery/billing
```

**Accepted alternative 2 (syntax) — 2 counted commands**

```sh
git reflog
git checkout -b recovery/billing c5
git push -u origin recovery/billing
```

**Accepted alternative 3 (workflow) — 3 counted commands**

```sh
git reflog
git branch recovery/billing c5
git switch recovery/billing
git push -u origin recovery/billing
```

**Accepted alternative 4 (syntax) — 2 counted commands**

```sh
git reflog
git switch --create recovery/billing c5
git push -u origin recovery/billing
```

**Accepted alternative 5 (syntax) — 2 counted commands**

```sh
git reflog
git switch -c recovery/billing c5
git push --set-upstream origin recovery/billing
```

### h1

**Difficulty:** Hard  
**Scenario:** pick-the-right-candidate  
**Alternative category:** multiple workflows

**Objective**

Find the lost work among the old positions in the reflog. Recover the commit containing the borrower search fix on a new branch named `recovery/h1`, then switch to that branch. Reject the candidate containing an abandoned search experiment.

**Leave `main` at its reset position and keep the working tree clean.**

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch -c recovery/h1 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git checkout -b recovery/h1 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c4
git show c3
git branch recovery/h1 c3
git switch recovery/h1
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch --create recovery/h1 c3
```

### h2

**Difficulty:** Hard  
**Scenario:** pick-the-right-candidate  
**Alternative category:** multiple workflows

**Objective**

Find the lost work among the old positions in the reflog. Recover the commit containing the completed borrowing report on a new branch named `recovery/h2`, then switch to that branch. Reject the candidate containing an earlier draft of the report.

**Leave `main` at its reset position and keep the working tree clean.**

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch -c recovery/h2 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git checkout -b recovery/h2 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c4
git show c3
git branch recovery/h2 c3
git switch recovery/h2
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch --create recovery/h2 c3
```

### h3

**Difficulty:** Hard  
**Scenario:** pick-the-right-candidate  
**Alternative category:** multiple workflows

**Objective**

Find the lost work among the old positions in the reflog. Recover the commit containing the validation fix and its passing test on a new branch named `recovery/h3`, then switch to that branch. Reject the candidate containing a cleanup that does not include the validation fix.

**Leave `main` at its reset position and keep the working tree clean.**

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch -c recovery/h3 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git checkout -b recovery/h3 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c4
git show c3
git branch recovery/h3 c3
git switch recovery/h3
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch --create recovery/h3 c3
```

### h4

**Difficulty:** Hard  
**Scenario:** pick-the-right-candidate  
**Alternative category:** multiple workflows

**Objective**

Find the lost work among the old positions in the reflog. Recover the commit containing the working export before the failed merge on a new branch named `recovery/h4`, then switch to that branch. Reject the candidate containing the failed merge result.

**Leave `main` at its reset position and keep the working tree clean.**

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch -c recovery/h4 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git checkout -b recovery/h4 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c4
git show c3
git branch recovery/h4 c3
git switch recovery/h4
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch --create recovery/h4 c3
```

### h5

**Difficulty:** Hard  
**Scenario:** pick-the-right-candidate  
**Alternative category:** multiple workflows

**Objective**

Find the lost work among the old positions in the reflog. Recover the commit containing the final login timeout fix on a new branch named `recovery/h5`, then switch to that branch. Reject the candidate containing a temporary debugging change.

**Leave `main` at its reset position and keep the working tree clean.**

**Taught / authored example — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch -c recovery/h5 c3
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git checkout -b recovery/h5 c3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git reflog
git show c4
git show c3
git branch recovery/h5 c3
git switch recovery/h5
```

**Accepted alternative 3 (syntax) — 1 counted command**

```sh
git reflog
git show c4
git show c3
git switch --create recovery/h5 c3
```

<a id="level-20"></a>
## Story: reversing-pushed-commits-safely

### revert-easy-pull-then-revert-docs

**Difficulty:** Easy  
**Scenario:** sync-then-revert  
**Alternative category:** syntax alternatives

**Objective**

Bring `main` up to date with `origin`, undo `c3` with a new commit, and push `main` to `origin`.

**Taught / authored example — 3 counted commands**

```sh
git pull origin main
git revert c3
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git pull
git revert c3
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git pull origin main
git revert --no-edit c3
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git pull origin main
git revert c3
git push origin main
```

### revert-easy-pull-then-revert-api

**Difficulty:** Easy  
**Scenario:** sync-then-revert  
**Alternative category:** syntax alternatives

**Objective**

Bring `main` up to date with `origin`, undo `c4` with a new commit, and push `main` to `origin`.

**Taught / authored example — 3 counted commands**

```sh
git pull origin main
git revert c4
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git pull
git revert c4
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git pull origin main
git revert --no-edit c4
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git pull origin main
git revert c4
git push origin main
```

### revert-medium-release-branch-pricing

**Difficulty:** Medium  
**Scenario:** revert-on-the-release-branch  
**Alternative category:** syntax alternatives

**Objective**

Switch to `release/2.1`, undo `c4` with a new commit, and push `release/2.1` to `origin`.

**Leave `main` unchanged.**

**Taught / authored example — 3 counted commands**

```sh
git switch release/2.1
git revert c4
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git checkout release/2.1
git revert c4
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git switch release/2.1
git revert --no-edit c4
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git switch release/2.1
git revert c4
git push origin release/2.1
```

### revert-medium-release-branch-auth

**Difficulty:** Medium  
**Scenario:** revert-on-the-release-branch  
**Alternative category:** syntax alternatives

**Objective**

Switch to `release/1.8`, undo `c3` with a new commit, and push `release/1.8` to `origin`.

**Leave `main` unchanged.**

**Taught / authored example — 3 counted commands**

```sh
git switch release/1.8
git revert c3
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git checkout release/1.8
git revert c3
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git switch release/1.8
git revert --no-edit c3
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git switch release/1.8
git revert c3
git push origin release/1.8
```

### revert-hard-amend-local-revert-pushed-shop

**Difficulty:** Hard  
**Scenario:** rewrite-only-unpublished  
**Alternative category:** syntax alternatives

**Objective**

Change `c4`'s message to `Add order export`, undo `c2` with a new commit, and push `main` to `origin` once.

**Taught / authored example — 3 counted commands**

```sh
git commit --amend -m "Add order export"
git revert c2
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git commit --amend --message 'Add order export'
git revert c2
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add order export"
git revert --no-edit c2
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add order export"
git revert c2
git push origin main
```

### revert-hard-amend-local-revert-pushed-blog

**Difficulty:** Hard  
**Scenario:** rewrite-only-unpublished  
**Alternative category:** syntax alternatives

**Objective**

Change `c4`'s message to `Add RSS feed`, undo `c3` with a new commit, and push `main` to `origin` once.

**Taught / authored example — 3 counted commands**

```sh
git commit --amend -m "Add RSS feed"
git revert c3
git push
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git commit --amend --message 'Add RSS feed'
git revert c3
git push
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add RSS feed"
git revert --no-edit c3
git push
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git commit --amend -m "Add RSS feed"
git revert c3
git push origin main
```

<a id="level-21"></a>
## Story: completing-rebase-recovery-sequences

### be6

**Difficulty:** Easy  
**Scenario:** replay-onto-main  
**Alternative category:** syntax alternatives

**Objective**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Required techniques:** rebase

**Taught / authored example — 1 counted command**

```sh
git rebase main
git log --oneline --graph --all
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git rebase main feature/recovery
git log --oneline --graph --all
```

### be7

**Difficulty:** Easy  
**Scenario:** replay-onto-main  
**Alternative category:** syntax alternatives

**Objective**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Required techniques:** rebase

**Taught / authored example — 1 counted command**

```sh
git rebase main
git log --oneline --graph --all
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git rebase main feature/search-filters
git log --oneline --graph --all
```

### be8

**Difficulty:** Easy  
**Scenario:** replay-onto-main  
**Alternative category:** syntax alternatives

**Objective**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Required techniques:** rebase

**Taught / authored example — 1 counted command**

```sh
git rebase main
git log --oneline --graph --all
```

**Accepted alternative 1 (syntax) — 1 counted command**

```sh
git rebase main feature/cli-flags
git log --oneline --graph --all
```

### rebase-hard-continue

**Difficulty:** Easy  
**Scenario:** resolve-and-continue-a-rebase  
**Alternative category:** multiple workflows

**Objective**

Resolve `src/limiter.py` so it contains exactly the lines shown below, with no conflict markers, and finish the rebase. The finished branch must sit on top of `main` with all its commits.

**Taught / authored example — 2 counted commands**

```sh
git add src/limiter.py
git rebase --continue
```

Before running commands: `write` file `src/limiter.py` with this exact content:

```text
LIMIT_NAME = 'api'
RETRY_COUNT = 3
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/limiter.py
git rebase --continue
```

Before running commands: `write` file `src/limiter.py` with this exact content:

```text
LIMIT_NAME = 'api'
RETRY_COUNT = 3
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git rebase --continue
```

Before running commands: `write` file `src/limiter.py` with this exact content:

```text
LIMIT_NAME = 'api'
RETRY_COUNT = 3
```

**Accepted alternative 3 (syntax) — 2 counted commands**

```sh
git add -A
git rebase --continue
```

Before running commands: `write` file `src/limiter.py` with this exact content:

```text
LIMIT_NAME = 'api'
RETRY_COUNT = 3
```

### rebase-easy-continue-config

**Difficulty:** Easy  
**Scenario:** resolve-and-continue-a-rebase  
**Alternative category:** multiple workflows

**Objective**

Resolve `config/app.yml` to the content below, stage it, and continue the rebase until it finishes.

**Required techniques:** rebase:continue

**Taught / authored example — 2 counted commands**

```sh
git add config/app.yml
git rebase --continue
```

Before running commands: `write` file `config/app.yml` with this exact content:

```text
loader: toml
watch: true
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- config/app.yml
git rebase --continue
```

Before running commands: `write` file `config/app.yml` with this exact content:

```text
loader: toml
watch: true
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git rebase --continue
```

Before running commands: `write` file `config/app.yml` with this exact content:

```text
loader: toml
watch: true
```

### rebase-easy-continue-styles

**Difficulty:** Easy  
**Scenario:** resolve-another-stopped-rebase  
**Alternative category:** multiple workflows

**Objective**

Resolve `styles/theme.css` to the content below, stage it, and continue the rebase until it finishes.

**Required techniques:** rebase:continue

**Taught / authored example — 2 counted commands**

```sh
git add styles/theme.css
git rebase --continue
```

Before running commands: `write` file `styles/theme.css` with this exact content:

```text
--accent: navy;
--surface: #111;
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- styles/theme.css
git rebase --continue
```

Before running commands: `write` file `styles/theme.css` with this exact content:

```text
--accent: navy;
--surface: #111;
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git rebase --continue
```

Before running commands: `write` file `styles/theme.css` with this exact content:

```text
--accent: navy;
--surface: #111;
```

### rebase-easy-continue-routes

**Difficulty:** Easy  
**Scenario:** resolve-another-stopped-rebase  
**Alternative category:** multiple workflows

**Objective**

Resolve `src/routes.py` to the content below, stage it, and continue the rebase until it finishes.

**Required techniques:** rebase:continue

**Taught / authored example — 2 counted commands**

```sh
git add src/routes.py
git rebase --continue
```

Before running commands: `write` file `src/routes.py` with this exact content:

```text
ROUTES = ['/', '/login']
HEALTH = '/health'
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git add -- src/routes.py
git rebase --continue
```

Before running commands: `write` file `src/routes.py` with this exact content:

```text
ROUTES = ['/', '/login']
HEALTH = '/health'
```

**Accepted alternative 2 (workflow) — 2 counted commands**

```sh
git add .
git rebase --continue
```

Before running commands: `write` file `src/routes.py` with this exact content:

```text
ROUTES = ['/', '/login']
HEALTH = '/health'
```

### rebase-hard-abort-then-onto-reports

**Difficulty:** Hard  
**Scenario:** abort-then-move-only-your-commits  
**Alternative category:** syntax alternatives

**Objective**

Cancel the current rebase. Then move __only__ `feature/reports`' own commits onto `main`, leaving the spike's commits behind.

**Required techniques:** rebase

**Taught / authored example — 2 counted commands**

```sh
git rebase --abort
git rebase --onto main spike/charts feature/reports
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git rebase --abort
git rebase --onto main spike/charts
```

### rebase-hard-abort-then-onto-ui

**Difficulty:** Hard  
**Scenario:** abort-then-move-only-your-commits  
**Alternative category:** syntax alternatives

**Objective**

Cancel the current rebase. Then move __only__ `feature/table-ui`'s own commits onto `main`, leaving the spike's commits behind.

**Required techniques:** rebase

**Taught / authored example — 2 counted commands**

```sh
git rebase --abort
git rebase --onto main spike/new-grid feature/table-ui
```

**Accepted alternative 1 (syntax) — 2 counted commands**

```sh
git rebase --abort
git rebase --onto main spike/new-grid
```

### rebase-hard-continue-then-lease-search

**Difficulty:** Hard  
**Scenario:** continue-then-publish-safely  
**Alternative category:** multiple workflows

**Objective**

Resolve `src/search.py` to the content below, finish the rebase, and update `origin`'s `feature/search` **without overwriting work you have not seen**.

**Taught / authored example — 3 counted commands**

```sh
git add src/search.py
git rebase --continue
git push --force-with-lease origin feature/search
```

Before running commands: `write` file `src/search.py` with this exact content:

```text
RESULTS = 20
FUZZY = True
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add -- src/search.py
git rebase --continue
git push --force-with-lease origin feature/search
```

Before running commands: `write` file `src/search.py` with this exact content:

```text
RESULTS = 20
FUZZY = True
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git add .
git rebase --continue
git push --force-with-lease origin feature/search
```

Before running commands: `write` file `src/search.py` with this exact content:

```text
RESULTS = 20
FUZZY = True
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git add src/search.py
git rebase --continue
git push --force-with-lease
```

Before running commands: `write` file `src/search.py` with this exact content:

```text
RESULTS = 20
FUZZY = True
```

### rebase-hard-continue-then-lease-billing

**Difficulty:** Hard  
**Scenario:** continue-then-publish-safely  
**Alternative category:** multiple workflows

**Objective**

Resolve `src/billing.py` to the content below, finish the rebase, and update `origin`'s `feature/billing` safely.

**Taught / authored example — 3 counted commands**

```sh
git add src/billing.py
git rebase --continue
git push --force-with-lease origin feature/billing
```

Before running commands: `write` file `src/billing.py` with this exact content:

```text
CURRENCY = 'USD'
ROUNDING = 'half-up'
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git add -- src/billing.py
git rebase --continue
git push --force-with-lease origin feature/billing
```

Before running commands: `write` file `src/billing.py` with this exact content:

```text
CURRENCY = 'USD'
ROUNDING = 'half-up'
```

**Accepted alternative 2 (workflow) — 3 counted commands**

```sh
git add .
git rebase --continue
git push --force-with-lease origin feature/billing
```

Before running commands: `write` file `src/billing.py` with this exact content:

```text
CURRENCY = 'USD'
ROUNDING = 'half-up'
```

### rebase-hard-reset-rebase-lease-cli

**Difficulty:** Hard  
**Scenario:** undo-a-bad-rebase-and-republish  
**Alternative category:** syntax alternatives

**Objective**

Find the pre-rebase tip in the reflog, reset the branch to it, rebase it onto `main` again, and update `origin`'s `feature/cli-flags` **without overwriting work you have not seen**.

**Required techniques:** rebase

**Taught / authored example — 3 counted commands**

```sh
git reflog
git reset --hard c6
git rebase main
git push --force-with-lease origin feature/cli-flags
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reflog
git reset --hard origin/feature/cli-flags
git rebase main
git push --force-with-lease origin feature/cli-flags
```

### rebase-hard-reset-rebase-lease-api

**Difficulty:** Hard  
**Scenario:** undo-a-bad-rebase-and-republish  
**Alternative category:** syntax alternatives

**Objective**

Find the pre-rebase tip in the reflog, reset the branch to it, rebase it onto `main` again, and update `origin`'s `feature/rate-limits` safely.

**Required techniques:** rebase

**Taught / authored example — 3 counted commands**

```sh
git reflog
git reset --hard c5
git rebase main
git push --force-with-lease origin feature/rate-limits
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reflog
git reset --hard origin/feature/rate-limits
git rebase main
git push --force-with-lease origin feature/rate-limits
```

<a id="level-22"></a>
## Challenge: module-1-challenge-gate

### gate1-easy-two-commit-start-field-log

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Make `field-log` a Git repository on `main`. Commit `notes.md` and `readings.csv` with the message `Start field log`, then commit `README.md` on top of it with the message `Add field log guide`.

**Leave `scratch.txt` untracked.**

**Taught / authored example — 5 counted commands**

```sh
git init -b main
git add notes.md readings.csv
git commit -m "Start field log"
git add README.md
git commit -m "Add field log guide"
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git init --initial-branch main
git add notes.md readings.csv
git commit -m "Start field log"
git add README.md
git commit -m "Add field log guide"
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git init
git add notes.md readings.csv
git commit -m "Start field log"
git add README.md
git commit -m "Add field log guide"
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git init -b main
git add notes.md readings.csv
git commit --message 'Start field log'
git add README.md
git commit -m "Add field log guide"
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git init -b main
git add notes.md readings.csv
git commit -m "Start field log"
git add -- README.md
git commit -m "Add field log guide"
```

**Accepted alternative 5 (syntax) — 5 counted commands**

```sh
git init -b main
git add notes.md readings.csv
git commit -m "Start field log"
git add README.md
git commit --message 'Add field log guide'
```

### gate1-easy-two-commit-start-quiz

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Make `quiz-app` a Git repository on `main`. Commit `index.html` and `quiz.js` with the message `Start quiz app`, then commit `README.md` on top of it with the message `Add quiz setup notes`.

**Leave `todo.txt` untracked.**

**Taught / authored example — 5 counted commands**

```sh
git init -b main
git add index.html quiz.js
git commit -m "Start quiz app"
git add README.md
git commit -m "Add quiz setup notes"
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git init --initial-branch main
git add index.html quiz.js
git commit -m "Start quiz app"
git add README.md
git commit -m "Add quiz setup notes"
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git init
git add index.html quiz.js
git commit -m "Start quiz app"
git add README.md
git commit -m "Add quiz setup notes"
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git init -b main
git add index.html quiz.js
git commit --message 'Start quiz app'
git add README.md
git commit -m "Add quiz setup notes"
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git init -b main
git add index.html quiz.js
git commit -m "Start quiz app"
git add -- README.md
git commit -m "Add quiz setup notes"
```

**Accepted alternative 5 (syntax) — 5 counted commands**

```sh
git init -b main
git add index.html quiz.js
git commit -m "Start quiz app"
git add README.md
git commit --message 'Add quiz setup notes'
```

### gate1-medium-complete-last-commit-search

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Unstage `notes.txt` (keep it), then complete the latest commit with `templates/search.html` and the ranking hunk from `src/search.py`, keeping its message `Add search page`.

**Leave the debug hunk uncommitted** and finish on `main`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged notes.txt
git add templates/search.html
git add -p src/search.py
git commit --amend -m "Add search page"
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- notes.txt
git add templates/search.html
git add -p src/search.py
git commit --amend -m "Add search page"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged notes.txt
git add -- templates/search.html
git add -p src/search.py
git commit --amend -m "Add search page"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged notes.txt
git add templates/search.html
git add --patch src/search.py
git commit --amend -m "Add search page"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore --staged notes.txt
git add templates/search.html
git add --patch
git commit --amend -m "Add search page"
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git restore --staged notes.txt
git add templates/search.html
git add -p src/search.py
git commit --amend --message 'Add search page'
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git restore --staged notes.txt
git add templates/search.html
git add -p src/search.py
git commit --amend --no-edit
```

### gate1-medium-complete-last-commit-upload

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Unstage `scratch.md` (keep it), then complete the latest commit with `docs/upload.md` and the size-limit hunk from `src/upload.py`, keeping its message `Add file upload`.

**Leave the debug hunk uncommitted** and finish on `main`.

**Taught / authored example — 4 counted commands**

```sh
git restore --staged scratch.md
git add docs/upload.md
git add -p src/upload.py
git commit --amend -m "Add file upload"
```

**Accepted alternative 1 (workflow) — 4 counted commands**

```sh
git reset HEAD -- scratch.md
git add docs/upload.md
git add -p src/upload.py
git commit --amend -m "Add file upload"
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git restore --staged scratch.md
git add -- docs/upload.md
git add -p src/upload.py
git commit --amend -m "Add file upload"
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git restore --staged scratch.md
git add docs/upload.md
git add --patch src/upload.py
git commit --amend -m "Add file upload"
```

**Accepted alternative 4 (syntax) — 4 counted commands**

```sh
git restore --staged scratch.md
git add docs/upload.md
git add --patch
git commit --amend -m "Add file upload"
```

**Accepted alternative 5 (syntax) — 4 counted commands**

```sh
git restore --staged scratch.md
git add docs/upload.md
git add -p src/upload.py
git commit --amend --message 'Add file upload'
```

**Accepted alternative 6 (syntax) — 4 counted commands**

```sh
git restore --staged scratch.md
git add docs/upload.md
git add -p src/upload.py
git commit --amend --no-edit
```

### gate1-hard-reword-then-commit-export

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Rename the latest commit to `Add export` __without adding anything to it__, discard the edits to `cache/report.json`, then commit the header fix from `src/export.py` together with `docs/export.md` as `Fix export headers`. Keep `tmp/run.log` in the folder, uncommitted, leave the debug hunk uncommitted and finish on `main`.

**Taught / authored example — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add -p src/export.py
git add docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 1 (workflow) — 6 counted commands**

```sh
git reset HEAD -- tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add -p src/export.py
git add docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 2 (syntax) — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend --message 'Add export'
git restore cache/report.json
git add -p src/export.py
git add docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 3 (syntax) — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add --patch src/export.py
git add docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 4 (syntax) — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add --patch
git add docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 5 (syntax) — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add -p src/export.py
git add -- docs/export.md
git commit -m "Fix export headers"
```

**Accepted alternative 6 (syntax) — 6 counted commands**

```sh
git restore --staged tmp/run.log
git commit --amend -m "Add export"
git restore cache/report.json
git add -p src/export.py
git add docs/export.md
git commit --message 'Fix export headers'
```

### gate1-hard-reword-then-commit-billing

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Rename the latest commit to `Add billing` __without adding anything to it__, discard the edits to `cache/invoices.json`, then commit the tax fix from `src/billing.py` together with `docs/billing.md` as `Fix billing tax`. Keep `logs/billing.log` in the folder, uncommitted, leave the debug hunk uncommitted and finish on `main`.

**Taught / authored example — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add -p src/billing.py
git add docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 1 (workflow) — 6 counted commands**

```sh
git reset HEAD -- logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add -p src/billing.py
git add docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 2 (syntax) — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend --message 'Add billing'
git restore cache/invoices.json
git add -p src/billing.py
git add docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 3 (syntax) — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add --patch src/billing.py
git add docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 4 (syntax) — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add --patch
git add docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 5 (syntax) — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add -p src/billing.py
git add -- docs/billing.md
git commit -m "Fix billing tax"
```

**Accepted alternative 6 (syntax) — 6 counted commands**

```sh
git restore --staged logs/billing.log
git commit --amend -m "Add billing"
git restore cache/invoices.json
git add -p src/billing.py
git add docs/billing.md
git commit --message 'Fix billing tax'
```

<a id="level-23"></a>
## Challenge: module-2-challenge-gate

### gate2-easy-fresh-branch-search

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Go back to `main`, bring it up to date with `origin`, then create and switch to `feature/search-filters` from it.

**Taught / authored example — 3 counted commands**

```sh
git switch main
git pull origin main
git switch -c feature/search-filters
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git checkout main
git pull origin main
git switch -c feature/search-filters
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git switch main
git pull
git switch -c feature/search-filters
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git switch main
git pull origin main
git checkout -b feature/search-filters
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git switch main
git pull origin main
git branch feature/search-filters
git switch feature/search-filters
```

**Accepted alternative 5 (syntax) — 3 counted commands**

```sh
git switch main
git pull origin main
git switch --create feature/search-filters
```

### gate2-easy-fresh-branch-invoices

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Go back to `main`, bring it up to date with `origin`, then create and switch to `feature/invoice-pdf` from it.

**Taught / authored example — 3 counted commands**

```sh
git switch main
git pull origin main
git switch -c feature/invoice-pdf
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git checkout main
git pull origin main
git switch -c feature/invoice-pdf
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git switch main
git pull
git switch -c feature/invoice-pdf
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git switch main
git pull origin main
git checkout -b feature/invoice-pdf
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git switch main
git pull origin main
git branch feature/invoice-pdf
git switch feature/invoice-pdf
```

**Accepted alternative 5 (syntax) — 3 counted commands**

```sh
git switch main
git pull origin main
git switch --create feature/invoice-pdf
```

### gate2-medium-stash-and-sync-reports

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Set your `src/reports.py` edits aside, update your local `main` from `origin`, then return to `feature/reports` and bring the edits back.

**Leave no stash entry behind.**

**Taught / authored example — 5 counted commands**

```sh
git stash
git switch main
git pull origin main
git switch feature/reports
git stash pop
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git stash push
git switch main
git pull origin main
git switch feature/reports
git stash pop
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git stash
git checkout main
git pull origin main
git switch feature/reports
git stash pop
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git stash
git switch main
git pull
git switch feature/reports
git stash pop
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git stash
git switch main
git pull origin main
git checkout feature/reports
git stash pop
```

### gate2-medium-stash-and-sync-profile

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Set your `src/profile.py` edits aside, update your local `main` from `origin`, then return to `feature/profile` and bring the edits back.

**Leave no stash entry behind.**

**Taught / authored example — 5 counted commands**

```sh
git stash
git switch main
git pull origin main
git switch feature/profile
git stash pop
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git stash push
git switch main
git pull origin main
git switch feature/profile
git stash pop
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git stash
git checkout main
git pull origin main
git switch feature/profile
git stash pop
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git stash
git switch main
git pull
git switch feature/profile
git stash pop
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git stash
git switch main
git pull origin main
git checkout feature/profile
git stash pop
```

### gate2-hard-land-and-retire-filters

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Update `main` from `origin`, land `feature/filters` on it as one commit with the message `Add search filters`, publish `main`, then delete `feature/filters` locally and on `origin`. Finish on `main`.

**Taught / authored example — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/filters
git commit -m "Add search filters"
git push origin main
git branch -D feature/filters
git push origin --delete feature/filters
```

**Accepted alternative 1 (syntax) — 7 counted commands**

```sh
git checkout main
git pull origin main
git merge --squash feature/filters
git commit -m "Add search filters"
git push origin main
git branch -D feature/filters
git push origin --delete feature/filters
```

**Accepted alternative 2 (syntax) — 7 counted commands**

```sh
git switch main
git pull
git merge --squash feature/filters
git commit -m "Add search filters"
git push origin main
git branch -D feature/filters
git push origin --delete feature/filters
```

**Accepted alternative 3 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/filters
git commit --message 'Add search filters'
git push origin main
git branch -D feature/filters
git push origin --delete feature/filters
```

**Accepted alternative 4 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/filters
git commit -m "Add search filters"
git push
git branch -D feature/filters
git push origin --delete feature/filters
```

**Accepted alternative 5 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/filters
git commit -m "Add search filters"
git push origin main
git branch -D feature/filters
git push origin -d feature/filters
```

### gate2-hard-land-and-retire-export

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Update `main` from `origin`, land `feature/export` on it as one commit with the message `Add CSV export`, publish `main`, then delete `feature/export` locally and on `origin`. Finish on `main`.

**Taught / authored example — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/export
git commit -m "Add CSV export"
git push origin main
git branch -D feature/export
git push origin --delete feature/export
```

**Accepted alternative 1 (syntax) — 7 counted commands**

```sh
git checkout main
git pull origin main
git merge --squash feature/export
git commit -m "Add CSV export"
git push origin main
git branch -D feature/export
git push origin --delete feature/export
```

**Accepted alternative 2 (syntax) — 7 counted commands**

```sh
git switch main
git pull
git merge --squash feature/export
git commit -m "Add CSV export"
git push origin main
git branch -D feature/export
git push origin --delete feature/export
```

**Accepted alternative 3 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/export
git commit --message 'Add CSV export'
git push origin main
git branch -D feature/export
git push origin --delete feature/export
```

**Accepted alternative 4 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/export
git commit -m "Add CSV export"
git push
git branch -D feature/export
git push origin --delete feature/export
```

**Accepted alternative 5 (syntax) — 7 counted commands**

```sh
git switch main
git pull origin main
git merge --squash feature/export
git commit -m "Add CSV export"
git push origin main
git branch -D feature/export
git push origin -d feature/export
```

<a id="level-24"></a>
## Challenge: module-3-challenge-gate

### gate3-easy-merge-then-backport-banner

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/banner` into `main`, resolve `src/banner.html` to the content below, and complete the merge with its prepared message. Then copy __only__ “Fix checkout total” onto `release/1.4`. Finish on `release/1.4`.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git merge feature/banner
git add src/banner.html
git commit --no-edit
git switch release/1.4
git cherry-pick c3
```

After command 1: `write` file `src/banner.html` with this exact content:

```text
<p>Welcome back, team!</p>
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git merge feature/banner
git add -- src/banner.html
git commit --no-edit
git switch release/1.4
git cherry-pick c3
```

After command 1: `write` file `src/banner.html` with this exact content:

```text
<p>Welcome back, team!</p>
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git merge feature/banner
git add .
git commit --no-edit
git switch release/1.4
git cherry-pick c3
```

After command 1: `write` file `src/banner.html` with this exact content:

```text
<p>Welcome back, team!</p>
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git merge feature/banner
git add src/banner.html
git commit --no-edit
git checkout release/1.4
git cherry-pick c3
```

After command 1: `write` file `src/banner.html` with this exact content:

```text
<p>Welcome back, team!</p>
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git merge feature/banner
git add src/banner.html
git commit --no-edit
git switch release/1.4
git cherry-pick -x c3
```

After command 1: `write` file `src/banner.html` with this exact content:

```text
<p>Welcome back, team!</p>
```

### gate3-easy-merge-then-backport-footer

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Merge `feature/footer` into `main`, resolve `src/footer.html` to the content below, and complete the merge with its prepared message. Then copy __only__ “Fix tax rounding” onto `release/2.0`. Finish on `release/2.0`.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git merge feature/footer
git add src/footer.html
git commit --no-edit
git switch release/2.0
git cherry-pick c3
```

After command 1: `write` file `src/footer.html` with this exact content:

```text
<footer>Contact support</footer>
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git merge feature/footer
git add -- src/footer.html
git commit --no-edit
git switch release/2.0
git cherry-pick c3
```

After command 1: `write` file `src/footer.html` with this exact content:

```text
<footer>Contact support</footer>
```

**Accepted alternative 2 (workflow) — 5 counted commands**

```sh
git merge feature/footer
git add .
git commit --no-edit
git switch release/2.0
git cherry-pick c3
```

After command 1: `write` file `src/footer.html` with this exact content:

```text
<footer>Contact support</footer>
```

**Accepted alternative 3 (syntax) — 5 counted commands**

```sh
git merge feature/footer
git add src/footer.html
git commit --no-edit
git checkout release/2.0
git cherry-pick c3
```

After command 1: `write` file `src/footer.html` with this exact content:

```text
<footer>Contact support</footer>
```

**Accepted alternative 4 (syntax) — 5 counted commands**

```sh
git merge feature/footer
git add src/footer.html
git commit --no-edit
git switch release/2.0
git cherry-pick -x c3
```

After command 1: `write` file `src/footer.html` with this exact content:

```text
<footer>Contact support</footer>
```

### gate3-medium-backport-tax

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

On `release/2.1`, apply `main`'s latest commit while recording its origin, resolve `src/tax.py` to the content below, and finish the cherry-pick. **`main` must stay as it is.**

**Required techniques:** cherry-pick

**Taught / authored example — 4 counted commands**

```sh
git switch release/2.1
git cherry-pick -x c3
git add src/tax.py
git cherry-pick --continue
```

After command 2: `write` file `src/tax.py` with this exact content:

```text
ROUND_PER_LINE = True
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout release/2.1
git cherry-pick -x c3
git add src/tax.py
git cherry-pick --continue
```

After command 2: `write` file `src/tax.py` with this exact content:

```text
ROUND_PER_LINE = True
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch release/2.1
git cherry-pick -x main
git add src/tax.py
git cherry-pick --continue
```

After command 2: `write` file `src/tax.py` with this exact content:

```text
ROUND_PER_LINE = True
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch release/2.1
git cherry-pick -x c3
git add -- src/tax.py
git cherry-pick --continue
```

After command 2: `write` file `src/tax.py` with this exact content:

```text
ROUND_PER_LINE = True
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git switch release/2.1
git cherry-pick -x c3
git add .
git cherry-pick --continue
```

After command 2: `write` file `src/tax.py` with this exact content:

```text
ROUND_PER_LINE = True
```

### gate3-medium-backport-locale

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

On `release/3.0`, apply `main`'s latest commit while recording its origin, resolve `src/locale.py` to the content below, and finish the cherry-pick. **`main` must stay as it is.**

**Required techniques:** cherry-pick

**Taught / authored example — 4 counted commands**

```sh
git switch release/3.0
git cherry-pick -x c3
git add src/locale.py
git cherry-pick --continue
```

After command 2: `write` file `src/locale.py` with this exact content:

```text
DATE_FORMAT = 'MM/DD/YYYY'
```

**Accepted alternative 1 (syntax) — 4 counted commands**

```sh
git checkout release/3.0
git cherry-pick -x c3
git add src/locale.py
git cherry-pick --continue
```

After command 2: `write` file `src/locale.py` with this exact content:

```text
DATE_FORMAT = 'MM/DD/YYYY'
```

**Accepted alternative 2 (syntax) — 4 counted commands**

```sh
git switch release/3.0
git cherry-pick -x main
git add src/locale.py
git cherry-pick --continue
```

After command 2: `write` file `src/locale.py` with this exact content:

```text
DATE_FORMAT = 'MM/DD/YYYY'
```

**Accepted alternative 3 (syntax) — 4 counted commands**

```sh
git switch release/3.0
git cherry-pick -x c3
git add -- src/locale.py
git cherry-pick --continue
```

After command 2: `write` file `src/locale.py` with this exact content:

```text
DATE_FORMAT = 'MM/DD/YYYY'
```

**Accepted alternative 4 (workflow) — 4 counted commands**

```sh
git switch release/3.0
git cherry-pick -x c3
git add .
git cherry-pick --continue
```

After command 2: `write` file `src/locale.py` with this exact content:

```text
DATE_FORMAT = 'MM/DD/YYYY'
```

### gate3-hard-abort-then-tool-merge-pricing

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Abandon the stopped merge, set `meld` as the merge tool, merge `feature/pricing-v2`, resolve `src/prices.py` in the merge tool to the content below, and complete the merge with its prepared message. Finish on `main`.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git merge --abort
git config merge.tool meld
git merge feature/pricing-v2
git mergetool
git commit --no-edit
```

After command 4: `write` file `src/prices.py` with this exact content:

```text
PRICE_TIERS = ['basic', 'pro']
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git merge --abort
git config --global merge.tool meld
git merge feature/pricing-v2
git mergetool
git commit --no-edit
```

After command 4: `write` file `src/prices.py` with this exact content:

```text
PRICE_TIERS = ['basic', 'pro']
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git merge --abort
git config merge.tool meld
git merge feature/pricing-v2
git mergetool --tool=meld
git commit --no-edit
```

After command 4: `write` file `src/prices.py` with this exact content:

```text
PRICE_TIERS = ['basic', 'pro']
```

### gate3-hard-abort-then-tool-merge-copy

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Abandon the stopped merge, set `meld` as the merge tool, merge `feature/checkout-copy`, resolve `src/checkout.js` in the merge tool to the content below, and complete the merge with its prepared message. Finish on `main`.

**Required techniques:** merge

**Taught / authored example — 5 counted commands**

```sh
git merge --abort
git config merge.tool meld
git merge feature/checkout-copy
git mergetool
git commit --no-edit
```

After command 4: `write` file `src/checkout.js` with this exact content:

```text
const label = 'Place order'
```

**Accepted alternative 1 (syntax) — 5 counted commands**

```sh
git merge --abort
git config --global merge.tool meld
git merge feature/checkout-copy
git mergetool
git commit --no-edit
```

After command 4: `write` file `src/checkout.js` with this exact content:

```text
const label = 'Place order'
```

**Accepted alternative 2 (syntax) — 5 counted commands**

```sh
git merge --abort
git config merge.tool meld
git merge feature/checkout-copy
git mergetool --tool=meld
git commit --no-edit
```

After command 4: `write` file `src/checkout.js` with this exact content:

```text
const label = 'Place order'
```

<a id="level-25"></a>
## Challenge: module-4-challenge-gate

### gate4-easy-recover-replay-publish-search

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Create `recovery/search` at your lost “Fix borrower search” commit, replay the branch onto `main`, and publish it to `origin` for review.

**Leave `main` where it is.**

**Taught / authored example — 3 counted commands**

```sh
git reflog
git switch -c recovery/search c2
git rebase main
git push -u origin recovery/search
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reflog
git checkout -b recovery/search c2
git rebase main
git push -u origin recovery/search
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git reflog
git branch recovery/search c2
git switch recovery/search
git rebase main
git push -u origin recovery/search
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git reflog
git switch --create recovery/search c2
git rebase main
git push -u origin recovery/search
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/search c2
git rebase main recovery/search
git push -u origin recovery/search
```

**Accepted alternative 5 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/search c2
git rebase main
git push --set-upstream origin recovery/search
```

**Accepted alternative 6 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/search c2
git rebase main
git push origin recovery/search
```

### gate4-easy-recover-replay-publish-receipts

**Difficulty:** Easy  
**Scenario:** Challenge trial  
**Alternative category:** multiple workflows

**Objective**

Create `recovery/receipts` at your lost “Fix receipt totals” commit, replay the branch onto `main`, and publish it to `origin` for review.

**Leave `main` where it is.**

**Taught / authored example — 3 counted commands**

```sh
git reflog
git switch -c recovery/receipts c2
git rebase main
git push -u origin recovery/receipts
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reflog
git checkout -b recovery/receipts c2
git rebase main
git push -u origin recovery/receipts
```

**Accepted alternative 2 (workflow) — 4 counted commands**

```sh
git reflog
git branch recovery/receipts c2
git switch recovery/receipts
git rebase main
git push -u origin recovery/receipts
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git reflog
git switch --create recovery/receipts c2
git rebase main
git push -u origin recovery/receipts
```

**Accepted alternative 4 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/receipts c2
git rebase main recovery/receipts
git push -u origin recovery/receipts
```

**Accepted alternative 5 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/receipts c2
git rebase main
git push --set-upstream origin recovery/receipts
```

**Accepted alternative 6 (syntax) — 3 counted commands**

```sh
git reflog
git switch -c recovery/receipts c2
git rebase main
git push origin recovery/receipts
```

### gate4-medium-drop-local-revert-published-banner

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Remove the local experiment from `main`, reverse the published banner commit with a new commit, and publish `main`. Finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git reset --hard c2
git revert c2
git push origin main
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reset --hard 'HEAD~1'
git revert c2
git push origin main
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git reset --hard c2
git revert --no-edit c2
git push origin main
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git reset --hard c2
git revert c2
git push
```

### gate4-medium-drop-local-revert-published-alerts

**Difficulty:** Medium  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Remove the local experiment from `main`, reverse the published alert commit with a new commit, and publish `main`. Finish on `main`.

**Taught / authored example — 3 counted commands**

```sh
git reset --hard c2
git revert c2
git push origin main
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git reset --hard 'HEAD~1'
git revert c2
git push origin main
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git reset --hard c2
git revert --no-edit c2
git push origin main
```

**Accepted alternative 3 (syntax) — 3 counted commands**

```sh
git reset --hard c2
git revert c2
git push
```

### gate4-hard-move-branch-onto-main-receipts

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Abandon the stopped rebase, move __only__ the commits made on `feature/receipts` after `release/1.0` onto `main`, and update `origin`'s copy of the branch safely. Finish on `feature/receipts`.

**Required techniques:** rebase

**Taught / authored example — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0 feature/receipts
git push --force-with-lease origin feature/receipts
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0
git push --force-with-lease origin feature/receipts
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0 feature/receipts
git push --force-with-lease
```

### gate4-hard-move-branch-onto-main-coupons

**Difficulty:** Hard  
**Scenario:** Challenge trial  
**Alternative category:** syntax alternatives

**Objective**

Abandon the stopped rebase, move __only__ the commits made on `feature/coupons` after `release/1.0` onto `main`, and update `origin`'s copy of the branch safely. Finish on `feature/coupons`.

**Required techniques:** rebase

**Taught / authored example — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0 feature/coupons
git push --force-with-lease origin feature/coupons
```

**Accepted alternative 1 (syntax) — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0
git push --force-with-lease origin feature/coupons
```

**Accepted alternative 2 (syntax) — 3 counted commands**

```sh
git rebase --abort
git rebase --onto main release/1.0 feature/coupons
git push --force-with-lease
```


# Module 1 — Answer Key

**Status: Internal reference only — not shown to students**  
**Last updated: 2026-05-29**

Each entry shows the scenario brief context, then the accepted solution command(s).
Diagnostic commands (`git status`, `git log`, `git diff`, etc.) are never counted and may appear at any point.

---

## Lesson 1 — Initializing a Local Repository

### Easy

---

**init-easy-current-empty**

> Your team just created a project folder but never initialized it as a Git repository. Initialize the current directory so the project can be version-controlled.

```
git init
```

---

**init-easy-trunk-branch**

> Your team uses 'trunk' as the main branch name by convention. Initialize the current directory as a Git repository with 'trunk' as the initial branch.

```
git init --initial-branch=trunk
```

---

**init-easy-invoice**

> A client hired you to build a simple invoice tracker. You need to start the project from scratch with Git version control. Create and initialize a new Git repository named invoice-tracker.

```
git init invoice-tracker
```

---

### Medium

---

**init-med-oss**

> You want to start contributing to an open-source project. Your mentor told you to first create a local scaffold directory called oss-contrib where you'll mirror your fork setup. Create and initialize the repo.

```
git init oss-contrib
```

---

**init-medium-docs-site**

> Your team needs a dedicated Git repository for the project documentation site. Initialize a new repo named docs-site in your current workspace.

```
git init docs-site
```

---

**init-medium-trunk-api-playground**

> You're setting up a sandbox repo for API experiments. The team uses 'trunk' as the default branch. Initialize a new named directory api-playground with trunk as the initial branch.

```
git init -b trunk api-playground
```

---

**init-medium-quiet-research-log**

> You're initializing a research notes repository called research-log. The CI script expects quiet output so nothing is printed to the console. Initialize it with quiet mode enabled.

```
git init --quiet --initial-branch=main research-log
```

---

### Hard

---

**init-hard-ci**

> You've been asked to create a versioned pipeline configuration store. The ops team refers to it as ci-configs. No step-by-step instructions were given — figure out what needs to be done and do it.

```
git init ci-configs
```

---

**init-hard-research-log**

> You're working in a parent workspace with multiple subdirectories. Only the research-log subfolder should become a Git repository — the parent and sibling folders must not be affected. Initialize only that subdirectory, quietly.

```
git init -q -b main research-log
```

---

**init-hard-ui-kit**

> You're in a design parent workspace. Only the ui-kit subfolder should be version-controlled — sibling folders like brand-assets and experiments must be left alone. Initialize ui-kit quietly with 'trunk' as the branch name.

```
git init --quiet --initial-branch=trunk ui-kit
```

---

**init-hard-safe-rerun**

> The release-notes directory is already a Git repository with one commit. A teammate ran a script that re-runs git init as a safety check. You need to safely reinitialize without losing the existing history. Run it quietly.

```
git init --quiet
```

---

## Lesson 2 — Cloning a Remote Repository

### Easy

---

**clone-easy-docs-portal**

> Your team's documentation portal is hosted remotely. Clone it so you can start contributing to the docs locally.

```
git clone https://example.test/training/docs-portal.git
```

---

**clone-easy-api-lab**

> You're onboarding at a startup. The backend API is hosted remotely. Your team's convention is to store repos in a folder named api-workshop. Clone it into that folder.

```
git clone https://example.test/training/api-lab.git api-workshop
```

---

**clone-easy-profile-starter**

> The profile site repo has a starter branch with template files ready to use. Clone it and check out the starter branch directly instead of main.

```
git clone -b starter https://example.test/training/profile-site.git
```

---

**clone-easy-oss-ssh**

> You've set up SSH keys and want to clone the OSS project you're contributing to. Clone it using the SSH URL.

```
git clone git@github.com:open-dev/oss-toolkit.git
```

---

**clone-easy-corp**

> Your company hosts Git internally. Clone the internal audit logs repository into a local folder named audit-logs-local.

```
git clone https://git.corp.example/it/audit-logs.git audit-logs-local
```

---

### Medium

---

**clone-med-feature**

> The backend team is mid-sprint on a feature/auth branch. You need to clone the repo and start from that branch directly rather than switching after cloning.

```
git clone -b feature/auth https://github.com/acme-startup/backend-api.git
```

---

**clone-medium-analytics-ssh**

> You've configured SSH access to the analytics lab repository. Clone it into a custom local folder named analytics-worktree using the SSH URL.

```
git clone git@example.test:training/analytics-lab.git analytics-worktree
```

---

**clone-medium-cli-starter-folder**

> A CLI tool repo has a starter branch prepared for onboarding contributors. Clone it into a folder called cli-starter-lab, checking out the starter branch immediately.

```
git clone --branch starter https://example.test/tools/cli-tool.git cli-starter-lab
```

---

**clone-medium-css-kit-shallow**

> Your CI pipeline needs a lightweight clone of the CSS kit repository for a one-time build. Disk space is limited — use a shallow clone of depth 1 to keep it fast.

```
git clone --depth 1 https://example.test/frontend/css-kit.git
```

---

### Hard

---

**clone-hard-ssh-shallow**

> You want a minimal clone of the OSS toolkit repository with only the latest commit using SSH, stored in a folder named oss-review. Combine shallow cloning with a custom destination.

```
git clone --depth 1 git@github.com:open-dev/oss-toolkit.git oss-review
```

---

**clone-hard-mobile-ui-shallow-branch**

> You need a lightweight copy of the mobile UI starter branch for a quick review. Clone only the tip of the starter branch into a folder named mobile-ui-lab — no full history needed.

```
git clone --depth 1 -b starter https://example.test/frontend/mobile-ui.git mobile-ui-lab
```

---

**clone-hard-lab-notebook-depth-branch**

> You need to review specific lab notebook entries on the review branch, but don't need the full commit history. Clone only the tip of the review branch into a folder named notebook-review.

```
git clone --depth 1 --branch review https://example.test/docs/lab-notebook.git notebook-review
```

---

**clone-hard-research-log-ssh**

> You've configured SSH access and need a full clone of the research log repository. Clone it via SSH into a local folder named research-log-lab for offline analysis.

```
git clone git@example.test:docs/research-log.git research-log-lab
```

---

## Lesson 3 — Staging and Committing

### Easy

---

**commit-easy-initial**

> You've just initialized the library-system repo. You have three files ready: README.md, main.py, and requirements.txt. Your group lead says 'do the initial commit.'

```
git add .
git commit -m "Initial commit"
```

---

**commit-easy-auth-dir**

> You added a new src/auth/ directory containing login.py and logout.py. Both are new files. Stage the entire directory and commit it as one focused snapshot.

```
git add src/auth/
git commit -m "Add auth module"
```

---

**commit-easy-form-validation**

> You updated the form validation logic in src/form.js. It's the only file changed and it's ready to commit.

```
git add src/form.js
git commit -m "Update form validation"
```

---

**commit-easy-readme-setup**

> You revised the README.md to make the setup instructions clearer. Stage it and commit with the required message.

```
git add README.md
git commit --message "Clarify setup steps"
```

---

**commit-easy-navbar-spacing**

> You tweaked the navbar spacing in styles/navbar.css to fix a visual alignment issue. Stage and commit just that one file.

```
git add -A
git commit -m "Adjust navbar spacing"
```

---

### Medium

---

**commit-med-docker**

> You updated Dockerfile and .env.example as part of a container setup. Stage both files and commit them together as one focused snapshot.

```
git add Dockerfile .env.example
git commit -m "Add Docker configuration"
```

---

**commit-medium-profile-card**

> You redesigned the profile card component. Both the JavaScript logic and the CSS stylesheet are updated and ready to commit together.

```
git add --all
git commit -m "Update profile card layout"
```

---

**commit-medium-search-results**

> You refined the search results view — the JavaScript handler and the HTML template both changed. Commit both files together with the required message.

```
git add src/search.js templates/search.html
git commit --message "Refine search results view"
```

---

**commit-medium-export-flow**

> You updated the export module and rewrote the matching documentation to reflect the new behavior. Commit both the code and the docs as one snapshot.

```
git add src/export.py docs/export.md
git commit -m "Document export flow update"
```

---

### Hard

---

**commit-hard-selective**

> You've been working on two things: a bug fix in api/handler.py and experimental work in api/experimental.py. Only the bug fix is ready. Stage handler.py and leave the experimental file out.

```
git add api/handler.py
git commit -m "Fix request handler null check"
```

---

**commit-hard-parser**

> You're preparing a PR for a new parser feature. The files ready to go are src/parser.py and tests/test_parser.py. A debug.log and scratch.py are also in the tree — keep them out of the commit.

```
git add src/parser.py tests/test_parser.py
git commit -m "Add parser module with unit tests"
```

---

**commit-hard-profile-distractor**

> You updated the profile card behavior in src/profile-card.js. You also have a notes/profile-ideas.md scratch file in the working tree — that's not ready and should stay out of the commit.

```
git add src/profile-card.js
git commit -m "Update profile card behavior"
```

---

**commit-hard-export-distractor**

> You fixed the export validation logic in src/export.py. A scratch/export-test-output.txt file from your testing is also present — leave it uncommitted.

```
git add src/export.py
git commit -m "Fix export validation"
```

---

**commit-hard-search-two-targets-one-distractor**

> You refined the search ranking display — both src/search.js and templates/search.html are updated and ready. A notes/search-ranking.md scratch file is present but must stay out of this commit.

```
git add src/search.js templates/search.html
git commit -m "Refine search ranking display"
```

---

## Lesson 5 — Partial Staging with git add -p

*During `git add -p`: respond `y` to stage a hunk, `n` to skip it.*

### Easy

---

**partial-easy-billing**

> You modified billing.py. The file has two changed sections: a rounding fix at the top and some experimental print statements at the bottom. Your client is waiting on the fix only — stage just that hunk.

```
git add -p src/billing.py   (y for billing-fix-hunk, n for billing-experimental-hunk)
git commit -m "Fix billing calculation rounding error"
```

---

**partial-easy-routes**

> src/routes.py has two changed sections: updated route handlers (ready to commit) and a commented-out experimental auth middleware section (skip this for now).

```
git add -p src/routes.py   (y for routes-handler-hunk, n for routes-experimental-hunk)
git commit -m "Update API route handlers"
```

---

**partial-easy-auth-validation**

> src/auth.py has two hunks: a validation fix that's ready and a larger refactor that's still in progress. Stage only the validation fix.

```
git add -p src/auth.py   (y for auth-validation-hunk, n for auth-refactor-hunk)
git commit -m "Isolate auth validation"
```

---

**partial-easy-search-ranking**

> src/search.py has two hunks: a ranking algorithm fix (ready) and some cleanup refactoring (not ready). Commit only the ranking fix.

```
git add -p src/search.py   (y for search-ranking-hunk, n for search-cleanup-hunk)
git commit -m "Isolate search ranking"
```

---

**partial-easy-export-format**

> src/export.py has two changed sections: a formatting fix (stage this) and some added logging statements (leave these out for now).

```
git add -p src/export.py   (y for export-format-hunk, n for export-logging-hunk)
git commit -m "Isolate export formatting"
```

---

### Medium

---

**partial-med-three-hunk**

> src/parser.py has three hunks: a bug fix (stage), a refactor (skip — not ready), and an experimental section (skip).

```
git add -p src/parser.py   (y for parser-bugfix-hunk, n for parser-refactor-hunk, n for parser-experimental-hunk)
git commit -m "Fix parser bug and refactor token handling"
```

---

**partial-medium-profile-validation**

> src/profile.py has three changed sections: a validation fix (stage), a copy update (skip), and a cleanup block (skip). A notes/profile-todo.md file is also present — leave it out.

```
git add -p src/profile.py   (y for profile-validation-hunk, n for others)
git commit -m "Commit profile validation only"
```

---

**partial-medium-payment-rounding**

> src/payment.py has three changed sections: a rounding fix (stage), added logging (skip), and a comment update (skip). A tmp/payment-scratch.txt file is also in the working tree.

```
git add -p src/payment.py   (y for payment-rounding-hunk, n for others)
git commit -m "Commit payment rounding fix"
```

---

**partial-medium-dashboard-filter**

> src/dashboard.js has three hunks: a filter logic fix (stage), a theme update (skip), and some console.log statements (skip). A notes/dashboard-ideas.md is also present.

```
git add -p src/dashboard.js   (y for dashboard-filter-hunk, n for others)
git commit -m "Commit dashboard filter change"
```

---

### Hard

---

**partial-hard-terraform**

> terraform/main.tf has two hunks: network configuration (stage) and experimental feature flags (skip). A terraform/debug.txt file is also in the workspace.

```
git add -p terraform/main.tf   (y for terraform-network-hunk, n for terraform-experimental-hunk)
git commit -m "Update network Terraform configuration"
```

---

**partial-hard-auth-cross-file**

> Two files are modified: src/auth.py (validation fix hunk to stage, refactor hunk to skip) and tests/test_auth.py (validation test hunk to stage, test cleanup hunk to skip). A notes/auth-debug.md is also present.

```
git add -p src/auth.py       (y for auth-validation-hunk, n for auth-refactor-hunk)
git add -p tests/test_auth.py  (y for auth-validation-test-hunk, n for auth-test-cleanup-hunk)
git commit -m "Commit auth validation path"
```

---

**partial-hard-search-cross-file**

> Two files are modified: src/search.py (ranking fix to stage, cleanup to skip) and tests/test_search.py (ranking test to stage, fixture cleanup to skip). A tmp/search-output.txt is also present.

```
git add -p src/search.py        (y for search-ranking-hunk, n for search-cleanup-hunk)
git add -p tests/test_search.py  (y for search-ranking-test-hunk, n for search-test-fixture-hunk)
git commit -m "Commit search ranking path"
```

---

**partial-hard-export-cross-file**

> Two files are modified: src/export.py (formatting fix to stage, logging additions to skip) and tests/test_export.py (formatting test to stage, test cleanup to skip). A notes/export-followup.md is also present.

```
git add -p src/export.py        (y for export-format-hunk, n for export-logging-hunk)
git add -p tests/test_export.py  (y for export-format-test-hunk, n for export-test-cleanup-hunk)
git commit -m "Commit export formatting path"
```

---

## Lesson 6 — Amending Commits

### Easy

---

**amend-easy-typo**

> You committed with the message 'Initiall commit' — a typo. No file content needs to change, just the message.

```
git commit --amend -m "Initial commit"
```

---

**amend-easy-forgot**

> You committed login.py but forgot to include logout.py — it belongs in the same commit. Stage logout.py and amend the last commit to include it without changing the message.

```
git add src/logout.py
git commit --amend --no-edit
```

---

**amend-easy-login-copy-message**

> Your last commit message says 'Update text' — too vague. It should be 'Clarify login copy'. No file content needs to change.

```
git commit --amend -m "Clarify login copy"
```

---

**amend-easy-readme-message**

> Your last commit message is 'Update README' — not specific enough. The correct message is 'Clarify setup requirements'. Amend the commit message without changing any files.

```
git commit --amend -m "Clarify setup requirements"
```

---

**amend-easy-navbar-message**

> Your last commit message is 'CSS updates' — too generic. It should be 'Adjust navbar spacing'. No content changes needed — just fix the message.

```
git commit --amend -m "Adjust navbar spacing"
```

---

### Medium

---

**amend-med-both**

> Your last commit message was 'update stuff' (too vague) AND you forgot to include docs/CHANGELOG.md. Stage the changelog and fix the message in one amend operation.

```
git add docs/CHANGELOG.md
git commit --amend -m "Add parser feature and update changelog"
```

---

**amend-medium-profile-missing-css**

> You committed profile-card.js but forgot to include styles/profile-card.css — it belongs in the same commit. Stage the missing CSS file and amend without changing the commit message.

```
git add styles/profile-card.css
git commit --amend --no-edit
```

---

**amend-medium-export-doc**

> You committed the export module code but forgot to include docs/export.md. Amend the last commit to add the documentation without changing the message.

```
git add docs/export.md
git commit --amend --no-edit
```

---

**amend-medium-search-template**

> You committed the search JavaScript but forgot to include templates/search.html — it belongs in the same snapshot. Stage the missing template and amend the commit without changing the message.

```
git add templates/search.html
git commit --amend --no-edit
```

---

### Hard

---

**amend-hard-convention**

> Your last commit message is 'terraform configs have been updated for staging env' — passive voice, lowercase, too verbose. Correct it to follow Git imperative convention. No file content changes needed.

```
git commit --amend -m "Update Terraform staging environment configuration"
```

---

**amend-hard-profile-message-and-layout**

> Your last commit has two problems: the message 'Update profile stuff' is too vague, and styles/profile-layout.css was left out by mistake. Fix both — correct the message and add the missing file in one amend.

```
git add styles/profile-layout.css
git commit --amend -m "Polish profile card layout"
```

---

**amend-hard-auth-message-and-test**

> Your last commit message is 'Auth changes' (too vague) and it's missing tests/test_auth.py. Fix both issues in one amend: correct the message and add the missing test file.

```
git add tests/test_auth.py
git commit --amend -m "Add auth validation coverage"
```

---

**amend-hard-export-message-and-doc**

> Your last commit message is 'Export update' (too vague) and docs/export.md is missing from the commit. Fix both: add the documentation file and correct the message in a single amend.

```
git add docs/export.md
git commit --amend -m "Document export validation behavior"
```

---

## Lesson 7 — Unstaging and Discarding Changes

### Easy

---

**restore-easy-unstage**

> You ran git add . and accidentally staged notes.txt along with your intended files. The commit isn't ready yet. Unstage notes.txt while keeping your working-tree changes.

```
git restore --staged notes.txt
```

---

**restore-easy-discard**

> You made some experimental edits to config.py trying out a new approach that didn't work. Discard all working-tree changes to config.py and get back to the last committed state.

```
git restore config.py
```

---

**restore-easy-unstage-app**

> You staged src/app.py but realize you're not ready to commit it yet. Unstage it so it stays as a working-tree change without being discarded.

```
git restore --staged src/app.py
```

---

**restore-easy-unstage-guide**

> You staged docs/guide.md, but you want to revise it more before committing. Unstage it — your edits should remain in the working tree, not be discarded.

```
git restore --staged docs/guide.md
```

---

**restore-easy-unstage-css**

> You staged styles/site.css but then realized another CSS change needs to be grouped with it. Unstage it for now so you can re-stage everything together later.

```
git restore --staged styles/site.css
```

---

### Medium

---

**restore-med-unstage-discard**

> You staged experimental.py (keep it as a working-tree change) and also have working-tree edits to README.md that you want to throw away entirely. First unstage experimental.py, then discard the README changes.

```
git restore --staged experimental.py
git restore README.md
```

---

**restore-medium-app-debug**

> You staged src/app.py but aren't ready to commit it yet, and you also have a debug.log in the working tree that you want to get rid of. Unstage app.py to preserve your work, then discard debug.log.

```
git restore --staged src/app.py
git restore debug.log
```

---

**restore-medium-docs-scratch**

> You staged docs/guide.md for a later commit and also have a tmp/scratch.txt that was just temporary notes. Unstage the guide to continue editing it, and discard the scratch file entirely.

```
git restore --staged docs/guide.md
git restore tmp/scratch.txt
```

---

**restore-medium-css-build**

> You staged styles/site.css for revision and also have a generated dist/site.css in your working tree from an old build. Unstage the source CSS to keep working on it, and discard the generated dist file.

```
git restore --staged styles/site.css
git restore dist/site.css
```

---

### Hard

---

**restore-hard-cleanup**

> You have a noisy mixed state: debug.log and scratch/notes.txt are staged (unstage them — don't discard, just move back to working tree), and api/experimental.py has working-tree changes you want to throw away.

```
git restore --staged debug.log scratch/notes.txt
git restore api/experimental.py
```

---

**restore-hard-mixed-profile**

> Two files are staged: src/profile-card.js (keep your edits as a working-tree change) and notes/profile-ideas.md (also keep, just unstage). A debug/profile.log in the working tree should be discarded entirely.

```
git restore --staged src/profile-card.js notes/profile-ideas.md
git restore debug/profile.log
```

---

**restore-hard-mixed-export**

> Two files are staged: src/export.py (keep the edits as a working-tree change) and notes/export-plan.md (also keep, just unstage). A tmp/export-output.txt generated file is in the working tree and should be discarded.

```
git restore --staged src/export.py notes/export-plan.md
git restore tmp/export-output.txt
```

---

**restore-hard-mixed-search**

> Two files are staged: src/search.js (preserve your edits, just unstage) and notes/search.md (also keep, just unstage). A debug/search.log in the working tree should be discarded entirely.

```
git restore --staged src/search.js notes/search.md
git restore debug/search.log
```

---

## Lesson 8 — Module 1 Review and Practice

### Easy

---

**cap1-easy-staged-with-ignore**

> You added the auth module to the service. Stage src/auth.py and the .gitignore together — the logs/auth.log file is generated and must stay out of the commit.

```
git add src/auth.py .gitignore
git commit -m "Add auth module"
```

---

**cap1-easy-two-source-ignore**

> You added the data pipeline module. Commit src/pipeline.py and .gitignore together — the output/results.csv is a generated artifact and must not be included.

```
git add src/pipeline.py .gitignore
git commit -m "Add data pipeline module"
```

---

**review-easy-docs-ignore**

> You wrote the introductory docs page. Commit docs/intro.md and .gitignore together — dist/site.html is a build artifact and should remain excluded.

```
git add docs/intro.md .gitignore
git commit -m "Prepare docs portal intro"
```

---

**review-easy-profile-ignore**

> You updated the profile card component. Commit src/profile-card.js and .gitignore as one focused snapshot — the dist/profile-card.js build artifact must be left out.

```
git add src/profile-card.js .gitignore
git commit -m "Prepare profile card update"
```

---

**review-easy-export-ignore**

> You updated the export workflow module. Stage src/export.py and .gitignore for a focused commit — the output/export.csv file is generated output and must stay out.

```
git add src/export.py .gitignore
git commit -m "Prepare export workflow update"
```

---

### Medium

---

**cap1-med-api-with-note**

> You added the API module with its tests. Commit src/api.py, tests/test_api.py, and .gitignore together. A notes/api-design.md personal note should stay in your working tree — don't commit it. The dist/api.js build artifact is ignored and must stay out.

```
git add src/api.py tests/test_api.py .gitignore
git commit -m "Add API module with tests"
```

---

**review-medium-profile-with-note**

> You finalized the profile card update. Commit src/profile-card.js, styles/profile-card.css, and .gitignore as one snapshot. A notes/profile-ideas.md personal note can stay in your working tree.

```
git add src/profile-card.js styles/profile-card.css .gitignore
git commit -m "Finalize profile card update"
```

---

**review-medium-search-with-output**

> You finalized the search results view. Commit src/search.js, templates/search.html, and .gitignore. Your notes/search-ranking.md notes can stay in the working tree.

```
git add src/search.js templates/search.html .gitignore
git commit -m "Finalize search results update"
```

---

**review-medium-export-with-note**

> You finalized the export module and its documentation. Commit src/export.py, docs/export.md, and .gitignore together. Your notes/export-plan.md personal notes can remain in the working tree.

```
git add src/export.py docs/export.md .gitignore
git commit -m "Finalize export documentation update"
```

---

### Hard (Partial Staging)

---

**cap1-hard-infra-partial**

> Two files are modified: terraform/main.tf (network config hunk to stage, experimental hunk to skip) and tests/test_infra.py (coverage test hunk to stage, cleanup hunk to skip). A notes/infra-plan.md is also present.

```
git add -p terraform/main.tf    (y for infra-network-hunk, n for infra-experimental-hunk)
git add -p tests/test_infra.py  (y for infra-test-coverage-hunk, n for infra-test-cleanup-hunk)
git commit -m "Add network infrastructure and test coverage"
```

---

**review-hard-auth-partial**

> Two files are modified: src/auth.py (validation fix hunk to stage, refactor hunk to skip) and tests/test_auth.py (validation test hunk to stage, test cleanup hunk to skip). A notes/auth-debug.md is also present.

```
git add -p src/auth.py          (y for auth-validation-hunk, n for auth-refactor-hunk)
git add -p tests/test_auth.py   (y for auth-validation-test-hunk, n for auth-test-cleanup-hunk)
git commit -m "Finalize auth validation change"
```

---

**review-hard-search-partial**

> Two files are modified: src/search.js (ranking fix hunk to stage, theme update hunk to skip) and tests/test_search.js (ranking test hunk to stage, fixture cleanup hunk to skip). A tmp/search-output.json is also present.

```
git add -p src/search.js          (y for search-ranking-hunk, n for search-theme-hunk)
git add -p tests/test_search.js   (y for search-ranking-test-hunk, n for search-fixture-cleanup-hunk)
git commit -m "Finalize search ranking behavior"
```

---

### Hard (Amend)

---

**cap1-hard-api-amend**

> Your last commit message is 'WIP api stuff' (not ready for review) and it's missing tests/test_api.py. Fix both: add the test file and correct the message in one amend operation.

```
git add tests/test_api.py
git commit --amend -m "Add API module with test coverage"
```

---

**review-hard-export-amend**

> Your last commit message is 'Export update' (too vague) and it's missing docs/export.md. Amend the commit to add the documentation and correct the message — without creating a new commit.

```
git add docs/export.md
git commit --amend -m "Finalize export validation behavior"
```

---

*Note: Lesson 4 (.gitignore) is flagged — no approved SO. Its cases are excluded from this answer key.*

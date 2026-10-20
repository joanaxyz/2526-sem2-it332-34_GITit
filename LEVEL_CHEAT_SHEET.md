# GIT it! — Level answer sheet (STAFF ONLY)

Generated from the wave plan by `python scripts/curriculum/render_level_cheat_sheet.py`;
do not edit by hand. Covers 21 levels, 132 waves and 349 variants in Modules 1–4,
plus each module's Challenge Gate.

A tier's waves play in order. The first variant listed is a first-time learner's;
a retry rotates within the same wave. Commands run left to right, and file edits
happen in Project Files at the point shown.

## Module 1 — Local Repository Foundations

### Initializing Repositories

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Track this folder (debut) | `init-easy-current-empty` Initialize the current folder | `git init -b main` |
|  | `init-easy-trunk-branch` Initialize with trunk as the first branch | `git init --initial-branch=trunk` |
| Easy 2. Start a new project folder (practice) | `init-easy-invoice` Initialize invoice-tracker | `git init -b main invoice-tracker` |
|  | `init-med-oss` Initialize oss-contrib | `git init -b main oss-contrib` |
| Medium 1. Folder and branch from the brief (practice) | `init-medium-docs-site` Initialize docs-site | `git init -b main docs-site` |
|  | `init-medium-trunk-api-playground` Initialize api-playground with trunk | `git init -b trunk api-playground` |
| Medium 2. Existing files stay untracked (practice) | `init-medium-existing-files` Initialize field-notes with existing files | `git init -b main field-notes` |
|  | `init-hard-ci` Initialize ci-configs | `git init -b main ci-configs` |
| Hard 1. Only the right subfolder (transfer) | `init-hard-research-log` Initialize research-log subfolder only | `git init -b main research-log` |
|  | `init-hard-ui-kit` Initialize ui-kit with trunk | `git init --initial-branch=trunk ui-kit` |
| Hard 2. A nested project folder (transfer) | `init-hard-nested-service` Set up the billing service inside the services folder | `git init -b trunk services/billing-api` |
|  | `init-hard-nested-course` Set up the Git basics course inside the courses folder | `git init -b main courses/git-basics` |

### Cloning Remote Repositories

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Clone a repository (debut) | `clone-easy-docs-portal` Clone docs-portal | `git clone https://example.test/training/docs-portal.git` |
|  | `clone-easy-oss-ssh` Clone oss-toolkit via SSH | `git clone git@github.com:open-dev/oss-toolkit.git` |
| Easy 2. Clone into a named folder (debut) | `clone-easy-api-lab` Clone api-lab into api-workshop | `git clone https://example.test/training/api-lab.git api-workshop` |
|  | `clone-easy-corp` Clone audit-logs into audit-logs-local | `git clone https://git.corp.example/it/audit-logs.git audit-logs-local` |
| Easy 3. Clone a specific branch (debut) | `clone-easy-profile-starter` Clone profile-site at the starter branch | `git clone -b starter https://example.test/training/profile-site.git` |
|  | `clone-med-feature` Clone backend-api at feature/auth | `git clone -b feature/auth https://github.com/acme-startup/backend-api.git` |
|  | `clone-medium-cli-starter-folder` Clone cli-tool at starter into cli-starter-lab | `git clone --branch starter https://example.test/tools/cli-tool.git cli-starter-lab` |
| Medium 1. SSH address, named folder (practice) | `clone-medium-analytics-ssh` Clone analytics-lab via SSH into analytics-worktree | `git clone git@example.test:training/analytics-lab.git analytics-worktree` |
|  | `clone-hard-research-log-ssh` Clone research-log via SSH into research-log-lab | `git clone git@example.test:docs/research-log.git research-log-lab` |
| Medium 2. Shallow history (debut) | `clone-medium-css-kit-shallow` Shallow clone css-kit | `git clone --depth 1 https://example.test/frontend/css-kit.git` |
|  | `clone-medium-shallow-metrics` Shallow copy of the metrics dashboard | `git clone --depth 1 https://example.test/data/metrics-dash.git metrics-review` |
| Hard 1. Shallow copy of one branch (transfer) | `clone-hard-mobile-ui-shallow-branch` Shallow clone mobile-ui at starter into mobile-ui-lab | `git clone --depth 1 -b starter https://example.test/frontend/mobile-ui.git mobile-ui-lab` |
|  | `clone-hard-lab-notebook-depth-branch` Shallow clone lab-notebook at review into notebook-review | `git clone --depth 1 --branch review https://example.test/docs/lab-notebook.git notebook-review` |
| Hard 2. Shallow review copy over SSH (transfer) | `clone-hard-ssh-shallow` Shallow SSH clone of oss-toolkit into oss-review | `git clone --depth 1 git@github.com:open-dev/oss-toolkit.git oss-review` |
|  | `clone-hard-shallow-ssh-audit` Two commits of the audit rules over SSH | `git clone --depth 2 git@example.test:security/audit-rules.git rules-review` |

### Staging and Committing

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Stage and commit one change (debut) | `commit-easy-form-validation` Commit form validation update | `git add src/form.js` → `git commit -m "Update form validation"` |
|  | `commit-easy-readme-setup` Commit README clarification | `git add README.md` → `git commit -m "Clarify setup steps"` |
|  | `commit-easy-navbar-spacing` Commit navbar spacing fix | `git add styles/navbar.css` → `git commit -m "Adjust navbar spacing"` |
|  | `commit-easy-auth-dir` Commit the auth module directory | `git add src/auth/` → `git commit -m "Add auth module"` |
| Easy 2. Stage several files at once (debut) | `commit-easy-initial` Initial commit for library-system | `git add README.md main.py requirements.txt` → `git commit -m "Initial commit"` |
|  | `commit-med-docker` Commit Docker configuration | `git add Dockerfile .env.example` → `git commit -m "Add Docker configuration"` |
| Medium 1. A two-file change (practice) | `commit-medium-profile-card` Commit profile card layout | `git add src/profile-card.js styles/profile-card.css` → `git commit -m "Update profile card layout"` |
|  | `commit-medium-search-results` Commit search results view | `git add src/search.js templates/search.html` → `git commit -m "Refine search results view"` |
|  | `commit-medium-export-flow` Commit export flow update | `git add src/export.py docs/export.md` → `git commit -m "Document export flow update"` |
| Medium 2. First snapshot of a new project (spiral) | `commit-medium-new-project-portfolio` First snapshot of the portfolio | `git init -b main` → `git add index.html styles.css` → `git commit -m "Initial portfolio"` |
|  | `commit-medium-new-project-recipes` Start tracking the recipe notes | `git init -b main` → `git add recipes.md shopping.md` → `git commit -m "Start recipe notes"` |
| Hard 1. Leave the distractor out (transfer) | `commit-hard-selective` Commit handler fix, leave experimental file out | `git add api/handler.py` → `git commit -m "Fix request handler null check"` |
|  | `commit-hard-profile-distractor` Commit profile card change, leave notes out | `git add src/profile-card.js` → `git commit -m "Update profile card behavior"` |
|  | `commit-hard-export-distractor` Commit export fix, leave scratch output out | `git add src/export.py` → `git commit -m "Fix export validation"` |
| Hard 2. Two targets, two distractors (transfer) | `commit-hard-parser` Commit parser and tests, leave debug/scratch files out | `git add src/parser.py tests/test_parser.py` → `git commit -m "Add parser module with unit tests"` |
|  | `commit-hard-search-two-targets-one-distractor` Commit search ranking display, leave notes out | `git add src/search.js templates/search.html` → `git commit -m "Refine search ranking display"` |

### Partial Staging

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Stage one hunk (debut) | `partial-easy-billing` Stage the billing fix hunk only | `git add -p src/billing.py` → `git commit -m "Fix billing calculation rounding error"` |
|  | `partial-easy-auth-validation` Stage the auth validation hunk only | `git add -p src/auth.py` → `git commit -m "Fix auth validation"` |
|  | `partial-easy-export-format` Stage the export formatting hunk only | `git add -p src/export.py` → `git commit -m "Fix export formatting"` |
| Easy 2. Another file, another hunk (practice) | `partial-easy-routes` Stage the routes handler hunk only | `git add -p src/routes.py` → `git commit -m "Update API route handlers"` |
|  | `partial-easy-search-ranking` Stage the search ranking hunk only | `git add -p src/search.py` → `git commit -m "Fix search ranking"` |
| Medium 1. One hunk out of many (practice) | `partial-med-three-hunk` Stage only the parser bug fix hunk | `git add -p src/parser.py` → `git commit -m "Fix parser blank-line bug"` |
|  | `partial-medium-profile-validation` Stage only the profile validation hunk | `git add -p src/profile.py` → `git commit -m "Fix profile validation"` |
|  | `partial-medium-payment-rounding` Stage only the payment rounding hunk | `git add -p src/payment.py` → `git commit -m "Fix payment rounding"` |
|  | `partial-medium-dashboard-filter` Stage only the dashboard filter hunk | `git add -p src/dashboard.js` → `git commit -m "Fix dashboard filter"` |
| Medium 2. A hunk and a whole file (spiral) | `partial-medium-hunk-plus-test` The rounding fix and its test | `git add -p src/cart.py` → `git add tests/test_cart.py` → `git commit -m "Fix cart total rounding"` |
|  | `partial-medium-hunk-plus-doc` The quoting fix and its documentation | `git add -p src/export.py` → `git add docs/export.md` → `git commit -m "Fix CSV quoting"` |
| Hard 1. Hunks across code and tests (transfer) | `partial-hard-terraform` Stage only the network Terraform hunk | `git add -p terraform/main.tf` → `git commit -m "Update network Terraform configuration"` |
|  | `partial-hard-auth-cross-file` Stage validation hunks across auth code and tests | `git add -p src/auth.py` → `git add -p tests/test_auth.py` → `git commit -m "Fix auth validation and add its test"` |
|  | `partial-hard-search-cross-file` Stage ranking hunks across search code and tests | `git add -p src/search.py` → `git add -p tests/test_search.py` → `git commit -m "Fix search ranking and add its test"` |
|  | `partial-hard-export-cross-file` Stage formatting hunks across export code and tests | `git add -p src/export.py` → `git add -p tests/test_export.py` → `git commit -m "Fix export formatting and add its test"` |
| Hard 2. Split one file into two commits (compose) | `partial-hard-split-two-commits-api` Split the API changes into two commits | `git add -p src/api.py` → `git commit -m "Fix token expiry check"` → `git add src/api.py` → `git commit -m "Tidy API logging"` |
|  | `partial-hard-split-two-commits-ui` Split the menu changes into two commits | `git add -p src/menu.js` → `git commit -m "Fix menu focus trap"` → `git add src/menu.js` → `git commit -m "Rename menu helpers"` |

### Amending Commits

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Fix the last commit message (debut) | `amend-easy-typo` Fix a typo in the last commit message | `git commit --amend -m "Initial commit"` |
|  | `amend-easy-login-copy-message` Clarify a vague commit message | `git commit --amend -m "Clarify login copy"` |
|  | `amend-easy-readme-message` Clarify the README commit message | `git commit --amend -m "Clarify setup requirements"` |
|  | `amend-easy-navbar-message` Clarify the navbar commit message | `git commit --amend -m "Adjust navbar spacing"` |
|  | `amend-hard-convention` Correct a verbose passive-voice commit message | `git commit --amend -m "Update Terraform staging environment configuration"` |
| Easy 2. Add the forgotten file (practice) | `amend-easy-forgot` Add a forgotten file to the last commit | `git add src/logout.py` → `git commit --amend -m "Add auth module"` |
|  | `amend-medium-profile-missing-css` Add missing profile CSS to the last commit | `git add styles/profile-card.css` → `git commit --amend -m "Update profile card layout"` |
| Medium 1. Amend content and message (practice) | `amend-med-both` Add changelog and correct the commit message | `git add docs/CHANGELOG.md` → `git commit --amend -m "Add parser feature and update changelog"` |
|  | `amend-medium-export-doc` Add missing export docs to the last commit | `git add docs/export.md` → `git commit --amend -m "Document export flow update"` |
|  | `amend-medium-search-template` Add missing search template to the last commit | `git add templates/search.html` → `git commit --amend -m "Refine search results view"` |
| Medium 2. Amend in one hunk (spiral) | `amend-medium-hunk-into-last-checkout` Fold the missing guard into the last commit | `git add -p src/checkout.py` → `git commit --amend -m "Validate checkout totals"` |
|  | `amend-medium-hunk-into-last-search` Fold the exact-match ranking into the last commit | `git add -p src/search.py` → `git commit --amend -m "Rank exact matches first"` |
| Hard 1. Missing file and wrong message (transfer) | `amend-hard-profile-message-and-layout` Add missing CSS and correct the commit message | `git add styles/profile-layout.css` → `git commit --amend -m "Polish profile card layout"` |
|  | `amend-hard-auth-message-and-test` Add missing test and correct the commit message | `git add tests/test_auth.py` → `git commit --amend -m "Add auth validation coverage"` |
|  | `amend-hard-export-message-and-doc` Add missing docs and correct the commit message | `git add docs/export.md` → `git commit --amend -m "Document export validation behavior"` |
| Hard 2. Fix the last message, then commit the rest (compose) | `amend-hard-fix-message-then-commit-api` Reword, then document the rate limiter | `git commit --amend -m "Add rate limiter"` → `git add docs/limits.md` → `git commit -m "Document rate limits"` |
|  | `amend-hard-fix-message-then-commit-docs` Reword, then add the install FAQ | `git commit --amend -m "Document install steps"` → `git add docs/faq.md` → `git commit -m "Add install FAQ"` |

### Unstaging and Discarding Changes

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Unstage but keep the edit (debut) | `restore-easy-unstage` Unstage notes.txt without discarding it | `git restore --staged notes.txt` |
|  | `restore-easy-unstage-app` Unstage src/app.py without discarding it | `git restore --staged src/app.py` |
|  | `restore-easy-unstage-guide` Unstage docs/guide.md without discarding it | `git restore --staged docs/guide.md` |
|  | `restore-easy-unstage-css` Unstage styles/site.css without discarding it | `git restore --staged styles/site.css` |
| Easy 2. Throw away a working change (debut) | `restore-easy-discard` Discard experimental config.py changes | `git restore config.py` |
|  | `restore-easy-discard-theme` Throw away the neon theme | `git restore styles/theme.css` |
| Medium 1. Unstage one, discard another (compose) | `restore-med-unstage-discard` Unstage experimental.py, discard README.md changes | `git restore --staged experimental.py` → `git restore README.md` |
|  | `restore-medium-app-debug` Preserve app.py, discard debug.log | `git restore --staged src/app.py` → `git restore debug.log` |
|  | `restore-medium-docs-scratch` Preserve guide.md, discard scratch.txt | `git restore --staged docs/guide.md` → `git restore tmp/scratch.txt` |
|  | `restore-medium-css-build` Preserve source CSS, discard generated dist CSS | `git restore --staged styles/site.css` → `git restore dist/site.css` |
| Medium 2. Fix the staging, then commit (spiral) | `restore-medium-unstage-then-commit-login` Unstage the to-do list, then commit the login fix | `git restore --staged notes/todo.md` → `git commit -m "Fix login redirect"` |
|  | `restore-medium-unstage-then-commit-cart` Unstage the ideas file, then commit the badge fix | `git restore --staged scratch/ideas.txt` → `git commit -m "Fix cart badge count"` |
| Hard 1. Several to unstage, one to discard (transfer) | `restore-hard-cleanup` Unstage two files, discard experimental.py | `git restore --staged debug.log scratch/notes.txt` → `git restore api/experimental.py` |
|  | `restore-hard-mixed-profile` Unstage two files, discard debug log | `git restore --staged src/profile-card.js notes/profile-ideas.md` → `git restore debug/profile.log` |
|  | `restore-hard-mixed-export` Unstage two files, discard generated output | `git restore --staged src/export.py notes/export-plan.md` → `git restore tmp/export-output.txt` |
|  | `restore-hard-mixed-search` Unstage two files, discard debug search log | `git restore --staged src/search.js notes/search.md` → `git restore debug/search.log` |
| Hard 2. Clean up, then commit only the fix (spiral) | `restore-hard-capstone-report` Clean up before the report fix | `git restore --staged debug.log` → `git restore tmp/output.txt` → `git add -p src/report.py` → `git commit -m "Fix report totals"` |
|  | `restore-hard-capstone-invoice` Clean up before the invoice fix | `git restore --staged notes/invoice-ideas.md` → `git restore build/invoice.html` → `git add -p src/invoice.py` → `git commit -m "Fix invoice due date"` |

### Challenge Gate — Foundations Gate

| Trial | Variant | Answer key |
|---|---|---|
| Easy | `gate1-easy-first-snapshot-field-log` Start the field log | `git init -b main` → `git add notes.md readings.csv` → `git commit -m "Start field log"` |
|  | `gate1-easy-first-snapshot-quiz` Start the quiz app | `git init -b main` → `git add index.html quiz.js` → `git commit -m "Start quiz app"` |
| Medium | `gate1-medium-complete-last-commit-search` Finish the search page commit | `git restore --staged notes.txt` → `git add templates/search.html` → `git add -p src/search.py` → `git commit --amend -m "Add search page"` |
|  | `gate1-medium-complete-last-commit-upload` Finish the file upload commit | `git restore --staged scratch.md` → `git add docs/upload.md` → `git add -p src/upload.py` → `git commit --amend -m "Add file upload"` |
| Hard | `gate1-hard-reword-then-commit-export` Reword, tidy up and commit the export fix | `git restore --staged tmp/run.log` → `git commit --amend -m "Add export"` → `git restore cache/report.json` → `git add -p src/export.py` → `git add docs/export.md` → `git commit -m "Fix export headers"` |
|  | `gate1-hard-reword-then-commit-billing` Reword, tidy up and commit the billing fix | `git restore --staged logs/billing.log` → `git commit --amend -m "Add billing"` → `git restore cache/invoices.json` → `git add -p src/billing.py` → `git add docs/billing.md` → `git commit -m "Fix billing tax"` |

## Module 2 — Branching and Collaboration

### Creating and Switching Branches

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Create a branch and switch to it (debut) | `v21e-auth` Create feature/auth and switch to it | `git switch -c feature/auth` |
|  | `v21e-login` Create bugfix/login and switch to it | `git switch -c bugfix/login` |
|  | `v21e-ui` Create experiment/ui and switch to it | `git switch -c experiment/ui` |
|  | `bc-easy-capstone-db` Create feature/database-models and switch to it | `git switch -c feature/database-models` |
|  | `bc-easy-corp-hotfix` Create hotfix/session-timeout and switch to it | `git switch -c hotfix/session-timeout` |
| Easy 2. Go back to main (debut) | `switch-easy-back-to-main-docs` Back to main after the docs refresh | `git switch main` |
|  | `switch-easy-back-to-main-api` Back to main after the API keys model | `git switch main` |
| Medium 1. Create a branch without switching (debut) | `v21m-payments` Create feature/payments and a test branch from the 2-commit main tip | `git branch feature/payments-tests` → `git switch -c feature/payments` |
|  | `v21m-notifications` Create feature/notifications and a docs branch from the 3-commit main tip | `git branch feature/notifications-docs` → `git switch -c feature/notifications` |
|  | `v21m-export` Create feature/export and a docs branch from the 4-commit main tip | `git branch feature/export-docs` → `git switch -c feature/export` |
| Medium 2. Start from another branch's tip (practice) | `bc-med-oss-develop` Create feature/docs-update from develop's tip | `git switch -c feature/docs-update` |
|  | `v21h-from-develop` Create feature/workspace from main's tip while on develop | `git switch -c feature/workspace main` |
| Hard 1. Start from an older commit (transfer) | `v21h-hotfix-c1` Create hotfix/critical at c1 (not HEAD) | `git switch -c hotfix/critical c1` |
|  | `v21h-detach-save` Create saved-work at the detached HEAD position | `git switch -c saved-work` |
| Hard 2. Save detached work, then go back (transfer) | `bc-hard-review-snap` Create review/v1-snapshot at c1, then return to main | `git switch -c review/v1-snapshot` → `git switch main` |
|  | `switch-hard-detached-save-and-return` Keep the spike, then head to develop | `git switch -c archive/spike-results` → `git switch develop` |

### Branch Naming Conventions

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Follow the naming convention (practice) | `bn-easy-corp-jira` Create PROJ-418/password-reset | `git switch -c PROJ-418/password-reset` |
|  | `bn-easy-startup-feat` Create feature/shopping-cart | `git switch -c feature/shopping-cart` |
|  | `bn-easy-oss-user` Create jdelacruz/fix-parser-edge-case | `git switch -c jdelacruz/fix-parser-edge-case` |
|  | `bn-easy-cap-initials` Create feature/jm/database-models | `git switch -c feature/jm/database-models` |
|  | `bn-easy-free-client` Create client/55-contact-form-redesign | `git switch -c client/55-contact-form-redesign` |
| Easy 2. Delete a merged branch (debut) | `bn-easy-delete-merged-typo` Delete the merged typo branch | `git branch -d fix/readme-typo` |
|  | `bn-easy-delete-merged-spike` Delete the merged search spike | `git branch -d spike/old-search` |
| Medium 1. Build the name from the brief (practice) | `bn-med-corp-notif` Construct and create PROJ-512/email-notification | `git switch -c PROJ-512/email-notification` |
|  | `bn-med-startup-bugfix` Construct and create bugfix/login-redirect | `git switch -c bugfix/login-redirect` |
|  | `bn-med-devops-scope` Construct and create infra/api-gateway/log-rotation | `git switch -c infra/api-gateway/log-rotation` |
|  | `bn-med-oss-infer` Infer the convention and create fix/tokenizer-crash | `git switch -c fix/tokenizer-crash` |
| Medium 2. Replace a badly named branch (compose) | `bn-hard-oss-rename` Replace myFix with fix/renderer-memory-leak | `git branch -d myFix` → `git switch -c fix/renderer-memory-leak` |
|  | `bn-hard-corp-rename` Replace auth-update with PROJ-301/auth-module-update | `git branch -d auth-update` → `git switch -c PROJ-301/auth-module-update` |
| Hard 1. Fix the name, keep the convention (transfer) | `bn-hard-startup-prefix` Replace fix/cart-total with bugfix/cart-total | `git branch -d fix/cart-total` → `git switch -c bugfix/cart-total` |
|  | `bn-hard-qa-camel` Replace test/LoginFlow with test/login-flow | `git branch -d test/LoginFlow` → `git switch -c test/login-flow` |
| Hard 2. Start the fix on a well-named branch (spiral) | `bn-hard-named-branch-commit-parser` Start the parser fix on a proper branch | `git restore debug.log` → `git switch -c fix/parser-unicode` → `git add src/parser.py` → `git commit -m "Handle unicode identifiers"` |
|  | `bn-hard-named-branch-commit-billing` Start the invoice fix on a ticket branch | `git restore tmp/billing-dump.txt` → `git switch -c PROJ-733/invoice-rounding` → `git add src/billing.py` → `git commit -m "Round invoice totals"` |

### Stashing Work in Progress

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Shelve work and switch (debut) | `v23e-auth` Stash auth work and switch to main | `git stash` → `git switch main` |
|  | `v23e-notify` Stash notify work and switch to develop | `git stash` → `git switch develop` |
|  | `v23e-cache` Stash cache work and switch to release/v2 | `git stash` → `git switch release/v2` |
|  | `stash-easy-cap-review` Stash models work and switch to review/groupmate-branch | `git stash` → `git switch review/groupmate-branch` |
|  | `stash-easy-docs-switch` Stash docs work and switch to release/stable | `git stash` → `git switch release/stable` |
| Easy 2. Bring the shelved work back (debut) | `stash-easy-pop-search` Bring back the search ranking draft | `git stash pop` |
|  | `stash-easy-pop-profile` Bring back the profile avatar draft | `git stash pop` |
| Medium 1. Stash, visit, return, restore (compose) | `v23m-to-main` Stash payments work, check main, restore | `git stash` → `git switch main` → `git switch feature/payments` → `git stash pop` |
|  | `v23m-to-hotfix` Stash orders work, check hotfix, restore | `git stash` → `git switch hotfix/fix-tax` → `git switch feature/orders` → `git stash pop` |
|  | `v23m-to-release` Stash analytics work, check release/v2, restore | `git stash` → `git switch release/v2` → `git switch feature/analytics` → `git stash pop` |
|  | `stash-med-corp-named` Stash billing work, check hotfix/tax-fix, restore | `git stash` → `git switch hotfix/tax-fix` → `git switch feature/billing` → `git stash pop` |
| Medium 2. Discard a cancelled draft (debut) | `v23h-dropped-auth` Check main while the auth rework is cancelled | `git stash` → `git switch main` → `git switch feature/auth-rework` → `git stash drop` |
|  | `v23h-dropped-api` Check hotfix/urgent while the api-v2 draft is cancelled | `git stash` → `git switch hotfix/urgent` → `git switch feature/api-v2` → `git stash drop` |
| Hard 1. Two stashes, keep the right one (transfer) | `stash-hard-oss-multi` Discard one abandoned stash and restore the other | `git stash drop stash@{0}` → `git stash pop` |
|  | `stash-hard-two-stashes-reports` Two drafts in the stash, keep the real one | `git stash drop stash@{0}` → `git stash pop` |
| Hard 2. Cancelled work, clean exit (transfer) | `v23h-dropped-refactor` Check release/v1 while the refactor is cancelled | `git stash` → `git switch release/v1` → `git switch feature/refactor` → `git stash drop` |
|  | `stash-hard-cancelled-experiment` Check the release, then drop the layout experiment | `git stash` → `git switch release/v3` → `git switch feature/experiment` → `git stash drop` |

### Pushing to a Remote

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Publish a branch (debut) | `v24e-auth` Push feature/auth to origin | `git push origin feature/auth` |
|  | `v24e-orders` Push feature/orders to origin | `git push origin feature/orders` |
|  | `v24e-parser` Push feature/parser to origin | `git push origin feature/parser` |
|  | `push-easy-cap-auth` Push feature/user-auth to origin | `git push origin feature/user-auth` |
|  | `push-easy-free-landing` Push feature/client-landing to origin | `git push origin feature/client-landing` |
| Easy 2. Publish and track (debut) | `v24m-auth` Push feature/auth and set its upstream | `git push -u origin feature/auth` |
|  | `v24m-orders` Push feature/orders and set its upstream | `git push -u origin feature/orders` |
|  | `v24m-parser` Push feature/parser and set its upstream | `git push -u origin feature/parser` |
|  | `push-med-docs-track` Push feature/v2-migration-guide and set its upstream | `git push -u origin feature/v2-migration-guide` |
| Medium 1. Branch, commit, publish (spiral) | `push-medium-branch-commit-publish-search` Branch, commit and publish the search filters | `git switch -c feature/search-filters` → `git add src/filters.js` → `git commit -m "Add search filters"` → `git push -u origin feature/search-filters` |
|  | `push-medium-branch-commit-publish-invoices` Branch, commit and publish the invoice PDF export | `git switch -c feature/invoice-pdf` → `git add src/invoice_pdf.py` → `git commit -m "Add invoice PDF export"` → `git push -u origin feature/invoice-pdf` |
| Medium 2. Republish rewritten history safely (debut) | `v24h-auth` Publish rewritten feature/auth without overwriting a teammate's work | `git push --force-with-lease origin feature/auth` |
|  | `v24h-orders` Publish rewritten feature/orders without overwriting a teammate's work | `git push --force-with-lease origin feature/orders` |
| Hard 1. Amend a published commit, republish (spiral) | `push-hard-amend-then-lease-api` Reword a published commit and republish safely | `git commit --amend -m "Add retry to API client"` → `git push --force-with-lease origin feature/api-retry` |
|  | `push-hard-amend-then-lease-docs` Reword the SSO docs commit and republish | `git commit --amend -m "Document SSO setup"` → `git push --force-with-lease origin docs/sso` |
| Hard 2. Rewritten branch, careful publish (transfer) | `v24h-parser` Publish rewritten feature/parser without overwriting a teammate's work | `git push --force-with-lease origin feature/parser` |
|  | `push-hard-devops-fwl` Publish rewritten feature/pipeline-config without overwriting a teammate's work | `git push --force-with-lease origin feature/pipeline-config` |

### Fetching and Pulling from a Remote

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. See what's new on origin (debut) | `v25e-main` Fetch to update origin/main tracking | `git fetch origin` |
|  | `v25e-feature` Fetch to update origin/feature/auth tracking | `git fetch origin` |
|  | `v25e-develop` Fetch to update origin/develop tracking | `git fetch origin` |
|  | `fetch-easy-cap-check` Fetch to update origin/feature/models tracking | `git fetch origin` |
|  | `fetch-easy-corp-list` Fetch to update origin/release/v2 tracking | `git fetch origin` |
| Easy 2. Bring the new commits in (debut) | `v25m-main` Pull origin/main into local main | `git pull origin main` |
|  | `v25m-feature` Pull origin/feature/auth into local feature/auth | `git pull origin feature/auth` |
|  | `v25m-develop` Pull origin/develop into local develop | `git pull origin develop` |
|  | `pull-med-free-client` Pull origin/staging into local staging | `git pull origin staging` |
| Medium 1. Review before integrating (compose) | `v25h-main` Review incoming work on main, then update main | `git fetch origin` → `git log --oneline main..origin/main` → `git pull origin main` |
|  | `v25h-feature` Review incoming work on feature/auth, then update it | `git fetch origin` → `git log --oneline feature/auth..origin/feature/auth` → `git pull origin feature/auth` |
| Medium 2. Update, then branch from fresh main (spiral) | `pull-medium-update-then-branch-ui` Update main, then start dark mode | `git pull origin main` → `git switch -c feature/dark-mode` |
|  | `pull-medium-update-then-branch-api` Update main, then start the webhooks | `git pull origin main` → `git switch -c feature/webhooks` |
| Hard 1. Review incoming work (transfer) | `v25h-develop` Review incoming work on develop, then update it | `git fetch origin` → `git log --oneline develop..origin/develop` → `git pull origin develop` |
|  | `fetch-hard-oss-review` Review incoming work on release/next, then update it | `git fetch origin` → `git log --oneline release/next..origin/release/next` → `git pull origin release/next` |
| Hard 2. Pull with local work in progress (spiral) | `pull-hard-stash-pull-pop-docs` Update main without losing your guide edits | `git stash` → `git pull origin main` → `git stash pop` |
|  | `pull-hard-stash-pull-pop-app` Update develop without losing your timeout setting | `git stash` → `git pull origin develop` → `git stash pop` |

### Reconciling Diverged Local and Remote Histories

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Pull, then push again (practice) | `v26e-auth` Reconcile and push feature/auth | `git pull origin feature/auth` → `git push origin feature/auth` |
|  | `v26e-payments` Reconcile and push feature/payments | `git pull origin feature/payments` → `git push origin feature/payments` |
|  | `v26e-hotfix` Reconcile and push hotfix/critical | `git pull origin hotfix/critical` → `git push origin hotfix/critical` |
|  | `rec-easy-cap-ui` Reconcile and push feature/ui-layout | `git pull origin feature/ui-layout` → `git push origin feature/ui-layout` |
|  | `rec-easy-docs-chapter` Reconcile and push main | `git pull origin main` → `git push origin main` |
| Easy 2. Fetch, merge the remote branch, push (debut) | `v26m-auth` Fetch, merge, push feature/auth | `git fetch origin` → `git merge origin/feature/auth` → `git push origin feature/auth` |
|  | `v26m-payments` Fetch, merge, push feature/payments | `git fetch origin` → `git merge origin/feature/payments` → `git push origin feature/payments` |
| Medium 1. Reconcile a teammate's branch (practice) | `v26m-hotfix` Fetch, merge, push hotfix/critical | `git fetch origin` → `git merge origin/hotfix/critical` → `git push origin hotfix/critical` |
|  | `rec-med-qa-testrunner` Fetch, merge, push feature/test-runner-v2 | `git fetch origin` → `git merge origin/feature/test-runner-v2` → `git push origin feature/test-runner-v2` |
| Medium 2. Commit, reconcile, publish (spiral) | `rec-medium-commit-then-reconcile-docs` Commit the setup docs, reconcile and publish | `git restore --staged notes/draft.md` → `git commit -m "Document local setup"` → `git pull origin main` → `git push origin main` |
|  | `rec-medium-commit-then-reconcile-api` Commit the health check, reconcile and publish | `git restore --staged scratch/payload.json` → `git commit -m "Add health check"` → `git pull origin develop` → `git push origin develop` |
| Hard 1. Reconcile from the wrong branch (transfer) | `v26h-auth` Reconcile and publish feature/auth from the wrong branch | `git switch feature/auth` → `git fetch origin` → `git merge origin/feature/auth` → `git push origin feature/auth` |
|  | `v26h-payments` Reconcile and publish feature/payments from the wrong branch | `git switch feature/payments` → `git fetch origin` → `git merge origin/feature/payments` → `git push origin feature/payments` |
| Hard 2. Reconcile and publish under pressure (transfer) | `v26h-hotfix` Reconcile and publish hotfix/critical from the wrong branch | `git switch hotfix/critical` → `git fetch origin` → `git merge origin/hotfix/critical` → `git push origin hotfix/critical` |
|  | `rec-hard-corp-audit` Reconcile and publish the audit branch from develop | `git switch feature/compliance-audit` → `git fetch origin` → `git merge origin/feature/compliance-audit` → `git push origin feature/compliance-audit` |

### Completing Branch Merges

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Fast-forward merge (practice) | `v27e-auth` Fast-forward merge feature/auth into main | `git merge feature/auth` |
|  | `v27e-payments` Fast-forward merge feature/payments into develop | `git merge feature/payments` |
|  | `v27e-hotfix` Fast-forward merge hotfix/fix-critical into release/v2 | `git merge hotfix/fix-critical` |
|  | `merge-easy-cap-docs` Fast-forward merge docs/readme-update into staging | `git merge docs/readme-update` |
|  | `merge-easy-free-contact` Fast-forward merge feature/contact-form into integration | `git merge feature/contact-form` |
| Easy 2. Keep a visible merge commit (debut) | `v27m-auth` No-ff merge feature/auth into main | `git merge --no-ff feature/auth` |
|  | `v27m-payments` No-ff merge feature/payments into develop | `git merge --no-ff feature/payments` |
| Medium 1. Merge with a merge commit (practice) | `v27m-hotfix` No-ff merge hotfix/fix-critical into release/v2 | `git merge --no-ff hotfix/fix-critical` |
|  | `merge-med-corp-sso` No-ff merge feature/sso-integration into release/v1 | `git merge --no-ff feature/sso-integration` |
| Medium 2. Finish the feature, then land it (spiral) | `merge-medium-commit-switch-noff-reports` Finish the monthly report, then land it | `git add src/reports.py` → `git commit -m "Add monthly report"` → `git switch main` → `git merge --no-ff feature/reports` |
|  | `merge-medium-commit-switch-noff-auth` Finish the MFA prompt, then land it on develop | `git add src/mfa.py` → `git commit -m "Add MFA prompt"` → `git switch develop` → `git merge --no-ff feature/mfa` |
| Hard 1. Land from the wrong branch (transfer) | `v27h-auth` Land feature/auth on main from the wrong branch, with a visible merge | `git switch main` → `git merge --no-ff feature/auth` |
|  | `v27h-payments` Land feature/payments on develop from the wrong branch, with a visible merge | `git switch develop` → `git merge --no-ff feature/payments` |
|  | `v27h-hotfix` Land hotfix/critical on release/v1 from the wrong branch, with a visible merge | `git switch release/v1` → `git merge --no-ff hotfix/critical` |
|  | `merge-hard-devops-cert` Land hotfix/cert-renewal on release/stable from the wrong branch, with a visible merge | `git switch release/stable` → `git merge --no-ff hotfix/cert-renewal` |
| Hard 2. Land, publish, tidy up (spiral) | `merge-hard-land-publish-tidy-search` Land the search page, publish and tidy up | `git switch main` → `git merge --no-ff feature/search` → `git push origin main` → `git branch -d feature/search` |
|  | `merge-hard-land-publish-tidy-billing` Land the rounding hotfix on the release, publish and tidy up | `git switch release/v2` → `git merge --no-ff hotfix/billing-rounding` → `git push origin release/v2` → `git branch -d hotfix/billing-rounding` |

### Squash Merging

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Squash a branch into one commit (debut) | `v28e-auth` Squash-merge feature/auth into main | `git merge --squash feature/auth` → `git commit -m "Add auth feature"` |
|  | `v28e-orders` Squash-merge feature/orders into develop | `git merge --squash feature/orders` → `git commit -m "Add orders feature"` |
|  | `v28e-parser` Squash-merge feature/parser into release/v2 | `git merge --squash feature/parser` → `git commit -m "Add parser feature"` |
|  | `squash-easy-cap-report` Squash-merge feature/report-generator into integration | `git merge --squash feature/report-generator` → `git commit -m "Add report generator module"` |
|  | `squash-easy-free-payment` Squash-merge feature/payment-flow into staging | `git merge --squash feature/payment-flow` → `git commit -m "Add payment flow"` |
| Easy 2. Squash, then force-delete the branch (debut) | `v28h-auth` Land feature/auth as one commit and clean up | `git merge --squash feature/auth` → `git commit -m "Add auth feature"` → `git branch -D feature/auth` |
|  | `v28h-orders` Land feature/orders as one commit and clean up | `git merge --squash feature/orders` → `git commit -m "Add orders feature"` → `git branch -D feature/orders` |
| Medium 1. Squash a teammate's remote branch (practice) | `v28m-auth` Fetch then squash-merge origin/feature/auth into main | `git fetch origin` → `git merge --squash origin/feature/auth` → `git commit -m "Add auth feature"` |
|  | `v28m-orders` Fetch then squash-merge origin/feature/orders into develop | `git fetch origin` → `git merge --squash origin/feature/orders` → `git commit -m "Add orders feature"` |
|  | `v28m-parser` Fetch then squash-merge origin/feature/parser into release/v2 | `git fetch origin` → `git merge --squash origin/feature/parser` → `git commit -m "Add parser feature"` |
|  | `squash-med-corp-gdpr` Fetch then squash-merge origin/feature/gdpr-export into staging | `git fetch origin` → `git merge --squash origin/feature/gdpr-export` → `git commit -m "Add GDPR data export endpoint"` |
| Medium 2. Squash and publish (spiral) | `squash-medium-squash-publish-onboarding` Squash the onboarding flow and publish | `git merge --squash feature/onboarding` → `git commit -m "Add onboarding flow"` → `git push origin main` |
|  | `squash-medium-squash-publish-export` Squash the CSV export and publish | `git merge --squash feature/export-csv` → `git commit -m "Add CSV export"` → `git push origin develop` |
| Hard 1. One commit, no leftovers (transfer) | `v28h-parser` Land feature/parser as one commit and clean up | `git merge --squash feature/parser` → `git commit -m "Add parser feature"` → `git branch -D feature/parser` |
|  | `squash-hard-devops-log` Land feature/log-rotation as one commit and clean up | `git merge --squash feature/log-rotation` → `git commit -m "Add log rotation configuration"` → `git branch -D feature/log-rotation` |
| Hard 2. Squash-land from another branch (spiral) | `squash-hard-switch-squash-cleanup-cli` Squash the CLI colours from their branch and clean up | `git switch main` → `git merge --squash feature/cli-colors` → `git commit -m "Add CLI colors"` → `git branch -D feature/cli-colors` |
|  | `squash-hard-switch-squash-cleanup-ui` Squash the toast notifications onto develop and clean up | `git switch develop` → `git merge --squash feature/toast-ui` → `git commit -m "Add toast notifications"` → `git branch -D feature/toast-ui` |

### Deleting and Recovering Remote Branches

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Delete a remote branch (debut) | `v29e-auth` Delete origin/feature/auth | `git push origin --delete feature/auth` |
|  | `v29e-orders` Delete origin/feature/orders | `git push origin --delete feature/orders` |
|  | `v29e-parser` Delete origin/feature/parser | `git push origin --delete feature/parser` |
|  | `rb-easy-cap-group` Delete origin/feature/group-auth | `git push origin --delete feature/group-auth` |
|  | `rb-easy-corp-sprint` Delete origin/feature/sprint12-compliance | `git push origin --delete feature/sprint12-compliance` |
| Easy 2. Prune stale remote-tracking refs (debut) | `v29m-auth` Prune stale origin/feature/auth ref | `git fetch --prune origin` |
|  | `v29m-orders` Prune stale origin/feature/orders ref | `git fetch --prune origin` |
|  | `v29m-parser` Prune stale origin/feature/parser ref | `git fetch --prune origin` |
|  | `rb-med-free-prune` Prune stale origin/feature/old-landing ref | `git fetch --prune origin` |
| Medium 1. Retire a branch everywhere (compose) | `v29h-auth` Retire feature/auth on origin and locally | `git push origin --delete feature/auth` → `git branch -d feature/auth` |
|  | `v29h-orders` Retire feature/orders on origin and locally | `git push origin --delete feature/orders` → `git branch -d feature/orders` |
| Medium 2. Land and retire (spiral) | `rb-medium-land-and-retire-search` Land the search page and retire its remote branch | `git merge --no-ff feature/search` → `git push origin main` → `git push origin --delete feature/search` |
|  | `rb-medium-land-and-retire-billing` Land the billing summary and retire its remote branch | `git merge --no-ff feature/billing` → `git push origin main` → `git push origin --delete feature/billing` |
| Hard 1. Retire safely (transfer) | `v29h-parser` Retire feature/parser on origin and locally | `git push origin --delete feature/parser` → `git branch -d feature/parser` |
|  | `rb-hard-oss-full` Retire feature/oss-contribution on origin and locally | `git push origin --delete feature/oss-contribution` → `git branch -d feature/oss-contribution` |
| Hard 2. Fetch, land, publish, retire, prune (spiral) | `rb-hard-capstone-release-notes` Release notes: fetch, land, publish, retire, prune | `git fetch origin` → `git merge --no-ff origin/feature/release-notes` → `git push origin main` → `git push origin --delete feature/release-notes` → `git fetch --prune origin` |
|  | `rb-hard-capstone-payments` Payments v2: fetch, land, publish, retire, prune | `git fetch origin` → `git merge --no-ff origin/feature/payments-v2` → `git push origin main` → `git push origin --delete feature/payments-v2` → `git fetch --prune origin` |

### Challenge Gate — Collaboration Gate

| Trial | Variant | Answer key |
|---|---|---|
| Easy | `gate2-easy-fresh-branch-search` Start the search filters from a fresh main | `git switch main` → `git pull origin main` → `git switch -c feature/search-filters` |
|  | `gate2-easy-fresh-branch-invoices` Start the invoice export from a fresh main | `git switch main` → `git pull origin main` → `git switch -c feature/invoice-pdf` |
| Medium | `gate2-medium-stash-and-sync-reports` Update main without losing the chart work | `git stash` → `git switch main` → `git pull origin main` → `git switch feature/reports` → `git stash pop` |
|  | `gate2-medium-stash-and-sync-profile` Update main without losing the avatar work | `git stash` → `git switch main` → `git pull origin main` → `git switch feature/profile` → `git stash pop` |
| Hard | `gate2-hard-land-and-retire-filters` Land the search filters and retire the branch | `git switch main` → `git pull origin main` → `git merge --squash feature/filters` → `git commit -m "Add search filters"` → `git push origin main` → `git branch -D feature/filters` → `git push origin --delete feature/filters` |
|  | `gate2-hard-land-and-retire-export` Land the CSV export and retire the branch | `git switch main` → `git pull origin main` → `git merge --squash feature/export` → `git commit -m "Add CSV export"` → `git push origin main` → `git branch -D feature/export` → `git push origin --delete feature/export` |

## Module 3 — Conflict Resolution

### Resolving Merge Conflicts Manually

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Resolve one conflicted file (debut) | `manual-easy-auth-copy` Resolve src/auth.js | `git merge feature/auth-timeout` → *edit `src/auth.js`* → `git add src/auth.js` → `git commit --no-edit` |
|  | `manual-easy-profile-copy` Resolve src/profile.tsx | `git merge feature/profile-copy` → *edit `src/profile.tsx`* → `git add src/profile.tsx` → `git commit --no-edit` |
|  | `manual-easy-billing-copy` Resolve src/billing.py | `git merge feature/regional-currency` → *edit `src/billing.py`* → `git add src/billing.py` → `git commit --no-edit` |
| Easy 2. Resolve another file (practice) | `manual-easy-config-copy` Resolve src/config.py | `git merge feature/debug-config` → *edit `src/config.py`* → `git add src/config.py` → `git commit --no-edit` |
|  | `manual-easy-navbar-copy` Resolve src/components/Navbar.tsx | `git merge feature/navbar-rebrand` → *edit `src/components/Navbar.tsx`* → `git add src/components/Navbar.tsx` → `git commit --no-edit` |
| Easy 3. Back out of a merge (debut) | `manual-easy-abort-wrong-branch` Back out of the legacy theme merge | `git merge --abort` |
|  | `manual-easy-abort-too-early` Back out of the payments merge until review ends | `git merge --abort` |
| Medium 1. Resolve config conflicts (practice) | `manual-medium-router` Resolve src/routes.ts | `git merge feature/routes` → *edit `src/routes.ts`* → `git add src/routes.ts` → `git commit --no-edit` |
|  | `manual-medium-policy` Resolve src/policy.yml | `git merge feature/policy` → *edit `src/policy.yml`* → `git add src/policy.yml` → `git commit --no-edit` |
|  | `manual-medium-gateway` Resolve config/gateway.yml | `git merge feature/gateway` → *edit `config/gateway.yml`* → `git add config/gateway.yml` → `git commit --no-edit` |
| Medium 2. A pull that conflicts (spiral) | `manual-medium-pull-conflict-readme` A pull that conflicts in the README | `git pull origin main` → *edit `README.md`* → `git add README.md` → `git commit --no-edit` → `git push origin main` |
|  | `manual-medium-pull-conflict-config` A pull that conflicts in the app config | `git pull origin develop` → *edit `config/app.yml`* → `git add config/app.yml` → `git commit --no-edit` → `git push origin develop` |
| Hard 1. Resolve with less guidance (transfer) | `manual-hard-pricing` Resolve src/pricing.rb | `git merge feature/pricing` → *edit `src/pricing.rb`* → `git add src/pricing.rb` → `git commit --no-edit` |
|  | `manual-hard-schema` Resolve schema/orders.sql | `git merge feature/schema` → *edit `schema/orders.sql`* → `git add schema/orders.sql` → `git commit --no-edit` |
|  | `manual-hard-migration` Resolve db/migrations/001_users.sql | `git merge feature/migration` → *edit `db/migrations/001_users.sql`* → `git add db/migrations/001_users.sql` → `git commit --no-edit` |
| Hard 2. Abort the wrong merge, resolve the right one (transfer) | `manual-hard-abort-redo` Abort a wrong merge, then resolve the right one | `git merge --abort` → `git merge feature/help-center` → *edit `src/routes.ts`* → `git add src/routes.ts` → `git commit --no-edit` |
|  | `manual-hard-abort-redo-payments` Abort the v1 payments merge and merge v2 | `git merge --abort` → `git merge feature/payments-v2` → *edit `src/payments.py`* → `git add src/payments.py` → `git commit --no-edit` |

### Resolving Conflicts Using a Merge Tool

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Resolve in the merge tool (debut) | `mergetool-easy-cache-ttl` Resolve src/cache.py in the merge tool | `git merge feature/cache-ttl` → `git mergetool` → *edit `src/cache.py`* → `git commit --no-edit` |
|  | `mergetool-easy-mail-footer` Resolve src/mailer.py in the merge tool | `git merge feature/mail-footer` → `git mergetool` → *edit `src/mailer.py`* → `git commit --no-edit` |
|  | `mergetool-easy-upload-limit` Resolve src/limits.js in the merge tool | `git merge feature/upload-limit` → `git mergetool` → *edit `src/limits.js`* → `git commit --no-edit` |
| Easy 2. Another conflict, same tool (practice) | `mergetool-easy-app-locale` Resolve config/app.ini in the merge tool | `git merge feature/app-locale` → `git mergetool` → *edit `config/app.ini`* → `git commit --no-edit` |
|  | `mergetool-easy-labels` Resolve src/labels.ts in the merge tool | `git merge feature/labels-fil` → `git mergetool` → *edit `src/labels.ts`* → `git commit --no-edit` |
| Medium 1. Two files in one pass (practice) | `mergetool-medium-checkout-copy` Resolve two checkout files in the merge tool | `git merge feature/checkout-copy` → `git mergetool` → *edit `src/checkout.js`* → *edit `src/receipt.js`* → `git commit --no-edit` |
|  | `mergetool-medium-api-limits` Resolve rate-limit and CORS settings in the merge tool | `git merge feature/api-limits` → `git mergetool` → *edit `config/limits.yml`* → *edit `config/cors.yml`* → `git commit --no-edit` |
|  | `mergetool-medium-db-names` Resolve two schema files in the merge tool | `git merge feature/db-rename` → `git mergetool` → *edit `schema/books.sql`* → *edit `schema/authors.sql`* → `git commit --no-edit` |
|  | `mergetool-medium-docs-sync` Resolve two documentation files in the merge tool | `git merge feature/docs-sync` → `git mergetool` → *edit `docs/setup.md`* → *edit `docs/usage.md`* → `git commit --no-edit` |
| Medium 2. Set up the team's tool first (debut) | `mergetool-hard-choose-tool` Resolve src/prices.py when no merge tool is set up | `git config merge.tool meld` → `git merge feature/pricing-v2` → `git mergetool` → *edit `src/prices.py`* → `git commit --no-edit` |
|  | `mergetool-medium-configure-tool-billing` Set up the team's merge tool, then merge | `git config merge.tool meld` → `git merge feature/billing-copy` → `git mergetool` → *edit `src/billing_copy.txt`* → `git commit --no-edit` |
| Hard 1. Judge which side to keep (transfer) | `mergetool-hard-one-of-two` Resolve only the conflicted file after a partial merge | `git merge feature/release-notes` → `git mergetool` → *edit `src/version.py`* → `git commit --no-edit` |
|  | `mergetool-hard-take-theirs` Keep the incoming version of src/i18n.json | `git merge feature/i18n-refresh` → `git mergetool` → *edit `src/i18n.json`* → `git commit --no-edit` |
| Hard 2. No leftovers (transfer) | `mergetool-hard-no-leftovers` Resolve src/auth.js and leave no backup files behind | `git config mergetool.keepBackup false` → `git merge feature/auth-timeout` → `git mergetool` → *edit `src/auth.js`* → `git commit --no-edit` |
|  | `mergetool-hard-no-backup-api` Merge the API version without backup files | `git config mergetool.keepBackup false` → `git merge feature/api-v3` → `git mergetool` → *edit `src/api_version.py`* → `git commit --no-edit` |

### Cherry-Picking Commits

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Copy one commit (debut) | `cherry-easy-login-timeout` Cherry-pick c1 onto release-1.0 | `git cherry-pick c1` |
|  | `cherry-easy-invoice-rounding` Cherry-pick c1 onto release-1.1 | `git cherry-pick c1` |
|  | `cherry-easy-export-null` Cherry-pick c1 onto release-2.0 | `git cherry-pick c1` |
|  | `cherry-easy-rate-limit` Cherry-pick c1 onto release-1.2 | `git cherry-pick c1` |
|  | `cherry-easy-null-check` Cherry-pick c1 onto release-2.1 | `git cherry-pick c1` |
|  | `cherry-medium-login-timeout` Cherry-pick c1 and c2 onto release-1.0 | `git cherry-pick c1` → `git cherry-pick c2` |
|  | `cherry-medium-invoice-rounding` Cherry-pick the newest invoice fix onto release-1.1 | `git cherry-pick feature/invoice-rounding` |
| Easy 2. Record where it came from (debut) | `cherry-hard-trace-source` Cherry-pick c1 onto release-finalize and record its source | `git cherry-pick -x c1` |
|  | `cherry-easy-trace-source-hotfix` Backport the retry fix and note its source | `git cherry-pick -x c2` |
| Easy 3. Pick without committing (debut) | `cherry-medium-no-commit` Cherry-pick c1 into the index (no commit) on release-review | `git cherry-pick --no-commit c1` |
|  | `cherry-medium-staged-review` Cherry-pick c1 into the index (no commit) on release-staged | `git cherry-pick --no-commit c1` |
| Medium 1. Resolve and continue (debut) | `cherry-hard-export-conflict` Cherry-pick c1 onto release-2.0 and resolve the conflict | `git cherry-pick c1` → *edit `src/export.py`* → `git add src/export.py` → `git cherry-pick --continue` |
|  | `cherry-medium-conflict-continue-auth` Resolve and continue the lockout backport | `git cherry-pick c1` → *edit `src/auth.py`* → `git add src/auth.py` → `git cherry-pick --continue` |
| Medium 2. Cancel a stopped pick (debut) | `cherry-hard-abort-conflict` Cancel a cherry-pick that stopped on a conflict | `git cherry-pick --abort` |
|  | `cherry-medium-abort-stopped-pick` Cancel the stopped cart backport | `git cherry-pick --abort` |
| Medium 3. Two fixes, one reviewed commit (compose) | `cherry-medium-two-fixes-one-commit-login` Two login fixes, one reviewed backport | `git cherry-pick --no-commit c2` → `git cherry-pick --no-commit c3` → `git commit -m "Backport login fixes"` |
|  | `cherry-medium-two-fixes-one-commit-tax` Two tax fixes, one reviewed backport | `git cherry-pick --no-commit c1` → `git cherry-pick --no-commit c4` → `git commit -m "Backport tax fixes"` |
| Hard 1. Backport to two releases (transfer) | `cherry-hard-two-releases` Cherry-pick c1 onto both release-1.2 and release-1.1 | `git switch release-1.2` → `git cherry-pick c1` → `git switch release-1.1` → `git cherry-pick c1` |
|  | `cherry-hard-two-releases-security` Backport the session fix to both releases | `git switch release-2.1` → `git cherry-pick c3` → `git switch release-2.0` → `git cherry-pick c3` |
| Hard 2. Abort the wrong pick, backport the right one (spiral) | `cherry-hard-backport-capstone-export` Wrong pick out, right fix in, with its source | `git cherry-pick --abort` → `git cherry-pick -x c4` → *edit `src/export.py`* → `git add src/export.py` → `git cherry-pick --continue` |
|  | `cherry-hard-backport-capstone-login` Wrong pick out, right login fix in, with its source | `git cherry-pick --abort` → `git cherry-pick -x c4` → *edit `src/login.py`* → `git add src/login.py` → `git cherry-pick --continue` |

### Challenge Gate — Conflict Gate

| Trial | Variant | Answer key |
|---|---|---|
| Easy | `gate3-easy-merge-and-resolve-banner` Merge the banner and settle its conflict | `git merge feature/banner` → *edit `src/banner.html`* → `git add src/banner.html` → `git commit --no-edit` |
|  | `gate3-easy-merge-and-resolve-footer` Merge the footer and settle its conflict | `git merge feature/footer` → *edit `src/footer.html`* → `git add src/footer.html` → `git commit --no-edit` |
| Medium | `gate3-medium-backport-tax` Backport the tax fix with its origin noted | `git switch release/2.1` → `git cherry-pick -x c3` → *edit `src/tax.py`* → `git add src/tax.py` → `git cherry-pick --continue` |
|  | `gate3-medium-backport-locale` Backport the date format fix with its origin noted | `git switch release/3.0` → `git cherry-pick -x c3` → *edit `src/locale.py`* → `git add src/locale.py` → `git cherry-pick --continue` |
| Hard | `gate3-hard-abort-then-tool-merge-pricing` Back out the wrong merge and use the team's tool | `git merge --abort` → `git config merge.tool meld` → `git merge feature/pricing-v2` → `git mergetool` → *edit `src/prices.py`* → `git commit --no-edit` |
|  | `gate3-hard-abort-then-tool-merge-copy` Back out the wrong merge and use the team's tool | `git merge --abort` → `git config merge.tool meld` → `git merge feature/checkout-copy` → `git mergetool` → *edit `src/checkout.js`* → `git commit --no-edit` |

## Module 4 — Advanced Recovery and History

### Recovering from Hard Resets

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Recover the lost tip (debut) | `e1` Recover an accidental reset | `git reflog` → `git show c3` → `git switch -c recovery/e1 c3` |
|  | `e2` Recover after a script reset | `git reflog` → `git show c3` → `git switch -c recovery/e2 c3` |
|  | `e3` Recover after resetting too far | `git reflog` → `git show c3` → `git switch -c recovery/e3 c3` |
| Easy 2. Recover after another reset (practice) | `e4` Recover after a merge reset | `git reflog` → `git show c3` → `git switch -c recovery/e4 c3` |
|  | `e5` Recover a debugging reset | `git reflog` → `git show c3` → `git switch -c recovery/e5 c3` |
| Medium 1. Deeper in the reflog (practice) | `m1` Recover an accidental reset | `git reflog` → `git show c3` → `git switch -c recovery/m1 c3` |
|  | `m2` Recover after a script reset | `git reflog` → `git show c3` → `git switch -c recovery/m2 c3` |
|  | `m3` Recover after resetting too far | `git reflog` → `git show c3` → `git switch -c recovery/m3 c3` |
|  | `m4` Recover after a merge reset | `git reflog` → `git show c3` → `git switch -c recovery/m4 c3` |
|  | `m5` Recover a debugging reset | `git reflog` → `git show c3` → `git switch -c recovery/m5 c3` |
| Medium 2. Recover and share it (spiral) | `reflog-medium-recover-and-publish-search` Recover the search ranking fix and publish it | `git reflog` → `git switch -c recovery/search-fix c4` → `git push -u origin recovery/search-fix` |
|  | `reflog-medium-recover-and-publish-billing` Recover the billing summary and publish it | `git reflog` → `git switch -c recovery/billing c5` → `git push -u origin recovery/billing` |
| Hard 1. Pick the right candidate (transfer) | `h1` Recover an accidental reset | `git reflog` → `git show c4` → `git show c3` → `git switch -c recovery/h1 c3` |
|  | `h2` Recover after a script reset | `git reflog` → `git show c4` → `git show c3` → `git switch -c recovery/h2 c3` |
|  | `h3` Recover after resetting too far | `git reflog` → `git show c4` → `git show c3` → `git switch -c recovery/h3 c3` |
|  | `h4` Recover after a merge reset | `git reflog` → `git show c4` → `git show c3` → `git switch -c recovery/h4 c3` |
|  | `h5` Recover a debugging reset | `git reflog` → `git show c4` → `git show c3` → `git switch -c recovery/h5 c3` |
| Hard 2. Recover, then bring the fix to main (spiral) | `reflog-hard-recover-then-pick-auth` Bookmark the lost work, then bring only the auth fix to main | `git reflog` → `git show c4` → `git branch recovery/auth c4` → `git cherry-pick c4` |
|  | `reflog-hard-recover-then-pick-export` Bookmark the lost work, then bring only the export fix to main | `git reflog` → `git show c4` → `git branch recovery/export c4` → `git cherry-pick c4` |

### Reversing Pushed Commits Safely

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Undo a pushed commit safely (debut) | `re6` Revert c3 safely | `git revert c3` → `git push` |
|  | `re7` Revert c2 safely | `git revert c2` → `git push` |
|  | `re8` Revert c4 safely | `git revert c4` → `git push` |
| Easy 2. Sync first, then revert (spiral) | `revert-easy-pull-then-revert-docs` Sync first, then undo the docs theme | `git pull origin main` → `git revert c3` → `git push` |
|  | `revert-easy-pull-then-revert-api` Sync first, then undo the endpoint rename | `git pull origin main` → `git revert c4` → `git push` |
| Medium 1. Find the culprit from the symptom (practice) | `rm6` Restore progressive tax withholding | `git log --oneline` → `git show c2` → `git revert c2` → `git push` |
|  | `rm7` Stop the every-minute push notifications | `git log --oneline` → `git show c2` → `git revert c2` → `git push` |
|  | `rm8` Restore relevance ranking in search | `git log --oneline` → `git show c1` → `git revert c1` → `git push` |
| Medium 2. Revert on the release branch (spiral) | `revert-medium-release-branch-pricing` Undo the pricing change on release 2.1 | `git switch release/2.1` → `git revert c4` → `git push` |
|  | `revert-medium-release-branch-auth` Undo the SSO requirement on release 1.8 | `git switch release/1.8` → `git revert c3` → `git push` |
| Hard 1. Two faulty commits, one publish (transfer) | `rh6` Roll back two faulty checkout changes | `git revert c3` → `git revert c1` → `git push` |
|  | `rh7` Roll back two faulty session changes | `git revert c3` → `git revert c1` → `git push` |
|  | `rh8` Roll back two faulty site changes | `git revert c4` → `git revert c2` → `git push` |
| Hard 2. Rewrite only what isn't published (spiral) | `revert-hard-amend-local-revert-pushed-shop` Reword the local commit, revert the published one | `git commit --amend -m "Add order export"` → `git revert c2` → `git push` |
|  | `revert-hard-amend-local-revert-pushed-blog` Reword the local commit, revert the published feed change | `git commit --amend -m "Add RSS feed"` → `git revert c3` → `git push` |

### Completing Rebase Recovery Sequences

| Wave | Variant | Answer key |
|---|---|---|
| Easy 1. Replay your branch onto main (debut) | `be6` Rebase feature/recovery onto main | `git rebase main` → `git log --oneline --graph --all` |
|  | `be7` Rebase feature/search-filters onto main | `git rebase main` → `git log --oneline --graph --all` |
|  | `be8` Rebase feature/cli-flags onto main | `git rebase main` → `git log --oneline --graph --all` |
| Easy 2. Abandon a stopped rebase (debut) | `rebase-medium-abort` Abandon a rebase that stopped on a conflict | `git rebase --abort` |
|  | `rebase-easy-abort-stopped-docs` Abandon the stopped docs rebase | `git rebase --abort` |
| Easy 3. Resolve and continue a rebase (debut) | `rebase-hard-continue` Finish a rebase after fixing a conflict | *edit `src/limiter.py`* → `git add src/limiter.py` → `git rebase --continue` |
|  | `rebase-easy-continue-config` Resolve and continue the config loader rebase | *edit `config/app.yml`* → `git add config/app.yml` → `git rebase --continue` |
| Medium 1. Move only your commits (debut) | `bm6` Move fix/footer-typo onto main | `git log --oneline --graph --all` → `git rebase --onto main feature/checkout-redesign fix/footer-typo` |
|  | `bm7` Move hotfix/login-timeout onto main | `git log --oneline --graph --all` → `git rebase --onto main release/2.0-beta hotfix/login-timeout` |
| Medium 2. Reset to the original tip, then rebase (debut) | `bh6` Recover the dropped commit on feature/cli-flags | `git reflog` → `git reset --hard c4` → `git rebase main` |
|  | `bh7` Recover the dropped commit on hotfix/export-csv | `git reflog` → `git reset --hard c5` → `git rebase main` |
| Hard 1. Continue the rebase, then publish safely (spiral) | `rebase-hard-continue-then-lease-search` Finish the search rebase and republish safely | *edit `src/search.py`* → `git add src/search.py` → `git rebase --continue` → `git push --force-with-lease origin feature/search` |
|  | `rebase-hard-continue-then-lease-billing` Finish the billing rebase and republish safely | *edit `src/billing.py`* → `git add src/billing.py` → `git rebase --continue` → `git push --force-with-lease origin feature/billing` |
| Hard 2. Abort, then move only your commits (transfer) | `rebase-hard-abort-then-onto-reports` Abort, then move only the reports commits | `git rebase --abort` → `git rebase --onto main spike/charts feature/reports` |
|  | `rebase-hard-abort-then-onto-ui` Abort, then move only the table commits | `git rebase --abort` → `git rebase --onto main spike/new-grid feature/table-ui` |
| Hard 3. Undo a bad rebase and republish (spiral) | `rebase-hard-reset-rebase-lease-cli` Undo a bad rebase of the CLI flags and republish | `git reflog` → `git reset --hard c6` → `git rebase main` → `git push --force-with-lease origin feature/cli-flags` |
|  | `rebase-hard-reset-rebase-lease-api` Undo a bad rebase of the rate limiter and republish | `git reflog` → `git reset --hard c5` → `git rebase main` → `git push --force-with-lease origin feature/rate-limits` |

### Challenge Gate — Recovery Gate

| Trial | Variant | Answer key |
|---|---|---|
| Easy | `gate4-easy-recover-search-fix` Rescue the lost search fix | `git reflog` → `git show c3` → `git switch -c recovery/search c3` |
|  | `gate4-easy-recover-receipt-fix` Rescue the lost receipt fix | `git reflog` → `git show c3` → `git switch -c recovery/receipts c3` |
| Medium | `gate4-medium-drop-local-revert-published-banner` Drop the experiment, reverse the published banner | `git reset --hard c2` → `git revert c2` → `git push origin main` |
|  | `gate4-medium-drop-local-revert-published-alerts` Drop the experiment, reverse the published alert change | `git reset --hard c2` → `git revert c2` → `git push origin main` |
| Hard | `gate4-hard-move-branch-onto-main-receipts` Move the receipts branch off the release line | `git rebase --abort` → `git rebase --onto main release/1.0 feature/receipts` → `git push --force-with-lease origin feature/receipts` |
|  | `gate4-hard-move-branch-onto-main-coupons` Move the coupons branch off the release line | `git rebase --abort` → `git rebase --onto main release/1.0 feature/coupons` → `git push --force-with-lease origin feature/coupons` |

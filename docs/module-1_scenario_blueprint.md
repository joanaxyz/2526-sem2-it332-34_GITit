# GIT it! Module 1 Scenario Blueprints — Seed-Ready v3

**Scope:** Module 1 only.  
**Purpose:** Concrete scenario-definition content for seeding `ScenarioSkillFocus`, `DifficultyInstance`, `CommandCountPolicy`, and `ScenarioGenerationBlueprint` records.  
**Important constraint:** The 9 Module 1 scenarios are fixed by the curriculum. This document does **not** change the scenario set. It refines each scenario definition so every runtime-generated variant has a different answer and a different expected repository state.

---

## 0. Content architecture

Runtime generation should use this model:

```text
ScenarioSkillFocus = fixed curriculum skill
DifficultyInstance = Easy / Medium / Hard version of that skill
ScenarioGenerationBlueprint = seed-authored template + authored cases
ScenarioVariant = generated concrete playable attempt
```

The builder must select from authored `parameter_pools.cases`. It should not invent arbitrary scenario values.

Each generated variant must render its own:

```text
parameter_context
initial_state
target_rule
target_state
expected_state_diagram
student_context
solution_commands       # internal only; never exposed to frontend
```

A variant is valid only when its **expected-state answer differs** from other cases in the same difficulty or retry pool. Different story text alone is not a valid variant.

---

## 1. Shared non-counted diagnostic commands

Use these as `non_counted_patterns` for all Module 1 command-count policies unless a difficulty explicitly narrows them:

```json
[
  "git status",
  "git status -s",
  "git status --short",
  "git status --porcelain",
  "git status -sb",
  "git status --ignored",
  "git log",
  "git log --oneline",
  "git log --oneline --graph --all",
  "git log -n <number>",
  "git log --max-count=<number>",
  "git diff",
  "git diff <path>",
  "git diff --staged",
  "git diff --cached",
  "git diff --staged <path>",
  "git diff --cached <path>",
  "git diff HEAD",
  "git diff --name-only",
  "git diff --staged --name-only",
  "git show",
  "git show <commit>",
  "git show --name-only",
  "git remote",
  "git remote -v",
  "git branch",
  "git branch -v",
  "git reflog",
  "git check-ignore -v <path>",
  "git ls-files"
]
```

The full parser/preview support matrix lives in `docs/module-1_command_support_matrix.md`.

Diagnostic commands should support state-based practice, but diagnostic-only learning belongs in lesson overview and command-preview content.

---

## 2. Required evaluator/simulator support

The following support is required because this document intentionally keeps the richer curriculum cases:

1. `git init <directory>` must set `operation_metadata.last_init_directory` and allow the evaluator to confirm the target directory.
2. `git clone` must support default/custom destinations, `-b`/`--branch`, and `--depth`; it must set clone operation metadata and materialize remote fixture commits with real `tree` and `changes`, not empty placeholder commits.
3. `.gitignore` cases must distinguish ignored untracked files from tracked generated files.
4. Hard `.gitignore` cases require `git rm --cached <path>` or equivalent simulator support.
5. Partial staging cases require hunk/content-token support. A path-only check is insufficient.
6. Amend cases must prove the latest commit was amended, not followed by an extra normal commit.
7. Inspection cases require answer capture or structured observation submission, not only command execution.
8. Expected-state diagrams must render commit messages, changed paths, tree summaries, staging, working tree, remotes, stash, conflicts, and operation metadata where relevant.

Do not remove these cases. Upgrade the evaluator/simulator if needed.

---

## 3. Shared student-context rule

Every generated variant must expose exact values checked by `target_rule` in `student_context.provided_values`, `requirements`, or `success_checklist`.

Show:

```text
commit message, target files, excluded files, branch names, remote URLs, destination folders,
ignored patterns, hunk labels/tokens, files to preserve/discard, diagnostic questions
```

Do not show:

```text
solution_commands, ordered command sequence, raw target_rule JSON
```

---

# Scenario 1.1 — Initialize a Local Repository

```yaml
scenario_slug: initialize-local-repository
title: Initialize a local repository
focus: git init
skill_focus_type: command_specific
primary_focus_commands: ["git init"]
supporting_diagnostic_commands: ["git status"]
completion_type: state_based
related_git_concepts: ["repository metadata", ".git directory", "HEAD", "working tree", "untracked files"]
```

## Preview content

**Skill explanation:** `git init` creates Git repository metadata. It does not stage files, commit files, or change file contents.  
**Preview demo:** show a non-repository folder, initialize it, then show `repository_initialized=true`, `HEAD -> main`, no commits, empty staging, and unchanged working tree.

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Initialize the current empty folder. | Single state transition. |
| Medium | Initialize the current folder with existing untracked files. | Student must understand init does not track files. |
| Hard | Initialize a new named directory from a parent workspace. | Student must target the correct directory and avoid initializing the parent/sibling. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 1 | 1 |
| Medium | 1 | 1 |
| Hard | 1 | 1 |

## Seed blueprints

### Easy cases

```yaml
difficulty: Easy
blueprint_signature: module1.init.current-empty
subtemplate_signature: current-directory-empty
solution_commands_template: ["git init"]
target_rule_template:
  repository_initialized: true
  head_branch: main
  staging_empty: true
  working_tree_matches_exact_paths: []
  rules:
    - {type: commit_count_equals, count: 0}
    - {type: operation_metadata_absent, key: last_init_directory}
parameter_pools:
  cases:
    - case_id: init-easy-empty-lab
      project: empty-lab
      expected_untracked_paths: []
      answer_anchor: initialized current empty folder; zero commits
    - case_id: init-easy-notes-shell
      project: notes-shell
      expected_untracked_paths: []
      answer_anchor: initialized current empty notes shell; zero commits
    - case_id: init-easy-sandbox
      project: sandbox
      expected_untracked_paths: []
      answer_anchor: initialized current sandbox; zero commits
```

### Medium cases

```yaml
difficulty: Medium
blueprint_signature: module1.init.current-with-untracked
subtemplate_signature: current-directory-untracked
solution_commands_template: ["git init"]
target_rule_template:
  repository_initialized: true
  head_branch: main
  staging_empty: true
  working_tree_matches_exact_paths: "{{expected_untracked_paths}}"
  rules:
    - {type: commit_count_equals, count: 0}
    - {type: working_tree_contains, paths: "{{expected_untracked_paths}}"}
parameter_pools:
  cases:
    - case_id: init-medium-docs-folder
      project: docs-folder
      initial_working_tree: {README.md: untracked, docs/intro.md: untracked}
      expected_untracked_paths: [README.md, docs/intro.md]
      answer_anchor: README.md and docs/intro.md remain untracked; zero commits
    - case_id: init-medium-web-starter
      project: web-starter
      initial_working_tree: {index.html: untracked, styles/site.css: untracked, scripts/app.js: untracked}
      expected_untracked_paths: [index.html, styles/site.css, scripts/app.js]
      answer_anchor: three starter files remain untracked; zero commits
    - case_id: init-medium-api-starter
      project: api-starter
      initial_working_tree: {README.md: untracked, api/routes.py: untracked, api/config.py: untracked}
      expected_untracked_paths: [README.md, api/routes.py, api/config.py]
      answer_anchor: API starter files remain untracked; zero commits
```

### Hard cases

```yaml
difficulty: Hard
blueprint_signature: module1.init.named-directory
subtemplate_signature: named-directory-from-parent
solution_commands_template: ["git init {{target_directory}}"]
target_rule_template:
  repository_initialized: true
  head_branch: main
  staging_empty: true
  rules:
    - {type: commit_count_equals, count: 0}
    - {type: operation_metadata_equals, key: last_init_directory, value: "{{target_directory}}"}
    - {type: operation_metadata_not_equals, key: last_init_directory, value: "."}
parameter_pools:
  cases:
    - case_id: init-hard-new-research-log
      project: parent-workspace
      target_directory: research-log
      sibling_directories: [notes, archive]
      answer_anchor: initialized research-log only; parent not initialized; zero commits
    - case_id: init-hard-new-ui-kit
      project: design-parent
      target_directory: ui-kit
      sibling_directories: [brand-assets, experiments]
      answer_anchor: initialized ui-kit only; sibling folders untouched; zero commits
    - case_id: init-hard-new-deploy-checklist
      project: ops-parent
      target_directory: deploy-checklist
      sibling_directories: [docs, scripts]
      answer_anchor: initialized deploy-checklist only; parent/siblings untouched; zero commits
```

---

# Scenario 1.2 — Clone a Remote Repository

```yaml
scenario_slug: clone-remote-repository
title: Clone a remote repository
focus: git clone
skill_focus_type: command_specific
primary_focus_commands: ["git clone"]
supporting_diagnostic_commands: ["git remote -v", "git log --oneline", "git status"]
completion_type: state_based
related_git_concepts: ["origin", "remote-tracking branch", "upstream", "branch checkout", "shallow clone"]
```

## Preview content

**Skill explanation:** `git clone` creates a local repository from an existing remote, configures `origin`, creates the selected local branch, records the matching `origin/<branch>` remote-tracking branch, checks out the remote tree, and leaves the working tree clean.
**Preview demo:** show remote fixture -> clone -> local branch and `origin/<branch>` both pointing to the cloned commit.

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Default destination, custom destination, and simple branch checkout. | Student must distinguish omitted destination from named destination and selected branch. |
| Medium | SSH custom destination, branch into folder, and shallow default clone. | Student must combine URL style, destination, branch, or depth exactly. |
| Hard | Shallow selected-branch clones and SSH custom destination variants. | More exact option order, branch refs, and metadata to verify. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 1 | 1 |
| Medium | 1 | 1 |
| Hard | 1 | 1 |

## Seed blueprints

```yaml
shared_target_rule_template:
  repository_initialized: true
  head_branch: "{{selected_branch}}"
  remote_url_matches: {origin: "{{remote_url}}"}
  branch_points_to: {"{{selected_branch}}": "{{remote_head}}"}
  remote_branch_points_to: {"{{selected_remote_branch}}": "{{remote_head}}"}
  upstream_tracking: {"{{selected_branch}}": "{{selected_remote_branch}}"}
  staging_empty: true
  working_tree_clean: true
  rules:
    - {type: operation_metadata_equals, key: last_clone_destination, value: "{{destination_folder}}"}
    - {type: operation_metadata_equals, key: last_clone_url, value: "{{remote_url}}"}
    - {type: operation_metadata_equals, key: last_clone_branch, value: "{{selected_branch}}"}
    - {type: operation_metadata_equals, key: last_clone_depth, value: "{{clone_depth}}"}
    - {type: operation_metadata_equals, key: last_clone_remote_name, value: origin}
    - {type: operation_metadata_equals, key: last_clone_default_branch, value: "{{default_branch}}"}
    - {type: operation_metadata_equals, key: last_clone_shallow, value: "{{clone_shallow}}"}
    - {type: commit_exists, commit: "{{remote_head}}"}
    - {type: commit_tree_contains, commit: "{{remote_head}}", tree: "{{remote_tree}}"}
```

### Case coverage

Each clone blueprint keeps one command in `solution_commands_template`: `["{{solution_command}}"]`.
The case pool provides a concrete supported command plus remote fixture data.

Current case categories:

| Category | Example supported solution |
|---|---|
| Default destination clone | `git clone https://example.test/training/docs-portal.git` |
| Custom destination clone | `git clone https://example.test/training/api-lab.git api-workshop` |
| SSH URL custom destination clone | `git clone git@example.test:training/analytics-lab.git analytics-worktree` |
| Specific branch clone | `git clone -b starter https://example.test/training/profile-site.git` |
| Specific branch into custom folder | `git clone --branch starter https://example.test/tools/cli-tool.git cli-starter-lab` |
| Shallow clone with `--depth 1` | `git clone --depth 1 https://example.test/frontend/css-kit.git` |
| Shallow selected branch into folder | `git clone --depth 1 -b starter https://example.test/frontend/mobile-ui.git mobile-ui-lab` |

---

# Scenario 1.3 — Staging and Committing: Basic Workflow

```yaml
scenario_slug: stage-and-commit-basic-workflow
title: Stage and commit the intended change
focus: git commit
skill_focus_type: workflow_specific
primary_focus_commands: ["git add", "git commit"]
supporting_diagnostic_commands: ["git status", "git diff", "git diff --staged"]
completion_type: state_based
related_git_concepts: ["working tree", "staging area", "commit", "branch tip"]
```

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | One intended modified file, no distractor. | Direct stage-and-commit. |
| Medium | Two intended files forming one logical change. | Student must stage a coherent multi-file snapshot. |
| Hard | Intended file(s) plus unrelated local change. | Student must preserve unrelated work outside the commit. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 2 | 3 |
| Medium | 2 | 4 |
| Hard | 2 | 5 |

## Shared target-rule template

```yaml
target_rule_template:
  head_branch: main
  latest_commit:
    branch: main
    message_contains: ["{{required_commit_message}}"]
    contains_paths: "{{target_files}}"
    excludes_paths: "{{excluded_files}}"
  staging_empty: true
  working_tree_clean_except: "{{allowed_working_tree_paths}}"
  rules:
    - {type: commit_parent_equals, branch: main, parent: "{{base_commit}}"}
    - {type: commit_tree_contains, branch: main, tree: "{{target_tree_requirements}}"}
```

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: commit-easy-form-validation
      project: form-flow
      base_commit: c1
      initial_working_tree: {src/form.js: form-validation-v2}
      target_files: [src/form.js]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {src/form.js: form-validation-v2}
      required_commit_message: Update form validation
      solution_commands: ["git add src/form.js", "git commit -m 'Update form validation'"]
      answer_anchor: commit message and changed path src/form.js
    - case_id: commit-easy-readme-setup
      project: setup-notes
      base_commit: c1
      initial_working_tree: {README.md: readme-setup-v2}
      target_files: [README.md]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {README.md: readme-setup-v2}
      required_commit_message: Clarify setup steps
      solution_commands: ["git add README.md", "git commit -m 'Clarify setup steps'"]
      answer_anchor: commit message and changed path README.md
    - case_id: commit-easy-navbar-spacing
      project: style-polish
      base_commit: c1
      initial_working_tree: {styles/navbar.css: navbar-spacing-v2}
      target_files: [styles/navbar.css]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {styles/navbar.css: navbar-spacing-v2}
      required_commit_message: Adjust navbar spacing
      solution_commands: ["git add styles/navbar.css", "git commit -m 'Adjust navbar spacing'"]
      answer_anchor: commit message and changed path styles/navbar.css
  medium_cases:
    - case_id: commit-medium-profile-card
      project: profile-card
      base_commit: c1
      initial_working_tree: {src/profile-card.js: profile-js-v2, styles/profile-card.css: profile-css-v2}
      target_files: [src/profile-card.js, styles/profile-card.css]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {src/profile-card.js: profile-js-v2, styles/profile-card.css: profile-css-v2}
      required_commit_message: Update profile card layout
      solution_commands: ["git add src/profile-card.js styles/profile-card.css", "git commit -m 'Update profile card layout'"]
      answer_anchor: commit has two profile-card paths
    - case_id: commit-medium-search-results
      project: search-view
      base_commit: c1
      initial_working_tree: {src/search.js: search-js-v2, templates/search.html: search-template-v2}
      target_files: [src/search.js, templates/search.html]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {src/search.js: search-js-v2, templates/search.html: search-template-v2}
      required_commit_message: Refine search results view
      solution_commands: ["git add src/search.js templates/search.html", "git commit -m 'Refine search results view'"]
      answer_anchor: commit has JS and template paths
    - case_id: commit-medium-export-flow
      project: export-flow
      base_commit: c1
      initial_working_tree: {src/export.py: export-code-v2, docs/export.md: export-docs-v2}
      target_files: [src/export.py, docs/export.md]
      excluded_files: []
      allowed_working_tree_paths: []
      target_tree_requirements: {src/export.py: export-code-v2, docs/export.md: export-docs-v2}
      required_commit_message: Document export flow update
      solution_commands: ["git add src/export.py docs/export.md", "git commit -m 'Document export flow update'"]
      answer_anchor: commit has code and docs paths
  hard_cases:
    - case_id: commit-hard-profile-distractor
      project: profile-card
      base_commit: c1
      initial_working_tree: {src/profile-card.js: profile-js-v3, notes/profile-ideas.md: profile-notes-draft}
      target_files: [src/profile-card.js]
      excluded_files: [notes/profile-ideas.md]
      allowed_working_tree_paths: [notes/profile-ideas.md]
      target_tree_requirements: {src/profile-card.js: profile-js-v3}
      required_commit_message: Update profile card behavior
      solution_commands: ["git add src/profile-card.js", "git commit -m 'Update profile card behavior'"]
      answer_anchor: commit includes profile-card.js; notes remain uncommitted
    - case_id: commit-hard-export-distractor
      project: export-flow
      base_commit: c1
      initial_working_tree: {src/export.py: export-code-v3, scratch/export-test-output.txt: export-output-draft}
      target_files: [src/export.py]
      excluded_files: [scratch/export-test-output.txt]
      allowed_working_tree_paths: [scratch/export-test-output.txt]
      target_tree_requirements: {src/export.py: export-code-v3}
      required_commit_message: Fix export validation
      solution_commands: ["git add src/export.py", "git commit -m 'Fix export validation'"]
      answer_anchor: commit includes export.py; scratch output remains uncommitted
    - case_id: commit-hard-search-two-targets-one-distractor
      project: search-view
      base_commit: c1
      initial_working_tree: {src/search.js: search-js-v3, templates/search.html: search-template-v3, notes/search-ranking.md: search-notes-draft}
      target_files: [src/search.js, templates/search.html]
      excluded_files: [notes/search-ranking.md]
      allowed_working_tree_paths: [notes/search-ranking.md]
      target_tree_requirements: {src/search.js: search-js-v3, templates/search.html: search-template-v3}
      required_commit_message: Refine search ranking display
      solution_commands: ["git add src/search.js templates/search.html", "git commit -m 'Refine search ranking display'"]
      answer_anchor: commit includes two target paths; notes remain uncommitted
```

---

# Scenario 1.4 — Ignoring Files with `.gitignore`

```yaml
scenario_slug: configure-gitignore-rules
title: Configure ignore rules
focus: .gitignore
skill_focus_type: concept_specific
primary_focus_commands: ["git add", "git commit"]
supporting_diagnostic_commands: ["git status", "git diff", "git diff --staged"]
completion_type: expanded_state_based
related_git_concepts: ["ignored files", "untracked files", "tracked files", "index"]
```

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Commit a provided `.gitignore`; ignored artifacts stay out. | Basic ignore rule outcome. |
| Medium | Commit `.gitignore` with multiple ecosystem patterns and visible ignored artifacts. | More patterns/files to preserve locally. |
| Hard | Stop tracking an already-tracked generated file and commit `.gitignore`. | Requires understanding that `.gitignore` does not affect already tracked files. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 2 | 4 |
| Medium | 2 | 5 |
| Hard | 3 | 6 |

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: ignore-easy-node-env
      project: node-app
      gitignore_path: .gitignore
      gitignore_token: node-ignore-v1
      ignored_paths: [node_modules/pkg/index.js, .env]
      required_commit_message: Add Node ignore rules
      target_files: [.gitignore]
      excluded_files: [node_modules/pkg/index.js, .env]
      solution_commands: ["git add .gitignore", "git commit -m 'Add Node ignore rules'"]
      answer_anchor: commit contains .gitignore token node-ignore-v1; excludes node_modules and .env
    - case_id: ignore-easy-python-cache
      project: python-api
      gitignore_path: .gitignore
      gitignore_token: python-ignore-v1
      ignored_paths: [__pycache__/app.cpython.pyc, .env]
      required_commit_message: Add Python ignore rules
      target_files: [.gitignore]
      excluded_files: [__pycache__/app.cpython.pyc, .env]
      solution_commands: ["git add .gitignore", "git commit -m 'Add Python ignore rules'"]
      answer_anchor: commit contains .gitignore token python-ignore-v1; excludes pycache and .env
    - case_id: ignore-easy-web-build
      project: static-site
      gitignore_path: .gitignore
      gitignore_token: web-ignore-v1
      ignored_paths: [dist/site.js, dist/site.css]
      required_commit_message: Add web build ignore rules
      target_files: [.gitignore]
      excluded_files: [dist/site.js, dist/site.css]
      solution_commands: ["git add .gitignore", "git commit -m 'Add web build ignore rules'"]
      answer_anchor: commit contains .gitignore token web-ignore-v1; excludes dist outputs
  medium_cases:
    - case_id: ignore-medium-node-logs-build
      project: node-dashboard
      gitignore_token: node-ignore-v2
      ignored_paths: [node_modules/lib.js, dist/app.js, logs/debug.log, .env.local]
      required_commit_message: Ignore Node dependencies and build output
      target_files: [.gitignore]
      excluded_files: [node_modules/lib.js, dist/app.js, logs/debug.log, .env.local]
      solution_commands: ["git add .gitignore", "git commit -m 'Ignore Node dependencies and build output'"]
      answer_anchor: excludes four ignored artifact paths
    - case_id: ignore-medium-python-venv-cache
      project: data-tools
      gitignore_token: python-ignore-v2
      ignored_paths: [.venv/pyvenv.cfg, __pycache__/clean.cpython.pyc, output/report.csv]
      required_commit_message: Ignore Python environment artifacts
      target_files: [.gitignore]
      excluded_files: [.venv/pyvenv.cfg, __pycache__/clean.cpython.pyc, output/report.csv]
      solution_commands: ["git add .gitignore", "git commit -m 'Ignore Python environment artifacts'"]
      answer_anchor: excludes venv, cache, and output paths
    - case_id: ignore-medium-java-target
      project: java-service
      gitignore_token: java-ignore-v1
      ignored_paths: [target/classes/App.class, target/app.jar, logs/server.log]
      required_commit_message: Ignore Java build artifacts
      target_files: [.gitignore]
      excluded_files: [target/classes/App.class, target/app.jar, logs/server.log]
      solution_commands: ["git add .gitignore", "git commit -m 'Ignore Java build artifacts'"]
      answer_anchor: excludes target and log paths
  hard_cases:
    - case_id: ignore-hard-untrack-env
      project: backend-service
      gitignore_token: service-ignore-v3
      tracked_generated_path: .env
      ignored_paths: [.env, logs/server.log]
      target_files: [.gitignore]
      excluded_files: [.env, logs/server.log]
      required_commit_message: Stop tracking local environment files
      solution_commands: ["git rm --cached .env", "git add .gitignore", "git commit -m 'Stop tracking local environment files'"]
      answer_anchor: .env removed from committed tree but remains local/ignored; .gitignore committed
    - case_id: ignore-hard-untrack-dist
      project: frontend-bundle
      gitignore_token: frontend-ignore-v3
      tracked_generated_path: dist/app.js
      ignored_paths: [dist/app.js, dist/app.css]
      target_files: [.gitignore]
      excluded_files: [dist/app.js, dist/app.css]
      required_commit_message: Stop tracking build outputs
      solution_commands: ["git rm --cached dist/app.js", "git add .gitignore", "git commit -m 'Stop tracking build outputs'"]
      answer_anchor: dist/app.js removed from commit tree; build outputs remain local/ignored
    - case_id: ignore-hard-untrack-pycache
      project: script-runner
      gitignore_token: pycache-ignore-v3
      tracked_generated_path: __pycache__/runner.cpython.pyc
      ignored_paths: [__pycache__/runner.cpython.pyc, .pytest_cache/v/cache]
      target_files: [.gitignore]
      excluded_files: [__pycache__/runner.cpython.pyc, .pytest_cache/v/cache]
      required_commit_message: Stop tracking Python cache files
      solution_commands: ["git rm --cached __pycache__/runner.cpython.pyc", "git add .gitignore", "git commit -m 'Stop tracking Python cache files'"]
      answer_anchor: tracked pycache removed from future tree; .gitignore committed
```

---

# Scenario 1.5 — Partial Staging and `git add -p`

```yaml
scenario_slug: partial-staging-add-p
title: Stage selected hunks
focus: git add -p
skill_focus_type: command_specific
primary_focus_commands: ["git add -p", "git commit"]
supporting_diagnostic_commands: ["git status", "git diff", "git diff --staged"]
completion_type: expanded_state_based
related_git_concepts: ["hunks", "partial staging", "index", "working tree leftovers"]
```

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | One file has two hunks; commit one named hunk. | Introduces partial staging. |
| Medium | One file has multiple hunks plus an unrelated file. | Student must leave unrelated work untouched. |
| Hard | Two files contain mixed hunks; commit only the requested logical change. | Requires content-token reasoning, not path-only staging. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 2 | 4 |
| Medium | 2 | 5 |
| Hard | 2 | 6 |

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: partial-easy-auth-validation
      project: auth-module
      target_file: src/auth.py
      target_hunks: [auth-validation-hunk]
      leftover_hunks: [auth-refactor-hunk]
      required_commit_message: Isolate auth validation
      solution_commands: ["git add -p src/auth.py", "git commit -m 'Isolate auth validation'"]
      answer_anchor: commit contains auth-validation-hunk; working tree keeps auth-refactor-hunk
    - case_id: partial-easy-search-ranking
      project: search-module
      target_file: src/search.py
      target_hunks: [search-ranking-hunk]
      leftover_hunks: [search-cleanup-hunk]
      required_commit_message: Isolate search ranking
      solution_commands: ["git add -p src/search.py", "git commit -m 'Isolate search ranking'"]
      answer_anchor: commit contains search-ranking-hunk; working tree keeps search-cleanup-hunk
    - case_id: partial-easy-export-format
      project: export-module
      target_file: src/export.py
      target_hunks: [export-format-hunk]
      leftover_hunks: [export-logging-hunk]
      required_commit_message: Isolate export formatting
      solution_commands: ["git add -p src/export.py", "git commit -m 'Isolate export formatting'"]
      answer_anchor: commit contains export-format-hunk; working tree keeps export-logging-hunk
  medium_cases:
    - case_id: partial-medium-profile-validation
      project: profile-editor
      target_file: src/profile.py
      target_hunks: [profile-validation-hunk]
      leftover_hunks: [profile-copy-hunk, profile-cleanup-hunk]
      unrelated_files: [notes/profile-todo.md]
      required_commit_message: Commit profile validation only
      solution_commands: ["git add -p src/profile.py", "git commit -m 'Commit profile validation only'"]
      answer_anchor: validation hunk committed; two hunks and notes remain uncommitted
    - case_id: partial-medium-payment-rounding
      project: payment-flow
      target_file: src/payment.py
      target_hunks: [payment-rounding-hunk]
      leftover_hunks: [payment-logging-hunk, payment-comment-hunk]
      unrelated_files: [tmp/payment-scratch.txt]
      required_commit_message: Commit payment rounding fix
      solution_commands: ["git add -p src/payment.py", "git commit -m 'Commit payment rounding fix'"]
      answer_anchor: rounding hunk committed; logging/comment hunks remain
    - case_id: partial-medium-dashboard-filter
      project: dashboard
      target_file: src/dashboard.js
      target_hunks: [dashboard-filter-hunk]
      leftover_hunks: [dashboard-theme-hunk, dashboard-console-hunk]
      unrelated_files: [notes/dashboard-ideas.md]
      required_commit_message: Commit dashboard filter change
      solution_commands: ["git add -p src/dashboard.js", "git commit -m 'Commit dashboard filter change'"]
      answer_anchor: filter hunk committed; theme/console hunks remain
  hard_cases:
    - case_id: partial-hard-auth-cross-file
      project: auth-module
      target_files: [src/auth.py, tests/test_auth.py]
      target_hunks: [auth-validation-hunk, auth-validation-test-hunk]
      leftover_hunks: [auth-refactor-hunk, auth-test-cleanup-hunk]
      unrelated_files: [notes/auth-debug.md]
      required_commit_message: Commit auth validation path
      solution_commands: ["git add -p src/auth.py", "git add -p tests/test_auth.py", "git commit -m 'Commit auth validation path'"]
      answer_anchor: two validation hunks committed across files; refactor/test cleanup and notes remain
    - case_id: partial-hard-search-cross-file
      project: search-module
      target_files: [src/search.py, tests/test_search.py]
      target_hunks: [search-ranking-hunk, search-ranking-test-hunk]
      leftover_hunks: [search-cleanup-hunk, search-test-fixture-hunk]
      unrelated_files: [tmp/search-output.txt]
      required_commit_message: Commit search ranking path
      solution_commands: ["git add -p src/search.py", "git add -p tests/test_search.py", "git commit -m 'Commit search ranking path'"]
      answer_anchor: ranking hunks committed across code/test; cleanup/fixture and tmp remain
    - case_id: partial-hard-export-cross-file
      project: export-module
      target_files: [src/export.py, tests/test_export.py]
      target_hunks: [export-format-hunk, export-format-test-hunk]
      leftover_hunks: [export-logging-hunk, export-test-cleanup-hunk]
      unrelated_files: [notes/export-followup.md]
      required_commit_message: Commit export formatting path
      solution_commands: ["git add -p src/export.py", "git add -p tests/test_export.py", "git commit -m 'Commit export formatting path'"]
      answer_anchor: export formatting hunks committed; logging/test cleanup and notes remain
```

Target rules for this scenario must check hunk/content tokens, not only paths.

---

# Scenario 1.6 — Amending Commits

```yaml
scenario_slug: amend-latest-commit
title: Amend the latest commit
focus: git commit --amend
skill_focus_type: command_specific
primary_focus_commands: ["git commit --amend"]
supporting_diagnostic_commands: ["git status", "git log --oneline", "git diff", "git diff --staged"]
completion_type: expanded_state_based
related_git_concepts: ["latest commit", "amend", "branch tip replacement", "commit message"]
```

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Fix only the latest commit message. | No file staging required. |
| Medium | Add missing staged content while keeping the message. | Student must stage the missing file then amend. |
| Hard | Fix both message and missing content. | Student must repair both commit metadata and tree without creating an extra commit. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 1 | 2 |
| Medium | 2 | 4 |
| Hard | 2 | 5 |

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: amend-easy-login-copy-message
      project: login-copy
      old_tip: c2
      old_message: Update text
      corrected_message: Clarify login copy
      target_files_already_in_tip: [src/login.js]
      solution_commands: ["git commit --amend -m 'Clarify login copy'"]
      answer_anchor: branch tip is amended commit with message Clarify login copy; no extra commit
    - case_id: amend-easy-readme-message
      project: setup-docs
      old_tip: c2
      old_message: Update README
      corrected_message: Clarify setup requirements
      target_files_already_in_tip: [README.md]
      solution_commands: ["git commit --amend -m 'Clarify setup requirements'"]
      answer_anchor: amended tip message Clarify setup requirements; same tree
    - case_id: amend-easy-navbar-message
      project: style-polish
      old_tip: c2
      old_message: CSS updates
      corrected_message: Adjust navbar spacing
      target_files_already_in_tip: [styles/navbar.css]
      solution_commands: ["git commit --amend -m 'Adjust navbar spacing'"]
      answer_anchor: amended tip message Adjust navbar spacing; same tree
  medium_cases:
    - case_id: amend-medium-profile-missing-css
      project: profile-card
      old_tip: c2
      kept_message: Update profile card layout
      missing_working_tree: {styles/profile-card.css: profile-css-v2}
      target_files_final: [src/profile-card.js, styles/profile-card.css]
      solution_commands: ["git add styles/profile-card.css", "git commit --amend -m 'Update profile card layout'"]
      answer_anchor: amended tip includes missing CSS without creating new commit
    - case_id: amend-medium-export-doc
      project: export-flow
      old_tip: c2
      kept_message: Document export flow update
      missing_working_tree: {docs/export.md: export-docs-v2}
      target_files_final: [src/export.py, docs/export.md]
      solution_commands: ["git add docs/export.md", "git commit --amend -m 'Document export flow update'"]
      answer_anchor: amended tip includes export docs
    - case_id: amend-medium-search-template
      project: search-view
      old_tip: c2
      kept_message: Refine search results view
      missing_working_tree: {templates/search.html: search-template-v2}
      target_files_final: [src/search.js, templates/search.html]
      solution_commands: ["git add templates/search.html", "git commit --amend -m 'Refine search results view'"]
      answer_anchor: amended tip includes search template
  hard_cases:
    - case_id: amend-hard-profile-message-and-css
      project: profile-card
      old_tip: c2
      old_message: Update profile stuff
      corrected_message: Update profile card layout
      missing_working_tree: {styles/profile-card.css: profile-css-v3}
      target_files_final: [src/profile-card.js, styles/profile-card.css]
      solution_commands: ["git add styles/profile-card.css", "git commit --amend -m 'Update profile card layout'"]
      answer_anchor: amended tip has corrected message and missing CSS; old tip replaced
    - case_id: amend-hard-auth-message-and-test
      project: auth-module
      old_tip: c2
      old_message: Auth changes
      corrected_message: Add auth validation coverage
      missing_working_tree: {tests/test_auth.py: auth-test-v2}
      target_files_final: [src/auth.py, tests/test_auth.py]
      solution_commands: ["git add tests/test_auth.py", "git commit --amend -m 'Add auth validation coverage'"]
      answer_anchor: amended tip has corrected message and test path; no extra child commit
    - case_id: amend-hard-export-message-and-doc
      project: export-flow
      old_tip: c2
      old_message: Export update
      corrected_message: Document export validation behavior
      missing_working_tree: {docs/export.md: export-docs-v3}
      target_files_final: [src/export.py, docs/export.md]
      solution_commands: ["git add docs/export.md", "git commit --amend -m 'Document export validation behavior'"]
      answer_anchor: amended tip has corrected message and docs; old tip replaced
```

Target rules must prove amend behavior through branch-tip replacement metadata or equivalent history-shape checks.

---

# Scenario 1.7 — Unstaging and Discarding Changes

```yaml
scenario_slug: unstage-and-discard-changes
title: Unstage and discard safely
focus: git restore
skill_focus_type: command_specific
primary_focus_commands: ["git restore"]
supporting_diagnostic_commands: ["git status", "git diff", "git diff --staged"]
completion_type: state_based
related_git_concepts: ["index", "working tree", "unstage", "discard"]
```

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Unstage one file while keeping its working-tree change. | Separates index from working tree. |
| Medium | Unstage one file and discard another working-tree change. | Requires two different restore intents. |
| Hard | Multiple staged/working paths; preserve one, discard one, leave branch/history unchanged. | Requires precise state cleanup without commits. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 1 | 2 |
| Medium | 2 | 4 |
| Hard | 2 | 5 |

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: restore-easy-unstage-app
      project: cleanup-lab
      initial_staging: {src/app.py: app-change-v2}
      keep_working_tree: [src/app.py]
      discard_paths: []
      solution_commands: ["git restore --staged src/app.py"]
      answer_anchor: src/app.py moves from staging to working_tree; no commit created
    - case_id: restore-easy-unstage-guide
      project: docs-lab
      initial_staging: {docs/guide.md: guide-change-v2}
      keep_working_tree: [docs/guide.md]
      discard_paths: []
      solution_commands: ["git restore --staged docs/guide.md"]
      answer_anchor: docs/guide.md unstaged and preserved
    - case_id: restore-easy-unstage-css
      project: style-lab
      initial_staging: {styles/site.css: css-change-v2}
      keep_working_tree: [styles/site.css]
      discard_paths: []
      solution_commands: ["git restore --staged styles/site.css"]
      answer_anchor: styles/site.css unstaged and preserved
  medium_cases:
    - case_id: restore-medium-app-debug
      project: cleanup-lab
      initial_staging: {src/app.py: app-change-v2}
      initial_working_tree: {debug.log: debug-draft}
      keep_working_tree: [src/app.py]
      discard_paths: [debug.log]
      solution_commands: ["git restore --staged src/app.py", "git restore debug.log"]
      answer_anchor: app.py preserved as working change; debug.log discarded
    - case_id: restore-medium-docs-scratch
      project: docs-lab
      initial_staging: {docs/guide.md: guide-change-v2}
      initial_working_tree: {tmp/scratch.txt: scratch-draft}
      keep_working_tree: [docs/guide.md]
      discard_paths: [tmp/scratch.txt]
      solution_commands: ["git restore --staged docs/guide.md", "git restore tmp/scratch.txt"]
      answer_anchor: guide preserved; scratch discarded
    - case_id: restore-medium-css-build
      project: style-lab
      initial_staging: {styles/site.css: css-change-v2}
      initial_working_tree: {dist/site.css: dist-generated}
      keep_working_tree: [styles/site.css]
      discard_paths: [dist/site.css]
      solution_commands: ["git restore --staged styles/site.css", "git restore dist/site.css"]
      answer_anchor: source CSS preserved; generated dist discarded
  hard_cases:
    - case_id: restore-hard-mixed-profile
      project: profile-card
      initial_staging: {src/profile-card.js: profile-js-v2, notes/profile-ideas.md: notes-draft}
      initial_working_tree: {debug/profile.log: debug-draft}
      keep_working_tree: [src/profile-card.js]
      discard_paths: [debug/profile.log]
      staging_must_exclude: [src/profile-card.js, notes/profile-ideas.md]
      solution_commands: ["git restore --staged src/profile-card.js notes/profile-ideas.md", "git restore debug/profile.log"]
      answer_anchor: all staging cleared; profile-card.js preserved; debug log discarded; no commit
    - case_id: restore-hard-mixed-export
      project: export-flow
      initial_staging: {src/export.py: export-code-v2, notes/export-plan.md: notes-draft}
      initial_working_tree: {tmp/export-output.txt: generated-output}
      keep_working_tree: [src/export.py]
      discard_paths: [tmp/export-output.txt]
      staging_must_exclude: [src/export.py, notes/export-plan.md]
      solution_commands: ["git restore --staged src/export.py notes/export-plan.md", "git restore tmp/export-output.txt"]
      answer_anchor: export.py preserved; notes unstaged; generated output discarded; no commit
    - case_id: restore-hard-mixed-search
      project: search-view
      initial_staging: {src/search.js: search-js-v2, notes/search.md: notes-draft}
      initial_working_tree: {debug/search.log: search-debug}
      keep_working_tree: [src/search.js]
      discard_paths: [debug/search.log]
      staging_must_exclude: [src/search.js, notes/search.md]
      solution_commands: ["git restore --staged src/search.js notes/search.md", "git restore debug/search.log"]
      answer_anchor: search.js preserved; notes unstaged; debug log discarded; no commit
```

---

# Scenario 1.8 — Reading Repository Status and History

```yaml
scenario_slug: read-repository-status-and-history
title: Read repository status and history
focus: diagnostic commands
skill_focus_type: concept_specific
primary_focus_commands: ["git status"]
supporting_diagnostic_commands: ["git status", "git log --oneline", "git diff", "git diff --staged", "git show"]
playable_difficulties: []
related_git_concepts: ["status interpretation", "history interpretation", "diff interpretation"]
```

## Preview content

Lesson 1.8 is lesson overview plus Skill Focus Preview content. It should not seed Easy/Medium/Hard playable sessions because there is no state-changing target.

The command preview should cover:

```yaml
preview_examples:
  easy_cases:
    - case_id: inspect-easy-status-staged
      project: status-lab
      required_commands: ["git status"]
      diagnostic_question: Which file is staged for the next commit?
      must_identify: [staged_paths]
      expected_answer: {staged_paths: [src/app.py]}
      answer_anchor: staged path src/app.py
    - case_id: inspect-easy-log-latest
      project: history-lab
      required_commands: ["git log --oneline"]
      diagnostic_question: What is the latest commit message?
      must_identify: [commit_message]
      expected_answer: {commit_message: Add profile card}
      answer_anchor: latest commit message Add profile card
    - case_id: inspect-easy-diff-working
      project: diff-lab
      required_commands: ["git diff"]
      diagnostic_question: Which file has unstaged changes?
      must_identify: [unstaged_paths]
      expected_answer: {unstaged_paths: [README.md]}
      answer_anchor: unstaged path README.md
  medium_cases:
    - case_id: inspect-medium-status-mixed
      project: mixed-status-lab
      required_commands: ["git status"]
      diagnostic_question: Identify the staged, unstaged, and untracked paths.
      must_identify: [staged_paths, unstaged_paths, untracked_paths]
      expected_answer: {staged_paths: [src/app.py], unstaged_paths: [README.md], untracked_paths: [notes/todo.md]}
      answer_anchor: three distinct file areas
    - case_id: inspect-medium-staged-diff
      project: staged-diff-lab
      required_commands: ["git diff --staged"]
      diagnostic_question: Which path is staged for the next snapshot?
      must_identify: [staged_diff_paths]
      expected_answer: {staged_diff_paths: [styles/site.css]}
      answer_anchor: staged diff path styles/site.css
    - case_id: inspect-medium-branch-history
      project: branch-history-lab
      required_commands: ["git log --oneline"]
      diagnostic_question: Which commit is currently at HEAD?
      must_identify: [latest_commit, commit_message]
      expected_answer: {latest_commit: c3, commit_message: Refine search results view}
      answer_anchor: latest commit c3 with specific message
  hard_cases:
    - case_id: inspect-hard-full-state
      project: full-state-lab
      required_commands: ["git status", "git diff --staged", "git log --oneline"]
      diagnostic_question: Identify the current branch, staged file, unstaged file, and latest commit message.
      must_identify: [head_branch, staged_paths, unstaged_paths, commit_message]
      expected_answer: {head_branch: main, staged_paths: [src/export.py], unstaged_paths: [docs/export.md], commit_message: Add export starter}
      answer_anchor: branch + staged + unstaged + latest message
    - case_id: inspect-hard-conflict-state
      project: conflict-read-lab
      required_commands: ["git status", "git diff"]
      diagnostic_question: Which path is conflicted and which branch is active?
      must_identify: [head_branch, conflicted_paths]
      expected_answer: {head_branch: main, conflicted_paths: [src/app.py]}
      answer_anchor: active branch main and conflict path src/app.py
    - case_id: inspect-hard-history-and-diff
      project: history-diff-lab
      required_commands: ["git log --oneline", "git diff HEAD"]
      diagnostic_question: Identify the latest commit and all paths changed since HEAD.
      must_identify: [latest_commit, commit_message, diff_target]
      expected_answer: {latest_commit: c4, commit_message: Add dashboard shell, diff_target: {unstaged: [src/dashboard.js], staged: [styles/dashboard.css], conflicted: []}}
      answer_anchor: latest commit c4 plus staged/unstaged diff split
```

Students apply these diagnostic commands inside the normal state-based scenarios, where diagnostic commands are logged as non-counted and excluded from CAR.

---

# Scenario 1.9 — Module 1 Review and Practice

```yaml
scenario_slug: module1-integrated-local-workflow
title: Complete a focused local workflow
focus: local repository workflow
skill_focus_type: workflow_specific
primary_focus_commands: ["git add", "git commit"]
supporting_diagnostic_commands: ["git status", "git diff", "git diff --staged", "git log --oneline"]
completion_type: expanded_state_based
related_git_concepts: ["focused snapshot", "ignore rules", "partial staging", "amend", "clean final state"]
```

## Stable scenario definition

The integrated review scenario must remain one stable learning goal:

> Prepare one focused local snapshot while leaving unrelated local work out of that snapshot.

Approved subtemplates may combine previous skills, but they must not become unrelated tasks like clone-only, branch-only, or merge-only.

## Difficulty progression

| Difficulty | Definition | Why harder |
|---|---|---|
| Easy | Clean focused commit with one target file and one ignored artifact. | Review of staging/commit/ignore basics. |
| Medium | Focused commit with `.gitignore` plus excluded local note/output. | More file classification. |
| Hard | Focused snapshot using partial staging or amend repair. | Requires deep state reasoning from prior scenarios. |

## Command policies

| Difficulty | min_counted | max_counted |
|---|---:|---:|
| Easy | 3 | 6 |
| Medium | 3 | 7 |
| Hard | 3 | 8 |

## Authored cases

```yaml
parameter_pools:
  easy_cases:
    - case_id: review-easy-docs-ignore
      subtemplate: clean-commit-with-ignore
      project: docs-portal
      target_files: [docs/intro.md, .gitignore]
      ignored_paths: [dist/site.html]
      excluded_files: [dist/site.html]
      required_commit_message: Prepare docs portal intro
      solution_commands: ["git add docs/intro.md .gitignore", "git commit -m 'Prepare docs portal intro'"]
      answer_anchor: commit contains docs/intro.md + .gitignore; excludes dist/site.html
    - case_id: review-easy-profile-ignore
      subtemplate: clean-commit-with-ignore
      project: profile-site
      target_files: [src/profile-card.js, .gitignore]
      ignored_paths: [dist/profile-card.js]
      excluded_files: [dist/profile-card.js]
      required_commit_message: Prepare profile card update
      solution_commands: ["git add src/profile-card.js .gitignore", "git commit -m 'Prepare profile card update'"]
      answer_anchor: commit contains profile-card.js + .gitignore; excludes dist artifact
    - case_id: review-easy-export-ignore
      subtemplate: clean-commit-with-ignore
      project: export-flow
      target_files: [src/export.py, .gitignore]
      ignored_paths: [output/export.csv]
      excluded_files: [output/export.csv]
      required_commit_message: Prepare export workflow update
      solution_commands: ["git add src/export.py .gitignore", "git commit -m 'Prepare export workflow update'"]
      answer_anchor: commit contains export.py + .gitignore; excludes output CSV
  medium_cases:
    - case_id: review-medium-profile-with-note
      subtemplate: focused-commit-with-leftover
      project: profile-card
      target_files: [src/profile-card.js, styles/profile-card.css, .gitignore]
      excluded_files: [notes/profile-ideas.md, dist/profile-card.js]
      allowed_working_tree_paths: [notes/profile-ideas.md]
      required_commit_message: Finalize profile card update
      solution_commands: ["git add src/profile-card.js styles/profile-card.css .gitignore", "git commit -m 'Finalize profile card update'"]
      answer_anchor: commit has two source files + .gitignore; note remains; dist ignored
    - case_id: review-medium-search-with-output
      subtemplate: focused-commit-with-leftover
      project: search-view
      target_files: [src/search.js, templates/search.html, .gitignore]
      excluded_files: [notes/search-ranking.md, output/search-results.json]
      allowed_working_tree_paths: [notes/search-ranking.md]
      required_commit_message: Finalize search results update
      solution_commands: ["git add src/search.js templates/search.html .gitignore", "git commit -m 'Finalize search results update'"]
      answer_anchor: source/template committed; note remains; output ignored
    - case_id: review-medium-export-with-note
      subtemplate: focused-commit-with-leftover
      project: export-flow
      target_files: [src/export.py, docs/export.md, .gitignore]
      excluded_files: [notes/export-plan.md, output/export.csv]
      allowed_working_tree_paths: [notes/export-plan.md]
      required_commit_message: Finalize export documentation update
      solution_commands: ["git add src/export.py docs/export.md .gitignore", "git commit -m 'Finalize export documentation update'"]
      answer_anchor: code/docs/.gitignore committed; note remains; output ignored
  hard_cases:
    - case_id: review-hard-auth-partial
      subtemplate: partial-staging-review
      project: auth-module
      target_files: [src/auth.py, tests/test_auth.py]
      target_hunks: [auth-validation-hunk, auth-validation-test-hunk]
      leftover_hunks: [auth-refactor-hunk, auth-test-cleanup-hunk]
      excluded_files: [notes/auth-debug.md]
      allowed_working_tree_paths: [src/auth.py, tests/test_auth.py, notes/auth-debug.md]
      required_commit_message: Finalize auth validation change
      solution_commands: ["git add -p src/auth.py", "git add -p tests/test_auth.py", "git commit -m 'Finalize auth validation change'"]
      answer_anchor: only validation hunks committed; leftovers and notes remain
    - case_id: review-hard-export-amend
      subtemplate: amend-review
      project: export-flow
      old_tip: c2
      old_message: Export update
      corrected_message: Finalize export validation behavior
      missing_working_tree: {docs/export.md: export-docs-final}
      target_files_final: [src/export.py, docs/export.md]
      required_commit_message: Finalize export validation behavior
      solution_commands: ["git add docs/export.md", "git commit --amend -m 'Finalize export validation behavior'"]
      answer_anchor: branch tip is amended commit with corrected message and docs; no extra commit
    - case_id: review-hard-search-partial
      subtemplate: partial-staging-review
      project: search-view
      target_files: [src/search.js, tests/test_search.js]
      target_hunks: [search-ranking-hunk, search-ranking-test-hunk]
      leftover_hunks: [search-theme-hunk, search-fixture-cleanup-hunk]
      excluded_files: [tmp/search-output.json]
      allowed_working_tree_paths: [src/search.js, tests/test_search.js, tmp/search-output.json]
      required_commit_message: Finalize search ranking behavior
      solution_commands: ["git add -p src/search.js", "git add -p tests/test_search.js", "git commit -m 'Finalize search ranking behavior'"]
      answer_anchor: ranking hunks committed; theme/fixture/tmp leftovers remain
```

---

## 4. Seeding acceptance checklist

Before publishing the seed, verify every generated variant satisfies these checks:

```text
[ ] Same scenario skill focus as the curriculum row.
[ ] Parameter context is authored, not random.
[ ] Expected-state answer differs from the other cases.
[ ] Target rule checks exact state anchors, not only broad clean/staged flags.
[ ] Student context shows every exact value checked by target rule.
[ ] Solution commands are internal only.
[ ] Generated target state satisfies target rule.
[ ] Expected-state diagram is generated from target_state.
[ ] Retry after fail/abandon/quit selects a different case whenever possible.
[ ] Review mode reuses the historical generated variant and does not regenerate unexpectedly.
```

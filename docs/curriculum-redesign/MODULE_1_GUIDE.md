# Module 1 — Scenario Design Guide

**Status: Implemented — seed live, context strings added, answer key written**
**Last updated: 2026-05-29**

---

## Module Overview

**Title:** Local Repository Foundations  
**Chapters:** 2–3  
**Lessons:** 9  
**Target students:** BSIT 3rd-year, CIT-U — prior basic Git exposure assumed

---

## SO Mapping

Source of truth: *GIT it! Capstone 2 Presentation Content Guide*, Slide 8.

### Instructional SOs — redesign scope

These six SOs define the instructional content of Module 1. Every redesigned scenario
must trace back to one of these.

| SO | Approved Description | UI Lesson | KPI |
|----|----------------------|-----------|-----|
| SO 1.1 | Initializing Repositories | Lesson 1 — `initializing-a-local-repository` | CAR ≥ 70% |
| SO 1.2 | Cloning Remote Repositories | Lesson 2 — `clone-remote-repository` | CAR ≥ 70% |
| SO 1.3 | Staging and Committing | Lesson 3 — `stage-and-commit-basic-workflow` | CAR ≥ 70% |
| SO 1.4 | Partial Staging | Lesson 5 — `partial-staging-add-p` | CAR ≥ 70% |
| SO 1.5 | Amending Commits | Lesson 6 — `amend-latest-commit` | CAR ≥ 70% |
| SO 1.6 | Unstaging and Discarding Changes | Lesson 7 — `unstage-and-discard-changes` | CAR ≥ 70% |

### KPI SOs — measurement only, not instructional objectives

These two SOs are performance indicators reported on the dashboard. They are measured
across the six instructional lessons above. They do not define separate lessons and
do not drive scenario redesign.

| SO | Description | KPI | How it is measured |
|----|-------------|-----|--------------------|
| SO 1.7 | Independent Local Repository Management | HLCR ≥ 70% | Aggregated Hard-session completion rate across SO 1.1–1.6 lessons, plus Lesson 8 (integration) |
| SO 1.8 | Efficient Repository-State Reasoning | ARC ≤ 2 | Average retry count across all Module 1 sessions |

### UI structure

The seed's internal sort order does not match the displayed lesson numbers in the UI.
The Guided Preview card appears above the numbered lessons and is not counted as Lesson 1.

| UI display | Seed sort order | Slug | SO | Redesign |
|-----------|-----------------|------|----|---------|
| Guided Preview (not numbered) | 1 | `inspect-repository-state` | ⛔ Not redesigned — no difficulties, no scenarios. Content page only. Leave as-is. | — |
| Lesson 1 | 2 | `initializing-a-local-repository` | SO 1.1 | ✅ |
| Lesson 2 | 3 | `cloning-a-remote-repository` | SO 1.2 | ✅ |
| Lesson 3 | 4 | `stage-and-commit-basic-workflow` | SO 1.3 | ✅ |
| Lesson 4 | 5 | `ignoring-files-with-gitignore` | ⚠️ Flagged — no approved SO. Leave as-is. | — |
| Lesson 5 | 6 | `partial-staging-add-p` | SO 1.4 | ✅ |
| Lesson 6 | 7 | `amend-latest-commit` | SO 1.5 | ✅ |
| Lesson 7 | 8 | `unstage-and-discard-changes` | SO 1.6 | ✅ |
| Lesson 8 | 9 | `module-1-review-and-practice` | Integration (HLCR vehicle) | ✅ |

**Note on `git config`:** Absent from Module 1 and the approved proposal. Intentional.
Students are expected to have prior Git exposure (BSIT 3rd-year).
Module 0 Orientation covers `git config` as prerequisite setup.
This is a prior-knowledge assumption, not a curriculum gap.

---

## Curriculum Assumptions

| Item | Decision |
|------|----------|
| `git config` | Prior knowledge — not introduced in Module 1 |
| `.gitignore` (Lesson 4) | ⚠️ Flagged — no approved instructional SO. Retain existing seed unchanged. |
| `git add .` | Valid counted action — introduced in Lesson 3 (SO 1.3), usable in variants |
| `git commit --amend` | Lesson 6 (SO 1.5) — safe-only (pre-push) scope |
| Guided Preview (diagnostic) | ⛔ Not redesigned — `difficulties={}`, no playable sessions exist or should be added |
| Lesson 8 (integration) | ✅ Redesigned — multi-SO capstone, HLCR measurement vehicle; scenarios use SO 1.1–1.6 skills only |

---

## Pool Sizing Requirements

Applies to the six instructional SO lessons and Lesson 8 (integration).
The Guided Preview (no difficulties) and Lesson 4 (flagged) are excluded from pool sizing.

| UI Lesson | SO | Easy req. | Easy pool | Medium req. | Medium pool | Hard req. | Hard pool |
|-----------|-----|-----------|-----------|-------------|-------------|-----------|-----------|
| Lesson 1 — Init | SO 1.1 | 1 | ≥ 3 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 2 — Clone | SO 1.2 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 3 — Commit | SO 1.3 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 5 — Partial | SO 1.4 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 6 — Amend | SO 1.5 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 7 — Restore | SO 1.6 | 3 | ≥ 5 | 2 | ≥ 4 | 2 | ≥ 4 |
| Lesson 8 — Integration | Multi-SO | 3 | ≥ 5 | 2 | ≥ 4 | 3 | ≥ 5 |

---

## Command Coverage Matrix

UI lesson numbers are used throughout. Counted action commands are the primary
skill of each instructional SO. Diagnostic commands are non-counted in all sessions.

| Command | UI Lesson | SO | Counted? |
|---------|-----------|-----|---------|
| `git init` | Lesson 1 | SO 1.1 | Yes |
| `git init <dir>` | Lesson 1 | SO 1.1 | Yes |
| `git clone <url>` | Lesson 2 | SO 1.2 | Yes |
| `git clone <url> <dir>` | Lesson 2 | SO 1.2 | Yes |
| `git clone -b <branch> <url>` | Lesson 2 | SO 1.2 | Yes |
| `git clone --depth <n> <url>` | Lesson 2 | SO 1.2 | Yes |
| `git add <file>` | Lesson 3 | SO 1.3 | Yes |
| `git add .` | Lesson 3 | SO 1.3 | Yes |
| `git add <dir>/` | Lesson 3 | SO 1.3 | Yes |
| `git commit -m "msg"` | Lesson 3 | SO 1.3 | Yes |
| `git add .gitignore` | Lesson 4 | ⚠️ Flagged | Yes |
| `git rm --cached <file>` | Lesson 4 | ⚠️ Flagged | Yes |
| `git add -p` | Lesson 5 | SO 1.4 | Yes |
| `git restore --staged <file>` | Lesson 5 / 7 | SO 1.4 / SO 1.6 | Yes |
| `git commit --amend -m "msg"` | Lesson 6 | SO 1.5 | Yes |
| `git commit --amend --no-edit` | Lesson 6 | SO 1.5 | Yes |
| `git restore <file>` | Lesson 7 | SO 1.6 | Yes |
| `git status` | All lessons | Non-counted diagnostic | No |
| `git log` | All lessons | Non-counted diagnostic | No |
| `git log --oneline` | All lessons | Non-counted diagnostic | No |
| `git diff` | All lessons | Non-counted diagnostic | No |
| `git diff --staged` | All lessons | Non-counted diagnostic | No |
| `git remote -v` | Lesson 2 | Non-counted diagnostic | No |

---

## Lesson 1 (SO 1.1) — Initializing a Local Repository

**Approved SO:** SO 1.1 — Initializing Repositories | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Repository initialization

### Completion requirements
- Easy: 1 session (pool ≥ 3)
- Medium: 2 sessions (pool ≥ 4)
- Hard: 2 sessions (pool ≥ 4)

### Easy variants (E1–E3)

---

**E1 — Student Capstone: The Group Project That Isn't Tracked**

*Environment:* student-capstone

*Context:* You're a BSIT 3rd-year student. Your group has been working on a capstone
project called "Library Management System" in a shared folder. Your groupmate just
realized the folder has never been initialized as a Git repo — there's no version
history, nothing. Your group lead asks you to initialize it.

*Brief:* Initialize the Git repository in the existing project directory `/home/student/capstone/library-system`.

*Repository initial state:*
```
/home/student/capstone/library-system/
  README.md      (untracked)
  main.py        (untracked)
  requirements.txt (untracked)
```
No `.git` directory.

*Required details:* The directory already exists and contains files. Just run `git init` inside it.

*Expected reasoning:* The task is straightforward — navigate to the project directory
and run `git init`. No directory name argument needed because the directory already exists.

*Expected commands:*
```
git init
```

*Target state:* `.git` directory exists; `git status` shows files as untracked.

*Case ID:* `init-easy-library`

---

**E2 — Freelance: Start a New Client Project**

*Environment:* freelance

*Context:* A client hired you to build a simple invoice tracker.
You need to start the project from scratch with Git version control.
The client's folder name should be `invoice-tracker`.

*Brief:* Create and initialize a new Git repository named `invoice-tracker` in your working directory.

*Repository initial state:*
```
/workspace/    (empty)
```

*Required details:* Use `git init invoice-tracker` — this creates the folder AND initializes the repo.

*Expected reasoning:* The directory doesn't exist yet. The single-argument form
`git init <directory>` creates and initializes it in one step.

*Expected commands:*
```
git init invoice-tracker
```

*Target state:* `/workspace/invoice-tracker/.git` exists; `invoice-tracker` is an empty repo.

*Case ID:* `init-easy-invoice`

---

**E3 — QA Testing: Isolated Test Environment**

*Environment:* qa-testing

*Context:* You're a QA intern at a software firm. Your team uses a Git-tracked folder
to store test result logs and configuration files. You've been asked to set up a new
tracking folder called `qa-results` for a new test cycle.

*Brief:* Initialize a new Git repository called `qa-results`.

*Repository initial state:*
```
/qa-workspace/    (empty)
```

*Required details:* Use `git init qa-results`.

*Expected commands:*
```
git init qa-results
```

*Target state:* `/qa-workspace/qa-results/.git` exists.

*Case ID:* `init-easy-qa`

---

### Medium variants (M1–M4)

---

**M1 — Startup: Multi-Project Workspace**

*Environment:* startup

*Context:* You've just joined a small startup. You've been handed a working directory
with a folder called `backend-api` that contains Python files but no Git repo.
Your team lead wants it version-controlled before the day ends.

*Brief:* Initialize a repository in the existing `backend-api` directory.
Verify the initialization succeeded using `git status`.

*Repository initial state:*
```
/workspace/backend-api/
  app.py     (untracked)
  config.py  (untracked)
  db.py      (untracked)
```
No `.git` directory.

*Expected reasoning:* `backend-api` already exists — use `git init` inside it, not
`git init backend-api` (that would try to create a nested directory). Run `git status`
to confirm the `.git` was created and files are now tracked as untracked.

*Expected commands:*
```
git init
git status
```
(only `git init` is counted)

*Case ID:* `init-med-backend`

---

**M2 — Open Source: Fork Scaffold**

*Environment:* open-source

*Context:* You want to start contributing to an open-source project.
Your mentor told you to first create a local scaffold directory called `oss-contrib`
where you'll mirror your fork setup. Create and initialize the repo.

*Brief:* Create and initialize a Git repository named `oss-contrib`.

*Expected commands:*
```
git init oss-contrib
```

*Case ID:* `init-med-oss`

---

**M3 — Corporate: Compliance Archive**

*Environment:* corporate

*Context:* Your IT department needs a Git-tracked archive folder called `audit-logs-2025`
to store quarterly compliance exports. The folder must be a Git repo so diffs can be
inspected. Create and initialize it.

*Expected commands:*
```
git init audit-logs-2025
```

*Case ID:* `init-med-audit`

---

**M4 — Docs Project: Knowledge Base Bootstrap**

*Environment:* docs-project

*Context:* The documentation team needs a version-controlled folder for the new
product knowledge base. The folder name is `kb-docs`. Initialize it.

*Expected commands:*
```
git init kb-docs
```

*Case ID:* `init-med-docs`

---

### Hard variants (H1–H4)

---

**H1 — DevOps: CI Pipeline Repo**

*Environment:* devops

*Context:* You've been asked to create a versioned pipeline configuration store.
The ops team refers to it as `ci-configs`. You know what needs to happen but there
are no step-by-step instructions. Do it.

*Brief:* Initialize a Git repository for the pipeline config store.

*Expected reasoning:* No instructions given. Student determines `git init ci-configs`
is the correct action, creates and initializes the repo.

*Expected commands:*
```
git init ci-configs
```

*Case ID:* `init-hard-ci`

---

**H2 — Startup: Microservice Bootstrap**

*Environment:* startup

*Context:* You're setting up a new microservice directory called `auth-service`.
The tech lead just said "get it versioned." No further instructions.

*Expected commands:*
```
git init auth-service
```

*Case ID:* `init-hard-auth`

---

**H3 — Freelance: Portfolio Project**

*Environment:* freelance

*Context:* You're starting a new portfolio project for a client. The folder is called
`portfolio-site`. Version control it.

*Expected commands:*
```
git init portfolio-site
```

*Case ID:* `init-hard-portfolio`

---

**H4 — Corporate: Data Pipeline Workspace**

*Environment:* corporate

*Context:* Your data engineering team needs a versioned workspace for ETL scripts.
They call it `etl-workspace`. Set it up.

*Expected commands:*
```
git init etl-workspace
```

*Case ID:* `init-hard-etl`

---

## Lesson 2 (SO 1.2) — Cloning a Remote Repository

**Approved SO:** SO 1.2 — Cloning Remote Repositories | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Fresh clone setup

### Easy variants (E1–E5)

---

**E1 — Student Capstone: Clone the Group Repo**

*Environment:* student-capstone

*Context:* Your group's capstone repo is on GitHub. The repo URL is
`https://github.com/citu-bsit/library-system.git`. Your groupmate already pushed
the initial setup. Clone it so you can start working.

*Brief:* Clone the repository into the default directory name.

*Expected commands:*
```
git clone https://github.com/citu-bsit/library-system.git
```

*Case ID:* `clone-easy-library`

---

**E2 — Startup: Clone the API Repo into Custom Folder**

*Environment:* startup

*Context:* You're onboarding at a startup. The backend API is at
`https://github.com/acme-startup/backend-api.git`. Your team's convention is to
store repos in a folder named `api`. Clone into `api`.

*Expected commands:*
```
git clone https://github.com/acme-startup/backend-api.git api
```

*Case ID:* `clone-easy-api`

---

**E3 — Open Source: Clone with SSH**

*Environment:* open-source

*Context:* You've set up SSH keys and want to clone the OSS project you're contributing to.
The SSH URL is `git@github.com:open-dev/oss-toolkit.git`. Clone it.

*Expected commands:*
```
git clone git@github.com:open-dev/oss-toolkit.git
```

*Case ID:* `clone-easy-oss-ssh`

---

**E4 — Corporate: Clone Internal Repo**

*Environment:* corporate

*Context:* Your company hosts Git internally. You need to clone
`https://git.corp.example/it/audit-logs.git` into a folder called `audit-logs-local`.

*Expected commands:*
```
git clone https://git.corp.example/it/audit-logs.git audit-logs-local
```

*Case ID:* `clone-easy-corp`

---

**E5 — Docs Project: Clone the Documentation Repo**

*Environment:* docs-project

*Context:* The docs team's repo is at `https://github.com/techco/kb-docs.git`.
Clone it into the default directory.

*Expected commands:*
```
git clone https://github.com/techco/kb-docs.git
```

*Case ID:* `clone-easy-docs`

---

### Medium variants (M1–M4)

---

**M1 — Startup: Clone a Specific Feature Branch**

*Environment:* startup

*Context:* The backend team is in the middle of a feature sprint on branch `feature/auth`.
You need to clone the repo and start from that branch directly.
Repo: `https://github.com/acme-startup/backend-api.git`.

*Brief:* Clone the repo and check out `feature/auth` immediately.

*Expected reasoning:* Use `-b feature/auth` to select the branch at clone time.

*Expected commands:*
```
git clone -b feature/auth https://github.com/acme-startup/backend-api.git
```

*Case ID:* `clone-med-feature`

---

**M2 — DevOps: Shallow Clone for CI**

*Environment:* devops

*Context:* Your CI pipeline needs a lightweight clone of `https://github.com/corp/infra-scripts.git`
for a one-time build. Clone with depth 1 to keep it fast.

*Expected commands:*
```
git clone --depth 1 https://github.com/corp/infra-scripts.git
```

*Case ID:* `clone-med-shallow`

---

**M3 — Freelance: Branch + Custom Folder**

*Environment:* freelance

*Context:* A client's repo is at `https://github.com/clientco/portal.git`.
You only need the `stable` branch. Clone it into a folder called `client-portal`.

*Expected reasoning:* Combine `-b stable` with a custom directory argument.

*Expected commands:*
```
git clone -b stable https://github.com/clientco/portal.git client-portal
```

*Case ID:* `clone-med-stable`

---

**M4 — Open Source: SSH with Custom Name**

*Environment:* open-source

*Context:* The OSS project uses SSH at `git@github.com:open-dev/oss-toolkit.git`.
Clone it into a folder named `my-oss-work`.

*Expected commands:*
```
git clone git@github.com:open-dev/oss-toolkit.git my-oss-work
```

*Case ID:* `clone-med-oss-named`

---

### Hard variants (H1–H4)

---

**H1 — Corporate: Shallow Clone of a Specific Branch**

*Environment:* corporate

*Context:* You need only the tip of the `release/2025-q2` branch from
`https://git.corp.example/it/audit-logs.git` for a compliance diff.
Disk space is limited — shallow clone only.

*Expected reasoning:* Combine `--depth 1` with `-b release/2025-q2` and a directory name.

*Expected commands:*
```
git clone --depth 1 -b release/2025-q2 https://git.corp.example/it/audit-logs.git audit-q2
```

*Case ID:* `clone-hard-shallow-branch`

---

**H2 — DevOps: Pinned Release Clone**

*Environment:* devops

*Context:* You need a shallow clone of the `v3.1` tag/branch from
`https://github.com/corp/infra-scripts.git` into a folder named `infra-v31`.

*Expected commands:*
```
git clone --depth 1 -b v3.1 https://github.com/corp/infra-scripts.git infra-v31
```

*Case ID:* `clone-hard-pinned`

---

**H3 — Startup: Full Clone + Branch**

*Environment:* startup

*Context:* You need the full history of the `feature/payments` branch from
`https://github.com/acme-startup/backend-api.git` in a folder called `payments-dev`.
No depth limit this time — you need the full history for blame analysis.

*Expected commands:*
```
git clone -b feature/payments https://github.com/acme-startup/backend-api.git payments-dev
```

*Case ID:* `clone-hard-full-branch`

---

**H4 — Open Source: SSH Shallow Clone into Named Folder**

*Environment:* open-source

*Context:* You want a minimal clone of `git@github.com:open-dev/oss-toolkit.git`
with only the latest commit, stored in a folder named `oss-review`.

*Expected commands:*
```
git clone --depth 1 git@github.com:open-dev/oss-toolkit.git oss-review
```

*Case ID:* `clone-hard-ssh-shallow`

---

## Lesson 3 (SO 1.3) — Staging and Committing

**Approved SO:** SO 1.3 — Staging and Committing | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Stage-and-commit workflow

### Easy variants (E1–E5)

---

**E1 — Student Capstone: First Commit of the Group Project**

*Environment:* student-capstone

*Context:* You've just initialized the `library-system` repo (Lesson 1.1 E1 follow-up).
You have three files: `README.md`, `main.py`, `requirements.txt`.
Your group lead says "do the initial commit."

*Brief:* Stage all three files and commit with the message "Initial commit".

*Repository initial state:*
```
README.md        (untracked)
main.py          (untracked)
requirements.txt (untracked)
```

*Expected commands:*
```
git add README.md
git add main.py
git add requirements.txt
git commit -m "Initial commit"
```
(or `git add .` — both are valid)

*Case ID:* `commit-easy-initial`

---

**E2 — Freelance: Single-File Feature Commit**

*Environment:* freelance

*Context:* You added a `pricing.py` module to the invoice tracker. It's ready.
Stage and commit just that one file.

*Repository initial state:*
```
pricing.py    (modified/new, untracked)
invoice.py    (clean — already committed)
```

*Brief:* Stage `pricing.py` and commit with "Add pricing module".

*Expected commands:*
```
git add pricing.py
git commit -m "Add pricing module"
```

*Case ID:* `commit-easy-pricing`

---

**E3 — Startup: Stage a Directory**

*Environment:* startup

*Context:* You added a new `src/auth/` directory containing `login.py` and `logout.py`.
Both are new files. Stage the entire `src/auth/` directory and commit.

*Repository initial state:*
```
src/auth/login.py   (untracked)
src/auth/logout.py  (untracked)
src/main.py         (clean)
```

*Brief:* Stage `src/auth/` and commit with "Add auth module".

*Expected commands:*
```
git add src/auth/
git commit -m "Add auth module"
```

*Case ID:* `commit-easy-auth-dir`

---

**E4 — QA Testing: Commit a Config Update**

*Environment:* qa-testing

*Context:* You updated `test-config.yaml` with new environment variables for the test cycle.
Stage it and commit.

*Repository initial state:*
```
test-config.yaml   (modified)
test-results/      (untracked — should NOT be staged)
```

*Brief:* Stage `test-config.yaml` and commit with "Update test configuration".

*Expected commands:*
```
git add test-config.yaml
git commit -m "Update test configuration"
```

*Case ID:* `commit-easy-config`

---

**E5 — Open Source: Add All Changes with git add .**

*Environment:* open-source

*Context:* You've fixed two typos across `README.md` and `CONTRIBUTING.md`.
Both files are modified and both should be committed together.
Use `git add .` to stage everything at once.

*Repository initial state:*
```
README.md        (modified)
CONTRIBUTING.md  (modified)
```

*Brief:* Stage all changes with `git add .` and commit with "Fix documentation typos".

*Expected commands:*
```
git add .
git commit -m "Fix documentation typos"
```

*Case ID:* `commit-easy-all`

---

### Medium variants (M1–M4)

---

**M1 — Corporate: Multi-File Selective Stage**

*Environment:* corporate

*Context:* You've been working on two unrelated changes: a bug fix in `api/handler.py`
and experimental work in `api/experimental.py`. Only the bug fix should go in this commit.

*Repository initial state:*
```
api/handler.py       (modified — bug fix, ready to commit)
api/experimental.py  (modified — not ready, do not stage)
```

*Brief:* Stage only `handler.py` and commit with "Fix request handler null check".

*Expected commands:*
```
git add api/handler.py
git commit -m "Fix request handler null check"
```

*Case ID:* `commit-med-selective`

---

**M2 — DevOps: Stage Multiple Specific Files**

*Environment:* devops

*Context:* You updated `Dockerfile` and `.env.example` as part of a container setup.
A `notes.txt` scratch file is also in the working tree but should not be committed.

*Expected commands:*
```
git add Dockerfile
git add .env.example
git commit -m "Add Docker configuration"
```

*Case ID:* `commit-med-docker`

---

**M3 — Freelance: Commit After Directory Restructure**

*Environment:* freelance

*Context:* You moved client assets into a new `assets/images/` subdirectory.
Stage the new directory and commit.

*Expected commands:*
```
git add assets/images/
git commit -m "Reorganize images into assets directory"
```

*Case ID:* `commit-med-assets`

---

**M4 — Student Capstone: Two-Stage Commit**

*Environment:* student-capstone

*Context:* You have three new files: `models.py`, `views.py`, and a scratch `todo.txt`.
Your groupmate says "commit models and views separately" — two commits, not one.
`todo.txt` should not be committed yet.

*Expected commands:*
```
git add models.py
git commit -m "Add data models"
git add views.py
git commit -m "Add view layer"
```

*Case ID:* `commit-med-two-stage`

---

### Hard variants (H1–H4)

---

**H1 — Startup: Feature Branch Initial Commit**

*Environment:* startup

*Context:* You've built the initial skeleton of a payments feature. Three files are new:
`payments/gateway.py`, `payments/models.py`, `payments/__init__.py`.
A `payments/scratch.txt` file exists from brainstorming — it must not be committed.
No instructions beyond "commit the feature skeleton."

*Expected commands:*
```
git add payments/gateway.py
git add payments/models.py
git add payments/__init__.py
git commit -m "Add payments feature skeleton"
```

*Case ID:* `commit-hard-payments`

---

**H2 — Corporate: Three-File Targeted Commit**

*Environment:* corporate

*Context:* Compliance requires you to commit only the three files changed for the quarterly
audit update: `reports/q2.csv`, `reports/summary.md`, `config/audit.yaml`.
Two other modified files (`config/dev.yaml`, `temp/export.tmp`) must not be included.

*Expected commands:*
```
git add reports/q2.csv
git add reports/summary.md
git add config/audit.yaml
git commit -m "Add Q2 audit report and update audit configuration"
```

*Case ID:* `commit-hard-audit`

---

**H3 — Open Source: PR-Ready Commit**

*Environment:* open-source

*Context:* You're preparing a PR for a new feature. The files ready to go are
`src/parser.py` and `tests/test_parser.py`. A `debug.log` and `scratch.py` are also
in the tree. The PR should be one focused commit.

*Expected commands:*
```
git add src/parser.py
git add tests/test_parser.py
git commit -m "Add parser module with unit tests"
```

*Case ID:* `commit-hard-parser`

---

**H4 — DevOps: Config-Only Deploy Commit**

*Environment:* devops

*Context:* A deploy requires committing only the infrastructure config files:
`terraform/main.tf` and `terraform/variables.tf`. Application code changes
in `src/` are not ready. Commit only the infra changes.

*Expected commands:*
```
git add terraform/main.tf
git add terraform/variables.tf
git commit -m "Update Terraform infrastructure configuration"
```

*Case ID:* `commit-hard-infra`

---

## Lesson 4 — Ignoring Files with .gitignore

> ⚠️ **FLAGGED — NO APPROVED SO**
> This lesson exists in the current seed implementation but cannot be mapped to any
> approved SO in the Final Proposal. It must not be redesigned or expanded until either:
> (a) an approved SO is identified that covers `.gitignore`, or
> (b) a new SO is explicitly approved by the team and documented in the proposal.
>
> The variant library below is **preserved for reference only** — it describes the
> existing seed design, not an approved redesign. Do not implement new variants for
> this lesson until its SO status is resolved.

**Flagged SO:** None — pending resolution  
**Scenario skill focus:** .gitignore setup

### Easy variants (E1–E5)

---

**E1 — Student Capstone: Ignore Build Output**

*Environment:* student-capstone

*Context:* Your Python capstone project is generating `__pycache__/` directories.
Your groupmate asked you to make sure these never get committed.

*Brief:* Create a `.gitignore` with the pattern `__pycache__/`, then stage and commit it.

*Repository initial state:*
```
main.py        (clean)
__pycache__/   (untracked — should be ignored)
```

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude Python cache"
```
(Student must create the `.gitignore` file content first — the platform provides this
as part of the scenario scaffolding)

*Case ID:* `ignore-easy-pycache`

---

**E2 — Freelance: Ignore Node Modules**

*Environment:* freelance

*Context:* You set up a Node.js invoice tracker. `node_modules/` is huge and must
never be committed. Add it to `.gitignore`.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude node_modules"
```

*Case ID:* `ignore-easy-node`

---

**E3 — Corporate: Ignore Sensitive Config**

*Environment:* corporate

*Context:* Your repo has a `.env` file with database credentials.
It must be excluded from version control. Add `.env` to `.gitignore`.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude environment secrets"
```

*Case ID:* `ignore-easy-env`

---

**E4 — QA Testing: Ignore Test Logs**

*Environment:* qa-testing

*Context:* Your QA repo generates `*.log` files after each test run.
These should never be committed. Add `*.log` to `.gitignore`.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude test log files"
```

*Case ID:* `ignore-easy-logs`

---

**E5 — DevOps: Ignore Build Artifacts**

*Environment:* devops

*Context:* Your CI pipeline creates a `dist/` directory when building.
Ignore the entire `dist/` directory.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude build artifacts"
```

*Case ID:* `ignore-easy-dist`

---

### Medium variants (M1–M4)

---

**M1 — Startup: Multi-Pattern gitignore**

*Environment:* startup

*Context:* Your repo needs to ignore three things: `node_modules/`, `*.log`, and `.env`.
Create the `.gitignore` with all three patterns, then stage and commit it.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore for Node, logs, and env files"
```

*Case ID:* `ignore-med-multi`

---

**M2 — Open Source: Untrack an Already-Committed File**

*Environment:* open-source

*Context:* A `config/secrets.json` file was accidentally committed two commits ago.
It's now in `.gitignore` but Git is still tracking it because it was tracked before
the `.gitignore` was created.

*Brief:* Remove `config/secrets.json` from the index without deleting it from disk,
then commit the removal.

*Expected reasoning:* `.gitignore` alone won't stop tracking an already-tracked file.
Must use `git rm --cached config/secrets.json`.

*Expected commands:*
```
git rm --cached config/secrets.json
git commit -m "Remove secrets file from version control"
```

*Case ID:* `ignore-med-untrack`

---

**M3 — Corporate: Untrack and Update gitignore**

*Environment:* corporate

*Context:* `logs/app.log` was committed when it shouldn't have been. Remove it from
tracking and also add `logs/*.log` to `.gitignore` so future log files are automatically ignored.

*Expected commands:*
```
git rm --cached logs/app.log
git add .gitignore
git commit -m "Remove tracked log file and update .gitignore"
```

*Case ID:* `ignore-med-untrack-update`

---

**M4 — Student Capstone: Add gitignore to Existing Repo**

*Environment:* student-capstone

*Context:* The group repo has been running for a week with no `.gitignore`.
`__pycache__/` and `.pyc` files have been accumulating but haven't been committed
(still untracked). Now add a proper `.gitignore` covering both patterns before
anyone accidentally commits them.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore to exclude Python cache and bytecode"
```

*Case ID:* `ignore-med-existing`

---

### Hard variants (H1–H4)

---

**H1 — DevOps: Comprehensive gitignore for Monorepo**

*Environment:* devops

*Context:* A new monorepo needs a `.gitignore` covering: `node_modules/`, `dist/`,
`*.log`, `.env`, `__pycache__/`, `.DS_Store`. Set it up and commit.

*Expected commands:*
```
git add .gitignore
git commit -m "Add comprehensive .gitignore for monorepo"
```

*Case ID:* `ignore-hard-monorepo`

---

**H2 — Corporate: Mass Untrack + Update**

*Environment:* corporate

*Context:* Several `*.tmp` files and a `debug.log` were committed by accident.
Remove all of them from tracking using `git rm --cached` and update `.gitignore`
to prevent recurrence. Three files to untrack: `temp/export.tmp`, `temp/import.tmp`,
`debug.log`.

*Expected commands:*
```
git rm --cached temp/export.tmp
git rm --cached temp/import.tmp
git rm --cached debug.log
git add .gitignore
git commit -m "Remove accidentally tracked temp files and update .gitignore"
```

*Case ID:* `ignore-hard-mass-untrack`

---

**H3 — Open Source: Root-Only gitignore Pattern**

*Environment:* open-source

*Context:* The project has a `secrets.txt` at the root that should be ignored
(using `/secrets.txt` pattern — root-only) but `docs/secrets.txt` should still
be tracked. Create a `.gitignore` with the root-only pattern.

*Expected commands:*
```
git add .gitignore
git commit -m "Add .gitignore with root-scoped secrets exclusion"
```

*Case ID:* `ignore-hard-root-pattern`

---

**H4 — Startup: Untrack, gitignore, and Commit in One Go**

*Environment:* startup

*Context:* `config/.env` and `logs/server.log` are both being tracked.
Neither should be. Remove both from tracking, add appropriate patterns to `.gitignore`,
and produce a single clean commit.

*Expected commands:*
```
git rm --cached config/.env
git rm --cached logs/server.log
git add .gitignore
git commit -m "Remove sensitive files from tracking and add .gitignore"
```

*Case ID:* `ignore-hard-full`

---

## Lesson 5 (SO 1.4) — Partial Staging with git add -p

**Approved SO:** SO 1.4 — Partial Staging | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Partial staging

### Easy variants (E1–E5)

---

**E1 — Freelance: Two-Hunk File, Stage Only the Fix**

*Environment:* freelance

*Context:* You modified `billing.py`. The file has two hunks of changes:
a bug fix at the top and some experimental print statements at the bottom.
Your client is waiting on the bug fix only.

*Brief:* Use `git add -p` to stage only the first hunk (the bug fix), skip the second.
Then commit the staged fix.

*Expected commands:*
```
git add -p
git commit -m "Fix billing calculation rounding error"
```
(During `git add -p`: `y` for first hunk, `n` for second)

*Case ID:* `partial-easy-billing`

---

**E2 — Student Capstone: Stage the Feature, Skip Debug Code**

*Environment:* student-capstone

*Context:* You added a new `search()` function to `library.py` but also left some
`print()` debug statements in a separate hunk. Stage only the `search()` function hunk.

*Expected commands:*
```
git add -p
git commit -m "Add search function to library module"
```

*Case ID:* `partial-easy-search`

---

**E3 — Startup: Stage Header, Skip Experimental Footer**

*Environment:* startup

*Context:* `api/routes.py` has two changed sections: updated route handlers (stage these)
and a commented-out experimental auth middleware section (skip this).

*Expected commands:*
```
git add -p
git commit -m "Update API route handlers"
```

*Case ID:* `partial-easy-routes`

---

**E4 — Corporate: Partial Stage Then Unstage**

*Environment:* corporate

*Context:* You staged all of `report.py` with `git add report.py` but then realized
only part of it should go in this commit. Unstage `report.py`, then use `git add -p`
to stage only the first hunk.

*Expected commands:*
```
git restore --staged report.py
git add -p
git commit -m "Update report header generation"
```

*Case ID:* `partial-easy-unstage-first`

---

**E5 — QA Testing: Stage Config Section Only**

*Environment:* qa-testing

*Context:* `test-runner.py` has two changed sections: a timeout config update (stage it)
and some WIP logic for a new test type (skip it).

*Expected commands:*
```
git add -p
git commit -m "Update test runner timeout configuration"
```

*Case ID:* `partial-easy-timeout`

---

### Medium variants (M1–M4)

---

**M1 — Open Source: Three-Hunk Split Decision**

*Environment:* open-source

*Context:* `src/parser.py` has three hunks. Hunk 1: bug fix (stage). Hunk 2: refactor
(stage). Hunk 3: experimental feature (skip). Stage the first two, skip the third.

*Expected commands:*
```
git add -p
git commit -m "Fix parser bug and refactor token handling"
```

*Case ID:* `partial-med-three-hunk`

---

**M2 — Corporate: Split Hunk and Stage Part**

*Environment:* corporate

*Context:* A single hunk in `config.py` mixes two changes. Use `s` to split it,
then stage only the first sub-hunk (the security config update).

*Expected commands:*
```
git add -p
git commit -m "Update security configuration"
```

*Case ID:* `partial-med-split`

---

**M3 — Startup: Multi-File Partial Stage**

*Environment:* startup

*Context:* Two files are modified: `users.py` (stage hunk 1 only) and `orders.py`
(stage all hunks). A third file `debug_tools.py` should not be staged at all.

*Expected commands:*
```
git add -p
git commit -m "Update user authentication and order processing"
```

*Case ID:* `partial-med-multi-file`

---

**M4 — Freelance: Stage, Verify, Then Commit**

*Environment:* freelance

*Context:* After partial staging, check `git diff --staged` to confirm only the
intended hunk is staged before committing.

*Expected commands:*
```
git add -p
git diff --staged
git commit -m "Add invoice export function"
```
(only `git add -p` and `git commit -m` are counted; `git diff --staged` is diagnostic)

*Case ID:* `partial-med-verify`

---

### Hard variants (H1–H4)

---

**H1 — DevOps: Precise Infrastructure Hunk Selection**

*Environment:* devops

*Context:* `terraform/main.tf` has four hunks: network config (stage), compute config
(stage), experimental feature flags (skip), debug outputs (skip).
No hints about which hunks to stage — infer from context.

*Expected commands:*
```
git add -p
git commit -m "Update network and compute Terraform configuration"
```

*Case ID:* `partial-hard-terraform`

---

**H2 — Corporate: Three Files, Selective Per-File**

*Environment:* corporate

*Context:* Three files changed. `auth.py`: stage all. `reports.py`: stage hunk 1 only
(hunk 2 is WIP). `temp_helpers.py`: skip entirely.

*Expected commands:*
```
git add -p
git commit -m "Update authentication and report generation logic"
```

*Case ID:* `partial-hard-three-files`

---

**H3 — Open Source: Unstage Then Partial Re-Stage**

*Environment:* open-source

*Context:* You accidentally ran `git add .` and staged everything. Unstage the entire
working tree, then carefully use `git add -p` on `src/lexer.py` to stage only the
relevant hunk for the PR.

*Expected commands:*
```
git restore --staged src/lexer.py
git restore --staged tests/test_lexer.py
git add -p
git commit -m "Fix lexer token boundary detection"
```

*Case ID:* `partial-hard-unstage-restage`

---

**H4 — Startup: End-to-End Clean Commit**

*Environment:* startup

*Context:* You've made wide-ranging edits across `api/auth.py` (one hunk to stage),
`api/users.py` (two hunks to stage, one to skip), and `api/debug.py` (skip entirely).
Produce a focused commit with only the production-ready changes.

*Expected commands:*
```
git add -p
git commit -m "Add user authentication and update user management"
```

*Case ID:* `partial-hard-wide`

---

## Lesson 6 (SO 1.5) — Amending Commits

**Approved SO:** SO 1.5 — Amending Commits | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Commit amendment

### Easy variants (E1–E5)

---

**E1 — Student Capstone: Fix a Typo in the Last Commit Message**

*Environment:* student-capstone

*Context:* You committed with the message "Initiall commit" — a typo.
No content needs to change, just the message.

*Expected commands:*
```
git commit --amend -m "Initial commit"
```

*Case ID:* `amend-easy-typo`

---

**E2 — Freelance: Fix Wrong Tense in Commit Message**

*Environment:* freelance

*Context:* Your last commit message says "Added pricing module" — wrong tense.
It should be "Add pricing module".

*Expected commands:*
```
git commit --amend -m "Add pricing module"
```

*Case ID:* `amend-easy-tense`

---

**E3 — Startup: Add a Forgotten File to Last Commit**

*Environment:* startup

*Context:* You committed `login.py` but forgot to include `logout.py` — it belongs
in the same commit. Stage `logout.py` and amend the last commit without changing the message.

*Repository initial state:*
```
logout.py    (modified/new — needs to be added to last commit)
```

*Expected commands:*
```
git add logout.py
git commit --amend --no-edit
```

*Case ID:* `amend-easy-forgot`

---

**E4 — Corporate: Fix Non-Imperative Message**

*Environment:* corporate

*Context:* Last commit message is "Fixed the null pointer exception in the handler".
It should follow conventions: "Fix null pointer exception in request handler".

*Expected commands:*
```
git commit --amend -m "Fix null pointer exception in request handler"
```

*Case ID:* `amend-easy-imperative`

---

**E5 — QA Testing: Add Missing Test File to Last Commit**

*Environment:* qa-testing

*Context:* You committed the feature code but forgot the corresponding test file.
Stage `tests/test_feature.py` and amend the commit to include it.

*Expected commands:*
```
git add tests/test_feature.py
git commit --amend --no-edit
```

*Case ID:* `amend-easy-test-file`

---

### Medium variants (M1–M4)

---

**M1 — Open Source: Amend Message AND Add Content**

*Environment:* open-source

*Context:* Your last commit message was "update stuff" (too vague) AND you forgot
to include `docs/CHANGELOG.md`. Stage the changelog and fix the message in one amend.

*Expected commands:*
```
git add docs/CHANGELOG.md
git commit --amend -m "Add parser feature and update changelog"
```

*Case ID:* `amend-med-both`

---

**M2 — DevOps: Amend to Include Config File**

*Environment:* devops

*Context:* Your last commit "Add Dockerfile" is missing `docker-compose.yml`.
Amend without changing the commit message.

*Expected commands:*
```
git add docker-compose.yml
git commit --amend --no-edit
```

*Case ID:* `amend-med-compose`

---

**M3 — Freelance: Fix Vague Commit Message**

*Environment:* freelance

*Context:* The last commit says "changes". This is completely non-descriptive.
Change it to "Add client invoice export to PDF" — no content changes needed.

*Expected commands:*
```
git commit --amend -m "Add client invoice export to PDF"
```

*Case ID:* `amend-med-vague`

---

**M4 — Corporate: Amend to Remove Wrongly Staged File**

*Environment:* corporate

*Context:* Your last commit accidentally included `debug.log`. You need to undo
the staging of that file from the commit and amend. Unstage `debug.log`, then amend.

*Expected commands:*
```
git restore --staged debug.log
git commit --amend --no-edit
```

*Case ID:* `amend-med-remove-staged`

---

### Hard variants (H1–H4)

---

**H1 — Startup: Multi-Step Fix (Wrong File + Wrong Message)**

*Environment:* startup

*Context:* Last commit "updated stuff" has two problems: wrong message AND it accidentally
included `scratch.py`. Remove `scratch.py` from staging, fix the message, and amend.

*Expected commands:*
```
git restore --staged scratch.py
git commit --amend -m "Update user authentication flow"
```

*Case ID:* `amend-hard-multi-fix`

---

**H2 — Open Source: Amend to Separate Concerns**

*Environment:* open-source

*Context:* Your last commit bundled two things: a bug fix and new feature code.
The PR reviewer wants them separate. Remove the feature file (`src/new_feature.py`)
from the commit, fix the message to reflect only the bug fix, then amend.
(A follow-up commit for the feature will be made separately — not in this scenario.)

*Expected commands:*
```
git restore --staged src/new_feature.py
git commit --amend -m "Fix lexer token boundary detection"
```

*Case ID:* `amend-hard-separate`

---

**H3 — Corporate: Correct Three Issues in One Amend**

*Environment:* corporate

*Context:* Last commit has: (1) wrong message "misc updates", (2) missing file
`reports/q2_summary.md`, (3) accidentally staged `temp/notes.txt`.
Fix all three in one amend operation.

*Expected commands:*
```
git restore --staged temp/notes.txt
git add reports/q2_summary.md
git commit --amend -m "Add Q2 summary report"
```

*Case ID:* `amend-hard-three-issues`

---

**H4 — DevOps: Amend a Message That Violates Convention**

*Environment:* devops

*Context:* Last commit message: "terraform configs have been updated for staging env"
— passive voice, lowercase start, too verbose. Correct it to follow imperative convention.
No content changes needed.

*Expected commands:*
```
git commit --amend -m "Update Terraform staging environment configuration"
```

*Case ID:* `amend-hard-convention`

---

## Lesson 7 (SO 1.6) — Unstaging and Discarding Changes

**Approved SO:** SO 1.6 — Unstaging and Discarding Changes | **KPI:** CAR ≥ 70%  
**Scenario skill focus:** Unstage and discard

### Easy variants (E1–E5)

---

**E1 — Student Capstone: Unstage a Wrongly Staged File**

*Environment:* student-capstone

*Context:* You ran `git add .` and accidentally staged `notes.txt` along with
your intended files. The commit is not ready yet. Unstage `notes.txt`.

*Expected commands:*
```
git restore --staged notes.txt
```

*Case ID:* `restore-easy-unstage`

---

**E2 — Freelance: Unstage the Wrong Module**

*Environment:* freelance

*Context:* You staged both `invoice.py` and `debug_tools.py`. Only `invoice.py`
should be in the next commit. Unstage `debug_tools.py`.

*Expected commands:*
```
git restore --staged debug_tools.py
```

*Case ID:* `restore-easy-debug`

---

**E3 — Startup: Discard Experimental Changes**

*Environment:* startup

*Context:* You made some experimental edits to `config.py` trying out a new
approach that didn't work. Discard all working-tree changes to `config.py`
and get back to the last committed state.

*Expected commands:*
```
git restore config.py
```

*Case ID:* `restore-easy-discard`

---

**E4 — Corporate: Discard Accidental Edits**

*Environment:* corporate

*Context:* You accidentally edited `schema.sql` while investigating a bug.
No intentional changes were made to it. Discard the working-tree changes.

*Expected commands:*
```
git restore schema.sql
```

*Case ID:* `restore-easy-accidental`

---

**E5 — QA Testing: Unstage Multiple Files**

*Environment:* qa-testing

*Context:* You staged three files but only two should be committed right now.
Unstage `wip-tests.py` while keeping `config.yaml` and `fixtures.py` staged.

*Expected commands:*
```
git restore --staged wip-tests.py
```

*Case ID:* `restore-easy-multi-unstage`

---

### Medium variants (M1–M4)

---

**M1 — Open Source: Unstage Then Discard**

*Environment:* open-source

*Context:* You staged `experimental.py` and also have unstaged edits to `README.md`
that you want to discard. First unstage `experimental.py`, then discard the README edits.

*Expected commands:*
```
git restore --staged experimental.py
git restore README.md
```

*Case ID:* `restore-med-unstage-discard`

---

**M2 — DevOps: Discard Multiple Working-Tree Files**

*Environment:* devops

*Context:* You made experimental edits to three Terraform files that all turned out wrong.
Discard all three: `terraform/network.tf`, `terraform/compute.tf`, `terraform/storage.tf`.

*Expected commands:*
```
git restore terraform/network.tf
git restore terraform/compute.tf
git restore terraform/storage.tf
```

*Case ID:* `restore-med-multi-discard`

---

**M3 — Corporate: Selective Unstage from Multi-File Stage**

*Environment:* corporate

*Context:* You staged `auth.py`, `reports.py`, and `debug.py`. A code review reminder
comes in: `debug.py` must not be committed. Unstage it without touching the others.

*Expected commands:*
```
git restore --staged debug.py
```

*Case ID:* `restore-med-selective`

---

**M4 — Startup: Mixed Unstage and Discard**

*Environment:* startup

*Context:* You have three things in play: `users.py` is staged (unstage it),
`orders.py` has working-tree edits that are wrong (discard them), and `auth.py`
is staged and correct (leave it alone). Restore the incorrect states without
touching `auth.py`.

*Expected commands:*
```
git restore --staged users.py
git restore orders.py
```

*Case ID:* `restore-med-mixed`

---

### Hard variants (H1–H4)

---

**H1 — Open Source: Three-Way Restore**

*Environment:* open-source

*Context:* You have: `parser.py` staged (unstage), `lexer.py` with working-tree
changes (discard), `tokenizer.py` staged AND with additional working-tree edits
(unstage the staging; keep the working-tree changes). `tests/test_parser.py` is
staged and correct — leave it.

*Expected commands:*
```
git restore --staged parser.py
git restore lexer.py
git restore --staged tokenizer.py
```

*Case ID:* `restore-hard-three-way`

---

**H2 — Corporate: Full Cleanup Before Commit**

*Environment:* corporate

*Context:* Before the daily commit, you need to clean up:
- `debug.log` — staged, should not be committed (unstage)
- `scratch/notes.txt` — staged, should not be committed (unstage)
- `api/experimental.py` — working-tree changes, turn back (discard)
- `config/production.yaml` — staged and correct (leave)
- `config/dev.yaml` — staged and correct (leave)

*Expected commands:*
```
git restore --staged debug.log
git restore --staged scratch/notes.txt
git restore api/experimental.py
```

*Case ID:* `restore-hard-cleanup`

---

**H3 — Startup: Unstage-All After git add .**

*Environment:* startup

*Context:* You ran `git add .` in a hurry and staged 5 files. On reflection, only
`src/auth.py` and `src/users.py` should be in the next commit.
Unstage everything else: `src/debug.py`, `src/scratch.py`, `tests/wip_test.py`.

*Expected commands:*
```
git restore --staged src/debug.py
git restore --staged src/scratch.py
git restore --staged tests/wip_test.py
```

*Case ID:* `restore-hard-unstage-all`

---

**H4 — DevOps: Discard, Unstage, and Partial Cleanup**

*Environment:* devops

*Context:* Multiple things need cleaning before the next commit:
`pipeline/build.yml` — wrong working-tree edits (discard),
`pipeline/test.yml` — staged unnecessarily (unstage),
`infrastructure/deploy.sh` — staged and correct (leave alone).

*Expected commands:*
```
git restore pipeline/build.yml
git restore --staged pipeline/test.yml
```

*Case ID:* `restore-hard-pipeline`

---

## Lesson 1 — Inspecting Repository State

> ⛔ **NOT IN REDESIGN SCOPE**
>
> Lesson 1 (`inspect-repository-state`) has `difficulties={}` in the seed — no
> difficulty instances, no variants, no playable sessions. It is a concept-only
> reference page listing diagnostic commands. It cannot be played, cannot generate
> session data, and does not contribute to any KPI.
>
> SO 1.8 (Efficient Repository-State Reasoning / ARC ≤ 2) is a KPI measured across
> all Module 1 sessions, not a standalone instructional lesson. No variants should
> be designed for Lesson 1.
>
> The variant library that previously appeared here has been removed.
> Do not add difficulty instances or scenarios to this lesson.

## Lesson 8 — Module 1 Review and Practice (Integration)

**Purpose:** Multi-SO integration. HLCR measurement vehicle.  
**Scenario skill focus:** Full local workflow combining SO 1.1–SO 1.6  
**Note:** Hard ×3 sessions (not ×2 as in single-skill lessons)

*Design note:* Each scenario must require at least 3 distinct skills from SO 1.1–1.6.
No new commands are introduced. `.gitignore` skills (Lesson 4, flagged) must not
appear in integration scenarios.

### Easy variants (E1–E5)

---

**E1 — Student Capstone: Setup + First Commit**

*Skills tested:* SO 1.1 (init), SO 1.3 (stage + commit)

*Context:* Initialize a new repo in the existing `todo-app` directory,
then stage `app.py` and commit with "Add initial application file".

*Expected commands:*
```
git init
git add app.py
git commit -m "Add initial application file"
```

*Case ID:* `cap1-easy-init-commit`

---

**E2 — Freelance: Two-File Selective Stage**

*Skills tested:* SO 1.3 (stage), SO 1.3 (commit)

*Context:* You finished two independent features: `billing.py` and `export.py`.
Your client says "commit them separately — one commit per feature."
`debug.py` is also modified but not ready. Do not stage it.

*Repository initial state:*
```
billing.py   (modified)
export.py    (modified)
debug.py     (modified — do not stage)
```

*Expected commands:*
```
git add billing.py
git commit -m "Add billing module"
git add export.py
git commit -m "Add export module"
```

*Case ID:* `cap1-easy-two-commits`

---

**E3 — Startup: Commit + Amend Message**

*Skills tested:* SO 1.3 (commit), SO 1.5 (amend)

*Context:* Commit `utils.py` with "utils added" (wrong message),
then amend to "Add utility module".

*Expected commands:*
```
git add utils.py
git commit -m "utils added"
git commit --amend -m "Add utility module"
```

*Case ID:* `cap1-easy-commit-amend`

---

**E4 — QA Testing: Stage + Unstage + Restage**

*Skills tested:* SO 1.3 (stage + commit), SO 1.6 (unstage)

*Context:* Stage `test_suite.py` and `debug_helper.py`. Then unstage `debug_helper.py`.
Commit only `test_suite.py`.

*Expected commands:*
```
git add test_suite.py
git add debug_helper.py
git restore --staged debug_helper.py
git commit -m "Add test suite"
```

*Case ID:* `cap1-easy-stage-unstage`

---

**E5 — Corporate: Discard + Stage + Commit**

*Skills tested:* SO 1.6 (discard), SO 1.3 (stage + commit)

*Context:* `scratch.py` has wrong working-tree edits — discard them.
Then stage `handler.py` and commit "Fix request handler".

*Expected commands:*
```
git restore scratch.py
git add handler.py
git commit -m "Fix request handler"
```

*Case ID:* `cap1-easy-discard-commit`

---

### Medium variants (M1–M4)

---

**M1 — Startup: Partial Stage + Commit + Check**

*Skills tested:* SO 1.4 (partial stage), SO 1.3 (commit), SO 1.8 (diagnostic read)

*Context:* `api.py` has two hunks. Stage only the first. Check `git diff --staged`
to verify. Then commit.

*Expected commands:*
```
git add -p
git diff --staged
git commit -m "Add API authentication endpoint"
```

*Case ID:* `cap1-med-partial-commit`

---

**M2 — Open Source: Partial Stage + Amend**

*Skills tested:* SO 1.4 (partial stage), SO 1.5 (amend)

*Context:* `src/parser.py` has two hunks. Use `git add -p` to stage only the first
(the bug fix). Commit with "Add parser module". Then realize the commit message
should be "Fix parser token boundary" — amend it without changing content.

*Expected commands:*
```
git add -p
git commit -m "Add parser module"
git commit --amend -m "Fix parser token boundary"
```

*Case ID:* `cap1-med-partial-amend2`

---

**M3 — Corporate: Selective Stage + Amend**

*Skills tested:* SO 1.3 (selective stage + commit), SO 1.5 (amend with new file)

*Context:* Stage `reports/q3.csv` and commit "Add Q3 report". Then realize
`reports/q3_summary.md` was forgotten — add it to the last commit via amend.

*Expected commands:*
```
git add reports/q3.csv
git commit -m "Add Q3 report"
git add reports/q3_summary.md
git commit --amend --no-edit
```

*Case ID:* `cap1-med-commit-then-amend`

---

**M4 — Freelance: Discard + Partial Stage + Commit**

*Skills tested:* SO 1.6 (discard), SO 1.4 (partial stage), SO 1.3 (commit)

*Context:* Discard wrong changes in `scratch.py`, then use `git add -p` on
`billing.py` to stage only the fix hunk, then commit.

*Expected commands:*
```
git restore scratch.py
git add -p
git commit -m "Fix billing calculation"
```

*Case ID:* `cap1-med-discard-partial`

---

### Hard variants (H1–H5)

---

**H1 — DevOps: Full Workflow — Init, Commit, Amend**

*Skills tested:* SO 1.1 (init), SO 1.3 (commit), SO 1.5 (amend)

*Context:* Initialize `infra-repo`. Stage `Dockerfile` and commit with "add dockerfile"
(bad message — wrong tense, wrong format). Stage `docker-compose.yml` and commit
"Add Compose configuration". Then go back and amend the first commit message
to "Add Dockerfile for container setup".

*Expected commands:*
```
git init infra-repo
git add Dockerfile
git commit -m "add dockerfile"
git add docker-compose.yml
git commit -m "Add Compose configuration"
git commit --amend -m "Add Dockerfile for container setup"
```
(Amend applies to the most recent commit — the Compose commit — not the Dockerfile one.
The scenario must be designed so the Compose commit is the one needing amendment, not
the Dockerfile commit, to keep the solution linear. Adjust context accordingly.)

*Design note:* Platform handles directory navigation after `git init infra-repo`.

*Case ID:* `cap1-hard-full-init`

---

**H2 — Open Source: Partial + Amend + Restore**

*Skills tested:* SO 1.4 (partial stage), SO 1.5 (amend), SO 1.6 (discard)

*Context:* Partially stage `parser.py` (hunk 1 only), commit "Add parser".
Then realize `changelog.md` was not included — add and amend. Then discard
wrong working-tree edits to `scratch.py`.

*Expected commands:*
```
git add -p
git commit -m "Add parser module"
git add changelog.md
git commit --amend --no-edit
git restore scratch.py
```

*Case ID:* `cap1-hard-partial-amend`

---

**H3 — Corporate: Selective Stage + Discard + Amend**

*Skills tested:* SO 1.3 (selective stage), SO 1.6 (discard + unstage), SO 1.5 (amend)

*Context:* The repo has several things in play. `api/handler.py` is staged correctly.
`debug.py` is also staged but should not be — unstage it. `scratch.txt` has wrong
working-tree edits — discard them. Commit the staged `api/handler.py` with
"Fix request handler". Then realize the message needs a more precise scope —
amend to "Fix null pointer in API request handler".

*Expected commands:*
```
git restore --staged debug.py
git restore scratch.txt
git commit -m "Fix request handler"
git commit --amend -m "Fix null pointer in API request handler"
```

*Case ID:* `cap1-hard-selective-amend`

---

**H4 — Startup: Full Sprint Close**

*Skills tested:* SO 1.3 (commit), SO 1.4 (partial stage), SO 1.5 (amend), SO 1.6 (unstage), SO 1.8 (diagnostic)

*Context:* End of sprint. The repo needs:
(1) `git diff --staged` audit to see what's staged (diagnostic),
(2) Unstage `wip.py`, (3) Partial stage `auth.py` (hunk 1 only),
(4) Commit "Add authentication endpoint", (5) Amend to include `tests/test_auth.py`.

*Expected commands:*
```
git diff --staged
git restore --staged wip.py
git add -p
git commit -m "Add authentication endpoint"
git add tests/test_auth.py
git commit --amend --no-edit
```

*Case ID:* `cap1-hard-sprint-close`

---

**H5 — Freelance: New Project Setup + History Audit**

*Skills tested:* SO 1.2 (clone), SO 1.3 (stage + commit), SO 1.8 (diagnostic log)

*Context:* Clone the client's existing repo from `https://github.com/clientco/portal.git`
into `client-portal`, check the last 5 commits with `git log -n 5` to understand history,
then create `hotfix.py`, stage it, and commit "Add emergency hotfix".

*Expected commands:*
```
git clone https://github.com/clientco/portal.git client-portal
git log -n 5
git add hotfix.py
git commit -m "Add emergency hotfix"
```

*Case ID:* `cap1-hard-clone-history`

---

## Seed Implementation Notes

### Case ID naming convention

Format: `{lesson-abbrev}-{difficulty}-{distinguishing-term}`

| Seed Lesson | SO | Abbrev |
|-------------|-----|--------|
| Lesson 1 — Init | SO 1.1 | `init` |
| Lesson 2 — Clone | SO 1.2 | `clone` |
| Lesson 3 — Commit | SO 1.3 | `commit` |
| Lesson 4 — Ignore | ⚠️ FLAGGED | `ignore` — do not expand |
| Lesson 5 — Partial | SO 1.4 | `partial` |
| Lesson 6 — Amend | SO 1.5 | `amend` |
| Lesson 7 — Restore | SO 1.6 | `restore` |
| Lesson 8 — Integration | Multi-SO | `cap1` |

Keep case IDs under 30 characters. The first 18 characters after slugification
must be unique within the scenario × difficulty pool.

### Pool sizes

All pools in this guide meet the minimum (completion + 2).
During seed implementation, verify with a count assertion before running the seeder.

### Randomization

The platform selects variants randomly from the pool for each session.
The seed must not hard-code variant order — use random selection or leave ordering
to the platform's session creation logic.

### `required_attempts` override

UI Lesson 1 (SO 1.1 — Init) Easy: `required_attempts=1` (not the default 3).
All other lessons use the defaults from `SESSION_COUNTS`.

### Context string pattern (reference implementation for all modules)

Module 1 is the **reference implementation** for the `{{context}}` placeholder pattern.
All other modules (2, 3, 4) must follow this same approach.

**Pattern:**

1. `student_context_template(kind)` returns `"story": "{{context}}"` for every kind.
   The static story strings that existed before redesign have been replaced.

2. Every case helper (`commit_case`, `partial_case`, `amend_case`, `restore_case`,
   `review_clean_case`) accepts a `context: str = ""` keyword argument and forwards it
   into the case dict as `"context": context`.

3. The raw `restore-easy-discard` case dict includes `"context"` inline (it cannot use
   `restore_case()` because empty `initial_staging` generates an invalid command).

4. Each case call passes the *Context:* narrative paragraph from this guide as the
   `context=` argument. The materializer substitutes `{{context}}` into the Scenario Brief.

**Why this matters:** The `{{context}}` approach ensures every scenario has a distinct,
rich student-facing narrative. Without it, all variants in the same lesson kind share the
same generic story, which makes harder difficulties feel like parameter substitutions.

**Validated:** `--validate-build` confirmed all 97 Module 1 variants pass with context
strings in place. The seed is live in the DB as of 2026-05-29.

**Answer key:** [docs/curriculum-redesign/MODULE_1_ANSWERKEY.md](MODULE_1_ANSWERKEY.md)
lists every case ID, context brief, and solution commands for instructor reference.

### State-Based Evaluator

All scenarios in this module use `completion_type = "state_based"`.
The evaluator checks the final repository state, not the sequence of commands.
Multiple valid solution paths are acceptable — the evaluator does not penalize
alternative approaches as long as the final state matches `target_state`.

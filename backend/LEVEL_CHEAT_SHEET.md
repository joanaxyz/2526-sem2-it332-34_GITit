# GIT it! — All-level command cheat sheet

Generated from the live seeded curriculum on 2026-07-17. Covers **240 levels**, **582 waves**, and **1294 authored variants** across all three stories.

Use the sequence for the variant whose story details, file names, branch names, commit IDs, or URLs match the level shown in the frontend. Commands on one row must be submitted left-to-right.

## Quick totals

| Story | Levels | Waves |
|---|---:|---:|
| The Arcane Spire | 69 | 364 |
| Frostbound Citadel | 106 | 139 |
| Neon Backstreets | 65 | 79 |

## The Arcane Spire

### Chapter 01: Repository Foundations

#### Level 1: Start a Repository

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Create repository metadata | All variants | `git init` |
| 2. Initialize named folder | All variants | `git init project` |
| 3. Choose first branch | All variants | `git init -b main` |

#### Level 2: Read the Workspace

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read plain status | All variants | `git status` |
| 2. Read an unstaged change | All variants | `git diff` |
| 3. Read before touching | All variants | `git status` → `git diff` |

#### Level 3: Stage and Commit

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stage one file | All variants | `git add README.md` |
| 2. Commit staged work | All variants | `git commit -m 'Save staged work'` |
| 3. Stage the whole folder | All variants | `git add .` |
| 4. First save workflow | All variants | `git status` → `git add README.md` → `git commit -m 'Save first feature'` |

#### Level 4: The First Snapshot

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Initialize current folder | All variants | `git init` → `git add .` → `git commit -m 'Initial commit'` |
| 2. Read the staged snapshot | All variants | `git diff --staged` |
| 3. Diff before staging | All variants | `git diff` → `git add README.md` → `git commit -m 'Save reviewed edit'` |
| 4. Diff staged work | All variants | `git diff --staged` → `git commit -m 'Save staged edit'` |
| 5. Save folder work | All variants | `git add .` → `git commit -m 'Save folder work'` |

#### Level 5: Practice Fresh Starts

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Found a docs site | All variants | `git init` → `git add .` → `git commit -m 'Publish docs seed'` |
| 2. Set up a named tool folder | All variants | `git init tool-kit` → `git add .` → `git commit -m 'Tool kit start'` |
| 3. Start history on trunk | All variants | `git init -b trunk` → `git add .` → `git commit -m 'Start on trunk'` |

#### Level 6: Read History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read compact history | All variants | `git log --oneline` |
| 2. Graph every ref | All variants | `git log --oneline --graph --all` |
| 3. Limit history output | All variants | `git log -n 2` |
| 4. Compact history | All variants | `git log --oneline` → `git add REVIEW.md` → `git commit -m 'Add review note'` |
| 5. Graph history | All variants | `git log --oneline --graph --all` → `git add GRAPH.md` → `git commit -m 'Document branch tip'` |

#### Level 7: Inspect Commits

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the newest snapshot | All variants | `git show` |
| 2. Inspect a named snapshot | All variants | `git show c0` |
| 3. List a snapshot's paths | All variants | `git show --name-only c0` |
| 4. Show a commit | All variants | `git show c0` → `git add CHANGELOG.md` → `git commit -m 'Add changelog note'` |

#### Level 8: History Details

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read history as patches | All variants | `git log -p` |
| 2. Read history change summaries | All variants | `git log --stat` |
| 3. Detailed history audit | All variants | `git log -n 1` → `git log -p` → `git log --stat` → `git show --name-only c0` → `git add AUDIT.md` → `git commit -m 'Add audit note'` |
| 4. Audit then record findings | All variants | `git log --stat` → `git show` → `git add AUDIT.md` → `git commit -m 'Record audit findings'` |

#### Level 9: Status at a Glance

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read compact status | All variants | `git status -s` |
| 2. Read script-stable status | All variants | `git status --porcelain` |
| 3. Compact script status | All variants | `git status -s` → `git status --porcelain` → `git add README.md` → `git commit -m 'Save compact status work'` |
| 4. Glance then save everything | All variants | `git status -s` → `git add .` → `git commit -m 'Save inspected work'` → `git log --oneline` |

#### Level 10: Copy a Project

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Copy a remote project | All variants | `git clone https://example.test/team/app.git` |
| 2. Copy into a chosen folder | All variants | `git clone https://example.test/team/app.git starter-copy` |
| 3. Copy a specific branch | All variants | `git clone -b starter https://example.test/team/app.git` |
| 4. Copy only recent history | All variants | `git clone --depth 1 https://example.test/team/app.git` |

#### Level 11: Inspect What You Cloned

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Clone default folder | All variants | `git clone https://example.test/team/app.git` → `git status` |
| 2. Clone named folder | All variants | `git clone https://example.test/team/app.git app-copy` → `git log --oneline` |
| 3. Clone specific branch | All variants | `git clone -b starter https://example.test/team/app.git` → `git status` |
| 4. Clone shallow history | All variants | `git clone --depth 1 https://example.test/team/app.git` → `git log --oneline` |

#### Level 12: Clone Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Copy to a lab folder and verify | All variants | `git clone https://example.test/team/app.git app-lab` → `git status` |
| 2. Copy a branch and map it | All variants | `git clone -b starter https://example.test/team/app.git` → `git log --oneline --graph --all` |
| 3. Shallow copy, shallow read | All variants | `git clone --depth 1 https://example.test/team/app.git` → `git log -n 1` |
| 4. Copy then open the newest snapshot | All variants | `git clone https://example.test/team/app.git` → `git show` |
| 5. Fresh workspace, not a copy | All variants | `git init scratch-pad` → `git status` |

#### Level 13: Configure Identity and Aliases

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Set user name | All variants | `git config --global user.name 'Learner A'` |
| 2. Set user email | All variants | `git config --global user.email learner-a@example.test` |
| 3. List effective settings | All variants | `git config --list` |
| 4. Create a status shortcut | All variants | `git config --global alias.st status` |
| 5. List config | All variants | `git config --list` → `git add README.md` → `git commit -m 'Save verified identity'` |
| 6. Create alias | All variants | `git config --global alias.st status` → `git config --list` → `git add README.md` → `git commit -m 'Save alias setup'` |

#### Level 14: Ignore Noise

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. See what Git ignores | All variants | `git status --ignored` |
| 2. Trace an ignore rule | All variants | `git check-ignore -v build.log` |
| 3. Write ignore rule | All variants | `git status --ignored` → `git add .gitignore src/app.py` → `git commit -m 'Ignore build output'` |
| 4. Explain ignore rule | All variants | `git check-ignore -v build.log` → `git add src/app.py` → `git commit -m 'Save source without build log'` |

#### Level 15: Founding Workflows

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Found a project with identity | All variants | `git init` → `git config --global user.name 'Learner A'` → `git config --global user.email learner-a@example.test` → `git add .` → `git commit -m 'Initial commit'` |
| 2. Initialize, inspect, save, verify | All variants | `git init` → `git status` → `git add .` → `git commit -m 'First snapshot'` → `git log --oneline` |
| 3. Found a studio workspace | All variants | `git init studio` → `git status` → `git add .` → `git commit -m 'Studio setup'` |
| 4. Review every angle, then save | All variants | `git status` → `git diff` → `git add README.md` → `git diff --staged` → `git commit -m 'Save reviewed work'` |
| 5. Build history in two snapshots | All variants | `git init` → `git add README.md` → `git commit -m 'Add readme'` → `git add .` → `git commit -m 'Add source'` → `git log --oneline` |
| 6. Adopt ignore rules end to end | All variants | `git status --ignored` → `git check-ignore -v build.log` → `git add .gitignore src/app.py` → `git commit -m 'Adopt ignore rules'` |

#### Level 16: Fresh Start Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Create an archive workspace | All variants | `git init archive-lab` → `git status -s` |
| 2. Found a field-notes workspace | All variants | `git init field-notes` → `git add .` → `git commit -m 'Field notes start'` |
| 3. Begin on the release line | All variants | `git init -b release` → `git status` |
| 4. Docs history on its own line | All variants | `git init -b docs-main` → `git add .` → `git commit -m 'Docs baseline'` |
| 5. Branch copy, compact check | All variants | `git clone -b starter https://example.test/team/app.git` → `git status -s` |
| 6. Shallow copy, open the tip | All variants | `git clone --depth 1 https://example.test/team/app.git` → `git show` |

#### Level 17: Inspection Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Script check mid-snapshot | All variants | `git status --porcelain` |
| 2. Set up a fresh machine | All variants | `git config --global user.name 'Learner C'` → `git config --global user.email learner-c@example.test` → `git config --list` |
| 3. Create a history shortcut | All variants | `git config --global alias.lg log` → `git config --list` |
| 4. Describe the latest change | All variants | `git show c1` → `git add CHANGELOG.md` → `git commit -m 'Describe latest change'` |
| 5. Patch review, then a note | All variants | `git log -p` → `git add REVIEW.md` → `git commit -m 'Record patch review'` |
| 6. Path audit, then a note | All variants | `git show --name-only c0` → `git add AUDIT.md` → `git commit -m 'List first commit paths'` |

### Chapter 02: Tracking Changes and Snapshots

#### Level 1: See What Changed

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List changed paths only | All variants | `git diff --name-only` |
| 2. Review both sides of the index | All variants | `git diff` → `git add README.md` → `git diff --staged` |
| 3. Triage from paths to patches | All variants | `git status -s` → `git diff --name-only` → `git diff` |

#### Level 2: Choose What Enters the Snapshot

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stage all changes | All variants | `git add -A` |
| 2. Stage tracked only | All variants | `git add -u` |
| 3. Stage selected hunks | All variants | `git add -p src/app.py` |
| 4. Changed paths only | All variants | `git diff --name-only` → `git add README.md` → `git commit -m 'Save selected path'` |

#### Level 3: Precision Staging Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Sweep tracked edits into a commit | All variants | `git status --porcelain` → `git add -u` → `git commit -m 'Save tracked work'` |
| 2. Stage everything, verify the landing | All variants | `git status -s` → `git add -A` → `git commit -m 'Save everything'` → `git log --oneline` |
| 3. Ship only the fix hunk | All variants | `git add -p src/app.py` → `git diff --staged` → `git commit -m 'Ship only the fix'` |
| 4. Stage tracked, prove the rest stayed | All variants | `git status --porcelain` → `git add -u` |
| 5. Batch stage, script check | All variants | `git add -A` → `git status --porcelain` |
| 6. Paths first, then sweep | All variants | `git diff --name-only` → `git add -u` → `git commit -m 'Save listed paths'` |

#### Level 4: Shape Two Snapshots

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Split messy work | All variants | `git add -p src/app.py` → `git commit -m 'Save app fix'` → `git add -A` → `git commit -m 'Save remaining cleanup'` |
| 2. Split a batch by path list | All variants | `git diff --name-only` → `git add README.md` → `git commit -m 'Save the real edit'` → `git add -A` → `git commit -m 'Save the rest'` |
| 3. Sweep tracked edits deliberately | All variants | `git status -s` → `git diff --name-only` → `git add -u` → `git diff --staged` → `git commit -m 'Sweep tracked edits'` |
| 4. Stage a folder, prove it, seal it | All variants | `git add -A` → `git diff --staged` → `git commit -m 'Save the whole batch'` |

#### Level 5: Commit Tracked Work Directly

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Commit tracked directly | All variants | `git commit -a -m 'Save tracked edits'` |
| 2. Direct commit, verified landing | All variants | `git status -s` → `git commit -a -m 'Ship tracked fix'` → `git log --oneline` |
| 3. Direct commit, sized audit | All variants | `git commit -a -m 'Record tracked update'` → `git log --stat` |

#### Level 6: Amend Local History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Amend message or content | All variants | `git commit --amend -m 'Clarify local commit'` |
| 2. Fold staged work into the last commit | All variants | `git commit --amend --no-edit` |
| 3. Amend without message change | All variants | `git add README.md` → `git commit --amend --no-edit` |
| 4. Inspect, then rewrite in place | All variants | `git show` → `git log -n 1` → `git commit --amend -m 'Describe the shell update'` |
| 5. Fix identity, restamp the commit | All variants | `git config --global user.name 'Learner E'` → `git config --global user.email learner-e@example.test` → `git commit --amend --no-edit` |
| 6. Amend, then audit the rewrite | All variants | `git add README.md` → `git commit --amend --no-edit` → `git show` → `git log -p` |

#### Level 7: Sealing Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Review, script-check, seal | All variants | `git diff` → `git status --porcelain` → `git commit -a -m 'Save the reviewed pass'` |
| 2. Rename the snapshot, prove it | All variants | `git commit --amend -m 'Name the feature properly'` → `git show` |
| 3. Audit sizes, then seal the note | All variants | `git log --stat` → `git log -p` → `git show --name-only c0` → `git commit -a -m 'Record audit pass'` |
| 4. Quick save, quick look | All variants | `git commit -a -m 'Note the tweak'` → `git show` |
| 5. Confirm scope, then rewrite | All variants | `git log -n 1` → `git commit --amend -m 'Describe the auth work'` |
| 6. Sweep, fold, audit | All variants | `git add -u` → `git commit --amend --no-edit` → `git log --stat` |

#### Level 8: Fix Staging Mistakes

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Unstage one file | All variants | `git restore --staged README.md` |
| 2. Discard working edit | All variants | `git restore README.md` |
| 3. Repair before commit | All variants | `git status` → `git restore --staged scratch.txt` → `git restore debug.log` → `git add -p src/app.py` → `git commit -m 'Commit real fix'` |
| 4. Unstage, re-read, discard | All variants | `git restore --staged README.md` → `git diff` → `git restore README.md` |
| 5. Script-check, then repair | All variants | `git status --porcelain` → `git restore --staged scratch.txt` → `git restore debug.log` → `git add -p src/app.py` → `git commit -m 'Keep only the real fix'` |

#### Level 9: Remove or Stop Tracking Files

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stage a file's removal | All variants | `git rm old.txt` |
| 2. Stop tracking, keep the file | All variants | `git rm --cached .env` |
| 3. Stop tracking a directory | All variants | `git rm -r --cached dist` |
| 4. Remove tracked file | All variants | `git rm old.txt` → `git commit -m 'Remove obsolete file'` |
| 5. Untrack local file | All variants | `git rm --cached .env` → `git commit -m 'Stop tracking local config'` |
| 6. Untrack generated directory | All variants | `git rm -r --cached dist` → `git add .gitignore` → `git commit -m 'Stop tracking build output'` |
| 7. Clean tracked junk | All variants | `git rm old.txt` → `git rm --cached .env` → `git add .gitignore` → `git commit -m 'Clean tracked junk'` |

#### Level 10: Verify the Cleanup

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Untrack, protect, prove | All variants | `git rm --cached .env` → `git add .gitignore` → `git commit -m 'Ignore local config'` → `git status --ignored` |
| 2. Untrack, then trace the shield | All variants | `git rm --cached .env` → `git add .gitignore` → `git commit -m 'Stop tracking secrets'` → `git status --ignored` → `git check-ignore -v .env` |
| 3. Preview a directory untracking | All variants | `git rm -r --cached dist` → `git status --porcelain` |
| 4. Drop build output, verify twice | All variants | `git rm -r --cached dist` → `git add .gitignore` → `git commit -m 'Drop build output'` → `git status --ignored` → `git check-ignore -v dist/app.js` |
| 5. Untrack artifacts, trace the rule | All variants | `git rm -r --cached dist` → `git add .gitignore` → `git commit -m 'Ignore build artifacts'` → `git check-ignore -v dist/app.css` |
| 6. Remove, then audit the origin | All variants | `git rm old.txt` → `git commit -m 'Drop the obsolete file'` → `git show --name-only c0` |

#### Level 11: Undo Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Glance, then discard | All variants | `git status -s` → `git restore README.md` |
| 2. Script-check, then unstage | All variants | `git status --porcelain` → `git restore --staged README.md` |
| 3. Hand back a pristine machine | All variants | `git config --global user.name 'Learner D'` → `git config --global user.email learner-d@example.test` → `git config --list` → `git restore --staged README.md` → `git restore README.md` |
| 4. Unstage junk, sweep the real work | All variants | `git restore --staged scratch.txt` → `git add -u` → `git commit -m 'Stage the right batch'` |
| 5. Confirm, then retire a file | All variants | `git status --porcelain` → `git rm old.txt` → `git commit -m 'Retire the old notes'` |
| 6. Untrack and see the shield | All variants | `git rm --cached .env` → `git status --ignored` |
| 7. Untrack the regenerating bundle | All variants | `git rm -r --cached dist` → `git commit -m 'Untrack generated output'` |

### Chapter 03: Branch Navigation

#### Level 1: Create and Inspect Branches

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List branches | All variants | `git branch` |
| 2. Create branch | All variants | `git branch release` |
| 3. Create branch at start | All variants | `git branch hotfix c0` |
| 4. Verbose branches | All variants | `git branch -v` |
| 5. Survey, then add a pointer | All variants | `git branch` → `git branch feature/audit` |
| 6. Compare tips, pin the archive | All variants | `git branch -v` → `git branch archive c1` |

#### Level 2: Move HEAD

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Step onto another branch | All variants | `git switch feature/ui` |
| 2. Create and step on in one move | All variants | `git switch -c feature/new` |
| 3. The older create-and-switch spelling | All variants | `git checkout -b legacy/feature` |
| 4. Inspect detached | All variants | `git switch --detach c0` |

#### Level 3: Move HEAD Safely

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Switch existing | All variants | `git switch feature/ui` → `git add README.md` → `git commit -m 'Work on feature'` |
| 2. Switch create | All variants | `git switch -c feature/new` → `git add README.md` → `git commit -m 'Start new feature'` |
| 3. Checkout legacy create | All variants | `git checkout -b legacy/feature` → `git add README.md` → `git commit -m 'Start legacy branch'` |
| 4. Map the graph, then move | All variants | `git log --oneline --graph --all` → `git branch` → `git switch feature/ui` |
| 5. Inspect detached, report on main | All variants | `git switch --detach c1` → `git show` → `git switch main` → `git add README.md` → `git commit -m 'Record inspection'` |

#### Level 4: Start Lines Deliberately

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. New project on the trunk line | All variants | `git init -b trunk` → `git add .` → `git commit -m 'Trunk baseline'` → `git branch` |
| 2. Baseline, then a kickoff line | All variants | `git init -b main` → `git add .` → `git commit -m 'Product baseline'` → `git branch feature/kickoff` |
| 3. A shortcut for moving around | All variants | `git config --global alias.sw switch` → `git config --list` → `git switch feature/ui` |

#### Level 5: Branch Workflows with Clean Snapshots

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Branch for feature | All variants | `git status` → `git switch -c feature/report` → `git add -p src/app.py` → `git commit -m 'Add report feature'` |
| 2. Branch from release | All variants | `git branch hotfix c0` → `git switch hotfix` → `git add README.md` → `git commit -m 'Patch release note'` |
| 3. Recover detached work | All variants | `git switch --detach c0` → `git add README.md` → `git commit -m 'Detached useful work'` → `git branch rescue HEAD` → `git switch rescue` |
| 4. New line, then map the result | All variants | `git switch -c feature/notes` → `git add README.md` → `git commit -m 'Draft notes'` → `git log --oneline --graph --all` |
| 5. Hotfix the legacy way | All variants | `git checkout -b hotfix/legacy` → `git add README.md` → `git commit -m 'Legacy hotfix'` → `git branch -v` |

#### Level 6: Delete Branch Pointers Deliberately

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Delete merged branch | All variants | `git branch -d old` |
| 2. Force delete scratch branch | All variants | `git branch -D scratch` |
| 3. Branch cleanup workflow | All variants | `git log --oneline --graph --all` → `git branch -v` → `git branch -d old` → `git branch -D scratch` |
| 4. Survey, then retire a pointer | All variants | `git branch` → `git branch -d old` |
| 5. Compare tips, then force-remove | All variants | `git branch -v` → `git branch -D scratch` |

#### Level 7: Branch Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stage two environments | All variants | `git branch staging` → `git branch qa` → `git branch` → `git branch -v` |
| 2. One pointer per task | All variants | `git branch task/login` → `git branch task/search` → `git branch task/profile` → `git branch` |
| 3. Tour the lines, land on old | All variants | `git branch` → `git switch feature/ui` → `git switch old` |
| 4. Legacy spelling, quick fix line | All variants | `git checkout -b fix/typo` → `git branch -v` |
| 5. Detached audit of an old tip | All variants | `git switch --detach c1` → `git show` |
| 6. Pin the release history | All variants | `git branch release/v1 c0` → `git branch release/v2 c1` → `git branch integration` → `git branch` |

#### Level 8: Cleanup Gauntlet

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Retire both kinds of clutter | All variants | `git branch` → `git branch -d old` → `git branch -D scratch` |
| 2. Retire, then verify the list | All variants | `git branch -d old` → `git branch -v` |
| 3. Force-remove, then redraw | All variants | `git branch -D scratch` → `git log --oneline --graph --all` |
| 4. Prune one, pin one | All variants | `git branch -d old` → `git branch keep c1` → `git branch` |
| 5. Force-remove, read the story | All variants | `git branch -D scratch` → `git log --oneline` |

### Chapter 04: Merging and Conflict Resolution

#### Level 1: Understand Merge Shape

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Find merge base | All variants | `git merge-base main feature/profile` |
| 2. Merge fast-forward | All variants | `git merge feature/profile` |
| 3. Merge no fast-forward | All variants | `git merge --no-ff feature/profile` |
| 4. Stage a branch as one snapshot | All variants | `git merge --squash feature/profile` |
| 5. Merge squash | All variants | `git merge --squash feature/profile` → `git commit -m 'Squash profile feature'` |

#### Level 2: Merge Real Histories

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Find the base, then integrate | All variants | `git merge-base main feature/profile` → `git merge feature/profile` |
| 2. Map, measure, merge visibly | All variants | `git log --oneline --graph --all` → `git merge-base main feature/profile` → `git merge --no-ff feature/profile` |
| 3. Branch out, merge back | All variants | `git switch -c feature/notes` → `git add README.md` → `git commit -m 'Notes update'` → `git switch main` → `git merge feature/notes` |
| 4. Policy: keep the branch visible | All variants | `git merge --no-ff feature/profile` → `git log --oneline --graph --all` |
| 5. Verify the fast-forward, then take it | All variants | `git branch -v` → `git merge-base main feature/profile` → `git merge feature/profile` |

#### Level 3: Abort and Retry

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Abort conflicted merge | All variants | `git merge --abort` |
| 2. Retry correct merge | All variants | `git merge --abort` → `git switch main` → `git merge feature/profile` |
| 3. Read, back out, confirm | All variants | `git log --oneline --graph --all` → `git merge --abort` → `git status` |
| 4. Script-check the damage, then retreat | All variants | `git status --porcelain` → `git merge --abort` → `git status` |

#### Level 4: Read the Conflict

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read our side of the conflict | All variants | `git diff --ours src/auth.js` |
| 2. Read their side of the conflict | All variants | `git diff --theirs src/auth.js` |
| 3. List unmerged files | All variants | `git ls-files -u` |
| 4. Diff conflict base | All variants | `git diff --base src/auth.js` |
| 5. Diff conflict sides | All variants | `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` |
| 6. Base, ours, theirs: full picture | All variants | `git diff --base src/auth.js` → `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` |
| 7. Launch mergetool | All variants | `git mergetool` |

#### Level 5: Choose a Side

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Keep our version | All variants | `git checkout --ours src/auth.js` |
| 2. Take the incoming version | All variants | `git checkout --theirs src/auth.js` |
| 3. Finish a resolved merge | All variants | `git merge --continue` |

#### Level 6: Resolve Conflicts and Finish

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Take ours | All variants | `git checkout --ours src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 2. Take theirs | All variants | `git checkout --theirs src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 3. Manual mixed resolution | All variants | `git ls-files -u` → `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` → `git checkout --theirs src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 4. Two-file conflict workflow | All variants | `git checkout --ours src/auth.js` → `git add src/auth.js` → `git merge --continue` |

#### Level 7: Evidence-First Resolutions

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare both, keep ours | All variants | `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` → `git checkout --ours src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 2. Full evidence, incoming wins | All variants | `git diff --base src/auth.js` → `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` → `git checkout --theirs src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 3. Tool-assisted resolution | All variants | `git mergetool` → `git add src/auth.js` → `git merge --continue` |
| 4. Inherited resolution, finish it | All variants | `git status` → `git merge --continue` → `git log --oneline --graph --all` |
| 5. List, choose incoming, finish | All variants | `git ls-files -u` → `git checkout --theirs src/auth.js` → `git add src/auth.js` → `git merge --continue` |

#### Level 8: Merge Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Squash, seal, read the story | All variants | `git merge --squash feature/profile` → `git commit -m 'Fold profile work'` → `git log --oneline` |
| 2. Squash, inspect, then seal | All variants | `git merge --squash feature/profile` → `git diff --staged` → `git commit -m 'Land squashed feature'` |
| 3. Squash with a state check | All variants | `git merge --squash feature/profile` → `git status` → `git commit -m 'Squash with checks'` |
| 4. Find the split, open it | All variants | `git merge-base main feature/profile` → `git show c0` |
| 5. Refuse the silent fast-forward | All variants | `git merge-base main feature/profile` → `git merge --no-ff feature/profile` → `git log --oneline --graph --all` |
| 6. Scope it, then abandon it | All variants | `git ls-files -u` → `git merge --abort` |
| 7. Base first, then the tool | All variants | `git diff --base src/auth.js` → `git mergetool` |
| 8. Read every version, then the tool | All variants | `git diff --base src/auth.js` → `git diff --ours src/auth.js` → `git diff --theirs src/auth.js` → `git mergetool` |

#### Level 9: Resolution Gauntlet

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve, finish, map the join | All variants | `git checkout --ours src/auth.js` → `git add src/auth.js` → `git merge --continue` → `git log --oneline --graph --all` |
| 2. Verify, keep ours, finish | All variants | `git diff --ours src/auth.js` → `git checkout --ours src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 3. Verify, take theirs, finish | All variants | `git diff --theirs src/auth.js` → `git checkout --theirs src/auth.js` → `git add src/auth.js` → `git merge --continue` |
| 4. Tool, stage, finish, confirm | All variants | `git mergetool` → `git add src/auth.js` → `git merge --continue` → `git status` |
| 5. Scope, tool, finish, map | All variants | `git ls-files -u` → `git mergetool` → `git add src/auth.js` → `git merge --continue` → `git log --oneline --graph --all` |
| 6. Abandon, then survey the field | All variants | `git ls-files -u` → `git diff --base src/auth.js` → `git merge --abort` → `git log --oneline --graph --all` |

#### Level 10: Integration Capstones

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Isolate, finish, integrate visibly | All variants | `git switch -c feature/banner` → `git add README.md` → `git commit -m 'Banner work'` → `git switch main` → `git merge --no-ff feature/banner` |
| 2. Insurance first, then integrate | All variants | `git merge-base main feature/profile` → `git branch backup/main` → `git merge feature/profile` → `git log --oneline` |
| 3. Compact landing | All variants | `git merge --squash feature/profile` → `git commit -m 'Compact the feature'` |
| 4. Integrate, map, tidy up | All variants | `git merge --no-ff feature/profile` → `git log --oneline --graph --all` → `git branch -d feature/profile` |
| 5. Another service lands | All variants | `git merge feature/profile` → `git log --oneline --graph --all` |

### Chapter 05: Undoing and Recovery

#### Level 1: Read Recovery Clues

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read reflog | All variants | `git reflog` |
| 2. Two views of recent history | All variants | `git reflog` → `git log --oneline` |
| 3. Interrogate the suspect commit | All variants | `git log -n 2` → `git show c2` |
| 4. Full patches, then the path list | All variants | `git log -p` → `git show --name-only c2` |
| 5. Stand inside the suspect commit | All variants | `git switch --detach c2` → `git show` |

#### Level 2: Move Private History Back

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Reset hard to commit | All variants | `git reset --hard c1` |
| 2. Reset hard parent | All variants | `git reset --hard HEAD~1` |
| 3. Branch before reset | All variants | `git branch backup HEAD` → `git reset --hard HEAD~1` |
| 4. Confirm the target, then step back | All variants | `git show c2` → `git reset --hard c1` |
| 5. Preview the past, then adopt it | All variants | `git switch --detach c1` → `git switch main` → `git reset --hard HEAD~1` |
| 6. Safety net, then the rewrite | All variants | `git branch safety-net` → `git reset --hard c1` |
| 7. The smallest undo that works | All variants | `git log -n 1` → `git commit --amend -m 'Correct the release note'` |
| 8. Fold the fix, keep the history | All variants | `git status -s` → `git add README.md` → `git commit --amend --no-edit` |

#### Level 3: Private History Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read, then step back by name | All variants | `git log --oneline` → `git reset --hard c1` |
| 2. Check, then step back one | All variants | `git status` → `git reset --hard HEAD~1` |
| 3. Record the before, then step back | All variants | `git reflog` → `git reset --hard HEAD~1` |
| 4. A removal, regretted entirely | All variants | `git rm old.txt` → `git commit -m 'Retire junk note'` → `git reset --hard HEAD~1` |
| 5. A shortcut for stepping back | All variants | `git config --global alias.undo reset` → `git config --list` |

#### Level 4: Undo Shared Work Safely

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Revert one commit | All variants | `git revert c2` |
| 2. Revert no edit | All variants | `git revert --no-edit c2` |
| 3. Revert then fix | All variants | `git revert c2` → `git add README.md` → `git commit -m 'Add safer replacement'` |
| 4. Fast reversal, quick read | All variants | `git revert --no-edit c2` → `git log --oneline` |
| 5. Reverse, then open the result | All variants | `git revert --no-edit c2` → `git show` |
| 6. Reverse, then size the damage | All variants | `git revert --no-edit c2` → `git log --stat` |
| 7. Map the shared line, then reverse | All variants | `git log --oneline --graph --all` → `git revert c2` |

#### Level 5: Recover After a Mistake

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Recover lost tip | All variants | `git reflog` → `git branch recovered c2` → `git switch recovered` |
| 2. Restore main from reflog | All variants | `git reflog` → `git reset --hard HEAD@{0}` |
| 3. Choose reset or revert | All variants | `git log --oneline --graph --all` → `git show c2` → `git revert c2` |
| 4. What the log forgot | All variants | `git reflog` → `git log --oneline` |
| 5. Restore the tip, mark it safe | All variants | `git reflog` → `git reset --hard HEAD@{0}` → `git branch confirmed` |
| 6. Reverse, then read the room | All variants | `git revert --no-edit c2` → `git status` |
| 7. Reflog first, reverse fast | All variants | `git reflog` → `git revert --no-edit c2` |
| 8. Reverse on a dedicated line | All variants | `git switch -c fix/rollback` → `git revert c2` |
| 9. Reverse, then map the record | All variants | `git revert c2` → `git log --oneline --graph --all` |

### Chapter 06: Temporary Work and Patch Movement

#### Level 1: Shelve Local Work

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stash current work | All variants | `git stash` |
| 2. List stashes | All variants | `git stash list` |
| 3. Stash before switch | All variants | `git status` → `git stash` → `git switch hotfix/navbar` |

#### Level 2: Restore Stashed Work

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pop stash | All variants | `git stash pop` |
| 2. Apply stash | All variants | `git stash apply` |
| 3. Drop stash | All variants | `git stash drop` |
| 4. Stash restore commit | All variants | `git stash` → `git switch hotfix/navbar` → **Project Files:** edit `README.md`, set content to `"base\nUrgent navbar fix\n"`, and click **Save** → `git add README.md` → `git commit -m 'Commit urgent fix'` → `git switch main` → `git stash pop` → `git add src/app.py` → `git commit -m 'Save restored WIP'` |

#### Level 3: Manage the Stash Stack

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the shelf, then restore | All variants | `git stash list` → `git stash pop` |
| 2. Check the shelf, restore a copy | All variants | `git stash list` → `git stash apply` |
| 3. Check the shelf, then clear it | All variants | `git stash list` → `git stash drop` → `git status` |
| 4. Restore a copy, land it | All variants | `git stash apply` → `git add src/app.py` → `git commit -m 'Land restored work'` |
| 5. Restore, verify, then clear | All variants | `git stash apply` → `git stash drop` |
| 6. One full shelf cycle | All variants | `git stash` → `git stash list` → `git stash pop` |

#### Level 4: Interruption Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Interrupt, fix, restore carefully | All variants | `git stash` → `git switch hotfix/navbar` → **Project Files:** edit `README.md`, set content to `"base\nQuick navbar patch\n"`, and click **Save** → `git add README.md` → `git commit -m 'Quick navbar patch'` → `git switch main` → `git stash apply` → `git stash drop` |
| 2. Clear the shelf, prove it | All variants | `git stash drop` → `git stash list` |
| 3. Restore onto a fresh line | All variants | `git switch -c feature/wip-landing` → `git stash pop` → `git add src/app.py` → `git commit -m 'Land WIP on its own line'` |
| 4. Old spelling, careful restore | All variants | `git checkout -b review/stash-check` → `git stash apply` |
| 5. Glance, then clear the shelf | All variants | `git status -s` → `git stash drop` |

#### Level 5: Move One Commit

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Cherry-pick one | All variants | `git cherry-pick c2` |
| 2. Cherry-pick no commit | All variants | `git cherry-pick --no-commit c2` |
| 3. Abort cherry-pick | All variants | `git cherry-pick --abort` |

#### Level 6: Patch Movement Workflows

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pick then adjust | All variants | `git cherry-pick --no-commit c2` → **Project Files:** edit `src/auth.py`, set content to `"guard\nadapted=True\n"`, and click **Save** → `git add src/auth.py` → `git commit -m 'Adapt picked fix'` |
| 2. Stash and pick | All variants | `git stash` → `git cherry-pick c2` → `git stash pop` → `git add README.md` → `git commit -m 'Restore WIP after pick'` |
| 3. Abort then pick right commit | All variants | `git cherry-pick --abort` → `git cherry-pick c2` |

#### Level 7: Transplant Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Transplant, then read the record | All variants | `git cherry-pick c2` → `git log --oneline` |
| 2. Open it first, then transplant | All variants | `git show c2` → `git cherry-pick c2` |
| 3. Stage the patch, review, seal | All variants | `git cherry-pick --no-commit c2` → `git diff --staged` → `git commit -m 'Reviewed transplant'` |
| 4. Combine the patch with local work | All variants | `git cherry-pick --no-commit c2` → `git add README.md` → `git commit -m 'Fix plus local note'` |
| 5. Read the wreck, back out | All variants | `git status` → `git cherry-pick --abort` |
| 6. Back out, then read the record | All variants | `git cherry-pick --abort` → `git log --oneline` |

#### Level 8: Transplant Capstones

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Abort, then transplant carefully | All variants | `git cherry-pick --abort` → `git cherry-pick --no-commit c2` → **Project Files:** edit `src/auth.py`, set content to `"guard\nadapted_after_abort=True\n"`, and click **Save** → `git add src/auth.py` → `git commit -m 'Adapted after abort'` |
| 2. Script-check, retreat, confirm | All variants | `git status --porcelain` → `git cherry-pick --abort` → `git status` |
| 3. Transplant, then open the result | All variants | `git cherry-pick c2` → `git show` |
| 4. Stage the patch, script-check it | All variants | `git cherry-pick --no-commit c2` → `git status --porcelain` |

### Chapter 07: Remotes and Collaboration

#### Level 1: Inspect Remote Setup

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List remotes | All variants | `git remote` |
| 2. List remote URLs | All variants | `git remote -v` |
| 3. Remote inspection workflow | All variants | `git remote -v` → `git log --oneline --graph --all` → `git status` |
| 4. Names first, state second | All variants | `git remote` → `git status` |
| 5. Identity before collaboration | All variants | `git config --global user.name 'Learner B'` → `git config --global user.email learner-b@example.test` → `git config --list` → `git remote -v` |
| 6. A shortcut for remote checks | All variants | `git config --global alias.rv remote` → `git remote -v` |

#### Level 2: Fresh Machine

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Copy down, check the wiring | All variants | `git clone https://example.test/team/app.git` → `git remote` |
| 2. Named copy, verified URLs | All variants | `git clone https://example.test/team/app.git team-app` → `git remote -v` |
| 3. Branch copy, wired and checked | All variants | `git clone -b starter https://example.test/team/app.git` → `git remote` |
| 4. Shallow copy, full wiring | All variants | `git clone --depth 1 https://example.test/team/app.git` → `git remote -v` |
| 5. Copy, then branch the old way | All variants | `git clone https://example.test/team/app.git` → `git checkout -b feature/onboarding` |
| 6. Sandbox copy, sandbox line | All variants | `git clone https://example.test/team/app.git sandbox` → `git switch -c experiment/sandbox` |
| 7. Copy, check, read the story | All variants | `git clone https://example.test/team/app.git` → `git status` → `git log --oneline` |
| 8. Review copy, recent entries | All variants | `git clone https://example.test/team/app.git review-copy` → `git log -n 2` |
| 9. Starter branch, newest snapshot | All variants | `git clone -b starter https://example.test/team/app.git` → `git show` |
| 10. CI copy, script-stable check | All variants | `git clone --depth 1 https://example.test/team/app.git` → `git status --porcelain` |

#### Level 3: Fetch Before Acting

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fetch origin | All variants | `git fetch origin` |
| 2. Fetch prune | All variants | `git fetch --prune` |
| 3. Fetch then branch | All variants | `git fetch origin` → `git branch feature/from-origin origin/main` → `git switch feature/from-origin` |
| 4. Refresh, then map both worlds | All variants | `git fetch origin` → `git log --oneline --graph --all` |
| 5. Check the wiring, prune the dead | All variants | `git remote -v` → `git fetch --prune` |
| 6. Prune, then admire the graph | All variants | `git fetch --prune` → `git log --oneline --graph --all` |
| 7. Names, prune, state | All variants | `git remote` → `git fetch --prune` → `git status` |

#### Level 4: Pull and Integrate

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pull default | All variants | `git pull` |
| 2. Pull rebase | All variants | `git pull --rebase` |
| 3. Pull with local work safe | All variants | `git stash` → `git pull --rebase` → `git stash pop` |
| 4. Sync, then read what arrived | All variants | `git pull` → `git log --oneline` |
| 5. Confirm clean, then sync | All variants | `git status` → `git pull` |
| 6. Look before you integrate | All variants | `git fetch origin` → `git log --oneline --graph --all` → `git pull` |
| 7. Replay, then read the new order | All variants | `git pull --rebase` → `git log --oneline` |
| 8. Verify the source, then sync | All variants | `git remote -v` → `git pull` |

#### Level 5: Upstream Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. The morning sync | All variants | `git status -s` → `git pull` |
| 2. Sync, then open the newest work | All variants | `git pull` → `git show` |
| 3. Replay, then check the top two | All variants | `git pull --rebase` → `git log -n 2` |
| 4. Replay, then confirm calm | All variants | `git pull --rebase` → `git status` |
| 5. Land the feature before sharing | All variants | `git merge feature/profile` → `git log --oneline` |
| 6. State check, then integrate | All variants | `git status` → `git merge feature/profile` |
| 7. Insurance pointer, then integrate | All variants | `git branch pre-merge-backup` → `git merge feature/profile` |

#### Level 6: Publish Work

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Push set upstream | All variants | `git push -u origin feature/payment` |
| 2. Push current | All variants | `git push` |
| 3. Force with lease | All variants | `git push --force-with-lease` |
| 4. Delete remote branch | All variants | `git push origin --delete feature/payment` |
| 5. Read the unshared work, then share | All variants | `git log -n 1` → `git push` |
| 6. Check, then share | All variants | `git status` → `git push` |
| 7. Share, then confirm calm | All variants | `git push` → `git status` |
| 8. Verify target, publish with tracking | All variants | `git remote -v` → `git push -u origin feature/payment` |
| 9. Publish, then read the record | All variants | `git push -u origin feature/payment` → `git log --oneline` |
| 10. First share, then the state | All variants | `git push -u origin feature/payment` → `git status` |

#### Level 7: Publish Drills

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Publish a rewrite, safely | All variants | `git log -n 1` → `git push --force-with-lease` |
| 2. Rewrite, then lease it out | All variants | `git commit --amend -m 'Payment: final copy'` → `git push --force-with-lease` |
| 3. Lease out, then confirm calm | All variants | `git push --force-with-lease` → `git status` |
| 4. Lease out, read the record | All variants | `git push --force-with-lease` → `git log --oneline` |
| 5. Verify, then retire remotely | All variants | `git remote -v` → `git push origin --delete feature/payment` |
| 6. Retire remotely, sweep locally | All variants | `git push origin --delete feature/payment` → `git fetch --prune` |
| 7. Retire, then redraw | All variants | `git push origin --delete feature/payment` → `git log --oneline --graph --all` |
| 8. Retire, then count the remotes | All variants | `git push origin --delete feature/payment` → `git remote` |
| 9. State first, then retire | All variants | `git status` → `git push origin --delete feature/payment` |
| 10. Share the fix, read the record | All variants | `git push` → `git log --oneline` |
| 11. Confirm the destination, then ship | All variants | `git remote -v` → `git push` |
| 12. Know the wiring, then publish | All variants | `git remote` → `git push -u origin feature/payment` |

#### Level 8: Full Collaboration Loops

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Branch publish merge cleanup | All variants | `git fetch origin` → `git switch -c feature/review` → `git add README.md` → `git commit -m 'Add review work'` → `git push -u origin feature/review` → `git fetch --prune` |
| 2. Sync diverged work | All variants | `git fetch origin` → `git pull --rebase` → `git push` |
| 3. Rewrite and lease | All variants | `git fetch origin` → `git commit --amend -m 'Correct local history'` → `git push --force-with-lease` |
| 4. The daily loop | All variants | `git pull` → **Project Files:** edit `README.md`, set content to `"remote update\nlocal daily note\n"`, and click **Save** → `git add README.md` → `git commit -m 'Daily update'` → `git push` |
| 5. Morning sync, evening ship | All variants | `git status -s` → `git pull` → **Project Files:** edit `README.md`, set content to `"remote update\nevening work\n"`, and click **Save** → `git add README.md` → `git commit -m 'Evening ship'` → `git push` |
| 6. Sync, branch, build, publish | All variants | `git pull` → `git switch -c feature/metrics` → **Project Files:** edit `README.md`, set content to `"remote update\nmetrics seed\n"`, and click **Save** → `git add README.md` → `git commit -m 'Metrics seed'` → `git push -u origin feature/metrics` |
| 7. Pointer, move, build, publish | All variants | `git pull` → `git branch feature/alerts` → `git switch feature/alerts` → **Project Files:** edit `README.md`, set content to `"remote update\nalerts seed\n"`, and click **Save** → `git add README.md` → `git commit -m 'Alerts seed'` → `git push -u origin feature/alerts` |
| 8. Publish, then map both worlds | All variants | `git push -u origin feature/payment` → `git log --oneline --graph --all` |
| 9. Glance, share, read the record | All variants | `git status -s` → `git push` → `git log --oneline` |
| 10. Read, then publish with tracking | All variants | `git log --oneline` → `git push -u origin feature/payment` |

### Chapter 08: Complete the Guild Handoff

#### Level 1: Prepare the Chronicle for Review

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Prepare the Chronicle for Review | Record the map repair on a branch, then fast-forward it | `git status` → `git log --oneline --graph --all` → `git switch -c repair/handoff-1-maps` → `git add maps/northern-route.md` → `git commit -m 'Restore route maps'` → `git switch main` → `git merge repair/handoff-1-maps` → `git log --oneline --graph --all` |
|  | Repair from the earlier stable crystal and preserve the merge | `git status` → `git show i1` → `git switch -c repair/handoff-1-lens i1` → `git add src/lens.py` → `git commit -m 'Correct signal lens'` → `git switch main` → `git merge --no-ff repair/handoff-1-lens` → `git log --oneline --graph --all` |
|  | Review the repair branch and hand it over as one snapshot | `git status` → `git switch -c repair/handoff-1-index` → `git add src/index.py` → `git commit -m 'Draft rebuilt index'` → `git switch main` → `git merge --squash repair/handoff-1-index` → `git commit -m 'Rebuild archive index'` → `git log --oneline --graph --all` |
|  | Finish the relay repair and publish the reviewed main branch | `git remote -v` → `git fetch origin` → `git status` → `git switch -c repair/handoff-1-relay` → `git add src/relay.py` → `git commit -m 'Prepare Guild relay'` → `git switch main` → `git merge repair/handoff-1-relay` → `git push` → `git log --oneline --graph --all` |

#### Level 2: Complete the Signal-Chamber Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Complete the Signal-Chamber Handoff | Record the map repair on a branch, then fast-forward it | `git status` → `git log --oneline --graph --all` → `git switch -c repair/handoff-2-maps` → `git add maps/northern-route.md` → `git commit -m 'Restore route maps'` → `git switch main` → `git merge repair/handoff-2-maps` → `git log --oneline --graph --all` |
|  | Repair from the earlier stable crystal and preserve the merge | `git status` → `git show i1` → `git switch -c repair/handoff-2-lens i1` → `git add src/lens.py` → `git commit -m 'Correct signal lens'` → `git switch main` → `git merge --no-ff repair/handoff-2-lens` → `git log --oneline --graph --all` |
|  | Review the repair branch and hand it over as one snapshot | `git status` → `git switch -c repair/handoff-2-index` → `git add src/index.py` → `git commit -m 'Draft rebuilt index'` → `git switch main` → `git merge --squash repair/handoff-2-index` → `git commit -m 'Rebuild archive index'` → `git log --oneline --graph --all` |
|  | Finish the relay repair and publish the reviewed main branch | `git remote -v` → `git fetch origin` → `git status` → `git switch -c repair/handoff-2-relay` → `git add src/relay.py` → `git commit -m 'Prepare Guild relay'` → `git switch main` → `git merge repair/handoff-2-relay` → `git push` → `git log --oneline --graph --all` |


## Frostbound Citadel

### Chapter 01: Temper the Commit

#### Level 1: Audit and Stage the Patch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Measure the pending change | All variants | `git diff --stat` |
| 2. Check the change for whitespace errors | All variants | `git diff --check` |
| 3. Stage the change hunk by hunk | All variants | `git add -p src/app.ts` |
| 4. Stage tracked edits only | All variants | `git add -u` |

#### Level 2: Rewrite the Tip

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Rewrite the unpublished tip commit | All variants | `git commit --amend -m 'Temper the relay tip'` |
| 2. Fold staged work into the tip commit | All variants | `git commit --amend --no-edit` |

#### Level 3: Step Back with Intent

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Step the branch back, keep the work | First team's repository | `git reset --soft m1` |
|  | Second team's repository | `git reset --soft n1` |
| 2. Step back and unstage everything | First team's repository | `git reset --mixed m1` |
|  | Second team's repository | `git reset --mixed n1` |
| 3. Discard the broken state completely | First team's repository | `git reset --hard m1` |
|  | Second team's repository | `git reset --hard n1` |

#### Level 4: Restore and Mark Known-Good

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Bring back one file from an old commit | First team's repository | `git restore --source m0 src/app.ts` |
|  | Second team's repository | `git restore --source n0 src/app.ts` |
| 2. Tag the known-good commit | All variants | `git tag relay-checkpoint` |

#### Level 5: Measure, then stage precisely

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Measure, then stage precisely | All variants | `git diff --stat` → `git add -p src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Check whitespace, then stage

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check whitespace, then stage | All variants | `git diff --check` → `git add -p src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 7: Measure, then stage tracked edits

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Measure, then stage tracked edits | All variants | `git diff --stat` → `git add -u` → `git status` → `git log --oneline --graph --all` |

#### Level 8: Fold the fix into the tip commit

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fold the fix into the tip commit | All variants | `git diff --check` → `git add -u` → `git commit --amend -m 'Fold the field fix into the tip'` → `git status` → `git log --oneline --graph --all` |

#### Level 9: Absorb staged notes and fix the message

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Absorb staged notes and fix the message | All variants | `git diff --stat` → `git commit --amend -m 'Clarify the relay tip'` → `git status` → `git log --oneline --graph --all` |

#### Level 10: Fold hunks in, keep the message

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fold hunks in, keep the message | All variants | `git add -p src/app.ts` → `git commit --amend --no-edit` → `git status` → `git log --oneline --graph --all` |

#### Level 11: Check, then fold without renaming

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check, then fold without renaming | All variants | `git diff --check` → `git commit --amend --no-edit` → `git status` → `git log --oneline --graph --all` |

#### Level 12: Step back softly from the bad tip

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Step back softly from the bad tip | First team's repository | `git diff --stat` → `git reset --soft m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git diff --stat` → `git reset --soft n1` → `git status` → `git log --oneline --graph --all` |

#### Level 13: Step back in two layers

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Step back in two layers | First team's repository | `git reset --soft m1` → `git reset --mixed m0` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git reset --soft n1` → `git reset --mixed n0` → `git status` → `git log --oneline --graph --all` |

#### Level 14: Unstage the broken commit for rework

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Unstage the broken commit for rework | First team's repository | `git diff --stat` → `git reset --mixed m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git diff --stat` → `git reset --mixed n1` → `git status` → `git log --oneline --graph --all` |

#### Level 15: Discard the rejected work entirely

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Discard the rejected work entirely | First team's repository | `git diff --check` → `git reset --hard m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git diff --check` → `git reset --hard n1` → `git status` → `git log --oneline --graph --all` |

#### Level 16: Reset hard, then recover one file

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Reset hard, then recover one file | First team's repository | `git reset --hard m1` → `git restore --source m0 src/app.ts` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git reset --hard n1` → `git restore --source n0 src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 17: Compare today's file with the original

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare today's file with the original | First team's repository | `git restore --source m0 src/app.ts` → `git diff --stat` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git restore --source n0 src/app.ts` → `git diff --stat` → `git status` → `git log --oneline --graph --all` |

#### Level 18: Separate the Frozen Patch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Separate the Frozen Patch | Author the repair from pending work | `git diff --stat` → `git status` → `git switch -c incident/fc-temper-the-commit-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-temper-the-commit-1 incident'` → `git tag fc-temper-the-commit-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git diff --stat` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-temper-the-commit-1 repair'` → `git tag fc-temper-the-commit-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git diff --stat` → `git merge-base main feature/work` → `git switch -c incident/fc-temper-the-commit-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-temper-the-commit-1 repair'` → `git tag fc-temper-the-commit-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git diff --stat` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-1-reverted main` → `git revert --no-edit d2` → `git tag fc-temper-the-commit-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 19: Rebuild the Review Boundary

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Rebuild the Review Boundary | Author the repair from pending work | `git diff --check` → `git status` → `git switch -c incident/fc-temper-the-commit-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-temper-the-commit-2 incident'` → `git tag fc-temper-the-commit-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git diff --check` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-temper-the-commit-2 repair'` → `git tag fc-temper-the-commit-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git diff --check` → `git merge-base main feature/work` → `git switch -c incident/fc-temper-the-commit-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-temper-the-commit-2 repair'` → `git tag fc-temper-the-commit-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git diff --check` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-2-reverted main` → `git revert --no-edit d2` → `git tag fc-temper-the-commit-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 20: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-temper-the-commit-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-temper-the-commit-3 incident'` → `git tag fc-temper-the-commit-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-temper-the-commit-3 repair'` → `git tag fc-temper-the-commit-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-temper-the-commit-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-temper-the-commit-3 repair'` → `git tag fc-temper-the-commit-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-temper-the-commit-3-reverted main` → `git revert --no-edit d2` → `git tag fc-temper-the-commit-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 02: Choose the Integration

#### Level 1: Compare and Choose the Integration

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Count the commits in a range | First team's repository | `git rev-list --count m0..main` |
|  | Second team's repository | `git rev-list --count n0..main` |
| 2. Compare a branch from where it started | All variants | `git diff main...feature/work` |
| 3. Merge with a visible merge commit | All variants | `git merge --no-ff feature/work` |
| 4. Squash a branch into one staged change | All variants | `git merge --squash feature/work` |

#### Level 2: Review the branch, then merge visibly

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Review the branch, then merge visibly | All variants | `git diff main...feature/work` → `git merge --no-ff feature/work` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Count the range, then merge visibly

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Count the range, then merge visibly | First team's repository | `git rev-list --count m0..main` → `git merge --no-ff feature/work` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git rev-list --count n0..main` → `git merge --no-ff feature/work` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Review, then squash to one change

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Review, then squash to one change | All variants | `git diff main...feature/work` → `git merge --squash feature/work` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Count, then squash deliberately

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Count, then squash deliberately | First team's repository | `git rev-list --count m0..main` → `git merge --squash feature/work` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git rev-list --count n0..main` → `git merge --squash feature/work` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Choose the Safe Gate

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Choose the Safe Gate | Author the repair from pending work | `git rev-list --count a0..main` → `git status` → `git switch -c incident/fc-choose-the-integration-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-choose-the-integration-1 incident'` → `git tag fc-choose-the-integration-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rev-list --count b0..main` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-choose-the-integration-1 repair'` → `git tag fc-choose-the-integration-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rev-list --count c0..main` → `git merge-base main feature/work` → `git switch -c incident/fc-choose-the-integration-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-choose-the-integration-1 repair'` → `git tag fc-choose-the-integration-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rev-list --count d0..main` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-1-reverted main` → `git revert --no-edit d2` → `git tag fc-choose-the-integration-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Preserve the Integration Record

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Preserve the Integration Record | Author the repair from pending work | `git merge-base main feature/work` → `git status` → `git switch -c incident/fc-choose-the-integration-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-choose-the-integration-2 incident'` → `git tag fc-choose-the-integration-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git merge-base main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-choose-the-integration-2 repair'` → `git tag fc-choose-the-integration-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git merge-base main feature/work` → `git merge-base main feature/work` → `git switch -c incident/fc-choose-the-integration-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-choose-the-integration-2 repair'` → `git tag fc-choose-the-integration-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git merge-base main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-2-reverted main` → `git revert --no-edit d2` → `git tag fc-choose-the-integration-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 8: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-choose-the-integration-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-choose-the-integration-3 incident'` → `git tag fc-choose-the-integration-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-choose-the-integration-3 repair'` → `git tag fc-choose-the-integration-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-choose-the-integration-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-choose-the-integration-3 repair'` → `git tag fc-choose-the-integration-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-choose-the-integration-3-reverted main` → `git revert --no-edit d2` → `git tag fc-choose-the-integration-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 03: Survive the Conflict

#### Level 1: Map the Conflict

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Preview a merge without running it | All variants | `git merge-tree main feature/work` |
| 2. List the conflicted index entries | All variants | `git ls-files -u` |
| 3. Compare the conflict against the base | All variants | `git diff --base src/relay.conf` |

#### Level 2: Compare Both Sides

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare against our side | All variants | `git diff --ours src/relay.conf` |
| 2. Compare against their side | All variants | `git diff --theirs src/relay.conf` |

#### Level 3: Resolve or Retreat

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve by taking our side | All variants | `git checkout --ours src/relay.conf` |
| 2. Resolve by taking their side | All variants | `git checkout --theirs src/relay.conf` |
| 3. Abort the conflicted merge | All variants | `git merge --abort` |
| 4. Finish the resolved merge | All variants | `git merge --continue` |

#### Level 4: Inspect the conflict, then keep our change

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the conflict, then keep our change | All variants | `git ls-files -u` → `git diff --ours src/relay.conf` → `git checkout --ours src/relay.conf` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Inspect the conflict, then adopt their change

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the conflict, then adopt their change | All variants | `git ls-files -u` → `git diff --theirs src/relay.conf` → `git checkout --theirs src/relay.conf` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Check the base, then abort

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the base, then abort | All variants | `git diff --base src/relay.conf` → `git merge --abort` → `git status` → `git log --oneline --graph --all` |

#### Level 7: Confirm the state, then finish the merge

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Confirm the state, then finish the merge | All variants | `git status` → `git merge --continue` → `git log --oneline --graph --all` |

#### Level 8: Resolve, stage, and finish

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve, stage, and finish | All variants | `git checkout --ours src/relay.conf` → `git add src/relay.conf` → `git merge --continue` → `git status` → `git log --oneline --graph --all` |

#### Level 9: Start resolving, then stand down

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Start resolving, then stand down | All variants | `git ls-files -u` → `git checkout --theirs src/relay.conf` → `git merge --abort` → `git status` → `git log --oneline --graph --all` |

#### Level 10: Read the conflict from base and their side

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the conflict from base and their side | All variants | `git diff --base src/relay.conf` → `git diff --theirs src/relay.conf` → `git status` → `git log --oneline --graph --all` |

#### Level 11: Weigh both sides of the conflict

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Weigh both sides of the conflict | All variants | `git diff --ours src/relay.conf` → `git diff --theirs src/relay.conf` → `git status` → `git log --oneline --graph --all` |

#### Level 12: Forecast the Collision

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Forecast the Collision | Author the repair from pending work | `git merge-tree main feature/work` → `git status` → `git switch -c incident/fc-survive-the-conflict-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-survive-the-conflict-1 incident'` → `git tag fc-survive-the-conflict-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git merge-tree main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-survive-the-conflict-1 repair'` → `git tag fc-survive-the-conflict-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git merge-tree main feature/work` → `git merge-base main feature/work` → `git switch -c incident/fc-survive-the-conflict-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-survive-the-conflict-1 repair'` → `git tag fc-survive-the-conflict-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git merge-tree main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-1-reverted main` → `git revert --no-edit d2` → `git tag fc-survive-the-conflict-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 13: Resolve the Shared Rune

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve the Shared Rune | Author the repair from pending work | `git merge-base main feature/work` → `git status` → `git switch -c incident/fc-survive-the-conflict-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-survive-the-conflict-2 incident'` → `git tag fc-survive-the-conflict-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git merge-base main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-survive-the-conflict-2 repair'` → `git tag fc-survive-the-conflict-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git merge-base main feature/work` → `git merge-base main feature/work` → `git switch -c incident/fc-survive-the-conflict-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-survive-the-conflict-2 repair'` → `git tag fc-survive-the-conflict-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git merge-base main feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-2-reverted main` → `git revert --no-edit d2` → `git tag fc-survive-the-conflict-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 14: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-survive-the-conflict-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-survive-the-conflict-3 incident'` → `git tag fc-survive-the-conflict-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-survive-the-conflict-3 repair'` → `git tag fc-survive-the-conflict-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-survive-the-conflict-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-survive-the-conflict-3 repair'` → `git tag fc-survive-the-conflict-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-survive-the-conflict-3-reverted main` → `git revert --no-edit d2` → `git tag fc-survive-the-conflict-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 04: Move the Patch

#### Level 1: Inspect and Shelve the Patch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare two versions of a patch series | First team's repository | `git range-diff m0..old/series m0..feature/work` |
|  | Second team's repository | `git range-diff n0..old/series n0..feature/work` |
| 2. Shelve unfinished work, untracked included | All variants | `git stash push -u -m 'Shelve relay draft'` |
| 3. Look inside a stash entry | All variants | `git stash show stash@{0}` |

#### Level 2: Recover or Retreat

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Restore stashed work, keep the copy | All variants | `git stash apply stash@{0}` |
| 2. Restore stashed work and remove the entry | All variants | `git stash pop stash@{0}` |
| 3. Delete a stale stash entry | All variants | `git stash drop stash@{0}` |
| 4. Back out of a stuck cherry-pick | All variants | `git cherry-pick --abort` |

#### Level 3: Stash the work, then check the entry

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Stash the work, then check the entry | All variants | `git stash push -u -m 'Shelve probe wiring'` → `git stash show stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Check the entry, then restore carefully

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the entry, then restore carefully | All variants | `git stash show stash@{0}` → `git stash apply stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Park the work, then take it back

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Park the work, then take it back | All variants | `git stash push -u -m 'Park the relay sweep'` → `git stash pop stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Check the entry one last time, then delete it

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the entry one last time, then delete it | All variants | `git stash show stash@{0}` → `git stash drop stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 7: Restore the work, then clear the entry

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Restore the work, then clear the entry | All variants | `git stash apply stash@{0}` → `git stash drop stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 8: Confirm the entry, then pop it

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Confirm the entry, then pop it | All variants | `git stash show stash@{0}` → `git stash pop stash@{0}` → `git status` → `git log --oneline --graph --all` |

#### Level 9: Confirm the damage, then back out

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Confirm the damage, then back out | All variants | `git status` → `git cherry-pick --abort` → `git log --oneline --graph --all` |

#### Level 10: Abort the cherry-pick immediately

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Abort the cherry-pick immediately | All variants | `git cherry-pick --abort` → `git status` → `git log --oneline --graph --all` |

#### Level 11: Carry the Relay Patch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Carry the Relay Patch | Author the repair from pending work | `git range-diff a0..old/series a0..feature/work` → `git status` → `git switch -c incident/fc-move-the-patch-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-move-the-patch-1 incident'` → `git tag fc-move-the-patch-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git range-diff b0..old/series b0..feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-move-the-patch-1 repair'` → `git tag fc-move-the-patch-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git range-diff c0..old/series c0..feature/work` → `git merge-base main feature/work` → `git switch -c incident/fc-move-the-patch-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-move-the-patch-1 repair'` → `git tag fc-move-the-patch-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git range-diff d0..old/series d0..feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-1-reverted main` → `git revert --no-edit d2` → `git tag fc-move-the-patch-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 12: Recover the Interrupted Transfer

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Recover the Interrupted Transfer | Author the repair from pending work | `git show a3` → `git status` → `git switch -c incident/fc-move-the-patch-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-move-the-patch-2 incident'` → `git tag fc-move-the-patch-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git show b3` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-move-the-patch-2 repair'` → `git tag fc-move-the-patch-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git show c3` → `git merge-base main feature/work` → `git switch -c incident/fc-move-the-patch-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-move-the-patch-2 repair'` → `git tag fc-move-the-patch-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git show d3` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-2-reverted main` → `git revert --no-edit d2` → `git tag fc-move-the-patch-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 13: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-move-the-patch-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-move-the-patch-3 incident'` → `git tag fc-move-the-patch-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-move-the-patch-3 repair'` → `git tag fc-move-the-patch-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-move-the-patch-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-move-the-patch-3 repair'` → `git tag fc-move-the-patch-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-move-the-patch-3-reverted main` → `git revert --no-edit d2` → `git tag fc-move-the-patch-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 05: Reforge the Branch

#### Level 1: Rebase or Stand Down

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Rebase the branch onto today's main | All variants | `git rebase main` |
| 2. Abort a rebase that went wrong | All variants | `git rebase --abort` |

#### Level 2: Rebase, then prove nothing was lost

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Rebase, then prove nothing was lost | First team's repository | `git rebase main` → `git range-diff m0..old/series m0..feature/work` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git rebase main` → `git range-diff n0..old/series n0..feature/work` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Read the history, then rebase

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the history, then rebase | All variants | `git log --oneline --graph --all` → `git rebase main` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Compare the series, then call it off

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare the series, then call it off | First team's repository | `git range-diff m0..old/series m0..feature/work` → `git rebase --abort` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git range-diff n0..old/series n0..feature/work` → `git rebase --abort` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Abort the rebase and report

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Abort the rebase and report | All variants | `git rebase --abort` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Reforge the Review Series

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Reforge the Review Series | Author the repair from pending work | `git range-diff a0..old/series a0..feature/work` → `git status` → `git switch -c incident/fc-reforge-the-branch-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-reforge-the-branch-1 incident'` → `git tag fc-reforge-the-branch-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git range-diff b0..old/series b0..feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-reforge-the-branch-1 repair'` → `git tag fc-reforge-the-branch-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git range-diff c0..old/series c0..feature/work` → `git merge-base main feature/work` → `git switch -c incident/fc-reforge-the-branch-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-reforge-the-branch-1 repair'` → `git tag fc-reforge-the-branch-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git range-diff d0..old/series d0..feature/work` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-1-reverted main` → `git revert --no-edit d2` → `git tag fc-reforge-the-branch-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Prove the Rewrite

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Prove the Rewrite | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-reforge-the-branch-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-reforge-the-branch-2 incident'` → `git tag fc-reforge-the-branch-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-reforge-the-branch-2 repair'` → `git tag fc-reforge-the-branch-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-reforge-the-branch-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-reforge-the-branch-2 repair'` → `git tag fc-reforge-the-branch-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-2-reverted main` → `git revert --no-edit d2` → `git tag fc-reforge-the-branch-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 8: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-reforge-the-branch-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-reforge-the-branch-3 incident'` → `git tag fc-reforge-the-branch-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-reforge-the-branch-3 repair'` → `git tag fc-reforge-the-branch-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-reforge-the-branch-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-reforge-the-branch-3 repair'` → `git tag fc-reforge-the-branch-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-reforge-the-branch-3-reverted main` → `git revert --no-edit d2` → `git tag fc-reforge-the-branch-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 06: Govern the Remote

#### Level 1: Inspect and Refresh Remotes

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the upstream tracking table | All variants | `git branch -vv` |
| 2. Fetch from every remote | All variants | `git fetch --all` |
| 3. Fetch and remove stale tracking refs | All variants | `git fetch --prune` |

#### Level 2: Integrate Under Guard

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pull only if it can fast-forward | All variants | `git pull --ff-only` |
| 2. Pull with rebase | All variants | `git pull --rebase` |

#### Level 3: Publish with Guardrails

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Publish rewritten history safely | All variants | `git push --force-with-lease` |
| 2. Delete a branch on the remote | All variants | `git push origin --delete old-experiment` |
| 3. Point origin at a new URL | All variants | `git remote set-url origin https://relay.frost.test/operations.git` |

#### Level 4: Read tracking, then fetch everything

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read tracking, then fetch everything | All variants | `git branch -vv` → `git fetch --all` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Read tracking, then prune stale refs

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read tracking, then prune stale refs | All variants | `git branch -vv` → `git fetch --prune` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Fetch everything, then pull safely

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fetch everything, then pull safely | All variants | `git fetch --all` → `git pull --ff-only` → `git status` → `git log --oneline --graph --all` |

#### Level 7: Read tracking, then pull with rebase

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read tracking, then pull with rebase | All variants | `git branch -vv` → `git pull --rebase` → `git status` → `git log --oneline --graph --all` |

#### Level 8: Check tracking, then publish the rewrite

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check tracking, then publish the rewrite | All variants | `git branch -vv` → `git push --force-with-lease` → `git status` → `git log --oneline --graph --all` |

#### Level 9: Fetch first, then take the lease

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fetch first, then take the lease | All variants | `git fetch --all` → `git push --force-with-lease` → `git status` → `git log --oneline --graph --all` |

#### Level 10: Prune first, then delete the branch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Prune first, then delete the branch | All variants | `git fetch --prune` → `git push origin --delete old-experiment` → `git status` → `git log --oneline --graph --all` |

#### Level 11: Check tracking, then delete deliberately

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check tracking, then delete deliberately | All variants | `git branch -vv` → `git push origin --delete old-experiment` → `git status` → `git log --oneline --graph --all` |

#### Level 12: Change the URL, then verify tracking

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Change the URL, then verify tracking | All variants | `git remote set-url origin https://relay.frost.test/operations.git` → `git branch -vv` → `git status` → `git log --oneline --graph --all` |

#### Level 13: Switch to the mirror URL

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Switch to the mirror URL | All variants | `git status` → `git remote set-url origin https://mirror.frost.test/operations.git` → `git log --oneline --graph --all` |

#### Level 14: Prune, then pull under the guard

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Prune, then pull under the guard | All variants | `git fetch --prune` → `git pull --ff-only` → `git status` → `git log --oneline --graph --all` |

#### Level 15: Fetch everything, then pull with rebase

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Fetch everything, then pull with rebase | All variants | `git fetch --all` → `git pull --rebase` → `git status` → `git log --oneline --graph --all` |

#### Level 16: Read the Signal Towers

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the Signal Towers | Author the repair from pending work | `git branch -vv` → `git status` → `git switch -c incident/fc-govern-the-remote-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-govern-the-remote-1 incident'` → `git tag fc-govern-the-remote-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git branch -vv` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-govern-the-remote-1 repair'` → `git tag fc-govern-the-remote-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git branch -vv` → `git merge-base main feature/work` → `git switch -c incident/fc-govern-the-remote-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-govern-the-remote-1 repair'` → `git tag fc-govern-the-remote-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git branch -vv` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-1-reverted main` → `git revert --no-edit d2` → `git tag fc-govern-the-remote-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 17: Publish Without Overwriting

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Publish Without Overwriting | Author the repair from pending work | `git remote -v` → `git status` → `git switch -c incident/fc-govern-the-remote-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-govern-the-remote-2 incident'` → `git tag fc-govern-the-remote-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git remote -v` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-govern-the-remote-2 repair'` → `git tag fc-govern-the-remote-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git remote -v` → `git merge-base main feature/work` → `git switch -c incident/fc-govern-the-remote-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-govern-the-remote-2 repair'` → `git tag fc-govern-the-remote-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git remote -v` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-2-reverted main` → `git revert --no-edit d2` → `git tag fc-govern-the-remote-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 18: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-govern-the-remote-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-govern-the-remote-3 incident'` → `git tag fc-govern-the-remote-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-govern-the-remote-3 repair'` → `git tag fc-govern-the-remote-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-govern-the-remote-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-govern-the-remote-3 repair'` → `git tag fc-govern-the-remote-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-govern-the-remote-3-reverted main` → `git revert --no-edit d2` → `git tag fc-govern-the-remote-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 07: Deliver the Release

#### Level 1: Read the Release History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Summarize commits by author | All variants | `git shortlog` |
| 2. Count commits per author | All variants | `git shortlog -sn` |
| 3. Name the current commit from its tags | All variants | `git describe --tags` |

#### Level 2: Mark and Publish the Release

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Create an annotated release tag | All variants | `git tag -a v1.1 -m 'Heat core release candidate'` |
| 2. Delete an outdated tag | All variants | `git tag -d v1.0` |
| 3. Publish all tags | All variants | `git push --tags` |

#### Level 3: Check the current name, then tag

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the current name, then tag | All variants | `git describe --tags` → `git tag -a v1.1 -m 'Signed relay candidate'` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Tag the hotfix, then publish the tags

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Tag the hotfix, then publish the tags | All variants | `git tag -a v1.2 -m 'Relay hotfix marker'` → `git push --tags` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Credit the authors, then delete the tag

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Credit the authors, then delete the tag | All variants | `git shortlog` → `git tag -d v1.0` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Check the name, then delete the stale tag

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check the name, then delete the stale tag | All variants | `git describe --tags` → `git tag -d v1.0` → `git status` → `git log --oneline --graph --all` |

#### Level 7: Count contributions, then publish the tags

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Count contributions, then publish the tags | All variants | `git shortlog -sn` → `git push --tags` → `git status` → `git log --oneline --graph --all` |

#### Level 8: Assemble the release record

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Assemble the release record | All variants | `git shortlog` → `git describe --tags` → `git status` → `git log --oneline --graph --all` |

#### Level 9: Assemble the Release Evidence

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Assemble the Release Evidence | Author the repair from pending work | `git shortlog -sn` → `git status` → `git switch -c incident/fc-deliver-the-release-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-deliver-the-release-1 incident'` → `git tag fc-deliver-the-release-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git shortlog -sn` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-deliver-the-release-1 repair'` → `git tag fc-deliver-the-release-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git shortlog -sn` → `git merge-base main feature/work` → `git switch -c incident/fc-deliver-the-release-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-deliver-the-release-1 repair'` → `git tag fc-deliver-the-release-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git shortlog -sn` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-1-reverted main` → `git revert --no-edit d2` → `git tag fc-deliver-the-release-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 10: Mark the Candidate

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Mark the Candidate | Author the repair from pending work | `git describe --tags` → `git status` → `git switch -c incident/fc-deliver-the-release-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-deliver-the-release-2 incident'` → `git tag fc-deliver-the-release-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git describe --tags` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-deliver-the-release-2 repair'` → `git tag fc-deliver-the-release-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git describe --tags` → `git merge-base main feature/work` → `git switch -c incident/fc-deliver-the-release-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-deliver-the-release-2 repair'` → `git tag fc-deliver-the-release-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git describe --tags` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-2-reverted main` → `git revert --no-edit d2` → `git tag fc-deliver-the-release-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 11: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-deliver-the-release-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-deliver-the-release-3 incident'` → `git tag fc-deliver-the-release-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-deliver-the-release-3 repair'` → `git tag fc-deliver-the-release-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-deliver-the-release-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-deliver-the-release-3 repair'` → `git tag fc-deliver-the-release-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-deliver-the-release-3-reverted main` → `git revert --no-edit d2` → `git tag fc-deliver-the-release-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 08: Hunt the Frozen Regression

#### Level 1: Run and Preserve the Search

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Find the bad commit automatically | All variants | `git bisect run heat-relay-test` |
| 2. Read the bisect record | All variants | `git bisect log` |

#### Level 2: Run the search, then keep the record

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Run the search, then keep the record | All variants | `git bisect run heat-relay-test` → `git bisect log` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Confirm with a second test script

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Confirm with a second test script | All variants | `git bisect run relay-freeze-test` → `git bisect log` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Read the history, then run the search

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the history, then run the search | All variants | `git log --oneline --graph --all` → `git bisect run heat-relay-test` → `git status` |

#### Level 5: Reproduce yesterday's search

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Reproduce yesterday's search | All variants | `git bisect run heat-relay-test` → `git bisect log` → `git log --oneline --graph --all` → `git status` |

#### Level 6: Find the First Frozen Failure

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Find the First Frozen Failure | Author the repair from pending work | `git bisect run test-suite` → `git status` → `git switch -c incident/fc-hunt-the-regression-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-hunt-the-regression-1 incident'` → `git tag fc-hunt-the-regression-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git bisect run test-suite` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-hunt-the-regression-1 repair'` → `git tag fc-hunt-the-regression-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git bisect run test-suite` → `git merge-base main feature/work` → `git switch -c incident/fc-hunt-the-regression-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-hunt-the-regression-1 repair'` → `git tag fc-hunt-the-regression-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git bisect run test-suite` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-1-reverted main` → `git revert --no-edit d2` → `git tag fc-hunt-the-regression-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Repair the Located Regression

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Repair the Located Regression | Author the repair from pending work | `git bisect log` → `git status` → `git switch -c incident/fc-hunt-the-regression-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-hunt-the-regression-2 incident'` → `git tag fc-hunt-the-regression-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git bisect log` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-hunt-the-regression-2 repair'` → `git tag fc-hunt-the-regression-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git bisect log` → `git merge-base main feature/work` → `git switch -c incident/fc-hunt-the-regression-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-hunt-the-regression-2 repair'` → `git tag fc-hunt-the-regression-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git bisect log` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-2-reverted main` → `git revert --no-edit d2` → `git tag fc-hunt-the-regression-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 8: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-hunt-the-regression-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-hunt-the-regression-3 incident'` → `git tag fc-hunt-the-regression-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-hunt-the-regression-3 repair'` → `git tag fc-hunt-the-regression-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-hunt-the-regression-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-hunt-the-regression-3 repair'` → `git tag fc-hunt-the-regression-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-hunt-the-regression-3-reverted main` → `git revert --no-edit d2` → `git tag fc-hunt-the-regression-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 09: Publish the Restored Core

#### Level 1: Verify the Release Record

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify a release tag's signature | All variants | `git verify-tag v1.0` |
| 2. List every ref and its target | All variants | `git show-ref` |

#### Level 2: Verify the tag, then list the refs

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the tag, then list the refs | All variants | `git verify-tag v1.0` → `git show-ref` → `git status` → `git log --oneline --graph --all` |

#### Level 3: List the refs, then prove the tag

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List the refs, then prove the tag | All variants | `git show-ref` → `git verify-tag v1.0` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Audit the Restored Core

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the Restored Core | Author the repair from pending work | `git verify-tag v1.0` → `git status` → `git switch -c incident/fc-publish-the-core-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-publish-the-core-1 incident'` → `git tag fc-publish-the-core-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git verify-tag v1.0` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-publish-the-core-1 repair'` → `git tag fc-publish-the-core-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git verify-tag v1.0` → `git merge-base main feature/work` → `git switch -c incident/fc-publish-the-core-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-publish-the-core-1 repair'` → `git tag fc-publish-the-core-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git verify-tag v1.0` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-1-reverted main` → `git revert --no-edit d2` → `git tag fc-publish-the-core-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 5: Publish the Final Heat History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Publish the Final Heat History | Author the repair from pending work | `git show-ref` → `git status` → `git switch -c incident/fc-publish-the-core-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-publish-the-core-2 incident'` → `git tag fc-publish-the-core-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-publish-the-core-2 repair'` → `git tag fc-publish-the-core-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git show-ref` → `git merge-base main feature/work` → `git switch -c incident/fc-publish-the-core-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-publish-the-core-2 repair'` → `git tag fc-publish-the-core-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-2-reverted main` → `git revert --no-edit d2` → `git tag fc-publish-the-core-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/fc-publish-the-core-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve fc-publish-the-core-3 incident'` → `git tag fc-publish-the-core-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant fc-publish-the-core-3 repair'` → `git tag fc-publish-the-core-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/fc-publish-the-core-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate fc-publish-the-core-3 repair'` → `git tag fc-publish-the-core-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/fc-publish-the-core-3-reverted main` → `git revert --no-edit d2` → `git tag fc-publish-the-core-3-reverted` → `git show` → `git log --oneline --graph --all` |


## Neon Backstreets

### Chapter 01: Speak the Revision Language

#### Level 1: Locate and Resolve

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve a revision to a commit id | All variants | `git rev-parse HEAD~1` |
| 2. Locate the repository root | All variants | `git rev-parse --show-toplevel` |

#### Level 2: Locate the root, then resolve the revision

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Locate the root, then resolve the revision | All variants | `git rev-parse --show-toplevel` → `git rev-parse HEAD~1` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Pin the audit coordinates

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pin the audit coordinates | All variants | `git rev-parse --show-toplevel` → `git rev-parse main` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Resolve the Incident Coordinates

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Resolve the Incident Coordinates | Author the repair from pending work | `git rev-parse HEAD~1` → `git status` → `git switch -c incident/sn-revision-language-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-revision-language-1 incident'` → `git tag sn-revision-language-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rev-parse HEAD~1` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-revision-language-1 repair'` → `git tag sn-revision-language-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rev-parse HEAD~1` → `git merge-base main feature/work` → `git switch -c incident/sn-revision-language-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-revision-language-1 repair'` → `git tag sn-revision-language-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rev-parse HEAD~1` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-1-reverted main` → `git revert --no-edit d2` → `git tag sn-revision-language-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 5: Name the Exact History Set

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Name the Exact History Set | Author the repair from pending work | `git rev-list --count a0..main` → `git status` → `git switch -c incident/sn-revision-language-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-revision-language-2 incident'` → `git tag sn-revision-language-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rev-list --count b0..main` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-revision-language-2 repair'` → `git tag sn-revision-language-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rev-list --count c0..main` → `git merge-base main feature/work` → `git switch -c incident/sn-revision-language-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-revision-language-2 repair'` → `git tag sn-revision-language-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rev-list --count d0..main` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-2-reverted main` → `git revert --no-edit d2` → `git tag sn-revision-language-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-revision-language-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-revision-language-3 incident'` → `git tag sn-revision-language-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-revision-language-3 repair'` → `git tag sn-revision-language-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-revision-language-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-revision-language-3 repair'` → `git tag sn-revision-language-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-revision-language-3-reverted main` → `git revert --no-edit d2` → `git tag sn-revision-language-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 02: Read the Hidden History

#### Level 1: Search the Hidden History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Find who last changed each line | All variants | `git blame src/app.ts` |
| 2. Search the tracked content | All variants | `git grep stable` |
| 3. Read a file as it was in an old commit | First team's repository | `git show m1:src/app.ts` |
|  | Second team's repository | `git show n1:src/app.ts` |

#### Level 2: Search first, then trace the line

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Search first, then trace the line | All variants | `git grep stable` → `git blame src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Read the old version, then the evidence trail

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the old version, then the evidence trail | First team's repository | `git show m1:src/app.ts` → `git blame src/app.ts` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git show n1:src/app.ts` → `git blame src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Search today, then read the old snapshot

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Search today, then read the old snapshot | First team's repository | `git grep stable` → `git show m1:src/app.ts` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git grep stable` → `git show n1:src/app.ts` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Trace the Changed Line

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Trace the Changed Line | Author the repair from pending work | `git blame src/app.ts` → `git status` → `git switch -c incident/sn-hidden-history-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-hidden-history-1 incident'` → `git tag sn-hidden-history-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git blame src/app.ts` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-hidden-history-1 repair'` → `git tag sn-hidden-history-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git blame src/app.ts` → `git merge-base main feature/work` → `git switch -c incident/sn-hidden-history-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-hidden-history-1 repair'` → `git tag sn-hidden-history-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git blame src/app.ts` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-1-reverted main` → `git revert --no-edit d2` → `git tag sn-hidden-history-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Search the Archive for the Fault

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Search the Archive for the Fault | Author the repair from pending work | `git grep stable` → `git status` → `git switch -c incident/sn-hidden-history-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-hidden-history-2 incident'` → `git tag sn-hidden-history-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git grep stable` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-hidden-history-2 repair'` → `git tag sn-hidden-history-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git grep stable` → `git merge-base main feature/work` → `git switch -c incident/sn-hidden-history-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-hidden-history-2 repair'` → `git tag sn-hidden-history-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git grep stable` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-2-reverted main` → `git revert --no-edit d2` → `git tag sn-hidden-history-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-hidden-history-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-hidden-history-3 incident'` → `git tag sn-hidden-history-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-hidden-history-3 repair'` → `git tag sn-hidden-history-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-hidden-history-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-hidden-history-3 repair'` → `git tag sn-hidden-history-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-hidden-history-3-reverted main` → `git revert --no-edit d2` → `git tag sn-hidden-history-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 03: Hunt the First Broken Commit

#### Level 1: Automate the Regression Search

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Automate the Regression Search | Author the repair from pending work | `git bisect run integration-test` → `git status` → `git switch -c incident/sn-first-broken-commit-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-first-broken-commit-1 incident'` → `git tag sn-first-broken-commit-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git bisect run integration-test` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-first-broken-commit-1 repair'` → `git tag sn-first-broken-commit-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git bisect run integration-test` → `git merge-base main feature/work` → `git switch -c incident/sn-first-broken-commit-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-first-broken-commit-1 repair'` → `git tag sn-first-broken-commit-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git bisect run integration-test` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-1-reverted main` → `git revert --no-edit d2` → `git tag sn-first-broken-commit-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 2: Preserve the Bisect Evidence

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Preserve the Bisect Evidence | Author the repair from pending work | `git bisect log` → `git status` → `git switch -c incident/sn-first-broken-commit-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-first-broken-commit-2 incident'` → `git tag sn-first-broken-commit-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git bisect log` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-first-broken-commit-2 repair'` → `git tag sn-first-broken-commit-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git bisect log` → `git merge-base main feature/work` → `git switch -c incident/sn-first-broken-commit-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-first-broken-commit-2 repair'` → `git tag sn-first-broken-commit-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git bisect log` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-2-reverted main` → `git revert --no-edit d2` → `git tag sn-first-broken-commit-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 3: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-first-broken-commit-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-first-broken-commit-3 incident'` → `git tag sn-first-broken-commit-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-first-broken-commit-3 repair'` → `git tag sn-first-broken-commit-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-first-broken-commit-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-first-broken-commit-3 repair'` → `git tag sn-first-broken-commit-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-first-broken-commit-3-reverted main` → `git revert --no-edit d2` → `git tag sn-first-broken-commit-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 04: Master Repeated Conflict

#### Level 1: Read the Resolution Memory

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List the recorded conflict paths | All variants | `git rerere status` |
| 2. Inspect the recorded resolutions | All variants | `git rerere diff` |

#### Level 2: Audit the recorded resolution

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the recorded resolution | All variants | `git rerere status` → `git rerere diff` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Pre-flight the conflict memory

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Pre-flight the conflict memory | All variants | `git rerere diff` → `git rerere status` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Inspect the Resolution Memory

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the Resolution Memory | Author the repair from pending work | `git rerere status` → `git status` → `git switch -c incident/sn-repeated-conflict-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-repeated-conflict-1 incident'` → `git tag sn-repeated-conflict-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rerere status` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-repeated-conflict-1 repair'` → `git tag sn-repeated-conflict-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rerere status` → `git merge-base main feature/work` → `git switch -c incident/sn-repeated-conflict-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-repeated-conflict-1 repair'` → `git tag sn-repeated-conflict-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rerere status` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-1-reverted main` → `git revert --no-edit d2` → `git tag sn-repeated-conflict-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 5: Reuse the Proven Conflict Repair

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Reuse the Proven Conflict Repair | Author the repair from pending work | `git rerere diff` → `git status` → `git switch -c incident/sn-repeated-conflict-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-repeated-conflict-2 incident'` → `git tag sn-repeated-conflict-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rerere diff` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-repeated-conflict-2 repair'` → `git tag sn-repeated-conflict-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rerere diff` → `git merge-base main feature/work` → `git switch -c incident/sn-repeated-conflict-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-repeated-conflict-2 repair'` → `git tag sn-repeated-conflict-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rerere diff` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-2-reverted main` → `git revert --no-edit d2` → `git tag sn-repeated-conflict-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-repeated-conflict-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-repeated-conflict-3 incident'` → `git tag sn-repeated-conflict-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-repeated-conflict-3 repair'` → `git tag sn-repeated-conflict-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-repeated-conflict-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-repeated-conflict-3 repair'` → `git tag sn-repeated-conflict-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-repeated-conflict-3-reverted main` → `git revert --no-edit d2` → `git tag sn-repeated-conflict-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 05: Work Across Many Realities

#### Level 1: Map the Parallel Workspaces

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. List the attached worktrees | All variants | `git worktree list` |
| 2. List the sparse checkout paths | All variants | `git sparse-checkout list` |
| 3. Check the submodule state | All variants | `git submodule status` |

#### Level 2: Map the whole workspace setup

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Map the whole workspace setup | All variants | `git worktree list` → `git sparse-checkout list` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Audit the dependency pins

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the dependency pins | All variants | `git submodule status` → `git worktree list` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Explain the missing files

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Explain the missing files | All variants | `git sparse-checkout list` → `git submodule status` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Run the morning floor check

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Run the morning floor check | All variants | `git worktree list` → `git sparse-checkout list` → `git submodule status` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Map the Parallel Work Floors

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Map the Parallel Work Floors | Author the repair from pending work | `git worktree list` → `git status` → `git switch -c incident/sn-many-realities-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-many-realities-1 incident'` → `git tag sn-many-realities-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git worktree list` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-many-realities-1 repair'` → `git tag sn-many-realities-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git worktree list` → `git merge-base main feature/work` → `git switch -c incident/sn-many-realities-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-many-realities-1 repair'` → `git tag sn-many-realities-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git worktree list` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-1-reverted main` → `git revert --no-edit d2` → `git tag sn-many-realities-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Repair the Reduced Workspace

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Repair the Reduced Workspace | Author the repair from pending work | `git sparse-checkout list` → `git status` → `git switch -c incident/sn-many-realities-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-many-realities-2 incident'` → `git tag sn-many-realities-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git sparse-checkout list` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-many-realities-2 repair'` → `git tag sn-many-realities-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git sparse-checkout list` → `git merge-base main feature/work` → `git switch -c incident/sn-many-realities-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-many-realities-2 repair'` → `git tag sn-many-realities-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git sparse-checkout list` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-2-reverted main` → `git revert --no-edit d2` → `git tag sn-many-realities-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 8: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-many-realities-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-many-realities-3 incident'` → `git tag sn-many-realities-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-many-realities-3 repair'` → `git tag sn-many-realities-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-many-realities-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-many-realities-3 repair'` → `git tag sn-many-realities-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-many-realities-3-reverted main` → `git revert --no-edit d2` → `git tag sn-many-realities-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 06: Configure Git's Behavior

#### Level 1: Audit the Effective Behavior

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read one configuration value | All variants | `git config --get user.name` |
| 2. Audit the effective configuration | All variants | `git config --get user.name` → `git config --list` → `git status` → `git log --oneline --graph --all` |

#### Level 2: Audit the Effective Configuration

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the Effective Configuration | Author the repair from pending work | `git config --get user.name` → `git status` → `git switch -c incident/sn-enchant-behavior-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-enchant-behavior-1 incident'` → `git tag sn-enchant-behavior-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git config --get user.name` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-enchant-behavior-1 repair'` → `git tag sn-enchant-behavior-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git config --get user.name` → `git merge-base main feature/work` → `git switch -c incident/sn-enchant-behavior-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-enchant-behavior-1 repair'` → `git tag sn-enchant-behavior-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git config --get user.name` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-1-reverted main` → `git revert --no-edit d2` → `git tag sn-enchant-behavior-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 3: Correct the Automation Contract

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Correct the Automation Contract | Author the repair from pending work | `git config --list` → `git status` → `git switch -c incident/sn-enchant-behavior-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-enchant-behavior-2 incident'` → `git tag sn-enchant-behavior-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git config --list` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-enchant-behavior-2 repair'` → `git tag sn-enchant-behavior-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git config --list` → `git merge-base main feature/work` → `git switch -c incident/sn-enchant-behavior-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-enchant-behavior-2 repair'` → `git tag sn-enchant-behavior-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git config --list` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-2-reverted main` → `git revert --no-edit d2` → `git tag sn-enchant-behavior-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 4: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-enchant-behavior-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-enchant-behavior-3 incident'` → `git tag sn-enchant-behavior-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-enchant-behavior-3 repair'` → `git tag sn-enchant-behavior-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-enchant-behavior-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-enchant-behavior-3 repair'` → `git tag sn-enchant-behavior-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-enchant-behavior-3-reverted main` → `git revert --no-edit d2` → `git tag sn-enchant-behavior-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 07: Guard the Archive

#### Level 1: Inspect and Verify the Commit

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify a commit's signature | First team's repository | `git verify-commit m1` |
|  | Second team's repository | `git verify-commit n1` |
| 2. Inspect and verify the release commit | First team's repository | `git show m1` → `git verify-commit m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git show n1` → `git verify-commit n1` → `git status` → `git log --oneline --graph --all` |

#### Level 2: Verify the Release Identity

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Release Identity | Author the repair from pending work | `git verify-commit a1` → `git status` → `git switch -c incident/sn-guard-the-archive-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-guard-the-archive-1 incident'` → `git tag sn-guard-the-archive-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git verify-commit b1` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-guard-the-archive-1 repair'` → `git tag sn-guard-the-archive-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git verify-commit c1` → `git merge-base main feature/work` → `git switch -c incident/sn-guard-the-archive-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-guard-the-archive-1 repair'` → `git tag sn-guard-the-archive-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git verify-commit d1` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-1-reverted main` → `git revert --no-edit d2` → `git tag sn-guard-the-archive-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 3: Quarantine the Untrusted Ref

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Quarantine the Untrusted Ref | Author the repair from pending work | `git verify-tag v1.0` → `git status` → `git switch -c incident/sn-guard-the-archive-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-guard-the-archive-2 incident'` → `git tag sn-guard-the-archive-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git verify-tag v1.0` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-guard-the-archive-2 repair'` → `git tag sn-guard-the-archive-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git verify-tag v1.0` → `git merge-base main feature/work` → `git switch -c incident/sn-guard-the-archive-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-guard-the-archive-2 repair'` → `git tag sn-guard-the-archive-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git verify-tag v1.0` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-2-reverted main` → `git revert --no-edit d2` → `git tag sn-guard-the-archive-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 4: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-guard-the-archive-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-guard-the-archive-3 incident'` → `git tag sn-guard-the-archive-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-guard-the-archive-3 repair'` → `git tag sn-guard-the-archive-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-guard-the-archive-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-guard-the-archive-3 repair'` → `git tag sn-guard-the-archive-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-guard-the-archive-3-reverted main` → `git revert --no-edit d2` → `git tag sn-guard-the-archive-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 08: Restore and Maintain the Archive

#### Level 1: Measure and Recover the Store

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Run a full integrity check | All variants | `git fsck --full` |
| 2. Measure the object store | All variants | `git count-objects -vH` |
| 3. Read one ref's movement history | All variants | `git reflog show main` |
| 4. Recover the known-good state | First team's repository | `git reset --hard m1` |
|  | Second team's repository | `git reset --hard n1` |

#### Level 2: Read the reflog, then recover

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read the reflog, then recover | First team's repository | `git reflog show main` → `git reset --hard m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git reflog show main` → `git reset --hard n1` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Produce the storage health report

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Produce the storage health report | All variants | `git fsck --full` → `git count-objects -vH` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Check integrity, then recover the branch

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check integrity, then recover the branch | First team's repository | `git fsck --full` → `git reset --hard m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git fsck --full` → `git reset --hard n1` → `git status` → `git log --oneline --graph --all` |

#### Level 5: Audit the ref movement

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the ref movement | All variants | `git reflog show main` → `git count-objects -vH` → `git status` → `git log --oneline --graph --all` |

#### Level 6: Inspect the Object Store

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the Object Store | Author the repair from pending work | `git fsck --full` → `git status` → `git switch -c incident/sn-restore-maintain-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-restore-maintain-1 incident'` → `git tag sn-restore-maintain-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git fsck --full` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-restore-maintain-1 repair'` → `git tag sn-restore-maintain-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git fsck --full` → `git merge-base main feature/work` → `git switch -c incident/sn-restore-maintain-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-restore-maintain-1 repair'` → `git tag sn-restore-maintain-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git fsck --full` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-1-reverted main` → `git revert --no-edit d2` → `git tag sn-restore-maintain-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 7: Recover Before Maintenance

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Recover Before Maintenance | Author the repair from pending work | `git count-objects -vH` → `git status` → `git switch -c incident/sn-restore-maintain-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-restore-maintain-2 incident'` → `git tag sn-restore-maintain-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git count-objects -vH` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-restore-maintain-2 repair'` → `git tag sn-restore-maintain-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git count-objects -vH` → `git merge-base main feature/work` → `git switch -c incident/sn-restore-maintain-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-restore-maintain-2 repair'` → `git tag sn-restore-maintain-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git count-objects -vH` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-2-reverted main` → `git revert --no-edit d2` → `git tag sn-restore-maintain-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 8: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-restore-maintain-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-restore-maintain-3 incident'` → `git tag sn-restore-maintain-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-restore-maintain-3 repair'` → `git tag sn-restore-maintain-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-restore-maintain-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-restore-maintain-3 repair'` → `git tag sn-restore-maintain-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-restore-maintain-3-reverted main` → `git revert --no-edit d2` → `git tag sn-restore-maintain-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 11: Enter Git's Machinery

#### Level 1: Trace HEAD to the Object

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Read what HEAD points to | All variants | `git symbolic-ref HEAD` |
| 2. Decode a raw object | First team's repository | `git cat-file -p m1` |
|  | Second team's repository | `git cat-file -p n1` |

#### Level 2: Follow HEAD down to its object

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Follow HEAD down to its object | First team's repository | `git symbolic-ref HEAD` → `git cat-file -p m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git symbolic-ref HEAD` → `git cat-file -p n1` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Decode the object and prove its type

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Decode the object and prove its type | First team's repository | `git cat-file -t m1` → `git cat-file -p m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git cat-file -t n1` → `git cat-file -p n1` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Trace HEAD to Its Ref

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Trace HEAD to Its Ref | Author the repair from pending work | `git symbolic-ref HEAD` → `git status` → `git switch -c incident/sn-git-machinery-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-git-machinery-1 incident'` → `git tag sn-git-machinery-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git symbolic-ref HEAD` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-git-machinery-1 repair'` → `git tag sn-git-machinery-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git symbolic-ref HEAD` → `git merge-base main feature/work` → `git switch -c incident/sn-git-machinery-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-git-machinery-1 repair'` → `git tag sn-git-machinery-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git symbolic-ref HEAD` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-1-reverted main` → `git revert --no-edit d2` → `git tag sn-git-machinery-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 5: Repair the Visible Reference

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Repair the Visible Reference | Author the repair from pending work | `git show-ref` → `git status` → `git switch -c incident/sn-git-machinery-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-git-machinery-2 incident'` → `git tag sn-git-machinery-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-git-machinery-2 repair'` → `git tag sn-git-machinery-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git show-ref` → `git merge-base main feature/work` → `git switch -c incident/sn-git-machinery-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-git-machinery-2 repair'` → `git tag sn-git-machinery-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-2-reverted main` → `git revert --no-edit d2` → `git tag sn-git-machinery-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-git-machinery-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-git-machinery-3 incident'` → `git tag sn-git-machinery-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-git-machinery-3 repair'` → `git tag sn-git-machinery-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-git-machinery-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-git-machinery-3 repair'` → `git tag sn-git-machinery-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-git-machinery-3-reverted main` → `git revert --no-edit d2` → `git tag sn-git-machinery-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 09: Serve the City's Repositories

#### Level 1: Audit the Served Ref Set

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Enumerate every ref, formatted | All variants | `git for-each-ref` |
| 2. Audit the served reference set | All variants | `git show-ref` → `git for-each-ref` → `git status` → `git log --oneline --graph --all` |

#### Level 2: Audit the Served Refs

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Audit the Served Refs | Author the repair from pending work | `git for-each-ref` → `git status` → `git switch -c incident/sn-serve-the-city-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-serve-the-city-1 incident'` → `git tag sn-serve-the-city-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git for-each-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-serve-the-city-1 repair'` → `git tag sn-serve-the-city-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git for-each-ref` → `git merge-base main feature/work` → `git switch -c incident/sn-serve-the-city-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-serve-the-city-1 repair'` → `git tag sn-serve-the-city-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git for-each-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-1-reverted main` → `git revert --no-edit d2` → `git tag sn-serve-the-city-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 3: Repair the Synchronization Boundary

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Repair the Synchronization Boundary | Author the repair from pending work | `git show-ref` → `git status` → `git switch -c incident/sn-serve-the-city-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-serve-the-city-2 incident'` → `git tag sn-serve-the-city-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-serve-the-city-2 repair'` → `git tag sn-serve-the-city-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git show-ref` → `git merge-base main feature/work` → `git switch -c incident/sn-serve-the-city-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-serve-the-city-2 repair'` → `git tag sn-serve-the-city-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git show-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-2-reverted main` → `git revert --no-edit d2` → `git tag sn-serve-the-city-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 4: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-serve-the-city-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-serve-the-city-3 incident'` → `git tag sn-serve-the-city-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-serve-the-city-3 repair'` → `git tag sn-serve-the-city-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-serve-the-city-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-serve-the-city-3 repair'` → `git tag sn-serve-the-city-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-serve-the-city-3-reverted main` → `git revert --no-edit d2` → `git tag sn-serve-the-city-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 10: Migrate the Civic Grid

#### Level 1: Inspect the Migrated Objects

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Check what kind of object an id names | First team's repository | `git cat-file -t m1` |
|  | Second team's repository | `git cat-file -t n1` |
| 2. List what a commit's tree contains | First team's repository | `git ls-tree m1` |
|  | Second team's repository | `git ls-tree n1` |

#### Level 2: Verify one migrated commit end to end

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify one migrated commit end to end | First team's repository | `git cat-file -t m1` → `git ls-tree m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git cat-file -t n1` → `git ls-tree n1` → `git status` → `git log --oneline --graph --all` |

#### Level 3: Compare two commits' layouts

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Compare two commits' layouts | First team's repository | `git ls-tree m0` → `git ls-tree m1` → `git status` → `git log --oneline --graph --all` |
|  | Second team's repository | `git ls-tree n0` → `git ls-tree n1` → `git status` → `git log --oneline --graph --all` |

#### Level 4: Inspect the Migration Objects

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Inspect the Migration Objects | Author the repair from pending work | `git cat-file -t a1` → `git status` → `git switch -c incident/sn-migrate-the-grid-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-migrate-the-grid-1 incident'` → `git tag sn-migrate-the-grid-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git cat-file -t b1` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-migrate-the-grid-1 repair'` → `git tag sn-migrate-the-grid-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git cat-file -t c1` → `git merge-base main feature/work` → `git switch -c incident/sn-migrate-the-grid-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-migrate-the-grid-1 repair'` → `git tag sn-migrate-the-grid-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git cat-file -t d1` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-1-reverted main` → `git revert --no-edit d2` → `git tag sn-migrate-the-grid-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 5: Verify the Imported History

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Imported History | Author the repair from pending work | `git ls-tree a1` → `git status` → `git switch -c incident/sn-migrate-the-grid-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-migrate-the-grid-2 incident'` → `git tag sn-migrate-the-grid-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git ls-tree b1` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-migrate-the-grid-2 repair'` → `git tag sn-migrate-the-grid-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git ls-tree c1` → `git merge-base main feature/work` → `git switch -c incident/sn-migrate-the-grid-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-migrate-the-grid-2 repair'` → `git tag sn-migrate-the-grid-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git ls-tree d1` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-2-reverted main` → `git revert --no-edit d2` → `git tag sn-migrate-the-grid-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 6: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-migrate-the-grid-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-migrate-the-grid-3 incident'` → `git tag sn-migrate-the-grid-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-migrate-the-grid-3 repair'` → `git tag sn-migrate-the-grid-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-migrate-the-grid-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-migrate-the-grid-3 repair'` → `git tag sn-migrate-the-grid-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-migrate-the-grid-3-reverted main` → `git revert --no-edit d2` → `git tag sn-migrate-the-grid-3-reverted` → `git show` → `git log --oneline --graph --all` |

### Chapter 12: Open the Command Laboratory

#### Level 1: Classify the Remaining Interfaces

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Classify the Remaining Interfaces | Author the repair from pending work | `git for-each-ref` → `git status` → `git switch -c incident/sn-command-laboratory-1-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-command-laboratory-1 incident'` → `git tag sn-command-laboratory-1-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git for-each-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-1-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-command-laboratory-1 repair'` → `git tag sn-command-laboratory-1-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git for-each-ref` → `git merge-base main feature/work` → `git switch -c incident/sn-command-laboratory-1-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-command-laboratory-1 repair'` → `git tag sn-command-laboratory-1-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git for-each-ref` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-1-reverted main` → `git revert --no-edit d2` → `git tag sn-command-laboratory-1-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 2: Prove the Final Ref Transition

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Prove the Final Ref Transition | Author the repair from pending work | `git rev-parse HEAD` → `git status` → `git switch -c incident/sn-command-laboratory-2-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-command-laboratory-2 incident'` → `git tag sn-command-laboratory-2-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git rev-parse HEAD` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-2-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-command-laboratory-2 repair'` → `git tag sn-command-laboratory-2-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git rev-parse HEAD` → `git merge-base main feature/work` → `git switch -c incident/sn-command-laboratory-2-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-command-laboratory-2 repair'` → `git tag sn-command-laboratory-2-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git rev-parse HEAD` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-2-reverted main` → `git revert --no-edit d2` → `git tag sn-command-laboratory-2-reverted` → `git show` → `git log --oneline --graph --all` |

#### Level 3: Verify the Operational Handoff

| Wave | Variant | Command sequence |
|---:|---|---|
| 1. Verify the Operational Handoff | Author the repair from pending work | `git log --oneline --graph --all` → `git status` → `git switch -c incident/sn-command-laboratory-3-authored` → `git add src/repair.ts` → `git diff --staged` → `git commit -m 'Resolve sn-command-laboratory-3 incident'` → `git tag sn-command-laboratory-3-authored` → `git log --oneline --graph --all` |
|  | Transplant the isolated patch | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-3-transplanted main` → `git cherry-pick --no-commit b3` → `git status` → `git commit -m 'Transplant sn-command-laboratory-3 repair'` → `git tag sn-command-laboratory-3-transplanted` → `git log --oneline --graph --all` |
|  | Integrate the divergent repair as one reviewed snapshot | `git log --oneline --graph --all` → `git merge-base main feature/work` → `git switch -c incident/sn-command-laboratory-3-integrated main` → `git merge --squash feature/work` → `git status` → `git commit -m 'Integrate sn-command-laboratory-3 repair'` → `git tag sn-command-laboratory-3-integrated` → `git log --oneline --graph --all` |
|  | Reverse the shared failure additively | `git log --oneline --graph --all` → `git log --oneline --graph --all` → `git switch -c incident/sn-command-laboratory-3-reverted main` → `git revert --no-edit d2` → `git tag sn-command-laboratory-3-reverted` → `git show` → `git log --oneline --graph --all` |

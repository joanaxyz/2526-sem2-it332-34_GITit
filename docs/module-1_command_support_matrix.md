# Module 1 Command Support Matrix

Scope: Module 1 seeded scenarios and Skill Focus Preview only.

The simulator accepts only the forms below for Module 1. Diagnostic commands are read-only and non-counted. Action commands can change simulator state and count against the scenario action budget.

## Diagnostic, Non-Counted

| Command form | Module 1 purpose |
| --- | --- |
| `git status` | Inspect branch, staged, unstaged, and untracked state. |
| `git status -s` | Compact status. |
| `git status --short` | Compact status. |
| `git status --porcelain` | Stable compact status. |
| `git status -sb` | Compact status with branch header. |
| `git status --ignored` | Show ignored generated/local files. |
| `git diff` | Inspect unstaged tracked changes. |
| `git diff <path>` | Inspect unstaged changes for one path. |
| `git diff --staged` | Inspect staged changes. |
| `git diff --cached` | Inspect staged changes. |
| `git diff --staged <path>` | Inspect staged changes for one path. |
| `git diff --cached <path>` | Inspect staged changes for one path. |
| `git diff HEAD` | Inspect staged plus unstaged tracked changes since HEAD. |
| `git diff --name-only` | List unstaged changed paths only. |
| `git diff --staged --name-only` | List staged changed paths only. |
| `git log` | Inspect full commit history. |
| `git log --oneline` | Inspect compact commit history. |
| `git log --oneline --graph --all` | Inspect known branch/ref shape. |
| `git log -n <number>` | Limit displayed commits. |
| `git log --max-count=<number>` | Limit displayed commits. |
| `git show` | Inspect HEAD commit details. |
| `git show <commit>` | Inspect a named commit. |
| `git show --name-only` | Inspect changed paths for HEAD. |
| `git branch` | List local branches. |
| `git branch -v` | List branches with tip details. |
| `git remote` | List remote names. |
| `git remote -v` | List remote URLs. |
| `git reflog` | Inspect local HEAD movement records. |
| `git check-ignore -v <path>` | Explain the matching ignore rule for a path. |
| `git ls-files` | List tracked/index paths. |

## Action, Counted

| Command form | Module 1 purpose |
| --- | --- |
| `git init` | Initialize the current folder. |
| `git init <directory>` | Initialize a named folder. |
| `git init -b <branch>` | Set the first branch name. |
| `git init --initial-branch <branch>` | Set the first branch name. |
| `git init --initial-branch=<branch>` | Set the first branch name. |
| `git init -q` | Initialize quietly. |
| `git init --quiet` | Initialize quietly. |
| `git init -q -b <branch> <directory>` | Combine quiet mode, branch, and directory. |
| `git init --quiet --initial-branch=<branch> <directory>` | Combine quiet mode, branch, and directory. |
| `git clone <url>` | Clone a remote fixture into the default folder. |
| `git clone <url> <directory>` | Clone into a named local folder. |
| `git clone -b <branch> <url>` | Clone and check out a remote branch. |
| `git clone --branch <branch> <url>` | Clone and check out a remote branch. |
| `git clone -b <branch> <url> <directory>` | Clone a remote branch into a named local folder. |
| `git clone --branch <branch> <url> <directory>` | Clone a remote branch into a named local folder. |
| `git clone --depth <number> <url>` | Clone shallow history for the default branch. |
| `git clone --depth <number> <url> <directory>` | Clone shallow history into a named local folder. |
| `git clone --depth <number> -b <branch> <url> <directory>` | Shallow clone a selected branch into a named folder. |
| `git clone --depth <number> --branch <branch> <url> <directory>` | Shallow clone a selected branch into a named folder. |
| `git add <path>` | Stage one path. |
| `git add <path> <path>` | Stage multiple paths. |
| `git add <directory>/` | Stage changes under a directory. |
| `git add .` | Stage all visible working-tree changes. |
| `git add -A` | Stage all visible working-tree changes. |
| `git add --all` | Stage all visible working-tree changes. |
| `git add -u` | Stage tracked changes only. |
| `git add --update` | Stage tracked changes only. |
| `git add -p` | Stage authored target hunks. |
| `git add -p <path>` | Stage authored target hunks for a path. |
| `git add --patch <path>` | Stage authored target hunks for a path. |
| `git commit -m "message"` | Commit staged changes. |
| `git commit --message "message"` | Commit staged changes. |
| `git commit -am "message"` | Stage tracked changes, then commit. |
| `git commit -a -m "message"` | Stage tracked changes, then commit. |
| `git commit --amend` | Amend the latest commit with staged changes or existing message behavior. |
| `git commit --amend -m "message"` | Amend the latest commit with a new message. |
| `git commit --amend --no-edit` | Amend staged content while keeping the latest message. |
| `git rm --cached <path>` | Stop tracking a file while preserving local ignored content. |
| `git rm -r --cached <directory>` | Stop tracking a directory while preserving local ignored content. |
| `git restore <path>` | Discard working-tree changes for one path. |
| `git restore <path> <path>` | Discard working-tree changes for multiple paths. |
| `git restore .` | Discard visible working-tree changes. |
| `git restore --staged <path>` | Unstage one path. |
| `git restore --staged <path> <path>` | Unstage multiple paths. |
| `git restore --staged .` | Unstage all staged paths. |

## Explicitly Out Of Scope For Module 1

The Module 1 simulator rejects `git fetch`, `git pull`, `git push`, `git merge`, `git rebase`, `git stash`, `git tag`, `git cherry-pick`, and `git revert`.

Branch creation/deletion, remote mutation, checkout/switch, reset, empty commits, author filtering, arbitrary commit-range diffing, and advanced clone options such as `--bare`, `--mirror`, `--recurse-submodules`, `--no-checkout`, `--filter`, `--template`, and `--separate-git-dir` are also not documented for Module 1 preview content.

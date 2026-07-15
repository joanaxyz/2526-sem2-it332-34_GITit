"""Educational enrichment profiles for the Git command library.

The command catalog already knows *which* command forms exist. This module adds
teaching intent: mental models, before/after checks, scenarios, comparisons, and
self-check questions. Keeping this separate from the raw command catalog prevents
thin generated reference pages from becoming the long-term default.
"""
from __future__ import annotations

from typing import Any

BEGINNER_COMMAND_KEYS = {
    "git-init",
    "git-clone",
    "git-status",
    "git-add",
    "git-diff",
    "git-commit",
    "git-log",
    "git-branch",
    "git-switch",
    "git-restore",
    "gitignore",
}

EDUCATIONAL_PROFILES: dict[str, dict[str, Any]] = {
    "git-init": {
        "learning_goal": "Understand that git init creates repository metadata, not a first commit.",
        "problem_it_solves": "You have a local project folder and want Git to start tracking snapshots from this folder onward.",
        "mental_model": "git init turns a normal folder into a repository by creating .git metadata. Your files remain ordinary working-tree files until you stage and commit them.",
        "before_you_run": [
            "Confirm you are inside the correct project folder, not a parent folder such as Documents or Desktop.",
            "Run pwd or inspect the terminal path so the repository starts in the intended directory.",
            "Check whether the folder is already inside another Git repository before initializing again.",
        ],
        "after_you_run": [
            "Run git status to confirm Git recognizes the folder as a repository.",
            "Expect files to appear as untracked until you use git add.",
            "Do not expect a commit to exist yet; git init only prepares tracking.",
        ],
        "beginner_traps": [
            "Running git init from the wrong folder and accidentally making the parent directory the repository root.",
            "Thinking git init saves the current project files into history.",
            "Repeating git init when the real problem is unstaged or uncommitted work.",
        ],
        "wrong_command_comparisons": [
            {"command": "git init", "use_when": "Starting version control in an existing local folder.", "not_for": "Copying a remote repository."},
            {"command": "git clone", "use_when": "Creating a local copy from a remote URL.", "not_for": "Turning the current local folder into a new repository."},
        ],
        "scenario_examples": [
            {
                "title": "Start tracking a class project",
                "situation": "You created a folder named git-it and want Git history to begin there.",
                "steps": ["cd into the git-it folder.", "Run git init.", "Run git status and verify the project is now a repository."],
                "safe_command": "git init",
            }
        ],
        "mini_quiz": {
            "question": "After git init, are your project files already committed?",
            "choices": ["Yes", "No"],
            "answer": "No. They are only in the working tree until you stage and commit them.",
        },
        "state_flow": ["Normal folder", "Repository metadata (.git)", "Untracked working files", "Future staged snapshot", "Future commit"],
    },
    "git-clone": {
        "learning_goal": "Understand that git clone creates a new local repository copied from a remote source.",
        "problem_it_solves": "You need a working copy of an existing project, including its Git history and origin remote.",
        "mental_model": "git clone is init plus remote download plus checkout. It creates a new folder unless a destination directory is provided.",
        "before_you_run": [
            "Copy the exact remote URL from the scenario or repository host.",
            "Choose the destination folder deliberately so you do not clone into the wrong location.",
            "Check whether the scenario requires a branch or shallow depth option.",
        ],
        "after_you_run": [
            "cd into the cloned folder before running later Git commands.",
            "Run git status to confirm the working tree is clean.",
            "Run git remote -v when the scenario asks you to prove the origin URL.",
        ],
        "beginner_traps": [
            "Running git init before clone and creating an unnecessary nested repository.",
            "Cloning to the wrong destination folder.",
            "Forgetting to enter the cloned directory after the command succeeds.",
        ],
        "wrong_command_comparisons": [
            {"command": "git clone", "use_when": "You start from a remote project URL.", "not_for": "A local folder you already created yourself."},
            {"command": "git init", "use_when": "You start from local files only.", "not_for": "Downloading a remote repository."},
        ],
        "scenario_examples": [
            {
                "title": "Copy a remote starter repo",
                "situation": "The level gives a URL and asks you to begin from that remote project.",
                "steps": ["Use the exact URL.", "Add a destination folder only if the scenario names one.", "Open the cloned folder before continuing."],
                "safe_command": "git clone <url> <directory>",
            }
        ],
        "mini_quiz": {
            "question": "What relationship does clone record by default?",
            "choices": ["origin remote", "a staged snapshot", "a new commit"],
            "answer": "It records the source repository as the origin remote.",
        },
        "state_flow": ["Remote repository", "Local clone folder", "origin remote", "Checked-out branch"],
    },
    "git-status": {
        "learning_goal": "Use git status as the main map of working-tree, index, branch, and conflict state.",
        "problem_it_solves": "You need to know what changed before deciding whether to add, commit, restore, or inspect more deeply.",
        "mental_model": "git status is a dashboard. It does not fix anything; it tells you which area each path currently belongs to.",
        "before_you_run": ["Be inside the repository you want to inspect.", "Know whether you need normal, short, branch, or ignored output."],
        "after_you_run": [
            "Separate staged changes from unstaged changes.",
            "Notice untracked files before assuming git add or commit will include them.",
            "Use git diff or git diff --staged for content details when status only gives path names.",
        ],
        "beginner_traps": [
            "Seeing a file name in status and assuming it is already staged.",
            "Ignoring the branch/upstream line.",
            "Treating status as an action command when it only reports state.",
        ],
        "wrong_command_comparisons": [
            {"command": "git status", "use_when": "You need file categories and branch state.", "not_for": "Reading exact line-by-line changes."},
            {"command": "git diff", "use_when": "You need patch details for unstaged changes.", "not_for": "A quick overall summary of every path category."},
        ],
        "scenario_examples": [
            {"title": "Choose the next command", "situation": "A level says files may be staged, unstaged, or untracked.", "steps": ["Run git status.", "Identify the exact category of each path.", "Only then choose add, restore, commit, or diff."], "safe_command": "git status"}
        ],
        "mini_quiz": {"question": "Does git status change repository state?", "choices": ["Yes", "No"], "answer": "No. It is a diagnostic command."},
        "state_flow": ["Working tree", "Index", "Current branch", "Status report"],
    },
    "git-add": {
        "learning_goal": "Understand that git add copies selected current file content into the index.",
        "problem_it_solves": "You changed files, but Git needs to know which exact content belongs in the next commit snapshot.",
        "mental_model": "The index is a draft of the next commit. git add updates that draft; it does not save history by itself.",
        "before_you_run": [
            "Run git status to see which paths changed.",
            "Run git diff when you need to inspect unstaged content before staging it.",
            "Choose the narrowest path or patch mode that matches the scenario.",
        ],
        "after_you_run": [
            "Run git status again to confirm the intended paths moved to staged changes.",
            "Run git diff --staged to inspect the exact snapshot prepared for commit.",
            "Unstage with git restore --staged if the wrong content entered the index.",
        ],
        "beginner_traps": [
            "Thinking git add creates a commit.",
            "Using git add . when the scenario only asked for one file.",
            "Editing a file again after staging and forgetting the index still contains the older staged version.",
        ],
        "wrong_command_comparisons": [
            {"command": "git add", "use_when": "You want selected content in the next commit.", "not_for": "Saving the commit into history."},
            {"command": "git commit", "use_when": "The index is already correct and should become history.", "not_for": "Choosing which changed files enter the snapshot."},
            {"command": "git restore --staged", "use_when": "Something was staged by mistake.", "not_for": "Discarding working-tree edits."},
        ],
        "scenario_examples": [
            {"title": "Stage only the lesson file", "situation": "README.md and debug.log changed, but only README.md belongs in the next commit.", "steps": ["Run git status.", "Use git add README.md, not git add .", "Run git diff --staged to verify debug.log was not staged."], "safe_command": "git add README.md"}
        ],
        "mini_quiz": {"question": "Which area does git add change?", "choices": ["Working tree", "Index/staging area", "Remote repository"], "answer": "It changes the index/staging area."},
        "state_flow": ["Working tree change", "git add <path>", "Index / staged snapshot", "git commit", "Repository history"],
    },
    "git-diff": {
        "learning_goal": "Use git diff to inspect content differences before choosing an action.",
        "problem_it_solves": "Status tells you which paths changed; diff shows the actual line-level edits.",
        "mental_model": "diff is a comparison lens. Different flags choose different sides: working tree, index, HEAD, or conflict stages.",
        "before_you_run": ["Decide whether you need unstaged changes, staged changes, or committed differences.", "Use a path argument when the scenario names one file."],
        "after_you_run": ["Decide whether the shown edits should be staged, discarded, or left alone.", "If the output is empty, check whether the changes are already staged or in another path."],
        "beginner_traps": ["Running plain git diff after staging and thinking the staged content disappeared.", "Comparing the wrong side of the index.", "Skipping diff and staging unwanted debug edits."],
        "wrong_command_comparisons": [
            {"command": "git diff", "use_when": "You need unstaged working-tree edits by default.", "not_for": "A summary of all file categories."},
            {"command": "git diff --staged", "use_when": "You need the snapshot already prepared for commit.", "not_for": "Unstaged edits still outside the index."},
            {"command": "git status", "use_when": "You need categories first.", "not_for": "Line-by-line content review."},
        ],
        "scenario_examples": [
            {"title": "Inspect before staging", "situation": "A level says one file has accidental debug output.", "steps": ["Run git diff <path>.", "Confirm whether the debug line is present.", "Only stage the file after the content is correct."], "safe_command": "git diff <path>"}
        ],
        "mini_quiz": {"question": "Why might plain git diff show no output after git add?", "choices": ["The staged changes are compared with --staged", "The repository was deleted", "Git cannot diff text files"], "answer": "Because plain git diff shows unstaged changes; staged changes require git diff --staged."},
        "state_flow": ["Working tree", "Index", "HEAD", "Selected comparison", "Patch output"],
    },
    "git-diff-staged": {
        "learning_goal": "Inspect the exact staged snapshot before committing it.",
        "problem_it_solves": "You need to verify what the next commit would contain, not just what is still unstaged.",
        "mental_model": "git diff --staged compares the index against HEAD. It previews the commit draft.",
        "before_you_run": ["Stage the candidate files first.", "Know whether you are checking the whole index or one path."],
        "after_you_run": ["Commit only if the staged patch matches the scenario.", "Use git restore --staged for anything that should leave the index."],
        "beginner_traps": ["Committing without reviewing the staged patch.", "Using plain git diff and missing staged mistakes.", "Forgetting that new edits after git add may still be unstaged."],
        "wrong_command_comparisons": [
            {"command": "git diff --staged", "use_when": "Reviewing the commit draft.", "not_for": "Viewing unstaged edits not yet added."},
            {"command": "git diff", "use_when": "Viewing working-tree edits outside the index.", "not_for": "Final staged snapshot review."},
        ],
        "scenario_examples": [
            {"title": "Review the commit draft", "situation": "You staged README.md and want to prove only the intended lesson text will be committed.", "steps": ["Run git diff --staged README.md.", "Read the added and removed lines.", "Commit only when the staged patch is correct."], "safe_command": "git diff --staged README.md"}
        ],
        "mini_quiz": {"question": "What does git diff --staged compare?", "choices": ["Index vs HEAD", "Working tree vs index", "Remote vs local"], "answer": "It compares the index/staging area against HEAD."},
        "state_flow": ["HEAD", "Index / staged snapshot", "git diff --staged", "Patch to be committed"],
    },
    "git-commit": {
        "learning_goal": "Understand that git commit saves the staged snapshot as a local history point.",
        "problem_it_solves": "The index contains a correct snapshot and you need to record it with a message.",
        "mental_model": "A commit is a labeled snapshot plus parent link. It comes from the index, not automatically from every file on disk.",
        "before_you_run": ["Run git status to confirm the staged paths.", "Run git diff --staged to review the exact snapshot.", "Choose a message that describes why this snapshot exists."],
        "after_you_run": ["Run git log --oneline to see the new commit.", "Run git status to verify no intended changes were left behind.", "Remember the commit is still local until pushed."],
        "beginner_traps": ["Committing with nothing staged.", "Assuming unstaged files were included.", "Using vague messages that do not match the scenario."],
        "wrong_command_comparisons": [
            {"command": "git add", "use_when": "Preparing the index.", "not_for": "Creating history."},
            {"command": "git commit", "use_when": "The staged snapshot is ready to save.", "not_for": "Publishing to a remote."},
            {"command": "git push", "use_when": "Local commits need to be sent to a remote.", "not_for": "Creating the local commit itself."},
        ],
        "scenario_examples": [
            {"title": "Save a focused snapshot", "situation": "Only README.md is staged and the level gives the message 'document init'.", "steps": ["Review git diff --staged.", "Run git commit -m \"document init\".", "Check git log --oneline for the new message."], "safe_command": "git commit -m \"document init\""}
        ],
        "mini_quiz": {"question": "Where does commit get its file content from?", "choices": ["Index/staging area", "All files in the folder", "The remote repository"], "answer": "From the index/staging area."},
        "state_flow": ["Index / staged snapshot", "git commit", "New commit", "Current branch points to new commit"],
    },
    "git-log": {
        "learning_goal": "Use git log to read commit history and branch shape before choosing a commit or judging progress.",
        "problem_it_solves": "You need evidence about past commits, messages, ancestry, or graph structure.",
        "mental_model": "git log walks commit links. Options decide how much history and which refs are visible.",
        "before_you_run": ["Decide whether you need current-branch history only or all refs.", "Use --oneline or --graph when shape matters more than full details."],
        "after_you_run": ["Copy the exact commit id or message evidence from the output.", "Do not assume hidden branches were shown unless you used the right ref options."],
        "beginner_traps": ["Reading only the current branch when the task asks about all branches.", "Confusing newest-first order with oldest-first order.", "Using log when status is needed for uncommitted changes."],
        "wrong_command_comparisons": [
            {"command": "git log", "use_when": "Reading committed history.", "not_for": "Checking unstaged or staged files."},
            {"command": "git status", "use_when": "Checking current working/index state.", "not_for": "Reading old commits."},
        ],
        "scenario_examples": [
            {"title": "Find the latest commit", "situation": "The level asks which commit message is at the branch tip.", "steps": ["Run git log --oneline -n 3.", "Read the first line as the newest visible commit.", "Use --all --graph if branch shape matters."], "safe_command": "git log --oneline -n 3"}
        ],
        "mini_quiz": {"question": "Does git log show uncommitted working-tree edits?", "choices": ["Yes", "No"], "answer": "No. Use status or diff for uncommitted state."},
        "state_flow": ["Branch ref", "Commit chain", "git log options", "History report"],
    },
    "git-branch": {
        "learning_goal": "Understand that git branch manages branch names/pointers, not your current checkout by itself.",
        "problem_it_solves": "You need to list, create, inspect, or delete branch pointers.",
        "mental_model": "A branch is a movable name pointing to a commit. Creating a branch creates the name; switching moves HEAD to it.",
        "before_you_run": ["Run git status or git branch to know where HEAD is.", "Confirm whether the task asks to create, list, or delete a branch."],
        "after_you_run": ["Run git branch to verify the pointer exists or was removed.", "Use git switch if the task also requires moving onto that branch."],
        "beginner_traps": ["Creating a branch and assuming you switched to it.", "Deleting the wrong branch name.", "Confusing branch names with commit ids."],
        "wrong_command_comparisons": [
            {"command": "git branch", "use_when": "Creating/listing/deleting branch pointers.", "not_for": "Moving HEAD to another branch."},
            {"command": "git switch", "use_when": "Changing the current branch.", "not_for": "Only listing all branch pointers."},
        ],
        "scenario_examples": [
            {"title": "Create a branch pointer", "situation": "The level asks you to create feature/login but keep your current branch unchanged.", "steps": ["Run git branch feature/login.", "Run git branch and check the star remains on the old branch."], "safe_command": "git branch feature/login"}
        ],
        "mini_quiz": {"question": "After git branch new-name, are you automatically on new-name?", "choices": ["Yes", "No"], "answer": "No. Use git switch new-name to move HEAD there."},
        "state_flow": ["Current commit", "git branch <name>", "New branch pointer", "HEAD unchanged"],
    },
    "git-switch": {
        "learning_goal": "Use git switch to move HEAD to another branch, optionally creating it first.",
        "problem_it_solves": "You need to work from a different branch pointer without using checkout's older mixed behavior.",
        "mental_model": "HEAD follows the selected branch. Switching changes the branch you are working on; it does not merge branches.",
        "before_you_run": ["Run git status and handle local changes that should not travel with you.", "Confirm the target branch exists or use -c when the task asks to create it."],
        "after_you_run": ["Run git status or git branch to verify the current branch line.", "Do not assume any commits were merged just because you switched."],
        "beginner_traps": ["Switching with accidental local changes.", "Using git branch to create a branch but forgetting to switch.", "Expecting switch to integrate another branch's work."],
        "wrong_command_comparisons": [
            {"command": "git switch", "use_when": "Moving HEAD to a branch.", "not_for": "Combining branch histories."},
            {"command": "git merge", "use_when": "Integrating another branch into the current branch.", "not_for": "Simply changing the current branch."},
        ],
        "scenario_examples": [
            {"title": "Create and enter a feature branch", "situation": "The level asks you to start work on feature/map from the current commit.", "steps": ["Run git status first.", "Run git switch -c feature/map.", "Verify the branch line now names feature/map."], "safe_command": "git switch -c feature/map"}
        ],
        "mini_quiz": {"question": "Does git switch merge branch histories?", "choices": ["Yes", "No"], "answer": "No. It only changes the current branch."},
        "state_flow": ["HEAD -> old branch", "git switch <branch>", "HEAD -> target branch", "Working tree updates"],
    },
    "git-restore": {
        "learning_goal": "Understand when git restore discards working-tree edits and why that is different from unstaging.",
        "problem_it_solves": "You want selected files on disk to return to the chosen source version.",
        "mental_model": "restore writes files from a source into the working tree unless --staged tells it to target the index instead.",
        "before_you_run": ["Check git status and git diff so you know what will be lost.", "Confirm the path is exact and narrow.", "Use --staged instead if the goal is only to unstage."],
        "after_you_run": ["Run git status to confirm the working-tree change disappeared.", "Recover only if you have another copy; discarded unstaged edits are not saved as history."],
        "beginner_traps": ["Discarding work that was supposed to be kept but unstaged.", "Running a broad restore path.", "Forgetting restore affects files on disk by default."],
        "wrong_command_comparisons": [
            {"command": "git restore <path>", "use_when": "Discarding working-tree edits for a path.", "not_for": "Only removing staged content from the index."},
            {"command": "git restore --staged <path>", "use_when": "Unstaging while keeping local edits.", "not_for": "Discarding local edits from disk."},
        ],
        "scenario_examples": [
            {"title": "Discard an accidental debug edit", "situation": "debug.log was edited locally and the level says those edits should be thrown away.", "steps": ["Run git diff debug.log to inspect what will be lost.", "Run git restore debug.log.", "Run git status to verify the working-tree change is gone."], "safe_command": "git restore debug.log"}
        ],
        "mini_quiz": {"question": "Plain git restore <path> changes which area?", "choices": ["Working tree", "Remote repository", "Commit history"], "answer": "It changes the working tree file on disk."},
        "state_flow": ["HEAD or source", "git restore <path>", "Working tree file replaced"],
    },
    "git-restore-staged": {
        "learning_goal": "Use git restore --staged to unstage content without deleting local edits.",
        "problem_it_solves": "Something entered the index, but it should not be part of the next commit yet.",
        "mental_model": "--staged targets the index. The working tree keeps the edited file so you can revise or stage it later.",
        "before_you_run": ["Run git status or git diff --staged to identify the staged path.", "Confirm you want to keep the working-tree changes."],
        "after_you_run": ["Run git status to confirm the path moved from staged to unstaged.", "Use git diff to review the still-present local edits."],
        "beginner_traps": ["Using plain restore and accidentally discarding the working-tree file.", "Thinking unstage means undo all edits.", "Unstaging the wrong path from a broad command."],
        "wrong_command_comparisons": [
            {"command": "git restore --staged <path>", "use_when": "Removing content from the index while keeping the file edited.", "not_for": "Discarding the edit from disk."},
            {"command": "git restore <path>", "use_when": "Discarding working-tree edits.", "not_for": "A safe unstage operation."},
        ],
        "scenario_examples": [
            {"title": "Unstage a secret file", "situation": "secrets.env was staged by mistake but should remain locally for now.", "steps": ["Run git diff --staged secrets.env.", "Run git restore --staged secrets.env.", "Run git status and confirm secrets.env is no longer staged."], "safe_command": "git restore --staged secrets.env"}
        ],
        "mini_quiz": {"question": "After git restore --staged file.txt, is file.txt deleted from disk?", "choices": ["Yes", "No"], "answer": "No. It is kept in the working tree unless another command discards it."},
        "state_flow": ["Index / staged path", "git restore --staged <path>", "Working-tree edit remains", "Index returns toward HEAD"],
    },
    "gitignore": {
        "learning_goal": "Understand that .gitignore prevents matching untracked files from appearing as candidates for staging.",
        "problem_it_solves": "Generated files, local settings, logs, or secrets should stay out of Git history by default.",
        "mental_model": ".gitignore is a rule file. It hides matching untracked paths from normal status/add behavior, but it does not remove files already tracked.",
        "before_you_run": ["Identify whether the file is untracked or already tracked.", "Write the narrowest ignore pattern that matches the generated path.", "Avoid ignoring source files that classmates or production need."],
        "after_you_run": ["Run git status to see whether the generated path disappeared from untracked files.", "Use git check-ignore -v <path> when you need to prove which rule matched.", "Stage and commit the .gitignore rule if the team needs it."],
        "beginner_traps": ["Expecting .gitignore to untrack files that were already committed.", "Using broad patterns that hide real source code.", "Forgetting to commit the .gitignore file itself."],
        "wrong_command_comparisons": [
            {"command": ".gitignore", "use_when": "Future untracked generated files should stay out of status/add.", "not_for": "Removing a file that is already tracked."},
            {"command": "git rm --cached", "use_when": "A tracked file should stop being tracked but remain locally.", "not_for": "Creating a future ignore rule by itself."},
        ],
        "scenario_examples": [
            {"title": "Ignore generated logs", "situation": "app.log is generated locally and should not be committed.", "steps": ["Add app.log or *.log to .gitignore based on the scenario.", "Run git check-ignore -v app.log.", "Stage .gitignore, not the generated log."], "safe_command": "echo app.log >> .gitignore"}
        ],
        "mini_quiz": {"question": "Does .gitignore automatically remove a file that is already tracked?", "choices": ["Yes", "No"], "answer": "No. Tracked files require an explicit untracking command such as git rm --cached."},
        "state_flow": ["Ignore rule", "Untracked generated file", "Hidden from normal status/add", "Tracked files unaffected"],
    },
}

# Some catalog keys are specialized forms of the same concept. Use the focused
# profile when available; otherwise fall back to the base command's profile.
_PROFILE_FALLBACKS = {
    "git-add-p": "git-add",
    "git-commit-amend": "git-commit",
}


def educational_profile_for_key(key: str, base_command: str = "") -> dict[str, Any]:
    """Return educational enrichment for a library entry key.

    A shallow copy is returned so callers can safely add entry-specific values.
    """
    direct = EDUCATIONAL_PROFILES.get(key)
    if direct is None:
        direct = EDUCATIONAL_PROFILES.get(_PROFILE_FALLBACKS.get(key, ""))
    if direct is None and base_command:
        base_key = base_command.strip().lower().replace(" ", "-").replace(".", "")
        direct = EDUCATIONAL_PROFILES.get(base_key)
    return dict(direct or {})

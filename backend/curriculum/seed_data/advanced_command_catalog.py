"""Additive advanced/expert command catalog for Frostbound Citadel and Neon Backstreets.

The Arcane Spire catalog is intentionally left untouched. Forms marked
``reference_only`` are fully authored in the chapter book but are not yet used
as standalone simulator levels; interactive and external-system workflows are
introduced through representative playable forms and can be expanded without
changing chapter identity or command-library keys.
"""


def form(slug, usage, label, module, *, reference_only=False, summary=""):
    row = {
        "slug": slug,
        "usage_form": usage,
        "label": label,
        "module": module,
        "summary": summary,
    }
    if reference_only:
        row["reference_only"] = True
    return row


COMMAND_FORM_EXTENSIONS = {
    "git-diff": [
        form("stat-advanced", "git diff --stat", "Summarize patch size", "frost-temper-the-commit"),
        form("word-diff", "git diff --word-diff", "Review word-level changes", "frost-temper-the-commit", reference_only=True),
        form("check-whitespace", "git diff --check", "Check whitespace errors", "frost-temper-the-commit"),
        form("three-dot", "git diff <a>...<b>", "Compare a branch from its merge base", "frost-choose-the-integration"),
    ],
    "git-add": [
        form("patch-advanced", "git add -p", "Stage selected hunks deliberately", "frost-temper-the-commit"),
        form("tracked-only-advanced", "git add -u", "Stage tracked edits and deletions", "frost-temper-the-commit"),
    ],
    "git-commit": [
        form("amend-advanced", "git commit --amend", "Rewrite the latest local commit", "frost-temper-the-commit"),
        form("amend-no-edit-advanced", "git commit --amend --no-edit", "Amend while preserving the message", "frost-temper-the-commit"),
        form("fixup", "git commit --fixup <commit>", "Create an autosquash fixup commit", "frost-reforge-the-branch", reference_only=True),
        form("signed", "git commit -S", "Create a signed commit", "skyline-guard-the-archive", reference_only=True),
    ],
    "git-reset": [
        form("soft", "git reset --soft <commit>", "Move HEAD and keep the index", "frost-temper-the-commit"),
        form("mixed", "git reset --mixed <commit>", "Move HEAD and unstage the snapshot", "frost-temper-the-commit"),
        form("hard-advanced", "git reset --hard <commit>", "Move HEAD and discard local state", "frost-temper-the-commit"),
        form("reflog-recovery", "git reset --hard <reflog-entry>", "Recover a known reflog state", "skyline-restore-maintain"),
    ],
    "git-restore": [
        form("patch", "git restore -p", "Restore selected hunks", "frost-temper-the-commit", reference_only=True),
        form("source-advanced", "git restore --source <commit> <path>", "Restore a path from another revision", "frost-temper-the-commit"),
    ],
    "git-merge": [
        form("no-ff-advanced", "git merge --no-ff <branch>", "Preserve an explicit integration commit", "frost-choose-the-integration"),
        form("squash-advanced", "git merge --squash <branch>", "Stage a branch as one combined change", "frost-choose-the-integration"),
        form("continue-advanced", "git merge --continue", "Continue a resolved merge", "frost-survive-the-conflict"),
        form("abort-advanced", "git merge --abort", "Abort an unsafe merge", "frost-survive-the-conflict"),
    ],
    "git-merge-base": [
        form("is-ancestor", "git merge-base --is-ancestor <a> <b>", "Test ancestry", "skyline-revision-language", reference_only=True),
    ],
    "git-ls-files": [
        form("unmerged-advanced", "git ls-files -u", "Inspect conflict stages", "frost-survive-the-conflict"),
        form("stage", "git ls-files --stage", "Inspect index entries", "skyline-git-machinery", reference_only=True),
    ],
    "git-checkout-conflict": [
        form("ours-advanced", "git checkout --ours <path>", "Take the current side", "frost-survive-the-conflict"),
        form("theirs-advanced", "git checkout --theirs <path>", "Take the incoming side", "frost-survive-the-conflict"),
    ],
    "git-diff-conflict": [
        form("base-advanced", "git diff --base <path>", "Compare the conflict base", "frost-survive-the-conflict"),
        form("ours-advanced", "git diff --ours <path>", "Compare the current side", "frost-survive-the-conflict"),
        form("theirs-advanced", "git diff --theirs <path>", "Compare the incoming side", "frost-survive-the-conflict"),
    ],
    "git-stash": [
        form("push-untracked-message", "git stash push -u -m <message>", "Stash tracked and untracked work", "frost-move-the-patch"),
        form("show-patch", "git stash show stash@{n}", "Inspect a stash entry", "frost-move-the-patch"),
        form("apply-indexed", "git stash apply stash@{n}", "Apply a chosen stash", "frost-move-the-patch"),
        form("pop-indexed", "git stash pop stash@{n}", "Pop a chosen stash", "frost-move-the-patch"),
        form("branch", "git stash branch <branch> stash@{n}", "Recover a stash on a branch", "frost-move-the-patch", reference_only=True),
        form("drop-indexed", "git stash drop stash@{n}", "Drop a chosen stash", "frost-move-the-patch"),
    ],
    "git-cherry-pick": [
        form("range", "git cherry-pick <start>^..<end>", "Transplant a commit range", "frost-move-the-patch", reference_only=True),
        form("continue", "git cherry-pick --continue", "Continue a resolved cherry-pick", "frost-move-the-patch", reference_only=True),
        form("abort-advanced", "git cherry-pick --abort", "Abort a cherry-pick sequence", "frost-move-the-patch"),
    ],
    "git-revert": [
        form("merge-mainline", "git revert -m <parent> <merge-commit>", "Revert a merge relative to its mainline", "frost-move-the-patch", reference_only=True),
    ],
    "git-fetch": [
        form("all-advanced", "git fetch --all", "Fetch every configured remote", "frost-govern-the-remote"),
        form("prune-advanced", "git fetch --prune", "Fetch and prune stale refs", "frost-govern-the-remote"),
        form("tags", "git fetch --tags", "Fetch tags", "frost-govern-the-remote", reference_only=True),
        form("refspec", "git fetch origin main:refs/remotes/origin/main", "Fetch with an explicit refspec", "frost-govern-the-remote", reference_only=True),
        form("filter", "git fetch --filter=<filter>", "Fetch through a partial-clone filter", "skyline-many-realities", reference_only=True),
    ],
    "git-pull": [
        form("ff-only-advanced", "git pull --ff-only", "Pull only when fast-forward is possible", "frost-govern-the-remote"),
        form("rebase-advanced", "git pull --rebase", "Fetch and replay local work", "frost-govern-the-remote"),
        form("merge-policy", "git pull --no-rebase", "Fetch and merge upstream", "frost-govern-the-remote", reference_only=True),
    ],
    "git-push": [
        form("force-with-lease-advanced", "git push --force-with-lease", "Publish rewritten history safely", "frost-govern-the-remote"),
        form("delete-advanced", "git push <remote> --delete <branch>", "Delete a remote branch", "frost-govern-the-remote"),
        form("one-tag", "git push <remote> <tag>", "Publish one tag", "frost-deliver-the-release", reference_only=True),
        form("all-tags", "git push --tags", "Publish all tags", "frost-deliver-the-release"),
    ],
    "git-remote": [
        form("show", "git remote show <name>", "Inspect a remote relationship", "frost-govern-the-remote", reference_only=True),
        form("prune", "git remote prune <remote>", "Prune stale remote-tracking refs", "frost-govern-the-remote", reference_only=True),
        form("rename", "git remote rename <old> <new>", "Rename a remote", "frost-govern-the-remote", reference_only=True),
        form("set-url-advanced", "git remote set-url <name> <url>", "Change a remote URL", "frost-govern-the-remote"),
    ],
    "git-branch": [
        form("tracking", "git branch -vv", "Inspect upstream tracking", "frost-govern-the-remote"),
        form("set-upstream", "git branch --set-upstream-to=<remote>/<branch>", "Set an upstream branch", "frost-govern-the-remote", reference_only=True),
    ],
    "git-log": [
        form("first-parent", "git log --first-parent", "Read integration history", "frost-choose-the-integration", reference_only=True),
        form("left-right", "git log --left-right <a>...<b>", "Read both sides of divergence", "frost-choose-the-integration", reference_only=True),
        form("author", "git log --author=<pattern>", "Search history by author", "skyline-hidden-history", reference_only=True),
        form("grep", "git log --grep=<pattern>", "Search commit messages", "skyline-hidden-history", reference_only=True),
        form("date-range", "git log --since=<date> --until=<date>", "Search a time range", "skyline-hidden-history", reference_only=True),
        form("pickaxe-string", "git log -S<string>", "Search where text count changed", "skyline-hidden-history", reference_only=True),
        form("pickaxe-regex", "git log -G<regex>", "Search patches by regex", "skyline-hidden-history", reference_only=True),
        form("follow", "git log --follow -- <path>", "Follow a renamed path", "skyline-hidden-history", reference_only=True),
        form("format", "git log --format=<format>", "Format history output", "skyline-hidden-history", reference_only=True),
        form("show-signature", "git log --show-signature", "Inspect commit signatures", "skyline-guard-the-archive", reference_only=True),
    ],
    "git-show": [
        form("path-at-revision", "git show <commit>:<path>", "Read a file from a revision", "skyline-hidden-history"),
    ],
    "git-reflog": [
        form("show-ref", "git reflog show <ref>", "Inspect one ref's reflog", "skyline-restore-maintain"),
    ],
    "git-clone": [
        form("partial", "git clone --filter=blob:none <url>", "Create a partial clone", "skyline-many-realities", reference_only=True),
        form("bare", "git clone --bare <url>", "Create a bare clone", "skyline-git-machinery", reference_only=True),
        form("mirror", "git clone --mirror <url>", "Create a mirror clone", "skyline-git-machinery", reference_only=True),
    ],
    "git-init": [
        form("bare", "git init --bare", "Create a bare repository", "skyline-git-machinery", reference_only=True),
    ],
    "git-config": [
        form("system", "git config --system <key> <value>", "Set system configuration", "skyline-enchant-behavior", reference_only=True),
        form("local", "git config --local <key> <value>", "Set repository configuration", "skyline-enchant-behavior", reference_only=True),
        form("worktree", "git config --worktree <key> <value>", "Set worktree configuration", "skyline-enchant-behavior", reference_only=True),
        form("get", "git config --get <key>", "Read one configuration value", "skyline-enchant-behavior"),
        form("get-all", "git config --get-all <key>", "Read all values for a key", "skyline-enchant-behavior", reference_only=True),
        form("unset", "git config --unset <key>", "Remove a configuration value", "skyline-enchant-behavior", reference_only=True),
        form("show-scope", "git config --show-scope --list", "Inspect configuration scopes", "skyline-enchant-behavior", reference_only=True),
        form("rerere-enable", "git config rerere.enabled true", "Enable recorded conflict reuse", "skyline-repeated-conflict", reference_only=True),
        form("conflict-style", "git config merge.conflictStyle zdiff3", "Choose richer conflict markers", "skyline-repeated-conflict", reference_only=True),
        form("safe-directory", "git config --global --add safe.directory <path>", "Trust an explicitly safe repository", "skyline-guard-the-archive", reference_only=True),
    ],
    "git-tag": [
        form("lightweight-advanced", "git tag <name>", "Create a lightweight tag", "frost-deliver-the-release"),
        form("annotated-advanced", "git tag -a <name> -m <message>", "Create an annotated release tag", "frost-deliver-the-release"),
        form("delete-advanced", "git tag -d <name>", "Delete a local tag", "frost-deliver-the-release"),
        form("signed", "git tag -s <tag> -m <message>", "Create a signed tag", "skyline-guard-the-archive", reference_only=True),
    ],
    "git-rev-list": [
        form("left-right-count", "git rev-list --left-right --count <a>...<b>", "Count both sides of divergence", "frost-choose-the-integration", reference_only=True),
        form("revision-set", "git rev-list <revision-set>", "Enumerate a commit set", "skyline-revision-language"),
        form("ancestry-path", "git rev-list --ancestry-path <old>..<new>", "Trace an ancestry path", "skyline-revision-language", reference_only=True),
    ],
}


NEW_COMMAND_SKILLS = [
    {
        "module": "frost-reforge-the-branch",
        "slug": "git-rebase",
        "base_command": "git rebase",
        "title": "git rebase",
        "summary": "Replay a commit series onto a new base while preserving a reviewable patch sequence.",
        "usages": [
            form("branch", "git rebase <upstream>", "Replay the current branch onto an upstream", "frost-reforge-the-branch"),
            form("onto", "git rebase --onto <new-base> <old-base> <branch>", "Move a selected commit range to a new base", "frost-reforge-the-branch", reference_only=True),
            form("interactive", "git rebase -i <upstream>", "Edit a local commit series interactively", "frost-reforge-the-branch", reference_only=True),
            form("autosquash", "git rebase -i --autosquash <upstream>", "Apply fixup and squash intentions", "frost-reforge-the-branch", reference_only=True),
            form("continue", "git rebase --continue", "Continue after resolving a rebase stop", "frost-reforge-the-branch", reference_only=True),
            form("abort", "git rebase --abort", "Return to the pre-rebase state", "frost-reforge-the-branch"),
        ],
    },
    {
        "module": "frost-choose-the-integration",
        "slug": "git-range-diff",
        "base_command": "git range-diff",
        "title": "git range-diff",
        "summary": "Compare two versions of a patch series after rewriting.",
        "usages": [form("series", "git range-diff <old-range> <new-range>", "Compare rewritten patch series", "frost-reforge-the-branch")],
    },
    {
        "module": "frost-choose-the-integration",
        "slug": "git-shortlog",
        "base_command": "git shortlog",
        "title": "git shortlog",
        "summary": "Summarize commits by author for releases and contributor reports.",
        "usages": [
            form("summary", "git shortlog", "Summarize contributors", "frost-deliver-the-release"),
            form("numbered", "git shortlog -sn <range>", "Count commits by contributor", "frost-deliver-the-release"),
        ],
    },
    {
        "module": "frost-deliver-the-release",
        "slug": "git-describe",
        "base_command": "git describe",
        "title": "git describe",
        "summary": "Name a commit relative to the nearest reachable tag.",
        "usages": [form("tags", "git describe --tags", "Describe HEAD from release tags", "frost-deliver-the-release")],
    },
    {
        "module": "skyline-revision-language",
        "slug": "git-rev-parse",
        "base_command": "git rev-parse",
        "title": "git rev-parse",
        "summary": "Resolve revision expressions and repository paths into canonical values.",
        "usages": [
            form("revision", "git rev-parse <revision>", "Resolve a revision", "skyline-revision-language"),
            form("toplevel", "git rev-parse --show-toplevel", "Locate the repository root", "skyline-revision-language"),
        ],
    },
    {
        "module": "skyline-hidden-history",
        "slug": "git-blame",
        "base_command": "git blame",
        "title": "git blame",
        "summary": "Trace each line to the commit that last changed it.",
        "usages": [form("path", "git blame <path>", "Trace line ownership", "skyline-hidden-history")],
    },
    {
        "module": "skyline-hidden-history",
        "slug": "git-grep",
        "base_command": "git grep",
        "title": "git grep",
        "summary": "Search tracked repository content in the working tree or a revision.",
        "usages": [form("pattern", "git grep <pattern> <tree>", "Search repository content", "skyline-hidden-history")],
    },
    {
        "module": "skyline-first-broken-commit",
        "slug": "git-bisect",
        "base_command": "git bisect",
        "title": "git bisect",
        "summary": "Binary-search commit history to locate the first bad change.",
        "usages": [
            form("start", "git bisect start", "Start a bisect session", "skyline-first-broken-commit", reference_only=True),
            form("bad", "git bisect bad <commit>", "Mark a bad boundary", "skyline-first-broken-commit", reference_only=True),
            form("good", "git bisect good <commit>", "Mark a good boundary", "skyline-first-broken-commit", reference_only=True),
            form("skip", "git bisect skip <commit>", "Skip an untestable commit", "skyline-first-broken-commit", reference_only=True),
            form("run", "git bisect run <authored-test>", "Run an authored test automatically", "skyline-first-broken-commit"),
            form("log", "git bisect log", "Inspect the bisect record", "skyline-first-broken-commit"),
            form("replay", "git bisect replay <logfile>", "Replay a bisect record", "skyline-first-broken-commit", reference_only=True),
            form("reset", "git bisect reset", "End the bisect session", "skyline-first-broken-commit", reference_only=True),
        ],
    },
    {
        "module": "skyline-repeated-conflict",
        "slug": "git-rerere",
        "base_command": "git rerere",
        "title": "git rerere",
        "summary": "Record and reuse conflict resolutions across repeated integrations.",
        "usages": [
            form("run", "git rerere", "Record or replay a resolution", "skyline-repeated-conflict", reference_only=True),
            form("status", "git rerere status", "List recorded conflict paths", "skyline-repeated-conflict"),
            form("diff", "git rerere diff", "Inspect recorded resolutions", "skyline-repeated-conflict"),
        ],
    },
    {
        "module": "skyline-repeated-conflict",
        "slug": "git-merge-tree",
        "base_command": "git merge-tree",
        "title": "git merge-tree",
        "summary": "Inspect a virtual merge without changing the working tree.",
        "usages": [form("branches", "git merge-tree <branch-a> <branch-b>", "Preview a merge", "skyline-repeated-conflict")],
    },
    {
        "module": "skyline-many-realities",
        "slug": "git-worktree",
        "base_command": "git worktree",
        "title": "git worktree",
        "summary": "Manage multiple working trees attached to one repository.",
        "usages": [
            form("list", "git worktree list", "List worktrees", "skyline-many-realities"),
            form("add", "git worktree add <path> <branch>", "Add a worktree", "skyline-many-realities", reference_only=True),
            form("move", "git worktree move <old> <new>", "Move a worktree", "skyline-many-realities", reference_only=True),
            form("remove", "git worktree remove <path>", "Remove a worktree", "skyline-many-realities", reference_only=True),
            form("prune", "git worktree prune", "Prune stale worktree metadata", "skyline-many-realities", reference_only=True),
        ],
    },
    {
        "module": "skyline-many-realities",
        "slug": "git-sparse-checkout",
        "base_command": "git sparse-checkout",
        "title": "git sparse-checkout",
        "summary": "Limit the working directory to selected paths in a large repository.",
        "usages": [
            form("init", "git sparse-checkout init --cone", "Enable cone-mode sparse checkout", "skyline-many-realities", reference_only=True),
            form("set", "git sparse-checkout set <paths...>", "Set sparse paths", "skyline-many-realities", reference_only=True),
            form("add", "git sparse-checkout add <paths...>", "Add sparse paths", "skyline-many-realities", reference_only=True),
            form("list", "git sparse-checkout list", "List sparse paths", "skyline-many-realities"),
            form("disable", "git sparse-checkout disable", "Disable sparse checkout", "skyline-many-realities", reference_only=True),
        ],
    },
    {
        "module": "skyline-many-realities",
        "slug": "git-submodule",
        "base_command": "git submodule",
        "title": "git submodule",
        "summary": "Track another repository at a specific commit inside the current project.",
        "usages": [
            form("add", "git submodule add <url> <path>", "Add a submodule", "skyline-many-realities", reference_only=True),
            form("status", "git submodule status", "Inspect submodule state", "skyline-many-realities"),
            form("update", "git submodule update --init --recursive", "Initialize and update submodules", "skyline-many-realities", reference_only=True),
            form("sync", "git submodule sync --recursive", "Synchronize submodule URLs", "skyline-many-realities", reference_only=True),
            form("deinit", "git submodule deinit <path>", "Deinitialize a submodule", "skyline-many-realities", reference_only=True),
        ],
    },
    {
        "module": "skyline-guard-the-archive",
        "slug": "git-verify-commit",
        "base_command": "git verify-commit",
        "title": "git verify-commit",
        "summary": "Verify a commit's cryptographic signature.",
        "usages": [form("commit", "git verify-commit <commit>", "Verify a signed commit", "skyline-guard-the-archive")],
    },
    {
        "module": "skyline-guard-the-archive",
        "slug": "git-verify-tag",
        "base_command": "git verify-tag",
        "title": "git verify-tag",
        "summary": "Verify an annotated tag's cryptographic signature.",
        "usages": [form("tag", "git verify-tag <tag>", "Verify a signed tag", "skyline-guard-the-archive")],
    },
    {
        "module": "skyline-restore-maintain",
        "slug": "git-fsck",
        "base_command": "git fsck",
        "title": "git fsck",
        "summary": "Validate object connectivity and report unreachable objects.",
        "usages": [form("full", "git fsck --full", "Run a full integrity check", "skyline-restore-maintain")],
    },
    {
        "module": "skyline-restore-maintain",
        "slug": "git-count-objects",
        "base_command": "git count-objects",
        "title": "git count-objects",
        "summary": "Inspect loose and packed object storage usage.",
        "usages": [form("verbose-human", "git count-objects -vH", "Inspect object storage", "skyline-restore-maintain")],
    },
    {
        "module": "skyline-git-machinery",
        "slug": "git-cat-file",
        "base_command": "git cat-file",
        "title": "git cat-file",
        "summary": "Inspect an object's type or decoded content.",
        "usages": [
            form("pretty", "git cat-file -p <object>", "Pretty-print an object", "skyline-git-machinery"),
            form("type", "git cat-file -t <object>", "Inspect an object type", "skyline-git-machinery"),
        ],
    },
    {
        "module": "skyline-git-machinery",
        "slug": "git-ls-tree",
        "base_command": "git ls-tree",
        "title": "git ls-tree",
        "summary": "Inspect the entries stored in a tree object.",
        "usages": [form("tree", "git ls-tree <tree>", "List tree entries", "skyline-git-machinery")],
    },
    {
        "module": "skyline-git-machinery",
        "slug": "git-symbolic-ref",
        "base_command": "git symbolic-ref",
        "title": "git symbolic-ref",
        "summary": "Read or update a symbolic reference such as HEAD.",
        "usages": [form("head", "git symbolic-ref HEAD", "Inspect HEAD's symbolic ref", "skyline-git-machinery")],
    },
    {
        "module": "skyline-git-machinery",
        "slug": "git-show-ref",
        "base_command": "git show-ref",
        "title": "git show-ref",
        "summary": "List refs and their object identifiers.",
        "usages": [form("all", "git show-ref", "List references", "skyline-git-machinery")],
    },
    {
        "module": "skyline-git-machinery",
        "slug": "git-for-each-ref",
        "base_command": "git for-each-ref",
        "title": "git for-each-ref",
        "summary": "Query refs with controlled sorting and formatting.",
        "usages": [form("all", "git for-each-ref", "Query references", "skyline-git-machinery")],
    },
]

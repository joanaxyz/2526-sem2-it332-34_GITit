from __future__ import annotations

import re
from typing import Any


def normalize_command_text(command: str) -> str:
    return " ".join(str(command).strip().split()).lower()


COMMAND_KEY_PREFIXES: tuple[tuple[str, str], ...] = (
    ("git diff --staged", "git-diff-staged"),
    ("git diff --cached", "git-diff-staged"),
    ("git add -p", "git-add-p"),
    ("git commit --amend", "git-commit-amend"),
    ("git restore --staged", "git-restore-staged"),
    ("git rm --cached", "git-rm-cached"),
    ("git remote -v", "git-remote-v"),
    ("git remote", "git-remote-v"),
    ("git log", "git-log"),
    ("git status", "git-status"),
    ("git diff", "git-diff"),
    ("git show", "git-show"),
    ("git branch", "git-branch"),
    ("git reflog", "git-reflog"),
    ("git check-ignore", "git-check-ignore"),
    ("git ls-files", "git-ls-files"),
    ("git init", "git-init"),
    ("git clone", "git-clone"),
    ("git add", "git-add"),
    ("git commit", "git-commit"),
    ("git restore", "git-restore"),
    (".gitignore", "gitignore"),
)


def command_content_key_for_command(command: str) -> str:
    normalized = normalize_command_text(command)
    for prefix, key in COMMAND_KEY_PREFIXES:
        if normalized == prefix or normalized.startswith(f"{prefix} "):
            return key
    return normalized.replace(" ", "-").replace("/", "-").replace(".", "dot")


def base_command_for_command(command: str) -> str:
    normalized = normalize_command_text(command)
    if not normalized:
        return ""
    if normalized == ".gitignore":
        return ".gitignore"
    parts = normalized.split()
    if parts and parts[0] == "git":
        return "git" if len(parts) == 1 else f"git {parts[1]}"
    return str(command).strip()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize_command_text(value))
    return slug.strip("-") or "section"


def _paragraph(body: str) -> dict[str, Any]:
    return {"type": "paragraph", "body": body}


def _commands(items: list[str]) -> dict[str, Any]:
    return {"type": "command", "title": "Command forms", "items": items}


def _bullets(title: str, items: list[str]) -> dict[str, Any]:
    return {"type": "bullet_list", "title": title, "items": items}


def _warning(body: str) -> dict[str, Any]:
    return {"type": "warning", "title": "Watch for", "body": body}


def _callout(title: str, body: str) -> dict[str, Any]:
    return {"type": "callout", "title": title, "body": body}


def _terminal(body: str) -> dict[str, Any]:
    return {"type": "terminal_output", "title": "Typical output", "body": body}


def _rich_form_section(
    *,
    section_id: str,
    title: str,
    command: str,
    does: str,
    sample_output: str,
    how_to_read: list[str],
    effects: list[str],
    boundaries: list[str],
    mistake: str,
) -> dict[str, Any]:
    return _section(
        section_id=section_id,
        section_type="form",
        title=title,
        command=command,
        content=[
            _paragraph(does),
            _terminal(sample_output),
            _bullets("How to read it", how_to_read),
            _bullets("What changes", effects),
            _bullets("What does not change", boundaries),
            _warning(mistake),
        ],
    )


def _section(
    *,
    section_id: str,
    section_type: str,
    title: str,
    content: list[dict[str, Any]],
    command: str = "",
    token: str = "",
) -> dict[str, Any]:
    section = {
        "id": section_id,
        "type": section_type,
        "title": title,
        "content": content,
    }
    if command:
        section["command"] = command
    if token:
        section["token"] = token
    return section


def _semantic_item_sections(
    *,
    section_type: str,
    prefix: str,
    items: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    sections = []
    for item in items or []:
        token = item.get("token") or item.get("command") or item.get("title") or ""
        title = item.get("title") or token or section_type.replace("_", " ").title()
        content = item.get("content")
        if not isinstance(content, list):
            body = item.get("body") or item.get("description") or ""
            content = [_paragraph(body)] if body else []
        sections.append(
            _section(
                section_id=item.get("id") or f"{prefix}-{_slug(token or title)}",
                section_type=section_type,
                title=title,
                command=item.get("command") or "",
                token=item.get("token") or "",
                content=content,
            )
        )
    return sections


def _sections(
    *,
    canonical_command: str,
    summary: str,
    syntax: list[str],
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
    terminal_output: str = "",
    options: list[dict[str, Any]] | None = None,
    arguments: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    overview_blocks = [_paragraph(summary)]
    if terminal_output:
        overview_blocks.append(_terminal(terminal_output))

    sections = [
        _section(
            section_id="overview",
            section_type="overview",
            title="Overview",
            command=canonical_command,
            content=overview_blocks,
        )
    ]
    if syntax:
        sections.append(
            _section(
                section_id="forms",
                section_type="form",
                title="Supported forms",
                command=syntax[0],
                content=[
                    _commands(syntax),
                    _callout(
                        "Simulator scope",
                        "These are the command forms this simulator accepts for this lesson content.",
                    ),
                ],
            )
        )
    sections.extend(
        _semantic_item_sections(section_type="option", prefix="option", items=options)
    )
    sections.extend(
        _semantic_item_sections(section_type="argument", prefix="argument", items=arguments)
    )
    sections.extend(
        [
            _section(
                section_id="effects",
                section_type="effect",
                title="Effects and boundaries",
                content=[
                    _bullets("Repository effect", effects),
                    _bullets("Boundaries", boundaries),
                ],
            ),
            _section(
                section_id="mistakes",
                section_type="mistake",
                title="Common beginner mistake",
                content=[_warning(watch_for)],
            ),
            _section(
                section_id="practice-notes",
                section_type="practice_note",
                title="Practice notes",
                content=[_bullets("Before running it", readiness)],
            ),
        ]
    )
    return sections


def pages_from_command_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages = []
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            continue
        page = {
            "id": section.get("id") or f"section-{index}",
            "title": section.get("title") or f"Section {index}",
            "heading": section.get("title") or f"Section {index}",
            "blocks": section.get("content") or [],
            "section_type": section.get("type") or "overview",
        }
        if section.get("command"):
            page["eyebrow"] = section["command"]
        elif section.get("token"):
            page["eyebrow"] = section["token"]
        pages.append(page)
    return pages


def _content(
    *,
    key: str,
    display_name: str,
    canonical_command: str,
    aliases: list[str],
    summary: str,
    tags: list[str],
    syntax: list[str],
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
    terminal_output: str = "",
    base_command: str = "",
    options: list[dict[str, Any]] | None = None,
    arguments: list[dict[str, Any]] | None = None,
    authored_sections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    sections = authored_sections or _sections(
        canonical_command=canonical_command,
        summary=summary,
        syntax=syntax,
        effects=effects,
        boundaries=boundaries,
        watch_for=watch_for,
        readiness=readiness,
        terminal_output=terminal_output,
        options=options,
        arguments=arguments,
    )
    return {
        "key": key,
        "base_command": base_command or base_command_for_command(canonical_command),
        "display_name": display_name,
        "canonical_command": canonical_command,
        "aliases": aliases,
        "summary": summary,
        "tags": tags,
        "sections": sections,
        "pages": pages_from_command_sections(sections),
    }


def _git_log_sections() -> list[dict[str, Any]]:
    return [
        _section(
            section_id="overview",
            section_type="overview",
            title="Overview",
            command="git log",
            content=[
                _paragraph(
                    "git log reads commit history. The simulator supports the base history view, "
                    "a compact one-line view, a graph view across all refs, and simple count limits."
                ),
                _callout(
                    "Read-only command",
                    "Every git log form here is diagnostic: it reports commits and refs without moving HEAD, editing files, staging, or committing.",
                ),
            ],
        ),
        _rich_form_section(
            section_id="reading-history",
            title="Reading History",
            command="git log",
            does=(
                "git log shows commit history from the current HEAD. Use it when you need commit "
                "messages, authorship-style context, parent order, or the newest commit before choosing an action."
            ),
            sample_output="commit c2\nAuthor: Demo User\n\n    Add profile validation\n\ncommit c1\nAuthor: Demo User\n\n    Add baseline feature",
            how_to_read=[
                "The top commit is the newest commit reachable from the current HEAD.",
                "The commit id, such as c2, is the name you can pass to supported inspection commands like git show.",
                "The indented message is the human explanation of that snapshot.",
            ],
            effects=["No repository state changes. It only reads commit history."],
            boundaries=[
                "It does not show unstaged file edits.",
                "It does not stage, commit, switch branches, or rewrite history.",
            ],
            mistake="Reading the newest message as proof that the working tree is clean. Pair history checks with git status when files may have changed.",
        ),
        _rich_form_section(
            section_id="compact-history",
            title="Compact History",
            command="git log --oneline",
            does=(
                "git log --oneline compresses each commit into one row. It is the fastest way to "
                "scan commit order and messages when the full commit body is more detail than you need."
            ),
            sample_output="c2 Add profile validation\nc1 Add baseline feature",
            how_to_read=[
                "Each line starts with a short commit id followed by the commit message.",
                "Rows are still newest first.",
                "Use this view to answer questions like what changed most recently or whether the expected message exists.",
            ],
            effects=["No repository state changes. It only changes how history is displayed."],
            boundaries=[
                "It does not hide commits; it hides extra detail from each commit row.",
                "It does not tell you whether files are staged or unstaged.",
            ],
            mistake="Copying a short id from the wrong line because the output is compact. Read the message beside the id before using it.",
        ),
        _rich_form_section(
            section_id="visual-branch-history",
            title="Visual Branch History",
            command="git log --oneline --graph --all",
            does=(
                "git log --oneline --graph --all shows compact history with branch shape. In the simulator, "
                "this is the teaching form for seeing more than the current branch path."
            ),
            sample_output="* c3 (feature) Draft profile copy\n| * c2 (main) Add profile validation\n|/\n* c1 Add baseline feature",
            how_to_read=[
                "Asterisks mark commits, while lines show how branch paths relate.",
                "Labels in parentheses show branch tips or known refs when the simulator can display them.",
                "--all matters when the task asks about branch tips beyond the current branch.",
            ],
            effects=["No repository state changes. It only draws history with branch context."],
            boundaries=[
                "It does not merge branches or move branch tips.",
                "It does not fetch remote history; it only shows refs already present in simulator state.",
            ],
            mistake="Assuming graph lines changed the repository. They are visual output only; choose an action command separately if the task asks for a change.",
        ),
        _section(
            section_id="forms",
            section_type="form",
            title="Supported Forms",
            command="git log",
            content=[
                _commands(
                    [
                        "git log",
                        "git log --oneline",
                        "git log --oneline --graph --all",
                        "git log -n <number>",
                        "git log --max-count=<number>",
                    ]
                ),
                _callout(
                    "Simulator scope",
                    "These are the history forms accepted for Module 1 inspection scenarios.",
                ),
            ],
        ),
        _section(
            section_id="option-oneline",
            section_type="option",
            title="Option: --oneline",
            token="--oneline",
            content=[
                _paragraph(
                    "--oneline keeps the history order but prints each commit as a short id plus message. "
                    "Use it for quick scanning before choosing a commit to inspect."
                ),
                _bullets(
                    "Good for",
                    [
                        "Finding the newest commit message.",
                        "Comparing a short sequence of recent commits.",
                        "Copying a commit id for a follow-up git show command.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="option-graph",
            section_type="option",
            title="Option: --graph",
            token="--graph",
            content=[
                _paragraph(
                    "--graph adds visual branch lines to log output. It is most useful with --oneline "
                    "because the compact rows leave room for the branch drawing."
                ),
                _warning(
                    "Do not treat graph marks as commands. The marks only explain relationships between commits."
                ),
            ],
        ),
        _section(
            section_id="option-all",
            section_type="option",
            title="Option: --all",
            token="--all",
            content=[
                _paragraph(
                    "--all asks the simulator to include all known refs in the log traversal, not only the "
                    "current branch path. Use it when a scenario asks about another branch tip."
                ),
                _bullets(
                    "Boundaries",
                    [
                        "It does not contact a remote.",
                        "It does not create, delete, or switch branches.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="option-count",
            section_type="option",
            title="Option: -n / --max-count",
            token="-n / --max-count",
            content=[
                _paragraph(
                    "-n and --max-count limit how many commits the simulator prints. Use them when a task asks for only the most recent entries."
                ),
                _bullets(
                    "Accepted forms",
                    ["git log -n <number>", "git log --max-count=<number>"],
                ),
            ],
        ),
        _section(
            section_id="effects",
            section_type="effect",
            title="Effects and boundaries",
            content=[
                _bullets(
                    "Repository effect",
                    ["Reports commit history, commit ids, messages, and branch shape only."],
                ),
                _bullets(
                    "What does not change",
                    [
                        "HEAD stays where it is.",
                        "Branches, commits, staged files, and working-tree files are unchanged.",
                        "No remote data is fetched.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="mistakes",
            section_type="mistake",
            title="Common Mistakes",
            content=[
                _warning(
                    "Using git log as a cleanliness check. History output tells you what has been committed, not what is currently staged or edited."
                ),
                _bullets(
                    "Watch for",
                    [
                        "Reading only the first oneline row when the task asks about branch shape.",
                        "Forgetting --all when the relevant commit is on another known ref.",
                        "Assuming --graph performs a branch operation instead of drawing output.",
                    ],
                ),
            ],
        ),
    ]


GIT_COMMAND_CONTENT_LIBRARY: list[dict[str, Any]] = [
    _content(
        key="git-status",
        display_name="git status",
        canonical_command="git status",
        aliases=[
            "git status -s",
            "git status --short",
            "git status --porcelain",
            "git status -sb",
            "git status --ignored",
        ],
        summary=(
            "git status reports the current branch, staged changes, unstaged changes, "
            "and untracked files without changing repository state."
        ),
        tags=["diagnostic", "working-tree", "index"],
        syntax=[
            "git status",
            "git status -s",
            "git status --short",
            "git status --porcelain",
            "git status -sb",
            "git status --ignored",
        ],
        effects=["Reports repository state only."],
        boundaries=["It does not stage, commit, discard, or rewrite files."],
        watch_for="Treating status output as a fix instead of evidence.",
        readiness=["Name the branch, staged paths, unstaged paths, and untracked paths."],
        terminal_output="On branch main\nChanges to be committed:\n  modified: demo.txt",
        options=[
            {
                "token": "-s / --short",
                "title": "Short status",
                "body": "Shows the same repository state in compact two-column status lines.",
            },
            {
                "token": "--porcelain",
                "title": "Porcelain status",
                "body": "Uses the simulator's short status output for stable machine-readable status practice.",
            },
            {
                "token": "-sb",
                "title": "Short status with branch",
                "body": "Adds the current branch header to compact status output.",
            },
            {
                "token": "--ignored",
                "title": "Show ignored files",
                "body": "Includes ignored working-tree paths so .gitignore scenarios can verify generated files are excluded.",
            },
        ],
    ),
    _content(
        key="git-log",
        display_name="git log",
        canonical_command="git log",
        aliases=[
            "git log --oneline",
            "git log --oneline --graph --all",
            "git log -n <number>",
            "git log --max-count=<number>",
        ],
        summary=(
            "git log reads commit history. Formatting flags change how the history is "
            "shown, not the commits themselves."
        ),
        tags=["diagnostic", "history"],
        syntax=[
            "git log",
            "git log --oneline",
            "git log --oneline --graph --all",
            "git log -n <number>",
            "git log --max-count=<number>",
        ],
        effects=["Reports commit history and branch shape only."],
        boundaries=["It does not move HEAD, create commits, or edit files."],
        watch_for="Reading only the newest line when the task asks for branch or graph context.",
        readiness=["Identify the latest commit, message, and relevant branch tips."],
        authored_sections=_git_log_sections(),
    ),
    _content(
        key="git-diff",
        display_name="git diff",
        canonical_command="git diff",
        aliases=[
            "git diff <path>",
            "git diff --staged",
            "git diff --cached",
            "git diff HEAD",
            "git diff --name-only",
        ],
        summary="git diff shows unstaged working-tree changes compared with the index.",
        tags=["diagnostic", "working-tree", "diff"],
        syntax=[
            "git diff",
            "git diff <path>",
            "git diff --staged",
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff HEAD",
            "git diff --name-only",
            "git diff --staged --name-only",
        ],
        effects=["Reports unstaged content changes only."],
        boundaries=["It does not show staged changes unless you use a staged diff command."],
        watch_for="Assuming plain git diff includes changes already staged for commit.",
        readiness=["Use it before staging when you need to inspect working-tree edits."],
        options=[
            {
                "token": "--staged / --cached",
                "title": "Staged diff",
                "body": "Shows what is already in the index for the next commit instead of unstaged working-tree edits.",
            },
            {
                "token": "HEAD",
                "title": "All changes since HEAD",
                "body": "Shows the combined staged and unstaged tracked changes since the latest commit.",
            },
            {
                "token": "--name-only",
                "title": "Path names only",
                "body": "Prints only changed paths for quick beginner-friendly inspection.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path filter",
                "body": "Limits the diff output to a path the simulator knows about.",
            },
        ],
    ),
    _content(
        key="git-diff-staged",
        display_name="git diff --staged",
        canonical_command="git diff --staged",
        base_command="git diff",
        aliases=[
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff --staged --name-only",
        ],
        summary="git diff --staged shows what is already in the index for the next commit.",
        tags=["diagnostic", "index", "diff"],
        syntax=[
            "git diff --staged",
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff --staged --name-only",
        ],
        effects=["Reports staged content changes only."],
        boundaries=["It does not include unstaged working-tree edits."],
        watch_for="Checking only plain diff and missing what is already staged.",
        readiness=["Compare staged diff with status before committing."],
        options=[
            {
                "token": "--staged / --cached",
                "title": "Read the index",
                "body": "Switches diff from unstaged working-tree changes to the staged snapshot.",
            },
        ],
    ),
    _content(
        key="git-show",
        display_name="git show",
        canonical_command="git show",
        aliases=["git show <commit>", "git show --name-only"],
        summary="git show displays details for the current or named Git object, usually a commit.",
        tags=["diagnostic", "history", "object"],
        syntax=["git show", "git show <commit>", "git show --name-only"],
        effects=["Reports commit metadata and patch details only."],
        boundaries=["It does not change branches, files, or the index."],
        watch_for="Inspecting the wrong commit when the task names a specific revision.",
        readiness=["Confirm whether you need HEAD or a named commit."],
        arguments=[
            {
                "token": "<commit>",
                "title": "Object to inspect",
                "body": "The simulator accepts at most one object name; omitting it means HEAD.",
            },
        ],
    ),
    _content(
        key="git-branch",
        display_name="git branch",
        canonical_command="git branch",
        aliases=["git branch -v"],
        summary="git branch lists local branches; -v also shows the commit each branch points to.",
        tags=["diagnostic", "branches"],
        syntax=["git branch", "git branch -v"],
        effects=["Reports local branch names and tips when used as a listing command."],
        boundaries=["Listing branches does not create, delete, or switch branches."],
        watch_for="Confusing a branch listing with changing the current branch.",
        readiness=["Identify the current branch marker and any named branch tips."],
        options=[
            {
                "token": "-v",
                "title": "Verbose branch list",
                "body": "Adds commit-tip detail to the branch listing.",
            },
        ],
    ),
    _content(
        key="git-remote-v",
        display_name="git remote -v",
        canonical_command="git remote -v",
        base_command="git remote",
        aliases=["git remote"],
        summary="git remote -v lists configured remote names and their fetch/push URLs.",
        tags=["diagnostic", "remotes"],
        syntax=["git remote", "git remote -v"],
        effects=["Reports configured remote relationships only."],
        boundaries=["Remote listing does not contact the remote or change remote-tracking branches."],
        watch_for="Assuming a remote listing proves local history is up to date.",
        readiness=["Confirm the remote name and URL before clone or remote-related work."],
        options=[
            {
                "token": "-v / --verbose",
                "title": "Verbose remote list",
                "body": "Shows fetch and push URLs for each configured remote.",
            },
        ],
    ),
    _content(
        key="git-reflog",
        display_name="git reflog",
        canonical_command="git reflog",
        aliases=[],
        summary="git reflog shows recent HEAD movements so you can orient or recover local work.",
        tags=["diagnostic", "history", "recovery"],
        syntax=["git reflog"],
        effects=["Reports local reference movements only."],
        boundaries=["It does not restore anything by itself."],
        watch_for="Using reflog entries as commands before confirming the current state.",
        readiness=["Use it with status and log when you need to verify where HEAD has been."],
    ),
    _content(
        key="git-check-ignore",
        display_name="git check-ignore -v",
        canonical_command="git check-ignore -v <path>",
        base_command="git check-ignore",
        aliases=[],
        summary="git check-ignore -v explains which .gitignore rule matched an ignored path.",
        tags=["diagnostic", "ignore"],
        syntax=["git check-ignore -v <path>"],
        effects=["Reports ignore-rule evidence only."],
        boundaries=["It does not edit .gitignore, stage files, or untrack anything."],
        watch_for="Using it on a path that is not ignored and assuming silence means success.",
        readiness=["Use it after adding ignore rules when a scenario asks you to verify a generated path."],
        options=[
            {
                "token": "-v",
                "title": "Verbose rule source",
                "body": "Shows the simulated .gitignore source and matching rule token for the path.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Ignored path",
                "body": "Names one generated or local path to check.",
            },
        ],
    ),
    _content(
        key="git-ls-files",
        display_name="git ls-files",
        canonical_command="git ls-files",
        aliases=[],
        summary="git ls-files lists paths currently tracked by the index.",
        tags=["diagnostic", "index"],
        syntax=["git ls-files"],
        effects=["Reports tracked paths only."],
        boundaries=["It does not include ignored untracked files and does not stage new files."],
        watch_for="Confusing tracked files with every visible file in the working tree.",
        readiness=["Use it when you need to confirm whether a generated path is still tracked."],
    ),
    _content(
        key="git-init",
        display_name="git init",
        canonical_command="git init",
        aliases=[
            "git init <directory>",
            "git init -b <branch>",
            "git init --initial-branch <branch>",
            "git init --initial-branch=<branch>",
            "git init -q",
            "git init --quiet",
        ],
        summary=(
            "git init creates Git metadata for a folder so future snapshots can be "
            "tracked there."
        ),
        tags=["action", "repository-setup"],
        syntax=[
            "git init",
            "git init <directory>",
            "git init -b <branch>",
            "git init --initial-branch <branch>",
            "git init --initial-branch=<branch>",
            "git init -q",
            "git init --quiet",
            "git init -q -b <branch> <directory>",
            "git init --quiet --initial-branch=<branch> <directory>",
        ],
        effects=["Creates simulator Git metadata at the current or named directory; safe reinitialization preserves existing repository state."],
        boundaries=["It does not stage files, create commits, or rewrite file contents."],
        watch_for="Initializing the parent folder when the scenario names a child directory.",
        readiness=["Check whether the task names the current folder or a destination folder."],
        options=[
            {
                "token": "-b / --initial-branch",
                "title": "Initial branch name",
                "body": "Sets the first branch name in simulator state instead of using main.",
            },
            {
                "token": "-q / --quiet",
                "title": "Quiet init",
                "body": "Suppresses extra initialization chatter while still creating the simulator repository state.",
            },
        ],
        arguments=[
            {
                "token": "<directory>",
                "title": "Destination directory",
                "body": "Records that the repository was initialized in a named directory.",
            },
        ],
    ),
    _content(
        key="git-clone",
        display_name="git clone",
        canonical_command="git clone <url>",
        aliases=["git clone <url> <folder>"],
        summary=(
            "git clone creates a local working copy from a remote repository and sets "
            "up the origin relationship."
        ),
        tags=["action", "remote", "repository-setup"],
        syntax=["git clone <url>", "git clone <url> <folder>"],
        effects=["Creates a local repository, checks out the default branch, and configures origin."],
        boundaries=["It does not modify the remote repository."],
        watch_for="Forgetting the destination folder when the scenario names one.",
        readiness=["Confirm the remote URL and destination folder before cloning."],
        arguments=[
            {
                "token": "<url>",
                "title": "Remote URL",
                "body": "Required. The simulator uses this as the origin URL for the local copy.",
            },
            {
                "token": "<folder>",
                "title": "Destination folder",
                "body": "Optional. Records the local folder name for the cloned repository.",
            },
        ],
    ),
    _content(
        key="git-add",
        display_name="git add",
        canonical_command="git add <path>",
        aliases=["git add .", "git add -A", "git add --all", "git add -u", "git add --update"],
        summary="git add copies selected working-tree changes into the staging area.",
        tags=["action", "index", "staging"],
        syntax=[
            "git add <path>",
            "git add <path> <path>",
            "git add <directory>/",
            "git add .",
            "git add -A",
            "git add --all",
            "git add -u",
            "git add --update",
            "git add -p <path>",
            "git add --patch <path>",
        ],
        effects=["Moves selected path changes from the working tree into the index."],
        boundaries=["It does not create a commit or remove the edits from your files."],
        watch_for="Staging every file when only one path belongs in the next commit.",
        readiness=["Use status and diff to confirm the path before staging."],
        options=[
            {
                "token": "-A / --all",
                "title": "Stage all changes",
                "body": "Stages tracked and untracked changes selected by the simulator path rules.",
            },
            {
                "token": "-u / --update",
                "title": "Stage tracked changes only",
                "body": "Stages modifications and deletions to tracked files without adding new untracked files.",
            },
            {
                "token": "-p / --patch",
                "title": "Patch staging",
                "body": "Stages authored partial hunks instead of the whole selected file.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Pathspec",
                "body": "Selects one or more paths for staging; use it instead of staging unrelated files.",
            },
        ],
    ),
    _content(
        key="git-add-p",
        display_name="git add -p",
        canonical_command="git add -p",
        base_command="git add",
        aliases=["git add -p <path>", "git add --patch <path>"],
        summary="git add -p lets you stage selected hunks instead of an entire file.",
        tags=["action", "index", "partial-staging"],
        syntax=["git add -p", "git add -p <path>", "git add --patch <path>"],
        effects=["Moves selected hunks from the working tree into the index."],
        boundaries=["It leaves unselected hunks in the working tree."],
        watch_for="Accepting unrelated hunks because they happen to be in the same file.",
        readiness=["Read each hunk and match it to the scenario's requested change."],
        options=[
            {
                "token": "-p / --patch",
                "title": "Patch staging",
                "body": "Uses the simulator's authored hunk data to stage only selected changes.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Optional path",
                "body": "Limits patch staging to a path; when omitted, the simulator uses available authored hunks.",
            },
        ],
    ),
    _content(
        key="git-rm-cached",
        display_name="git rm --cached",
        canonical_command="git rm --cached <path>",
        base_command="git rm",
        aliases=[],
        summary="git rm --cached removes a path from the index while leaving the local file present.",
        tags=["action", "index", "ignore"],
        syntax=["git rm --cached <path>", "git rm -r --cached <directory>"],
        effects=["Stages removal of the tracked path from future commits."],
        boundaries=["It does not delete the local working-tree file."],
        watch_for="Using a removal command that deletes a local file you meant to keep.",
        readiness=["Use it with ignore rules when a generated file is already tracked."],
        options=[
            {
                "token": "--cached",
                "title": "Keep the local file",
                "body": "Removes the path from the index while preserving it in the working tree as ignored content.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to remove",
                "body": "Names the tracked, staged, or working-tree path affected by git rm.",
            },
        ],
    ),
    _content(
        key="git-commit",
        display_name="git commit",
        canonical_command='git commit -m "message"',
        aliases=[
            'git commit --message "message"',
            'git commit -am "message"',
            'git commit -a -m "message"',
        ],
        summary="git commit saves the staged snapshot and advances the current branch tip.",
        tags=["action", "history", "snapshot"],
        syntax=[
            'git commit -m "message"',
            'git commit --message "message"',
            'git commit -am "message"',
            'git commit -a -m "message"',
            "git commit --amend",
            'git commit --amend -m "message"',
            "git commit --amend --no-edit",
        ],
        effects=["Creates a new commit from the index and moves the current branch to it."],
        boundaries=["It does not include unstaged changes or ignored files."],
        watch_for="Committing before checking exactly what is staged.",
        readiness=["Confirm staged paths and the required message before committing."],
        options=[
            {
                "token": "-m / --message",
                "title": "Commit message",
                "body": "Supplies the commit message accepted by the simulator.",
            },
            {
                "token": "-a / --all",
                "title": "Stage tracked changes before committing",
                "body": "Stages modifications to tracked files, then creates the commit.",
            },
            {
                "token": "--amend",
                "title": "Amend latest commit",
                "body": "Replaces the latest local commit instead of creating a new follow-up commit.",
            },
        ],
    ),
    _content(
        key="git-commit-amend",
        display_name="git commit --amend",
        canonical_command="git commit --amend",
        base_command="git commit",
        aliases=['git commit --amend -m "message"', "git commit --amend --no-edit"],
        summary=(
            "git commit --amend replaces the latest local commit with a corrected "
            "commit instead of adding a follow-up commit."
        ),
        tags=["action", "history", "rewrite"],
        syntax=["git commit --amend", 'git commit --amend -m "message"', "git commit --amend --no-edit"],
        effects=["Replaces the latest local commit with a new commit object."],
        boundaries=["It should not be used to rewrite shared history in these local-only scenarios."],
        watch_for="Creating a second commit instead of repairing the latest one.",
        readiness=["Confirm the commit is local and the staged content/message are correct."],
        options=[
            {
                "token": "--amend",
                "title": "Replace latest commit",
                "body": "Creates a replacement commit and records the replaced commit in simulator metadata.",
            },
            {
                "token": "--no-edit",
                "title": "Keep the old message",
                "body": "Accepted only with --amend; keeps the existing commit message when staged content changes.",
            },
            {
                "token": "-m / --message",
                "title": "New amend message",
                "body": "Supplies the message for the replacement commit.",
            },
        ],
    ),
    _content(
        key="git-restore",
        display_name="git restore",
        canonical_command="git restore <path>",
        aliases=["git restore <path> <path>", "git restore ."],
        summary="git restore discards selected working-tree changes by restoring paths from the index or HEAD.",
        tags=["action", "working-tree", "discard"],
        syntax=["git restore <path>", "git restore <path> <path>", "git restore ."],
        effects=["Replaces selected working-tree paths with the chosen source version."],
        boundaries=["It does not affect unrelated paths."],
        watch_for="Restoring the wrong path and losing edits you meant to keep.",
        readiness=["Separate paths to discard from paths to keep before running it."],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to restore",
                "body": "Required. Names the working-tree path whose local changes should be discarded.",
            },
        ],
    ),
    _content(
        key="git-restore-staged",
        display_name="git restore --staged",
        canonical_command="git restore --staged <path>",
        base_command="git restore",
        aliases=["git restore --staged <path> <path>", "git restore --staged ."],
        summary="git restore --staged moves selected changes out of the staging area.",
        tags=["action", "index", "unstage"],
        syntax=[
            "git restore --staged <path>",
            "git restore --staged <path> <path>",
            "git restore --staged .",
        ],
        effects=["Updates the index so selected changes are no longer staged."],
        boundaries=["It does not discard the working-tree file content."],
        watch_for="Leaving off --staged and discarding work instead of unstaging it.",
        readiness=["Use status after unstaging to verify the path moved back to unstaged."],
        options=[
            {
                "token": "--staged",
                "title": "Unstage instead of discard",
                "body": "Moves selected staged content back to the working tree.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to unstage",
                "body": "Required. Names the staged path to move out of the index.",
            },
        ],
    ),
    _content(
        key="gitignore",
        display_name=".gitignore",
        canonical_command=".gitignore",
        aliases=[],
        summary=".gitignore tells Git which untracked generated or local files to ignore.",
        tags=["ignore", "working-tree"],
        syntax=[".gitignore", "git add .gitignore"],
        effects=["Changes ignore rules once the .gitignore file is edited and staged."],
        boundaries=["It does not remove files that are already tracked."],
        watch_for="Adding ignore rules but forgetting to untrack a generated file already in Git.",
        readiness=["Pair ignore rules with git status and git rm --cached when needed."],
    ),
]


def seed_git_command_content_library() -> int:
    from scenarios.models import GitCommandContent

    active_keys = []
    for sort_order, item in enumerate(GIT_COMMAND_CONTENT_LIBRARY, start=1):
        active_keys.append(item["key"])
        GitCommandContent.objects.update_or_create(
            key=item["key"],
            defaults={
                "base_command": item["base_command"],
                "display_name": item["display_name"],
                "canonical_command": item["canonical_command"],
                "aliases": item["aliases"],
                "summary": item["summary"],
                "tags": item["tags"],
                "sections": item["sections"],
                "pages": item["pages"],
                "is_active": True,
                "version": 1,
                "sort_order": sort_order,
            },
        )
    return len(active_keys)

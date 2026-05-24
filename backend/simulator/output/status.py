from __future__ import annotations


def format_status(runtime, state: dict, *, short: bool = False) -> str:
    return format_short_status(runtime, state) if short else format_long_status(runtime, state)


def format_long_status(runtime, state: dict) -> str:
    branch = runtime._head_branch(state) or "HEAD (detached)"
    staged = state.get("staging", {}) or {}
    working = {
        path: value
        for path, value in (state.get("working_tree", {}) or {}).items()
        if runtime.normalizer.entry_status(value) != "ignored"
    }
    conflicts = sorted(state.get("conflicts", []))
    has_commits = bool(runtime._head_commit(state))
    lines = [f"On branch {branch}"]
    upstream = state.get("upstream_tracking", {}).get(branch)
    if upstream:
        lines.append(f"Your branch is tracking {upstream}.")
    if not has_commits:
        lines.extend(["", "No commits yet"])

    if conflicts:
        lines.extend(
            [
                "",
                "You have unmerged paths.",
                '  (fix conflicts and run "git commit")',
                "",
                "Unmerged paths:",
            ]
        )
        lines.extend(f"\tboth modified:   {path}" for path in conflicts)

    if staged:
        lines.extend(
            ["", "Changes to be committed:", '  (use "git restore --staged <file>..." to unstage)']
        )
        for path in sorted(staged):
            lines.append(f"\t{_long_label(runtime, staged[path]):<12} {path}")

    modified = [
        path
        for path, value in sorted(working.items())
        if runtime.normalizer.entry_status(value) != "untracked"
    ]
    untracked = [
        path
        for path, value in sorted(working.items())
        if path not in staged
        and (
            runtime.normalizer.entry_status(value) == "untracked"
            or path not in runtime._head_tree(state)
        )
    ]
    modified = [path for path in modified if path not in untracked]

    if modified:
        lines.extend(
            [
                "",
                "Changes not staged for commit:",
                '  (use "git add <file>..." to update what will be committed)',
                '  (use "git restore <file>..." to discard changes in working directory)',
            ]
        )
        for path in modified:
            lines.append(f"\t{_long_label(runtime, working[path]):<12} {path}")

    if untracked:
        lines.extend(
            [
                "",
                "Untracked files:",
                '  (use "git add <file>..." to include in what will be committed)',
            ]
        )
        lines.extend(f"\t{path}" for path in untracked)

    if not staged and not working and not conflicts:
        if has_commits:
            lines.extend(["", "nothing to commit, working tree clean"])
        else:
            lines.extend(["", 'nothing to commit (create/copy files and use "git add" to track)'])
    elif not staged and untracked and not modified and not conflicts:
        lines.extend(
            ["", 'nothing added to commit but untracked files present (use "git add" to track)']
        )
    elif not staged and (modified or conflicts):
        lines.extend(["", 'no changes added to commit (use "git add" and/or "git commit -a")'])

    return "\n".join(lines)


def format_short_status(runtime, state: dict) -> str:
    staged = state.get("staging", {}) or {}
    working = {
        path: value
        for path, value in (state.get("working_tree", {}) or {}).items()
        if runtime.normalizer.entry_status(value) != "ignored"
    }
    head_tree = runtime._head_tree(state)
    lines: list[str] = []
    for path in sorted(set(staged) | set(working)):
        staged_value = staged.get(path)
        working_value = working.get(path)
        if path not in staged and (
            runtime.normalizer.entry_status(working_value) == "untracked" or path not in head_tree
        ):
            lines.append(f"?? {path}")
            continue
        x = _short_label(runtime, staged_value, " ")
        y = _short_label(runtime, working_value, " ")
        lines.append(f"{x}{y} {path}")
    return "\n".join(lines)


def _long_label(runtime, value: object) -> str:
    status = runtime.normalizer.entry_status(value)
    if status in {"added", "new", "untracked", "intent-to-add"}:
        return "new file:"
    if status in {"deleted", "removed"}:
        return "deleted:"
    return "modified:"


def _short_label(runtime, value: object | None, default: str) -> str:
    if value is None:
        return default
    status = runtime.normalizer.entry_status(value)
    if status in {"added", "new", "untracked", "intent-to-add"}:
        return "A"
    if status in {"deleted", "removed"}:
        return "D"
    return "M"

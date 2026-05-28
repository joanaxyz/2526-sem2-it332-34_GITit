from __future__ import annotations


def format_log(runtime, state: dict, outcome) -> str:
    if outcome.stderr is not None:
        return outcome.stderr
    commits = _history(runtime, state, all_refs=bool(outcome.details.get("all")))
    limit = outcome.details.get("limit")
    if limit:
        commits = commits[: int(limit)]
    oneline = bool(outcome.details.get("oneline"))
    graph = bool(outcome.details.get("graph"))
    lines: list[str] = []
    branch_labels = _branch_labels(state)
    for commit in commits:
        if oneline:
            prefix = "* " if graph else ""
            labels = branch_labels.get(commit["id"], "")
            decoration = f" ({labels})" if labels else ""
            lines.append(f"{prefix}{commit['id']}{decoration} {commit.get('message', '')}".rstrip())
        else:
            lines.extend(
                [
                    f"commit {commit['id']}",
                    "Author: GIT it <git-it@example.test>",
                    "",
                    f"    {commit.get('message', '')}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip()


def _branch_labels(state: dict) -> dict[str, str]:
    labels_by_commit: dict[str, list[str]] = {}
    for name, target in (state.get("branches") or {}).items():
        if target:
            labels_by_commit.setdefault(target, []).append(name)
    for name, target in (state.get("remote_branches") or {}).items():
        if target:
            labels_by_commit.setdefault(target, []).append(name)
    head = state.get("head") or {}
    if head.get("type") == "branch":
        current_branch = head.get("name")
        current_target = (state.get("branches") or {}).get(current_branch)
        if current_branch and current_target:
            labels_by_commit.setdefault(current_target, []).append("HEAD")
    elif head.get("type") == "detached" and head.get("name"):
        labels_by_commit.setdefault(head["name"], []).append("HEAD")
    return {
        commit_id: ", ".join(dict.fromkeys(names))
        for commit_id, names in labels_by_commit.items()
    }


def _history(runtime, state: dict, *, all_refs: bool) -> list[dict]:
    commits_by_id = {commit["id"]: commit for commit in state.get("commits", [])}
    if all_refs:
        starts = [
            target
            for target in [
                *state.get("branches", {}).values(),
                *state.get("remote_branches", {}).values(),
            ]
            if target
        ]
    else:
        starts = [runtime._head_commit(state)] if runtime._head_commit(state) else []
    seen: list[str] = []
    stack = list(starts)
    while stack:
        commit_id = stack.pop()
        if commit_id in seen or commit_id not in commits_by_id:
            continue
        seen.append(commit_id)
        stack.extend(commits_by_id[commit_id].get("parents", []))
    order = {commit["id"]: index for index, commit in enumerate(state.get("commits", []))}
    return [
        commits_by_id[commit_id]
        for commit_id in sorted(seen, key=lambda item: order.get(item, 0), reverse=True)
    ]

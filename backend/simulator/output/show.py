from __future__ import annotations

from simulator.output.diff import _format_file


def format_show(runtime, state: dict, outcome) -> str:
    if outcome.stderr is not None:
        return outcome.stderr
    target = outcome.details.get("target")
    commit = runtime._commit_by_id(state, target)
    if not commit:
        return f"fatal: bad object {target}"
    lines = [
        f"commit {commit['id']}",
        "Author: GIT it <git-it@example.test>",
        "",
        f"    {commit.get('message', '')}",
    ]
    changes = commit.get("changes") or {}
    if changes:
        lines.append("")
        lines.extend(
            _format_file(runtime, path, change) for path, change in sorted(changes.items())
        )
    return "\n".join(lines).rstrip()

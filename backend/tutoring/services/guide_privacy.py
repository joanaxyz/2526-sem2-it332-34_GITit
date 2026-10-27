"""One outward projection for both new and legacy command-guide payloads."""

from tutoring.services.anatomy import anatomy
from tutoring.services.teaching import catalog, guide_key, safe_usage

_EFFECTS = {
    "repository": ("A folder becomes a Git repository.", "<directory>"),
    "staging": ("The staging area changes for the paths you choose.", "<path>"),
    "working_tree": ("The working files change for the paths you choose.", "<path>"),
    "commit": ("The recorded history changes.", "<commit>"),
    "branch": ("A branch pointer changes.", "<branch>"),
    "head": ("HEAD changes where you are working.", "<branch>"),
    "remote": ("The connection with another repository changes.", "<remote>"),
    "conflict": ("The conflict state changes.", "<path>"),
    "tag": ("A fixed label on a commit changes.", "<tag>"),
    "config": ("A Git setting changes.", "<value>"),
    "stash": ("Saved unfinished work changes.", "<stash>"),
    "operation": ("The paused operation changes.", "<operation>"),
}


def prospective_changes(changes):
    result = []
    seen = set()
    for change in changes:
        kind = change.get("kind")
        action = change.get("action")
        if kind not in _EFFECTS or (kind, action) in seen:
            continue
        seen.add((kind, action))
        text, placeholder = _EFFECTS[kind]
        safe = {"kind": kind, "text": text, "subjects": [placeholder]}
        if action in {"create", "delete", "move", "add", "remove", "set", "start", "finish"}:
            safe["action"] = action
        result.append(safe)
    return result


def safe_guide(payload):
    form = payload.get("command_form") or {}
    usage = safe_usage(form.get("usage_form", ""))
    family = usage.split()[1]
    overview = catalog().get(f"command:{family}")
    completed_explanation = payload.get("explanation")
    if completed_explanation not in {
        "That's the right command.",
        "That worked. Check the task for your next step.",
    }:
        completed_explanation = "That worked. Review what changed."
    return {
        "title": usage,
        "command_form": {
            "teaching_key": guide_key(form.get("teaching_key", "")),
            "usage_form": usage,
            "label": usage,
            "summary": overview.text if overview else "Read the syntax and supply your own values.",
        },
        "needs": prospective_changes(payload.get("needs", [])),
        "anatomy": anatomy(usage),
        # These describe verified actions already performed, never prospective answers.
        "changes": payload.get("changes", []),
        "verdict": payload.get("verdict"),
        "explanation": (
            completed_explanation
            if payload.get("verdict") == "correct"
            else "Review the syntax and placeholder meanings, then try your own values."
            if payload.get("verdict") == "incorrect"
            else None
        ),
    }

"""Neutral constants and builders shared by advanced form-drill ledgers."""

from __future__ import annotations

from ..advanced_story_support import build_advanced_story_state
from .common import ev, v

CORE_FORM_TAGS = ["git-status/plain", "git-log/graph-all"]
STATUS_COMMAND = "git status"
GRAPH_COMMAND = "git log --oneline --graph --all"


def build_clean_form_state(prefix: str) -> dict:
    """Return the shared clean repository fixture used by form drills."""

    return build_advanced_story_state(prefix, mode="transplant")


def build_broken_form_state(prefix: str) -> dict:
    """Return the shared known-bad repository fixture used by recovery drills."""

    return build_advanced_story_state(prefix, mode="revert")


def build_drill_variants(
    slug,
    fixture,
    commands,
    evaluation,
    details=None,
):
    """Build two prefix-distinct variants of one authored command sequence."""

    def render(prefix):
        return [command.replace("{p}", prefix) for command in commands]

    def rendered_details(prefix):
        return [detail.replace("{p}", prefix) for detail in (details or [])]

    return [
        v(
            f"{slug}-a",
            "First team's repository",
            fixture("m"),
            render("m"),
            evaluation("m"),
            details=rendered_details("m"),
        ),
        v(
            f"{slug}-b",
            "Second team's repository",
            fixture("n"),
            render("n"),
            evaluation("n"),
            details=rendered_details("n"),
        ),
    ]


def build_read_evaluation(commands, *, count=5):
    """Build evaluation for read-only waves while allowing diagnostic metadata."""

    def build(prefix):
        return ev(
            {"rules": [{"type": "commit_count_equals", "count": count}]},
            required=[command.replace("{p}", prefix) for command in commands],
        )

    return build


def build_requirement_evaluation(requirements, commands, rules=None):
    """Build a prefix-aware state and required-command evaluation factory."""

    def build(prefix):
        spec = {key: render_variant_value(value, prefix) for key, value in requirements.items()}
        if rules:
            spec["rules"] = [
                {key: render_variant_value(value, prefix) for key, value in rule.items()}
                for rule in rules
            ]
        return ev(
            spec,
            required=[command.replace("{p}", prefix) for command in commands],
        )

    return build


def render_variant_value(value, prefix):
    """Recursively replace the authored variant prefix placeholder."""

    if isinstance(value, str):
        return value.replace("{p}", prefix)
    if isinstance(value, dict):
        return {key: render_variant_value(item, prefix) for key, item in value.items()}
    if isinstance(value, list):
        return [render_variant_value(item, prefix) for item in value]
    return value


def required_command_check(label, commands):
    """Build a variant-safe objective check for required command families."""

    return {"label": label, "requirement": {"required_commands": commands}}


__all__ = [
    "CORE_FORM_TAGS",
    "GRAPH_COMMAND",
    "STATUS_COMMAND",
    "build_broken_form_state",
    "build_clean_form_state",
    "build_drill_variants",
    "build_read_evaluation",
    "build_requirement_evaluation",
    "render_variant_value",
    "required_command_check",
]

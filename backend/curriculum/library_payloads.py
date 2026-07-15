from __future__ import annotations

from typing import Any

from curriculum.library_commands import base_command_for_command
from curriculum.library_education import educational_profile_for_key
from curriculum.library_section_builders import _sections


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
    diagram: dict[str, Any] | None = None,
    learning_goal: str = "",
    problem_it_solves: str = "",
    mental_model: str = "",
    before_you_run: list[str] | None = None,
    after_you_run: list[str] | None = None,
    beginner_traps: list[str] | None = None,
    wrong_command_comparisons: list[dict[str, Any]] | None = None,
    scenario_examples: list[dict[str, Any]] | None = None,
    mini_quiz: dict[str, Any] | None = None,
    state_flow: list[str] | None = None,
) -> dict[str, Any]:
    resolved_base_command = base_command or base_command_for_command(canonical_command)
    education = educational_profile_for_key(key, resolved_base_command)
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
        diagram=diagram,
        learning_goal=learning_goal or education.get("learning_goal", ""),
        problem_it_solves=problem_it_solves or education.get("problem_it_solves", ""),
        mental_model=mental_model or education.get("mental_model", ""),
        before_you_run=before_you_run or education.get("before_you_run"),
        after_you_run=after_you_run or education.get("after_you_run"),
        beginner_traps=beginner_traps or education.get("beginner_traps"),
        wrong_command_comparisons=wrong_command_comparisons or education.get("wrong_command_comparisons"),
        scenario_examples=scenario_examples or education.get("scenario_examples"),
        mini_quiz=mini_quiz or education.get("mini_quiz"),
        state_flow=state_flow or education.get("state_flow"),
    )
    return {
        "key": key,
        "base_command": resolved_base_command,
        "display_name": display_name,
        "canonical_command": canonical_command,
        "aliases": aliases,
        "summary": summary,
        "tags": tags,
        "sections": sections,
        "pages": pages_from_command_sections(sections),
    }

def lesson_pages(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a lesson's renderable pages from authored sections.

    Lessons (general lessons) are authored with the same section/block vocabulary
    as command library entries, so the Chapter Book reader renders both."""
    return pages_from_command_sections(sections)


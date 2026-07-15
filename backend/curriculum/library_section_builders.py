from __future__ import annotations

from typing import Any

from curriculum.library_commands import (
    _bullets,
    _callout,
    _paragraph,
    _slug,
    _terminal,
    _warning,
    command_syntax_section_id,
)
from curriculum.library_preview_outputs import _sample_output_for_syntax, _syntax_title
from curriculum.library_sections import (
    _clean_items,
    _section,
    _state_language,
    _syntax_explanation,
    _syntax_how_to_read,
    _syntax_when_to_use,
    _verification_items,
)


def _generic_syntax_section(
    *,
    command: str,
    canonical_command: str,
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
) -> dict[str, Any]:
    return _section(
        section_id=command_syntax_section_id(command),
        section_type="syntax",
        title=_syntax_title(command),
        command=command,
        content=[
            _paragraph(_syntax_explanation(command, canonical_command)),
            _terminal(_sample_output_for_syntax(command)),
            _bullets("How to read this syntax", _syntax_how_to_read(command)),
            _bullets("When to use this exact command", _syntax_when_to_use(command)),
            _bullets("What changes", effects),
            _bullets("What does not change", boundaries),
            _bullets(
                "Check before/after",
                readiness
                or [
                    "Run a diagnostic command after action commands to confirm the repository state matches the scenario."
                ],
            ),
            _warning(watch_for),
        ],
    )


def _rich_syntax_section(
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
        section_type="syntax",
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
        body = item.get("body") or item.get("description") or ""
        content = item.get("content")
        if not isinstance(content, list):
            token_label = str(token or title).strip()
            content = []
            if body:
                content.append(_paragraph(body))
            content.extend(
                [
                    _callout(
                        "How to use this in a scenario",
                        f"Look for the exact clue that requires {token_label}. If the scenario does not ask for that behavior, prefer the simpler supported syntax.",
                    ),
                    _bullets(
                        "Decision checklist",
                        _clean_items(
                            [
                                f"Confirm the scenario names or implies {token_label} before using this syntax.",
                                "Keep the rest of the command unchanged unless the scenario gives another required value.",
                                "After running it, inspect the state that this option or argument is supposed to affect.",
                            ]
                        ),
                    ),
                ]
            )
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


def _comparison_block(items: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    rows = []
    for item in items or []:
        command = str(item.get("command") or "").strip()
        use_when = str(item.get("use_when") or "").strip()
        not_for = str(item.get("not_for") or "").strip()
        if command and (use_when or not_for):
            rows.append({"command": command, "use_when": use_when, "not_for": not_for})
    if not rows:
        return None
    return {
        "type": "comparison_table",
        "title": "Choose the right command",
        "rows": rows,
    }


def _before_after_block(before: list[str], after: list[str]) -> dict[str, Any] | None:
    before = _clean_items(before)
    after = _clean_items(after)
    if not before and not after:
        return None
    return {
        "type": "before_after",
        "title": "Before / after checklist",
        "before": before,
        "after": after,
    }


def _traps_block(traps: list[str]) -> dict[str, Any] | None:
    traps = _clean_items(traps)
    if not traps:
        return None
    return {
        "type": "do_dont",
        "title": "Beginner traps to avoid",
        "do_items": [
            "Match the command to the repository state, not just to a familiar name.",
            "Verify with a diagnostic command after any action command.",
        ],
        "dont_items": traps,
    }


def _scenario_blocks(scenarios: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for scenario in scenarios or []:
        title = str(scenario.get("title") or "Scenario walkthrough").strip()
        situation = str(scenario.get("situation") or "").strip()
        steps = _clean_items(scenario.get("steps") or [])
        safe_command = str(scenario.get("safe_command") or "").strip()
        if not situation and not steps and not safe_command:
            continue
        blocks.append(
            {
                "type": "scenario",
                "title": title,
                "body": situation,
                "steps": steps,
                "command": safe_command,
            }
        )
    return blocks


def _quiz_block(quiz: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(quiz, dict):
        return None
    question = str(quiz.get("question") or "").strip()
    answer = str(quiz.get("answer") or "").strip()
    choices = _clean_items(quiz.get("choices") or [])
    if not question or not answer:
        return None
    return {
        "type": "quiz",
        "title": "Self-check",
        "question": question,
        "choices": choices,
        "answer": answer,
    }


def _state_flow_block(items: list[str] | None) -> dict[str, Any] | None:
    items = _clean_items(items)
    if len(items) < 2:
        return None
    return {
        "type": "state_flow",
        "title": "State flow",
        "items": items,
    }


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
) -> list[dict[str, Any]]:
    syntax = _clean_items(syntax)
    effects = _clean_items(effects)
    boundaries = _clean_items(boundaries)
    readiness = _clean_items(readiness)
    before_items = _clean_items(before_you_run or readiness)
    after_items = _clean_items(after_you_run)
    traps = _clean_items(beginner_traps or [watch_for])

    overview_blocks: list[dict[str, Any]] = []
    if learning_goal:
        overview_blocks.append(_callout("Learning goal", learning_goal))
    overview_blocks.append(_paragraph(summary))
    if problem_it_solves:
        overview_blocks.append(_callout("Problem it solves", problem_it_solves))
    overview_blocks.append(
        _callout(
            "Mental model",
            mental_model
            or _state_language(command=canonical_command, effects=effects, boundaries=boundaries),
        )
    )
    state_flow_block = _state_flow_block(state_flow)
    if state_flow_block:
        overview_blocks.append(state_flow_block)
    if diagram:
        overview_blocks.append(diagram)
    overview_blocks.append(
        _bullets(
            "What to look at before using it",
            before_items
            or [
                "Read the scenario values carefully before choosing command syntax.",
                "Check whether the task is asking you to inspect, stage, commit, initialize, clone, ignore, unstage, or discard.",
            ],
        )
    )
    if terminal_output:
        overview_blocks.append(_terminal(terminal_output))
    overview_blocks.append(
        _bullets(
            "How to verify the result",
            _verification_items(
                command=canonical_command,
                effects=effects,
                boundaries=boundaries,
                readiness=before_items or readiness,
            )
            + after_items,
        )
    )

    sections = [
        _section(
            section_id="overview",
            section_type="overview",
            title="Overview",
            command=canonical_command,
            content=overview_blocks,
        )
    ]

    checklist = _before_after_block(before_items, after_items)
    if checklist:
        sections.append(
            _section(
                section_id="before-after",
                section_type="checklist",
                title="Before / after checklist",
                content=[checklist],
            )
        )

    for syntax_example in syntax:
        sections.append(
            _generic_syntax_section(
                command=syntax_example,
                canonical_command=canonical_command,
                effects=effects,
                boundaries=boundaries,
                watch_for=watch_for,
                readiness=before_items or readiness,
            )
        )
    sections.extend(_semantic_item_sections(section_type="option", prefix="option", items=options))
    sections.extend(_semantic_item_sections(section_type="argument", prefix="argument", items=arguments))

    comparison = _comparison_block(wrong_command_comparisons)
    if comparison:
        sections.append(
            _section(
                section_id="compare",
                section_type="comparison",
                title="Compare with similar commands",
                content=[comparison],
            )
        )

    scenario_content = _scenario_blocks(scenario_examples)
    if scenario_content:
        sections.append(
            _section(
                section_id="scenario",
                section_type="scenario",
                title="Scenario walkthrough",
                content=scenario_content,
            )
        )

    quiz = _quiz_block(mini_quiz)
    if quiz:
        sections.append(
            _section(
                section_id="mini-quiz",
                section_type="quiz",
                title="Mini quiz",
                content=[quiz],
            )
        )

    sections.extend(
        [
            _section(
                section_id="effects",
                section_type="effect",
                title="Effects and boundaries",
                content=[
                    _paragraph(
                        "Before you run the command in a scored scenario, separate the thing it changes or reports from the things it deliberately leaves alone."
                    ),
                    _bullets("Repository effect", effects),
                    _bullets("What does not change", boundaries),
                    _callout(
                        "State-check habit",
                        "After an action command, inspect the repository again. After a diagnostic command, use the evidence to choose the next action rather than treating the diagnostic output as the solution itself.",
                    ),
                ],
            ),
            _section(
                section_id="mistakes",
                section_type="mistake",
                title="Common beginner mistakes",
                content=[
                    _warning(watch_for),
                    *([_traps_block(traps)] if _traps_block(traps) else []),
                    _bullets(
                        "Safer habit",
                        _clean_items(
                            [
                                "Read the scenario's exact path, branch, directory, URL, or message before typing.",
                                "Use status, diff, log, or another diagnostic command when you are unsure what state you are changing.",
                                "Prefer narrow command syntax over a broad command when the scenario only asks for one file, one hunk, or one folder.",
                            ]
                        ),
                    ),
                ],
            ),
            _section(
                section_id="practice-notes",
                section_type="practice_note",
                title="Field notes",
                content=[
                    _paragraph(
                        "Use this page as the last check before opening an authored level variant. The preview teaches behavior; the scenario will still require you to apply the exact values from its brief."
                    ),
                    _bullets("Before running it", before_items or readiness),
                    _bullets("After running it", after_items),
                    _bullets(
                        "While solving",
                        _clean_items(
                            [
                                "Keep diagnostic commands separate from counted action commands.",
                                "Do not guess from memory when the scenario gives concrete file names or messages.",
                                "When the state is not what you expected, inspect first instead of piling on more action commands.",
                            ]
                        ),
                    ),
                ],
            ),
        ]
    )
    return sections

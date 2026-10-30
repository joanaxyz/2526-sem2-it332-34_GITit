"""Shared reference-command accounting and efficient-target authoring floors.

Policy 2 awards three stars within the efficient target. Targets must cover
verified reasonable routes; valid inspections and file-editor operations are free.
"""

from collections.abc import Iterable

from simulator.services import is_diagnostic_command, normalize_command

from common.git.shell_commands import shell_program

# Inspection-only scenarios cost nothing to solve, but a target of 0 renders as
# "Star target: <= 0 commands" and would dock a star for a single typo
# (unprocessable commands are counted), so every level keeps one command of room.
MINIMUM_STAR_TARGET = 1


def counted_command_total(commands: Iterable[str] | None) -> int:
    """How many of ``commands`` consume command budget at runtime."""

    return sum(
        1
        for command in commands or []
        if command.strip()
        and not is_diagnostic_command(normalize_command(command))
        and not shell_program(command)
    )


def star_target_for_variants(
    variants: Iterable[dict] | None,
    *,
    authored: int | None = None,
    solution_key: str = "solution_commands_template",
) -> int:
    """The counted-command star target for a scenario/trial spec.

    Taken across every variant so the target is reachable whichever variant is
    served. An authored value is honoured only when it is at least that cost:
    a smaller one would put two and three stars out of reach for every player.
    """

    required = max(
        (counted_command_total(variant.get(solution_key)) for variant in variants or []),
        default=0,
    )
    if authored is not None:
        required = max(int(authored), required)
    return max(MINIMUM_STAR_TARGET, required)


def command_budget_for_spec(
    spec: dict, *, solution_key: str = "solution_commands_template"
) -> dict:
    """``{"min_counted_commands", "max_counted_commands"}`` for one seed spec."""

    star_target = star_target_for_variants(
        spec.get("variants"),
        authored=spec.get("min_counted_commands"),
        solution_key=solution_key,
    )
    return {
        "min_counted_commands": star_target,
        # The limit is the losing condition, never below the scoring target.
        "max_counted_commands": max(int(spec.get("max_counted_commands") or 0), star_target),
    }

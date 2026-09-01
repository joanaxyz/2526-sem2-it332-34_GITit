"""Star-target (par) accounting shared by the curriculum seeders.

Two stars require ``counted_commands <= min_counted_commands`` and three require
that on the first try, so the target has to be at least what the authored
solution costs. Authoring defaults and hand-written values drifted below that
and locked levels at one star, so the seed derives the floor from the solution
itself, classified by the same engine rule the runtime bills commands with:
valid read-only inspections are free, everything else costs one counted command.
"""

from collections.abc import Iterable

from simulator.services import is_diagnostic_command

# Inspection-only waves cost nothing to solve, but a target of 0 renders as
# "Star target: <= 0 commands" and would dock a star for a single typo
# (unprocessable commands are counted), so every level keeps one command of room.
MINIMUM_STAR_TARGET = 1


def counted_command_total(commands: Iterable[str] | None) -> int:
    """How many of ``commands`` consume command budget at runtime."""

    return sum(1 for command in commands or [] if not is_diagnostic_command(command))


def star_target_for_variants(
    variants: Iterable[dict] | None,
    *,
    authored: int | None = None,
    solution_key: str = "solution_commands_template",
) -> int:
    """The counted-command star target for a wave/trial spec.

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

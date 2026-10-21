"""Authoritative variant-specific action limits for launch and offline replay."""


def _value(params, key, fallback):
    try:
        return int(params.get(key, fallback))
    except (TypeError, ValueError):
        return fallback


def command_budget(variant) -> tuple[int, int]:
    params = variant.parameter_context if isinstance(variant.parameter_context, dict) else {}
    scenario = variant.scenario
    minimum = max(1, _value(params, "minimum_counted_commands", scenario.min_counted_commands))
    maximum = max(minimum, _value(params, "maximum_counted_commands", scenario.max_counted_commands))
    return minimum, maximum

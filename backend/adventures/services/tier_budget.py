"""Authoritative variant-specific action limits for launch and offline replay."""


def _value(params, key, fallback):
    try:
        return int(params.get(key, fallback))
    except (TypeError, ValueError):
        return fallback


def command_budget(variant) -> tuple[int, int]:
    params = variant.parameter_context if isinstance(variant.parameter_context, dict) else {}
    wave = variant.wave
    minimum = max(1, _value(params, "minimum_counted_commands", wave.min_counted_commands))
    maximum = max(minimum, _value(params, "maximum_counted_commands", wave.max_counted_commands))
    return minimum, maximum

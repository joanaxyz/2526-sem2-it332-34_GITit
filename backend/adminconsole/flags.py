"""Canonical feature-flag registry and default resolution."""

from __future__ import annotations

SUPPORTED_FLAGS = {
    "shop-purchases": {
        "key": "shop-purchases",
        "label": "Shop purchases",
        "description": "Allow players to claim or purchase stories and companions.",
        "default": True,
    },
}


def feature_enabled(key: str) -> bool:
    spec = SUPPORTED_FLAGS.get(key)
    if spec is None:
        return False
    from adminconsole.models import FeatureFlag

    override = FeatureFlag.objects.filter(key=key).only("enabled").first()
    return override.enabled if override is not None else bool(spec["default"])

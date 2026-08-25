"""Feature-flag read models for the admin console."""

from __future__ import annotations

from adminconsole.flags import SUPPORTED_FLAGS
from adminconsole.models import FeatureFlag


def admin_settings_payload() -> dict:
    overrides = {
        row.key: row for row in FeatureFlag.objects.filter(key__in=SUPPORTED_FLAGS)
    }
    return {
        "feature_flags": [
            {
                "key": key,
                "label": spec["label"],
                "description": spec["description"],
                "enabled": (
                    overrides[key].enabled if key in overrides else bool(spec["default"])
                ),
            }
            for key, spec in SUPPORTED_FLAGS.items()
        ]
    }


def flag_payload(flag) -> dict:
    return {
        "key": flag.key,
        "label": flag.label,
        "description": flag.description,
        "enabled": flag.enabled,
    }

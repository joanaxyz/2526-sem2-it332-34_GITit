"""Official Arcane Spire tower asset seed specs.

Structural assets are intentionally generic: a tower is made from one crown, one
base, repeatable sections, and landings. Adventure/challenge/tome behavior is
authored by placing interactable artifacts into sections.
"""

ARCANE_SPIRE_TAG = "arcane-spire"

OFFICIAL_TOWER_PIECE_SPECS = [
    {
        "slug": "official-crown",
        "label": "Arcane Crown",
        "piece_type": "crown",
        "svg": "crown/spire.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 560 250",
        "anchors": {
            "center": {"x": 280, "y": 126},
            "stack_bottom": {"x": 280, "y": 236},
        },
        "bounds": {
            "x": 24,
            "y": 4,
            "width": 512,
            "height": 232,
            "artifact_safe_bounds": {"x": 92, "y": 52, "width": 376, "height": 128},
        },
    },
    {
        "slug": "official-hall-section",
        "label": "Arcane Hall Section",
        "piece_type": "section",
        "svg": "sections/hall.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 368 200",
        "anchors": {"center": {"x": 184, "y": 100}},
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 368,
            "height": 200,
            "artifact_safe_bounds": {"x": 36, "y": 24, "width": 296, "height": 152},
        },
    },
    {
        "slug": "official-trial-section",
        "label": "Arcane Trial Section",
        "piece_type": "section",
        "svg": "sections/trial.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 368 200",
        "anchors": {"center": {"x": 184, "y": 100}},
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 368,
            "height": 200,
            "artifact_safe_bounds": {"x": 34, "y": 28, "width": 300, "height": 136},
        },
    },
    {
        "slug": "official-window-section",
        "label": "Arcane Window Section",
        "piece_type": "section",
        "svg": "sections/window.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 480 140",
        "anchors": {"center": {"x": 240, "y": 70}},
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 480,
            "height": 140,
            "artifact_safe_bounds": {"x": 52, "y": 18, "width": 376, "height": 104},
        },
    },
    {
        "slug": "official-landing",
        "label": "Arcane Walkway Landing",
        "piece_type": "landing",
        "svg": "landings/walkway.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 592 73.28",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 2.24, "x2": 540, "y2": 2.24},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73.28,
            "artifact_safe_bounds": {"x": 44, "y": 0, "width": 504, "height": 24},
        },
    },
    {
        "slug": "official-challenge-landing",
        "label": "Arcane Crenel Landing",
        "piece_type": "landing",
        "svg": "landings/crenel.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 592 73.28",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 12.48, "x2": 580, "y2": 12.48},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73.28,
            "artifact_safe_bounds": {"x": 44, "y": 6, "width": 504, "height": 28},
        },
    },
    {
        "slug": "official-tome-landing",
        "label": "Arcane Tome Landing",
        "piece_type": "landing",
        "svg": "landings/tome.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 592 73.28",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 0, "x2": 486, "y2": 0},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73.28,
            "artifact_safe_bounds": {"x": 64, "y": 0, "width": 408, "height": 28},
        },
    },
    {
        "slug": "official-empty-landing",
        "label": "Empty Landing",
        "piece_type": "landing",
        "svg": "landings/empty.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 592 73.28",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 12.48, "x2": 580, "y2": 12.48},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73.28,
            "artifact_safe_bounds": {"x": 44, "y": 6, "width": 504, "height": 28},
        },
    },
    {
        "slug": "official-base",
        "label": "Arcane Base",
        "piece_type": "base",
        "svg": "landings/walkway.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 592 73.28",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 2.24, "x2": 540, "y2": 2.24},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73.28,
            "artifact_safe_bounds": {"x": 44, "y": 0, "width": 504, "height": 24},
        },
    },
]

OFFICIAL_TOWER_ARTIFACT_SPECS = [
    {
        "slug": "official-gate-artifact",
        "label": "Arcane Gate",
        "svg": "artifacts/adventure-gate.svg",
        "tags": [ARCANE_SPIRE_TAG, "interactable"],
        "view_box": "-24 0 163 188",
        "config": {
            "view_box": "-24 0 163 188",
            "bounds": {"x": 0, "y": 0, "width": 115, "height": 159},
            "interaction_zones": {"activate": {"x": 6, "y": 15, "width": 103, "height": 140}},
        },
    },
    {
        "slug": "official-trial-gate-easy-artifact",
        "label": "Arcane Plank Gate",
        "svg": "artifacts/trial-gate-easy.svg",
        "tags": [ARCANE_SPIRE_TAG, "interactable"],
        "view_box": "0 0 88.8 128.7",
        "config": {
            "view_box": "0 0 88.8 128.7",
            "bounds": {"x": 2, "y": 2, "width": 84.8, "height": 126.7},
            "interaction_zones": {"activate": {"x": 8, "y": 10, "width": 72.8, "height": 116}},
        },
    },
    {
        "slug": "official-portcullis-artifact",
        "label": "Arcane Portcullis",
        "svg": "artifacts/trial-portcullis.svg",
        "tags": [ARCANE_SPIRE_TAG, "interactable"],
        "view_box": "0 0 88.8 128.7",
        "config": {
            "view_box": "0 0 88.8 128.7",
            "bounds": {"x": 2, "y": 2, "width": 84.8, "height": 126.7},
            "interaction_zones": {"activate": {"x": 8, "y": 10, "width": 72.8, "height": 116}},
        },
    },
    {
        "slug": "official-trial-gate-hard-artifact",
        "label": "Arcane Demon Gate",
        "svg": "artifacts/trial-gate-hard.svg",
        "tags": [ARCANE_SPIRE_TAG, "interactable"],
        "view_box": "0 0 88.8 128.7",
        "config": {
            "view_box": "0 0 88.8 128.7",
            "bounds": {"x": 2, "y": 2, "width": 84.8, "height": 126.7},
            "interaction_zones": {"activate": {"x": 8, "y": 10, "width": 72.8, "height": 116}},
        },
    },
    {
        "slug": "official-tome-artifact",
        "label": "Arcane Tome",
        "svg": "artifacts/tome-lectern.svg",
        "tags": [ARCANE_SPIRE_TAG, "interactable"],
        "view_box": "0 0 200 184",
        "config": {
            "view_box": "0 0 200 184",
            "bounds": {"x": 36, "y": 11, "width": 128, "height": 163},
            "interaction_zones": {"read": {"x": 36, "y": 24, "width": 128, "height": 142}},
        },
    },
]

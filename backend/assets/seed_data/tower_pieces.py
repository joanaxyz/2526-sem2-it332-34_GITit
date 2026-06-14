"""Official structural tower-piece asset seed specs.

These six pieces are the **Arcane Spire** starter set: they are tagged
``arcane-spire`` and granted to every player's asset registry on sign-up, so a
new author opens the tower editor with a usable, on-brand kit by default.
"""

ARCANE_SPIRE_TAG = "arcane-spire"

OFFICIAL_TOWER_PIECE_SPECS = [
    {
        "slug": "official-spire",
        "label": "Arcane Spire",
        "piece_type": "spire",
        "svg": "spire.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 200 120",
        "anchors": {
            "center": {"x": 100, "y": 76},
            "stack_bottom": {"x": 100, "y": 116},
        },
        "bounds": {"x": 12, "y": 4, "width": 176, "height": 112},
    },
    {
        "slug": "official-landing",
        "label": "Arcane Landing",
        "piece_type": "landing",
        "svg": "landing.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 220 48",
        "anchors": {
            "walk_rail": {"x1": 18, "y1": 18, "x2": 202, "y2": 18},
            "artifact_safe_bounds": {"x": 28, "y": 6, "width": 164, "height": 28},
        },
        "bounds": {"x": 6, "y": 4, "width": 208, "height": 40},
    },
    {
        "slug": "official-door",
        "label": "Arcane Door",
        "piece_type": "door",
        "svg": "door.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 120 160",
        "anchors": {
            "door_center": {"x": 60, "y": 88},
            "walk_rail": {"x1": 16, "y1": 142, "x2": 104, "y2": 142},
        },
        "bounds": {"x": 10, "y": 8, "width": 100, "height": 144},
        "interaction_zones": {
            "door": {"x": 24, "y": 38, "width": 72, "height": 104}
        },
        "state_variants": {
            "locked": {"class_name": "is-locked"},
            "unlocked": {"class_name": "is-unlocked"},
        },
    },
    {
        "slug": "official-adventure-section",
        "label": "Arcane Adventure Hall",
        "piece_type": "adventure_section",
        "svg": "adventure-section.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 260 220",
        "anchors": {
            "door_center": {"x": 130, "y": 136},
            "artifact_safe_bounds": {"x": 32, "y": 24, "width": 196, "height": 162},
        },
        "bounds": {"x": 12, "y": 8, "width": 236, "height": 204},
    },
    {
        "slug": "official-challenge-section",
        "label": "Arcane Challenge Hall",
        "piece_type": "challenge_section",
        "svg": "challenge-section.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 300 240",
        "anchors": {
            "door_row": {"x1": 44, "y1": 174, "x2": 256, "y2": 174},
            "artifact_safe_bounds": {"x": 30, "y": 24, "width": 240, "height": 182},
        },
        "bounds": {"x": 12, "y": 8, "width": 276, "height": 224},
    },
    {
        "slug": "official-tome",
        "label": "Arcane Tome",
        "piece_type": "tome",
        "svg": "tome.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 180 160",
        "anchors": {
            "tome_center": {"x": 90, "y": 78},
            "walk_rail": {"x1": 26, "y1": 138, "x2": 154, "y2": 138},
        },
        "bounds": {"x": 18, "y": 10, "width": 144, "height": 140},
        "interaction_zones": {
            "read": {"x": 38, "y": 24, "width": 104, "height": 104}
        },
    },
]

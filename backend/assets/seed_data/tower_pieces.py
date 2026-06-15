"""Official structural tower-piece asset seed specs.

These pieces are the **Arcane Spire** starter set: they are tagged
``arcane-spire`` and granted to every player's asset registry on sign-up, so a
new author opens the tower editor with a usable, on-brand kit by default.
"""

ARCANE_SPIRE_TAG = "arcane-spire"

OFFICIAL_TOWER_PIECE_SPECS = [
    {
        "slug": "official-spire",
        "label": "Arcane Crown",
        "piece_type": "spire",
        "svg": "spire.svg",
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
        "slug": "official-window-section",
        "label": "Arcane Window Section",
        "piece_type": "window_section",
        "svg": "window-section.svg",
        "tags": [ARCANE_SPIRE_TAG],
        # viewBox is trimmed to the real art bottom (the belt base ends at ~139.2,
        # incl. its 2px stroke) instead of the old 148 — the ~9px of trailing dead
        # space was the gap under the window band. Pieces now stack on their true
        # bounds, so the joint below needs no compensating negative margin.
        "view_box": "0 0 480 140",
        "anchors": {
            "stack_top": {"x": 240, "y": 0},
            "stack_bottom": {"x": 240, "y": 139},
        },
        "bounds": {
            "x": 20,
            "y": 0,
            "width": 440,
            "height": 139,
            "artifact_safe_bounds": {"x": 58, "y": 14, "width": 364, "height": 94},
        },
    },
    {
        "slug": "official-landing",
        "label": "Arcane Landing",
        "piece_type": "landing",
        "svg": "landing.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 552 64.8",
        "anchors": {
            "walk_rail": {"x1": 12, "y1": 2.24, "x2": 540, "y2": 2.24},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 552,
            "height": 64.8,
            "artifact_safe_bounds": {"x": 44, "y": 0, "width": 464, "height": 20},
        },
        "state_variants": {
            "regular": {
                "view_box": "0 0 552 64.8",
                "anchors": {
                    "walk_rail": {"x1": 12, "y1": 2.24, "x2": 540, "y2": 2.24},
                },
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 552,
                    "height": 64.8,
                    "artifact_safe_bounds": {
                        "x": 44,
                        "y": 0,
                        "width": 464,
                        "height": 20,
                    },
                },
            },
            "after-challenges": {
                "view_box": "0 0 592 73.28",
                "anchors": {
                    "walk_rail": {"x1": 14, "y1": 12.48, "x2": 578, "y2": 12.48},
                },
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 592,
                    "height": 73.28,
                    "artifact_safe_bounds": {
                        "x": 48,
                        "y": 0,
                        "width": 496,
                        "height": 28,
                    },
                },
            },
            "tome": {
                "view_box": "0 0 480 46.4",
                "anchors": {
                    "walk_rail": {"x1": 0, "y1": 0, "x2": 480, "y2": 0},
                },
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 480,
                    "height": 46.4,
                    "artifact_safe_bounds": {
                        "x": 36,
                        "y": 0,
                        "width": 408,
                        "height": 24,
                    },
                },
            },
        },
    },
    {
        "slug": "official-door",
        "label": "Arcane Gate",
        "piece_type": "door",
        "svg": "door.svg",
        "tags": [ARCANE_SPIRE_TAG],
        # The arched two-leaf gate. Its SVG tags `leaf-left`/`leaf-right`/
        # `interior`/`accent` so the `swing-open` preset can open it. A single
        # door or portcullis is its own asset (`swing-single` / `slide-up`).
        # Presets are platform-defined; they never run user code.
        "view_box": "-24 0 163 188",
        "animation": {"preset": "swing-open"},
        "anchors": {
            "door_center": {"x": 57.6, "y": 85},
            "walk_rail": {"x1": 4, "y1": 159, "x2": 111, "y2": 159},
        },
        "bounds": {"x": 0, "y": 0, "width": 115, "height": 159},
        "interaction_zones": {
            "door": {"x": 6, "y": 15, "width": 103, "height": 140}
        },
        "state_variants": {
            "locked": {"class_name": "is-locked"},
            "unlocked": {"class_name": "is-unlocked"},
        },
    },
    {
        "slug": "official-portcullis",
        "label": "Arcane Portcullis",
        "piece_type": "door",
        "svg": "portcullis.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 88.8 128.7",
        "animation": {"preset": "slide-up"},
        "anchors": {
            "door_center": {"x": 44.4, "y": 70},
            "walk_rail": {"x1": 6, "y1": 128.7, "x2": 82.8, "y2": 128.7},
        },
        "bounds": {"x": 2, "y": 2, "width": 84.8, "height": 126.7},
        "interaction_zones": {
            "door": {"x": 8, "y": 10, "width": 72.8, "height": 116}
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
        "view_box": "0 0 368 200",
        "anchors": {
            "door_center": {"x": 184, "y": 132},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 368,
            "height": 200,
            "artifact_safe_bounds": {"x": 36, "y": 24, "width": 296, "height": 152},
        },
        "state_variants": {
            "adventure": {
                "view_box": "0 0 368 200",
                "bounds": {
                    "artifact_safe_bounds": {
                        "x": 36,
                        "y": 24,
                        "width": 296,
                        "height": 152,
                    },
                },
            }
        },
    },
    {
        "slug": "official-challenge-section",
        "label": "Arcane Challenge Hall",
        "piece_type": "challenge_section",
        "svg": "challenge-section.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 368 200",
        "anchors": {
            "door_row": {"x1": 54, "y1": 150, "x2": 314, "y2": 150},
        },
        "bounds": {
            "x": 0,
            "y": 0,
            "width": 368,
            "height": 200,
            "artifact_safe_bounds": {"x": 34, "y": 28, "width": 300, "height": 136},
        },
        "state_variants": {
            "challenge": {
                "view_box": "0 0 368 200",
                "bounds": {
                    "artifact_safe_bounds": {
                        "x": 34,
                        "y": 28,
                        "width": 300,
                        "height": 136,
                    },
                },
            }
        },
    },
    {
        "slug": "official-tome",
        "label": "Arcane Tome",
        "piece_type": "tome",
        "svg": "tome.svg",
        "tags": [ARCANE_SPIRE_TAG],
        "view_box": "0 0 200 184",
        "animation": {"preset": "fade"},
        "anchors": {
            "tome_center": {"x": 100, "y": 76},
            "walk_rail": {"x1": 46, "y1": 174, "x2": 154, "y2": 174},
        },
        "bounds": {
            "x": 36,
            "y": 11,
            "width": 128,
            "height": 163,
            "artifact_safe_bounds": {"x": 52, "y": 28, "width": 96, "height": 134},
        },
        "interaction_zones": {
            "read": {"x": 36, "y": 24, "width": 128, "height": 142}
        },
    },
]

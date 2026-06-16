"""Storey plan for the v2 Git-it curriculum.

The tower is ordered by concept dependency. A Challenge in a storey may combine
commands from that storey's Command Adventure and earlier Command Adventures,
but it must never introduce a Git problem type before Adventure has taught the
pieces needed to solve it.

Note: across curriculum_v2 specs, the frozen authoring key ``"module"`` means
"storey slug" - it predates the storey naming and stays frozen so authored
entries never need rewriting.
"""

def tower_layout(
    *,
    adventure_section: str = "official-hall-section",
    adventure_landing: str = "official-landing",
    challenge_section: str = "official-trial-section",
    challenge_landing: str = "official-challenge-landing",
    window_section: str = "official-window-section",
    window_landing: str = "official-landing",
    tome_artifact: str = "official-tome-artifact",
) -> dict:
    """Asset-level visual defaults for one official storey.

    These are authored data, not renderer assumptions: each storey can choose
    different structural art and artifact defaults while the frontend still
    renders only crown/base/section/landing plus placed artifacts.
    """

    return {
        "crown": {"asset_slug": "official-crown"},
        "base": {"asset_slug": "official-base"},
        "slots": {
            "window": {
                "section_asset_slug": window_section,
                "landing_asset_slug": window_landing,
                "artifact_asset_slug": tome_artifact,
                "artifact": {"x": 184, "y": 112, "width": 96, "height": 88, "z_index": 12},
            },
            "adventure": {
                "section_asset_slug": adventure_section,
                "landing_asset_slug": adventure_landing,
                "artifact_asset_slug": "official-gate-artifact",
                "artifact": {"x": 184, "y": 122, "width": 116, "height": 134, "z_index": 12},
            },
            "challenge": {
                "section_asset_slug": challenge_section,
                "landing_asset_slug": challenge_landing,
                "artifact": {"y": 124, "width": 62, "height": 94, "z_index": 12},
            },
            "empty_challenge": {"section_asset_slug": challenge_section},
        },
    }


STOREYS = [
    {
        "slug": "creating-inspecting-repositories",
        "number": 1,
        "title": "Repository Foundations",
        "description": (
            "Start from empty or remote projects, then read branch and commit-history signals "
            "before changing anything."
        ),
        "mob_roster": ["slime", "skeleton", "archer"],
        "boss_roster": ["werebear"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "tracking-changes-snapshots",
        "number": 2,
        "title": "Tracking Changes and Snapshots",
        "description": (
            "Use diff, staging, commits, restore, and tracked-file removal to create intentional snapshots."
        ),
        "mob_roster": ["skeleton", "archer", "skeleton-archer"],
        "boss_roster": ["werewolf"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "branching-switching",
        "number": 3,
        "title": "Branch Navigation",
        "description": (
            "Create branch pointers, move HEAD safely, branch from old commits, and clean up merged branches."
        ),
        "mob_roster": ["archer", "skeleton-archer", "swordsman"],
        "boss_roster": ["elite-orc"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "merging-conflicts",
        "number": 4,
        "title": "Merging and Conflict Resolution",
        "description": (
            "Integrate branch histories, recognize fast-forward versus merge commits, and finish conflicted merges."
        ),
        "mob_roster": ["skeleton-archer", "swordsman", "armored-orc"],
        "boss_roster": ["knight-templar"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "undoing-recovery",
        "number": 5,
        "title": "Undoing and Recovery",
        "description": (
            "Choose between restore, amend, reset, revert, and reflog-based recovery based on history safety."
        ),
        "mob_roster": ["swordsman", "armored-orc", "skeleton"],
        "boss_roster": ["wizard"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "temporary-work-patches",
        "number": 6,
        "title": "Temporary Work and Patch Movement",
        "description": (
            "Shelve unfinished work and transplant selected commits without dragging an entire branch history."
        ),
        "mob_roster": ["armored-orc", "swordsman", "skeleton-archer"],
        "boss_roster": ["priest"],
        "tower_layout": tower_layout(),
    },
    {
        "slug": "remotes-collaboration",
        "number": 7,
        "title": "Remotes and Collaboration",
        "description": (
            "Read remote relationships, update remote-tracking refs, pull, publish, and handle collaboration history."
        ),
        "mob_roster": ["armored-orc", "swordsman", "archer"],
        "boss_roster": ["knight-templar", "wizard"],
        "tower_layout": tower_layout(),
    },
]

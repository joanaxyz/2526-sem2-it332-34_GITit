"""Storey plan for the v2 Git-it curriculum.

The tower is ordered by concept dependency. A Challenge in a storey may combine
commands from that storey's Command Adventure and earlier Command Adventures,
but it must never introduce a Git problem type before Adventure has taught the
pieces needed to solve it.

Note: across curriculum_v2 specs, the frozen authoring key ``"module"`` means
"storey slug" — it predates the storey naming and stays frozen so authored
entries never need rewriting.
"""

STOREYS = [
    {
        "slug": "creating-inspecting-repositories",
        "number": 1,
        "title": "Repository Foundations",
        "description": (
            "Start from empty or remote projects, then read branch and commit-history signals "
            "before changing anything."
        ),
    },
    {
        "slug": "tracking-changes-snapshots",
        "number": 2,
        "title": "Tracking Changes and Snapshots",
        "description": (
            "Use diff, staging, commits, restore, and tracked-file removal to create intentional snapshots."
        ),
    },
    {
        "slug": "branching-switching",
        "number": 3,
        "title": "Branch Navigation",
        "description": (
            "Create branch pointers, move HEAD safely, branch from old commits, and clean up merged branches."
        ),
    },
    {
        "slug": "merging-conflicts",
        "number": 4,
        "title": "Merging and Conflict Resolution",
        "description": (
            "Integrate branch histories, recognize fast-forward versus merge commits, and finish conflicted merges."
        ),
    },
    {
        "slug": "undoing-recovery",
        "number": 5,
        "title": "Undoing and Recovery",
        "description": (
            "Choose between restore, amend, reset, revert, and reflog-based recovery based on history safety."
        ),
    },
    {
        "slug": "temporary-work-patches",
        "number": 6,
        "title": "Temporary Work and Patch Movement",
        "description": (
            "Shelve unfinished work and transplant selected commits without dragging an entire branch history."
        ),
    },
    {
        "slug": "remotes-collaboration",
        "number": 7,
        "title": "Remotes and Collaboration",
        "description": (
            "Read remote relationships, update remote-tracking refs, pull, publish, and handle collaboration history."
        ),
    },
]

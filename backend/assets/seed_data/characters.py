"""Official character asset seed specs.

Blue's source sheets already live in the frontend package. The seeder copies
them into backend media so the normal descriptor path can serve the active
character while the frontend keeps its local fallback for development/offline
contexts.
"""

CHARACTER_SPECS = [
    {
        "slug": "blue",
        "label": "Blue",
        "scale": 0.65,
        "metrics": {
            "walk_speed": 140,
            "run_speed": 280,
            "fly_speed": 380,
            "foot_offset": 51,
            "take_off_airborne_frame": 45,
            "take_off_lift_speed": 55,
            "land_fall_frame": 32,
        },
        "random_actions": ["random1"],
        "actions": {
            "idle": {"file": "idle.png", "fps": 10, "loops": True},
            "walk": {"file": "walk.png", "fps": 12, "loops": True},
            "run": {"file": "run.png", "fps": 14, "loops": True},
            "fly": {"file": "fly.png", "fps": 24, "loops": True},
            "float": {"file": "float.png", "fps": 8, "loops": True},
            "take_off": {"file": "take_off.png", "fps": 40, "loops": False},
            "land": {"file": "land.png", "fps": 40, "loops": False},
            "random1": {"file": "random1.png", "fps": 20, "loops": False},
            "cast": {"file": "cast.png", "fps": 32, "loops": False},
            "hurt": {"file": "hurt.png", "fps": 20, "loops": False},
            "book": {"file": "book.png", "fps": 20, "loops": False},
            "summon": {"file": "summon.png", "fps": 28, "loops": False},
        },
    }
]


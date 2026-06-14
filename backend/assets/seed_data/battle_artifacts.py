"""Official battle artifact asset seed specs.

Battle artifacts are standalone set-pieces that sit on the battle stage rather
than in the tower structure - currently the crystal Blue defends. Source sheets
live in the frontend package (256x256 frames, 5x5 grid) alongside the character
sheets; the seeder copies them into backend media so the normal descriptor path
can serve them while the frontend keeps its local copy for development.
"""

BATTLE_ARTIFACT_SPECS = [
    {
        "slug": "crystal",
        "label": "Arcane Crystal",
        "scale": 0.5,
        # Part of the default Arcane Spire kit granted to every player.
        "tags": ["arcane-spire"],
        # Source frames pad ~52px below the crystal's base; the battle stage pulls
        # it down by foot_offset * scale to stand it on the ledge line.
        "config": {"foot_offset": 52},
        "actions": {
            "idle": {"file": "idle.png", "fps": 12, "loops": True},
            "defeat": {"file": "defeat.png", "fps": 16, "loops": False},
        },
    }
]

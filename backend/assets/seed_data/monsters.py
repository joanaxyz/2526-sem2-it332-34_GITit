"""Official monster asset specs (migrated from the old frontend monsters.ts).

Frame counts are NOT listed here - the seed importer reads each PNG and counts
frames itself (assets.models.AssetSprite.recompute_frames). Each spec only
carries what an image can't express: tier, display scale, attack tuning,
hp-bar/foot metrics, and which file + fps maps to each action category.

Sheets live next to this module under ``seed_assets/monsters/<slug>/``; projectile
sheets live under ``seed_assets/monsters/projectiles/`` and are attached to the
firing monster as its ``projectile`` action.
"""

from __future__ import annotations

# action -> (filename, fps). The "attack" action selects the right attackNN.png.
# A "projectile" action (path under projectiles/) is added for ranged attackers.
MONSTER_SPECS: list[dict] = [
    # -- Mobs --------------------------------------------------------------
    {
        "slug": "slime", "label": "Slime", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "melee", "hit_frame": 3, "lunge_px": 48},
        "metrics": {"hp_bar_fraction": 0.42},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 10), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "skeleton", "label": "Skeleton", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "melee", "hit_frame": 4, "lunge_px": 56},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 10), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "archer", "label": "Archer", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "projectile", "hit_frame": 6, "projectile": "arrow"},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 12), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
            "projectile": ("projectiles/arrow.png", 1),
        },
    },
    {
        "slug": "skeleton-archer", "label": "Skeleton Archer", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "projectile", "hit_frame": 6, "projectile": "arrow"},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack.png", 12), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
            "projectile": ("projectiles/arrow.png", 1),
        },
    },
    {
        "slug": "swordsman", "label": "Swordsman", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "melee", "hit_frame": 4, "lunge_px": 56},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "armored-orc", "label": "Armored Orc", "tier": "mob", "scale": 1.0,
        "attack": {"kind": "melee", "hit_frame": 4, "lunge_px": 52},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },

    # -- Elites ------------------------------------------------------------
    {
        "slug": "armored-skeleton", "label": "Armored Skeleton", "tier": "elite", "scale": 1.1,
        "attack": {"kind": "melee", "hit_frame": 5, "lunge_px": 60},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "greatsword-skeleton", "label": "Greatsword Skeleton", "tier": "elite", "scale": 1.1,
        "attack": {"kind": "melee", "hit_frame": 6, "lunge_px": 60},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "knight", "label": "Knight", "tier": "elite", "scale": 1.1,
        "attack": {"kind": "melee", "hit_frame": 4, "lunge_px": 56},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "lancer", "label": "Lancer", "tier": "elite", "scale": 1.1,
        "attack": {"kind": "melee", "hit_frame": 3, "lunge_px": 72},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk01.png", 10),
            "attack": ("attack01.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },

    # -- Bosses (rendered 1.5"2x) ------------------------------------------
    {
        "slug": "elite-orc", "label": "Elite Orc", "tier": "boss", "scale": 1.6,
        "attack": {"kind": "melee", "hit_frame": 7, "lunge_px": 72},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack02.png", 12), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "knight-templar", "label": "Knight Templar", "tier": "boss", "scale": 1.6,
        "attack": {"kind": "melee", "hit_frame": 7, "lunge_px": 72},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk01.png", 10),
            "attack": ("attack03.png", 12), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "werebear", "label": "Werebear", "tier": "boss", "scale": 1.8,
        "attack": {"kind": "melee", "hit_frame": 8, "lunge_px": 80},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack02.png", 13), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "werewolf", "label": "Werewolf", "tier": "boss", "scale": 1.8,
        "attack": {"kind": "melee", "hit_frame": 8, "lunge_px": 80},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack02.png", 13), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
        },
    },
    {
        "slug": "wizard", "label": "Wizard", "tier": "boss", "scale": 1.6,
        "attack": {"kind": "projectile", "hit_frame": 4, "projectile": "magic-wizard"},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack01.png", 9), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
            "projectile": ("projectiles/magic-wizard.png", 20),
        },
    },
    {
        "slug": "priest", "label": "Priest", "tier": "boss", "scale": 1.5,
        "attack": {"kind": "projectile", "hit_frame": 6, "projectile": "magic-priest"},
        "actions": {
            "idle": ("idle.png", 8), "walk": ("walk.png", 10),
            "attack": ("attack.png", 11), "hurt": ("hurt.png", 10),
            "death": ("death.png", 8), "portrait": ("portrait.png", 1),
            "projectile": ("projectiles/magic-priest.png", 14),
        },
    },
]

# Actions that loop while displayed; the rest play once. Canonical definition
# lives in assets.sprite_actions; re-exported here for the seed importer.
from assets.sprite_actions import LOOPING_ACTIONS  # noqa: E402,F401

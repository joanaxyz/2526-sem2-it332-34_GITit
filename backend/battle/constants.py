"""Battle layer constants shared by adventures and challenges.

The player has no separate HP pool: the command budget is the player's
resource ("mana" in the UI), so defeat is the existing budget exhaustion.
Monster/boss HP is authoritative here and travels in `battle_state` JSON on
the attempt/run rows.

Monster species values are Asset.slug keys. Seed validation fails loudly when
an authored roster names a slug that is not present in the official assets.
"""

BATTLE_SCHEMA_VERSION = 1

EVENT_PLAYER_ATTACK = "player_attack"
EVENT_MONSTER_ATTACK = "monster_attack"
EVENT_MONSTER_DEATH = "monster_death"
EVENT_ENCOUNTER_CLEARED = "encounter_cleared"
EVENT_PLAYER_DEFEAT = "player_defeat"

# Why a monster got a free hit. Only one cause today: a counted command that
# made no progress (a wrong or failed git command).
CAUSE_MISS = "miss"

TIER_MOB = "mob"
TIER_BOSS = "boss"

# Deterministic default rosters cycle these species (stable hash of the level
# slug picks the offset, so seeds never churn and every environment agrees).
# Authored `encounter_spec` rows may still name any monster asset slug/tier
# (incl. elites); the defaults below only cover unauthored mob/boss cases.
MOB_SPECIES_CYCLE = (
    "slime",
    "skeleton",
    "archer",
    "swordsman",
    "skeleton-archer",
    "armored-orc",
)
BOSS_SPECIES_CYCLE = (
    "werebear",
    "knight-templar",
    "elite-orc",
    "werewolf",
    "wizard",
    "priest",
)

# Default adventure encounter size cap. Total roster HP equals the variant's
# rule count (battle.state._target_hp), spread across at most this many mobs, so
# clean play chips everything down as the repo nears target and the solving
# command lands the finishing blow.
MAX_DEFAULT_MONSTERS = 3

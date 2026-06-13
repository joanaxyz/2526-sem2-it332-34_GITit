from assets.seed_data.monsters import MONSTER_SPECS
from curriculum.management.commands.seed_curriculum_v2 import battle_asset_slug_errors


def test_current_curriculum_battle_asset_slugs_are_seeded():
    seeded = {spec["slug"] for spec in MONSTER_SPECS}

    assert battle_asset_slug_errors(seeded) == []


def test_battle_asset_slug_validation_reports_missing_authored_slugs():
    errors = battle_asset_slug_errors(set())

    assert errors
    assert any("unknown monster asset slug" in error for error in errors)

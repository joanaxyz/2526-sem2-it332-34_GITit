from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEED_DATA = ROOT / "backend" / "curriculum" / "seed_data"


PARTITION_PACKAGES = {
    "adventure_levels": "adventure_level_specs",
    "challenges": "challenge_specs",
    "blueprint_overlay": "blueprint",
}


def test_large_authored_seed_data_lives_under_partitioned_source_packages():
    for module_name, package_name in PARTITION_PACKAGES.items():
        public_module = SEED_DATA / f"{module_name}.py"
        source_module = SEED_DATA / "source" / f"{module_name}.py"
        partition = SEED_DATA / "source" / package_name
        assert public_module.exists()
        assert source_module.exists()
        assert partition.exists()
        assert (partition / "__init__.py").exists()
        assert len(public_module.read_text().splitlines()) <= 50
        assert len(source_module.read_text().splitlines()) <= 50
        assert "curriculum.seed_data.source" in public_module.read_text()


def test_migration_files_are_committed_as_schema_history():
    migration_files = sorted(
        path
        for path in (ROOT / "backend").glob("*/migrations/*.py")
        if path.name != "__init__.py"
    )
    assert migration_files, "Model changes must ship with committed migrations."
    assert all(path.stem[:4].isdigit() for path in migration_files)

    test_settings = (ROOT / "backend" / "config" / "test_settings.py").read_text()
    assert "MIGRATION_MODULES" not in test_settings

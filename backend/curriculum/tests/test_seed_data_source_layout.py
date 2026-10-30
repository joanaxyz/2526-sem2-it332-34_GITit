from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_migration_files_are_committed_as_schema_history():
    migration_files = sorted(
        path for path in (ROOT / "backend").glob("*/migrations/*.py") if path.name != "__init__.py"
    )
    assert migration_files, "Model changes must ship with committed migrations."
    assert all(path.stem[:4].isdigit() for path in migration_files)

    test_settings = (ROOT / "backend" / "config" / "test_settings.py").read_text()
    assert "MIGRATION_MODULES" not in test_settings

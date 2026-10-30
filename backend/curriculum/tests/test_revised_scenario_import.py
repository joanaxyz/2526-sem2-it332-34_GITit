from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
IMPORTER = REPO_ROOT / "scripts" / "curriculum" / "import_revised_scenarios.py"


def _importer_module():
    spec = importlib.util.spec_from_file_location("import_revised_scenarios", IMPORTER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_importer_preserves_commands_file_edits_and_budgets():
    module = _importer_module()
    document = """
### 3.1.1 Resolve the file · Easy

**Variant ID:** `manual-one`

**Story**
A story.

**Starting point:** A merge is stopped.

**Real-World Context**
Conflicts need decisions.

**Your Task**
Resolve the file.

**Required resolved file content**

`src/app.py`

```
VALUE = 1
```

**Objective Checklist**

- [ ] The file is exact.
- [ ] The merge is complete.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git merge feature/app` — Begin.
2. In the simulator's file editor, set `src/app.py` to exactly: Resolve it.

   ```
   VALUE = 1
   ```
3. `git add src/app.py` — Stage it.
4. `git commit --no-edit` — Finish.

**Accepted Alternatives (STAFF ONLY)**

- Any route with the same end state.

**Expected Result**
The merge is complete.

**Evaluation (STAFF ONLY)**

- Clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12 (proposed)
"""

    parsed = module.parse_document(document, enforce_bank_counts=False)["manual-one"]

    assert parsed["starting_point"] == "A merge is stopped."
    assert parsed["objective_checks"] == ["The file is exact.", "The merge is complete."]
    assert parsed["solution_commands"] == [
        "git merge feature/app",
        "git add src/app.py",
        "git commit --no-edit",
    ]
    assert parsed["solution_workspace_files"] == [
        {
            "mode": "write",
            "path": "src/app.py",
            "content": "VALUE = 1",
            "after_command_index": 1,
        }
    ]
    assert (parsed["minimum_counted_commands"], parsed["maximum_counted_commands"]) == (3, 12)


def test_importer_rejects_an_unsupported_answer_step():
    module = _importer_module()
    document = """
### 1.1.1 Broken · Easy
**Variant ID:** `broken`
**Story** A
**Starting point:** B
**Real-World Context** C
**Your Task** D
**Objective Checklist**
- [ ] E
**Answer Key (STAFF ONLY)**
1. Click a mystery button.
**Accepted Alternatives (STAFF ONLY)**
- None.
**Expected Result** F
**Evaluation (STAFF ONLY)**
- Minimum counted commands: 1 · Maximum counted commands: 12 (proposed)
"""

    with pytest.raises(module.ImportError, match="Unsupported Answer Key step"):
        module.parse_document(document, enforce_bank_counts=False)


def test_importer_rejects_required_file_content_that_differs_from_the_answer_key():
    module = _importer_module()
    document = """
### 3.1.1 Broken file · Easy
**Variant ID:** `broken-file`
**Story** A
**Starting point:** B
**Real-World Context** C
**Your Task** D
**Required resolved file content**
`src/app.py`
```
EXPECTED = 1
```
**Objective Checklist**
- [ ] E
**Answer Key (STAFF ONLY)**
1. In the simulator's file editor, set `src/app.py` to exactly:
   ```
   DIFFERENT = 2
   ```
2. `git add src/app.py`
**Accepted Alternatives (STAFF ONLY)**
- None.
**Expected Result** F
**Evaluation (STAFF ONLY)**
- Minimum counted commands: 1 · Maximum counted commands: 12 (proposed)
"""

    with pytest.raises(module.ImportError, match="different required-file"):
        module.parse_document(document, enforce_bank_counts=False)


_EXTENSION_SCENARIO = """
### {number} {title} · Easy

**Variant ID:** `{variant}`

**Story**
A story.

**Starting point:** A start.

**Real-World Context**
Context.

**Your Task**
Do it.

**Objective Checklist**

- [ ] Done.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git status` — Look.

**Accepted Alternatives (STAFF ONLY)**

- None.

**Expected Result**
Done.

**Evaluation (STAFF ONLY)**

Minimum counted commands: 1 · Maximum counted commands: 12

- First check.
- Last check.
"""


def _write_bank(tmp_path, scenarios: dict) -> object:
    import json

    bank = tmp_path / "bank.json"
    bank.write_text(json.dumps(scenarios), encoding="utf-8")
    return bank


def test_extension_mode_ends_scenarios_at_module_headings_and_accepts_gate_numbers(tmp_path):
    module = _importer_module()
    source = tmp_path / "scenarios.md"
    source.write_text(
        "# Scenarios\n\n## Module 1\n"
        + _EXTENSION_SCENARIO.format(number="1.1.12", title="One", variant="scenario-one")
        + "\n## Module 2\n"
        + _EXTENSION_SCENARIO.format(number="2.G.1", title="Gate", variant="gate-one"),
        encoding="utf-8",
    )

    import json

    rendered = json.loads(
        module.render_document(source, extension=True, bank_path=_write_bank(tmp_path, {}))
    )

    assert list(rendered) == ["scenario-one", "gate-one"]
    assert rendered["scenario-one"]["evaluation"] == ["First check.", "Last check."]
    assert rendered["gate-one"]["scenario_number"] == "2.G.1"


def test_extension_mode_rejects_ids_or_numbers_already_in_the_bank(tmp_path):
    module = _importer_module()
    source = tmp_path / "scenarios.md"
    source.write_text(
        _EXTENSION_SCENARIO.format(number="1.1.12", title="One", variant="taken"),
        encoding="utf-8",
    )

    with pytest.raises(module.ImportError, match="already exist in the bank"):
        module.render_document(
            source,
            extension=True,
            bank_path=_write_bank(tmp_path, {"taken": {"scenario_number": "9.9.9"}}),
        )
    with pytest.raises(module.ImportError, match="numbers already used"):
        module.render_document(
            source,
            extension=True,
            bank_path=_write_bank(tmp_path, {"other": {"scenario_number": "1.1.12"}}),
        )


def test_committed_scenario_bank_is_current_with_its_markdown():
    module = _importer_module()
    source = REPO_ROOT / "backend/curriculum/seed_data/source/extension_scenarios.md"
    compiled = REPO_ROOT / "backend/curriculum/seed_data/scenario_bank_extension.json"

    assert module.render_document(source, extension=True) == compiled.read_text(encoding="utf-8")


def test_importer_keeps_formatted_prose_paragraphs():
    module = _importer_module()
    document = """
### 1.1.1 Format the story · Easy

**Variant ID:** `formatted-one`

**Story**
Raven left `ci-configs` for you.

**“Ship it before the meeting.”**

You *almost* believe her.

**Starting point:** You are in `ci-configs`.

**Real-World Context**
Boundaries __matter__.

**Your Task**
Initialize `ci-configs`. **Leave everything else alone.**

**Objective Checklist**

- [ ] ci-configs is a repository.

**Answer Key (STAFF ONLY, never shown to students)**

1. `git init ci-configs` — Initialize it.

**Accepted Alternatives (STAFF ONLY)**

- None.

**Expected Result**
Only `ci-configs` is a repository.

**Evaluation (STAFF ONLY)**

- Minimum counted commands: 1 · Maximum counted commands: 4
"""

    parsed = module.parse_document(document, enforce_bank_counts=False)["formatted-one"]

    assert parsed["story"] == (
        "Raven left `ci-configs` for you.\n\n"
        "**“Ship it before the meeting.”**\n\n"
        "You *almost* believe her."
    )
    assert parsed["real_world_context"] == "Boundaries __matter__."
    assert parsed["task"] == "Initialize `ci-configs`. **Leave everything else alone.**"

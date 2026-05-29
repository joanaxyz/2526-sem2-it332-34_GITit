# Curriculum Redesign — Source of Truth

This folder is the authoritative reference for all GIT it! scenario redesign work.
It governs what gets built, not what is currently seeded.

## Workflow

```
Design (this folder) → Review & Approval → Seed Implementation → Migration
```

**Do not modify seed files until the corresponding guide in this folder is approved.**

## Contents

| File | Status | Description |
|------|--------|-------------|
| [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) | Approved | Global standards for all scenario design |
| [MODULE_1_GUIDE.md](MODULE_1_GUIDE.md) | **Implemented** ✅ | Full scenario library for Module 1; reference implementation |
| [MODULE_1_ANSWERKEY.md](MODULE_1_ANSWERKEY.md) | **Live** ✅ | Instructor answer key — all Module 1 cases, contexts, solutions |
| [MODULE_2_GUIDE.md](MODULE_2_GUIDE.md) | Approved — pool expansion pending | Full scenario library for Module 2 (36 new variants designed) |
| [MODULE_3_GUIDE.md](MODULE_3_GUIDE.md) | Approved — pool expansion pending | Full scenario library for Module 3 (new variants designed) |
| [MODULE_4_GUIDE.md](MODULE_4_GUIDE.md) | Approved — seed fixes pending | Full scenario library for Module 4 (seed bugs documented) |

## Relationship to Existing Docs

The `docs/` folder contains legacy curriculum documents
(`curriculum-module1.md`, `module-1_scenario_blueprint.md`, etc.).
Those describe what was designed at various earlier stages.
This `curriculum-redesign/` subfolder supersedes them for implementation decisions.

## Platform Context

- **Product:** GIT it! — scenario-driven Git learning platform
- **Target audience:** BSIT 3rd-year students at CIT-U with prior basic Git exposure
- **Stack:** React + Django + PostgreSQL
- **Scenario evaluation:** State-Based Evaluator — checks final repository state, not command sequence
- **Command budget:** Global limits from `DIFFICULTY_MAX_COUNTED_COMMANDS` (easy=12, medium=10, hard=8)
- **Completion requirements:** Set per-lesson in seed via `SESSION_COUNTS` (typically easy=3, medium=2, hard=2)
- **Minimum pool rule:** Variants per difficulty ≥ completion requirement + 2

## Context String Pattern (`{{context}}` placeholder)

All modules use the `{{context}}` placeholder pattern established in Module 1.
See **Module 1 Guide → Seed Implementation Notes → Context string pattern** for the
full reference implementation.

**In brief:** `student_context_template` returns `"story": "{{context}}"`. Every case
dict passes a `context=` string containing the narrative paragraph from the guide.
The materializer substitutes it into the Scenario Brief at render time.

**Modules 2, 3, 4 seeds need this migration** — their templates currently return static
strings. Each module's guide has a "Context string requirement" checklist in its Seed
Implementation Notes section.

## Key Constraint: `git config` is Prior Knowledge

Module 1 does NOT introduce `git config`. Students are third-year with prior Git exposure.
The Module 0 Orientation Completion Gate covers fundamentals.
`git config` is documented as a prior-knowledge assumption, not a curriculum gap.

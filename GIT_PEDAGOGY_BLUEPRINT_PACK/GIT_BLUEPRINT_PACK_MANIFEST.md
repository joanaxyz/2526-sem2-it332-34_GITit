<!--
GIT it! curriculum blueprint rebuilt from:
- CONTENT_AUTHORING_GUIDE.md
- CURRICULUM_AUTHORING_PLAN.md
- PRODUCT.md / DESIGN.md pedagogy

Authoring lens used here:
- Do not modularize by documentation chapter alone.
- Chapter = command-suite growth for a practical repository-state capability.
- Command Adventure = checklist-scaffolded fluency practice.
- Challenge = cumulative mastery proof through target DAG/state mutation.
- Ignore current command-engine gaps while authoring the ideal curriculum.
-->
# Git Blueprint Pack Manifest

This pack rebuilds the blueprints around the authoring guide and product pedagogy. It intentionally ignores current command-engine gaps. The blueprints define the ideal content target.

## Pack contents

- `CH1_BLUEPRINT.md`
- `CH2_BLUEPRINT.md`
- `CH3_BLUEPRINT.md`
- `CH4_BLUEPRINT.md`
- `CH5_BLUEPRINT.md`
- `CH6_BLUEPRINT.md`
- `CH7_BLUEPRINT.md`
- `GIT_CURRICULUM_CHAPTER_OUTLINE.md`

## Non-negotiable authoring laws

1. Plain chapter names. No cryptic fantasy chapter titles inside blueprint filenames or chapter headings.
2. Adventures teach with objective checklists only.
3. Challenges assess with DAG/state targets and no checklist.
4. Every command form gets a dedicated SOLO intro wave (single-command solution, no extra forms) that appears strictly BEFORE any other wave uses that form, in seeded curriculum order.
5. Every command form recurs across at least 6 distinct adventure waves; the core everyday suite (status/add/commit/log/branch/switch/merge/push/pull families) recurs across at least 10. Challenge trials do not count toward these floors - mastery is credited from adventure waves only.
6. Every challenge trial mutates repository graph/refs/state.
7. Hard challenges use near-full current suite plus prior forms.
8. Engine gaps are implementation work, not a reason to weaken content.

Laws 4-5 are machine-enforced by `backend/curriculum/tests/test_blueprint_pedagogy_invariants.py`. Mastery is per-wave: a form's mastery bar counts the distinct published waves that exercise it (capped at 8, `MASTERY_TARGET_CAP`), and clearing a level credits one solve per wave that used the form.

## Canonical ledger

`backend/curriculum/seed_data/blueprint_overlay.py` is the single authoritative content ledger (362 waves across 67 levels as of the 2026-07 intro-first restructure). The per-level wave tables inside `CH1_BLUEPRINT.md`-`CH7_BLUEPRINT.md` describe the original 107-wave pass and are historical context only; when they disagree with the overlay, the overlay wins.

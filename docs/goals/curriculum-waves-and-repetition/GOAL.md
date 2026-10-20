# Goal: Curriculum Waves and Repetition

Use Krypton Execution to execute `docs/goals/curriculum-waves-and-repetition/PLAN.md`.

Core rules:
- Treat PLAN.md as the source plan and WAVE_MAP.md as the placement contract. `wave-map.json` is the same data, machine-readable; it is an execution input, not a runtime source. `blueprint/` is the readable, per-module version of the same curriculum.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- The 21 levels, their slugs and order, and the command each teaches are fixed by the team. Change waves, variants, and tier placement only.
- Keep the full 132-wave plan and its time budget (PLAN.md §3–§4): about 4.9 hours on the no-fail path, which the team accepted. Re-measure before adding waves.
- Decisions D1–D5 are recorded in PLAN.md §12 (D5 = register the 11 forms). D6–D8 are still open; confirm them before the tasks that depend on them.
- Claude writes the 84 new scenarios (D4) and the 24 Challenge Gate scenarios (D11).
- Execution order: Tasks 0–3 → Task G (gates, §14) → Task L (legacy removal, §15) → Task 4 → Tasks 5–8 → Tasks 9–10.
- Never apply Task L's drop migrations to the shared dev database without asking the user.
- Run Task 0 (simulator spike) before writing any scenario it flags.
- Do not add a new dominant path without deleting, redirecting, demoting, or shimming the displaced path. The transitional single-wave seed branch dies in Task 8.
- Never hand-edit generated targets, trajectories, or API types. Regenerate them.
- Do not add a "Co-Authored-By: Claude" trailer to commits.
- Capture acceptance evidence from the target perspective: a disposable fresh account and a veteran account in the running app.
- Say "implemented but unproven" if that evidence cannot be captured.

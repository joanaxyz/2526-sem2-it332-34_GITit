# Goal: Learner Progress KPI Instrument

Use Krypton Execution to execute `docs/goals/learner-progress-kpi-instrument/PLAN.md`.

Core rules:
- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep `MetricsService._performance_summary_for_runs()` and `GET /api/progress/performance/` as the unchanged value and response owners; do not calculate KPIs in the frontend.
- Preserve all pre-existing dirty work, especially the current mastery/profile changes, using the plan's baseline and final hash audit.
- Make the learner surface visually rich through meaningful state light, target traces, and earned glow, with no generic card grid, decorative noise, or missing reduced-motion behavior.
- Do not add a new dominant path without deleting, redirecting, demoting, or shimming the displaced path.
- Capture acceptance evidence from the learner perspective and Admin parity evidence.
- Say "implemented but unproven" if the required browser, network, accessibility, or parity evidence cannot be captured.

# Goal: Overview and Admin Performance Consolidation

Use Krypton Execution to execute `docs/goals/overview-performance-consolidation/PLAN.md`.

Core rules:

- Treat `PLAN.md` as the source plan and preserve its intent, truth owner, contract boundary, cutover, displaced path, evidence lane, and kill criteria.
- Replace the pictured static CTA and the mixed-scope Overview KPI strip with one learner-focused performance lens at the top of Home > Overview.
- Keep KPI formulas in `MetricsService`; preserve the existing player response and reuse the exact aggregation path for a new staff-only global summary in Admin analytics.
- Offer exactly SCR and HLCR to learners through a two-option segmented control. Move CAR (labeled accurately as command processability), RTR, and ARC into Admin > Analytics; never fabricate module CAR.
- Improve the Admin shell and Analytics CSS with restrained, responsive, accessible product styling rather than repeated decorative cards.
- Remove Performance from both desktop and mobile global navigation, redirect `/performance` to the Overview lens, and delete the displaced page/styles in the same cutover.
- Re-anchor the Home onboarding tour before deleting `overview-next`; preserve the existing companion-acquisition path.
- Preserve mastery, activity, story progress, achievements, Loadout, Profile, Modules, and unrelated dirty work.
- Capture target-perspective learner and staff browser evidence, keyboard/URL/request traces, permission proof, responsive/empty states, and redirect evidence. If that evidence cannot be captured, report the result as implemented but unproven.

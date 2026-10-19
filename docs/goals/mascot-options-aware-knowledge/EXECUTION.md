# Execution Record: Options-Aware Contextual Mascot Knowledge

**Status:** Implementation, acceptance evidence, and review gates complete.
**Plan:** [PLAN.md](./PLAN.md)
**Goal:** [GOAL.md](./GOAL.md)

## Execution contract

- Use the first unlocked, unpassed level as the tip focus; this does not change progression.
- Source command syntax and cues from level-attached forms, and option/argument meaning from the Chapter Book library pages.
- Return compact knowledge through the existing chapter overview and replace summary-only current-level tips.
- Keep cleared levels cycleable, preserve earned skills as history, and leave first-encounter teaching unchanged.
- Order cleared levels by `completion.completed_at`, with `passed_at` as a fallback for legacy passed runs, and order earned skills by their latest `learned_at` time.
- Append an evergreen command-anatomy tip after contextual and earned guidance, and include it in the introductory cycle.
- Do not add a second catalog, a mascot-only endpoint, a full book fetch, or tip persistence.
- Preserve unrelated in-progress worktree edits, including reward/map changes and `WorldMascot.tsx` appearance work.

## Ordered task board

| Task | Status | Owner | Output and evidence |
|---|---|---|---|
| 1. Build the compact curriculum projection | Complete | Main agent | Batched form/page projection with deterministic option/argument matching. Captured chapter 1 and progressed chapter overview responses under `evidence/`. |
| 2. Define the read contract and learner-facing cycle | Complete | Main agent | Typed current-level tips, cleared-level history, earned history, context reset, compact accessible bubble, and evergreen command anatomy tip. Repeated command summaries are deduplicated while form-specific option and argument tips remain distinct. Captured current, past, anatomy, and reset states in the browser. |
| 3. Capture end-to-end acceptance evidence and retire the interim path | Complete | Main agent | Saved request/response and browser evidence under `evidence/`; confirmed current map guidance uses the structured overview contract and the shared mascot bubble renderer. |

## Acceptance evidence

Captured against the local API and story map. `chapter-1-overview.json` shows the unpassed Start a Repository level with `git init -b <branch>` and the authored `-b / --initial-branch` meaning and cue. `git-config-placeholder-mapping.json` confirms `git config --global user.name <name>` maps `<name>` to the Chapter Book's `<value>` explanation, while `alias.<name>` maps to `<key>`. `progress-overview.json` shows focus changing to unpassed Stage and Commit after levels 1 and 2 were cleared in an isolated database copy; its focus knowledge includes `git commit -m <message>` and `-m / --message`. `earned-skills-unearned-tip.json` records a 200 response with no earned skills for that same test account, confirming the current-level tip is available before mastery. `progress-overview-out-of-order.json` and its browser capture show Start a Repository ahead of the earlier map level Read the Workspace because its completion timestamp is newer. `progress-overview-all-cleared.json` and `all-cleared-fallback.png` show the most recently cleared Read the Workspace level leading when all 17 levels are passed. `progress-overview-passed-at-fallback.json` records a legacy passed level with `completion: null`; its newer run `passed_at` makes Start a Repository lead, as confirmed by `passed-at-fallback.png`. Browser captures also show the context reset to the new level's first `git status` tip and the evergreen anatomy tip on desktop/mobile. The browser cycle displayed only Stage and Commit, Read the Workspace, Start a Repository, then command anatomy; 14 other unpassed levels were omitted. The reward panel in the current-level screenshot shows milestone percentages without “Locked” labels.

Evidence files:

- API: [chapter-1-overview.json](./evidence/chapter-1-overview.json), [git-config-placeholder-mapping.json](./evidence/git-config-placeholder-mapping.json), [progress-overview.json](./evidence/progress-overview.json), [earned-skills-unearned-tip.json](./evidence/earned-skills-unearned-tip.json), [progress-overview-out-of-order.json](./evidence/progress-overview-out-of-order.json), [progress-overview-all-cleared.json](./evidence/progress-overview-all-cleared.json), [progress-overview-passed-at-fallback.json](./evidence/progress-overview-passed-at-fallback.json)
- Browser: [current-option-desktop.png](./evidence/current-option-desktop.png), [current-option-mobile.png](./evidence/current-option-mobile.png), [current-level-option-progress.png](./evidence/current-level-option-progress.png), [past-cleared-option.png](./evidence/past-cleared-option.png), [out-of-order-cleared-levels.png](./evidence/out-of-order-cleared-levels.png), [all-cleared-fallback.png](./evidence/all-cleared-fallback.png), [passed-at-fallback.png](./evidence/passed-at-fallback.png), [context-reset-first-tip-mobile.png](./evidence/context-reset-first-tip-mobile.png), [command-anatomy.png](./evidence/command-anatomy.png), [command-anatomy-mobile.png](./evidence/command-anatomy-mobile.png)
- Interaction sequence and environment: [browser-cycle-notes.md](./evidence/browser-cycle-notes.md)

## Reviews

- PRE plan review: aligned; the remaining wording note was corrected in PLAN.md.
- POST plan review: aligned; no remaining contract or acceptance findings.
- Correctness review: no actionable findings.
- Maintainability review: no actionable findings.
- Target-perspective verifier: pass; the earned-skills response now explicitly proves the displayed current-level guidance is unearned.


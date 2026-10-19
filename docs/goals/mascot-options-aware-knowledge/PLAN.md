# Options-Aware Contextual Mascot Knowledge Implementation Plan

**Intent:** Make the map mascot give concise, useful guidance about the commands, options, and arguments relevant to the learner's current level, regardless of mastery, while preserving a route back through cleared material.
**Current Behavior:** The mascot uses earned `CommandSkill.summary` entries as its main knowledge source. The in-progress level projection adds only those same short summaries; it omits the authored usage forms and the option/argument explanations already present in the Chapter Book.
**Expected Outcome:** The first unlocked, unpassed level in map order leads the tip cycle with its relevant command forms, options, and arguments. Where levels are not gated, this is simply the first unpassed level; this focus does not change level access or progression. When no unlocked, unpassed level remains, the most recently cleared level leads. Other cleared-level knowledge and earlier earned knowledge follow in reverse recency order. An evergreen command-anatomy tip follows contextual and earned guidance and also appears in the introductory cycle. Other unpassed levels never enter the tip cycle, even when they are open; locked future levels do not leak into the tips.
**Target-Perspective Output:** A learner can open the mascot on the story map before mastering the current level's forms, see a concrete form such as `git init -b <branch>`, the Chapter Book meaning of `-b / --initial-branch`, and the matched form's authored “when to use” cue, then cycle through the other current-level options and earlier cleared-level guidance.
**Truth Owner:** Curriculum authoring owns command forms (`CommandForm.usage_form`, `label`, and `summary`) and option/argument meaning (`LibraryEntry.pages`, surfaced by the Chapter Book). The chapter overview owns level order and pass/lock state. Mastery remains a source of historical knowledge only.
**Contract Boundary:** The existing `GET /chapters/{chapterId}/overview/` response carries compact, structured knowledge items on each adventure level: stable id, kind (`command`, `option`, or `argument`), title/token, exact attached form syntax, concise authored explanation, and the form-specific authored cue. Option and argument pages are included only when their token matches a form attached to that level. The frontend orders those items from existing level state and renders them in the existing mascot bubble.
**Cutover:** Replace the interim summary-only per-level `knowledge` projection with the structured option-aware contract. Promote current-level authored guidance ahead of earned skills; retain the earned-skills path only as older reference material. No extra Chapter Book fetch is added to the map.
**Displaced Path:** `CommandSkill.summary` alone as the level tip; earned-skill filtering as the selector for what the mascot teaches now; any parallel mascot-only option catalog or persistent tip state.
**Value Density:** Reuse authored command and option content already present in curriculum data, return only compact level-relevant fields, and keep cycling stateless and local to the mascot.
**Acceptance Evidence:** Capture the chapter-overview response and browser state showing an unearned current-level option tip, its full syntax and meaning, a second distinct option/argument tip, navigation into cleared-level tips, the evergreen command-anatomy tip, and a context reset when the next playable level changes. Confirm no locked future-level tip appears.
**Evidence Lane:** API response plus target-perspective browser capture on the story map.
**Kill Criteria:** Do not ship a second option/argument authoring source, a mascot-only knowledge endpoint, or a full Chapter Book download on every map visit. Do not leave the summary-only field as a parallel path after the structured contract lands. If compact projection cannot reuse the Chapter Book's authored page content without N+1 reads, stop and revise the projection before widening the payload.
**Architecture Slice:** Backend curriculum selectors project compact per-level content from the existing command forms and Chapter Book option/argument pages. The story-map overview remains the sole read path for level context. Frontend skill utilities order current-level, cleared-level, and earned-history entries; the shared mascot bubble renders their type, syntax, and explanation. No persistence, mastery, or first-encounter teaching contract changes.
**Plan Review Gate:** Requires PRE review before execution.

## Outcome Contract

The mascot is a read-only, optional reference. It must answer “what should I understand for the level I'm looking at?” before the learner has earned that command. It must also let the learner revisit completed material without turning the mascot into a second tutorial or progression gate.

## Architecture Slice

**Files to create:**

- `docs/goals/mascot-options-aware-knowledge/PLAN.md`
- `docs/goals/mascot-options-aware-knowledge/GOAL.md`

`EXECUTION.md` and acceptance evidence are added during execution, after the plan gate.

**Files to modify during execution:**

- `backend/curriculum/selectors/book.py` — project option/argument teaching from the same authored pages used by the Chapter Book.
- `backend/curriculum/library_commands.py` — add the explicit argument placeholder identity map beside the existing command-to-section map.
- `backend/curriculum/selectors/content.py` — batch the compact content projection for the chapter overview so level assembly does not issue per-level or per-command reads.
- `backend/curriculum/selectors/access_helpers.py` and `backend/curriculum/selectors/adventure_access.py` — replace the interim summary-only field with the structured level knowledge contract.
- `backend/curriculum/selectors/command_skills.py` and `backend/common/openapi.py` — expose the latest authored skill-learning timestamp so earned historical tips follow actual recency.
- `backend/curriculum/management/commands/seed_curriculum.py` and `backend/curriculum/seed_data/command_catalog.py` — refine canonical form labels only if the cue audit finds a gap.
- `frontend/src/features/story-map/types.ts` — define the overview knowledge item contract.
- `frontend/src/features/story-map/pages/StoryMapPage.tsx` and `frontend/src/features/story-map/utils/storyMapChapter.ts` — use the next playable level as the current focus, fall back to the most recently cleared level after the final clear, and reset mascot context when the effective focus changes.
- `frontend/src/features/skills/types.ts`, `frontend/src/features/skills/utils/mascotKnowledge.ts`, and `frontend/src/features/skills/hooks/useMascotKnowledge.ts` — order current-level items first, then cleared levels by `completion.completed_at` newest-first, then earned history by `learned_at` newest-first; deduplicate overlapping command summaries.
- `frontend/src/shared/api/generated/openapi.json` and `frontend/src/shared/api/generated/apiTypes.ts` — regenerate the learned-skill timestamp contract.
- `frontend/src/shared/mascot/mascotKnowledge.ts`, `frontend/src/shared/mascot/MascotKnowledgeBubble.tsx`, and `frontend/src/shared/mascot/knowledge-bubble.css` — support typed command, option, and argument tips with visible syntax and compact explanation.

**Files to avoid:**

- `backend/tutoring/**` and `frontend/src/features/story-map/scaffolding/**` — first-encounter teaching owns in-run instruction, persistence, and feedback. This plan only adds optional read-only map knowledge.
- `backend/curriculum/library_data.py` and `backend/curriculum/library_education.py` — keep option/argument explanations sourced from the Chapter Book; do not duplicate or rewrite them for the mascot.
- `frontend/src/features/story-map/components/book/**` — the Chapter Book stays the reference reader; the mascot uses a compact projection and does not replace its navigation or content.
- `frontend/src/shared/mascot/WorldMascot.tsx` unless execution proves a change is required. It has unrelated in-progress appearance edits in the shared worktree; preserve them.

**Source of truth:** `CommandForm` usage forms attached to each level, `CommandSkill` summaries, and `LibraryEntry.pages` option/argument sections. `AdventureLevel` ordering and `is_passed` / `locked` state determine current-level selection; completion timestamps order the cleared history and choose the all-cleared fallback. `SkillMastery.learned_at` orders already-earned history but must not gate current-level guidance.

**Read path:** `chapter_content_overview` loads the chapter's adventure levels and their forms. A batched selector resolves each distinct command's Chapter Book pages and projects only option/argument items whose token appears in a form attached to that level. The existing overview API returns that compact projection. `StoryMapPage` selects the first unlocked, unpassed level in map order; when levels are ungated, this is the first unpassed level. If none remains, it selects the most recently cleared level by `completion.completed_at`, falling back to `passed_at` for passed runs without a completion row. `knowledgeForMascot` places that focus first, appends other cleared levels by completion timestamp newest-first, then appends non-duplicate earned history by `learned_at` newest-first. Other unpassed levels are omitted whether currently locked or open. The effective focus level is part of the bubble context key so a changed focus resets the cycle. The bubble displays the selected item.

**Write path:** None. Tips do not mutate mastery, first-encounter records, progression, or local storage.

**Contract boundary:** `AdventureSummary.knowledge[]` is a compact read-model contract. Each item includes a stable curriculum-derived identity, a kind, a human-readable token/title, the matching form syntax, and a short explanation. For options and arguments, the source is the corresponding Chapter Book page and it is included only if its token appears in a form attached to the level. It does not expose full page blocks, quizzes, diagrams, or unrelated commands.

**Deterministic matching rule:** Join each attached form to the single `LibraryEntry` for its command. Split an option page's token on `/` into short/long aliases and match each alias as a whole option token in `usage_form`; allow `=` or whitespace after the alias so both `--depth=<count>` and `--depth <count>` match, and never use substring matches. For an argument page, extract `<placeholder>` tokens from the form (including placeholders inside optional brackets, variadic forms, or prefixed tokens such as `HEAD~<n>`), then match the page token exactly or use this explicit command-scoped alias map: `argument-path` accepts `<file>`/`<path>`; `argument-directory` accepts `<folder>`/`<directory>`; `argument-number` accepts `<n>`/`<count>`/`<number>`; `argument-value` accepts `<value>`/`<name>`/`<email>`/`<command>`; and `argument-key` accepts `<key>`. For `git config`, `<name>` inside the literal `alias.<name>` belongs to `argument-key`; `<name>` used as the value of `user.name` belongs to `argument-value`. Keep this identity map in `library_commands.py`, beside the existing command-to-section map; include the existing `argument-number` page for `git log` so `-n <count>` has an explanation. This maps labels and does not duplicate explanations. Emit one entry per matched page/form pair with that form's exact syntax and summary. If duplicate page tokens still make a match ambiguous within one library entry, omit the ambiguous entries and record the content issue in `EXECUTION.md`; do not guess. Unmatched pages stay in the Chapter Book but do not appear as level tips.

**Cue rule:** The bubble pairs the option/argument page's authored explanation with its matched form's `CommandForm.label` and `summary` as the “Use this when” cue. The seed currently stores the form label as its summary. During execution, audit forms linked to current-level option/argument tips for a useful cue. If a label/summary is missing or too vague, refine that canonical form label in `MODULE_COMMAND_FORMS` or `COMMAND_CATALOG`; do not add a mascot-only copy.

**Cutover and displaced path:** Replace the current summary-only `knowledge` entries in the uncommitted worktree. Preserve `learned-skills` for historical tips, but stop using it as the current map's teaching source. Do not fetch `/chapters/{id}/book/` solely to populate the mascot.

**Acceptance evidence gate:** Before calling the goal complete, capture the real chapter overview response and a learner-facing browser capture. The response must identify exact current-level forms and matching authored options/arguments. The browser must show an unearned option tip with its full matching syntax, Chapter Book meaning, and matched form's “when to use” cue; “Another tip” must cycle through distinct current-level items and then cleared history ordered by completion time; out-of-order clears must retain their recency order; when all levels are cleared, the most recently cleared level must lead; changing effective focus must reset the first tip; all other unpassed levels' material must stay absent, whether those levels are locked or open.

## Ordered Tasks

### 1. Build the compact curriculum projection

- **Files allowed:** `backend/curriculum/selectors/book.py`, `backend/curriculum/selectors/content.py`, `backend/curriculum/selectors/access_helpers.py`, `backend/curriculum/selectors/adventure_access.py`, `backend/curriculum/selectors/command_skills.py`, `backend/common/openapi.py`, `backend/curriculum/library_commands.py`, `backend/curriculum/management/commands/seed_curriculum.py`, `backend/curriculum/seed_data/command_catalog.py`, `frontend/src/shared/api/generated/openapi.json`, `frontend/src/shared/api/generated/apiTypes.ts`.
- **Output:** A batched projection of command summaries, level-attached forms, and matching authored option/argument explanations. Each level returns only the compact entries it can actually teach; reference-only or unrelated future forms are excluded. Earned-skill responses include `learned_at` so historical knowledge follows actual recency.
- **Matching details:** Apply the deterministic alias and placeholder rules above. Matching one authored page against multiple attached forms yields one form-specific tip per match, so each tip keeps its own syntax and scenario cue. Ambiguous page matches are omitted and recorded for resolution rather than selected arbitrarily.
- **Cue details:** Audit form labels/summaries and refine only canonical labels that fail to communicate when to use the syntax.
- **Verification command:** Generate the API contract, start the local API and request `GET /api/chapters/<active-chapter-id>/overview/`; inspect that the focus level contains its forms and option/argument entries and that other unpassed levels are not selected by frontend ordering.
- **Acceptance evidence:** Save response excerpts proving `git init -b <branch>` matches `-b / --initial-branch`, `git add <file>` matches `<path>`, `git clone --depth <n>` and `git log -n <count>` match `<number>`, and `git config` routes `alias.<name>` to `<key>` while the `user.name` value maps to `<value>`. Include the exact syntax, explanation, and form-specific cue.
- **Depends on:** None.
- **Parallel safe:** No; the overview's batching and per-level mapping must be designed together.

### 2. Define the read contract and learner-facing cycle

- **Files allowed:** `frontend/src/features/story-map/types.ts`, `frontend/src/features/story-map/utils/storyMapChapter.ts`, `frontend/src/features/story-map/pages/StoryMapPage.tsx`, `frontend/src/features/skills/types.ts`, `frontend/src/features/skills/utils/mascotKnowledge.ts`, `frontend/src/features/skills/hooks/useMascotKnowledge.ts`, `frontend/src/shared/mascot/mascotKnowledge.ts`, `frontend/src/shared/mascot/MascotKnowledgeBubble.tsx`, `frontend/src/shared/mascot/knowledge-bubble.css`.
- **Output:** Typed tips render the option/argument label, exact syntax, concise authored meaning, form-specific “Use this when” cue, and level context. The next playable level comes first; cleared levels follow timestamp recency; when no next playable level remains, the most recently cleared level leads; earlier earned tips follow their `learned_at` timestamp; one evergreen command-anatomy tip comes last and is also included in the introductory cycle. Context changes close/reset the tip. The uncommitted guide-appearance edits in `WorldMascot.tsx` remain untouched.
- **Cue display:** Render the matched form's label/summary as the “Use this when” cue alongside the page meaning; if the summary is empty, the canonical curriculum summary gap must be filled during Task 1 before this task can pass acceptance.
- **Verification command:** Run the local frontend and inspect the story map in a browser at desktop and narrow viewport widths; use keyboard focus and “Another tip” to cycle through current and past content.
- **Acceptance evidence:** Capture a bubble showing an unearned current-level option with its syntax, meaning, and “Use this when” cue, another showing a prior-level option or argument, and the evergreen command-anatomy tip; verify out-of-order cleared history, the most-recently-cleared fallback, and the selected tip changing when advancing focus.
- **Depends on:** Task 1 contract.
- **Parallel safe:** No; the renderer and selector must consume the exact backend contract.

### 3. Capture end-to-end acceptance evidence and retire the interim path

- **Files allowed:** `docs/goals/mascot-options-aware-knowledge/{PLAN.md,GOAL.md,EXECUTION.md}` and `docs/goals/mascot-options-aware-knowledge/evidence/**`.
- **Output:** Store request/response and browser captures, update `EXECUTION.md` with observed results, and confirm there is one current-level knowledge source and one mascot rendering path.
- **Verification command:** Review the captured overview payload and browser state against every acceptance criterion above; run `git diff --check` on the scoped changes.
- **Acceptance evidence:** The evidence set demonstrates the target learner flow, not just a type contract or code diff.
- **Depends on:** Tasks 1 and 2.
- **Parallel safe:** No; evidence follows the integrated UI.

## Non-Goals

- Change first-encounter lessons, form acknowledgment, mastery, scoring, or level gates.
- Show every command option in the current chapter regardless of level relevance.
- Add new authored content when the canonical Chapter Book content already supplies the option/argument explanation.
- Change reward chest visuals or labels as part of this plan.

## Risk If Wrong

If level tips are assembled from all commands or all Chapter Book options instead of the exact forms attached to the current level, the mascot becomes noisy and may teach future content early. If option explanations are copied into a mascot-specific catalog, they will drift from the Chapter Book. If the full Chapter Book payload is fetched on every map view, the small UX improvement may add unnecessary network and rendering cost.

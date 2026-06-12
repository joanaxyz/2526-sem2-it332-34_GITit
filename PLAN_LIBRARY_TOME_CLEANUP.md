# Plan: Foundations removal · Naming unification · Tome content type

Branch: `chore/codebase-improvements`. Three workstreams, ordered so each leaves the repo green.

## Background (why)

- `command_topics.py` is the **seed authoring spec** for the command catalog (`CommandSkill` + `CommandForm` rows per storey). The **library** (`command_content.py`) is the rich reference content layered on those commands, served per storey as a **book** (`/api/storeys/<id>/book/` → `StoreyBookModal`). Different layers, blurred names — hence the rename.
- **The library has no model today — and that's a bug-shaped design, not a decision.** `book_command_payload` (`selectors.py:211-238`) merges three sources in precedence: (1) `skill.command_preview["pages"]` — but the seeder writes `command_preview` *without* pages, so this branch is dead; (2) the in-code `GIT_COMMAND_CONTENT_LIBRARY` index — **empty** (`command_content.py:1067`); (3) a synthesized fallback page — *what every book actually shows today*. `seed_command_library.py` is a no-op scaffold whose own TODO says "once a CommandLibraryEntry model exists, persist…". This plan finishes that work (Phase B3): a real `LibraryEntry` model, a working seed, and one source of truth for book pages.
- "Drill" and "workflow" are **legacy seed-spec names** for what the models/API already call adventures and challenges: `COMMAND_DRILLS` (drills.py) seeds `AdventureQuest` rows; `WORKFLOW_SCENARIOS` (workflows.py) seeds `Challenge`/`ChallengeQuest` rows. The 2026-06-11 quest-terminology normalization already renamed every model, FK, related_name, and API key — so the drill/workflow remnants are file names, spec-list names, one help string, and one frontend local variable. **Unifying them requires zero migrations.**
- `foundations.py` is already deleted from `curriculum_v2/`, leaving `seed_curriculum_v2.py` with a **broken import** (line 9). All other foundations plumbing (ConceptPage model → serializer → view → URL → tests → unused frontend API) is dead and must go.
- New content type: **Tome** — a general (non-command) lesson, authored like library content, surfaced on `/tower` as a new non-repeating storey section above the adventure gate, with its own door artifact that opens a book reader.

Decisions made with the user: new lesson type = **Tome**; model/API renames + migrations are allowed where needed for unification (audit result: none needed — models/API are already on the unified names; the only migrations are the ConceptPage drop and the Tome creation).

## The unified naming system (after this plan)

| Concept | Model(s) | Seed spec | Notes |
|---|---|---|---|
| Storey | `Storey` | `storeys.py` → `STOREYS` (was `modules.py`/`MODULES`) | tower floor |
| Command catalog | `CommandSkill`, `CommandForm` | `command_catalog.py` → `COMMAND_CATALOG` | the commands a storey teaches |
| Library / Book | `LibraryEntry` (new) | `library.py` entries, seeded by `seed_command_library` | per-storey reference book over the catalog |
| Tome | `Tome` (new) | `tomes.py` → `TOMES` | general lesson, opens as a book |
| Adventure | `CommandAdventure`, `AdventureQuest` | `adventures.py` → `COMMAND_ADVENTURES`, `adventure_quests.py` → `ADVENTURE_QUESTS` | per-storey command practice |
| Challenge | `Challenge`, `ChallengeQuest` | `challenges.py` → `CHALLENGES` | scenario quests, gated by the adventure |

"Drill" and "workflow" cease to exist as concepts (historical migrations and incidental prose excepted). "Quest" remains the shared sub-unit of both adventures and challenges. "Scenario" survives only inside `scenario_context` (a frozen model field/spec key), not as a content-type name.

---

## Phase A — Remove foundations (fixes the broken seed)

Backend:
1. `backend/curriculum/management/commands/seed_curriculum_v2.py`
   - Drop import `from curriculum.curriculum_v2.foundations import FOUNDATIONS` (line 9) and `ConceptPage` from the models import (line 15).
   - Drop `self._seed_foundations()` call (line 80) and the `_seed_foundations()` method (lines 90–106).
   - In `_reset_seeded_data()`, drop the `ConceptPage.objects.all().delete()` line (~372).
2. `backend/curriculum/models.py` — delete `ConceptPage` (lines 34–48).
3. New migration `0005_delete_conceptpage` via `python manage.py makemigrations curriculum`.
4. `backend/curriculum/selectors.py` — delete `published_foundations()` (lines 21–22) + `ConceptPage` import.
5. `backend/curriculum/views.py` — delete `FoundationTopicListAPIView` (17–19) + the `published_foundations` / `FoundationTopicSerializer` imports.
6. `backend/curriculum/serializers.py` — delete `FoundationTopicSerializer` (6–18); import becomes `from curriculum.models import Storey`.
7. `backend/config/urls.py` — remove `api/concept-pages/` route (line 40) + view import.
8. `backend/curriculum/tests/test_curriculum_api.py` — remove the foundations test (lines 8–14) + `ConceptPage`/`published_foundations` imports; keep storey tests.

Frontend:
9. `frontend/src/features/storeys/api/storeysApi.ts` — remove `listFoundations()` + `FoundationTopic` import.
10. `frontend/src/features/storeys/types.ts` — delete `FoundationTopic` (lines 7–20).
11. `frontend/src/shared/api/queryKeys.ts` — remove `foundations` key (line 8).

(Prose mentions of "foundations" in `AuthLayout.tsx`/`ChallengeOutcomeModal.tsx` are marketing copy, not code — leave or reword; not required.)

## Phase B — Naming unification

**Frozen — do not touch:** seed-spec dict keys inside the data entries (`"module"`, `"usage"`, `"levels"`, form keys like `"git-status/plain"`, `"scenario_context"`/`"scenario_context_template"`, `"challenge_type"` values), the `"problem"` hash key in `backend/practice/builders.py:238` (feeds `semantic_key`), and **historical migration files** (never rewrite — `related_name='drills'` / `workflow_scenario` references in `0001_initial.py` files are inert history). The book API (`StoreyBookAPIView`, `storey_book`, `/api/storeys/<id>/book/`, frontend `StoreyBook`/`BookCommand` types) already carries the unified names and stays.

### B1. Library = content layer

1. `git mv backend/curriculum/command_content.py backend/curriculum/library.py`. Inside:
   - `command_content_entry_for_command` → `library_entry_for_command`
   - `command_content_key_for_command` → `library_key_for_command`
   - `_build_command_content_index` → `_build_library_index`; `_COMMAND_CONTENT_INDEX` → `_LIBRARY_INDEX`; `GIT_COMMAND_CONTENT_LIBRARY` → `LIBRARY_ENTRIES`
   - Block builder helpers (`_content`, `_sections`, `_paragraph`, `_commands`, `_bullets`, `_diagram`, …) keep names.
   - Add `tome_pages(sections)` convenience (thin wrapper over `pages_from_command_sections`) for Phase C.
2. Update callers: `selectors.py` (import line 17 + call in `book_command_payload` ~212, update "command_content.py" docstring mention), `management/commands/seed_command_library.py` (import line 33 + docstrings), `tests/test_storey_book.py` (51–52).
3. `git mv backend/curriculum/curriculum_v2/command_topics.py … command_catalog.py`; `COMMAND_TOPICS` → `COMMAND_CATALOG`. Update `seed_curriculum_v2.py` import (line 7) + usages in `_seed_command_skills`, `_published_storey_slugs`, `_validate_challenge_intro_contract`.

### B2. Eliminate "drill" → adventure, "workflow" → challenge

Audit confirmed all occurrences (models/API already clean; no migrations):

4. Extract the spec-builder helpers shared by drills and workflows (`ev`, `repo`, `commit`, `meta_equals`, `uninitialized` — currently in `drills.py`, imported by `workflows.py:18`) into a new `backend/curriculum/curriculum_v2/spec_helpers.py`, so the challenge spec file doesn't import from the adventure spec file.
5. `git mv backend/curriculum/curriculum_v2/drills.py … adventure_quests.py`; `COMMAND_DRILLS` → `ADVENTURE_QUESTS` (all 7 list-extend sites, lines 204–969); update the module docstring (line 5 references "workflows.py").
6. `backend/curriculum/curriculum_v2/adventures.py` — `COMMAND_DRILL_ADVENTURES` → `COMMAND_ADVENTURES` (matches the `CommandAdventure` model); `command_drill_adventure_for` → `command_adventure_for`.
7. `git mv backend/curriculum/curriculum_v2/workflows.py … challenges.py`; `WORKFLOW_SCENARIOS` → `CHALLENGES`; update its import to `spec_helpers` and docstrings. Internal `_scenario()` helper keeps its name (it builds `scenario_context`, a frozen field).
7b. `git mv backend/curriculum/curriculum_v2/modules.py … storeys.py`; `MODULES` → `STOREYS`. The frozen spec key `"module"` inside entries stays — add a one-line comment in `storeys.py` stating `"module"` is the frozen authoring key for "storey slug".
8. `backend/curriculum/management/commands/seed_curriculum_v2.py` — update all imports (lines 6, 8, 11) and usages (`COMMAND_DRILLS` at 78, 208, 229, 337, 486; `COMMAND_DRILL_ADVENTURES` at 138; `WORKFLOW_SCENARIOS` at 243, 340, 489); help string (line 55) → `"Seed the v2 curriculum: storeys, command catalog, adventures, challenges, tomes."`
9. Frontend `frontend/src/features/storeys/components/StoreyPracticeHub.tsx` — rename locals `workflowQuery` → `challengesQuery`, `workflowLoadRef` → `challengeLoadRef` (lines 454–565). No type/API changes.
10. Optional prose: `backend/progress/services.py:34` ("…you've drilled the commands…") → reword to "practiced" to keep the word out of user-facing copy. The storey-slug assertion `"integrated-workflows"` in `test_challenge_curriculum.py:262` is a regression guard against an old slug — leave it.

11. Grep gate: `command_content`, `command_topics`, `COMMAND_TOPICS`, `MODULES`, `drill` (case-insensitive), `workflow` (case-insensitive) return zero code hits under `backend/` (excluding `migrations/`) and `frontend/src/`.

### B3. Give the library a model (finish the half-built persistence)

Today book pages have three sources with precedence (`selectors.py:211-238`): dead `command_preview.pages` branch → empty in-code library → synthesized fallback. Replace with one DB source:

12. `backend/curriculum/models.py` — add:
    ```python
    class LibraryEntry(models.Model):
        command_key = CharField(unique=True)   # canonical key from library_key_for_command, e.g. "git commit"
        title = CharField(160, blank=True); summary = TextField(blank=True)
        pages = JSONField(default=list)        # list[BookPage]
        is_published = BooleanField(default=True)
    ```
    Migration `0007_libraryentry`.
13. Implement `seed_command_library.py` for real (its TODO): iterate `LIBRARY_ENTRIES` in `library.py`, build pages via the block builders, `update_or_create` by `command_key`, unpublish entries no longer in the spec. Author the spec entries in `library.py` exactly as the scaffold template intended.
14. `selectors.py` `book_command_payload` — new precedence: published `LibraryEntry` matching `library_key_for_command(skill.base_command)` → synthesized fallback. **Delete the `command_preview.pages` branch** (dead: the seeder always rewrites `command_preview` without pages, so nothing can live there).
15. `command_preview` keeps its real, single job: the practice preview (`CommandFormPreviewAPIView`, `/api/command-forms/<id>/preview/` — title/summary/syntax shown in the practice workspace). It no longer doubles as a book-content slot — that overload was a major source of the confusion.
16. `library.py` becomes purely the **authoring DSL + spec list** (builders + `LIBRARY_ENTRIES` + `TOMES`-shared helpers); the DB is the runtime source. Same shape as tomes: author in code, seed to DB, serve from DB.
17. Tests: extend `test_storey_book.py` — seeded `LibraryEntry` pages win over fallback; unpublished entry falls back to synthesized page.

### Audited and intentionally left alone

- Frozen seed-spec keys `"module"` (= storey slug), `"usage"`/`"usages"` (= command form), `"levels"` (= the easy/medium/hard `ChallengeQuest` specs) — frozen authoring format; renaming them means rewriting every authored entry for zero runtime gain. Documented via comments instead.
- **"Field Guide"** (UI label in `StoreyBookCard`/`StoreyBookModal`) vs **book** (code) — intentional: in-world display name vs code term, same as "Tome" will be. Keep.
- `/dashboard`, `/stats`, `/performance` redirects in `router.tsx:60-63` — deliberate legacy redirects from the home rename. Keep.
- `backend/practice/` app (command execution: steps, logs, variant building, scaffolding) and `StoreyPracticeHub.tsx` (UI) — "practice" means session execution vs the storey's content hub; mild overlap, high churn to rename, low confusion payoff. Keep.
- Adventure `Run`+`QuestAttempt` vs Challenge `Run`+steps asymmetry, `ChallengeAccessContext` dataclass name — noted, not worth churn now.

## Phase C — Tome backend

1. `backend/curriculum/models.py` — add:
   ```python
   TOME_PLACEMENTS = [("above_adventure", …), ("below_adventure", …), ("below_challenges", …)]

   class Tome(models.Model):
       storey = FK(Storey, related_name="tomes", CASCADE)
       slug = SlugField(); title = CharField(160); summary = TextField(blank=True)
       pages = JSONField(default=list)        # list[BookPage] — same schema BookContent renders
       placement = CharField(32, choices=TOME_PLACEMENTS, default="above_adventure")
       is_published = BooleanField(default=True); sort_order = PositiveIntegerField(default=0)
       Meta: unique_together ("storey", "slug"); ordering ["storey__sort_order", "sort_order", "id"]
   ```
   Placement is a slot enum (named insertion points in the designed storey sequence) — not a free ordinal. Multiple tomes per storey/slot allowed, ordered by `sort_order`.
2. Migration `0006_tome` via makemigrations.
3. New `backend/curriculum/curriculum_v2/tomes.py` — `TOMES` spec list: `{"module": <storey-slug>, "slug", "title", "summary", "placement", "sections": [...]}`, sections authored with `library.py` block helpers. Ship at least one real tome so seed + UI have content.
4. `seed_curriculum_v2.py` — import `TOMES`, `tome_pages`, `Tome`; add `self._seed_tomes(storeys)` in `handle()` (after `_seed_command_adventures`); method mirrors `_seed_command_skills` (`update_or_create` per spec, then `Tome.objects.exclude(id__in=live).update(is_published=False)`). Add `Tome.objects.all().delete()` to `_reset_seeded_data()`.
5. `backend/curriculum/selectors.py` — add `tome_summary_payload(tome)` → `{item_type: "tome", id, slug, title, summary, placement, pages}` and a `tomes` branch in `storey_content_page()` (non-paginated: `next_cursor: None`, like the `command_adventures` branch). Pages ship **inline** — no second fetch, no new endpoint; `StoreyContentAPIView` already passes `section` through.
6. New `backend/curriculum/tests/test_tomes.py` — seed creates published tomes with non-empty pages; `section=tomes` payload shape (item_type/placement/pages/next_cursor).

Tomes are **always unlocked** — pure reading, no run/attempt/progress models.

## Phase D — Tome frontend + door artifact

Types/selection:
1. `frontend/src/features/challenges/types.ts` — add `TomePlacement`, `TomeSummary { item_type:'tome', id, slug, title, summary, placement, pages: BookPage[] }`; add `'tomes'` to `StoreyContentSection`.
2. `frontend/src/features/storeys/hooks/useTowerSelection.ts` — add `{ kind: 'tome'; storeyId; tome: TomeSummary }` to `TowerSelection`; `isSelected` branch on `tome.id`.

Hub:
3. `frontend/src/features/storeys/components/StoreyPracticeHub.tsx` — `useStoreyContent<TomeSummary>(storey.id, 'tomes', shouldLoad)`; widen `ContentItem` union for `flattenPages`. Render a new `TomeSection` between the window band and the adventure stage (~line 490), **only when** tomes with `placement === 'above_adventure'` exist — non-authored storeys are pixel-identical. (Other slots: define the filter, wire later.)

Artifact — **"Lectern Archive"** (new `TomeArtifact.tsx` or co-located like `AdventureDoor`):
4. A singular standing lectern: stone plinth + post + slanted desk holding an **open book**. Distinct silhouette from the adventure double-leaf gate and challenge portcullis — furniture, not a doorway; never a repeating row. `motion.button` with `whileInView` rise entrance like `AdventureDoor`. Per DESIGN.md: stone surfaces; the open-book interior is the One Warm Note (window-amber `rgba(255,209,130,…)`); cyan glow only on hover (`aurora-sm`) and selected (`aurora-md`, `data-selected`); JetBrains Mono "Tome" kicker; `prefers-reduced-motion` fallback; no locked state.
5. Clicking calls `select({ kind: 'tome', storeyId, tome })`.

Rail + dock + reader:
6. `DoorOverview.tsx` — `kind === 'tome'` branch: kicker "Tome", `BookOpen` icon, title/summary, no progress bar.
7. `TowerActionButton.tsx` — `kind === 'tome'` branch: label **"Read"**; opens a modal (local `useState<TomeSummary|null>`) instead of routing — `useTowerDoorNavigation` untouched.
8. New `frontend/src/features/storeys/book/TomeReaderModal.tsx` — `{ tome, onClose }`; same modal sizing as `StoreyBookModal` but no command rail / bookNav / prev-next. Extract a `BookPages({ pages })` renderer from `BookContent.tsx` (which currently takes a `BookCommand`) and have both delegate to it — tome pages are plain `BookPage[]`/`BookBlock[]`, no new block types. Renders synchronously from inline `tome.pages`.

Styles + tests:
9. `frontend/src/styles/globals.css` — `.tome-stage` (modeled on `.tower-adventure-stage`), `.tome-lectern` / `.tome-book` rules (modeled on `.adventure-door` + `.storey-book`): stone stand, amber book glow, cyan hover/selected, reduced-motion.
10. `StoreyPracticeHub.test.tsx` — mock must branch on `section === 'tomes'` explicitly (current mock returns challenge payload for non-adventure sections). New test: artifact renders above adventure → select fills DoorOverview → "Read" opens reader → tome page heading visible.

---

## Verification

1. `python manage.py makemigrations --check` — exactly three: `0005_delete_conceptpage`, `0006_tome`, `0007_libraryentry` (the renames themselves generate **no** migrations; anything extra means a model was touched by mistake).
2. `python manage.py migrate` then `python manage.py seed_curriculum_v2 --validate` — clean (broken import gone, tomes seeded; seeded row counts for adventures/challenges identical to before the rename); `python manage.py seed_command_library` now actually persists `LibraryEntry` rows, and `/api/storeys/<id>/book/` serves those pages instead of the synthesized fallback for seeded commands.
3. Backend tests: full `pytest backend/` (storey_book import rename, foundations test removed, drill/workflow spec imports in any test updated, new test_tomes.py).
4. Greps return zero code hits: `command_content|command_topics|COMMAND_TOPICS|FOUNDATIONS|ConceptPage|published_foundations|FoundationTopic` and case-insensitive `drill|workflow` (backend excluding `migrations/`), `FoundationTopic|listFoundations` and case-insensitive `drill|workflow` (frontend/src).
5. API: `GET /api/storeys/<id>/content/?section=tomes` → inline pages, `next_cursor: null`; `/api/concept-pages/` → 404; `/api/storeys/<id>/book/` unchanged.
6. Frontend: `tsc`/build green; vitest green incl. new tome tests.
7. Manual on `/tower`: authored storey shows the lectern above the adventure gate; select → rail overview + "Read" dock → reader renders the tome's pages; non-authored storeys unchanged.

## Critical files

- `backend/curriculum/management/commands/seed_curriculum_v2.py` (A, B, C) · `seed_command_library.py` (B3, becomes real)
- `backend/curriculum/models.py` (drop ConceptPage; add Tome, LibraryEntry) + migrations 0005/0006/0007
- `backend/curriculum/selectors.py` · `views.py` · `serializers.py` · `backend/config/urls.py`
- `backend/curriculum/command_content.py` → `library.py` · `curriculum_v2/command_topics.py` → `command_catalog.py` · `curriculum_v2/drills.py` → `adventure_quests.py` · `curriculum_v2/workflows.py` → `challenges.py` · `curriculum_v2/modules.py` → `storeys.py` · `curriculum_v2/adventures.py` (rename `COMMAND_DRILL_ADVENTURES`) · new `curriculum_v2/spec_helpers.py` · new `curriculum_v2/tomes.py`
- `frontend/src/features/storeys/components/StoreyPracticeHub.tsx` · `hooks/useTowerSelection.ts` · `components/DoorOverview.tsx` · `components/TowerActionButton.tsx`
- new `frontend/src/features/storeys/book/TomeReaderModal.tsx` (+ `BookPages` extraction from `BookContent.tsx`) · new `TomeArtifact` · `frontend/src/styles/globals.css`

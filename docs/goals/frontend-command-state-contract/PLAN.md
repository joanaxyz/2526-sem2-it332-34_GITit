# Frontend Command State Contract Regression Fix Implementation Plan

**Intent:** Restore reliable completion of every authored story level when its documented command sequence is entered through the real frontend terminal.
**Current Behavior:** The API sends the browser a filtered and sometimes enriched repository snapshot, while the backend transition verifier compares the submitted next state with the original normalized persisted state. Valid frontend transitions are therefore rejected when legacy metadata is dropped or conflict details are synthesized. A smaller set of diagnostic forms and mutating commands also have simulator/verifier parity gaps.
**Expected Outcome:** The browser mutates a canonical, lossless repository-state copy; the backend verifies the same contract; supported diagnostic commands remain read-only; and every authored solution sequence either completes its level or exposes a narrowly attributable authored-content defect.
**Target-Perspective Output:** A player can paste each cheat-sheet sequence into the visible frontend terminal and see the level advance without false tampering errors, ambiguous-argument errors for supported syntax, or a silent non-advance.
**Truth Owner:** The frontend Git simulator owns command execution semantics. The normalized persisted `repository_state` owns canonical state shape. The backend client-transition verifier mirrors allowed transitions as the security boundary.
**Contract Boundary:** API `repository_state` and command-response `repository_state` must normalize and hash identically to the canonical persisted state after excluding only derived UI fields (`project_tree` and `visible_tree`). Browser snapshots must preserve every canonical top-level key and must not synthesize mutable canonical fields.
**Cutover:** Replace the backend and frontend manual snapshot allowlists with lossless normalized clones. Add derived project-tree fields only to display snapshots. Classify read-only config listing consistently and add supported `git show <revision>:<path>` output. Repair verifier parity only for command families still failing after the boundary cutover.
**Displaced Path:** The manual top-level snapshot allowlists and conflict-detail enrichment inside canonical `repository_state` cease to be execution paths. No second filtered command-state path remains.
**Value Density:** The boundary correction addresses most of the 66 failures across checkout conflict resolution, merge abort/continue, fetch/prune, reset, stash, cherry-pick, and downstream multi-command flows before command-specific patches are considered.
**Acceptance Evidence:** A fresh disposable player replays all 284 authored sequences through the rendered frontend terminal, with a generated report showing 284 passes, zero backend rejections, and zero non-advancing levels. Focused screenshots/logs capture representative formerly failing conflict, metadata, diagnostic, and historical-path scenarios. Before completion is accepted, the implementing maintainer inspects those totals and representative captures from the player's perspective.
**Evidence Lane:** Backend and frontend contract tests; simulator command tests; representative in-browser terminal replays; then the complete frontend matrix on a fresh QA player.
**Kill Criteria:** No command-response snapshot may enumerate a preferred subset of canonical state keys or enrich `conflict_details`. No diagnostic classifier disagreement may remain between frontend and backend. No known failing level may be marked fixed solely from unit tests or direct API calls.
**Architecture Slice:** Authored variants persist initial/target state and solution commands; adventure payloads serialize state through `RepositorySnapshotService`; the frontend terminal normalizes and executes it through `executeGitCommand`; submissions cross `client_command_execution.py`; the verifier checks the transition and persists it; response snapshots feed the next optimistic command.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Files to create

- `frontend/src/shared/git/simulator/state/snapshot.test.ts` if no existing test file can express lossless browser snapshot round trips.
- Focused verifier regression tests under the existing backend verifier test module only when a remaining command-specific mismatch is proven.

### Files to modify

- `backend/simulator/services/core.py`
- `backend/simulator/tests/test_repository_snapshot_service.py`
- `frontend/src/shared/git/simulator/state/snapshot.ts`
- `frontend/src/shared/git/simulator/commandMetadata.ts`
- `backend/simulator/services/core.py` diagnostic classification
- Existing frontend/backend diagnostic tests
- `frontend/src/shared/git/simulator/commands/formatters.ts`
- Existing frontend simulator tests
- Backend verifier modules and tests only for mismatches that survive the state-contract fix
- `scripts/checks/verify_frontend_level_sequences.py`, `LEVEL_CHEAT_SHEET.md`, and `dogfood-output/frontend-level-test-results.md` for final evidence

### Files to avoid

- Unrelated dirty curriculum, payment, cosmetic, and UI files already present in the worktree
- Authored seed targets unless replay proves the authored target itself contradicts the intended command
- Authentication and production user data
- Broad verifier relaxations that accept arbitrary client state

### Source of truth

- Canonical state shape: `backend/simulator/state.py::RepositoryStateNormalizer`
- Command behavior: `frontend/src/shared/git/simulator/engine.ts` and command handlers
- Security parity: `backend/common/git/client_command_execution.py` and verification modules
- Authored outcomes: persisted variant `initial_state`, `solution_commands`, and `target_state`

### Read path

`AdventureAttempt.repository_state` → `backend/adventures/payloads.py::attempt_payload` → `RepositorySnapshotService.snapshot` → frontend attempt cache → terminal engine.

### Write path

Frontend terminal → `executeGitCommand` → optimistic `next_state` → adventure command endpoint → client-transition verification → persisted attempt state → response snapshot → frontend cache.

### Contract boundary

The state received by the browser, after normalizing away only derived display trees, must be byte/hash equivalent to the verifier's normalized current state. The browser's post-command snapshot must retain arbitrary compatible metadata rather than reselecting known fields.

### Integration points

- Snapshot normalization and display-tree derivation
- Optimistic cache replacement after each command
- Diagnostic command metadata and backend immutable-state validation
- Historical object/path resolution for `git show`
- Per-family backend transition verifiers
- Level evaluation and advancement in the adventure UI

### Migration/cutover

This is an immediate internal contract cutover with no data migration: normalized stored JSON is already canonical. Existing attempts receive lossless snapshots on their next read. Derived trees remain response-only additions and are removed by normalization before hashing/submission.

### Displaced path

Delete the manual field-by-field command snapshot construction and stop calling `_conflict_details` from the canonical repository-state response. Remove `_conflict_details` if it has no remaining display-only caller.

### Acceptance evidence gate

Do not claim completion until a new QA account runs every sequence through visible frontend interactions. Any failure must identify the exact terminal output or non-advance and be traced to state contract, simulator behavior, verifier parity, or authored content.

## Task 1: Lock the lossless snapshot contract

**Allowed scope:** Backend/frontend snapshot services and focused tests only.

**Files:**

- `backend/simulator/services/core.py`
- `backend/simulator/tests/test_repository_snapshot_service.py`
- `frontend/src/shared/git/simulator/state/snapshot.ts`
- `frontend/src/shared/git/simulator/state/snapshot.test.ts` or the nearest existing simulator test

**Expected output:**

- Command snapshots are deep-cloned normalized states with only derived display fields absent.
- Display snapshots add `project_tree` and `visible_tree` without changing canonical fields.
- Raw authored `conflict_details`, unknown compatible metadata, and legacy top-level operation mirrors survive round trips unchanged.
- Returned snapshots cannot mutate the caller's state by aliasing nested data.

**Verification:**

- `python -m pytest simulator/tests/test_repository_snapshot_service.py`
- `npm test -- --run src/shared/git/simulator/state/snapshot.test.ts` or the selected existing test file

**Acceptance evidence:** Tests compare normalized hashes for conflict-heavy and metadata-heavy states and assert no enrichment or key loss.

**Parallel:** No. This changes the shared contract used by all later tasks.

## Task 2: Align read-only diagnostics and historical-path display

**Allowed scope:** Diagnostic metadata, `show` formatter, and focused tests.

**Files:**

- `backend/simulator/services/core.py`
- Backend diagnostic inventory tests
- `frontend/src/shared/git/simulator/commandMetadata.ts`
- `frontend/src/shared/git/simulator/commands/formatters.ts`
- Existing frontend simulator tests

**Expected output:**

- `git config --list` and `git config -l` are diagnostic on both sides and never mutate repository state.
- `git show <revision>:<path>` resolves the revision, reads that commit tree, emits the historical file content, and reports an appropriate missing-path or ambiguous-revision error.

**Verification:**

- Focused backend diagnostic tests
- Focused frontend simulator tests for both config listing forms and historical path display

**Acceptance evidence:** The exact previously failing authored commands execute successfully with unchanged state in the frontend engine and are accepted by backend diagnostic validation.

**Parallel:** May run after Task 1; its file scope is disjoint from verifier-family repairs.

## Task 3: Replay representative failures through the frontend

**Allowed scope:** Disposable QA data, the existing local frontend/backend, and the sequence verifier. No production code changes during the replay.

**Scenarios:**

- Conflict choice: `git checkout --ours src/relay.conf`
- Conflict abort/continue path
- Remote pruning
- Soft/hard/mixed reset
- Interactive add
- Squash merge
- Config listing
- Historical path show
- Multi-command stash/cherry-pick/removal flows

**Expected output:** A classified remaining-failure list after the shared contract fix.

**Verification:** Interact with the rendered frontend terminal and inspect the resulting UI advancement and backend response, not just direct engine calls.

**Acceptance evidence:** Captured run IDs, command text, terminal output, and advancement status for each representative.

**Parallel:** No. Results determine whether Task 4 is needed.

## Task 4: Decompose and review proven simulator/verifier parity gaps

**Allowed scope:** Planning evidence only. Do not modify command handlers or verifiers in this task.

**Files:**

- `docs/goals/frontend-command-state-contract/PLAN.md`
- The classified Task 3 evidence report

**Expected output:** Amend this plan with one bounded implementation task per proven mismatch. Each task must name the exact command family, frontend handler or backend verifier owner, exact transition invariant, exact test files, allowed write scope, and one real frontend replay.

**Verification:**

- Confirm every remaining failure from Task 3 is classified as state contract, frontend simulator behavior, backend verifier parity, authored content, harness defect, or environment defect.
- Run a lightweight PRE review of the amended tasks before changing any command handler or verifier.

**Acceptance evidence:** The PRE reviewer returns `aligned`, or every blocker/major finding is corrected or explicitly accepted by the user.

**Parallel:** No. This is a review checkpoint.

### Task 3 classified evidence

The rendered frontend replay after Tasks 1–2 produced this classification:

- **State contract fixed:** `git checkout --ours src/relay.conf` returned HTTP 200 and showed `Adventure cleared` for run 179. The submitted `conflict_details` exactly matched canonical authored data.
- **State contract fixed:** `git fetch --prune` completed run 223.
- **State contract fixed:** `git stash pop`, `git stash apply`, `git cherry-pick --no-commit c2`, `git mergetool`, and `git merge --continue` all returned HTTP 200. The single-wave mergetool and merge-continue runs completed; the multi-command runs advanced their command count and remained ready for their documented next command.
- **Diagnostic fixes proven:** `git config --list` emitted the effective config and advanced run 78 from wave 2 to wave 3. `git show m1:src/app.ts` returned HTTP 200 and completed run 284.
- **Backend partial-add verifier mismatch:** run 137 returned HTTP 400. The browser stages one fallback hunk token, `"modified export const mode = 'patched'\n"`, while `StagingVerificationMixin._entry_tokens` expects two tokens, `"modified"` and the content.
- **Backend reset verifier mismatch:** soft, mixed, and hard runs 141–143 returned HTTP 400. The browser preserves the exact pre-reset canonical state in `merge_abort_state` and mirrors only the four newly written reset metadata keys. The verifier omits that snapshot and incorrectly promotes every pre-existing nested `operation_metadata` entry to a legacy top-level key.
- **Backend squash-merge verifier mismatch:** run 166 returned HTTP 400. Staging matches, but the verifier omits the frontend-owned `last_merge_branch`, `last_merge_target`, and `squash_merge_staged` metadata in both nested and legacy-mirror locations.
- **Frontend merge-abort simulator mismatch:** run 181 returned HTTP 400. The normalized default `merge_abort_state: {}` is truthy in JavaScript, so `abortMerge` restores an empty object and erases commits, branches, and HEAD. The backend correctly treats an empty mapping as absent and expects fallback cleanup that preserves repository history.

Task 4 PRE review must approve the four bounded repairs below before their production files are changed.

## Task 5: Implement the reviewed command-family repairs

### Task 5A: Match partial-add fallback tokenization

**Owner:** Backend transition-verifier mirror.

**Files allowed:**

- `backend/common/git/verification/staging.py`
- `backend/practice/tests/test_command_executor.py`

**Transition invariant:** When no authored partial-hunk list exists, structured worktree content is collapsed through the canonical normalizer token haystack into the same single fallback hunk token emitted by frontend `entryTokens`. Authored `hunks`, `tokens`, `target_hunks`, and `leftover_hunks` lists retain their existing list semantics.

**Expected output:** The exact frontend next state for `git add -p src/app.ts` is accepted; forged changes outside staging/worktree remain rejected by existing immutable-key checks.

**Verification:** Focused backend acceptance test, existing command-executor security tests, and rendered frontend replay of run 137.

### Task 5B: Match reset snapshot and metadata semantics

**Owner:** Backend transition-verifier mirror.

**Files allowed:**

- `backend/common/git/verification/staging.py`
- `backend/practice/tests/test_command_executor.py`

**Transition invariant:** Before moving HEAD, all reset modes store an exact deep copy of the normalized previous state in `merge_abort_state`. The verifier mirrors only `last_reset_mode`, `last_reset_target`, `last_reset_target_expr`, and `last_reset_previous_head` at top level while merging those four into nested `operation_metadata`; it never promotes unrelated existing nested metadata.

**Expected output:** Soft, mixed, and hard frontend transitions are accepted while exact HEAD, tree-diff, reflog, cleanup, and metadata checks remain enforced.

**Verification:** Parameterized backend acceptance test for all three modes with pre-existing nested-only metadata, existing forged-transition tests, and rendered frontend replays of runs 141–143.

### Task 5C: Match squash-merge operation metadata

**Owner:** Backend transition-verifier mirror.

**Files allowed:**

- `backend/common/git/verification/merge_stash.py`
- `backend/practice/tests/test_command_executor.py`

**Transition invariant:** A squash merge stages the target/current tree diff without moving HEAD or creating a commit and writes `last_merge_branch`, `last_merge_target`, and `squash_merge_staged: true` through `_set_operation_metadata`, producing both nested and legacy mirrors.

**Expected output:** The exact frontend transition is accepted without relaxing staging, branch, HEAD, or commit checks.

**Verification:** Focused backend acceptance test plus rendered frontend replay of run 166.

### Task 5D: Treat an empty merge-abort snapshot as absent

**Owner:** Frontend Git simulator.

**Files allowed:**

- `frontend/src/shared/git/simulator/commands/merge.ts`
- `frontend/src/shared/git/simulator/engine.test.ts` or `frontend/src/shared/git/simulator/engine.advanced.test.ts`

**Transition invariant:** `git merge --abort` restores `merge_abort_state` only when it is a non-empty record. An empty normalized default uses fallback cleanup: preserve commits, branches, HEAD, remotes, and unrelated metadata; clear conflicts, staging, working tree, conflict details, and merge parent; then record `last_merge_aborted`. A real non-empty merge snapshot continues to restore exactly.

**Expected output:** The frontend-produced next state matches the already-correct backend verifier and the authored target.

**Verification:** Frontend simulator tests for empty-default fallback and non-empty restoration, production build, and rendered frontend replay of run 181.

### Task 5 integration gate

**Allowed scope:** Only the exact owner files and tests named above.

**Expected output:** Each backend expected transition matches the frontend truth owner for its valid authored operation, or the frontend handler correctly implements the supported command form. Unrelated immutable-field checks remain unchanged.

**Verification:**

- Focused unit test using the exact initial state and frontend-produced next state
- Target comparison against the authored variant
- Repeat the corresponding frontend terminal scenario

**Acceptance evidence:** Each formerly rejected command advances its real level through the frontend.

**Parallel:** No. Tasks 5A–5D run sequentially in the main agent because three share the same backend test file and integration proof remains sequential.

## Task 6: Repair proven authored-contract defects when necessary

**Allowed scope:** Only a seed/spec owner whose initial state, target state, evaluator, or documented sequence is proven contradictory after Tasks 1–5. Do not use this lane to mask simulator or verifier defects.

**Files:**

- The exact owning file under `backend/curriculum/seed_data/source/`
- Its nearest focused compiler/seed/evaluator test
- Local persisted curriculum rows refreshed through the supported seed command

**Expected output:** The authored initial state, sequence, evaluator, and target describe one reachable teaching outcome while preserving the intended lesson.

**Verification:**

- Add a focused test proving the authored sequence reaches the evaluator/target.
- Run the supported local seed refresh without resetting unrelated user data.
- Replay the affected level through the frontend.

**Acceptance evidence:** The corrected level advances using the cheat-sheet sequence and its persisted variant matches the corrected source.

**Parallel:** No. Each authored defect must first be classified and traced to one source owner.

### Task 6 classified evidence from the first fresh-account matrix

The first complete rendered-frontend matrix finished at **279 / 284 passed**. All
five residuals accepted their terminal submissions; none was a recurrence of the
snapshot or mutating-command verifier failures fixed in Tasks 1–5.

- **Verified diagnostic-evidence persistence gap (three levels):** runs 387, 388,
  and 394 executed `git merge-base main feature/profile` and displayed `c0`.
  The frontend simulator deterministically writes `last_merge_base: c0`, but
  `ClientCommandExecutionService` discards every diagnostic `next_state`.
  Consequently the persisted state lacks the evidence required by the authored
  evaluator. The backend must derive this evidence itself rather than trust the
  client-provided value.
- **Authored initial-state contradiction (one level):** run 383 selected
  `ch3-adv-branch-from-release`. Its initial `branch-dirty` state already contains
  `hotfix: c0`, while its first official command is `git branch hotfix c0` and its
  process contract requires a successful `git branch`. The command correctly
  fails with “branch already exists,” so the otherwise-correct final state cannot
  complete the wave.
- **Frontend harness omission (one level):** run 417 selected
  `ch7-adv-daily-loop`. The authored variant requires a Project Files edit of
  `README.md` after `git pull` and before `git add`; that action is stored in
  `parameter_context.solution_workspace_files`. The verifier harness and cheat
  sheet currently list and submit only terminal commands, so `git add README.md`
  correctly finds no pending edit. This is not a simulator or curriculum defect.

### Task 6A: Persist trusted diagnostic evidence without trusting client state

**Owner:** Backend client-execution trust boundary and transition-verifier
helpers.

**Files allowed:**

- `backend/common/git/client_command_execution.py`
- The narrow backend verification helper that owns revision graph calculations
- `backend/practice/tests/test_command_executor.py`

**Transition invariant:** Diagnostic Git commands remain unable to alter commits,
refs, index, worktree, remotes, or arbitrary metadata. For supported evidence
commands (`git merge-base`, and the existing frontend-parity `git rev-list`
count), the backend computes the evidence from the authoritative previous state
and normalized command, writes only the exact nested and legacy operation
metadata keys, and persists that verified evidence. The browser-submitted
evidence value is ignored, so a forged diagnostic payload cannot earn progress.

**Expected output:** A successful `git merge-base main feature/profile` persists
`last_merge_base: c0` and can satisfy later evaluation after a merge, while a
forged submitted value is replaced by the backend-computed result.

**Verification:** Focused client-execution tests for correct evidence, forged
evidence replacement, ordinary diagnostic immutability, and `rev-list` parity;
then rendered frontend replays of the three affected waves.

### Task 6B: Make the branch-from-release official sequence processable

**Owner:** Blueprint authored initial-state fixture.

**Files allowed:**

- `backend/curriculum/seed_data/source/adventure_level_specs/blueprint_generated.py`
- The nearest blueprint curriculum invariant test
- Generated target output produced only by the supported target generator

**Transition invariant:** The shared `branch-dirty` fixture keeps `main` and
`feature/ui` plus the pending README edit, but does not pre-create `hotfix`.
Other waves using the fixture continue to have every branch they reference.
`ch3-adv-branch-from-release` must be able to create `hotfix` at `c0`, switch to
it, and commit without an unprocessable step.

**Verification:** Focused source invariant, generated-target freshness checks,
idempotent `seed_curriculum` refresh without `--reset`, and rendered frontend
replay of the full affected multi-wave level.

### Task 6C: Include authored Project Files actions in the cheat sheet and UI harness

**Owner:** Frontend level-sequence evidence harness.

**Files allowed:**

- `scripts/checks/verify_frontend_level_sequences.py`
- `LEVEL_CHEAT_SHEET.md`
- Final evidence outputs under `dogfood-output/`

**Transition invariant:** `solution_workspace_files` actions are interleaved at
their authored one-based `after_command_index`. The harness opens the named file
through the rendered Project Files panel, fills the visible File content editor,
clicks Save, and confirms the disposable run’s worktree changed before submitting
the next terminal command. No direct command-submission or workspace API call is
used. The cheat sheet displays the same edit/save step in sequence.

**Verification:** Generate the cheat sheet and assert all eight published
workspace-action variants include their Project Files step; replay the affected
ten-wave collaboration level through the frontend; then rerun the complete
fresh-account matrix.

### Task 6 amendment review gate

Do not execute Tasks 6A–6C until a PRE reviewer confirms that the evidence owner,
trust boundary, content owner, and harness owner are correctly separated and
that none of the fixes masks another layer’s defect.

## Task 7: Run the complete frontend level matrix

**Allowed scope:** A newly created disposable QA user, local app data for that user, the browser, and evidence artifacts.

**Files:**

- `scripts/checks/verify_frontend_level_sequences.py`
- `LEVEL_CHEAT_SHEET.md`
- `dogfood-output/frontend-level-test-results.md`
- `dogfood-output/report.md`

**Expected output:** Every story and level has its sequence listed and replayed from the frontend. The harness distinguishes terminal failure, backend rejection, non-advance, and pass.

**Verification:**

- Run the complete verifier against all 284 levels using the fresh account.
- Independently spot-check at least one formerly failing level in each story world.

**Acceptance evidence:** Final report totals 284/284 passed, includes per-story totals and any retry notes, and links each level to its cheat-sheet sequence. The implementing maintainer inspects the report's total pass count, backend-rejection count, non-advance count, and representative captures before accepting completion.

**Parallel:** No. This is the final integration/evidence gate.

## Non-goals

- Redesigning the terminal or level UI
- Reauthoring curriculum difficulty or wording
- Replacing the client-owned command engine with server-side Git execution
- Loosening the verifier to trust arbitrary frontend state
- Cleaning unrelated worktree changes

## Risk if wrong

A lossy snapshot leaves intermittent false rejections in multi-command levels. An over-broad verifier fix could allow client state forgery. Enriching canonical conflict data at read time creates an untraceable state mutation. Editing authored targets before fixing the boundary can hide simulator defects rather than resolve them.

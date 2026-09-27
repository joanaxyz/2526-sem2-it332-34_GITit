# Implementation and verification

## Completed board

| Task | Owner | Allowed scope | Outcome |
| --- | --- | --- | --- |
| Identity/persistence | Main | tutoring app/models/migrations | Unique per-player concept completion, separate pending feedback |
| Planner and verified feedback | Main | tutoring services + tier command observer | init/add/normal commit prerequisites; ordinary terminal accounting |
| API integration | Main | tier payloads/schemas, tutoring completion API, generated contracts | Nullable tutor in full/compact responses; signed state-bound acknowledgment |
| Workspace | Main | story-map tutorial component/hook | No guess input; onboarding-style overlay on every difficulty; cache/bootstrap persistence |
| Diagram | Main | shared LiveDagPanel and graph helpers/styles | Metadata, working/index, refs/remotes/stash/config/conflicts; centered pre-init folder |
| Acceptance | Main/verifier | disposable DB, browser, tests/docs | Evidence below; final independent review tracked below |

Implementation followed PLAN.md as revised by the user's terminal-only clarification. The earlier guess service, route and field were removed. No separate teaching execution path remains.

## Learner-facing evidence

Screenshots in `evidence/` were captured from the running Vite frontend on port 5175 and Django API on port 8015, using an isolated SQLite database under the system temporary directory. No production learner data was changed.

- `01-initial-introduction.png`: contextual reading with only the ordinary terminal input.
- `02-wrong-terminal-command.png`: actual `git start` command produces normal terminal failure and reveals `git init` with repository explanation.
- `03-init-and-next-lesson.png`: actual init creates .git metadata and unborn main reference, zero commits, and selects staging next.
- `04-staging-feedback.png`: README.md moves into staging; the diagram still has no commits; useful selective staging is accepted.
- `05-commit-feedback-before-outcome.png`: final commit succeeds and the tutorial explains its effect before the result dialog. After acknowledgment, the level completion dialog appears.
- `06-hard-first-encounter.png`: learner2 receives an independent first encounter on Hard after skipping the existing UI tour. This capture predates the later overlay presentation change. This capture also verifies the final folder centering correction.

Learner1's actual terminal sequence was `git start`, `git init`, `git add README.md`, `git add app.py`, `git commit -m "Save work"`. The persisted run has status completed, 5 attempts and 5 counted actions, exactly 1 commit, empty staging, and only draft.txt left in working changes. The database contains exactly the three completed concepts for learner1. A reload after staging acknowledgment did not repeat that introduction; learner2 still received initialization.

Additional final browser checks:

- `07-shared-diagram-smoke.png`: actual shared LiveDagPanel rendered outside Adventure in 340x320 and 520x520 containers, with centered folder and commit history plus configuration. Both graph and repository-state views remain visible. The temporary smoke page was removed after capture.
- `08-pending-feedback-after-status.png`: Hard learner enters git init followed by git status without acknowledging; initialization feedback remains. The database confirms 2 attempts, 1 counted command and pending git-init/current-directory, so normal diagnostic accounting is preserved.
- `09-reload-does-not-repeat-init.png`: after acknowledgment and reload, the learner receives staging context rather than another initialization tutorial.

## Supporting checks

- Backend: `python -m pytest tutoring/tests adventures/tests simulator/tests -q` — **70 passed** (536.16 seconds).
- Frontend: focused CommandIntroductionPanel, RepositoryStateMap, LiveDagPanel, TierWorkspace/TierRun suites — **17 passed**. New empty-repository viewport tests — **3 passed**. The diagram/panel subset was rerun after the centering correction — **13 passed**.
- Frontend production build, TypeScript and ESLint passed. Final production build after the centering correction also passed (17.99 seconds); focused ESLint on the final changed files passed.
- Ruff on new tutoring code and changed backend integration passed. `makemigrations --check --dry-run` reports no changes. Both migrations applied successfully to the disposable acceptance database. The existing local development database also has both tutoring migrations applied.
- `git diff --check` passed. Generated API types include the completion operation and nullable tutor response. No guess API remains.
- Full quality guard runner still reports baseline failures: existing frontend oversized modules/dev fixture folder/HomeLoadoutView, existing Story schema boundary mismatch, admin adapter ORM reads, oversized admin CSS, missing admin KPI response schema, and manual admin KPI types. The named source files are unchanged from HEAD, and the generated Story schema is identical to HEAD. Legacy terms, curriculum layout/2056 target checks, generated API usage, docs, CI manifest, and artifact checks pass.

## Review record

- Explorer and PRE plan review completed before implementation.
- Correctness review findings were fixed: init branch/directory validation, detached/unsupported commit constraints, extra branch-tip requirements, and pending feedback being replaced before acknowledgment. Reviewer rechecked the pending-feedback correction and reported no remaining blocking findings.
- Maintainer review reported no actionable findings. The earlier cache/bootstrap acknowledgment issue was corrected using the existing cache helper. Shared diagram sizing and final browser proof were subsequently captured below.
- POST review: **aligned**, no blocker/major drift. Its stale execution-board minor was resolved by rewriting this record.
- Final independent verifier: **acceptance supported**, no acceptance blocker; inspected all six initial screenshots and focused persistence tests. Subsequent shared-component and reload captures below close the remaining visual evidence requests.

## Explicit limits

Deep state-effect verification covers initialization in the current directory, selective staging, and normal message commits for supported rule-based Adventure tier goals. First-encounter syntax guidance additionally covers every published, playable command form attached to the current wave. Generic guidance verifies successful use of an authored form but never claims that form solved the level; grading remains state-based. Diagram state views are shared by LiveDagPanel consumers. The configured development database was verified as local SQLite with DEBUG enabled. Its pending tutoring migration was applied; no production migration, deployment, mastery backfill, or unrelated baseline cleanup was performed.

## Command-form coverage revision

The tutorial response now carries the unseen forms for the selected command family. The workspace card shows each usage shape and label, explicitly asks the learner to choose from the task plus live repository state, and states that multiple routes may work. Acknowledging feedback records every form displayed in that guide, preventing repeated popups while allowing genuinely new forms introduced later to receive their own first encounter.

Form matching supports placeholders, optional operands, variadic path lists, inline placeholders, and common equivalent Git option spellings such as `git add -A` / `git add --all` and `git diff --staged` / `git diff --cached`. Reference-only forms remain excluded. Complex states that the contextual init/add/commit planner deliberately declines are not overridden by a generic suggestion.

## Onboarding-style overlay revision

The final UI uses `GameplayWorkspaceTour` for the first-encounter card, spotlight, scrim, connector and responsive placement. The introduction targets the ordinary terminal input; after a command, feedback targets the repository diagram. The battle stage stays mounted under the overlay. The terminal remains executable, and wrong commands retain normal penalties. One-step tutorial controls omit the tour progress bar; hiding an introduction does not complete it. Feedback has an acknowledgment action. On mobile, the card keeps its action visible and uses a full scrim when the target is offscreen.

- `10-overlay-introduction.png`: Hard-mode staging introduction spotlights the terminal input.
- `11-overlay-feedback.png`: an actual invalid terminal command brings up the answer and explanation beside the highlighted repository diagram.
- `12-overlay-mobile-feedback.png`: 390 px viewport with a visible acknowledgment action and repository state below the overlay card.

Targeted CommandIntroductionPanel, GameplayWorkspaceTour and TierWorkspace tests pass (18 tests). TypeScript and frontend production build were rerun after this presentation change. Backend teaching behavior and migrations did not change.

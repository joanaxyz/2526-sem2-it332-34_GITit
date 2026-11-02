# Contextual First-Encounter Teaching

## Revision 2026-09-27: one form, when the problem needs it

The user clarified the intent: introduce a command form only when the problem's next useful move needs a form the learner has never used, one form at a time, for any seeded or authored problem. This supersedes the wave-form grouping ("Meet git X" with every form) and the hand-modelled init/add/commit planner described below, both removed.

- The next move comes from the variant's generated `solution_trajectory` (see ARCHITECTURE.md, Command Introductions), not per-command rules. Off-route repositories get no lesson.
- Lessons are keyed by form syntax; a form counts as known after a completed introduction, a mastery solve, or any successful use.
- Diagnostic solution steps are never introduced.
- The payload carries one `command_form`; the concrete solution command is revealed only after a missed attempt.

## Intent and accepted scope

Teach a command concept when the learner first needs it in the actual repository, across variants, without prescribing a fixed solution sequence. Main was fast-forwarded from `2dade95` to `040b355` before implementation.

The user's implementation clarification supersedes the original prediction design: there is no separate guess field, no dry-run teaching endpoint, and no free attempt. The learner reads a short introduction and uses the normal terminal. Wrong commands use normal penalties (explicitly confirmed by the user), reveal a useful example when still valid, and explain its repository effect. Correct commands explain the actual change. Teaching appears in the existing onboarding-style spotlight overlay, independently of difficulty-based diagram/context scaffolding. The introduction highlights the ordinary terminal; feedback highlights the repository diagram.

The state-verified capability slice remains current-directory initialization, selective file staging, and normal message commits in Adventure tiers. The first-encounter registry now also covers every published, playable command form attached to the current wave. Those broader introductions teach the authored syntax and verify that the learner successfully used that form; the normal evaluator remains solely responsible for whether the resulting repository solves the level. Ambiguous objectives therefore receive syntax guidance without being collapsed into a prescribed solution.

## Ownership and contract

- Backend tutoring owns canonical concept identity, candidate selection, verified-effect feedback, and completion persistence.
- `PlayerCommandIntroduction` is a per-player/per-concept boolean represented by record existence, with a completion timestamp. It survives run/form deletion and is separate from mastery and variant encounter counts. A counter provides no extra value for the current once-only behavior.
- `PendingCommandIntroduction` stores unacknowledged feedback for one run. It is not learner mastery or an encounter count.
- Existing browser Git simulation, backend transition verification, command accounting, evaluation, rewards, and command logs remain authoritative. Teaching observes that single execution path.
- Full and compact tier payloads include an explicit nullable `tutor`. Generated API types define the frontend contract.
- The only dedicated write endpoint is `POST /api/adventure-tier-runs/{id}/introduction/complete/`. Signed feedback tokens bind player, run, variant, objective, command revision, and repository fingerprint. Run ownership and row locking apply; duplicate acknowledgment is idempotent. Final-command feedback can be acknowledged after the run ends.

## Behavior

1. Derive the next useful capability from the current repository, objective rules, command history, and playable forms attached to the wave. Apply prerequisites before looking up completion; never skip a known necessary step to teach a later unseen command. Forms outside the deeply modelled init/add/commit slice are state-gated but never presented as the unique next step.
2. Show a short context explanation for an unseen supported capability. The regular terminal remains available. Hiding the introduction does not complete it.
3. Process input through the existing terminal command path. Deeply modelled capabilities require a verified useful effect; other command forms require a successful processed command matching the authored syntax shape. In both cases, level completion remains state-based. Equivalent useful choices and common Git option aliases are accepted. A different mutating route triggers replanning rather than revealing an obsolete example.
4. Keep unacknowledged feedback across reloads and further terminal submissions, updating its binding. Correcting a revealed command updates its feedback. If the repository changes along another route, withdraw the old example rather than presenting it as currently valid.
5. Acknowledge to persist completion and derive the next context. Cache and session bootstrap are updated together. Old in-flight acknowledgments cannot clear a newer lesson.
6. UI tours take precedence. Teaching uses the workspace tour overlay and defers contextual hints to avoid competing explanations, but its visibility never depends on difficulty scaffolding. The card leaves the highlighted terminal usable; feedback remains visible until acknowledged. Final feedback is read before the outcome dialog.

## Repository diagram

Extend the shared LiveDagPanel using the existing repository snapshot. Show ordinary folder versus initialized .git metadata, working changes, staging, references, remotes, stash, configuration, and conflicts alongside commit history. Before initialization, show a project folder rather than a fictitious HEAD/branch. Initialization creates metadata and an unborn branch reference, never a fake commit. Staging changes the index display without adding a commit node. Preserve optional snapshot metadata during graph normalization.

## Cutover and forbidden moves

The initial guess component, guess service, and guess API were removed during implementation. There is one terminal execution path and one backend teaching planner. No new Git interpreter, solution_commands indexing, changed grading, mastery reuse, local-storage teaching truth, or default answer for unsupported objectives is allowed. Existing UI tours, drills, and mastery retain their roles.

## Acceptance and gates

Use disposable learner data for real browser proof: introduction without another input, incorrect terminal command with a normal penalty, reveal and acknowledgment, init metadata change without commits, selective staging, commit feedback before completion, reload persistence, and first encounter on harder difficulty. Automated tests additionally cover alternate variants/accounts, stale tokens/file edits, forged transitions, unsupported goals, prerequisites, and pending feedback preservation.

Main agent owns all implementation. Explorer/PRE plan review completed before implementation. POST review, correctness review, maintainer review, and target-perspective verification are required. Evidence and actual check outcomes are recorded in EXECUTION.md. Do not claim proof from tests alone.

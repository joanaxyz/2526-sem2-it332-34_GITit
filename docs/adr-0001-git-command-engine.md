# ADR 0001: Simulated Git Command Engine Strategy

## Status

Accepted, revised May 2026.

## Context

GIT it! is a teaching environment, not a hosted shell. Student commands must stay deterministic, safe, and aligned with authored curriculum states. The backend stores compact scenario JSON for commits, refs, index entries, working-tree changes, remotes, reflog, and operation metadata.

The simulator is therefore the production source of command behavior. It may use helpers to normalize or snapshot authored state, but production command submission must not require Git to be installed and must not execute Git processes.

## Decision

Keep production command execution fully simulated:

1. Parse raw input with a safe Git command parser.
2. Map syntax variants to command intents.
3. Apply the relevant simulated command handler to the teaching state.
4. Format high-fidelity Git-like terminal output for supported curriculum commands.
5. Evaluate completion from the resulting state or, for diagnostic scenarios, from inspection intent metadata.

The simulator targets high-fidelity behavior for supported curriculum command families. It does not claim complete compatibility with every Git command or every Git version.

## Safety Boundary

The browser terminal must not become arbitrary server execution. Production command processing rejects:

- non-Git commands
- shell chaining and pipes
- redirects
- command substitution
- unsupported Git command families or options

Rejected commands return Git-like errors instead of server errors.

## Runtime Shape

Command submission remains synchronous and deterministic for scenario-scale work:

1. DRF validates the session and command text.
2. `GitCommandParser` parses and normalizes safe Git input.
3. `CommandIntentMapper` converts aliases/options into simulator operations.
4. A command-family handler mutates the simulated repository state.
5. A formatter module produces Git-like stdout/stderr and exit code metadata.
6. The evaluator checks the target state or diagnostic/inspection requirements.

## Optional Development Comparison

Development-only tests may compare simulator output against a local Git installation when one is available. Those tests must be optional and skipped when Git is missing. They must not introduce production executor classes/settings, per-session real repository workspaces, or Git process execution in command submission.

## Consequences

- The simulator remains the source of truth for production command behavior.
- Adding command variants should happen by extending parser support, intent mapping, command handlers, and output formatters.
- The backend server does not need Git installed for students to use the app.
- Output should be realistic and consistent for supported curriculum commands, while unsupported Git behavior remains explicitly out of scope.

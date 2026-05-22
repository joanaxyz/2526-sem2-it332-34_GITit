# ADR 0001: Git Command Engine Strategy

## Status

Accepted.

## Context

The current scenario workspace uses an in-process repository-state simulator. It is deterministic and safe, but it is also a growing reimplementation of Git behavior. That is a poor long-term fit if the product goal is broad Git command coverage.

`pygit2` is already installed and should become the primary Git semantics layer for runtime command processing. It gives the backend direct libgit2 access without spawning a shell for ordinary repository operations.

## Decision

Move toward a hybrid command engine:

1. Use a pygit2-backed command engine to materialize each authored scenario state into an isolated Git workspace.
2. Run student `git ...` porcelain through the Git executable without a shell so terminal output matches real Git instead of hand-authored simulator messages.
3. Keep the existing compact scenario JSON as the durable teaching state while the pygit2 snapshotter expands coverage for index/worktree/remotes.
4. Keep evaluation behind a separate completion strategy so command execution is not mixed with state-based vs inspection-based scoring.
5. Run slow or remote-capable operations through queued workers once the product enables broader command coverage beyond local scenario-scale commands.

## Why Commands Still Need a Safety Boundary

The product should teach and accept broad Git usage, but a browser terminal must not become arbitrary server execution.

Git commands can trigger or depend on:

- hooks and configured helpers
- credential helpers
- local filesystem paths
- remote URLs and network access
- submodules, filters, smudge/clean drivers, and external diff/merge tools
- shell parsing if commands are handed to a subprocess

`pygit2` helps because it exposes Git operations as library calls instead of shelling out. It does not remove the need to decide which operations are allowed, which are queued, which need network isolation, and which are out of scope for a student session.

## Runtime Shape

Command submission should become asynchronous:

1. DRF validates the session and command text.
2. The command engine parses only enough to confirm it is a Git command and to avoid shell execution.
3. pygit2 materializes the authored state into a temporary workspace, including commits, refs, index, working tree, and local fake remotes.
4. The Git executable runs inside that workspace with prompts, pagers, editors, and global config disabled.
5. The service stores real terminal output, advances the compact teaching state, and evaluates completion through the appropriate strategy.
6. The frontend receives a single command response today; the same boundary can move to SSE/WebSocket or polling when commands become queued jobs.

Fast local commands can complete quickly, but the interface should still use the same job/event model. That keeps `clone`, `fetch`, `pull`, large diffs, and conflict operations from blocking web workers.

## Migration Plan

1. Keep the simulator available as the deterministic state-transition fallback and seed compiler.
2. Use the pygit2 materializer and local Git runner for runtime terminal output.
3. Expand the pygit2 snapshotter until it can replace simulator state transitions category by category.
4. Move remote-capable and long-running commands into queued isolated workers before enabling them broadly.

## Consequences

- The current simulator should not grow into a full Git clone.
- pygit2 should be kept and optimized into the command engine.
- Safe parsing is not a product compromise; it is what lets the product support broad Git behavior without exposing the backend host.
- Some commands may still need sandboxed `git` subprocess execution because libgit2 does not implement every porcelain behavior. Those commands should run only in an isolated worker with network and filesystem controls.

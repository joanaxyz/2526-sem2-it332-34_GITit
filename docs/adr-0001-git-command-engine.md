# ADR 0001: Git Command Engine Strategy

## Status

Accepted.

## Context

The current scenario workspace uses an in-process repository-state simulator. It is deterministic and safe, but it is also a growing reimplementation of Git behavior. That is a poor long-term fit if the product goal is broad Git command coverage.

`pygit2` is already installed and should become the primary Git semantics layer for runtime command processing. It gives the backend direct libgit2 access without spawning a shell for ordinary repository operations.

## Decision

Move toward a hybrid command engine:

1. Use a pygit2-backed runtime engine for real repository state transitions.
2. Keep the existing simulator as a deterministic fallback, demo engine, and fixture/compiler aid during migration.
3. Keep an application-owned command parser and safety policy in front of any Git engine.
4. Run slow or remote-capable operations through queued workers, not inside DRF request handlers.

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
2. The command is parsed into an internal command model.
3. The API persists a command job and immediately returns `accepted`.
4. A worker runs the command against an isolated repository workspace.
5. The worker writes terminal output, state snapshots, and evaluation results.
6. The frontend receives progress through SSE/WebSocket or polls a command status endpoint.

Fast local commands can complete quickly, but the interface should still use the same job/event model. That keeps `clone`, `fetch`, `pull`, large diffs, and conflict operations from blocking web workers.

## Migration Plan

1. Keep the simulator as the default engine while latency hot paths are fixed.
2. Add a pygit2 materializer that can turn authored scenario JSON into an isolated Git repository.
3. Add a pygit2 snapshotter that maps libgit2 repository state back into the UI's DAG/status schema.
4. Route a small command subset through pygit2 behind the same command-engine interface.
5. Expand command coverage by category: status/log/diff, add/restore, commit/branch/switch/checkout, merge/rebase/cherry-pick/revert, remote operations.
6. Move remote-capable commands into queued isolated workers before enabling them broadly.

## Consequences

- The current simulator should not grow into a full Git clone.
- pygit2 should be kept and optimized into the command engine.
- Safe parsing is not a product compromise; it is what lets the product support broad Git behavior without exposing the backend host.
- Some commands may still need sandboxed `git` subprocess execution because libgit2 does not implement every porcelain behavior. Those commands should run only in an isolated worker with network and filesystem controls.

# Repository State Evaluator V2 Audit

This note captures the pre-refactor behavior that motivated the canonical state model.

- `repository_state` already contained commits, branches, HEAD, staging, working tree, conflicts, remotes, remote branches, upstream tracking, stash, reflog, partial hunks, and initialization state.
- Commits were mostly graph nodes with `id`, `message`, `parents`, and an ambiguous `files` map. The map acted like "paths changed by this commit", not a full committed tree.
- Legacy `target_rule` checks covered broad facts: required/forbidden commands, branch presence and tips, current branch, clean working tree, empty staging, remotes, stash emptiness, reflog text, and a shallow latest-commit path/message check.
- `expected_state_diagram` was generated from the target state, but the frontend type narrowed it to only commits, branches, and HEAD.
- `LiveDagPanel` rendered local branch refs and HEAD on commit circles, but omitted commit trees, change records, remote refs, staging, working tree, conflicts, remotes, stash, and rule-match diagnostics.
- Diagnostic commands remain read-only, non-counted commands inside normal state-based scenarios; separate inspection-completion scenarios are deprecated.

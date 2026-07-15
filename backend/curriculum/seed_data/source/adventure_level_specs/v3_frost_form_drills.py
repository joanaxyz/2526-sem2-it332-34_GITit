"""Frostbound Citadel form drills: solo intros + applied recurrence waves.

Every playable Frostbound command form gets a dedicated SOLO intro wave
(single-command solution, two variants) placed at its first use in play order,
followed by applied multi-command workflow waves that re-exercise it alongside
the arcane core loop (status + graph log). Chapter incident levels then provide
the capstone appearances for each chapter's diagnostic form.

Authoring rules honored here:
- Story briefs are plain language: they say exactly what happened and what is
  needed, and they name every literal the learner must type (branch names,
  commit messages, tags, files). Values that differ per variant are surfaced
  in Copy details, which the brief points at.
- Copy details are bare copyable values (the frontend shows no labels).
- A wave never tags a form taught in an earlier story unless that story
  already meets the form's capped mastery target (the only earlier-story tags
  used are arcane core forms with ten or more arcane waves against the cap).
"""

from __future__ import annotations

from .common import commit, ev, q, repo, v
from .v3_advanced_workflows import _state

CORE_TAGS = ["git-status/plain", "git-log/graph-all"]
STATUS = "git status"
GRAPH = "git log --oneline --graph --all"


# ---------------------------------------------------------------------------
# Fixtures (two variants per wave via distinct commit-id prefixes m/n)
# ---------------------------------------------------------------------------

def _clean(p: str) -> dict:
    return _state(p, mode="transplant")


def _work(p: str) -> dict:
    return _state(p, mode="author")


def _broken(p: str) -> dict:
    return _state(p, mode="revert")


def _dirty(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["working_tree"] = {
        "src/app.ts": {"status": "modified", "content": "export const mode = 'patched'\n"}
    }
    return state


def _broken_dirty(p: str) -> dict:
    state = _state(p, mode="revert")
    state["working_tree"] = {
        "src/app.ts": {"status": "modified", "content": "export const mode = 'field-patch'\n"}
    }
    return state


def _staged(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["staging"] = {"src/notes.md": "release repair notes\n"}
    return state


def _stashed(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["stash_stack"] = [
        {
            "working_tree": {
                "src/hotfix.ts": {"status": "untracked", "content": "export const hotfix = true\n"}
            },
            "staging": {},
            "conflicts": [],
            "message": "hotfix draft",
        }
    ]
    return state


def _cherry_conflict(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["staging"] = {"src/relay.ts": {"status": "added", "content": "export const relay = 'half-picked'\n"}}
    state["cherry_pick_in_progress"] = True
    state["cherry_pick_original_head"] = f"{p}1"
    return state


def _conflict(p: str) -> dict:
    return repo(
        commits=[
            commit(f"{p}c0", "Create relay config", [], {"src/relay.conf": "load=low\nmode='shared'\n"}),
            commit(f"{p}m1", "Raise main load ceiling", [f"{p}c0"], {"src/relay.conf": "load=high\nmode='shared'\n"}),
            commit(f"{p}f1", "Adopt strict relay mode", [f"{p}c0"], {"src/relay.conf": "load=low\nmode='strict'\n"}),
        ],
        branches={"main": f"{p}m1", "team/strict-mode": f"{p}f1"},
        head="main",
        working_tree={
            "src/relay.conf": {
                "status": "conflicted",
                "content": "<<<<<<< HEAD\nload=high\nmode='shared'\n=======\nload=low\nmode='strict'\n>>>>>>> team/strict-mode",
            }
        },
        conflicts=["src/relay.conf"],
        merge_parent=f"{p}f1",
        conflict_details={
            "src/relay.conf": {
                "base": "load=low\nmode='shared'\n",
                "ours": "load=high\nmode='shared'\n",
                "theirs": "load=low\nmode='strict'\n",
                "merge_branch": "team/strict-mode",
            }
        },
        operation_metadata={"last_merge_branch": "team/strict-mode"},
    )


def _resolved_merge(p: str) -> dict:
    state = _conflict(p)
    state["working_tree"] = {}
    state["conflicts"] = []
    state["staging"] = {"src/relay.conf": "load=high\nmode='strict'\n"}
    return state


def _behind_remote(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["branches"]["main"] = f"{p}1"
    state["remote_branches"] = {"origin/main": f"{p}2"}
    return state


def _stale_remote(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["remote_branches"] = {
        "origin/main": state["branches"]["main"],
        "origin/old-experiment": f"{p}3",
    }
    state["remote_stale_branches"] = ["old-experiment"]
    return state


def _rebase_ready(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["head"] = {"type": "branch", "name": "feature/work"}
    return state


def _retire_remote(p: str) -> dict:
    """One remote branch to retire by hand plus a separate stale ref to prune."""
    state = _state(p, mode="transplant")
    state["remote_branches"] = {
        "origin/main": state["branches"]["main"],
        "origin/old-experiment": f"{p}3",
        "origin/tmp-probe": f"{p}4",
    }
    state["remote_stale_branches"] = ["tmp-probe"]
    return state


def _rebase_paused(p: str) -> dict:
    state = _state(p, mode="transplant")
    state["rebase_state"] = {
        "abort_state": _state(p, mode="transplant"),
        "remaining": [f"{p}3"],
        "applied": [],
    }
    return state


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _dv(slug, fixture, commands, evaluation, details=None):
    """Two variants (prefixes m/n) of one command sequence.

    ``commands``/``details`` may use {p} for the variant's commit-id prefix;
    ``evaluation`` is a callable(prefix) -> evaluation spec. Details are bare
    copyable values.
    """

    def render(p):
        return [c.replace("{p}", p) for c in commands]

    def dets(p):
        return [d.replace("{p}", p) for d in (details or [])]

    return [
        v(f"{slug}-a", "First team's repository", fixture("m"), render("m"), evaluation("m"), details=dets("m")),
        v(f"{slug}-b", "Second team's repository", fixture("n"), render("n"), evaluation("n"), details=dets("n")),
    ]


def _read_eval(commands, *, count=5):
    """Evaluation for read-only waves.

    Some diagnostics record metadata (e.g. last_rev_list_count), so
    repository_state_unchanged is too strict; an exact commit count pins the
    graph while tolerating diagnostic bookkeeping.
    """

    def build(p):
        return ev(
            {"rules": [{"type": "commit_count_equals", "count": count}]},
            required=[c.replace("{p}", p) for c in commands],
        )

    return build


def _req(requirements, commands, rules=None):
    def build(p):
        spec = {}
        for key, value in requirements.items():
            spec[key] = _render_value(value, p)
        if rules:
            spec["rules"] = [
                {k: _render_value(val, p) for k, val in rule.items()} for rule in rules
            ]
        return ev(spec, required=[c.replace("{p}", p) for c in commands])

    return build


def _render_value(value, p):
    if isinstance(value, str):
        return value.replace("{p}", p)
    if isinstance(value, dict):
        return {k: _render_value(val, p) for k, val in value.items()}
    if isinstance(value, list):
        return [_render_value(item, p) for item in value]
    return value


def _required_check(label, commands):
    return {"label": label, "requirement": {"required_commands": commands}}


def _meta(key, value):
    return {"type": "operation_metadata_equals", "key": key, "value": value}


def _meta_set(key):
    return {"type": "operation_metadata_not_equals", "key": key, "value": None}


# ---------------------------------------------------------------------------
# Chapter 1 - frost-temper-the-commit
# ---------------------------------------------------------------------------

TEMPER_DRILLS = [
    q(
        "git-diff/stat-advanced",
        "ft-intro-diff-stat",
        "Measure the pending change",
        "A teammate left an unstaged edit in src/app.ts and the reviewer wants to know how big it is before it goes anywhere.",
        "Show a per-file summary of how much the working tree has changed.",
        _dv("ft-intro-diff-stat", _dirty, ["git diff --stat"], _read_eval(["git diff --stat"])),
        checks=[_required_check("The change size was measured before staging.", ["git diff --stat"])],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
    ),
    q(
        "git-diff/check-whitespace",
        "ft-intro-diff-check",
        "Check the change for whitespace errors",
        "The editor that produced the pending src/app.ts change is known to add trailing whitespace. The reviewer will reject the change unless it is checked first.",
        "Check the working-tree changes for whitespace errors.",
        _dv("ft-intro-diff-check", _dirty, ["git diff --check"], _read_eval(["git diff --check"])),
        checks=[_required_check("The change was checked for whitespace errors.", ["git diff --check"])],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
    ),
    q(
        "git-add/patch-advanced",
        "ft-intro-add-patch",
        "Stage the change hunk by hunk",
        "Only part of the pending edit to src/app.ts was approved in review. Stage the file hunk by hunk so you choose exactly what goes into the next commit.",
        "Stage src/app.ts using hunk-level staging.",
        _dv(
            "ft-intro-add-patch",
            _dirty,
            ["git add -p src/app.ts"],
            _req({}, ["git add -p"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "The approved hunks are staged for the next commit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-add/tracked-only-advanced",
        "ft-intro-add-update",
        "Stage tracked edits only",
        "The working tree mixes an approved edit to the tracked file src/app.ts with scratch files that must stay out of history. Stage only what is already tracked.",
        "Stage every tracked edit without adding any untracked file.",
        _dv(
            "ft-intro-add-update",
            _dirty,
            ["git add -u"],
            _req({}, ["git add -u"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "Tracked edits are staged for the next commit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-intro-amend",
        "Rewrite the unpublished tip commit",
        "The latest commit has not been pushed yet: it is missing the staged release notes and its message is a placeholder. Rewrite it in place using the commit message 'Temper the relay tip'.",
        "Amend the latest commit so it includes the staged work and carries the message 'Temper the relay tip'.",
        _dv(
            "ft-intro-amend",
            _staged,
            ["git commit --amend -m 'Temper the relay tip'"],
            _req(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Temper the relay tip"]},
                    "staging_empty": True,
                },
                ["git commit --amend"],
            ),
        ),
        checks=[
            {
                "label": "The tip commit now carries the requested message.",
                "requirement": {
                    "latest_commit": {"branch": "main", "message_contains": ["Temper the relay tip"]}
                },
            }
        ],
        details=["Temper the relay tip"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-intro-amend-no-edit",
        "Fold staged work into the tip commit",
        "The staged file src/notes.md belongs to the commit already at the tip, and that commit's message is already correct. Fold the staged work in without changing the message.",
        "Amend the tip commit with the staged content while keeping its existing message.",
        _dv(
            "ft-intro-amend-no-edit",
            _staged,
            ["git commit --amend --no-edit"],
            _req(
                {
                    "latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]},
                    "staging_empty": True,
                },
                ["git commit --amend --no-edit"],
            ),
        ),
        checks=[
            {
                "label": "The staged file is folded into the existing tip commit.",
                "requirement": {"latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]}},
            }
        ],
        details=["src/notes.md"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/soft",
        "ft-intro-reset-soft",
        "Step the branch back, keep the work",
        "The commit at the tip of main broke the deployment, but its changes are still needed for rework. Move main back to the last good commit (its id is in Copy details) while keeping the changes.",
        "Soft-reset main to the last good commit so the work stays available for restaging.",
        _dv(
            "ft-intro-reset-soft",
            _broken,
            ["git reset --soft {p}1"],
            _req({}, ["git reset --soft"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[_required_check("The branch stepped back with the work preserved.", ["git reset --soft"])],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/mixed",
        "ft-intro-reset-mixed",
        "Step back and unstage everything",
        "The broken tip commit needs to be rebuilt from scratch, starting from an unstaged state. Move main back to the last good commit (see Copy details) and leave the changes unstaged.",
        "Mixed-reset main to the last good commit.",
        _dv(
            "ft-intro-reset-mixed",
            _broken,
            ["git reset --mixed {p}1"],
            _req({}, ["git reset --mixed"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[_required_check("The branch stepped back with nothing staged.", ["git reset --mixed"])],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/hard-advanced",
        "ft-intro-reset-hard",
        "Discard the broken state completely",
        "Both the broken tip commit and the local edits on top of it have been rejected. Nothing local is worth keeping: move main back to the last good commit (see Copy details) and discard everything else.",
        "Hard-reset main to the last good commit, discarding local edits.",
        _dv(
            "ft-intro-reset-hard",
            _broken_dirty,
            ["git reset --hard {p}1"],
            _req(
                {"working_tree_clean": True},
                ["git reset --hard"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            {
                "label": "The workspace is clean at the last good commit.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-restore/source-advanced",
        "ft-intro-restore-source",
        "Bring back one file from an old commit",
        "Today's src/app.ts is suspected of being wrong. Copy the version from the first commit (its id is in Copy details) into the working tree so the two versions can be compared. No branch should move.",
        "Restore src/app.ts from the old commit into the working tree.",
        _dv(
            "ft-intro-restore-source",
            _clean,
            ["git restore --source {p}0 src/app.ts"],
            _req({}, ["git restore --source"], rules=[{"type": "working_tree_dirty"}]),
            details=["{p}0", "src/app.ts"],
        ),
        checks=[
            {
                "label": "The old version of the file is in the working tree.",
                "requirement": {"rules": [{"type": "working_tree_dirty"}]},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-tag/lightweight-advanced",
        "ft-intro-tag-checkpoint",
        "Tag the known-good commit",
        "Before any history rewriting starts, the team wants the current trusted commit to have a name so later work can be compared against it. Create a lightweight tag called relay-checkpoint at the current commit.",
        "Create the lightweight tag relay-checkpoint at HEAD.",
        _dv(
            "ft-intro-tag-checkpoint",
            _clean,
            ["git tag relay-checkpoint"],
            _req({}, ["git tag"], rules=[_meta("last_tag_created", "relay-checkpoint")]),
        ),
        checks=[
            {
                "label": "The checkpoint tag exists at the trusted commit.",
                "requirement": {"rules": [_meta("last_tag_created", "relay-checkpoint")]},
            }
        ],
        details=["relay-checkpoint"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
]

TEMPER_WORKFLOWS = [
    q(
        "git-add/patch-advanced",
        "ft-apply-measured-staging",
        "Measure, then stage precisely",
        "A mixed edit to src/app.ts is waiting. Measure how big it is, stage only the approved hunks, then check the repository state to confirm the split.",
        "Measure the change, stage src/app.ts hunk by hunk, then verify with status and log.",
        _dv(
            "ft-apply-measured-staging",
            _dirty,
            ["git diff --stat", "git add -p src/app.ts", STATUS, GRAPH],
            _req({}, ["git diff --stat", "git add -p", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            _required_check("The change was measured before staging.", ["git diff --stat"]),
            {
                "label": "The approved hunks are staged.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-add/patch-advanced",
        "ft-apply-guarded-staging",
        "Check whitespace, then stage",
        "The pending src/app.ts edit came from an editor that mangles whitespace. Prove the change is clean, then stage it hunk by hunk and verify the state.",
        "Check for whitespace errors, stage src/app.ts hunk by hunk, then verify.",
        _dv(
            "ft-apply-guarded-staging",
            _dirty,
            ["git diff --check", "git add -p src/app.ts", STATUS, GRAPH],
            _req({}, ["git diff --check", "git add -p", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            _required_check("The change was checked for whitespace errors.", ["git diff --check"]),
            {
                "label": "The clean hunks are staged.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-diff/check-whitespace", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-add/tracked-only-advanced",
        "ft-apply-tracked-sweep",
        "Measure, then stage tracked edits",
        "Every tracked edit in the working tree is approved; nothing untracked is. Measure the pending work, stage the tracked edits only, and confirm the result.",
        "Measure the change, stage tracked edits only, then verify with status and log.",
        _dv(
            "ft-apply-tracked-sweep",
            _dirty,
            ["git diff --stat", "git add -u", STATUS, GRAPH],
            _req({}, ["git diff --stat", "git add -u", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            _required_check("The pending work was measured.", ["git diff --stat"]),
            {
                "label": "Tracked edits are staged; untracked files are not.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-apply-fold-and-rename",
        "Fold the fix into the tip commit",
        "A reviewed fix to src/app.ts belongs inside the unpublished tip commit, which also needs its real message. Check the change, stage the tracked edit, then rewrite the tip using the commit message 'Fold the field fix into the tip'.",
        "Check whitespace, stage tracked edits, then amend the tip with the message 'Fold the field fix into the tip'.",
        _dv(
            "ft-apply-fold-and-rename",
            _dirty,
            ["git diff --check", "git add -u", "git commit --amend -m 'Fold the field fix into the tip'", STATUS, GRAPH],
            _req(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Fold the field fix into the tip"]},
                    "working_tree_clean": True,
                    "staging_empty": True,
                },
                ["git diff --check", "git add -u", "git commit --amend", "git status", "git log"],
            ),
        ),
        checks=[
            _required_check("The change was checked before staging.", ["git diff --check"]),
            {
                "label": "The tip commit carries the fix and the requested message.",
                "requirement": {
                    "latest_commit": {"branch": "main", "message_contains": ["Fold the field fix into the tip"]}
                },
            },
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        details=["Fold the field fix into the tip"],
        command_forms=["git-add/tracked-only-advanced", "git-diff/check-whitespace", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-apply-clarify-tip",
        "Absorb staged notes and fix the message",
        "The tip commit has a placeholder message and the release notes are still only staged. Rewrite the tip so it absorbs the staged notes and carries the commit message 'Clarify the relay tip'.",
        "Amend the tip with the staged notes and the message 'Clarify the relay tip', then verify.",
        _dv(
            "ft-apply-clarify-tip",
            _staged,
            ["git diff --stat", "git commit --amend -m 'Clarify the relay tip'", STATUS, GRAPH],
            _req(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Clarify the relay tip"]},
                    "staging_empty": True,
                },
                ["git diff --stat", "git commit --amend", "git status", "git log"],
            ),
        ),
        checks=[
            {
                "label": "The tip commit carries the requested message.",
                "requirement": {"latest_commit": {"branch": "main", "message_contains": ["Clarify the relay tip"]}},
            },
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        details=["Clarify the relay tip"],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-apply-silent-fold",
        "Fold hunks in, keep the message",
        "The reviewed hunks of src/app.ts belong to the tip commit, whose message is already approved. Stage the hunks, then fold them in without changing the message.",
        "Stage src/app.ts hunk by hunk, amend without editing the message, then verify.",
        _dv(
            "ft-apply-silent-fold",
            _dirty,
            ["git add -p src/app.ts", "git commit --amend --no-edit", STATUS, GRAPH],
            _req(
                {"staging_empty": True},
                ["git add -p", "git commit --amend --no-edit", "git status", "git log"],
            ),
        ),
        checks=[
            _required_check(
                "The staged hunks were folded into the tip without renaming it.",
                ["git add -p", "git commit --amend --no-edit"],
            ),
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-add/patch-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-apply-checked-fold",
        "Check, then fold without renaming",
        "Staged notes in src/notes.md must join the tip commit unchanged. Check the pending state first, then fold the staged work in while keeping the approved message.",
        "Check whitespace, amend without editing the message, then verify the history.",
        _dv(
            "ft-apply-checked-fold",
            _staged,
            ["git diff --check", "git commit --amend --no-edit", STATUS, GRAPH],
            _req(
                {
                    "latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]},
                    "staging_empty": True,
                },
                ["git diff --check", "git commit --amend --no-edit", "git status", "git log"],
            ),
        ),
        checks=[
            {
                "label": "The staged notes are folded into the existing tip.",
                "requirement": {"latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]}},
            },
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        details=["src/notes.md"],
        command_forms=["git-diff/check-whitespace", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/soft",
        "ft-apply-soft-retreat",
        "Step back softly from the bad tip",
        "The broken commit at the tip still holds valuable changes. Measure the state, move main back to the last good commit (see Copy details) while keeping the work, then verify.",
        "Measure the state, soft-reset main to the last good commit, then verify.",
        _dv(
            "ft-apply-soft-retreat",
            _broken,
            ["git diff --stat", "git reset --soft {p}1", STATUS, GRAPH],
            _req({}, ["git diff --stat", "git reset --soft", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The branch stepped back with the work preserved.", ["git reset --soft"]),
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/soft",
        "ft-apply-layered-retreat",
        "Step back in two layers",
        "First step back softly to the last good commit to inspect what the broken tip held, then release the snapshot from staging by stepping back to the first commit with a mixed reset. Both commit ids are in Copy details.",
        "Soft-reset to the last good commit, then mixed-reset to the first commit, then verify.",
        _dv(
            "ft-apply-layered-retreat",
            _broken,
            ["git reset --soft {p}1", "git reset --mixed {p}0", STATUS, GRAPH],
            _req({}, ["git reset --soft", "git reset --mixed", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}0"}]),
            details=["{p}1", "{p}0"],
        ),
        checks=[
            _required_check("The branch stepped back in two deliberate layers.", ["git reset --soft", "git reset --mixed"]),
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-reset/mixed", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/mixed",
        "ft-apply-mixed-rework",
        "Unstage the broken commit for rework",
        "The broken tip commit needs a fresh file-selection pass. Measure it, move main back to the last good commit (see Copy details) with a mixed reset, then check what is left to restage.",
        "Measure the change, mixed-reset main to the last good commit, then verify.",
        _dv(
            "ft-apply-mixed-rework",
            _broken,
            ["git diff --stat", "git reset --mixed {p}1", STATUS, GRAPH],
            _req({}, ["git diff --stat", "git reset --mixed", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The commit was unstaged for rework.", ["git reset --mixed"]),
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/hard-advanced",
        "ft-apply-condemned-floor",
        "Discard the rejected work entirely",
        "Review rejected both the tip commit and every local edit on top of it. Check what would be lost, then hard-reset main to the last good commit (see Copy details) and confirm the workspace is clean.",
        "Check the pending edits, hard-reset to the last good commit, then verify a clean state.",
        _dv(
            "ft-apply-condemned-floor",
            _broken_dirty,
            ["git diff --check", "git reset --hard {p}1", STATUS, GRAPH],
            _req(
                {"working_tree_clean": True},
                ["git diff --check", "git reset --hard", "git status", "git log"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            {
                "label": "The workspace is clean at the last good commit.",
                "requirement": {"working_tree_clean": True},
            },
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/check-whitespace", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-restore/source-advanced",
        "ft-apply-recover-then-compare",
        "Reset hard, then recover one file",
        "After discarding the rejected work, one file is still needed from the first commit for comparison. Hard-reset to the last good commit, then restore src/app.ts from the first commit. Both ids are in Copy details.",
        "Hard-reset to the last good commit, restore src/app.ts from the first commit, then verify.",
        _dv(
            "ft-apply-recover-then-compare",
            _broken_dirty,
            ["git reset --hard {p}1", "git restore --source {p}0 src/app.ts", STATUS, GRAPH],
            _req(
                {},
                ["git reset --hard", "git restore --source", "git status", "git log"],
                rules=[
                    {"type": "branch_points_to", "branch": "main", "commit": "{p}1"},
                    {"type": "working_tree_dirty"},
                ],
            ),
            details=["{p}1", "{p}0", "src/app.ts"],
        ),
        checks=[
            _required_check("The workspace was reset, then one file recovered.", ["git reset --hard", "git restore --source"]),
            _required_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-reset/hard-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-restore/source-advanced",
        "ft-apply-foundation-audit",
        "Compare today's file with the original",
        "The team suspects src/app.ts has drifted from its original version. Restore the copy from the first commit (see Copy details) into the working tree, then measure exactly how different today's file is.",
        "Restore src/app.ts from the first commit, then measure the difference.",
        _dv(
            "ft-apply-foundation-audit",
            _clean,
            ["git restore --source {p}0 src/app.ts", "git diff --stat", STATUS, GRAPH],
            _req({}, ["git restore --source", "git diff --stat", "git status", "git log"], rules=[{"type": "working_tree_dirty"}]),
            details=["{p}0", "src/app.ts"],
        ),
        checks=[
            {
                "label": "The original version is in the working tree for comparison.",
                "requirement": {"rules": [{"type": "working_tree_dirty"}]},
            },
            _required_check("The difference was measured.", ["git diff --stat"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 2 - frost-choose-the-integration
# ---------------------------------------------------------------------------

CHOOSE_DRILLS = [
    q(
        "git-rev-list/revision-set",
        "fc-intro-rev-list-count",
        "Count the commits in a range",
        "Two teams disagree about how far main has moved since the project's first commit. Settle it with a number: count the commits reachable from main but not from the first commit (its id is in Copy details).",
        "Count the commits in the range between the first commit and main.",
        _dv(
            "fc-intro-rev-list-count",
            _broken,
            ["git rev-list --count {p}0..main"],
            _read_eval(["git rev-list --count {p}0..main"]),
            details=["{p}0..main"],
        ),
        checks=[_required_check("The commit range was counted before integrating.", ["git rev-list --count"])],
        adventure="frost-choose-the-integration-drills",
    ),
    q(
        "git-diff/three-dot",
        "fc-intro-three-dot",
        "Compare a branch from where it started",
        "A review must see the feature/work branch the way its author wrote it: compared against the point where it split from main, not against today's main. Use the three-dot comparison between main and feature/work.",
        "Compare feature/work against main starting from their common ancestor.",
        _dv(
            "fc-intro-three-dot",
            _clean,
            ["git diff main...feature/work"],
            _read_eval(["git diff main...feature/work"]),
        ),
        checks=[_required_check("The branch was compared from its starting point.", ["git diff main...feature/work"])],
        details=["main...feature/work"],
        adventure="frost-choose-the-integration-drills",
    ),
    q(
        "git-merge/no-ff-advanced",
        "fc-intro-merge-no-ff",
        "Merge with a visible merge commit",
        "Team policy says every integration must stay visible in history. Merge the branch feature/work into main so an explicit merge commit records the join, even though a fast-forward would be possible.",
        "Merge feature/work into main with an explicit merge commit.",
        _dv(
            "fc-intro-merge-no-ff",
            _clean,
            ["git merge --no-ff feature/work"],
            _req({}, ["git merge --no-ff"], rules=[{"type": "commit_count_equals", "count": 6}]),
        ),
        checks=[
            {
                "label": "An explicit merge commit records the integration.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            }
        ],
        details=["feature/work"],
        adventure="frost-choose-the-integration-drills",
        workflow=True,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-intro-merge-squash",
        "Squash a branch into one staged change",
        "The feature/work branch is full of noisy work-in-progress commits, and only its end result should enter review. Squash the branch into a single staged change without committing yet.",
        "Squash-merge feature/work so its combined change is staged, ready for one commit.",
        _dv(
            "fc-intro-merge-squash",
            _clean,
            ["git merge --squash feature/work"],
            _req({}, ["git merge --squash"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        details=["feature/work"],
        adventure="frost-choose-the-integration-drills",
        workflow=True,
    ),
]

CHOOSE_WORKFLOWS = [
    q(
        "git-merge/no-ff-advanced",
        "fc-apply-reviewed-join",
        "Review the branch, then merge visibly",
        "Before feature/work is admitted into main, read its changes from where it branched off, then merge it with an explicit merge commit and confirm the join in the history.",
        "Compare from the branch point, merge with an explicit merge commit, then verify.",
        _dv(
            "fc-apply-reviewed-join",
            _clean,
            ["git diff main...feature/work", "git merge --no-ff feature/work", STATUS, GRAPH],
            _req(
                {},
                ["git diff main...feature/work", "git merge --no-ff", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 6}],
            ),
        ),
        checks=[
            _required_check("The branch was reviewed from its starting point.", ["git diff main...feature/work"]),
            {
                "label": "An explicit merge commit records the join.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            },
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        details=["feature/work"],
        command_forms=["git-diff/three-dot", *CORE_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/no-ff-advanced",
        "fc-apply-counted-join",
        "Count the range, then merge visibly",
        "The reviewer wants numbers first: count how many commits main holds beyond the first commit (see Copy details), then merge feature/work with a visible merge commit and verify.",
        "Count the range, merge with an explicit merge commit, then verify the history.",
        _dv(
            "fc-apply-counted-join",
            _clean,
            ["git rev-list --count {p}0..main", "git merge --no-ff feature/work", STATUS, GRAPH],
            _req(
                {},
                ["git rev-list --count", "git merge --no-ff", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 6}],
            ),
            details=["{p}0..main", "feature/work"],
        ),
        checks=[
            _required_check("The commit range was counted first.", ["git rev-list --count"]),
            {
                "label": "An explicit merge commit records the join.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            },
        ],
        command_forms=["git-rev-list/revision-set", *CORE_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-apply-reviewed-squash",
        "Review, then squash to one change",
        "The team wants feature/work's result without its noisy commit history. Read the three-dot comparison first, then squash the branch into one staged change and check what is pending.",
        "Compare from the branch point, squash the branch, then verify the staged result.",
        _dv(
            "fc-apply-reviewed-squash",
            _clean,
            ["git diff main...feature/work", "git merge --squash feature/work", STATUS, GRAPH],
            _req(
                {},
                ["git diff main...feature/work", "git merge --squash", "git status", "git log"],
                rules=[{"type": "staging_not_empty"}],
            ),
        ),
        checks=[
            _required_check("The branch was reviewed from its starting point.", ["git diff main...feature/work"]),
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
        ],
        details=["feature/work"],
        command_forms=["git-diff/three-dot", *CORE_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-apply-counted-squash",
        "Count, then squash deliberately",
        "Numbers first, shape second: count the commits main holds beyond the first commit (see Copy details), then stage feature/work's entire result as one squashed change and check the pending state.",
        "Count the range, squash feature/work, then verify the staged result.",
        _dv(
            "fc-apply-counted-squash",
            _clean,
            ["git rev-list --count {p}0..main", "git merge --squash feature/work", STATUS, GRAPH],
            _req(
                {},
                ["git rev-list --count", "git merge --squash", "git status", "git log"],
                rules=[{"type": "staging_not_empty"}],
            ),
            details=["{p}0..main", "feature/work"],
        ),
        checks=[
            _required_check("The commit range was counted first.", ["git rev-list --count"]),
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
        ],
        command_forms=["git-rev-list/revision-set", *CORE_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 3 - frost-survive-the-conflict
# ---------------------------------------------------------------------------

def _conflict_read(slug, form, title, story, task, command, label):
    return q(
        form,
        slug,
        title,
        story,
        task,
        _dv(slug, _conflict, [command], _read_eval([command], count=3)),
        checks=[_required_check(label, [command])],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
    )


NO_MARKERS = {
    "type": "working_tree_excludes_tokens",
    "path": "src/relay.conf",
    "tokens": ["<<<<<<<"],
}

SURVIVE_DRILLS = [
    q(
        "git-merge-tree/branches",
        "fs-intro-merge-tree",
        "Preview a merge without running it",
        "Two branches are about to be integrated and the team wants to know in advance whether they collide. Preview how main and feature/work would combine, without touching the working tree.",
        "Preview the merge of main and feature/work.",
        _dv(
            "fs-intro-merge-tree",
            _clean,
            ["git merge-tree main feature/work"],
            _read_eval(["git merge-tree main feature/work"]),
        ),
        checks=[_required_check("The merge was previewed without changing anything.", ["git merge-tree"])],
        details=["main feature/work"],
        adventure="frost-survive-the-conflict-drills",
    ),
    _conflict_read(
        "fs-intro-ls-files-u",
        "git-ls-files/unmerged-advanced",
        "List the conflicted index entries",
        "A merge stopped on src/relay.conf. Before editing anything, list the unmerged index entries to see the base version and both sides laid out as stages.",
        "List the unmerged index entries for the conflicted file.",
        "git ls-files -u",
        "The conflict stages were inspected.",
    ),
    _conflict_read(
        "fs-intro-diff-base",
        "git-diff-conflict/base-advanced",
        "Compare the conflict against the base",
        "To judge both sides of the conflict fairly, first read how the conflicted src/relay.conf differs from the version both branches started from.",
        "Compare the conflicted file against the common ancestor version.",
        "git diff --base src/relay.conf",
        "The conflict was compared against its base.",
    ),
    _conflict_read(
        "fs-intro-diff-ours",
        "git-diff-conflict/ours-advanced",
        "Compare against our side",
        "Your own team's change raised the load setting in src/relay.conf. Read how the conflicted file differs from your side before deciding anything.",
        "Compare the conflicted file against our side.",
        "git diff --ours src/relay.conf",
        "Our side of the conflict was inspected.",
    ),
    _conflict_read(
        "fs-intro-diff-theirs",
        "git-diff-conflict/theirs-advanced",
        "Compare against their side",
        "The other team's change switched src/relay.conf to strict mode. Read how the conflicted file differs from their side before deciding anything.",
        "Compare the conflicted file against their side.",
        "git diff --theirs src/relay.conf",
        "Their side of the conflict was inspected.",
    ),
    q(
        "git-checkout-conflict/ours-advanced",
        "fs-intro-checkout-ours",
        "Resolve by taking our side",
        "The decision is made: the raised load setting must stay, and the other team's change will be re-applied later. Resolve the conflicted src/relay.conf by taking our side.",
        "Resolve the conflicted file by taking our side.",
        _dv(
            "fs-intro-checkout-ours",
            _conflict,
            ["git checkout --ours src/relay.conf"],
            _req({}, ["git checkout --ours"], rules=[NO_MARKERS]),
        ),
        checks=[
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            }
        ],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-checkout-conflict/theirs-advanced",
        "fs-intro-checkout-theirs",
        "Resolve by taking their side",
        "Analysis shows the other team was right about this file. Resolve the conflicted src/relay.conf by taking their side.",
        "Resolve the conflicted file by taking their side.",
        _dv(
            "fs-intro-checkout-theirs",
            _conflict,
            ["git checkout --theirs src/relay.conf"],
            _req({}, ["git checkout --theirs"], rules=[NO_MARKERS]),
        ),
        checks=[
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            }
        ],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-intro-merge-abort",
        "Abort the conflicted merge",
        "New instructions arrived in the middle of the merge: this integration must not happen today. Abort the conflicted merge and return the workspace to the state it had before the merge started.",
        "Abort the in-progress merge safely.",
        _dv(
            "fs-intro-merge-abort",
            _conflict,
            ["git merge --abort"],
            _req({"working_tree_clean": True}, ["git merge --abort"]),
        ),
        checks=[
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-intro-merge-continue",
        "Finish the resolved merge",
        "The conflicted file has already been resolved and staged; only the merge commit is missing. Continue the merge so the resolution becomes a commit.",
        "Continue the resolved merge to create the merge commit.",
        _dv(
            "fs-intro-merge-continue",
            _resolved_merge,
            ["git merge --continue"],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git merge --continue"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            }
        ],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
]

SURVIVE_WORKFLOWS = [
    q(
        "git-checkout-conflict/ours-advanced",
        "fs-apply-hold-the-ceiling",
        "Inspect the conflict, then keep our change",
        "Read the unmerged index entries and our side's difference, then resolve src/relay.conf by keeping your team's raised load setting. Check the workspace afterward.",
        "Inspect the stages and our side, take our side, then verify the state.",
        _dv(
            "fs-apply-hold-the-ceiling",
            _conflict,
            ["git ls-files -u", "git diff --ours src/relay.conf", "git checkout --ours src/relay.conf", STATUS, GRAPH],
            _req({}, ["git ls-files -u", "git diff --ours", "git checkout --ours", "git status", "git log"], rules=[NO_MARKERS]),
        ),
        checks=[
            _required_check("The conflict evidence was read first.", ["git ls-files -u", "git diff --ours"]),
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-ls-files/unmerged-advanced", "git-diff-conflict/ours-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-checkout-conflict/theirs-advanced",
        "fs-apply-adopt-strict-mode",
        "Inspect the conflict, then adopt their change",
        "Read the unmerged index entries and their side's difference, then resolve src/relay.conf by adopting the other team's strict-mode change. Check the workspace afterward.",
        "Inspect the stages and their side, take their side, then verify the state.",
        _dv(
            "fs-apply-adopt-strict-mode",
            _conflict,
            ["git ls-files -u", "git diff --theirs src/relay.conf", "git checkout --theirs src/relay.conf", STATUS, GRAPH],
            _req({}, ["git ls-files -u", "git diff --theirs", "git checkout --theirs", "git status", "git log"], rules=[NO_MARKERS]),
        ),
        checks=[
            _required_check("The conflict evidence was read first.", ["git ls-files -u", "git diff --theirs"]),
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-ls-files/unmerged-advanced", "git-diff-conflict/theirs-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-apply-abort-after-base-check",
        "Check the base, then abort",
        "Compare the conflict against the common ancestor. The difference is too large to resolve safely under deadline, so abort the merge and confirm the workspace returned to its pre-merge state.",
        "Compare against the base, abort the merge, then verify the clean state.",
        _dv(
            "fs-apply-abort-after-base-check",
            _conflict,
            ["git diff --base src/relay.conf", "git merge --abort", STATUS, GRAPH],
            _req({"working_tree_clean": True}, ["git diff --base", "git merge --abort", "git status", "git log"]),
        ),
        checks=[
            _required_check("The conflict was compared against its base.", ["git diff --base"]),
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        command_forms=["git-diff-conflict/base-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-apply-seal-staged-resolution",
        "Confirm the state, then finish the merge",
        "The resolution is staged and waiting. Confirm the workspace state, continue the merge to create the merge commit, then read the history to prove the join landed.",
        "Verify the staged resolution, continue the merge, then confirm the merge commit.",
        _dv(
            "fs-apply-seal-staged-resolution",
            _resolved_merge,
            [STATUS, "git merge --continue", GRAPH],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git status", "git merge --continue", "git log"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            },
            _required_check("The resulting history was verified.", ["git log"]),
        ],
        command_forms=CORE_TAGS,
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-apply-full-resolution",
        "Resolve, stage, and finish",
        "Run the complete resolution: take our side of src/relay.conf, stage the resolved file, and continue the merge so the join enters history. Verify afterward.",
        "Take our side, stage the resolution, continue the merge, then verify.",
        _dv(
            "fs-apply-full-resolution",
            _conflict,
            ["git checkout --ours src/relay.conf", "git add src/relay.conf", "git merge --continue", STATUS, GRAPH],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git checkout --ours", "git add", "git merge --continue", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            _required_check("The conflict was resolved and staged.", ["git checkout --ours", "git add"]),
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-checkout-conflict/ours-advanced", "git-add/file", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-apply-stand-down",
        "Start resolving, then stand down",
        "Read the unmerged entries and provisionally take their side — then the integration is called off entirely. Abort the merge and confirm the workspace returned to its pre-merge state.",
        "Inspect the stages, take their side, then abort the merge and verify.",
        _dv(
            "fs-apply-stand-down",
            _conflict,
            ["git ls-files -u", "git checkout --theirs src/relay.conf", "git merge --abort", STATUS, GRAPH],
            _req(
                {"working_tree_clean": True},
                ["git ls-files -u", "git checkout --theirs", "git merge --abort", "git status", "git log"],
            ),
        ),
        checks=[
            _required_check("The conflict evidence was read first.", ["git ls-files -u"]),
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        command_forms=["git-ls-files/unmerged-advanced", "git-checkout-conflict/theirs-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-diff-conflict/base-advanced",
        "fs-apply-triangulate-base",
        "Read the conflict from base and their side",
        "Before deciding, read the conflict from two angles: how it differs from the common ancestor, and how it differs from the other team's version. Nothing may change yet.",
        "Read the base and their-side comparisons for the conflicted file.",
        _dv(
            "fs-apply-triangulate-base",
            _conflict,
            ["git diff --base src/relay.conf", "git diff --theirs src/relay.conf", STATUS, GRAPH],
            _read_eval(["git diff --base", "git diff --theirs", "git status", "git log"], count=3),
        ),
        checks=[
            _required_check(
                "The conflict was read from base and their side.",
                ["git diff --base", "git diff --theirs"],
            ),
        ],
        details=["src/relay.conf"],
        command_forms=["git-diff-conflict/theirs-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-diff-conflict/ours-advanced",
        "fs-apply-compare-both-sides",
        "Weigh both sides of the conflict",
        "Weigh your team's raised load setting against the other team's strict mode by reading both comparisons back to back. Nothing may change until the decision is recorded.",
        "Read the our-side and their-side comparisons for the conflicted file.",
        _dv(
            "fs-apply-compare-both-sides",
            _conflict,
            ["git diff --ours src/relay.conf", "git diff --theirs src/relay.conf", STATUS, GRAPH],
            _read_eval(["git diff --ours", "git diff --theirs", "git status", "git log"], count=3),
        ),
        checks=[
            _required_check(
                "Both sides of the conflict were weighed.",
                ["git diff --ours", "git diff --theirs"],
            ),
        ],
        details=["src/relay.conf"],
        command_forms=["git-diff-conflict/theirs-advanced", *CORE_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 4 - frost-move-the-patch
# ---------------------------------------------------------------------------

MOVE_DRILLS = [
    q(
        "git-range-diff/series",
        "fm-intro-range-diff",
        "Compare two versions of a patch series",
        "An older candidate branch and the current feature/work branch both claim to contain the same fix. Compare the two patch series (the exact ranges are in Copy details) to see how the fix evolved.",
        "Compare the old series against the current branch's series.",
        _dv(
            "fm-intro-range-diff",
            _clean,
            ["git range-diff {p}0..old/series {p}0..feature/work"],
            _read_eval(["git range-diff {p}0..old/series {p}0..feature/work"]),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[_required_check("The two patch series were compared.", ["git range-diff"])],
        adventure="frost-move-the-patch-drills",
    ),
    q(
        "git-stash/push-untracked-message",
        "fm-intro-stash-push",
        "Shelve unfinished work, untracked included",
        "An urgent task interrupts your unfinished work, which includes a brand-new untracked file. Stash everything — tracked and untracked — using the stash message 'Shelve relay draft'.",
        "Stash the local work, including untracked files, with the message 'Shelve relay draft'.",
        _dv(
            "fm-intro-stash-push",
            _work,
            ["git stash push -u -m 'Shelve relay draft'"],
            _req({}, ["git stash push -u"], rules=[_meta("last_stash_action", "push")]),
        ),
        checks=[
            {
                "label": "The draft is stashed with untracked work included.",
                "requirement": {"rules": [_meta("last_stash_action", "push")]},
            }
        ],
        details=["Shelve relay draft"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/show-patch",
        "fm-intro-stash-show",
        "Look inside a stash entry",
        "There is a stash entry called 'hotfix draft' and nobody remembers exactly what it holds. Inspect the entry stash@{0} before it is restored anywhere.",
        "Show the contents of the stash entry stash@{0}.",
        _dv(
            "fm-intro-stash-show",
            _stashed,
            ["git stash show stash@{0}"],
            _read_eval(["git stash show stash@{0}"]),
        ),
        checks=[_required_check("The stash entry was inspected before restoring.", ["git stash show"])],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
    ),
    q(
        "git-stash/apply-indexed",
        "fm-intro-stash-apply",
        "Restore stashed work, keep the copy",
        "The stashed hotfix is needed again, but the stash copy must survive in case this attempt fails. Apply the entry stash@{0} without removing it from the stash.",
        "Apply the stash entry stash@{0} while keeping it on the stash list.",
        _dv(
            "fm-intro-stash-apply",
            _stashed,
            ["git stash apply stash@{0}"],
            _req({}, ["git stash apply"], rules=[_meta("last_stash_action", "apply")]),
        ),
        checks=[
            {
                "label": "The stashed work is restored and the stash copy kept.",
                "requirement": {"rules": [_meta("last_stash_action", "apply")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-intro-stash-pop",
        "Restore stashed work and remove the entry",
        "The interruption is over for good. Restore the stashed hotfix and remove the entry from the stash in one step, using stash@{0}.",
        "Pop the stash entry stash@{0} back into the working tree.",
        _dv(
            "fm-intro-stash-pop",
            _stashed,
            ["git stash pop stash@{0}"],
            _req({}, ["git stash pop"], rules=[_meta("last_stash_action", "pop")]),
        ),
        checks=[
            {
                "label": "The stashed work is restored and the entry removed.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/drop-indexed",
        "fm-intro-stash-drop",
        "Delete a stale stash entry",
        "The stashed draft was replaced by a better fix that already landed. Drop the stale entry stash@{0} so nobody restores it by mistake.",
        "Drop the stash entry stash@{0}.",
        _dv(
            "fm-intro-stash-drop",
            _stashed,
            ["git stash drop stash@{0}"],
            _req({}, ["git stash drop"], rules=[_meta("last_stash_action", "drop")]),
        ),
        checks=[
            {
                "label": "The stale entry is gone from the stash.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-intro-cherry-abort",
        "Back out of a stuck cherry-pick",
        "A cherry-pick stopped halfway and the half-applied change sitting in staging is wrong for this branch. Abort the cherry-pick and return the branch to its original state.",
        "Abort the in-progress cherry-pick cleanly.",
        _dv(
            "fm-intro-cherry-abort",
            _cherry_conflict,
            ["git cherry-pick --abort"],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git cherry-pick --abort"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            }
        ],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
]

MOVE_WORKFLOWS = [
    q(
        "git-stash/push-untracked-message",
        "fm-apply-shelve-and-inspect",
        "Stash the work, then check the entry",
        "Stash the interrupted work — untracked file included — using the message 'Shelve probe wiring', then inspect the new entry to confirm it holds everything.",
        "Stash with the message 'Shelve probe wiring', inspect stash@{0}, then verify.",
        _dv(
            "fm-apply-shelve-and-inspect",
            _work,
            ["git stash push -u -m 'Shelve probe wiring'", "git stash show stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash push -u", "git stash show", "git status", "git log"],
                rules=[_meta("last_stash_action", "push")],
            ),
        ),
        checks=[
            {
                "label": "The work is stashed with untracked files included.",
                "requirement": {"rules": [_meta("last_stash_action", "push")]},
            },
            _required_check("The new stash entry was inspected.", ["git stash show"]),
        ],
        details=["Shelve probe wiring", "stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/apply-indexed",
        "fm-apply-inspect-then-apply",
        "Check the entry, then restore carefully",
        "Before the stashed hotfix goes back into the working tree, inspect the entry stash@{0}, apply it while keeping the stash copy, and confirm the restore landed.",
        "Inspect stash@{0}, apply it keeping the copy, then verify the state.",
        _dv(
            "fm-apply-inspect-then-apply",
            _stashed,
            ["git stash show stash@{0}", "git stash apply stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash show", "git stash apply", "git status", "git log"],
                rules=[_meta("last_stash_action", "apply")],
            ),
        ),
        checks=[
            _required_check("The entry was inspected before restoring.", ["git stash show"]),
            {
                "label": "The work is restored with the stash copy kept.",
                "requirement": {"rules": [_meta("last_stash_action", "apply")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-apply-park-and-pop",
        "Park the work, then take it back",
        "Park the in-progress work on the stash using the message 'Park the relay sweep', then take it straight back with a pop once the interruption clears. Confirm the stash is empty again.",
        "Stash with the message 'Park the relay sweep', pop stash@{0}, then verify.",
        _dv(
            "fm-apply-park-and-pop",
            _work,
            ["git stash push -u -m 'Park the relay sweep'", "git stash pop stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash push -u", "git stash pop", "git status", "git log"],
                rules=[_meta("last_stash_action", "pop")],
            ),
        ),
        checks=[
            _required_check("The work was parked on the stash.", ["git stash push -u"]),
            {
                "label": "The work is back and the stash entry is gone.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            },
        ],
        details=["Park the relay sweep", "stash@{0}"],
        command_forms=["git-stash/push-untracked-message", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/drop-indexed",
        "fm-apply-audit-then-drop",
        "Check the entry one last time, then delete it",
        "The stash entry stash@{0} is believed stale. Inspect it one last time, drop it, and confirm the working tree was never touched.",
        "Inspect stash@{0}, drop it, then verify the state.",
        _dv(
            "fm-apply-audit-then-drop",
            _stashed,
            ["git stash show stash@{0}", "git stash drop stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash show", "git stash drop", "git status", "git log"],
                rules=[_meta("last_stash_action", "drop")],
            ),
        ),
        checks=[
            _required_check("The entry was checked before deleting.", ["git stash show"]),
            {
                "label": "The stale entry is gone from the stash.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/apply-indexed",
        "fm-apply-restore-then-clear",
        "Restore the work, then clear the entry",
        "Apply the stashed hotfix from stash@{0} while keeping the copy, confirm the restore landed, then remove the now-redundant entry from the stash.",
        "Apply stash@{0}, then drop the stash copy, then verify the state.",
        _dv(
            "fm-apply-restore-then-clear",
            _stashed,
            ["git stash apply stash@{0}", "git stash drop stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash apply", "git stash drop", "git status", "git log"],
                rules=[_meta("last_stash_action", "drop")],
            ),
        ),
        checks=[
            _required_check("The work was restored before clearing the stash.", ["git stash apply"]),
            {
                "label": "The redundant stash entry is gone.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/drop-indexed", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-apply-inspect-then-pop",
        "Confirm the entry, then pop it",
        "The interruption is over. Inspect the stash entry stash@{0} to confirm it is the right one, then pop it back into the working tree and verify the restore.",
        "Inspect stash@{0}, pop it, then verify the state.",
        _dv(
            "fm-apply-inspect-then-pop",
            _stashed,
            ["git stash show stash@{0}", "git stash pop stash@{0}", STATUS, GRAPH],
            _req(
                {},
                ["git stash show", "git stash pop", "git status", "git log"],
                rules=[_meta("last_stash_action", "pop")],
            ),
        ),
        checks=[
            _required_check("The entry was confirmed before popping.", ["git stash show"]),
            {
                "label": "The work is restored and the entry removed.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-apply-inspect-then-back-out",
        "Confirm the damage, then back out",
        "Check what the stuck cherry-pick left in staging, then abort it and read the history to prove the branch returned to its original tip.",
        "Check the state, abort the cherry-pick, then verify the history.",
        _dv(
            "fm-apply-inspect-then-back-out",
            _cherry_conflict,
            [STATUS, "git cherry-pick --abort", GRAPH],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git status", "git cherry-pick --abort", "git log"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            },
            _required_check("The recovered history was verified.", ["git log"]),
        ],
        command_forms=CORE_TAGS,
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-apply-abort-under-orders",
        "Abort the cherry-pick immediately",
        "The transplant was called off mid-flight. Abort the cherry-pick right away, then check the workspace and history so the rollback can be reported.",
        "Abort the cherry-pick, then verify the workspace and history.",
        _dv(
            "fm-apply-abort-under-orders",
            _cherry_conflict,
            ["git cherry-pick --abort", STATUS, GRAPH],
            _req(
                {"working_tree_clean": True, "staging_empty": True},
                ["git cherry-pick --abort", "git status", "git log"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            },
            _required_check("The rollback was verified.", ["git status", "git log"]),
        ],
        command_forms=CORE_TAGS,
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 5 - frost-reforge-the-branch
# ---------------------------------------------------------------------------

REFORGE_DRILLS = [
    q(
        "git-rebase/branch",
        "fr-intro-rebase",
        "Rebase the branch onto today's main",
        "The branch feature/work was started from an old commit, and main has moved on since. You are on feature/work: replay its commits onto today's main so review sees one straight line of history.",
        "Rebase the current branch feature/work onto main.",
        _dv(
            "fr-intro-rebase",
            _rebase_ready,
            ["git rebase main"],
            _req({}, ["git rebase"], rules=[_meta("last_rebase_target", "main")]),
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            }
        ],
        details=["feature/work", "main"],
        adventure="frost-reforge-the-branch-drills",
        workflow=True,
    ),
    q(
        "git-rebase/abort",
        "fr-intro-rebase-abort",
        "Abort a rebase that went wrong",
        "A rebase stopped midway and the team no longer trusts the plan. Abort it and put the branch back exactly where it was before the rebase started.",
        "Abort the in-progress rebase safely.",
        _dv(
            "fr-intro-rebase-abort",
            _rebase_paused,
            ["git rebase --abort"],
            _req({}, ["git rebase --abort"], rules=[_meta("last_rebase_aborted", True)]),
        ),
        checks=[
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            }
        ],
        adventure="frost-reforge-the-branch-drills",
        workflow=True,
    ),
]

REFORGE_WORKFLOWS = [
    q(
        "git-rebase/branch",
        "fr-apply-rebase-and-compare",
        "Rebase, then prove nothing was lost",
        "Replay feature/work onto main, then compare the earlier candidate series against the rewritten branch (the ranges are in Copy details) to prove the patches kept their meaning.",
        "Rebase onto main, compare the patch series, then verify the history.",
        _dv(
            "fr-apply-rebase-and-compare",
            _rebase_ready,
            ["git rebase main", "git range-diff {p}0..old/series {p}0..feature/work", STATUS, GRAPH],
            _req(
                {},
                ["git rebase", "git range-diff", "git status", "git log"],
                rules=[_meta("last_rebase_target", "main")],
            ),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            },
            _required_check("The rewrite was checked with a series comparison.", ["git range-diff"]),
        ],
        command_forms=["git-range-diff/series", *CORE_TAGS],
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/branch",
        "fr-apply-survey-then-rebase",
        "Read the history, then rebase",
        "Read the commit graph before touching anything, replay feature/work onto main, then read the graph again so the before and after can be compared.",
        "Read the graph, rebase onto main, then verify the new shape.",
        _dv(
            "fr-apply-survey-then-rebase",
            _rebase_ready,
            [GRAPH, "git rebase main", STATUS, GRAPH],
            _req(
                {},
                ["git log", "git rebase", "git status"],
                rules=[_meta("last_rebase_target", "main")],
            ),
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            },
            _required_check("The new shape was verified.", ["git status", "git log"]),
        ],
        details=["main"],
        command_forms=CORE_TAGS,
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/abort",
        "fr-apply-compare-then-abort",
        "Compare the series, then call it off",
        "In the middle of the rebase, compare the old candidate series against the current branch (ranges in Copy details). The comparison shows the rewrite is drifting, so abort it and confirm the branch returned to its pre-rebase state.",
        "Compare the series, abort the rebase, then verify the state.",
        _dv(
            "fr-apply-compare-then-abort",
            _rebase_paused,
            ["git range-diff {p}0..old/series {p}0..feature/work", "git rebase --abort", STATUS, GRAPH],
            _req(
                {},
                ["git range-diff", "git rebase --abort", "git status", "git log"],
                rules=[_meta("last_rebase_aborted", True)],
            ),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[
            _required_check("The drift was measured before deciding.", ["git range-diff"]),
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            },
        ],
        command_forms=["git-range-diff/series", *CORE_TAGS],
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/abort",
        "fr-apply-stand-down-rewrite",
        "Abort the rebase and report",
        "The rewrite window was cancelled. Abort the paused rebase immediately, then check the workspace and history so the rollback can be reported.",
        "Abort the rebase, then verify the workspace and history.",
        _dv(
            "fr-apply-stand-down-rewrite",
            _rebase_paused,
            ["git rebase --abort", STATUS, GRAPH],
            _req(
                {},
                ["git rebase --abort", "git status", "git log"],
                rules=[_meta("last_rebase_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            },
            _required_check("The rollback was verified.", ["git status", "git log"]),
        ],
        command_forms=CORE_TAGS,
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 6 - frost-govern-the-remote
# ---------------------------------------------------------------------------

GOVERN_DRILLS = [
    q(
        "git-branch/tracking",
        "fg-intro-branch-vv",
        "Read the upstream tracking table",
        "Before anything is pulled or pushed, find out which local branches track which upstream branches and how far ahead or behind each one sits.",
        "Show upstream tracking information for every local branch.",
        _dv("fg-intro-branch-vv", _clean, ["git branch -vv"], _read_eval(["git branch -vv"])),
        checks=[_required_check("Upstream tracking was inspected.", ["git branch -vv"])],
        adventure="frost-govern-the-remote-drills",
    ),
    q(
        "git-fetch/all-advanced",
        "fg-intro-fetch-all",
        "Fetch from every remote",
        "Several remotes may hold newer work than your local copies show. Update the remote-tracking refs from every configured remote in one command.",
        "Fetch from all configured remotes.",
        _dv(
            "fg-intro-fetch-all",
            _clean,
            ["git fetch --all"],
            _req({}, ["git fetch --all"], rules=[_meta("last_fetch_all", True)]),
        ),
        checks=[
            {
                "label": "Every remote's refs were refreshed.",
                "requirement": {"rules": [_meta("last_fetch_all", True)]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-fetch/prune-advanced",
        "fg-intro-fetch-prune",
        "Fetch and remove stale tracking refs",
        "The branch old-experiment was deleted on the remote, but your repository still shows a tracking ref for it. Fetch with pruning so refs that no longer exist upstream disappear locally.",
        "Fetch updates and prune tracking refs that were deleted upstream.",
        _dv(
            "fg-intro-fetch-prune",
            _stale_remote,
            ["git fetch --prune"],
            _req({}, ["git fetch --prune"], rules=[_meta_set("fetch_pruned_refs")]),
        ),
        checks=[
            {
                "label": "Stale remote-tracking refs were pruned.",
                "requirement": {"rules": [_meta_set("fetch_pruned_refs")]},
            }
        ],
        details=["old-experiment"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-intro-pull-ff-only",
        "Pull only if it can fast-forward",
        "The remote has newer commits and your local main has none of its own. Pull with the fast-forward-only rule so the branch advances only if no merge commit would be invented.",
        "Pull upstream work using the fast-forward-only rule.",
        _dv(
            "fg-intro-pull-ff-only",
            _behind_remote,
            ["git pull --ff-only"],
            _req({}, ["git pull --ff-only"], rules=[_meta("pull_strategy", "ff-only")]),
        ),
        checks=[
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-intro-pull-rebase",
        "Pull with rebase",
        "The remote moved ahead while your local commits were in progress. Pull with the rebase rule so your local commits are replayed on top of the newer upstream history.",
        "Pull upstream work, replaying local commits on top.",
        _dv(
            "fg-intro-pull-rebase",
            _behind_remote,
            ["git pull --rebase"],
            _req({}, ["git pull --rebase"], rules=[_meta("pull_strategy", "rebase")]),
        ),
        checks=[
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-intro-push-lease",
        "Publish rewritten history safely",
        "A reviewed rewrite must replace the published branch — but only if nobody pushed something newer in the meantime. Push with the force-with-lease guard instead of a plain force.",
        "Publish the rewritten branch with force-with-lease.",
        _dv(
            "fg-intro-push-lease",
            _clean,
            ["git push --force-with-lease"],
            _req({}, ["git push --force-with-lease"], rules=[_meta("force_with_lease", True)]),
        ),
        checks=[
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-push/delete-advanced",
        "fg-intro-push-delete",
        "Delete a branch on the remote",
        "The experiment is finished and its published branch old-experiment must not attract new work. Delete that branch from the origin remote.",
        "Delete the branch old-experiment from origin.",
        _dv(
            "fg-intro-push-delete",
            _stale_remote,
            ["git push origin --delete old-experiment"],
            _req({}, ["git push origin --delete"], rules=[_meta("remote_branch_deleted", "old-experiment")]),
        ),
        checks=[
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            }
        ],
        details=["old-experiment"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-intro-set-url",
        "Point origin at a new URL",
        "The project's hosting moved to a new server. Change the origin remote's URL to https://relay.frost.test/operations.git so future syncs reach the right place.",
        "Change origin's URL to the new address.",
        _dv(
            "fg-intro-set-url",
            _clean,
            ["git remote set-url origin https://relay.frost.test/operations.git"],
            _req(
                {},
                ["git remote set-url"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the new address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}
                    ]
                },
            }
        ],
        details=["https://relay.frost.test/operations.git"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
]

GOVERN_WORKFLOWS = [
    q(
        "git-fetch/all-advanced",
        "fg-apply-survey-then-sweep",
        "Read tracking, then fetch everything",
        "Read the tracking table first, then refresh every remote's refs in one sweep and check what changed.",
        "Inspect tracking, fetch from all remotes, then verify the state.",
        _dv(
            "fg-apply-survey-then-sweep",
            _clean,
            ["git branch -vv", "git fetch --all", STATUS, GRAPH],
            _req(
                {},
                ["git branch -vv", "git fetch --all", "git status", "git log"],
                rules=[_meta("last_fetch_all", True)],
            ),
        ),
        checks=[
            _required_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Every remote's refs were refreshed.",
                "requirement": {"rules": [_meta("last_fetch_all", True)]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-fetch/prune-advanced",
        "fg-apply-clean-the-board",
        "Read tracking, then prune stale refs",
        "Read the tracking table, then fetch with pruning so the deleted old-experiment ref disappears, and confirm the cleaned picture.",
        "Inspect tracking, fetch with pruning, then verify the state.",
        _dv(
            "fg-apply-clean-the-board",
            _stale_remote,
            ["git branch -vv", "git fetch --prune", STATUS, GRAPH],
            _req(
                {},
                ["git branch -vv", "git fetch --prune", "git status", "git log"],
                rules=[_meta_set("fetch_pruned_refs")],
            ),
        ),
        checks=[
            _required_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Stale remote-tracking refs were pruned.",
                "requirement": {"rules": [_meta_set("fetch_pruned_refs")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-apply-guarded-advance",
        "Fetch everything, then pull safely",
        "Refresh every remote's refs, then advance main under the fast-forward-only rule and confirm the branch landed on the remote's newest commit.",
        "Fetch all remotes, pull with the fast-forward rule, then verify.",
        _dv(
            "fg-apply-guarded-advance",
            _behind_remote,
            ["git fetch --all", "git pull --ff-only", STATUS, GRAPH],
            _req(
                {},
                ["git fetch --all", "git pull --ff-only", "git status", "git log"],
                rules=[_meta("pull_strategy", "ff-only")],
            ),
        ),
        checks=[
            _required_check("The remote refs were refreshed first.", ["git fetch --all"]),
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-apply-replay-over-upstream",
        "Read tracking, then pull with rebase",
        "Read the tracking table, then pull with the rebase rule so local work is replayed over the remote's newer history. Confirm the straightened history afterward.",
        "Inspect tracking, pull with rebase, then verify the history.",
        _dv(
            "fg-apply-replay-over-upstream",
            _behind_remote,
            ["git branch -vv", "git pull --rebase", STATUS, GRAPH],
            _req(
                {},
                ["git branch -vv", "git pull --rebase", "git status", "git log"],
                rules=[_meta("pull_strategy", "rebase")],
            ),
        ),
        checks=[
            _required_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-apply-leased-publication",
        "Check tracking, then publish the rewrite",
        "Read the tracking table, publish the reviewed rewrite under the lease guard, and confirm the published state matches the local branch.",
        "Inspect tracking, push with force-with-lease, then verify.",
        _dv(
            "fg-apply-leased-publication",
            _clean,
            ["git branch -vv", "git push --force-with-lease", STATUS, GRAPH],
            _req(
                {},
                ["git branch -vv", "git push --force-with-lease", "git status", "git log"],
                rules=[_meta("force_with_lease", True)],
            ),
        ),
        checks=[
            _required_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-apply-refresh-then-lease",
        "Fetch first, then take the lease",
        "Refresh every remote's refs so the lease is taken against current knowledge, then publish the rewrite and verify the result.",
        "Fetch all remotes, push with force-with-lease, then verify.",
        _dv(
            "fg-apply-refresh-then-lease",
            _clean,
            ["git fetch --all", "git push --force-with-lease", STATUS, GRAPH],
            _req(
                {},
                ["git fetch --all", "git push --force-with-lease", "git status", "git log"],
                rules=[_meta("force_with_lease", True)],
            ),
        ),
        checks=[
            _required_check("Remote knowledge was refreshed before the lease.", ["git fetch --all"]),
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/delete-advanced",
        "fg-apply-prune-then-retire",
        "Prune first, then delete the branch",
        "Fetch with pruning to clear the already-deleted tmp-probe ref, then delete the retired old-experiment branch from origin and confirm the result.",
        "Fetch with pruning, delete the remote branch, then verify.",
        _dv(
            "fg-apply-prune-then-retire",
            _retire_remote,
            ["git fetch --prune", "git push origin --delete old-experiment", STATUS, GRAPH],
            _req(
                {},
                ["git fetch --prune", "git push origin --delete", "git status", "git log"],
                rules=[_meta("remote_branch_deleted", "old-experiment")],
            ),
        ),
        checks=[
            _required_check("The remote picture was pruned first.", ["git fetch --prune"]),
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-fetch/prune-advanced", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/delete-advanced",
        "fg-apply-survey-then-retire",
        "Check tracking, then delete deliberately",
        "Read the tracking table, delete the retired old-experiment branch from origin, and confirm the deletion registered.",
        "Inspect tracking, delete the remote branch, then verify.",
        _dv(
            "fg-apply-survey-then-retire",
            _stale_remote,
            ["git branch -vv", "git push origin --delete old-experiment", STATUS, GRAPH],
            _req(
                {},
                ["git branch -vv", "git push origin --delete", "git status", "git log"],
                rules=[_meta("remote_branch_deleted", "old-experiment")],
            ),
        ),
        checks=[
            _required_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-apply-repoint-and-verify",
        "Change the URL, then verify tracking",
        "Point origin at the new address https://relay.frost.test/operations.git, then read the tracking table to confirm everything still lines up.",
        "Change origin's URL, inspect tracking, then verify the state.",
        _dv(
            "fg-apply-repoint-and-verify",
            _clean,
            ["git remote set-url origin https://relay.frost.test/operations.git", "git branch -vv", STATUS, GRAPH],
            _req(
                {},
                ["git remote set-url", "git branch -vv", "git status", "git log"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the new address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}
                    ]
                },
            },
            _required_check("The tracking table was verified afterward.", ["git branch -vv"]),
        ],
        details=["https://relay.frost.test/operations.git"],
        command_forms=["git-branch/tracking", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-apply-migrate-the-mirror",
        "Switch to the mirror URL",
        "The primary server is down for maintenance, so syncs must temporarily go through the mirror. Point origin at https://mirror.frost.test/operations.git and verify the state.",
        "Change origin's URL to the mirror address and verify the state.",
        _dv(
            "fg-apply-migrate-the-mirror",
            _clean,
            [STATUS, "git remote set-url origin https://mirror.frost.test/operations.git", GRAPH],
            _req(
                {},
                ["git status", "git remote set-url", "git log"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://mirror.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the mirror address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://mirror.frost.test/operations.git"}
                    ]
                },
            },
            _required_check("The switch was verified.", ["git log"]),
        ],
        details=["https://mirror.frost.test/operations.git"],
        command_forms=CORE_TAGS,
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-apply-prune-then-advance",
        "Prune, then pull under the guard",
        "Fetch with pruning so the picture is honest, then advance main under the fast-forward-only rule and verify the landing.",
        "Fetch with pruning, pull with the fast-forward rule, then verify.",
        _dv(
            "fg-apply-prune-then-advance",
            _behind_remote,
            ["git fetch --prune", "git pull --ff-only", STATUS, GRAPH],
            _req(
                {},
                ["git fetch --prune", "git pull --ff-only", "git status", "git log"],
                rules=[_meta("pull_strategy", "ff-only")],
            ),
        ),
        checks=[
            _required_check("The remote picture was pruned first.", ["git fetch --prune"]),
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            },
        ],
        command_forms=["git-fetch/prune-advanced", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-apply-sweep-then-replay",
        "Fetch everything, then pull with rebase",
        "Refresh every remote's refs, then pull with the rebase rule and confirm local work now sits on top of the remote's newest history.",
        "Fetch all remotes, pull with rebase, then verify the history.",
        _dv(
            "fg-apply-sweep-then-replay",
            _behind_remote,
            ["git fetch --all", "git pull --rebase", STATUS, GRAPH],
            _req(
                {},
                ["git fetch --all", "git pull --rebase", "git status", "git log"],
                rules=[_meta("pull_strategy", "rebase")],
            ),
        ),
        checks=[
            _required_check("The remote refs were refreshed first.", ["git fetch --all"]),
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 7 - frost-deliver-the-release
# ---------------------------------------------------------------------------

DELIVER_DRILLS = [
    q(
        "git-shortlog/summary",
        "fd-intro-shortlog",
        "Summarize commits by author",
        "The release record must say who did the work. Produce the commit summary grouped by author.",
        "Summarize the commit history grouped by author.",
        _dv("fd-intro-shortlog", _clean, ["git shortlog"], _read_eval(["git shortlog"])),
        checks=[_required_check("Contributors were summarized for the record.", ["git shortlog"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-shortlog/numbered",
        "fd-intro-shortlog-numbered",
        "Count commits per author",
        "The release board wants numbers, not prose: produce the per-author commit counts, sorted by how many commits each person made.",
        "Produce numbered, sorted per-author commit counts.",
        _dv("fd-intro-shortlog-numbered", _clean, ["git shortlog -sn"], _read_eval(["git shortlog -sn"])),
        checks=[_required_check("Per-author commit counts were produced.", ["git shortlog -sn"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-describe/tags",
        "fd-intro-describe",
        "Name the current commit from its tags",
        "Every build that ships needs a human-readable name derived from the nearest release tag. Produce that name for the current commit.",
        "Describe HEAD relative to the nearest reachable tag.",
        _dv("fd-intro-describe", _clean, ["git describe --tags"], _read_eval(["git describe --tags"])),
        checks=[_required_check("The commit was named from its tags.", ["git describe --tags"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-tag/annotated-advanced",
        "fd-intro-tag-annotated",
        "Create an annotated release tag",
        "The reviewed commit becomes a release candidate today. Create an annotated tag named v1.1 with the message 'Heat core release candidate' so the release has a durable name and description.",
        "Create the annotated tag v1.1 with the message 'Heat core release candidate'.",
        _dv(
            "fd-intro-tag-annotated",
            _clean,
            ["git tag -a v1.1 -m 'Heat core release candidate'"],
            _req({}, ["git tag -a"], rules=[_meta("last_tag_created", "v1.1")]),
        ),
        checks=[
            {
                "label": "The annotated release tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.1")]},
            }
        ],
        details=["v1.1", "Heat core release candidate"],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-intro-tag-delete",
        "Delete an outdated tag",
        "The old v1.0 tag now points at superseded work and keeps confusing people. Delete the local tag v1.0.",
        "Delete the outdated local tag v1.0.",
        _dv(
            "fd-intro-tag-delete",
            _clean,
            ["git tag -d v1.0"],
            _req({}, ["git tag -d"], rules=[_meta_set("last_tags_deleted")]),
        ),
        checks=[
            {
                "label": "The outdated tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            }
        ],
        details=["v1.0"],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
    q(
        "git-push/all-tags",
        "fd-intro-push-tags",
        "Publish all tags",
        "Downstream consumers synchronize on tags, not branches. Push every local tag to origin so the release markers are visible everywhere.",
        "Push all local tags to the origin remote.",
        _dv(
            "fd-intro-push-tags",
            _clean,
            ["git push --tags"],
            _req({}, ["git push --tags"], rules=[_meta("last_push_tags", True)]),
        ),
        checks=[
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            }
        ],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
]

DELIVER_WORKFLOWS = [
    q(
        "git-tag/annotated-advanced",
        "fd-apply-name-then-mark",
        "Check the current name, then tag",
        "Find the commit's current tag-derived name, then create the annotated tag v1.1 with the message 'Signed relay candidate' and verify the new marker.",
        "Describe the tip, create the annotated tag v1.1, then verify.",
        _dv(
            "fd-apply-name-then-mark",
            _clean,
            ["git describe --tags", "git tag -a v1.1 -m 'Signed relay candidate'", STATUS, GRAPH],
            _req(
                {},
                ["git describe --tags", "git tag -a", "git status", "git log"],
                rules=[_meta("last_tag_created", "v1.1")],
            ),
        ),
        checks=[
            _required_check("The current tag-derived name was checked first.", ["git describe --tags"]),
            {
                "label": "The annotated release tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.1")]},
            },
        ],
        details=["v1.1", "Signed relay candidate"],
        command_forms=["git-describe/tags", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/all-tags",
        "fd-apply-mark-then-broadcast",
        "Tag the hotfix, then publish the tags",
        "Create the annotated tag v1.2 with the message 'Relay hotfix marker', then push all tags so every consumer picks the new marker up together. Verify afterward.",
        "Create the annotated tag v1.2, push all tags, then verify.",
        _dv(
            "fd-apply-mark-then-broadcast",
            _clean,
            ["git tag -a v1.2 -m 'Relay hotfix marker'", "git push --tags", STATUS, GRAPH],
            _req(
                {},
                ["git tag -a", "git push --tags", "git status", "git log"],
                rules=[_meta("last_push_tags", True)],
            ),
        ),
        checks=[
            {
                "label": "The hotfix tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.2")]},
            },
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            },
        ],
        details=["v1.2", "Relay hotfix marker"],
        command_forms=["git-tag/annotated-advanced", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-apply-credit-then-retire",
        "Credit the authors, then delete the tag",
        "Produce the author summary for the release record, then delete the superseded tag v1.0 and check the remaining state.",
        "Summarize authors, delete the tag v1.0, then verify.",
        _dv(
            "fd-apply-credit-then-retire",
            _clean,
            ["git shortlog", "git tag -d v1.0", STATUS, GRAPH],
            _req(
                {},
                ["git shortlog", "git tag -d", "git status", "git log"],
                rules=[_meta_set("last_tags_deleted")],
            ),
        ),
        checks=[
            _required_check("Authors were credited first.", ["git shortlog"]),
            {
                "label": "The superseded tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            },
        ],
        details=["v1.0"],
        command_forms=["git-shortlog/summary", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-apply-rename-the-marker",
        "Check the name, then delete the stale tag",
        "The v1.0 tag must give way to a corrected one. Check the tip's tag-derived name, delete the stale tag v1.0, and confirm the removal registered.",
        "Describe the tip, delete the tag v1.0, then verify.",
        _dv(
            "fd-apply-rename-the-marker",
            _clean,
            ["git describe --tags", "git tag -d v1.0", STATUS, GRAPH],
            _req(
                {},
                ["git describe --tags", "git tag -d", "git status", "git log"],
                rules=[_meta_set("last_tags_deleted")],
            ),
        ),
        checks=[
            _required_check("The tip's name was checked before deleting.", ["git describe --tags"]),
            {
                "label": "The stale tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            },
        ],
        details=["v1.0"],
        command_forms=["git-describe/tags", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/all-tags",
        "fd-apply-credit-then-broadcast",
        "Count contributions, then publish the tags",
        "Produce the per-author commit counts for the release record, then push all tags to origin and confirm the publication registered.",
        "Count contributions, push all tags, then verify.",
        _dv(
            "fd-apply-credit-then-broadcast",
            _clean,
            ["git shortlog -sn", "git push --tags", STATUS, GRAPH],
            _req(
                {},
                ["git shortlog -sn", "git push --tags", "git status", "git log"],
                rules=[_meta("last_push_tags", True)],
            ),
        ),
        checks=[
            _required_check("Contribution counts were produced first.", ["git shortlog -sn"]),
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            },
        ],
        command_forms=["git-shortlog/numbered", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-shortlog/summary",
        "fd-apply-release-ledger",
        "Assemble the release record",
        "The release record pairs the author summary with the build's tag-derived name. Produce both reads back to back; nothing in the repository may change.",
        "Summarize authors and describe the tip for the record.",
        _dv(
            "fd-apply-release-ledger",
            _clean,
            ["git shortlog", "git describe --tags", STATUS, GRAPH],
            _read_eval(["git shortlog", "git describe --tags", "git status", "git log"]),
        ),
        checks=[
            _required_check("Both record reads were produced.", ["git shortlog", "git describe --tags"]),
        ],
        command_forms=["git-describe/tags", *CORE_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 8 - frost-hunt-the-regression
# ---------------------------------------------------------------------------

HUNT_DRILLS = [
    q(
        "git-bisect/run",
        "fh-intro-bisect-run",
        "Find the bad commit automatically",
        "Something between the known-good first commit and today's tip broke the deployment. Run the project's test script heat-relay-test under bisect so the first bad commit is found automatically.",
        "Run the test script under an automated bisect session.",
        _dv(
            "fh-intro-bisect-run",
            _broken,
            ["git bisect run heat-relay-test"],
            _read_eval(["git bisect run heat-relay-test"]),
        ),
        checks=[_required_check("The regression search was automated.", ["git bisect run"])],
        details=["heat-relay-test"],
        adventure="frost-hunt-the-regression-drills",
    ),
    q(
        "git-bisect/log",
        "fh-intro-bisect-log",
        "Read the bisect record",
        "A bisect verdict nobody can audit is worthless. Read the bisect session's log so the search can be attached to the incident report.",
        "Show the bisect session's log.",
        _dv("fh-intro-bisect-log", _broken, ["git bisect log"], _read_eval(["git bisect log"])),
        checks=[_required_check("The search record was read.", ["git bisect log"])],
        adventure="frost-hunt-the-regression-drills",
    ),
]

HUNT_WORKFLOWS = [
    q(
        "git-bisect/run",
        "fh-apply-hunt-and-record",
        "Run the search, then keep the record",
        "Run the test script heat-relay-test under bisect, then read the bisect log and the history so the verdict ships with its evidence.",
        "Run the automated bisect, read its log, then verify the history.",
        _dv(
            "fh-apply-hunt-and-record",
            _broken,
            ["git bisect run heat-relay-test", "git bisect log", STATUS, GRAPH],
            _read_eval(["git bisect run", "git bisect log", "git status", "git log"]),
        ),
        checks=[
            _required_check("The search was automated.", ["git bisect run"]),
            _required_check("The verdict ships with its record.", ["git bisect log"]),
        ],
        details=["heat-relay-test"],
        command_forms=["git-bisect/log", *CORE_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-second-opinion",
        "Confirm with a second test script",
        "A second, independent test script must confirm the verdict. Run relay-freeze-test under bisect and read the record so both searches can be compared.",
        "Run the second automated bisect and read its record.",
        _dv(
            "fh-apply-second-opinion",
            _broken,
            ["git bisect run relay-freeze-test", "git bisect log", STATUS, GRAPH],
            _read_eval(["git bisect run", "git bisect log", "git status", "git log"]),
        ),
        checks=[
            _required_check("The confirming search was automated.", ["git bisect run"]),
            _required_check("Its record was read.", ["git bisect log"]),
        ],
        details=["relay-freeze-test"],
        command_forms=["git-bisect/log", *CORE_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-survey-then-hunt",
        "Read the history, then run the search",
        "Read the commit graph to understand the search range, run the test script heat-relay-test under bisect, then check the state afterward.",
        "Read the graph, run the automated bisect, then verify.",
        _dv(
            "fh-apply-survey-then-hunt",
            _broken,
            [GRAPH, "git bisect run heat-relay-test", STATUS],
            _read_eval(["git log", "git bisect run", "git status"]),
        ),
        checks=[
            _required_check("The history was read first.", ["git log"]),
            _required_check("The search was automated.", ["git bisect run"]),
        ],
        details=["heat-relay-test"],
        command_forms=CORE_TAGS,
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-audit-the-hunt",
        "Reproduce yesterday's search",
        "Re-run the automated search that produced yesterday's verdict, then read its record so the audit can compare both runs line by line.",
        "Re-run the automated bisect and read its record for the audit.",
        _dv(
            "fh-apply-audit-the-hunt",
            _broken,
            ["git bisect run heat-relay-test", "git bisect log", GRAPH, STATUS],
            _read_eval(["git bisect run", "git bisect log", "git log", "git status"]),
        ),
        checks=[
            _required_check("The search was reproduced for the audit.", ["git bisect run"]),
            _required_check("The audit record was read.", ["git bisect log"]),
        ],
        details=["heat-relay-test"],
        command_forms=["git-bisect/log", *CORE_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 9 - frost-publish-the-core
# ---------------------------------------------------------------------------

PUBLISH_DRILLS = [
    q(
        "git-verify-tag/tag",
        "fp-intro-verify-tag",
        "Verify a release tag's signature",
        "Before the restored release ships, the v1.0 tag's signature must be checked against the trusted release keys. Verify the tag v1.0.",
        "Verify the release tag's signature.",
        _dv("fp-intro-verify-tag", _clean, ["git verify-tag v1.0"], _read_eval(["git verify-tag v1.0"])),
        checks=[_required_check("The release signature was verified.", ["git verify-tag"])],
        details=["v1.0"],
        adventure="frost-publish-the-core-drills",
    ),
    q(
        "git-show-ref/all",
        "fp-intro-show-ref",
        "List every ref and its target",
        "The final handoff has to list every ref this repository exposes. Read the complete ref list with the commit each ref points to.",
        "List every ref and the object it points to.",
        _dv("fp-intro-show-ref", _clean, ["git show-ref"], _read_eval(["git show-ref"])),
        checks=[_required_check("The complete ref list was read.", ["git show-ref"])],
        adventure="frost-publish-the-core-drills",
    ),
]

PUBLISH_WORKFLOWS = [
    q(
        "git-show-ref/all",
        "fp-apply-verify-then-audit",
        "Verify the tag, then list the refs",
        "Verify the release tag v1.0's signature, then read the complete ref list so the publication can be signed off.",
        "Verify the tag, list the refs, then verify the state.",
        _dv(
            "fp-apply-verify-then-audit",
            _clean,
            ["git verify-tag v1.0", "git show-ref", STATUS, GRAPH],
            _read_eval(["git verify-tag", "git show-ref", "git status", "git log"]),
        ),
        checks=[
            _required_check("The release signature was verified first.", ["git verify-tag"]),
            _required_check("The complete ref list was read.", ["git show-ref"]),
        ],
        details=["v1.0"],
        command_forms=["git-verify-tag/tag", *CORE_TAGS],
        adventure="frost-publish-the-core-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-show-ref/all",
        "fp-apply-audit-then-verify",
        "List the refs, then prove the tag",
        "Read the ref list to see what the repository exposes, then prove the release tag v1.0's signature before anyone trusts it.",
        "List the refs, verify the tag, then verify the state.",
        _dv(
            "fp-apply-audit-then-verify",
            _clean,
            ["git show-ref", "git verify-tag v1.0", STATUS, GRAPH],
            _read_eval(["git show-ref", "git verify-tag", "git status", "git log"]),
        ),
        checks=[
            _required_check("The ref list was read first.", ["git show-ref"]),
            _required_check("The release signature was proven.", ["git verify-tag"]),
        ],
        details=["v1.0"],
        command_forms=["git-verify-tag/tag", *CORE_TAGS],
        adventure="frost-publish-the-core-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


LEVELS = [
    *TEMPER_DRILLS,
    *TEMPER_WORKFLOWS,
    *CHOOSE_DRILLS,
    *CHOOSE_WORKFLOWS,
    *SURVIVE_DRILLS,
    *SURVIVE_WORKFLOWS,
    *MOVE_DRILLS,
    *MOVE_WORKFLOWS,
    *REFORGE_DRILLS,
    *REFORGE_WORKFLOWS,
    *GOVERN_DRILLS,
    *GOVERN_WORKFLOWS,
    *DELIVER_DRILLS,
    *DELIVER_WORKFLOWS,
    *HUNT_DRILLS,
    *HUNT_WORKFLOWS,
    *PUBLISH_DRILLS,
    *PUBLISH_WORKFLOWS,
]

__all__ = ["LEVELS"]

"""Blueprint-generated adventure levels."""

from __future__ import annotations

from .chapter_3_branching import BRANCH_BASE
from .chapter_4_merging import MERGE_BASE, PRECONFLICT, RESOLVED_MERGE
from .chapter_5_recovery import RECOVERY_COMMITS
from .chapter_6_patches import CHERRY_REPO, STASH_REPO, STASHED_REPO
from .chapter_7_remotes import PUSH_REPO, REMOTE_LOCAL
from .common import *  # noqa: F403


def _blueprint_state(kind: str) -> dict:
    dirty_readme = {"README.md": {"status": "modified", "content": "Project notes\nBlueprint edit\n"}}
    if kind == "uninitialized":
        return uninitialized({"README.md": "Project notes\n", "src/app.py": "print('hi')\n"})
    if kind == "clone":
        return uninitialized({}, remote_fixtures=REMOTE_FIXTURE_STARTER)
    if kind == "clean":
        return repo(commits=BASE)
    if kind == "dirty":
        return repo(commits=BASE, working_tree=dirty_readme)
    if kind == "staged":
        return repo(commits=BASE, staging={"README.md": {"status": "modified", "content": "Project notes\nStaged edit\n"}})
    if kind == "folder":
        return repo(
            commits=BASE,
            working_tree={
                "src/app.py": {"status": "modified", "content": "print('blueprint')\n"},
                "docs/guide.md": {"status": "untracked", "content": "Guide\n"},
            },
        )
    if kind == "history-note":
        return repo(commits=TWO_COMMITS, working_tree={"REVIEW.md": {"status": "untracked", "content": "Review c1\n"}})
    if kind == "branch-note":
        return repo(
            commits=BRANCH_BASE,
            branches={"main": "c2", "feature/ui": "c1"},
            working_tree={"GRAPH.md": {"status": "untracked", "content": "main is current\n"}},
        )
    if kind == "show-note":
        return repo(commits=TWO_COMMITS, working_tree={"CHANGELOG.md": {"status": "untracked", "content": "Seen c0\n"}})
    if kind == "audit-note":
        return repo(commits=THREE_COMMITS, working_tree={"AUDIT.md": {"status": "untracked", "content": "Audit\n"}})
    if kind == "ignore":
        return repo(
            commits=BASE,
            working_tree={
                ".gitignore": {"status": "untracked", "content": "*.log\n"},
                "build.log": {"status": "ignored", "content": "noise\n"},
                "src/app.py": {"status": "modified", "content": "print('source')\n"},
            },
        )
    if kind == "mixed":
        return repo(
            commits=BASE,
            working_tree={
                "README.md": {"status": "modified", "content": "Project notes\nUpdated\n"},
                "scratch.txt": {"status": "untracked", "content": "local only\n"},
            },
        )
    if kind == "partial":
        return repo(
            commits=BASE,
            working_tree={"src/app.py": {"status": "modified", "hunks": ["fix", "debug"]}},
            partial_hunks={"src/app.py": {"target_hunks": ["fix"], "leftover_hunks": ["debug"]}},
        )
    if kind == "partial-plus":
        state = _blueprint_state("partial")
        state["working_tree"]["docs/notes.md"] = {"status": "untracked", "content": "notes\n"}
        return state
    if kind == "repair":
        return repo(
            commits=BASE,
            staging={"scratch.txt": {"status": "added", "content": "scratch\n"}},
            working_tree={
                "debug.log": {"status": "untracked", "content": "debug\n"},
                "src/app.py": {"status": "modified", "hunks": ["fix", "debug"]},
            },
            partial_hunks={"src/app.py": {"target_hunks": ["fix"], "leftover_hunks": ["debug"]}},
        )
    if kind == "tracked-junk":
        commits = [commit("c0", "Initial", [], {**BASE_TREE, "old.txt": "old\n", ".env": "SECRET=1\n"})]
        return repo(commits=commits, branches={"main": "c0"}, working_tree={".gitignore": {"status": "untracked", "content": "*.env\n"}})
    if kind == "tracked-dir":
        commits = [commit("c0", "Track build output", [], {**BASE_TREE, "dist/app.js": "bundle", "dist/app.css": "css"})]
        return repo(commits=commits, branches={"main": "c0"}, working_tree={".gitignore": {"status": "untracked", "content": "dist/\n"}})
    if kind == "amend":
        return repo(commits=[commit("c0", "Initial", [], BASE_TREE), commit("c1", "wip", ["c0"], BASE_TREE)], branches={"main": "c1"})
    if kind == "amend-dirty":
        return repo(
            commits=[commit("c0", "Initial", [], BASE_TREE), commit("c1", "Update app shell", ["c0"], BASE_TREE)],
            branches={"main": "c1"},
            working_tree=dirty_readme,
        )
    if kind == "amend-staged":
        return repo(
            commits=[commit("c0", "Initial", [], BASE_TREE), commit("c1", "Update app shell", ["c0"], BASE_TREE)],
            branches={"main": "c1"},
            staging={"README.md": {"status": "modified", "content": "Project notes\nStaged follow-up\n"}},
        )
    if kind == "branch":
        return repo(commits=BRANCH_BASE, branches={"main": "c2", "feature/ui": "c1", "old": "c1", "scratch": "c0"})
    if kind == "branch-dirty":
        return repo(
            commits=BRANCH_BASE,
            branches={"main": "c2", "feature/ui": "c1"},
            working_tree=dirty_readme,
        )
    if kind == "branch-delete":
        commits = [*BRANCH_BASE, commit("c3", "Scratch", ["c0"], {"README.md": "scratch\n"})]
        return repo(commits=commits, branches={"main": "c2", "old": "c1", "scratch": "c3"})
    if kind == "merge":
        return repo(commits=MERGE_BASE, branches={"main": "c1", "feature/profile": "c2"})
    if kind == "merge-ff":
        return repo(commits=MERGE_BASE, branches={"main": "c0", "feature/profile": "c2"})
    if kind == "conflict":
        return copy.deepcopy(PRECONFLICT)
    if kind == "conflict-with-feature":
        state = copy.deepcopy(PRECONFLICT)
        state["branches"]["feature/profile"] = "c2"
        return state
    if kind == "conflict-resolved":
        return copy.deepcopy(RESOLVED_MERGE)
    if kind == "recovery":
        return repo(commits=RECOVERY_COMMITS, branches={"main": "c2"})
    if kind == "recovery-dirty":
        return repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}, working_tree=dirty_readme)
    if kind == "reflog-lost":
        return repo(
            commits=RECOVERY_COMMITS,
            branches={"main": "c1"},
            reflog=[
                {"ref": "HEAD@{0}", "target": "c2", "message": "commit: lost work"},
                {"ref": "HEAD@{1}", "target": "c1", "message": "reset: moving to c1"},
            ],
        )
    if kind == "stash-dirty":
        return copy.deepcopy(STASH_REPO)
    if kind == "stashed":
        return copy.deepcopy(STASHED_REPO)
    if kind == "cherry":
        return copy.deepcopy(CHERRY_REPO)
    if kind == "cherry-abort":
        state = copy.deepcopy(CHERRY_REPO)
        state["staging"] = {"src/auth.py": {"status": "added", "content": "guard=True"}}
        state["cherry_pick_in_progress"] = True
        state["cherry_pick_original_head"] = "c1"
        return state
    if kind == "stash-cherry":
        state = copy.deepcopy(CHERRY_REPO)
        state["working_tree"] = {"README.md": {"status": "modified", "content": "wip\n"}}
        return state
    if kind == "remote":
        return copy.deepcopy(REMOTE_LOCAL)
    if kind == "remote-prune":
        return repo(
            commits=BASE,
            remotes={"origin": "https://example.test/team/app.git"},
            remote_branches={"origin/main": "c0", "origin/old-feature": "c0"},
            remote_stale_branches=["old-feature"],
        )
    if kind == "remote-diverged":
        return repo(
            commits=[
                commit("c0", "Initial", [], {"README.md": "base"}),
                commit("c1", "Remote setup", ["c0"], {"README.md": "remote"}),
                commit("c2", "Local note", ["c0"], {"README.md": "base", "notes.md": "local"}),
            ],
            branches={"main": "c2"},
            remotes={"origin": "https://example.test/team/app.git"},
            remote_branches={"origin/main": "c1"},
            upstream_tracking={"main": "origin/main"},
        )
    if kind == "remote-dirty":
        state = copy.deepcopy(REMOTE_LOCAL)
        state["working_tree"] = dirty_readme
        return state
    if kind == "push":
        return copy.deepcopy(PUSH_REPO)
    if kind == "push-tracked":
        state = copy.deepcopy(PUSH_REPO)
        state["upstream_tracking"] = {"feature/payment": "origin/feature/payment"}
        state["remote_branches"] = {"origin/main": "c0", "origin/feature/payment": "c0"}
        return state
    if kind == "push-delete":
        return repo(
            commits=PUSH_REPO["commits"],
            branches={"main": "c1"},
            remotes={"origin": "https://example.test/team/app.git"},
            remote_branches={"origin/main": "c1", "origin/feature/payment": "c1"},
        )
    if kind == "push-amend":
        state = _blueprint_state("push-tracked")
        state["head"] = {"type": "branch", "name": "feature/payment", "target": "c1"}
        return state
    return repo(commits=BASE, working_tree=dirty_readme)

_BLUEPRINT_ADVENTURE_COPY = {
    "repository-foundations": {
        "scene": "A teammate has handed you the starter app before the first review.",
        "why": "The team needs the first history to be clean and auditable before anyone builds on it.",
    },
    "stage-with-intent": {
        "scene": "A review branch has several edits lying around at once.",
        "why": "Only the finished work should cross the index boundary into the next snapshot.",
    },
    "untrack-and-undo-edits": {
        "scene": "A local workspace has useful work mixed with staging mistakes and tracked noise.",
        "why": "The cleanup must protect real source changes while keeping throwaway files out of history.",
    },
    "seal-the-snapshot": {
        "scene": "A local commit is about to become the team's next reference point.",
        "why": "The snapshot and message need to match the work without dragging unfinished edits along.",
    },
    "create-and-move": {
        "scene": "The team is splitting work across branches before the next feature pass.",
        "why": "HEAD and the branch pointers need to land in the right place before new commits happen.",
    },
    "detach-and-clean": {
        "scene": "A small branch graph needs inspection and cleanup before the release note is saved.",
        "why": "Useful work must keep a name, and stale labels should not clutter the map.",
    },
    "integrate-branches": {
        "scene": "Two lines of work are ready to compare or combine.",
        "why": "The integration should preserve the intended history shape instead of hiding what happened.",
    },
    "resolve-conflicts": {
        "scene": "A merge has paused in the middle of a teammate handoff.",
        "why": "The conflict needs evidence-driven resolution before the repository can move forward.",
    },
    "step-back-safely": {
        "scene": "A private branch tip contains a mistake caught before review.",
        "why": "The branch can move back only after the safe target is clear.",
    },
    "reverse-and-recover": {
        "scene": "A bad change is visible in history and the team needs the right recovery path.",
        "why": "Private mistakes and shared mistakes need different Git repairs.",
    },
    "shelve-work": {
        "scene": "Unfinished local work is blocking an urgent branch switch.",
        "why": "The work should survive, but it cannot leak into the interruption task.",
    },
    "transplant-commits": {
        "scene": "One approved fix belongs on this branch, while the surrounding branch history does not.",
        "why": "Only the selected change should travel.",
    },
    "connect-and-inspect": {
        "scene": "A local repository is connected to origin and needs a safe read before action.",
        "why": "Local refs and remote-tracking refs should be understood before any integration or publishing.",
    },
    "integrate-upstream": {
        "scene": "Origin has moved while local work still matters.",
        "why": "The sync should bring in upstream changes without surprise commits or lost WIP.",
    },
    "publish-work": {
        "scene": "A feature branch is ready to coordinate with the remote.",
        "why": "The remote refs should change deliberately and only in the way the task asks.",
    },
}

_BLUEPRINT_STATE_BRIEFS = {
    "uninitialized": "a folder with project files but no Git metadata",
    "clone": "an empty local folder with a prepared remote fixture",
    "clean": "a clean repository at the current commit",
    "dirty": "a tracked README edit waiting in the working tree",
    "staged": "a staged README change ready to become a snapshot",
    "folder": "a small folder with both tracked and new visible files",
    "history-note": "a short history plus an untracked review note",
    "branch-note": "a tiny branch graph plus an untracked graph note",
    "show-note": "a two-commit history plus a changelog draft",
    "audit-note": "a three-commit history plus an audit draft",
    "ignore": "source work beside ignored generated output",
    "mixed": "tracked edits beside untracked local scratch",
    "partial": "one file with a real fix and a leftover debug hunk",
    "partial-plus": "partial source work plus an unrelated notes file",
    "repair": "a staged scratch file, an unwanted debug file, and a real source fix",
    "tracked-junk": "tracked junk that should either be removed or stopped at the index",
    "tracked-dir": "generated build output already tracked in history",
    "amend": "a local commit whose message or content can still be rewritten",
    "amend-dirty": "a local commit plus one more edit that belongs in it",
    "amend-staged": "a staged follow-up edit waiting to join the latest local commit",
    "branch": "several branch pointers on a small commit graph",
    "branch-dirty": "branch pointers plus a dirty README edit",
    "branch-delete": "merged and unmerged branch pointers waiting for cleanup",
    "merge": "two branches with a common ancestor and different tips",
    "merge-ff": "a current branch that can move directly to the feature tip",
    "conflict": "an in-progress merge with conflicted files",
    "conflict-with-feature": "a conflicted merge that must be backed out before retrying from main",
    "conflict-resolved": "a conflicted merge already resolved and staged, one step from completion",
    "recovery": "a short history where HEAD can be moved or reversed",
    "recovery-dirty": "history that needs reversal plus a local replacement edit",
    "reflog-lost": "a branch that moved back while the reflog still remembers the lost tip",
    "stash-dirty": "dirty local work blocking a branch workflow",
    "stashed": "a saved stash stack ready to inspect, restore, or drop",
    "cherry": "a branch that needs one commit from another line of work",
    "cherry-abort": "a cherry-pick already in progress and ready to abort",
    "stash-cherry": "local WIP plus a useful commit on another branch",
    "remote": "local refs connected to an origin remote",
    "remote-prune": "remote-tracking refs including one stale branch",
    "remote-diverged": "local and upstream history that have diverged",
    "remote-dirty": "remote-tracking state plus local WIP",
    "push": "a local feature branch ready to publish",
    "push-tracked": "a branch already tracking its remote counterpart",
    "push-delete": "a remote feature branch ready to remove",
    "push-amend": "a tracked feature branch after a local history rewrite",
}

_BLUEPRINT_READ_ONLY_PREFIXES = (
    "git status",
    "git log",
    "git show",
    "git diff",
    "git branch",
    "git remote",
    "git reflog",
    "git ls-files",
    "git merge-base",
    "git stash list",
    "git check-ignore",
    "git mergetool",
)

def _blueprint_move_summary(commands: list[str]) -> str:
    labels = {
        "add": "staging",
        "branch": "branch pointer management",
        "check-ignore": "ignore-rule inspection",
        "checkout": "legacy checkout or conflict-side selection",
        "cherry-pick": "commit transplanting",
        "clone": "remote clone setup",
        "commit": "snapshot creation",
        "config": "configuration",
        "diff": "change inspection",
        "fetch": "remote-tracking update",
        "init": "repository initialization",
        "log": "history inspection",
        "ls-files": "index inspection",
        "merge": "branch integration",
        "merge-base": "common-ancestor inspection",
        "mergetool": "merge-tool launch",
        "pull": "upstream integration",
        "push": "remote publication",
        "reflog": "recovery-log inspection",
        "remote": "remote inspection",
        "reset": "private history movement",
        "restore": "worktree or index restoration",
        "revert": "shared-history reversal",
        "rm": "tracked-path removal",
        "show": "object inspection",
        "stash": "temporary work shelving",
        "status": "repository state inspection",
        "switch": "HEAD movement",
    }
    moves = []
    for command in commands:
        parts = command.split()
        family = parts[1] if parts[:1] == ["git"] and len(parts) > 1 else command
        label = labels.get(family, "repository state work")
        if label not in moves:
            moves.append(label)
    return ", ".join(moves)

def _blueprint_is_read_only(solution: list[str]) -> bool:
    return all(command.startswith(_BLUEPRINT_READ_ONLY_PREFIXES) for command in solution)

def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:
    if wave.get("story"):
        return str(wave["story"]).strip()
    frame = _BLUEPRINT_ADVENTURE_COPY.get(
        adventure_slug,
        {
            "scene": "A teammate has handed you a focused repository task.",
            "why": "The repository needs one careful Git move before work continues.",
        },
    )
    state_brief = _BLUEPRINT_STATE_BRIEFS.get(wave.get("state", ""), "the authored blueprint start state")
    if _blueprint_is_read_only(list(wave.get("solution") or [])):
        outcome = (
            f"Gather only the requested evidence for {wave['title'].lower()}; do not create "
            "commits, move refs, change the index, or rewrite files."
        )
    else:
        outcome = (
            f"Reach the requested outcome for {wave['title'].lower()}, then stop without "
            "unrelated work."
        )
    return f"{frame['scene']} You open the workspace and find {state_brief}. {outcome} {frame['why']}"

def _blueprint_task(wave: dict, solution: list[str]) -> str:
    return ""

def _blueprint_check_label(required: list[str]) -> str:
    if len(required) == 1:
        return f"Use {required[0]} for the intended repository move."
    return "Complete the required blueprint command path in order."

def _blueprint_variant_state(initial: dict, *, alternate: bool) -> dict:
    state = copy.deepcopy(initial)
    if not alternate:
        return state
    state.setdefault("config", {}).setdefault("user.name", "Blueprint Variant")
    state.setdefault("operation_metadata", {})["blueprint_variant"] = "alternate"
    if state.get("repository_initialized"):
        branches = state.setdefault("branches", {})
        head = state.get("head") if isinstance(state.get("head"), dict) else {}
        target = head.get("target") or branches.get(head.get("name")) or next(
            (value for value in branches.values() if value),
            None,
        )
        if target:
            branch_name = "review/context"
            if branch_name in branches:
                branch_name = "review/context-alt"
            branches[branch_name] = target
            if state.get("remotes"):
                state.setdefault("remote_branches", {}).setdefault("origin/context", target)
    else:
        state.setdefault("working_tree", {}).setdefault(
            "docs/context.md",
            "Alternate project note\n",
        )
    return state

def _blueprint_variants(wave: dict, solution: list[str], required: list[str]) -> list[dict]:
    initial = _blueprint_state(wave.get("state", "worktree"))
    state_requirements = copy.deepcopy(wave.get("evaluation") or {})
    return [
        v(
            wave["id"],
            wave["title"],
            _blueprint_variant_state(initial, alternate=False),
            solution,
            ev(state_requirements, required=required),
            workspace_files=list(wave.get("workspace_files") or []),
        ),
        v(
            f"{wave['id']}-alt",
            f"{wave['title']} - alternate",
            _blueprint_variant_state(initial, alternate=True),
            list(solution),
            ev(state_requirements, required=required),
            workspace_files=list(wave.get("workspace_files") or []),
        ),
    ]

def _blueprint_specs() -> list[dict]:
    specs = []
    for adventure_slug, levels in BLUEPRINT_ADVENTURE_LEVELS.items():
        for level in levels:
            for wave in level["waves"]:
                required = list(wave.get("required") or [])
                solution = list(wave["solution"])
                story = _blueprint_story(adventure_slug, level, wave)
                task = _blueprint_task(wave, solution)
                specs.append(
                    q(
                        wave["usage"],
                        wave["slug"],
                        wave["title"],
                        story,
                        task,
                        _blueprint_variants(wave, solution, required),
                        checks=wave.get("checks")
                        or [
                            {
                                "label": _blueprint_check_label(required),
                                "requirement": {"required_commands": required},
                            }
                        ],
                        details=list(wave.get("details") or []),
                        command_forms=list(wave.get("forms") or []),
                        adventure=adventure_slug,
                        workflow=True,
                        min_counted_commands=0 if _blueprint_is_read_only(solution) else 1,
                        max_counted_commands=max(4, len(solution) + 2),
                    )
                )
    return specs

LEVELS = _blueprint_specs()

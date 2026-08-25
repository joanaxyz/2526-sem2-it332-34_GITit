"""Frostbound-specific repository state fixtures."""

from __future__ import annotations

from ...advanced_story_support import build_advanced_story_state
from ..common import commit, repo


def _work(p: str) -> dict:
    return build_advanced_story_state(p, mode="author")

def _dirty(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
    state["working_tree"] = {
        "src/app.ts": {"status": "modified", "content": "export const mode = 'patched'\n"}
    }
    return state

def _broken_dirty(p: str) -> dict:
    state = build_advanced_story_state(p, mode="revert")
    state["working_tree"] = {
        "src/app.ts": {"status": "modified", "content": "export const mode = 'field-patch'\n"}
    }
    return state

def _staged(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
    state["staging"] = {"src/notes.md": "release repair notes\n"}
    return state

def _stashed(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
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
    state = build_advanced_story_state(p, mode="transplant")
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
    state = build_advanced_story_state(p, mode="transplant")
    state["branches"]["main"] = f"{p}1"
    state["remote_branches"] = {"origin/main": f"{p}2"}
    return state

def _stale_remote(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
    state["remote_branches"] = {
        "origin/main": state["branches"]["main"],
        "origin/old-experiment": f"{p}3",
    }
    state["remote_stale_branches"] = ["old-experiment"]
    return state

def _rebase_ready(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
    state["head"] = {"type": "branch", "name": "feature/work"}
    return state

def _retire_remote(p: str) -> dict:
    """One remote branch to retire by hand plus a separate stale ref to prune."""
    state = build_advanced_story_state(p, mode="transplant")
    state["remote_branches"] = {
        "origin/main": state["branches"]["main"],
        "origin/old-experiment": f"{p}3",
        "origin/tmp-probe": f"{p}4",
    }
    state["remote_stale_branches"] = ["tmp-probe"]
    return state

def _rebase_paused(p: str) -> dict:
    state = build_advanced_story_state(p, mode="transplant")
    state["rebase_state"] = {
        "abort_state": build_advanced_story_state(p, mode="transplant"),
        "remaining": [f"{p}3"],
        "applied": [],
    }
    return state

def _meta(key, value):
    return {"type": "operation_metadata_equals", "key": key, "value": value}

def _meta_set(key):
    return {"type": "operation_metadata_not_equals", "key": key, "value": None}


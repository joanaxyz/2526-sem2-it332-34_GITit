from simulator.state import RepositoryStateNormalizer


class RepositoryVisualizationService:
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def snapshot(
        self,
        state: dict,
        *,
        previous_state: dict | None = None,
        target_state: dict | None = None,
    ) -> dict:
        current = self.normalizer.normalize(state)
        previous = self.normalizer.normalize(previous_state) if previous_state is not None else None
        target = self.normalizer.normalize(target_state) if target_state is not None else None
        return {
            "schema_version": 2,
            "commit_dag": self._commit_dag(current),
            "state_lens": self._state_lens(current),
            "target_state_lens": self._state_lens(target) if target is not None else {},
            "command_effect_delta": self._delta(previous, current) if previous is not None else {},
        }

    def _commit_dag(self, state: dict) -> dict:
        return {
            "commits": state.get("commits", []),
            "branches": state.get("branches", {}),
            "head": state.get("head", {}),
            "remote_tracking_branches": state.get("remote_branches", {}),
            "reflog": state.get("reflog", []),
        }

    def _state_lens(self, state: dict) -> dict:
        return {
            "repository_initialized": state.get("repository_initialized", True),
            "working_directory": self._path_entries(state.get("working_tree", {})),
            "staging_area": self._path_entries(state.get("staging", {})),
            "local_repository": {
                "head": state.get("head", {}),
                "branches": state.get("branches", {}),
                "commit_count": len(state.get("commits", [])),
            },
            "branch_pointers": state.get("branches", {}),
            "remote_tracking_branches": state.get("remote_branches", {}),
            "remotes": state.get("remotes", {}),
            "stash_stack": state.get("stash_stack", []),
            "conflicts": [
                {
                    "path": path,
                    "detail": (state.get("conflict_details") or {}).get(path, {}),
                }
                for path in state.get("conflicts", [])
            ],
        }

    def _delta(self, previous: dict | None, current: dict) -> dict:
        if previous is None:
            return {}
        return {
            "files_staged": sorted(
                set(current.get("staging", {})) - set(previous.get("staging", {}))
            ),
            "files_unstaged": sorted(
                set(previous.get("staging", {})) - set(current.get("staging", {}))
            ),
            "files_modified": self._changed_keys(
                previous.get("working_tree", {}),
                current.get("working_tree", {}),
            ),
            "files_restored": sorted(
                set(previous.get("working_tree", {})) - set(current.get("working_tree", {}))
            ),
            "commits_created": [
                commit
                for commit in current.get("commits", [])
                if commit.get("id") not in {item.get("id") for item in previous.get("commits", [])}
            ],
            "branches_created": sorted(
                set(current.get("branches", {})) - set(previous.get("branches", {}))
            ),
            "branches_deleted": sorted(
                set(previous.get("branches", {})) - set(current.get("branches", {}))
            ),
            "branches_moved": self._changed_refs(
                previous.get("branches", {}),
                current.get("branches", {}),
            ),
            "head_moved": previous.get("head") != current.get("head"),
            "remote_tracking_updated": self._changed_refs(
                previous.get("remote_branches", {}),
                current.get("remote_branches", {}),
            ),
            "stash_pushed": len(current.get("stash_stack", [])) > len(previous.get("stash_stack", [])),
            "stash_popped": len(current.get("stash_stack", [])) < len(previous.get("stash_stack", [])),
            "conflicts_created": sorted(
                set(current.get("conflicts", [])) - set(previous.get("conflicts", []))
            ),
            "conflicts_resolved": sorted(
                set(previous.get("conflicts", [])) - set(current.get("conflicts", []))
            ),
        }

    def _path_entries(self, entries: dict) -> list[dict]:
        return [
            {
                "path": path,
                "status": self._entry_status(value),
                "tokens": self._entry_tokens(value),
                "value": value,
            }
            for path, value in sorted(entries.items())
        ]

    def _changed_keys(self, previous: dict, current: dict) -> list[str]:
        paths = set(previous) | set(current)
        return sorted(path for path in paths if previous.get(path) != current.get(path))

    def _changed_refs(self, previous: dict, current: dict) -> list[dict]:
        return [
            {"name": name, "before": previous.get(name), "after": current.get(name)}
            for name in sorted(set(previous) | set(current))
            if previous.get(name) != current.get(name)
        ]

    def _entry_status(self, value) -> str:
        if isinstance(value, dict) and isinstance(value.get("status"), str):
            return value["status"]
        return "modified"

    def _entry_tokens(self, value) -> list[str]:
        if isinstance(value, dict):
            for key in ("hunks", "tokens", "target_hunks", "leftover_hunks"):
                if key in value:
                    raw = value.get(key)
                    return [str(item) for item in (raw if isinstance(raw, list) else [raw])]
        return []
